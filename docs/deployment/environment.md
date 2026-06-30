# Variabili d'ambiente

Elenco completo in [`.env.example`](../../.env.example) (solo variabili lette dal codice).

## Percorsi

### `SBOBINATOR_DATA`

Cartella radice dati (input, output, `.secrets`).

| Valore | Effetto |
|--------|---------|
| Non impostata | `{project_root}/data` |
| `/data` (Docker) | Volume container |

### `NEMO_CACHE_DIR`

Cartella modelli ASR (`.nemo`) e opzionale Qwen GGUF.

| Valore | Effetto |
|--------|---------|
| Non impostata | `{project_root}/models` |
| `/models` (Docker) | Modelli nell'immagine |

---

## Interfaccia web

### `SBOBINATOR_UI_HOST`

| Valore | Effetto |
|--------|---------|
| Non impostata | `127.0.0.1` |
| `0.0.0.0` | Docker — espone porta 8501 |

---

## API key riassunto LLM

Alternative al file `data/.secrets/summary_keys.json`:

| Variabile | Provider |
|-----------|----------|
| `SBOBINATOR_DEEPSEEK_API_KEY` | DeepSeek |
| `SBOBINATOR_OPENAI_API_KEY` | OpenAI |
| `SBOBINATOR_GEMINI_API_KEY` | Gemini |
| `SBOBINATOR_ANTHROPIC_API_KEY` | Claude |
| `SBOBINATOR_KIMI_API_KEY` | Kimi |

Configurazione consigliata: UI → `/settings/summary`.

---

## Docker Compose

```yaml
environment:
  - NEMO_CACHE_DIR=/models
  - SBOBINATOR_DATA=/data
  - SBOBINATOR_UI_HOST=0.0.0.0
  - SBOBINATOR_DEEPSEEK_API_KEY=sk-...
volumes:
  - ../data:/data
```

---

## Verifica

```cmd
sbobina info
```

```python
from sbobinator.config import data_dir, models_dir
from sbobinator.summary_config import secrets_path
print(data_dir(), models_dir(), secrets_path())
```
