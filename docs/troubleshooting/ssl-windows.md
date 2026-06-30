# SSL su Windows

## Problema 1 — Download modelli (HuggingFace)

Su **Python 3.13 / Windows**, `huggingface_hub` può fallire con:

```
SSLCertVerificationError: certificate verify failed
```

**Soluzione:** scarica modelli con **curl** (usa certificati Windows):

| Modello | Script |
|---------|--------|
| Parakeet ASR | `scripts/download_model.py` |
| Qwen riassunto | `scripts/download_summary_llm.py` |

---

## Problema 2 — API riassunto cloud (`Connection error`)

Su Windows, le chiamate **DeepSeek / OpenAI / …** via SDK Python (`httpx`) possono fallire con:

```
Connection error.
```

**Causa:** Python non usa il certificate store di Windows.

**Soluzione:** pacchetto `truststore` (già in `requirements/local.txt`):

```cmd
pip install truststore
pip install -r requirements/local.txt
```

Poi riavvia: `python scripts\restart_ui.py`

Sbobinator chiama `truststore.inject_into_ssl()` all'avvio (`http_ssl.py`).

---

## Cosa NON fare

- Non disabilitare SSL globalmente
- Non usare `HF_HUB_DISABLE_SSL` in produzione

---

## Docker / Linux

In container Linux entrambi i problemi sono rari. `truststore` è installato ma di solito non necessario.

---

## Riferimento

`bug-fix/TRACCIAMENTO-BUG.md` — BUG-ENV-001, BUG-WIN-011.
