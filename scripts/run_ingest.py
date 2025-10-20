import argparse, os
from backend.app.retrieval.ingest import iter_docs, chunk_text
from backend.app.retrieval.vector_faiss import FaissIndex
from backend.app.config import settings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs_dir", default="./data/docs")
    parser.add_argument("--index_dir", default=settings.INDEX_DIR)
    args = parser.parse_args()

    os.makedirs(args.index_dir, exist_ok=True)
    store = FaissIndex(index_dir=args.index_dir,
                       embed_provider=settings.EMBEDDINGS_PROVIDER,
                       embed_model=settings.EMBEDDINGS_MODEL,
                       openai_embed_model=settings.OPENAI_EMBEDDING_MODEL)
    texts, sources = [], []
    for path, text in iter_docs(args.docs_dir):
        if not text.strip():
            continue
        chunks = chunk_text(text, max_tokens=450, overlap=80)
        texts.extend(chunks)
        sources.extend([os.path.basename(path)] * len(chunks))
    if not texts:
        print("No documents found.")
        return
    store.add(texts, sources)
    print(f"Added {len(texts)} chunks to index at {args.index_dir}")

if __name__ == "__main__":
    main()
