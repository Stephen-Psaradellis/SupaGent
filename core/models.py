"""
SQLAlchemy models for business intelligence data storage.

Provides database persistence for scraped content, business intelligence,
and related metadata in PostgreSQL.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from cryptography.fernet import Fernet
import os
from typing import ClassVar

Base = declarative_base()


class BusinessDomain(Base):
    """Represents a business domain that has been processed for intelligence."""

    __tablename__ = "business_domains"

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    scraped_contents = relationship("ScrapedContent", back_populates="business_domain", cascade="all, delete-orphan")
    intelligence_bundles = relationship("IntelligenceBundle", back_populates="business_domain", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<BusinessDomain(domain='{self.domain}')>"


class ScrapedContent(Base):
    """Represents scraped content from a business website."""

    __tablename__ = "scraped_contents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer, ForeignKey("business_domains.id"), nullable=False, index=True)

    # Content metadata
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), nullable=False, index=True)  # 'about', 'services', 'team', 'blog', 'general'
    metadata_json = Column(JSON, nullable=True)  # Scraping metadata

    # Timestamps
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_domain = relationship("BusinessDomain", back_populates="scraped_contents")

    # Indexes
    __table_args__ = (
        Index('idx_scraped_content_domain_type', 'domain_id', 'content_type'),
        Index('idx_scraped_content_url', 'url'),
    )

    def __repr__(self) -> str:
        return f"<ScrapedContent(url='{self.url[:50]}...', type='{self.content_type}')>"


class IntelligenceBundle(Base):
    """Represents a complete intelligence bundle for a lead/domain."""

    __tablename__ = "intelligence_bundles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer, ForeignKey("business_domains.id"), nullable=False, index=True)

    # Lead information
    lead_name = Column(String(255), nullable=True)
    lead_title = Column(String(255), nullable=True)
    lead_company = Column(String(255), nullable=True)
    lead_industry = Column(String(255), nullable=True)
    lead_location = Column(String(255), nullable=True)
    lead_email = Column(String(255), nullable=True)
    lead_phone = Column(String(50), nullable=True)
    lead_score = Column(String(10), nullable=True)  # Stored as string to preserve precision
    lead_source = Column(String(100), nullable=True)

    # Intelligence data (stored as JSON for flexibility)
    lead_profile = Column(JSON, nullable=True)
    metadata_insights = Column(JSON, nullable=True)
    hunter_enrichment = Column(JSON, nullable=True)
    content_summaries = Column(JSON, nullable=True)
    content_highlights = Column(JSON, nullable=True)
    keyword_signals = Column(JSON, nullable=True)
    online_presence = Column(JSON, nullable=True)
    llm_digest = Column(Text, nullable=True)

    # Content sources (references to scraped content)
    content_sources = Column(JSON, nullable=True)

    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_domain = relationship("BusinessDomain", back_populates="intelligence_bundles")

    # Indexes
    __table_args__ = (
        Index('idx_intelligence_bundle_lead_name', 'lead_name'),
        Index('idx_intelligence_bundle_lead_email', 'lead_email'),
        Index('idx_intelligence_bundle_generated_at', 'generated_at'),
    )

    def __repr__(self) -> str:
        return f"<IntelligenceBundle(domain_id={self.domain_id}, lead='{self.lead_name}')>"


class HunterEnrichment(Base):
    """Stores Hunter.io enrichment data for domains."""

    __tablename__ = "hunter_enrichments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer, ForeignKey("business_domains.id"), nullable=False, index=True)

    # Hunter.io data
    domain_search_data = Column(JSON, nullable=True)
    email_finder_data = Column(JSON, nullable=True)

    # Metadata
    enrichment_type = Column(String(50), nullable=False)  # 'domain_search', 'email_finder'
    target_email = Column(String(255), nullable=True)  # For email finder requests
    target_first_name = Column(String(100), nullable=True)
    target_last_name = Column(String(100), nullable=True)

    # Timestamps
    enriched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    business_domain = relationship("BusinessDomain", back_populates="hunter_enrichments")

    # Indexes
    __table_args__ = (
        Index('idx_hunter_enrichment_domain_type', 'domain_id', 'enrichment_type'),
        Index('idx_hunter_enrichment_target_email', 'target_email'),
    )

    def __repr__(self) -> str:
        return f"<HunterEnrichment(domain_id={self.domain_id}, type='{self.enrichment_type}')>"


# Add the hunter_enrichments relationship to BusinessDomain
BusinessDomain.hunter_enrichments = relationship("HunterEnrichment", back_populates="business_domain", cascade="all, delete-orphan")


class GoogleTokens(Base):
    """Stores encrypted Google OAuth2 tokens for secure token management.

    All token fields are encrypted before storage to protect sensitive data.
    """

    __tablename__ = "google_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(50), nullable=False, index=True)  # 'calendar', 'sheets', etc.
    access_token = Column(Text, nullable=False)  # Encrypted
    refresh_token = Column(Text, nullable=True)  # Encrypted
    token_expiry = Column(DateTime, nullable=True)
    token_type = Column(String(50), nullable=True)  # Usually 'Bearer'
    scope = Column(Text, nullable=True)  # Space-separated scopes

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Cache for generated encryption key to ensure consistency
    _cached_encryption_key: ClassVar[Optional[bytes]] = None

    # Indexes
    __table_args__ = (
        Index('idx_google_tokens_service', 'service_name'),
        Index('idx_google_tokens_expiry', 'token_expiry'),
    )

    @classmethod
    def _get_encryption_key(cls) -> bytes:
        """Get or create encryption key for token storage.

        Caches the generated key to ensure encryption/decryption consistency.
        """
        # First check environment variable
        key = os.getenv("GOOGLE_TOKEN_ENCRYPTION_KEY")
        if key:
            return key.encode() if isinstance(key, str) else key

        # Use cached key if available
        if cls._cached_encryption_key is not None:
            return cls._cached_encryption_key

        # Generate new key and cache it
        generated_key = Fernet.generate_key()
        cls._cached_encryption_key = generated_key

        # Only show warning on first generation
        if not hasattr(cls, '_warned_about_key_generation'):
            key_str = generated_key.decode()
            print(f"⚠️  WARNING: Generated new encryption key: {key_str}")
            print("Set GOOGLE_TOKEN_ENCRYPTION_KEY environment variable for production")
            cls._warned_about_key_generation = True

        return generated_key

    def encrypt_token(self, token: str) -> str:
        """Encrypt a token for storage."""
        if not token:
            raise ValueError("Cannot encrypt empty or None token")
        f = Fernet(self._get_encryption_key())
        return f.encrypt(token.encode()).decode()

    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a stored token."""
        if not encrypted_token:
            return encrypted_token
        f = Fernet(self._get_encryption_key())
        return f.decrypt(encrypted_token.encode()).decode()

    def set_access_token(self, token: str):
        """Set and encrypt access token."""
        if not token:
            raise ValueError("Access token cannot be empty or None")
        self.access_token = self.encrypt_token(token)

    def get_access_token(self) -> str:
        """Get and decrypt access token."""
        return self.decrypt_token(self.access_token)

    def set_refresh_token(self, token: str):
        """Set and encrypt refresh token."""
        self.refresh_token = self.encrypt_token(token) if token else None

    def get_refresh_token(self) -> str:
        """Get and decrypt refresh token."""
        return self.decrypt_token(self.refresh_token) if self.refresh_token else None

    def __repr__(self) -> str:
        return f"<GoogleTokens(service='{self.service_name}', expiry={self.token_expiry})>"
