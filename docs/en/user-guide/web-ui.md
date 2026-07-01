# Web interface

The interface is built with **FastAPI + HTMX** (`src/sbobinator/ui/server.py`), default port **8501** (Docker `cpu` profile: host **8502**).

## Starting

```cmd
sbobina ui
sbobina ui --port 9000
start.bat
python scripts\restart_ui.py
```

## Navigation

| Item | URL | Description |
|------|-----|-------------|
| Home | `/` | Upload, live queue |
| Queue & history | `/jobs` | Full list, filters, actions |
| Job detail | `/jobs/{id}` | Transcript, summary, downloads, actions |
| LLM summary | `/settings/summary` | API keys, engine status, Qwen download |
| License | `/settings/license` | Terms of use, documentation links, install acknowledgment |

---

## Home (`/`)

File upload, sidebar settings, active queue panel (HTMX every 2 s). After enqueuing, redirect to the new job's **`/jobs/{id}`**.

Sidebar: latest **8** jobs with links to the dedicated page.

---

## Queue & history (`/jobs`)

Table of all jobs with filters, search and quick actions. Click the **file name** or **Open** → `/jobs/{id}`.

---

## Job detail (`/jobs/{id}`)

Dedicated page to review a single job:

- Breadcrumb "Queue & history / file name"
- Job **in progress**: progress panel with HTMX polling (`/partials/job/{id}/status`), auto-reload on completion
- Job **completed**: transcript, summary, TXT/SRT/summary downloads
- Folder path, **Open folder**, reprocess, delete

---

## Summary settings (`/settings/summary`)

- Cloud provider API keys (DeepSeek, OpenAI, …)
- Engine availability status
- Download / path of the local Qwen model
- System RAM vs minimum threshold (16 GB for local)

---

## Background worker

When the UI starts, `start_background_worker()` launches a **separate process**:

```text
python -m sbobinator.cli worker
```

NeMo does **not** run in the uvicorn process (avoids `lightning.fabric` crashes).

PID saved in `data/output/jobs/worker.pid`.

At worker startup: `recover_orphaned_running_jobs()` + `reconcile_jobs_with_disk()`.

---

## HTTP API (main)

| Method | Path | Use |
|--------|------|-----|
| POST | `/enqueue` | Upload and enqueue |
| GET | `/partials/queue` | HTMX queue fragment |
| GET | `/partials/job/{id}/status` | Single job progress |
| GET | `/jobs/{id}` | Job detail page |
| POST | `/api/jobs/{id}/cancel` | Cancel (optional `return_to` param) |
| POST | `/api/jobs/{id}/delete` | Delete job and folder |
| POST | `/api/jobs/{id}/reprocess` | New processing |
| POST | `/api/jobs/{id}/requeue` | Requeue |
| POST | `/api/jobs/reconcile` | Sync DB ↔ disk |
| GET | `/download/{id}/{kind}` | Download txt / srt / summary |

---

## Tips

- Only one `restart_ui.py` at a time — avoid multiple instances on the same port
- After `clean_output.py`, reload the page (F5)
- First job after startup: 1–2 min to load Parakeet into RAM
- Same file multiple times → multiple folders: use `/jobs` and the labels with time/summary to tell them apart

See [Job queue and history](jobs-queue.md) for the full logic.
