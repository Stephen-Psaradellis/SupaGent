#!/usr/bin/env python3
"""
Migration script to transfer existing file-based business intelligence data to PostgreSQL.

This script scans the pipeline/business_data directory and migrates all existing
scraped content and intelligence bundles to the database.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import get_db_session, create_tables
from core.models import BusinessDomain, ScrapedContent, IntelligenceBundle

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BusinessDataMigrator:
    """Handles migration of business intelligence data from files to database."""

    def __init__(self, data_dir: str = "pipeline/business_data"):
        """Initialize migrator with data directory path."""
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory {data_dir} does not exist")

    def migrate_all_data(self) -> None:
        """Migrate all business data from files to database."""
        logger.info("Starting business data migration...")

        # Ensure database tables exist
        create_tables()

        # Find all domain directories
        domain_dirs = [d for d in self.data_dir.iterdir() if d.is_dir()]
        logger.info(f"Found {len(domain_dirs)} domain directories to process")

        total_migrated = 0
        for domain_dir in domain_dirs:
            try:
                domain = domain_dir.name.replace("_", ".")
                migrated = self.migrate_domain_data(domain_dir, domain)
                total_migrated += migrated
                logger.info(f"Migrated {migrated} items for domain {domain}")
            except Exception as e:
                logger.error(f"Failed to migrate domain {domain_dir.name}: {e}")
                continue

        logger.info(f"Migration complete! Migrated {total_migrated} total items")

    def migrate_domain_data(self, domain_dir: Path, domain: str) -> int:
        """Migrate data for a specific domain."""
        migrated_count = 0

        with get_db_session() as session:
            # Get or create business domain
            business_domain = session.query(BusinessDomain).filter_by(domain=domain).first()
            if not business_domain:
                business_domain = BusinessDomain(domain=domain)
                session.add(business_domain)
                session.flush()

            # Check if already migrated (has scraped content)
            if business_domain.scraped_contents:
                logger.info(f"Domain {domain} already has data in database, skipping")
                return 0

            # Migrate scraped content
            content_file = domain_dir / "content.json"
            if content_file.exists():
                migrated_count += self.migrate_scraped_content(session, business_domain, content_file)

            # Migrate intelligence bundles
            intelligence_file = domain_dir / "intelligence.json"
            if intelligence_file.exists():
                self.migrate_intelligence_bundle(session, business_domain, intelligence_file)
                migrated_count += 1

        return migrated_count

    def migrate_scraped_content(self, session, business_domain: BusinessDomain, content_file: Path) -> int:
        """Migrate scraped content from JSON file to database."""
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                content_data = json.load(f)

            migrated_count = 0
            for content_type, items in content_data.items():
                for item in items:
                    # Convert metadata timestamps
                    metadata = item.get("metadata", {})
                    scraped_at = None
                    if "scraped_at" in metadata:
                        try:
                            scraped_at = datetime.fromtimestamp(int(metadata["scraped_at"]))
                        except (ValueError, TypeError):
                            scraped_at = datetime.utcnow()

                    scraped_content = ScrapedContent(
                        domain_id=business_domain.id,
                        url=item["url"],
                        title=item["title"],
                        content=item["content"],
                        content_type=content_type,
                        metadata_json=metadata,
                        scraped_at=scraped_at
                    )
                    session.add(scraped_content)
                    migrated_count += 1

            logger.info(f"Migrated {migrated_count} scraped content items for domain {business_domain.domain}")
            return migrated_count

        except Exception as e:
            logger.error(f"Failed to migrate scraped content from {content_file}: {e}")
            return 0

    def migrate_intelligence_bundle(self, session, business_domain: BusinessDomain, intelligence_file: Path) -> None:
        """Migrate intelligence bundle from JSON file to database."""
        try:
            with open(intelligence_file, 'r', encoding='utf-8') as f:
                intelligence_data = json.load(f)

            lead_profile = intelligence_data.get("lead_profile", {})

            # Convert generated_at timestamp
            generated_at = datetime.utcnow()
            if "generated_at" in intelligence_data:
                try:
                    generated_at = datetime.fromtimestamp(int(intelligence_data["generated_at"]))
                except (ValueError, TypeError):
                    pass

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
                metadata_insights=intelligence_data.get("metadata_insights"),
                hunter_enrichment=intelligence_data.get("hunter_enrichment"),
                content_summaries=intelligence_data.get("content_summaries"),
                content_highlights=intelligence_data.get("content_highlights"),
                keyword_signals=intelligence_data.get("keyword_signals"),
                online_presence=intelligence_data.get("online_presence"),
                llm_digest=intelligence_data.get("llm_digest"),
                content_sources=intelligence_data.get("content_sources"),
                generated_at=generated_at
            )

            session.add(bundle)
            logger.info(f"Migrated intelligence bundle for domain {business_domain.domain}")

        except Exception as e:
            logger.error(f"Failed to migrate intelligence bundle from {intelligence_file}: {e}")

    def dry_run(self) -> None:
        """Perform a dry run to show what would be migrated."""
        logger.info("Performing dry run...")

        total_content_items = 0
        total_intelligence_bundles = 0

        domain_dirs = [d for d in self.data_dir.iterdir() if d.is_dir()]
        for domain_dir in domain_dirs:
            domain = domain_dir.name.replace("_", ".")

            content_file = domain_dir / "content.json"
            if content_file.exists():
                try:
                    with open(content_file, 'r', encoding='utf-8') as f:
                        content_data = json.load(f)
                    content_count = sum(len(items) for items in content_data.values())
                    total_content_items += content_count
                    logger.info(f"Domain {domain}: {content_count} content items")
                except Exception as e:
                    logger.warning(f"Could not read content for {domain}: {e}")

            intelligence_file = domain_dir / "intelligence.json"
            if intelligence_file.exists():
                total_intelligence_bundles += 1
                logger.info(f"Domain {domain}: 1 intelligence bundle")

        logger.info(f"Dry run complete: {total_content_items} content items, {total_intelligence_bundles} intelligence bundles")


def main():
    """Main entry point for migration script."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate business intelligence data to PostgreSQL")
    parser.add_argument("--data-dir", default="pipeline/business_data", help="Business data directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without actually migrating")
    parser.add_argument("--force", action="store_true", help="Force migration even if data exists")

    args = parser.parse_args()

    try:
        migrator = BusinessDataMigrator(args.data_dir)

        if args.dry_run:
            migrator.dry_run()
        else:
            migrator.migrate_all_data()

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
