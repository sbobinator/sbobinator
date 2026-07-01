# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""Riassunto via OpenAI API."""

from __future__ import annotations

from sbobinator.config import SummaryLength
from sbobinator.summary_config import DEFAULT_MODELS, get_api_key, get_model_override
from sbobinator.summarize_providers.base import ProgressCallback, SummaryResult, count_sentences
from sbobinator.summarize_providers.openai_compat import chat_complete
from sbobinator.summarize_providers.prompt import SYSTEM_PROMPT, user_prompt


class OpenAIProvider:
    provider_id = "openai"
    display_name = "OpenAI"

    def is_available(self) -> tuple[bool, str]:
        if not get_api_key(self.provider_id):
            return False, "Inserisci la API key OpenAI in Impostazioni"
        return True, ""

    def default_model(self) -> str:
        return get_model_override(self.provider_id) or DEFAULT_MODELS[self.provider_id]

    def estimate_tokens(self, text: str) -> int:
        return max(1, int(len(text.split()) * 1.35))

    def single_pass_token_limit(self) -> int:
        return 100_000

    def chunk_char_limit(self) -> int:
        return 120_000

    def complete(
        self,
        system: str,
        user: str,
        *,
        model: str | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> str:
        if on_progress:
            on_progress("summarize", 0.5, "Generazione riassunto (OpenAI)...")
        return chat_complete(
            api_key=get_api_key(self.provider_id),
            model=model or self.default_model(),
            system=system,
            user=user,
        )

    def summarize(
        self,
        text: str,
        *,
        length: SummaryLength = SummaryLength.auto,
        model: str | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> SummaryResult:
        used_model = model or self.default_model()
        summary = self.complete(
            SYSTEM_PROMPT,
            user_prompt(text, length),
            model=used_model,
            on_progress=on_progress,
        )
        return SummaryResult(
            text=summary,
            provider=self.provider_id,
            model=used_model,
            source_chars=len(text),
            input_tokens=self.estimate_tokens(text),
            strategy="single",
            summary_sentences=count_sentences(summary),
        )
