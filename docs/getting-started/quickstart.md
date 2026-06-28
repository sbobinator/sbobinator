# Avvio rapido

## 1. Scarica i modelli (una tantum)

```cmd
python scripts\download_model.py
python scripts\download_summary_model.py
```

| Script | Dimensione | Obbligatorio |
|--------|------------|--------------|
| `download_model.py` | ~2.5 GB | Sì (trascrizione) |
| `download_summary_model.py` | ~1.1 GB | Solo per riassunto mT5 |

Il riassunto **estrativo** funziona senza il secondo script.

---

## 2. Avvia l'interfaccia

**Windows — doppio click:**

```
start.bat
```

**Oppure da terminale:**

```cmd
sbobina ui
```

**Oppure riavvio pulito (chiude istanze Streamlit duplicate):**

```cmd
python scripts\restart_ui.py
```

Apri: **http://localhost:8501**

---

## 3. Sbobina un file

1. Sidebar → imposta **Riassunto** (estrativo o mT5 se scaricato)
2. Trascina un file audio/video
3. Clicca **▶️ Accoda sbobinatura**
4. Segui la **Coda elaborazione**
5. Risultati in `data\output\jobs\YYYYMMDD_HHMMSS_nomefile\`

---

## 4. CLI — un file senza UI

```cmd
sbobina transcribe data\input\miofile.wav -s
```

Accoda nel registro job ed elabora subito.

---

## 5. Svuota lo storico e ricomincia

```cmd
python scripts\clean_output.py
```

Rimuove tutte le cartelle job e resetta `queue.db`. Non tocca `data\input\` né `models\`.

---

## Struttura cartelle dopo il primo utilizzo

```
sbobinator/
├── data/
│   ├── input/          ← metti qui i file sorgente
│   └── output/
│       └── jobs/       ← risultati e queue.db
├── models/
│   ├── parakeet-tdt-0.6b-v3.nemo
│   └── mt5-small/      ← opzionale
└── .venv/              ← ambiente Python
```

---

## Problemi comuni al primo avvio

| Sintomo | Soluzione |
|---------|-----------|
| `ffmpeg non trovato` | Installa ffmpeg, riavvia terminale |
| `Dipendenze ASR mancanti` | `pip install -e ".[local]"` |
| Bottone accoda disabilitato | Ricarica pagina dopo upload file |
| Riassunto mT5 non disponibile | `python scripts\download_summary_model.py` |

Vedi [Risoluzione problemi](../troubleshooting/common-issues.md).
