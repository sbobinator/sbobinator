# Configurazione

Modulo: `src/sbobinator/config.py`  
API key riassunto: `src/sbobinator/summary_config.py`

## Costanti ASR

| Nome | Valore | Descrizione |
|------|--------|-------------|
| `DEFAULT_MODEL` | `nvidia/parakeet-tdt-0.6b-v3` | Modello ASR |
| `SAMPLE_RATE` | 16000 | Hz per NeMo |
| `CHUNK_THRESHOLD_SEC` | 1800 (30 min) | Soglia chunking |

## LLM locale (Qwen)

| Nome | Valore |
|------|--------|
| `LOCAL_LLM_FOLDER` | `qwen2.5-3b-instruct` |
| `LOCAL_LLM_GGUF_FILE` | `qwen2.5-3b-instruct-q4_k_m.gguf` |
| `MIN_RAM_GB` | 16 |

Funzioni: `local_gguf_path()`, `local_llm_available()`, `system_ram_gb()`.

## Enum

### `SummaryLength`

`auto`, `short`, `normal`, `detailed`

### `SummaryMode` (legacy DB)

`extractive`, `abstractive` — deprecato, non usato dal riassunto LLM.

## Funzioni path

| Funzione | Descrizione |
|----------|-------------|
| `data_dir()` | `SBOBINATOR_DATA` o `./data` |
| `models_dir()` | `NEMO_CACHE_DIR` o `./models` |
| `local_model_path()` | Path `.nemo` Parakeet |

## Dipendenze Python

Fonte di verità: `pyproject.toml` → vedi [`requirements/README.md`](../../requirements/README.md).

## Variabili ambiente

Vedi [Environment](../deployment/environment.md) e `.env.example`.
