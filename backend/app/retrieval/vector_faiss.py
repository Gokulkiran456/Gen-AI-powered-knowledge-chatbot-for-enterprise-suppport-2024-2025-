import os
import faiss
import pickle
import numpy as np
from typing import List, Tuple

from sentence_transformers import SentenceTransformer
from ..config import settings

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

class FaissIndex:
    def __init__(self, index_dir: str, embed_provider: str, embed_model: str, openai_embed_model: str):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        self.index_path = os.path.join(index_dir, "index.faiss")
        self.meta_path = os.path.join(index_dir, "meta.pkl")
        self.embed_provider = embed_provider
        self.embed_model_name = embed_model
        self.openai_embed_model = openai_embed_model

        self._model = None
        self._openai = None
        self._index = None
        self._meta: list[tuple[str, str]] = []  # (text, source)

        self._load()

    # ---------- Embeddings ----------
    def _ensure_embedder(self):
        if self.embed_provider == "sentence-transformers":
            if self._model is None:
                self._model = SentenceTransformer(self.embed_model_name)
        elif self.embed_provider == "openai":
            if OpenAI is None:
                raise RuntimeError("openai package not installed")
            if self._openai is None:
                self._openai = OpenAI()
        else:
            raise ValueError(f"Unknown embed provider: {self.embed_provider}")

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        self._ensure_embedder()
        if self.embed_provider == "sentence-transformers":
            emb = self._model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
            return emb.astype("float32")
        else:  # openai
            resp = self._openai.embeddings.create(model=self.openai_embed_model, input=texts)
            arr = [d.embedding for d in resp.data]
            arr = np.array(arr, dtype="float32")
            # Normalize
            norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
            arr = arr / norms
            return arr

    # ---------- Index persistence ----------
    def _load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self._index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                self._meta = pickle.load(f)
        else:
            # lazy create on first add
            self._index = None
            self._meta = []

    def _save(self):
        if self._index is not None:
            faiss.write_index(self._index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self._meta, f)

    # ---------- Public API ----------
    def add(self, texts: List[str], sources: List[str]):
        vecs = self._embed_texts(texts)
        d = vecs.shape[1]
        if self._index is None:
            self._index = faiss.IndexFlatIP(d)
        self._index.add(vecs)
        self._meta.extend(list(zip(texts, sources)))
        self._save()

    def search(self, query: str, top_k: int) -> List[tuple[str, str, float]]:
        if self._index is None or len(self._meta) == 0:
            return []
        q = self._embed_texts([query])
        D, I = self._index.search(q, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1:
                continue
            text, src = self._meta[idx]
            results.append((text, src, float(score)))
        return results
