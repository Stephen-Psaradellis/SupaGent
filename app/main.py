"""
Main FastAPI application entry point.

This module is now minimal and focused on app creation and route registration.
All route handlers are organized in the app/routes/ directory.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from core.config import get_config
from core.di import create_container
from core.http_client import HTTPClientManager
from app.setup import setup_elevenlabs_mcp_server, setup_elevenlabs_agent
from app.routes import register_routes


def build_app() -> FastAPI:
    """Build and configure the FastAPI application.
    
    Uses the new service container architecture for better
    dependency management and testability.
    
    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(title="SupaGent Support Agent")
    
    # Initialize configuration and service container
    config = get_config()
    container = create_container(config)
    
    # Store container and config in app state for access in endpoints
    app.state.container = container
    app.state.config = config
    
    # Initialize legacy components for backward compatibility
    # (stored on app.state for hot-reload capability)
    app.state.store = container.get("vector_store")
    app.state.mcp = container.get("mcp_client")
    app.state.rag = container.get("rag")
    app.state.sessions = container.get("sessions")
    app.state.analytics = container.get("analytics")
    app.state.escalations = container.get("escalations")
    app.state.compliance = container.get("compliance")
    app.state.crm = container.get("crm")
    
    # Store services
    app.state.conversation_service = container.get("conversation_service")
    app.state.voice_service = container.get("voice_service")
    
    # Setup ElevenLabs integration
    setup_elevenlabs_mcp_server(app, config)
    setup_elevenlabs_agent(app, config)
    
    # Static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    # Demo redirect
    @app.get("/demo")
    def demo_redirect():
        return RedirectResponse(url="/static/demo.html")
    
    # Register all routes
    register_routes(app)
    
    # Cleanup on shutdown
    @app.on_event("shutdown")
    def shutdown_event():
        """Cleanup resources on application shutdown."""
        HTTPClientManager.close_all()
    
    return app


app = build_app()
