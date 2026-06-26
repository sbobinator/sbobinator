# Roadmap evolutive — Sbobinator

Documento principale di pianificazione.  
**Versione:** 0.1 · **Data:** 26 giugno 2026 · **Base:** v0.2.0 (UI Streamlit + jobs persistenti)

---

## 1. Perché serve evolvere

Sbobinator oggi risolve **un problema** (audio/video → testo in italiano in locale) ma non **un flusso di lavoro**.

### Cosa funziona (non toccare senza motivo)

| Capacità | Stato |
|----------|-------|
| Trascrizione IT con Parakeet v3 | ✅ Verificata |
| Export TXT + SRT | ✅ |
| Riassunto estrattivo offline | ✅ |
| Storico lavori su disco (`jobs/`) | ✅ |
| Modello locale + script download Windows | ✅ |
| Chunking file lunghi (>30 min) | ✅ In codice, poco visibile in UI |
| Docker CPU/GPU | 🔧 Esiste, da riallineare |

### Cosa è troppo limitato

| Limite | Effetto sul utente |
|--------|-------------------|
| **Un job alla volta, UI bloccante** | Non può accodare; deve restare con il browser aperto |
| **Un file per upload** | 10 riunioni = 10 cicli manuali |
| **Streamlit come runtime** | Rerun, session state, difficile worker in background |
| **CLI separata dalla UI** | Output flat, overwrite, niente storico |
| **Nessuna automazione** | Niente cartella inbox, niente API |
| **Testo read-only** | Correzioni solo in editor esterno |
| **Progress opaco** | 1–2 min "caricamento modello" senza dettaglio |
| **Riassunto mT5 fragile** | SSL Windows, download HF |
| **Nessun deploy "server"** | Mini PC AMD non sfruttato come motore dedicato |

**Conclusione:** il nucleo ASR è solido; il **prodotto** intorno è ancora MVP. Le evolutive mirano al guscio operativo: coda, batch, API, UX da strumento di lavoro.

---

## 2. Visione prodotto (12 mesi)

> **Sbobinator** = motore locale di sbobinatura italiana, usabile da chiunque senza cloud, con coda affidabile, storico completo e automazione opzionale (cartella, API, Docker su mini server).

### Principi guida

1. **Locale first** — niente obbligo di inviare audio a terzi
2. **Nessuna perdita dati** — ogni job tracciato, stati espliciti, recovery dopo crash
3. **Un backend, più front-end** — UI, CLI, API, watch-folder condividono `jobs/`
4. **Progressivo** — funziona su laptop 16 GB; scala su mini PC 32 GB e GPU
5. **Onesto sulle attese** — tempi modello/trascrizione comunicati chiaramente

### Non-obiettivi (v1)

- Training/fine-tuning modelli custom
- Traduzione multilingue del testo sbobinato
- SaaS multi-tenant con billing
- App mobile nativa
- Sostituire servizi cloud enterprise (Rev, Otter, ecc.) su tutta la linea

---

## 3. Pilastri evolutivi

Otto aree interconnesse. Ogni feature va mappata su un pilastro.

```
┌─────────────────────────────────────────────────────────────┐
│                    PILASTRI SBobinator                        │
├──────────┬──────────┬──────────┬──────────┬──────────┬────────┤
│  CODA    │  BATCH   │  STORICO │   UX     │ QUALITÀ  │ DEPLOY │
│  JOB     │  AUTO    │  DATI    │ FEEDBACK │  TESTO   │ INFRA  │
├──────────┴──────────┴──────────┴──────────┴──────────┴────────┤
│              BACKEND UNIFICATO (jobs + worker)                │
└─────────────────────────────────────────────────────────────┘
```

### P1 — Coda job

**Problema:** storico ≠ coda. Oggi salvi i risultati ma non puoi accodare.

**Obiettivo:**
- Stati: `queued` | `running` | `completed` | `failed` | `cancelled`
- Accodare N file mentre uno è in `running`
- Persistenza su disco (sopravvive a chiusura browser / crash processo)
- Un solo worker ASR per processo (evita OOM); coda FIFO

**Deliverable minimo (v0.3):**
- `JobRecord.status`, `started_at`, `finished_at`, `error`, `progress_pct`
- Worker thread o processo separato che consuma la coda
- UI: tab "Coda" con lista stati + annulla

**Dipendenze:** refactor uscita da "tutto in `main()` Streamlit"

---

### P2 — Batch e automazione

**Problema:** upload singolo, nessun watch folder.

**Obiettivo:**
- Multi-upload in UI (5–20 file)
- CLI: `sbobina batch data/input/*.mp3`
- Watch folder: `data/input/inbox/` → job automatico → sposta in `processed/`
- Opzione "riassunto per tutti" / "solo TXT"

**Deliverable (v0.4):**
- Comando batch + documentazione cartella inbox
- Regole: estensioni ammesse, skip duplicati, log errori per file

---

### P3 — Storico e gestione dati

**Problema:** storico base ok, manca gestione e ricerca.

**Obiettivo:**
- Ricerca per nome file, data, tag
- Elimina lavoro (con conferma)
- Export ZIP per lavoro
- Migrazione output legacy (`data/output/*.txt` → `jobs/`)
- Pulizia automatica opzionale (es. elimina job > 90 giorni)

**Deliverable (v0.3–0.4):**
- `scripts/migrate-legacy-jobs.ps1`
- Pulsanti UI: Elimina, Scarica ZIP
- Campo `tags: list[str]` in `job.json`

---

### P4 — UX e feedback

**Problema:** attese lunghe senza contesto; UI che sembra "bloccata".

**Obiettivo:**
- Fasi esplicite: `extract_audio` → `load_model` → `transcribe` → `export` → `summarize`
- Progress reale su chunk (file > 30 min): "Chunk 3/12"
- ETA stimata (euristica: secondi audio × fattore device)
- Wizard primo avvio: ffmpeg ✓ modello ✓ RAM sufficiente ✓
- Notifica browser/desktop a job completato (Web Notification API)

**Deliverable (v0.3):**
- Callback progress nel pipeline `transcribe()` → aggiorna `job.json`
- UI legge progress da file, non solo da session Streamlit

---

### P5 — Qualità testo e riassunto

**Problema:** output grezzo ASR; riassunto mT5 instabile.

**Obiettivo:**
- Editor inline con salvataggio `trascrizione_edit.txt` + versione originale
- Player audio + scroll sincronizzato su segmenti SRT
- Riassunto: default estrattivo; mT5 con download offline come Parakeet
- Opzioni post-ASR: punteggiatura migliorata (modello leggero o regole IT)
- Export: DOCX, VTT, PDF

**Deliverable (v0.5+):**
- `scripts/download-summary-model.ps1`
- Tab "Modifica" nella UI
- Export DOCX via `python-docx`

**Futuro (v1+):**
- Diarizzazione (chi parla) — modello aggiuntivo, RAM elevata
- Glossario utente (nomi propri, termini tecnici)

---

### P6 — Deploy e infrastruttura

**Problema:** Docker datato; mini PC AMD non usato come server dedicato.

**Obiettivo:**
- Docker allineato a `jobs/`, volumi `data/`, `models/`
- Compose profile: `cpu` (AMD mini PC), `gpu` (NVIDIA)
- Healthcheck endpoint
- Documentazione: "server domestico" con accesso LAN `http://mini-pc:8501`
- Variabili env: `SBOBINATOR_JOBS_DIR`, `SBOBINATOR_WATCH_INBOX`

**Deliverable (v0.4):**
- Aggiornamento Dockerfile + compose
- README sezione "Modalità server"

---

### P7 — API e integrazioni

**Problema:** nessun modo per automatizzare da script esterni (n8n, Power Automate, cron).

**Obiettivo API REST minima (FastAPI accanto o al posto del coupling Streamlit):

| Endpoint | Azione |
|----------|--------|
| `POST /api/jobs` | Upload file + opzioni → `job_id` |
| `GET /api/jobs` | Lista job con filtri stato |
| `GET /api/jobs/{id}` | Dettaglio + progress |
| `GET /api/jobs/{id}/files/{name}` | Download artefatto |
| `DELETE /api/jobs/{id}` | Elimina |
| `POST /api/jobs/{id}/cancel` | Annulla se in coda/running |

**Deliverable (v0.5):**
- FastAPI in `src/sbobinator/api/`
- `sbobina serve --api --ui` oppure processi separati

---

### P8 — CLI unificata

**Problema:** `sbobina transcribe` non usa `jobs/`.

**Obiettivo:**
- Ogni invocazione CLI crea un `JobRecord` come la UI
- Flag `--legacy-output` per chi vuole ancora `data/output/{stem}.txt`
- `sbobina jobs list`, `sbobina jobs show <id>`, `sbobina jobs rm <id>`

**Deliverable (v0.3):**
- Refactor `cli.py` → chiama `register_job` + worker sync per singolo file

---

## 4. Roadmap per fasi

### Fase 0 — Oggi (v0.2) ✅

- [x] Trascrizione + export
- [x] UI Streamlit
- [x] Storico lavori persistente
- [x] Fix messaggi riassunto
- [x] Modello locale Windows

---

### Fase 1 — "Strumento affidabile" (v0.3) — **prossima**

**Durata stimata:** 2–4 settimane  
**Focus:** coda + backend unificato + UX progress

| # | Feature | Pilastro | Effort |
|---|---------|----------|--------|
| 1.1 | Stati job estesi (`status`, `progress`, timestamp) | P1, P3 | M |
| 1.2 | Worker job (thread/processo) decoupled da Streamlit | P1 | L |
| 1.3 | UI coda: accoda multipli, vedi stato, annulla | P1, P4 | M |
| 1.4 | Progress per fase e per chunk | P4 | M |
| 1.5 | CLI allineata a `jobs/` | P8 | S |
| 1.6 | Migrazione output legacy | P3 | S |
| 1.7 | Export ZIP lavoro | P3 | S |
| 1.8 | Wizard / health check primo avvio | P4 | S |

**Definition of Done v0.3:**
- Utente carica 3 file, clicca sbobina 3 volte rapidamente → tutti in coda, elaborati in sequenza, tutti nello storico
- Chiude browser durante job 2 → al riaprire job 2 continua o risulta completed/failed su disco
- CLI `sbobina transcribe x.wav` appare nello storico UI

---

### Fase 2 — "Volume e automazione" (v0.4)

**Durata stimata:** 3–5 settimane  
**Focus:** batch, watch folder, Docker server

| # | Feature | Pilastro |
|---|---------|----------|
| 2.1 | Multi-upload UI | P2 |
| 2.2 | `sbobina batch` | P2, P8 |
| 2.3 | Watch folder inbox | P2 |
| 2.4 | Docker + compose aggiornati | P6 |
| 2.5 | Notifiche completamento | P4 |
| 2.6 | Ricerca / filtri storico | P3 |
| 2.7 | Elimina lavoro | P3 |

---

### Fase 3 — "Prodotto completo" (v0.5)

**Durata stimata:** 4–8 settimane  
**Focus:** API, editor, export avanzati, offline riassunto

| # | Feature | Pilastro |
|---|---------|----------|
| 3.1 | API REST FastAPI | P7 |
| 3.2 | Editor trascrizione | P5 |
| 3.3 | Player + sync SRT | P5 |
| 3.4 | Download offline mT5 | P5 |
| 3.5 | Export DOCX / VTT | P5 |
| 3.6 | Tag e note su job | P3 |

---

### Fase 4 — "Server e scala" (v1.0)

| # | Feature |
|---|---------|
| 4.1 | Worker remoto (UI su laptop → ASR su mini PC) |
| 4.2 | Diarizzazione opzionale |
| 4.3 | Glossario / hotwords |
| 4.4 | Metriche uso (tempo/job, device) |
| 4.5 | Test automatici CI (smoke ASR su campione) |

---

## 5. Priorità assoluta (se si fa una cosa sola)

Ordine consigliato se le risorse sono limitate:

```
1. Worker + coda persistente     ← sblocca tutto il resto
2. CLI → jobs/                   ← coerenza dati
3. Progress reale                  ← fiducia utente
4. Multi-upload / batch            ← produttività
5. Watch folder                    ← automazione "set and forget"
6. API REST                        ← integrazioni
7. Editor + export DOCX            ← qualità output
```

**Perché la coda prima di tutto:** senza coda, batch e watch folder creano solo più frustrazione (file persi in attesa o UI che non regge).

---

## 6. Decisioni architetturali aperte

| Decisione | Opzioni | Raccomandazione |
|-----------|---------|-----------------|
| Worker runtime | Thread in processo Streamlit vs processo `sbobina worker` separato | **Processo separato** — Streamlit non è fatto per long-running |
| Coda storage | `index.json` vs SQLite | **SQLite** da v0.3 — query stati, meno race condition |
| API + UI | Stesso processo vs split | **Split** — FastAPI worker + Streamlit client che legge API |
| Notifiche | Polling job.json vs WebSocket | Polling semplice prima; SSE/WebSocket dopo |
| Riassunto default | mT5 vs estrattivo | **Estrattivo** default su Windows |

Dettaglio tecnico in [ARCHITETTURA-FUTURA.md](./ARCHITETTURA-FUTURA.md).

---

## 7. Requisiti hardware per fase

| Scenario | RAM | Note |
|----------|-----|------|
| File breve (<10 min), solo TXT | 8 GB | Lento su CPU |
| Uso confortevole UI + estrattivo | 16 GB | Setup utente attuale |
| File lunghi + riassunto + coda | 16–32 GB | Chunk sequenziali |
| Server mini PC batch notturno | 32 GB | CPU-only accettabile |
| GPU NVIDIA | 8+ GB VRAM | 5–10× più veloce ASR |

---

## 8. Metriche di successo

| Metrica | Target v0.3 | Target v1.0 |
|---------|-------------|-------------|
| Job persi dopo crash | 0% | 0% |
| File accodabili senza attendere | ≥10 | illimitato (disco) |
| Tempo "tutto bloccato" in UI | 0 s (solo submit) | 0 s |
| Copertura CLI/UI stesso storico | 100% | 100% |
| Trascrizione campione 10 s | <60 s CPU | <15 s GPU |

---

## 9. Rischio e mitigazione

| Rischio | Mitigazione |
|---------|-------------|
| Streamlit limite architetturale | Worker esterno; UI diventa "dashboard" |
| OOM con più modello in RAM | Un worker, unload tra ASR e riassunto (già parziale) |
| SQLite + Windows path | Test early; backup `index.json` export |
| Scope creep | Fasi rigide; non-obiettivi espliciti |
| NeMo breaking changes | Pin version in `pyproject.toml`, test smoke |

---

## 10. Collegamento bug-fix → evolutive

| Bug aperto (bug-fix/) | Evolutiva che lo risolve |
|-----------------------|--------------------------|
| BUG-ARCH-012 CLI overwrite | P8 — CLI unificata |
| BUG-ARCH-013 Nessuna coda concorrente | P1 — Coda job |
| BUG-ARCH-015 Legacy flat output | P3 — Migrazione |
| BUG-WIN-011 mT5 SSL | P5 — Download offline riassunto |
| BUG-UX-007 Progress opaco | P4 — Feedback |
| Docker non aggiornato | P6 — Deploy |

---

## 11. Prossimi passi operativi

1. **Validare** con te le Fasi 1–2 (priorità coda vs batch)
2. **Implementare** schema `JobRecord` v2 (`status`, `progress`, `phase`)
3. **Prototipo** `sbobina worker` che legge coda da SQLite
4. **Adattare** UI: submit job → messaggio "in coda" → polling stato
5. **Aggiornare** README quando v0.3 è rilasciata

---

## Cronologia documento

| Data | Modifica |
|------|----------|
| 2026-06-26 | Creazione roadmap iniziale, 8 pilastri, fasi 0–4 |
