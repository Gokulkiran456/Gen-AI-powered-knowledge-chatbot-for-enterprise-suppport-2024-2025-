from pydantic import BaseModel

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: list[str] = []

class IngestRequest(BaseModel):
    docs_dir: str | None = None
    index_dir: str | None = None
