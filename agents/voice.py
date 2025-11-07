from __future__ import annotations

import base64
import os
from typing import Optional, Protocol, Dict, Any, List

from agents.rag import RAGAnswerer
from memory.mcp_client import MCPClient


class TTSEngine(Protocol):
    """Protocol for Text-to-Speech engines.
    
    Defines the interface that TTS implementations must follow.
    """
    
    def synth(self, text: str) -> bytes:
        """Synthesize speech for the given text and return audio bytes (mp3).
        
        Args:
            text: Text to synthesize into speech.
            
        Returns:
            Audio bytes in MP3 format.
        """
        ...


class ElevenLabsTTS:
    """Thin wrapper around the ElevenLabs TTS API.

    This is optional. If the SDK isn't installed or the API key is missing,
    calling synth() will raise a clear RuntimeError.
    
    Attributes:
        CHUNK_BYTES: Default chunk size for streaming audio (32KB).
    """

    CHUNK_BYTES = 32_768

    def __init__(self, voice_id: Optional[str] = None):
        """Initialize ElevenLabs TTS client.
        
        Args:
            voice_id: Optional voice ID. If not provided, uses ELEVENLABS_VOICE_ID
                environment variable or default voice.
                
        Raises:
            RuntimeError: If elevenlabs SDK is not installed or API key is missing.
        """
        self.voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID", "")
        self._init_sdk()

    def _init_sdk(self) -> None:
        """Initialize the ElevenLabs SDK client.
        
        Raises:
            RuntimeError: If SDK is not installed or API key is missing.
        """
        try:
            from elevenlabs import set_api_key  # type: ignore
            from elevenlabs.client import ElevenLabs  # type: ignore
        except Exception as e:  # ImportError or other
            raise RuntimeError(
                "elevenlabs SDK not installed. Run `pip install elevenlabs` to enable TTS.") from e

        from core.secrets import get_elevenlabs_api_key
        
        api_key = get_elevenlabs_api_key()
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY not set in Doppler.")

        set_api_key(api_key)
        self._client = ElevenLabs(api_key=api_key)

    def synth(self, text: str) -> bytes:
        """Synthesize speech from text and return complete audio bytes.
        
        Args:
            text: Text to convert to speech.
            
        Returns:
            Complete MP3 audio bytes.
        """
        voice_id = self.voice_id or ""  # allow default
        # Use the TTS endpoint to synthesize MP3 bytes
        audio = self._client.text_to_speech.convert(
            voice_id=voice_id or "",  # empty -> default voice
            optimize_streaming_latency=0,
            output_format="mp3_44100_128",
            text=text,
        )
        # The SDK stream-like object yields byte chunks
        chunks: List[bytes] = []
        for b in audio:
            chunks.append(b)
        return b"".join(chunks)

    def stream(self, text: str):
        """Stream synthesized audio in chunks.
        
        Yields audio chunks as they become available, enabling real-time
        playback without waiting for complete synthesis.
        
        Args:
            text: Text to convert to speech.
            
        Yields:
            Audio byte chunks in MP3 format.
        """
        # Prefer a streamed SDK method if available; fall back to chunking synthesized bytes
        try:
            audio = self._client.text_to_speech.convert(
                voice_id=self.voice_id or "",
                optimize_streaming_latency=0,
                output_format="mp3_44100_128",
                text=text,
            )
            for b in audio:
                if b:
                    yield b
            return
        except Exception:
            pass
        data = self.synth(text)
        for i in range(0, len(data), self.CHUNK_BYTES):
            yield data[i:i+self.CHUNK_BYTES]


class VoiceAgent:
    """Voice agent that uses RAG for answers and a TTS engine for audio.
    
    Combines RAG-based answer generation with text-to-speech synthesis
    to provide voice-enabled customer support responses.
    """

    def __init__(self, rag: RAGAnswerer, tts: Optional[TTSEngine] = None):
        """Initialize the voice agent.
        
        Args:
            rag: RAGAnswerer instance for generating text answers.
            tts: Optional TTS engine for audio synthesis. If None, returns
                text-only responses without audio.
        """
        self._rag = rag
        self._tts = tts

    def answer(self, question: str) -> Dict[str, Any]:
        """Generate a voice answer to a question.
        
        Uses RAG to generate a text answer, then synthesizes it to audio
        if TTS is available. Returns both text and base64-encoded audio.
        
        Args:
            question: The user's question.
            
        Returns:
            Dictionary containing:
                - "answer": Text answer from RAG
                - "sources": Source document metadata
                - "audio_base64": Base64-encoded MP3 audio (if TTS available)
                - "warnings": List of warnings (e.g., if TTS failed)
        """
        result = self._rag.answer(question)
        answer_text = result.get("answer", "")
        audio_b64: Optional[str] = None
        if self._tts is not None and answer_text:
            try:
                audio_bytes = self._tts.synth(answer_text)
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
            except Exception as e:
                # Fail soft: return text and sources even if TTS fails
                result.setdefault("warnings", []).append(str(e))
        result["audio_base64"] = audio_b64
        return result

    def stream_answer(self, question: str):
        """Stream audio answer in real-time.
        
        Generates answer using RAG and streams audio chunks as they become
        available, enabling low-latency voice responses.
        
        Args:
            question: The user's question.
            
        Yields:
            Audio byte chunks in MP3 format.
            
        Returns:
            Empty iterator if TTS is not available or answer is empty.
        """
        result = self._rag.answer(question)
        answer_text = result.get("answer", "")
        
        # Return empty iterator if TTS unavailable or no answer text
        if self._tts is None or not answer_text:
            return iter(())
        
        # Use TTS stream method if available, otherwise chunk synthesized bytes
        stream_fn = getattr(self._tts, "stream", None)
        if callable(stream_fn):
            return stream_fn(answer_text)
        data = self._tts.synth(answer_text)
        def gen():
            for i in range(0, len(data), 32768):
                yield data[i:i+32768]
        return gen()
