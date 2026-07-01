# Architecture overview

## Components

```
┌─────────────────────────────────────────────────────────────┐
│  FastAPI UI (server.py)         port 8501                   │
│  - upload, queue, results                                   │
│  - reads/writes queue.db                                    │
│  - starts worker subprocess                                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Worker (worker.py)           separate process              │
│  sbobina worker                                             │
│  - claim_next_job() loop                                    │
│  - run_pipeline()                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌──────────┐    ┌────────────┐   ┌───────────┐
    │ pipeline │    │ transcribe │   │ summarize │
    └──────────┘    │   + NeMo   │   │ LexRank / │
                    └────────────┘   │   LLM     │
                                     └───────────┘
                           │
                           ▼
                    ┌────────────┐
                    │ jobs.py    │
                    │ SQLite WAL │
                    └────────────┘
```

## Main modules

| Module | Responsibility |
|--------|----------------|
| `config.py` | Paths, models, device, summary enums |
| `jobs.py` | SQLite queue, `JobRecord`, CRUD |
| `worker.py` | Worker process, PID file |
| `pipeline.py` | Single-job orchestration |
| `transcribe.py` | NeMo ASR, chunking |
| `extract.py` | ffmpeg/ffprobe |
| `export.py` | TXT, SRT |
| `summarize.py` | Extractive / abstractive summary |
| `cli.py` | Typer CLI |
| `ui/server.py` | FastAPI web UI |
| `ui/launch.py` | Start uvicorn subprocess |

## Why a separate worker

NeMo/PyTorch/Lightning are **not** stable in a thread inside the FastAPI server on Windows. The worker runs in a **dedicated Python process** with a clean NeMo import.

## Version

**0.3.0** — SQLite queue, worker subprocess, human-readable folder IDs.

See also:

- [Data flow](data-flow.md)
- [Worker](worker.md)
- [Storage](storage.md)
