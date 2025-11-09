"""
FastAPI integration for MCP SDK server.

Uses the official MCP Python SDK's built-in Streamable HTTP transport
for automatic MCP protocol handling.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import Request, Response

from app.routes.mcp_sdk import server, MCP_AUTH_REQUIRED, MCP_AUTH_TOKEN

logger = logging.getLogger(__name__)


def create_mcp_app():
    """
    Create the MCP ASGI app using the SDK's built-in SSE transport.

    The SDK handles all MCP protocol compliance, tool discovery, and transport automatically.
    """
    # Configure the server for SSE transport
    mcp_app = server.sse_app()

    # Also create a synchronous HTTP endpoint for ElevenLabs compatibility
    from fastapi import APIRouter, HTTPException
    from fastapi.responses import JSONResponse
    import json

    sync_router = APIRouter()

    @sync_router.post("/tools/list")
    async def sync_tools_list():
        """Synchronous endpoint for ElevenLabs tool discovery."""
        try:
            tools = await server.list_tools()
            tool_list = []
            for tool in tools:
                tool_list.append({
                    "name": tool.name,
                    "description": tool.description or "",
                    "inputSchema": tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                })

            return {
                "jsonrpc": "2.0",
                "id": None,  # ElevenLabs doesn't send an ID
                "result": {
                    "tools": tool_list
                }
            }
        except Exception as e:
            logger.error(f"Error in sync tools list: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Mount the sync router
    from starlette.middleware.base import BaseHTTPMiddleware

    class SyncMCPMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            # Intercept requests to /mcp/tools/list and route to sync endpoint
            if request.url.path == "/mcp/tools/list":
                # Parse JSON body
                try:
                    body = await request.json()
                    if body.get("method") == "tools/list":
                        # Return sync response
                        tools = await server.list_tools()
                        tool_list = []
                        for tool in tools:
                            tool_list.append({
                                "name": tool.name,
                                "description": tool.description or "",
                                "inputSchema": tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                            })

                        return JSONResponse({
                            "jsonrpc": "2.0",
                            "id": body.get("id"),
                            "result": {
                                "tools": tool_list
                            }
                        })
                except Exception as e:
                    logger.error(f"Error in sync middleware: {e}")
                    pass

            return await call_next(request)

    # Wrap the app with sync middleware
    mcp_app = SyncMCPMiddleware(mcp_app)

    # Add authentication middleware if required
    if MCP_AUTH_REQUIRED and MCP_AUTH_TOKEN:

        async def auth_middleware(request: Request, call_next):
            """Validate MCP authorization token."""
            authorization = request.headers.get("Authorization")

            if not authorization:
                return Response(
                    status_code=401,
                    content='{"error": "Missing authorization token"}',
                    media_type="application/json"
                )

            if not authorization.startswith("Bearer "):
                return Response(
                    status_code=401,
                    content='{"error": "Invalid authorization format"}',
                    media_type="application/json"
                )

            token = authorization[7:].strip()
            if token != MCP_AUTH_TOKEN:
                return Response(
                    status_code=401,
                    content='{"error": "Invalid authorization token"}',
                    media_type="application/json"
                )

            return await call_next(request)

        # Wrap the MCP app with authentication
        from starlette.middleware.base import BaseHTTPMiddleware

        class AuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                return await auth_middleware(request, call_next)

        mcp_app = AuthMiddleware(mcp_app)

    return mcp_app


# Create the MCP ASGI app instance
mcp_app = create_mcp_app()
