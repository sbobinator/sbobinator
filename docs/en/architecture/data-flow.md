# Data flow

## Enqueueing (UI or CLI)

```mermaid
sequenceDiagram
    participant U as User
    participant UI as FastAPI
    participant J as jobs.py
    participant DB as queue.db

    U->>UI: Upload + Enqueue
    UI->>J: enqueue_job()
    J->>J: new_job_id()
    J->>J: copy source into job folder
    J->>DB: INSERT job queued
    UI->>U: Success message
```

## Processing

```mermaid
sequenceDiagram
    participant W as Worker
    participant J as jobs.py
    participant P as pipeline
    participant T as transcribe
    participant S as summarize

    W->>J: claim_next_job()
    J->>J: status = running
    W->>P: run_pipeline(job_id)
    P->>T: transcribe()
    T->>T: load Parakeet from models/
    P->>P: export TXT + SRT
    alt summary requested
        P->>S: summarize()
        P->>P: export riassunto.txt
    end
    P->>J: status = completed
```

## Reading results (UI)

1. `load_index()` → job list from SQLite
2. User selects job → `get_job(id)`
3. `job.txt_path().read_text()` → content from disk

The database **does not** store transcribed text — only metadata and paths.

## Path variables

| Variable | Local default | Docker |
|----------|---------------|--------|
| `SBOBINATOR_DATA` | `./data` | `/data` |
| `NEMO_CACHE_DIR` | `./models` | `/models` |

See [Configuration](../reference/configuration.md).
