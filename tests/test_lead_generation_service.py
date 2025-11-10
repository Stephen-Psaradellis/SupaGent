"""Targeted tests for the refactored lead generation pipeline."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from pipeline.lead_generation import (
    Lead,
    LeadGenerator,
    LeadPipelineContext,
    LeadPipelineSettings,
    LeadQuery,
    SQLiteCacheBackend,
    WebDirectoryScraperConnector,
    YelpOpenDatasetConnector,
)


@pytest.fixture()
def tmp_settings(tmp_path: Path) -> LeadPipelineSettings:
    """Return pipeline settings pointing at a temporary workspace."""
    return LeadPipelineSettings.from_env(
        leads_dir=tmp_path,
        cache_path=tmp_path / "cache.sqlite3",
    )


def test_sqlite_cache_backend_expiration(tmp_path: Path) -> None:
    """Ensure cached payloads respect TTL boundaries."""
    cache_path = tmp_path / "cache.sqlite3"
    cache = SQLiteCacheBackend(cache_path, ttl_seconds=5)

    with patch("pipeline.lead_generation.now_ts", return_value=1000.0):
        cache.set("alpha", json.dumps({"value": 1}), ttl_seconds=2)

    with patch("pipeline.lead_generation.now_ts", return_value=1001.0):
        assert cache.get("alpha") is not None

    with patch("pipeline.lead_generation.now_ts", return_value=1003.5):
        assert cache.get("alpha") is None


def test_lead_generator_pipeline_stubbed(tmp_settings: LeadPipelineSettings) -> None:
    """Exercise the orchestration pipeline with stubbed providers."""

    generator = LeadGenerator(leads_dir=str(tmp_settings.leads_dir), settings=tmp_settings)

    class StubSource:
        name = "stub_source"

        async def fetch(self, query: LeadQuery, context: LeadPipelineContext):
            return [
                Lead(
                    name="Bright Dental",
                    domain="brightdental.com",
                    location=query.location,
                    industry=query.industry,
                    email="info@brightdental.com",
                    source=self.name,
                ),
                Lead(
                    name="Sunrise Dental",
                    domain="sunrisedental.com",
                    location=query.location,
                    industry=query.industry,
                    source=self.name,
                ),
            ]

        def is_configured(self, settings: LeadPipelineSettings) -> bool:
            return True

    class StubEnricher:
        name = "stub_enricher"

        async def enrich(self, lead: Lead, context: LeadPipelineContext) -> Lead:
            lead.add_email(f"contact@{lead.domain}")
            lead.tags.add("stubbed")
            return lead

        def is_configured(self, settings: LeadPipelineSettings) -> bool:
            return True

    generator.sources = {"stub_source": StubSource()}
    generator.enrichers = {"stub_enricher": StubEnricher()}
    generator.filter.min_score = 0.0

    leads = generator.generate_leads(
        industry="dentists",
        location="Austin, TX",
        limit=5,
        sources=["stub_source"],
    )

    assert len(leads) == 2
    assert all("stubbed" in lead.tags for lead in leads)
    assert all(lead.emails for lead in leads)

    exports = list(tmp_settings.leads_dir.rglob("*.json"))
    assert exports, "Expected a persisted export file."

    with exports[0].open("r", encoding="utf-8") as handle:
        payload: Any = json.load(handle)
    assert isinstance(payload, list)
    assert payload[0]["name"] == "Bright Dental"


def test_yelp_open_dataset_connector_filters_results(tmp_path: Path) -> None:
    """Ensure the Yelp dataset connector surfaces relevant businesses."""

    dataset_path = tmp_path / "yelp.json"
    dataset_path.write_text(
        '\n'.join(
            [
                json.dumps(
                    {
                        "name": "Austin Dental Co",
                        "categories": "Dentists, Health & Medical",
                        "city": "Austin",
                        "state": "TX",
                        "postal_code": "78701",
                        "website": "https://austindental.example.com",
                        "phone": "+1-512-555-0100",
                        "business_id": "abc123",
                        "stars": 4.9,
                        "review_count": 127,
                    }
                ),
                json.dumps(
                    {
                        "name": "Chicago Plumbing",
                        "categories": "Plumbing",
                        "city": "Chicago",
                        "state": "IL",
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )

    settings = LeadPipelineSettings.from_env(
        leads_dir=tmp_path,
        cache_path=tmp_path / "cache.sqlite3",
        yelp_dataset_path=str(dataset_path),
    )
    cache = SQLiteCacheBackend(settings.cache_path, settings.cache_ttl_seconds)

    class DummyHTTP:  # pragma: no cover - simple stub
        pass

    context = LeadPipelineContext(settings=settings, cache=cache, http=DummyHTTP())
    connector = YelpOpenDatasetConnector()
    query = LeadQuery(industry="dentists", location="Austin, TX", limit=5)

    leads = asyncio.run(connector.fetch(query, context))

    assert len(leads) == 1
    assert leads[0].domain == "austindental.example.com"
    assert leads[0].metadata["yelp_business_id"] == "abc123"


def test_web_directory_scraper_connector_parses_html(tmp_path: Path) -> None:
    """Validate directory scraping heuristics."""

    settings = LeadPipelineSettings.from_env(
        leads_dir=tmp_path,
        cache_path=tmp_path / "cache.sqlite3",
    )
    cache = SQLiteCacheBackend(settings.cache_path, settings.cache_ttl_seconds)

    class DummyHTTP:
        async def get(self, *args, **kwargs):
            raise AssertionError("HTTP calls should be stubbed in this test")

    connector = WebDirectoryScraperConnector()

    sample_html = """
    <html>
    <body>
        <div>
            <h2><a href="https://example.com">Example Dental</a></h2>
            <a href="https://example.com/contact">Contact</a>
        </div>
        <div>
            <h2><a href="https://another-example.org">Another Example Clinic</a></h2>
        </div>
    </body>
    </html>
    """

    async def fake_fetch(url, context):  # pragma: no cover - deterministic stub
        return sample_html

    connector._fetch_html = fake_fetch  # type: ignore[assignment]

    context = LeadPipelineContext(settings=settings, cache=cache, http=DummyHTTP())
    query = LeadQuery(industry="dentists", location="Austin, TX", limit=5)
    leads = asyncio.run(connector.fetch(query, context))

    assert len(leads) == 2
    assert {lead.domain for lead in leads} == {"example.com", "another-example.org"}

