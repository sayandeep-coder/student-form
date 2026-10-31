"""Application configuration module using pydantic-settings."""

from functools import lru_cache
import re
from typing import List, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="Student Details API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(
        default="postgresql+psycopg://USERNAME:PASSWORD@HOST:5432/DATABASE_NAME",
        alias="DATABASE_URL",
    )
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    cors_origins: Union[List[str], str] = Field(default=["*"], alias="CORS_ORIGINS")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    def is_placeholder_database_url(self) -> bool:
        """Check if the configured database URL is a placeholder."""
        if not self.database_url:
            return True
        placeholders = [
            "USERNAME:PASSWORD@HOST",
            "DATABASE_NAME",
            "localhost/placeholder",
        ]
        return any(placeholder in self.database_url for placeholder in placeholders)

    def get_validated_database_url(self) -> str:
        """Validate that the database URL is present and not a placeholder.

        Raises a clear configuration error if the database URL is missing or
        still contains placeholder credentials.
        """
        if not self.database_url or self.database_url.strip() == "":
            raise ValueError(
                "DATABASE_URL is not configured. Please supply a valid PostgreSQL "
                "connection URL in your environment or .env file."
            )
        if self.is_placeholder_database_url():
            raise ValueError(
                "DATABASE_URL contains placeholder credentials ('USERNAME:PASSWORD@HOST'). "
                "Please replace the placeholder in your .env file with your actual "
                "PostgreSQL connection URL (e.g. postgresql+psycopg://user:pass@host:5432/dbname)."
            )
        url = self.database_url
        if url.startswith("postgresql://"):
            url = "postgresql+psycopg://" + url[len("postgresql://") :]
        return url

    def get_masked_database_url(self) -> str:
        """Return a sanitized version of the database URL for logging."""
        if not self.database_url:
            return "<empty>"
        # Regex to mask password: scheme://user:password@host
        return re.sub(r":([^:@]+)@", r":***@", self.database_url)


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()
