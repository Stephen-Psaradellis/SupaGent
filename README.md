# SupaGent Support Voice Agent

A demo-ready customer support agent with:
- RAG over your docs (via MCP -> vector store)
- ElevenLabs Agent for voice output (preferred), with TTS fallback
- Optional ASR endpoint for microphone input
- FastAPI server plus a simple web demo

## Quick start

1) Create venv and install:

```
pip install -r requirements.txt
# Optional: voice/ASR backend
pip install elevenlabs
```

2) Environment

Copy `.env.example` to `.env` and set:
- ELEVENLABS_API_KEY={{ELEVENLABS_API_KEY}}
- ELEVENLABS_AGENT_ID={{ELEVENLABS_AGENT_ID}} (preferred voice backend)
- Optional (fallback TTS): ELEVENLABS_VOICE_ID={{VOICE_ID}}
- Optional: CHROMA_PERSIST_DIR, EMBEDDING_MODEL

3) Ingest docs

```
python -m tools.ingest --dir dataset
```

4) Run API

```
uvicorn app.main:app --reload
```

Visit http://localhost:8000/demo for the web UI.

## Endpoints
- POST `/query`: { "question": "..." } -> { answer, sources }
- POST `/voice`: { "question": "...", "voice_id"?: "..." } -> { answer, sources, audio_base64 }
  - Uses ElevenLabs Agent if configured; otherwise TTS; otherwise text-only.
- POST `/asr`: multipart/form-data `file` (audio/webm, wav, etc.) -> { text }
  - Returns warnings if ASR not configured.
- POST `/voice_from_audio`: multipart/form-data `file` + optional `fallback_text` -> { answer, sources, audio_base64 }
  - If ASR unavailable, `fallback_text` is used.

## Architecture
- `agents/rag.py`: retrieval and answer synthesis (placeholder synthesis).
- `memory/vector_store.py`: Chroma+HF embeddings; persisted store.
- `agents/eleven_agent.py`: ElevenLabs Agent client and voice agent.
- `agents/voice.py`: generic voice agent with TTS fallback.
- `agents/asr.py`: optional ElevenLabs ASR wrapper.
- `app/main.py`: FastAPI app, endpoints, and demo static server.
- `tools/ingest.py`: dataset ingestion and chunking.

## Deployment

- Environment variables
  - ELEVENLABS_API_KEY, ELEVENLABS_AGENT_ID, optional ELEVENLABS_VOICE_ID
  - VECTOR_BACKEND: CHROMA (default) or FAISS
  - CHROMA_PERSIST_DIR: path for Chroma/FAISS persistence
  - EMBEDDING_MODEL: HF model name
  - SESSIONS_DIR: session transcripts directory
- Production run: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Health: `/admin/status` shows current vector store dir

## Notes
- The ElevenLabs SDK usage may differ by version; errors are surfaced with helpful runtime messages and the app degrades gracefully.
- Tests: `pytest -q` (do not require ElevenLabs SDK).

## Dataset scraping
- Use `python -m tools.scrape https://docs.gitlab.com --out dataset/company --limit 300`
- Review and fill `dataset/LICENSE.md` with the site and license details
- Ingest: `python -m tools.ingest --dir dataset/company`

## Evaluation
- Create `dataset/eval.jsonl` with lines like: `{ "question": "How do I reset my password?", "expected_substring": "password" }`
- Run: `python -m eval.evaluate --file dataset/eval.jsonl`
- Metrics include accuracy, retrieval_rate, and avg_latency_ms

# SupaGent: ElevenLabs Customer Support Voice Agent (RAG + MCP)

This project implements a demo-ready customer support voice agent. It runs on the ElevenLabs Agent platform (voice I/O), retrieves factual answers via a RAG pipeline, and persists memory in a vector store accessed through an MCP-style adapter.

See `WARP.md.md` and `project_spec.md` for requirements. This README focuses on setup and usage.

## Setup

1) Create and activate a virtual environment, then install deps:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

2) Configure environment:

```bash
cp .env.example .env
# Fill ELEVENLABS_API_KEY if/when integrating real voice
```

## Run API

```bash
uvicorn app.main:app --reload
```

- POST `/query` with JSON: `{ "question": "How do I reset my password?" }`
- Returns an answer with retrieved sources.

## Ingest data

```bash
python -m tools.ingest --dir dataset
```

- Uses recursive chunking (size 800, overlap 120) and persists to Chroma under `CHROMA_PERSIST_DIR`.

## Tests

```bash
pytest -q
```

## Notes

- The MCP client in `memory/mcp_client.py` is an adapter boundary. Tests use in-process vector retrieval to simulate MCP until a real MCP server is connected.
- Dataset ingestion is handled by `tools/ingest.py`. Place your chosen public dataset under `dataset/` and document it in `dataset/README.md`.
