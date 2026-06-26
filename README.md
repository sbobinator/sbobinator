# Sbobinator

Trascrizione **audio e video → testo** in italiano, in locale, con modelli pre-addestrati [NVIDIA NeMo Parakeet](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3).

Include **interfaccia web** e **riassunto testo** (estrativo veloce o mT5).

## Avvio rapido (Windows, senza Docker)

### 1. Installa ffmpeg

```powershell
winget install Gyan.FFmpeg
```

### 2. Installa Sbobinator

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-local.ps1
```

### 3. Avvia l'interfaccia web

Doppio click su **`start.bat`** oppure:

```powershell
sbobina
```

Si apre il browser su **http://localhost:8501** — trascina un file, clicca **Sbobina**, scarica TXT/SRT/riassunto.

> Primo avvio: download modelli (~2.5 GB ASR + ~300 MB riassunto mT5). Richiede tempo e connessione.

## Interfaccia web

| Funzione | Descrizione |
|----------|-------------|
| Upload drag & drop | Audio e video (MP4, MKV, WAV, MP3…) |
| Trascrizione | NeMo Parakeet v3, italiano auto |
| Riassunto veloce | Estrattivo, offline, nessun modello extra |
| Riassunto qualità | mT5-small multilingue (~300 MB) |
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
docker compose -f docker/docker-compose.yml --profile cpu build
docker compose -f docker/docker-compose.yml --profile cpu run --rm -p 8501:8501 sbobinator-cpu ui
```

## Modello

| Impostazione | Valore |
|--------------|--------|
| ASR | `nvidia/parakeet-tdt-0.6b-v3` |
| Riassunto | LexRank (veloce) o `google/mt5-small` |
| Lingua | Italiano (auto-rilevamento) |

## Struttura

```
sbobinator/
├── start.bat              # avvio rapido Windows
├── scripts/install-local.ps1
├── src/sbobinator/ui/     # interfaccia Streamlit
├── data/input/            # file da trascrivere
├── data/output/           # risultati
└── models/                # cache modelli
```

## Licenza

MIT — modelli NVIDIA/HuggingFace con le rispettive licenze.
