from typing import Optional
from .base import LLM
from ..config import settings

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

class OpenAiLLM(LLM):
    def __init__(self, model: str, api_key: Optional[str] = None):
        if OpenAI is None:
            raise RuntimeError("openai package not installed")
        if not api_key and not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI provider")
        self.client = OpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self.model = model

    def generate(self, system: str, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content.strip()
