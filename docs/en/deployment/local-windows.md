# Local use on Windows

Guide for development and daily use **without Docker**.

## Full setup

```cmd
git clone https://github.com/sbobinator/sbobinator.git
cd sbobinator
python scripts\install_local.py
python scripts\download_model.py
python scripts\download_summary_model.py
```

## Startup

```cmd
start.bat
```

`start.bat` uses:

1. `.venv\Scripts\python.exe` if it exists
2. Otherwise `C:\Python313\python.exe`
3. Runs `scripts\restart_ui.py` (single FastAPI instance)

## Paths

| Item | Path |
|------|------|
| Input | `data\input\` |
| Job output | `data\output\jobs\` |
| Models | `models\` |
| Virtualenv | `.venv\` |

## Global Python vs venv

Recommended: **venv** created by `install_local.py`.  
If you use global Python, ensure `pip install -e ".[local]"` on the same interpreter as `sbobina`.

## WSL

Sbobinator also works in WSL2 Ubuntu with the same Linux commands. HuggingFace SSL on Linux is generally more reliable, but the approach **remains offline** with curl/python download scripts.

## Maintenance

| Operation | Command |
|-----------|---------|
| Clear output | `python scripts\clean_output.py` |
| Clean UI restart | `python scripts\restart_ui.py` |
| Retry failed jobs | `sbobina jobs retry` |
| Benchmark | `python scripts\benchmark_monitor.py` |

## Antivirus

Do not use PowerShell `.ps1` scripts — they may be blocked. Use Python and `start.bat` only.

See [SSL on Windows](../troubleshooting/ssl-windows.md) if downloads fail.
