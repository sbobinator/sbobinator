# Models

Sbobinator uses **one required model** for transcription and **optional models** for LLM summary. No downloads during processing.

## ASR model (required)

| Property | Value |
|----------|-------|
| Hugging Face name | `nvidia/parakeet-tdt-0.6b-v3` |
| Local file | `models/parakeet-tdt-0.6b-v3.nemo` |
| Size | ~2.5 GB |
| Engine | NVIDIA NeMo |

```cmd
python scripts\download_model.py
```

Uses **curl** (system certificates). Optional variable: `NEMO_CACHE_DIR`.

---

## Cloud LLM summary (optional)

No model on disk. Requires an **API key** for the chosen provider.

| Provider | Env (alternative to secrets file) |
|----------|-----------------------------------|
| DeepSeek | `SBOBINATOR_DEEPSEEK_API_KEY` |
| OpenAI | `SBOBINATOR_OPENAI_API_KEY` |
| Gemini | `SBOBINATOR_GEMINI_API_KEY` |
| Claude | `SBOBINATOR_ANTHROPIC_API_KEY` |
| Kimi | `SBOBINATOR_KIMI_API_KEY` |

UI configuration: `/settings/summary`  
File: `data/.secrets/summary_keys.json`

---

## Local LLM summary — Qwen (optional)

| Property | Value |
|----------|-------|
| Model | `Qwen2.5-3B-Instruct` (GGUF Q4) |
| Folder | `models/qwen2.5-3b-instruct/` |
| Size | ~2 GB |
| RAM | ≥ 16 GB |
| Engine | llama.cpp (CPU) |

```cmd
python scripts\download_summary_llm.py
```

Requires `pip install -r requirements/local.txt` (includes `llama-cpp-python`).

---

## Docker

At build time: **Parakeet ASR only** in `/models/`.  
Summary: cloud API via env or `data/.secrets/` on the `/data` volume.  
Local Qwen: can be downloaded at runtime in the container with `download_summary_llm.py`.

---

## Summary table

| Component | Path | Download | Network at runtime |
|-----------|------|----------|-------------------|
| Parakeet ASR | `models/*.nemo` | `download_model.py` | No |
| Cloud summary | — | API key | Yes |
| Local Qwen | `models/qwen2.5-3b-instruct/*.gguf` | `download_summary_llm.py` | No |

---

## Deprecated

| Legacy | Replacement |
|--------|-------------|
| IT5 / `download_summary_model.py` | Multi-provider LLM |
| LexRank extractive | Removed as product «summary» |

---

## Licenses

- **Parakeet**: NVIDIA / NeMo
- **Qwen**: Alibaba model license — see Hugging Face
- Sbobinator code: proprietary license Antonio Trento (see `LICENSE`)
