# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

#!/usr/bin/env python3
"""Scarica il modello GGUF Qwen2.5 per riassunto locale."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbobinator.local_llm_download import download_local_summary_llm  # noqa: E402


def main() -> int:
    return download_local_summary_llm()


if __name__ == "__main__":
    raise SystemExit(main())
