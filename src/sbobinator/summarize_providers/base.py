"""Interfacce condivise per i provider di riassunto."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from sbobinator.config import SummaryLength

ProgressCallback = Callable[[str, float, str], None]


@dataclass
class SummaryResult:
    text: str
    provider: str
    model: str
    source_chars: int
    input_tokens: int = 0
    output_tokens: int = 0
    strategy: str = "single"
    summary_sentences: int = 0


class SummaryProvider(Protocol):
    provider_id: str
    display_name: str

    def is_available(self) -> tuple[bool, str]:
        """Ritorna (disponibile, messaggio se non disponibile)."""
        ...

    def default_model(self) -> str:
        ...

    def estimate_tokens(self, text: str) -> int:
        ...

    def summarize(
        self,
        text: str,
        *,
        length: SummaryLength = SummaryLength.auto,
        model: str | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> SummaryResult:
        ...


def count_sentences(text: str) -> int:
    import re

    parts = re.split(r"(?<=[.!?…])\s+", text.strip())
    return len([p for p in parts if p.strip()])
