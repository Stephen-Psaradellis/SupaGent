"""
Database connection and session management for PostgreSQL.

Provides SQLAlchemy engine, session factory, and utility functions
for database operations in the business intelligence system.
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from core.config import get_config
from core.models import Base

logger = logging.getLogger(__name__)

# Global variables for engine and session factory
_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


def get_engine() -> Engine:
    """Get the SQLAlchemy engine instance.

    Creates the engine on first call using the configured DATABASE_URL.

    Returns:
        SQLAlchemy Engine instance.

    Raises:
        ValueError: If DATABASE_URL is not configured.
    """
    global _engine
    if _engine is None:
        config = get_config()
        if not config.database_url:
            raise ValueError(
                "DATABASE_URL not configured. Please set the DATABASE_URL "
                "environment variable to your Railway Postgres connection string."
            )

        # Configure engine with PostgreSQL-specific settings
        connect_args = {}
        if config.is_railway():
            # Railway uses connection pooling with SSL
            connect_args = {"sslmode": "require"}
        # For all PostgreSQL connections, use standard settings

        _engine = create_engine(
            config.database_url,
            pool_pre_ping=True,  # Test connections before use
            pool_recycle=300,    # Recycle connections every 5 minutes
            echo=False,          # Set to True for SQL query logging in development
            connect_args=connect_args,
        )

        logger.info("Database engine created successfully")

    return _engine


def get_session_factory() -> sessionmaker:
    """Get the session factory.

    Returns:
        SQLAlchemy sessionmaker instance.
    """
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            class_=Session,
            expire_on_commit=False,  # Don't expire objects after commit
        )
    return _session_factory


def create_tables() -> None:
    """Create all database tables.

    This should be called once during application startup.
    In production, consider using Alembic migrations instead.
    """
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def drop_tables() -> None:
    """Drop all database tables.

    WARNING: This will delete all data. Use with caution.
    """
    try:
        engine = get_engine()
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions.

    Provides a transactional session that automatically commits on success
    and rolls back on exception.

    Yields:
        SQLAlchemy Session instance.

    Example:
        with get_db_session() as session:
            # Use session for database operations
            session.query(SomeModel).all()
    """
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def health_check() -> bool:
    """Perform a database health check.

    Returns:
        True if database is accessible, False otherwise.
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def reset_engine() -> None:
    """Reset the global engine instance.

    Useful for testing or when database configuration changes.
    """
    global _engine, _session_factory
    if _engine:
        _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database engine reset")


# Database table initialization is handled by the application startup process
# This prevents issues during Docker build when DATABASE_URL may not be available
# Tables will be created when the FastAPI app starts up
