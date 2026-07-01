# Piano microevolutivo — App desktop (Tauri + sidecar Python)

> **Data**: 2026-06-26 · **Stato**: 📋 pianificato  
> **Obiettivo**: installer **Windows** e **macOS** per uso retail/commerciale,
> senza riscrivere NeMo in Rust. Shell nativa + backend Python esistente.  
> **Riferimento commerciale:** `docs/en/reference/commercial-license.md` (desktop pianificato).

---

## 0. Cosa esiste già (forte base)

| Pezzo | File / path | Riuso desktop |
|-------|-------------|---------------|
| Web UI | `src/sbobinator/ui/server.py` (FastAPI) | WebView → `http://127.0.0.1:8501` |
| Avvio UI | `start.bat`, `sbobina ui`, `ui/launch.py` | Sidecar entrypoint |
| Worker ASR | `worker.py` + `process_guard.py` | Stesso processo o subprocess |
| Coda job | `jobs.py` (SQLite) | Path sotto AppData |
| Licenza | `license_info.py` + modal UI | First-run obbligatorio |
| Download modelli | `download_model.py`, `download_summary_llm.py` | Wizard integrato |
| Docker | `docker/` | **Non** è il desktop — resta per mini PC/server |

**Considerazione:** il refactor "desktop" è in gran parte **packaging e percorsi**,
non riscrittura della pipeline ASR. Il rischio maggiore è **distribuire Python + PyTorch + NeMo**
in modo affidabile su Windows (dimensioni installer, antivirus, VC++ redist).

---

## 1. Architettura target

```
┌─────────────────────────────────────────────────────────┐
│  Tauri 2.x (Rust)                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │ WebView (Wry) → http://127.0.0.1:{port}/          │  │
│  └───────────────────────────────────────────────────┘  │
│  Tray icon · single instance · auto-update (fase 3)       │
│  Spawn / monitor / kill sidecar                          │
└──────────────────────────┬──────────────────────────────┘
                           │ stdio / health HTTP
┌──────────────────────────▼──────────────────────────────┐
│  Sidecar Python (frozen o venv embedded)                 │
│  ┌─────────────┐    ┌──────────────┐                    │
│  │ FastAPI UI  │    │ sbobina      │                    │
│  │ (uvicorn)   │◄──►│ worker       │                    │
│  └─────────────┘    └──────────────┘                    │
│  NeMo · ffmpeg · models/ · data/                       │
└─────────────────────────────────────────────────────────┘
```

### Decisioni da NON cambiare

1. **NeMo resta in Python** — niente port ASR in Rust/C++.
2. **Un solo backend** — UI web embedded = stessa UI del browser (zero duplicazione template).
3. **Localhost only** — nessun bind su `0.0.0.0` in modalità desktop (sicurezza).
4. **Dati utente fuori dal bundle** — `AppData/Sbobinator/` (Win) o `~/Library/Application Support/Sbobinator/` (Mac).

---

## 2. Layout percorsi desktop

| Risorsa | Sviluppo (oggi) | Desktop |
|---------|-----------------|---------|
| Modelli ASR/LLM | `{repo}/models/` | `%AppData%/Sbobinator/models/` |
| Job + SQLite | `{repo}/data/` | `%AppData%/Sbobinator/data/` |
| Secrets / API key | `data/.secrets/` | stesso sotto AppData |
| Log | console / file | `%AppData%/Sbobinator/logs/` |
| ffmpeg | PATH / winget | Bundled in `resources/ffmpeg.exe` |

**Env:** `SBOBINATOR_DATA`, `NEMO_CACHE_DIR` già supportati in `config.py` — usarli come contratto ufficiale desktop.

---

## 3. Fasi

### Fase 2a — "Wrapper dev" (senza installer) — **2–3 settimane**

Obiettivo: dimostrare finestra nativa che avvia tutto con un doppio click **in dev**.

| # | Task | DoD |
|---|------|-----|
| 2a.1 | Repo `desktop/` o `apps/desktop-tauri/` | `cargo tauri dev` avvia |
| 2a.2 | Sidecar: script `desktop/start_backend.ps1` / `.sh` | Health `GET /health` OK |
| 2a.3 | Tauri apre WebView su porta dinamica | UI upload funziona |
| 2a.4 | Chiusura app → termina worker + uvicorn | Nessun processo zombie |
| 2a.5 | Single instance (secondo avvio focus finestra) | Test manuale Win |

**Non include:** PyInstaller, code signing, auto-update.

Struttura suggerita:

```
sbobinator/
├── desktop/
│   ├── src-tauri/
│   │   ├── tauri.conf.json
│   │   ├── src/main.rs      # spawn sidecar, webview URL
│   │   └── icons/
│   ├── README.md
│   └── sidecar/
│       └── start_backend.py # wrapper: set env, launch ui+worker
```

### Fase 2b — Backend "desktop-ready" — **2–4 settimane** (in parallelo parziale)

Refactor minimo nel repo principale (non solo cartella Tauri):

| # | Task | File coinvolti |
|---|------|----------------|
| 2b.1 | `GET /health` + `GET /api/status` | `ui/server.py` |
| 2b.2 | Porta configurabile + bind 127.0.0.1 | `launch.py`, env `SBOBINATOR_PORT` |
| 2b.3 | `resolve_paths()` centralizzato | `config.py` |
| 2b.4 | Wizard CLI: `sbobina doctor` | nuovo `scripts/doctor.py` — ffmpeg, modello, RAM |
| 2b.5 | Log file rotante | `logging` config |

**Definition of Done 2a+2b:** su PC pulito con Python già installato, Tauri avvia Sbobinator completo senza `start.bat` manuale.

### Fase 2c — Packaging installer — **4–8 settimane**

| # | Task | Piattaforma |
|---|------|-------------|
| 2c.1 | PyInstaller o **python-build-standalone** + venv | Win + Mac |
| 2c.2 | Bundle ffmpeg | Win (zip) / Mac (homebrew dep o static) |
| 2c.3 | MSI / NSIS o WiX | Windows |
| 2c.4 | DMG + notarization Apple | macOS (account dev richiesto) |
| 2c.5 | Code signing | Entrambi |
| 2c.6 | Primo avvio: download modelli guidato (non nel MSI da 3 GB) | UX |

**Dimensioni attese:**

| Componente | Ordine grandezza |
|------------|------------------|
| App shell Tauri | ~15–30 MB |
| Python + torch CPU | ~1–2 GB |
| Modello Parakeet (download post-install) | ~2.5 GB |
| Qwen opzionale | ~2 GB |

Strategia commerciale: **installer leggero + download modelli al first-run** (come oggi, ma con UI integrata).

### Fase 2d — Licenza commerciale integrata — **dopo 2c o in parallelo**

Vedi `PLAN_BACKLOG.md` § Licenza.

- Chiave per postazione o file `.license`
- Disabilita batch/API in build "Personal" vs "Pro" (opzionale)

---

## 4. Cosa NON fare

| Evitare | Motivo |
|---------|--------|
| Electron + Node | Duplica stack; Tauri più leggero |
| Riscrivere UI in Qt/WPF | Due front-end da mantenere |
| Includere 2.5 GB nel MSI | Download falliti, CI lenta |
| GPU obbligatoria in desktop | Target laptop CPU 16 GB |
| macOS come prima piattaforma | Win = mercato primario IT; Mac dopo |

---

## 5. Rischi e mitigazioni

| Rischio | Mitigazione |
|---------|-------------|
| PyTorch + NeMo difficile da freezare | python-build-standalone; test CI; fallback "installer che richiede Python 3.11" per beta |
| Antivirus false positive | Code signing; build riproducibili |
| Worker zombie | Tauri kill tree; `process_guard` già presente |
| SSL download modello su Win | `download_model.py` nel wizard — già documentato |
| Apple notarization | Budget + tempo; fase Mac dopo Win stabile |

---

## 6. Test accettazione (release desktop v1)

- [ ] Install su Windows 11 pulito → wizard → trascrizione 1 min MP3
- [ ] Chiudi app durante job → riapri → job in coda/stato coerente
- [ ] Seconda istanza → focus prima finestra
- [ ] Disinstall → dati in AppData opzionalmente conservati (checkbox)
- [ ] Licenza personal ack + link commerciale
- [ ] Nessun listener su LAN (`netstat` solo 127.0.0.1)

---

## 7. Stima effort totale

| Fase | Effort | Note |
|------|--------|------|
| 2a Wrapper | **M** | |
| 2b Backend-ready | **M** | parte riusabile anche senza Tauri |
| 2c Installer | **L–XL** | signing e notarization |
| 2d Licenza | **M** | vedi PLAN_BACKLOG |

**Sequenza consigliata:** 2b (parziale) → 2a → 2c → 2d.

---

## 8. Riferimenti

```
src/sbobinator/ui/launch.py
src/sbobinator/ui/process_guard.py
src/sbobinator/worker.py
src/sbobinator/config.py          # SBOBINATOR_DATA
src/sbobinator/license_info.py
start.bat                         # comportamento da replicare
docs/en/reference/commercial-license.md
```

Tauri docs: https://v2.tauri.app/  
Pattern sidecar: https://v2.tauri.app/develop/sidecar/
