# Riferimento moduli

## `sbobinator.jobs`

Gestione coda e persistenza.

| Funzione | Descrizione |
|----------|-------------|
| `jobs_root()` | Path cartella job |
| `db_path()` | Path `queue.db` |
| `load_index()` | Lista job (ordinati per data) |
| `load_active_queue()` | Job queued + running |
| `get_job(id)` | Singolo job |
| `enqueue_job(...)` | Nuovo job + copia sorgente |
| `update_job(job)` | Aggiorna record |
| `update_job_progress(...)` | Aggiorna progresso |
| `claim_next_job()` | Prende prossimo queued (atomico) |
| `cancel_job(id)` | Annulla se queued |
| `requeue_job(id)` | Rimette in coda failed/cancelled |
| `requeue_failed()` | Ritenta tutti i falliti |
| `recover_orphaned_running_jobs()` | Recovery crash |
| `count_active_jobs()` | Conteggio attivi |
| `is_source_in_active_queue(name)` | True se nome file già in coda/running |
| `find_active_jobs_by_source(name)` | Lista job attivi con stesso `source_name` |
| `delete_job(id)` | Elimina record e cartella (non se `running`) |
| `reprocess_job(id, ...)` | Nuovo job da file sorgente già salvato |
| `reconcile_jobs_with_disk()` | Allinea DB e filesystem; ritorna `ReconcileReport` |

### `JobRecord`

Campi principali: `id`, `source_name`, `status`, `output_dir`, `progress_pct`, `summary_requested`, `summary_provider`, `summary_strategy`, `error`, timestamp.

Metodi: `display_title()`, `folder_exists()`, `txt_path()`, `srt_path()`, `summary_path()`, `source_copy_path()`.

---

## `sbobinator.pipeline`

`run_pipeline(job_id: str)` — orchestrazione completa singolo job.

---

## `sbobinator.transcribe`

| Funzione | Descrizione |
|----------|-------------|
| `warmup_asr()` | Import NeMo (main thread worker) |
| `transcribe(path, config, work_dir, on_progress)` | ASR |
| `unload_model()` | Libera RAM modello |

---

## `sbobinator.summarize`

| Funzione | Descrizione |
|----------|-------------|
| `summarize(text, provider, length)` | Riassunto LLM |
| `unload_summary_models()` | Libera LLM locale |

Provider in `sbobinator.summarize_providers.*`.

---

## `sbobinator.worker`

| Funzione | Descrizione |
|----------|-------------|
| `start_background_worker()` | Subprocess worker |
| `run_worker_forever()` | Loop CLI |
| `is_worker_running()` | Stato worker |
| `stop_background_worker()` | Termina worker |

---

## `sbobinator.export`

| Funzione | Descrizione |
|----------|-------------|
| `export_txt(result, path)` | Salva TXT |
| `export_srt(result, path)` | Salva SRT |
| `export_summary_text(text, path)` | Salva riassunto |
| `export_all(...)` | Multi-formato legacy |

---

## `sbobinator.extract`

| Funzione | Descrizione |
|----------|-------------|
| `prepare_audio(input, work_dir)` | ffmpeg → WAV 16kHz |
| `get_duration_sec(path)` | Durata ffprobe |
| `split_audio_chunks(...)` | Chunking file lunghi |

---

## `sbobinator.ui.launch`

`launch_ui(port=8501)` — avvia uvicorn (FastAPI).
