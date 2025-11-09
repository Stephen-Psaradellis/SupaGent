"""
Tool endpoints for ElevenLabs Agent integration.
"""
from __future__ import annotations

import time
from typing import Any, Dict
from fastapi import APIRouter, Request

from app.models import (
    ToolCallRequest,
    CreateTicketRequest,
    GetCustomerRequest,
    EscalateRequest,
    LogInteractionRequest,
    CheckOrderRequest,
)
from app.dependencies import MCPDep, ConfigDep

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("/search_knowledge_base")
def search_knowledge_base(
    request: ToolCallRequest,
    mcp: MCPDep = None,
) -> Dict[str, Any]:
    """Tool endpoint for ElevenLabs Agent to search the knowledge base via MCP."""
    try:
        results = mcp.retrieve(request.query, k=request.k or 4)
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.get("page_content", ""),
                "metadata": doc.get("metadata", {}),
                "title": doc.get("metadata", {}).get("title") or doc.get("metadata", {}).get("source", "Document")
            })
        return {
            "success": True,
            "query": request.query,
            "results": formatted_results,
            "count": len(formatted_results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "results": [],
            "count": 0
        }


@router.post("/create_support_ticket")
def create_support_ticket(
    request: Request,
    ticket_request: CreateTicketRequest,
) -> Dict[str, Any]:
    """Tool endpoint for creating a support ticket in the CRM system."""
    try:
        crm = request.app.state.crm
        if not crm:
            return {
                "success": True,
                "ticket_id": f"ticket_{int(time.time())}",
                "title": ticket_request.title,
                "status": "created",
                "message": "CRM not configured - ticket created in mock mode"
            }
        
        result = crm.create_ticket(
            title=ticket_request.title,
            description=ticket_request.description,
            customer_id=ticket_request.customer_id,
            priority=ticket_request.priority,
            tags=ticket_request.tags or []
        )
        return {
            "success": True,
            "ticket_id": result.get("id", "unknown"),
            "title": result.get("title", ticket_request.title),
            "status": result.get("status", "created"),
            "message": "Ticket created successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create ticket"
        }


@router.post("/get_customer_info")
def get_customer_info(
    request: Request,
    customer_request: GetCustomerRequest,
) -> Dict[str, Any]:
    """Tool endpoint for retrieving customer information from CRM."""
    try:
        crm = request.app.state.crm
        if not crm:
            return {
                "success": True,
                "customer": {
                    "id": customer_request.identifier,
                    "name": "Mock Customer",
                    "email": "mock@example.com",
                    "status": "active"
                },
                "message": "CRM not configured - returning mock data"
            }
        
        customer = crm.get_customer(customer_request.identifier)
        if not customer:
            return {
                "success": False,
                "error": "Customer not found",
                "message": f"No customer found with identifier: {customer_request.identifier}"
            }
        
        return {
            "success": True,
            "customer": customer,
            "message": "Customer information retrieved successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve customer information"
        }


@router.post("/escalate_to_human")
def escalate_to_human(
    request: Request,
    escalate_request: EscalateRequest,
) -> Dict[str, Any]:
    """Tool endpoint for escalating a conversation to a human agent."""
    try:
        escalations = request.app.state.escalations
        escalations.update_escalation(
            escalate_request.session_id,
            {
                "status": "escalated",
                "reason": escalate_request.reason or "user_request",
                "customer_id": escalate_request.customer_id,
                "conversation_summary": escalate_request.conversation_summary,
            }
        )
        return {
            "success": True,
            "session_id": escalate_request.session_id,
            "message": "Conversation escalated to human agent"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to escalate conversation"
        }


@router.post("/log_interaction")
def log_interaction(
    request: Request,
    interaction_request: LogInteractionRequest,
) -> Dict[str, Any]:
    """Tool endpoint for logging customer interactions in CRM."""
    try:
        crm = request.app.state.crm
        if not crm:
            return {
                "success": True,
                "message": "CRM not configured - interaction logged in mock mode"
            }
        
        success = crm.log_interaction(
            interaction_request.customer_id,
            interaction_request.activity_type,
            interaction_request.details,
        )
        return {
            "success": success,
            "message": "Interaction logged successfully" if success else "Failed to log interaction"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to log interaction"
        }


@router.post("/check_order_status")
def check_order_status(
    request: CheckOrderRequest,
) -> Dict[str, Any]:
    """Tool endpoint for checking order status."""
    # Mock implementation - in production, this would query an order system
    return {
        "success": True,
        "order_id": request.order_id,
        "status": "processing",
        "estimated_delivery": "3-5 business days",
        "message": "Mock response - order system not integrated"
    }


@router.get("/definitions")
def get_tool_definitions(
    config: ConfigDep = None,
) -> Dict[str, Any]:
    """Returns tool definitions for ElevenLabs Agent configuration."""
    base_url = config.base_url
    return {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search the customer support knowledge base to find relevant documentation, FAQs, and troubleshooting guides. Use this tool when you need to answer questions about products, services, policies, or procedures.",
                    "parameters": {
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
                    },
                    "url": f"{base_url}/tools/search_knowledge_base"
                }
            }
        ]
    }



