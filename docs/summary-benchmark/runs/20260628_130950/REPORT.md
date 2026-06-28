# Benchmark riassunti Sbobinator

Generato: 2026-06-28T13:13:35
IT5 disponibile: sì

## Tabella comparativa

| Sorgente | Modalità | Lunghezza | Parole src | Parole out | % | Frasi out | sec |
|----------|----------|-----------|------------|------------|---|-----------|-----|
| campione-italiano-breve | extractive | auto | 19 | 19 | 100.0 | 2 | 0.0 |
| campione-italiano-breve | extractive | short | 19 | 19 | 100.0 | 2 | 0.0 |
| campione-italiano-breve | extractive | normal | 19 | 19 | 100.0 | 2 | 0.0 |
| campione-italiano-breve | extractive | detailed | 19 | 19 | 100.0 | 2 | 0.0 |
| campione-italiano-breve | abstractive | auto | 19 | 15 | 78.9 | 2 | 33.52 |
| campione-italiano-breve | abstractive | short | 19 | 15 | 78.9 | 2 | 2.62 |
| campione-italiano-breve | abstractive | normal | 19 | 21 | 110.5 | 2 | 3.35 |
| campione-italiano-breve | abstractive | detailed | 19 | 34 | 178.9 | 3 | 4.33 |
| campione-italiano-lungo | extractive | auto | 641 | 180 | 28.1 | 5 | 0.0 |
| campione-italiano-lungo | extractive | short | 641 | 57 | 8.9 | 2 | 0.0 |
| campione-italiano-lungo | extractive | normal | 641 | 103 | 16.1 | 3 | 0.0 |
| campione-italiano-lungo | extractive | detailed | 641 | 180 | 28.1 | 5 | 0.0 |
| campione-italiano-lungo | abstractive | auto | 641 | 84 | 13.1 | 3 | 11.57 |
| campione-italiano-lungo | abstractive | short | 641 | 84 | 13.1 | 3 | 11.39 |
| campione-italiano-lungo | abstractive | normal | 641 | 84 | 13.1 | 3 | 11.76 |
| campione-italiano-lungo | abstractive | detailed | 641 | 94 | 14.7 | 4 | 13.47 |
| campione-italiano-medio | extractive | auto | 292 | 99 | 33.9 | 5 | 0.0 |
| campione-italiano-medio | extractive | short | 292 | 44 | 15.1 | 2 | 0.0 |
| campione-italiano-medio | extractive | normal | 292 | 67 | 22.9 | 3 | 0.0 |
| campione-italiano-medio | extractive | detailed | 292 | 99 | 33.9 | 5 | 0.0 |
| campione-italiano-medio | abstractive | auto | 292 | 36 | 12.3 | 3 | 5.35 |
| campione-italiano-medio | abstractive | short | 292 | 24 | 8.2 | 2 | 3.27 |
| campione-italiano-medio | abstractive | normal | 292 | 36 | 12.3 | 3 | 5.43 |
| campione-italiano-medio | abstractive | detailed | 292 | 49 | 16.8 | 3 | 6.91 |
| campione-italiano-molto-lungo | extractive | auto | 1336 | 306 | 22.9 | 7 | 0.01 |
| campione-italiano-molto-lungo | extractive | short | 1336 | 219 | 16.4 | 4 | 0.01 |
| campione-italiano-molto-lungo | extractive | normal | 1336 | 306 | 22.9 | 7 | 0.01 |
| campione-italiano-molto-lungo | extractive | detailed | 1336 | 455 | 34.1 | 11 | 0.01 |
| campione-italiano-molto-lungo | abstractive | auto | 1336 | 179 | 13.4 | 7 | 27.82 |
| campione-italiano-molto-lungo | abstractive | short | 1336 | 179 | 13.4 | 7 | 27.8 |
| campione-italiano-molto-lungo | abstractive | normal | 1336 | 179 | 13.4 | 7 | 28.31 |
| campione-italiano-molto-lungo | abstractive | detailed | 1336 | 179 | 13.4 | 7 | 27.82 |

## Come leggere

- Cartella per sorgente: contiene `_sorgente.txt` e un file per ogni combinazione.
- **extractive** = sintesi LexRank (frasi originali selezionate).
- **abstractive** = IT5 (`gsarti/it5-small-news-summarization`).
- Confronta qualità e copertura del contenuto, non solo la lunghezza.

## Note qualità (da valutare a mano)

- Riassunto troppo corto rispetto al testo sorgente?
- Perde concetti chiave della trascrizione?
- IT5 addestrato su **news**, non su parlato/interviste: può deformare il senso.
