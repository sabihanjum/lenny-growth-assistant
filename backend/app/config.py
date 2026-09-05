"""Application configuration settings."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App Settings
    PROJECT_NAME: str = "The Lenny Growth Assistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api"

    # Database
    # Default points to local Postgres (or pgvector Docker container)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password123@localhost:5432/lenny_assistant",
        description="Async database connection string"
    )

    # LLM Providers
    DEFAULT_LLM_PROVIDER: str = Field(default="ollama", description="Default LLM: 'ollama', 'claude', or 'openai'")
    DEFAULT_OLLAMA_MODEL: str = Field(default="llama3.1:8b", description="Default Ollama model")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Ollama API base URL")

    # Cloud LLM API Keys (optional, can be passed via env or request)
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic Claude API Key")
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key")

    # RAG Settings
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIMENSION: int = 384
    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.55  # Strict threshold for groundedness

    # Paths
    TRANSCRIPTS_DIR: Path = BASE_DIR / "data" / "transcripts"
    CACHE_DIR: Path = BASE_DIR / "data" / "cache"



settings = Settings()
