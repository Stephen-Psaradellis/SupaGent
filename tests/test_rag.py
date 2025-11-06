from memory.mcp_client import MCPClient
from agents.rag import RAGAnswerer


def test_rag_returns_sources_and_answer():
    # Fake retrieval results (what MCP would return)
    docs = [
        {"page_content": "Reset your password via Settings > Security.", "metadata": {"title": "Password Reset"}},
        {"page_content": "If you forgot your email, contact support.", "metadata": {"title": "Account Recovery"}},
    ]

    def fake_retrieve(q: str, k: int = 4):
        return docs[:k]

    rag = RAGAnswerer(MCPClient(fake_retrieve))
    result = rag.answer("How do I reset my password?")

    assert "Answer:" in result["answer"]
    assert len(result["sources"]) >= 1
    titles = {s.get("title") for s in result["sources"]}
    assert "Password Reset" in titles
