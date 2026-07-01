# Script di utilità

Tutti in `scripts/` — **Python puro**.

## `install_local.py`

Installazione completa ambiente locale.

```cmd
python scripts\install_local.py
```

- Crea `.venv`
- PyTorch CPU
- `pip install -r requirements/local.txt` → extra `[local]` da `pyproject.toml`

---

## `download_model.py`

Scarica Parakeet ASR (~2.5 GB) in `models/` via curl.

```cmd
python scripts\download_model.py
```

---

## `download_summary_llm.py`

Scarica Qwen2.5 GGUF per riassunto **locale** (~2 GB).

```cmd
python scripts\download_summary_llm.py
```

Richiede `huggingface_hub` (in `[local]` / `[summarize]`).

---

## `download_summary_model.py` (deprecato)

IT5 news — **non più usato**. Usa `download_summary_llm.py` o API cloud.

---

## `clean_output.py`

Svuota `data/output/jobs/` (cartelle + `queue.db`).

```cmd
python scripts\clean_output.py
```

---

## `restart_ui.py`

Termina UI/worker sulla porta 8501 e riavvia FastAPI.

```cmd
python scripts\restart_ui.py
```

Usato da `start.bat`.

---

## `summary_benchmark.py`

Benchmark riassunto LLM su trascrizioni esistenti.

```cmd
python scripts\summary_benchmark.py --provider deepseek
python scripts\summary_benchmark.py --provider local --only campione-italiano-lungo
```

---

## `benchmark_monitor.py`

Monitor performance job in tempo reale.

---

## `generate_samples.py`

Campioni audio italiani da Wikimedia (test).

---

## `start.bat`

Wrapper Windows → `restart_ui.py`.

---

## `publish_docs.py` / `publish_docs.bat`

Pubblica la documentazione su **sbobinator.github.io** (stesso metodo di Sbobinator — nessuna GitHub Action).

```cmd
scripts\publish_docs.bat
```

1. `mkdocs build` in una cartella temporanea  
2. Copia in `../sbobinator.github.io/docs/`  
3. `git commit` nel repo Pages  

Poi manualmente:

```cmd
cd ..\sbobinator.github.io
git push
```

**Una tantum:** clona il repo Pages accanto a questo progetto:

```cmd
cd ..
git clone https://github.com/sbobinator/sbobinator.github.io.git
```

Sito: https://sbobinator.github.io/docs/

---

## Tabella rapida

| Script | Quando usarlo |
|--------|---------------|
| `install_local.py` | Prima installazione |
| `download_model.py` | Prima trascrizione |
| `download_summary_llm.py` | Riassunto locale Qwen |
| `publish_docs.bat` | Pubblicare docs su GitHub Pages |
| `clean_output.py` | Reset storico job |
| `restart_ui.py` | UI bloccata / porta occupata |
| `summary_benchmark.py` | Valutare qualità riassunto LLM |
