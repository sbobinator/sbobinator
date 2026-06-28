# Sbobinator

Trascrizione **audio e video → testo** in italiano, in locale, con modelli pre-addestrati [NVIDIA NeMo Parakeet](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3).

Include **interfaccia web** e **riassunto testo** (sintesi estrattiva o IT5 fine-tuned).

📖 **Documentazione completa:** [docs su GitHub Pages](https://sbobinator.github.io/sbobinator/) — sorgenti in `docs/`, build con `mkdocs serve`.

## Avvio rapido (Windows, senza Docker)

### 1. Installa ffmpeg

```powershell
winget install Gyan.FFmpeg
```

### 2. Installa Sbobinator

```cmd
python scripts\install_local.py
```

### 3. Scarica il modello ASR (una volta, ~2.5 GB)

```cmd
python scripts\download_model.py
```

### 4. Avvia l'interfaccia web

Doppio click su **`start.bat`** oppure:

```cmd
start.bat
```

oppure:

```cmd
sbobina ui
```

Si apre il browser su **http://localhost:8501** — trascina un file, clicca **Sbobina**, scarica TXT/SRT/riassunto.

> Primo avvio: `python scripts/download_model.py` (~2.5 GB ASR). Per riassunto IT5: `python scripts/download_summary_model.py` (~400 MB).

## Interfaccia web

| Funzione | Descrizione |
|----------|-------------|
| Upload drag & drop | Audio e video (MP4, MKV, WAV, MP3…) |
| Trascrizione | NeMo Parakeet v3, italiano auto |
| Riassunto veloce | Estrattivo, offline, nessun modello extra |
| Riassunto | IT5-small news in `models/it5-small-news-summarization/` (~400 MB) |
| Download | TXT, SRT, riassunto |

## Comandi CLI

```powershell
sbobina                              # avvia UI web
sbobina ui                           # idem
sbobina transcribe video.mp4 -o data/output
sbobina transcribe audio.wav -s      # con riassunto
sbobina transcribe audio.wav -s --summary-mode abstractive
sbobina info
```

## Requisiti

- Python 3.12+
- **ffmpeg** nel PATH
- RAM: 8 GB minimo, 16–32 GB consigliati
- GPU NVIDIA opzionale (più veloce)

## Docker (alternativa)

Per il mini PC AMD o deploy containerizzato:

```bash
cd docker
docker compose --profile cpu build
docker compose --profile cpu up
```

Modelli inclusi nell'immagine. Solo `data/` montato dal host. Vedi [docs/deployment/docker.md](docs/deployment/docker.md).

## Modello

| Impostazione | Valore |
|--------------|--------|
| ASR | `nvidia/parakeet-tdt-0.6b-v3` |
| Riassunto | LexRank (sintesi) o `gsarti/it5-small-news-summarization` |
| Lingua | Italiano (auto-rilevamento) |

## Struttura

```
sbobinator/
├── start.bat              # avvio rapido Windows
├── scripts/install_local.py
├── scripts/download_model.py
├── scripts/generate_samples.py
├── src/sbobinator/ui/     # interfaccia Streamlit
├── data/input/            # file da trascrivere
├── data/output/           # risultati
└── models/                # cache modelli
```

## Licenza

MIT — modelli NVIDIA/HuggingFace con le rispettive licenze.
