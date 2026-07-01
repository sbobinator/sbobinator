# Worker

The worker processes the job queue **sequentially** (FIFO).

## Automatic startup (UI)

`server.py` (lifespan + `_ensure_worker()`) → `start_background_worker()`:

```text
python -m sbobinator.cli worker
```

- Only one worker at a time (`worker.pid` check)
- **Daemon** process separate from uvicorn/FastAPI
- `warmup_asr()` in the worker before the loop (NeMo import on the worker main thread)

## Manual startup

```cmd
sbobina worker
sbobina worker --interval 2.0
```

Useful for:

- Docker (one container = UI + worker subprocess, or `worker` only)
- Headless debugging
- Splitting UI and processing across machines (same `queue.db` on NFS — not yet documented/tested)

## Loop

```python
while True:
    job = claim_next_job()  # atomic SQLite
    if job is None:
        sleep(poll_interval)
        continue
    run_pipeline(job.id)
```

## Crash recovery and disk sync

On worker startup:

1. **`recover_orphaned_running_jobs()`** — resets jobs left in `running` back to `queued`
2. **`reconcile_jobs_with_disk()`** — aligns `queue.db` with folders on disk

The UI runs the same reconcile in its lifespan and when opening `/` and `/jobs`.

## PID file

`data/output/jobs/worker.pid` — PID of the active worker process.

`scripts/restart_ui.py` also stops workers and removes the PID file.

## Docker

In the Docker image, `sbobina docker-ui` starts the UI plus a worker subprocess. ASR models live in `/models/` in the image.

For worker-only deploy (no UI):

```yaml
command: worker
```

## Do not

- Do not start **multiple workers** on the same `queue.db` (claim races — mitigated by SQLite but discouraged)
- Do not use in-process threads for NeMo inside the web server
