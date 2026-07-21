from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SIOU Document AI"
    app_env: str = "local"
    api_prefix: str = "/api"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    database_url: str | None = None

    documents_dir: Path = Path("documents")
    document_include_patterns: str = "*.pdf,*.docx"
    vector_store_dir: Path = Path("vector_store")
    chunk_size: int = Field(default=1200, ge=300)
    chunk_overlap: int = Field(default=220, ge=0)
    top_k: int = Field(default=6, ge=1)
    min_confidence: float = Field(default=0.18, ge=0, le=1)
    ocr_enabled: bool = True
    ocr_language: str = "fra+eng"
    ocr_dpi: int = Field(default=220, ge=120, le=400)
    tesseract_cmd: str | None = None
    ocr_tessdata_dir: Path | None = Path("tessdata")

    embedding_provider: str = "hash"
    embedding_dimensions: int = Field(default=384, ge=16)
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    ollama_base_url: str = "http://localhost:11434"
    ollama_embedding_model: str = "nomic-embed-text"

    llm_provider: str = "openai"
    openai_model: str | None = None
    openai_chat_model: str = "gpt-4o-mini"
    ollama_chat_model: str = "llama3.1"
    llm_temperature: float = 0.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def document_patterns(self) -> list[str]:
        return [pattern.strip() for pattern in self.document_include_patterns.split(",") if pattern.strip()]

    @property
    def resolved_openai_chat_model(self) -> str:
        return self.openai_model or self.openai_chat_model

    def ensure_directories(self) -> None:
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
