#!/usr/bin/env python3
"""Scarica gsarti/it5-small-news-summarization in models/ (offline, come Parakeet)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbobinator.config import (  # noqa: E402
    DEFAULT_SUMMARY_MODEL_HF,
    local_summary_model_available,
    summary_model_dir,
)

HF_MODEL = DEFAULT_SUMMARY_MODEL_HF
API_URL = f"https://huggingface.co/api/models/{HF_MODEL}/tree/main"

# Solo file necessari per inference Transformers (no flax/tf/msgpack duplicati)
ALLOWED_SUFFIXES = (
    ".json",
    ".model",
    ".safetensors",
    ".bin",
    ".txt",
)
SKIP_NAMES = {
    "flax_model.msgpack",
    "tf_model.h5",
    "rust_model.ot",
    "onnx",
}


def _curl_bin() -> str:
    win_curl = Path(r"C:\Windows\System32\curl.exe")
    if sys.platform == "win32" and win_curl.is_file():
        return str(win_curl)
    found = shutil.which("curl")
    if not found:
        raise RuntimeError("curl non trovato nel PATH.")
    return found


def _curl(args: list[str]) -> subprocess.CompletedProcess[str]:
    extra = ["--ssl-no-revoke"] if sys.platform == "win32" else []
    cmd = [_curl_bin(), *extra, "-L", *args]
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace")


def _list_repo_files() -> list[str]:
    result = _curl(["-s", API_URL])
    if result.returncode != 0:
        raise RuntimeError(f"Impossibile leggere elenco file da HuggingFace: {result.stderr}")
    items = json.loads(result.stdout)
    files: list[str] = []
    for item in items:
        if item.get("type") != "file":
            continue
        name = item["path"]
        if name in SKIP_NAMES:
            continue
        if not any(name.endswith(s) for s in ALLOWED_SUFFIXES):
            continue
        files.append(name)
    if not files:
        raise RuntimeError("Nessun file trovato nel repository HuggingFace.")
    # Preferisci safetensors: non scaricare pytorch_model.bin se c'è safetensors
    if "model.safetensors" in files:
        files = [f for f in files if f != "pytorch_model.bin"]
    return files


def _download_file(rel_path: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://huggingface.co/{HF_MODEL}/resolve/main/{rel_path}"
    print(f"  -> {rel_path}")
    result = subprocess.run(
        [
            _curl_bin(),
            *(
                ["--ssl-no-revoke"]
                if sys.platform == "win32"
                else []
            ),
            "-L",
            "--fail",
            "-C",
            "-",
            "-o",
            str(dest),
            url,
        ],
    )
    if result.returncode != 0:
        raise RuntimeError(f"Download fallito: {rel_path}")


def main() -> int:
    try:
        _curl_bin()
    except RuntimeError as exc:
        print(f"ERRORE: {exc}", file=sys.stderr)
        return 1

    out = summary_model_dir()
    if local_summary_model_available():
        print(f"Modello riassunto IT5 gia presente: {out}")
        return 0

    print(f"Download {HF_MODEL} in {out} ...\n")
    try:
        files = _list_repo_files()
        for rel in files:
            target = out / rel
            if target.is_file() and target.stat().st_size > 0:
                print(f"  skip {rel}")
                continue
            _download_file(rel, target)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERRORE: {exc}", file=sys.stderr)
        return 1

    if not local_summary_model_available():
        print("ERRORE: download incompleto (file mancanti).", file=sys.stderr)
        return 1

    print(f"\nDownload completato: {out}")
    print("Ora puoi usare Riassunto (IT5) nell'interfaccia.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
