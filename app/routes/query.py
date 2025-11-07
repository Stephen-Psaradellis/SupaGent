"""
Query processing routes.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter

from app.models import Query
from app.dependencies import ConversationServiceDep

router = APIRouter(tags=["query"])


@router.post("/query")
def query(
    q: Query,
    session_id: Optional[str] = None,
    service: ConversationServiceDep = None,
) -> Dict[str, Any]:
    """Process a text query using the conversation service."""
    return service.process_query(q.question, session_id=session_id, k=4)

