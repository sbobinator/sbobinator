import os
import subprocess
import sys
import time


def launch_ui(port: int = 8501) -> None:
    from sbobinator.ui.process_guard import (
        ensure_clean_ui_environment,
        pids_on_port,
        verify_runtime,
    )

    verify_runtime()
    killed = ensure_clean_ui_environment(port)
    if killed:
        print(f"Terminate {killed} istanza/e Sbobinator precedente/i.")
        time.sleep(1.0)

    if pids_on_port(port):
        print(f"ERRORE: porta {port} ancora occupata. Esegui: python scripts\\restart_ui.py")
        raise SystemExit(1)

    host = os.environ.get("SBOBINATOR_UI_HOST", "127.0.0.1")
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "sbobinator.ui.server:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    print(f"Avvio interfaccia web (FastAPI) con {sys.executable}")
    print(f"Ascolto su http://{host}:{port}")
    raise SystemExit(subprocess.call(cmd))
