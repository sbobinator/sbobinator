# Storage e persistenza

## Layout dati

```
data/                          ← SBOBINATOR_DATA (default: project_root/data)
├── input/                     ← file sorgente (manuale o upload)
│   └── README.md
└── output/
    ├── jobs/
    │   ├── queue.db         ← SQLite WAL
    │   ├── worker.pid       ← PID worker attivo
    │   └── YYYYMMDD_HHMMSS_nome/
    │       ├── source.wav
    │       ├── job.json
    │       ├── trascrizione.txt
    │       ├── sottotitoli.srt
    │       └── riassunto.txt
    └── benchmark_*.json/md    ← report benchmark opzionali

models/                        ← NEMO_CACHE_DIR
├── parakeet-tdt-0.6b-v3.nemo
└── mt5-small/
    ├── config.json
    ├── model.safetensors
    └── spiece.model
```

## SQLite `queue.db`

- Tabella `jobs` con tutti i campi di `JobRecord`
- WAL mode per letture concorrenti (UI poll + worker write)
- Migrazione automatica da vecchio `index.json` (se presente)

### Cosa succede se...

| Azione | Lista UI | File testo |
|--------|----------|------------|
| Riavvio app | ✅ Persiste | ✅ Persiste |
| Cancella cartella job | ⚠️ Job in DB, file mancanti | ❌ |
| Cancella solo queue.db | ❌ Lista vuota | ✅ File restano |
| `clean_output.py` | ❌ Vuoto | ❌ Tutto rimosso |

## `job.json`

Copia JSON del record SQLite, sincronizzata a ogni update. Utile per ispezione manuale e backup; **l'UI non lo usa per l'elenco**.

## Git

`.gitignore` esclude:

- `data/output/*` (tranne `.gitkeep`)
- `data/output/jobs/*` (tranne `.gitkeep`)
- `models/*` (tranne `.gitkeep`)
- `queue.db`

I risultati **non** vanno in git.

Per schema completo vedi [Schema job e database](../reference/job-schema.md).

## Docker volume

Solo `../data:/data` montato dal host. Modelli **nell'immagine** (`/models`), non nel volume.
