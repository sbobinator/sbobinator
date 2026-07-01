# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""FastAPI web UI for Sbobinator (replaces Streamlit)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from urllib.parse import quote

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sbobinator import __version__
from sbobinator.config import (
    DEFAULT_MODEL,
    LOCAL_LLM_FOLDER,
    LOCAL_LLM_GGUF_FILE,
    MIN_RAM_GB,
    TranscribeConfig,
    data_dir,
    local_gguf_path,
    local_llm_available,
    local_llm_dir,
    models_dir,
    system_ram_gb,
)
from sbobinator.license_info import acknowledge_license, license_ui_context
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
    delete_job,
    ensure_db,
    enqueue_job,
    find_active_jobs_by_source,
    get_job,
    jobs_root,
    load_active_queue,
    load_index,
    reconcile_jobs_with_disk,
    reprocess_job,
    requeue_job,
)
from sbobinator.summary_config import (
    DEFAULT_MODELS,
    PROVIDER_ENV_KEYS,
    has_api_key,
    load_secrets,
    save_secrets,
    secrets_path,
)
from sbobinator.summarize_providers.registry import (
    PROVIDER_IDS,
    first_available_provider,
    get_provider,
    list_provider_capabilities,
    provider_label,
    test_provider_connection,
)
from sbobinator.worker import is_worker_running, start_background_worker
from sbobinator.http_ssl import ensure_ssl

UI_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(UI_DIR / "templates"))
templates.env.globals["provider_label"] = provider_label

CLOUD_PROVIDER_FIELDS = {
    "openai": "OpenAI",
    "gemini": "Google Gemini",
    "claude": "Anthropic Claude",
    "deepseek": "DeepSeek",
    "kimi": "Moonshot Kimi",
}


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


def _summary_context(*, preferred_provider: str = "") -> dict:
    providers = list_provider_capabilities()
    available_ids = [p["id"] for p in providers if p["available"]]
    default_provider = preferred_provider.strip().lower()
    if default_provider not in PROVIDER_IDS:
        default_provider = first_available_provider() or "deepseek"
    if default_provider not in PROVIDER_IDS:
        default_provider = "deepseek"

    ram = system_ram_gb()
    gguf = local_gguf_path()
    secrets = load_secrets()

    cloud_providers = []
    for pid, label in CLOUD_PROVIDER_FIELDS.items():
        cap = next((p for p in providers if p["id"] == pid), None)
        cloud_providers.append(
            {
                "id": pid,
                "label": label,
                "env_var": PROVIDER_ENV_KEYS[pid],
                "default_model": DEFAULT_MODELS[pid],
                "has_key": has_api_key(pid),
                "available": cap["available"] if cap else False,
                "reason": cap["reason"] if cap else "",
            }
        )

    local_cap = next((p for p in providers if p["id"] == "local"), None)

    return {
        "default_model": DEFAULT_MODEL,
        "summary_providers": providers,
        "default_summary_provider": default_provider,
        "available_provider_ids": available_ids,
        "configured_providers_count": len(available_ids),
        "system_ram_gb": round(ram, 1) if ram is not None else None,
        "min_ram_gb": MIN_RAM_GB,
        "local_gguf_path": gguf,
        "local_llm_ready": local_llm_available(),
        "local_llm_dir": local_llm_dir(),
        "local_llm_folder": LOCAL_LLM_FOLDER,
        "local_llm_gguf_file": LOCAL_LLM_GGUF_FILE,
        "models_dir": models_dir(),
        "secrets_path": secrets_path(),
        "cloud_providers": cloud_providers,
        "local_provider": local_cap,
        "saved_key_hints": {k: bool(v) for k, v in secrets.items() if k in CLOUD_PROVIDER_FIELDS},
    }


def _queue_context() -> dict:
    active = _dedupe_jobs(load_active_queue())
    queued = [j for j in active if j.status == STATUS_QUEUED]
    return {
        "active": active,
        "queued_count": len(queued),
        "jobs_root": jobs_root().resolve(),
    }


def _ui_shell_context(**extra: object) -> dict:
    """Shared template context: license URLs, acknowledgment, version."""
    return {
        "version": __version__,
        **license_ui_context(),
        **extra,
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


def _job_detail_template_context(
    job: JobRecord,
    *,
    nav_active: str = "jobs",
    flash: str = "",
    flash_type: str = "success",
    detail_standalone: bool = False,
    return_to: str | None = None,
) -> dict:
    job_return_to = return_to if return_to and return_to.startswith("/") else f"/jobs/{job.id}"
    return {
        "version": __version__,
        "jobs_root": jobs_root().resolve(),
        "selected_job": job,
        "detail_standalone": detail_standalone,
        "return_to": job_return_to,
        "flash": flash,
        "flash_type": flash_type,
        "nav_active": nav_active,
        "status_queued": STATUS_QUEUED,
        "status_running": STATUS_RUNNING,
        "status_completed": STATUS_COMPLETED,
        "status_failed": STATUS_FAILED,
        "status_cancelled": STATUS_CANCELLED,
        "active_statuses": ACTIVE_STATUSES,
        **_job_context(job),
        **_summary_context(),
        **license_ui_context(),
    }


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_ssl()
    ensure_db()
    reconcile_jobs_with_disk()
    start_background_worker()
    yield


def _ensure_worker() -> None:
    ensure_db()
    if not is_worker_running():
        start_background_worker()


app = FastAPI(title="Sbobinator", version=__version__, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(UI_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    job: str = "",
    provider: str = "",
    summary: str = "",
    flash: str = "",
    flash_type: str = "success",
) -> HTMLResponse:
    _ensure_worker()
    reconcile_jobs_with_disk()
    jobs = load_index(limit=8)
    selected_id = job or (jobs[0].id if jobs else "")
    selected = get_job(selected_id) if selected_id else None
    config = TranscribeConfig()
    ctx: dict = {
        "version": __version__,
        "python_exe": sys.executable,
        "device": config.resolve_device().upper(),
        "jobs_count": len(load_index()),
        "active_count": count_active_jobs(),
        "jobs": jobs,
        "selected_job": selected,
        "selected_id": selected_id,
        "jobs_root": jobs_root().resolve(),
        "data_dir": data_dir(),
        "default_model": DEFAULT_MODEL,
        "flash": flash,
        "flash_type": flash_type,
        "summary_checked": summary.strip().lower() in ("1", "true", "yes", "on"),
        "status_queued": STATUS_QUEUED,
        "status_running": STATUS_RUNNING,
        "status_completed": STATUS_COMPLETED,
        "status_failed": STATUS_FAILED,
        "status_cancelled": STATUS_CANCELLED,
        "active_statuses": ACTIVE_STATUSES,
        "nav_active": "home",
        "transcript_text": "",
        "summary_text": "",
        "word_count": 0,
        **_summary_context(preferred_provider=provider),
        **license_ui_context(),
    }
    if selected:
        ctx.update(_job_context(selected))
        ctx["return_to"] = f"/?job={selected.id}"
        ctx["detail_standalone"] = False
    return templates.TemplateResponse(request, "index.html", ctx)


@app.get("/jobs", response_class=HTMLResponse)
async def jobs_page(
    request: Request,
    filter: str = "all",
    q: str = "",
    flash: str = "",
    flash_type: str = "success",
) -> HTMLResponse:
    _ensure_worker()
    report = reconcile_jobs_with_disk()
    jobs = load_index()
    query = q.strip().lower()
    if query:
        jobs = [j for j in jobs if query in j.source_name.lower() or query in j.id.lower()]
    filt = filter.strip().lower()
    if filt == "active":
        jobs = [j for j in jobs if j.status in ACTIVE_STATUSES]
    elif filt == "completed":
        jobs = [j for j in jobs if j.status == STATUS_COMPLETED]
    elif filt == "failed":
        jobs = [j for j in jobs if j.status in {STATUS_FAILED, STATUS_CANCELLED}]
    elif filt == "no_summary":
        jobs = [j for j in jobs if j.status == STATUS_COMPLETED and j.summary_requested and not j.has_summary]

    return templates.TemplateResponse(
        request,
        "jobs.html",
        {
            "version": __version__,
            "jobs": jobs,
            "jobs_root": jobs_root().resolve(),
            "filter": filt or "all",
            "q": q,
            "flash": flash,
            "flash_type": flash_type,
            "reconcile_removed": len(report.removed_missing),
            "status_queued": STATUS_QUEUED,
            "status_running": STATUS_RUNNING,
            "status_completed": STATUS_COMPLETED,
            "status_failed": STATUS_FAILED,
            "status_cancelled": STATUS_CANCELLED,
            "active_statuses": ACTIVE_STATUSES,
            "nav_active": "jobs",
            **_summary_context(),
            **license_ui_context(),
        },
    )


@app.get("/jobs/{job_id}", response_class=HTMLResponse, response_model=None)
async def job_detail_page(
    request: Request,
    job_id: str,
    flash: str = "",
    flash_type: str = "success",
) -> HTMLResponse | RedirectResponse:
    _ensure_worker()
    job = get_job(job_id)
    if not job:
        return RedirectResponse(
            url="/jobs?flash=Job+non+trovato&flash_type=warning",
            status_code=303,
        )
    return templates.TemplateResponse(
        request,
        "job_detail_page.html",
        _job_detail_template_context(
            job,
            flash=flash,
            flash_type=flash_type,
            detail_standalone=True,
        ),
    )


@app.get("/partials/job/{job_id}/status", response_class=HTMLResponse)
async def job_status_partial(request: Request, job_id: str) -> HTMLResponse:
    job = get_job(job_id)
    if not job:
        return HTMLResponse("<p class='warning'>Job non trovato.</p>", status_code=404)
    return templates.TemplateResponse(
        request,
        "partials/job_status.html",
        {
            "job": job,
            "status_queued": STATUS_QUEUED,
            "status_running": STATUS_RUNNING,
            "active_statuses": ACTIVE_STATUSES,
        },
    )


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


@app.get("/settings/summary", response_class=HTMLResponse)
async def settings_summary(
    request: Request,
    flash: str = "",
    flash_type: str = "success",
    highlight: str = "",
) -> HTMLResponse:
    _ensure_worker()
    return templates.TemplateResponse(
        request,
        "settings_summary.html",
        {
            "version": __version__,
            "python_exe": sys.executable,
            "flash": flash,
            "flash_type": flash_type,
            "highlight_provider": highlight.strip().lower(),
            "jobs_root": jobs_root().resolve(),
            "nav_active": "summary",
            **_summary_context(),
            **license_ui_context(),
        },
    )


@app.get("/settings/license", response_class=HTMLResponse)
async def settings_license(
    request: Request,
    flash: str = "",
    flash_type: str = "success",
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "settings_license.html",
        _ui_shell_context(
            flash=flash,
            flash_type=flash_type,
            nav_active="license",
        ),
    )


@app.post("/api/license/acknowledge")
async def license_acknowledge_route(return_to: str = Form("/")) -> RedirectResponse:
    acknowledge_license(app_version=__version__)
    dest = return_to if return_to.startswith("/") else "/"
    sep = "&" if "?" in dest else "?"
    return RedirectResponse(
        url=f"{dest}{sep}flash={quote('License accepted')}&flash_type=success",
        status_code=303,
    )


@app.post("/api/jobs/{job_id}/cancel", response_model=None)
async def cancel_job_route(
    request: Request,
    job_id: str,
    return_to: str = Form(""),
) -> HTMLResponse | RedirectResponse:
    cancel_job(job_id)
    if return_to.startswith("/"):
        return RedirectResponse(
            url=f"{return_to}?flash={quote('Job annullato')}&flash_type=success",
            status_code=303,
        )
    return await queue_partial(request)


@app.post("/api/jobs/cancel-all-queued", response_class=HTMLResponse)
async def cancel_all_queued_route(request: Request) -> HTMLResponse:
    for job in load_active_queue():
        if job.status == STATUS_QUEUED:
            cancel_job(job.id)
    return await queue_partial(request)


@app.post("/api/jobs/{job_id}/delete")
async def delete_job_route(
    job_id: str,
    return_to: str = Form("/jobs"),
) -> RedirectResponse:
    ok, err = delete_job(job_id)
    dest = return_to if return_to.startswith("/") else "/jobs"
    if ok:
        flash = quote("Job eliminato")
        flash_type = "success"
    else:
        flash = quote(err or "Eliminazione fallita")
        flash_type = "warning"
    sep = "&" if "?" in dest else "?"
    return RedirectResponse(url=f"{dest}{sep}flash={flash}&flash_type={flash_type}", status_code=303)


@app.post("/api/jobs/{job_id}/reprocess")
async def reprocess_job_route(
    job_id: str,
    model_name: str = Form(DEFAULT_MODEL),
    device: str = Form("auto"),
    summary_enabled: str | None = Form(default=None),
    summary_provider: str = Form("deepseek"),
    summary_length: str = Form("auto"),
    return_to: str = Form("/jobs"),
) -> RedirectResponse:
    _ensure_worker()
    device_val = None if device == "auto" else device
    summary_on = summary_enabled == "true"
    provider_id = summary_provider.strip().lower()
    dest = return_to if return_to.startswith("/") else "/jobs"

    if summary_on:
        if provider_id not in PROVIDER_IDS:
            return RedirectResponse(
                url=f"{dest}?flash=Provider+non+valido&flash_type=warning",
                status_code=303,
            )
        impl = get_provider(provider_id)
        available, reason = impl.is_available()
        if not available:
            return RedirectResponse(
                url=f"/settings/summary?flash={quote(reason)}&flash_type=warning&highlight={provider_id}",
                status_code=303,
            )

    try:
        new_job = reprocess_job(
            job_id,
            summary_requested=summary_on,
            model_name=model_name,
            device=device_val,
            summary_provider=provider_id if summary_on else "",
            summary_length=summary_length,
        )
    except (ValueError, FileNotFoundError) as exc:
        return RedirectResponse(
            url=f"{dest}?flash={quote(str(exc))}&flash_type=warning",
            status_code=303,
        )

    msg = "Nuova elaborazione accodata"
    if summary_on:
        msg += f" · con riassunto ({provider_label(provider_id)})"
    return RedirectResponse(
        url=f"/jobs/{new_job.id}?flash={quote(msg)}&flash_type=success",
        status_code=303,
    )


@app.post("/api/jobs/{job_id}/requeue")
async def requeue_job_route(
    job_id: str,
    return_to: str = Form("/jobs"),
) -> RedirectResponse:
    dest = return_to if return_to.startswith("/") else "/jobs"
    if requeue_job(job_id):
        sep = "&" if "?" in dest else "?"
        return RedirectResponse(
            url=f"{dest}{sep}flash={quote('Job rimesso in coda')}&flash_type=success",
            status_code=303,
        )
    sep = "&" if "?" in dest else "?"
    return RedirectResponse(
        url=f"{dest}{sep}flash={quote('Impossibile rimettere in coda')}&flash_type=warning",
        status_code=303,
    )


@app.post("/api/jobs/reconcile")
async def reconcile_route() -> RedirectResponse:
    report = reconcile_jobs_with_disk()
    parts: list[str] = []
    if report.removed_missing:
        parts.append(f"{len(report.removed_missing)} record fantasma rimossi")
    if report.imported_orphans:
        parts.append(f"{len(report.imported_orphans)} cartelle importate")
    if report.failed_missing_folder:
        parts.append(f"{len(report.failed_missing_folder)} job segnati falliti (cartella assente)")
    msg = " · ".join(parts) if parts else "Nessuna differenza tra disco e database"
    return RedirectResponse(
        url=f"/jobs?flash={quote(msg)}&flash_type=success",
        status_code=303,
    )


@app.post("/api/open-folder/{job_id}")
async def open_folder_route(job_id: str) -> dict[str, bool]:
    job = get_job(job_id)
    if not job:
        return {"ok": False}
    _open_folder(job.path)
    return {"ok": True}


@app.post("/api/settings/summary-keys")
async def save_summary_keys_route(
    openai_key: str = Form(""),
    gemini_key: str = Form(""),
    claude_key: str = Form(""),
    deepseek_key: str = Form(""),
    kimi_key: str = Form(""),
) -> RedirectResponse:
    updates: dict[str, str] = {}
    for provider, value in (
        ("openai", openai_key),
        ("gemini", gemini_key),
        ("claude", claude_key),
        ("deepseek", deepseek_key),
        ("kimi", kimi_key),
    ):
        cleaned = value.strip()
        if cleaned:
            updates[provider] = cleaned
    if updates:
        save_secrets(updates)
    return RedirectResponse(
        url="/settings/summary?flash=API+key+salvate&flash_type=success",
        status_code=303,
    )


@app.post("/api/settings/test-provider/{provider_id}")
async def test_provider_route(
    provider_id: str,
    api_key: str = Form(""),
) -> JSONResponse:
    if provider_id not in PROVIDER_IDS:
        return JSONResponse({"ok": False, "message": "Provider sconosciuto"}, status_code=400)
    ok, message = test_provider_connection(
        provider_id,
        api_key=api_key.strip() or None,
    )
    return JSONResponse({"ok": ok, "message": message})


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
    summary_provider: str = Form("deepseek"),
    summary_length: str = Form("auto"),
    allow_duplicate: str | None = Form(default=None),
) -> RedirectResponse:
    _ensure_worker()
    if not files:
        return RedirectResponse(url="/?flash=Nessun+file+selezionato&flash_type=warning", status_code=303)

    device_val = None if device == "auto" else device
    summary_on = summary_enabled == "true"
    provider_id = summary_provider.strip().lower()

    if summary_on:
        if provider_id not in PROVIDER_IDS:
            return RedirectResponse(
                url="/?flash=Provider+riassunto+non+valido&flash_type=warning",
                status_code=303,
            )
        impl = get_provider(provider_id)
        available, reason = impl.is_available()
        if not available:
            flash = quote(f"Configura {provider_label(provider_id)}: {reason}")
            return RedirectResponse(
                url=f"/settings/summary?flash={flash}&flash_type=warning&highlight={provider_id}",
                status_code=303,
            )

    enqueued: list[str] = []
    skipped: list[str] = []
    allow_dup = allow_duplicate == "true"
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
            blocking = find_active_jobs_by_source(source_name)
            if blocking and not allow_dup:
                blocker = blocking[0]
                skipped.append(f"{source_name} (attivo: {blocker.id})")
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
                summary_provider=provider_id if summary_on else "",
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
        if summary_on:
            msg += f" · con riassunto ({provider_label(provider_id)})"
        else:
            msg += " · solo trascrizione"
        if skipped:
            msg += f" · saltati: {', '.join(skipped)}"
        summary_q = "summary=1" if summary_on else "summary=0"
        return RedirectResponse(
            url=(
                f"/jobs/{last}?{summary_q}"
                f"&flash={quote(msg)}&flash_type=success"
            ),
            status_code=303,
        )

    if skipped:
        return RedirectResponse(
            url=(
                f"/?flash={quote('Saltati (file già in coda — spunta Accoda comunque o annulla il job attivo): ' + '; '.join(skipped))}"
                f"&flash_type=warning"
            ),
            status_code=303,
        )
    return RedirectResponse(url="/?flash=Nessun+file+valido&flash_type=warning", status_code=303)
