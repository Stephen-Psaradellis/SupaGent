"""
MCP (Model Context Protocol) routes.
"""
from __future__ import annotations

import json
import logging
import asyncio
import time
from typing import Any, Dict, Optional
from collections import defaultdict
from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse

from app.dependencies import MCPDep

logger = logging.getLogger(__name__)

# Store active SSE connections and their response queues
# Key: connection_id, Value: dict with 'queue' and 'metadata'
_sse_connections: Dict[str, Dict[str, Any]] = {}
_sse_connection_counter = 0

# Store connection IDs by various identifiers for matching
_connection_by_ip: Dict[str, str] = {}  # IP -> connection_id
_connection_by_user_agent: Dict[str, str] = {}  # User-Agent -> connection_id
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
    handle_browser_navigate,
    handle_browser_interact,
    handle_browser_extract,
    handle_browser_screenshot,
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
    
    # Generate a unique connection ID for this SSE connection
    global _sse_connection_counter
    _sse_connection_counter += 1
    client_ip = request.client.host if request.client else 'unknown'
    user_agent = request.headers.get('user-agent', 'unknown')
    connection_id = f"{client_ip}_{_sse_connection_counter}"
    response_queue = asyncio.Queue()
    
    # Store connection with metadata for matching
    _sse_connections[connection_id] = {
        'queue': response_queue,
        'ip': client_ip,
        'user_agent': user_agent,
        'created_at': time.time()
    }
    
    # Index by IP and User-Agent for matching POST requests
    _connection_by_ip[client_ip] = connection_id
    if user_agent:
        _connection_by_user_agent[user_agent] = connection_id
    
    logger.info(f"SSE connection established: {connection_id} (IP: {client_ip}, UA: {user_agent[:50]})")
    
    async def event_stream():
        logger.info(f"Starting SSE event stream for connection {connection_id}")
        
        try:
            # Send immediate connection message - MCP protocol expects this
            connection_msg = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            yield f"data: {json.dumps(connection_msg)}\n\n"
            logger.info(f"Sent connection initialized notification for {connection_id}")
            
            # Note: We don't send connection_ready notification as it's not part of standard MCP protocol
            # The dashboard will send initialize POST and expect response through SSE
            
            # If there's an initialize request in query params, respond to it immediately
            if initialize_request:
                try:
                    init_data = json.loads(initialize_request)
                    if init_data.get("method") == "initialize":
                        logger.info(f"Responding to initialize from query params for {connection_id}")
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
                        logger.info(f"Sent initialize response for {connection_id}")
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse initialize request: {e}")
            
            # Monitor for responses to POST requests and send them through SSE
            # Also send periodic keepalives
            keepalive_count = 0
            while True:
                try:
                    # Wait for either a response or timeout for keepalive
                    # Use shorter timeout (2s) to respond faster to dashboard validation
                    try:
                        response_data = await asyncio.wait_for(response_queue.get(), timeout=2.0)
                        # Skip status messages
                        if isinstance(response_data, dict) and response_data.get('status') == 'sent_via_sse':
                            response_queue.task_done()
                            continue
                        logger.info(f"Sending response through SSE for {connection_id}: method={response_data.get('method', 'response')}, id={response_data.get('id', 'N/A')}")
                        # Ensure proper SSE format - must be exactly "data: <json>\n\n"
                        json_str = json.dumps(response_data, ensure_ascii=False)
                        yield f"data: {json_str}\n\n"
                        response_queue.task_done()
                    except asyncio.TimeoutError:
                        # Timeout - send keepalive
                        keepalive_count += 1
                        if keepalive_count % 6 == 0:  # Log every minute
                            logger.info(f"SSE connection alive for {connection_id}, keepalive #{keepalive_count}")
                        yield f": keepalive\n\n"
                except Exception as e:
                    logger.error(f"Error in SSE stream for {connection_id}: {e}", exc_info=True)
                    break
        except Exception as e:
            logger.error(f"Error in SSE stream for {connection_id}: {e}", exc_info=True)
            raise
        finally:
            # Clean up connection
            if connection_id in _sse_connections:
                conn_data = _sse_connections[connection_id]
                if isinstance(conn_data, dict):
                    # Clean up indexes
                    ip = conn_data.get('ip')
                    user_agent = conn_data.get('user_agent')
                    if ip and ip in _connection_by_ip:
                        del _connection_by_ip[ip]
                    if user_agent and user_agent in _connection_by_user_agent:
                        del _connection_by_user_agent[user_agent]
                del _sse_connections[connection_id]
                logger.info(f"SSE connection closed: {connection_id}")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Connection-ID",
            "X-Connection-ID": connection_id,  # Send connection ID in header for correlation
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
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"MCP POST request from {client_ip}")
    logger.info(f"Request body: {json.dumps(request_body, indent=2)}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Check for connection ID in header (if client sends it)
    connection_id_header = request.headers.get('X-Connection-ID')
    if connection_id_header:
        logger.info(f"POST request includes connection ID header: {connection_id_header}")
    
    # Handle JSON-RPC format
    method = request_body.get("method") or request_body.get("jsonrpc_method")
    params = request_body.get("params", {})
    request_id = request_body.get("id")
    
    logger.info(f"MCP method: {method}, request_id: {request_id}")
    
    # Determine if this is a validation request BEFORE building response
    # Dashboard validation sends initialize/tools/list and expects immediate HTTP response
    # For validation requests, NEVER use SSE - always return HTTP response directly
    is_validation_request = method in ["initialize", "tools/list"]
    logger.info(f"Request type: {'VALIDATION' if is_validation_request else 'TOOL_CALL'}, method={method}")
    
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
    
    # Determine if we should use SSE or HTTP response
    # For dashboard validation (initialize, tools/list), always return HTTP response
    # For actual tool calls during agent conversations, prefer SSE if available
    use_sse_for_response = False
    sse_connection = None
    connection_id = None
    user_agent = request.headers.get('user-agent', '')
    
    # CRITICAL: For validation requests, NEVER use SSE - always return HTTP response
    # This is required for ElevenLabs dashboard connection testing
    if not is_validation_request:
        # For tool calls, try to find an active SSE connection
        # Match by connection ID header if provided (most reliable)
        if connection_id_header and connection_id_header in _sse_connections:
            connection_id = connection_id_header
            conn_data = _sse_connections[connection_id]
            if isinstance(conn_data, dict):
                sse_connection = conn_data.get('queue')
                use_sse_for_response = True
                logger.info(f"Found SSE connection {connection_id} by X-Connection-ID header")
        
        # Match by IP (reliable for same-origin requests)
        if not sse_connection and client_ip in _connection_by_ip:
            connection_id = _connection_by_ip[client_ip]
            conn_data = _sse_connections.get(connection_id)
            if conn_data and isinstance(conn_data, dict):
                # Only use if connection is recent (within 5 minutes)
                created_at = conn_data.get('created_at', 0)
                age = time.time() - created_at
                if age < 300:  # 5 minutes
                    sse_connection = conn_data.get('queue')
                    use_sse_for_response = True
                    logger.info(f"Found SSE connection {connection_id} by IP {client_ip} (age: {age:.1f}s)")
    
    async def send_response_via_sse_or_http(response: Dict[str, Any]) -> Dict[str, Any]:
        """Send response through SSE if available and appropriate, otherwise return HTTP response.
        
        For dashboard validation requests (initialize, tools/list), always return HTTP response.
        For tool calls during agent conversations, use SSE if available.
        """
        if use_sse_for_response and sse_connection:
            try:
                # Put response in queue - it will be sent through SSE stream
                await sse_connection.put(response)
                logger.info(f"Queued response for SSE to {connection_id}: method={response.get('method', 'response')}, id={response.get('id', 'N/A')}")
                
                # Return minimal response - actual response goes through SSE
                return {"status": "sent_via_sse", "connection_id": connection_id}
            except Exception as e:
                logger.error(f"Failed to queue response for SSE: {e}", exc_info=True)
                # Fallback to HTTP if SSE queue fails
                return response
        else:
            # Return HTTP response directly (required for dashboard validation)
            logger.info(f"Returning HTTP response for method={method}, use_sse={use_sse_for_response}, has_sse_conn={sse_connection is not None}")
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
        
        return await send_response_via_sse_or_http(response)
    elif method == "tools/list":
        # Return available tools - this is a large list, kept here for now
        # Could be moved to a separate module if needed
        logger.info("Handling tools/list request")
        tools_list = _get_mcp_tools_list()
        response = make_response({"tools": tools_list})
        logger.info(f"tools/list response: {len(tools_list)} tools")
        
        return await send_response_via_sse_or_http(response)
    elif method == "tools/call":
        # Execute tool call
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Handling tools/call for tool: {tool_name}")
        logger.info(f"Tool arguments: {json.dumps(arguments, indent=2)}")
        
        try:
            tool_response = None
            if tool_name == "search_knowledge_base":
                tool_response = handle_search_knowledge_base(mcp, arguments, make_response)
            elif tool_name == "create_support_ticket":
                tool_response = handle_create_ticket(request, arguments, make_response)
            elif tool_name == "get_customer_info":
                tool_response = handle_get_customer(request, arguments, make_response)
            elif tool_name == "escalate_to_human":
                tool_response = handle_escalate(request, arguments, make_response)
            elif tool_name == "log_interaction":
                tool_response = handle_log_interaction(request, arguments, make_response)
            elif tool_name == "check_order_status":
                tool_response = handle_check_order(request, arguments, make_response)
            elif tool_name == "check_availability":
                tool_response = handle_check_availability(request, arguments, make_response)
            elif tool_name == "get_user_bookings":
                tool_response = handle_get_user_bookings(request, arguments, make_response)
            elif tool_name == "book_appointment":
                tool_response = handle_book_appointment(request, arguments, make_response)
            elif tool_name == "modify_appointment":
                tool_response = handle_modify_appointment(request, arguments, make_response)
            elif tool_name == "cancel_appointment":
                tool_response = handle_cancel_appointment(request, arguments, make_response)
            elif tool_name == "post_call_data":
                tool_response = handle_post_call_data(request, arguments, make_response)
            elif tool_name == "get_clients":
                tool_response = handle_get_clients(request, arguments, make_response)
            elif tool_name == "add_clients":
                tool_response = handle_add_clients(request, arguments, make_response)
            elif tool_name == "browser_navigate":
                tool_response = handle_browser_navigate(request, arguments, make_response)
            elif tool_name == "browser_interact":
                tool_response = handle_browser_interact(request, arguments, make_response)
            elif tool_name == "browser_extract":
                tool_response = handle_browser_extract(request, arguments, make_response)
            elif tool_name == "browser_screenshot":
                tool_response = handle_browser_screenshot(request, arguments, make_response)
            else:
                logger.warning(f"Unknown tool requested: {tool_name}")
                tool_response = make_response({
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }, is_error=True)
            
            # Send response through SSE if available
            if tool_response:
                return await send_response_via_sse_or_http(tool_response)
            return tool_response
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            error_response = make_response({
                "code": -32603,
                "message": f"Internal error executing tool: {str(e)}"
            }, is_error=True)
            return await send_response_via_sse_or_http(error_response)
    else:
        error_response = make_response({
            "code": -32601,
            "message": f"Method not found: {method or 'unknown'}"
        }, is_error=True)
        return await send_response_via_sse_or_http(error_response)


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
        },
        {
            "name": "browser_navigate",
            "description": "Navigate to a URL in the browser. Opens and renders web pages with full JavaScript support. Maintains session context for multi-step workflows.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to navigate to"},
                    "session_id": {"type": "string", "description": "Browser session ID for maintaining context (defaults to 'default')"},
                    "wait_for": {"type": "string", "description": "Optional CSS selector or text to wait for after navigation"}
                },
                "required": ["url"]
            }
        },
        {
            "name": "browser_interact",
            "description": "Perform intelligent interactions on the web page (clicking, typing, submitting forms, scrolling, waiting for elements). Uses BrowserUse's autonomous control for smart element detection.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["click", "type", "submit", "scroll", "wait"], "description": "Action to perform"},
                    "selector": {"type": "string", "description": "CSS selector, text, or description to identify the element"},
                    "text": {"type": "string", "description": "Text to type (required for 'type' action)"},
                    "session_id": {"type": "string", "description": "Browser session ID (defaults to 'default')"}
                },
                "required": ["action"]
            }
        },
        {
            "name": "browser_extract",
            "description": "Extract structured data from the current page such as titles, text, links, and metadata. Can extract from the entire page or a specific element.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "extract_type": {"type": "string", "enum": ["all", "title", "text", "links", "metadata"], "description": "Type of data to extract (default: 'all')"},
                    "selector": {"type": "string", "description": "Optional CSS selector to limit extraction to a specific element"},
                    "session_id": {"type": "string", "description": "Browser session ID (defaults to 'default')"}
                }
            }
        },
        {
            "name": "browser_screenshot",
            "description": "Capture a screenshot of the current page or a specific element. Useful for visual verification or debugging.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Browser session ID (defaults to 'default')"},
                    "full_page": {"type": "boolean", "description": "Whether to capture the full scrollable page (default: false)"},
                    "selector": {"type": "string", "description": "Optional CSS selector to screenshot a specific element"}
                }
            }
        }
    ]



