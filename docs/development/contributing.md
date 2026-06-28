# Contribuire

## Setup sviluppo

```cmd
git clone https://github.com/sbobinator/sbobinator.git
cd sbobinator
python scripts\install_local.py
pip install -e ".[local,dev]"
```

## Convenzioni

| Aspetto | Regola |
|---------|--------|
| Python | 3.12+, type hints dove possibile |
| Lint | `ruff` (line-length 100) |
| Script | Solo Python — **no** `.ps1` |
| Commit | Messaggi chiari in italiano o inglese |
| Scope | Diff minimi, niente refactor non richiesti |

## Aggiungere documentazione

1. Modifica file in `docs/`
2. Aggiorna `nav` in `mkdocs.yml` se nuova pagina
3. `mkdocs serve` per anteprima
4. Push su `main` → deploy automatico GitHub Pages

## Aggiungere funzionalità

1. Leggi [Architettura](../architecture/overview.md)
2. Job → passa da `jobs.py` + `pipeline.py`
3. Modelli → sempre offline in `models/`
4. UI → non bloccare thread con NeMo (usa worker)

## Segnalazione bug

Documenta in `bug-fix/TRACCIAMENTO-BUG.md` con:

- Sintomo
- Causa root
- Fix o workaround
- Come riprodurre

## Roadmap

Vedi `evolutive/ROADMAP-EVOLUTIVE.md` per evoluzioni pianificate.

## Licenza

Contribuendo accetti licenza MIT del progetto.
