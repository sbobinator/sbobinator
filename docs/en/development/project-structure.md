# Project structure

```
sbobinator/
├── scripts/
│   └── publish_docs.py       # mkdocs build → ../sbobinator.github.io/docs/
├── bug-fix/                  # Internal bug tracking
├── data/
│   ├── input/                # Source files
│   └── output/jobs/          # Jobs + queue.db
├── docker/
│   ├── Dockerfile.cpu
│   ├── Dockerfile.gpu
│   └── docker-compose.yml
├── docs/                     # MkDocs documentation (this site)
├── evolutive/                # Roadmap and future architecture
├── models/                   # Offline models (gitignored)
├── scripts/                  # Utility Python scripts
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

Editable install: `src/sbobinator` → import `sbobinator`.

CLI entry point: `sbobina = sbobinator.cli:app`

## Runtime dependencies

| Package | Use |
|---------|-----|
| typer, rich | CLI |
| torch | NeMo backend |
| nemo_toolkit[asr] | Parakeet |
| streamlit | UI |
| transformers, sentencepiece | mT5 |

## Tests

```cmd
ruff check src/
```

## Documentation

```cmd
pip install -r docs/requirements.txt
mkdocs serve
```

## Folders not in release

- `bug-fix/`, `evolutive/` — internal development documentation
- `data/output/` — generated at runtime
- `models/` — downloaded at runtime
