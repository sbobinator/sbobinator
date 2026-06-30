# Modelli

Sbobinator usa **un modello obbligatorio** per la trascrizione e **modelli opzionali** per il riassunto LLM. Nessun download durante l'elaborazione.

## Modello ASR (obbligatorio)

| Proprietà | Valore |
|-----------|--------|
| Nome HuggingFace | `nvidia/parakeet-tdt-0.6b-v3` |
| File locale | `models/parakeet-tdt-0.6b-v3.nemo` |
| Dimensione | ~2.5 GB |
| Engine | NVIDIA NeMo |

```cmd
python scripts\download_model.py
```

Usa **curl** (certificati di sistema). Variabile opzionale: `NEMO_CACHE_DIR`.

---

## Riassunto LLM cloud (opzionale)

Nessun modello su disco. Serve **API key** del provider scelto.

| Provider | Env (alternativa al file secrets) |
|----------|-----------------------------------|
| DeepSeek | `SBOBINATOR_DEEPSEEK_API_KEY` |
| OpenAI | `SBOBINATOR_OPENAI_API_KEY` |
| Gemini | `SBOBINATOR_GEMINI_API_KEY` |
| Claude | `SBOBINATOR_ANTHROPIC_API_KEY` |
| Kimi | `SBOBINATOR_KIMI_API_KEY` |

Configurazione UI: `/settings/summary`  
File: `data/.secrets/summary_keys.json`

---

## Riassunto LLM locale — Qwen (opzionale)

| Proprietà | Valore |
|-----------|--------|
| Modello | `Qwen2.5-3B-Instruct` (GGUF Q4) |
| Cartella | `models/qwen2.5-3b-instruct/` |
| Dimensione | ~2 GB |
| RAM | ≥ 16 GB |
| Engine | llama.cpp (CPU) |

```cmd
python scripts\download_summary_llm.py
```

Richiede `pip install -r requirements/local.txt` (include `llama-cpp-python`).

---

## Docker

Al build: solo **Parakeet ASR** in `/models/`.  
Riassunto: API cloud via env o `data/.secrets/` nel volume `/data`.  
Qwen locale: scaricabile a runtime nel container con `download_summary_llm.py`.

---

## Tabella riepilogo

| Componente | Path | Download | Rete a runtime |
|------------|------|----------|----------------|
| Parakeet ASR | `models/*.nemo` | `download_model.py` | No |
| Riassunto cloud | — | API key | Sì |
| Qwen locale | `models/qwen2.5-3b-instruct/*.gguf` | `download_summary_llm.py` | No |

---

## Deprecato

| Vecchio | Sostituto |
|---------|-----------|
| IT5 / `download_summary_model.py` | LLM multi-provider |
| LexRank estrattivo | Rimosso come «riassunto» |

---

## Licenze

- **Parakeet**: NVIDIA / NeMo
- **Qwen**: licenza modello Alibaba — vedi HuggingFace
- Codice Sbobinator: MIT
