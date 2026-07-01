# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

#!/usr/bin/env python3
"""
Monitor benchmark Sbobinator — tabella live + report finale.

Uso:
  python scripts/benchmark_monitor.py          # attende nuovi job, poi monitora
  python scripts/benchmark_monitor.py --watch    # monitora subito tutti i job attivi
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbobinator.config import TranscribeConfig, output_dir  # noqa: E402
from sbobinator.extract import get_duration_sec  # noqa: E402
from sbobinator.jobs import (  # noqa: E402
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_RUNNING,
    JobRecord,
    load_index,
)


@dataclass
class HardwareProfile:
    hostname: str
    os: str
    python: str
    cpu: str
    cpu_cores: int
    ram_gb: float
    device_asr: str
    cuda_available: bool
    captured_at: str


@dataclass
class JobMetrics:
    job_id: str
    file: str
    status: str
    audio_sec: float = 0.0
    file_mb: float = 0.0
    queue_wait_sec: float = 0.0
    process_sec: float = 0.0
    total_sec: float = 0.0
    rtf: float = 0.0  # process / audio (>1 = più lento del realtime)
    speed_x: float = 0.0  # audio / process (quante volte più veloce del realtime)
    transcript_chars: int = 0
    transcript_words: int = 0
    chars_per_audio_min: float = 0.0
    summary_mode: str = ""
    has_summary: bool = False
    summary_chars: int = 0
    model_name: str = ""
    device: str = ""
    phase: str = ""
    progress_pct: float = 0.0
    error: str = ""


@dataclass
class BenchmarkReport:
    hardware: HardwareProfile
    jobs: list[JobMetrics] = field(default_factory=list)
    wall_clock_sec: float = 0.0
    completed: int = 0
    failed: int = 0


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def _sec_between(a: str | None, b: str | None) -> float:
    ta, tb = _parse_ts(a), _parse_ts(b)
    if not ta or not tb:
        return 0.0
    return max(0.0, (tb - ta).total_seconds())


def _ram_gb() -> float:
    if sys.platform == "win32":
        try:
            out = subprocess.check_output(
                ["wmic", "computersystem", "get", "TotalPhysicalMemory", "/value"],
                text=True,
                errors="replace",
            )
            for line in out.splitlines():
                if line.startswith("TotalPhysicalMemory="):
                    return int(line.split("=", 1)[1]) / (1024**3)
        except (subprocess.CalledProcessError, ValueError, OSError):
            pass
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        total = os.sysconf("SC_PHYS_PAGES")
        return (page_size * total) / (1024**3)
    except (AttributeError, ValueError, OSError):
        return 0.0


def _cpu_name() -> str:
    if sys.platform == "win32":
        try:
            out = subprocess.check_output(
                ["wmic", "cpu", "get", "Name", "/value"],
                text=True,
                errors="replace",
            )
            for line in out.splitlines():
                if line.startswith("Name="):
                    return line.split("=", 1)[1].strip()
        except (subprocess.CalledProcessError, OSError):
            pass
    return platform.processor() or platform.machine()


def capture_hardware() -> HardwareProfile:
    cfg = TranscribeConfig()
    cuda = False
    try:
        import torch

        cuda = bool(torch.cuda.is_available())
    except ImportError:
        pass

    return HardwareProfile(
        hostname=platform.node(),
        os=f"{platform.system()} {platform.release()} ({platform.version()})",
        python=platform.python_version(),
        cpu=_cpu_name(),
        cpu_cores=os.cpu_count() or 0,
        ram_gb=round(_ram_gb(), 1),
        device_asr=cfg.resolve_device(),
        cuda_available=cuda,
        captured_at=datetime.now().isoformat(timespec="seconds"),
    )


def _source_path(job: JobRecord) -> Path | None:
    p = Path(job.input_path) if job.input_path else job.source_copy_path()
    return p if p.exists() else None


def _audio_duration(job: JobRecord, cache: dict[str, float]) -> float:
    if job.id in cache:
        return cache[job.id]
    src = _source_path(job)
    if not src:
        cache[job.id] = 0.0
        return 0.0
    try:
        cache[job.id] = get_duration_sec(src)
    except Exception:
        cache[job.id] = 0.0
    return cache[job.id]


def _fmt_duration(sec: float) -> str:
    if sec <= 0:
        return "—"
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def build_metrics(job: JobRecord, audio_cache: dict[str, float]) -> JobMetrics:
    audio = _audio_duration(job, audio_cache)
    src = _source_path(job)
    file_mb = round(src.stat().st_size / (1024 * 1024), 2) if src else 0.0

    queue_wait = _sec_between(job.queued_at, job.started_at)
    process = _sec_between(job.started_at, job.finished_at)
    total = _sec_between(job.queued_at, job.finished_at)

    if job.status == STATUS_RUNNING and job.started_at:
        now = datetime.now().isoformat(timespec="seconds")
        process = _sec_between(job.started_at, now)
        total = _sec_between(job.queued_at, now)

    rtf = round(process / audio, 2) if audio > 0 and process > 0 else 0.0
    speed = round(audio / process, 2) if process > 0 and audio > 0 else 0.0

    words = 0
    chars = job.transcript_chars
    txt = job.txt_path()
    if txt.exists():
        text = txt.read_text(encoding="utf-8")
        chars = len(text)
        words = len(text.split())

    summary_chars = 0
    if job.summary_path().exists():
        summary_chars = len(job.summary_path().read_text(encoding="utf-8"))

    chars_per_min = round(chars / (audio / 60), 0) if audio > 0 and chars else 0.0

    return JobMetrics(
        job_id=job.id,
        file=job.source_name,
        status=job.status,
        audio_sec=round(audio, 1),
        file_mb=file_mb,
        queue_wait_sec=round(queue_wait, 1),
        process_sec=round(process, 1),
        total_sec=round(total, 1),
        rtf=rtf,
        speed_x=speed,
        transcript_chars=chars,
        transcript_words=words,
        chars_per_audio_min=chars_per_min,
        summary_mode=job.summary_mode,
        has_summary=job.has_summary,
        summary_chars=summary_chars,
        model_name=job.model_name,
        device=job.device or "auto",
        phase=job.phase,
        progress_pct=job.progress_pct,
        error=job.error or "",
    )


def _print_hardware(hw: HardwareProfile) -> None:
    print("\n=== HARDWARE ===", flush=True)
    print(f"  CPU:     {hw.cpu} ({hw.cpu_cores} core)")
    print(f"  RAM:     {hw.ram_gb} GB")
    print(f"  OS:      {hw.os}")
    print(f"  Python:  {hw.python}")
    print(f"  ASR:     device={hw.device_asr}  cuda={hw.cuda_available}")


def _print_table(metrics: list[JobMetrics], *, live: bool = False) -> None:
    tag = "LIVE" if live else "FINALE"
    print(f"\n=== BENCHMARK {tag} ===")
    header = (
        f"{'File':<28} {'Audio':>7} {'Elab.':>7} {'Tot.':>7} "
        f"{'RTF':>5} {'Vel.':>6} {'Chars':>6} {'Riass.':>7} {'Stato':>10}"
    )
    print(header)
    print("-" * len(header))
    for m in metrics:
        riass = m.summary_mode[:7] if m.summary_mode else "—"
        if m.status == STATUS_RUNNING:
            stato = f"{int(m.progress_pct)}%"
        else:
            stato = m.status[:10]
        print(
            f"{m.file[:28]:<28} "
            f"{_fmt_duration(m.audio_sec):>7} "
            f"{_fmt_duration(m.process_sec):>7} "
            f"{_fmt_duration(m.total_sec):>7} "
            f"{m.rtf:>5.2f} "
            f"{m.speed_x:>5.2f}x "
            f"{m.transcript_chars:>6} "
            f"{riass:>7} "
            f"{stato:>10}"
        )
    print("\n  Audio = durata registrazione | Elab. = tempo elaborazione | Tot. = coda+elab.")
    print("  RTF = Elab./Audio (>1 più lento del realtime) | Vel. = Audio/Elab. (es. 0.5x = metà realtime)")


def _print_totals(metrics: list[JobMetrics], wall: float) -> None:
    done = [m for m in metrics if m.status == STATUS_COMPLETED]
    if not done:
        return
    tot_audio = sum(m.audio_sec for m in done)
    tot_proc = sum(m.process_sec for m in done)
    tot_chars = sum(m.transcript_chars for m in done)
    print("\n=== TOTALI (completati) ===")
    print(f"  Job completati:    {len(done)}")
    print(f"  Audio totale:      {_fmt_duration(tot_audio)} ({tot_audio:.0f} s)")
    print(f"  Elaborazione tot:  {_fmt_duration(tot_proc)} ({tot_proc:.0f} s)")
    print(f"  Wall clock run:    {_fmt_duration(wall)} ({wall:.0f} s)")
    if tot_proc > 0:
        print(f"  RTF medio:         {tot_proc / tot_audio:.2f}" if tot_audio else "")
        print(f"  Velocità media:    {tot_audio / tot_proc:.2f}x realtime" if tot_audio else "")
    print(f"  Caratteri totali:  {tot_chars:,}")


def save_report(report: BenchmarkReport) -> Path:
    out_dir = output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"benchmark_{ts}.json"
    path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# Benchmark Sbobinator — {ts}",
        "",
        "## Hardware",
        f"- CPU: {report.hardware.cpu} ({report.hardware.cpu_cores} core)",
        f"- RAM: {report.hardware.ram_gb} GB",
        f"- Device ASR: {report.hardware.device_asr}",
        "",
        "## Job",
        "",
        "| File | Audio | Elab. | Tot. | RTF | Vel. | Chars | Riassunto | Stato |",
        "|------|-------|-------|------|-----|------|-------|-----------|-------|",
    ]
    for m in report.jobs:
        lines.append(
            f"| {m.file} | {_fmt_duration(m.audio_sec)} | {_fmt_duration(m.process_sec)} | "
            f"{_fmt_duration(m.total_sec)} | {m.rtf} | {m.speed_x}x | {m.transcript_chars} | "
            f"{m.summary_mode} | {m.status} |"
        )
    md_path = out_dir / f"benchmark_{ts}.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return path


def wait_for_jobs(initial_count: int, timeout: float = 600.0) -> bool:
    """Attende che compaiano nuovi job rispetto a initial_count."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if len(load_index()) > initial_count:
            return True
        time.sleep(1)
    return False


def monitor(
  *,
    wait_new: bool,
    poll_sec: float = 3.0,
) -> BenchmarkReport:
    hw = capture_hardware()
    _print_hardware(hw)

    baseline = len(load_index())
    if wait_new:
        print(f"\nIn attesa che accodi i file (job attuali: {baseline})...", flush=True)
        print("Quando sei pronto: avvia i 4 file dal frontend.\n", flush=True)
        if not wait_for_jobs(baseline):
            print("Timeout: nessun nuovo job rilevato.")
            return BenchmarkReport(hardware=hw)

    start_wall = time.time()
    audio_cache: dict[str, float] = {}
    seen_ids: set[str] = set()
    last_print = 0.0

    print("Monitoraggio avviato. Ctrl+C per report parziale.\n")

    try:
        while True:
            jobs = load_index()
            metrics = [build_metrics(j, audio_cache) for j in jobs]
            new_ids = {j.id for j in jobs}
            if new_ids != seen_ids or time.time() - last_print >= poll_sec:
                # clear screen-ish: use ANSI or just reprint
                if metrics:
                    print("\033[2J\033[H", end="")  # clear terminal
                    _print_hardware(hw)
                    _print_table(metrics, live=True)
                    active = sum(1 for m in metrics if m.status in (STATUS_RUNNING, "queued"))
                    done = sum(1 for m in metrics if m.status == STATUS_COMPLETED)
                    fail = sum(1 for m in metrics if m.status == STATUS_FAILED)
                    print(f"\n  In corso/coda: {active} | Completati: {done} | Falliti: {fail}")
                seen_ids = new_ids
                last_print = time.time()

            if metrics and all(m.status in (STATUS_COMPLETED, STATUS_FAILED) for m in metrics):
                break
            time.sleep(poll_sec)
    except KeyboardInterrupt:
        print("\n\nInterrotto dall'utente — report parziale.")

    wall = time.time() - start_wall
    jobs = load_index()
    metrics = [build_metrics(j, audio_cache) for j in jobs]
    report = BenchmarkReport(
        hardware=hw,
        jobs=metrics,
        wall_clock_sec=round(wall, 1),
        completed=sum(1 for m in metrics if m.status == STATUS_COMPLETED),
        failed=sum(1 for m in metrics if m.status == STATUS_FAILED),
    )

    _print_table(metrics, live=False)
    _print_totals(metrics, wall)
    out = save_report(report)
    print(f"\nReport salvato: {out}")
    print(f"Markdown:       {out.with_suffix('.md')}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor benchmark Sbobinator")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Monitora subito (non attendere nuovi job)",
    )
    parser.add_argument("--poll", type=float, default=3.0, help="Intervallo aggiornamento (s)")
    args = parser.parse_args()
    monitor(wait_new=not args.watch, poll_sec=args.poll)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
