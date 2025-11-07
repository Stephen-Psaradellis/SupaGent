from typing import List, Dict, Any, Optional

try:
    from langchain_core.prompts import PromptTemplate
except ImportError:
    try:
        from langchain.prompts import PromptTemplate
    except ImportError:
        # Fallback: create a simple template class if langchain not available
        class PromptTemplate:
            @staticmethod
            def from_template(template: str):
                class _Template:
                    def format(self, **kwargs):
                        return template.format(**kwargs)
                return _Template()

from memory.mcp_client import MCPClient


DEFAULT_TEMPLATE = """
You are a tier-1 customer support assistant.
Use the provided context to answer the user question concisely.
Always cite sources by title if available.

Question: {question}

Context:
{context}

Answer:
"""


def format_context(docs: List[Dict[str, Any]]) -> str:
    """Format retrieved documents into a context string.
    
    Converts a list of document dictionaries into a formatted string
    suitable for inclusion in a prompt. Each document is prefixed with
    its title/source and truncated to 500 characters.
    
    Args:
        docs: List of document dictionaries with "page_content" and "metadata" keys.
        
    Returns:
        Formatted context string with one document per line.
    """
    lines = []
    for d in docs:
        meta = d.get("metadata", {})
        title = meta.get("title") or meta.get("source") or "doc"
        lines.append(f"- ({title}) {d['page_content'][:500]}")
    return "\n".join(lines)


def _inline_citations(question: str, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate an answer with inline citations from retrieved documents.
    
    Uses a simple extractive approach: selects up to 3 sentences from the
    retrieved documents that match keywords from the question. Attaches
    citation markers [1], [2], etc. based on document titles.
    
    Args:
        question: The user's question.
        docs: List of retrieved document dictionaries.
        
    Returns:
        Dictionary with:
            - "text": Answer text with inline citation markers
            - "citations": List of citation metadata with index and title
    """
    # Simple extractive approach: pick up to 3 sentences that match keywords
    q_terms = {t.lower() for t in question.split() if len(t) > 3}
    selected: List[str] = []
    for d in docs:
        text = d.get("page_content", "")
        for sent in text.split('.'):
            s = sent.strip()
            if not s:
                continue
            score = sum(1 for t in q_terms if t in s.lower())
            if score >= 1:
                selected.append(s)
            if len(selected) >= 3:
                break
        if len(selected) >= 3:
            break
    if not selected and docs:
        # fallback to first snippet
        selected.append(docs[0].get("page_content", "").split('\n')[0][:200])

    # Build citation indices based on distinct titles in order
    titles: List[str] = []
    for d in docs:
        meta = d.get("metadata", {})
        title = meta.get("title") or meta.get("source") or "doc"
        if title not in titles:
            titles.append(title)
    citation_map = {title: i + 1 for i, title in enumerate(titles)}

    # Attach inline [n] markers greedily based on the doc each sentence came from (approximate)
    parts: List[str] = []
    for d in docs:
        meta = d.get("metadata", {})
        title = meta.get("title") or meta.get("source") or "doc"
        for s in list(selected):
            if s in d.get("page_content", ""):
                parts.append(f"{s} [{citation_map.get(title, 1)}].")
                selected.remove(s)
    # Any remaining sentences get appended without marker
    parts.extend([f"{s}." for s in selected])

    answer_body = " ".join(parts).strip()

    citations = [{"index": i + 1, "title": t} for i, t in enumerate(titles)]
    return {"text": answer_body, "citations": citations}


class RAGAnswerer:
    """Retrieval-Augmented Generation answerer for customer support queries.
    
    Uses MCP client to retrieve relevant documents from the knowledge base,
    then synthesizes answers with inline citations. Supports conversation
    history for context-aware responses.
    """
    
    def __init__(self, mcp: MCPClient, prompt_template: str = DEFAULT_TEMPLATE, synthesizer: Optional[callable] = None):
        """Initialize the RAG answerer.
        
        Args:
            mcp: MCPClient instance for retrieving documents from vector store.
            prompt_template: Optional prompt template string. Uses DEFAULT_TEMPLATE if not provided.
            synthesizer: Optional custom synthesis function. Uses simple extractive
                approach by default.
        """
        self.mcp = mcp
        self.prompt = PromptTemplate.from_template(prompt_template)
        self._synth = synthesizer or self._simple_synthesis

    def answer(self, question: str, k: int = 4, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Generate an answer to a question using RAG.
        
        Retrieves relevant documents, augments the query with conversation
        history if provided, and generates an answer with inline citations.
        
        Args:
            question: The user's question.
            k: Number of documents to retrieve (default: 4).
            history: Optional conversation history in format
                [{"role": "user"|"assistant", "text": str}].
                
        Returns:
            Dictionary containing:
                - "answer": Formatted answer text with citations
                - "sources": List of source document metadata
        """
        # Augment query with recent conversation history for better context
        q_aug = question
        if history:
            # Extract last 2 user messages for context
            recent_user = [t["text"] for t in history if t.get("role") == "user"][-2:]
            if recent_user:
                q_aug = question + " \n\nRelated: " + " | ".join(recent_user)
        
        # Retrieve relevant documents from knowledge base via MCP
        retrieved = self.mcp.retrieve(q_aug, k=k)
        
        # Generate answer with inline citations using extractive approach
        extract = _inline_citations(question, retrieved)
        context = format_context(retrieved)
        
        # Format final answer with question, answer text, and citation list
        # This format is used for tests and readability
        synthesized = (
            f"Question: {question}\n\n"
            f"Answer:\n{extract['text']}\n\nCitations:\n"
            + "\n".join([f"[{c['index']}] {c['title']}" for c in extract["citations"]])
        )
        return {
            "answer": synthesized,
            "sources": [d.get("metadata", {}) for d in retrieved],
        }

    @staticmethod
    def _simple_synthesis(prompt_text: str) -> str:
        """Simple synthesis fallback (legacy, currently unused).
        
        Legacy method kept for compatibility. The current answer() method
        uses _inline_citations instead.
        
        Args:
            prompt_text: Prompt text to synthesize.
            
        Returns:
            Last 6 non-empty lines of the prompt.
        """
        # Legacy fallback (unused in current answer()) kept for compatibility
        lines = [l for l in prompt_text.splitlines() if l.strip()]
        return "\n".join(lines[-6:])
