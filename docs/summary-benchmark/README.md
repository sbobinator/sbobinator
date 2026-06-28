# Benchmark riassunti (offline)

Confronto **qualità e lunghezza** dei riassunti su trascrizioni già salvate, **senza UI** e **senza ASR**.

## Esecuzione

```cmd
python scripts/summary_benchmark.py
```

Opzioni:

```cmd
python scripts/summary_benchmark.py --only campione-italiano-lungo
python scripts/summary_benchmark.py --skip-abstractive
```

## Output

Ogni run crea una cartella in `runs/YYYYMMDD_HHMMSS/`:

| File | Contenuto |
|------|-----------|
| `REPORT.md` | Tabella comparativa parole/tempi |
| `REPORT.json` | Stessi dati in JSON |
| `<sorgente>/` | `_sorgente.txt` + un file per combinazione |

## Combinazioni testate

| Modalità | Lunghezze |
|----------|-----------|
| `extractive` (sintesi LexRank) | auto, short, normal, detailed |
| `abstractive` (IT5) | auto, short, normal, detailed |

## Valutazione manuale

Apri `REPORT.md`, poi per ogni sorgente confronta i file `.txt` nella sottocartella.

Domande guida:

1. Il riassunto copre i punti principali del parlato?
2. La lunghezza è proporzionata (es. 600 parole → più di 5 righe utili)?
3. IT5 distorce il senso (modello news vs intervista/trascrizione)?

I problemi vanno tracciati in `bug-fix/TRACCIAMENTO-BUG.md` (sezione BUG-SUM).
