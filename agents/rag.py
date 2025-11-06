from typing import List, Dict, Any, Optional
from langchain.prompts import PromptTemplate

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
    lines = []
    for d in docs:
        meta = d.get("metadata", {})
        title = meta.get("title") or meta.get("source") or "doc"
        lines.append(f"- ({title}) {d['page_content'][:500]}")
    return "\n".join(lines)


def _inline_citations(question: str, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
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
    def __init__(self, mcp: MCPClient, prompt_template: str = DEFAULT_TEMPLATE, synthesizer: Optional[callable] = None):
        self.mcp = mcp
        self.prompt = PromptTemplate.from_template(prompt_template)
        self._synth = synthesizer or self._simple_synthesis

    def answer(self, question: str, k: int = 4, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        # Optionally expand the query using recent user messages
        q_aug = question
        if history:
            recent_user = [t["text"] for t in history if t.get("role") == "user"][-2:]
            if recent_user:
                q_aug = question + " \n\nRelated: " + " | ".join(recent_user)
        retrieved = self.mcp.retrieve(q_aug, k=k)
        # Compose a deterministic, concise answer with inline citations
        extract = _inline_citations(question, retrieved)
        context = format_context(retrieved)
        # Keep the "Answer:" prefix for tests and readability; include question for clarity
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
        # Legacy fallback (unused in current answer()) kept for compatibility
        lines = [l for l in prompt_text.splitlines() if l.strip()]
        return "\n".join(lines[-6:])
