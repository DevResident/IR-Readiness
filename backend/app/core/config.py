"""Application settings, read from environment variables or backend/.env.

Secrets (the Anthropic API key) live only in the environment, never in code or logs.
"""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # "anthropic" calls the model; "demo" replays examples/ so the app runs without an API key
    llm_provider: Literal["anthropic", "demo"] = "anthropic"
    anthropic_api_key: SecretStr | None = None  # SecretStr hides the value in repr() and logs
    anthropic_model: str = "claude-opus-5-5"
    anthropic_effort: str = "medium"  # low | medium | high | xhigh | max
    # Optional Anthropic-compatible gateway (e.g. OpenCode Console). None = api.anthropic.com
    anthropic_base_url: str | None = None
    # Optional extra HTTP headers for the gateway, as JSON, e.g. {"x-opencode-session": "ses_..."}
    anthropic_extra_headers: dict[str, str] = {}
    cors_origins: str = "http://localhost:5173"
    log_level: str = "INFO"

    @property
    def llm_configured(self) -> bool:
        return self.llm_provider == "demo" or self.anthropic_api_key is not None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
