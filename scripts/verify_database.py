#!/usr/bin/env python3
"""
Verification script for database integration.

Tests that business intelligence data is properly stored and retrievable from PostgreSQL.
"""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import health_check, get_db_session
from core.models import BusinessDomain, ScrapedContent, IntelligenceBundle


def verify_database_setup():
    """Verify database setup and data migration."""
    import os

    if not os.getenv("DATABASE_URL"):
        print("⏭️  DATABASE_URL not configured, skipping database verification")
        return True

    print("🔍 Verifying database setup...")

    # Check database connection
    if not health_check():
        print("❌ Database connection failed")
        return False

    print("✅ Database connection successful")

    # Check tables exist
    with get_db_session() as session:
        try:
            # Count domains
            domain_count = session.query(BusinessDomain).count()
            print(f"📊 Business domains: {domain_count}")

            # Count scraped content
            content_count = session.query(ScrapedContent).count()
            print(f"📄 Scraped content items: {content_count}")

            # Count intelligence bundles
            bundle_count = session.query(IntelligenceBundle).count()
            print(f"🧠 Intelligence bundles: {bundle_count}")

            # Show sample data
            if domain_count > 0:
                sample_domain = session.query(BusinessDomain).first()
                print(f"🎯 Sample domain: {sample_domain.domain}")

                content_sample = session.query(ScrapedContent.content_type).filter_by(
                    domain_id=sample_domain.id
                ).distinct().all()
                print(f"📋 Content types: {[ct[0] for ct in content_sample]}")

                # Check recent activity
                recent_bundle = session.query(IntelligenceBundle).filter_by(
                    domain_id=sample_domain.id
                ).order_by(IntelligenceBundle.generated_at.desc()).first()

                if recent_bundle:
                    print(f"📅 Last intelligence update: {recent_bundle.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")

        except Exception as e:
            print(f"❌ Database query failed: {e}")
            return False

    print("✅ Database verification complete!")
    return True


def test_business_intelligence_loader():
    """Test that the business intelligence loader works with database."""
    print("\n🔍 Testing BusinessIntelligenceLoader...")

    try:
        from pipeline.business_intelligence import BusinessIntelligenceLoader

        loader = BusinessIntelligenceLoader()

        # Test with a known domain that should have data
        with get_db_session() as session:
            sample_domain = session.query(BusinessDomain).first()
            if sample_domain:
                print(f"🧪 Testing loader with domain: {sample_domain.domain}")
                data = loader.load_business_data(sample_domain.domain, max_pages=1)
                print(f"✅ Loaded {sum(len(items) for items in data.values())} content items")
                print(f"📋 Content types: {list(data.keys())}")
            else:
                print("⚠️  No domains found in database")

    except Exception as e:
        print(f"❌ BusinessIntelligenceLoader test failed: {e}")
        return False

    print("✅ BusinessIntelligenceLoader test passed!")
    return True


if __name__ == "__main__":
    success = verify_database_setup()
    if success:
        test_business_intelligence_loader()
    else:
        sys.exit(1)
