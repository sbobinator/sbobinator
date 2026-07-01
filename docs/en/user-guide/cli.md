# Command-line interface (CLI)

Entry point: **`sbobina`** (`src/sbobinator/cli.py`)

## Main commands

| Command | Description |
|---------|-------------|
| `sbobina` | Start the web UI (default) |
| `sbobina ui` | Same, with `--port` option |
| `sbobina worker` | Queue worker (headless) |
| `sbobina transcribe FILE` | Transcribe a file |
| `sbobina jobs list` | List jobs |
| `sbobina jobs show ID` | Job detail |
| `sbobina jobs retry` | Requeue failed jobs |
| `sbobina info` | System info |

---

## `sbobina transcribe`

### Job mode (default)

Creates a job in `data/output/jobs/`, processes it, and saves everything in the job folder.

```cmd
sbobina transcribe video.mp4
sbobina transcribe audio.wav -s
sbobina transcribe audio.wav -s --summary-mode abstractive
sbobina transcribe audio.wav -d cpu -m nvidia/parakeet-tdt-0.6b-v3
```

| Option | Description |
|--------|-------------|
| `-s`, `--summarize` | Generate a summary |
| `--summary-mode` | `extractive` or `abstractive` |
| `--summary-length` | `auto`, `short`, `normal`, `detailed` |
| `-d`, `--device` | `cpu` or `cuda` |
| `-m`, `--model` | NeMo model |
| `-v`, `--verbose` | Detailed logs |

### Legacy mode (`--legacy-output`)

Saves directly to `data/output/` without a job registry (may overwrite).

```cmd
sbobina transcribe file.wav -o data/output --legacy-output
sbobina transcribe file.wav --legacy-output -f txt -f srt -s
```

---

## `sbobina worker`

Processes the queue headlessly (Docker, server):

```cmd
sbobina worker
sbobina worker --interval 2.0
```

Loop: takes a `queued` job → `running` → pipeline → `completed`/`failed`.

---

## `sbobina jobs`

```cmd
sbobina jobs list
sbobina jobs list --status completed -n 50
sbobina jobs show 20260628_102554_campione-italiano-breve
sbobina jobs retry
sbobina jobs retry 20260628_102554_campione-italiano-breve
```

`retry` requeues `failed` or `cancelled` jobs — the source files stay in the job folder.

---

## `sbobina info`

Shows version, model, device, jobs folder.

---

## Examples

```cmd
REM Transcription with extractive summary
sbobina transcribe data\input\discorso.wav -s

REM Worker only (UI started separately)
sbobina worker

REM Retry all failed jobs
sbobina jobs retry
```

See also [Full CLI reference](../reference/cli-reference.md).
