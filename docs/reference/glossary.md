# Glossario

| Termine | Significato |
|---------|-------------|
| **ASR** | Automatic Speech Recognition — riconoscimento vocale automatico |
| **Parakeet** | Famiglia modelli NVIDIA NeMo per ASR; Sbobinator usa TDT 0.6B v3 |
| **NeMo** | NVIDIA NeMo Toolkit — framework per modelli speech/LLM |
| **mT5** | Multilingual T5 — modello seq2seq Google per riassunto astrattivo |
| **RTF** | Real-Time Factor — tempo_elaborazione / durata_audio; &lt;1 = più veloce del realtime |
| **SRT** | SubRip — formato sottotitoli con timestamp |
| **FIFO** | First In, First Out — ordine coda job |
| **WAL** | Write-Ahead Logging — modalità SQLite per concorrenza lettura/scrittura |
| **Worker** | Processo separato che consuma la coda job |
| **Pipeline** | Sequenza extract → transcribe → summarize → export per un job |
| **Chunking** | Suddivisione audio lungo in segmenti sovrapposti per ASR |
| **Estrattivo** | Riassunto che seleziona frasi dal testo originale |
| **Astrattivo** | Riassunto che genera nuovo testo (mT5) |
| **Stem** | Nome file senza estensione |
| **SBOBINATOR_DATA** | Variabile ambiente root dati (`data/` o `/data` in Docker) |
| **NEMO_CACHE_DIR** | Variabile ambiente directory modelli NeMo/mT5 |
| **Streamlit** | Framework Python per UI web interattiva |
| **Typer** | Libreria CLI basata su Click |
| **ffmpeg** | Tool per conversione estrazione audio da video |
| **ffprobe** | Tool per metadati media (durata, codec) |
| **Headless** | Esecuzione senza interfaccia grafica (solo CLI/worker) |
| **Orphan job** | Job lasciato in `running` dopo crash worker — recuperato al riavvio |
