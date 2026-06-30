# Docker

Deploy containerizzato su **Linux**. Modello ASR incluso nel build; riassunto LLM via API cloud.

## Profili

| Servizio | Profilo | Base image |
|----------|---------|------------|
| `sbobinator-cpu` | `cpu` | python:3.12-slim |
| `sbobinator-gpu` | `gpu` | nvidia/cuda:12.6 |

## Build (~2.5 GB modello ASR)

```bash
cd docker
docker compose --profile cpu build
```

Durante il build:

1. `pip install -e ".[ui,summarize]"` — FastAPI, NeMo, provider LLM, `truststore`, `llama-cpp-python`
2. `download_model.py` → `/models/parakeet-tdt-0.6b-v3.nemo`

**Non** include più IT5. Qwen GGUF opzionale a runtime.

## Avvio

```bash
docker compose --profile cpu up
```

UI: **http://localhost:8501**

## Volumi

```yaml
volumes:
  - ../data:/data
```

| Host | Container | Uso |
|------|-----------|-----|
| `./data/input/` | `/data/input/` | File sorgente |
| `./data/output/` | `/data/output/` | Job e risultati |
| `./data/.secrets/` | `/data/.secrets/` | API key riassunto |

## Variabili ambiente

```yaml
environment:
  - NEMO_CACHE_DIR=/models
  - SBOBINATOR_DATA=/data
  - SBOBINATOR_UI_HOST=0.0.0.0
  # Riassunto cloud (opzionale):
  - SBOBINATOR_DEEPSEEK_API_KEY=sk-...
```

Oppure configura da UI → salvato in `/data/.secrets/summary_keys.json`.

## GPU

```bash
docker compose --profile gpu up
```

Richiede [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

## Differenze vs locale Windows

| Aspetto | Locale | Docker |
|---------|--------|--------|
| UI | `127.0.0.1:8501` | `0.0.0.0:8501` |
| ASR | `models/` nel repo | `/models` in immagine |
| Riassunto cloud | API key in secrets | Stesso (volume `/data`) |
| Qwen locale | `download_summary_llm.py` | Opzionale nel container |
| SSL API | `truststore` (Windows) | Di solito non serve (Linux) |

## Produzione

- Pre-build immagine una volta
- Monta solo `data/`
- Backup `data/output/jobs/`
- Healthcheck su `/partials/queue`
