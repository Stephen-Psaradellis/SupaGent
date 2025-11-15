"""
Analytics and reporting routes.
"""
from __future__ import annotations

import csv
import io
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter
from fastapi.responses import Response

from app.dependencies import AnalyticsDep

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
def get_analytics_dashboard(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    analytics: AnalyticsDep = None,
) -> Dict[str, Any]:
    """Get analytics dashboard data."""
    start = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
    end = datetime.fromisoformat(end_date) if end_date else datetime.now()
    
    metrics = analytics.calculate_analytics(start, end)
    knowledge_gaps = analytics.get_knowledge_gaps()
    
    return {
        "metrics": metrics,
        "knowledge_gaps": knowledge_gaps[:20],  # Top 20
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat(),
        }
    }


@router.get("/knowledge-gaps")
def get_knowledge_gaps(
    min_priority: int = 0,
    gap_type: Optional[str] = None,
    analytics: AnalyticsDep = None,
) -> Dict[str, Any]:
    """Get knowledge gaps."""
    gaps = analytics.get_knowledge_gaps(min_priority, gap_type)
    return {
        "gaps": gaps,
        "count": len(gaps),
    }


@router.get("/export")
def export_analytics(
    format: str = "json",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    analytics: AnalyticsDep = None,
) -> Any:
    """Export analytics data."""
    start = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
    end = datetime.fromisoformat(end_date) if end_date else datetime.now()
    
    metrics = analytics.get_metrics(start, end)
    feedback = analytics.get_feedback(start, end)
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["session_id", "start_time", "duration", "resolution_status"])
        writer.writeheader()
        for m in metrics:
            writer.writerow(m)
        return Response(content=output.getvalue(), media_type="text/csv")
    elif format == "json":
        return {
            "metrics": metrics,
            "feedback": feedback,
        }
    else:
        return {"error": "Unsupported format"}












