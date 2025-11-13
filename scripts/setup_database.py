#!/usr/bin/env python3
"""
Database setup and migration script for Railway deployment.

This script initializes the database tables and migrates existing business intelligence data.
Only runs if the database is not already set up or migration is needed.
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import create_tables, health_check, get_db_session
from core.models import BusinessDomain
from tools.migrate_business_data import BusinessDataMigrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def is_database_setup():
    """Check if database is already set up and has tables."""
    try:
        with get_db_session() as session:
            # Check if tables exist by trying to query
            session.query(BusinessDomain).limit(1).all()
        return True
    except Exception:
        return False


def needs_migration():
    """Check if migration is needed (file data exists but database is empty)."""
    try:
        # Check if there's data to migrate
        data_dir = Path(__file__).parent.parent / "pipeline" / "business_data"
        if not data_dir.exists():
            return False

        # Check for content files
        has_content_files = any((data_dir / d).glob("content.json")
                              for d in data_dir.iterdir() if d.is_dir())

        if not has_content_files:
            return False

        # Check if database is empty
        with get_db_session() as session:
            domain_count = session.query(BusinessDomain).count()
            return domain_count == 0

    except Exception:
        return False


def main():
    """Main setup function - only runs if necessary."""
    logger.info("🔍 Checking SupaGent database status...")

    # Check if DATABASE_URL is configured
    import os
    if not os.getenv("DATABASE_URL"):
        logger.info("⏭️  DATABASE_URL not configured, skipping database setup")
        return

    # Test database connection
    logger.info("🔍 Testing database connection...")
    if not health_check():
        logger.error("❌ Database connection failed. Check your DATABASE_URL.")
        sys.exit(1)

    logger.info("✅ Database connection successful")

    # Check if database is already set up
    if is_database_setup():
        logger.info("✅ Database tables already exist")

        # Check if migration is needed
        if needs_migration():
            logger.info("📦 File data found, running migration...")
            try:
                migrator = BusinessDataMigrator()
                total_migrated = migrator.migrate_all_data()
                logger.info(f"✅ Migration complete! Migrated {total_migrated} total items")
            except Exception as e:
                logger.error(f"❌ Migration failed: {e}")
                sys.exit(1)
        else:
            logger.info("✅ No migration needed - database is up to date")
    else:
        logger.info("📋 Database tables not found, creating them...")
        try:
            create_tables()
            logger.info("✅ Database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            sys.exit(1)

        # Always migrate after creating tables
        logger.info("📦 Migrating existing business intelligence data...")
        try:
            migrator = BusinessDataMigrator()
            total_migrated = migrator.migrate_all_data()
            logger.info(f"✅ Migration complete! Migrated {total_migrated} total items")
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            sys.exit(1)

    logger.info("🎉 Database is ready!")


if __name__ == "__main__":
    main()
