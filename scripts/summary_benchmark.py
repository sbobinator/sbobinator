# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

#!/usr/bin/env python3
"""Benchmark riassunti LLM — solo trascrizioni, senza UI né pipeline ASR.

Genera un report in docs/summary-benchmark/runs/<timestamp>/

Uso:
  python scripts/summary_benchmark.py --provider openai
  python scripts/summary_benchmark.py --provider local --only campione-italiano-lungo
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

from sbobinator.config import SummaryLength  # noqa: E402
from sbobinator.summarize import summarize, unload_summary_models  # noqa: E402
from sbobinator.summarize_providers.registry import PROVIDER_IDS, get_provider  # noqa: E402

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
    provider: str
    model: str
    strategy: str
    length: str
    source_words: int
    source_chars: int
    input_tokens: int
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


def _run_one(label: str, source_path: Path, provider_id: str, length: SummaryLength) -> RunRow:
    text = source_path.read_text(encoding="utf-8").strip()
    t0 = time.perf_counter()
    result = summarize(text, provider=provider_id, length=length)
    elapsed = time.perf_counter() - t0
    src_words = _word_count(text)
    sum_words = _word_count(result.text)
    compression = round(100 * sum_words / src_words, 1) if src_words else 0.0
    return RunRow(
        source_id=label,
        source_path=str(source_path.resolve()),
        provider=result.provider,
        model=result.model,
        strategy=result.strategy,
        length=length.value,
        source_words=src_words,
        source_chars=len(text),
        input_tokens=result.input_tokens,
        summary_words=sum_words,
        summary_chars=len(result.text),
        summary_sentences=result.summary_sentences,
        compression_pct=compression,
        seconds=round(elapsed, 2),
        summary_text=result.text,
    )


def _write_report(out_dir: Path, rows: list[RunRow], provider_id: str) -> None:
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
                    "provider": provider_id,
                    "source_words": meta.source_words,
                    "source_chars": meta.source_chars,
                    "input_tokens": meta.input_tokens,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        for row in source_rows:
            fname = f"{row.length}.txt"
            header = (
                f"# provider: {row.provider} / model: {row.model} / {row.length}\n"
                f"# strategia: {row.strategy} | token input stimati: {row.input_tokens}\n"
                f"# parole sorgente: {row.source_words} -> riassunto: {row.summary_words} "
                f"({row.compression_pct}%)\n"
                f"# frasi out: {row.summary_sentences} | tempo: {row.seconds}s\n\n"
            )
            (src_dir / fname).write_text(header + row.summary_text, encoding="utf-8")

    md_lines = [
        "# Benchmark riassunti LLM — Sbobinator",
        "",
        f"Generato: {datetime.now().isoformat(timespec='seconds')}",
        f"Provider: `{provider_id}`",
        "",
        "## Tabella comparativa",
        "",
        "| Sorgente | Lunghezza | Parole src | Token ~ | Parole out | % | Strategia | sec |",
        "|----------|-----------|------------|---------|------------|---|-----------|-----|",
    ]
    for row in rows:
        md_lines.append(
            f"| {row.source_id} | {row.length} | {row.source_words} | {row.input_tokens} | "
            f"{row.summary_words} | {row.compression_pct} | {row.strategy} | {row.seconds} |"
        )
    md_lines.extend(
        [
            "",
            "## Come leggere",
            "",
            "- Un file per lunghezza in ogni cartella sorgente.",
            "- Valuta qualità: contesto, punti chiave, niente invenzioni.",
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
    parser = argparse.ArgumentParser(description="Benchmark riassunto LLM su trascrizioni esistenti")
    parser.add_argument("--jobs-dir", type=Path, default=DEFAULT_JOBS)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--only", type=str, default=None)
    parser.add_argument(
        "--provider",
        type=str,
        default="openai",
        choices=list(PROVIDER_IDS),
        help="Provider LLM da testare",
    )
    args = parser.parse_args()

    provider_id = args.provider.strip().lower()
    impl = get_provider(provider_id)
    ok, reason = impl.is_available()
    if not ok:
        print(f"Provider {provider_id} non disponibile: {reason}")
        return 1

    transcripts = _find_transcripts(args.jobs_dir, args.only)
    if not transcripts:
        print(f"Nessuna trascrizione in {args.jobs_dir}")
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out_dir or (DEFAULT_OUT / f"{ts}_{provider_id}")

    print(f"Provider: {provider_id} ({impl.default_model()})")
    print(f"Trovate {len(transcripts)} trascrizioni -> output: {out_dir}")
    rows: list[RunRow] = []

    try:
        for label, path in transcripts:
            print(f"\n=== {label} ===")
            for length in LENGTHS:
                tag = f"{length.value}"
                print(f"  {tag}...", end=" ", flush=True)
                row = _run_one(label, path, provider_id, length)
                rows.append(row)
                print(
                    f"{row.summary_words} parole ({row.compression_pct}%), "
                    f"{row.strategy}, {row.seconds}s"
                )
    finally:
        unload_summary_models()

    _write_report(out_dir, rows, provider_id)
    print(f"\nReport: {out_dir / 'REPORT.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
