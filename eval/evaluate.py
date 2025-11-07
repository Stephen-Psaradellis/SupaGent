import json
import sys
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
    from core.domain_config import get_domain_config
    
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=None, help="Path to eval.jsonl file (defaults to domain-specific eval file)")
    ap.add_argument("--k", type=int, default=4)
    args = ap.parse_args()

    print("Evaluating...")

    items: List[EvalItem] = []
    
    # Use domain-specific eval questions if file not specified
    if args.file is None:
        domain = get_domain_config()
        if domain.eval_questions:
            # Use domain-specific evaluation questions
            for q in domain.eval_questions:
                items.append(EvalItem(
                    question=q.get("question", ""),
                    expected_substring=q.get("expected_substring", ""),
                ))
        else:
            # Fallback to default eval file
            args.file = "dataset/eval.jsonl"
    
    # Load from file if specified or if domain doesn't have eval questions
    if args.file:
        p = Path(args.file)
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                obj = json.loads(line)
                items.append(EvalItem(**obj))
        elif not items:
            print(f"Warning: Eval file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    
    if not items:
        print("Error: No evaluation items found. Check domain config or eval file.", file=sys.stderr)
        sys.exit(1)
    
    res = run_eval(items, k=args.k)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
