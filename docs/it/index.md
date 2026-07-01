# Sbobinator

**Sbobinator** trascrive audio e video in testo in italiano, in locale, usando il modello pre-addestrato [NVIDIA NeMo Parakeet TDT 0.6B v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3).

!!! info "Documentazione bilingue"
    Questa documentazione è disponibile anche in **inglese**. Usa il selettore lingua in alto nella barra di navigazione (plugin i18n MkDocs).

## Cosa fa

| Funzione | Descrizione |
|----------|-------------|
| **Trascrizione** | Audio/video → testo + sottotitoli SRT |
| **Coda job** | Più file elaborati uno alla volta; elenco in `/jobs`, dettaglio in `/jobs/{id}` |
| **Riassunto** | LLM multi-provider (DeepSeek, OpenAI, Qwen locale, …) |
| **Interfaccia web** | FastAPI + HTMX su porta 8501 |
| **CLI** | `sbobina` per automazione e server headless |

## Principi di progetto

1. **Elaborazione locale** — nessun invio di audio a cloud durante l'uso normale.
2. **Modelli offline** — Parakeet (ASR) e opzionale Qwen GGUF in `models/`.
3. **Nessun overwrite** — ogni job ha la sua cartella con timestamp.
4. **Multipiattaforma** — Python nativo (sviluppo) e Docker Linux (deploy).

## Requisiti hardware

Dipendono dallo scenario d'uso (solo trascrizione, riassunto API, riassunto locale). Vedi la guida dedicata:

**[Risorse hardware](getting-started/hardware.md)** — RAM, disco, rete e GPU per ogni modalità.

| Risorsa | Minimo | Consigliato |
|---------|--------|-------------|
| Python | 3.12+ | 3.12 o 3.13 |
| RAM (solo ASR) | 8 GB | 16 GB |
| RAM (Qwen locale) | 16 GB | 32 GB |
| Disco | 6 GB liberi | 10 GB |
| ffmpeg | Obbligatorio | Nel PATH |
| GPU NVIDIA | Opzionale | CUDA per velocità ASR |

## Avvio rapido (Windows, Python)

```cmd
python scripts\install_local.py
python scripts\download_model.py
start.bat
```

Riassunto cloud: configura API key su http://localhost:8501/settings/summary

Apri **http://localhost:8501**, carica un file, clicca **Accoda sbobinatura**.

## Documentazione

| Sezione | Contenuto |
|---------|-----------|
| [Per iniziare](getting-started/overview.md) | Installazione e primi passi |
| [Guida utente](user-guide/web-ui.md) | UI, CLI, coda, riassunti |
| [Architettura](architecture/overview.md) | Componenti e flusso dati |
| [Deploy](deployment/docker.md) | Docker e variabili ambiente |
| [Risoluzione problemi](troubleshooting/common-issues.md) | Errori frequenti |
| [Riferimento](reference/faq.md) | FAQ, schema DB, glossario, licenze |

## Build documentazione locale

```bash
pip install -r docs/requirements.txt
mkdocs serve
```

Sito su http://127.0.0.1:8000 — pubblicazione: `scripts\publish_docs.bat` (o `python scripts/publish_docs.py`), poi `git push` nel repo gemello `sbobinator.github.io`.

## Licenza

**Software proprietario** — Copyright © 2024-2026 [Antonio Trento](https://antoniotrento.net). Uso personale gratuito; uso aziendale/commerciale su licenza a pagamento. Vedi [`LICENSE`](../LICENSE) e [Licenze](reference/licenses.md).

I modelli NVIDIA e HuggingFace hanno licenze proprie.
