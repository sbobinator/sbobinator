# Worker

Il worker elabora la coda job in modo **sequenziale** (FIFO).

## Avvio automatico (UI)

`app.py` → `_ensure_worker()` → `start_background_worker()`:

```text
python -m sbobinator.cli worker
```

- Un solo worker per volta (controllo `worker.pid`)
- Processo **daemon** separato da Streamlit
- `warmup_asr()` nel worker prima del loop (import NeMo nel main thread del worker)

## Avvio manuale

```cmd
sbobina worker
sbobina worker --interval 2.0
```

Utile per:

- Docker (un container = UI + worker subprocess, oppure solo `worker`)
- Debug headless
- Separare UI e elaborazione su macchine diverse (stesso `queue.db` su NFS — non ancora documentato/testato)

## Loop

```python
while True:
    job = claim_next_job()  # atomico SQLite
    if job is None:
        sleep(poll_interval)
        continue
    run_pipeline(job.id)
```

## Recupero crash

All'avvio, `recover_orphaned_running_jobs()` rimette in `queued` i job lasciati in `running` (crash, kill processo).

## File PID

`data/output/jobs/worker.pid` — PID del processo worker attivo.

`scripts/restart_ui.py` termina anche i worker e rimuove il PID file.

## Docker

Nell'immagine Docker, `sbobina ui` avvia comunque il worker subprocess. I modelli sono in `/models/` nell'immagine.

Per deploy solo worker (senza UI):

```yaml
command: worker
```

## Non fare

- Non avviare **più worker** sullo stesso `queue.db` (race su claim — mitigato da SQLite ma sconsigliato)
- Non usare thread in-process per NeMo dentro Streamlit
