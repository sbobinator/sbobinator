# Dipendenze Sbobinator

**Fonte di verità:** [`pyproject.toml`](../pyproject.toml) → `[project.optional-dependencies]`

I file `*.txt` in questa cartella sono **alias** per `pip install -r` — non duplicano versioni a mano.

## Extra

| Extra | Contenuto | Quando usarlo |
|-------|-----------|---------------|
| **`local`** | ASR NeMo + UI FastAPI + riassunto LLM completo | Installazione Windows/Linux consigliata |
| **`ui`** | FastAPI + provider cloud + `truststore` | Solo interfaccia (senza NeMo) |
| **`summarize`** | Provider LLM cloud + `llama-cpp-python` + `huggingface_hub` | Libreria riassunto senza UI |
| **`asr`** | PyTorch + NeMo | Solo trascrizione CLI |

## Riassunto LLM — pacchetti Python

| Pacchetto | Ruolo |
|-----------|--------|
| `openai` | OpenAI, DeepSeek, Kimi (API compatible) |
| `anthropic` | Claude |
| `google-genai` | Gemini |
| `truststore` | Certificati SSL su Windows (Python 3.13) |
| `llama-cpp-python` | Qwen GGUF locale (CPU) |
| `huggingface_hub` | `scripts/download_summary_llm.py` |
| `psutil` | Gate RAM 16 GB per LLM locale |

## Comandi

```cmd
pip install -r requirements/local.txt
pip install -e ".[local]"
```

Equivalenti. `install_local.py` usa `requirements/local.txt`.

## Docker

`docker/Dockerfile.*` installa `-e ".[ui,summarize]"` (= stessi pacchetti riassunto + web, + NeMo via pip separato).

## Deprecato

- `transformers` / `sentencepiece` — vecchio stack IT5/LexRank, **rimosso**
- `scripts/download_summary_model.py` — IT5, sostituito da `download_summary_llm.py`
