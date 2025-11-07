"""
Configuration and ElevenLabs setup routes.
"""
from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Request

from app.dependencies import ConfigDep

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/eleven")
def eleven_config(
    request: Request,
    config: ConfigDep,
) -> Dict[str, Any]:
    """Get ElevenLabs configuration status."""
    err = getattr(request.app.state, "_agent_error", None)
    mcp_server_id = config.elevenlabs_mcp_server_id or getattr(request.app.state, "_mcp_server_id", None)
    mcp_error = getattr(request.app.state, "_mcp_server_error", None)
    
    return {
        "agent_id": config.elevenlabs_agent_id,
        "has_key": bool(config.elevenlabs_api_key),
        "status": "ok" if config.elevenlabs_agent_id else "missing",
        "error": err,
        "mcp_server": {
            "id": mcp_server_id,
            "endpoint": config.get_mcp_endpoint(),
            "tool_endpoint": config.get_tool_endpoint(),
            "error": mcp_error,
            "status": "configured" if mcp_server_id else "not_configured"
        }
    }


@router.post("/eleven/configure_mcp")
def configure_mcp_endpoint(
    request: Request,
    config: ConfigDep,
) -> Dict[str, Any]:
    """Manually trigger MCP server creation/registration with ElevenLabs."""
    if not config.elevenlabs_api_key:
        return {"success": False, "error": "ELEVENLABS_API_KEY not set in Doppler"}
    
    # Get the create_or_get_mcp_server function from app state
    create_or_get_mcp_server = getattr(request.app.state, "_create_or_get_mcp_server", None)
    if not create_or_get_mcp_server:
        return {"success": False, "error": "MCP server creation function not available. Restart the app to initialize."}
    
    mcp_server_id = create_or_get_mcp_server()
    if mcp_server_id:
        return {
            "success": True,
            "message": "MCP server configured successfully",
            "mcp_server_id": mcp_server_id
        }
    else:
        error = getattr(request.app.state, "_mcp_server_error", None)
        return {
            "success": False,
            "error": error or "Failed to create/register MCP server. Check API key and network connectivity."
        }

