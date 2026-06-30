# Changelog

## In sviluppo — Riassunto LLM multi-provider

### Aggiunto

- Riassunto LLM: DeepSeek, OpenAI, Gemini, Claude, Kimi, Qwen locale
- Pagina `/settings/summary` per API key e stato motori
- `truststore` per SSL API cloud su Windows
- `requirements/` (alias pip → `pyproject.toml`)
- `scripts/download_summary_llm.py`, `scripts/summary_benchmark.py --provider`
- `.env.example`

### Modificato

- UI FastAPI (non più Streamlit)
- Docker: solo ASR in immagine, no IT5
- `pip install -r requirements/local.txt` in `install_local.py`

### Rimosso / deprecato

- LexRank e IT5 come riassunto prodotto
- `transformers` / `sentencepiece` dalle dipendenze
- `download_summary_model.py` (deprecato)

---

## 0.3.0 — Coda job e worker

### Aggiunto

- Coda job SQLite (`queue.db`) con stati queued/running/completed/failed/cancelled
- Worker in **processo separato** (non thread Streamlit)
- Cartelle job `YYYYMMDD_HHMMSS_nomefile`
- CLI `sbobina jobs list|show|retry`
- CLI `sbobina worker`
- Script: `clean_output.py`, `restart_ui.py`, `benchmark_monitor.py`
- Download mT5 offline: `download_summary_model.py`
- Variabile `SBOBINATOR_DATA` per Docker
- Docker build con modelli inclusi
- Documentazione MkDocs completa

### Modificato

- `transcribe` CLI usa job registry (default)
- UI: pannello coda, upload multiplo, worker auto
- Riassunto mT5 solo da `models/mt5-small/` locale

### Corretto

- ImportError / lightning.fabric con NeMo in thread
- Istanze Streamlit duplicate su porta 8501
- Bottone accoda disabilitato (uploader fuori form)
- SSL Windows per mT5 (download curl, no runtime HF)

### Rimosso

- Tutti gli script PowerShell `.ps1`

---

## 0.2.x — Interfaccia web e riassunto

- UI Streamlit
- Riassunto estrattivo e mT5
- Export TXT/SRT

---

## 0.1.x — CLI base

- Trascrizione NeMo Parakeet
- `sbobina transcribe`

---

Per bug noti storici vedi `bug-fix/TRACCIAMENTO-BUG.md`.  
Per roadmap futura vedi `evolutive/ROADMAP-EVOLUTIVE.md`.
