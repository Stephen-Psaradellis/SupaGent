"""
Administrative routes for system management.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional
from fastapi import APIRouter, Request

from app.dependencies import ConfigDep, StoreDep
from memory.vector_store import VectorStore
from memory.mcp_client import MCPClient
from agents.rag import RAGAnswerer

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reload_store")
def reload_store(
    request: Request,
    persist_dir: Optional[str] = None,
    config: ConfigDep = None,
) -> Dict[str, Any]:
    """Reload the vector store with a new persist directory."""
    final_persist_dir = persist_dir or config.chroma_persist_dir
    
    # Rebuild store and dependencies
    new_store = VectorStore(
        persist_dir=final_persist_dir,
        embedding_model=config.embedding_model,
    )
    new_mcp = MCPClient(new_store.similarity_search)
    new_rag = RAGAnswerer(new_mcp)
    
    # Update app state
    request.app.state.store = new_store
    request.app.state.mcp = new_mcp
    request.app.state.rag = new_rag
    
    # Update container
    container = request.app.state.container
    container.register_instance("vector_store", new_store)
    container.register_instance("mcp_client", new_mcp)
    container.register_instance("rag", new_rag)
    
    return {"ok": True, "persist_dir": final_persist_dir}


@router.get("/status")
def status(
    request: Request,
    config: ConfigDep = None,
    store: StoreDep = None,
) -> Dict[str, Any]:
    """Get application status and configuration."""
    persist_dir = getattr(store, "_persist_dir", None) or config.chroma_persist_dir
    return {
        "persist_dir": persist_dir,
        "environment": "railway" if config.is_railway() else "local",
        "vector_backend": getattr(store, "_backend", "unknown"),
        "has_data": (
            os.path.exists(persist_dir) and len(os.listdir(persist_dir)) > 0
            if os.path.exists(persist_dir)
            else False
        )
    }


@router.get("/knowledge-base/flagged-answers")
def get_flagged_answers(
    request: Request,
) -> Dict[str, Any]:
    """Get flagged incorrect answers."""
    analytics = request.app.state.analytics
    feedback = analytics.get_feedback()
    flagged = [
        f for f in feedback
        if (f.get("rating") is not None and f.get("rating") < 2)
        or f.get("escalation_triggered", False)
    ]
    return {
        "flagged_answers": flagged,
        "count": len(flagged),
    }


@router.post("/knowledge-base/resolve-gap")
def resolve_knowledge_gap(
    query_text: str,
    resolution_notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Mark a knowledge gap as resolved."""
    # In a full implementation, this would update the gap status
    # For now, we'll just return success
    return {
        "success": True,
        "message": f"Knowledge gap for '{query_text}' marked as resolved",
    }

