# Job schema and database

## Job states

| State | Meaning |
|-------|---------|
| `queued` | Waiting in the worker |
| `running` | Processing in progress |
| `completed` | Transcription (and summary if requested) finished |
| `failed` | Irreversible pipeline error |
| `cancelled` | Cancelled by user (only from queued) |

## Phases (`phase`)

During `running`, the pipeline updates `phase` and `progress_pct`:

| Phase | Description |
|-------|-------------|
| `idle` | Initial |
| `extract` | Audio extraction from video |
| `transcribe` | NeMo ASR |
| `summarize` | Summary |
| `export` | Writing final files |
| `done` | Completed |

## SQLite table `jobs`

File: `data/output/jobs/queue.db`

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT PK | `YYYYMMDD_HHMMSS_stem` |
| `stem` | TEXT | Filename without extension |
| `source_name` | TEXT | Original filename |
| `created_at` | TEXT | ISO creation timestamp |
| `output_dir` | TEXT | Absolute job folder path |
| `input_path` | TEXT | Source copy path in job |
| `status` | TEXT | Current state |
| `phase` | TEXT | Pipeline phase |
| `progress_pct` | REAL | 0–100 |
| `progress_message` | TEXT | UI message |
| `queued_at` | TEXT | Enqueued |
| `started_at` | TEXT | Processing started |
| `finished_at` | TEXT | Finished (success or error) |
| `error` | TEXT | Pipeline error |
| `has_summary` | INTEGER | 1 if summary saved |
| `summary_requested` | INTEGER | 1 if requested |
| `summary_error` | TEXT | Summary-only error |
| `transcript_chars` | INTEGER | Text length |
| `model_name` | TEXT | NeMo model used |
| `device` | TEXT | cpu / cuda |
| `summary_mode` | TEXT | extractive / abstractive |
| `summary_length` | TEXT | auto / short / normal / detailed |

Indexes: `idx_jobs_status`, `idx_jobs_created`.

## Files per job

Folder: `data/output/jobs/YYYYMMDD_HHMMSS_stem/`

| File | Content |
|------|---------|
| `source.*` | Copy of uploaded file |
| `job.json` | JSON mirror of SQLite record |
| `trascrizione.txt` | Full text |
| `sottotitoli.srt` | Subtitles with timestamps |
| `riassunto.txt` | Summary (if generated) |
| `work/` | Temp files (WAV, chunks) — may remain |

## Job ID

Format: `{timestamp}_{stem_sanitized}`

Example: `20260628_143022_campione-italiano-lungo`

The `stem` is truncated and sanitized of unsafe filesystem characters.

## Migration

On startup, if the old `index.json` exists and `queue.db` is empty, records are imported automatically.
