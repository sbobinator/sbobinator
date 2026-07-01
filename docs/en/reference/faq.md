# FAQ

## General

### Does Sbobinator send my audio over the internet?

No. After the initial model download, processing is **100% local**. No cloud upload during transcription or summarization.

### Which languages are supported?

Parakeet TDT 0.6B v3 is optimized for **Italian**. It also works on other languages with varying quality.

### Can I use only the CLI without the web interface?

Yes. `sbobina transcribe file.wav` or `sbobina worker` for a headless queue.

---

## Models

### How much disk space do models use?

| Model | Approximate size |
|-------|------------------|
| Parakeet ASR | ~2.5 GB |
| mT5-small | ~1.1 GB |

### Do I need to re-download models after every update?

No, if they remain in `models/`. Update only if the model version changes in the release notes.

### Does Docker download models on every start?

No. They are **in the image** at build time. Only `data/` is mounted from the host.

---

## Queue and jobs

### Why does it process one file at a time?

The worker processes the queue **FIFO** to limit RAM (NeMo + mT5 are heavy).

### Can I process the same file twice?

Yes, if the previous job is `completed`. A **new folder** is created with a new timestamp.

### What happens if I close the browser?

The worker continues in the background. Reopen `http://localhost:8501` to see the status.

### I delete a job folder manually — what happens?

The record remains in `queue.db`. The UI shows the job but files are missing. Use `clean_output.py` for a full reset.

---

## Interface

### Why do I see only one job in the main panel?

The sidebar selects one job at a time. The **queue** at the top lists all. Multi-result improvements are on the roadmap (`evolutive/`).

### Does the worker start automatically?

Yes. Every UI startup calls `start_background_worker()`, which launches a subprocess if not already active.

---

## Summarization

### Extractive vs abstractive?

| Mode | Speed | Quality | Requirements |
|------|-------|---------|--------------|
| Extractive | Instant | Selected original sentences | No extra model |
| Abstractive (mT5) | Slow | Reformulated text | Complete `models/mt5-small/` |

### Transcription is OK but summary fails

Normal if mT5 is missing or there is an SSL error. Text is in `trascrizione.txt`. See [SSL Windows](../troubleshooting/ssl-windows.md).

---

## Performance

### How fast is it on CPU?

Depends on hardware. On a mobile i5 ~**2× realtime** (1 min audio ≈ 2 min processing). NVIDIA GPU greatly reduces ASR time.

### Why is the first job slower?

NeMo model loading into RAM on the first transcription.

---

## Development and deploy

### Why no PowerShell scripts?

Project choice: antivirus compatibility and a cross-platform approach with Python + `cmd`.

### How do I publish the documentation?

From the repo root: `python scripts/publish_docs.py` (or `scripts\publish_docs.bat`) — builds MkDocs and copies HTML to `../sbobinator.github.io/docs/`, then commits there. **No GitHub Actions.** Publish with `git push` in the Pages repo (branch `main`, like CryptoQuantix).
