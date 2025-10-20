import requests
from .base import LLM

class OllamaLLM(LLM):
    """Minimal Ollama client (http://localhost:11434 by default)."""

    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate(self, system: str, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.2},
        }
        try:
            r = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data.get("message", {}).get("content", "").strip() or data.get("response", "").strip()
        except Exception as e:
            return f"(Ollama error: {e})"
