# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""Download modello Qwen GGUF per riassunto locale."""

from __future__ import annotations

import sys

from sbobinator.config import (
    LOCAL_LLM_GGUF_FILE,
    MIN_RAM_GB,
    local_gguf_path,
    local_llm_dir,
    models_dir,
    system_ram_gb,
)

HF_REPO = "Qwen/Qwen2.5-3B-Instruct-GGUF"
HF_FILE = LOCAL_LLM_GGUF_FILE


def download_local_summary_llm() -> int:
    """Scarica Qwen se assente. Ritorna 0 se ok/già presente, 1 se errore."""
    existing = local_gguf_path()
    if existing:
        print(f"Già presente: {existing}")
        return 0

    dest_dir = local_llm_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / HF_FILE

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


def ensure_local_summary_llm_auto() -> None:
    """Avvio Docker: scarica Qwen solo se RAM sufficiente e modello assente."""
    existing = local_gguf_path()
    if existing:
        print(f"[sbobinator] LLM locale già presente: {existing}")
        return

    ram = system_ram_gb()
    if ram is not None and ram < MIN_RAM_GB:
        print(
            f"[sbobinator] LLM locale non scaricato: RAM ~{ram:.1f} GB "
            f"(richiesti ≥ {MIN_RAM_GB} GB). Usa riassunto cloud."
        )
        return

    ram_label = f"~{ram:.1f} GB" if ram is not None else "sufficiente"
    print(f"[sbobinator] RAM {ram_label} — download LLM locale Qwen (~2 GB)...")
    if download_local_summary_llm() != 0:
        print(
            "[sbobinator] Download LLM locale fallito. "
            "Riassunto cloud resta disponibile se configurato."
        )
