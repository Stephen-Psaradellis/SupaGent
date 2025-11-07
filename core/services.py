"""
Service layer for business logic.

Separates business logic from API endpoints for better testability
and reusability.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from core.config import get_config
from core.utils import normalize_session_id
from memory.analytics import ConversationMetrics, FeedbackEntry, KnowledgeGap
from memory.compliance import AuditLogEntry, PIIDetection, PIIDetector
from memory.escalation import (
    EscalationContext,
    EscalationReason,
    detect_escalation_trigger,
)
from memory.mcp_client import MCPClient
from memory.session import SessionStore
from agents.rag import RAGAnswerer


class ConversationService:
    """Service for handling conversation logic.
    
    Encapsulates the business logic for processing queries, tracking
    metrics, handling escalations, and managing compliance.
    """
    
    def __init__(
        self,
        rag: RAGAnswerer,
        mcp: MCPClient,
        sessions: SessionStore,
        analytics_store: Any,  # AnalyticsStore
        escalation_store: Any,  # EscalationStore
        compliance_store: Any,  # ComplianceStore
        crm_adapter: Optional[Any] = None,  # Optional[CRMAdapter]
    ):
        """Initialize the conversation service.
        
        Args:
            rag: RAG answerer for generating responses.
            mcp: MCP client for retrieval.
            sessions: Session store for conversation history.
            analytics_store: Analytics store for metrics.
            escalation_store: Escalation store for tracking escalations.
            compliance_store: Compliance store for audit logs.
            crm_adapter: Optional CRM adapter for ticket creation.
        """
        self.rag = rag
        self.mcp = mcp
        self.sessions = sessions
        self.analytics_store = analytics_store
        self.escalation_store = escalation_store
        self.compliance_store = compliance_store
        self.crm_adapter = crm_adapter
    
    def process_query(
        self,
        question: str,
        session_id: Optional[str] = None,
        k: int = 4,
    ) -> Dict[str, Any]:
        """Process a user query and generate a response.
        
        Handles the full conversation flow including:
        - Session management
        - PII detection
        - RAG-based answer generation
        - Metrics tracking
        - Escalation detection
        - Compliance logging
        
        Args:
            question: User's question.
            session_id: Optional session identifier.
            k: Number of documents to retrieve.
            
        Returns:
            Dictionary containing answer, sources, and metadata.
        """
        sid = normalize_session_id(session_id)
        start_time = time.time()
        
        # Log conversation start
        self.compliance_store.log_audit_event(
            AuditLogEntry(
                timestamp=start_time,
                event_type="conversation_start",
                session_id=sid,
            )
        )
        
        # Detect PII in query
        pii_detections = PIIDetector.detect(question)
        for det in pii_detections:
            self.compliance_store.save_pii_detection(
                PIIDetection(
                    pii_type=det["type"],
                    value=det["value"],
                    session_id=sid,
                    timestamp=start_time,
                )
            )
        
        # Get conversation history
        hist = [vars(t) for t in self.sessions.history(sid)]
        self.sessions.append(sid, "user", question)
        
        # Retrieve documents and generate answer
        retrieved = self.mcp.retrieve(question, k=k)
        confidence = 0.7 if retrieved else 0.0
        has_results = len(retrieved) > 0
        
        result = self.rag.answer(question, history=hist)
        answer_text = result.get("answer", "")
        self.sessions.append(sid, "assistant", answer_text)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Check for escalation trigger
        failure_count = len([t for t in hist if t.get("role") == "user"])
        escalation_reason = detect_escalation_trigger(
            confidence=confidence,
            has_results=has_results,
            user_text=question,
            failure_count=failure_count,
        )
        
        # Track metrics
        metrics = ConversationMetrics(
            session_id=sid,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            resolution_status="resolved" if not escalation_reason else "escalated",
            escalation_reason=escalation_reason.value if escalation_reason else None,
            query_count=len(hist) + 1,
            avg_confidence=confidence,
        )
        self.analytics_store.save_metrics(metrics)
        
        # Handle escalation if needed
        if escalation_reason:
            escalation_context = EscalationContext(
                session_id=sid,
                escalation_reason=escalation_reason.value,
                timestamp=end_time,
                conversation_transcript=[
                    {"role": t.role, "text": t.text, "timestamp": t.ts}
                    for t in self.sessions.history(sid)
                ],
                retrieved_documents=retrieved,
                confidence_scores=[0.7] * len(retrieved) if retrieved else [],
                suggested_responses=[answer_text],
            )
            self.escalation_store.save_escalation(escalation_context)
            
            # Create CRM ticket if CRM is configured
            if self.crm_adapter:
                ticket = self.crm_adapter.create_ticket(
                    title=f"Voice Agent Escalation: {question[:50]}",
                    description=answer_text,
                    priority="high" if escalation_reason == EscalationReason.USER_REQUEST else "normal",
                    tags=["voice-agent", escalation_reason.value],
                )
                escalation_context.ticket_id = ticket.get("id")
                self.escalation_store.update_escalation(
                    sid, {"ticket_id": ticket.get("id")}
                )
            
            result["escalated"] = True
            result["escalation_reason"] = escalation_reason.value
        
        # Log conversation end
        self.compliance_store.log_audit_event(
            AuditLogEntry(
                timestamp=end_time,
                event_type="conversation_end",
                session_id=sid,
                details={
                    "duration": duration,
                    "resolution_status": metrics.resolution_status,
                },
            )
        )
        
        return result


class VoiceService:
    """Service for handling voice-related operations.
    
    Manages voice agent creation and voice query processing.
    """
    
    def __init__(
        self,
        rag: RAGAnswerer,
        config: Optional[Any] = None,  # Optional[AppConfig]
    ):
        """Initialize the voice service.
        
        Args:
            rag: RAG answerer for generating responses.
            config: Optional configuration. Uses get_config() if not provided.
        """
        from core.config import get_config as _get_config
        
        self.rag = rag
        self.config = config or _get_config()
        self._voice_agent_cache: Optional[Any] = None
    
    def get_voice_agent(self, voice_id: Optional[str] = None):
        """Get or create a voice agent instance.
        
        Uses caching to avoid recreating agents unnecessarily.
        
        Args:
            voice_id: Optional voice ID override.
            
        Returns:
            VoiceAgent or ElevenLabsVoiceAgent instance.
        """
        # Test override: force dummy TTS for deterministic tests
        if self.config.dummy_tts:
            from agents.voice import VoiceAgent
            
            class _DummyTTS:
                def synth(self, text: str) -> bytes:
                    return b"ID3\x03\x00\x00\x00\x00\x00\x21" + (
                        text[:8].encode() or b"aaaa"
                    )
            
            return VoiceAgent(self.rag, _DummyTTS())
        
        # Prefer fully-managed ElevenLabs Agent if configured
        try:
            from agents.eleven_agent import ElevenLabsAgentClient, ElevenLabsVoiceAgent
            
            agent_client = ElevenLabsAgentClient()
            return ElevenLabsVoiceAgent(self.rag, agent_client)
        except Exception:
            # Fallback to direct TTS if agent not configured
            from agents.voice import ElevenLabsTTS, VoiceAgent
            
            try:
                tts = ElevenLabsTTS(voice_id=voice_id)
            except Exception:
                tts = None
            return VoiceAgent(self.rag, tts)
    
    def process_voice_query(
        self,
        question: str,
        session_id: Optional[str] = None,
        voice_id: Optional[str] = None,
        sessions: Optional[SessionStore] = None,
    ) -> Dict[str, Any]:
        """Process a voice query and generate audio response.
        
        Args:
            question: User's question.
            session_id: Optional session identifier.
            voice_id: Optional voice ID override.
            sessions: Optional session store for history tracking.
            
        Returns:
            Dictionary containing answer, sources, and audio.
        """
        agent = self.get_voice_agent(voice_id=voice_id)
        
        if sessions:
            sid = normalize_session_id(session_id)
            hist = [vars(t) for t in sessions.history(sid)]
            sessions.append(sid, "user", question)
            result = agent.answer(question)
            sessions.append(sid, "assistant", result.get("answer", ""))
        else:
            result = agent.answer(question)
        
        return result

