"""Production-grade lead generation pipeline for the Growth Automation stack.

The module exposes a modular, extensible, and cost-aware lead generation
service capable of orchestrating multiple upstream data providers, caching
interactions, enriching sparse results, and exporting ranked, ready-to-use
lead data.

High-level responsibilities:
    * Discover candidate businesses from pluggable data sources
    * Enrich leads with emails, firmographics, & metadata
    * Score and filter the resulting inventory for downstream automation
    * Persist deterministic exports and maintain deduplication history

Supported data sources:
    * Yelp Open Dataset (free, local businesses)
    * Web directory scraping (public business directories)
    * Hunter.io (email discovery via domain search)
    * Apollo.io People Search (people search API for business discovery)
    * Apollo.io Organization Search (company enrichment)

The implementation emphasizes:
    * Minimal paid API usage – free tiers first, caching everywhere
    * Async networking with retry/backoff semantics
    * Google-style docstrings and inline commentary for critical logic
    * Drop-in provider abstractions for future integrations
"""

from __future__ import annotations

import abc
import asyncio
import hashlib
import json
import logging
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, ConfigDict, Field, ValidationError

# Try to import OpenRouter client for keyword generation
try:
    from pipeline.openrouter_client import OpenRouterClient
    OPENROUTER_AVAILABLE = True
except ImportError:
    OPENROUTER_AVAILABLE = False
    OpenRouterClient = None


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def generate_industry_keywords(industry: str, cache: Optional[SQLiteCacheBackend] = None) -> List[str]:
    """Generate industry-related keywords using LLM for flexible category matching.
    
    Args:
        industry: The industry term (e.g., "dentist")
        cache: Optional cache backend to store generated keywords
        
    Returns:
        List of keywords that might appear in business directories
    """
    cache_key = f"industry_keywords:{industry.lower()}"
    
    # Check cache first
    if cache:
        cached = cache.get(cache_key)
        if cached:
            try:
                return json.loads(cached)
            except (json.JSONDecodeError, ValueError):
                pass
    
    # Fallback keywords if OpenRouter not available
    fallback_keywords = {
        "dentist": ["dentist", "dentistry", "dentists", "dental", "orthodontist", "orthodontics", 
                    "oral surgeon", "periodontist", "endodontist", "prosthodontist"],
        "plumber": ["plumber", "plumbing", "plumbers", "pipe", "drain", "sewer", "water", 
                    "heating", "repair", "installation"],
        "lawyer": ["lawyer", "attorney", "law", "legal", "law firm", "litigation", "counsel", 
                   "advocate", "barrister", "solicitor"],
        "hvac": ["hvac", "heating", "cooling", "air conditioning", "furnace", "ac", "climate", 
                 "ventilation", "refrigeration", "thermal"],
    }
    
    # Use fallback if OpenRouter not available
    if not OPENROUTER_AVAILABLE:
        keywords = fallback_keywords.get(industry.lower(), [industry.lower()])
        if cache:
            cache.set(cache_key, json.dumps(keywords), ttl_seconds=60 * 60 * 24 * 7)  # Cache for 7 days
        return keywords
    
    try:
        # Use OpenRouter client's method to call API
        client = OpenRouterClient()
        
        # Generate keywords using Mistral Medium
        prompt = f"""You are an expert at identifying business categories and keywords used in business directories.

Given an industry term, generate a list of 10 keywords that might appear in business directory categories for that industry.

Industry: {industry}

Generate exactly 10 keywords that businesses in this industry might be categorized under in directories like Yelp, Yellow Pages, etc.
Include variations, related terms, and common category names.

Return ONLY a JSON array of strings, nothing else. Example format:
["keyword1", "keyword2", "keyword3", ...]

Keywords:"""

        # Temporarily set model to mistral-medium for keyword generation
        original_model = client.config.model
        original_temp = client.config.temperature
        original_max_tokens = client.config.max_tokens
        
        client.config.model = "mistralai/mixtral-8x7b-instruct"  # Use Mixtral as it's more widely available
        client.config.temperature = 0.3
        client.config.max_tokens = 200
        
        # Call OpenRouter
        logger.info(f"Calling OpenRouter API to generate keywords for '{industry}'...")
        content = client._call_openrouter(prompt)
        
        # Restore original settings
        client.config.model = original_model
        client.config.temperature = original_temp
        client.config.max_tokens = original_max_tokens
        
        logger.debug(f"OpenRouter response: {content[:200]}...")
        
        # Try to parse JSON array from response
        # Remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        try:
            keywords = json.loads(content)
            if isinstance(keywords, list) and len(keywords) > 0:
                # Ensure all keywords are lowercase strings
                keywords = [str(k).lower().strip() for k in keywords if k]
                logger.info(f"Successfully generated {len(keywords)} keywords via LLM")
                if cache:
                    cache.set(cache_key, json.dumps(keywords), ttl_seconds=60 * 60 * 24 * 7)
                return keywords
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse keywords JSON from LLM response: {content[:200]}. Error: {e}")
        
        # Fallback to default keywords
        logger.warning(f"Falling back to default keywords for '{industry}'")
        keywords = fallback_keywords.get(industry.lower(), [industry.lower()])
        if cache:
            cache.set(cache_key, json.dumps(keywords), ttl_seconds=60 * 60 * 24 * 7)
        return keywords
        
    except Exception as e:
        logger.warning(f"Failed to generate keywords via LLM for '{industry}': {e}. Using fallback.")
        import traceback
        logger.debug(traceback.format_exc())
        keywords = fallback_keywords.get(industry.lower(), [industry.lower()])
        if cache:
            cache.set(cache_key, json.dumps(keywords), ttl_seconds=60 * 60 * 24 * 7)
        return keywords


EMAIL_REGEX = re.compile(
    r"(?:(?:mailto:)?)([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})",
    flags=re.IGNORECASE,
)
SCRAPE_PATHS: Tuple[str, ...] = (
    "/",
    "/contact",
    "/contact-us",
    "/contact-us/",
    "/about",
    "/about-us",
    "/team",
    "/our-team",
    "/people",
    "/leadership",
    "/staff",
    "/get-in-touch",
    "/support",
    "/support/contact",
    "/help",
    "/faq",
    "/services",
    "/what-we-do",
    "/locations",
    "/location",
    "/branches",
    "/appointments",
    "/request-appointment",
    "/schedule",
    "/book",
    "/book-now",
    "/connect",
    "/community",
    "/news",
    "/blog",
)
DEFAULT_SCORE_THRESHOLD = 0.35


def normalize_domain(value: Optional[str]) -> Optional[str]:
    """Normalize a domain or URL into a bare hostname.

    Args:
        value: The candidate domain or URL extracted from upstream sources.

    Returns:
        A lower-cased hostname stripped of schemes, ports, and paths, or None
        when a valid hostname cannot be inferred.
    """
    if not value:
        return None

    candidate = value.strip()
    if not candidate:
        return None

    if candidate.startswith(("http://", "https://")):
        parsed = urlparse(candidate)
        hostname = parsed.netloc or parsed.path
    else:
        hostname = candidate

    hostname = hostname.lower().split("@")[-1].split(":")[0].strip("/")

    if not hostname or "." not in hostname:
        return None

    return hostname


def slugify(value: str) -> str:
    """Generate a filesystem-safe slug for placeholder identifiers.

    Args:
        value: Raw string (e.g., business name).

    Returns:
        A slug comprised of lowercase alphanumerics and hyphens.
    """
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return cleaned or "unknown"


def generate_placeholder_domain(name: str, source: str) -> str:
    """Generate a deterministic placeholder domain when none is provided.

    Args:
        name: Business name used to seed the placeholder.
        source: Source identifier to guarantee uniqueness across providers.

    Returns:
        Synthetic domain suitable for deduplication without collisions.
    """
    slug = slugify(name)
    return f"{slug}.{source}.placeholder"


def extract_emails_from_html(html: str) -> Set[str]:
    """Extract email addresses from HTML content using BeautifulSoup & regex.

    Args:
        html: Raw HTML text pulled from a website.

    Returns:
        A set of normalized email addresses discovered in anchors or text.
    """
    emails: Set[str] = set()
    soup = BeautifulSoup(html, "lxml")

    # Extract mailto links explicitly.
    for anchor in soup.select("a[href^=mailto]"):
        match = EMAIL_REGEX.search(anchor["href"])
        if match:
            emails.add(match.group(1).lower())

    # Fallback to raw regex scanning for plain text emails.
    for match in EMAIL_REGEX.finditer(html):
        emails.add(match.group(1).lower())

    return emails


def now_ts() -> float:
    """Return the current Unix timestamp."""
    return time.time()


@dataclass
class Lead:
    """Canonical lead representation shared across the pipeline."""

    name: str
    domain: str
    location: Optional[str] = None
    industry: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    source: str = "unknown"
    linkedin_url: Optional[str] = None
    yelp_url: Optional[str] = None
    google_maps_url: Optional[str] = None
    bbb_url: Optional[str] = None
    crunchbase_url: Optional[str] = None
    score: float = 0.0
    confidence: float = 0.0
    tags: Set[str] = field(default_factory=set)
    emails: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert lead into a serializable dictionary."""
        return {
            "name": self.name,
            "domain": self.domain,
            "location": self.location,
            "industry": self.industry,
            "email": self.email,
            "phone": self.phone,
            "description": self.description,
            "source": self.source,
            "linkedin_url": self.linkedin_url,
            "yelp_url": self.yelp_url,
            "google_maps_url": self.google_maps_url,
            "bbb_url": self.bbb_url,
            "crunchbase_url": self.crunchbase_url,
            "score": self.score,
            "confidence": self.confidence,
            "tags": sorted(self.tags),
            "emails": sorted(self.emails),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Lead:
        """Instantiate a lead from a dictionary."""
        return cls(
            name=data["name"],
            domain=data["domain"],
            location=data.get("location"),
            industry=data.get("industry"),
            email=data.get("email"),
            phone=data.get("phone"),
            description=data.get("description"),
            source=data.get("source", "unknown"),
            linkedin_url=data.get("linkedin_url"),
            yelp_url=data.get("yelp_url"),
            google_maps_url=data.get("google_maps_url"),
            bbb_url=data.get("bbb_url"),
            crunchbase_url=data.get("crunchbase_url"),
            score=data.get("score", 0.0),
            confidence=data.get("confidence", 0.0),
            tags=set(data.get("tags", [])),
            emails=set(data.get("emails", [])),
            metadata=data.get("metadata", {}),
        )

    def get_hash(self) -> str:
        """Return a deterministic hash for deduplicating leads."""
        key = f"{self.domain.lower()}|{self.email or ''}".strip("|")
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def add_email(self, email: str) -> None:
        """Append an email address to the lead."""
        normalized = email.lower()
        if normalized:
            self.emails.add(normalized)
            if not self.email:
                self.email = normalized

    def merge(self, other: Lead) -> Lead:
        """Merge data from another lead into the current instance."""
        if other.email and not self.email:
            self.email = other.email
        if other.phone and not self.phone:
            self.phone = other.phone
        if other.description and not self.description:
            self.description = other.description
        if other.industry and not self.industry:
            self.industry = other.industry
        if other.location and not self.location:
            self.location = other.location
        self.tags.update(other.tags)
        self.emails.update(other.emails)
        self.metadata.update(other.metadata)
        return self


@dataclass(frozen=True)
class LeadQuery:
    """Query payload describing a lead search request."""

    industry: str
    location: str
    limit: int


class LeadPipelineSettings(BaseModel):
    """Runtime configuration for the lead generation service."""

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    leads_dir: Path = Field(default=Path("pipeline/leads"))
    cache_path: Path = Field(default=Path("pipeline/cache/lead_cache.sqlite3"))
    cache_ttl_seconds: int = Field(default=60 * 60 * 12, ge=60)
    http_timeout: float = Field(default=20.0, gt=0)
    max_concurrency: int = Field(default=5, ge=1)
    request_retry_attempts: int = Field(default=3, ge=1)
    request_retry_backoff: float = Field(default=1.6, gt=0)
    yelp_dataset_path: Optional[Path] = Field(
        default=Path("pipeline/yelp_academic_dataset_business.json"), alias="YELP_OPEN_DATASET_PATH"
    )
    APOLLOIO_API_KEY: Optional[str] = Field(default=None, alias="APOLLOIO_API_KEY")
    SCRAPERAPI_API_KEY: Optional[str] = Field(default=None, alias="SCRAPERAPI_API_KEY")
    directory_scrape_targets: List[str] = Field(
        default_factory=lambda: [
            # Primary sources (may block but worth trying)
            "https://www.dexknows.com/search?what={industry}&where={location}",
            "https://www.superpages.com/search?search_terms={industry}&geo_location_terms={location}",
            "https://www.yellowpages.com/search?search_terms={industry}&geo_location_terms={location}",
            "https://www.whitepages.com/search/FindPeople?who={industry}&where={location}",
            "https://www.switchboard.com/business/search/{location}/{industry}",
            "https://www.brownbook.net/business/search/?keyword={industry}&location={location}",
            "https://www.hotfrog.com/search/{location}/{industry}",

            # Additional sources (more niche, potentially less blocked)
            "https://www.chamberofcommerce.com/{location}?query={industry}",
            "https://www.bizjournals.com/{location}/search?q={industry}",
            "https://www.merchantcircle.com/search?what={industry}&where={location}",
            "https://www.citysearch.com/search?what={industry}&where={location}",
            "https://www.shoplocal.com/results?keywords={industry}&location={location}",
            "https://www.bbb.org/search?find_country=USA&find_text={industry}&find_loc={location}",
            "https://www.homeadvisor.com/search/{industry}-{location}",
            "https://www.care.com/search/{industry}/{location}",
            "https://www.nextdoor.com/search/{industry}/{location}",
            "https://www.golocal247.com/search/{industry}/{location}",
            "https://www.showmelocal.com/search.aspx?what={industry}&where={location}",
            "https://www.yellowbook.com/search/{industry}/{location}",
        ]
    )
    user_agent: str = Field(
        default=(
            "LeadPipelineBot/1.0 (+https://supagent.ai; contact: leads@supagent.ai)"
        )
    )
    use_playwright: bool = Field(default=True)
    playwright_timeout: float = Field(default=25.0, gt=0)
    exporter_format: str = Field(default="json")

    @classmethod
    def _env_aliases(cls) -> Dict[str, str]:
        """Map internal field names to environment variable aliases."""
        return {
            "leads_dir": "LEAD_PIPELINE_LEADS_DIR",
            "cache_path": "LEAD_PIPELINE_CACHE_PATH",
            "cache_ttl_seconds": "LEAD_PIPELINE_CACHE_TTL_SECONDS",
            "http_timeout": "LEAD_PIPELINE_HTTP_TIMEOUT",
            "max_concurrency": "LEAD_PIPELINE_MAX_CONCURRENCY",
            "request_retry_attempts": "LEAD_PIPELINE_REQUEST_RETRY_ATTEMPTS",
            "request_retry_backoff": "LEAD_PIPELINE_REQUEST_RETRY_BACKOFF",
            "yelp_dataset_path": "YELP_OPEN_DATASET_PATH",
            "APOLLOIO_API_KEY": "APOLLOIO_API_KEY",
            "SCRAPERAPI_API_KEY": "SCRAPERAPI_API_KEY",
            "directory_scrape_targets": "LEAD_PIPELINE_DIRECTORY_SCRAPE_TARGETS",
            "user_agent": "LEAD_PIPELINE_USER_AGENT",
            "use_playwright": "LEAD_PIPELINE_USE_PLAYWRIGHT",
            "playwright_timeout": "LEAD_PIPELINE_PLAYWRIGHT_TIMEOUT",
            "exporter_format": "LEAD_PIPELINE_EXPORTER_FORMAT",
        }

    @classmethod
    def from_env(cls, **overrides: Any) -> LeadPipelineSettings:
        """Instantiate settings from environment variables with overrides."""
        # Load .env file if it exists
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # dotenv not available, continue with os.environ

        raw: Dict[str, Any] = {}
        for field, env_name in cls._env_aliases().items():
            if env_name in os.environ:
                raw[field] = os.environ[env_name]
        if "directory_scrape_targets" in raw and isinstance(
            raw["directory_scrape_targets"], str
        ):
            raw["directory_scrape_targets"] = [
                item.strip()
                for item in raw["directory_scrape_targets"].split("|")
                if item.strip()
            ]
        raw.update(overrides)
        try:
            settings = cls(**raw)
        except ValidationError as exc:
            raise ValueError(f"Invalid lead pipeline configuration: {exc}") from exc

        settings.leads_dir = Path(settings.leads_dir)
        settings.cache_path = Path(settings.cache_path)
        if settings.yelp_dataset_path:
            settings.yelp_dataset_path = Path(settings.yelp_dataset_path)
        settings.leads_dir.mkdir(parents=True, exist_ok=True)
        settings.cache_path.parent.mkdir(parents=True, exist_ok=True)
        return settings


async def fetch_with_scraperapi(url: str, api_key: str, outscraper_key: Optional[str] = None) -> Optional[str]:
    """Fetch HTML using ScraperAPI or Outscraper as fallback when Playwright fails."""
    # Try ScraperAPI first, then Outscraper as fallback
    keys_to_try = []
    if api_key:
        keys_to_try.append(("ScraperAPI", f"http://api.scraperapi.com/?api_key={api_key}&url={url}&render=true"))
    if outscraper_key:
        # For Outscraper, we need to encode the URL
        import urllib.parse
        encoded_url = urllib.parse.quote(url)
        keys_to_try.append(("Outscraper", f"https://api.outscraper.com/request?query={encoded_url}&key={outscraper_key}"))

    if not keys_to_try:
        return None

    for service_name, scraperapi_url in keys_to_try:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(scraperapi_url)
                if response.status_code == 200:
                    return response.text
                else:
                    logger.debug("%s failed with status: %s", service_name, response.status_code)
        except Exception as exc:
            logger.debug("%s fetch failed: %s", service_name, exc)
            continue

    return None


async def fetch_with_playwright(url: str, timeout: float) -> Optional[str]:
    """Fetch fully rendered HTML using Playwright when installed."""
    try:
        from playwright.async_api import async_playwright  # type: ignore
    except ImportError:
        logger.debug("Playwright not installed; skipping JS-rendered fetch for %s", url)
        return None

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            page = await browser.new_page()

            # Set user agent to avoid bot detection
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })

            # Navigate with shorter timeout
            await page.goto(url, timeout=int(min(timeout, 15.0) * 1000))

            # Quick wait for content to load
            await page.wait_for_timeout(1000)  # Only 1 second

            # Check if we got a captcha or block page
            content = await page.content()
            if any(indicator in content.lower() for indicator in ['captcha', 'cloudflare', 'blocked', 'access denied']):
                await browser.close()
                return None  # Don't waste time on blocked pages

            content = await page.content()
            await browser.close()
            return content
    except Exception as exc:  # pragma: no cover - diagnostic
        logger.debug("Playwright fetch failed for %s: %s", url, exc)
        return None


class SQLiteCacheBackend:
    """Persistence layer for caching outbound HTTP responses."""

    def __init__(self, path: Path, ttl_seconds: int):
        """Initialize the SQLite cache backend."""
        self.path = Path(path)
        self.ttl_seconds = ttl_seconds
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._prepare()

    def _prepare(self) -> None:
        """Create the backing table if it does not yet exist."""
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    cache_key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    expires_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache (expires_at)"
            )
            conn.commit()

    def get(self, cache_key: str) -> Optional[str]:
        """Return a cached payload if it is still fresh."""
        current_ts = now_ts()
        with sqlite3.connect(self.path) as conn:
            cursor = conn.execute(
                "SELECT payload, expires_at FROM cache WHERE cache_key = ?",
                (cache_key,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            payload, expires_at = row
            if expires_at < current_ts:
                conn.execute("DELETE FROM cache WHERE cache_key = ?", (cache_key,))
                conn.commit()
                return None
            return payload

    def set(self, cache_key: str, payload: str, ttl_seconds: Optional[int] = None) -> None:
        """Persist a payload along with an absolute expiry."""
        ttl = ttl_seconds or self.ttl_seconds
        expires_at = now_ts() + ttl
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                INSERT INTO cache (cache_key, payload, expires_at)
                VALUES (?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    payload = excluded.payload,
                    expires_at = excluded.expires_at
                """,
                (cache_key, payload, expires_at),
            )
            conn.commit()

    def delete(self, cache_key: str) -> None:
        """Remove a cached payload."""
        with sqlite3.connect(self.path) as conn:
            conn.execute("DELETE FROM cache WHERE cache_key = ?", (cache_key,))
            conn.commit()

    async def aget(self, cache_key: str) -> Optional[str]:
        """Async wrapper around ``get`` for compatibility with async flows."""
        return await asyncio.to_thread(self.get, cache_key)

    async def aset(
        self, cache_key: str, payload: str, ttl_seconds: Optional[int] = None
    ) -> None:
        """Async wrapper around ``set`` for compatibility with async flows."""
        await asyncio.to_thread(self.set, cache_key, payload, ttl_seconds)


@dataclass
class HTTPResult:
    """Normalized HTTP response payload returned by ``AsyncHTTPClient``."""

    url: str
    status_code: int
    headers: Dict[str, str]
    text: Optional[str] = None
    json: Optional[Any] = None


class AsyncHTTPClient:
    """Async HTTP client with concurrency limits, retries, and caching."""

    def __init__(self, settings: LeadPipelineSettings, cache: SQLiteCacheBackend):
        self._settings = settings
        self._cache = cache
        self._client = httpx.AsyncClient(
            timeout=settings.http_timeout,
            headers={"User-Agent": settings.user_agent},
        )
        self._semaphore = asyncio.Semaphore(settings.max_concurrency)

    async def __aenter__(self) -> AsyncHTTPClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._client.aclose()

    async def get(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cache_key: Optional[str] = None,
        cache_ttl: Optional[int] = None,
        use_cache: bool = True,
    ) -> HTTPResult:
        """Perform an HTTP GET request with retries and caching."""
        key = cache_key or self._make_cache_key("GET", url, params)
        if use_cache:
            cached = await self._cache.aget(key)
            if cached:
                return self._deserialize(cached)

        last_error: Optional[Exception] = None
        for attempt in range(self._settings.request_retry_attempts):
            try:
                async with self._semaphore:
                    response = await self._client.get(
                        url, params=params, headers=headers
                    )
                result = self._normalize_response(response)
                if use_cache:
                    await self._cache.aset(
                        key, self._serialize(result), cache_ttl
                    )
                return result
            except httpx.HTTPError as exc:
                last_error = exc
                backoff = self._settings.request_retry_backoff * (attempt + 1)
                await asyncio.sleep(backoff)
        raise RuntimeError(f"Request to {url} failed") from last_error

    async def post(
        self,
        url: str,
        *,
        json_payload: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cache_key: Optional[str] = None,
        cache_ttl: Optional[int] = None,
        use_cache: bool = False,
    ) -> HTTPResult:
        """Perform an HTTP POST request with retries and optional caching."""
        key = cache_key or self._make_cache_key("POST", url, json_payload or data)
        if use_cache:
            cached = await self._cache.aget(key)
            if cached:
                return self._deserialize(cached)

        last_error: Optional[Exception] = None
        for attempt in range(self._settings.request_retry_attempts):
            try:
                async with self._semaphore:
                    response = await self._client.post(
                        url, json=json_payload, data=data, headers=headers
                    )
                result = self._normalize_response(response)
                if use_cache:
                    await self._cache.aset(
                        key, self._serialize(result), cache_ttl
                    )
                return result
            except httpx.HTTPError as exc:
                last_error = exc
                backoff = self._settings.request_retry_backoff * (attempt + 1)
                await asyncio.sleep(backoff)
        raise RuntimeError(f"Request to {url} failed") from last_error

    def _normalize_response(self, response: httpx.Response) -> HTTPResult:
        """Normalize httpx responses into ``HTTPResult``."""
        try:
            payload = response.json()
            json_payload: Optional[Any] = payload
            text_payload: Optional[str] = None
        except (ValueError, json.JSONDecodeError):
            payload = response.text
            json_payload = None
            text_payload = payload

        return HTTPResult(
            url=str(response.request.url),
            status_code=response.status_code,
            headers=dict(response.headers),
            json=json_payload,
            text=text_payload,
        )

    def _make_cache_key(
        self, method: str, url: str, payload: Optional[Dict[str, Any]]
    ) -> str:
        """Build a deterministic cache key for the request."""
        normalized_payload = json.dumps(payload or {}, sort_keys=True, default=str)
        hashed = hashlib.sha256(normalized_payload.encode("utf-8")).hexdigest()
        return f"{method}:{url}:{hashed}"

    def _serialize(self, result: HTTPResult) -> str:
        """Serialize ``HTTPResult`` for caching."""
        return json.dumps(
            {
                "url": result.url,
                "status_code": result.status_code,
                "headers": result.headers,
                "text": result.text,
                "json": result.json,
            },
            ensure_ascii=False,
        )

    def _deserialize(self, payload: str) -> HTTPResult:
        """Deserialize cache payload into ``HTTPResult``."""
        data = json.loads(payload)
        return HTTPResult(
            url=data["url"],
            status_code=data["status_code"],
            headers=data["headers"],
            text=data.get("text"),
            json=data.get("json"),
        )


@dataclass
class LeadPipelineContext:
    """Shared resources injected into connectors and enrichers."""

    settings: LeadPipelineSettings
    cache: SQLiteCacheBackend
    http: AsyncHTTPClient


class LeadSourceConnector(abc.ABC):
    """Base class for pluggable lead source connectors."""

    name: str = "base"

    @abc.abstractmethod
    async def fetch(
        self, query: LeadQuery, context: LeadPipelineContext
    ) -> List[Lead]:
        """Fetch leads for the supplied query."""

    def is_configured(self, settings: LeadPipelineSettings) -> bool:
        """Return True when the connector has required credentials."""
        return True


class LeadEnricher(abc.ABC):
    """Base class for enrichment modules acting on discovered leads."""

    name: str = "enricher"

    @abc.abstractmethod
    async def enrich(
        self, lead: Lead, context: LeadPipelineContext
    ) -> Lead:
        """Enrich the provided lead in-place and return it."""

    def is_configured(self, settings: LeadPipelineSettings) -> bool:
        """Return True when the enricher has required credentials."""
        return True


class YelpOpenDatasetConnector(LeadSourceConnector):
    """Connector that surfaces businesses from the local Yelp Open Dataset."""

    name = "yelp_open_dataset"

    def is_configured(self, settings: LeadPipelineSettings) -> bool:
        return bool(settings.yelp_dataset_path and settings.yelp_dataset_path.exists())

    async def fetch(
        self, query: LeadQuery, context: LeadPipelineContext
    ) -> List[Lead]:
        if not self.is_configured(context.settings):
            logger.info("Skipping Yelp Open Dataset – dataset path not configured.")
            return []

        # Generate industry keywords using LLM (cached)
        print(f"INFO: Generating keywords for industry '{query.industry}'...")
        industry_keywords = await asyncio.to_thread(
            generate_industry_keywords, query.industry, context.cache
        )
        print(f"INFO: Generated {len(industry_keywords)} keywords: {industry_keywords[:5]}...")

        leads = await asyncio.to_thread(
            self._read_dataset, context.settings.yelp_dataset_path, query, industry_keywords
        )
        return leads[: query.limit]

    def _read_dataset(
        self, dataset_path: Path, query: LeadQuery, industry_keywords: List[str]
    ) -> List[Lead]:
        """Stream the Yelp dataset file and extract candidate leads."""
        normalized_industry = query.industry.lower()
        location_terms = {
            term.strip().lower()
            for term in re.split(r"[,/]", query.location)
            if term.strip()
        }
        print(f"DEBUG: Yelp search - industry: '{normalized_industry}', location terms: {location_terms}")
        results: List[Lead] = []
        checked = 0
        matched_industry = 0
        matched_location = 0
        target_leads = query.limit * 3  # We want 3x the limit to have options after filtering
        
        try:
            with dataset_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    checked += 1
                    # Early termination if we have enough leads
                    if len(results) >= target_leads:
                        print(f"DEBUG: Yelp found {len(results)} leads (target: {target_leads}), stopping early")
                        break
                    
                    if checked % 50000 == 0:
                        print(f"DEBUG: Yelp checked {checked} businesses, found {len(results)} leads so far")
                    
                    if not line.strip():
                        continue
                    
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Fast category check - use LLM-generated keywords for flexible matching
                    categories_str = (payload.get("categories") or "").lower()
                    if categories_str:
                        # Check if any industry keyword appears in any category word
                        category_words = [cat.strip() for cat in categories_str.split(",") if cat.strip()]
                        industry_match = False
                        for cat_word in category_words:
                            # Check if any keyword matches this category word
                            for keyword in industry_keywords:
                                if (keyword in cat_word or 
                                    cat_word.startswith(keyword) or
                                    keyword.startswith(cat_word[:len(keyword)])):
                                    industry_match = True
                                    break
                            if industry_match:
                                break
                        if not industry_match:
                            continue
                    matched_industry += 1

                    # Location matching - optimized to check city first (most common match)
                    city = (payload.get("city") or "").strip().lower()
                    state = (payload.get("state") or "").strip().lower()
                    postal_code = (payload.get("postal_code") or "").strip().lower()
                    
                    # Match if any location term appears in city, state, postal_code, or combined
                    location_match = False
                    if location_terms:
                        # Check city first (most common match case)
                        for term in location_terms:
                            if term in city:
                                location_match = True
                                break
                        # If city didn't match, check other fields
                        if not location_match:
                            for term in location_terms:
                                if (term in state or 
                                    term in postal_code or
                                    term in f"{city} {state}"):
                                    location_match = True
                                    break
                    else:
                        location_match = True  # If no location specified, match all
                    
                    if location_match:
                        matched_location += 1
                        name = payload.get("name")
                        if not name:
                            continue
                        website = payload.get("website") or payload.get("url")
                        domain = normalize_domain(website) or generate_placeholder_domain(
                            name, self.name
                        )
                        lead = Lead(
                            name=name,
                            domain=domain,
                            location=", ".join(
                                filter(
                                    None,
                                    [
                                        payload.get("address"),
                                        payload.get("city"),
                                        payload.get("state"),
                                        payload.get("postal_code"),
                                    ],
                                )
                            )
                            or query.location,
                            industry=query.industry,
                            phone=payload.get("phone"),
                            source=self.name,
                            yelp_url=payload.get("url"),
                        )
                        lead.metadata["yelp_business_id"] = payload.get("business_id")
                        lead.metadata["rating"] = payload.get("stars")
                        lead.metadata["review_count"] = payload.get("review_count")
                        results.append(lead)
                        if len(results) >= query.limit * 3:
                            break
        except OSError as exc:
            logger.error("Failed to read Yelp dataset at %s: %s", dataset_path, exc)
        
        print(f"DEBUG: Yelp checked {checked} businesses, matched {matched_industry} industry, {matched_location} location, returning {len(results)} leads")

        return results


class WebDirectoryScraperConnector(LeadSourceConnector):
    """Scrape public business directories to discover leads."""

    name = "web_directories"

    async def fetch(
        self, query: LeadQuery, context: LeadPipelineContext
    ) -> List[Lead]:
        leads: List[Lead] = []
        seen_domains: Set[str] = set()

        # Only use the most reliable sources to avoid hanging
        all_sources = [
            "https://www.dexknows.com/search?what={industry}&where={location}",
        ]

        for template in all_sources:
            try:
                url = template.format(
                    industry=query.industry.replace(" ", "+"),
                    location=query.location.replace(" ", "+"),
                )

                html = await self._fetch_html(url, context)
                print(f"DEBUG: Fetched {len(html) if html else 0} chars from {url}")
                if not html or len(html) < 1000:  # Skip if too small (likely error page)
                    print(f"DEBUG: Skipping {url} - too small or no HTML")
                    continue

                directory_domain = urlparse(url).netloc
                extracted = self._parse_directory_listings(
                    html, query, template, directory_domain
                )

                if extracted:
                    print(f"DEBUG: {urlparse(template).netloc} yielded {len(extracted)} leads")

                for lead in extracted:
                    if lead.domain in seen_domains:
                        continue
                    seen_domains.add(lead.domain)
                    leads.append(lead)
                    if len(leads) >= query.limit:
                        return leads
            except Exception as e:
                # Continue to next source if one fails
                continue

        return leads

    async def _fetch_html(
        self, url: str, context: LeadPipelineContext
    ) -> Optional[str]:
        try:
            # Try Playwright first with very aggressive timeout
            if context.settings.use_playwright:
                try:
                    html = await asyncio.wait_for(
                        fetch_with_playwright(url, min(context.settings.playwright_timeout, 8.0)),
                        timeout=10.0  # 10 second total timeout for Playwright
                    )
                    if html and not any(indicator in html.lower() for indicator in ['captcha', 'cloudflare', 'blocked', 'access denied']):
                        return html
                except asyncio.TimeoutError:
                    logger.debug("Playwright timeout for %s", url)
                    pass

            # Fallback to ScraperAPI/Outscraper with timeout
            try:
                outscraper_key = os.environ.get('OUTSCRAPER_API_KEY')
                if context.settings.SCRAPERAPI_API_KEY or outscraper_key:
                    html = await asyncio.wait_for(
                        fetch_with_scraperapi(
                            url,
                            context.settings.SCRAPERAPI_API_KEY,
                            outscraper_key
                        ),
                        timeout=15.0  # 15 second timeout for ScraperAPI
                    )
                    if html:
                        return html
            except asyncio.TimeoutError:
                logger.debug("ScraperAPI timeout for %s", url)
                pass

            # Final fallback to HTTP with timeout
            try:
                result = await asyncio.wait_for(
                    context.http.get(
                        url,
                        cache_key=f"scrape:{url}",
                        cache_ttl=60 * 60 * 3,
                        use_cache=True,
                    ),
                    timeout=8.0  # 8 second timeout for HTTP
                )
                return result.text or ""
            except asyncio.TimeoutError:
                logger.debug("HTTP timeout for %s", url)
                return None

        except Exception as exc:
            logger.debug("Directory scrape failed for %s: %s", url, exc)
            return None

    def _parse_directory_listings(
        self,
        html: str,
        query: LeadQuery,
        template: str,
        directory_domain: str,
    ) -> List[Lead]:
        soup = BeautifulSoup(html, "lxml")
        results: List[Lead] = []

        # Skip error pages and irrelevant content
        if "cloudflare" in html.lower() or "403" in html or "blocked" in html.lower() or "access denied" in html.lower():
            return results

        # Look for structured business listings (common patterns)
        business_selectors = [
            ".business-listing", ".listing", ".result-item", ".business-card",
            ".company-info", ".business-info", "[data-business]", "[data-listing]",
            ".search-result", ".local-result", ".result", ".business",
            ".listing-item", ".company-listing", ".local-business",
            "[class*='result']", "[class*='listing']", "[class*='business']"
        ]

        business_containers = []
        for selector in business_selectors:
            business_containers.extend(soup.select(selector))

        # If no structured listings found, fall back to link analysis but be more selective
        if not business_containers:
            business_containers = [soup]  # Use whole page

        # Collect all potential business links
        potential_links = []
        all_found_links = []

        for container in business_containers:
            for anchor in container.find_all("a", href=True):
                href = anchor["href"]
                domain = normalize_domain(href)
                if not domain or domain == directory_domain:
                    continue

                # Skip obviously non-business domains
                skip_domains = {"facebook.com", "twitter.com", "instagram.com",
                              "youtube.com", "linkedin.com", "google.com",
                              "maps.google.com", "cloudflare.com", "yelp.com"}
                if any(skip_domain in domain for skip_domain in skip_domains):
                    continue

                text = anchor.get_text(strip=True)
                if not text or len(text) < 3:
                    # Look for nearby heading or business name
                    heading = anchor.find_previous(["h1", "h2", "h3", "h4", "h5"])
                    if heading:
                        text = heading.get_text(strip=True)

                all_found_links.append(text)

                # Skip generic navigation links
                if not text or any(
                    token in text.lower()
                    for token in ("website", "directions", "menu", "learn more",
                                "view map", "get directions", "call now", "visit site",
                                "contact", "about", "home", "services", "privacy", "terms")
                ):
                    continue

                # Must be reasonable length
                if len(text) < 3 or len(text) > 120:
                    continue

                potential_links.append((text, domain, href))

        # Debug: show what links were found
        if all_found_links:
            print(f"DEBUG: Found {len(all_found_links)} total links, {len(potential_links)} after filtering")
            print(f"DEBUG: Sample links: {all_found_links[:5]}")

        # Score and filter links
        scored_links = []
        industry_keywords = {
            'dentists': ['dental', 'dentist', 'orthodontist', 'teeth', 'smile', 'clinic', 'dds', 'dmd'],
            'plumbers': ['plumbing', 'plumber', 'leak', 'drain', 'pipe', 'heating'],
            'lawyers': ['law', 'attorney', 'legal', 'firm', 'esq'],
            'restaurants': ['restaurant', 'cafe', 'diner', 'food', 'eatery', 'bistro'],
            'hvac': ['heating', 'cooling', 'air', 'hvac', 'furnace', 'ac'],
        }

        query_industry = query.industry.lower()
        relevant_keywords = industry_keywords.get(query_industry, [query_industry])

        for text, domain, href in potential_links:
            score = 0

            # Keyword matches
            if any(keyword in text.lower() for keyword in relevant_keywords):
                score += 3

            # Business-like formatting
            if text.istitle() or any(word[0].isupper() for word in text.split() if word):
                score += 2

            # Contains numbers (addresses, phone fragments)
            if any(char.isdigit() for char in text):
                score += 1

            # Reasonable business name patterns
            if any(word in text.lower() for word in ['inc', 'llc', 'corp', 'co', 'ltd', 'clinic', 'center', 'group']):
                score += 2

            # Debug output for first few links
            if len(scored_links) < 3:
                print(f"DEBUG: Link '{text}' -> score: {score}")

            scored_links.append((score, text, domain, href))

        # Sort by score and take top candidates
        scored_links.sort(reverse=True, key=lambda x: x[0])

        for score, text, domain, href in scored_links[:20]:  # Take top 20 candidates
            if score >= 1:  # Lower threshold for batch processing
                lead = Lead(
                    name=text[:120],
                    domain=domain,
                    location=query.location,
                    industry=query.industry,
                    source=f"directory:{urlparse(template).netloc}",
                    metadata={"listing_url": href, "confidence_score": score},
                )
                results.append(lead)

        return results


class ApolloPeopleSearchConnector(LeadSourceConnector):
    """Search for people using Apollo.io People Search API as a lead source."""

    name = "apollo_people_search"
    SEARCH_URL = "https://api.apollo.io/api/v1/mixed_people/search"

    def is_configured(self, settings: LeadPipelineSettings) -> bool:
        return bool(settings.APOLLOIO_API_KEY)

    async def fetch(
        self, query: LeadQuery, context: LeadPipelineContext
    ) -> List[Lead]:
        """Fetch leads using Apollo.io People Search API."""
        if not self.is_configured(context.settings):
            return []

        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": context.settings.APOLLOIO_API_KEY,
        }

        # Build search payload based on industry and location
        # Apollo People Search supports various filters
        payload = {
            "page": 1,
            "per_page": min(query.limit * 3, 100),  # Get more to account for filtering - increased multiplier
            "organization_locations": [query.location],
            "q_keywords": query.industry,  # Search using keywords for the industry
            "person_titles": [],  # Could be enhanced to filter by titles
        }

        # For broader search, don't restrict by specific titles - let Apollo find relevant people
        # The industry keyword search should be sufficient
        # industry_titles = self._get_industry_titles(query.industry)
        # if industry_titles:
        #     payload["person_titles"] = industry_titles[:10]  # Commented out for broader search

        cache_key = f"{self.name}:{query.industry}:{query.location}"
        try:
            result = await context.http.post(
                self.SEARCH_URL,
                json_payload=payload,
                headers=headers,
                cache_key=cache_key,
                cache_ttl=60 * 60 * 6,  # Cache for 6 hours
            )
        except RuntimeError as e:
            logger.warning(f"Apollo People Search API request failed: {e}")
            return []

        response_data = result.json or {}

        if result.status_code != 200:
            logger.warning(f"Apollo People Search returned status {result.status_code}: {response_data}")
            return []

        people = response_data.get("people", [])
        logger.info(f"Apollo People Search returned {len(people)} people for {query.industry} in {query.location}")

        leads = []
        seen_domains = set()
        filtered_out = {"missing_both": 0, "duplicate_domain": 0}

        for person in people[:query.limit]:
            # Extract person details
            name = person.get("name", "")
            email = person.get("email", "")
            linkedin_url = person.get("linkedin_url", "")
            title = person.get("title", "")

            # Extract organization details
            organization = person.get("organization", {})
            org_name = organization.get("name", "")
            org_domain = organization.get("website_url", "")
            org_location = organization.get("location", "")

            if org_domain:
                org_domain = normalize_domain(org_domain)

            # Create lead if we have at least a name or domain
            if not org_name and not org_domain:
                filtered_out["missing_both"] += 1
                continue

            # Generate placeholder domain if missing
            if not org_domain and org_name:
                org_domain = generate_placeholder_domain(org_name, self.name)

            # Skip if we already have a lead from this domain
            if org_domain and org_domain in seen_domains:
                filtered_out["duplicate_domain"] += 1
                continue

            # Create lead from organization data (more permissive)
            lead = Lead(
                name=org_name or f"Contact at {org_domain}",  # Fallback name
                domain=org_domain,
                location=org_location or query.location,
                industry=query.industry,
                source=self.name,
                email=email,  # Primary contact email if available
                linkedin_url=linkedin_url,
            )

            # Add person metadata
            lead.metadata["apollo_person"] = {
                "name": name,
                "title": title,
                "email": email,
                "linkedin_url": linkedin_url,
            }

            leads.append(lead)
            if org_domain:
                seen_domains.add(org_domain)

            if len(leads) >= query.limit:
                break

        logger.info(f"Apollo People Search generated {len(leads)} leads")
        return leads

    def _get_industry_titles(self, industry: str) -> List[str]:
        """Return relevant job titles for an industry to improve search results."""
        industry = industry.lower().strip()

        title_mapping = {
            "dentist": ["dentist", "dds", "dmd", "orthodontist", "periodontist", "endodontist", "oral surgeon"],
            "plumber": ["plumber", "owner", "president", "manager", "ceo", "founder"],
            "lawyer": ["attorney", "lawyer", "partner", "esq", "counsel", "associate"],
            "hvac": ["owner", "president", "ceo", "founder", "manager", "technician"],
            "restaurant": ["owner", "chef", "manager", "president", "ceo"],
            "real estate": ["realtor", "agent", "broker", "owner", "manager"],
            "construction": ["owner", "president", "ceo", "founder", "manager", "contractor"],
        }

        return title_mapping.get(industry, ["owner", "president", "ceo", "founder", "manager"])


class ApolloEnricher(LeadSourceConnector, LeadEnricher):
    """Enrichment via Apollo.io company lookup, can also be used as lead source."""

    name = "apollo"
    SEARCH_URL = "https://api.apollo.io/v1/organizations/search"

    def is_configured(self, settings: LeadPipelineSettings) -> bool:
        return bool(settings.APOLLOIO_API_KEY)

    async def fetch(
        self, query: LeadQuery, context: LeadPipelineContext
    ) -> List[Lead]:
        """Fetch leads using Apollo.io organization search as a lead source."""
        if not self.is_configured(context.settings):
            return []

        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": context.settings.APOLLOIO_API_KEY,
        }
        payload = {
            "q_organization_name": query.industry,
            "organization_locations": [query.location],
            "page": 1,
            "per_page": min(query.limit, 10),  # Apollo has limits
        }

        cache_key = f"{self.name}:source:{query.industry}:{query.location}"
        try:
            result = await context.http.post(
                self.SEARCH_URL,
                json_payload=payload,
                headers=headers,
                cache_key=cache_key,
                cache_ttl=60 * 60 * 6,
            )
        except RuntimeError as e:
            print(f"WARNING: Apollo.io API request failed: {e}")
            return []

        response_data = result.json or {}
        
        # Debug: check what Apollo returned
        if result.status_code != 200:
            print(f"WARNING: Apollo.io returned status {result.status_code}: {response_data}")
        
        organizations = response_data.get("organizations", [])
        print(f"DEBUG: Apollo.io returned {len(organizations)} organizations")
        
        leads = []

        for org in organizations[:query.limit]:
            name = org.get("name", "")
            domain = org.get("website_url", "")
            if domain:
                domain = normalize_domain(domain)
            if name and domain:
                lead = Lead(
                    name=name,
                    domain=domain,
                    industry=query.industry,
                    location=query.location,
                    source=self.name,
                )
                leads.append(lead)
            else:
                print(f"DEBUG: Skipping org '{name}' - domain: {org.get('website_url', 'N/A')}")

        return leads

    async def enrich(
        self, lead: Lead, context: LeadPipelineContext
    ) -> Lead:
        if not self.is_configured(context.settings):
            return lead
        if not lead.domain or ".placeholder" in lead.domain:
            return lead

        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": context.settings.APOLLOIO_API_KEY,
        }
        payload = {
            "q_organization_domains": [lead.domain],
            "page": 1,
            "per_page": 1,
        }
        try:
            result = await context.http.post(
                self.SEARCH_URL,
                json_payload=payload,
                headers=headers,
                cache_key=f"{self.name}:{lead.domain}",
                cache_ttl=60 * 60 * 6,
                use_cache=True,
            )
        except RuntimeError:
            return lead

        companies = (result.json or {}).get("organizations", [])
        if not companies:
            return lead

        company = companies[0]
        lead.metadata.setdefault("enrichment", {})["apollo"] = company
        if not lead.industry and company.get("industry"):
            lead.industry = company["industry"]
        if not lead.phone and company.get("phone"):
            lead.phone = company["phone"]
        if not lead.location and company.get("city"):
            lead.location = ", ".join(
                filter(None, [company.get("city"), company.get("state")])
            )
        return lead


class WebsiteEmailCrawler(LeadEnricher):
    """Scrape company websites for fallback email discovery."""

    name = "website_email_crawler"

    async def enrich(
        self, lead: Lead, context: LeadPipelineContext
    ) -> Lead:
        if not lead.domain or lead.emails:
            return lead

        base_url = f"https://{lead.domain}"
        seen: Set[str] = set()
        for path in SCRAPE_PATHS:
            target = urljoin(base_url, path)
            cache_key = f"crawler:{lead.domain}:{path}"
            try:
                result = await context.http.get(
                    target,
                    cache_key=cache_key,
                    cache_ttl=60 * 60 * 6,
                )
            except RuntimeError:
                continue

            html = result.text or ""
            if not html:
                continue

            emails = extract_emails_from_html(html)
            for email in emails:
                if email not in seen:
                    seen.add(email)
                    lead.add_email(email)

            if context.settings.use_playwright and not emails:
                await self._playwright_scrape(target, lead, context)

        return lead

    async def _playwright_scrape(
        self, url: str, lead: Lead, context: LeadPipelineContext
    ) -> None:
        content = await fetch_with_playwright(
            url, context.settings.playwright_timeout
        )
        if not content:
            return

        emails = extract_emails_from_html(content)
        for email in emails:
            lead.add_email(email)


class LeadScorer:
    """Score leads based on completeness, contactability, and relevance."""

    def score(self, leads: Sequence[Lead], query: LeadQuery) -> List[Lead]:
        """Assign score/confidence to each lead."""
        results: List[Lead] = []
        for lead in leads:
            score = 0.1  # base prior
            if lead.emails:
                score += 0.45
            elif lead.email:
                score += 0.35
            if lead.phone:
                score += 0.15
            if lead.industry and query.industry.lower() in lead.industry.lower():
                score += 0.1
            if lead.description and query.industry.lower() in lead.description.lower():
                score += 0.05
            if "rating" in lead.metadata:
                try:
                    score += min(float(lead.metadata["rating"]) / 10, 0.05)
                except (TypeError, ValueError):
                    pass
            lead.score = min(score, 1.0)
            lead.confidence = min(1.0, lead.score + 0.1)
            results.append(lead)
        return results


class LeadFilter:
    """Filter and rank leads for export readiness."""

    def __init__(self, min_score: float = DEFAULT_SCORE_THRESHOLD):
        self.min_score = min_score

    def filter(self, leads: Sequence[Lead], limit: int) -> List[Lead]:
        """Return the highest scoring leads within the requested limit."""
        sorted_leads = sorted(leads, key=lambda lead: lead.score, reverse=True)
        filtered = [lead for lead in sorted_leads if lead.score >= self.min_score]
        if not filtered:
            # Fallback – if no leads exceed threshold, return best N.
            filtered = sorted_leads[:limit]
        return filtered[:limit]


class LeadExporter:
    """Persist leads to disk in a deterministic folder structure."""

    def __init__(self, base_dir: Path, exporter_format: str = "json"):
        self.base_dir = base_dir
        self.exporter_format = exporter_format

    def export(self, leads: Sequence[Lead], query: LeadQuery) -> Optional[Path]:
        """Persist leads to disk, returning the resolved filepath."""
        if not leads:
            return None

        industry_dir = self.base_dir / slugify(query.industry)
        location_dir = industry_dir / slugify(query.location.replace(",", ""))
        location_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        filename = f"{timestamp}_{len(leads)}.{self.exporter_format}"
        path = location_dir / filename

        payload = [lead.to_dict() for lead in leads]
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

        return path


class LeadGenerator:
    """Production-grade lead generator orchestrating discovery and enrichment."""

    def __init__(
        self,
        leads_dir: str = "pipeline/leads",
        settings: Optional[LeadPipelineSettings] = None,
    ):
        """Create a new instance of the lead generator."""
        self.settings = settings or LeadPipelineSettings.from_env(
            leads_dir=Path(leads_dir)
        )
        self.leads_dir = self.settings.leads_dir
        self.cache = SQLiteCacheBackend(
            self.settings.cache_path, self.settings.cache_ttl_seconds
        )
        self.seen_hashes: Set[str] = set()
        self.scorer = LeadScorer()
        self.filter = LeadFilter()
        self.exporter = LeadExporter(
            self.settings.leads_dir, exporter_format=self.settings.exporter_format
        )

        # Initialize providers.
        self.sources: Dict[str, LeadSourceConnector] = {
            connector.name: connector
            for connector in [
                YelpOpenDatasetConnector(),
                WebDirectoryScraperConnector(),
                ApolloEnricher(),
                ApolloPeopleSearchConnector(),
            ]
        }
        self.enrichers: Dict[str, LeadEnricher] = {
            enricher.name: enricher
            for enricher in [
                ApolloEnricher(),
                # WebsiteEmailCrawler(),  # Temporarily disabled - causes timeouts
            ]
        }

        self._load_existing_leads()

    def _load_existing_leads(self) -> None:
        """Warm the deduplication cache with previously exported leads."""
        for json_file in self.leads_dir.rglob("*.json"):
            try:
                with json_file.open("r", encoding="utf-8") as handle:
                    contents = json.load(handle)
            except (OSError, json.JSONDecodeError):
                continue

            if isinstance(contents, list):
                for item in contents:
                    try:
                        lead = Lead.from_dict(item)
                    except KeyError:
                        continue
                    self.seen_hashes.add(lead.get_hash())

    async def _run_enrichers(
        self, lead: Lead, context: LeadPipelineContext
    ) -> Lead:
        enriched = lead
        for enricher in self.enrichers.values():
            if not enricher.is_configured(context.settings):
                continue
            try:
                enriched = await enricher.enrich(enriched, context)
            except Exception as exc:  # pragma: no cover - defensive
                logger.debug("Enricher %s failed for %s: %s", enricher.name, lead.domain, exc)
        return enriched

    async def _generate_async(
        self, query: LeadQuery, sources: Sequence[str]
    ) -> List[Lead]:
        """Async orchestration pipeline for lead generation."""
        async with AsyncHTTPClient(self.settings, self.cache) as http:
            context = LeadPipelineContext(self.settings, self.cache, http)
            
            # Log which sources will be used
            active_sources = [
                name for name in sources
                if name in self.sources and self.sources[name].is_configured(self.settings)
            ]
            logger.info("Using lead sources: %s", ", ".join(active_sources))
            
            discovery_tasks = [
                self.sources[name].fetch(query, context)
                for name in active_sources
            ]

            # Execute source discovery concurrently.
            discovery_results = await asyncio.gather(
                *discovery_tasks, return_exceptions=True
            )

            discovered: List[Lead] = []
            for i, result in enumerate(discovery_results):
                source_name = active_sources[i] if i < len(active_sources) else "unknown"
                if isinstance(result, Exception):
                    print(f"WARNING: Lead source '{source_name}' execution error: {result}")
                    logger.warning("Lead source '%s' execution error: %s", source_name, result)
                    continue
                leads_count = len(result) if isinstance(result, list) else 0
                print(f"INFO: Source '{source_name}' returned {leads_count} leads")
                logger.info("Source '%s' returned %d leads", source_name, leads_count)
                discovered.extend(result)

            deduped = self._deduplicate(discovered)
            print(f"DEBUG: After deduplication: {len(deduped)} leads")

            # Enrich leads concurrently.
            enrichment_tasks = [
                self._run_enrichers(lead, context) for lead in deduped
            ]
            enriched_leads = await asyncio.gather(
                *enrichment_tasks, return_exceptions=True
            )

            sanitized: List[Lead] = []
            for item in enriched_leads:
                if isinstance(item, Lead):
                    sanitized.append(item)
                elif isinstance(item, Exception):
                    logger.debug("Lead enrichment error: %s", item)

            scored = self.scorer.score(sanitized, query)
            print(f"DEBUG: Lead scores before filtering:")
            for lead in scored[:10]:  # Show first 10
                print(f"  - {lead.name[:40]:40s} score={lead.score:.2f} email={lead.email or 'none'}")
            filtered = self.filter.filter(scored, limit=query.limit)
            print(f"DEBUG: After scoring: {len(scored)} leads, after filtering: {len(filtered)} leads")
            exported_path = self.exporter.export(filtered, query)
            if exported_path:
                logger.info("Exported %s leads to %s", len(filtered), exported_path)

            for lead in filtered:
                self.seen_hashes.add(lead.get_hash())

            return filtered

    def _deduplicate(self, leads: Iterable[Lead]) -> List[Lead]:
        """Deduplicate incoming leads against history and within the batch."""
        unique: Dict[str, Lead] = {}
        for lead in leads:
            lead_hash = lead.get_hash()
            if lead_hash in self.seen_hashes:
                continue
            if lead_hash in unique:
                unique[lead_hash].merge(lead)
            else:
                unique[lead_hash] = lead
        return list(unique.values())

    def generate_leads(
        self,
        industry: str,
        location: str,
        limit: int = 15,
        sources: Optional[List[str]] = None,
    ) -> List[Lead]:
        """Generate, enrich, and persist leads for the supplied query."""
        if limit <= 0:
            raise ValueError("Limit must be greater than zero.")

        requested_sources = (
            sources if sources else list(self.sources.keys())
        )
        query = LeadQuery(
            industry=industry.strip(),
            location=location.strip(),
            limit=limit,
        )

        leads = asyncio.run(self._generate_async(query, requested_sources))
        return leads

    def _save_leads(self, leads: List[Lead], industry: str, location: str) -> None:
        """Backward-compatible wrapper for legacy callers/tests."""
        query = LeadQuery(industry=industry, location=location, limit=len(leads))
        self.exporter.export(leads, query)
        for lead in leads:
            self.seen_hashes.add(lead.get_hash())


def test_email_extraction() -> None:
    """Test email extraction functionality with sample domains."""
    import asyncio

    # Test domains with known contact pages
    test_domains = [
        "www.southaustindentist.com",  # From the hotfrog results
        "www.dentalclinicofaustin.com",  # Hypothetical but realistic
        "www.austinsmiles.com",  # Hypothetical but realistic
    ]

    async def test_domain(domain: str):
        settings = LeadPipelineSettings.from_env(use_playwright=True)
        cache = SQLiteCacheBackend(settings.cache_path, settings.cache_ttl_seconds)
        http = AsyncHTTPClient(settings, cache)

        async with http:
            context = LeadPipelineContext(settings=settings, cache=cache, http=http)
            crawler = WebsiteEmailCrawler()

            lead = Lead(
                name=f"Test Dental {domain.split('.')[0]}",
                domain=domain,
                industry="dentists",
                location="Austin, TX",
                source="test"
            )

            print(f"Testing email extraction for {domain}...")
            enriched_lead = await crawler.enrich(lead, context)
            print(f"  Found emails: {list(enriched_lead.emails)}")
            print(f"  Primary email: {enriched_lead.email}")
            return enriched_lead

    async def main():
        results = await asyncio.gather(*[test_domain(domain) for domain in test_domains])
        total_emails = sum(len(lead.emails) for lead in results)
        print(f"\nTotal emails found across {len(test_domains)} domains: {total_emails}")

    asyncio.run(main())


def main() -> None:
    """CLI entrypoint for ad-hoc lead generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate business leads")
    parser.add_argument("--industry", help="Target industry")
    parser.add_argument("--location", help="Target location")
    parser.add_argument("--limit", type=int, default=15, help="Number of leads to return")
    parser.add_argument(
        "--sources",
        nargs="+",
        help="Specific sources to query (default: all configured sources)",
    )
    parser.add_argument(
        "--leads-dir",
        default="pipeline/leads",
        help="Directory where lead exports will be written",
    )
    parser.add_argument(
        "--test-emails",
        action="store_true",
        help="Test email extraction functionality instead of generating leads",
    )

    args = parser.parse_args()

    if args.test_emails:
        test_email_extraction()
        return

    if not args.industry or not args.location:
        parser.error("--industry and --location are required unless --test-emails is used")

    generator = LeadGenerator(leads_dir=args.leads_dir)
    leads = generator.generate_leads(
        industry=args.industry,
        location=args.location,
        limit=args.limit,
        sources=args.sources,
    )

    print(f"Generated {len(leads)} leads:")
    for lead in leads:
        email_info = f" email={lead.email}" if lead.email else ""
        print(f"- {lead.name} ({lead.domain}) score={lead.score:.2f}{email_info}")


if __name__ == "__main__":
    main()
