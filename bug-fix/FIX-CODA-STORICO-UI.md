# FIX-CODA-STORICO-UI — Coda, storico lavori e UX gestione job

> **File:** `bug-fix/FIX-CODA-STORICO-UI.md`  
> **Creato:** 2026-06-30  
> **Stato:** ✅ Implementato (2026-06-26)  
> **Correlato:** `TRACCIAMENTO-BUG.md`, `evolutive/ROADMAP-EVOLUTIVE.md`  
> **Priorità:** **P0** — blocca uso quotidiano da utente medio

---

## 1. Executive summary

L’utente segnala che la gestione **coda + storico lavori** è **confusa, poco user-friendly** e impedisce flussi naturali:

1. **Rielaborare** lo stesso file (es. prima senza riassunto, poi con riassunto) senza trucchi manuali.
2. **Capire** quali job esistono quando lo stesso `campione-italiano-medio.wav` compare **due volte** con ID diversi.
3. **Pulire** lo storico dalla UI senza cancellare cartelle a mano o toccare SQLite.
4. **Sincronizzare** DB e disco quando qualcuno elimina cartelle job manualmente.

Il backend (`jobs.py` + SQLite) è **corretto per persistenza** ma il **modello mentale UI** è sbagliato: mescola upload, coda attiva e archivio completo sulla stessa pagina, con deduplica upload troppo aggressiva e zero riconciliazione filesystem.

**Obiettivo refactor:** pagina dedicata **Coda & Storico**, azioni chiare (elimina, rielabora, annulla), sync DB↔disco automatica, messaggi che spiegano *perché* un file è stato saltato.

---

## 2. Caso reale utente (30/06/2026)

### 2.1 Job sul disco

| Cartella | `source_name` | `summary_requested` | `status` |
|----------|---------------|---------------------|----------|
| `20260630_121640_campione-italiano-medio` | `campione-italiano-medio.wav` | `false` | completed |
| `20260630_121709_campione-italiano-medio` | `campione-italiano-medio.wav` | `true` | completed |

Stesso nome file, **due job distinti** — comportamento **corretto** per design attuale (`new_job_id()` sempre univoco).

### 2.2 Problema percepito

- In sidebar **«I tuoi lavori»** compaiono **entrambi** con label simili → l’utente non capisce quale è quale.
- Al secondo caricamento, se un job con lo stesso `source_name` è ancora `queued`/`running`, l’upload viene **saltato** con messaggio generico *«Saltati (già in coda)»* — anche quando l’intento è **rielaborare** con impostazioni diverse.
- Non esiste modo UI di **eliminare** un job dallo storico o di **forzare riaccodamento** dal file già salvato.
- Se l’utente cancella cartelle a mano, la UI mostra ancora job fantasma dal DB.

---

## 3. Inventario bug (nuovi ID)

### BUG-QUEUE-021 — Deduplica upload per `source_name` blocca rielaborazione

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 📋 Aperto |
| **Severità** | Alta |
| **Segnalazione** | 30/06 — stesso file non si riaccoda; messaggio «già in coda» |

**Codice attuale** (`server.py` ~407):

```python
if is_source_in_active_queue(source_name):
    skipped.append(source_name)
    continue
```

`is_source_in_active_queue()` (`jobs.py` ~501) controlla solo job con `status IN (queued, running)` e **uguale `source_name`**.

**Comportamento:**

| Situazione | Risultato |
|------------|-----------|
| File già **completed** | ✅ Nuovo upload consentito → nuova cartella (duplicato storico) |
| File ancora **queued/running** | ❌ Saltato — anche se utente vuole nuove impostazioni |
| File **failed/cancelled** | ✅ Nuovo upload consentito |

**Problema UX:** non c’è distinzione tra *«duplicato accidentale nello stesso batch»* e *«voglio rifare questo file»*. Il messaggio non dice **quale job** blocca né offre *«rielabora comunque»*.

**Fix proposto:**

- Sostituire skip silenzioso con **scelta esplicita** o flag `force_requeue=1`.
- Oppure: pulsante **«Rielabora»** su job completato (nuovo job, stesso `source` da disco).
- Messaggio flash: *«`medio.wav` saltato: in elaborazione (job `20260630_121640_…`) — annulla quel job o attendi»*.

---

### BUG-QUEUE-022 — Stesso `source_name`, più job: UI non raggruppa né distingue

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 📋 Aperto |
| **Severità** | Alta (UX) |
| **Segnalazione** | 30/06 — due cartelle `campione-italiano-medio`, frontend confuso |

**Causa:** `load_index()` restituisce **tutti** i job; sidebar mostra `job.label` = `⏳/✅ nome (id)` senza:

- data/ora leggibile in evidenza
- badge «con/senza riassunto»
- raggruppamento per `source_name`
- indicazione «ultima versione» vs «vecchie run»

**Fix proposto:** pagina storico con colonne chiare + opzione «mostra solo ultima run per file».

---

### BUG-QUEUE-023 — Nessuna sincronizzazione DB ↔ filesystem

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 📋 Aperto |
| **Severità** | Alta |
| **Segnalazione** | 30/06 — eliminazione manuale cartelle non aggiorna UI |

**Causa:** SQLite (`queue.db`) è **source of truth**; cartelle job sono mirror via `_sync_job_json()`. Non esiste:

- `reconcile_jobs()` all’avvio / periodicamente
- stato `missing` / `orphaned` quando `output_dir` non esiste
- rimozione record DB quando cartella eliminata

**Effetti collaterali:**

- Job fantasma in sidebar
- `get_job()` + dettaglio possono puntare a path inesistenti
- Worker potrebbe fallire su job `queued` la cui cartella è stata cancellata

**Fix proposto** (`jobs.py`):

```python
def reconcile_jobs_with_disk() -> ReconcileReport:
    """
    - Cartella assente + job non running → status='missing' o DELETE
    - Cartella presente senza riga DB → import opzionale da job.json
    - job.json assente ma cartella presente → rigenera meta o marca orphan
    """
```

Chiamare in: `ensure_db()`, `lifespan` UI, prima di `load_index()` in pagina storico.

---

### BUG-QUEUE-024 — Nessuna eliminazione job da UI

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 📋 Aperto |
| **Severità** | Media-Alta |
| **Segnalazione** | 30/06 — pulizia solo manuale su disco/DB |

**Oggi:** solo `cancel_job()` per status `queued`. Nessun `delete_job()`.

**Fix proposto:**

- `DELETE` da SQLite + `shutil.rmtree(job.path)` (solo se non `running`)
- `POST /api/jobs/{id}/delete` con conferma HTMX
- «Elimina selezionati» / «Elimina completati più vecchi di N giorni» (opzionale fase 2)

---

### BUG-QUEUE-025 — Homepage sovraccarica: coda + upload + storico + dettaglio

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 📋 Aperto |
| **Severità** | Media (UX) |

**Oggi** (`index.html`):

| Sezione | Contenuto |
|---------|-----------|
| Stats | contatori |
| Coda elaborazione | solo attivi (HTMX poll) |
| Carica file | upload |
| Sidebar | **tutti** i job (storico completo) |
| Main | dettaglio job selezionato |

**Problema:** utente medio non distingue **coda attiva** vs **archivio**. La sidebar cresce senza limite e senza filtri.

**Fix proposto — nuova IA navigazione:**

```
/                 → Dashboard: upload + coda attiva (compatto) + ultimi 5 lavori
/jobs             → Storico completo (tabella, filtri, azioni bulk)
/jobs/{id}        → Dettaglio singolo job (opzionale, o panel su /jobs)
/settings/summary → (esistente)
```

---

### BUG-QUEUE-026 — Nessuna azione «Rielabora con impostazioni attuali»

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 📋 Aperto |
| **Severità** | Alta |
| **Segnalazione** | 30/06 — dimenticato riassunto al primo giro, non può rifare facilmente |

**Esigenza:** da job completato **senza** riassunto → un click **«Rielabora (riassunto ON)»** che:

1. Copia `source.wav` (già in cartella) o accetta nuovo upload
2. Crea **nuovo** `job_id` con impostazioni sidebar correnti
3. Non richiede delete manuale del job vecchio

**API proposta:**

```python
def enqueue_from_existing_source(
    source_job_id: str,
    *,
    summary_requested: bool,
    ...
) -> JobRecord
```

O: `requeue_as_new(job_id, **settings)` — sempre nuovo ID, mai overwrite.

---

### BUG-QUEUE-027 — Messaggi flash opachi su file saltati

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 📋 Aperto |
| **Severità** | Media |

**Oggi:** `Saltati+(gia+in+coda):+file.wav` — non indica job bloccante, né azioni possibili.

**Fix:** messaggio strutturato + link a job in coda o pulsante «annulla e riprova».

---

### BUG-QUEUE-028 — `requeue_job()` non copre completed

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 📋 Aperto |
| **Severità** | Media |

`requeue_job()` (`jobs.py` ~407) funziona solo per `failed` / `cancelled`. Job **completed** non si può rimettere in coda — serve **nuovo job** (BUG-QUEUE-026), non reuse ID.

---

### BUG-UX-029 — Label job poco informative

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 📋 Aperto |
| **Severità** | Media |

`JobRecord.label` include ID tecnico ma non evidenzia:

- `12:16` vs `12:17` (due medio)
- ✅ senza riassunto vs ✅ con riassunto
- durata / dimensione file

**Fix:** `display_title()` per UI + `technical_id` separato.

---

### BUG-UX-030 — Nessun indicatore «job inconsistente» (disco/DB)

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 📋 Aperto |
| **Severità** | Media |

Se `trascrizione.txt` manca ma status `completed` → UI dovrebbe mostrare ⚠️ inconsistenza e offrire elimina / rielabora.

---

## 4. Architettura attuale (riferimento)

```
Upload POST /enqueue
    → is_source_in_active_queue? skip
    → enqueue_job() → nuova cartella + INSERT SQLite
    → worker claim_next_job() FIFO

UI /
    → load_index() TUTTI i job → sidebar
    → /partials/queue → solo ACTIVE_STATUSES

Persistenza:
    queue.db (master)
    jobs/{id}/job.json (mirror)
    jobs/{id}/source.*, trascrizione.txt, ...
```

**Punti di forza da conservare:**

- ID cartella univoci (no overwrite)
- Coda FIFO SQLite
- Worker separato + `recover_orphaned_running_jobs()`
- Cancel solo su `queued` (corretto per sicurezza)

---

## 5. Architettura target

### 5.1 Modello dati

| Concetto | Definizione |
|----------|-------------|
| **Job** | Una esecuzione (1 ID, 1 cartella, 1 snapshot impostazioni) |
| **Sorgente logica** | `source_name` (può avere **N job** nel tempo) |
| **Coda attiva** | `status ∈ {queued, running}` |
| **Storico** | tutti gli alti stati + eventuale `missing` |

**Nuovo stato opzionale:** `missing` (record DB, cartella assente) — oppure **hard delete** del record su reconcile.

**Campi UI utili (non obbligatori in DB subito):**

- `deleted_at` (soft delete)
- `content_hash` / `file_size` (futuro: dedup intelligente)

### 5.2 Sync disco

```
ensure_db()
    → reconcile_jobs_with_disk()
        per ogni riga jobs:
            if not Path(output_dir).exists():
                if status == running: → recover to queued o failed
                else: → delete row OR status=missing
        per ogni cartella jobs/* con job.json:
            if id not in DB: → import_job_from_folder()
```

Eseguire anche ogni 30s sul poll HTMX storico (leggero: solo conteggio cartelle vs count DB).

### 5.3 Flussi utente target

#### A) Primo upload

Come oggi → nuovo job → coda.

#### B) Rielaborare stesso file (impostazioni diverse)

**Opzione 1 (consigliata):** pulsante **«Nuova elaborazione»** su job storico → crea nuovo job (nuovo ID), copia source dalla cartella precedente o chiede nuovo file.

**Opzione 2:** upload stesso filename mentre nessun job attivo → nuovo job (già funziona) + storico mostra «2 elaborazioni di medio.wav».

#### C) Upload mentre job attivo con stesso nome

- **Default:** avviso + link al job attivo
- **Conferma:** «Accoda comunque» → nuovo job in coda dietro quello attivo (FIFO) — **rimuovere** `is_source_in_active_queue` hard block, sostituire con warning + opt-in

#### D) Pulizia

- Elimina singolo job (disco + DB)
- Elimina tutti i `completed` selezionati
- «Pulisci record fantasma» (reconcile one-click)

### 5.4 Nuova pagina `/jobs`

**Layout proposto:**

| Colonna | Contenuto |
|---------|-----------|
| Stato | icona + testo |
| File | `source_name` |
| Quando | `created_at` / durata |
| Opzioni | riassunto sì/no, provider |
| Risultato | TXT / SRT / riassunto (link) |
| Azioni | Apri · Scarica · **Rielabora** · **Elimina** |

**Filtri:**

- Tutti / In coda / Completati / Falliti / Senza riassunto
- Cerca per nome file
- Raggruppa per `source_name` (accordion)

**Bulk:**

- Seleziona multipli → Elimina
- (fase 2) Esporta ZIP

### 5.5 Homepage semplificata

- Coda attiva (come ora)
- Upload
- **Ultimi 5 lavori** + link «Vedi tutti → /jobs»
- Rimuovere storico completo dalla sidebar (o collassare)

---

## 6. Piano implementazione a fasi

### Fase 1 — Backend fondamenta (P0)

| Task | File |
|------|------|
| `reconcile_jobs_with_disk()` | `jobs.py` |
| `delete_job(job_id, *, remove_files=True)` | `jobs.py` |
| `enqueue_from_job_source(job_id, **settings)` | `jobs.py` |
| Chiamata reconcile in `ensure_db()` / worker startup | `jobs.py`, `worker.py` |
| Test unitari reconcile + delete | `tests/test_jobs_reconcile.py` |

**Criteri accettazione:**

1. Elimino cartella a mano → dopo refresh UI job sparisce o marcato `missing` con pulsante pulizia.
2. `delete_job` rimuove DB + cartella.
3. «Rielabora» da job completato crea nuovo ID e accoda.

### Fase 2 — API + messaggi (P0)

| Endpoint | Azione |
|----------|--------|
| `POST /api/jobs/{id}/delete` | elimina |
| `POST /api/jobs/{id}/reprocess` | nuovo job da source esistente |
| `POST /api/jobs/reconcile` | sync manuale |
| `POST /enqueue` | warning invece di skip hard (param `allow_duplicate`) |

**Criteri:** flash spiegano job bloccante; nessun «saltato» senza motivo.

### Fase 3 — Pagina `/jobs` (P1)

| File | Azione |
|------|--------|
| `templates/jobs.html` | tabella storico |
| `templates/partials/jobs_table.html` | HTMX filtri |
| `server.py` | route `GET /jobs` |
| `static/style.css` | tabella, badge, azioni |

### Fase 4 — Homepage cleanup (P1)

- Sidebar: link navigazione (`Home`, `Coda & Storico`, `Impostazioni`)
- Rimuovere lista completa job da `/`
- Ultimi N job in dashboard

### Fase 5 — Raffinate UX (P2)

- Raggruppamento per `source_name`
- «Mostra solo ultima per file»
- Elimina completati > 30 giorni
- Export ZIP job
- Notifica browser a job completato (opzionale)

---

## 7. Altre migliorie UX implementabili (backlog facilità d’uso)

Oltre al refactor coda/storico, per **utente medio**:

| ID | Miglioria | Impatto | Effort |
|----|-----------|---------|--------|
| UX-031 | **Wizard primo avvio**: «Carica file → Spunta riassunto se vuoi → Accoda» con checklist visiva | Alto | Basso |
| UX-032 | **Badge persistente** in header: «Riassunto ON/OFF» prima di accodare | Alto | Basso |
| UX-033 | **Stima tempo** in coda («~3 min rimanenti» da media job precedenti) | Medio | Medio |
| UX-034 | **Notifica sonora / toast** a completamento job (HTMX trigger) | Medio | Basso |
| UX-035 | **Apri cartella** più visibile (non solo API) — pulsante su ogni job | Alto | Basso |
| UX-036 | **Drag & drop** area upload più grande con anteprima file selezionati | Medio | Basso |
| UX-037 | **Rinomina display** job (alias utente, es. «Lezione 3 — prof Rossi») | Medio | Medio |
| UX-038 | **Confronto run**: diff tra due riassunti dello stesso `source_name` | Medio | Medio |
| UX-039 | **Preset impostazioni** salvati («Solo trascrizione», «Riassunto DeepSeek», «Locale max qualità») | Alto | Medio |
| UX-040 | **Lingua / glossario utente** opzionale (correzioni ASR personali, non wiki) | Medio | Medio |
| UX-041 | **Mobile-friendly** tabella storico (card layout) | Medio | Medio |
| UX-042 | **Help contestuale** «Perché è stato saltato?» con link doc | Alto | Basso |
| UX-043 | **Pulsante «Riprova»** su job `failed` (già parziale via `requeue_job`) in UI storico | Alto | Basso |
| UX-044 | **Indicatore worker morto** se coda piena ma nessun progresso da N minuti | Alto | Medio |
| UX-045 | **Batch upload**: riepilogo pre-accoda (N file, riassunto sì/no, provider) | Alto | Basso |

---

## 8. Decisioni di prodotto da confermare

| # | Domanda | Proposta default |
|---|---------|------------------|
| D1 | Stesso file in coda due volte contemporaneamente? | **Sì**, con warning — utente sa cosa fa |
| D2 | Eliminare job `running`? | **No** — solo cancel poi delete |
| D3 | Job `missing` (cartella cancellata)? | **Auto-rimuovi record** al reconcile |
| D4 | Mantenere tutte le run storiche? | **Sì**, finché utente non elimina |
| D5 | Raggruppare per nome file di default? | **Sì** su `/jobs`, collassato |

---

## 9. Test manuali post-refactor

### Test T1 — Rielabora senza riassunto → con riassunto

1. Accoda `medio.wav` senza spunta → completed
2. Da `/jobs` → **Rielabora** con riassunto ON
3. Nuovo job ID, entrambi in storico, badge distinti

### Test T2 — Upload duplicato mentre in coda

1. Accoda file lungo
2. Prima che finisca, accoda stesso nome con «forza» o secondo job in coda
3. Nessun skip silenzioso; 2 job in coda FIFO

### Test T3 — Delete da UI

1. Elimina job completato da `/jobs`
2. Cartella sparita, riga DB sparita, sidebar pulita

### Test T4 — Reconcile dopo delete manuale

1. Elimina cartella job in Explorer
2. Refresh `/jobs` o attendi reconcile
3. Record sparisce o pulsante «Rimuovi record orfano»

### Test T5 — Utente medio 5 minuti

Persona non tecnica riesce a: caricare, capire coda, trovare risultato, rifare con riassunto, pulire vecchio job — **senza aprire SQLite**.

---

## 10. Riferimenti codice attuale

| Path | Ruolo |
|------|--------|
| `src/sbobinator/jobs.py` | SQLite, enqueue, `is_source_in_active_queue` |
| `src/sbobinator/ui/server.py` | `/enqueue`, partials, sidebar `load_index()` |
| `src/sbobinator/ui/templates/index.html` | UI monolitica |
| `src/sbobinator/ui/templates/partials/queue.html` | Solo coda attiva |
| `src/sbobinator/worker.py` | Worker FIFO |
| `scripts/clean_output.py` | Pulisce solo `jobs/*` (CLI, non UI) |

---

## 11. Cronologia documento

| Data | Modifica |
|------|----------|
| 2026-06-30 | Creazione documento da segnalazione utente (duplicati medio 121640/121709, skip coda, pulizia UI) |

---

*Prossimo passo: implementazione Fase 1–2 (backend + API), poi pagina `/jobs`.*
