"""Application settings loaded from environment variables."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the orchestrator."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    openai_model_name: str = Field(default="gpt-4o", description="OpenAI model")
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    anthropic_model_name: str = Field(
        default="claude-3-5-sonnet-20241022", description="Anthropic model"
    )
    llm_provider: Literal["openai", "anthropic"] = Field(
        default="openai", description="Primary LLM provider"
    )

    # Pinecone
    pinecone_api_key: str | None = Field(default=None, description="Pinecone API key")
    pinecone_environment: str = Field(default="us-east-1", description="Pinecone env")
    pinecone_index_name: str = Field(
        default="business-docs", description="Pinecone index for RAG"
    )

    # ERP / Database
    erp_database_path: str = Field(
        default="./data/erp.db", description="SQLite path for ERP simulation"
    )

    # SMTP (supplier communication)
    smtp_host: str = Field(default="smtp.example.com", description="SMTP host")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_user: str = Field(default="", description="SMTP user")
    smtp_password: str = Field(default="", description="SMTP password")
    smtp_use_tls: bool = Field(default=True, description="Use TLS for SMTP")
    smtp_mock_mode: bool = Field(
        default=True, description="If True, log emails only (no real send)"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Log level")

    def get_erp_path(self) -> Path:
        """Return ERP database path as Path; ensure parent dir exists."""
        path = Path(self.erp_database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return singleton settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
