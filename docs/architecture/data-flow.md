# Flusso dati

## Accodamento (UI o CLI)

```mermaid
sequenceDiagram
    participant U as Utente
    participant UI as Streamlit
    participant J as jobs.py
    participant DB as queue.db

    U->>UI: Upload + Accoda
    UI->>J: enqueue_job()
    J->>J: new_job_id()
    J->>J: copia source in cartella job
    J->>DB: INSERT job queued
    UI->>U: Messaggio successo
```

## Elaborazione

```mermaid
sequenceDiagram
    participant W as Worker
    participant J as jobs.py
    participant P as pipeline
    participant T as transcribe
    participant S as summarize

    W->>J: claim_next_job()
    J->>J: status = running
    W->>P: run_pipeline(job_id)
    P->>T: transcribe()
    T->>T: load Parakeet da models/
    P->>P: export TXT + SRT
    alt riassunto richiesto
        P->>S: summarize()
        P->>P: export riassunto.txt
    end
    P->>J: status = completed
```

## Lettura risultati (UI)

1. `load_index()` → lista job da SQLite
2. Utente seleziona job → `get_job(id)`
3. `job.txt_path().read_text()` → contenuto da disco

Il DB **non** contiene il testo trascritto — solo metadati e path.

## Variabili path

| Variabile | Default locale | Docker |
|-----------|----------------|--------|
| `SBOBINATOR_DATA` | `./data` | `/data` |
| `NEMO_CACHE_DIR` | `./models` | `/models` |

Vedi [Configurazione](../reference/configuration.md).
