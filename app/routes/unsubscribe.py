from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, PlainTextResponse

# Reuse helpers from pipeline.unsubscribe_api to avoid duplication
from pipeline.unsubscribe_api import _verify_sig, _get_secret, _save_suppression


router = APIRouter()


@router.get("/unsub", response_class=HTMLResponse, tags=["unsubscribe"])
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


@router.post("/unsub", tags=["unsubscribe"])
async def unsub_post(request: Request) -> Response:
    e = request.query_params.get("e")
    sig = request.query_params.get("sig")
    if not e or not sig:
        raise HTTPException(status_code=400, detail="Missing parameters")
    if not _verify_sig(e, sig, _get_secret()):
        raise HTTPException(status_code=403, detail="Invalid signature")
    _save_suppression(e, source="one_click")
    return PlainTextResponse(content="", status_code=200)


