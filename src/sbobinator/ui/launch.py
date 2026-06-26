import subprocess
import sys
from pathlib import Path


def launch_ui(port: int = 8501) -> None:
    app_path = Path(__file__).parent / "app.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    raise SystemExit(subprocess.call(cmd))
