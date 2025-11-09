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
    Create the MCP ASGI app using the SDK's built-in Streamable HTTP transport.

    The SDK handles all MCP protocol compliance, tool discovery, and transport automatically.
    """
    # Configure the server for Streamable HTTP transport (supports both SSE and HTTP POST)
    mcp_app = server.streamable_http_app()

    # Add synchronous endpoint for ElevenLabs compatibility
    from starlette.responses import JSONResponse

    # Create a wrapper ASGI app that handles both SSE and sync endpoints
    async def mcp_wrapper(scope, receive, send):
        if scope["type"] == "http" and scope["method"] == "POST":
            path = scope["path"]
            if path == "/tools/list":
                # Handle synchronous tools/list request for ElevenLabs
                try:
                    # Read the request body
                    body = await receive_body(receive)
                    import json
                    request_data = json.loads(body.decode())

                    if request_data.get("method") == "tools/list":
                        # Get tools synchronously
                        tools = await server.list_tools()
                        tool_list = []

                        for tool in tools:
                            tool_info = {
                                "name": tool.name,
                                "description": tool.description or "",
                            }

                            # Add input schema if available
                            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                                tool_info["inputSchema"] = tool.inputSchema
                            elif hasattr(tool, 'parameters') and tool.parameters:
                                tool_info["inputSchema"] = tool.parameters

                            tool_list.append(tool_info)

                        response = {
                            "jsonrpc": "2.0",
                            "id": request_data.get("id"),
                            "result": {
                                "tools": tool_list
                            }
                        }

                        # Send synchronous response
                        await send({
                            "type": "http.response.start",
                            "status": 200,
                            "headers": [(b"content-type", b"application/json")],
                        })
                        await send({
                            "type": "http.response.body",
                            "body": json.dumps(response).encode(),
                        })
                        return
                except Exception as e:
                    logger.error(f"Error in sync MCP endpoint: {e}")
                    # Send error response
                    await send({
                        "type": "http.response.start",
                        "status": 500,
                        "headers": [(b"content-type", b"application/json")],
                    })
                    await send({
                        "type": "http.response.body",
                        "body": json.dumps({"error": str(e)}).encode(),
                    })
                    return

        # For all other requests, use the normal MCP app
        await mcp_app(scope, receive, send)

    return mcp_wrapper


async def receive_body(receive):
    """Helper to read the full request body."""
    body = b""
    while True:
        message = await receive()
        if message["type"] == "http.request":
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break
        elif message["type"] == "http.disconnect":
            break
    return body

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
