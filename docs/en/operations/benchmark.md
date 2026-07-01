# Benchmark and performance

## Monitor script

```cmd
python scripts\benchmark_monitor.py
```

1. Captures hardware profile (CPU, RAM, ASR device)
2. Waits for new jobs (or `--watch` for existing jobs)
3. Updates live table every N seconds
4. On completion saves JSON + Markdown in `data/output/`

## Per-job metrics

| Metric | Meaning |
|--------|---------|
| **Audio** | Recording duration (ffprobe) |
| **Proc.** | `finished_at - started_at` |
| **Total** | `finished_at - queued_at` (includes queue wait) |
| **RTF** | Proc. ÷ Audio (>1 = slower than realtime) |
| **Speed** | Audio ÷ Proc. (e.g. 2x = double realtime) |
| **Chars** | Transcribed characters |

## RTF — Real Time Factor

- **RTF 0.5** → process 1 hour of audio in 30 minutes
- **RTF 1.0** → realtime
- **RTF 2.0** → twice realtime

## Factors affecting performance

| Factor | Effect |
|--------|--------|
| CPU vs GPU | GPU much faster for NeMo |
| First job | Includes model load into RAM (~1–2 min) |
| Later jobs | Model already in memory (until unload for summary) |
| mT5 summary | Unloads ASR, loads mT5 — RAM/time overhead |
| Audio length | Chunking above 30 min |
| Short file first | High RTF (fixed overhead dominates) |

## Example results (i5-1235U, CPU, mT5)

| File | Audio | Proc. | RTF |
|------|-------|-------|-----|
| short 10s | 0:10 | ~1:07 | ~6.6* |
| long 5min | 5:00 | ~2:21 | 0.47 |
| very-long 10min | 10:26 | ~3:35 | 0.34 |

\*The short file includes model load + mT5 on the first job.

## Saved reports

```
data/output/benchmark_20260628_111738.json
data/output/benchmark_20260628_111738.md
```

## Tips

- For a clean benchmark: run `clean_output.py` first
- Start the monitor **before** enqueueing files
- Compare extractive vs mT5 in separate runs
