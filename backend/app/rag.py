from typing import List, Tuple
from .config import settings
from .retrieval.vector_faiss import FaissIndex
from .llm.base import LLM
from .llm.openai_llm import OpenAiLLM
from .llm.ollama_llm import OllamaLLM

class RAGPipeline:
    def __init__(self):
        self.index = FaissIndex(index_dir=settings.INDEX_DIR,
                                embed_provider=settings.EMBEDDINGS_PROVIDER,
                                embed_model=settings.EMBEDDINGS_MODEL,
                                openai_embed_model=settings.OPENAI_EMBEDDING_MODEL)
        if settings.LLM_PROVIDER == "openai":
            self.llm: LLM = OpenAiLLM(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)
        else:
            self.llm = OllamaLLM(model=settings.OLLAMA_MODEL)

    def retrieve(self, query: str, k: int | None = None) -> List[Tuple[str, str, float]]:
        return self.index.search(query, top_k=k or settings.TOP_K)

    def generate(self, question: str, contexts: List[str]) -> str:
        system = (
            "You are an enterprise knowledge assistant. "
            "Answer strictly using the provided context. If unknown, say you don't know. "
            "Cite filenames in square brackets like [source]."
        )
        context_block = "\n\n".join([f"[{i+1}] {c}" for i, c in enumerate(contexts)])
        prompt = f"Context:\n{context_block}\n\nQuestion: {question}\nAnswer:"
        return self.llm.generate(system=system, prompt=prompt)

    def ask(self, question: str) -> Tuple[str, List[str]]:
        hits = self.retrieve(question)
        contexts = [h[0] for h in hits]
        sources = [h[1] for h in hits]
        answer = self.generate(question, contexts)
        return answer, sources
