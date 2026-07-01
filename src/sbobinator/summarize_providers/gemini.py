# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""Riassunto via Google Gemini API."""

from __future__ import annotations

from sbobinator.config import SummaryLength
from sbobinator.http_ssl import ensure_ssl
from sbobinator.summary_config import DEFAULT_MODELS, get_api_key, get_model_override
from sbobinator.summarize_providers.base import ProgressCallback, SummaryResult, count_sentences
from sbobinator.summarize_providers.prompt import SYSTEM_PROMPT, user_prompt


class GeminiProvider:
    provider_id = "gemini"
    display_name = "Google Gemini"

    def is_available(self) -> tuple[bool, str]:
        if not get_api_key(self.provider_id):
            return False, "Inserisci la API key Gemini in Impostazioni"
        return True, ""

    def default_model(self) -> str:
        return get_model_override(self.provider_id) or DEFAULT_MODELS[self.provider_id]

    def estimate_tokens(self, text: str) -> int:
        return max(1, int(len(text.split()) * 1.35))

    def single_pass_token_limit(self) -> int:
        return 200_000

    def chunk_char_limit(self) -> int:
        return 200_000

    def complete(
        self,
        system: str,
        user: str,
        *,
        model: str | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> str:
        if on_progress:
            on_progress("summarize", 0.5, "Generazione riassunto (Gemini)...")
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ImportError(
                "Gemini richiede google-genai. Installa con:\n"
                "  pip install -e '.[summarize]'"
            ) from exc

        ensure_ssl()
        client = genai.Client(api_key=get_api_key(self.provider_id))
        response = client.models.generate_content(
            model=model or self.default_model(),
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.3,
            ),
        )
        return (response.text or "").strip()

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
