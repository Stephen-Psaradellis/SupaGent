"""
MCP (Model Context Protocol) routes.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict
from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse

from app.dependencies import MCPDep

logger = logging.getLogger(__name__)
from app.routes.mcp_handlers import (
    handle_search_knowledge_base,
    handle_create_ticket,
    handle_get_customer,
    handle_escalate,
    handle_log_interaction,
    handle_check_order,
    handle_check_availability,
    handle_get_user_bookings,
    handle_book_appointment,
    handle_modify_appointment,
    handle_cancel_appointment,
    handle_post_call_data,
    handle_get_clients,
    handle_add_clients,
)

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.options("")
async def mcp_endpoint_options(request: Request) -> Response:
    """Handle CORS preflight requests for MCP endpoint."""
    logger.info(f"MCP OPTIONS request from {request.client.host if request.client else 'unknown'}")
    logger.info(f"Headers: {dict(request.headers)}")
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
async def mcp_endpoint_get(
    request: Request,
    mcp: MCPDep = None,
) -> Response:
    """MCP protocol endpoint for SSE (Server-Sent Events) transport.
    
    ElevenLabs uses SSE transport which requires a GET request to establish
    the connection. This endpoint handles the SSE handshake and responds to
    MCP protocol messages.
    """
    # Log the incoming request for debugging
    logger.info(f"MCP GET (SSE) request from {request.client.host if request.client else 'unknown'}")
    logger.info(f"Query params: {dict(request.query_params)}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Check if this is an initialize request (common in MCP SSE)
    # The client may send the initialize request as a query parameter or header
    initialize_request = request.query_params.get("message")
    if initialize_request:
        logger.info(f"Initialize request in query: {initialize_request}")
    
    async def event_stream():
        logger.info("Starting SSE event stream")
        
        # For MCP with SSE transport, the protocol typically works like this:
        # 1. Client connects via GET (this request)
        # 2. Client sends initialize request (usually via POST, but could be in query params)
        # 3. Server responds with initialize result
        # 4. Client requests tools/list
        # 5. Server responds with tools
        
        # Since we can't easily read from SSE stream in FastAPI, we handle requests via POST
        # But we need to send an initial message to indicate the connection is ready
        
        # Send initial connection message in MCP format
        # Some implementations send this, others wait for initialize
        # Let's try sending a minimal ready signal
        try:
            # Wait a brief moment to see if client sends initialize via query param
            import asyncio
            await asyncio.sleep(0.1)
            
            # If there's an initialize request in query params, respond to it
            if initialize_request:
                try:
                    init_data = json.loads(initialize_request)
                    if init_data.get("method") == "initialize":
                        logger.info("Responding to initialize from query params")
                        response = {
                            "jsonrpc": "2.0",
                            "id": init_data.get("id"),
                            "result": {
                                "protocolVersion": "2024-11-05",
                                "serverInfo": {
                                    "name": "SupaGent Knowledge Base",
                                    "version": "1.0.0"
                                },
                                "capabilities": {
                                    "tools": {}
                                }
                            }
                        }
                        yield f"data: {json.dumps(response)}\n\n"
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse initialize request: {e}")
            
            # Send periodic keepalives to maintain the SSE connection
            # The actual MCP protocol messages will be handled via POST requests
            keepalive_count = 0
            while True:
                await asyncio.sleep(10)  # Send keepalive every 10 seconds
                keepalive_count += 1
                if keepalive_count % 6 == 0:  # Log every minute
                    logger.info(f"SSE connection alive, keepalive #{keepalive_count}")
                yield f": keepalive\n\n"
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}", exc_info=True)
            raise
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )


@router.post("")
async def mcp_endpoint(
    request: Request,
    request_body: Dict[str, Any],
    mcp: MCPDep = None,
) -> Dict[str, Any]:
    """MCP protocol endpoint for ElevenLabs Agent.
    
    Implements the MCP protocol for tool discovery and execution.
    Supports both JSON-RPC format and direct method calls.
    """
    # Log the incoming request for debugging
    logger.info(f"MCP POST request from {request.client.host if request.client else 'unknown'}")
    logger.info(f"Request body: {json.dumps(request_body, indent=2)}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Handle JSON-RPC format
    method = request_body.get("method") or request_body.get("jsonrpc_method")
    params = request_body.get("params", {})
    request_id = request_body.get("id")
    
    logger.info(f"MCP method: {method}, request_id: {request_id}")
    
    # Build response wrapper
    def make_response(result: Dict[str, Any], is_error: bool = False) -> Dict[str, Any]:
        response = {"jsonrpc": "2.0"}
        if request_id is not None:
            response["id"] = request_id
        if is_error:
            response["error"] = result
        else:
            response["result"] = result
        return response
    
    if method == "initialize":
        # Handle initialize request - return server capabilities
        logger.info("Handling initialize request")
        response = make_response({
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "SupaGent Knowledge Base",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {}
            }
        })
        logger.info(f"Initialize response: {json.dumps(response, indent=2)}")
        return response
    elif method == "tools/list":
        # Return available tools - this is a large list, kept here for now
        # Could be moved to a separate module if needed
        logger.info("Handling tools/list request")
        tools_list = _get_mcp_tools_list()
        response = make_response({"tools": tools_list})
        logger.info(f"tools/list response: {len(tools_list)} tools")
        return response
    elif method == "tools/call":
        # Execute tool call
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Handling tools/call for tool: {tool_name}")
        logger.info(f"Tool arguments: {json.dumps(arguments, indent=2)}")
        
        try:
            if tool_name == "search_knowledge_base":
                return handle_search_knowledge_base(mcp, arguments, make_response)
            elif tool_name == "create_support_ticket":
                return handle_create_ticket(request, arguments, make_response)
            elif tool_name == "get_customer_info":
                return handle_get_customer(request, arguments, make_response)
            elif tool_name == "escalate_to_human":
                return handle_escalate(request, arguments, make_response)
            elif tool_name == "log_interaction":
                return handle_log_interaction(request, arguments, make_response)
            elif tool_name == "check_order_status":
                return handle_check_order(request, arguments, make_response)
            elif tool_name == "check_availability":
                return handle_check_availability(request, arguments, make_response)
            elif tool_name == "get_user_bookings":
                return handle_get_user_bookings(request, arguments, make_response)
            elif tool_name == "book_appointment":
                return handle_book_appointment(request, arguments, make_response)
            elif tool_name == "modify_appointment":
                return handle_modify_appointment(request, arguments, make_response)
            elif tool_name == "cancel_appointment":
                return handle_cancel_appointment(request, arguments, make_response)
            elif tool_name == "post_call_data":
                return handle_post_call_data(request, arguments, make_response)
            elif tool_name == "get_clients":
                return handle_get_clients(request, arguments, make_response)
            elif tool_name == "add_clients":
                return handle_add_clients(request, arguments, make_response)
            else:
                logger.warning(f"Unknown tool requested: {tool_name}")
                return make_response({
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }, is_error=True)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return make_response({
                "code": -32603,
                "message": f"Internal error executing tool: {str(e)}"
            }, is_error=True)
    else:
        return make_response({
            "code": -32601,
            "message": f"Method not found: {method or 'unknown'}"
        }, is_error=True)


def _get_mcp_tools_list() -> list:
    """Get the list of MCP tools with their schemas."""
    return [
        {
            "name": "search_knowledge_base",
            "description": "Search the customer support knowledge base to find relevant documentation, FAQs, and troubleshooting guides. Use this tool when you need to answer questions about products, services, policies, or procedures.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant information in the knowledge base"
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 4, max: 10)",
                        "default": 4,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "create_support_ticket",
            "description": "Create a support ticket in the CRM system when an issue cannot be resolved through the knowledge base or requires human intervention.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Brief title summarizing the issue"},
                    "description": {"type": "string", "description": "Detailed description of the issue"},
                    "customer_id": {"type": "string", "description": "Customer ID if available"},
                    "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"], "default": "normal"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional tags"}
                },
                "required": ["title", "description"]
            }
        },
        {
            "name": "get_customer_info",
            "description": "Retrieve customer information from the CRM system including account details, order history, and previous interactions.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "identifier": {"type": "string", "description": "Customer identifier (customer_id, email, or phone)"}
                },
                "required": ["identifier"]
            }
        },
        {
            "name": "escalate_to_human",
            "description": "Escalate the conversation to a human support agent when needed.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Current conversation session ID"},
                    "reason": {"type": "string", "description": "Reason for escalation"},
                    "customer_id": {"type": "string", "description": "Customer ID if available"},
                    "conversation_summary": {"type": "string", "description": "Brief summary of conversation"}
                },
                "required": ["session_id"]
            }
        },
        {
            "name": "log_interaction",
            "description": "Log a customer interaction in the CRM system for analytics, compliance, and future reference.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "Customer ID"},
                    "activity_type": {"type": "string", "description": "Type of activity"},
                    "details": {"type": "object", "description": "Additional details as JSON object"}
                },
                "required": ["customer_id", "activity_type", "details"]
            }
        },
        {
            "name": "check_order_status",
            "description": "Check the status of a customer order including shipping information and estimated delivery date.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID or order number"},
                    "customer_id": {"type": "string", "description": "Customer ID for verification"}
                },
                "required": ["order_id"]
            }
        },
        {
            "name": "check_availability",
            "description": "Check calendar availability for a time range. Returns available time slots and existing events.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "time_min": {"type": "string", "description": "Start time for availability check (ISO 8601 format, optional, defaults to now)"},
                    "time_max": {"type": "string", "description": "End time for availability check (ISO 8601 format, optional, defaults to now + 7 days)"},
                    "duration_minutes": {"type": "integer", "description": "Minimum duration needed for availability in minutes (default: 30)"}
                }
            }
        },
        {
            "name": "get_user_bookings",
            "description": "Get user's calendar bookings/appointments for a specified time range.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "time_min": {"type": "string", "description": "Start time for query (ISO 8601 format, optional, defaults to now)"},
                    "time_max": {"type": "string", "description": "End time for query (ISO 8601 format, optional, defaults to now + 30 days)"},
                    "max_results": {"type": "integer", "description": "Maximum number of results to return (default: 50)"}
                }
            }
        },
        {
            "name": "book_appointment",
            "description": "Create a new appointment/event in the calendar.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Event title/summary"},
                    "start_time": {"type": "string", "description": "Start time of the appointment (ISO 8601 format)"},
                    "end_time": {"type": "string", "description": "End time of the appointment (ISO 8601 format)"},
                    "description": {"type": "string", "description": "Optional description of the appointment"},
                    "location": {"type": "string", "description": "Optional location"},
                    "attendees": {"type": "array", "items": {"type": "string"}, "description": "Optional list of attendee email addresses"}
                },
                "required": ["summary", "start_time", "end_time"]
            }
        },
        {
            "name": "modify_appointment",
            "description": "Update an existing appointment/event in the calendar.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "ID of the event to update"},
                    "summary": {"type": "string", "description": "New summary/title (optional)"},
                    "start_time": {"type": "string", "description": "New start time (ISO 8601 format, optional)"},
                    "end_time": {"type": "string", "description": "New end time (ISO 8601 format, optional)"},
                    "description": {"type": "string", "description": "New description (optional)"},
                    "location": {"type": "string", "description": "New location (optional)"},
                    "attendees": {"type": "array", "items": {"type": "string"}, "description": "New list of attendees (optional)"}
                },
                "required": ["event_id"]
            }
        },
        {
            "name": "cancel_appointment",
            "description": "Cancel/delete an appointment/event from the calendar.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "ID of the event to cancel"}
                },
                "required": ["event_id"]
            }
        },
        {
            "name": "post_call_data",
            "description": "Post call/interaction data to Google Sheets for logging and analytics.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "call_data": {"type": "object", "description": "Object containing call information (e.g., customer_id, duration, outcome, notes)"},
                    "sheet_name": {"type": "string", "description": "Name of the sheet tab (optional, defaults to 'Calls')"}
                },
                "required": ["call_data"]
            }
        },
        {
            "name": "get_clients",
            "description": "Get client data from Google Sheets.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sheet_name": {"type": "string", "description": "Name of the sheet tab (optional, defaults to first sheet)"},
                    "range_name": {"type": "string", "description": "A1 notation range (e.g., 'A1:D10') or leave empty for all data"}
                }
            }
        },
        {
            "name": "add_clients",
            "description": "Add client data to Google Sheets.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "clients": {"type": "array", "items": {"type": "object"}, "description": "Array of client objects to add"},
                    "sheet_name": {"type": "string", "description": "Name of the sheet tab (optional, defaults to first sheet)"}
                },
                "required": ["clients"]
            }
        }
    ]



