# Architettura futura — ragionamento tecnico

Come passare da **Streamlit monolitico** a un sistema con **coda affidabile**, backend unico e deploy su mini server.

---

## 1. Architettura attuale (v0.2)

```
┌──────────────────────────────────────────────────┐
│              Streamlit (app.py)                  │
│  ┌────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │ upload UI  │→ │ transcribe()│→ │ jobs.py   │ │
│  │ sidebar    │  │ summarize() │  │ index.json│ │
│  └────────────┘  └─────────────┘  └───────────┘ │
│         tutto nello stesso processo Python       │
└──────────────────────────────────────────────────┘
         ↓
   data/output/jobs/{id}/
```

### Problemi strutturali

1. **Blocking:** `transcribe()` gira nel thread Streamlit → UI congelata
2. **Single flight:** secondo click "Sbobina" durante il primo = comportamento indefinito
3. **Global model cache:** `_model` in `transcribe.py` — ok per performance, fragile per multi-process
4. **Progress:** `st.progress` vive solo nella sessione corrente
5. **Recovery:** se il processo muore a metà, job resta senza stato `failed` esplicito

---

## 2. Architettura target (v0.3+)

```
                    ┌─────────────────┐
                    │  Streamlit UI   │
                    │  (dashboard)    │
                    └────────┬────────┘
                             │ read/write
                    ┌────────▼────────┐
                    │  Job store      │
                    │  SQLite + files │
                    └────────┬────────┘
                             │ dequeue
                    ┌────────▼────────┐
                    │  sbobina worker │
                    │  (1 processo)   │
                    ├─────────────────┤
                    │ extract         │
                    │ transcribe      │
                    │ summarize       │
                    │ export          │
                    └─────────────────┘

Opzionale v0.5:
                    ┌─────────────────┐
                    │  FastAPI        │
                    │  POST /jobs     │
                    └────────┬────────┘
                             │
                    stesso Job store
```

### Perché separare worker

| Aspetto | Monolite Streamlit | Worker dedicato |
|---------|-------------------|-----------------|
| UI bloccata | Sì | No |
| Sopravvive refresh browser | No | Sì (job continua) |
| Riavvio UI senza kill job | No | Sì |
| Testabilità pipeline | Difficile | `worker.run_once()` |
| Deploy Docker | 1 container confuso | `ui` + `worker` chiari |

**Streamlit resta** per: upload, storico, download, impostazioni.  
**Non fa più** trascrizione inline nel callback del bottone.

---

## 3. Modello dati job v2

Estensione di `JobRecord` (`jobs.py`):

```python
@dataclass
class JobRecord:
    id: str
    stem: str
    source_name: str
    created_at: str
    output_dir: str

    # NUOVO
    status: str          # queued | running | completed | failed | cancelled
    phase: str           # idle | extract | load_model | transcribe | summarize | export
    progress_pct: float  # 0.0 .. 100.0
    progress_message: str
    queued_at: str
    started_at: str | None
    finished_at: str | None
    error: str
    input_path: str      # path assoluto file sorgente (in job dir)

    # esistente
    has_summary: bool
    summary_requested: bool
    summary_error: str
    transcript_chars: int
    tags: list[str]      # futuro
```

### Layout cartella job

```
data/output/jobs/20260626_153045/
  job.json              # stato aggiornato dal worker
  source.mp3            # copia input (o symlink)
  work/                 # temp ffmpeg, chunk wav
  trascrizione.txt
  sottotitoli.srt
  riassunto.txt
```

**Regola:** lo stato canonico è `job.json`. UI e API leggono solo quello (polling ogni 1–2 s durante `running`).

---

## 4. Coda: SQLite vs JSON

### Oggi: `index.json`

- Pro: semplice, leggibile
- Contro: race se worker + UI scrivono insieme; no query per `status=queued`

### Proposta v0.3: SQLite

File: `data/output/jobs/queue.db`

```sql
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    phase TEXT,
    progress_pct REAL DEFAULT 0,
    progress_message TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    queued_at TEXT,
    started_at TEXT,
    finished_at TEXT,
    source_name TEXT,
    stem TEXT,
    output_dir TEXT,
    input_path TEXT,
    summary_requested INTEGER DEFAULT 0,
    has_summary INTEGER DEFAULT 0,
    summary_error TEXT DEFAULT '',
    transcript_chars INTEGER DEFAULT 0,
    error TEXT DEFAULT ''
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created ON jobs(created_at DESC);
```

`index.json` può restare come cache/export o essere rimosso dopo migrazione.

### Operazioni worker

```text
LOOP:
  job = SELECT * FROM jobs WHERE status='queued' ORDER BY queued_at LIMIT 1
  IF job IS NULL: sleep(1); CONTINUE
  UPDATE jobs SET status='running', started_at=now() WHERE id=job.id
  TRY:
    run_pipeline(job)  # aggiorna phase + progress_pct via callback
    UPDATE status='completed', finished_at=now()
  EXCEPT:
    UPDATE status='failed', error=..., finished_at=now()
```

---

## 5. Pipeline worker (pseudocodice)

```python
def run_pipeline(job: JobRecord, config: TranscribeConfig) -> None:
    def on_progress(phase: str, pct: float, msg: str) -> None:
        update_job_progress(job.id, phase=phase, progress_pct=pct, progress_message=msg)

    on_progress("extract", 5, "Estrazione audio...")
    wav = prepare_audio(Path(job.input_path), work_dir=job.path / "work")

    on_progress("load_model", 15, "Caricamento modello NeMo...")
    result = transcribe(wav, config=config, work_dir=job.path / "work", on_progress=on_progress)

    on_progress("export", 85, "Salvataggio TXT e SRT...")
    export_txt(result, job.txt_path())
    export_srt(result, job.srt_path())

    if job.summary_requested:
        on_progress("summarize", 90, "Riassunto...")
        unload_model()
        summary = summarize(result.text, ...)
        export_summary_text(summary.text, job.summary_path())

    on_progress("export", 100, "Completato")
```

`transcribe()` va esteso con callback opzionale `on_progress` — per chunk: `pct = 20 + 60 * (i / n_chunks)`.

---

## 6. UI Streamlit adattata

### Flusso submit

```python
# Prima (v0.2): transcribe inline
if run and uploaded:
    result = transcribe(...)  # BLOCCA

# Dopo (v0.3):
if run and uploaded:
    job = enqueue_job(uploaded, options)  # scrive DB + file, status=queued
    st.success(f"In coda: {job.id}")
    st.rerun()

# Render separato
_render_queue_panel()   # jobs con status queued/running
_render_job_history()   # completed/failed
```

### Polling

```python
@st.fragment(run_every=2)  # Streamlit 1.33+
def live_queue():
    running = list_jobs(status_in=["queued", "running"])
    for job in running:
        st.progress(job.progress_pct / 100, text=job.progress_message)
```

Se `run_every` non disponibile: `st_autorefresh` o meta refresh leggero.

---

## 7. CLI unificata

```powershell
# Singolo file → stesso DB della UI
sbobina transcribe video.mp4
# → crea job, se worker attivo: queued; altrimenti: esegue sync con warning

sbobina worker                    # avvia loop coda
sbobina jobs list [--status queued]
sbobina jobs show 20260626_153045
sbobina jobs cancel 20260626_153045

sbobina batch data/input/*.mp3 --summarize
```

**Modalità sync (senza worker):** utile per script CI; `transcribe` esegue inline ma registra comunque il job.

---

## 8. Watch folder (v0.4)

```
data/input/inbox/     ← utente copia file qui
data/input/processed/ ← spostati dopo enqueue
data/input/failed/    ← formato non supportato / errore enqueue
```

Worker secondario o thread nel worker principale:

```python
WATCH_INTERVAL = 5  # secondi

def watch_inbox():
    for path in inbox.glob("*"):
        if path.suffix.lower() in ALLOWED:
            enqueue_from_path(path)
            path.rename(processed / path.name)
```

Opzione env: `SBOBINATOR_WATCH=1`, `SBOBINATOR_INBOX=/path`.

---

## 9. Docker compose target

```yaml
services:
  worker:
    build: ...
    command: sbobina worker
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    deploy:
      resources:
        limits:
          memory: 28G

  ui:
    build: ...
    command: sbobina ui --server.address 0.0.0.0
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    depends_on:
      - worker
```

Su mini PC AMD: solo profile `cpu`, un worker, niente GPU.

---

## 10. API FastAPI (v0.5) — sketch

```python
@app.post("/api/jobs")
async def create_job(file: UploadFile, summarize: bool = False):
    job = enqueue_upload(file, summary_requested=summarize)
    return {"id": job.id, "status": job.status}

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    return load_job(job_id)

@app.get("/api/jobs/{job_id}/files/{name}")
async def download(job_id: str, name: str):
    # name in ("trascrizione.txt", "sottotitoli.srt", "riassunto.txt")
    ...
```

Autenticazione: per LAN domestica può bastare `API_KEY` in env; per esposizione internet serve reverse proxy + auth (fuori scope v1).

---

## 11. Gestione memoria

| Fase | RAM tipica | Azione |
|------|------------|--------|
| Modello ASR caricato | 3–6 GB | Tenere in RAM tra job se coda piena |
| Riassunto mT5 | +1–2 GB | `unload_model()` prima (già fatto) |
| Chunk lungo | picco temporaneo | Un chunk alla volta, delete wav temp |

**Regola:** max 1 job `running` per worker. Scale orizzontale = più worker su più macchine (v1+, non v0.3).

---

## 12. Migrazione da v0.2 a v0.3

1. Script `migrate_jobs_v2.py`:
   - Legge `index.json` + cartelle esistenti
   - Inserisce in SQLite con `status=completed`
   - Aggiunge campi mancanti con default
2. UI supporta entrambi per una release, poi rimuove `index.json`
3. Documentare in README breaking change minimo (nessuna perdita dati)

---

## 13. Ordine implementazione consigliato

```
Settimana 1:
  - JobRecord v2 + SQLite schema
  - enqueue_job() senza esecuzione
  - migrate script

Settimana 2:
  - sbobina worker + pipeline con callback progress
  - job.json / DB aggiornati ogni fase

Settimana 3:
  - UI: submit → coda, pannello stato, polling
  - CLI transcribe → enqueue
  - Test: 3 file in coda, kill UI a metà, verifica recovery

Settimana 4:
  - ZIP export, delete job, wizard health
  - Docker worker+ui
  - Release v0.3
```

---

## 14. Alternative scartate (e perché)

| Alternativa | Perché no |
|-------------|-----------|
| Celery + Redis | Troppo pesante per uso domestico / mini PC |
| Tutto async in Streamlit | Streamlit non progettato per worker lunghi |
| Solo file JSON per coda | Race condition, no query |
| Multi-worker stesso host | OOM quasi certo con NeMo |
| Sostituire Streamlit subito con React | Costo alto; Streamlit ok come dashboard |

---

## Riferimenti codice attuale

| Modulo | Ruolo migrazione |
|--------|------------------|
| `jobs.py` | Estendere → `jobs/store.py` + SQLite |
| `ui/app.py` | Solo enqueue + render, no `transcribe()` |
| `transcribe.py` | Aggiungere `on_progress` callback |
| `cli.py` | Nuovi comandi `worker`, `jobs` |
| Nuovo `worker.py` | Loop coda + pipeline |
