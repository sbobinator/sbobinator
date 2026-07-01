# Piano microevolutivo — Backlog (terzo asse + complementi)

> **Data**: 2026-06-26 · **Stato**: 📋 da prioritizzare  
> **Obiettivo**: raccogliere evoluzioni **non coperte** dai piani multilingua/desktop,
> con una raccomandazione su cosa fare **dopo** il primo pacchetto multilingua.  
> **Uso:** scegliere **una** linea per il prossimo sprint; non tutto insieme.

---

## 0. Contesto

Dopo coda job, FastAPI, licenza base e sito GitHub Pages, i candidati più utili per
**valore prodotto** e **monetizzazione** sono sotto. Ogni sezione è indipendente
con DoD proprio — si può promuovere una sezione a `PLAN_*.md` dedicato quando parte lo sviluppo.

---

## Raccomandazione sintetica

| Priorità | Tema | Perché ora |
|----------|------|------------|
| **A** | Licenza commerciale + chiavi | Allinea codice al sito e alle vendite B2B |
| **B** | Watch folder + batch | Alto impatto per utenti ricorrenti, codice vicino a worker |
| **C** | Wizard `sbobina doctor` | Riduce supporto; prerequisito desktop |
| **D** | Editor trascrizione in UI | Qualità output, meno export→Word |
| **E** | Worker remoto (UI laptop → mini PC) | Docker già deployato; differenziatore "server casa" |
| **F** | Diarizzazione | Complesso, RAM alta — solo su richiesta |

**Ordine suggerito:** **C** (piccolo) → **A** o **B** (scelta business) → **D** → **E** → **F**.

---

## A — Licenza commerciale e attivazione

**Problema:** oggi c’è ack first-run (personal) e testo legale; **nessuna chiave** per clienti paganti.

### Obiettivo

- Build "Personal" vs "Commercial" o singola build con unlock
- Chiave per postazione o account (fase 1: chiave file locale firmata)
- UI `/settings/license` mostra stato: Personal / Commercial valida / scaduta

### Fasi

| Fase | Deliverable |
|------|-------------|
| A1 | Formato chiave (JSON firmato o JWT offline con public key in app) |
| A2 | `license_info.py` → `validate_commercial_key()` |
| A3 | Pagina acquisto (link antoniotrento.net) + istruzioni incolla chiave |
| A4 | Watermark export opzionale in personal (discutibile — solo se richiesto legalmente) |

### DoD

Cliente con chiave valida → nessun modal personal; log audit `commercial_active` in settings.

### Effort

**M** (1–2 settimane) per A1–A3 offline; **L** se pagamento + server attivazione online.

### Collegamento desktop

Obbligatorio prima di vendere installer MSI (fase 2d di `PLAN_DESKTOP_TAURI.md`).

---

## B — Watch folder e batch automatico

**Problema:** ogni file richiede upload manuale; chi sbobina 10 registrazioni al giorno perde tempo.

### Obiettivo

```
data/input/inbox/     →  nuovo file  →  job automatico  →  sposta in inbox/processed/
```

### Fasi

| Fase | Deliverable |
|------|-------------|
| B1 | `sbobina watch <path>` — loop con watchdog (dipendenza `watchdog`) |
| B2 | Regole: estensioni, skip file in scrittura, debounce 5s |
| B3 | Settings UI: cartella inbox, toggle auto-summary |
| B4 | `sbobina batch glob/*.mp3` — già parzialmente in roadmap `evolutive/` P2 |

### DoD

Copia 3 MP3 in inbox → 3 job in coda senza aprire browser.

### Effort

**M** (B1–B2: 3–5 giorni; B3–B4: +1 settimana)

### Rischi

| Rischio | Mitigazione |
|---------|-------------|
| File grandi copiati a metà | Debounce + check size stable |
| Duplicati | Hash nome + mtime in SQLite |

---

## C — Wizard primo avvio (`sbobina doctor`)

**Problema:** utenti bloccati su ffmpeg mancante, modello non scaricato, RAM insufficiente.

### Obiettivo

Comando e pagina settings:

```
✓ ffmpeg in PATH
✓ parakeet-tdt-0.6b-v3.nemo presente
✓ RAM >= 8 GB (warning) / 16 GB per Qwen
✓ spazio disco >= 10 GB
```

### Fasi

| Fase | Deliverable |
|------|-------------|
| C1 | `scripts/doctor.py` + output JSON |
| C2 | Banner in UI se check fallisce |
| C3 | Link a `download_model.py` / winget ffmpeg |

### Effort

**S** (1–2 giorni)

### Nota

Prerequisito leggero per **desktop** e per ridurre issue GitHub.

---

## D — Editor trascrizione in browser

**Problema:** testo read-only; correzioni ASR solo in editor esterno.

### Obiettivo

- `/jobs/{id}` → textarea o editor leggero (CodeMirror 6 via CDN)
- Salva → `transcript.txt` + invalida summary obsoleto (flag)
- Opzione "Rigenera riassunto" dopo edit

### Fasi

| Fase | Deliverable |
|------|-------------|
| D1 | POST `/jobs/{id}/transcript` con validazione |
| D2 | UI edit + Salva |
| D3 | Backup `.txt.bak` prima di overwrite |

### Effort

**M** (1 settimana)

### Non obiettivo v1

Collaborazione multi-utente, CRDT, versioning git.

---

## E — Worker remoto (laptop → mini PC)

**Problema:** trascrizione lenta su laptop; mini PC con Docker già disponibile ma UI solo locale al container.

### Obiettivo

- UI su laptop punta a `http://mini-pc:8502` **oppure**
- API submit job su server + polling (già parzialmente possibile con FastAPI)

### Fasi

| Fase | Deliverable |
|------|-------------|
| E1 | Documentare deploy LAN + firewall |
| E2 | Auth token opzionale su API (header) |
| E3 | UI setting "Server URL" |

### Effort

**S–M** per E1+E3 se non serve auth; **L** con auth e TLS.

### Considerazione

Molti utenti home lab accettano HTTP su LAN; TLS opzionale (reverse proxy).

---

## F — Diarizzazione ("chi parla")

**Problema:** meeting con più speaker — un muro di testo.

### Obiettivo

- Modello aggiuntivo (es. NeMo diarization o pyannote) — **secondo download**
- Output: segmenti con label `Speaker 1`, `Speaker 2`

### Perché in backlog e non sprint

- RAM e tempo elaborazione x2–x3
- Qualità variabile su audio telefonico
- Richiede benchmark dedicato

### Effort

**L–XL**

---

## G — Altre idee (icebox)

| Idea | Note |
|------|------|
| Notifiche desktop (Web Notification API) | Già in `evolutive/` P4 — basso effort |
| Export DOCX / VTT | Formato professionale |
| Glossario / hotwords ASR | Migliora nomi propri |
| API REST pubblica documentata | OpenAPI già parziale in FastAPI |
| Mobile (PWA) | Solo se UI responsive migliorata |
| SaaS multi-tenant | Esplicitamente out of scope roadmap |

---

## Matrice scelta rapida

Rispondi a una domanda:

| Se la priorità è… | Scegli |
|-------------------|--------|
| Vendere a aziende nel 2026 | **A** Licenza |
| Utenti che sbobinano ogni giorno | **B** Watch folder |
| Meno ticket supporto | **C** Doctor |
| Qualità testo senza Word | **D** Editor |
| Hai già mini PC in produzione | **E** Remoto |
| Podcast / tribunale / multi-voce | **F** Diarizzazione |

---

## Prossimo passo operativo

1. Completare **multilingua summary + ASR** (piani dedicati).
2. Implementare **C** (`doctor`) in parallelo — costo basso.
3. Decisione business: **A** vs **B**.
4. Avviare **desktop 2a** quando `doctor` e path AppData sono chiari.

Quando una sezione parte, rinominare in `PLAN_LICENSE.md`, `PLAN_WATCH_FOLDER.md`, ecc. in questa cartella.
