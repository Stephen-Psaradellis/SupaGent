"""
Business Intelligence Loader for Growth Automation Pipeline.

Scrapes and enriches company data from websites, social media, and other sources.
Vectorizes content into per-business knowledge bases for personalized voice agents.

Features:
- Multi-page website scraping with sitemap discovery
- Content extraction (About, Services, Team, Blog)
- Vector store isolation per business (kb:{domain} namespace)
- Metadata enrichment and deduplication
- Rate limiting and error handling
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

from memory.vector_store import VectorStore
from pipeline.lead_generation import Lead, slugify

# Database imports
from core.database import get_db_session
from core.models import BusinessDomain, ScrapedContent as ScrapedContentModel, IntelligenceBundle, HunterEnrichment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Text chunking configuration
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120


@dataclass
class ScrapedContent:
    """Scraped content from a business website."""

    url: str
    title: str
    content: str
    content_type: str  # 'about', 'services', 'team', 'blog', 'general'
    metadata: Dict[str, str]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "content_type": self.content_type,
            "metadata": self.metadata,
        }


class HunterClient:
    """Simple Hunter.io client for domain and contact enrichment."""

    BASE_URL = "https://api.hunter.io/v2"

    def __init__(self, api_key: str, session: Optional[requests.Session] = None):
        """Initialize the Hunter.io client.

        Args:
            api_key: Hunter.io API key.
            session: Optional shared requests session.
        """
        self.api_key = api_key
        self.session = session or requests.Session()

    def is_configured(self) -> bool:
        """Return True when the client has a usable API key."""
        return bool(self.api_key)

    def domain_search(self, domain: str, limit: int = 10) -> Dict[str, Any]:
        """Return Hunter.io domain enrichment results.

        Args:
            domain: Domain name to enrich.
            limit: Maximum number of email records to return.

        Returns:
            Parsed JSON payload with organization and email data.
        """
        params = {"domain": domain, "limit": limit}
        return self._get("domain-search", params)

    def email_finder(
        self,
        domain: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Attempt to locate a direct contact email.

        Args:
            domain: Lead domain.
            first_name: Lead first name.
            last_name: Lead last name.
            company: Company or organization name.

        Returns:
            Parsed JSON result with email discovery metadata.
        """
        params = {"domain": domain}
        if first_name:
            params["first_name"] = first_name
        if last_name:
            params["last_name"] = last_name
        if company:
            params["company"] = company
        return self._get("email-finder", params)

    def _get(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a GET request against the Hunter.io API."""
        if not self.api_key:
            return {}

        payload = params.copy()
        payload["api_key"] = self.api_key

        try:
            response = self.session.get(
                f"{self.BASE_URL}/{endpoint}",
                params=payload,
                timeout=12,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data") or {}
        except requests.RequestException as exc:
            logger.debug("Hunter.io request failed (%s): %s", endpoint, exc)
            return {}
        except json.JSONDecodeError as exc:
            logger.debug("Hunter.io response parsing failed (%s): %s", endpoint, exc)
            return {}


class BusinessIntelligenceLoader:
    """Scrapes and vectorizes business website content."""

    def __init__(self, data_dir: str = "pipeline/business_data"):
        """Initialize business intelligence loader.

        Args:
            data_dir: Directory to store scraped business data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.hunter_client = HunterClient(os.getenv("HUNTERIO_API_KEY", ""), self.session)

        # Initialize text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def load_business_data(self, domain: str, max_pages: int = 50) -> Dict[str, List[ScrapedContent]]:
        """Load and scrape business data for a given domain.

        Args:
            domain: Business domain (e.g., 'example.com')
            max_pages: Maximum pages to scrape

        Returns:
            Dictionary of content types to scraped content
        """
        logger.info(f"🔍 Loading business intelligence for {domain}")

        # Try database first, fallback to file storage
        try:
            with get_db_session() as session:
                # Check if domain exists
                business_domain = session.query(BusinessDomain).filter_by(domain=domain).first()

                scraped_rows: List[ScrapedContentModel] = []
                if business_domain:
                    # The schema uses an explicit FK column (`domain_id`); query via that column to
                    # stay aligned with the ORM mappings rather than relying on implicit lazy relationships.
                    scraped_rows = (
                        session.query(ScrapedContentModel)
                        .filter_by(domain_id=business_domain.id)
                        .order_by(ScrapedContentModel.id)
                        .all()
                    )

                if scraped_rows:
                    logger.info(f"📁 Loading cached content for {domain} from database")
                    categorized_content = {}
                    for scraped in scraped_rows:
                        content_type = scraped.content_type
                        categorized_content.setdefault(content_type, [])
                        scraped_obj = ScrapedContent(
                            url=scraped.url,
                            title=scraped.title,
                            content=scraped.content,
                            content_type=scraped.content_type,
                            metadata=scraped.metadata_json or {},
                        )
                        categorized_content[content_type].append(scraped_obj)

                    return categorized_content

                # Scrape fresh content
                content = self._scrape_website(f"https://{domain}", max_pages)

                # Categorize content
                categorized_content = self._categorize_content(content)

                if not business_domain:
                    business_domain = BusinessDomain(domain=domain)
                    session.add(business_domain)
                    session.flush()  # Get the ID

                # Save scraped content
                for content_type, items in categorized_content.items():
                    for item in items:
                        scraped_db = ScrapedContentModel(
                            domain_id=business_domain.id,
                            url=item.url,
                            title=item.title,
                            content=item.content,
                            content_type=item.content_type,
                            metadata_json=item.metadata,
                            scraped_at=datetime.fromtimestamp(item.metadata.get("scraped_at", time.time())),
                        )
                        session.add(scraped_db)

                logger.info(
                    f"💾 Saved {sum(len(items) for items in categorized_content.values())} pages for {domain} to database"
                )
                return categorized_content

        except Exception as exc:
            logger.warning(f"Database not available, falling back to file storage: {exc}")
            return self._load_business_data_fallback(domain, max_pages)

    def _scrape_website(self, base_url: str, max_pages: int) -> List[ScrapedContent]:
        """Scrape website content with intelligent crawling.

        Args:
            base_url: Base URL to start crawling from
            max_pages: Maximum pages to scrape

        Returns:
            List of scraped content
        """
        content = []
        visited = set()
        queue = [base_url]
        domain = urlparse(base_url).netloc

        # Check robots.txt
        robots_url = f"https://{domain}/robots.txt"
        rp = RobotFileParser()
        try:
            rp.set_url(robots_url)
            rp.read()
        except:
            pass  # Continue without robots.txt

        # Try to get sitemap
        sitemap_urls = self._discover_sitemap_urls(base_url)
        if sitemap_urls:
            queue.extend(sitemap_urls[:max_pages//2])  # Reserve half for crawling

        pages_scraped = 0

        while queue and pages_scraped < max_pages:
            url = queue.pop(0)

            if url in visited:
                continue

            visited.add(url)

            # Check robots.txt
            if not rp.can_fetch("*", url):
                logger.debug(f"🤖 Robots.txt disallows: {url}")
                continue

            try:
                logger.debug(f"📄 Scraping: {url}")
                response = self.session.get(url, timeout=10)

                if response.status_code != 200:
                    continue

                if 'text/html' not in response.headers.get('content-type', ''):
                    continue

                # Extract content
                title, text = self._extract_content(response.text)
                if len(text.strip()) < 200:  # Skip very short pages
                    continue

                scraped = ScrapedContent(
                    url=url,
                    title=title,
                    content=text,
                    content_type="general",  # Will be categorized later
                    metadata={
                        "domain": domain,
                        "scraped_at": str(int(time.time())),
                        "status_code": str(response.status_code),
                    }
                )

                content.append(scraped)
                pages_scraped += 1

                # Extract links for further crawling
                if pages_scraped < max_pages:
                    links = self._extract_links(response.text, base_url, domain)
                    queue.extend(links)

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                logger.debug(f"Failed to scrape {url}: {e}")
                continue

        logger.info(f"🕷️ Scraped {len(content)} pages from {domain}")
        return content

    def _discover_sitemap_urls(self, base_url: str) -> List[str]:
        """Discover URLs from sitemap.xml."""
        urls = []
        domain = urlparse(base_url).netloc

        # Common sitemap locations
        sitemap_candidates = [
            f"https://{domain}/sitemap.xml",
            f"https://{domain}/sitemap_index.xml",
            f"https://{domain}/sitemap.php",
        ]

        for sitemap_url in sitemap_candidates:
            try:
                response = self.session.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    urls.extend(self._parse_sitemap(response.text, base_url))
                    break
            except:
                continue

        return urls

    def _parse_sitemap(self, sitemap_content: str, base_url: str) -> List[str]:
        """Parse sitemap XML content."""
        urls = []

        try:
            root = ET.fromstring(sitemap_content)

            # Handle sitemap index
            if root.tag.endswith('sitemapindex'):
                for sitemap in root:
                    loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and loc.text:
                        try:
                            response = self.session.get(loc.text, timeout=10)
                            if response.status_code == 200:
                                urls.extend(self._parse_sitemap(response.text, base_url))
                        except:
                            continue
            else:
                # Regular sitemap
                for url in root:
                    loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and loc.text:
                        urls.append(loc.text)

        except Exception as e:
            logger.debug(f"Failed to parse sitemap: {e}")

        return urls

    def _extract_content(self, html: str) -> Tuple[str, str]:
        """Extract clean text content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')

        # Get title
        title = soup.title.get_text(strip=True) if soup.title else ""

        # Remove unwanted elements
        for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "aside", "form"]):
            tag.decompose()

        # Get main content areas
        content_selectors = ["main", "article", ".content", "#content", ".main", "#main"]
        main_content = None

        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if not main_content:
            main_content = soup.body or soup

        # Extract text
        text = main_content.get_text("\n", strip=True)

        # Clean up text
        lines = [re.sub(r'\s+', ' ', line).strip() for line in text.split('\n')]
        text = '\n'.join([line for line in lines if line and len(line) > 10])

        return title, text

    def _extract_links(self, html: str, base_url: str, domain: str) -> List[str]:
        """Extract internal links from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        for a in soup.find_all('a', href=True):
            href = a['href']

            # Convert to absolute URL
            if href.startswith('/'):
                href = urljoin(base_url, href)
            elif not href.startswith('http'):
                href = urljoin(base_url, href)

            # Only include same domain links
            if urlparse(href).netloc == domain and href not in links:
                links.append(href)

        return links[:10]  # Limit links to avoid explosion

    def _categorize_content(self, content: List[ScrapedContent]) -> Dict[str, List[ScrapedContent]]:
        """Categorize scraped content by type."""
        categories = {
            "about": [],
            "services": [],
            "team": [],
            "blog": [],
            "general": []
        }

        for item in content:
            url_lower = item.url.lower()
            title_lower = item.title.lower()
            content_lower = item.content.lower()

            # Categorization rules
            if any(keyword in url_lower or keyword in title_lower for keyword in ['about', 'about-us', 'company', 'our-story']):
                item.content_type = "about"
                categories["about"].append(item)
            elif any(keyword in url_lower or keyword in title_lower for keyword in ['services', 'products', 'solutions', 'offerings']):
                item.content_type = "services"
                categories["services"].append(item)
            elif any(keyword in url_lower or keyword in title_lower for keyword in ['team', 'staff', 'leadership', 'leadership']):
                item.content_type = "team"
                categories["team"].append(item)
            elif any(keyword in url_lower or keyword in title_lower for keyword in ['blog', 'news', 'articles', 'insights']):
                item.content_type = "blog"
                categories["blog"].append(item)
            else:
                categories["general"].append(item)

        return categories

    def vectorize_business_data(self, domain: str, content: Dict[str, List[ScrapedContent]]) -> None:
        """Vectorize business content into isolated vector store namespace.

        Args:
            domain: Business domain
            content: Categorized scraped content
        """
        logger.info(f"🧠 Vectorizing content for {domain}")

        # Create domain-specific vector store
        vector_dir = self.data_dir / domain.replace(".", "_") / "vectors"
        vector_store = VectorStore(persist_dir=str(vector_dir))

        documents = []

        for content_type, items in content.items():
            for item in items:
                # Chunk content
                chunks = self.text_splitter.split_text(item.content)

                for i, chunk in enumerate(chunks):
                    documents.append({
                        "page_content": chunk,
                        "metadata": {
                            "domain": domain,
                            "namespace": f"kb:{domain}",
                            "url": item.url,
                            "title": item.title,
                            "content_type": content_type,
                            "chunk": i,
                            "total_chunks": len(chunks),
                            "scraped_at": item.metadata.get("scraped_at", ""),
                        }
                    })

        if documents:
            vector_store.add_documents(documents)
            logger.info(f"✅ Vectorized {len(documents)} chunks for {domain}")
        else:
            logger.warning(f"⚠️ No documents to vectorize for {domain}")

    def process_lead(self, lead: Lead, max_pages: int = 50) -> Optional[Dict[str, Any]]:
        """Build a comprehensive intelligence bundle for the supplied lead.

        Args:
            lead: Lead instance loaded from the pipeline JSON exports.
            max_pages: Maximum number of pages to crawl for website data.

        Returns:
            Dictionary containing structured intelligence or None if no signals were found.
        """
        domain = self._resolve_domain(lead)
        storage_dir = self._resolve_storage_dir(domain, lead)

        metadata_insights = self._extract_metadata_insights(lead)
        lead_profile = self._build_lead_profile(lead, domain, metadata_insights)

        categorized_content: Dict[str, List[ScrapedContent]] = {}
        content_summaries: Dict[str, str] = {}
        highlights: Dict[str, List[str]] = {}

        if domain:
            categorized_content = self.load_business_data(domain, max_pages)
            if categorized_content:
                content_summaries = self._summarize_content(categorized_content)
                highlights = self._extract_highlights(content_summaries)
                try:
                    self.vectorize_business_data(domain, categorized_content)
                except Exception as exc:
                    logger.debug("Vectorization failed for %s: %s", domain, exc)

        hunter_data = self._enrich_with_hunter(lead, lead_profile.get("company"), domain)
        keyword_signals = self._compute_keyword_signals(content_summaries)
        digest = self._build_digest(lead_profile, metadata_insights, hunter_data, highlights, keyword_signals)

        intelligence = {
            "lead_profile": lead_profile,
            "metadata_insights": metadata_insights,
            "hunter_enrichment": hunter_data,
            "content_summaries": content_summaries,
            "content_highlights": highlights,
            "keyword_signals": keyword_signals,
            "online_presence": self._build_online_presence(lead, domain),
            "llm_digest": digest,
            "generated_at": int(time.time()),
        }

        if categorized_content:
            intelligence["content_sources"] = {
                content_type: [item.to_dict() for item in items[:3]]
                for content_type, items in categorized_content.items()
            }

        self._persist_intelligence(storage_dir, intelligence)

        return intelligence

    def _resolve_domain(self, lead: Lead) -> Optional[str]:
        """Infer an actionable domain for the lead if possible."""
        if lead.domain and lead.domain.strip():
            return lead.domain.strip().lower()

        if lead.email and "@" in lead.email:
            return lead.email.split("@")[-1].lower()

        apollo_data = lead.metadata.get("apollo_contact_data", {}) if lead.metadata else {}
        candidate = apollo_data.get("organization_website") or apollo_data.get("email_domain")
        if candidate:
            return candidate.strip().lower()

        return None

    def _resolve_storage_dir(self, domain: Optional[str], lead: Lead) -> Path:
        """Resolve the filesystem directory for storing intelligence artifacts."""
        if domain:
            key = domain.replace(".", "_")
        else:
            key = slugify(lead.name or lead.source or "unknown")
        path = self.data_dir / key
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _extract_metadata_insights(self, lead: Lead) -> Dict[str, Any]:
        """Extract high-signal metadata from provider payloads."""
        insights: Dict[str, Any] = {}
        if not lead.metadata:
            return insights

        apollo_contact = lead.metadata.get("apollo_contact_data")
        if isinstance(apollo_contact, dict):
            contact_details = {
                "title": apollo_contact.get("title"),
                "organization_name": apollo_contact.get("organization_name"),
                "organization_id": apollo_contact.get("organization_id"),
                "city": apollo_contact.get("city"),
                "state": apollo_contact.get("state"),
                "country": apollo_contact.get("country"),
                "headline": apollo_contact.get("headline"),
                "time_zone": apollo_contact.get("time_zone"),
                "contact_stage_id": apollo_contact.get("contact_stage_id"),
                "owner_id": apollo_contact.get("owner_id"),
            }
            contact_emails = []
            for email_entry in apollo_contact.get("contact_emails", [])[:3]:
                contact_emails.append({
                    "email": email_entry.get("email"),
                    "status": email_entry.get("email_status"),
                    "source": email_entry.get("source"),
                    "confidence": email_entry.get("extrapolated_email_confidence"),
                })

            phone_numbers = []
            for phone_entry in apollo_contact.get("phone_numbers", [])[:3]:
                phone_numbers.append({
                    "number": phone_entry.get("raw_number"),
                    "type": phone_entry.get("type"),
                    "status": phone_entry.get("status"),
                })

            contact_details["contact_emails"] = contact_emails
            contact_details["phone_numbers"] = phone_numbers
            insights["apollo_contact"] = {k: v for k, v in contact_details.items() if v}

        workflow_stats = lead.metadata.get("apollo_workflow_stats")
        if isinstance(workflow_stats, dict):
            insights["apollo_workflow_stats"] = workflow_stats

        for key in ("yelp_profile", "google_maps_profile", "bbb_profile"):
            if key in lead.metadata:
                insights[key] = lead.metadata[key]

        return insights

    def _build_lead_profile(
        self,
        lead: Lead,
        domain: Optional[str],
        metadata_insights: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Construct a normalized lead profile for downstream processing."""
        apollo = metadata_insights.get("apollo_contact", {})

        profile = {
            "name": lead.name,
            "title": apollo.get("title") or lead.description,
            "company": apollo.get("organization_name"),
            "industry": lead.industry,
            "location": lead.location,
            "description": lead.description,
            "primary_email": lead.email,
            "phone": lead.phone,
            "score": round(float(lead.score or 0), 3),
            "confidence": round(float(lead.confidence or 0), 3),
            "domain": domain,
            "source": lead.source,
            "tags": sorted([*lead.tags]) if lead.tags else [],
        }

        if not profile["company"] and domain:
            profile["company"] = domain.split(".")[0].replace("-", " ").title()

        return {k: v for k, v in profile.items() if v not in (None, "", [], {})}

    def _build_online_presence(self, lead: Lead, domain: Optional[str]) -> Dict[str, Any]:
        """Compile public URLs and identifiers associated with the lead."""
        presence = {
            "domain": domain,
            "linkedin_url": lead.linkedin_url,
            "yelp_url": lead.yelp_url,
            "google_maps_url": lead.google_maps_url,
            "bbb_url": lead.bbb_url,
            "crunchbase_url": lead.crunchbase_url,
        }
        return {k: v for k, v in presence.items() if v}

    def _summarize_content(self, content: Dict[str, List[ScrapedContent]], clips: int = 2) -> Dict[str, str]:
        """Return trimmed summaries for each content category."""
        summaries: Dict[str, str] = {}
        for content_type, items in content.items():
            if not items:
                continue
            combined = " ".join(item.content for item in items[:clips])
            summaries[content_type] = combined[:1500]
        return summaries

    def _extract_highlights(self, summaries: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract sentence-level highlights for key categories."""
        highlights: Dict[str, List[str]] = {}
        for key, text in summaries.items():
            sentences = re.split(r"(?<=[.!?])\s+", text)
            cleaned = [
                sentence.strip()
                for sentence in sentences
                if 25 <= len(sentence.strip()) <= 200
            ]
            if cleaned:
                highlights[key] = cleaned[:3]
        return highlights

    def _compute_keyword_signals(self, summaries: Dict[str, str]) -> Dict[str, Any]:
        """Derive lightweight keyword signals from the available summaries."""
        aggregate_text = " ".join(summaries.values()).lower()
        if not aggregate_text:
            return {}

        tokens = re.findall(r"[a-zA-Z]{4,}", aggregate_text)
        counts = Counter(tokens)
        top_keywords = [
            keyword for keyword, _ in counts.most_common(15)
            if keyword not in {"https", "http", "about", "contact", "hours"}
        ]

        return {
            "top_keywords": top_keywords[:10],
            "total_unique_tokens": len(counts),
        }

    def _build_digest(
        self,
        profile: Dict[str, Any],
        metadata_insights: Dict[str, Any],
        hunter_data: Dict[str, Any],
        highlights: Dict[str, List[str]],
        keyword_signals: Dict[str, Any],
    ) -> str:
        """Compile a digest string optimized for prompt injection."""
        lines = [
            f"Lead Name: {profile.get('name')}",
            f"Title: {profile.get('title')}" if profile.get("title") else "",
            f"Company: {profile.get('company')}" if profile.get("company") else "",
            f"Industry: {profile.get('industry')}" if profile.get("industry") else "",
            f"Location: {profile.get('location')}" if profile.get("location") else "",
        ]

        if hunter_data.get("domain_search"):
            org = hunter_data["domain_search"].get("organization")
            employees = hunter_data["domain_search"].get("emails", [])
            lines.append(f"Hunter Organization: {org}" if org else "")
            if employees:
                lines.append(f"Hunter Verified Emails: {len(employees)} records")

        if keyword_signals.get("top_keywords"):
            lines.append(f"Top Keywords: {', '.join(keyword_signals['top_keywords'][:7])}")

        if highlights.get("services"):
            lines.append("Service Highlights:")
            lines.extend(f"- {sentence}" for sentence in highlights["services"])

        apollo = metadata_insights.get("apollo_contact", {})
        if apollo.get("contact_emails"):
            lines.append("Apollo Contact Emails:")
            for entry in apollo["contact_emails"]:
                lines.append(f"- {entry.get('email')} ({entry.get('status')})")

        return "\n".join(line for line in lines if line)

    def _enrich_with_hunter(
        self,
        lead: Lead,
        company: Optional[str],
        domain: Optional[str],
    ) -> Dict[str, Any]:
        """Enrich the lead using Hunter.io when credentials are available."""
        if not domain or not self.hunter_client.is_configured():
            return {}

        enrichment: Dict[str, Any] = {}

        try:
            with get_db_session() as session:
                # Get or create business domain
                business_domain = session.query(BusinessDomain).filter_by(domain=domain).first()
                if not business_domain:
                    business_domain = BusinessDomain(domain=domain)
                    session.add(business_domain)
                    session.flush()

                # Check for existing domain search data
                existing_domain_search = session.query(HunterEnrichment).filter_by(
                    domain_id=business_domain.id,
                    enrichment_type="domain_search"
                ).first()

                if existing_domain_search:
                    # Load from database
                    domain_data = existing_domain_search.domain_search_data
                    if domain_data:
                        enrichment["domain_search"] = domain_data
                else:
                    # Fetch from Hunter.io
                    domain_data = self.hunter_client.domain_search(domain)
                    if domain_data:
                        enrichment["domain_search"] = {
                            "organization": domain_data.get("organization"),
                            "country": domain_data.get("country"),
                            "state": domain_data.get("state"),
                            "emails": [
                                {
                                    "value": email.get("value"),
                                    "type": email.get("type"),
                                    "position": email.get("position"),
                                    "confidence": email.get("confidence"),
                                    "first_name": email.get("first_name"),
                                    "last_name": email.get("last_name"),
                                }
                                for email in (domain_data.get("emails") or [])[:5]
                            ],
                            "pattern": domain_data.get("pattern"),
                            "disposable": domain_data.get("disposable"),
                            "webmail": domain_data.get("webmail"),
                        }

                        # Save to database
                        hunter_enrichment = HunterEnrichment(
                            domain_id=business_domain.id,
                            enrichment_type="domain_search",
                            domain_search_data=enrichment["domain_search"]
                        )
                        session.add(hunter_enrichment)

                # Email finder enrichment
                first_name, last_name = self._split_name(lead.name)
                if first_name and last_name:
                    # Check for existing email finder data
                    target_email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
                    existing_finder = session.query(HunterEnrichment).filter_by(
                        domain_id=business_domain.id,
                        enrichment_type="email_finder",
                        target_email=target_email
                    ).first()

                    if existing_finder:
                        # Load from database
                        finder_data = existing_finder.email_finder_data
                        if finder_data:
                            enrichment["email_finder"] = finder_data
                    else:
                        # Fetch from Hunter.io
                        finder_data = self.hunter_client.email_finder(
                            domain=domain,
                            first_name=first_name,
                            last_name=last_name,
                            company=company,
                        )
                        if finder_data:
                            enrichment["email_finder"] = {
                                "email": finder_data.get("email"),
                                "score": finder_data.get("score"),
                                "verified": finder_data.get("verification", {}).get("status"),
                            }

                            # Save to database
                            hunter_enrichment = HunterEnrichment(
                                domain_id=business_domain.id,
                                enrichment_type="email_finder",
                                email_finder_data=enrichment["email_finder"],
                                target_email=target_email,
                                target_first_name=first_name,
                                target_last_name=last_name
                            )
                            session.add(hunter_enrichment)

        except Exception as exc:
            logger.warning("Failed to use database for Hunter enrichment, falling back to in-memory: %s", exc)
            # Fallback to original logic if database fails
            domain_data = self.hunter_client.domain_search(domain)
            if domain_data:
                enrichment["domain_search"] = {
                    "organization": domain_data.get("organization"),
                    "country": domain_data.get("country"),
                    "state": domain_data.get("state"),
                    "emails": [
                        {
                            "value": email.get("value"),
                            "type": email.get("type"),
                            "position": email.get("position"),
                            "confidence": email.get("confidence"),
                            "first_name": email.get("first_name"),
                            "last_name": email.get("last_name"),
                        }
                        for email in (domain_data.get("emails") or [])[:5]
                    ],
                    "pattern": domain_data.get("pattern"),
                    "disposable": domain_data.get("disposable"),
                    "webmail": domain_data.get("webmail"),
                }

            if first_name and last_name:
                finder_data = self.hunter_client.email_finder(
                    domain=domain,
                    first_name=first_name,
                    last_name=last_name,
                    company=company,
                )
                if finder_data:
                    enrichment["email_finder"] = {
                        "email": finder_data.get("email"),
                        "score": finder_data.get("score"),
                        "verified": finder_data.get("verification", {}).get("status"),
                    }

        return enrichment

    def _split_name(self, name: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """Split a human name into first and last components."""
        if not name:
            return None, None
        parts = [token for token in name.strip().split() if token]
        if not parts:
            return None, None
        if len(parts) == 1:
            return parts[0], None
        return parts[0], parts[-1]

    def _persist_intelligence(self, directory: Path, intelligence: Dict[str, Any]) -> None:
        """Persist the intelligence payload to database."""
        try:
            with get_db_session() as session:
                # Get or create business domain
                lead_profile = intelligence.get("lead_profile", {})
                domain = lead_profile.get("domain")
                if not domain:
                    logger.warning("No domain found in intelligence bundle, skipping database persistence")
                    return

                business_domain = session.query(BusinessDomain).filter_by(domain=domain).first()
                if not business_domain:
                    business_domain = BusinessDomain(domain=domain)
                    session.add(business_domain)
                    session.flush()

                # Create intelligence bundle
                bundle = IntelligenceBundle(
                    domain_id=business_domain.id,
                    lead_name=lead_profile.get("name"),
                    lead_title=lead_profile.get("title"),
                    lead_company=lead_profile.get("company"),
                    lead_industry=lead_profile.get("industry"),
                    lead_location=lead_profile.get("location"),
                    lead_email=lead_profile.get("primary_email"),
                    lead_phone=lead_profile.get("phone"),
                    lead_score=str(lead_profile.get("score", 0)),
                    lead_source=lead_profile.get("source"),
                    lead_profile=lead_profile,
                    metadata_insights=intelligence.get("metadata_insights"),
                    hunter_enrichment=intelligence.get("hunter_enrichment"),
                    content_summaries=intelligence.get("content_summaries"),
                    content_highlights=intelligence.get("content_highlights"),
                    keyword_signals=intelligence.get("keyword_signals"),
                    online_presence=intelligence.get("online_presence"),
                    llm_digest=intelligence.get("llm_digest"),
                    content_sources=intelligence.get("content_sources"),
                    generated_at=datetime.fromtimestamp(intelligence.get("generated_at", time.time()))
                )

                session.add(bundle)
                logger.info("💾 Stored intelligence bundle for domain %s in database", domain)

        except Exception as exc:
            logger.error("Failed to persist intelligence to database: %s", exc)
            # Fallback to file storage if database fails
            self._persist_intelligence_fallback(directory, intelligence)

    def _load_business_data_fallback(self, domain: str, max_pages: int) -> Dict[str, List[ScrapedContent]]:
        """Fallback method to load business data from files when database is unavailable."""
        # Create domain-specific directory
        domain_dir = self.data_dir / domain.replace(".", "_")
        domain_dir.mkdir(parents=True, exist_ok=True)

        # Check if already processed
        content_file = domain_dir / "content.json"
        if content_file.exists():
            logger.info(f"📁 Loading cached content for {domain} from files")
            try:
                with open(content_file, 'r', encoding='utf-8') as f:
                    content_data = json.load(f)
                    return {
                        content_type: [ScrapedContent(**item) for item in items]
                        for content_type, items in content_data.items()
                    }
            except Exception as e:
                logger.warning(f"Failed to load cached content: {e}")

        # Scrape fresh content
        content = self._scrape_website(f"https://{domain}", max_pages)

        # Categorize content
        categorized_content = self._categorize_content(content)

        # Save to disk
        content_dict = {
            content_type: [item.to_dict() for item in items]
            for content_type, items in categorized_content.items()
        }

        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(content_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Saved {sum(len(items) for items in categorized_content.values())} pages for {domain} to files")
        return categorized_content

    def _persist_intelligence_fallback(self, directory: Path, intelligence: Dict[str, Any]) -> None:
        """Fallback method to persist intelligence to disk when database is unavailable."""
        output_file = directory / "intelligence.json"
        try:
            with open(output_file, "w", encoding="utf-8") as handle:
                json.dump(intelligence, handle, indent=2, ensure_ascii=False)
            logger.info("💾 Stored intelligence bundle at %s (fallback)", output_file)
        except OSError as exc:
            logger.error("Failed to write intelligence file %s: %s", output_file, exc)

    def process_business(self, domain: str, max_pages: int = 50) -> bool:
        """Backward-compatible entry point using only a raw domain."""
        lead = Lead(
            name=domain,
            domain=domain,
            industry="general",
            source="manual_import",
        )
        intelligence = self.process_lead(lead, max_pages=max_pages)
        return bool(intelligence)


def main():
    """CLI interface for business intelligence loading."""
    import argparse

    parser = argparse.ArgumentParser(description="Load business intelligence")
    parser.add_argument("--domain", required=True, help="Business domain (e.g., 'example.com')")
    parser.add_argument("--max-pages", type=int, default=50, help="Maximum pages to scrape")
    parser.add_argument("--data-dir", default="pipeline/business_data", help="Data storage directory")

    args = parser.parse_args()

    loader = BusinessIntelligenceLoader(args.data_dir)
    success = loader.process_business(args.domain, args.max_pages)

    if success:
        print(f"Successfully processed {args.domain}")
    else:
        print(f"Failed to process {args.domain}")
        exit(1)


if __name__ == "__main__":
    main()
