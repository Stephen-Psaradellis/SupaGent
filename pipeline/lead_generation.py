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


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
    google_places_api_key: Optional[str] = Field(
        default=None, alias="GOOGLE_PLACES_API_KEY"
    )
    yelp_dataset_path: Optional[Path] = Field(
        default=None, alias="YELP_OPEN_DATASET_PATH"
    )
    hunter_api_key: Optional[str] = Field(default=None, alias="HUNTER_API_KEY")
    hunter_account_id: Optional[str] = Field(
        default=None, alias="HUNTER_ACCOUNT_ID"
    )
    apollo_api_key: Optional[str] = Field(default=None, alias="APOLLO_API_KEY")
    directory_scrape_targets: List[str] = Field(
        default_factory=lambda: [
            "https://www.yellowpages.com/search?search_terms={industry}&geo_location_terms={location}",
            "https://www.mapquest.com/search/{industry}/{location}",
            "https://www.chamberofcommerce.com/{location}?query={industry}",
            "https://www.localstack.com/find/{location}/{industry}",
            "https://www.manta.com/search?search_source=Business&search={industry}&search_location={location}",
            "https://www.alignable.com/listings/{location}/{industry}",
        ]
    )
    user_agent: str = Field(
        default=(
            "LeadPipelineBot/1.0 (+https://supagent.ai; contact: leads@supagent.ai)"
        )
    )
    use_playwright: bool = Field(default=False)
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
            "google_places_api_key": "GOOGLE_PLACES_API_KEY",
            "yelp_dataset_path": "YELP_OPEN_DATASET_PATH",
            "hunter_api_key": "HUNTER_API_KEY",
            "hunter_account_id": "HUNTER_ACCOUNT_ID",
            "apollo_api_key": "APOLLO_API_KEY",
            "directory_scrape_targets": "LEAD_PIPELINE_DIRECTORY_SCRAPE_TARGETS",
            "user_agent": "LEAD_PIPELINE_USER_AGENT",
            "use_playwright": "LEAD_PIPELINE_USE_PLAYWRIGHT",
            "playwright_timeout": "LEAD_PIPELINE_PLAYWRIGHT_TIMEOUT",
            "exporter_format": "LEAD_PIPELINE_EXPORTER_FORMAT",
        }

    @classmethod
    def from_env(cls, **overrides: Any) -> LeadPipelineSettings:
        """Instantiate settings from environment variables with overrides."""
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


async def fetch_with_playwright(url: str, timeout: float) -> Optional[str]:
    """Fetch fully rendered HTML using Playwright when installed."""
    try:
        from playwright.async_api import async_playwright  # type: ignore
    except ImportError:
        logger.debug("Playwright not installed; skipping JS-rendered fetch for %s", url)
        return None

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=int(timeout * 1000))
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


class GooglePlacesConnector(LeadSourceConnector):
    """Lead source leveraging the Google Places API."""

    name = "google_places"
    SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

    def is_configured(self, settings: LeadPipelineSettings) -> bool:
        return bool(settings.google_places_api_key)

    async def fetch(
        self, query: LeadQuery, context: LeadPipelineContext
    ) -> List[Lead]:
        if not self.is_configured(context.settings):
            logger.info("Skipping Google Places – missing API key.")
            return []

        params = {
            "query": f"{query.industry} in {query.location}",
            "key": context.settings.google_places_api_key,
        }
        result = await context.http.get(
            self.SEARCH_URL,
            params=params,
            cache_key=f"{self.name}:{params['query']}",
            cache_ttl=60 * 60 * 24,
        )
        payload = result.json or {}
        candidates = payload.get("results", [])
        leads: List[Lead] = []

        # Fetch additional details concurrently for richer data.
        tasks = [
            self._build_lead(
                summary=item,
                query=query,
                context=context,
            )
            for item in candidates[: query.limit * 2]
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for item in results:
            if isinstance(item, Lead):
                leads.append(item)
            elif isinstance(item, Exception):
                logger.debug("Google Places details failed: %s", item)

        return leads[: query.limit]

    async def _build_lead(
        self,
        summary: Dict[str, Any],
        query: LeadQuery,
        context: LeadPipelineContext,
    ) -> Optional[Lead]:
        place_id = summary.get("place_id")
        if not place_id:
            return None

        params = {
            "place_id": place_id,
            "fields": "name,website,formatted_address,formatted_phone_number,url,business_status,types",
            "key": context.settings.google_places_api_key,
        }
        details = await context.http.get(
            self.DETAILS_URL,
            params=params,
            cache_key=f"{self.name}:details:{place_id}",
            cache_ttl=60 * 60 * 24 * 7,
        )
        result = (details.json or {}).get("result", {})
        name = result.get("name") or summary.get("name")
        if not name:
            return None

        website = result.get("website")
        domain = normalize_domain(website)
        if not domain:
            domain = generate_placeholder_domain(name, self.name)

        lead = Lead(
            name=name,
            domain=domain,
            location=result.get("formatted_address") or summary.get("formatted_address"),
            phone=result.get("formatted_phone_number"),
            industry=query.industry,
            source=self.name,
            google_maps_url=result.get("url"),
        )
        lead.metadata["google_place_id"] = place_id
        lead.metadata["business_status"] = result.get("business_status")
        lead.metadata["types"] = summary.get("types")
        return lead


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

        leads = await asyncio.to_thread(
            self._read_dataset, context.settings.yelp_dataset_path, query
        )
        return leads[: query.limit]

    def _read_dataset(
        self, dataset_path: Path, query: LeadQuery
    ) -> List[Lead]:
        """Stream the Yelp dataset file and extract candidate leads."""
        normalized_industry = query.industry.lower()
        location_terms = {
            term.strip().lower()
            for term in re.split(r"[,/]", query.location)
            if term.strip()
        }
        results: List[Lead] = []
        try:
            with dataset_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    categories = [
                        (cat or "").strip().lower()
                        for cat in (payload.get("categories") or "").split(",")
                    ]
                    if categories and all(
                        normalized_industry not in cat for cat in categories
                    ):
                        continue

                    city = (payload.get("city") or "").lower()
                    state = (payload.get("state") or "").lower()
                    postal_code = (payload.get("postal_code") or "").lower()
                    location_match = any(
                        term in value
                        for term in location_terms
                        for value in (city, state, postal_code)
                        if value
                    )
                    if not location_terms or location_match:
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

        return results


class WebDirectoryScraperConnector(LeadSourceConnector):
    """Scrape public business directories to discover leads."""

    name = "web_directories"

    async def fetch(
        self, query: LeadQuery, context: LeadPipelineContext
    ) -> List[Lead]:
        leads: List[Lead] = []
        seen_domains: Set[str] = set()
        for template in context.settings.directory_scrape_targets:
            url = template.format(
                industry=query.industry.replace(" ", "+"),
                location=query.location.replace(" ", "+"),
            )
            html = await self._fetch_html(url, context)
            if not html:
                continue
            directory_domain = urlparse(url).netloc
            extracted = self._parse_directory_listings(
                html, query, template, directory_domain
            )
            for lead in extracted:
                if lead.domain in seen_domains:
                    continue
                seen_domains.add(lead.domain)
                leads.append(lead)
                if len(leads) >= query.limit:
                    return leads
        return leads

    async def _fetch_html(
        self, url: str, context: LeadPipelineContext
    ) -> Optional[str]:
        if context.settings.use_playwright:
            html = await fetch_with_playwright(url, context.settings.playwright_timeout)
            if html:
                return html

        try:
            result = await context.http.get(
                url,
                cache_key=f"scrape:{url}",
                cache_ttl=60 * 60 * 3,
                use_cache=True,
            )
            return result.text or ""
        except RuntimeError as exc:
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
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            domain = normalize_domain(href)
            if not domain or domain == directory_domain:
                continue

            text = anchor.get_text(strip=True)
            if not text or len(text) < 3:
                heading = anchor.find_previous(["h1", "h2", "h3", "h4"])
                text = heading.get_text(strip=True) if heading else ""
            if not text or any(
                token in text.lower()
                for token in ("website", "directions", "menu", "learn more")
            ):
                heading = anchor.find_previous(["h1", "h2", "h3", "h4"])
                text = heading.get_text(strip=True) if heading else text
            if not text:
                continue

            lead = Lead(
                name=text[:120],
                domain=domain,
                location=query.location,
                industry=query.industry,
                source=f"directory:{urlparse(template).netloc}",
                metadata={"listing_url": href},
            )
            results.append(lead)
        return results


class HunterEmailEnricher(LeadEnricher):
    """Email enrichment using Hunter.io domain search."""

    name = "hunter"
    SEARCH_URL = "https://api.hunter.io/v2/domain-search"

    def is_configured(self, settings: LeadPipelineSettings) -> bool:
        return bool(settings.hunter_api_key)

    async def enrich(
        self, lead: Lead, context: LeadPipelineContext
    ) -> Lead:
        if not self.is_configured(context.settings):
            return lead
        if not lead.domain or ".placeholder" in lead.domain:
            return lead

        params = {"domain": lead.domain, "api_key": context.settings.hunter_api_key}
        cache_key = f"{self.name}:{lead.domain}"
        try:
            result = await context.http.get(
                self.SEARCH_URL,
                params=params,
                cache_key=cache_key,
                cache_ttl=60 * 60 * 12,
            )
        except RuntimeError:
            return lead

        payload = result.json or {}
        emails = payload.get("data", {}).get("emails", [])
        for email in emails:
            value = email.get("value")
            if value:
                lead.add_email(value)
        lead.metadata.setdefault("enrichment", {})["hunter"] = emails
        return lead


class ApolloEnricher(LeadEnricher):
    """Enrichment via Apollo.io company lookup."""

    name = "apollo"
    SEARCH_URL = "https://api.apollo.io/v1/organizations/search"

    def is_configured(self, settings: LeadPipelineSettings) -> bool:
        return bool(settings.apollo_api_key)

    async def enrich(
        self, lead: Lead, context: LeadPipelineContext
    ) -> Lead:
        if not self.is_configured(context.settings):
            return lead
        if not lead.domain or ".placeholder" in lead.domain:
            return lead

        headers = {"Content-Type": "application/json"}
        payload = {
            "api_key": context.settings.apollo_api_key,
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
                GooglePlacesConnector(),
                YelpOpenDatasetConnector(),
                WebDirectoryScraperConnector(),
            ]
        }
        self.enrichers: Dict[str, LeadEnricher] = {
            enricher.name: enricher
            for enricher in [
                HunterEmailEnricher(),
                ApolloEnricher(),
                WebsiteEmailCrawler(),
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
            discovery_tasks = [
                self.sources[name].fetch(query, context)
                for name in sources
                if name in self.sources and self.sources[name].is_configured(self.settings)
            ]

            # Execute source discovery concurrently.
            discovery_results = await asyncio.gather(
                *discovery_tasks, return_exceptions=True
            )

            discovered: List[Lead] = []
            for result in discovery_results:
                if isinstance(result, Exception):
                    logger.debug("Lead source execution error: %s", result)
                    continue
                discovered.extend(result)

            deduped = self._deduplicate(discovered)

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
            filtered = self.filter.filter(scored, limit=query.limit)
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


def main() -> None:
    """CLI entrypoint for ad-hoc lead generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate business leads")
    parser.add_argument("--industry", required=True, help="Target industry")
    parser.add_argument("--location", required=True, help="Target location")
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

    args = parser.parse_args()
    generator = LeadGenerator(leads_dir=args.leads_dir)
    leads = generator.generate_leads(
        industry=args.industry,
        location=args.location,
        limit=args.limit,
        sources=args.sources,
    )

    print(f"Generated {len(leads)} leads:")
    for lead in leads:
        print(f"- {lead.name} ({lead.domain}) score={lead.score:.2f}")


if __name__ == "__main__":
    main()
