# Utility scripts

All in `scripts/` — **pure Python**.

## `install_local.py`

Full local environment setup.

```cmd
python scripts\install_local.py
```

- Creates `.venv`
- PyTorch CPU
- `pip install -r requirements/local.txt` → `[local]` extra from `pyproject.toml`

---

## `download_model.py`

Downloads Parakeet ASR (~2.5 GB) to `models/` via curl.

```cmd
python scripts\download_model.py
```

---

## `download_summary_llm.py`

Downloads Qwen2.5 GGUF for **local** summary (~2 GB).

```cmd
python scripts\download_summary_llm.py
```

Requires `huggingface_hub` (in `[local]` / `[summarize]`).

---

## `download_summary_model.py` (deprecated)

IT5 news — **no longer used**. Use `download_summary_llm.py` or cloud APIs.

---

## `clean_output.py`

Clears `data/output/jobs/` (folders + `queue.db`).

```cmd
python scripts\clean_output.py
```

---

## `restart_ui.py`

Stops UI/worker on port 8501 and restarts FastAPI.

```cmd
python scripts\restart_ui.py
```

Used by `start.bat`.

---

## `summary_benchmark.py`

Benchmark summary LLMs on existing transcriptions.

```cmd
python scripts\summary_benchmark.py --provider deepseek
python scripts\summary_benchmark.py --provider local --only campione-italiano-lungo
```

---

## `benchmark_monitor.py`

Real-time job performance monitor.

---

## `generate_samples.py`

Italian audio samples from Wikimedia (testing).

---

## `start.bat`

Windows wrapper → `restart_ui.py`.

---

## `publish_docs.py` / `publish_docs.bat`

Publish documentation to **sbobinator.github.io** (Sbobinator-style — no GitHub Actions).

```cmd
scripts\publish_docs.bat
```

1. `mkdocs build` to a temp folder  
2. Copy output to `../sbobinator.github.io/docs/`  
3. `git commit` in the Pages repo  

Then manually:

```cmd
cd ..\sbobinator.github.io
git push
```

**One-time:** clone the Pages repo next to this project:

```cmd
cd ..
git clone https://github.com/sbobinator/sbobinator.github.io.git
```

Site: https://sbobinator.github.io/docs/

---

## Quick reference

| Script | When to use |
|--------|-------------|
| `install_local.py` | First install |
| `download_model.py` | Before first transcription |
| `download_summary_llm.py` | Local Qwen summary |
| `publish_docs.bat` | Publish docs to GitHub Pages |
| `clean_output.py` | Reset job history |
| `restart_ui.py` | Stuck UI / port in use |
| `summary_benchmark.py` | Evaluate summary LLM quality |
