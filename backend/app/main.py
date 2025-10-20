from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import AskRequest, AskResponse, IngestRequest
from .rag import RAGPipeline
from .retrieval.ingest import iter_docs, chunk_text
from .retrieval.vector_faiss import FaissIndex
from .config import settings
from .integrations import slack as slack_routes
from .integrations import teams as teams_routes
import os

app = FastAPI(title="GenAI Knowledge Chatbot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGPipeline()

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}

@app.post("/api/ask", response_model=AskResponse)
def api_ask(payload: AskRequest):
    answer, sources = rag.ask(payload.question)
    return AskResponse(answer=answer, sources=list(dict.fromkeys(sources)))

@app.post("/api/ingest")
def api_ingest(payload: IngestRequest):
    docs_dir = payload.docs_dir or "./data/docs"
    index_dir = payload.index_dir or settings.INDEX_DIR
    os.makedirs(index_dir, exist_ok=True)
    store = FaissIndex(index_dir=index_dir,
                       embed_provider=settings.EMBEDDINGS_PROVIDER,
                       embed_model=settings.EMBEDDINGS_MODEL,
                       openai_embed_model=settings.OPENAI_EMBEDDING_MODEL)
    texts, sources = [], []
    for path, text in iter_docs(docs_dir):
        if not text.strip():
            continue
        chunks = chunk_text(text, max_tokens=450, overlap=80)
        texts.extend(chunks)
        sources.extend([os.path.basename(path)] * len(chunks))
    if not texts:
        return {"added": 0, "message": "No documents found"}
    store.add(texts, sources)
    return {"added": len(texts), "docs_dir": docs_dir, "index_dir": index_dir}

# Slack & Teams
app.include_router(slack_routes.router, prefix="/slack", tags=["slack"])
app.include_router(teams_routes.router, prefix="/teams", tags=["teams"])
