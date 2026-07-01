# Hardware requirements

Requirements depend on **what you use**: transcription only, cloud API summary, or offline local summary (Qwen).

## Common prerequisites

| Resource | Required |
|----------|----------|
| **Python** | 3.12+ (native install; Docker includes Python) |
| **ffmpeg** | Required — extracts audio from video |
| **CPU** | Modern x64; **sequential** processing (one job at a time) |
| **NVIDIA GPU** | Optional — accelerates **ASR transcription** only |

## Comparison by scenario

| Scenario | System RAM | Free disk | Network | Models on disk |
|----------|------------|-----------|---------|----------------|
| **Transcription only** | **8 GB** min · **16 GB** recommended | **~6 GB** | Only at initial setup | Parakeet ~2.5 GB |
| **Transcription + API summary** | Same as above | Same as above | **Yes** during summary | Parakeet only |
| **Transcription + local summary** | **≥ 16 GB** · **32 GB** ideal | **~8–10 GB** | Only at initial setup | Parakeet + Qwen ~2 GB |

!!! note "RAM and local summary"
    Before local summary the pipeline **unloads the ASR model from RAM**. You need **≥ 16 GB total physical RAM** (threshold in `MIN_RAM_GB`); below this threshold the Qwen engine is disabled.

---

## 1. Transcription only

| Resource | Detail |
|----------|--------|
| **RAM** | Minimum **8 GB**; **16 GB** recommended for long audio (1 h+). |
| **Disk** | ~2.5 GB ASR + ~3–4 GB dependencies + user output → **≥ 6 GB** free. |
| **Network** | Only for initial model download. Normal use is **offline**. |
| **GPU** | Optional. On CPU: ~**2× realtime** (1 min audio ≈ 2 min processing). |

---

## 2. Transcription + API summary

| Resource | Detail |
|----------|--------|
| **RAM** | Same as transcription only — LLM not local. |
| **Disk** | Same as transcription only — no summary model. |
| **Network** | **Required** for API calls during summary. |
| **API key** | UI `/settings/summary` or `data/.secrets/summary_keys.json`. |

Suitable for PCs with **8 GB RAM** if you use cloud only.

---

## 3. Transcription + local summary (Qwen)

| Resource | Detail |
|----------|--------|
| **RAM** | **≥ 16 GB** (checked at startup). **32 GB** recommended (mini PC, long files). |
| **Disk** | Transcription only **+ ~2 GB** Qwen GGUF. |
| **Network** | Only for initial Qwen download. Then **offline**. |
| **CPU** | Summary is **CPU-bound**; long texts: several minutes (map-reduce). |
| **Docker** | Auto-download Qwen on first start if RAM ≥ 16 GB (~10–20 min, one-time). |

See also [Models](models.md) and [Docker](../deployment/docker.md).
