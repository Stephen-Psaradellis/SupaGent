from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any, Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from memory.vector_store import VectorStore
from memory.mcp_client import MCPClient
from agents.rag import RAGAnswerer
from agents.voice import VoiceAgent, ElevenLabsTTS
from agents.eleven_agent import ElevenLabsAgentClient, ElevenLabsVoiceAgent
from agents.asr import ElevenLabsASR
from memory.session import SessionStore


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


def build_app() -> FastAPI:
    app = FastAPI(title="SupaGent Support Agent")

    # Initialize components (stored on app.state for hot-reload capability)
    def _build_store(persist_dir: str | None = None) -> VectorStore:
        # Default to Railway-friendly path, fallback to local development path
        default_persist_dir = "/app/data/chroma" if os.getenv("RAILWAY_ENVIRONMENT") else "./data/chroma"
        return VectorStore(
            persist_dir=persist_dir or os.getenv("CHROMA_PERSIST_DIR", default_persist_dir),
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        )

    app.state.store = _build_store()
    app.state.mcp = MCPClient(app.state.store.similarity_search)
    app.state.rag = RAGAnswerer(app.state.mcp)
    # Default to Railway-friendly path for sessions
    default_sessions_dir = "/app/data/sessions" if os.getenv("RAILWAY_ENVIRONMENT") else "./data/sessions"
    app.state.sessions = SessionStore(root_dir=os.getenv("SESSIONS_DIR", default_sessions_dir))

    # Helper function to create/register MCP server with ElevenLabs
    def create_or_get_mcp_server() -> Optional[str]:
        """Create or retrieve MCP server configuration in ElevenLabs.
        
        Returns the MCP server ID if successful, None otherwise.
        """
        try:
            from elevenlabs.client import ElevenLabs  # type: ignore
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                return None
            
            client = ElevenLabs(api_key=api_key)
            # Auto-detect Railway public URL if available
            railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
            railway_url = f"https://{railway_public_domain}" if railway_public_domain else None
            
            # Use Railway URL if available, otherwise use SUPAGENT_BASE_URL or default
            base_url = railway_url or os.getenv("SUPAGENT_BASE_URL", "http://localhost:8000")
            mcp_server_name = os.getenv("SUPAGENT_MCP_SERVER_NAME", "SupaGent Knowledge Base")
            
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

    # Create/register MCP server with ElevenLabs
    if os.getenv("ELEVENLABS_API_KEY"):
        mcp_server_id = create_or_get_mcp_server()
        if mcp_server_id:
            os.environ["ELEVENLABS_MCP_SERVER_ID"] = mcp_server_id

    # Auto-create ElevenLabs Agent if API key is present and no agent id provided
    if os.getenv("ELEVENLABS_API_KEY") and not os.getenv("ELEVENLABS_AGENT_ID"):
        try:
            from elevenlabs.client import ElevenLabs  # type: ignore
            from pathlib import Path
            client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
            
            # Create agent
            create_kwargs = {"name": os.getenv("SUPAGENT_AGENT_NAME", "SupaGent Support Agent")}
            agent = client.agents.create(**create_kwargs)
            
            aid = getattr(agent, "id", None) or getattr(agent, "agent_id", None)
            if aid:
                os.environ["ELEVENLABS_AGENT_ID"] = aid
                # persist to .env so restarts keep the agent id
                env_path = Path(".env")
                lines = []
                if env_path.exists():
                    lines = [l for l in env_path.read_text(encoding="utf-8").splitlines() if not l.startswith("ELEVENLABS_AGENT_ID=")]
                lines.append(f"ELEVENLABS_AGENT_ID={aid}")
                env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except Exception as e:
            # surface a hint on /config/eleven
            app.state._agent_error = str(e)

    store = app.state.store
    mcp = app.state.mcp
    rag = app.state.rag

    # Static demo
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Voice agent (optional TTS)
    def make_voice_agent(voice_id: Optional[str] = None):
        # Test override: force dummy TTS for deterministic tests/demos without SDK
        if os.getenv("SUPAGENT_DUMMY_TTS") == "1":
            class _DummyTTS:
                def synth(self, text: str) -> bytes:
                    return b"ID3\x03\x00\x00\x00\x00\x00\x21" + (text[:8].encode() or b"aaaa")
            return VoiceAgent(rag, _DummyTTS())
        # Prefer fully-managed ElevenLabs Agent if configured
        try:
            agent_client = ElevenLabsAgentClient()
            return ElevenLabsVoiceAgent(rag, agent_client)
        except Exception:
            # Fallback to direct TTS if agent not configured
            try:
                tts = ElevenLabsTTS(voice_id=voice_id)
            except Exception:
                tts = None
            return VoiceAgent(rag, tts)

    @app.get("/demo")
    def demo_redirect():
        return RedirectResponse(url="/static/demo.html")

    @app.get("/config/eleven")
    def eleven_config() -> Dict[str, Any]:
        aid = os.getenv("ELEVENLABS_AGENT_ID")
        err = getattr(app.state, "_agent_error", None)
        mcp_server_id = os.getenv("ELEVENLABS_MCP_SERVER_ID") or getattr(app.state, "_mcp_server_id", None)
        mcp_error = getattr(app.state, "_mcp_server_error", None)
        # Auto-detect Railway public URL if available
        railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
        railway_url = f"https://{railway_public_domain}" if railway_public_domain else None
        base_url = railway_url or os.getenv("SUPAGENT_BASE_URL", "http://localhost:8000")
        return {
            "agent_id": aid,
            "has_key": bool(os.getenv("ELEVENLABS_API_KEY")),
            "status": "ok" if aid else "missing",
            "error": err,
            "mcp_server": {
                "id": mcp_server_id,
                "endpoint": f"{base_url}/mcp",
                "tool_endpoint": f"{base_url}/tools/search_knowledge_base",
                "error": mcp_error,
                "status": "configured" if mcp_server_id else "not_configured"
            }
        }
    
    @app.post("/config/eleven/configure_mcp")
    def configure_mcp_endpoint() -> Dict[str, Any]:
        """Manually trigger MCP server creation/registration with ElevenLabs."""
        if not os.getenv("ELEVENLABS_API_KEY"):
            return {"success": False, "error": "ELEVENLABS_API_KEY not set"}
        
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
        sid = session_id or "default"
        hist = [vars(t) for t in app.state.sessions.history(sid)]
        app.state.sessions.append(sid, "user", q.question)
        result = rag.answer(q.question, history=hist)
        app.state.sessions.append(sid, "assistant", result.get("answer", ""))
        return result

    @app.post("/voice")
    def voice(q: VoiceQuery) -> Dict[str, Any]:
        sid = q.session_id or "default"
        hist = [vars(t) for t in app.state.sessions.history(sid)]
        app.state.sessions.append(sid, "user", q.question)
        agent = make_voice_agent(voice_id=q.voice_id)
        result = agent.answer(q.question)
        app.state.sessions.append(sid, "assistant", result.get("answer", ""))
        return result

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
            return {"text": "", "warnings": ["ASR not configured. Install elevenlabs and set ELEVENLABS_API_KEY."]}
        try:
            text = engine.transcribe(data, mime)
            return {"text": text}
        except Exception as e:
            return {"text": "", "warnings": [str(e)]}

    @app.post("/voice_from_audio")
    async def voice_from_audio(file: UploadFile = File(...), fallback_text: Optional[str] = Form(None), session_id: Optional[str] = Form(None)) -> Dict[str, Any]:
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
                return {"answer": "", "audio_base64": None, "sources": [], "warnings": ["ASR not available and no fallback_text provided."]}
        sid = session_id or "default"
        app.state.sessions.append(sid, "user", text)
        agent = make_voice_agent()
        result = agent.answer(text)
        app.state.sessions.append(sid, "assistant", result.get("answer", ""))
        return result

    @app.post("/admin/reload_store")
    def reload_store(persist_dir: Optional[str] = None) -> Dict[str, Any]:
        # Swap the store to a new directory (dataset) and rebuild dependencies
        default_persist_dir = "/app/data/chroma" if os.getenv("RAILWAY_ENVIRONMENT") else "./data/chroma"
        app.state.store = VectorStore(
            persist_dir=persist_dir or os.getenv("CHROMA_PERSIST_DIR", default_persist_dir),
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        )
        app.state.mcp = MCPClient(app.state.store.similarity_search)
        app.state.rag = RAGAnswerer(app.state.mcp)
        final_persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", default_persist_dir)
        return {"ok": True, "persist_dir": final_persist_dir}

    @app.get("/admin/status")
    def status() -> Dict[str, Any]:
        default_persist_dir = "/app/data/chroma" if os.getenv("RAILWAY_ENVIRONMENT") else "./data/chroma"
        persist_dir = getattr(app.state.store, "_persist_dir", None) or os.getenv("CHROMA_PERSIST_DIR", default_persist_dir)
        return {
            "persist_dir": persist_dir,
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "local"),
            "vector_backend": getattr(app.state.store, "_backend", "unknown"),
            "has_data": os.path.exists(persist_dir) and len(os.listdir(persist_dir)) > 0 if os.path.exists(persist_dir) else False
        }

    # Test endpoints for vector store and MCP connectivity
    @app.get("/test/vector_store")
    def test_vector_store(query: str = "password reset", k: int = 3) -> Dict[str, Any]:
        """Test direct vector store connectivity and similarity search."""
        try:
            results = store.similarity_search(query, k=k)
            return {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": [
                    {
                        "content_preview": doc.get("page_content", "")[:200] + "..." if len(doc.get("page_content", "")) > 200 else doc.get("page_content", ""),
                        "metadata": doc.get("metadata", {}),
                        "content_length": len(doc.get("page_content", ""))
                    }
                    for doc in results
                ],
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
            return {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": [
                    {
                        "content_preview": doc.get("page_content", "")[:200] + "..." if len(doc.get("page_content", "")) > 200 else doc.get("page_content", ""),
                        "metadata": doc.get("metadata", {}),
                        "title": doc.get("metadata", {}).get("title") or doc.get("metadata", {}).get("source", "Unknown")
                    }
                    for doc in results
                ]
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

    @app.get("/tools/definitions")
    def get_tool_definitions() -> Dict[str, Any]:
        """Returns tool definitions for ElevenLabs Agent configuration."""
        # Auto-detect Railway public URL if available
        railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
        railway_url = f"https://{railway_public_domain}" if railway_public_domain else None
        base_url = railway_url or os.getenv("SUPAGENT_BASE_URL", "http://localhost:8000")
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
                }
            ]
        }

    return app


app = build_app()
