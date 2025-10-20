import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ENV: str = os.getenv("ENV", "dev")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # openai | ollama
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1")

    EMBEDDINGS_PROVIDER: str = os.getenv("EMBEDDINGS_PROVIDER", "sentence-transformers")
    EMBEDDINGS_MODEL: str = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    INDEX_DIR: str = os.getenv("INDEX_DIR", "./backend_index")
    TOP_K: int = int(os.getenv("TOP_K", 5))

    SLACK_SIGNING_SECRET: str | None = os.getenv("SLACK_SIGNING_SECRET")
    SLACK_BOT_TOKEN: str | None = os.getenv("SLACK_BOT_TOKEN")
    TEAMS_WEBHOOK_URL: str | None = os.getenv("TEAMS_WEBHOOK_URL")

settings = Settings()
