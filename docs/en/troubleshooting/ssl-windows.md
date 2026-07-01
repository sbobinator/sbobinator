# SSL on Windows

## Issue 1 — Model downloads (HuggingFace)

On **Python 3.13 / Windows**, `huggingface_hub` may fail with:

```
SSLCertVerificationError: certificate verify failed
```

**Solution:** download models with **curl** (uses Windows certificates):

| Model | Script |
|-------|--------|
| Parakeet ASR | `scripts/download_model.py` |
| Qwen summary | `scripts/download_summary_llm.py` |

---

## Issue 2 — Cloud summary API (`Connection error`)

On Windows, **DeepSeek / OpenAI / …** calls via the Python SDK (`httpx`) may fail with:

```
Connection error.
```

**Cause:** Python does not use the Windows certificate store.

**Solution:** the `truststore` package (already in `requirements/local.txt`):

```cmd
pip install truststore
pip install -r requirements/local.txt
```

Then restart: `python scripts\restart_ui.py`

Sbobinator calls `truststore.inject_into_ssl()` at startup (`http_ssl.py`).

---

## What NOT to do

- Do not disable SSL globally
- Do not use `HF_HUB_DISABLE_SSL` in production

---

## Docker / Linux

In Linux containers both issues are rare. `truststore` is installed but usually not needed.

---

## Reference

`bug-fix/TRACCIAMENTO-BUG.md` — BUG-ENV-001, BUG-WIN-011.
