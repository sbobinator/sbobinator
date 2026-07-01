"""Worker coda job — elaborazione sequenziale in background."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

from sbobinator.config import project_root
from sbobinator.jobs import claim_next_job, jobs_root, recover_orphaned_running_jobs, reconcile_jobs_with_disk

logger = logging.getLogger(__name__)

_stop_event = threading.Event()
_worker_proc: subprocess.Popen[bytes] | None = None
_worker_lock = threading.Lock()


def _pid_path() -> Path:
    return jobs_root() / "worker.pid"


def _read_worker_pid() -> int | None:
    path = _pid_path()
    if not path.exists():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def _pid_running(pid: int) -> bool:
    if sys.platform == "win32":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True,
            text=True,
            check=False,
        )
        return str(pid) in result.stdout
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _write_worker_pid(pid: int) -> None:
    jobs_root().mkdir(parents=True, exist_ok=True)
    _pid_path().write_text(str(pid), encoding="utf-8")


def _clear_worker_pid() -> None:
    _pid_path().unlink(missing_ok=True)


def worker_loop(poll_interval: float = 1.0) -> None:
    """Loop principale: prende job dalla coda e li elabora uno alla volta."""
    from sbobinator.http_ssl import ensure_ssl
    from sbobinator.transcribe import warmup_asr

    ensure_ssl()
    warmup_asr()
    _write_worker_pid(os.getpid())
    recovered = recover_orphaned_running_jobs()
    if recovered:
        logger.info("Recuperati %d job orfani in coda: %s", len(recovered), ", ".join(recovered))
    report = reconcile_jobs_with_disk()
    if report.removed_missing or report.imported_orphans or report.failed_missing_folder:
        logger.info(
            "Reconcile disco: rimossi=%d importati=%d falliti=%d",
            len(report.removed_missing),
            len(report.imported_orphans),
            len(report.failed_missing_folder),
        )
    logger.info("Worker avviato (pid %s)", os.getpid())
    try:
        while not _stop_event.is_set():
            job = claim_next_job()
            if job is None:
                _stop_event.wait(poll_interval)
                continue
            logger.info("Elaborazione job %s (%s)", job.id, job.source_name)
            try:
                from sbobinator.pipeline import run_pipeline

                run_pipeline(job.id)
                logger.info("Job %s completato", job.id)
            except Exception:
                logger.exception("Job %s fallito", job.id)
    finally:
        _clear_worker_pid()
        logger.info("Worker fermato")


def start_background_worker() -> subprocess.Popen[bytes] | None:
    """Avvia un processo worker separato (Streamlit non può caricare NeMo in thread)."""
    global _worker_proc
    with _worker_lock:
        pid = _read_worker_pid()
        if pid and _pid_running(pid):
            return _worker_proc

        if _worker_proc is not None and _worker_proc.poll() is None:
            return _worker_proc

        cmd = [sys.executable, "-m", "sbobinator.cli", "worker"]
        logger.info("Avvio worker subprocess: %s", " ".join(cmd))
        _worker_proc = subprocess.Popen(
            cmd,
            cwd=str(project_root()),
        )
        time.sleep(1.0)
        if _worker_proc.poll() is not None:
            logger.error("Worker subprocess terminato subito (exit %s)", _worker_proc.returncode)
            _worker_proc = None
        return _worker_proc


def stop_background_worker() -> None:
    _stop_event.set()
    pid = _read_worker_pid()
    if pid and _pid_running(pid):
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False)


def is_worker_running() -> bool:
    pid = _read_worker_pid()
    if pid and _pid_running(pid):
        return True
    return _worker_proc is not None and _worker_proc.poll() is None


def run_worker_forever(poll_interval: float = 1.0) -> None:
    """Avvia il worker nel processo corrente (CLI `sbobina worker`)."""
    _stop_event.clear()
    try:
        worker_loop(poll_interval=poll_interval)
    except KeyboardInterrupt:
        logger.info("Interruzione worker")
        stop_background_worker()
