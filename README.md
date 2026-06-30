# Sbobinator

Trascrizione **audio e video → testo** in italiano, in locale, con modelli pre-addestrati [NVIDIA NeMo Parakeet](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3).

Include **interfaccia web FastAPI** e **riassunto LLM** (DeepSeek, OpenAI, Claude, Gemini, Kimi, o Qwen locale).

📖 **Documentazione:** [docs su GitHub Pages](https://sbobinator.github.io/sbobinator/) — build locale: `mkdocs serve`.

## Avvio rapido (Windows, senza Docker)

### 1. Installa ffmpeg

```powershell
winget install Gyan.FFmpeg
```

### 2. Installa Sbobinator (tutte le dipendenze)

```cmd
python scripts\install_local.py
```

Equivalente manuale: `pip install -r requirements/local.txt`

### 3. Scarica il modello ASR (una volta, ~2.5 GB)

```cmd
python scripts\download_model.py
```

### 4. Avvia l'interfaccia web

```cmd
start.bat
```

oppure `sbobina ui` → **http://localhost:8501**

### 5. Riassunto (opzionale)

| Motore | Setup |
|--------|--------|
| **Cloud** (DeepSeek, OpenAI, …) | [Impostazioni riassunto](http://localhost:8501/settings/summary) → API key |
| **Locale** (Qwen, offline) | `python scripts/download_summary_llm.py` + RAM ≥ 16 GB |

## Interfaccia web

| Funzione | Descrizione |
|----------|-------------|
| Upload | Audio e video (MP4, MKV, WAV, MP3…) |
| Trascrizione | NeMo Parakeet v3, italiano |
| Riassunto LLM | Opt-in, motore a scelta |
| Download | TXT, SRT, riassunto |

## Comandi CLI

```powershell
sbobina ui
sbobina transcribe video.mp4 -o data/output
sbobina transcribe audio.wav -s --summary-provider deepseek
sbobina info
```

## Dipendenze (`pyproject.toml`)

| Extra | Uso |
|-------|-----|
| `local` | **Completo** — ASR + UI + riassunto LLM |
| `ui` | Web + API cloud riassunto |
| `summarize` | Solo moduli LLM |
| `asr` | Solo NeMo |

Vedi [`requirements/README.md`](requirements/README.md).

## Requisiti

- Python 3.12+
- **ffmpeg** nel PATH
- RAM: 8 GB minimo (16 GB per riassunto locale Qwen)
- GPU NVIDIA opzionale (trascrizione più veloce)

## Docker

```bash
cd docker
docker compose --profile cpu build
docker compose --profile cpu up
```

Solo modello ASR nell'immagine; **Qwen locale si scarica da solo** all'avvio se RAM ≥ 16 GB. Riassunto cloud via API key. Vedi [docs/deployment/docker.md](docs/deployment/docker.md).

## Modello

| Componente | Valore |
|------------|--------|
| ASR | `nvidia/parakeet-tdt-0.6b-v3` |
| Riassunto | LLM multi-provider (vedi impostazioni) |

## Struttura

```
sbobinator/
├── requirements/          # alias pip → pyproject.toml
├── start.bat
├── scripts/install_local.py
├── scripts/download_model.py
├── scripts/download_summary_llm.py
├── src/sbobinator/ui/     # FastAPI + HTMX
├── data/.secrets/         # API key riassunto (gitignored)
└── models/                # ASR .nemo + Qwen GGUF opzionale
```

## Licenza

MIT — modelli NVIDIA/HuggingFace con le rispettive licenze.
