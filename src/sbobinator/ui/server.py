"""Interfaccia web FastAPI per Sbobinator (sostituisce Streamlit)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sbobinator import __version__
from sbobinator.config import (
    DEFAULT_MODEL,
    TranscribeConfig,
    data_dir,
    local_summary_model_available,
)
from sbobinator.jobs import (
    ACTIVE_STATUSES,
    STATUS_CANCELLED,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_QUEUED,
    STATUS_RUNNING,
    JobRecord,
    cancel_job,
    count_active_jobs,
    ensure_db,
    enqueue_job,
    get_job,
    is_source_in_active_queue,
    jobs_root,
    load_active_queue,
    load_index,
)
from sbobinator.worker import is_worker_running, start_background_worker

UI_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(UI_DIR / "templates"))


def _dedupe_jobs(jobs: list[JobRecord]) -> list[JobRecord]:
    seen: set[str] = set()
    unique: list[JobRecord] = []
    for job in jobs:
        if job.id in seen:
            continue
        seen.add(job.id)
        unique.append(job)
    return unique


def _open_folder(path: Path) -> None:
    resolved = path.resolve()
    if sys.platform == "win32":
        os.startfile(resolved)  # noqa: S606
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(resolved)])  # noqa: S603
    else:
        subprocess.Popen(["xdg-open", str(resolved)])  # noqa: S603


def _summary_mode_label(mode: str) -> str:
    return "Riassunto (IT5)" if mode == "abstractive" else "Sintesi (estrativo)"


def _summary_length_label(length: str) -> str:
    return {
        "auto": "Automatica",
        "short": "Breve",
        "normal": "Normale",
        "detailed": "Dettagliato",
    }.get(length, length)


def _queue_context() -> dict:
    active = _dedupe_jobs(load_active_queue())
    queued = [j for j in active if j.status == STATUS_QUEUED]
    return {
        "active": active,
        "queued_count": len(queued),
        "jobs_root": jobs_root().resolve(),
    }


def _job_context(job: JobRecord) -> dict:
    summary_text = ""
    if job.summary_path().exists():
        summary_text = job.summary_path().read_text(encoding="utf-8")
    transcript_text = ""
    if job.txt_path().exists():
        transcript_text = job.txt_path().read_text(encoding="utf-8")
    return {
        "job": job,
        "summary_text": summary_text,
        "transcript_text": transcript_text,
        "word_count": len(transcript_text.split()) if transcript_text else 0,
    }


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_db()
    start_background_worker()
    yield


def _ensure_worker() -> None:
    ensure_db()
    if not is_worker_running():
        start_background_worker()


app = FastAPI(title="Sbobinator", version=__version__, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(UI_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, job: str = "", flash: str = "", flash_type: str = "success") -> HTMLResponse:
    _ensure_worker()
    jobs = load_index()
    selected_id = job or (jobs[0].id if jobs else "")
    selected = get_job(selected_id) if selected_id else None
    config = TranscribeConfig()
    abstractive_ok = local_summary_model_available()
    ctx: dict = {
        "version": __version__,
        "python_exe": sys.executable,
        "device": config.resolve_device().upper(),
        "jobs_count": len(jobs),
        "active_count": count_active_jobs(),
        "jobs": jobs,
        "selected_job": selected,
        "selected_id": selected_id,
        "jobs_root": jobs_root().resolve(),
        "data_dir": data_dir(),
        "default_model": DEFAULT_MODEL,
        "abstractive_ok": abstractive_ok,
        "flash": flash,
        "flash_type": flash_type,
        "status_queued": STATUS_QUEUED,
        "status_running": STATUS_RUNNING,
        "status_completed": STATUS_COMPLETED,
        "status_failed": STATUS_FAILED,
        "status_cancelled": STATUS_CANCELLED,
        "active_statuses": ACTIVE_STATUSES,
        "transcript_text": "",
        "summary_text": "",
        "word_count": 0,
    }
    if selected:
        ctx.update(_job_context(selected))
    return templates.TemplateResponse(request, "index.html", ctx)


@app.get("/partials/queue", response_class=HTMLResponse)
async def queue_partial(request: Request) -> HTMLResponse:
    _ensure_worker()
    return templates.TemplateResponse(
        request,
        "partials/queue.html",
        {
            "status_queued": STATUS_QUEUED,
            "status_running": STATUS_RUNNING,
            **_queue_context(),
        },
    )


@app.post("/api/jobs/{job_id}/cancel", response_class=HTMLResponse)
async def cancel_job_route(request: Request, job_id: str) -> HTMLResponse:
    cancel_job(job_id)
    return await queue_partial(request)


@app.post("/api/jobs/cancel-all-queued", response_class=HTMLResponse)
async def cancel_all_queued_route(request: Request) -> HTMLResponse:
    for job in load_active_queue():
        if job.status == STATUS_QUEUED:
            cancel_job(job.id)
    return await queue_partial(request)


@app.post("/api/open-folder/{job_id}")
async def open_folder_route(job_id: str) -> dict[str, bool]:
    job = get_job(job_id)
    if not job:
        return {"ok": False}
    _open_folder(job.path)
    return {"ok": True}


@app.get("/download/{job_id}/{kind}")
async def download_file(job_id: str, kind: str) -> FileResponse:
    job = get_job(job_id)
    if not job:
        raise ValueError("Job non trovato")
    mapping = {
        "txt": (job.txt_path(), f"{job.stem}.txt", "text/plain"),
        "srt": (job.srt_path(), f"{job.stem}.srt", "text/plain"),
        "summary": (job.summary_path(), f"{job.stem}_riassunto.txt", "text/plain"),
    }
    if kind not in mapping:
        raise ValueError("Tipo file non valido")
    path, name, mime = mapping[kind]
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")
    return FileResponse(path, filename=name, media_type=mime)


@app.post("/enqueue")
async def enqueue_files(
    request: Request,
    files: Annotated[list[UploadFile], File()],
    model_name: str = Form(DEFAULT_MODEL),
    device: str = Form("auto"),
    summary_enabled: str | None = Form(default=None),
    summary_mode: str = Form("extractive"),
    summary_length: str = Form("auto"),
) -> RedirectResponse:
    _ensure_worker()
    if not files:
        return RedirectResponse(url="/?flash=Nessun+file+selezionato&flash_type=warning", status_code=303)

    device_val = None if device == "auto" else device
    summary_on = summary_enabled == "true"
    if summary_mode == "abstractive" and not local_summary_model_available():
        summary_mode = "extractive"

    enqueued: list[str] = []
    skipped: list[str] = []
    work_dir = Path(tempfile.mkdtemp(prefix="sbobinator_ui_"))
    try:
        seen_names: set[str] = set()
        for uploaded in files:
            if not uploaded.filename:
                continue
            source_name = Path(uploaded.filename).name
            if source_name in seen_names:
                continue
            seen_names.add(source_name)
            if is_source_in_active_queue(source_name):
                skipped.append(source_name)
                continue
            stem = Path(source_name).stem
            tmp_path = work_dir / source_name
            content = await uploaded.read()
            tmp_path.write_bytes(content)
            job = enqueue_job(
                tmp_path,
                source_name,
                stem,
                summary_requested=summary_on,
                model_name=model_name,
                device=device_val,
                summary_mode=summary_mode,
                summary_length=summary_length,
            )
            enqueued.append(job.id)
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

    if enqueued:
        last = enqueued[-1]
        msg = (
            f"{len(enqueued)} file accodati"
            if len(enqueued) > 1
            else "1 file accodato"
        )
        if skipped:
            msg += f" · saltati: {', '.join(skipped)}"
        return RedirectResponse(url=f"/?job={last}&flash={msg}&flash_type=success", status_code=303)

    if skipped:
        return RedirectResponse(
            url=f"/?flash=Saltati+(gia+in+coda):+{','.join(skipped)}&flash_type=warning",
            status_code=303,
        )
    return RedirectResponse(url="/?flash=Nessun+file+valido&flash_type=warning", status_code=303)
