"""Orchestratore riassunto LLM multi-provider con map-reduce per testi lunghi."""

from __future__ import annotations

import logging

from sbobinator.config import SummaryLength
from sbobinator.summarize_providers.base import ProgressCallback, SummaryResult, count_sentences
from sbobinator.summarize_providers.local_qwen import unload_local_llm
from sbobinator.summarize_providers.prompt import SYSTEM_PROMPT, merge_prompt, user_prompt
from sbobinator.summarize_providers.registry import get_provider, provider_label

logger = logging.getLogger(__name__)


def _split_chunks(text: str, max_chars: int) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            for sep in ("\n\n", "\n", ". ", "? ", "! "):
                cut = text.rfind(sep, start, end)
                if cut > start + max_chars // 4:
                    end = cut + len(sep)
                    break
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        start = end
    return chunks


def _resolve_provider_id(provider_id: str | None) -> str:
    if provider_id:
        return provider_id.strip().lower()
    from sbobinator.summarize_providers.registry import first_available_provider

    fallback = first_available_provider()
    if not fallback:
        raise RuntimeError(
            "Nessun provider riassunto disponibile. "
            "Configura un provider cloud in Impostazioni o scarica il modello locale."
        )
    return fallback


def summarize(
    text: str,
    *,
    provider: str | None = None,
    length: SummaryLength = SummaryLength.auto,
    model: str | None = None,
    on_progress: ProgressCallback | None = None,
) -> SummaryResult:
    """Genera un riassunto LLM del testo trascritto."""
    text = text.strip()
    if not text:
        return SummaryResult(
            text="",
            provider=provider or "",
            model=model or "",
            source_chars=0,
            strategy="single",
        )

    provider_id = _resolve_provider_id(provider)
    impl = get_provider(provider_id)
    available, reason = impl.is_available()
    if not available:
        raise RuntimeError(reason)

    tokens = impl.estimate_tokens(text)
    threshold = impl.single_pass_token_limit()
    used_model = model or impl.default_model()

    if tokens <= threshold:
        if on_progress:
            on_progress(
                "summarize",
                92.0,
                f"Riassunto ({provider_label(provider_id)})...",
            )
        result = impl.summarize(
            text,
            length=length,
            model=used_model,
            on_progress=on_progress,
        )
        result.strategy = "single"
        result.input_tokens = tokens
        return result

    # Map-reduce per testi che superano il contesto del provider
    chunk_limit = impl.chunk_char_limit()
    chunks = _split_chunks(text, chunk_limit)
    if on_progress:
        on_progress(
            "summarize",
            90.0,
            f"Riassunto map-reduce: {len(chunks)} segmenti ({provider_label(provider_id)})...",
        )

    partials: list[str] = []
    for i, chunk in enumerate(chunks):
        if on_progress:
            pct = 90.0 + (7.0 * (i + 1) / max(len(chunks), 1))
            on_progress(
                "summarize",
                pct,
                f"Segmento riassunto {i + 1}/{len(chunks)}...",
            )
        part = impl.complete(
            SYSTEM_PROMPT,
            user_prompt(chunk, SummaryLength.normal),
            model=used_model,
            on_progress=on_progress,
        )
        partials.append(part.strip())

    merged_input = merge_prompt("\n\n".join(partials), length)
    if on_progress:
        on_progress("summarize", 98.0, "Unione riassunti parziali...")

    final_text = impl.complete(
        SYSTEM_PROMPT,
        merged_input,
        model=used_model,
        on_progress=on_progress,
    )

    return SummaryResult(
        text=final_text.strip(),
        provider=provider_id,
        model=used_model,
        source_chars=len(text),
        input_tokens=tokens,
        strategy="map_reduce",
        summary_sentences=count_sentences(final_text),
    )


def unload_summary_models() -> None:
    """Libera memoria dei modelli riassunto caricati."""
    unload_local_llm()


# --- Legacy (deprecato, non usare in produzione) ---


def unload_abstractive_model() -> None:
    unload_summary_models()
