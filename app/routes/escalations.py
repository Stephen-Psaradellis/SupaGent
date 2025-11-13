"""
Escalation management routes.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter

from app.dependencies import EscalationsDep

router = APIRouter(prefix="/escalations", tags=["escalations"])


@router.get("")
def get_escalations(
    status: Optional[str] = None,
    assigned_agent: Optional[str] = None,
    escalations: EscalationsDep = None,
) -> Dict[str, Any]:
    """Get escalations."""
    results = escalations.get_escalations(status, assigned_agent)
    return {
        "escalations": results,
        "count": len(results),
    }


@router.get("/{session_id}")
def get_escalation_context(
    session_id: str,
    escalations: EscalationsDep = None,
) -> Dict[str, Any]:
    """Get escalation context for a session."""
    escalation = escalations.get_escalation(session_id)
    if not escalation:
        return {"error": "Escalation not found"}
    return escalation


@router.post("/{session_id}/update")
def update_escalation(
    session_id: str,
    updates: Dict[str, Any],
    escalations: EscalationsDep = None,
) -> Dict[str, Any]:
    """Update escalation status."""
    success = escalations.update_escalation(session_id, updates)
    return {"success": success}










