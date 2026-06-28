# SSL su Windows

## Il problema

Su Windows, **Python 3.13** spesso non valida i certificati SSL verso `huggingface.co`:

```
SSLCertVerificationError: certificate verify failed: unable to get local issuer certificate
```

Succede con:

- `transformers` / `huggingface_hub` download a runtime
- `urllib` / `requests` verso HuggingFace

**Non** succede con **curl.exe** che usa il certificate store di Windows.

---

## Soluzione Sbobinator

### Mai scaricare modelli a runtime

| Modello | Approccio |
|---------|-----------|
| Parakeet | `scripts/download_model.py` (curl) |
| mT5 | `scripts/download_summary_model.py` (curl) |

A runtime `transcribe.py` e `summarize.py` leggono **solo file locali**.

### Se vedi ancora errori SSL

1. Verifica di non usare vecchia versione che scaricava `google/mt5-small` online
2. Completa download in `models/mt5-small/`
3. Riavvia con `restart_ui.py`

---

## Download manuale alternativo

Se gli script falliscono, scarica da browser:

1. [Parakeet .nemo](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3/tree/main)
2. [mT5-small](https://huggingface.co/google/mt5-small/tree/main)

Metti in:

```
models/parakeet-tdt-0.6b-v3.nemo
models/mt5-small/   (tutti i file del repo)
```

---

## Docker / Linux / WSL

In container Linux il problema è raro. L'immagine Docker scarica al **build** con curl Debian.

WSL Ubuntu: stessi script Python, curl di Linux.

---

## Cosa NON fare

- Non disabilitare SSL globalmente in produzione
- Non usare `HF_HUB_DISABLE_SSL` come soluzione permanente
- Non affidarsi a download HuggingFace da Python su Windows in produzione

L'architettura corretta è: **download una tantum → uso offline**.

---

## Riferimento interno

Documentato anche in `bug-fix/TRACCIAMENTO-BUG.md` come BUG-ENV-001 / BUG-WIN-011.
