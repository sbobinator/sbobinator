#!/usr/bin/env python3
"""Termina le istanze UI/worker di Sbobinator e ne avvia una sola."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT / "src"))

    from sbobinator.ui.process_guard import (
        clear_package_cache,
        ensure_clean_ui_environment,
        pids_on_port,
        verify_runtime,
    )

    print("Pulizia istanze Sbobinator precedenti...")
    killed = ensure_clean_ui_environment(8501)
    clear_package_cache()
    if killed:
        print(f"Terminate {killed} processo/i.")
    else:
        print("Nessuna istanza precedente trovata.")

    try:
        verify_runtime()
    except RuntimeError as exc:
        print(f"ERRORE: {exc}")
        return 1

    if pids_on_port(8501):
        print("ERRORE: porta 8501 ancora occupata dopo la pulizia.")
        print("Chiudi manualmente i processi python/uvicorn e riprova.")
        return 1

    print("Verifica pacchetto OK.")
    print("Avvio interfaccia su http://localhost:8501")
    return subprocess.call(
        [sys.executable, "-m", "sbobinator.cli", "ui"],
        cwd=ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
