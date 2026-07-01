# Text summarization

After transcription, Sbobinator can generate an **LLM summary** of the text in `trascrizione.txt`.

## Providers

| ID | Engine | Setup |
|----|--------|-------|
| `deepseek` | DeepSeek API | API key in [Summary settings](/settings/summary) |
| `openai` | OpenAI | API key |
| `gemini` | Google Gemini | API key |
| `claude` | Anthropic Claude | API key |
| `kimi` | Moonshot Kimi | API key |
| `local` | Qwen2.5 GGUF (CPU) | `python scripts/download_summary_llm.py` + RAM ≥ 16 GB |

Configuration: **http://localhost:8501/settings/summary**

API keys are saved in `data/.secrets/summary_keys.json` (or `SBOBINATOR_*_API_KEY` variables — see `.env.example`).

---

## Length

| Value | Behavior |
|-------|----------|
| `auto` | Proportional to the text |
| `short` | Short |
| `normal` | Balanced |
| `detailed` | Longer |

---

## Pipeline

1. NeMo transcription completed
2. `unload_model()` — frees ASR RAM
3. `summarize()` — chosen provider, map-reduce for long text
4. Saves `riassunto.txt`

If the summary fails: job **`completed`**, `summary_error` with the reason, transcript and SRT stay valid.

---

## Long texts

Beyond the provider's context → **map-reduce** strategy (partial chunks + merge).

---

## CLI

```cmd
sbobina transcribe file.wav -s --summary-provider deepseek
sbobina transcribe file.wav -s --summary-provider local --summary-length detailed
```

---

## UI

1. Sidebar → **Engines and API keys** (first-time setup)
2. Check **Generate summary**
3. Choose engine and length
4. Enqueue the file

---

## Python dependencies

```cmd
pip install -r requirements/local.txt
```

Includes: `openai`, `anthropic`, `google-genai`, `truststore`, `llama-cpp-python`, `psutil`, `huggingface_hub`.

On **Windows**, `truststore` is required for the cloud APIs (Python 3.13 SSL fix).

---

## Deprecated

LexRank / IT5 (`extractive` / `abstractive`) — removed. See `bug-fix/FIX-RIASSUNTO-LLM.md`.
