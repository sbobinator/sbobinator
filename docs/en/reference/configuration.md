# Configuration

Module: `src/sbobinator/config.py`  
Summary API keys: `src/sbobinator/summary_config.py`

## ASR constants

| Name | Value | Description |
|------|-------|-------------|
| `DEFAULT_MODEL` | `nvidia/parakeet-tdt-0.6b-v3` | ASR model |
| `SAMPLE_RATE` | 16000 | Hz for NeMo |
| `CHUNK_THRESHOLD_SEC` | 1800 (30 min) | Chunking threshold |

## Local LLM (Qwen)

| Name | Value |
|------|-------|
| `LOCAL_LLM_FOLDER` | `qwen2.5-3b-instruct` |
| `LOCAL_LLM_GGUF_FILE` | `qwen2.5-3b-instruct-q4_k_m.gguf` |
| `MIN_RAM_GB` | 16 |

Functions: `local_gguf_path()`, `local_llm_available()`, `system_ram_gb()`.

## Enums

### `SummaryLength`

`auto`, `short`, `normal`, `detailed`

### `SummaryMode` (legacy DB)

`extractive`, `abstractive` — deprecated, not used by the LLM summary engine.

## Path functions

| Function | Description |
|----------|-------------|
| `data_dir()` | `SBOBINATOR_DATA` or `./data` |
| `models_dir()` | `NEMO_CACHE_DIR` or `./models` |
| `local_model_path()` | Parakeet `.nemo` path |

## Python dependencies

Source of truth: `pyproject.toml` → see [`requirements/README.md`](../../requirements/README.md).

## Environment variables

See [Environment](../deployment/environment.md) and `.env.example`.
