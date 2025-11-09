"""
CRM integration routes.
"""
from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Request

router = APIRouter(prefix="/crm", tags=["crm"])


@router.get("/customer/{identifier}")
def get_customer(
    request: Request,
    identifier: str,
) -> Dict[str, Any]:
    """Get customer information from CRM."""
    crm = request.app.state.crm
    if not crm:
        return {"error": "CRM not configured"}
    
    customer = crm.get_customer(identifier)
    if not customer:
        return {"error": "Customer not found"}
    return customer


@router.post("/log-interaction")
def log_crm_interaction(
    request: Request,
    customer_id: str,
    activity_type: str,
    details: Dict[str, Any],
) -> Dict[str, Any]:
    """Log interaction in CRM."""
    crm = request.app.state.crm
    if not crm:
        return {"error": "CRM not configured"}
    
    success = crm.log_interaction(customer_id, activity_type, details)
    return {"success": success}



