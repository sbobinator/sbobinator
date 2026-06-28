# Schema job e database

## Stati job

| Stato | Significato |
|-------|-------------|
| `queued` | In attesa nel worker |
| `running` | Elaborazione in corso |
| `completed` | Trascrizione (e riassunto se richiesto) terminati |
| `failed` | Errore irreversibile nella pipeline |
| `cancelled` | Annullato dall'utente (solo da queued) |

## Fasi (`phase`)

Durante `running`, la pipeline aggiorna `phase` e `progress_pct`:

| Fase | Descrizione |
|------|-------------|
| `idle` | Iniziale |
| `extract` | Estrazione audio da video |
| `transcribe` | ASR NeMo |
| `summarize` | Riassunto |
| `export` | Scrittura file finali |
| `done` | Completato |

## Tabella SQLite `jobs`

File: `data/output/jobs/queue.db`

| Colonna | Tipo | Descrizione |
|---------|------|-------------|
| `id` | TEXT PK | `YYYYMMDD_HHMMSS_stem` |
| `stem` | TEXT | Nome file senza estensione |
| `source_name` | TEXT | Nome file originale |
| `created_at` | TEXT | ISO timestamp creazione |
| `output_dir` | TEXT | Path assoluto cartella job |
| `input_path` | TEXT | Path copia sorgente nel job |
| `status` | TEXT | Stato corrente |
| `phase` | TEXT | Fase pipeline |
| `progress_pct` | REAL | 0–100 |
| `progress_message` | TEXT | Messaggio UI |
| `queued_at` | TEXT | Accodamento |
| `started_at` | TEXT | Inizio elaborazione |
| `finished_at` | TEXT | Fine (successo o errore) |
| `error` | TEXT | Errore pipeline |
| `has_summary` | INTEGER | 1 se riassunto salvato |
| `summary_requested` | INTEGER | 1 se richiesto |
| `summary_error` | TEXT | Errore solo riassunto |
| `transcript_chars` | INTEGER | Lunghezza testo |
| `model_name` | TEXT | Modello NeMo usato |
| `device` | TEXT | cpu / cuda |
| `summary_mode` | TEXT | extractive / abstractive |
| `summary_length` | TEXT | auto / short / normal / detailed |

Indici: `idx_jobs_status`, `idx_jobs_created`.

## File per job

Cartella: `data/output/jobs/YYYYMMDD_HHMMSS_stem/`

| File | Contenuto |
|------|-----------|
| `source.*` | Copia file caricato |
| `job.json` | Mirror JSON del record SQLite |
| `trascrizione.txt` | Testo completo |
| `sottotitoli.srt` | Sottotitoli con timestamp |
| `riassunto.txt` | Riassunto (se generato) |
| `work/` | Temporanei (WAV, chunk) — può restare |

## ID job

Formato: `{timestamp}_{stem_sanitized}`

Esempio: `20260628_143022_campione-italiano-lungo`

Lo `stem` è troncato e ripulito da caratteri non sicuri per il filesystem.

## Migrazione

All'avvio, se esiste il vecchio `index.json` e `queue.db` è vuoto, i record vengono importati automaticamente.
