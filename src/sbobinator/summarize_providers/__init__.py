"""Provider LLM per riassunto trascritti."""

from sbobinator.http_ssl import ensure_ssl

ensure_ssl()

from sbobinator.summarize_providers.registry import (
    PROVIDER_IDS,
    get_provider,
    list_provider_capabilities,
    provider_label,
)

__all__ = [
    "PROVIDER_IDS",
    "get_provider",
    "list_provider_capabilities",
    "provider_label",
]
