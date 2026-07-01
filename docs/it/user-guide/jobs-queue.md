# Coda e storico job

## Due livelli di dati

| Livello | File | Ruolo |
|---------|------|-------|
| **Registro** | `data/output/jobs/queue.db` | Elenco job, stati, timestamp, path |
| **File** | `data/output/jobs/ID/` | Audio, trascrizione, SRT, riassunto |

L'interfaccia legge l'**elenco** dal DB e il **contenuto** dai file. All'avvio (UI e worker) viene eseguita una **sincronizzazione** tra DB e disco (`reconcile_jobs_with_disk()`).

---

## Interfaccia: Home vs Coda & storico

| Pagina | URL | Contenuto |
|--------|-----|-----------|
| **Home** | `/` | Upload, coda attiva (polling), ultimi **8** job in sidebar |
| **Coda & storico** | `/jobs` | Tabella completa, filtri, ricerca, azioni su ogni job |
| **Dettaglio job** | `/jobs/{id}` | Trascrizione, riassunto, download, progresso live, azioni |

La sidebar in home mostra label leggibili, ad es. `campione.wav 12:17 · riassunto` o `· solo trascrizione` (`JobRecord.display_title()`). Ogni voce apre **`/jobs/{id}`**.

### Dettaglio job (`/jobs/{id}`)

Pagina dedicata: breadcrumb, trascrizione, riassunto, download, azioni. Job **in corso**: barra progresso HTMX con reload automatico al termine. Dalla tabella in `/jobs`: clic su **nome file** o **Apri**.

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

## Duplicati e re-upload

| Situazione | Comportamento |
|------------|---------------|
| Stesso nome file **in coda/running** | Saltato di default; messaggio flash con ID del job bloccante |
| Stesso nome + checkbox **«Accoda comunque»** | Nuovo job accodato anche se attivo |
| Stesso nome file **già completato** | **Nuovo** job, nuova cartella, nuova riga DB |
| Stesso contenuto, nome diverso | Trattato come file nuovo |

**Nessun overwrite** dei job precedenti. Due elaborazioni dello stesso file (es. con e senza riassunto) producono **due cartelle** distinte — è normale; usa `/jobs` per distinguerle.

---

## Azioni da UI

Disponibili in **`/jobs/{id}`** (e in tabella `/jobs` per azioni rapide):

| Azione | Quando | Effetto |
|--------|--------|---------|
| **Annulla** | Solo `queued` | Stato `cancelled` |
| **Riprova** | `failed` / `cancelled` | `requeue_job()` — stesso job, stessi file |
| **Rielabora** | `completed` | `reprocess_job()` — **nuovo** job (solo trascrizione) |
| **+ Riassunto** | `completed` | `reprocess_job()` con riassunto attivo |
| **Elimina** | Non `running` | Rimuove record DB e cartella su disco |
| **Sincronizza disco** | Sempre | `reconcile_jobs_with_disk()` |

### Sincronizzazione DB ↔ disco

`reconcile_jobs_with_disk()`:

- **Rimuove** dal DB i job la cui cartella non esiste più (es. cancellazione manuale)
- **Importa** cartelle con `job.json` ma senza record in SQLite
- Segna **failed** i job `running` la cui cartella è stata eliminata

Eseguita all'avvio UI/worker e su richiesta con **Sincronizza disco** in `/jobs`.

---

## Riavvio applicazione

- `queue.db` persiste → sidebar e `/jobs` mostrano ancora i lavori
- Worker riparte e riprende job `queued`
- Job `running` orfani → recuperati in coda all'avvio worker
- Reconcile allinea DB e cartelle dopo crash o pulizia manuale

---

## Cancellare lo storico

```cmd
python scripts\clean_output.py
```

Rimuove cartelle job e `queue.db`. Non tocca `models/` né `data/input/`.

Per singoli job usa **Elimina** in `/jobs` invece di cancellare manualmente le cartelle.

---

## Modulo Python

Logica in `src/sbobinator/jobs.py`:

| Funzione | Descrizione |
|----------|-------------|
| `load_index()` | Tutti i job (opz. `limit`, filtri stato) |
| `load_active_queue()` | queued + running |
| `get_job(id)` | Singolo job |
| `enqueue_job()` | Nuovo job |
| `find_active_jobs_by_source(name)` | Job attivi con stesso nome file |
| `is_source_in_active_queue(name)` | Shortcut booleano sui duplicati in coda |
| `requeue_job()` / `requeue_failed()` | Ritenta falliti/annullati |
| `reprocess_job()` | Nuova elaborazione da file già salvato |
| `delete_job()` | Elimina DB + cartella |
| `reconcile_jobs_with_disk()` | Allinea SQLite e filesystem |
| `cancel_job()` | Annulla se queued |

`JobRecord`: `display_title()`, `folder_exists()`, path `txt_path()`, `srt_path()`, `summary_path()`.
