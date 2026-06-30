# Avvio rapido

## 1. Installa dipendenze

```cmd
python scripts\install_local.py
```

oppure `pip install -r requirements/local.txt`

## 2. Scarica modello ASR (obbligatorio)

```cmd
python scripts\download_model.py
```

| Script | Dimensione | Obbligatorio |
|--------|------------|--------------|
| `download_model.py` | ~2.5 GB | Sì (trascrizione) |
| `download_summary_llm.py` | ~2 GB | Solo riassunto **locale** Qwen |

Riassunto **cloud** (DeepSeek, ecc.): nessun download modello — solo API key in `/settings/summary`.

---

## 3. Avvia l'interfaccia

```cmd
start.bat
```

oppure `sbobina ui` / `python scripts\restart_ui.py`

Apri: **http://localhost:8501**

---

## 4. Sbobina un file

1. (Opzionale) **Impostazioni riassunto** → API key DeepSeek o altro
2. Sidebar → **Genera riassunto** + motore
3. Carica file → **Accoda sbobinatura**
4. Risultati in `data\output\jobs\YYYYMMDD_HHMMSS_nomefile\`

---

## 5. CLI

```cmd
sbobina transcribe data\input\miofile.wav -s --summary-provider deepseek
```

---

## 6. Svuota storico

```cmd
python scripts\clean_output.py
```

---

## Struttura dopo il primo utilizzo

```
sbobinator/
├── data/
│   ├── .secrets/       ← API key riassunto
│   ├── input/
│   └── output/jobs/
├── models/
│   ├── parakeet-tdt-0.6b-v3.nemo
│   └── qwen2.5-3b-instruct/   ← opzionale
└── .venv/
```

---

## Problemi comuni

| Sintomo | Soluzione |
|---------|-----------|
| `ffmpeg non trovato` | `winget install Gyan.FFmpeg` |
| Dipendenze mancanti | `pip install -r requirements/local.txt` |
| DeepSeek `Connection error` | `pip install truststore` + riavvia UI |
| Riassunto locale disabilitato | RAM < 16 GB o manca GGUF |

Vedi [Risoluzione problemi](../troubleshooting/common-issues.md).
