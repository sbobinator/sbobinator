# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

#!/usr/bin/env python3
"""Scarica il modello Parakeet con curl (certificati Windows). Nessuno script PowerShell."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbobinator.config import DEFAULT_MODEL, models_dir  # noqa: E402

URL = "https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3/resolve/main/parakeet-tdt-0.6b-v3.nemo"
MIN_COMPLETE_MB = 2200


def _out_file() -> Path:
    name = DEFAULT_MODEL.split("/")[-1]
    return models_dir() / f"{name}.nemo"


def _curl_bin() -> str:
    win_curl = Path(r"C:\Windows\System32\curl.exe")
    if sys.platform == "win32" and win_curl.is_file():
        return str(win_curl)
    found = shutil.which("curl")
    if not found:
        raise RuntimeError("curl non trovato nel PATH.")
    return found


def main() -> int:
    try:
        _curl_bin()
    except RuntimeError:
        print("ERRORE: curl non trovato. Usa Windows 10+ o installa curl.", file=sys.stderr)
        return 1

    MODELS_DIR = models_dir()
    OUT_FILE = _out_file()
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    if OUT_FILE.is_file():
        size_mb = OUT_FILE.stat().st_size / (1024 * 1024)
        if size_mb > MIN_COMPLETE_MB:
            print(f"Modello già presente: {OUT_FILE} ({size_mb:.0f} MB)")
            return 0
        if size_mb > 50:
            print(f"Ripresa download da {size_mb:.0f} MB...")
        else:
            OUT_FILE.unlink(missing_ok=True)

    print("Download modello Parakeet (~2.5 GB)...")
    print(f"Destinazione: {OUT_FILE}")
    print("Può richiedere 10-30 minuti.\n")

    cmd = [
        _curl_bin(),
        *(
            ["--ssl-no-revoke"]
            if sys.platform == "win32"
            else []
        ),
        "-L",
        "-C",
        "-",
        "--progress-bar",
        "-o",
        str(OUT_FILE),
        URL,
    ]
    result = subprocess.run(cmd)
    if result.returncode != 0 or not OUT_FILE.is_file():
        print("ERRORE: download fallito.", file=sys.stderr)
        return 1

    final_mb = OUT_FILE.stat().st_size / (1024 * 1024)
    if final_mb < MIN_COMPLETE_MB:
        print(f"ERRORE: file incompleto ({final_mb:.0f} MB). Rilancia lo script.", file=sys.stderr)
        return 1

    print(f"\nDownload completato: {final_mb:.0f} MB")
    print("Ora riavvia Sbobinator e accoda una sbobinatura.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
