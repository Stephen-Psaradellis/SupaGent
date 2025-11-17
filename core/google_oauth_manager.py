"""
Google OAuth2 Token Manager for Railway Deployment.

Handles secure token storage and retrieval from PostgreSQL database,
with automatic token refresh functionality.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import sessionmaker, Session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from core.models import GoogleTokens
from core.database import get_engine


class GoogleOAuthManager:
    """Manages Google OAuth2 tokens stored in database."""

    def __init__(self, service_name: str = "calendar"):
        """Initialize OAuth manager for a specific service.

        Args:
            service_name: The Google service name (e.g., 'calendar', 'sheets')
        """
        self.service_name = service_name
        self._session_factory = sessionmaker(bind=get_engine())

    def get_stored_tokens(self) -> Optional[GoogleTokens]:
        """Retrieve stored tokens from database.

        Returns:
            GoogleTokens instance if found, None otherwise
        """
        with self._session_factory() as session:
            return session.query(GoogleTokens).filter_by(
                service_name=self.service_name
            ).first()

    def save_tokens(self, creds: Credentials) -> GoogleTokens:
        """Save OAuth2 credentials to database.

        Args:
            creds: Google OAuth2 credentials object

        Returns:
            The saved GoogleTokens instance
        """
        with self._session_factory() as session:
            # Check if tokens already exist for this service
            existing = session.query(GoogleTokens).filter_by(
                service_name=self.service_name
            ).first()

            if existing:
                # Update existing tokens
                existing.set_access_token(creds.token)
                existing.set_refresh_token(creds.refresh_token)
                existing.token_expiry = creds.expiry
                existing.token_type = creds.token_type or "Bearer"
                existing.scope = " ".join(creds.scopes) if creds.scopes else None
                existing.updated_at = datetime.utcnow()
                token_record = existing
            else:
                # Create new token record
                token_record = GoogleTokens(
                    service_name=self.service_name,
                    token_type=creds.token_type or "Bearer",
                    scope=" ".join(creds.scopes) if creds.scopes else None
                )
                token_record.set_access_token(creds.token)
                token_record.set_refresh_token(creds.refresh_token)
                token_record.token_expiry = creds.expiry
                session.add(token_record)

            session.commit()
            return token_record

    def get_credentials(self) -> Optional[Credentials]:
        """Get Google OAuth2 credentials from database.

        Returns:
            Credentials object if valid tokens exist, None otherwise
        """
        token_record = self.get_stored_tokens()
        if not token_record:
            return None

        # Create credentials object from stored data
        creds = Credentials(
            token=token_record.get_access_token(),
            refresh_token=token_record.get_refresh_token(),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            scopes=token_record.scope.split() if token_record.scope else None
        )
        creds.expiry = token_record.token_expiry

        # Check if token needs refresh
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed tokens
                self.save_tokens(creds)
            except Exception:
                # If refresh fails, return None to trigger re-auth
                return None

        return creds

    def clear_tokens(self) -> bool:
        """Clear stored tokens for this service.

        Returns:
            True if tokens were cleared, False if no tokens existed
        """
        with self._session_factory() as session:
            token_record = session.query(GoogleTokens).filter_by(
                service_name=self.service_name
            ).first()

            if token_record:
                session.delete(token_record)
                session.commit()
                return True
            return False

    def is_authenticated(self) -> bool:
        """Check if valid tokens exist for this service.

        Returns:
            True if valid tokens exist, False otherwise
        """
        creds = self.get_credentials()
        return creds is not None and not creds.expired

    def get_oauth_flow(self, scopes: list) -> InstalledAppFlow:
        """Create OAuth2 flow using environment variables.

        Args:
            scopes: List of OAuth scopes required

        Returns:
            Configured OAuth2 flow

        Raises:
            ValueError: If required environment variables are missing
        """
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

        if not all([client_id, client_secret, redirect_uri]):
            raise ValueError(
                "Missing required environment variables: "
                "GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI"
            )

        # Create client config from environment variables
        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": [redirect_uri],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }

        return InstalledAppFlow.from_client_config(
            client_config, scopes=scopes, redirect_uri=redirect_uri
        )

    def exchange_code_for_tokens(self, code: str, scopes: list) -> Credentials:
        """Exchange authorization code for access tokens.

        Args:
            code: Authorization code from OAuth callback
            scopes: List of OAuth scopes

        Returns:
            Credentials object with tokens

        Raises:
            Exception: If token exchange fails
        """
        flow = self.get_oauth_flow(scopes)
        flow.fetch_token(code=code)
        return flow.credentials

    def get_authorization_url(self, scopes: list) -> str:
        """Generate OAuth2 authorization URL.

        Args:
            scopes: List of OAuth scopes required

        Returns:
            Authorization URL for user consent
        """
        flow = self.get_oauth_flow(scopes)
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return auth_url


# Convenience functions for common services
def get_google_oauth_manager(service_name: str = "calendar") -> GoogleOAuthManager:
    """Get OAuth manager for a specific Google service.

    Args:
        service_name: The service name ('calendar', 'sheets', etc.)

    Returns:
        GoogleOAuthManager instance
    """
    return GoogleOAuthManager(service_name)


def get_calendar_oauth_manager() -> GoogleOAuthManager:
    """Get OAuth manager for Google Calendar."""
    return get_google_oauth_manager("calendar")


def get_sheets_oauth_manager() -> GoogleOAuthManager:
    """Get OAuth manager for Google Sheets."""
    return get_google_oauth_manager("sheets")
