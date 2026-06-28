"""Pipeline di elaborazione per un singolo job."""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path

from sbobinator.config import SummaryLength, SummaryMode, TranscribeConfig
from sbobinator.export import export_srt, export_summary_text, export_txt
from sbobinator.jobs import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    JobRecord,
    get_job,
    update_job,
    update_job_progress,
)
from sbobinator.summarize import summarize
from sbobinator.transcribe import transcribe, unload_model

logger = logging.getLogger(__name__)


def _progress(job_id: str, phase: str, pct: float, message: str) -> None:
    update_job_progress(
        job_id,
        phase=phase,
        progress_pct=min(100.0, max(0.0, pct)),
        progress_message=message,
    )


def run_pipeline(job_id: str) -> None:
    """Esegue trascrizione + export + riassunto opzionale per un job."""
    job = get_job(job_id)
    if not job:
        raise ValueError(f"Job {job_id} non trovato")

    input_path = Path(job.input_path) if job.input_path else job.source_copy_path()
    if not input_path.exists():
        raise FileNotFoundError(f"File sorgente non trovato: {input_path}")

    config = TranscribeConfig(model_name=job.model_name, device=job.device)
    work_dir = job.path / "work"
    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        _progress(job_id, "extract", 5, "Estrazione audio con ffmpeg...")
        _progress(job_id, "load_model", 12, "Caricamento modello NeMo (1–2 min al primo avvio)...")

        def on_progress(phase: str, pct: float, message: str) -> None:
            _progress(job_id, phase, pct, message)

        result = transcribe(input_path, config=config, work_dir=work_dir, on_progress=on_progress)

        _progress(job_id, "export", 85, "Salvataggio trascrizione e sottotitoli...")
        job = get_job(job_id)
        assert job is not None
        export_txt(result, job.txt_path())
        export_srt(result, job.srt_path())
        job.transcript_chars = len(result.text)

        if job.summary_requested and result.text.strip():
            _progress(job_id, "summarize", 90, "Generazione riassunto...")
            unload_model()
            try:
                summary = summarize(
                    result.text,
                    mode=SummaryMode(job.summary_mode),
                    length=SummaryLength(job.summary_length),
                )
                export_summary_text(summary.text, job.summary_path())
                job.has_summary = True
                job.summary_error = ""
            except Exception as exc:
                logger.exception("Riassunto fallito per job %s", job_id)
                job.has_summary = False
                job.summary_error = str(exc)

        job.status = STATUS_COMPLETED
        job.phase = "done"
        job.progress_pct = 100.0
        job.progress_message = "Completato"
        job.finished_at = datetime.now().isoformat(timespec="seconds")
        job.error = ""
        update_job(job)
        _progress(job_id, "done", 100, "Completato!")

    except Exception as exc:
        logger.exception("Pipeline fallita per job %s", job_id)
        job = get_job(job_id)
        if job:
            job.status = STATUS_FAILED
            job.phase = "failed"
            job.error = str(exc)
            job.progress_message = f"Errore: {exc}"
            job.finished_at = datetime.now().isoformat(timespec="seconds")
            update_job(job)
        raise
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
