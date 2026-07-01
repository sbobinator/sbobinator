# Struttura progetto

```
sbobinator/
├── scripts/
│   └── publish_docs.py       # mkdocs build → ../sbobinator.github.io/docs/
├── bug-fix/                  # Tracciamento bug interno
├── data/
│   ├── input/                # File sorgente
│   └── output/jobs/          # Job + queue.db
├── docker/
│   ├── Dockerfile.cpu
│   ├── Dockerfile.gpu
│   └── docker-compose.yml
├── docs/                     # Documentazione MkDocs (questo sito)
├── evolutive/                # Roadmap e architettura futura
├── models/                   # Modelli offline (gitignored)
├── scripts/                  # Script Python utilità
├── src/sbobinator/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── config.py
│   ├── export.py
│   ├── extract.py
│   ├── jobs.py
│   ├── pipeline.py
│   ├── summarize.py
│   ├── transcribe.py
│   ├── worker.py
│   └── ui/
│       ├── app.py
│       └── launch.py
├── mkdocs.yml
├── pyproject.toml
├── start.bat
└── README.md
```

## Package layout

Installazione editable: `src/sbobinator` → import `sbobinator`.

Entry point CLI: `sbobina = sbobinator.cli:app`

## Dipendenze runtime

| Pacchetto | Uso |
|-----------|-----|
| typer, rich | CLI |
| torch | Backend NeMo |
| nemo_toolkit[asr] | Parakeet |
| streamlit | UI |
| transformers, sentencepiece | mT5 |

## Test

```cmd
ruff check src/
```

## Documentazione

```cmd
pip install -r docs/requirements.txt
mkdocs serve
```

## Cartelle non in release

- `bug-fix/`, `evolutive/` — documentazione sviluppo interno
- `data/output/` — generata a runtime
- `models/` — scaricata a runtime
