# Tracciamento bug — Sbobinator

Documento aggiornato al **28 giugno 2026** (v0.3.0).  
Elenco sistematico dei bug rilevati durante sviluppo e test su Windows, con causa, impatto, stato e fix.

---

## Legenda stati

| Stato | Significato |
|-------|-------------|
| ✅ Risolto | Fix in codice, verificato o ragionevolmente coperto |
| 🔧 Parziale | Mitigazione in atto; limitazioni documentate |
| 📋 Aperto | Noto, fix pianificato |
| 🔍 In analisi | Causa individuata o verificata; fix non ancora applicato |
| ℹ️ Limitazione | Comportamento atteso / vincolo ambiente, non bug puro |

---

## Indice

1. [Bug segnalati dall'utente (sessione corrente)](#1-bug-segnalati-dallutente-sessione-corrente)
2. [Bug coda / upload — 28 giugno 2026](#2-bug-coda--upload--28-giugno-2026)
3. [Bug critici risolti in precedenza](#3-bug-critici-risolti-in-precedenza)
4. [Bug UI / UX](#4-bug-ui--ux)
5. [Bug ambiente Windows](#5-bug-ambiente-windows)
6. [Bug architettura / dati](#6-bug-architettura--dati)
7. [Rischi residui e backlog](#7-rischi-residui-e-backlog)
8. [Come testare le fix](#8-come-testare-le-fix)

---

## 1. Bug segnalati dall'utente (sessione corrente)

### BUG-UI-001 — Messaggio riassunto fuorviante

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | ✅ Risolto |
| **Severità** | Media |
| **Segnalazione** | Con "Genera riassunto" attivo, il tab Riassunto mostrava: *"Riassunto non generato. Attivalo nella sidebar e riesegui."* |

**Causa root:**  
Il messaggio non distingueva tre casi diversi:

1. Riassunto **disattivato** dall'utente
2. Riassunto **richiesto** ma **fallito** (es. errore SSL su mT5, eccezione Python)
3. Riassunto **richiesto** ma file non scritto per altri motivi

In tutti i casi 2 e 3 l'UI suggeriva di "attivare nella sidebar", anche se il toggle era già ON.

**Impatto:**  
Confusione, sensazione che l'app non funzioni nonostante impostazioni corrette.

**Fix (v0.2.x):**  
- Ogni lavoro salva `summary_requested`, `has_summary`, `summary_error` in `job.json`
- Il tab Riassunto mostra messaggi differenziati:
  - Toggle off → info "disattivato per questo lavoro"
  - Toggle on + errore → warning con testo errore
  - Toggle on + file mancante → warning generico (trascrizione comunque salvata)

**File:** `src/sbobinator/ui/app.py` → `_summary_tab_message()`

---

### BUG-DATA-002 — Perdita lavori precedenti (nessuna coda / storico)

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | ✅ Risolto |
| **Severità** | Alta |
| **Segnalazione** | Avviando `sbobinato2` prima di scaricare `sbobinato1`, il primo sparisce dall'interfaccia |

**Causa root:**

1. Un solo `filename` in `st.session_state`
2. Export in `data/output/{stem}.txt` — **stesso nome file = overwrite**
3. UI mostrava solo l'ultimo lavoro (o il file `.txt` più recente)
4. Download da browser non rimuove i file su disco, ma l'UI non permetteva di rivederli

**Impatto:**  
Perdita di accesso ai risultati precedenti; rischio overwrite se due file hanno lo stesso nome.

**Fix (v0.2.x):**  
Introdotto **registro lavori persistente**:

```
data/output/jobs/
  index.json
  20260626_194530_mio_video/
    job.json
    trascrizione.txt
    sottotitoli.srt
    riassunto.txt          (opzionale)
```

- Ogni sbobinata crea una cartella univoca (`YYYYMMDD_HHMMSS`)
- `index.json` elenca tutti i lavori (più recente in cima)
- Sidebar **"Storico lavori"** con selectbox per rivedere/scaricare qualsiasi lavoro
- **Nessun overwrite** tra lavori diversi

**File:** `src/sbobinator/jobs.py`, `src/sbobinator/ui/app.py`

**Nota:** File legacy in `data/output/*.txt` (prima del fix) non compaiono nello storico; restano su disco ma vanno migrati manualmente se servono.

---

## 2. Bug coda / upload — 28 giugno 2026

> **Contesto:** segnalati durante benchmark con 4 file (`breve`, `lungo`, `medio`, `molto-lungo`) mentre il worker elaborava.  
> **Verifica DB (read-only, 28/06 ~12:00):** 4 job totali, **1 riga per file**, nessun duplicato in `queue.db`.  
> Il triplo `molto-lungo` in UI **non** corrisponde a 3 record SQLite.

---

### BUG-QUEUE-016 — Stesso file mostrato più volte nel pannello coda

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 🔍 In analisi |
| **Severità** | Media |
| **Segnalazione** | `campione-italiano-molto-lungo.wav` compariva **3 volte** in "Coda elaborazione", stesso ID cartella `20260628_114944_campione-italiano-molto-lungo`, mentre `medio` compariva una volta |

**Sintomo osservato:**

```
▶️ campione-italiano-medio.wav — in elaborazione
⏳ campione-italiano-molto-lungo.wav — in coda   (x3, stesso job id)
```

**Evidenza tecnica:**

| Controllo | Risultato |
|-----------|-----------|
| `load_index()` su `queue.db` | 4 job: breve/lungo/medio `completed`, molto-lungo `running` — **nessun duplicato `source_name`** |
| Cartelle `jobs/` | Una cartella per stem, nessun suffisso `_2` / `_3` su molto-lungo |
| Conclusione | Probabile **bug di rendering UI**, non accodamento multiplo persistente |

**Cause probabili (ordinate per probabilità):**

1. **`_poll_queue_refresh()` + `st.rerun(scope="app")` ogni 2s** (`app.py` ~268–272)  
   Il fragment forza rerun globale mentre ci sono job attivi. Su alcune versioni Streamlit questo può produrre **widget duplicati** o sezioni ridisegnate senza reset, specialmente se combinato con `st.container(border=True)` nel loop coda.

2. **Più istanze Streamlit** sulla stessa porta (problema già visto in sessione) — l'utente potrebbe vedere stato incoerente o sovrapposto tra tab/processi. Meno probabile se il testo ripete lo **stesso** `job.id`.

3. **Doppio/triplo click "Accoda"** con file ancora visibili nell'uploader (vedi BUG-UI-017): anche se il DB deduplica, la UI potrebbe aver mostrato stati intermedi prima del `rerun` finale.

4. **Accodamento reale sovrascritto** — `enqueue_job` usa `ON CONFLICT(id) DO UPDATE` (`jobs.py` `_upsert_job`). Se per race `new_job_id()` generasse lo stesso ID due volte nello stesso secondo **prima** che esista la cartella, si aggiornerebbe una sola riga. Non spiega da solo **3 righe visive** con stesso ID.

**Codice coinvolto:**

| File | Funzione / rigione |
|------|-------------------|
| `src/sbobinator/ui/app.py` | `_render_queue_panel()` — loop `for job in active` |
| `src/sbobinator/ui/app.py` | `_poll_queue_refresh()` — `@st.fragment(run_every=2s)` + `st.rerun(scope="app")` |
| `src/sbobinator/jobs.py` | `load_active_queue()`, `enqueue_job()`, `new_job_id()` |

**Impatto:**  
Contatore "In coda" fuorviante, rischio di clic "Annulla" confusi, sensazione che l'ultimo file venga accodato N volte.

**Fix proposti (non applicati — worker in esecuzione):**

1. Spostare il refresh coda in un **fragment isolato** che ridisegna solo il pannello coda (senza `st.rerun(scope="app")` sull'intera app).
2. Oppure usare `st.status` / `st.empty()` con aggiornamento localizzato.
3. Deduplicare `active` in UI per `job.id` prima del render (mitigazione difensiva).
4. Aggiungere test: N file in un batch → `COUNT(*)` in DB = N righe uniche.

---

### BUG-UI-017 — File restano nell'area upload dopo l'accodamento

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 🔍 In analisi |
| **Severità** | Media |
| **Segnalazione** | Dopo "Accoda sbobinatura", i file caricati **rimangono visibili** nell'uploader mentre la coda elabora → confusione ("devo ricliccare?" / accodamenti multipli) |

**Comportamento atteso:**  
Dopo accodamento riuscito, l'area upload si svuota (come documentato in BUG-UX-008 per il completamento).

**Comportamento attuale (parziale):**  
Il codice **tenta** di svuotare incrementando `uploader_nonce` e chiamando `st.rerun()`:

```python
# app.py ~438-457
st.session_state["uploader_nonce"] += 1
...
st.rerun()
```

Chiave widget: `key=f"uploader_{st.session_state['uploader_nonce']}"`.

**Cause probabili:**

1. **Race con `_poll_queue_refresh`**: ogni 2s un `st.rerun(scope="app")` può intervenire **nella stessa finestra** del click "Accoda", prima o dopo l'incremento `uploader_nonce`, lasciando il widget col vecchio `key` e i file ancora in memoria del browser.

2. **Streamlit `file_uploader`**: il reset via cambio `key` non è immediato su tutti i browser; con `accept_multiple_files=True` il buffer può persistere fino al rerun "pulito".

3. **Click ripetuti mentre i file sono ancora visibili**: l'utente clicca di nuovo "Accoda" credendo che il primo non sia andato a buon fine → alimenta BUG-QUEUE-016 (anche se il DB salta i duplicati con `load_active_queue()`).

4. **Manca feedback persistente**: il messaggio `st.success` scompare al rerun del fragment; restano solo i file nell'uploader → sembra che nulla sia successo.

**Codice coinvolto:**

| File | Rigione |
|------|---------|
| `src/sbobinator/ui/app.py` | `uploaded_files` / `uploader_nonce` / `submitted` (~397–461) |
| `src/sbobinator/ui/app.py` | `_poll_queue_refresh()` — rerun globale ogni 2s |
| `src/sbobinator/jobs.py` | `is_source_in_active_queue()` — esiste ma **non usato** in UI (duplicata logica inline) |

**Nota:** la deduplica in UI (`any(j.source_name == source_name for j in load_active_queue())`) **funziona a livello DB** nella run verificata; il problema principale è **UX**, non perdita dati.

**Fix proposti (non applicati):**

1. Dopo accodamento: `st.session_state.pop` esplicito + `uploader_nonce += 1` + **disabilitare** il bottone "Accoda" finché `uploaded_files` non è un set nuovo.
2. Mostrare banner fisso "N file in coda" sopra l'uploader (non solo `st.success` effimero).
3. Sostituire `st.rerun(scope="app")` del fragment con refresh solo del blocco coda.
4. Usare `is_source_in_active_queue()` da `jobs.py` + dedup `uploaded_files` per `name` prima del loop.
5. Opzionale: vincolo DB `UNIQUE(source_name)` per stati `queued|running` (enforcement server-side).

**Come riprodurre (test post-elaborazione):**

1. Carica 4 wav, clicca Accoda una volta.
2. **Senza ricaricare la pagina**, verifica se i 4 file sono ancora nell'uploader.
3. Controlla `SELECT id, source_name, status FROM jobs` — confronta con righe nel pannello coda.
4. Ripeti con un solo file (es. molto-lungo) e doppio click rapido su Accoda.

---

### BUG-SUM-019 — Riassunto mT5 inutilizzabile (token `<extra_id_0>`, ripetizioni, testo nonsense)

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | ✅ Risolto (v0.3.1) — sostituito con `gsarti/it5-small-news-summarization` |
| **Severità** | Critica (qualità prodotto) |
| **Segnalazione** | 28/06 benchmark: modalità `abstractive` su 4 campioni; output non professionale |

**Output reali in `data/output/jobs/20260628_114944_*/riassunto.txt`:**

| File | Riassunto mT5 (estratto) |
|------|--------------------------|
| breve | `<extra_id_0>...` + ripetizione frase intera |
| lungo | Wikimedia / `oggi - oggi - oggi` senza senso |
| medio | `Alberto Cavaliere.` x6 |
| molto-lungo | Frasi spezzate, non riassunto |

**Causa root:** ~85% scelta nostra (`google/mt5-small` **base**, non fine-tuned summarization); ~10% integrazione (`pipeline("summarization")` + prefisso `summarize:`); ~5% modello Google (prodotto sbagliato per il task, non difettoso). Vedi [google/mt5-small](https://huggingface.co/google/mt5-small): *must be fine-tuned before downstream task*.

**Fix applicato:** `google/mt5-small` rimosso; IT5 fine-tuned italiano; prefisso `summarize:` eliminato; UI rinominata Sintesi / Riassunto (IT5).

---

### BUG-SUM-020 — Qualità riassunti insufficiente per uso produzione

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 🔍 In analisi — benchmark offline creato, fix non ancora definito |
| **Severità** | **Critica (qualità prodotto)** |
| **Segnalazione** | 28/06 — utente: riassunti «non soddisfacenti»; 5 righe su testo da 600 parole che non spiegano il contenuto; rischio rimozione feature se non migliora |

**Sintomi osservati:**

| Problema | Esempio |
|----------|---------|
| Riassunto troppo corto | Testo lungo (~600+ parole) → poche frasi in output |
| Bassa copertura semantica | Punti chiave dell'intervista/trascritto assenti o accennati |
| IT5 deforma il senso | Output con frasi incoerenti, mix di concetti, finali nonsense (es. job `campione-italiano-lungo`) |
| Estrattivo = frasi sparse | LexRank seleziona frasi ma non «riassume» in senso umano |

**Cause probabili (da confermare con benchmark):**

1. **IT5 news** (`gsarti/it5-small-news-summarization`) addestrato su articoli giornalistici, non su parlato/trascritti/interviste Wikimedia.
2. **`estimate_abstractive_lengths` / `max_length`** troppo bassi per testi lunghi.
3. **Sintesi estrattiva** per design non genera testo nuovo — su monologhi lunghi sembra un taglio, non un riassunto.
4. **Chunking IT5** (3000 char) + riassunto dei chunk può perdere filo narrativo.

**Strumento di valutazione (senza UI):**

```cmd
python scripts/summary_benchmark.py
```

Output: `docs/summary-benchmark/runs/<timestamp>/` — confronto di tutte le combinazioni `extractive|abstractive` × `auto|short|normal|detailed` su ogni `trascrizione.txt` in `data/output/jobs/`.

**Criteri di accettazione (proposta utente):**

- Proporzione lunghezza sensata rispetto al sorgente (non 5 righe fisse su 600 parole).
- Copertura dei concetti principali leggibile da un umano senza leggere la trascrizione intera.
- Nessuna deformazione grave del significato.

**Possibili direzioni (non implementate — solo backlog):**

- Modello IT5/wiki o mBART/LED per testi lunghi e parlato.
- Parametri lunghezza più aggressivi su `detailed` / `auto`.
- Riassunto gerarchico (map-reduce) con prompt dedicati al parlato.
- Valutare se mantenere solo sintesi estrattiva + rimuovere IT5 se benchmark fallisce.

**→ Roadmap completa LLM locale:** vedi [`FIX-RIASSUNTO-LLM.md`](FIX-RIASSUNTO-LLM.md) (decisione 28/06/2026: sostituire approccio con Qwen CPU, gate 16 GB, analisi token).

---

### BUG-ARCH-020 — Streamlit inadatto a un prodotto in produzione (migrazione UI)

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 🔧 In corso — migrazione a **FastAPI + HTMX + Jinja2** |
| **Severità** | **Critica (architettura / UX)** |
| **Segnalazione** | 28/06 — utente: *«se la UI crea così tanti problemi di usabilità la cambi»*; frustrazione esplicita con Streamlit |

**Sintomi accumulati (tutti legati al modello Streamlit, non al backend jobs):**

| ID | Problema | Causa Streamlit |
|----|----------|-----------------|
| BUG-QUEUE-016 | Stesso job mostrato più volte in coda | `st.rerun(scope="app")` + fragment che ridisegna l'intera pagina |
| BUG-UI-017 | File restano nell'uploader dopo accoda | Reset widget via `key` + rerun globale inaffidabile |
| BUG-UI-019 | Pulsante **Annulla** non risponde | Race tra poll ogni 2s e click utente |
| BUG-ENV-018 | `ImportError data_dir` con codice aggiornato | Processi Streamlit stale, cache moduli, istanze multiple porta 8501 |
| — | Impossibile cambiare riassunto su job già accodati | `session_state` + impostazioni sidebar non legate al job in modo esplicito |
| — | Sensazione generale di UI «rotta» / non professionale | Paradigma rerun top-down, stato widget opaco, debug difficile |

**Perché Streamlit non va bene qui:**

1. **Rerun globale** — ogni interazione (o poll automatico) riesegue lo script dall'alto; i click si perdono, i widget si duplicano, l'uploader non si svuota.
2. **Stato implicito** — `session_state`, chiavi widget, fragment: fragile e difficile da testare.
3. **Produzione** — nessun controllo HTTP reale, difficile deployare dietro reverse proxy, API REST separata impossibile senza duplicare logica.
4. **Manutenzione** — ogni fix UX è un workaround (`on_click`, `uploader_nonce`, dedup difensivo) invece di comportamento naturale del browser.

**Decisione architetturale:**

| Prima | Dopo |
|-------|------|
| Streamlit (`app.py`) | **FastAPI** (`server.py`) + **Jinja2** + **HTMX** (poll coda via `hx-trigger="every 2s"`) |
| `streamlit run` porta 8501 | `uvicorn sbobinator.ui.server:app` porta 8501 (stesso URL per l'utente) |
| Click → rerun script | Click → `POST` HTTP → risposta HTML parziale (nessuna race) |

**File coinvolti:**

| File | Azione |
|------|--------|
| `src/sbobinator/ui/server.py` | **Nuovo** — app FastAPI |
| `src/sbobinator/ui/templates/` | **Nuovo** — HTML + partials HTMX |
| `src/sbobinator/ui/static/style.css` | **Nuovo** — stile (stesso look scuro) |
| `src/sbobinator/ui/launch.py` | Avvia uvicorn invece di streamlit; `SBOBINATOR_UI_HOST` per Docker |
| `docker/Dockerfile.*` | `pip install -e ".[ui,summarize]"`, FastAPI |
| `docker/docker-compose.yml` | `SBOBINATOR_UI_HOST=0.0.0.0`, healthcheck HTTP |
| `src/sbobinator/ui/app.py` | **Deprecato** — rinominato, non più entry point |
| `pyproject.toml` | `ui` extra: `fastapi`, `uvicorn`, `jinja2`, `python-multipart` al posto di `streamlit` |

**Backend invariato:** `jobs.py`, `worker.py`, `pipeline.py`, SQLite — solo il layer presentazione cambia.

**Criteri di accettazione migrazione:**

1. Accoda N file → uploader si svuota dopo submit (redirect 303).
2. Annulla job in coda → funziona al primo click, senza poll che mangia l'evento.
3. Coda si aggiorna ogni 2s senza ricaricare tutta la pagina.
4. Storico lavori, download TXT/SRT/riassunto, impostazioni riassunto prima dell'accodamento.
5. `python scripts/restart_ui.py` avvia la nuova UI su `http://localhost:8501`.

---

### BUG-ENV-018 — ImportError `data_dir` con istanza Streamlit stale

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 🔧 Parziale |
| **Severità** | Alta |
| **Segnalazione** | `cannot import name 'data_dir' from sbobinator.config` con path sorgente corretto |

**Causa root:**  
Processo Streamlit avviato **prima** di aggiornamenti codice / più istanze su porta 8501 → moduli Python in cache inconsistenti. Il sorgente contiene `data_dir`; l'import fallisce solo nel processo vecchio.

**Fix (v0.3.0):**  
`process_guard.py`, `restart_ui.py` migliorato, kill porta 8501, `verify_runtime()`, `.streamlit/config.toml` con `fastReruns = false`.

**Residuo:**  
Serve sempre `python scripts/restart_ui.py` dopo `git pull`, non basta F5 browser.

---

## 3. Bug critici risolti in precedenza

### BUG-ENV-001 — SSL HuggingFace su Windows

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | 🔧 Parziale |
| **Severità** | Critica (bloccante) |

**Sintomo:**  
`SSLCertVerificationError` scaricando `parakeet-tdt-0.6b-v3.nemo` da huggingface.co.

**Causa:**  
Python su Windows non valida correttamente i certificati SSL (antivirus, proxy, store certificati).

**Fix:**  
- Script `scripts/download-model.ps1` usa `curl.exe` (certificati Windows)
- `transcribe.py` carica modello locale da `models/` con `restore_from()` se presente
- `config.local_model_path()` risolve path assoluto da root progetto

**Residuo:**  
Download automatico da Python/HuggingFace ancora fallisce. mT5 per riassunto "Qualità" può avere lo stesso problema.

---

### BUG-PATH-002 — Modello locale non trovato (path relativo)

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | ✅ Risolto |
| **Severità** | Critica |

**Sintomo:**  
Modello da 2.4 GB presente in `models/` ma app tentava ancora download HuggingFace.

**Causa:**  
`models/` era path **relativo alla cwd**. Streamlit parte da directory diverse → `local_model_path()` restituiva `None`.

**Fix:**  
`project_root()` in `config.py` → path assoluto `C:\...\sbobinator\models\...`

---

### BUG-UI-003 — Risultati non mostrati dopo trascrizione OK

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | ✅ Risolto (prima iterazione) → migliorato con BUG-DATA-002 |
| **Severità** | Alta |

**Sintomo:**  
"Completato!" verde ma nessun testo in pagina.

**Causa:**  
Dopo 1–2 minuti di elaborazione, Streamlit perde `session_state` o oggetti `TranscriptResult` non serializzabili; la sezione risultati non si renderizzava.

**Fix iniziale:**  
Salvataggio su disco + `st.rerun()` + testo in session_state.

**Fix definitivo:**  
Sistema lavori con lettura da file su disco (BUG-DATA-002).

---

### BUG-IMPORT-004 — `SummaryLength` ImportError

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | ✅ Risolto |
| **Severità** | Alta |

**Sintomo:**  
`cannot import name 'SummaryLength' from sbobinator.summarize`

**Causa:**  
Cache modulo Streamlit + import da modulo sbagliato durante hot-reload.

**Fix:**  
`SummaryLength` e `SummaryMode` spostati in `config.py`.

---

### BUG-DEPS-005 — NeMo non installato

| Campo | Dettaglio |
|-------|-----------|
| **Stato** | ✅ Risolto (ambiente utente) |
| **Severità** | Alta |

**Sintomo:**  
`Dipendenze ASR mancanti`

**Causa:**  
Solo pacchetto base installato (`pip install -e .`), senza `[local]` / `nemo_toolkit[asr]`.

**Fix:**  
`scripts/install-local.ps1` e documentazione README.

---

## 4. Bug UI / UX

### BUG-UX-006 — Slider "Frasi nel riassunto" rigido

| Stato | ✅ Risolto |
|-------|-----------|

Sostituito con "Lunghezza riassunto" automatica (auto/breve/normale/dettagliato) proporzionale al testo.

---

### BUG-UX-007 — Nessun feedback durante caricamento modello (1–2 min)

| Stato | 🔧 Parziale |
|-------|-------------|

Progress bar presente ma non distingue "caricamento modello" vs "trascrizione".  
**Backlog:** timer stimato, % basata su fase.

---

### BUG-UX-008 — `st.rerun()` fa perdere contesto upload

| Stato | 🔍 In analisi (aggiornato 28/06) |
|-------|----------------------------------|

Dopo completamento, il file uploader si svuota. I risultati sono nello storico lavori, non nell'uploader.

**Aggiornamento 28/06:** l'utente segnala che i file **restano** nell'uploader anche **dopo** l'accodamento (non solo dopo completamento). Vedi **BUG-UI-017** — il nonce + rerun non basta in presenza del fragment di poll.

---

## 5. Bug ambiente Windows

### BUG-WIN-009 — `curl` download interrotto (exit 56)

| Stato | 🔧 Parziale |
|-------|-------------|

Connessione reset durante download 2.4 GB.  
**Mitigazione:** `curl -C -` per resume in `download-model.ps1`.

---

### BUG-WIN-010 — Più interpreti Python (3.12 / 3.13)

| Stato | ℹ️ Documentare |
|-------|----------------|

`sbobina.exe` può puntare a Python diverso da quello usato in IDE.  
**Raccomandazione:** usare sempre `.venv` del progetto o `install-local.ps1`.

---

### BUG-WIN-011 — Riassunto mT5 richiede download HuggingFace

| Stato | 📋 Aperto |
|-------|-----------|

Modalità "Qualità (mT5)" può fallire con stesso errore SSL.  
**Workaround:** usare "Veloce (estrativo)".  
**Backlog:** bundle mT5 locale o script download analogo a Parakeet.

---

## 6. Bug architettura / dati

### BUG-ARCH-012 — Export CLI sovrascrive per `stem` uguale

| Stato | 📋 Aperto (solo CLI) |
|-------|----------------------|

`sbobina transcribe video.mp4 -o data/output` sovrascrive `video.txt` se rieseguito.  
**Backlog:** allineare CLI al sistema `jobs/` della UI.

---

### BUG-ARCH-013 — Nessuna coda elaborazione concorrente

| Stato | ✅ Risolto (v0.3.0) |
|-------|----------------------|

Coda SQLite + worker subprocess. Vedi `jobs.py`, `worker.py`. Nuovi bug coda in sezione 2 (BUG-QUEUE-016, BUG-UI-017).

---

### BUG-ARCH-014 — Modello ASR in RAM tra job

| Stato | ℹ️ By design |
|-------|--------------|

`unload_model()` chiamato solo prima del riassunto. Modello resta in RAM tra trascrizioni nella stessa sessione (veloce ma ~3–6 GB RAM).

---

### BUG-ARCH-015 — File legacy `data/output/*.txt` fuori storico

| Stato | 📋 Aperto |
|-------|-----------|

Trascrizioni pre-fix (flat in `data/output/`) non in `index.json`.  
**Backlog:** script migrazione `scripts/migrate-legacy-jobs.ps1`.

---

## 7. Rischi residui e backlog

### Priorità alta (prossime release)

| ID | Task |
|----|------|
| P0 | **BUG-ARCH-020** — Migrazione UI Streamlit → FastAPI (in corso) |
| P1 | **BUG-UI-017** — Svuotare uploader dopo accoda (risolto con redirect POST) |
| P1 | **BUG-QUEUE-016** — Refresh coda senza rerun globale (risolto con HTMX partial) |
| P1 | Allineare CLI al registro `jobs/` |
| P2 | Script migrazione output legacy |
| P2 | Messaggio progress più dettagliato (fase + tempo) |

### Priorità media

| ID | Task |
|----|------|
| P3 | Coda job — fix UX duplicati visivi (BUG-QUEUE-016) |
| P3 | Pulsante "Elimina lavoro" nello storico |
| P3 | Export ZIP di un lavoro (txt+srt+riassunto) |

### Priorità bassa

| ID | Task |
|----|------|
| P4 | Watch folder automatico |
| P4 | API REST con stesso backend jobs |
| P4 | Diarizzazione (chi parla) |

---

## 8. Come testare le fix

### Test BUG-QUEUE-016 / BUG-UI-017 (coda + upload)

1. `python scripts/restart_ui.py` — una sola istanza
2. Carica 4 file, un solo click "Accoda"
3. Verifica: uploader **vuoto**; pannello coda con **4 righe distinte** (1 per file)
4. `python -c "from sbobinator.jobs import load_active_queue; ..."` — stesso conteggio
5. Con file ancora in uploader, riclicca Accoda → warning "Saltati", **nessuna** nuova riga in DB

### Test BUG-DATA-002 (storico / no overwrite)

1. Sbobina `file_A.wav` → verifica cartella `data/output/jobs/YYYYMMDD_HHMMSS_*/`
2. Sbobina `file_B.wav` senza scaricare A
3. Sidebar → Storico: devono comparire **entrambi**
4. Seleziona A → testo di A ancora visibile e scaricabile

### Test BUG-UI-001 (messaggio riassunto)

1. Attiva riassunto, modalità **estrativo** → tab Riassunto con testo
2. Attiva riassunto, modalità **mT5** su Windows con SSL rotto → messaggio errore, **non** "attivalo nella sidebar"
3. Disattiva riassunto → messaggio "disattivato per questo lavoro"

### Test BUG-PATH-002 + ENV-001 (modello locale)

```powershell
# Verifica path
python -c "from sbobinator.config import local_model_path; print(local_model_path())"
# Deve stampare path assoluto .nemo ~2400 MB
```

### Test regressione trascrizione

```powershell
sbobina transcribe data/input/campione-italiano-breve.wav -o data/output
# oppure UI: upload + Sbobina
```

---

## Cronologia modifiche documento

| Data | Modifica |
|------|----------|
| 2026-06-28 | BUG-QUEUE-016, BUG-UI-017, BUG-ENV-018; verifica DB benchmark; aggiornamento v0.3.0 |
| 2026-06-26 | Creazione documento; fix BUG-UI-001, BUG-DATA-002; inventario bug sessione |

---

## Riferimenti file

| Componente | Path |
|------------|------|
| UI Streamlit | `src/sbobinator/ui/app.py` |
| Registro lavori | `src/sbobinator/jobs.py` |
| Config / path | `src/sbobinator/config.py` |
| Trascrizione | `src/sbobinator/transcribe.py` |
| Download modello | `scripts/download-model.ps1` |
| Install locale | `scripts/install-local.ps1` |
| Output lavori | `data/output/jobs/` |
