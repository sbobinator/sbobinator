# Microevolutive — Sbobinator

Piani **corti ed eseguibili**: fasi, prerequisiti, Definition of Done, ordine di implementazione.

La cartella **`evolutive/`** resta la visione ampia e storica; qui si mettono solo
iniziative con fasi, prerequisiti, Definition of Done e ordine di implementazione.

## Documenti

| File | Focus | Priorità suggerita |
|------|--------|-------------------|
| [PLAN_MULTILANG_SUMMARY.md](./PLAN_MULTILANG_SUMMARY.md) | Riassunto LLM in più lingue (prompt + UI) | **1** — sforzo basso, valore alto |
| [PLAN_MULTILANG_ASR.md](./PLAN_MULTILANG_ASR.md) | Lingua trascrizione NeMo (hint + UI + job) | **2** — spesso senza nuovi `.nemo` |
| [PLAN_DESKTOP_TAURI.md](./PLAN_DESKTOP_TAURI.md) | App desktop Windows/macOS (Tauri + sidecar Python) | **3** — dopo backend stabile |
| [PLAN_BACKLOG.md](./PLAN_BACKLOG.md) | Terzo asse da decidere: licenza, watch folder, editor, … | **4** — scegliere una linea |

## Relazione con altre cartelle

| Cartella | Ruolo |
|----------|--------|
| `bug-fix/` | Cosa è rotto **oggi** |
| `evolutive/` | Roadmap storica (parte già realizzata: coda, FastAPI, `/jobs`) |
| `microevolutive/` | **Prossimi sprint** concreti |
| `docs/` | Documentazione utente (MkDocs) |

## Ordine di esecuzione consigliato

```
PLAN_MULTILANG_SUMMARY  →  PLAN_MULTILANG_ASR  →  PLAN_DESKTOP (fase 2a)
                                                      ↓
                                              PLAN_BACKLOG (licenza o watch folder)
                                                      ↓
                                              PLAN_DESKTOP (fase 2b–2c installer)
```

## Stato base (giugno 2026)

Già in produzione / quasi completo rispetto alla vecchia roadmap `evolutive/`:

- FastAPI + HTMX (non più Streamlit come runtime principale)
- Coda job SQLite, `/jobs`, `/jobs/{id}`, worker separato
- Riassunto multi-provider (cloud + Qwen locale)
- Licenza proprietaria + modal primo avvio
- Docker mini PC (`8502:8501`)
- Sito `sbobinator.github.io` + docs MkDocs

I piani qui sotto **partono da questo stato**, non da v0.2 Streamlit.
