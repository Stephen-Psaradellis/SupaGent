"""
FastAPI Unsubscribe Endpoint for One‑Click and Link-based unsubscribes.

Features:
- GET /unsub?e=<email>&sig=<signature> for link clicks
- POST /unsub?e=<email>&sig=<signature> for Gmail/Yahoo one‑click
- HMAC signature verification using UNSUB_SIGNING_SECRET
- Appends records to pipeline/emails/suppressions.jsonl

Run:
  uvicorn pipeline.unsubscribe_api:app --host 0.0.0.0 --port 8080
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse


app = FastAPI(title="Unsubscribe API", version="1.0.0")


def _verify_sig(email: str, sig: str, secret: str) -> bool:
    digest = hmac.new(secret.encode("utf-8"), email.encode("utf-8"), hashlib.sha256).digest()
    expected = base64.urlsafe_b64encode(digest).decode().rstrip("=")
    return hmac.compare_digest(expected, sig or "")


def _save_suppression(email: str, source: str) -> None:
    suppress_dir = Path("pipeline/emails")
    suppress_dir.mkdir(parents=True, exist_ok=True)
    suppress_file = suppress_dir / "suppressions.jsonl"
    record = {
        "email": email,
        "reason": "user_unsubscribed",
        "source": source,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    with open(suppress_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def _get_secret() -> str:
    secret = os.getenv("UNSUB_SIGNING_SECRET")
    if not secret:
        # Intentionally raise: this must be configured to prevent abuse
        raise RuntimeError("UNSUB_SIGNING_SECRET not set")
    return secret


@app.get("/unsub", response_class=HTMLResponse)
async def unsub_get(e: Optional[str] = None, sig: Optional[str] = None) -> HTMLResponse:
    if not e or not sig:
        raise HTTPException(status_code=400, detail="Missing parameters")
    if not _verify_sig(e, sig, _get_secret()):
        raise HTTPException(status_code=403, detail="Invalid signature")
    _save_suppression(e, source="link")
    return HTMLResponse(
        content="""
<!doctype html>
<html><head><meta charset="utf-8"><title>Unsubscribed</title></head>
<body style="font-family:Arial,Helvetica,sans-serif;">
  <h2>You’re unsubscribed</h2>
  <p>You won’t receive further emails from us at this address.</p>
</body></html>
""",
        status_code=200,
    )


@app.post("/unsub")
async def unsub_post(request: Request) -> Response:
    # Gmail One‑Click will POST to the same URL; keep params in query
    e = request.query_params.get("e")
    sig = request.query_params.get("sig")
    if not e or not sig:
        raise HTTPException(status_code=400, detail="Missing parameters")
    if not _verify_sig(e, sig, _get_secret()):
        raise HTTPException(status_code=403, detail="Invalid signature")
    _save_suppression(e, source="one_click")
    # Must return 200 quickly with empty body
    return PlainTextResponse(content="", status_code=200)


