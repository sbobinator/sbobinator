#!/usr/bin/env python3
"""Scarica il modello GGUF Qwen2.5 per riassunto locale."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbobinator.config import LOCAL_LLM_FOLDER, LOCAL_LLM_GGUF_FILE, local_llm_dir, models_dir

# HuggingFace repo con GGUF quantizzati (TheBloke / Qwen official mirrors)
HF_REPO = "Qwen/Qwen2.5-3B-Instruct-GGUF"
HF_FILE = LOCAL_LLM_GGUF_FILE


def main() -> int:
    dest_dir = local_llm_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / HF_FILE

    if dest.is_file() and dest.stat().st_size > 1_000_000:
        print(f"Già presente: {dest}")
        return 0

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print(
            "Serve huggingface_hub. Installa con:\n"
            "  pip install huggingface_hub",
            file=sys.stderr,
        )
        return 1

    print(f"Download {HF_REPO}/{HF_FILE} → {dest} ...")
    models_dir().mkdir(parents=True, exist_ok=True)
    cached = hf_hub_download(
        repo_id=HF_REPO,
        filename=HF_FILE,
        local_dir=str(dest_dir),
        local_dir_use_symlinks=False,
    )
    print(f"Completato: {cached}")
    print(f"Cartella modello: {dest_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
