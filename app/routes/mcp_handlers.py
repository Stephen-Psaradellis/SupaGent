"""
MCP tool call handlers.

These functions handle individual tool calls within the MCP protocol.
Separated from the main MCP route for better organization.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Callable

from memory.mcp_client import MCPClient


def handle_search_knowledge_base(
    mcp: MCPClient,
    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle search_knowledge_base tool call."""
    try:
        query = arguments.get("query", "")
        k = arguments.get("k", 4)
        results = mcp.retrieve(query, k=k)
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.get("page_content", ""),
                "metadata": doc.get("metadata", {}),
                "title": doc.get("metadata", {}).get("title") or doc.get("metadata", {}).get("source", "Document")
            })
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Found {len(formatted_results)} results for query: {query}\n\n" + 
                           "\n\n".join([f"**{r['title']}**\n{r['content'][:500]}" for r in formatted_results])
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error searching knowledge base: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_create_ticket(
    request: Any,
    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle create_support_ticket tool call."""
    try:
        crm = request.app.state.crm
        title = arguments.get("title", "")
        description = arguments.get("description", "")
        if not crm:
            ticket_id = f"ticket_{int(time.time())}"
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"Ticket created: {ticket_id}. Status: created. CRM not configured - ticket created in mock mode"
                    }
                ]
            })
        result = crm.create_ticket(
            title=title,
            description=description,
            customer_id=arguments.get("customer_id"),
            priority=arguments.get("priority", "normal"),
            tags=arguments.get("tags", [])
        )
        ticket_id = result.get("id", "unknown")
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Ticket created: {ticket_id}. Status: {result.get('status', 'created')}. Ticket created successfully"
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error creating ticket: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_get_customer(
    request: Any,
    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle get_customer_info tool call."""
    try:
        crm = request.app.state.crm
        identifier = arguments.get("identifier", "")
        if not crm:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"CRM not configured. Mock customer info for {identifier}: Customer ID: {identifier}, Status: active, Orders: 0"
                    }
                ]
            })
        customer = crm.get_customer(identifier)
        if not customer:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"Customer not found: {identifier}"
                    }
                ]
            })
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Customer found: {customer.get('id', identifier)}, Name: {customer.get('name', 'Unknown')}, Email: {customer.get('email', 'N/A')}"
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error retrieving customer: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_escalate(
    request: Any,
    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle escalate_to_human tool call."""
    try:
        escalations = request.app.state.escalations
        session_id = arguments.get("session_id", "")
        reason = arguments.get("reason", "user_request")
        escalations.update_escalation(session_id, {"status": "escalated", "reason": reason})
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Conversation escalated to human agent. Session: {session_id}, Reason: {reason}"
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error escalating conversation: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_log_interaction(
    request: Any,
    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle log_interaction tool call."""
    try:
        crm = request.app.state.crm
        customer_id = arguments.get("customer_id", "")
        activity_type = arguments.get("activity_type", "")
        details = arguments.get("details", {})
        if not crm:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"CRM not configured. Interaction logged in mock mode: Customer: {customer_id}, Type: {activity_type}"
                    }
                ]
            })
        success = crm.log_interaction(customer_id, activity_type, details)
        if success:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"Interaction logged successfully: Customer: {customer_id}, Type: {activity_type}"
                    }
                ]
            })
        else:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"Failed to log interaction: Customer: {customer_id}, Type: {activity_type}"
                    }
                ]
            })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error logging interaction: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_check_order(
    request: Any,
    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle check_order_status tool call."""
    try:
        order_id = arguments.get("order_id", "")
        # Mock implementation - in production, this would query an order system
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Order {order_id}: Status: processing, Estimated delivery: 3-5 business days. (Mock response - order system not integrated)"
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error checking order status: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)

