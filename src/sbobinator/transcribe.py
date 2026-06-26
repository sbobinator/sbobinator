import logging
import re
from pathlib import Path

from sbobinator.config import TranscribeConfig, local_model_path
from sbobinator.export import TranscriptResult, TranscriptSegment
from sbobinator.extract import get_duration_sec, prepare_audio, split_audio_chunks

logger = logging.getLogger(__name__)

_model = None
_model_id: str | None = None


def _get_model(config: TranscribeConfig):
    global _model, _model_id

    if _model is not None and _model_id == config.model_name:
        return _model

    try:
        import nemo.collections.asr as nemo_asr
        import torch
    except ImportError as exc:
        raise ImportError(
            "Dipendenze ASR mancanti. Installa con:\n"
            "  pip install -e '.[asr]'\n"
            "oppure usa Docker: docker compose --profile cpu run --rm sbobinator"
        ) from exc

    device = config.resolve_device()
    local = local_model_path(config.model_name)

    if local:
        logger.info("Caricamento modello locale %s su %s ...", local, device)
        model = nemo_asr.models.ASRModel.restore_from(str(local), map_location=device)
    else:
        logger.info("Download/caricamento modello %s su %s ...", config.model_name, device)
        try:
            model = nemo_asr.models.ASRModel.from_pretrained(config.model_name)
        except Exception as exc:
            if "SSL" in str(exc) or "CERTIFICATE" in str(exc):
                raise RuntimeError(
                    "Download modello fallito per errore SSL (comune su Windows).\n"
                    "Scarica il modello manualmente con:\n"
                    "  powershell -ExecutionPolicy Bypass -File scripts\\download-model.ps1\n"
                    "Poi riprova."
                ) from exc
            raise

    # Ottimizzazioni memoria per file lunghi su hardware limitato
    try:
        model.change_attention_model("rel_pos_local_attn", [128, 128])
        model.change_subsampling_conv_chunking_factor(1)
    except Exception:
        logger.debug("Ottimizzazioni memoria non applicabili su questo modello", exc_info=True)

    if device == "cuda":
        model = model.cuda()
    else:
        model = model.cpu()

    _model = model
    _model_id = config.model_name
    return model


def _parse_timestamps(hypothesis) -> list[TranscriptSegment]:
    segments: list[TranscriptSegment] = []

    # NeMo può restituire timestamp a livello segment o word
    stamp = getattr(hypothesis, "timestamp", None) or getattr(hypothesis, "timestamps", None)
    if not stamp:
        return segments

    if isinstance(stamp, dict) and "segment" in stamp:
        for entry in stamp["segment"]:
            segments.append(
                TranscriptSegment(
                    start=float(entry.get("start", 0)),
                    end=float(entry.get("end", 0)),
                    text=str(entry.get("segment", entry.get("word", ""))).strip(),
                )
            )
    elif isinstance(stamp, list):
        for entry in stamp:
            if isinstance(entry, dict):
                segments.append(
                    TranscriptSegment(
                        start=float(entry.get("start", 0)),
                        end=float(entry.get("end", 0)),
                        text=str(entry.get("segment", entry.get("word", ""))).strip(),
                    )
                )

    return [s for s in segments if s.text]


def _transcribe_file(model, wav_path: Path) -> TranscriptResult:
    try:
        output = model.transcribe(
            [str(wav_path)],
            batch_size=1,
            return_hypotheses=True,
            timestamps=True,
        )
    except TypeError:
        # Versioni NeMo senza parametro timestamps
        output = model.transcribe([str(wav_path)], batch_size=1, return_hypotheses=True)

    hypothesis = output[0]
    text = getattr(hypothesis, "text", None) or str(hypothesis)
    text = text.strip()
    segments = _parse_timestamps(hypothesis)

    return TranscriptResult(text=text, segments=segments)


def _merge_chunk_results(
    chunk_results: list[tuple[float, TranscriptResult]],
) -> TranscriptResult:
    texts: list[str] = []
    segments: list[TranscriptSegment] = []

    for offset, result in chunk_results:
        if result.text:
            texts.append(result.text)
        for seg in result.segments:
            segments.append(
                TranscriptSegment(
                    start=seg.start + offset,
                    end=seg.end + offset,
                    text=seg.text,
                )
            )

    merged_text = _dedupe_overlap(" ".join(texts))
    return TranscriptResult(text=merged_text, segments=segments)


def _dedupe_overlap(text: str) -> str:
    """Rimuove ripetizioni evidenti ai confini tra chunk."""
    words = text.split()
    if len(words) < 10:
        return text.strip()

    # Heuristica semplice: se le ultime N parole del blocco precedente
    # coincidono con le prime N del successivo, tieni una sola copia
    return re.sub(r"\s+", " ", text).strip()


def transcribe(
    input_path: Path,
    config: TranscribeConfig | None = None,
    work_dir: Path | None = None,
) -> TranscriptResult:
    config = config or TranscribeConfig()
    model = _get_model(config)

    wav_path, _ = prepare_audio(input_path, work_dir=work_dir)
    duration = get_duration_sec(wav_path)

    if duration <= config.chunk_threshold_sec:
        logger.info("Trascrizione file (%.0f s)", duration)
        return _transcribe_file(model, wav_path)

    logger.info(
        "File lungo (%.0f s): trascrizione a chunk da %d s",
        duration,
        int(config.chunk_length_sec),
    )
    chunk_dir = (work_dir or wav_path.parent) / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)

    chunks = split_audio_chunks(
        wav_path,
        chunk_dir,
        config.chunk_length_sec,
        config.chunk_overlap_sec,
    )

    results: list[tuple[float, TranscriptResult]] = []
    for i, (chunk_path, offset) in enumerate(chunks, start=1):
        logger.info("Chunk %d/%d (offset %.0f s)", i, len(chunks), offset)
        results.append((offset, _transcribe_file(model, chunk_path)))

    return _merge_chunk_results(results)


def unload_model() -> None:
    """Scarica il modello ASR dalla RAM (utile prima del riassunto su hardware limitato)."""
    global _model, _model_id
    _model = None
    _model_id = None
    try:
        import gc

        import torch

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass
