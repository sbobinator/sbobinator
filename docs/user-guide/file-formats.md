# Formati file

## Input supportati

### Audio

`.wav`, `.mp3`, `.flac`, `.m4a`, `.ogg`, `.opus`, `.aac`, `.wma`

### Video

`.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, `.m4v`, `.flv`, `.wmv`

L'audio viene estratto con **ffmpeg** a 16 kHz mono PCM (richiesto da NeMo).

---

## Output per job

| File | Formato | Contenuto |
|------|---------|-----------|
| `trascrizione.txt` | Testo piano UTF-8 | Trascrizione completa |
| `sottotitoli.srt` | SubRip | Segmenti con timestamp |
| `riassunto.txt` | Testo piano UTF-8 | Riassunto (se generato) |
| `source.*` | Originale | Copia file caricato |
| `job.json` | JSON | Metadati job |

---

## Formato SRT

Standard SubRip:

```srt
1
00:00:00,000 --> 00:00:05,120
Prima frase trascritta.

2
00:00:05,120 --> 00:00:10,450
Seconda frase.
```

Generato da `src/sbobinator/export.py` dai timestamp NeMo (quando disponibili).

---

## File lunghi

| Soglia | Comportamento |
|--------|---------------|
| ≤ 30 minuti | Trascrizione intera |
| > 30 minuti | Chunk da 30 s con overlap 2 s, poi merge |

Configurabile in `TranscribeConfig` (`chunk_threshold_sec`, ecc.).

---

## Legacy output (`--legacy-output`)

Senza cartella job:

```
data/output/
├── nomestem.txt
├── nomestem.srt
└── nomestem_riassunto.txt
```

Può **sovrascrivere** file con lo stesso nome. Preferire la modalità job predefinita.

---

## Encoding

Tutti i file testo: **UTF-8**.
