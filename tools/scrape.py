from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

import requests
from bs4 import BeautifulSoup


@dataclass
class Page:
    url: str
    title: str
    content: str


def clean_text(html: str) -> Tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else ""
    # Remove scripts/styles/navs
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    lines = [re.sub(r"\s+", " ", l).strip() for l in text.splitlines()]
    text = "\n".join([l for l in lines if l])
    return title, text


def in_domain(href: str, base: str) -> bool:
    try:
        return href.startswith(base) or (href.startswith("/") and base)
    except Exception:
        return False


def crawl(base_url: str, limit: int = 200) -> List[Page]:
    seen = set()
    queue = [base_url.rstrip("/")]
    pages: List[Page] = []
    session = requests.Session()
    while queue and len(pages) < limit:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            resp = session.get(url, timeout=20)
            if resp.status_code != 200 or "text/html" not in resp.headers.get("content-type", ""):
                continue
            title, text = clean_text(resp.text)
            if len(text) < 200:
                continue
            pages.append(Page(url=url, title=title, content=text))
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http") and in_domain(href, base_url.rstrip("/")):
                    queue.append(href)
                elif href.startswith("/"):
                    queue.append(base_url.rstrip("/") + href)
        except Exception:
            continue
    return pages


def save_markdown(pages: List[Page], out_dir: str) -> None:
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(pages):
        stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", page.title)[:80] or f"doc-{i}"
        md = f"# {page.title}\n\nSource: {page.url}\n\n{page.content}\n"
        (p / f"{stem}.md").write_text(md, encoding="utf-8")


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("base_url", help="Base docs URL to crawl, e.g., https://docs.gitlab.com")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--out", default="dataset/company")
    args = ap.parse_args()

    pages = crawl(args.base_url, limit=args.limit)
    save_markdown(pages, args.out)

    # Write license/source notice
    lic = Path(args.out).parent / "LICENSE.md"
    if not lic.exists():
        lic.write_text(
            """Data scraped from public documentation. Verify and comply with the site's license/terms before use.\nProvide attribution and follow robots.txt.\n""",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
