# Riassunto testo

Dopo la trascrizione, Sbobinator può generare un **riassunto** del testo in `trascrizione.txt`.

## Modalità

### Sintesi estrattiva — default

| Aspetto | Dettaglio |
|---------|-----------|
| Engine | LexRank semplificato (`summarize.py`) |
| Modello | Nessuno |
| Rete | Mai |
| Velocità | Quasi istantaneo |
| Output | Frasi originali selezionate |

**Consigliato** quando serve fedeltà al testo trascritto.

### Riassunto astrattivo (IT5)

| Aspetto | Dettaglio |
|---------|-----------|
| Engine | `gsarti/it5-small-news-summarization` via Transformers |
| Modello | `models/it5-small-news-summarization/` (offline) |
| Velocità | Più lento (CPU: secondi–minuti) |
| Output | Testo riscritto in italiano |

Modello **fine-tuned** per summarization — non il base mT5.

Richiede:

```cmd
python scripts\download_summary_model.py
```

---

## Lunghezza

| Valore | Comportamento |
|--------|---------------|
| `auto` | In base al numero di frasi del testo |
| `short` | Più breve |
| `normal` | Bilanciato |
| `detailed` | Più lungo |

---

## Pipeline

1. Trascrizione NeMo completata
2. `unload_model()` — libera RAM ASR
3. `summarize()` — estrattivo o IT5
4. Salva `riassunto.txt`

Se il riassunto fallisce:

- Job resta **`completed`**
- `has_summary = false`
- `summary_error` contiene il motivo
- Trascrizione e SRT **restano validi**

---

## Chunking testi lunghi (IT5)

Testi > ~3000 caratteri vengono divisi in chunk, riassunti parzialmente e ricombinati.

---

## Confronto pratico

| Criterio | Estrattivo | IT5 |
|----------|------------|-----|
| Setup | Nessuno | Download ~400 MB |
| Offline | Sì | Sì (dopo download) |
| Qualità IT | Fedele al testo | Riassunto generativo |
| CPU lungo audio | Trascurabile | Minuti extra |
| Fallimenti SSL | No | No (se modello locale) |

---

## CLI

```cmd
sbobina transcribe file.wav -s
sbobina transcribe file.wav -s --summary-mode abstractive --summary-length detailed
```

---

## UI

Sidebar → **Riassunto** → attiva toggle → scegli modalità.

Se IT5 non è installato, compare solo **Sintesi (estrativo)** e istruzione per il download.
