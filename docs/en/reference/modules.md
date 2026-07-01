# Module reference

## `sbobinator.jobs`

Queue management and persistence.

| Function | Description |
|----------|-------------|
| `jobs_root()` | Job folder path |
| `db_path()` | `queue.db` path |
| `load_index()` | Job list (sorted by date) |
| `load_active_queue()` | Queued + running jobs |
| `get_job(id)` | Single job |
| `enqueue_job(...)` | New job + source copy |
| `update_job(job)` | Update record |
| `update_job_progress(...)` | Update progress |
| `claim_next_job()` | Takes next queued job (atomic) |
| `cancel_job(id)` | Cancel if queued |
| `requeue_job(id)` | Re-queue failed/cancelled |
| `requeue_failed()` | Retry all failed |
| `recover_orphaned_running_jobs()` | Crash recovery |
| `count_active_jobs()` | Active count |
| `is_source_in_active_queue(name)` | True if filename already queued/running |
| `find_active_jobs_by_source(name)` | List active jobs with same `source_name` |
| `delete_job(id)` | Delete record and folder (not if `running`) |
| `reprocess_job(id, ...)` | New job from already saved source file |
| `reconcile_jobs_with_disk()` | Align DB and filesystem; returns `ReconcileReport` |

### `JobRecord`

Main fields: `id`, `source_name`, `status`, `output_dir`, `progress_pct`, `summary_requested`, `summary_provider`, `summary_strategy`, `error`, timestamps.

Methods: `display_title()`, `folder_exists()`, `txt_path()`, `srt_path()`, `summary_path()`, `source_copy_path()`.

---

## `sbobinator.pipeline`

`run_pipeline(job_id: str)` — full orchestration for a single job.

---

## `sbobinator.transcribe`

| Function | Description |
|----------|-------------|
| `warmup_asr()` | Import NeMo (worker main thread) |
| `transcribe(path, config, work_dir, on_progress)` | ASR |
| `unload_model()` | Free model RAM |

---

## `sbobinator.summarize`

| Function | Description |
|----------|-------------|
| `summarize(text, provider, length)` | LLM summary |
| `unload_summary_models()` | Free local LLM |

Providers in `sbobinator.summarize_providers.*`.

---

## `sbobinator.worker`

| Function | Description |
|----------|-------------|
| `start_background_worker()` | Worker subprocess |
| `run_worker_forever()` | CLI loop |
| `is_worker_running()` | Worker state |
| `stop_background_worker()` | Stop worker |

---

## `sbobinator.export`

| Function | Description |
|----------|-------------|
| `export_txt(result, path)` | Save TXT |
| `export_srt(result, path)` | Save SRT |
| `export_summary_text(text, path)` | Save summary |
| `export_all(...)` | Multi-format legacy |

---

## `sbobinator.extract`

| Function | Description |
|----------|-------------|
| `prepare_audio(input, work_dir)` | ffmpeg → 16 kHz WAV |
| `get_duration_sec(path)` | Duration via ffprobe |
| `split_audio_chunks(...)` | Chunking for long files |

---

## `sbobinator.ui.launch`

`launch_ui(port=8501)` — starts uvicorn (FastAPI).
