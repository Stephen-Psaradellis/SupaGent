from __future__ import annotations

import base64
import os
from typing import Any, Dict, List, Optional

from agents.rag import RAGAnswerer


class ElevenLabsAgentClient:
    """Optional ElevenLabs Agent client.

    Uses the ElevenLabs Agents API to generate speech responses. If the SDK
    or credentials aren't available, raises RuntimeError on use.
    
    This client provides access to fully-managed ElevenLabs Agents, which
    handle voice I/O, context management, and tool calling automatically.
    
    Attributes:
        CHUNK_BYTES: Default chunk size for streaming audio (32KB).
    """

    CHUNK_BYTES = 32_768

    def __init__(self, agent_id: Optional[str] = None):
        """Initialize ElevenLabs Agent client.
        
        Args:
            agent_id: Optional agent ID. If not provided, reads from
                ELEVENLABS_AGENT_ID environment variable.
                
        Raises:
            RuntimeError: If agent_id is not set or SDK is not installed.
        """
        self.agent_id = agent_id or os.getenv("ELEVENLABS_AGENT_ID")
        if not self.agent_id:
            raise RuntimeError("ELEVENLABS_AGENT_ID is not set.")
        self._init_sdk()

    def _init_sdk(self) -> None:
        """Initialize the ElevenLabs SDK client.
        
        Raises:
            RuntimeError: If SDK is not installed or API key is missing.
        """
        try:
            from elevenlabs.client import ElevenLabs  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "elevenlabs SDK not installed. Run `pip install elevenlabs` to enable Agents.") from e

        from core.secrets import get_elevenlabs_api_key
        
        api_key = get_elevenlabs_api_key()
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY not set in Doppler.")
        self._client = ElevenLabs(api_key=api_key)

    def speak_from_prompt(self, prompt: str) -> bytes:
        """Send prompt to Agent and return synthesized audio bytes (mp3).

        This uses a non-streaming convenience approach: collect chunks and return bytes.
        
        Args:
            prompt: Text prompt to send to the agent for speech synthesis.
            
        Returns:
            Complete MP3 audio bytes.
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
        """Stream audio from agent prompt in real-time.
        
        Args:
            prompt: Text prompt to send to the agent.
            
        Yields:
            Audio byte chunks as they become available.
            
        Raises:
            RuntimeError: If streaming API is not available in the SDK version.
        """
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
    attach sources, but uses the Agent for spoken output. This provides
    the best of both worlds: our RAG-based knowledge retrieval with
    ElevenLabs' high-quality voice synthesis.
    """

    def __init__(self, rag: RAGAnswerer, agent_client: ElevenLabsAgentClient):
        """Initialize the ElevenLabs voice agent.
        
        Args:
            rag: RAGAnswerer instance for generating grounded answers.
            agent_client: ElevenLabsAgentClient for speech synthesis.
        """
        self._rag = rag
        self._client = agent_client

    def answer(self, question: str) -> Dict[str, Any]:
        """Generate a voice answer using RAG + ElevenLabs Agent.
        
        Uses RAG to retrieve context and generate a text answer, then
        synthesizes it using the ElevenLabs Agent for high-quality voice output.
        
        Args:
            question: The user's question.
            
        Returns:
            Dictionary containing:
                - "answer": Text answer from RAG
                - "sources": Source document metadata
                - "audio_base64": Base64-encoded MP3 audio
                - "provider": "elevenlabs-agent"
        """
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
        """Stream audio answer in real-time using ElevenLabs Agent.
        
        Args:
            question: The user's question.
            
        Yields:
            Audio byte chunks in MP3 format.
        """
        result = self._rag.answer(question)
        answer_text = result.get("answer", "")
        if not answer_text:
            return iter(())
        return self._client._stream_from_prompt(answer_text)
