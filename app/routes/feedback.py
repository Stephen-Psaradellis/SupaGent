"""
Feedback collection routes.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional
from fastapi import APIRouter

from app.dependencies import AnalyticsDep
from memory.analytics import FeedbackEntry, KnowledgeGap

router = APIRouter(tags=["feedback"])


@router.post("/feedback")
def submit_feedback(
    session_id: str,
    rating: Optional[int] = None,
    comment: Optional[str] = None,
    query_text: Optional[str] = None,
    answer_text: Optional[str] = None,
    analytics: AnalyticsDep = None,
) -> Dict[str, Any]:
    """Submit user feedback."""
    feedback = FeedbackEntry(
        session_id=session_id,
        query_text=query_text,
        answer_text=answer_text,
        feedback_type="explicit",
        rating=rating,
        comment=comment,
    )
    analytics.save_feedback(feedback)
    
    # Check if this indicates a knowledge gap
    if rating is not None and rating < 3:
        gap = KnowledgeGap(
            query_text=query_text or "Unknown",
            session_id=session_id,
            timestamp=time.time(),
            gap_type="negative_feedback",
            priority=5 if rating == 1 else 3,
        )
        analytics.save_knowledge_gap(gap)
    
    return {"success": True, "message": "Feedback recorded"}




