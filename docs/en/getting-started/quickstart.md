# Quick start

## 1. Install dependencies

```cmd
python scripts\install_local.py
```

or `pip install -r requirements/local.txt`

## 2. Download ASR model (required)

```cmd
python scripts\download_model.py
```

| Script | Size | Required |
|--------|------|----------|
| `download_model.py` | ~2.5 GB | Yes (transcription) |
| `download_summary_llm.py` | ~2 GB | Only for **local** Qwen summary |

**Cloud** summary (DeepSeek, etc.): no model download — only an API key at `/settings/summary`.

---

## 3. Start the web UI

```cmd
start.bat
```

or `sbobina ui` / `python scripts\restart_ui.py`

Open: **http://localhost:8501**

With Docker (`docker compose --profile cpu up`), the UI is at **http://localhost:8502**.

---

## 4. Transcribe a file

1. (Optional) **Summary settings** → DeepSeek or other API key
2. Sidebar → **Generate summary** + engine
3. Upload file → **Queue transcription**
4. Track progress on **`/jobs/{id}`**; full history at **`/jobs`**
5. Results in `data\output\jobs\YYYYMMDD_HHMMSS_filename\`

---

## 5. CLI

```cmd
sbobina transcribe data\input\myfile.wav -s --summary-provider deepseek
```

---

## 6. Clear history

```cmd
python scripts\clean_output.py
```

---

## Structure after first use

```
sbobinator/
├── data/
│   ├── .secrets/       ← summary API keys
│   ├── input/
│   └── output/jobs/
├── models/
│   ├── parakeet-tdt-0.6b-v3.nemo
│   └── qwen2.5-3b-instruct/   ← optional
└── .venv/
```

---

## Common issues

| Symptom | Solution |
|---------|----------|
| `ffmpeg not found` | `winget install Gyan.FFmpeg` |
| Missing dependencies | `pip install -r requirements/local.txt` |
| DeepSeek `Connection error` | `pip install truststore` + restart UI |
| Local summary disabled | RAM < 16 GB or missing GGUF |

See [Troubleshooting](../troubleshooting/common-issues.md).
