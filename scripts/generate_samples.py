#!/usr/bin/env python3
"""Scarica campioni italiani da Wikimedia Commons e converte in WAV 16 kHz."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "input"
CACHE_DIR = OUT_DIR / "_wikimedia_cache"

SOURCES = {
    "nespoli": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/f/f4/ESA-Astronaut-Paolo-Nespoli_Voice-intro-ITA.flac/ESA-Astronaut-Paolo-Nespoli_Voice-intro-ITA.flac.mp3?download",
        "title": "Paolo Nespoli (ESA) - Voice intro ITA",
        "license": "CC BY-SA 3.0 (ESA / Wikipedia Voice Intro Project)",
    },
    "cavaliere": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/8/86/Alberto_Cavaliere-Intervista-Storia_di_Roma_in_versi.ogg",
        "title": "Alberto Cavaliere - Intervista Storia di Roma in versi",
        "license": "Pubblico dominio (Italia, registrazione radiofonica 1964)",
    },
    "elitre": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/c/cc/Erica_Elitre,_Wikipedia_e_Wikimedia_(ITA).mp3",
        "title": "Erica Elitre - Wikipedia e Wikimedia (Usmaradio)",
        "license": "CC BY-SA 4.0 (Iolanda Pensa / Wikipedia 20)",
    },
}


def require_tools() -> None:
    for tool in ("curl", "ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise RuntimeError(f"{tool} non trovato nel PATH.")


def download_wikimedia(key: str, meta: dict) -> Path:
    ext = Path(meta["url"].split("?")[0]).suffix or ".bin"
    dest = CACHE_DIR / f"{key}{ext}"
    if dest.is_file() and dest.stat().st_size > 10_000:
        mb = dest.stat().st_size / (1024 * 1024)
        print(f"  Cache: {key} ({mb:.2f} MB)")
        return dest
    print(f"  Download Wikimedia: {meta['title']}...")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["curl", "--ssl-no-revoke", "-L", "-A", "Sbobinator/0.3", "-o", str(dest), meta["url"]],
        check=True,
    )
    if not dest.is_file() or dest.stat().st_size < 10_000:
        raise RuntimeError(f"Download fallito per {key}")
    return dest


def convert_sample(
    input_file: Path,
    output_name: str,
    *,
    duration_sec: int = 0,
    source_note: str,
) -> None:
    out = OUT_DIR / f"{output_name}.wav"
    cmd = ["ffmpeg", "-y", "-i", str(input_file)]
    if duration_sec > 0:
        cmd.extend(["-t", str(duration_sec)])
    cmd.extend(["-ar", "16000", "-ac", "1", str(out)])
    subprocess.run(cmd, check=True, capture_output=True)
    dur = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(out),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    dur_s = float(dur.stdout.strip())
    mb = out.stat().st_size / (1024 * 1024)
    print(f"   OK {output_name}.wav - {dur_s:.1f}s - {mb:.2f} MB")
    print(f"      Fonte: {source_note}")


def write_attribution() -> None:
    path = OUT_DIR / "CAMPIONI-WIKIMEDIA.txt"
    path.write_text(
        f"""Campioni audio - Wikimedia Commons
==================================

campione-italiano-nespoli.wav (~50 s)
  {SOURCES["nespoli"]["title"]}
  {SOURCES["nespoli"]["license"]}

campione-italiano-medio.wav (~2 min)
  {SOURCES["cavaliere"]["title"]} - primi 2 minuti
  {SOURCES["cavaliere"]["license"]}

campione-italiano-lungo.wav (~5 min)
  {SOURCES["elitre"]["title"]} - primi 5 minuti
  {SOURCES["elitre"]["license"]}

campione-italiano-molto-lungo.wav (~10 min)
  {SOURCES["elitre"]["title"]} - file completo
  {SOURCES["elitre"]["license"]}

Rigenera con: python scripts/generate_samples.py
""",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera campioni audio da Wikimedia")
    parser.add_argument(
        "--livello",
        choices=["medio", "lungo", "molto-lungo", "tutti"],
        default="tutti",
    )
    args = parser.parse_args()

    try:
        require_tools()
    except RuntimeError as exc:
        print(f"ERRORE: {exc}", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Sbobinator - campioni da Wikimedia Commons")
    print(f"Output: {OUT_DIR}\n")

    nespoli = download_wikimedia("nespoli", SOURCES["nespoli"])
    cavaliere = download_wikimedia("cavaliere", SOURCES["cavaliere"])
    elitre = download_wikimedia("elitre", SOURCES["elitre"])

    print("\n>> campione-italiano-nespoli")
    convert_sample(nespoli, "campione-italiano-nespoli", source_note=SOURCES["nespoli"]["title"])

    levels = ["medio", "lungo", "molto-lungo"] if args.livello == "tutti" else [args.livello]
    jobs = {
        "medio": ("campione-italiano-medio", cavaliere, 120, SOURCES["cavaliere"]["title"]),
        "lungo": (
            "campione-italiano-lungo",
            elitre,
            300,
            f"{SOURCES['elitre']['title']} (primi 5 min)",
        ),
        "molto-lungo": (
            "campione-italiano-molto-lungo",
            elitre,
            0,
            f"{SOURCES['elitre']['title']} (completo)",
        ),
    }
    for level in levels:
        name, src, dur, note = jobs[level]
        print(f"\n>> {name}")
        convert_sample(src, name, duration_sec=dur, source_note=note)

    write_attribution()
    print("\nFatto. Attribuzioni in data/input/CAMPIONI-WIKIMEDIA.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
