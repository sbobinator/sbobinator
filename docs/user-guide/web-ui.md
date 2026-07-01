# Interfaccia web

L'interfaccia è costruita con **FastAPI + HTMX** (`src/sbobinator/ui/server.py`), porta predefinita **8501** (Docker profilo `cpu`: host **8502**).

## Avvio

```cmd
sbobina ui
sbobina ui --port 9000
start.bat
python scripts\restart_ui.py
```

## Navigazione

| Voce | URL | Descrizione |
|------|-----|-------------|
| Home | `/` | Upload, coda live |
| Coda & storico | `/jobs` | Elenco completo, filtri, azioni |
| Dettaglio job | `/jobs/{id}` | Trascrizione, riassunto, download, azioni |
| Riassunto LLM | `/settings/summary` | API key, stato motori, download Qwen |

---

## Home (`/`)

Upload file, impostazioni sidebar, pannello coda attiva (HTMX ogni 2 s). Dopo l'accodamento redirect a **`/jobs/{id}`** del nuovo job.

Sidebar: ultimi **8** job con link alla pagina dedicata.

---

## Coda & storico (`/jobs`)

Tabella di tutti i job con filtri, ricerca e azioni rapide. Clic sul **nome file** o **Apri** → `/jobs/{id}`.

---

## Dettaglio job (`/jobs/{id}`)

Pagina dedicata per consultare un singolo lavoro:

- Breadcrumb «Coda & storico / nome file»
- Job **in corso**: pannello progresso con polling HTMX (`/partials/job/{id}/status`), auto-reload al termine
- Job **completato**: trascrizione, riassunto, download TXT/SRT/riassunto
- Path cartella, **Apri cartella**, rielabora, elimina

---

## Impostazioni riassunto (`/settings/summary`)

- API key provider cloud (DeepSeek, OpenAI, …)
- Stato disponibilità motori
- Download / percorso modello Qwen locale
- RAM sistema vs soglia minima (16 GB per locale)

---

## Worker in background

All'avvio UI, `start_background_worker()` lancia un **processo separato**:

```text
python -m sbobinator.cli worker
```

NeMo **non** gira nel processo uvicorn (evita crash `lightning.fabric`).

PID salvato in `data/output/jobs/worker.pid`.

All'avvio worker: `recover_orphaned_running_jobs()` + `reconcile_jobs_with_disk()`.

---

## API HTTP (principali)

| Metodo | Path | Uso |
|--------|------|-----|
| POST | `/enqueue` | Upload e accodamento |
| GET | `/partials/queue` | Fragment HTMX coda |
| GET | `/partials/job/{id}/status` | Progresso singolo job |
| GET | `/jobs/{id}` | Pagina dettaglio job |
| POST | `/api/jobs/{id}/cancel` | Annulla (param `return_to` opzionale) |
| POST | `/api/jobs/{id}/delete` | Elimina job e cartella |
| POST | `/api/jobs/{id}/reprocess` | Nuova elaborazione |
| POST | `/api/jobs/{id}/requeue` | Rimetti in coda |
| POST | `/api/jobs/reconcile` | Sync DB ↔ disco |
| GET | `/download/{id}/{kind}` | Scarica txt / srt / summary |

---

## Suggerimenti

- Un solo `restart_ui.py` alla volta — evita più istanze sulla stessa porta
- Dopo `clean_output.py`, ricarica la pagina (F5)
- Primo job dopo avvio: 1–2 min per caricare Parakeet in RAM
- Stesso file più volte → più cartelle: usa `/jobs` e le label con ora/riassunto per orientarti

Vedi [Coda e storico job](jobs-queue.md) per la logica completa.
