import requests
from fastapi import APIRouter
from ..config import settings
from ..rag import RAGPipeline

router = APIRouter()
rag = RAGPipeline()

@router.post("/send")
def send_to_teams(message: str):
    if not settings.TEAMS_WEBHOOK_URL:
        return {"error": "TEAMS_WEBHOOK_URL not configured"}
    payload = {"text": message}
    r = requests.post(settings.TEAMS_WEBHOOK_URL, json=payload, timeout=30)
    return {"status": r.status_code}

@router.post("/ask")
def ask_to_teams(question: str):
    answer, sources = rag.ask(question)
    msg = answer + (f"\n\nSources: {set(sources)}" if sources else "")
    if settings.TEAMS_WEBHOOK_URL:
        requests.post(settings.TEAMS_WEBHOOK_URL, json={"text": msg}, timeout=30)
    return {"answer": answer, "sources": list(set(sources))}
