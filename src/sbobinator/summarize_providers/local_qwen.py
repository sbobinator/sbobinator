# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""Riassunto con LLM locale Qwen2.5 via llama.cpp (GGUF)."""

from __future__ import annotations

import logging
import os

from sbobinator.config import (
    LOCAL_LLM_CTX,
    LOCAL_LLM_FOLDER,
    LOCAL_LLM_GGUF_FILE,
    SummaryLength,
    local_gguf_path,
    system_ram_gb,
)
from sbobinator.summarize_providers.base import ProgressCallback, SummaryResult, count_sentences
from sbobinator.summarize_providers.prompt import SYSTEM_PROMPT, user_prompt

logger = logging.getLogger(__name__)

_llm = None


def _get_llm():
    global _llm
    if _llm is not None:
        return _llm

    try:
        from llama_cpp import Llama
    except ImportError as exc:
        raise ImportError(
            "LLM locale richiede llama-cpp-python. Installa con:\n"
            "  pip install -e '.[summarize]'"
        ) from exc

    path = local_gguf_path()
    if not path:
        raise RuntimeError(
            f"Modello GGUF non trovato in models/{LOCAL_LLM_FOLDER}/.\n"
            "Scaricalo con:\n"
            "  python scripts/download_summary_llm.py"
        )

    threads = max(2, (os.cpu_count() or 4) - 1)
    logger.info("Caricamento LLM locale %s (CPU, %d thread)...", path.name, threads)
    _llm = Llama(
        model_path=str(path),
        n_ctx=LOCAL_LLM_CTX,
        n_threads=threads,
        verbose=False,
    )
    return _llm


def unload_local_llm() -> None:
    global _llm
    _llm = None
    try:
        import gc

        gc.collect()
    except Exception:
        pass


class LocalQwenProvider:
    provider_id = "local"
    display_name = "LLM locale (Qwen)"

    def is_available(self) -> tuple[bool, str]:
        from sbobinator.config import MIN_RAM_GB

        ram = system_ram_gb()
        if ram is not None and ram < MIN_RAM_GB:
            return False, f"Richiede almeno {MIN_RAM_GB} GB di RAM (rilevati ~{ram:.0f} GB)"
        if not local_gguf_path():
            return (
                False,
                f"Modello assente. Esegui: python scripts/download_summary_llm.py",
            )
        try:
            import llama_cpp  # noqa: F401
        except ImportError:
            return False, "Installa dipendenze: pip install -e '.[summarize]'"
        return True, ""

    def default_model(self) -> str:
        return LOCAL_LLM_GGUF_FILE

    def estimate_tokens(self, text: str) -> int:
        return max(1, int(len(text.split()) * 1.35))

    def single_pass_token_limit(self) -> int:
        return 6000

    def chunk_char_limit(self) -> int:
        return 4000

    def use_map_reduce(self, tokens: int, chars: int) -> bool:
        """Qwen 3B: spezza testi medi/lunghi per qualità e copertura."""
        return tokens > 350 or chars > 1500

    def merge_batch_size(self) -> int:
        return 4

    def complete(
        self,
        system: str,
        user: str,
        *,
        model: str | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> str:
        if on_progress:
            on_progress("summarize", 0.5, "Generazione riassunto (LLM locale, può richiedere diversi minuti)...")
        llm = _get_llm()
        out = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            max_tokens=2048,
        )
        content = out["choices"][0]["message"]["content"]
        return (content or "").strip()

    def summarize(
        self,
        text: str,
        *,
        length: SummaryLength = SummaryLength.auto,
        model: str | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> SummaryResult:
        summary = self.complete(
            SYSTEM_PROMPT,
            user_prompt(text, length),
            model=model,
            on_progress=on_progress,
        )
        return SummaryResult(
            text=summary,
            provider=self.provider_id,
            model=self.default_model(),
            source_chars=len(text),
            input_tokens=self.estimate_tokens(text),
            strategy="single",
            summary_sentences=count_sentences(summary),
        )
