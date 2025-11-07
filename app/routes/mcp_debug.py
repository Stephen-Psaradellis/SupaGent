"""
Debug endpoint for MCP connection testing.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp-debug", tags=["mcp-debug"])


@router.get("/test")
async def test_mcp_connection(request: Request) -> Dict[str, Any]:
    """Test endpoint to check MCP server connectivity."""
    return {
        "status": "ok",
        "endpoint": "/mcp",
        "client_ip": request.client.host if request.client else "unknown",
        "headers": dict(request.headers),
        "message": "MCP server is reachable"
    }


@router.get("/logs")
async def get_recent_logs() -> Dict[str, Any]:
    """Get recent MCP-related logs (if we implement log storage)."""
    # This would require implementing log storage
    return {
        "message": "Log storage not implemented. Check application logs.",
        "note": "Recent MCP requests should appear in application logs"
    }


@router.post("/echo")
async def echo_request(
    request: Request,
    request_body: Dict[str, Any],
) -> Dict[str, Any]:
    """Echo back the request to see what ElevenLabs is sending."""
    logger.info(f"Echo request from {request.client.host if request.client else 'unknown'}")
    logger.info(f"Request body: {json.dumps(request_body, indent=2)}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    return {
        "echo": True,
        "received": request_body,
        "headers": dict(request.headers),
        "client_ip": request.client.host if request.client else "unknown"
    }

