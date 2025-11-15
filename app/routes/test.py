"""
Testing and diagnostic routes.
"""
from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter

from app.dependencies import StoreDep, MCPDep, RAGDep
from core.utils import format_documents_for_response

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/vector_store")
def test_vector_store(
    query: str = "password reset",
    k: int = 3,
    store: StoreDep = None,
) -> Dict[str, Any]:
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


@router.get("/mcp_client")
def test_mcp_client(
    query: str = "password reset",
    k: int = 3,
    mcp: MCPDep = None,
) -> Dict[str, Any]:
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


@router.get("/rag")
def test_rag(
    query: str = "How do I reset my password?",
    rag: RAGDep = None,
) -> Dict[str, Any]:
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


@router.post("/mcp_endpoint")
def test_mcp_endpoint(
    request_body: Dict[str, Any],
    mcp: MCPDep = None,
) -> Dict[str, Any]:
    """Test the MCP protocol endpoint directly."""
    try:
        # Simulate a tools/list call
        if request_body.get("method") == "tools/list" or not request_body.get("method"):
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


@router.get("/prompts")
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


@router.get("/full_chain")
def test_full_chain(
    query: str = "How do I reset my password?",
    store: StoreDep = None,
    mcp: MCPDep = None,
    rag: RAGDep = None,
) -> Dict[str, Any]:
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
    
    # Test 4: Tool Endpoint logic
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












