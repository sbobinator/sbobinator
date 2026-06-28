# Configurazione

Modulo: `src/sbobinator/config.py`

## Costanti

| Nome | Valore | Descrizione |
|------|--------|-------------|
| `DEFAULT_MODEL` | `nvidia/parakeet-tdt-0.6b-v3` | Modello ASR |
| `SAMPLE_RATE` | 16000 | Hz per NeMo |
| `CHUNK_THRESHOLD_SEC` | 1800 (30 min) | Soglia chunking |
| `CHUNK_LENGTH_SEC` | 30 | Durata chunk |
| `CHUNK_OVERLAP_SEC` | 2 | Overlap chunk |

## Estensioni file

`VIDEO_EXTENSIONS`, `AUDIO_EXTENSIONS` — set usati da `extract.py`.

## Enum

### `SummaryMode`

- `extractive`
- `abstractive`

### `SummaryLength`

- `auto`, `short`, `normal`, `detailed`

## `TranscribeConfig`

```python
@dataclass
class TranscribeConfig:
    model_name: str = DEFAULT_MODEL
    device: str | None = None  # None = auto
    chunk_threshold_sec: float = 1800
    chunk_length_sec: float = 30
    chunk_overlap_sec: float = 2
```

`resolve_device()` → `cuda` se disponibile, altrimenti `cpu`.

## Funzioni path

| Funzione | Descrizione |
|----------|-------------|
| `project_root()` | Root repo (parent di `src/`) |
| `data_dir()` | `SBOBINATOR_DATA` o `./data` |
| `input_dir()` | `data/input` |
| `output_dir()` | `data/output` |
| `models_dir()` | `NEMO_CACHE_DIR` o `./models` |
| `summary_model_dir()` | `models/mt5-small` |
| `local_model_path()` | Path `.nemo` se presente |
| `local_summary_model_path()` | Path mT5 se completo |
| `local_summary_model_available()` | bool |

## Variabili ambiente

Vedi [Deployment → Environment](../deployment/environment.md).
