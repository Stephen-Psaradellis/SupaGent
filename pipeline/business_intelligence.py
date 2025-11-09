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
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

from memory.vector_store import VectorStore

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

        # Create domain-specific directory
        domain_dir = self.data_dir / domain.replace(".", "_")
        domain_dir.mkdir(parents=True, exist_ok=True)

        # Check if already processed
        content_file = domain_dir / "content.json"
        if content_file.exists():
            logger.info(f"📁 Loading cached content for {domain}")
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

        logger.info(f"💾 Saved {sum(len(items) for items in categorized_content.values())} pages for {domain}")
        return categorized_content

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

    def process_business(self, domain: str, max_pages: int = 50) -> bool:
        """Complete pipeline: scrape, categorize, and vectorize business data.

        Args:
            domain: Business domain to process
            max_pages: Maximum pages to scrape

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load/scrape content
            content = self.load_business_data(domain, max_pages)

            if not content:
                logger.warning(f"❌ No content found for {domain}")
                return False

            # Vectorize content
            self.vectorize_business_data(domain, content)

            logger.info(f"🎉 Successfully processed {domain}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to process {domain}: {e}")
            return False


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
