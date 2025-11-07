"""
Dependency injection helpers for FastAPI routes.
"""
from __future__ import annotations

from typing import Annotated
from fastapi import Depends, Request

from core.config import AppConfig
from core.di import ServiceContainer
from memory.vector_store import VectorStore
from memory.mcp_client import MCPClient
from agents.rag import RAGAnswerer
from memory.session import SessionStore
from memory.analytics import AnalyticsStore
from memory.escalation import EscalationStore
from memory.compliance import ComplianceStore
from core.services import ConversationService, VoiceService


def get_config(request: Request) -> AppConfig:
    """Get application configuration from app state."""
    return request.app.state.config


def get_container(request: Request) -> ServiceContainer:
    """Get service container from app state."""
    return request.app.state.container


def get_store(request: Request) -> VectorStore:
    """Get vector store from app state."""
    return request.app.state.store


def get_mcp(request: Request) -> MCPClient:
    """Get MCP client from app state."""
    return request.app.state.mcp


def get_rag(request: Request) -> RAGAnswerer:
    """Get RAG answerer from app state."""
    return request.app.state.rag


def get_sessions(request: Request) -> SessionStore:
    """Get session store from app state."""
    return request.app.state.sessions


def get_analytics(request: Request) -> AnalyticsStore:
    """Get analytics store from app state."""
    return request.app.state.analytics


def get_escalations(request: Request) -> EscalationStore:
    """Get escalations store from app state."""
    return request.app.state.escalations


def get_compliance(request: Request) -> ComplianceStore:
    """Get compliance store from app state."""
    return request.app.state.compliance


def get_conversation_service(request: Request) -> ConversationService:
    """Get conversation service from app state."""
    return request.app.state.conversation_service


def get_voice_service(request: Request) -> VoiceService:
    """Get voice service from app state."""
    return request.app.state.voice_service


# Type aliases for cleaner route signatures
ConfigDep = Annotated[AppConfig, Depends(get_config)]
ContainerDep = Annotated[ServiceContainer, Depends(get_container)]
StoreDep = Annotated[VectorStore, Depends(get_store)]
MCPDep = Annotated[MCPClient, Depends(get_mcp)]
RAGDep = Annotated[RAGAnswerer, Depends(get_rag)]
SessionsDep = Annotated[SessionStore, Depends(get_sessions)]
AnalyticsDep = Annotated[AnalyticsStore, Depends(get_analytics)]
EscalationsDep = Annotated[EscalationStore, Depends(get_escalations)]
ComplianceDep = Annotated[ComplianceStore, Depends(get_compliance)]
ConversationServiceDep = Annotated[ConversationService, Depends(get_conversation_service)]
VoiceServiceDep = Annotated[VoiceService, Depends(get_voice_service)]

