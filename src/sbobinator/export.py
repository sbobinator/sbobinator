# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class TranscriptResult:
    text: str
    segments: list[TranscriptSegment]

    @property
    def has_timestamps(self) -> bool:
        return bool(self.segments)


def _format_srt_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds % 1) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def export_txt(result: TranscriptResult, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.text.strip() + "\n", encoding="utf-8")
    return output_path


def export_summary_text(text: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text.strip() + "\n", encoding="utf-8")
    return output_path


def export_srt(result: TranscriptResult, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    if result.segments:
        for i, seg in enumerate(result.segments, start=1):
            lines.append(str(i))
            lines.append(f"{_format_srt_time(seg.start)} --> {_format_srt_time(seg.end)}")
            lines.append(seg.text.strip())
            lines.append("")
    else:
        # Fallback: un unico blocco senza timestamp
        lines = ["1", "00:00:00,000 --> 00:00:59,999", result.text.strip(), ""]

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def export_all(
    result: TranscriptResult,
    output_dir: Path,
    stem: str,
    formats: list[str],
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    if "txt" in formats:
        written.append(export_txt(result, output_dir / f"{stem}.txt"))
    if "srt" in formats:
        written.append(export_srt(result, output_dir / f"{stem}.srt"))

    return written
