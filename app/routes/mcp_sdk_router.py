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

from app.routes.mcp_sdk import server, MCP_AUTH_REQUIRED, MCP_AUTH_TOKEN

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
                "params": {}
            }
            yield f"data: {json.dumps(init_msg)}\n\n"
            logger.info("Sent SSE initialization notification")
            
            # Keep connection alive with periodic keepalives
            import asyncio
            keepalive_count = 0
            while True:
                await asyncio.sleep(5)
                keepalive_count += 1
                if keepalive_count % 12 == 0:
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
            
            # Get tools from the SDK server
            tools = []
            for tool_name, tool_func in server._tool_handlers.items():
                import inspect
                sig = inspect.signature(tool_func)
                
                properties = {}
                required = []
                
                for param_name, param in sig.parameters.items():
                    param_type = param.annotation
                    
                    if param_type == str:
                        properties[param_name] = {"type": "string"}
                    elif param_type == int:
                        properties[param_name] = {"type": "integer"}
                    elif param_type == bool:
                        properties[param_name] = {"type": "boolean"}
                    elif param_type == float:
                        properties[param_name] = {"type": "number"}
                    elif hasattr(param_type, "__origin__"):
                        origin = param_type.__origin__
                        if origin is list:
                            properties[param_name] = {"type": "array"}
                        elif origin is dict:
                            properties[param_name] = {"type": "object"}
                    else:
                        properties[param_name] = {"type": "string"}
                    
                    if tool_func.__doc__:
                        properties[param_name]["description"] = f"Parameter: {param_name}"
                    
                    if param.default == inspect.Parameter.empty and not (
                        hasattr(param_type, "__origin__") and 
                        param_type.__origin__ is type(Optional)
                    ):
                        required.append(param_name)
                
                tool_schema = {
                    "name": tool_name,
                    "description": tool_func.__doc__ or f"Tool: {tool_name}",
                    "inputSchema": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
                tools.append(tool_schema)
            
            logger.info(f"Returning {len(tools)} tools from SDK")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": tools
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
    return {
        "status": "healthy",
        "server_name": server.name,
        "sdk_version": "official",
        "tool_count": len(server._tool_handlers),
        "tools": list(server._tool_handlers.keys())
    }
