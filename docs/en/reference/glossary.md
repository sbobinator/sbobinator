# Glossary

| Term | Meaning |
|------|---------|
| **ASR** | Automatic Speech Recognition |
| **Parakeet** | NVIDIA NeMo ASR model family; Sbobinator uses TDT 0.6B v3 |
| **NeMo** | NVIDIA NeMo Toolkit — framework for speech/LLM models |
| **mT5** | Multilingual T5 — Google seq2seq model for abstractive summarization |
| **RTF** | Real-Time Factor — processing_time / audio_duration; &lt;1 = faster than realtime |
| **SRT** | SubRip — subtitle format with timestamps |
| **FIFO** | First In, First Out — job queue order |
| **WAL** | Write-Ahead Logging — SQLite mode for read/write concurrency |
| **Worker** | Separate process that consumes the job queue |
| **Pipeline** | Sequence extract → transcribe → summarize → export for one job |
| **Chunking** | Splitting long audio into overlapping segments for ASR |
| **Extractive** | Summary that selects sentences from the original text |
| **Abstractive** | Summary that generates new text (mT5) |
| **Stem** | Filename without extension |
| **SBOBINATOR_DATA** | Environment variable for data root (`data/` or `/data` in Docker) |
| **NEMO_CACHE_DIR** | Environment variable for NeMo/mT5 model directory |
| **Streamlit** | Python framework for interactive web UI |
| **Typer** | CLI library based on Click |
| **ffmpeg** | Tool for audio conversion and extraction from video |
| **ffprobe** | Tool for media metadata (duration, codec) |
| **Headless** | Execution without a graphical interface (CLI/worker only) |
| **Orphan job** | Job left in `running` after worker crash — recovered on restart |
