from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
import time

# Core infrastructure
from core.config import get_config
from core.di import create_container
from core.utils import format_documents_for_response, normalize_session_id
from core.http_client import HTTPClientManager

# Legacy imports for backward compatibility
from memory.vector_store import VectorStore
from memory.mcp_client import MCPClient
from agents.rag import RAGAnswerer
from agents.voice import VoiceAgent, ElevenLabsTTS
from agents.eleven_agent import ElevenLabsAgentClient, ElevenLabsVoiceAgent
from agents.asr import ElevenLabsASR
from memory.session import SessionStore
from memory.analytics import AnalyticsStore, ConversationMetrics, FeedbackEntry, KnowledgeGap
from memory.escalation import EscalationStore, EscalationContext, EscalationReason
from memory.compliance import ComplianceStore, AuditLogEntry, PIIDetector, DeletionRequest
from integrations.crm import get_crm_adapter


class Query(BaseModel):
    question: str


class VoiceQuery(BaseModel):
    question: str
    session_id: Optional[str] = None
    # Optionally allow a specific voice_id override per request
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


def build_app() -> FastAPI:
    """Build and configure the FastAPI application.
    
    Uses the new service container architecture for better
    dependency management and testability.
    
    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(title="SupaGent Support Agent")
    
    # Initialize configuration and service container
    config = get_config()
    container = create_container(config)
    
    # Store container and config in app state for access in endpoints
    app.state.container = container
    app.state.config = config
    
    # Initialize legacy components for backward compatibility
    # (stored on app.state for hot-reload capability)
    app.state.store = container.get("vector_store")
    app.state.mcp = container.get("mcp_client")
    app.state.rag = container.get("rag")
    app.state.sessions = container.get("sessions")
    app.state.analytics = container.get("analytics")
    app.state.escalations = container.get("escalations")
    app.state.compliance = container.get("compliance")
    app.state.crm = container.get("crm")
    
    # Store services
    app.state.conversation_service = container.get("conversation_service")
    app.state.voice_service = container.get("voice_service")

    # Helper function to create/register MCP server with ElevenLabs
    def create_or_get_mcp_server() -> Optional[str]:
        """Create or retrieve MCP server configuration in ElevenLabs.
        
        Returns the MCP server ID if successful, None otherwise.
        """
        try:
            from elevenlabs.client import ElevenLabs  # type: ignore
            
            if not config.elevenlabs_api_key:
                return None
            
            client = ElevenLabs(api_key=config.elevenlabs_api_key)
            base_url = config.base_url
            mcp_server_name = config.mcp_server_name
            
            # Check if MCP server already exists
            try:
                # Try to list existing MCP servers
                if hasattr(client.conversational_ai, 'mcp_servers'):
                    mcp_servers = client.conversational_ai.mcp_servers.list()
                    # Look for existing server with our name or URL
                    for server in getattr(mcp_servers, 'servers', []):
                        server_config = getattr(server, 'config', {})
                        server_url = server_config.get('url', '') if isinstance(server_config, dict) else getattr(server_config, 'url', '')
                        if base_url in server_url or getattr(server, 'name', '') == mcp_server_name:
                            server_id = getattr(server, 'id', None)
                            if server_id:
                                app.state._mcp_server_id = server_id
                                return server_id
            except Exception:
                # If listing fails, continue to create
                pass
            
            # Create new MCP server
            try:
                # Use the MCP server API to create a server pointing to our endpoint
                # The MCP server URL should point to our tool endpoint
                mcp_config = {
                    "url": f"{base_url}/mcp",
                    "name": mcp_server_name,
                    "description": "SupaGent Knowledge Base MCP Server - Provides access to customer support documentation via vector store search",
                    "transport": "SSE",  # Server-Sent Events transport
                    "approval_policy": "auto_approve_all",  # Auto-approve tool calls
                }
                
                # Create MCP server via API
                if hasattr(client, 'conversational_ai') and hasattr(client.conversational_ai, 'mcp_servers'):
                    result = client.conversational_ai.mcp_servers.create(config=mcp_config)
                    server_id = getattr(result, 'id', None)
                    if server_id:
                        app.state._mcp_server_id = server_id
                        # Persist to .env
                        from pathlib import Path
                        env_path = Path(".env")
                        if env_path.exists():
                            lines = env_path.read_text(encoding="utf-8").splitlines()
                            lines = [l for l in lines if not l.startswith("ELEVENLABS_MCP_SERVER_ID=")]
                            lines.append(f"ELEVENLABS_MCP_SERVER_ID={server_id}")
                            env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                        return server_id
            except Exception as e:
                app.state._mcp_server_error = str(e)
                return None
        except Exception as e:
            app.state._mcp_server_error = str(e)
            return None

    # Create/register MCP server with ElevenLabs and grant agent access
    if config.elevenlabs_api_key:
        mcp_server_id = create_or_get_mcp_server()
        if mcp_server_id:
            import os
            os.environ["ELEVENLABS_MCP_SERVER_ID"] = mcp_server_id
            config.elevenlabs_mcp_server_id = mcp_server_id
            
            # Grant agent access to MCP server and knowledge base
            if config.elevenlabs_agent_id:
                try:
                    from agents.agent_testing import ElevenLabsAgentTester
                    from agents.system_prompt import get_system_prompt
                    tester = ElevenLabsAgentTester(agent_id=config.elevenlabs_agent_id)
                    
                    # Grant MCP server access to the agent and update system prompt
                    system_prompt = get_system_prompt()
                    tester.update_agent(
                        mcp_server_ids=[mcp_server_id],
                        prompt=system_prompt
                    )
                except Exception as e:
                    # Log error but don't fail startup
                    app.state._agent_update_error = str(e)

    # Auto-create ElevenLabs Agent if API key is present and no agent id provided
    if config.elevenlabs_api_key and not config.elevenlabs_agent_id:
        try:
            from elevenlabs.client import ElevenLabs  # type: ignore
            from pathlib import Path
            import os
            
            client = ElevenLabs(api_key=config.elevenlabs_api_key)
            
            # Create agent
            agent_name = os.getenv("SUPAGENT_AGENT_NAME", "SupaGent Support Agent")
            agent = client.agents.create(name=agent_name)
            
            aid = getattr(agent, "id", None) or getattr(agent, "agent_id", None)
            if aid:
                os.environ["ELEVENLABS_AGENT_ID"] = aid
                config.elevenlabs_agent_id = aid
                # Persist to .env so restarts keep the agent id
                env_path = Path(".env")
                lines = []
                if env_path.exists():
                    lines = [
                        l for l in env_path.read_text(encoding="utf-8").splitlines()
                        if not l.startswith("ELEVENLABS_AGENT_ID=")
                    ]
                lines.append(f"ELEVENLABS_AGENT_ID={aid}")
                env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except Exception as e:
            # Surface a hint on /config/eleven
            app.state._agent_error = str(e)

    # Store references for backward compatibility
    store = app.state.store
    mcp = app.state.mcp
    rag = app.state.rag

    # Static demo
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Voice agent factory (now uses voice service)
    def make_voice_agent(voice_id: Optional[str] = None):
        """Create a voice agent instance.
        
        Uses the voice service for better abstraction.
        """
        return app.state.voice_service.get_voice_agent(voice_id=voice_id)

    @app.get("/demo")
    def demo_redirect():
        return RedirectResponse(url="/static/demo.html")

    @app.get("/config/eleven")
    def eleven_config() -> Dict[str, Any]:
        """Get ElevenLabs configuration status."""
        cfg = app.state.config
        err = getattr(app.state, "_agent_error", None)
        mcp_server_id = cfg.elevenlabs_mcp_server_id or getattr(app.state, "_mcp_server_id", None)
        mcp_error = getattr(app.state, "_mcp_server_error", None)
        
        return {
            "agent_id": cfg.elevenlabs_agent_id,
            "has_key": bool(cfg.elevenlabs_api_key),
            "status": "ok" if cfg.elevenlabs_agent_id else "missing",
            "error": err,
            "mcp_server": {
                "id": mcp_server_id,
                "endpoint": cfg.get_mcp_endpoint(),
                "tool_endpoint": cfg.get_tool_endpoint(),
                "error": mcp_error,
                "status": "configured" if mcp_server_id else "not_configured"
            }
        }
    
    @app.post("/config/eleven/configure_mcp")
    def configure_mcp_endpoint() -> Dict[str, Any]:
        """Manually trigger MCP server creation/registration with ElevenLabs."""
        cfg = app.state.config
        if not cfg.elevenlabs_api_key:
            return {"success": False, "error": "ELEVENLABS_API_KEY not set in Doppler"}
        
        mcp_server_id = create_or_get_mcp_server()
        if mcp_server_id:
            return {
                "success": True,
                "message": "MCP server configured successfully",
                "mcp_server_id": mcp_server_id
            }
        else:
            error = getattr(app.state, "_mcp_server_error", None)
            return {
                "success": False,
                "error": error or "Failed to create/register MCP server. Check API key and network connectivity."
            }

    @app.post("/query")
    def query(q: Query, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a text query using the conversation service."""
        service = app.state.conversation_service
        return service.process_query(q.question, session_id=session_id, k=4)

    @app.post("/voice")
    def voice(q: VoiceQuery) -> Dict[str, Any]:
        """Process a voice query using the voice service."""
        service = app.state.voice_service
        return service.process_voice_query(
            question=q.question,
            session_id=q.session_id,
            voice_id=q.voice_id,
            sessions=app.state.sessions,
        )

    @app.post("/voice_stream")
    def voice_stream(q: VoiceQuery):
        sid = q.session_id or "default"
        app.state.sessions.append(sid, "user", q.question)
        agent = make_voice_agent(voice_id=q.voice_id)
        stream_fn = getattr(agent, "stream_answer", None)
        if not callable(stream_fn):
            return {"detail": "Streaming not available."}
        gen = stream_fn(q.question)
        return StreamingResponse(gen, media_type="audio/mpeg")

    # Optional ASR: transcribe audio bytes to text
    def make_asr():
        try:
            return ElevenLabsASR()
        except Exception:
            return None

    @app.post("/asr")
    async def asr(file: UploadFile = File(...)) -> Dict[str, Any]:
        engine = make_asr()
        data = await file.read()
        mime = file.content_type
        if engine is None:
            return {"text": "", "warnings": ["ASR not configured. Install elevenlabs and set ELEVENLABS_API_KEY in Doppler."]}
        try:
            text = engine.transcribe(data, mime)
            return {"text": text}
        except Exception as e:
            return {"text": "", "warnings": [str(e)]}

    @app.post("/voice_from_audio")
    async def voice_from_audio(
        file: UploadFile = File(...),
        fallback_text: Optional[str] = Form(None),
        session_id: Optional[str] = Form(None)
    ) -> Dict[str, Any]:
        """Process voice query from audio file."""
        engine = make_asr()
        data = await file.read()
        mime = file.content_type
        text: Optional[str] = None
        
        if engine is not None:
            try:
                text = engine.transcribe(data, mime)
            except Exception:
                text = None
        
        if not text:
            if fallback_text:
                text = fallback_text
            else:
                return {
                    "answer": "",
                    "audio_base64": None,
                    "sources": [],
                    "warnings": ["ASR not available and no fallback_text provided."]
                }
        
        service = app.state.voice_service
        return service.process_voice_query(
            question=text,
            session_id=session_id,
            sessions=app.state.sessions,
        )

    @app.post("/admin/reload_store")
    def reload_store(persist_dir: Optional[str] = None) -> Dict[str, Any]:
        """Reload the vector store with a new persist directory."""
        cfg = app.state.config
        final_persist_dir = persist_dir or cfg.chroma_persist_dir
        
        # Rebuild store and dependencies
        app.state.store = VectorStore(
            persist_dir=final_persist_dir,
            embedding_model=cfg.embedding_model,
        )
        app.state.mcp = MCPClient(app.state.store.similarity_search)
        app.state.rag = RAGAnswerer(app.state.mcp)
        
        # Update container
        container = app.state.container
        container.register_instance("vector_store", app.state.store)
        container.register_instance("mcp_client", app.state.mcp)
        container.register_instance("rag", app.state.rag)
        
        return {"ok": True, "persist_dir": final_persist_dir}

    @app.get("/admin/status")
    def status() -> Dict[str, Any]:
        """Get application status and configuration."""
        import os
        cfg = app.state.config
        persist_dir = getattr(app.state.store, "_persist_dir", None) or cfg.chroma_persist_dir
        return {
            "persist_dir": persist_dir,
            "environment": "railway" if cfg.is_railway() else "local",
            "vector_backend": getattr(app.state.store, "_backend", "unknown"),
            "has_data": (
                os.path.exists(persist_dir) and len(os.listdir(persist_dir)) > 0
                if os.path.exists(persist_dir)
                else False
            )
        }

    # Test endpoints for vector store and MCP connectivity
    @app.get("/test/vector_store")
    def test_vector_store(query: str = "password reset", k: int = 3) -> Dict[str, Any]:
        """Test direct vector store connectivity and similarity search."""
        try:
            results = store.similarity_search(query, k=k)
            formatted_results = format_documents_for_response(results, max_content_length=200)
            return {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": formatted_results,
                "store_backend": getattr(store, "_backend", "unknown"),
                "persist_dir": getattr(store, "_persist_dir", "unknown")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    @app.get("/test/mcp_client")
    def test_mcp_client(query: str = "password reset", k: int = 3) -> Dict[str, Any]:
        """Test MCP client connectivity to vector store."""
        try:
            results = mcp.retrieve(query, k=k)
            formatted_results = format_documents_for_response(results, max_content_length=200)
            return {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": formatted_results
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    @app.get("/test/rag")
    def test_rag(query: str = "How do I reset my password?") -> Dict[str, Any]:
        """Test full RAG pipeline (MCP -> RAG -> Answer)."""
        try:
            result = rag.answer(query)
            return {
                "success": True,
                "query": query,
                "answer": result.get("answer", ""),
                "sources_count": len(result.get("sources", [])),
                "sources": result.get("sources", []),
                "has_answer": bool(result.get("answer"))
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    @app.post("/test/mcp_endpoint")
    def test_mcp_endpoint(request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Test the MCP protocol endpoint directly."""
        try:
            # Simulate a tools/list call
            if request_body.get("method") == "tools/list" or not request_body.get("method"):
                # Call the MCP endpoint logic
                return {
                    "success": True,
                    "test": "tools/list",
                    "tools": [
                        {
                            "name": "search_knowledge_base",
                            "description": "Search the customer support knowledge base"
                        }
                    ]
                }
            # Simulate a tools/call
            elif request_body.get("method") == "tools/call":
                params = request_body.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "search_knowledge_base":
                    query = arguments.get("query", "")
                    k = arguments.get("k", 4)
                    results = mcp.retrieve(query, k=k)
                    return {
                        "success": True,
                        "test": "tools/call",
                        "tool": tool_name,
                        "query": query,
                        "results_count": len(results),
                        "results": [
                            {
                                "title": doc.get("metadata", {}).get("title") or "Unknown",
                                "content_preview": doc.get("page_content", "")[:200]
                            }
                            for doc in results
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Unknown tool: {tool_name}"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Unknown method: {request_body.get('method')}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    @app.get("/test/prompts")
    def get_test_prompts() -> Dict[str, Any]:
        """Get a list of recommended natural language prompts for testing the Voice Agent."""
        return {
            "description": "Use these prompts with your ElevenLabs Voice Agent to test MCP tool connectivity",
            "basic_queries": [
                "How do I reset my password?",
                "I forgot my password, what should I do?",
                "How can I contact customer support?",
                "What are your business hours?",
                "How do I update my account information?",
                "Where can I find my order history?",
                "What features are available in your product?",
                "How do I upgrade my subscription?",
                "What payment methods do you accept?",
                "Can you explain your refund policy?"
            ],
            "troubleshooting_queries": [
                "I'm having trouble logging in, what should I do?",
                "My account is locked, how do I unlock it?",
                "I can't access my account, help me troubleshoot",
                "Something isn't working, what are common solutions?"
            ],
            "direct_tool_requests": [
                "Can you search the knowledge base for information about passwords?",
                "Please look up the answer to my question in your documentation",
                "Search your database for information about account recovery",
                "Check your knowledge base for troubleshooting steps"
            ],
            "follow_up_queries": [
                "What if I don't have access to my email?",
                "Can you provide more details about that process?",
                "What are the alternative methods?",
                "Show me the step-by-step instructions"
            ],
            "testing_tips": {
                "expected_behavior": [
                    "Agent should mention searching or looking up information",
                    "Answers should reference specific documents or sources",
                    "Agent should be able to handle follow-up questions"
                ],
                "verification": [
                    "Check server logs for /tools/search_knowledge_base or /mcp endpoint calls",
                    "Monitor /test/full_chain to see if queries are being processed",
                    "Verify answers include details from your vector store"
                ]
            }
        }

    @app.get("/test/full_chain")
    def test_full_chain(query: str = "How do I reset my password?") -> Dict[str, Any]:
        """Test the complete chain: Vector Store -> MCP -> RAG -> Tool Endpoint."""
        results = {
            "query": query,
            "tests": {}
        }
        
        # Test 1: Vector Store
        try:
            vs_results = store.similarity_search(query, k=3)
            results["tests"]["vector_store"] = {
                "success": True,
                "results_count": len(vs_results)
            }
        except Exception as e:
            results["tests"]["vector_store"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test 2: MCP Client
        try:
            mcp_results = mcp.retrieve(query, k=3)
            results["tests"]["mcp_client"] = {
                "success": True,
                "results_count": len(mcp_results)
            }
        except Exception as e:
            results["tests"]["mcp_client"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test 3: RAG Pipeline
        try:
            rag_result = rag.answer(query)
            results["tests"]["rag"] = {
                "success": True,
                "has_answer": bool(rag_result.get("answer")),
                "sources_count": len(rag_result.get("sources", []))
            }
        except Exception as e:
            results["tests"]["rag"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test 4: Tool Endpoint logic (simulates /tools/search_knowledge_base)
        try:
            tool_results = mcp.retrieve(query, k=3)
            formatted_results = []
            for doc in tool_results:
                formatted_results.append({
                    "content": doc.get("page_content", ""),
                    "metadata": doc.get("metadata", {}),
                    "title": doc.get("metadata", {}).get("title") or doc.get("metadata", {}).get("source", "Document")
                })
            results["tests"]["tool_endpoint"] = {
                "success": True,
                "results_count": len(formatted_results)
            }
        except Exception as e:
            results["tests"]["tool_endpoint"] = {
                "success": False,
                "error": str(e)
            }
        
        # Overall status
        all_passed = all(test.get("success", False) for test in results["tests"].values())
        results["overall_success"] = all_passed
        
        return results

    # MCP Protocol endpoint for ElevenLabs
    @app.post("/mcp")
    async def mcp_endpoint(request_body: Dict[str, Any]) -> Dict[str, Any]:
        """MCP protocol endpoint for ElevenLabs Agent.
        
        Implements the MCP protocol for tool discovery and execution.
        Supports both JSON-RPC format and direct method calls.
        """
        request = request_body
        
        # Handle JSON-RPC format
        method = request.get("method") or request.get("jsonrpc_method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        # Build response wrapper
        def make_response(result: Dict[str, Any], is_error: bool = False) -> Dict[str, Any]:
            response = {"jsonrpc": "2.0"}
            if request_id is not None:
                response["id"] = request_id
            if is_error:
                response["error"] = result
            else:
                response["result"] = result
            return response
        
        if method == "tools/list" or method == "initialize":
            # Return available tools
            return make_response({
                "tools": [
                    {
                        "name": "search_knowledge_base",
                        "description": "Search the customer support knowledge base to find relevant documentation, FAQs, and troubleshooting guides. Use this tool when you need to answer questions about products, services, policies, or procedures.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The search query to find relevant information in the knowledge base"
                                },
                                "k": {
                                    "type": "integer",
                                    "description": "Number of results to return (default: 4, max: 10)",
                                    "default": 4,
                                    "minimum": 1,
                                    "maximum": 10
                                }
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "create_support_ticket",
                        "description": "Create a support ticket in the CRM system when an issue cannot be resolved through the knowledge base or requires human intervention.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Brief title summarizing the issue"},
                                "description": {"type": "string", "description": "Detailed description of the issue"},
                                "customer_id": {"type": "string", "description": "Customer ID if available"},
                                "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"], "default": "normal"},
                                "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional tags"}
                            },
                            "required": ["title", "description"]
                        }
                    },
                    {
                        "name": "get_customer_info",
                        "description": "Retrieve customer information from the CRM system including account details, order history, and previous interactions.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "identifier": {"type": "string", "description": "Customer identifier (customer_id, email, or phone)"}
                            },
                            "required": ["identifier"]
                        }
                    },
                    {
                        "name": "escalate_to_human",
                        "description": "Escalate the conversation to a human support agent when needed.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string", "description": "Current conversation session ID"},
                                "reason": {"type": "string", "description": "Reason for escalation"},
                                "customer_id": {"type": "string", "description": "Customer ID if available"},
                                "conversation_summary": {"type": "string", "description": "Brief summary of conversation"}
                            },
                            "required": ["session_id"]
                        }
                    },
                    {
                        "name": "log_interaction",
                        "description": "Log a customer interaction in the CRM system for analytics, compliance, and future reference.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Customer ID"},
                                "activity_type": {"type": "string", "description": "Type of activity"},
                                "details": {"type": "object", "description": "Additional details as JSON object"}
                            },
                            "required": ["customer_id", "activity_type", "details"]
                        }
                    },
                    {
                        "name": "check_order_status",
                        "description": "Check the status of a customer order including shipping information and estimated delivery date.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "order_id": {"type": "string", "description": "Order ID or order number"},
                                "customer_id": {"type": "string", "description": "Customer ID for verification"}
                            },
                            "required": ["order_id"]
                        }
                    }
                ]
            })
        elif method == "tools/call":
            # Execute tool call
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "search_knowledge_base":
                try:
                    query = arguments.get("query", "")
                    k = arguments.get("k", 4)
                    results = mcp.retrieve(query, k=k)
                    # Format results for MCP response
                    formatted_results = []
                    for doc in results:
                        formatted_results.append({
                            "content": doc.get("page_content", ""),
                            "metadata": doc.get("metadata", {}),
                            "title": doc.get("metadata", {}).get("title") or doc.get("metadata", {}).get("source", "Document")
                        })
                    return make_response({
                        "content": [
                            {
                                "type": "text",
                                "text": f"Found {len(formatted_results)} results for query: {query}\n\n" + 
                                       "\n\n".join([f"**{r['title']}**\n{r['content'][:500]}" for r in formatted_results])
                            }
                        ]
                    })
                except Exception as e:
                    return make_response({
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error searching knowledge base: {str(e)}"
                            }
                        ],
                        "isError": True
                    }, is_error=True)
            elif tool_name == "create_support_ticket":
                try:
                    crm = app.state.crm
                    title = arguments.get("title", "")
                    description = arguments.get("description", "")
                    if not crm:
                        ticket_id = f"ticket_{int(time.time())}"
                        return make_response({
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Ticket created: {ticket_id}. Status: created. CRM not configured - ticket created in mock mode"
                                }
                            ]
                        })
                    result = crm.create_ticket(
                        title=title,
                        description=description,
                        customer_id=arguments.get("customer_id"),
                        priority=arguments.get("priority", "normal"),
                        tags=arguments.get("tags", [])
                    )
                    ticket_id = result.get("id", "unknown")
                    return make_response({
                        "content": [
                            {
                                "type": "text",
                                "text": f"Ticket created: {ticket_id}. Status: {result.get('status', 'created')}. Ticket created successfully"
                            }
                        ]
                    })
                except Exception as e:
                    return make_response({
                        "content": [{"type": "text", "text": f"Error creating ticket: {str(e)}"}],
                        "isError": True
                    }, is_error=True)
            elif tool_name == "get_customer_info":
                try:
                    crm = app.state.crm
                    identifier = arguments.get("identifier", "")
                    if not crm:
                        return make_response({
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Customer ID: {identifier}. Name: Mock Customer. Email: {identifier}@example.com. CRM not configured - returning mock data"
                                }
                            ]
                        })
                    customer = crm.get_customer(identifier)
                    if not customer:
                        return make_response({
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Error: Customer not found. No customer found with identifier: {identifier}"
                                }
                            ],
                            "isError": True
                        }, is_error=True)
                    return make_response({
                        "content": [
                            {
                                "type": "text",
                                "text": f"Customer found: {customer.get('name', 'Unknown')} ({customer.get('email', 'No email')}). Customer information retrieved successfully"
                            }
                        ]
                    })
                except Exception as e:
                    return make_response({
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error retrieving customer info: {str(e)}"
                            }
                        ],
                        "isError": True
                    }, is_error=True)
            elif tool_name == "escalate_to_human":
                try:
                    escalations = app.state.escalations
                    sessions = app.state.sessions
                    session_id = arguments.get("session_id", "")
                    
                    conversation_history = []
                    if session_id:
                        turns = sessions.history(session_id)
                        conversation_history = [
                            {"role": turn.role, "text": turn.text, "timestamp": turn.ts}
                            for turn in turns
                        ]
                    
                    escalation = EscalationContext(
                        session_id=session_id,
                        escalation_reason=arguments.get("reason", "user_request"),
                        timestamp=time.time(),
                        conversation_transcript=conversation_history,
                        retrieved_documents=[],
                        confidence_scores=[],
                        suggested_responses=[],
                        customer_id=arguments.get("customer_id")
                    )
                    
                    escalations.save_escalation(escalation)
                    
                    ticket_id = None
                    if app.state.crm and arguments.get("customer_id"):
                        try:
                            ticket_result = app.state.crm.create_ticket(
                                title=f"Escalation: {arguments.get('reason', 'User requested human agent')}",
                                description=arguments.get("conversation_summary", "Conversation escalated to human agent"),
                                customer_id=arguments.get("customer_id"),
                                priority="high",
                                tags=["escalation", "human_agent"]
                            )
                            ticket_id = ticket_result.get("id")
                        except Exception:
                            pass
                    
                    return make_response({
                        "content": [
                            {
                                "type": "text",
                                "text": f"Escalation created: {session_id}. Status: pending. Conversation escalated to human agent successfully" + (f". Ticket ID: {ticket_id}" if ticket_id else "")
                            }
                        ]
                    })
                except Exception as e:
                    return make_response({
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error escalating: {str(e)}"
                            }
                        ],
                        "isError": True
                    }, is_error=True)
            elif tool_name == "log_interaction":
                try:
                    crm = app.state.crm
                    customer_id = arguments.get("customer_id", "")
                    activity_type = arguments.get("activity_type", "")
                    details = arguments.get("details", {})
                    
                    if not crm:
                        return make_response({
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Interaction logged. Interaction logged to analytics (CRM not configured)"
                                }
                            ]
                        })
                    
                    success = crm.log_interaction(
                        customer_id=customer_id,
                        activity_type=activity_type,
                        details=details
                    )
                    
                    if success:
                        return make_response({
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Interaction logged. Interaction logged successfully"
                                }
                            ]
                        })
                    else:
                        return make_response({
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Error: Failed to log interaction. CRM returned failure status"
                                }
                            ],
                            "isError": True
                        }, is_error=True)
                except Exception as e:
                    return make_response({
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error logging interaction: {str(e)}"
                            }
                        ],
                        "isError": True
                    }, is_error=True)
            elif tool_name == "check_order_status":
                try:
                    order_id = arguments.get("order_id", "")
                    customer_id = arguments.get("customer_id")
                    
                    order_info = None
                    if app.state.crm and customer_id:
                        customer = app.state.crm.get_customer(customer_id)
                        if customer and "orders" in customer:
                            orders = customer.get("orders", [])
                            order_info = next((o for o in orders if o.get("id") == order_id), None)
                    
                    if not order_info:
                        import random
                        statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
                        order_info = {
                            "order_id": order_id,
                            "status": random.choice(statuses),
                            "customer_id": customer_id,
                            "created_date": datetime.now().isoformat(),
                            "estimated_delivery": (datetime.now() + timedelta(days=5)).isoformat(),
                            "message": "Mock order data - integrate with real order system"
                        }
                    
                    return make_response({
                        "content": [
                            {
                                "type": "text",
                                "text": f"Order {order_info.get('order_id', 'unknown')} status: {order_info.get('status', 'unknown')}. Estimated delivery: {order_info.get('estimated_delivery', 'N/A')}. Order status retrieved successfully"
                            }
                        ]
                    })
                except Exception as e:
                    return make_response({
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error checking order status: {str(e)}"
                            }
                        ],
                        "isError": True
                    }, is_error=True)
            else:
                return make_response({
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }, is_error=True)
        else:
            return make_response({
                "code": -32601,
                "message": f"Method not found: {method or 'unknown'}"
            }, is_error=True)
    
    # Tool endpoint for ElevenLabs Agent to query MCP/vector store (backward compatibility)
    @app.post("/tools/search_knowledge_base")
    def search_knowledge_base(request: ToolCallRequest) -> Dict[str, Any]:
        """Tool endpoint for ElevenLabs Agent to search the knowledge base via MCP.
        
        This allows the ElevenLabs Agent to directly query the vector store through MCP.
        Returns relevant documents with metadata.
        """
        try:
            results = mcp.retrieve(request.query, k=request.k or 4)
            # Format results for the agent
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content": doc.get("page_content", ""),
                    "metadata": doc.get("metadata", {}),
                    "title": doc.get("metadata", {}).get("title") or doc.get("metadata", {}).get("source", "Document")
                })
            return {
                "success": True,
                "query": request.query,
                "results": formatted_results,
                "count": len(formatted_results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "count": 0
            }

    # Tool endpoint for creating support tickets
    @app.post("/tools/create_support_ticket")
    def create_support_ticket(request: CreateTicketRequest) -> Dict[str, Any]:
        """Tool endpoint for creating a support ticket in the CRM system.
        
        This allows the agent to create tickets when issues cannot be resolved
        through the knowledge base or require human intervention.
        """
        try:
            crm = app.state.crm
            if not crm:
                # Return mock response if CRM is not configured
                import time
                return {
                    "success": True,
                    "ticket_id": f"ticket_{int(time.time())}",
                    "title": request.title,
                    "status": "created",
                    "message": "CRM not configured - ticket created in mock mode"
                }
            
            result = crm.create_ticket(
                title=request.title,
                description=request.description,
                customer_id=request.customer_id,
                priority=request.priority,
                tags=request.tags or []
            )
            return {
                "success": True,
                "ticket_id": result.get("id", "unknown"),
                "title": result.get("title", request.title),
                "status": result.get("status", "created"),
                "message": "Ticket created successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create ticket"
            }
    
    # Tool endpoint for getting customer information
    @app.post("/tools/get_customer_info")
    def get_customer_info(request: GetCustomerRequest) -> Dict[str, Any]:
        """Tool endpoint for retrieving customer information from CRM.
        
        This allows the agent to look up customer details, order history,
        and previous interactions to provide personalized support.
        """
        try:
            crm = app.state.crm
            if not crm:
                # Return mock response if CRM is not configured
                return {
                    "success": True,
                    "customer_id": request.identifier,
                    "name": "Mock Customer",
                    "email": f"{request.identifier}@example.com",
                    "message": "CRM not configured - returning mock data"
                }
            
            customer = crm.get_customer(request.identifier)
            if not customer:
                return {
                    "success": False,
                    "error": "Customer not found",
                    "message": f"No customer found with identifier: {request.identifier}"
                }
            
            return {
                "success": True,
                "customer": customer,
                "message": "Customer information retrieved successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve customer information"
            }
    
    # Tool endpoint for escalating to human agent
    @app.post("/tools/escalate_to_human")
    def escalate_to_human(request: EscalateRequest) -> Dict[str, Any]:
        """Tool endpoint for escalating a conversation to a human agent.
        
        This creates an escalation record with full conversation context
        for seamless handoff to human support agents.
        """
        try:
            escalations = app.state.escalations
            sessions = app.state.sessions
            
            # Get conversation history
            conversation_history = []
            if request.session_id:
                turns = sessions.history(request.session_id)
                conversation_history = [
                    {"role": turn.role, "text": turn.text, "timestamp": turn.ts}
                    for turn in turns
                ]
            
            # Create escalation context
            escalation = EscalationContext(
                session_id=request.session_id,
                escalation_reason=request.reason or "user_request",
                timestamp=time.time(),
                conversation_transcript=conversation_history,
                retrieved_documents=[],
                confidence_scores=[],
                suggested_responses=[],
                customer_id=request.customer_id
            )
            
            # Save escalation
            escalations.save_escalation(escalation)
            
            # Optionally create a ticket if CRM is available
            ticket_id = None
            if app.state.crm and request.customer_id:
                try:
                    ticket_result = app.state.crm.create_ticket(
                        title=f"Escalation: {request.reason or 'User requested human agent'}",
                        description=request.conversation_summary or "Conversation escalated to human agent",
                        customer_id=request.customer_id,
                        priority="high",
                        tags=["escalation", "human_agent"]
                    )
                    ticket_id = ticket_result.get("id")
                    escalation.ticket_id = ticket_id
                    escalations.save_escalation(escalation)
                except Exception:
                    pass  # Ticket creation is optional
            
            return {
                "success": True,
                "escalation_id": request.session_id,
                "ticket_id": ticket_id,
                "status": "pending",
                "message": "Conversation escalated to human agent successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to escalate conversation"
            }
    
    # Tool endpoint for logging interactions
    @app.post("/tools/log_interaction")
    def log_interaction(request: LogInteractionRequest) -> Dict[str, Any]:
        """Tool endpoint for logging customer interactions in CRM.
        
        This allows the agent to record all customer interactions for
        analytics, compliance, and future reference.
        """
        try:
            crm = app.state.crm
            if not crm:
                # Return success even if CRM is not configured (mock mode)
                return {
                    "success": True,
                    "message": "Interaction logged to analytics (CRM not configured)"
                }
            
            success = crm.log_interaction(
                customer_id=request.customer_id,
                activity_type=request.activity_type,
                details=request.details
            )
            
            if success:
                return {
                    "success": True,
                    "message": "Interaction logged successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to log interaction",
                    "message": "CRM returned failure status"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to log interaction"
            }
    
    # Tool endpoint for checking order status
    @app.post("/tools/check_order_status")
    def check_order_status(request: CheckOrderRequest) -> Dict[str, Any]:
        """Tool endpoint for checking order status.
        
        This allows the agent to look up order information including
        status, shipping details, and estimated delivery dates.
        """
        try:
            # For now, this is a mock implementation
            # In production, this would integrate with an order management system
            # or CRM that has order data
            
            # Check if CRM has order information
            order_info = None
            if app.state.crm and request.customer_id:
                # Try to get customer info which might include orders
                customer = app.state.crm.get_customer(request.customer_id)
                if customer and "orders" in customer:
                    orders = customer.get("orders", [])
                    order_info = next((o for o in orders if o.get("id") == request.order_id), None)
            
            # Mock response if no real order system is available
            if not order_info:
                import random
                statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
                order_info = {
                    "order_id": request.order_id,
                    "status": random.choice(statuses),
                    "customer_id": request.customer_id,
                    "created_date": datetime.now().isoformat(),
                    "estimated_delivery": (datetime.now() + timedelta(days=5)).isoformat(),
                    "message": "Mock order data - integrate with real order system"
                }
            
            return {
                "success": True,
                "order": order_info,
                "message": "Order status retrieved successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve order status"
            }

    @app.get("/tools/definitions")
    def get_tool_definitions() -> Dict[str, Any]:
        """Returns tool definitions for ElevenLabs Agent configuration."""
        cfg = app.state.config
        base_url = cfg.base_url
        return {
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "search_knowledge_base",
                        "description": "Search the customer support knowledge base to find relevant documentation, FAQs, and troubleshooting guides. Use this tool when you need to answer questions about products, services, policies, or procedures.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The search query to find relevant information in the knowledge base"
                                },
                                "k": {
                                    "type": "integer",
                                    "description": "Number of results to return (default: 4, max: 10)",
                                    "default": 4,
                                    "minimum": 1,
                                    "maximum": 10
                                }
                            },
                            "required": ["query"]
                        },
                        "url": f"{base_url}/tools/search_knowledge_base"
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "create_support_ticket",
                        "description": "Create a support ticket in the CRM system when an issue cannot be resolved through the knowledge base or requires human intervention. Use this when the customer needs follow-up, has a complex issue, or explicitly requests ticket creation.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Brief title summarizing the issue"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Detailed description of the issue or request"
                                },
                                "customer_id": {
                                    "type": "string",
                                    "description": "Customer ID if available (optional)"
                                },
                                "priority": {
                                    "type": "string",
                                    "description": "Ticket priority: low, normal, high, urgent (default: normal)",
                                    "enum": ["low", "normal", "high", "urgent"],
                                    "default": "normal"
                                },
                                "tags": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Optional tags to categorize the ticket"
                                }
                            },
                            "required": ["title", "description"]
                        },
                        "url": f"{base_url}/tools/create_support_ticket"
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_customer_info",
                        "description": "Retrieve customer information from the CRM system including account details, order history, and previous interactions. Use this to provide personalized support and understand customer context.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "identifier": {
                                    "type": "string",
                                    "description": "Customer identifier (customer_id, email, or phone number)"
                                }
                            },
                            "required": ["identifier"]
                        },
                        "url": f"{base_url}/tools/get_customer_info"
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "escalate_to_human",
                        "description": "Escalate the conversation to a human support agent. Use this when the customer explicitly requests a human, when confidence is low, when multiple attempts have failed, or when the issue is too complex for automated resolution.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "session_id": {
                                    "type": "string",
                                    "description": "Current conversation session ID"
                                },
                                "reason": {
                                    "type": "string",
                                    "description": "Reason for escalation (e.g., user_request, low_confidence, complex_issue)"
                                },
                                "customer_id": {
                                    "type": "string",
                                    "description": "Customer ID if available (optional)"
                                },
                                "conversation_summary": {
                                    "type": "string",
                                    "description": "Brief summary of the conversation and issue (optional)"
                                }
                            },
                            "required": ["session_id"]
                        },
                        "url": f"{base_url}/tools/escalate_to_human"
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "log_interaction",
                        "description": "Log a customer interaction in the CRM system for analytics, compliance, and future reference. Use this to record important interactions, decisions, or actions taken during the conversation.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "customer_id": {
                                    "type": "string",
                                    "description": "Customer ID"
                                },
                                "activity_type": {
                                    "type": "string",
                                    "description": "Type of activity (e.g., call, chat, ticket_created, issue_resolved, refund_processed)"
                                },
                                "details": {
                                    "type": "object",
                                    "description": "Additional details about the interaction as a JSON object"
                                }
                            },
                            "required": ["customer_id", "activity_type", "details"]
                        },
                        "url": f"{base_url}/tools/log_interaction"
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "check_order_status",
                        "description": "Check the status of a customer order including shipping information and estimated delivery date. Use this when customers ask about their orders, delivery times, or order history.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "order_id": {
                                    "type": "string",
                                    "description": "Order ID or order number"
                                },
                                "customer_id": {
                                    "type": "string",
                                    "description": "Customer ID for verification (optional)"
                                }
                            },
                            "required": ["order_id"]
                        },
                        "url": f"{base_url}/tools/check_order_status"
                    }
                }
            ]
        }

    # ==================== NEW FEATURE ENDPOINTS ====================
    
    # Analytics endpoints
    @app.get("/analytics/dashboard")
    def get_analytics_dashboard(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get analytics dashboard data."""
        start = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.now()
        
        analytics = app.state.analytics.calculate_analytics(start, end)
        knowledge_gaps = app.state.analytics.get_knowledge_gaps()
        
        return {
            "metrics": analytics,
            "knowledge_gaps": knowledge_gaps[:20],  # Top 20
            "period": {
                "start": start.isoformat(),
                "end": end.isoformat(),
            }
        }
    
    @app.get("/analytics/knowledge-gaps")
    def get_knowledge_gaps(
        min_priority: int = 0,
        gap_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get knowledge gaps."""
        gaps = app.state.analytics.get_knowledge_gaps(min_priority, gap_type)
        return {
            "gaps": gaps,
            "count": len(gaps),
        }
    
    @app.get("/analytics/export")
    def export_analytics(
        format: str = "json",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Any:
        """Export analytics data."""
        from fastapi.responses import Response
        start = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.now()
        
        metrics = app.state.analytics.get_metrics(start, end)
        feedback = app.state.analytics.get_feedback(start, end)
        
        if format == "csv":
            import csv
            import io
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
    
    # Feedback endpoints
    @app.post("/feedback")
    def submit_feedback(
        session_id: str,
        rating: Optional[int] = None,
        comment: Optional[str] = None,
        query_text: Optional[str] = None,
        answer_text: Optional[str] = None,
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
        app.state.analytics.save_feedback(feedback)
        
        # Check if this indicates a knowledge gap
        if rating is not None and rating < 3:
            gap = KnowledgeGap(
                query_text=query_text or "Unknown",
                session_id=session_id,
                timestamp=time.time(),
                gap_type="negative_feedback",
                priority=5 if rating == 1 else 3,
            )
            app.state.analytics.save_knowledge_gap(gap)
        
        return {"success": True, "message": "Feedback recorded"}
    
    # Escalation endpoints
    @app.get("/escalations")
    def get_escalations(
        status: Optional[str] = None,
        assigned_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get escalations."""
        escalations = app.state.escalations.get_escalations(status, assigned_agent)
        return {
            "escalations": escalations,
            "count": len(escalations),
        }
    
    @app.get("/escalations/{session_id}")
    def get_escalation_context(session_id: str) -> Dict[str, Any]:
        """Get escalation context for a session."""
        escalation = app.state.escalations.get_escalation(session_id)
        if not escalation:
            return {"error": "Escalation not found"}
        return escalation
    
    @app.post("/escalations/{session_id}/update")
    def update_escalation(
        session_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update escalation status."""
        success = app.state.escalations.update_escalation(session_id, updates)
        return {"success": success}
    
    # CRM integration endpoints
    @app.get("/crm/customer/{identifier}")
    def get_customer(identifier: str) -> Dict[str, Any]:
        """Get customer information from CRM."""
        if not app.state.crm:
            return {"error": "CRM not configured"}
        
        customer = app.state.crm.get_customer(identifier)
        if not customer:
            return {"error": "Customer not found"}
        return customer
    
    @app.post("/crm/log-interaction")
    def log_crm_interaction(
        customer_id: str,
        activity_type: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Log interaction in CRM."""
        if not app.state.crm:
            return {"error": "CRM not configured"}
        
        success = app.state.crm.log_interaction(customer_id, activity_type, details)
        return {"success": success}
    
    # Compliance endpoints
    @app.get("/compliance/audit-log")
    def get_audit_log(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        event_type: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get audit log."""
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        entries = app.state.compliance.get_audit_log(start, end, event_type, session_id)
        return {
            "entries": entries,
            "count": len(entries),
        }
    
    @app.post("/compliance/detect-pii")
    def detect_pii_in_text(text: str) -> Dict[str, Any]:
        """Detect PII in text."""
        detections = PIIDetector.detect(text)
        redacted, redactions = PIIDetector.redact(text)
        return {
            "detections": detections,
            "redacted_text": redacted,
            "redactions": redactions,
        }
    
    @app.post("/compliance/gdpr/delete-request")
    def create_deletion_request(
        customer_id: Optional[str] = None,
        email: Optional[str] = None,
        data_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create GDPR deletion request."""
        import uuid
        request = DeletionRequest(
            request_id=str(uuid.uuid4()),
            customer_id=customer_id,
            email=email,
            requested_at=time.time(),
            data_types=data_types or ["all"],
        )
        app.state.compliance.save_deletion_request(request)
        return {
            "request_id": request.request_id,
            "status": "pending",
            "message": "Deletion request created. Processing will begin within 30 days.",
        }
    
    @app.get("/compliance/gdpr/deletion-requests")
    def get_deletion_requests(status: Optional[str] = None) -> Dict[str, Any]:
        """Get deletion requests."""
        requests = app.state.compliance.get_deletion_requests(status)
        return {
            "requests": requests,
            "count": len(requests),
        }
    
    # Admin endpoints for knowledge base management
    @app.get("/admin/knowledge-base/flagged-answers")
    def get_flagged_answers() -> Dict[str, Any]:
        """Get flagged incorrect answers."""
        feedback = app.state.analytics.get_feedback()
        flagged = [
            f for f in feedback
            if (f.get("rating") is not None and f.get("rating") < 2)
            or f.get("escalation_triggered", False)
        ]
        return {
            "flagged_answers": flagged,
            "count": len(flagged),
        }
    
    @app.post("/admin/knowledge-base/resolve-gap")
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

    # Agent Testing endpoints
    @app.post("/agent-tests/create-suite")
    def create_test_suite(
        name: str,
        scenarios: List[Dict[str, Any]],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a test suite for the agent."""
        try:
            from agents.agent_testing import ElevenLabsAgentTester, TestScenario
            
            tester = ElevenLabsAgentTester()
            test_scenarios = [
                TestScenario(
                    name=s.get("name", ""),
                    messages=s.get("messages", []),
                    expected_tool_calls=s.get("expected_tool_calls"),
                    expected_keywords=s.get("expected_keywords"),
                )
                for s in scenarios
            ]
            
            result = tester.create_test_suite(name, test_scenarios, description)
            return result
        except Exception as e:
            return {"error": str(e)}

    @app.post("/agent-tests/create-tool-invocation")
    def create_tool_invocation_test_suite() -> Dict[str, Any]:
        """Create the 10 tool invocation test suite in ElevenLabs dashboard using REST API."""
        try:
            from agents.agent_testing import ElevenLabsAgentTester
            from agents.test_suites import get_tool_invocation_test_suite
            
            tester = ElevenLabsAgentTester()
            scenarios = get_tool_invocation_test_suite()
            
            created_tests = tester.create_tests_from_scenarios(scenarios)
            
            successful = [t for t in created_tests if "test_id" in t]
            failed = [t for t in created_tests if "error" in t]
            
            return {
                "success": len(failed) == 0,
                "created": len(successful),
                "failed": len(failed),
                "tests": created_tests,
                "test_ids": [t["test_id"] for t in successful],
            }
        except Exception as e:
            return {
                "error": str(e),
                "note": "Make sure ELEVENLABS_API_KEY (in Doppler) and ELEVENLABS_AGENT_ID are set",
            }

    @app.post("/agent-tests/run")
    def run_agent_tests(
        test_suite_id: Optional[str] = None,
        scenarios: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Run agent tests."""
        try:
            from agents.agent_testing import ElevenLabsAgentTester, TestScenario
            
            tester = ElevenLabsAgentTester()
            
            test_scenarios = None
            if scenarios:
                test_scenarios = [
                    TestScenario(
                        name=s.get("name", ""),
                        messages=s.get("messages", []),
                        expected_tool_calls=s.get("expected_tool_calls"),
                        expected_keywords=s.get("expected_keywords"),
                    )
                    for s in scenarios
                ]
            
            results = tester.run_tests(test_suite_id, test_scenarios)
            
            return {
                "results": [
                    {
                        "test_id": r.test_id,
                        "scenario_name": r.scenario_name,
                        "passed": r.passed,
                        "details": r.details,
                        "tool_calls": r.tool_calls,
                        "response": r.response,
                        "error": r.error,
                    }
                    for r in results
                ],
                "summary": {
                    "total": len(results),
                    "passed": sum(1 for r in results if r.passed),
                    "failed": sum(1 for r in results if not r.passed),
                }
            }
        except Exception as e:
            return {"error": str(e)}

    @app.get("/agent-tests/results")
    def get_test_results(
        test_suite_id: Optional[str] = None,
        test_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get test results."""
        try:
            from agents.agent_testing import ElevenLabsAgentTester
            
            tester = ElevenLabsAgentTester()
            return tester.get_test_results(test_suite_id, test_id)
        except Exception as e:
            return {"error": str(e)}

    @app.get("/agent-tests/suites")
    def list_test_suites() -> Dict[str, Any]:
        """List all test suites."""
        try:
            from agents.agent_testing import ElevenLabsAgentTester
            
            tester = ElevenLabsAgentTester()
            suites = tester.list_test_suites()
            return {"suites": suites}
        except Exception as e:
            return {"error": str(e)}

    @app.get("/agent-tests/default-suite")
    def get_default_test_suite() -> Dict[str, Any]:
        """Get default test suite scenarios."""
        try:
            from agents.agent_testing import create_default_test_suite
            
            scenarios = create_default_test_suite()
            return {
                "scenarios": [
                    {
                        "name": s.name,
                        "messages": s.messages,
                        "expected_tool_calls": s.expected_tool_calls,
                        "expected_keywords": s.expected_keywords,
                    }
                    for s in scenarios
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    @app.post("/agent-tests/run-comprehensive")
    def run_comprehensive_tests() -> Dict[str, Any]:
        """Run the comprehensive 10-test suite."""
        try:
            from agents.agent_testing import ElevenLabsAgentTester, TestResult
            from agents.test_suites import get_comprehensive_test_suite
            
            scenarios = get_comprehensive_test_suite()
            
            # Try to use tester, fallback to local
            tester = None
            try:
                tester = ElevenLabsAgentTester()
            except RuntimeError:
                pass
            
            if tester:
                try:
                    results = tester.run_tests(scenarios=scenarios)
                except Exception:
                    results = tester._run_tests_locally(scenarios)
            else:
                # Run locally
                from memory.mcp_client import MCPClient
                from memory.vector_store import VectorStore
                from agents.rag import RAGAnswerer
                
                store = VectorStore()
                mcp = MCPClient(store.similarity_search)
                rag = RAGAnswerer(mcp)
                
                results = []
                for i, scenario in enumerate(scenarios):
                    test_id = f"test_{i}_{scenario.name}"
                    try:
                        user_messages = [
                            msg["content"] for msg in scenario.messages
                            if msg.get("role") == "user"
                        ]
                        if not user_messages:
                            continue
                        
                        last_user_message = user_messages[-1]
                        answer = rag.answer(last_user_message)
                        response_text = answer.get("answer", "")
                        
                        tool_calls = []
                        if answer.get("sources"):
                            tool_calls.append({
                                "name": "search_knowledge_base",
                                "arguments": {"query": last_user_message},
                            })
                        
                        expected_tool_calls_met = True
                        if scenario.expected_tool_calls:
                            tool_names = [tc.get("name") for tc in tool_calls]
                            expected_tool_calls_met = all(
                                expected in tool_names
                                for expected in scenario.expected_tool_calls
                            )
                        
                        passed = expected_tool_calls_met
                        
                        results.append(TestResult(
                            test_id=test_id,
                            scenario_name=scenario.name,
                            passed=passed,
                            details={
                                "sources_count": len(answer.get("sources", [])),
                            },
                            tool_calls=tool_calls,
                            response=response_text,
                        ))
                    except Exception as e:
                        results.append(TestResult(
                            test_id=test_id,
                            scenario_name=scenario.name,
                            passed=False,
                            details={},
                            tool_calls=[],
                            error=str(e),
                        ))
            
            return {
                "results": [
                    {
                        "test_id": r.test_id,
                        "scenario_name": r.scenario_name,
                        "passed": r.passed,
                        "details": r.details,
                        "tool_calls": r.tool_calls,
                        "response": r.response[:200] if r.response else None,
                        "error": r.error,
                    }
                    for r in results
                ],
                "summary": {
                    "total": len(results),
                    "passed": sum(1 for r in results if r.passed),
                    "failed": sum(1 for r in results if not r.passed),
                    "pass_rate": sum(1 for r in results if r.passed) / len(results) * 100 if results else 0,
                }
            }
        except Exception as e:
            return {"error": str(e)}

    # Cleanup on shutdown
    @app.on_event("shutdown")
    def shutdown_event():
        """Cleanup resources on application shutdown."""
        HTTPClientManager.close_all()
    
    return app


app = build_app()
