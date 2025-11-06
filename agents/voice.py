from __future__ import annotations

import base64
import os
from typing import Optional, Protocol, Dict, Any, List

from agents.rag import RAGAnswerer
from memory.mcp_client import MCPClient


class TTSEngine(Protocol):
    def synth(self, text: str) -> bytes:
        """Synthesize speech for the given text and return audio bytes (mp3)."""
        ...


class ElevenLabsTTS:
    """Thin wrapper around the ElevenLabs TTS API.

    This is optional. If the SDK isn't installed or the API key is missing,
    calling synth() will raise a clear RuntimeError.
    """

    CHUNK_BYTES = 32_768

    def __init__(self, voice_id: Optional[str] = None):
        self.voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID", "")
        self._init_sdk()

    def _init_sdk(self) -> None:
        try:
            from elevenlabs import set_api_key  # type: ignore
            from elevenlabs.client import ElevenLabs  # type: ignore
        except Exception as e:  # ImportError or other
            raise RuntimeError(
                "elevenlabs SDK not installed. Run `pip install elevenlabs` to enable TTS.") from e

        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY not set in environment.")

        set_api_key(api_key)
        self._client = ElevenLabs(api_key=api_key)

    def synth(self, text: str) -> bytes:
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
    """Voice agent that uses RAG for answers and a TTS engine for audio."""

    def __init__(self, rag: RAGAnswerer, tts: Optional[TTSEngine] = None):
        self._rag = rag
        self._tts = tts

    def answer(self, question: str) -> Dict[str, Any]:
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
        result = self._rag.answer(question)
        answer_text = result.get("answer", "")
        # Prepend a tiny silent mp3 frame? For simplicity, stream TTS/bytes if available
        if self._tts is None or not answer_text:
            # If no TTS, stream nothing (caller should handle 400)
            return iter(())
        # If TTS has a stream method use it; else chunk synth bytes
        stream_fn = getattr(self._tts, "stream", None)
        if callable(stream_fn):
            return stream_fn(answer_text)
        data = self._tts.synth(answer_text)
        def gen():
            for i in range(0, len(data), 32768):
                yield data[i:i+32768]
        return gen()
