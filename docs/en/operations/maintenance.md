# Maintenance

## Routine

| Frequency | Action |
|-----------|--------|
| Each session | `restart_ui.py` if UI is unstable |
| After testing | `clean_output.py` for a clean history |
| Monthly | Check disk space in `data/output/` and `models/` |
| Updates | `git pull` + `pip install -e ".[local]"` |

## Disk space

| Folder | Typical size |
|--------|--------------|
| `models/parakeet-*.nemo` | ~2.5 GB |
| `models/mt5-small/` | ~1.1 GB |
| Single job | Source audio + a few MB of text |
| `queue.db` | KB–MB |

## Backup

Save:

- `data/output/jobs/` — user results
- `models/` — if you do not want to re-download (optional, re-downloadable)

No need to back up `.venv/`.

## Model updates

Remove files/folders in `models/` and re-run the download scripts.

## Logs

- Worker: stdout of the `sbobina worker` process
- FastAPI: terminal where `restart_ui.py` runs
- Failed jobs: `job.json` `error` field or `sbobina jobs show ID`

## Recovery after crash

```cmd
sbobina jobs retry
python scripts\restart_ui.py
```

The worker automatically recovers orphaned `running` jobs.

## Git cleanup

Output and models are in `.gitignore` — do not commit `queue.db` or audio files.
