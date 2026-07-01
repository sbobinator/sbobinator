# Environment variables

Full list in [`.env.example`](../../.env.example) (only variables read by the code).

## Paths

### `SBOBINATOR_DATA`

Root data folder (input, output, `.secrets`).

| Value | Effect |
|-------|--------|
| Not set | `{project_root}/data` |
| `/data` (Docker) | Container volume |

### `NEMO_CACHE_DIR`

ASR model folder (`.nemo`) and optional Qwen GGUF.

| Value | Effect |
|-------|--------|
| Not set | `{project_root}/models` |
| `/models` (Docker) | Models in image |

---

## Web interface

### `SBOBINATOR_UI_HOST`

| Value | Effect |
|-------|--------|
| Not set | `127.0.0.1` |
| `0.0.0.0` | Docker — exposes port 8501 |

---

## Summary LLM API keys

Alternatives to `data/.secrets/summary_keys.json`:

| Variable | Provider |
|----------|----------|
| `SBOBINATOR_DEEPSEEK_API_KEY` | DeepSeek |
| `SBOBINATOR_OPENAI_API_KEY` | OpenAI |
| `SBOBINATOR_GEMINI_API_KEY` | Gemini |
| `SBOBINATOR_ANTHROPIC_API_KEY` | Claude |
| `SBOBINATOR_KIMI_API_KEY` | Kimi |

Recommended setup: UI → `/settings/summary`.

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

## Verification

```cmd
sbobina info
```

```python
from sbobinator.config import data_dir, models_dir
from sbobinator.summary_config import secrets_path
print(data_dir(), models_dir(), secrets_path())
```
