# Sbobinator

**Audio and video → text** transcription in Italian, running locally with pre-trained [NVIDIA NeMo Parakeet](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3).

Includes a **FastAPI web UI** and optional **LLM summarization** (DeepSeek, OpenAI, Claude, Gemini, Kimi, or local Qwen).

📖 **Documentation:** [GitHub Pages](https://sbobinator.github.io/docs/) (EN + IT) — preview: `mkdocs serve` · publish: `scripts\publish_docs.bat` then `git push` in `sbobinator.github.io`

## Quick start (Windows, no Docker)

### 1. Install ffmpeg

```powershell
winget install Gyan.FFmpeg
```

### 2. Install Sbobinator (full dependencies)

```cmd
python scripts\install_local.py
```

Manual equivalent: `pip install -r requirements/local.txt`

### 3. Download the ASR model (once, ~2.5 GB)

```cmd
python scripts\download_model.py
```

### 4. Start the web UI

```cmd
start.bat
```

or `sbobina ui` → **http://localhost:8501**

### 5. Summary (optional)

| Engine | Setup |
|--------|--------|
| **Cloud** (DeepSeek, OpenAI, …) | [Summary settings](http://localhost:8501/settings/summary) → API key |
| **Local** (Qwen, offline) | `python scripts/download_summary_llm.py` + RAM ≥ 16 GB |

## Web UI

| Feature | Description |
|---------|-------------|
| Upload | Audio and video (MP4, MKV, WAV, MP3…) |
| Transcription | NeMo Parakeet v3, Italian |
| LLM summary | Opt-in, provider of your choice |
| Download | TXT, SRT, summary |
| Job history | `/jobs` list · `/jobs/{id}` detail page |

## CLI

```powershell
sbobina ui
sbobina transcribe video.mp4 -o data/output
sbobina transcribe audio.wav -s --summary-provider deepseek
sbobina info
```

## Dependencies (`pyproject.toml`)

| Extra | Use |
|-------|-----|
| `local` | **Full** — ASR + UI + LLM summary |
| `ui` | Web + cloud summary APIs |
| `summarize` | LLM modules only |
| `asr` | NeMo only |

See [`requirements/README.md`](requirements/README.md).

## Hardware requirements

Sbobinator runs on **Windows/Linux** (Python install) or **Linux with Docker** (e.g. mini PC). Resources depend on transcription only, cloud API summary, or local offline summary.

### Common prerequisites

| Resource | Required |
|----------|----------|
| **Python** | 3.12+ (native install; Docker includes Python) |
| **ffmpeg** | Required — extracts audio from video |
| **CPU** | Modern x64; **sequential** processing (one job at a time) |
| **NVIDIA GPU** | Optional — speeds up **ASR** only (CUDA). Local Qwen summary uses CPU |

### By scenario

| Scenario | System RAM | Free disk | Network | On-disk models |
|----------|------------|-----------|---------|----------------|
| **Transcription only** | **8 GB** min · **16 GB** recommended | **~6 GB** | First-time ASR download only | Parakeet ~2.5 GB |
| **Transcription + API summary** | Same as above | Same | **Yes** during summary (API calls) | Parakeet only |
| **Transcription + local summary** | **≥ 16 GB** · **32 GB** ideal for long files | **~8–10 GB** | First-time setup only | Parakeet + Qwen ~2 GB |

> **Note:** before local summary the pipeline **unloads the ASR model from RAM**. You need **≥ 16 GB total physical RAM** (enforced at startup).

See [docs/en/getting-started/hardware.md](docs/en/getting-started/hardware.md) for details.

### Docker (mini PC / deploy)

| Profile | Typical use | UI port |
|---------|-------------|---------|
| `cpu` | Mini PC without NVIDIA GPU | **8502** → 8501 in container |
| `gpu` | Server with NVIDIA CUDA | 8502 |

```bash
cd docker
docker compose --profile cpu build
docker compose --profile cpu up -d
```

UI at **http://localhost:8502**. See [docs/en/deployment/docker.md](docs/en/deployment/docker.md).

## Models

| Component | Value |
|-----------|--------|
| ASR | `nvidia/parakeet-tdt-0.6b-v3` |
| Summary | Multi-provider LLM (see settings) |

## Project layout

```
sbobinator/
├── requirements/          # pip aliases → pyproject.toml
├── start.bat
├── scripts/install_local.py
├── scripts/download_model.py
├── scripts/download_summary_llm.py
├── src/sbobinator/ui/     # FastAPI + HTMX
├── data/.secrets/         # summary API keys (gitignored)
└── models/                # ASR .nemo + optional Qwen GGUF
```

## License

**Proprietary software** — Copyright © 2024-2026 [Antonio Trento](https://antoniotrento.net).

| Use | Terms |
|-----|--------|
| **Personal / education / documented non-profit** | Free (see [LICENSE](LICENSE)) |
| **Business, government, professionals, commercial use** | **Paid license** — [antoniotrento.net](https://antoniotrento.net) |

Docs: [commercial licensing](https://sbobinator.github.io/docs/reference/commercial-license/) · in-app notice at `/settings/license`

NVIDIA, HuggingFace models and third-party libraries remain under their own licenses ([docs/en/reference/licenses.md](docs/en/reference/licenses.md)).

Italian summary: [LICENSE.it](LICENSE.it).
