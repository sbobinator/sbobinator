# Script di utilità

Tutti in `scripts/` — **Python puro**, nessun PowerShell.

## `install_local.py`

Installazione completa ambiente locale.

```cmd
python scripts\install_local.py
```

- Crea `.venv`
- PyTorch CPU
- `pip install -e ".[local]"`

---

## `download_model.py`

Scarica Parakeet ASR (~2.5 GB) in `models/` via curl.

```cmd
python scripts\download_model.py
```

Rispetta `NEMO_CACHE_DIR`. Supporta ripresa download (`curl -C -`).

---

## `download_summary_model.py`

Scarica `google/mt5-small` in `models/mt5-small/`.

```cmd
python scripts\download_summary_model.py
```

Elenca file da API HuggingFace, scarica con curl. Su Windows usa `curl.exe`.

---

## `clean_output.py`

Svuota `data/output/jobs/` (cartelle + `queue.db`). Mantiene `.gitkeep`.

```cmd
python scripts\clean_output.py
```

---

## `restart_ui.py`

Termina Streamlit/worker Sbobinator sulla porta 8501 e riavvia UI.

```cmd
python scripts\restart_ui.py
```

Usato da `start.bat`. Evita istanze duplicate.

---

## `benchmark_monitor.py`

Monitor performance job in tempo reale.

```cmd
python scripts\benchmark_monitor.py
python scripts\benchmark_monitor.py --watch
python scripts\benchmark_monitor.py --poll 5
```

Metriche: durata audio, tempo elaborazione, RTF, velocità, caratteri.

Salva report in `data/output/benchmark_YYYYMMDD_HHMMSS.json` e `.md`.

---

## `generate_samples.py`

Genera campioni audio italiani da Wikimedia (test).

```cmd
python scripts\generate_samples.py
```

Output in `data/input/`.

---

## `start.bat`

Wrapper Windows → `restart_ui.py` con venv o Python313.

---

## Tabella rapida

| Script | Quando usarlo |
|--------|---------------|
| `install_local.py` | Prima installazione |
| `download_model.py` | Prima trascrizione |
| `download_summary_model.py` | Prima di usare mT5 |
| `clean_output.py` | Reset storico job |
| `restart_ui.py` | UI bloccata / porta occupata |
| `benchmark_monitor.py` | Test performance |
