"""
Route modules for the SupaGent application.
"""
from fastapi import APIRouter

from app.routes import (
    query,
    voice,
    admin,
    test,
    mcp_sdk_router,  # Official MCP SDK-based implementation
    mcp_debug,
    tools,
    analytics,
    feedback,
    escalations,
    crm,
    compliance,
    agent_tests,
    config,
)

def register_routes(router: APIRouter) -> None:
    """Register all route modules with the main router.
    
    Args:
        router: Main FastAPI router or app instance.
    """
    router.include_router(config.router, tags=["config"])
    router.include_router(query.router, tags=["query"])
    router.include_router(voice.router, tags=["voice"])
    router.include_router(admin.router, tags=["admin"])
    router.include_router(test.router, tags=["test"])
    router.include_router(mcp_sdk_router.router, tags=["mcp"])  # SDK-based MCP endpoint
    router.include_router(mcp_debug.router, tags=["mcp-debug"])
    router.include_router(tools.router, tags=["tools"])
    router.include_router(analytics.router, tags=["analytics"])
    router.include_router(feedback.router, tags=["feedback"])
    router.include_router(escalations.router, tags=["escalations"])
    router.include_router(crm.router, tags=["crm"])
    router.include_router(compliance.router, tags=["compliance"])
    router.include_router(agent_tests.router, tags=["agent-tests"])

