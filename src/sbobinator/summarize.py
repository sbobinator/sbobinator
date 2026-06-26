"""Riassunto testo: estrattivo (veloce) o astrattivo (mT5, più lento)."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from sbobinator.config import SummaryLength, SummaryMode

logger = logging.getLogger(__name__)

_abstractive_pipeline = None

# ~4k caratteri per chunk astrattivo su CPU
_ABSTRACTIVE_CHUNK_CHARS = 3500


@dataclass
class SummaryResult:
    text: str
    mode: SummaryMode
    source_chars: int
    source_sentences: int = 0
    summary_sentences: int = 0


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?…])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def estimate_summary_sentences(
    text: str,
    length: SummaryLength = SummaryLength.auto,
) -> int:
    """Calcola quante frasi includere in base alla lunghezza del testo."""
    sentences = _split_sentences(text)
    total = len(sentences)
    if total == 0:
        return 0
    if total <= 4:
        return total

    # ~12% delle frasi originali, con limiti ragionevoli
    base = max(3, min(30, round(total * 0.12)))

    if length == SummaryLength.short:
        target = max(2, round(base * 0.6))
    elif length == SummaryLength.detailed:
        target = min(total, round(base * 1.6))
    elif length == SummaryLength.normal:
        target = base
    else:  # auto
        if total <= 15:
            target = max(2, total // 3)
        elif total <= 40:
            target = max(3, total // 5)
        else:
            target = base

    return max(2, min(total, target))


def estimate_abstractive_lengths(text: str, length: SummaryLength = SummaryLength.auto) -> tuple[int, int]:
    """max_length e min_length per mT5 in base al testo sorgente."""
    words = len(text.split())
    if length == SummaryLength.short:
        return (80, 25)
    if length == SummaryLength.detailed:
        return (min(400, max(180, words // 3)), 60)
    if length == SummaryLength.normal:
        return (min(250, max(120, words // 5)), 40)
    # auto
    if words < 150:
        return (100, 30)
    if words < 600:
        return (180, 40)
    return (min(350, words // 4), 50)


def _word_set(sentence: str) -> set[str]:
    return set(re.findall(r"\w+", sentence.lower()))


def summarize_extractive(text: str, num_sentences: int = 5) -> str:
    """LexRank semplificato: nessun modello extra, funziona offline."""
    sentences = _split_sentences(text)
    if len(sentences) <= num_sentences:
        return text.strip()

    num_sentences = max(1, min(num_sentences, len(sentences)))
    vectors = [_word_set(s) for s in sentences]
    scores = [0.0] * len(sentences)

    for i, vi in enumerate(vectors):
        if not vi:
            continue
        for j, vj in enumerate(vectors):
            if i == j or not vj:
                continue
            overlap = len(vi & vj) / (len(vi | vj) ** 0.5 + 1e-9)
            scores[i] += overlap

    ranked = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)
    top = sorted(ranked[:num_sentences])
    return " ".join(sentences[i] for i in top)


def _get_abstractive_pipeline():
    global _abstractive_pipeline
    if _abstractive_pipeline is not None:
        return _abstractive_pipeline

    try:
        from transformers import pipeline
    except ImportError as exc:
        raise ImportError(
            "Riassunto astrattivo richiede transformers. Installa con:\n"
            "  pip install -e '.[local]'"
        ) from exc

    logger.info("Caricamento modello riassunto mT5-small ...")
    _abstractive_pipeline = pipeline(
        "summarization",
        model="google/mt5-small",
        tokenizer="google/mt5-small",
    )
    return _abstractive_pipeline


def _summarize_chunk_abstractive(chunk: str, max_length: int, min_length: int) -> str:
    pipe = _get_abstractive_pipeline()
    prompt = f"summarize: {chunk}"
    out = pipe(
        prompt,
        max_length=max_length,
        min_length=min_length,
        do_sample=False,
        truncation=True,
    )
    return out[0]["summary_text"].strip()


def summarize_abstractive(
    text: str,
    max_length: int = 180,
    min_length: int = 40,
) -> str:
    """Riassunto generativo multilingue (italiano incluso)."""
    text = text.strip()
    if not text:
        return ""

    if len(text) <= _ABSTRACTIVE_CHUNK_CHARS:
        return _summarize_chunk_abstractive(text, max_length, min_length)

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + _ABSTRACTIVE_CHUNK_CHARS, len(text))
        if end < len(text):
            cut = text.rfind(" ", start, end)
            if cut > start:
                end = cut
        chunks.append(text[start:end].strip())
        start = end

    partials = [
        _summarize_chunk_abstractive(c, max_length // 2 + 40, min_length // 2 + 10)
        for c in chunks
        if c
    ]
    combined = " ".join(partials)
    if len(combined) > _ABSTRACTIVE_CHUNK_CHARS:
        return _summarize_chunk_abstractive(combined, max_length, min_length)
    return combined


def unload_abstractive_model() -> None:
    global _abstractive_pipeline
    _abstractive_pipeline = None
    try:
        import gc

        import torch

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


def summarize(
    text: str,
    mode: SummaryMode = SummaryMode.extractive,
    num_sentences: int | None = None,
    length: SummaryLength = SummaryLength.auto,
    max_length: int | None = None,
) -> SummaryResult:
    source_sentences = len(_split_sentences(text))

    if mode == SummaryMode.extractive:
        target = num_sentences if num_sentences is not None else estimate_summary_sentences(text, length)
        summary = summarize_extractive(text, num_sentences=target)
        used = len(_split_sentences(summary))
    else:
        auto_max, auto_min = estimate_abstractive_lengths(text, length)
        summary = summarize_abstractive(
            text,
            max_length=max_length or auto_max,
            min_length=auto_min,
        )
        target = 0
        used = len(_split_sentences(summary))

    return SummaryResult(
        text=summary,
        mode=mode,
        source_chars=len(text),
        source_sentences=source_sentences,
        summary_sentences=used,
    )
