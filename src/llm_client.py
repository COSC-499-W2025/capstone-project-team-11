"""LLM configuration plumbing (no provider calls in PR1)."""

from dataclasses import dataclass
from typing import Optional
from config import load_config


@dataclass
class LLMConfig:
    enabled: bool
    consent: bool
    provider: str
    model: str
    base_url: str
    api_key: Optional[str]


def get_llm_config() -> LLMConfig:
    cfg = load_config()
    return LLMConfig(
        enabled=bool(cfg.get("llm_enabled")),
        consent=bool(cfg.get("llm_consent")),
        provider=str(cfg.get("llm_provider") or "ollama"),
        model=str(cfg.get("llm_model") or "llama3.2:3b"),
        base_url=str(cfg.get("llm_base_url") or "http://localhost:11434"),
        api_key=cfg.get("llm_api_key"),
    )


def llm_is_available() -> bool:
    cfg = get_llm_config()
    return cfg.enabled and cfg.consent and bool(cfg.model)
