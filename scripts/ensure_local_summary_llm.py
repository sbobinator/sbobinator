#!/usr/bin/env python3
"""Docker / avvio: scarica Qwen locale se RAM sufficiente."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbobinator.local_llm_download import ensure_local_summary_llm_auto  # noqa: E402


def main() -> int:
    ensure_local_summary_llm_auto()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
