# Sbobinator

**Sbobinator** transcribes audio and video to text in Italian, locally, using the pre-trained [NVIDIA NeMo Parakeet TDT 0.6B v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) model.

!!! info "Bilingual documentation"
    This site is also available in **Italiano**. Use the language selector in the top navigation bar.

## What it does

| Feature | Description |
|---------|-------------|
| **Transcription** | Audio/video → text + SRT subtitles |
| **Job queue** | Multiple files processed one at a time; list at `/jobs`, detail at `/jobs/{id}` |
| **Summary** | Multi-provider LLM (DeepSeek, OpenAI, Qwen local, …) |
| **Web UI** | FastAPI + HTMX on port **8501** (native) or **8502** (Docker) |
| **CLI** | `sbobina` for automation and headless server |

## Design principles

1. **Local processing** — no audio is sent to the cloud during normal use.
2. **Offline models** — Parakeet (ASR) and optional Qwen GGUF in `models/`.
3. **No overwrites** — each job gets its own timestamped folder.
4. **Cross-platform** — native Python (development) and Docker on Linux (deployment).

## Hardware requirements

Requirements depend on your use case (transcription only, API summary, local summary). See the dedicated guide:

**[Hardware requirements](getting-started/hardware.md)** — RAM, disk, network, and GPU for each mode.

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| Python | 3.12+ | 3.12 or 3.13 |
| RAM (ASR only) | 8 GB | 16 GB |
| RAM (local Qwen) | 16 GB | 32 GB |
| Disk | 6 GB free | 10 GB |
| ffmpeg | Required | In PATH |
| NVIDIA GPU | Optional | CUDA for faster ASR |

## Quick start (Windows, Python)

```cmd
python scripts\install_local.py
python scripts\download_model.py
start.bat
```

Cloud summary: configure an API key at http://localhost:8501/settings/summary

Open **http://localhost:8501**, upload a file, click **Queue transcription**.

## Documentation

| Section | Content |
|---------|---------|
| [Getting started](getting-started/overview.md) | Installation and first steps |
| [User guide](user-guide/web-ui.md) | UI, CLI, queue, summaries |
| [Architecture](architecture/overview.md) | Components and data flow |
| [Deploy](deployment/docker.md) | Docker and environment variables |
| [Troubleshooting](troubleshooting/common-issues.md) | Common errors |
| [Reference](reference/faq.md) | FAQ, DB schema, glossary, licenses |

## Build documentation locally

```bash
pip install -r docs/requirements.txt
mkdocs serve
```

Site at http://127.0.0.1:8000 — publish: `scripts/publish_docs.bat` (or `python scripts/publish_docs.py`), then `git push` in the sibling repo `sbobinator.github.io`.

## License

**Proprietary software** — Copyright © 2024-2026 [Antonio Trento](https://antoniotrento.net). Free for personal use; commercial/enterprise use requires a paid license. See [`LICENSE`](../LICENSE) and [Licenses](reference/licenses.md).

NVIDIA and Hugging Face models have their own licenses.
