#!/usr/bin/env python3
"""Benchmark riassunti offline — solo trascrizioni, senza UI né pipeline ASR.

Genera un report confrontabile in docs/summary-benchmark/runs/<timestamp>/
con tutte le combinazioni modalità × lunghezza su ogni trascrizione trovata.

Uso:
  python scripts/summary_benchmark.py
  python scripts/summary_benchmark.py --jobs-dir data/output/jobs
  python scripts/summary_benchmark.py --only campione-italiano-lungo
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JOBS = ROOT / "data" / "output" / "jobs"
DEFAULT_OUT = ROOT / "docs" / "summary-benchmark" / "runs"

if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from sbobinator.config import (  # noqa: E402
    SummaryLength,
    SummaryMode,
    local_summary_model_available,
)
from sbobinator.summarize import summarize, unload_abstractive_model  # noqa: E402

LENGTHS = (
    SummaryLength.auto,
    SummaryLength.short,
    SummaryLength.normal,
    SummaryLength.detailed,
)


@dataclass
class RunRow:
    source_id: str
    source_path: str
    mode: str
    length: str
    source_words: int
    source_chars: int
    source_sentences: int
    summary_words: int
    summary_chars: int
    summary_sentences: int
    compression_pct: float
    seconds: float
    summary_text: str


def _find_transcripts(jobs_dir: Path, only: str | None) -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    if not jobs_dir.is_dir():
        return found
    for txt in sorted(jobs_dir.glob("*/trascrizione.txt")):
        job_id = txt.parent.name
        label = job_id.split("_", 2)[-1] if "_" in job_id else job_id
        if only and only not in label and only not in job_id:
            continue
        found.append((label, txt))
    return found


def _word_count(text: str) -> int:
    return len(text.split())


def _run_one(label: str, source_path: Path, mode: SummaryMode, length: SummaryLength) -> RunRow:
    text = source_path.read_text(encoding="utf-8").strip()
    t0 = time.perf_counter()
    result = summarize(text, mode=mode, length=length)
    elapsed = time.perf_counter() - t0
    src_words = _word_count(text)
    sum_words = _word_count(result.text)
    compression = round(100 * sum_words / src_words, 1) if src_words else 0.0
    return RunRow(
        source_id=label,
        source_path=str(source_path.resolve()),
        mode=mode.value,
        length=length.value,
        source_words=src_words,
        source_chars=len(text),
        source_sentences=result.source_sentences,
        summary_words=sum_words,
        summary_chars=len(result.text),
        summary_sentences=result.summary_sentences,
        compression_pct=compression,
        seconds=round(elapsed, 2),
        summary_text=result.text,
    )


def _write_report(out_dir: Path, rows: list[RunRow], abstractive_ok: bool) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    by_source: dict[str, list[RunRow]] = {}
    for row in rows:
        by_source.setdefault(row.source_id, []).append(row)

    for label, source_rows in by_source.items():
        src_dir = out_dir / _safe_name(label)
        src_dir.mkdir(parents=True, exist_ok=True)
        meta = source_rows[0]
        (src_dir / "_sorgente.txt").write_text(
            Path(meta.source_path).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (src_dir / "_meta.json").write_text(
            json.dumps(
                {
                    "source_id": label,
                    "source_path": meta.source_path,
                    "source_words": meta.source_words,
                    "source_chars": meta.source_chars,
                    "source_sentences": meta.source_sentences,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        for row in source_rows:
            fname = f"{row.mode}_{row.length}.txt"
            header = (
                f"# {row.mode} / {row.length}\n"
                f"# parole sorgente: {row.source_words} -> riassunto: {row.summary_words} "
                f"({row.compression_pct}%)\n"
                f"# frasi: {row.source_sentences} -> {row.summary_sentences} | "
                f"tempo: {row.seconds}s\n\n"
            )
            (src_dir / fname).write_text(header + row.summary_text, encoding="utf-8")

    md_lines = [
        "# Benchmark riassunti Sbobinator",
        "",
        f"Generato: {datetime.now().isoformat(timespec='seconds')}",
        f"IT5 disponibile: {'sì' if abstractive_ok else 'no'}",
        "",
        "## Tabella comparativa",
        "",
        "| Sorgente | Modalità | Lunghezza | Parole src | Parole out | % | Frasi out | sec |",
        "|----------|----------|-----------|------------|------------|---|-----------|-----|",
    ]
    for row in rows:
        md_lines.append(
            f"| {row.source_id} | {row.mode} | {row.length} | "
            f"{row.source_words} | {row.summary_words} | {row.compression_pct} | "
            f"{row.summary_sentences} | {row.seconds} |"
        )
    md_lines.extend(
        [
            "",
            "## Come leggere",
            "",
            "- Cartella per sorgente: contiene `_sorgente.txt` e un file per ogni combinazione.",
            "- **extractive** = sintesi LexRank (frasi originali selezionate).",
            "- **abstractive** = IT5 (`gsarti/it5-small-news-summarization`).",
            "- Confronta qualità e copertura del contenuto, non solo la lunghezza.",
            "",
            "## Note qualità (da valutare a mano)",
            "",
            "- Riassunto troppo corto rispetto al testo sorgente?",
            "- Perde concetti chiave della trascrizione?",
            "- IT5 addestrato su **news**, non su parlato/interviste: può deformare il senso.",
            "",
        ]
    )
    (out_dir / "REPORT.md").write_text("\n".join(md_lines), encoding="utf-8")
    (out_dir / "REPORT.json").write_text(
        json.dumps([asdict(r) for r in rows], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _safe_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark riassunti su trascrizioni esistenti")
    parser.add_argument("--jobs-dir", type=Path, default=DEFAULT_JOBS)
    parser.add_argument("--out-dir", type=Path, default=None, help="Cartella output (default: docs/.../runs/TIMESTAMP)")
    parser.add_argument("--only", type=str, default=None, help="Filtra per nome sorgente (es. campione-italiano-lungo)")
    parser.add_argument("--skip-abstractive", action="store_true")
    args = parser.parse_args()

    transcripts = _find_transcripts(args.jobs_dir, args.only)
    if not transcripts:
        print(f"Nessuna trascrizione in {args.jobs_dir}")
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out_dir or (DEFAULT_OUT / ts)
    abstractive_ok = local_summary_model_available() and not args.skip_abstractive

    modes: list[SummaryMode] = [SummaryMode.extractive]
    if abstractive_ok:
        modes.append(SummaryMode.abstractive)
    else:
        print("IT5 non disponibile — solo sintesi estrattiva.")

    print(f"Trovate {len(transcripts)} trascrizioni -> output: {out_dir}")
    rows: list[RunRow] = []

    try:
        for label, path in transcripts:
            print(f"\n=== {label} ===")
            for mode in modes:
                for length in LENGTHS:
                    tag = f"{mode.value}/{length.value}"
                    print(f"  {tag}...", end=" ", flush=True)
                    row = _run_one(label, path, mode, length)
                    rows.append(row)
                    print(
                        f"{row.summary_words} parole ({row.compression_pct}%), "
                        f"{row.seconds}s"
                    )
    finally:
        if abstractive_ok:
            unload_abstractive_model()

    _write_report(out_dir, rows, abstractive_ok)
    print(f"\nReport: {out_dir / 'REPORT.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
