#!/usr/bin/env python3
"""Installazione locale Sbobinator (Windows/Linux/macOS). Nessuno script PowerShell."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_PY = ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / "python"


def run(cmd: list[str], *, cwd: Path = ROOT) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> int:
    print("=== Sbobinator - installazione locale ===\n")

    if not shutil.which("ffmpeg"):
        print("ATTENZIONE: ffmpeg non trovato nel PATH.")
        print("Windows: winget install Gyan.FFmpeg\n")

    if not shutil.which("python") and not sys.executable:
        print("ERRORE: Python 3.12+ non trovato.", file=sys.stderr)
        return 1

    py = sys.executable

    if not VENV_PY.parent.parent.exists():
        print("Creazione virtualenv...")
        run([py, "-m", "venv", str(ROOT / ".venv")])

    if not VENV_PY.exists():
        print(f"ERRORE: virtualenv non trovato: {VENV_PY}", file=sys.stderr)
        return 1

    print("Aggiornamento pip...")
    run([str(VENV_PY), "-m", "pip", "install", "--upgrade", "pip"])

    print("Installazione PyTorch (CPU)...")
    run(
        [
            str(VENV_PY),
            "-m",
            "pip",
            "install",
            "torch",
            "--index-url",
            "https://download.pytorch.org/whl/cpu",
        ]
    )

    print("Installazione Sbobinator con tutte le dipendenze...")
    run([str(VENV_PY), "-m", "pip", "install", "-r", "requirements/local.txt"])

    print("\n=== Installazione completata ===\n")
    print("Avvia l'interfaccia web con:")
    print("  start.bat")
    print("  oppure: sbobina ui")
    print("\nPrimo avvio — scarica i modelli:")
    print("  python scripts/download_model.py           (~2.5 GB, trascrizione ASR)")
    print("  python scripts/download_summary_llm.py     (~2 GB, Qwen locale, opzionale)")
    print("\nRiassunto cloud (DeepSeek, OpenAI, …): configura API key in")
    print("  http://localhost:8501/settings/summary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
