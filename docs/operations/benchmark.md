# Benchmark e performance

## Script monitor

```cmd
python scripts\benchmark_monitor.py
```

1. Cattura profilo hardware (CPU, RAM, device ASR)
2. Attende nuovi job (o `--watch` per job esistenti)
3. Aggiorna tabella live ogni N secondi
4. Al termine salva JSON + Markdown in `data/output/`

## Metriche per job

| Metrica | Significato |
|---------|-------------|
| **Audio** | Durata registrazione (ffprobe) |
| **Elab.** | `finished_at - started_at` |
| **Tot.** | `finished_at - queued_at` (include coda) |
| **RTF** | Elab. ÷ Audio (>1 = più lento del realtime) |
| **Vel.** | Audio ÷ Elab. (es. 2x = doppia velocità realtime) |
| **Chars** | Caratteri trascritti |

## RTF — Real Time Factor

- **RTF 0.5** → elabori 1 ora di audio in 30 minuti
- **RTF 1.0** → tempo reale
- **RTF 2.0** → il doppio del tempo reale

## Fattori che influenzano le performance

| Fattore | Effetto |
|---------|---------|
| CPU vs GPU | GPU molto più veloce per NeMo |
| Primo job | Include caricamento modello in RAM (~1–2 min) |
| Job successivi | Modello già in memoria (fino a unload per riassunto) |
| Riassunto mT5 | Scarica ASR, carica mT5 — overhead RAM/tempo |
| Lunghezza audio | Chunking sopra 30 min |
| File breve primo | RTF alto (overhead fisso dominante) |

## Esempio risultati (i5-1235U, CPU, mT5)

| File | Audio | Elab. | RTF |
|------|-------|-------|-----|
| breve 10s | 0:10 | ~1:07 | ~6.6* |
| lungo 5min | 5:00 | ~2:21 | 0.47 |
| molto-lungo 10min | 10:26 | ~3:35 | 0.34 |

\*Il breve include caricamento modello + mT5 al primo job.

## Report salvati

```
data/output/benchmark_20260628_111738.json
data/output/benchmark_20260628_111738.md
```

## Suggerimenti

- Per benchmark pulito: `clean_output.py` prima del run
- Avvia monitor **prima** di accodare i file
- Confronta estrattivo vs mT5 in run separati
