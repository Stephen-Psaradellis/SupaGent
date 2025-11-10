"""
Compliance and GDPR routes.
"""
from __future__ import annotations

import uuid
import time
from typing import Any, Dict, Optional, List
from datetime import datetime
from fastapi import APIRouter

from app.dependencies import ComplianceDep
from memory.compliance import PIIDetector, DeletionRequest

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.get("/audit-log")
def get_audit_log(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    event_type: Optional[str] = None,
    session_id: Optional[str] = None,
    compliance: ComplianceDep = None,
) -> Dict[str, Any]:
    """Get audit log."""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    entries = compliance.get_audit_log(start, end, event_type, session_id)
    return {
        "entries": entries,
        "count": len(entries),
    }


@router.post("/detect-pii")
def detect_pii_in_text(
    text: str,
) -> Dict[str, Any]:
    """Detect PII in text."""
    detections = PIIDetector.detect(text)
    redacted, redactions = PIIDetector.redact(text)
    return {
        "detections": detections,
        "redacted_text": redacted,
        "redactions": redactions,
    }


@router.post("/gdpr/delete-request")
def create_deletion_request(
    customer_id: Optional[str] = None,
    email: Optional[str] = None,
    data_types: Optional[List[str]] = None,
    compliance: ComplianceDep = None,
) -> Dict[str, Any]:
    """Create GDPR deletion request."""
    request = DeletionRequest(
        request_id=str(uuid.uuid4()),
        customer_id=customer_id,
        email=email,
        requested_at=time.time(),
        data_types=data_types or ["all"],
    )
    compliance.save_deletion_request(request)
    return {
        "request_id": request.request_id,
        "status": "pending",
        "message": "Deletion request created. Processing will begin within 30 days.",
    }


@router.get("/gdpr/deletion-requests")
def get_deletion_requests(
    status: Optional[str] = None,
    compliance: ComplianceDep = None,
) -> Dict[str, Any]:
    """Get deletion requests."""
    requests = compliance.get_deletion_requests(status)
    return {
        "requests": requests,
        "count": len(requests),
    }





