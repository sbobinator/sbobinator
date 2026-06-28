# Manutenzione

## Routine

| Frequenza | Azione |
|-----------|--------|
| A ogni sessione | `restart_ui.py` se UI instabile |
| Dopo test | `clean_output.py` se vuoi storico pulito |
| Mensile | Verifica spazio disco in `data/output/` e `models/` |
| Aggiornamento | `git pull` + `pip install -e ".[local]"` |

## Spazio disco

| Cartella | Dimensione tipica |
|----------|-------------------|
| `models/parakeet-*.nemo` | ~2.5 GB |
| `models/mt5-small/` | ~1.1 GB |
| Job singolo | Audio sorgente + pochi MB testo |
| `queue.db` | KB–MB |

## Backup

Da salvare:

- `data/output/jobs/` — risultati utente
- `models/` — se non vuoi riscaricare (opzionale, riscaricabile)

Non serve backup di `.venv/`.

## Aggiornamento modelli

Rimuovi file/cartella in `models/` e rilancia gli script download.

## Log

- Worker: stdout del processo `sbobina worker`
- Streamlit: terminale dove gira `restart_ui.py`
- Job falliti: `job.json` campo `error` o `sbobina jobs show ID`

## Ripristino dopo crash

```cmd
sbobina jobs retry
python scripts\restart_ui.py
```

Il worker recupera automaticamente job `running` orfani.

## Pulizia git

Output e modelli sono in `.gitignore` — non committare `queue.db` né file audio.
