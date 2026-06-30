# Riassunto testo

Dopo la trascrizione, Sbobinator può generare un **riassunto LLM** del testo in `trascrizione.txt`.

## Provider

| ID | Motore | Setup |
|----|--------|--------|
| `deepseek` | DeepSeek API | API key in [Impostazioni riassunto](/settings/summary) |
| `openai` | OpenAI | API key |
| `gemini` | Google Gemini | API key |
| `claude` | Anthropic Claude | API key |
| `kimi` | Moonshot Kimi | API key |
| `local` | Qwen2.5 GGUF (CPU) | `python scripts/download_summary_llm.py` + RAM ≥ 16 GB |

Configurazione: **http://localhost:8501/settings/summary**

Le API key sono salvate in `data/.secrets/summary_keys.json` (o variabili `SBOBINATOR_*_API_KEY` — vedi `.env.example`).

---

## Lunghezza

| Valore | Comportamento |
|--------|---------------|
| `auto` | Proporzionata al testo |
| `short` | Breve |
| `normal` | Bilanciato |
| `detailed` | Più lungo |

---

## Pipeline

1. Trascrizione NeMo completata
2. `unload_model()` — libera RAM ASR
3. `summarize()` — provider scelto, map-reduce se testo lungo
4. Salva `riassunto.txt`

Se il riassunto fallisce: job **`completed`**, `summary_error` con motivo, trascrizione e SRT restano validi.

---

## Testi lunghi

Oltre il contesto del provider → strategia **map-reduce** (chunk parziali + unione).

---

## CLI

```cmd
sbobina transcribe file.wav -s --summary-provider deepseek
sbobina transcribe file.wav -s --summary-provider local --summary-length detailed
```

---

## UI

1. Sidebar → **Motori e API key** (prima configurazione)
2. Spunta **Genera riassunto**
3. Scegli motore e lunghezza
4. Accoda file

---

## Dipendenze Python

```cmd
pip install -r requirements/local.txt
```

Include: `openai`, `anthropic`, `google-genai`, `truststore`, `llama-cpp-python`, `psutil`, `huggingface_hub`.

Su **Windows**, `truststore` è necessario per le API cloud (fix SSL Python 3.13).

---

## Deprecato

LexRank / IT5 (`extractive` / `abstractive`) — rimossi. Vedi `bug-fix/FIX-RIASSUNTO-LLM.md`.
