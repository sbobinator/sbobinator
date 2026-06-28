# Installazione

## Prerequisiti

### Python 3.12 o superiore

```cmd
python --version
```

### ffmpeg (obbligatorio)

Estrae l'audio da video e prepara i file per NeMo.

**Windows:**

```cmd
winget install Gyan.FFmpeg
```

Verifica:

```cmd
ffmpeg -version
ffprobe -version
```

### curl (per download modelli su Windows)

Incluso in Windows 10+. Gli script usano `curl.exe` esplicitamente.

---

## Installazione locale (consigliata su Windows)

Dalla root del repository:

```cmd
python scripts\install_local.py
```

Lo script:

1. Crea `.venv/` se mancante
2. Installa PyTorch (CPU)
3. Installa Sbobinator con `pip install -e ".[local]"` (NeMo, Streamlit, Transformers)

### Dipendenze opzionali (pyproject.toml)

| Extra | Pacchetti | Uso |
|-------|-----------|-----|
| `asr` | torch, nemo_toolkit | Solo trascrizione |
| `ui` | streamlit | Solo interfaccia |
| `summarize` | transformers, sentencepiece | Solo riassunto |
| `local` | tutti i sopra | Installazione completa |
| `dev` | ruff | Lint |

---

## Installazione manuale

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux:   source .venv/bin/activate
pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[local]"
```

---

## Verifica installazione

```cmd
sbobina info
```

Deve mostrare versione, modello predefinito e device rilevato.

---

## Cosa NON usare

!!! warning "Niente script PowerShell"
    Gli script `.ps1` sono stati rimossi (falsi positivi antivirus). Usa solo:

    - `python scripts/*.py`
    - `start.bat`
    - `sbobina` CLI

---

## Dopo l'installazione

1. [Scarica i modelli](models.md)
2. [Avvio rapido](quickstart.md)
