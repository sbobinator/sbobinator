# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""Registro provider riassunto LLM."""

from __future__ import annotations

from sbobinator.http_ssl import ensure_ssl
from sbobinator.summary_config import temporary_api_keys
from sbobinator.summarize_providers.anthropic import AnthropicProvider
from sbobinator.summarize_providers.base import SummaryProvider
from sbobinator.summarize_providers.deepseek import DeepSeekProvider
from sbobinator.summarize_providers.gemini import GeminiProvider
from sbobinator.summarize_providers.local_qwen import LocalQwenProvider
from sbobinator.summarize_providers.moonshot import MoonshotProvider
from sbobinator.summarize_providers.openai import OpenAIProvider

PROVIDER_IDS = ("local", "openai", "gemini", "claude", "deepseek", "kimi")

_INSTANCES: dict[str, SummaryProvider] = {
    "local": LocalQwenProvider(),
    "openai": OpenAIProvider(),
    "gemini": GeminiProvider(),
    "claude": AnthropicProvider(),
    "deepseek": DeepSeekProvider(),
    "kimi": MoonshotProvider(),
}

ensure_ssl()


def get_provider(provider_id: str) -> SummaryProvider:
    pid = provider_id.strip().lower()
    if pid not in _INSTANCES:
        raise ValueError(f"Provider riassunto sconosciuto: {provider_id}")
    return _INSTANCES[pid]


def provider_label(provider_id: str) -> str:
    try:
        return get_provider(provider_id).display_name
    except ValueError:
        return provider_id


def list_provider_capabilities() -> list[dict]:
    items: list[dict] = []
    for pid in PROVIDER_IDS:
        provider = _INSTANCES[pid]
        available, reason = provider.is_available()
        items.append(
            {
                "id": pid,
                "label": provider.display_name,
                "available": available,
                "reason": reason,
                "default_model": provider.default_model(),
            }
        )
    return items


def first_available_provider() -> str | None:
    for item in list_provider_capabilities():
        if item["available"]:
            return item["id"]
    return None


def test_provider_connection(
    provider_id: str,
    *,
    api_key: str | None = None,
) -> tuple[bool, str]:
    ensure_ssl()
    pid = provider_id.strip().lower()
    overrides = {pid: api_key} if api_key and api_key.strip() else {}

    with temporary_api_keys(overrides):
        provider = get_provider(pid)
        available, reason = provider.is_available()
        if not available:
            if api_key and api_key.strip():
                return False, "API key inserita ma non valida o provider non configurato"
            return False, reason
        if pid == "local":
            return True, "Modello locale pronto (il test completo richiede diversi minuti)"
        try:
            text = provider.complete(
                "Sei un assistente.",
                "Rispondi solo con la parola OK.",
            )
            if text.strip().upper().startswith("OK"):
                return True, "Connessione riuscita"
            if text.strip():
                return True, f"Risposta ricevuta: {text.strip()[:80]}"
            return False, "Risposta vuota dal provider"
        except Exception as exc:
            msg = str(exc).strip() or type(exc).__name__
            if "Connection error" in msg or "CERTIFICATE_VERIFY_FAILED" in msg:
                msg += (
                    " — Problema SSL su Windows/Python. "
                    "Esegui: pip install -r requirements/local.txt e riavvia l'app."
                )
            elif "401" in msg or "authentication" in msg.lower() or "invalid api key" in msg.lower():
                msg = f"API key non valida per {provider.display_name}"
            return False, msg
