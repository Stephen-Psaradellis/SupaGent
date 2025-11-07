"""
Scrape ElevenLabs API documentation and save as Markdown files.

This script crawls the ElevenLabs API documentation and saves each endpoint
as a Markdown file for offline access.
"""
from __future__ import annotations

import os
import sys
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# Base URL for ElevenLabs API documentation
BASE_URL = "https://elevenlabs.io/docs/api-reference/"

# Sections to scrape based on the image
SECTIONS = [
    "agents",
    "conversations",
    "tools",
    "knowledge-base",
    "tests",
    "phone-numbers",
    "widget",
    "workspace",
    "sip-trunk",
    "twilio",
    "batch-calling",
    "llm-usage",
    "mcp",
]

# Output directory
OUTPUT_DIR = project_root / "docs" / "api"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Track visited URLs to avoid duplicates
visited_urls: Set[str] = set()
endpoints: List[Dict[str, str]] = []


def clean_filename(url_path: str) -> str:
    """Convert URL path to clean filename."""
    # Remove leading/trailing slashes
    path = url_path.strip("/")
    # Replace slashes with hyphens
    filename = path.replace("/", "-")
    # Remove any invalid characters
    filename = re.sub(r'[<>:"|?*]', '', filename)
    # If empty, use 'index'
    if not filename:
        filename = "index"
    return f"{filename}.md"


def extract_main_content(soup: BeautifulSoup) -> str:
    """Extract main content from page, ignoring navbars, footers, and scripts."""
    # Remove script, style, nav, footer, header elements
    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
        element.decompose()
    
    # Remove common navigation patterns
    for element in soup.find_all(class_=re.compile(r'nav|menu|sidebar|breadcrumb', re.I)):
        element.decompose()
    
    # Try to find main content area - ElevenLabs docs structure
    main_content = None
    
    # Try specific selectors for ElevenLabs documentation
    main_selectors = [
        "main article",
        "main .content",
        "main",
        "[role='main']",
        ".documentation-content",
        ".docs-content",
        "article",
    ]
    
    for selector in main_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break
    
    # If no main content found, try to find the content div
    if not main_content:
        # Look for divs that likely contain the main content
        for div in soup.find_all("div", class_=True):
            classes = " ".join(div.get("class", []))
            if any(keyword in classes.lower() for keyword in ["content", "documentation", "docs", "article"]):
                if "nav" not in classes.lower() and "menu" not in classes.lower():
                    main_content = div
                    break
    
    # If still no main content, use body but remove navigation elements
    if not main_content:
        main_content = soup.find("body")
        if main_content:
            # Remove navigation, footer, header elements
            for elem in main_content.find_all(["nav", "footer", "header", "aside"]):
                elem.decompose()
            # Remove elements with navigation-related classes
            for elem in main_content.find_all(class_=re.compile(r'nav|menu|sidebar|breadcrumb', re.I)):
                elem.decompose()
    
    if not main_content:
        return ""
    
    # Convert to markdown
    content = md(str(main_content), heading_style="ATX", bullets="-")
    
    # Clean up the markdown
    # Remove excessive blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    # Remove navigation links that might have been converted
    content = re.sub(r'^\[.*?\]\(/docs/.*?\)\s*$', '', content, flags=re.MULTILINE)
    # Remove standalone link lines that are navigation
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip lines that are just navigation links
        if re.match(r'^\[.*?\]\(/docs/', line.strip()) and len(line.strip()) < 100:
            continue
        cleaned_lines.append(line)
    content = '\n'.join(cleaned_lines)
    
    return content.strip()


def scrape_page(url: str) -> Dict[str, str] | None:
    """Scrape a single page and return its content."""
    # Normalize URL (remove query parameters and fragments)
    parsed = urlparse(url)
    normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    if normalized_url in visited_urls:
        return None
    
    visited_urls.add(normalized_url)
    
    try:
        print(f"Scraping: {normalized_url}")
        response = requests.get(normalized_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        content = extract_main_content(soup)
        
        if not content:
            print(f"  [WARNING] No content extracted from {normalized_url}")
            return None
        
        # Extract title
        title = soup.find("title")
        title_text = title.get_text().strip() if title else "API Documentation"
        # Clean title (remove "| ElevenLabs Documentation" suffix)
        title_text = re.sub(r'\s*\|\s*ElevenLabs.*$', '', title_text, flags=re.IGNORECASE)
        
        # Extract endpoint info if available
        endpoint_info = extract_endpoint_info(soup, normalized_url)
        
        # Create markdown content
        markdown_content = f"""# {title_text}

**URL:** {normalized_url}

{endpoint_info}

---

{content}
"""
        
        # Determine filename from normalized URL
        parsed = urlparse(normalized_url)
        path = parsed.path.replace("/docs/api-reference/", "").strip("/")
        filename = clean_filename(path)
        filepath = OUTPUT_DIR / filename
        
        # Save file
        filepath.write_text(markdown_content, encoding='utf-8')
        print(f"  [OK] Saved: {filename}")
        
        return {
            "url": url,
            "title": title_text,
            "filename": filename,
            "path": path,
        }
        
    except Exception as e:
        print(f"  [ERROR] Error scraping {url}: {e}")
        return None


def extract_endpoint_info(soup: BeautifulSoup, url: str) -> str:
    """Extract endpoint information (method, path, etc.) from the page."""
    info_parts = []
    
    # Try to find HTTP method and path
    # Look for common patterns in documentation
    method_patterns = [
        r'(GET|POST|PUT|PATCH|DELETE)\s+([^\s]+)',
        r'`(GET|POST|PUT|PATCH|DELETE)\s+([^`]+)`',
    ]
    
    text_content = soup.get_text()
    for pattern in method_patterns:
        match = re.search(pattern, text_content)
        if match:
            method = match.group(1)
            path = match.group(2).strip()
            info_parts.append(f"**Method:** {method}")
            info_parts.append(f"**Path:** `{path}`")
            break
    
    # Extract from URL if it's an endpoint page
    if "/agents/" in url or "/conversations/" in url or "/tools/" in url:
        # Try to infer from URL structure
        path_parts = url.replace(BASE_URL, "").split("/")
        if len(path_parts) >= 2:
            section = path_parts[0]
            endpoint = path_parts[1] if len(path_parts) > 1 else "list"
            info_parts.append(f"**Section:** {section}")
            info_parts.append(f"**Endpoint:** {endpoint}")
    
    if info_parts:
        return "\n".join(info_parts) + "\n"
    return ""


def find_endpoint_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Find all endpoint links on a page."""
    links = []
    
    # Find all anchor tags
    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href")
        if not href:
            continue
        
        # Convert relative URLs to absolute
        full_url = urljoin(base_url, href)
        
        # Only include links to API reference pages
        if BASE_URL in full_url:
            # Normalize URL (remove query parameters)
            parsed = urlparse(full_url)
            normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            if normalized_url not in visited_urls:
                # Check if it's an endpoint page (not just a section index)
                path_parts = parsed.path.replace("/docs/api-reference/", "").strip("/").split("/")
                
                # Include if it's a specific endpoint (has at least 2 parts: section/endpoint)
                if len(path_parts) >= 2:
                    links.append(normalized_url)
                # Also include section pages
                elif len(path_parts) == 1 and path_parts[0] in SECTIONS:
                    links.append(normalized_url)
    
    return links


def scrape_section(section: str) -> List[Dict[str, str]]:
    """Scrape all endpoints in a section."""
    section_url = urljoin(BASE_URL, section)
    section_endpoints = []
    
    print(f"\n{'='*60}")
    print(f"Scraping section: {section}")
    print(f"{'='*60}")
    
    # First, get the section index page
    result = scrape_page(section_url)
    if result:
        section_endpoints.append(result)
    
    # Then find and scrape all endpoint pages in this section
    try:
        response = requests.get(section_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links to endpoints in this section
        links = find_endpoint_links(soup, section_url)
        
        for link in links:
            # Only process links for this section
            if f"/{section}/" in link:
                result = scrape_page(link)
                if result:
                    section_endpoints.append(result)
                time.sleep(0.5)  # Be polite to the server
        
    except Exception as e:
        print(f"Error processing section {section}: {e}")
    
    return section_endpoints


def create_index():
    """Create an index.md file listing all endpoints."""
    if not endpoints:
        return
    
    # Deduplicate endpoints by filename
    seen_filenames = set()
    unique_endpoints = []
    for endpoint in endpoints:
        filename = endpoint["filename"]
        if filename not in seen_filenames:
            seen_filenames.add(filename)
            unique_endpoints.append(endpoint)
    
    # Sort endpoints alphabetically by title
    sorted_endpoints = sorted(unique_endpoints, key=lambda x: x["title"])
    
    index_content = """# ElevenLabs API Documentation Index

This directory contains scraped documentation from the [ElevenLabs API Reference](https://elevenlabs.io/docs/api-reference/).

## Endpoints

"""
    
    # Group by section
    sections_dict: Dict[str, List[Dict[str, str]]] = {}
    for endpoint in sorted_endpoints:
        section = endpoint.get("path", "").split("/")[0] if endpoint.get("path") else "other"
        if section not in sections_dict:
            sections_dict[section] = []
        sections_dict[section].append(endpoint)
    
    # Write sections
    for section in sorted(sections_dict.keys()):
        section_endpoints = sections_dict[section]
        index_content += f"\n### {section.title().replace('-', ' ')}\n\n"
        
        # Sort by title within section
        for endpoint in sorted(section_endpoints, key=lambda x: x["title"]):
            filename = endpoint["filename"]
            title = endpoint["title"]
            index_content += f"- [{title}]({filename})\n"
    
    index_content += f"\n\n---\n\n**Total endpoints:** {len(unique_endpoints)}\n"
    index_content += f"**Last updated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    index_path = OUTPUT_DIR / "index.md"
    index_path.write_text(index_content, encoding='utf-8')
    print(f"\n[OK] Created index: {index_path}")


def main():
    """Main scraping function."""
    print("Starting ElevenLabs API documentation scraper...")
    print(f"Output directory: {OUTPUT_DIR}")
    
    # Scrape each section
    for section in SECTIONS:
        section_endpoints = scrape_section(section)
        endpoints.extend(section_endpoints)
        time.sleep(1)  # Be polite between sections
    
    # Also scrape the main index page
    print(f"\n{'='*60}")
    print("Scraping main index page")
    print(f"{'='*60}")
    result = scrape_page(BASE_URL)
    if result:
        endpoints.append(result)
    
    # Create index
    print(f"\n{'='*60}")
    print("Creating index file")
    print(f"{'='*60}")
    create_index()
    
    print(f"\n{'='*60}")
    print("Scraping complete!")
    print(f"Total pages scraped: {len(endpoints)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

