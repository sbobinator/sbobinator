# Coda e storico job

## Due livelli di dati

| Livello | File | Ruolo |
|---------|------|-------|
| **Registro** | `data/output/jobs/queue.db` | Elenco job, stati, timestamp, path |
| **File** | `data/output/jobs/ID/` | Audio, trascrizione, SRT, riassunto |

L'interfaccia legge l'**elenco** dal DB e il **contenuto** dai file.

---

## Stati job

| Stato | Significato |
|-------|-------------|
| `queued` | In coda, in attesa |
| `running` | In elaborazione |
| `completed` | Finito con successo |
| `failed` | Errore (vedi `error` in job.json) |
| `cancelled` | Annullato dall'utente (solo da coda) |

---

## ID e cartelle

Formato: `YYYYMMDD_HHMMSS_nome-file`

Esempio: `20260628_102554_campione-italiano-breve`

Se collisione nello stesso secondo: suffisso `_2`, `_3`, ...

### Contenuto cartella job

```
20260628_102554_campione-italiano-breve/
├── source.wav           ← copia file caricato
├── job.json             ← mirror del record SQLite
├── trascrizione.txt
├── sottotitoli.srt
└── riassunto.txt        ← se richiesto e riuscito
```

---

## Coda FIFO

1. Upload → `enqueue_job()` → stato `queued`
2. Worker → `claim_next_job()` (atomico) → `running`
3. Pipeline → trascrizione + export + riassunto
4. Fine → `completed` o `failed`

Un solo job alla volta per worker.

---

## Duplicati

| Situazione | Comportamento |
|------------|---------------|
| Stesso nome file **in coda/running** | Saltato, messaggio warning |
| Stesso nome file **già completato** | **Nuovo** job, nuova cartella, nuova riga DB |
| Stesso contenuto, nome diverso | Trattato come file nuovo |

**Nessun overwrite** dei job precedenti.

---

## Riavvio applicazione

- `queue.db` persiste → sidebar mostra ancora i lavori
- Worker riparte e riprende job `queued`
- Job `running` orfani → recuperati in coda all'avvio worker

---

## Cancellare lo storico

```cmd
python scripts\clean_output.py
```

Rimuove cartelle job e `queue.db`. Non tocca `models/` né `data/input/`.

---

## Cancellare solo il DB ma tenere cartelle

Se cancelli solo `queue.db` manualmente: l'UI **non** elenca più i job, ma i file nelle cartelle restano su disco.

---

## Modulo Python

Logica in `src/sbobinator/jobs.py`:

- `load_index()` — tutti i job
- `load_active_queue()` — queued + running
- `get_job(id)` — singolo job
- `enqueue_job()` — nuovo job
- `requeue_job()` / `requeue_failed()` — ritenta falliti
