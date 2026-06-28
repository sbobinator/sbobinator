# Interfaccia a riga di comando (CLI)

Entry point: **`sbobina`** (`src/sbobinator/cli.py`)

## Comandi principali

| Comando | Descrizione |
|---------|-------------|
| `sbobina` | Avvia UI web (default) |
| `sbobina ui` | Idem, opzione `--port` |
| `sbobina worker` | Worker coda (headless) |
| `sbobina transcribe FILE` | Trascrive un file |
| `sbobina jobs list` | Elenco lavori |
| `sbobina jobs show ID` | Dettaglio lavoro |
| `sbobina jobs retry` | Rimette in coda i falliti |
| `sbobina info` | Info sistema |

---

## `sbobina transcribe`

### Modalità job (default)

Crea un job in `data/output/jobs/`, elabora, salva tutto nella cartella job.

```cmd
sbobina transcribe video.mp4
sbobina transcribe audio.wav -s
sbobina transcribe audio.wav -s --summary-mode abstractive
sbobina transcribe audio.wav -d cpu -m nvidia/parakeet-tdt-0.6b-v3
```

| Opzione | Descrizione |
|---------|-------------|
| `-s`, `--summarize` | Genera riassunto |
| `--summary-mode` | `extractive` o `abstractive` |
| `--summary-length` | `auto`, `short`, `normal`, `detailed` |
| `-d`, `--device` | `cpu` o `cuda` |
| `-m`, `--model` | Modello NeMo |
| `-v`, `--verbose` | Log dettagliati |

### Modalità legacy (`--legacy-output`)

Salva direttamente in `data/output/` senza registro job (può sovrascrivere).

```cmd
sbobina transcribe file.wav -o data/output --legacy-output
sbobina transcribe file.wav --legacy-output -f txt -f srt -s
```

---

## `sbobina worker`

Elabora la coda in modo headless (Docker, server):

```cmd
sbobina worker
sbobina worker --interval 2.0
```

Loop: prende job `queued` → `running` → pipeline → `completed`/`failed`.

---

## `sbobina jobs`

```cmd
sbobina jobs list
sbobina jobs list --status completed -n 50
sbobina jobs show 20260628_102554_campione-italiano-breve
sbobina jobs retry
sbobina jobs retry 20260628_102554_campione-italiano-breve
```

`retry` rimette in coda job `failed` o `cancelled` — i file sorgente restano nella cartella job.

---

## `sbobina info`

Mostra versione, modello, device, cartella lavori.

---

## Esempi

```cmd
REM Trascrizione con riassunto estrattivo
sbobina transcribe data\input\discorso.wav -s

REM Solo worker (UI avviata separatamente)
sbobina worker

REM Ritenta tutti i job falliti
sbobina jobs retry
```

Vedi anche [Riferimento CLI completo](../reference/cli-reference.md).
