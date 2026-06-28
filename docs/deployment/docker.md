# Docker

Deploy containerizzato su **Linux** (immagine Debian/Ubuntu). Modelli inclusi nel build.

## Profili

| Servizio | Profilo | Base image |
|----------|---------|------------|
| `sbobinator-cpu` | `cpu` | python:3.12-slim |
| `sbobinator-gpu` | `gpu` | nvidia/cuda:12.6 |

## Build (include download modelli ~4 GB)

```bash
cd docker
docker compose --profile cpu build
```

Durante il build:

1. Installa dipendenze Python (`nemo`, `fastapi`, `uvicorn`, `transformers`, …)
2. Esegue `download_model.py` → `/models/parakeet-tdt-0.6b-v3.nemo`
3. Esegue `download_summary_model.py` → `/models/it5-small-news-summarization/`

Il build può richiedere **20–40 minuti** (rete + dimensione modelli).

## Avvio

```bash
docker compose --profile cpu up
```

UI **FastAPI** su **http://localhost:8501** (stesso comando `sbobina ui` dentro il container).

## Volumi

```yaml
volumes:
  - ../data:/data
```

| Host | Container | Uso |
|------|-----------|-----|
| `./data/input/` | `/data/input/` | Metti file da sbobinare |
| `./data/output/` | `/data/output/` | Prendi risultati |

**Non** si monta `models/` — i modelli sono nell'immagine.

## Variabili ambiente

```yaml
environment:
  - NEMO_CACHE_DIR=/models
  - SBOBINATOR_DATA=/data
  - SBOBINATOR_UI_HOST=0.0.0.0   # obbligatorio in container (porta esposta)
```

| Variabile | Default locale | Docker |
|-----------|----------------|--------|
| `SBOBINATOR_UI_HOST` | `127.0.0.1` | `0.0.0.0` |
| `SBOBINATOR_DATA` | `data/` nel repo | `/data` (volume) |

## GPU

```bash
docker compose --profile gpu up
```

Richiede [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

## Solo worker (headless)

```yaml
services:
  sbobinator-worker:
    ...
    command: worker
```

## Struttura file Docker

```
docker/
├── Dockerfile.cpu
├── Dockerfile.gpu
└── docker-compose.yml
```

Entry point: `sbobina ui` → `uvicorn sbobinator.ui.server:app` (non Streamlit).

## Differenze vs Python locale

| Aspetto | Locale Windows | Docker |
|---------|----------------|--------|
| UI | FastAPI su `127.0.0.1:8501` | FastAPI su `0.0.0.0:8501` |
| Modelli | `models/` nel repo | `/models` in immagine |
| Dati | `data/` nel repo | Volume `/data` |
| SSL download | curl.exe (Windows) | curl Linux al build |
| NeMo thread | Worker subprocess | Stesso pattern |

## Produzione

- Pre-build l'immagine una volta
- Monta solo `data/` dal host
- Backup di `data/output/jobs/` per storico
- Non serve entrare nel container per file input/output
- Healthcheck HTTP su `/partials/queue` (vedi `docker-compose.yml`)
