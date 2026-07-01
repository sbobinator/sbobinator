# Panoramica architettura

## Componenti

```
┌─────────────────────────────────────────────────────────────┐
│  Streamlit UI (app.py)          porta 8501                  │
│  - upload, coda, risultati                                  │
│  - legge/scrive queue.db                                    │
│  - avvia worker subprocess                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Worker (worker.py)           processo separato             │
│  sbobina worker                                               │
│  - claim_next_job() loop                                      │
│  - run_pipeline()                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌──────────┐    ┌────────────┐   ┌───────────┐
    │ pipeline │    │ transcribe │   │ summarize │
    └──────────┘    │   + NeMo   │   │ LexRank/  │
                    └────────────┘   │   mT5     │
                                     └───────────┘
                           │
                           ▼
                    ┌────────────┐
                    │ jobs.py    │
                    │ SQLite WAL │
                    └────────────┘
```

## Moduli principali

| Modulo | Responsabilità |
|--------|----------------|
| `config.py` | Path, modelli, device, enum riassunto |
| `jobs.py` | Coda SQLite, `JobRecord`, CRUD |
| `worker.py` | Processo worker, PID file |
| `pipeline.py` | Orchestrazione singolo job |
| `transcribe.py` | NeMo ASR, chunking |
| `extract.py` | ffmpeg/ffprobe |
| `export.py` | TXT, SRT |
| `summarize.py` | Riassunto estrattivo/astrattivo |
| `cli.py` | Typer CLI |
| `ui/app.py` | Streamlit |
| `ui/launch.py` | Avvio Streamlit subprocess |

## Perché worker separato

NeMo/PyTorch/Lightning **non** sono stabili in un thread dentro Streamlit su Windows. Il worker gira in un **processo Python dedicato** con import pulito di NeMo.

## Versione

**0.3.0** — coda SQLite, worker subprocess, ID cartelle leggibili.

Vedi anche:

- [Flusso dati](data-flow.md)
- [Worker](worker.md)
- [Storage](storage.md)
