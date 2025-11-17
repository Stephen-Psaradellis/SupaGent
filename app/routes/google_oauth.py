"""
Google OAuth2 endpoints for secure authentication flow.

Provides /oauth/start and /oauth/callback endpoints for Google OAuth2 flow
without requiring filesystem-based credentials.
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from core.google_oauth_manager import get_calendar_oauth_manager

# Scopes required for Calendar API
CALENDAR_SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events'
]

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get("/start")
async def oauth_start():
    """Initiate Google OAuth2 authorization flow.

    Returns:
        Redirect to Google OAuth consent screen
    """
    try:
        oauth_manager = get_calendar_oauth_manager()

        # Generate authorization URL
        auth_url = oauth_manager.get_authorization_url(CALENDAR_SCOPES)

        logger.info("🔗 Generated OAuth authorization URL")
        return RedirectResponse(url=auth_url)

    except ValueError as e:
        logger.error(f"❌ OAuth configuration error: {e}")
        raise HTTPException(
            status_code=500,
            detail="OAuth configuration incomplete. Check environment variables."
        )
    except Exception as e:
        logger.error(f"❌ Failed to start OAuth flow: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initiate OAuth flow"
        )


@router.get("/callback")
async def oauth_callback(request: Request, code: str = None, error: str = None):
    """Handle Google OAuth2 callback and exchange code for tokens.

    Args:
        code: Authorization code from Google
        error: Error parameter if OAuth failed

    Returns:
        Success message or error response
    """
    try:
        # Check for OAuth errors
        if error:
            logger.error(f"❌ OAuth error: {error}")
            raise HTTPException(
                status_code=400,
                detail=f"OAuth authorization failed: {error}"
            )

        if not code:
            logger.error("❌ No authorization code received")
            raise HTTPException(
                status_code=400,
                detail="No authorization code received"
            )

        oauth_manager = get_calendar_oauth_manager()

        # Exchange authorization code for tokens
        logger.info("🔄 Exchanging authorization code for tokens...")
        creds = oauth_manager.exchange_code_for_tokens(code, CALENDAR_SCOPES)

        # Save tokens to database
        logger.info("💾 Saving tokens to database...")
        oauth_manager.save_tokens(creds)

        logger.info("✅ OAuth authorization completed successfully")
        return {
            "message": "Authorization complete",
            "status": "success",
            "service": "google_calendar"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ OAuth callback failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to complete OAuth authorization"
        )


@router.get("/status")
async def oauth_status():
    """Check OAuth authentication status.

    Returns:
        Authentication status for Google Calendar
    """
    try:
        oauth_manager = get_calendar_oauth_manager()
        is_authenticated = oauth_manager.is_authenticated()

        return {
            "authenticated": is_authenticated,
            "service": "google_calendar",
            "message": "Authenticated" if is_authenticated else "Not authenticated"
        }

    except Exception as e:
        logger.error(f"❌ Failed to check auth status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to check authentication status"
        )


@router.post("/clear")
async def oauth_clear():
    """Clear stored OAuth tokens (for testing/debugging).

    Returns:
        Success message
    """
    try:
        oauth_manager = get_calendar_oauth_manager()
        cleared = oauth_manager.clear_tokens()

        if cleared:
            logger.info("🗑️  Cleared stored OAuth tokens")
            return {"message": "Tokens cleared successfully"}
        else:
            return {"message": "No tokens found to clear"}

    except Exception as e:
        logger.error(f"❌ Failed to clear tokens: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear tokens"
        )
