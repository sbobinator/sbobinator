import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from sbobinator.config import AUDIO_EXTENSIONS, SAMPLE_RATE, VIDEO_EXTENSIONS


class FFmpegNotFoundError(RuntimeError):
    pass


def _require_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise FFmpegNotFoundError(
            "ffmpeg non trovato. Installalo e assicurati che sia nel PATH, "
            "oppure usa l'immagine Docker che lo include già."
        )
    return path


def _require_ffprobe() -> str:
    path = shutil.which("ffprobe")
    if not path:
        raise FFmpegNotFoundError("ffprobe non trovato (incluso nel pacchetto ffmpeg).")
    return path


def is_video(path: Path) -> bool:
    return path.suffix.lower() in VIDEO_EXTENSIONS


def is_audio(path: Path) -> bool:
    return path.suffix.lower() in AUDIO_EXTENSIONS


def get_duration_sec(path: Path) -> float:
    ffprobe = _require_ffprobe()
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def extract_audio(input_path: Path, output_path: Path | None = None) -> Path:
    """Estrae o converte l'audio in WAV mono 16 kHz per NeMo."""
    input_path = input_path.resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"File non trovato: {input_path}")

    if output_path is None:
        output_path = input_path.with_suffix(".wav")
    else:
        output_path = output_path.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg = _require_ffmpeg()
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            "1",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )
    return output_path


def prepare_audio(input_path: Path, work_dir: Path | None = None) -> tuple[Path, bool]:
    """
    Restituisce (path_wav, da_eliminare).
    Se l'input è già WAV 16kHz mono ideale, potrebbe comunque riconvertire per sicurezza.
    """
    input_path = input_path.resolve()

    if work_dir is None:
        work_dir = Path(tempfile.mkdtemp(prefix="sbobinator_"))
    else:
        work_dir.mkdir(parents=True, exist_ok=True)

    if is_video(input_path) or not input_path.suffix.lower() == ".wav":
        out = work_dir / f"{input_path.stem}.wav"
        extract_audio(input_path, out)
        return out, True

    # Anche per WAV: normalizza formato
    out = work_dir / f"{input_path.stem}_norm.wav"
    extract_audio(input_path, out)
    return out, input_path != out


def split_audio_chunks(
    wav_path: Path,
    work_dir: Path,
    chunk_length_sec: float,
    overlap_sec: float,
) -> list[tuple[Path, float]]:
    """Divide l'audio in segmenti. Restituisce [(path_chunk, offset_sec), ...]."""
    ffmpeg = _require_ffmpeg()
    duration = get_duration_sec(wav_path)
    chunks: list[tuple[Path, float]] = []
    step = chunk_length_sec - overlap_sec
    offset = 0.0
    index = 0

    while offset < duration:
        chunk_path = work_dir / f"chunk_{index:04d}.wav"
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-ss",
                str(offset),
                "-t",
                str(chunk_length_sec),
                "-i",
                str(wav_path),
                "-acodec",
                "pcm_s16le",
                "-ar",
                str(SAMPLE_RATE),
                "-ac",
                "1",
                str(chunk_path),
            ],
            check=True,
            capture_output=True,
        )
        chunks.append((chunk_path, offset))
        offset += step
        index += 1

    return chunks
