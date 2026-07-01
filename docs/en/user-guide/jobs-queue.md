# Job queue and history

## Two data layers

| Layer | File | Role |
|-------|------|------|
| **Registry** | `data/output/jobs/queue.db` | Job list, states, timestamps, paths |
| **Files** | `data/output/jobs/ID/` | Audio, transcript, SRT, summary |

The interface reads the **list** from the DB and the **content** from the files. At startup (UI and worker) a **synchronization** between DB and disk is run (`reconcile_jobs_with_disk()`).

---

## Interface: Home vs Queue & history

| Page | URL | Content |
|------|-----|---------|
| **Home** | `/` | Upload, active queue (polling), latest **8** jobs in the sidebar |
| **Queue & history** | `/jobs` | Full table, filters, search, per-job actions |
| **Job detail** | `/jobs/{id}` | Transcript, summary, downloads, live progress, actions |

The home sidebar shows readable labels, e.g. `campione.wav 12:17 · summary` or `· transcript only` (`JobRecord.display_title()`). Each item opens **`/jobs/{id}`**.

### Job detail (`/jobs/{id}`)

Dedicated page: breadcrumb, transcript, summary, downloads, actions. Job **in progress**: HTMX progress bar with automatic reload on completion. From the `/jobs` table: click the **file name** or **Open**.

---

## Job states

| State | Meaning |
|-------|---------|
| `queued` | In queue, waiting |
| `running` | Being processed |
| `completed` | Finished successfully |
| `failed` | Error (see `error` in job.json) |
| `cancelled` | Cancelled by the user (from queue only) |

---

## IDs and folders

Format: `YYYYMMDD_HHMMSS_file-name`

Example: `20260628_102554_campione-italiano-breve`

On collision within the same second: suffix `_2`, `_3`, ...

### Job folder content

```
20260628_102554_campione-italiano-breve/
├── source.wav           ← copy of the uploaded file
├── job.json             ← mirror of the SQLite record
├── trascrizione.txt
├── sottotitoli.srt
└── riassunto.txt        ← if requested and successful
```

---

## FIFO queue

1. Upload → `enqueue_job()` → state `queued`
2. Worker → `claim_next_job()` (atomic) → `running`
3. Pipeline → transcription + export + summary
4. End → `completed` or `failed`

One job at a time per worker.

---

## Duplicates and re-upload

| Situation | Behavior |
|-----------|----------|
| Same file name **in queue/running** | Skipped by default; flash message with the blocking job's ID |
| Same name + **"Enqueue anyway"** checkbox | New job enqueued even if one is active |
| Same file name **already completed** | **New** job, new folder, new DB row |
| Same content, different name | Treated as a new file |

**No overwrite** of previous jobs. Two runs of the same file (e.g. with and without summary) produce **two** distinct folders — this is normal; use `/jobs` to tell them apart.

---

## UI actions

Available in **`/jobs/{id}`** (and in the `/jobs` table for quick actions):

| Action | When | Effect |
|--------|------|--------|
| **Cancel** | `queued` only | State `cancelled` |
| **Retry** | `failed` / `cancelled` | `requeue_job()` — same job, same files |
| **Reprocess** | `completed` | `reprocess_job()` — **new** job (transcript only) |
| **+ Summary** | `completed` | `reprocess_job()` with summary enabled |
| **Delete** | Not `running` | Removes DB record and disk folder |
| **Sync disk** | Always | `reconcile_jobs_with_disk()` |

### DB ↔ disk synchronization

`reconcile_jobs_with_disk()`:

- **Removes** from the DB jobs whose folder no longer exists (e.g. manual deletion)
- **Imports** folders with a `job.json` but no SQLite record
- Marks as **failed** `running` jobs whose folder has been deleted

Run at UI/worker startup and on demand via **Sync disk** in `/jobs`.

---

## Application restart

- `queue.db` persists → the sidebar and `/jobs` still show the jobs
- The worker restarts and resumes `queued` jobs
- Orphaned `running` jobs → recovered into the queue at worker startup
- Reconcile aligns DB and folders after a crash or manual cleanup

---

## Clearing the history

```cmd
python scripts\clean_output.py
```

Removes job folders and `queue.db`. Does not touch `models/` or `data/input/`.

For single jobs, use **Delete** in `/jobs` instead of deleting the folders manually.

---

## Python module

Logic in `src/sbobinator/jobs.py`:

| Function | Description |
|----------|-------------|
| `load_index()` | All jobs (opt. `limit`, state filters) |
| `load_active_queue()` | queued + running |
| `get_job(id)` | Single job |
| `enqueue_job()` | New job |
| `find_active_jobs_by_source(name)` | Active jobs with the same file name |
| `is_source_in_active_queue(name)` | Boolean shortcut for queue duplicates |
| `requeue_job()` / `requeue_failed()` | Retry failed/cancelled |
| `reprocess_job()` | New processing from an already saved file |
| `delete_job()` | Delete DB + folder |
| `reconcile_jobs_with_disk()` | Align SQLite and filesystem |
| `cancel_job()` | Cancel if queued |

`JobRecord`: `display_title()`, `folder_exists()`, paths `txt_path()`, `srt_path()`, `summary_path()`.
