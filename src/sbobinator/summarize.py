"""Orchestratore riassunto LLM multi-provider con map-reduce per testi lunghi."""

from __future__ import annotations

import logging

from sbobinator.config import SummaryLength
from sbobinator.summarize_providers.base import ProgressCallback, SummaryResult, count_sentences
from sbobinator.summarize_providers.local_qwen import unload_local_llm
from sbobinator.summarize_providers.prompt import SYSTEM_PROMPT, merge_prompt, user_prompt
from sbobinator.summarize_providers.registry import get_provider, provider_label

logger = logging.getLogger(__name__)

_DEFAULT_MERGE_BATCH = 6


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


def _should_map_reduce(impl: object, tokens: int, chars: int) -> bool:
    custom = getattr(impl, "use_map_reduce", None)
    if callable(custom):
        return bool(custom(tokens, chars))
    threshold = impl.single_pass_token_limit()  # type: ignore[attr-defined]
    return tokens > threshold


def _chunk_length(length: SummaryLength) -> SummaryLength:
    if length == SummaryLength.auto:
        return SummaryLength.normal
    return length


def _merge_batch_size(impl: object) -> int:
    return int(getattr(impl, "merge_batch_size", lambda: _DEFAULT_MERGE_BATCH)())


def _complete(
    impl: object,
    user: str,
    *,
    model: str | None,
    on_progress: ProgressCallback | None,
) -> str:
    return impl.complete(  # type: ignore[attr-defined]
        SYSTEM_PROMPT,
        user,
        model=model,
        on_progress=on_progress,
    )


def _hierarchical_merge(
    partials: list[str],
    impl: object,
    length: SummaryLength,
    used_model: str | None,
    on_progress: ProgressCallback | None,
) -> tuple[str, str]:
    """Unisce riassunti parziali a livelli (evita merge unico su decine di segmenti)."""
    batch_size = _merge_batch_size(impl)
    current = [p.strip() for p in partials if p.strip()]
    strategy = "map_reduce"
    level = 0

    while len(current) > 1:
        level += 1
        if len(current) > batch_size:
            strategy = "map_reduce_hierarchical"
        next_level: list[str] = []
        batches = [current[i : i + batch_size] for i in range(0, len(current), batch_size)]

        for bi, batch in enumerate(batches):
            if on_progress:
                on_progress(
                    "summarize",
                    97.5,
                    f"Unione livello {level}: gruppo {bi + 1}/{len(batches)}...",
                )
            if len(batch) == 1:
                next_level.append(batch[0])
                continue
            merged_input = merge_prompt("\n\n".join(batch), length)
            next_level.append(
                _complete(impl, merged_input, model=used_model, on_progress=on_progress)
            )
        current = next_level

    return current[0], strategy


def _map_reduce_summarize(
    text: str,
    *,
    impl: object,
    provider_id: str,
    length: SummaryLength,
    used_model: str | None,
    tokens: int,
    on_progress: ProgressCallback | None,
) -> SummaryResult:
    chunk_limit = impl.chunk_char_limit()  # type: ignore[attr-defined]
    chunks = _split_chunks(text, chunk_limit)
    chunk_len = _chunk_length(length)

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
        part = _complete(
            impl,
            user_prompt(chunk, chunk_len),
            model=used_model,
            on_progress=on_progress,
        )
        partials.append(part.strip())

    if len(partials) == 1:
        final_text = partials[0]
        strategy = "map_reduce"
    else:
        if on_progress:
            on_progress("summarize", 98.0, "Unione riassunti parziali...")
        final_text, strategy = _hierarchical_merge(
            partials, impl, length, used_model, on_progress
        )

    return SummaryResult(
        text=final_text.strip(),
        provider=provider_id,
        model=used_model or "",
        source_chars=len(text),
        input_tokens=tokens,
        strategy=strategy,
        summary_sentences=count_sentences(final_text),
    )


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
    chars = len(text)
    used_model = model or impl.default_model()

    if _should_map_reduce(impl, tokens, chars):
        return _map_reduce_summarize(
            text,
            impl=impl,
            provider_id=provider_id,
            length=length,
            used_model=used_model,
            tokens=tokens,
            on_progress=on_progress,
        )

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


def unload_summary_models() -> None:
    """Libera memoria dei modelli riassunto caricati."""
    unload_local_llm()


# --- Legacy (deprecato, non usare in produzione) ---


def unload_abstractive_model() -> None:
    unload_summary_models()
