import hmac, hashlib, time, os, json, requests
from fastapi import APIRouter, Header, HTTPException, Request
from ..config import settings
from ..rag import RAGPipeline

router = APIRouter()
rag = RAGPipeline()

def verify_slack_signature(request_body: bytes, timestamp: str, signature: str) -> bool:
    if not settings.SLACK_SIGNING_SECRET:
        return False
    sig_basestring = f"v0:{timestamp}:{request_body.decode()}".encode()
    my_sig = 'v0=' + hmac.new(settings.SLACK_SIGNING_SECRET.encode(), sig_basestring, hashlib.sha256).hexdigest()
    return hmac.compare_digest(my_sig, signature)

@router.post("/events")
async def slack_events(request: Request, x_slack_signature: str = Header(None), x_slack_request_timestamp: str = Header(None)):
    body = await request.body()
    # Basic replay protection
    if x_slack_request_timestamp and abs(time.time() - int(x_slack_request_timestamp)) > 60 * 5:
        raise HTTPException(status_code=400, detail="Stale request")
    # Verify signature (if provided)
    if x_slack_signature and not verify_slack_signature(body, x_slack_request_timestamp or "", x_slack_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}

    text = payload.get("event", {}).get("text") or payload.get("text") or ""
    if not text.strip():
        return {"ok": True}
    answer, sources = rag.ask(text)
    return {"text": answer + (f"\n\nSources: {set(sources)}" if sources else "")}
