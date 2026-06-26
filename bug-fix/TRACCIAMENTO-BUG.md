# Tracciamento bug — Sbobinator

Documento aggiornato al **26 giugno 2026** (v0.2.x).  
Elenco sistematico dei bug rilevati durante sviluppo e test su Windows, con causa, impatto, stato e fix.

---

## Legenda stati

| Stato | Significato |
|-------|-------------|
| ✅ Risolto | Fix in codice, verificato o ragionevolmente coperto |
| 🔧 Parziale | Mitigazione in atto; limitazioni documentate |
| 📋 Aperto | Noto, fix pianificato |
| ℹ️ Limitazione | Comportamento atteso / vincolo ambiente, non bug puro |

---

## Indice

1. [Bug segnalati dall'utente (sessione corrente)](#1-bug-segnalati-dallutente-sessione-corrente)
2. [Bug critici risolti in precedenza](#2-bug-critici-risolti-in-precedenza)
3. [Bug UI / UX](#3-bug-ui--ux)
4. [Bug ambiente Windows](#4-bug-ambiente-windows)
5. [Bug architettura / dati](#5-bug-architettura--dati)
6. [Rischi residui e backlog](#6-rischi-residui-e-backlog)
7. [Come testare le fix](#7-come-testare-le-fix)

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

## 2. Bug critici risolti in precedenza

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

## 3. Bug UI / UX

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

| Stato | ℹ️ Limitazione Streamlit |
|-------|--------------------------|

Dopo completamento, il file uploader si svuota. I risultati sono nello storico lavori, non nell'uploader.

---

## 4. Bug ambiente Windows

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

## 5. Bug architettura / dati

### BUG-ARCH-012 — Export CLI sovrascrive per `stem` uguale

| Stato | 📋 Aperto (solo CLI) |
|-------|----------------------|

`sbobina transcribe video.mp4 -o data/output` sovrascrive `video.txt` se rieseguito.  
**Backlog:** allineare CLI al sistema `jobs/` della UI.

---

### BUG-ARCH-013 — Nessuna coda elaborazione concorrente

| Stato | 📋 Aperto |
|-------|-----------|

Un solo job alla volta; non si può accodare sbobinato2 mentre sbobinato1 gira.  
**Backlog:** coda asincrona (Redis/SQLite worker) — vedi roadmap.

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

## 6. Rischi residui e backlog

### Priorità alta (prossime release)

| ID | Task |
|----|------|
| P1 | Allineare CLI al registro `jobs/` |
| P1 | Script migrazione output legacy |
| P2 | Download offline mT5 per riassunto qualità |
| P2 | Messaggio progress più dettagliato (fase + tempo) |

### Priorità media

| ID | Task |
|----|------|
| P3 | Coda job (accodare senza attendere) |
| P3 | Pulsante "Elimina lavoro" nello storico |
| P3 | Export ZIP di un lavoro (txt+srt+riassunto) |

### Priorità bassa

| ID | Task |
|----|------|
| P4 | Watch folder automatico |
| P4 | API REST con stesso backend jobs |
| P4 | Diarizzazione (chi parla) |

---

## 7. Come testare le fix

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
