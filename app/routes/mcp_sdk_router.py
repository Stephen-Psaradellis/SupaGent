"""
FastAPI router integration for MCP SDK server.

This module bridges the official MCP Python SDK with FastAPI,
providing HTTP/SSE transport for the MCP server.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from fastapi import APIRouter, Request, Response, HTTPException, Header
from fastapi.responses import StreamingResponse
from mcp import types

from app.routes.mcp_sdk import server, MCP_AUTH_REQUIRED, MCP_AUTH_TOKEN, list_available_tools

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["mcp"])


def validate_authorization(authorization: Optional[str] = None) -> bool:
    """
    Validate MCP request authorization.
    
    Args:
        authorization: Authorization header value (e.g., "Bearer <token>")
        
    Returns:
        True if authorized, False otherwise
    """
    if not MCP_AUTH_REQUIRED:
        return True
    
    if not MCP_AUTH_TOKEN:
        logger.warning("MCP_AUTH_REQUIRED is true but MCP_AUTH_TOKEN is not set")
        return False
    
    if not authorization:
        return False
    
    if not authorization.startswith("Bearer "):
        return False
    
    token = authorization[7:].strip()
    return token == MCP_AUTH_TOKEN


@router.options("")
async def mcp_options(request: Request) -> Response:
    """Handle CORS preflight requests."""
    logger.info(f"MCP OPTIONS request from {request.client.host if request.client else 'unknown'}")
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600",
        }
    )


@router.get("")
async def mcp_sse(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> Response:
    """
    SSE transport endpoint for MCP SDK.
    
    ElevenLabs and other MCP clients use SSE for real-time bidirectional communication.
    """
    if not validate_authorization(authorization):
        logger.warning(f"Unauthorized MCP GET request from {request.client.host if request.client else 'unknown'}")
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid or missing MCP authorization token"
        )
    
    logger.info(f"MCP SSE connection from {request.client.host if request.client else 'unknown'}")
    
    async def event_stream():
        """Generate SSE events for the MCP session."""
        try:
            # Send initialization notification
            init_msg = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": server.name,
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {},
                        "logging": {}
                    }
                }
            }
            yield f"data: {json.dumps(init_msg)}\n\n"
            logger.info("📤 Sent MCP server initialization via SSE")

            # Get and send tools list
            try:
                tools = await list_available_tools()

                tools_msg = {
                    "jsonrpc": "2.0",
                    "method": "notifications/tools/list_changed",
                    "params": {
                        "tools": [tool.model_dump() for tool in tools]
                    }
                }
                yield f"data: {json.dumps(tools_msg)}\n\n"
                logger.info(f"📤 Sent tools list via SSE ({len(tools)} tools)")
            except Exception as e:
                logger.error(f"Error sending tools list via SSE: {e}", exc_info=True)
                # Send error notification
                error_msg = {
                    "jsonrpc": "2.0",
                    "method": "notifications/tools/list_changed",
                    "params": {
                        "tools": []
                    }
                }
                yield f"data: {json.dumps(error_msg)}\n\n"

            # Keep connection alive with periodic keepalives
            keepalive_count = 0
            while True:
                await asyncio.sleep(15)  # Increased from 5 to 15 seconds
                keepalive_count += 1
                if keepalive_count % 4 == 0:  # Log every minute (15s * 4 = 60s)
                    logger.debug(f"SSE keepalive #{keepalive_count}")
                yield f": keepalive\n\n"
                    
        except Exception as e:
            logger.error(f"Error in MCP SSE stream: {e}", exc_info=True)
            raise
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )


@router.post("")
async def mcp_endpoint(
    request: Request,
    request_body: dict[str, Any],
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict[str, Any]:
    """
    Main MCP protocol endpoint using official SDK.
    """
    client_ip = request.client.host if request.client else "unknown"
    method = request_body.get("method", "unknown")
    request_id = request_body.get("id")
    
    logger.info("=" * 80)
    logger.info(f"🔥 MCP ENDPOINT HIT (SDK)")
    logger.info(f"   Client IP: {client_ip}")
    logger.info(f"   Method: {method}")
    logger.info(f"   Request ID: {request_id}")
    logger.info("=" * 80)
    
    # Validate authorization
    if not validate_authorization(authorization):
        logger.warning(f"Unauthorized MCP POST request from {client_ip}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32000,
                "message": "Unauthorized: Invalid or missing MCP authorization token"
            }
        }
    
    try:
        if method == "initialize":
            logger.info("Handling initialize request via SDK")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": server.name,
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {},
                        "logging": {}
                    }
                }
            }
            
        elif method == "tools/list":
            logger.info("Handling tools/list request via SDK")

            # Get tools from the SDK server's list_tools handler
            try:
                import asyncio
                tools_result = asyncio.run(server.request_handlers[types.ListToolsRequest](None))
                tools = tools_result.root.tools if hasattr(tools_result, 'root') and hasattr(tools_result.root, 'tools') else []

                logger.info(f"Returning {len(tools)} tools from SDK")

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [tool.model_dump() for tool in tools]
                    }
                }
            except Exception as e:
                logger.error(f"Error getting tools list: {e}", exc_info=True)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error listing tools: {str(e)}"
                    }
                }
            
        elif method == "tools/call":
            tool_name = request_body.get("params", {}).get("name")
            arguments = request_body.get("params", {}).get("arguments", {})
            
            logger.info(f"🔧 TOOL INVOCATION via SDK: {tool_name}")
            logger.info(f"   Arguments: {list(arguments.keys())}")
            
            if tool_name not in server._tool_handlers:
                logger.warning(f"Unknown tool requested: {tool_name}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            tool_handler = server._tool_handlers[tool_name]
            
            try:
                result = await tool_handler(**arguments)
                
                logger.info(f"✅ TOOL COMPLETED: {tool_name}")
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [item.model_dump() for item in result]
                    }
                }
                
            except Exception as e:
                logger.error(f"❌ TOOL ERROR: {tool_name} - {e}", exc_info=True)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error executing tool: {str(e)}"
                    }
                }
        
        else:
            logger.warning(f"Unknown method: {method}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


@router.get("/health")
async def mcp_health() -> dict[str, Any]:
    """Health check endpoint for MCP server."""
    try:
        import asyncio
        tools_result = asyncio.run(server.request_handlers[types.ListToolsRequest](None))
        tools = tools_result.root.tools if hasattr(tools_result, 'root') and hasattr(tools_result.root, 'tools') else []
        tool_count = len(tools)
        tool_names = [tool.name for tool in tools]
    except Exception as e:
        logger.error(f"Error getting tools for health check: {e}")
        tool_count = 0
        tool_names = []

    return {
        "status": "healthy",
        "server_name": server.name,
        "sdk_version": "official",
        "tool_count": tool_count,
        "tools": tool_names
    }


@router.get("/debug/tools")
def debug_tools() -> dict[str, Any]:
    """Debug endpoint to test tools retrieval."""
    try:
        import asyncio
        tools = asyncio.run(list_available_tools())
        return {
            "success": True,
            "tool_count": len(tools),
            "tools": [tool.model_dump() for tool in tools]
        }
    except Exception as e:
        logger.error(f"Error in debug tools: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
