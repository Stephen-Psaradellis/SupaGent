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
