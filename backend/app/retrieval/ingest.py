import os
import re
import glob
from typing import Iterable, List, Tuple

from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document
import markdown as md

def read_file_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in [".txt", ".md"]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        if ext == ".md":
            # keep as text (strip HTML)
            text = re.sub("<[^<]+?>", "", md.markdown(text))
        return text
    if ext == ".pdf":
        return pdf_extract_text(path) or ""
    if ext in [".docx"]:
        try:
            doc = Document(path)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            return ""
    return ""

def chunk_text(text: str, max_tokens: int = 450, overlap: int = 80) -> List[str]:
    # Rough tokenization by words; for production switch to tiktoken length
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        if end == len(words): break
        start = end - overlap
        if start < 0: start = 0
    return chunks

def iter_docs(docs_dir: str) -> Iterable[Tuple[str, str]]:
    patterns = ["**/*.txt", "**/*.md", "**/*.pdf", "**/*.docx"]
    for pat in patterns:
        for path in glob.glob(os.path.join(docs_dir, pat), recursive=True):
            yield path, read_file_text(path)
