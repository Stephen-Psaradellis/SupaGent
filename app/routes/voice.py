"""
Voice and audio processing routes.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse

from app.models import VoiceQuery
from app.dependencies import VoiceServiceDep, SessionsDep
from agents.asr import ElevenLabsASR

router = APIRouter(tags=["voice"])


def make_asr():
    """Create ASR engine instance."""
    try:
        return ElevenLabsASR()
    except Exception:
        return None


def make_voice_agent(request, voice_id: Optional[str] = None):
    """Create a voice agent instance."""
    return request.app.state.voice_service.get_voice_agent(voice_id=voice_id)


@router.post("/voice")
def voice(
    q: VoiceQuery,
    service: VoiceServiceDep,
    sessions: SessionsDep,
) -> Dict[str, Any]:
    """Process a voice query using the voice service."""
    return service.process_voice_query(
        question=q.question,
        session_id=q.session_id,
        voice_id=q.voice_id,
        sessions=sessions,
    )


@router.post("/voice_stream")
def voice_stream(
    q: VoiceQuery,
    request: Request,
    sessions: SessionsDep,
) -> StreamingResponse:
    """Stream voice response in real-time."""
    from core.utils import normalize_session_id
    
    sid = normalize_session_id(q.session_id)
    sessions.append(sid, "user", q.question)
    agent = make_voice_agent(request, voice_id=q.voice_id)
    stream_fn = getattr(agent, "stream_answer", None)
    if not callable(stream_fn):
        return {"detail": "Streaming not available."}
    gen = stream_fn(q.question)
    return StreamingResponse(gen, media_type="audio/mpeg")


@router.post("/asr")
async def asr(
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """Transcribe audio to text using ASR."""
    engine = make_asr()
    data = await file.read()
    mime = file.content_type
    if engine is None:
        return {
            "text": "",
            "warnings": ["ASR not configured. Install elevenlabs and set ELEVENLABS_API_KEY in Doppler."]
        }
    try:
        text = engine.transcribe(data, mime)
        return {"text": text}
    except Exception as e:
        return {"text": "", "warnings": [str(e)]}


@router.post("/voice_from_audio")
async def voice_from_audio(
    file: UploadFile = File(...),
    fallback_text: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    service: VoiceServiceDep = None,
    sessions: SessionsDep = None,
) -> Dict[str, Any]:
    """Process voice query from audio file."""
    engine = make_asr()
    data = await file.read()
    mime = file.content_type
    text: Optional[str] = None
    
    if engine is not None:
        try:
            text = engine.transcribe(data, mime)
        except Exception:
            text = None
    
    if not text:
        if fallback_text:
            text = fallback_text
        else:
            return {
                "answer": "",
                "audio_base64": None,
                "sources": [],
                "warnings": ["ASR not available and no fallback_text provided."]
            }
    
    return service.process_voice_query(
        question=text,
        session_id=session_id,
        sessions=sessions,
    )

