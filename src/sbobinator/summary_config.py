"""Configurazione API key e segreti per riassunto LLM."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sbobinator.config import data_dir

_api_key_overrides: dict[str, str] = {}

PROVIDER_ENV_KEYS = {
    "openai": "SBOBINATOR_OPENAI_API_KEY",
    "gemini": "SBOBINATOR_GEMINI_API_KEY",
    "claude": "SBOBINATOR_ANTHROPIC_API_KEY",
    "deepseek": "SBOBINATOR_DEEPSEEK_API_KEY",
    "kimi": "SBOBINATOR_KIMI_API_KEY",
}

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "gemini": "gemini-2.0-flash",
    "claude": "claude-3-5-haiku-20241022",
    "deepseek": "deepseek-chat",
    "kimi": "moonshot-v1-8k",
}


def secrets_path() -> Path:
    return data_dir() / ".secrets" / "summary_keys.json"


def load_secrets() -> dict[str, str]:
    data: dict[str, str] = {}
    path = secrets_path()
    if path.is_file():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                data.update({k: str(v) for k, v in raw.items() if v})
        except json.JSONDecodeError:
            pass
    for provider, env_name in PROVIDER_ENV_KEYS.items():
        val = os.environ.get(env_name, "").strip()
        if val:
            data[provider] = val
    return data


def save_secrets(keys: dict[str, str]) -> None:
    path = secrets_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if path.is_file():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    for provider, value in keys.items():
        cleaned = value.strip()
        if cleaned:
            existing[provider] = cleaned
        elif provider in existing:
            del existing[provider]
    path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")


def get_api_key(provider: str) -> str:
    override = _api_key_overrides.get(provider, "").strip()
    if override:
        return override
    return load_secrets().get(provider, "").strip()


@contextmanager
def temporary_api_keys(keys: dict[str, str]) -> Iterator[None]:
    """Sovrascrive temporaneamente le API key (es. test connessione prima del salvataggio)."""
    global _api_key_overrides
    previous = _api_key_overrides.copy()
    for provider, value in keys.items():
        cleaned = value.strip()
        if cleaned:
            _api_key_overrides[provider] = cleaned
        elif provider in _api_key_overrides:
            del _api_key_overrides[provider]
    try:
        yield
    finally:
        _api_key_overrides = previous


def has_api_key(provider: str) -> bool:
    return bool(get_api_key(provider))


def get_model_override(provider: str) -> str | None:
    secrets = load_secrets()
    key = f"{provider}_model"
    val = secrets.get(key, "").strip()
    return val or None


def configured_providers() -> dict[str, bool]:
    return {pid: has_api_key(pid) for pid in PROVIDER_ENV_KEYS}
