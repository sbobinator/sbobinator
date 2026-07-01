# Installation

## Prerequisites

### Python 3.12 or newer

```cmd
python --version
```

### ffmpeg (required)

Extracts audio from video and prepares files for NeMo.

**Windows:**

```cmd
winget install Gyan.FFmpeg
```

Verify:

```cmd
ffmpeg -version
ffprobe -version
```

### curl (for model downloads on Windows)

Included in Windows 10+. Scripts use `curl.exe` explicitly.

---

## Local installation (recommended on Windows)

From the repository root:

```cmd
python scripts\install_local.py
```

The script:

1. Creates `.venv/` if missing
2. Installs PyTorch (CPU)
3. Installs Sbobinator with `pip install -r requirements/local.txt` (NeMo, FastAPI, LLM summary)

### Optional dependencies (`pyproject.toml`)

| Extra | Packages | Use |
|-------|----------|-----|
| `asr` | torch, nemo_toolkit | Transcription only |
| `ui` | fastapi, uvicorn, jinja2, cloud LLM clients | Web UI + API summary |
| `summarize` | openai, anthropic, google-genai, llama-cpp-python | LLM summary modules |
| `local` | all of the above | Full installation |
| `dev` | ruff, mkdocs | Lint and docs |

---

## Manual installation

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux:   source .venv/bin/activate
pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[local]"
```

---

## Verify installation

```cmd
sbobina info
```

Should show version, default model, and detected device.

---

## What NOT to use

!!! warning "No PowerShell scripts"
    `.ps1` scripts have been removed (antivirus false positives). Use only:

    - `python scripts/*.py`
    - `start.bat`
    - `sbobina` CLI

---

## After installation

1. [Download models](models.md)
2. [Quick start](quickstart.md)
