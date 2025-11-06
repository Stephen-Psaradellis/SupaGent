import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

from agents.rag import RAGAnswerer
from memory.mcp_client import MCPClient
from memory.vector_store import VectorStore


@dataclass
class EvalItem:
    question: str
    expected_substring: str


def run_eval(items: List[EvalItem], k: int = 4) -> Dict[str, Any]:
    store = VectorStore()
    mcp = MCPClient(store.similarity_search)
    rag = RAGAnswerer(mcp)

    results = []
    t0 = time.time()
    hits = 0
    retrieved_hits = 0
    for it in items:
        t_start = time.time()
        docs = store.similarity_search(it.question, k=k)
        answer = rag.answer(it.question)
        dur = time.time() - t_start
        ok = it.expected_substring.lower() in (answer["answer"].lower())
        src_ok = any(it.expected_substring.lower() in (d.get("page_content", "").lower()) for d in docs)
        hits += 1 if ok else 0
        retrieved_hits += 1 if src_ok else 0
        results.append({
            "question": it.question,
            "ok": ok,
            "latency_ms": int(dur * 1000),
            "retrieval_hit": src_ok,
        })
    total = len(items)
    return {
        "total": total,
        "accuracy": hits / total if total else 0.0,
        "retrieval_rate": retrieved_hits / total if total else 0.0,
        "avg_latency_ms": int((time.time() - t0) * 1000 / max(total, 1)),
        "results": results,
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="dataset/eval.jsonl")
    ap.add_argument("--k", type=int, default=4)
    args = ap.parse_args()

    items: List[EvalItem] = []
    p = Path(args.file)
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            items.append(EvalItem(**obj))
    res = run_eval(items, k=args.k)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
