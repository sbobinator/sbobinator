# Common issues

## UI and startup

### ImportError `data_dir` / modules from `sbobinator.config`

**Cause:** A **stale** Streamlit instance still running with cached Python modules (typical after `git pull` or a code update without restarting).

**Solution:**

```cmd
python scripts\restart_ui.py
```

Refreshing the browser (F5) is not enough. `restart_ui.py` terminates all processes on port 8501 and clears `__pycache__`.

Check the sidebar: you should see `Sbobinator v0.3.0` and the correct Python path.

---

### ImportError / missing modules (generic)

```
ImportError: cannot import name '...' from 'sbobinator.jobs'
```

**Cause:** Old Streamlit instances or a `pip install` that is out of sync.

**Solution:**

```cmd
python scripts\restart_ui.py
pip install -e ".[local]"
```

Ctrl+F5 is **not** enough — you need to restart the Python process.

---

### Multiple instances on port 8501

**Symptoms:** Inconsistent behavior, jobs failing at random.

**Solution:**

```cmd
python scripts\restart_ui.py
```

Verify a single LISTENING row:

```cmd
netstat -ano | findstr :8501
```

---

### "Enqueue" button disabled

**Cause:** File uploader inside `st.form` (fixed in v0.3+) or no file selected.

**Solution:** Re-upload the file, press F5, try again.

---

## Transcription

### `Missing ASR dependencies`

```cmd
pip install -e ".[local]"
python scripts\download_model.py
```

---

### `lightning.fabric` / circular import

**Cause:** NeMo loaded in a Streamlit thread (old bug).

**Solution:** Update to v0.3+ with the worker subprocess. Run `restart_ui.py`.

---

### `ffmpeg not found`

Install ffmpeg, reopen the terminal, verify with `ffmpeg -version`.

---

## Summarization

### "Summary requested but not generated"

**Cause:** mT5 not downloaded or an error during summarize.

**Solution:**

```cmd
python scripts\download_summary_model.py
```

Use **extractive** mode if you do not need mT5.

The transcription is still saved in `trascrizione.txt`.

---

### mT5 option not visible in the sidebar

Normal if `models/mt5-small/` is incomplete. Complete the download.

---

## Queue

### Jobs stuck in `running`

```cmd
sbobina jobs retry
python scripts\restart_ui.py
```

---

### All jobs failed at once

Check `sbobina jobs show ID` for the error. Often a missing model or multiple workers.

---

## History

### I see jobs in the UI but files are missing

You deleted folders but not `queue.db`. Use `clean_output.py` or ignore those jobs.

### Re-uploading the same file

If the job is **completed** → new job, new folder. If **queued** → skipped.

---

## Performance

Slow CPU on long files is normal. Use a GPU or wait. See [Benchmark](../operations/benchmark.md).

For SSL on Windows see the [dedicated page](ssl-windows.md).
