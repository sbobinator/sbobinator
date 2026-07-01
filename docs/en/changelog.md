# Changelog

## In development — License notice (UI + docs)

### Added

- **[Commercial licensing](reference/commercial-license.md)** pages (EN + IT) on GitHub Pages
- In-app **first-run license modal** (bilingual) with links to documentation
- **`/settings/license`** in the web UI
- `license_info.py` — acknowledgment in `data/.sbobinator_license_ack.json`

---

## In development — Proprietary license

### Changed

- License from MIT to **proprietary** (free personal use; paid commercial/enterprise use)
- Copyright **Antonio Trento** (antoniotrento.net) in all `.py` files
- `LICENSE`, `COPYRIGHT` files, `pyproject.toml` and documentation updates

---

## In development — Queue & UI history

### Added

- **`/jobs`** page — full history, filters, search, per-job actions
- **`/jobs/{id}`** page — dedicated detail (transcription, summary, downloads, actions)
- HTMX partial **`/partials/job/{id}/status`** — live progress and auto-reload on completion
- **`reconcile_jobs_with_disk()`** — SQLite ↔ folder sync (startup + UI button)
- **`delete_job()`**, **`reprocess_job()`** — delete and reprocess from the UI
- **«Queue anyway»** checkbox — bypass deduplication for the same filename in queue
- Job label **`display_title()`** — distinguishes same file with/without summary
- Unified nav: Home / Queue & history / LLM summary
- [Hardware requirements](getting-started/hardware.md) documentation

### Changed

- Home: sidebar with last **8** jobs (links to `/jobs/{id}`); upload and active queue
- After upload or reprocess: redirect to **`/jobs/{id}`** (no longer only `/?job=`)
- Flash messages for skipped files include the blocking job ID
- `cancel` accepts `return_to` for redirect from `/jobs`

### Fixed

- BUG-QUEUE-021…030 — confused queue, ghost DB entries, no delete/reprocess from UI
- FastAPI: `cancel` return type with `response_model=None`

---

## In development — Multi-provider LLM summary

### Added

- LLM summary: DeepSeek, OpenAI, Gemini, Claude, Kimi, local Qwen
- `/settings/summary` page for API keys and engine status
- `truststore` for cloud API SSL on Windows
- `requirements/` (pip aliases → `pyproject.toml`)
- `scripts/download_summary_llm.py`, `scripts/summary_benchmark.py --provider`
- `.env.example`

### Changed

- FastAPI UI (no longer Streamlit)
- Docker: ASR only in image, no IT5
- `pip install -r requirements/local.txt` in `install_local.py`

### Removed / deprecated

- LexRank and IT5 as product summary engines
- `transformers` / `sentencepiece` from dependencies
- `download_summary_model.py` (deprecated)

---

## 0.3.0 — Job queue and worker

### Added

- SQLite job queue (`queue.db`) with states queued/running/completed/failed/cancelled
- Worker in a **separate process** (not a Streamlit thread)
- Job folders `YYYYMMDD_HHMMSS_filename`
- CLI `sbobina jobs list|show|retry`
- CLI `sbobina worker`
- Scripts: `clean_output.py`, `restart_ui.py`, `benchmark_monitor.py`
- Offline mT5 download: `download_summary_model.py`
- `SBOBINATOR_DATA` variable for Docker
- Docker build with models included
- Full MkDocs documentation

### Changed

- `transcribe` CLI uses job registry (default)
- UI: queue panel, multi-file upload, auto worker
- mT5 summary only from local `models/mt5-small/`

### Fixed

- ImportError / lightning.fabric with NeMo in thread
- Duplicate Streamlit instances on port 8501
- Disabled queue button (uploader outside form)
- Windows SSL for mT5 (curl download, no runtime HF)

### Removed

- All PowerShell `.ps1` scripts

---

## 0.2.x — Web UI and summary

- Streamlit UI
- Extractive and mT5 summary
- TXT/SRT export

---

## 0.1.x — Basic CLI

- NeMo Parakeet transcription
- `sbobina transcribe`

---

For historical known bugs see `bug-fix/TRACCIAMENTO-BUG.md`.  
For future roadmap see `evolutive/ROADMAP-EVOLUTIVE.md`.
