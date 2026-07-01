# Contributing

## Development setup

```cmd
git clone https://github.com/sbobinator/sbobinator.git
cd sbobinator
python scripts\install_local.py
pip install -e ".[local,dev]"
```

## Conventions

| Aspect | Rule |
|--------|------|
| Python | 3.12+, type hints where possible |
| Lint | `ruff` (line-length 100) |
| Scripts | Python only — **no** `.ps1` |
| Commits | Clear messages in Italian or English |
| Scope | Minimal diffs, no unrequested refactors |

## Adding documentation

1. Edit files in `docs/`
2. Update `nav` in `mkdocs.yml` if adding a new page
3. `mkdocs serve` for preview
4. Push to `main` → automatic GitHub Pages deploy

## Adding features

1. Read [Architecture](../architecture/overview.md)
2. Jobs → go through `jobs.py` + `pipeline.py`
3. Models → always offline in `models/`
4. UI → do not block threads with NeMo (use the worker)

## Reporting bugs

Document in `bug-fix/TRACCIAMENTO-BUG.md` with:

- Symptom
- Root cause
- Fix or workaround
- How to reproduce

## Roadmap

See `evolutive/ROADMAP-EVOLUTIVE.md` for planned evolutions.

## License

By contributing code or documentation to the repository, you declare that you have the necessary rights and accept that, if accepted, your contribution will be integrated into the Software owned by **Antonio Trento** under the terms of the license in [`LICENSE`](../../LICENSE). For significant contributions, a written agreement may be required.
