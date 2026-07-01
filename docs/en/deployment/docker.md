# Docker

Containerized deploy on **Linux**. ASR model included in the build; local summary LLM **downloaded automatically** at startup if RAM ≥ 16 GB.

## Profiles

| Service | Profile | Base image |
|---------|---------|------------|
| `sbobinator-cpu` | `cpu` | python:3.12-slim |
| `sbobinator-gpu` | `gpu` | nvidia/cuda:12.6 |

## Build (~2.5 GB ASR model)

```bash
cd docker
docker compose --profile cpu build
```

During build:

1. `pip install -e ".[ui,summarize]"` — FastAPI, NeMo, LLM providers, `llama-cpp-python`
2. `download_model.py` → `/models/parakeet-tdt-0.6b-v3.nemo`

## Startup

```bash
docker compose --profile cpu up
```

At startup (`sbobina docker-ui`):

1. Checks container RAM (≥ 16 GB)
2. If OK and Qwen is missing → downloads ~2 GB from HuggingFace
3. Starts UI at **http://localhost:8502** (default compose mapping `8502:8501`)

**First startup with Qwen download:** may take 10–20 minutes (network). Logs show progress.

If RAM is insufficient: skips download; **cloud** summary remains available with an API key.

**No need** to run `docker exec ... download_summary_llm.py` manually anymore.

## Volumes

```yaml
volumes:
  - ../data:/data
  - sbobinator-qwen:/models/qwen2.5-3b-instruct
```

| Host / volume | Container | Purpose |
|---------------|-----------|---------|
| `./data/input/` | `/data/input/` | Source files |
| `./data/output/` | `/data/output/` | Jobs and results |
| `./data/.secrets/` | `/data/.secrets/` | Summary API keys |
| `sbobinator-qwen` (named) | `/models/qwen2.5-3b-instruct/` | Qwen GGUF (persists across restarts) |

## Environment variables

```yaml
environment:
  - NEMO_CACHE_DIR=/models
  - SBOBINATOR_DATA=/data
  - SBOBINATOR_UI_HOST=0.0.0.0
  # Cloud summary (optional):
  - SBOBINATOR_DEEPSEEK_API_KEY=sk-...
```

Or configure from the UI → saved in `/data/.secrets/summary_keys.json`.

## GPU

```bash
docker compose --profile gpu up
```

Requires [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

## Differences vs local Windows

| Aspect | Local | Docker (cpu profile) |
|--------|-------|----------------------|
| UI | `127.0.0.1:8501` | `localhost:8502` → container `8501` |
| ASR | `models/` in repo | `/models` in image |
| Cloud summary | API key in secrets | Same (volume `/data`) |
| Local Qwen | `download_summary_llm.py` | Auto on Docker startup if RAM ≥ 16 GB |
| API SSL | `truststore` (Windows) | Usually not needed (Linux) |

## Production

- Pre-build the image once
- Mount only `data/`
- Back up `data/output/jobs/`
- Healthcheck on `/partials/queue`
