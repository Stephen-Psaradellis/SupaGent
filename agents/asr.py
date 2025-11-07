from __future__ import annotations

from typing import Protocol
import os


class STTEngine(Protocol):
    """Protocol for Speech-to-Text engines.
    
    Defines the interface that ASR implementations must follow.
    """
    
    def transcribe(self, audio_bytes: bytes, mime_type: str | None = None) -> str:
        """Transcribe audio bytes to text.
        
        Args:
            audio_bytes: Raw audio data to transcribe.
            mime_type: Optional MIME type of the audio (e.g., "audio/webm").
            
        Returns:
            Transcribed text string.
        """
        ...


class ElevenLabsASR:
    """Optional ElevenLabs ASR wrapper.

    If the SDK or credentials are missing, construction or use will raise
    RuntimeError with a helpful message.
    
    Provides speech-to-text transcription using ElevenLabs' multilingual
    ASR model (eleven_multilingual_v2).
    """

    def __init__(self):
        """Initialize ElevenLabs ASR client.
        
        Raises:
            RuntimeError: If SDK is not installed or API key is missing.
        """
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
                "elevenlabs SDK not installed. Run `pip install elevenlabs` to enable ASR.") from e

        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY not set in environment.")
        self._client = ElevenLabs(api_key=api_key)

    def transcribe(self, audio_bytes: bytes, mime_type: str | None = None) -> str:
        """Transcribe audio bytes to text using ElevenLabs ASR.
        
        Supports multiple audio formats (webm, wav, mp3, etc.) and handles
        different SDK versions by trying multiple API signatures.
        
        Args:
            audio_bytes: Raw audio data to transcribe.
            mime_type: Optional MIME type (e.g., "audio/webm"). Defaults to
                "audio/webm" if not provided.
                
        Returns:
            Transcribed text string.
            
        Raises:
            RuntimeError: If ASR is not supported by the SDK version or
                transcription returns no text.
        """
        # Use SDK speech-to-text; handle versions by trying common signatures
        try:
            # v1-style
            result = self._client.speech_to_text.convert(
                file=audio_bytes,
                model_id="eleven_multilingual_v2",
                content_type=mime_type or "audio/webm",
            )
        except AttributeError:
            # alt naming
            try:
                result = self._client.speech_to_text.transcribe(
                    file=audio_bytes,
                    model_id="eleven_multilingual_v2",
                    content_type=mime_type or "audio/webm",
                )
            except Exception as e:
                raise RuntimeError("ElevenLabs ASR not supported by installed SDK.") from e

        # Normalize result
        if isinstance(result, dict):
            text = result.get("text") or result.get("transcript")
        else:
            text = getattr(result, "text", None) or getattr(result, "transcript", None)
        if not text:
            raise RuntimeError("ASR returned no text.")
        return text
