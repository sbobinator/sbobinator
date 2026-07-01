# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

#!/usr/bin/env python3
"""Svuota data/output/jobs (DB + cartelle job), mantiene .gitkeep."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / "data" / "output" / "jobs"


def main() -> int:
    if not JOBS.exists():
        print("Nessuna cartella jobs da pulire.")
        return 0

    removed_dirs = 0
    removed_files = 0
    for item in JOBS.iterdir():
        if item.name == ".gitkeep":
            continue
        if item.is_dir():
            shutil.rmtree(item)
            removed_dirs += 1
        else:
            item.unlink()
            removed_files += 1

    print(f"Pulito: {removed_dirs} cartelle job, {removed_files} file (queue.db incluso).")
    print(f"Storico vuoto. Cartella: {JOBS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
