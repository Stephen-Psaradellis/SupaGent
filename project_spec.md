# ElevenLabs Customer Support Voice Agent (RAG + MCP)

## Overview
This agent simulates a customer support representative. It runs on the **ElevenLabs Agent Platform**, uses real voice interaction, and retrieves accurate answers using a RAG pipeline.

## Primary Capabilities
- Voice input/output (via ElevenLabs voice interface)
- Memory and search via **MCP connected to ChromaDB**
- RAG-based query answering with source awareness
- Persistent vector storage
- Multi-turn memory and context tracking

## Stack
- ElevenLabs Agent Framework
- LangChain (retrieval and prompt handling)
- ChromaDB vector store (connected via MCP)
- FAISS acceptable fallback if Chroma fails
- Hugging Face or OpenAI embeddings
- FastAPI for control endpoints
- pytest for TDD

## Use Case Flow
1. User speaks a support query: “How do I reset my password?”
2. ElevenLabs Agent transcribes and routes query through MCP.
3. MCP pulls relevant context from the vector store.
4. LangChain formats the prompt and synthesizes the final answer.
5. Answer is returned via ElevenLabs TTS.
6. Agent maintains context for follow-ups: “Wait, what if I forgot my email?”

## Dataset Instructions
The agent must choose and load a **complete customer support dataset**. It should contain:
- At least 100 articles across categories
- Clear policy documentation, FAQs, and workflow references
- Markdown or HTML preferred
- Public license (MIT, CC-BY, etc.)

Examples may include GitLab Docs, Notion Help Center, Shopify Docs. The agent must document the source in `dataset/README.md`.

## Constraints
- Use test-driven development throughout
- All memory must route through MCP
- No hardcoded vectors or flat file lookups
- No UI unless routed through FastAPI
- Code must be modular, typed, and testable

## Success Criteria
- Agent answers 30+ support questions with 90% accuracy
- Responses are voiced and backed by retrieved docs
- RAG system uses true context chunks, not summarizations
- All test cases pass with no skipped tests