"""
Pydantic models for API requests and responses.
"""
from __future__ import annotations

from pydantic import BaseModel
from typing import Any, Dict, Optional, List


class Query(BaseModel):
    """Request model for text queries."""
    question: str


class VoiceQuery(BaseModel):
    """Request model for voice queries."""
    question: str
    session_id: Optional[str] = None
    voice_id: Optional[str] = None


class ToolCallRequest(BaseModel):
    """Request format for ElevenLabs Agent tool calls."""
    query: str
    k: Optional[int] = 4


class CreateTicketRequest(BaseModel):
    """Request format for creating a support ticket."""
    title: str
    description: str
    customer_id: Optional[str] = None
    priority: str = "normal"
    tags: Optional[List[str]] = None


class GetCustomerRequest(BaseModel):
    """Request format for getting customer information."""
    identifier: str  # Can be customer_id, email, or phone


class EscalateRequest(BaseModel):
    """Request format for escalating to human agent."""
    session_id: str
    reason: Optional[str] = None
    customer_id: Optional[str] = None
    conversation_summary: Optional[str] = None


class LogInteractionRequest(BaseModel):
    """Request format for logging customer interaction."""
    customer_id: str
    activity_type: str
    details: Dict[str, Any]


class CheckOrderRequest(BaseModel):
    """Request format for checking order status."""
    order_id: str
    customer_id: Optional[str] = None

