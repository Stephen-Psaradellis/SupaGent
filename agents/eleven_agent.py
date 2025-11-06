from __future__ import annotations

import base64
import os
from typing import Any, Dict, List, Optional

from agents.rag import RAGAnswerer


class ElevenLabsAgentClient:
    """Optional ElevenLabs Agent client.

    Uses the ElevenLabs Agents API to generate speech responses. If the SDK
    or credentials aren't available, raises RuntimeError on use.
    """

    CHUNK_BYTES = 32_768

    def __init__(self, agent_id: Optional[str] = None):
        self.agent_id = agent_id or os.getenv("ELEVENLABS_AGENT_ID")
        if not self.agent_id:
            raise RuntimeError("ELEVENLABS_AGENT_ID is not set.")
        self._init_sdk()

    def _init_sdk(self) -> None:
        try:
            from elevenlabs.client import ElevenLabs  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "elevenlabs SDK not installed. Run `pip install elevenlabs` to enable Agents.") from e

        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY not set in environment.")
        self._client = ElevenLabs(api_key=api_key)

    def speak_from_prompt(self, prompt: str) -> bytes:
        """Send prompt to Agent and return synthesized audio bytes (mp3).

        This uses a non-streaming convenience approach: collect chunks and return bytes.
        """
        try:
            stream = self._stream_from_prompt(prompt)
            chunks: List[bytes] = []
            for b in stream:
                chunks.append(b)
            return b"".join(chunks)
        except AttributeError:
            # Fallback error path will be raised by _stream_from_prompt
            raise

    def _stream_from_prompt(self, prompt: str):
        # Try a streaming method on the Agents API
        try:
            stream = self._client.agents.speak(
                agent_id=self.agent_id,
                text=prompt,
                voice_settings=None,
                output_format="mp3_44100_128",
            )
            for b in stream:
                if b:
                    yield b
            return
        except AttributeError as e:
            # Fallback: if no streaming is exposed, attempt a single-shot API if available
            # Otherwise, raise a helpful error and let caller handle fallback.
            raise RuntimeError("Installed elevenlabs SDK lacks streaming Agents API.") from e


class ElevenLabsVoiceAgent:
    """Voice agent that delegates speech generation to an ElevenLabs Agent.

    It still uses our RAG pipeline to ensure retrieval through MCP and to
    attach sources, but uses the Agent for spoken output.
    """

    def __init__(self, rag: RAGAnswerer, agent_client: ElevenLabsAgentClient):
        self._rag = rag
        self._client = agent_client

    def answer(self, question: str) -> Dict[str, Any]:
        # Use RAG to ground the response and produce sources
        result = self._rag.answer(question)
        answer_text = result.get("answer", "")
        audio_b64: Optional[str] = None
        if answer_text:
            audio_bytes = self._client.speak_from_prompt(answer_text)
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        result["audio_base64"] = audio_b64
        result["provider"] = "elevenlabs-agent"
        return result

    def stream_answer(self, question: str):
        result = self._rag.answer(question)
        answer_text = result.get("answer", "")
        if not answer_text:
            return iter(())
        return self._client._stream_from_prompt(answer_text)
