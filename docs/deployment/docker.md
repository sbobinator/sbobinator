# Docker

Deploy containerizzato su **Linux**. Modello ASR incluso nel build; riassunto LLM locale **scaricato automaticamente** all'avvio se RAM ≥ 16 GB.

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

1. `pip install -e ".[ui,summarize]"` — FastAPI, NeMo, provider LLM, `llama-cpp-python`
2. `download_model.py` → `/models/parakeet-tdt-0.6b-v3.nemo`

## Avvio

```bash
docker compose --profile cpu up
```

All'avvio (`sbobina docker-ui`):

1. Controlla RAM nel container (≥ 16 GB)
2. Se ok e Qwen assente → scarica ~2 GB da HuggingFace
3. Avvia UI su **http://localhost:8502** (mapping `8502:8501` nel compose predefinito)

**Primo avvio con download Qwen:** può richiedere 10–20 minuti (rete). I log mostrano il progresso.

Se RAM insufficiente: salta il download, riassunto **cloud** resta disponibile con API key.

**Non serve** più `docker exec ... download_summary_llm.py` manualmente.

## Volumi

```yaml
volumes:
  - ../data:/data
  - sbobinator-qwen:/models/qwen2.5-3b-instruct
```

| Host / volume | Container | Uso |
|---------------|-----------|-----|
| `./data/input/` | `/data/input/` | File sorgente |
| `./data/output/` | `/data/output/` | Job e risultati |
| `./data/.secrets/` | `/data/.secrets/` | API key riassunto |
| `sbobinator-qwen` (named) | `/models/qwen2.5-3b-instruct/` | Qwen GGUF (persiste tra restart) |

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

| Aspetto | Locale | Docker (profilo cpu) |
|---------|--------|----------------------|
| UI | `127.0.0.1:8501` | `localhost:8502` → container `8501` |
| ASR | `models/` nel repo | `/models` in immagine |
| Riassunto cloud | API key in secrets | Stesso (volume `/data`) |
| Qwen locale | `download_summary_llm.py` | Auto all'avvio Docker se RAM ≥ 16 GB |
| SSL API | `truststore` (Windows) | Di solito non serve (Linux) |

## Produzione

- Pre-build immagine una volta
- Monta solo `data/`
- Backup `data/output/jobs/`
- Healthcheck su `/partials/queue`
