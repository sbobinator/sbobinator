# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

#!/usr/bin/env python3
"""Publish MkDocs to sbobinator.github.io (same flow as CryptoQuantix publish_docs)."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "docs" / "requirements.txt"
# Sibling clone: GitHub user/org Pages repo (branch main — no Actions, no gh-pages).
PAGES_REPO = ROOT.parent / "sbobinator.github.io"
# Same subfolder as CryptoQuantix: https://sbobinator.github.io/docs/
PAGES_SUBDIR = "docs"


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd or ROOT, check=True)


def main() -> int:
    print("=== Sbobinator — publish documentation ===\n")
    if not (PAGES_REPO / ".git").is_dir():
        print(f"[FAIL] Pages repo not found: {PAGES_REPO}")
        print("\nOne-time setup (sibling folder, like CryptoQuantix):")
        print(f"  cd {ROOT.parent}")
        print("  git clone https://github.com/sbobinator/sbobinator.github.io.git")
        print("\nGitHub Pages: serve from branch main on that repo (default for *.github.io).")
        return 1

    run([sys.executable, "-m", "pip", "install", "-r", str(REQ)])

    build_dir = Path(tempfile.mkdtemp(prefix="sbobinator_docs_"))
    try:
        print(f"\n[1/3] mkdocs build -> {build_dir}")
        run([sys.executable, "-m", "mkdocs", "build", "-d", str(build_dir)])

        target = PAGES_REPO / PAGES_SUBDIR
        print(f"[2/3] Copy -> {target}")
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(build_dir, target)

        print(f"[3/3] git commit in {PAGES_REPO}")
        run(["git", "add", PAGES_SUBDIR], cwd=PAGES_REPO)
        status = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=PAGES_REPO,
        )
        if status.returncode == 0:
            print("[OK] No documentation changes.")
            return 0

        run(
            ["git", "commit", "-m", "docs: update Sbobinator documentation"],
            cwd=PAGES_REPO,
        )
    finally:
        shutil.rmtree(build_dir, ignore_errors=True)

    print("\n[OK] Commit created in sbobinator.github.io")
    print(f"To publish: cd {PAGES_REPO} && git push")
    print("Site: https://sbobinator.github.io/docs/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
