# Modelli

Sbobinator usa **due modelli opzionali** per il riassunto e **uno obbligatorio** per la trascrizione. Tutti devono essere **su disco prima dell'uso** — nessun download durante l'elaborazione.

## Modello ASR (obbligatorio)

| Proprietà | Valore |
|-----------|--------|
| Nome HuggingFace | `nvidia/parakeet-tdt-0.6b-v3` |
| File locale | `models/parakeet-tdt-0.6b-v3.nemo` |
| Dimensione | ~2.5 GB |
| Lingue | 25 lingue EU incluso italiano |
| Engine | NVIDIA NeMo |

### Download

```cmd
python scripts\download_model.py
```

Usa **curl** con certificati di sistema (risolve problemi SSL di Python su Windows).

Variabile ambiente alternativa:

```text
NEMO_CACHE_DIR=/percorso/custom
```

Il file deve chiamarsi `parakeet-tdt-0.6b-v3.nemo` dentro quella cartella.

---

## Riassunto estrattivo (nessun modello)

- Algoritmo **LexRank** semplificato
- Sceglie le frasi più rappresentative dal testo trascritto
- Sempre disponibile, offline, istantaneo
- Nessun download

---

## Riassunto astrattivo IT5 (opzionale)

| Proprietà | Valore |
|-----------|--------|
| Nome HuggingFace | `gsarti/it5-small-news-summarization` |
| Cartella locale | `models/it5-small-news-summarization/` |
| Dimensione | ~300–400 MB |
| File richiesti | `config.json`, `spiece.model`, pesi |
| Training | Fine-tuned su riassunto news italiano (Fanpage, Il Post) |

**Non usare** `google/mt5-small` base — non è addestrato per il riassunto.

### Download

```cmd
python scripts\download_summary_model.py
```

L'interfaccia mostra **Riassunto (IT5)** solo se il modello è presente.

### Comportamento a runtime

`src/sbobinator/summarize.py` carica **solo** da `models/it5-small-news-summarization/`. Se manca:

```
Modello riassunto IT5 non trovato in models/it5-small-news-summarization/.
Scaricalo con: python scripts/download_summary_model.py
```

La **trascrizione completa comunque**; solo il riassunto fallisce (senza crash del job).

---

## Docker: modelli nell'immagine

Al `docker build` vengono eseguiti entrambi gli script di download in `/models/`.  
Non serve montare `models/` dal host. Vedi [Docker](../deployment/docker.md).

---

## Tabella riepilogo

| Componente | Path locale | Download | Rete a runtime |
|------------|-------------|----------|----------------|
| Parakeet ASR | `models/*.nemo` | `download_model.py` | No |
| IT5 riassunto | `models/it5-small-news-summarization/` | `download_summary_model.py` | No |
| Riassunto estrattivo | — | — | No |

---

## Licenze

- **Parakeet**: licenza NVIDIA / NeMo — vedi scheda HuggingFace
- **IT5**: licenza Google / paper Sarti & Nissim 2022 — vedi scheda HuggingFace
- Codice Sbobinator: MIT
