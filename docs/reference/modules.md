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
| `is_source_in_active_queue(name)` | Evita duplicati in coda |

### `JobRecord`

Campi principali: `id`, `source_name`, `status`, `output_dir`, `progress_pct`, `summary_mode`, `error`, timestamp.

Metodi path: `txt_path()`, `srt_path()`, `summary_path()`, `source_copy_path()`.

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
| `summarize(text, mode, length)` | Riassunto |
| `summarize_extractive(text, n)` | Solo estrattivo |
| `unload_abstractive_model()` | Libera mT5 |

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

`launch_ui(port=8501)` — avvia Streamlit subprocess.
