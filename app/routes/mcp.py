"""
MCP (Model Context Protocol) routes.
"""
from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Request

from app.dependencies import MCPDep
from app.routes.mcp_handlers import (
    handle_search_knowledge_base,
    handle_create_ticket,
    handle_get_customer,
    handle_escalate,
    handle_log_interaction,
    handle_check_order,
)

router = APIRouter(prefix="/mcp", tags=["mcp"])


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
    # Handle JSON-RPC format
    method = request_body.get("method") or request_body.get("jsonrpc_method")
    params = request_body.get("params", {})
    request_id = request_body.get("id")
    
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
    
    if method == "tools/list" or method == "initialize":
        # Return available tools - this is a large list, kept here for now
        # Could be moved to a separate module if needed
        tools_list = _get_mcp_tools_list()
        return make_response({"tools": tools_list})
    elif method == "tools/call":
        # Execute tool call
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
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
        else:
            return make_response({
                "code": -32601,
                "message": f"Unknown tool: {tool_name}"
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
        }
    ]



