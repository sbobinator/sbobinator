from dataclasses import dataclass

from enum import Enum

from pathlib import Path



# Modello pre-addestrato: italiano incluso tra le 25 lingue EU

DEFAULT_MODEL = "nvidia/parakeet-tdt-0.6b-v3"

DEFAULT_MODEL_FILE = "parakeet-tdt-0.6b-v3.nemo"

MODELS_DIR = Path("models")



# IT5 fine-tuned per riassunto italiano (news) — NON usare mt5/google base

DEFAULT_SUMMARY_MODEL_HF = "gsarti/it5-small-news-summarization"

SUMMARY_MODEL_FOLDER = "it5-small-news-summarization"





def project_root() -> Path:

    """Root del repo (cartella con pyproject.toml)."""

    return Path(__file__).resolve().parents[2]





def data_dir() -> Path:

    """Cartella dati (input/output). In Docker: SBOBINATOR_DATA=/data."""

    import os



    env = os.environ.get("SBOBINATOR_DATA")

    if env:

        path = Path(env)

        return path if path.is_absolute() else project_root() / path

    return project_root() / "data"





def input_dir() -> Path:

    return data_dir() / "input"





def output_dir() -> Path:

    return data_dir() / "output"





def models_dir() -> Path:

    import os



    env = os.environ.get("NEMO_CACHE_DIR")

    if env:

        path = Path(env)

        return path if path.is_absolute() else project_root() / path

    return project_root() / MODELS_DIR





def summary_model_dir() -> Path:

    """Cartella modello IT5 riassunto (offline, come Parakeet .nemo)."""

    return models_dir() / SUMMARY_MODEL_FOLDER





def local_summary_model_path() -> Path | None:

    """Percorso locale IT5 se scaricato con scripts/download_summary_model.py."""

    d = summary_model_dir()

    has_weights = (d / "model.safetensors").is_file() or (d / "pytorch_model.bin").is_file()

    has_tokenizer = (d / "spiece.model").is_file() or (d / "tokenizer.json").is_file()

    if (d / "config.json").is_file() and has_weights and has_tokenizer:

        return d.resolve()

    return None





def local_summary_model_available() -> bool:

    return local_summary_model_path() is not None





def local_model_path(model_name: str = DEFAULT_MODEL) -> Path | None:

    """Percorso del file .nemo se già scaricato in models/."""

    name = model_name.split("/")[-1]

    path = models_dir() / f"{name}.nemo"

    if path.is_file() and path.stat().st_size > 1_000_000_000:  # ~1 GB minimo

        return path.resolve()

    return None





SAMPLE_RATE = 16_000



# Sopra questa durata si usa trascrizione a chunk (secondi)

CHUNK_THRESHOLD_SEC = 30 * 60  # 30 minuti

CHUNK_LENGTH_SEC = 30

CHUNK_OVERLAP_SEC = 2



VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".flv", ".wmv"}

AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".opus", ".aac", ".wma"}





class SummaryMode(str, Enum):

    extractive = "extractive"

    abstractive = "abstractive"





class SummaryLength(str, Enum):

    auto = "auto"

    short = "short"

    normal = "normal"

    detailed = "detailed"


# LLM locale per riassunto (Qwen2.5 GGUF via llama.cpp)
LOCAL_LLM_FOLDER = "qwen2.5-3b-instruct"
LOCAL_LLM_GGUF_FILE = "qwen2.5-3b-instruct-q4_k_m.gguf"
LOCAL_LLM_CTX = 8192
MIN_RAM_GB = 16


def local_llm_dir() -> Path:
    return models_dir() / LOCAL_LLM_FOLDER


def local_gguf_path() -> Path | None:
    direct = local_llm_dir() / LOCAL_LLM_GGUF_FILE
    if direct.is_file() and direct.stat().st_size > 1_000_000:
        return direct.resolve()
    folder = local_llm_dir()
    if folder.is_dir():
        for candidate in sorted(folder.glob("*.gguf")):
            if candidate.stat().st_size > 1_000_000:
                return candidate.resolve()
    return None


def local_llm_available() -> bool:
    return local_gguf_path() is not None


def system_ram_gb() -> float | None:
    try:
        import psutil

        return psutil.virtual_memory().total / (1024**3)
    except ImportError:
        return None


@dataclass(frozen=True)

class TranscribeConfig:

    model_name: str = DEFAULT_MODEL

    device: str | None = None  # None = auto (cuda se disponibile)

    chunk_threshold_sec: float = CHUNK_THRESHOLD_SEC

    chunk_length_sec: float = CHUNK_LENGTH_SEC

    chunk_overlap_sec: float = CHUNK_OVERLAP_SEC

    cache_dir: Path | None = None



    def resolve_device(self) -> str:

        if self.device:

            return self.device

        try:

            import torch



            return "cuda" if torch.cuda.is_available() else "cpu"

        except ImportError:

            return "cpu"


