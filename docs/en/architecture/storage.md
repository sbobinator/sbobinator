# Storage and persistence

## Data layout

```
data/                          ← SBOBINATOR_DATA (default: project_root/data)
├── input/                     ← source files (manual or upload)
│   └── README.md
└── output/
    ├── jobs/
    │   ├── queue.db         ← SQLite WAL
    │   ├── worker.pid       ← active worker PID
    │   └── YYYYMMDD_HHMMSS_name/
    │       ├── source.wav
    │       ├── job.json
    │       ├── trascrizione.txt
    │       ├── sottotitoli.srt
    │       └── riassunto.txt
    └── benchmark_*.json/md    ← optional benchmark reports

models/                        ← NEMO_CACHE_DIR
├── parakeet-tdt-0.6b-v3.nemo
└── mt5-small/
    ├── config.json
    ├── model.safetensors
    └── spiece.model
```

## SQLite `queue.db`

- `jobs` table with all `JobRecord` fields
- WAL mode for concurrent reads (UI poll + worker writes)
- Automatic migration from legacy `index.json` (if present)

### What happens if...

| Action | UI list | Text files |
|--------|---------|------------|
| App restart | ✅ Persists | ✅ Persists |
| Delete job folder | ⚠️ Job in DB, files missing | ❌ |
| Delete only queue.db | ❌ Empty list | ✅ Files remain |
| `clean_output.py` | ❌ Empty | ❌ Everything removed |

## `job.json`

JSON copy of the SQLite record, synced on every update. Useful for manual inspection and backup; **the UI does not use it for the list**.

## Git

`.gitignore` excludes:

- `data/output/*` (except `.gitkeep`)
- `data/output/jobs/*` (except `.gitkeep`)
- `models/*` (except `.gitkeep`)
- `queue.db`

Results **must not** be committed to git.

For the full schema see [Job schema and database](../reference/job-schema.md).

## Docker volume

Only `../data:/data` is mounted from the host. Models are **in the image** (`/models`), not in the volume.
