import base64
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import build_app
from agents.voice import VoiceAgent, TTSEngine


class _DummyTTS:
    def synth(self, text: str) -> bytes:
        # Return small fake mp3 header + data
        return b"ID3\x03\x00\x00\x00\x00\x00\x21" + (text[:8].encode() or b"aaaa")


def _inject_dummy_voice(app) -> None:
    # monkeypatch the factory inside the app state by adding a route-local override
    # We can wrap the handler to replace make_voice_agent via closure
    for route in list(app.router.routes):
        if getattr(route, "endpoint", None) and route.name in {"voice", "voice_stream", "voice_from_audio"}:
            pass


@pytest.fixture()
def client(monkeypatch) -> Any:
    # Force dummy TTS path in the app
    monkeypatch.setenv("SUPAGENT_DUMMY_TTS", "1")
    app = build_app()
    return TestClient(app)


def test_voice_returns_audio_base64(client: TestClient):
    resp = client.post("/voice", json={"question": "Hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    # With dummy TTS we should have audio
    assert data.get("audio_base64")
    # Ensure base64 decodes
    base64.b64decode(data["audio_base64"])  # no exception


def test_voice_stream_works(client: TestClient):
    resp = client.post("/voice_stream", json={"question": "Stream it"})
    assert resp.status_code == 200
    assert resp.headers.get("content-type", "").startswith("audio/mpeg")


def test_voice_from_audio_with_fallback(client: TestClient):
    # Send tiny webm-like bytes; backend ignores and uses fallback_text
    files = {"file": ("audio.webm", b"\x1aE\xdf\xa3webm", "audio/webm")}
    data = {"fallback_text": "fallback question"}
    resp = client.post("/voice_from_audio", files=files, data=data)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("audio_base64")
