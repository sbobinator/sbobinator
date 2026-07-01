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

## Risorse hardware

Sbobinator gira su **PC Windows/Linux** (installazione Python) o **Linux con Docker** (es. mini PC). Le risorse dipendono da cosa usi: solo trascrizione, riassunto via API cloud, o riassunto locale offline.

### Prerequisiti comuni

| Risorsa | Richiesto |
|---------|-----------|
| **Python** | 3.12+ (solo installazione nativa; Docker include già Python) |
| **ffmpeg** | Obbligatorio — estrae l'audio da video |
| **CPU** | x64 moderna (AMD/Intel); elaborazione **sequenziale** (un job alla volta) |
| **GPU NVIDIA** | Opzionale — accelera solo la **trascrizione** ASR (CUDA). Il riassunto locale Qwen usa CPU |

### Confronto per scenario

| Scenario | RAM sistema | Disco libero | Rete | Modelli su disco |
|----------|-------------|--------------|------|------------------|
| **Solo trascrizione** | **8 GB** min · **16 GB** consigliato | **~6 GB** | Solo al primo setup (download ASR) | Parakeet ~2.5 GB |
| **Trascrizione + riassunto API** | Come sopra (+ pochi MB in più) | Come sopra | **Sì** durante il riassunto (chiamate API) | Solo Parakeet |
| **Trascrizione + riassunto locale** | **≥ 16 GB** (obbligatorio) · **32 GB** ideale per file lunghi | **~8–10 GB** | Solo al primo setup | Parakeet ~2.5 GB + Qwen ~2 GB |

> **Nota:** prima del riassunto locale la pipeline **scarica il modello ASR dalla RAM** per liberare memoria. Non servono 16 GB *in più* oltre al minimo per Qwen, ma il sistema deve avere **almeno 16 GB totali** (RAM fisica, non contando solo la cache).

---

### 1. Solo trascrizione

Trascrizione italiana con NeMo Parakeet — nessun riassunto LLM.

| Risorsa | Dettaglio |
|---------|-----------|
| **RAM** | Minimo **8 GB**. Con file audio **lunghi** (1 h+) o molti job in coda, meglio **16 GB** per evitare pressione memoria durante l'ASR. |
| **Disco** | **~2.5 GB** modello ASR + **~3–4 GB** dipendenze Python/PyTorch/NeMo + spazio per output (`data/output/jobs/`). Totale indicativo **≥ 6 GB** liberi. |
| **Rete** | Solo per scaricare il modello la prima volta (`download_model.py` o build Docker). In uso normale **offline**. |
| **GPU** | Opzionale. Su CPU tipica: ordine di **~2× realtime** (1 minuto di audio ≈ 2 minuti di elaborazione). Con GPU NVIDIA la trascrizione è molto più veloce. |
| **Docker** | L'immagine include già Parakeet (~2.5 GB). Volume `data/` per input/output. |

---

### 2. Trascrizione + riassunto API (cloud)

Stessa base della solo trascrizione; il riassunto gira sui server del provider (DeepSeek, OpenAI, Claude, Gemini, Kimi).

| Risorsa | Dettaglio |
|---------|-----------|
| **RAM** | Come **solo trascrizione** — il LLM non gira in locale. |
| **Disco** | Come **solo trascrizione** — **nessun** modello riassunto da scaricare. |
| **Rete** | **Obbligatoria** quando generi il riassunto (HTTPS verso l'API). La trascrizione resta locale. |
| **API key** | Configurabile da UI (`/settings/summary`) o in `data/.secrets/summary_keys.json`. |
| **Costi** | A carico del provider cloud (token usati sul testo trascritto). |

Adatto a PC con **8 GB di RAM** se usi solo riassunto cloud e non Qwen locale.

---

### 3. Trascrizione + riassunto locale (Qwen)

Riassunto **offline** con Qwen2.5-3B (GGUF Q4) via llama.cpp su CPU.

| Risorsa | Dettaglio |
|---------|-----------|
| **RAM** | **≥ 16 GB** di RAM fisica — soglia verificata all'avvio (UI e Docker). Sotto i 16 GB il motore locale viene disabilitato. **32 GB** (es. mini PC AMD) consigliati per audio lunghi e margine per OS + altre app. |
| **Disco** | Tutto come solo trascrizione **+ ~2 GB** per il GGUF Qwen (`models/qwen2.5-3b-instruct/` o volume Docker `sbobinator-qwen`). Totale indicativo **≥ 8–10 GB** liberi. |
| **Rete** | Solo per il download iniziale di Qwen (`download_summary_llm.py` o auto-download Docker all'avvio). Poi **offline**. |
| **CPU** | Il riassunto locale è **CPU-bound**; testi lunghi possono richiedere diversi minuti (map-reduce su chunk). |
| **Docker** | Se RAM ≥ 16 GB, Qwen si scarica automaticamente al primo avvio del container (~10–20 min, una tantum). |

---

### Docker (mini PC / deploy)

| Profilo | Uso tipico | Porta UI |
|---------|------------|----------|
| `cpu` | Mini PC senza GPU NVIDIA | **8502** → 8501 nel container (`docker-compose.yml`) |
| `gpu` | Server con NVIDIA CUDA | 8502 |

- **Immagine build:** include Parakeet ASR (~2.5 GB nel layer).
- **Volume `data/`:** job, trascrizioni, API key (non perdere in aggiornamenti).
- **Volume `sbobinator-qwen`:** modello Qwen locale (persistente tra rebuild).

Per i dettagli operativi: [docs/deployment/docker.md](docs/deployment/docker.md).

```bash
cd docker
docker compose --profile cpu build
docker compose --profile cpu up -d
```

UI su **http://localhost:8502** (profilo `cpu` nel compose predefinito).

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
