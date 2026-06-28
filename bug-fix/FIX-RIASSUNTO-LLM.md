# FIX-RIASSUNTO-LLM — Tracciamento decisionale e roadmap

> **File:** `bug-fix/FIX-RIASSUNTO-LLM.md`  
> **Creato:** 2026-06-28  
> **Stato:** 📋 Pianificazione — **nessuna implementazione codice** finché non approvato dopo benchmark  
> **Correlato:** `BUG-SUM-019` (mT5), `BUG-SUM-020` (qualità generale), `docs/summary-benchmark/`

---

## 1. Executive summary

La feature **riassunto** in Sbobinator **non è accettabile in produzione** nello stato attuale (sintesi estrattiva LexRank + IT5 news). I output non sono veri riassunti: sono tagli di frasi o testi deformati/inventati.

**Decisione di principio (utente, 28/06/2026):**

- L’approccio attuale è **sbagliato** e va **cambiato completamente**.
- Se offriamo riassunto, deve essere **fatto bene** — altrimenti meglio **non offrirlo**.
- Direzione scelta: **LLM locale** (non API cloud per ora).
- Vincoli hardware: **solo CPU** (GPU in un secondo momento).
- Soglia minima proposta: **16 GB RAM** — sotto questa soglia il riassunto **non si offre**.
- L’utente con hardware sufficiente **sceglie** se generare il riassunto, sapendo che **richiede molto più tempo** della sola trascrizione.

**Blocco esplicito:** nessuna modifica al codice applicativo finché non si completa valutazione scientifica (token, RAM, benchmark LLM) e approvazione utente.

---

## 2. Cronologia del problema

| Data | Evento |
|------|--------|
| Pre-28/06 | Riassunto con `google/mt5-small` base → output inutilizzabile (`<extra_id_0>`, ripetizioni) |
| 28/06 | Sostituito con `gsarti/it5-small-news-summarization` (IT5 news) |
| 28/06 | Utente insoddisfatto: riassunti troppo corti, non spiegano il contenuto |
| 28/06 | Creato `scripts/summary_benchmark.py` + run `docs/summary-benchmark/runs/20260628_130950/` |
| 28/06 | Valutazione IA su tutti i campioni: **nessuna variante è un vero riassunto** |
| 28/06 | Utente: «questa feature così non va» — serve cambio approccio, no patch |
| 28/06 | Scelta strategica: **LLM locale**, CPU, gate 16 GB, opt-in utente |
| 28/06 | Discussione approfondita su **token in input**, contesto, RAM, map-reduce |

---

## 3. Stato attuale del codice (da sostituire, non da patchare)

### 3.1 Sintesi estrattiva (`extractive`)

- **Motore:** LexRank semplificato in `src/sbobinator/summarize.py`
- **Comportamento:** seleziona frasi intere dal testo originale
- **Non è un riassunto:** è un **taglio / antologia** senza filo narrativo
- **Pro:** veloce, offline, zero modelli extra
- **Contro:** su monologhi lunghi sembra copia-incolla a salti; manca chi/cosa/contesto

### 3.2 Riassunto astrattivo (`abstractive`)

- **Motore:** `gsarti/it5-small-news-summarization` via `transformers` pipeline
- **Addestramento:** articoli di **news** in italiano
- **Input:** trascritti **parlati** (interviste, audio Wikimedia, ecc.)
- **Problemi osservati:**
  - Output troppo corto (es. 641 parole → 3–4 frasi)
  - Deformazione del senso (es. inversione posizione su «VIP/elitisti»)
  - Allucinazioni (es. «una delle persone più influenti al mondo»)
  - Parametro `detailed` non cambia quasi nulla su testi lunghi
  - Chunking a 3000 caratteri senza merge intelligente

### 3.3 Conclusione tecnica

Non è un problema di `max_length` o UI. È **scelta errata di metodo e modello** per il caso d’uso (trascrizioni italiane lunghe).

---

## 4. Benchmark esistente (28/06/2026)

### 4.1 Strumento

```cmd
python scripts/summary_benchmark.py
```

- Legge `trascrizione.txt` da `data/output/jobs/*/`
- **Non** usa UI, **non** usa ASR
- 8 combinazioni per file: `extractive|abstractive` × `auto|short|normal|detailed`
- Output: `docs/summary-benchmark/runs/<timestamp>/`

### 4.2 Run di riferimento

**Cartella:** `docs/summary-benchmark/runs/20260628_130950/`

| Sorgente | Parole src | Peggio estrattivo | Peggio IT5 |
|----------|------------|-------------------|------------|
| campione-italiano-breve | 19 | N/A (testo già minimo) | N/A |
| campione-italiano-lungo | 641 | short: 57 parole, 2 frasi | detailed: 94 parole, senso distorto |
| campione-italiano-medio | 292 | frammenti incoerenti | 49 parole, incompleto |
| campione-italiano-molto-lungo | 1336 | collage 11 frasi senza filo | 179 parole, allucinazioni |

### 4.3 Criteri di un «vero riassunto»

1. Dice **chi / cosa / contesto**
2. Estrae **punti principali** in ordine logico
3. È **più corto** dell’originale ma **autosufficiente**
4. **Non inventa** e **non ribalta** il significato
5. Chi legge solo il riassunto **capisce** il contenuto

**Esito:** nessuna delle 8 combinazioni attuali soddisfa questi criteri sui campioni lunghi.

### 4.4 Esempio di riferimento qualità (manuale, non generato)

Per `campione-italiano-lungo` (Erika / Wikimedia), un riassunto accettabile dovrebbe includere almeno:

- Identità e percorso dal 2004
- Ruolo in Wikimedia Foundation dal 2013 (community relations)
- Attività su copyright, TRS, GLAM, Wikimedia Italia
- Messaggio sulle «5 caratteristiche» uniche di Wikipedia
- Visione Wikimedia centrata sulle **persone**, non sui contenuti
- Critica all’elitismo basato sul numero di edit / «VIP»
- Chiusura su demografia reale di internet e ottimismo sul movimento

L’IT5 detailed attuale **inverte** il senso sulla parte VIP/elitisti → **inaccettabile in produzione**.

---

## 5. Decisione strategica: LLM locale

### 5.1 Perché LLM locale

| Motivo | Dettaglio |
|--------|-----------|
| Qualità | Unico modo realistico per riassunti **astratti** e coerenti su parlato trascritto |
| Privacy | Dati restano in locale (allineato al prodotto) |
| Esperienza utente | Utente già convinto: «a occhi chiusi» per questo use case |
| Qwen | Buona reputazione multilingue/italiano; già usato con successo in altri progetti |

### 5.2 Trade-off accettati

| Aspetto | Realtà |
|---------|--------|
| **Tempo** | Riassunto molto più lento della trascrizione (es. ~5 min ASR + **10–20 min** riassunto su CPU) |
| **RAM** | Serve memoria per modello + **KV cache** del contesto |
| **CPU** | Nessuna GPU per ora → token/sec bassi |
| **Hardware eterogeneo** | Non tutti i PC possono avere la feature |

### 5.3 Cosa NON rifare

- ❌ Alzare solo `max_length` su IT5
- ❌ Aggiungere altro modello news senza benchmark
- ❌ Chiamare «riassunto» l’estrattivo LexRank
- ❌ Patchare solo la UI
- ❌ Implementare codice prima del benchmark LLM approvato

---

## 6. Vincoli hardware e prodotto

### 6.1 Regole proposte (da confermare)

| Condizione | Comportamento prodotto |
|------------|------------------------|
| RAM sistema **< 16 GB** | Riassunto LLM **non offerto** (solo trascrizione TXT/SRT) |
| RAM sistema **≥ 16 GB** | Riassunto **disponibile** ma **opt-in** esplicito |
| RAM libera insufficiente al momento del riassunto (dopo unload ASR) | Non avviare; messaggio chiaro |
| CPU only | Accettato; mostrare stima tempi |
| GPU | Fuori scope fase 1; valutazione successiva |

### 6.2 Perché 16 GB come soglia

- NeMo Parakeet in trascrizione: ~3–6 GB RAM
- Strategia: **sequenza** trascrizione → unload ASR → caricamento LLM
- Su 16 GB: spazio per Qwen 3B quantizzato + contesto moderato (`n_ctx` 8K)
- Su 8 GB: trascrizione già critica; LLM serio **non realistico**

### 6.3 Opt-in utente

L’utente con hardware sufficiente **decide** se generare il riassunto, con messaggio tipo:

> «Il riassunto può richiedere molti minuti in più della sola sbobinatura (soprattutto su CPU).»

La coda job già esiste: il riassunto può essere fase separata con progresso dedicato.

---

## 7. Token in input — analisi scientifica (critica)

> **Punto sollevato dall’utente:** se il modello non «mangia» tutto il testo rilevante in input (o lo gestisce male a chunk), il riassunto resta scarso **anche con il miglior LLM**.

### 7.1 Perché i token contano

| Componente | Ruolo |
|------------|--------|
| **Token input** | Trascrizione codificata dal tokenizer del modello |
| **Contesto (`n_ctx`)** | Massimo token che il modello può vedere in un passaggio |
| **Token output** | Spazio per il riassunto generato |
| **KV cache** | Memoria extra che cresce con `n_ctx` — critica su CPU/RAM |

Se `token_input + token_output + overhead > n_ctx` → testo troncato o strategia map-reduce obbligatoria.

### 7.2 Stima token sui campioni attuali (italiano)

Regola rapida: **~1,3–1,6 token/parola**, **~4 caratteri/token**.

| Campione | Parole ~ | Token input ~ | Entra in 8K? | Entra in 32K? |
|----------|----------|---------------|--------------|---------------|
| breve | 19 | ~30 | ✅ | ✅ |
| medio | 292 | ~400–450 | ✅ | ✅ |
| lungo (Erika) | 641 | ~900–1 000 | ✅ | ✅ |
| molto-lungo | 1 336 | ~1 800–2 100 | ✅ | ✅ |

**I campioni attuali entrano in un singolo passaggio anche con `n_ctx=8192`.**

### 7.3 Stima per audio lunghi (produzione reale)

| Durata parlato | Parole trascritte ~ | Token input ~ |
|----------------|---------------------|---------------|
| 30 min | 3 000–4 500 | 4 000–7 000 |
| 1 h | 6 000–9 000 | 8 000–14 000 |
| 2 h | 12 000–18 000 | 16 000–28 000 |

Per questi casi:

- `n_ctx=8192` → **map-reduce obbligatorio**
- `n_ctx=32768` → singolo passaggio possibile ma **KV cache enorme** su 16 GB

### 7.4 KV cache e RAM (ordine di grandezza, da misurare su hardware reale)

| Setup | RAM modello ~ | KV cache extra ~ |
|-------|---------------|------------------|
| Qwen 3B Q4, `n_ctx=4096` | 2–2,5 GB | +0,5–1 GB |
| Qwen 3B Q4, `n_ctx=8192` | 2–2,5 GB | +1–2 GB |
| Qwen 3B Q4, `n_ctx=32768` | 2–2,5 GB | +4–8 GB |
| Qwen 7B Q4, `n_ctx=8192` | 4,5–5 GB | +2–4 GB |
| Qwen 7B Q4, `n_ctx=32768` | 4,5–5 GB | +8–16 GB |

**⚠️ Errore da evitare:** impostare `n_ctx=32768` «perché Qwen lo supporta» su PC 16 GB → OOM, swap, tempi peggiori.

### 7.5 Strategie per testi lunghi

#### A) Single-pass

- Tutta la trascrizione in un prompt
- Possibile solo se `token_input + margin < n_ctx` e RAM sufficiente

#### B) Map-reduce

```
Trascrizione → chunk (es. 3K token, overlap 200 token)
            → riassunto per chunk
            → testo combinato
            → riassunto finale (eventuale secondo passaggio)
```

- **Pro:** `n_ctx` basso per passaggio, funziona su 16 GB
- **Contro:** moltiplicatore sui tempi; rischio perdita coerenza se taglio chunk mal fatto
- **Requisito:** taglio per frase/paragrafo/SRT, da validare nel benchmark

#### C) Soglie operative proposte

| Token trascrizione | Strategia |
|--------------------|-----------|
| ≤ 6 000 | Single-pass |
| 6 000 – 24 000 | Map-reduce |
| > 24 000 | Map-reduce + avviso tempi / possibile limite su hardware debole |

---

## 8. Modelli LLM proposti (CPU, italiano)

### 8.1 Preferenza: famiglia Qwen 2.5

Motivazione utente + tecnica: buon italiano, usato con successo altrove, adatto a summarization con prompt.

### 8.2 Tier consigliati

| Tier | Modello | Quant. | RAM modello | Target hardware | Note |
|------|---------|--------|-------------|-----------------|------|
| **Default** | **Qwen2.5-3B-Instruct** | Q4_K_M | ~2–2,5 GB | 16 GB+, CPU | Miglior compromesso qualità/tempo/RAM |
| Alternativa | Llama 3.2 3B Instruct | Q4_K_M | ~2–2,5 GB | 16 GB+, CPU | Simile, italiano leggermente inferiore |
| Qualità lenta | Qwen2.5-7B-Instruct | Q4_K_M | ~4,5–5 GB | 32 GB ideale, 16 GB stretto | Migliore ma **molto** più lento su CPU |
| Solo anteprima | Qwen2.5-1.5B-Instruct | Q4 | ~1 GB | — | Veloce ma rischio qualità insufficiente |

### 8.3 Runtime proposto (fase implementazione futura)

| Opzione | Uso |
|---------|-----|
| **llama.cpp** + GGUF | Produzione, CPU-first, embeddabile nel worker |
| `llama-cpp-python` | Binding Python per integrazione Sbobinator |
| Ollama | Comodo in dev; meno controllo in produzione |

Modello scaricato una volta in `models/` (come ASR e vecchio IT5).

### 8.4 Profili prodotto (`n_ctx` per RAM)

| Profilo | RAM min | Modello | `n_ctx` | Uso |
|---------|---------|---------|---------|-----|
| **Standard** | 16 GB | Qwen 3B Q4 | **8192** | Trascrizioni fino ~5–6K token |
| **Lungo** | 32 GB | Qwen 3B o 7B Q4 | **16384** | File più lunghi |
| **Qualità** | 32 GB | Qwen 7B Q4 | **8192** | Riassunto migliore, tempi alti |

### 8.5 Tempi attesi (CPU, indicativi)

| Modello | Testo ~600–1300 parole | Note |
|---------|------------------------|------|
| Qwen 3B Q4 | ~3–8 min | Default realistico |
| Qwen 7B Q4 | ~10–25 min | Coerente con osservazione utente 5+15 min |
| Map-reduce | moltiplicatore × N chunk | Da misurare |

---

## 9. Architettura logica futura (non implementata)

```
[Trascrizione NeMo] → unload ASR
                   → rilevamento RAM
                   → se < 16 GB: skip riassunto
                   → conteggio token trascrizione
                   → scelta strategia (single-pass / map-reduce)
                   → scelta profilo modello (3B default)
                   → prompt fisso (trascritto parlato, IT, no invenzioni)
                   → generazione riassunto
                   → salvataggio riassunto.txt
```

### 9.1 Prompt (linee guida, da definire nel benchmark)

- Input: trascritto da parlato (non articolo)
- Output: riassunto in italiano, prosa, punti principali in ordine logico
- Vincoli: non inventare; non omettere chi parla e di cosa tratta; lunghezza proporzionata

### 9.2 Integrazione coda

- `summary_requested` + `summary_mode` già in job record
- Nuovo valore mode: es. `llm` (da definire) al posto di `abstractive`/`extractive` o in aggiunta
- Progress message dedicato: «Riassunto LLM (3/5 chunk)…»

---

## 10. Processo di valutazione prima del codice

### Fase 1 — Metriche (scientifico)

Per ogni `trascrizione.txt` del benchmark:

1. Conteggio token con **tokenizer Qwen** (non stima a occhio)
2. Tabella: parole, caratteri, token, % di `n_ctx` per profilo 8K/16K
3. Stima RAM per profilo (modello + KV cache)
4. Salvare in `docs/summary-benchmark/` (nuova run o appendice)

### Fase 2 — Benchmark LLM

1. Scaricare GGUF Qwen2.5-3B-Instruct (e opzionale 7B)
2. Stesso input del benchmark attuale
3. Prompt unificato per summarization parlato
4. Output in `docs/summary-benchmark/runs/<timestamp>-llm/`
5. Valutazione **umana** (utente) + checklist criteri §4.3

### Fase 3 — Decisione go/no-go

| Esito | Azione |
|-------|--------|
| Qwen 3B passa criteri su campioni lunghi | Implementare motore LLM + gate hardware |
| Solo 7B passa | Offrire 7B solo su 32 GB o con avviso tempi estremi |
| Nessun modello locale passa su CPU 16 GB | Rivalutare GPU, API cloud, o **rimuovere feature** |

### Fase 4 — Implementazione (solo dopo OK utente)

- Sostituire `summarize.py` motore astrattivo/estrattivo come «riassunto prodotto»
- Script download modello GGUF
- Rilevamento RAM
- UI: opt-in, stima tempi, disabilitazione sotto soglia
- Docker: modello in immagine o download al build
- Aggiornare `FIX-RIASSUNTO-LLM.md` e chiudere `BUG-SUM-020`

---

## 11. Cosa tenere / cosa rimuovere (decisione futura)

| Componente attuale | Destino proposto |
|--------------------|------------------|
| IT5 news | **Rimuovere** come motore riassunto |
| LexRank estrattivo | **Non** chiamarlo «riassunto»; opzionale come «estratti» o rimuovere |
| `summary_benchmark.py` | **Tenere ed estendere** per LLM |
| UI «Riassunto (IT5)» | Sostituire con «Riassunto (LLM)» o disabilitare fino a pronto |

---

## 12. Rischi residui

| Rischio | Mitigazione |
|---------|-------------|
| Tempi inaccettabili su CPU | Opt-in, stima tempi, profilo 3B default |
| RAM insufficiente con contesto alto | `n_ctx` conservativo, map-reduce, gate 16 GB |
| Qualità map-reduce bassa | Taglio intelligente chunk, benchmark prima |
| Modello GGUF grande da distribuire | Download script separato (~2 GB 3B) |
| Conflitto RAM ASR + LLM | Unload obbligatorio tra fasi (già parzialmente presente) |

---

## 13. Prossimi step (checklist)

- [ ] **Fase 1:** Tabella token reali (tokenizer Qwen) sui 4 campioni + proiezione 30 min / 1 h / 2 h
- [ ] **Fase 1:** Tabella RAM stimata per profili `n_ctx` 8K / 16K / 32K
- [ ] **Fase 2:** Download GGUF Qwen2.5-3B-Instruct in ambiente test
- [ ] **Fase 2:** Script benchmark LLM (estensione `summary_benchmark.py` o nuovo script)
- [ ] **Fase 2:** Run benchmark + salvataggio in `docs/summary-benchmark/`
- [ ] **Fase 3:** Revisione utente output vs criteri §4.3
- [ ] **Fase 3:** Decisione modello default (3B vs 7B) e soglia RAM definitiva
- [ ] **Fase 4:** Implementazione (solo se go)
- [ ] Aggiornare `TRACCIAMENTO-BUG.md` con link a questo file e stato BUG-SUM-020

---

## 14. Riferimenti file

| Path | Contenuto |
|------|-----------|
| `bug-fix/TRACCIAMENTO-BUG.md` | BUG-SUM-019, BUG-SUM-020 |
| `bug-fix/FIX-RIASSUNTO-LLM.md` | Questo documento |
| `docs/summary-benchmark/README.md` | Istruzioni benchmark attuale |
| `docs/summary-benchmark/runs/20260628_130950/` | Run IT5/LexRank di riferimento |
| `scripts/summary_benchmark.py` | Script benchmark offline |
| `src/sbobinator/summarize.py` | Motore attuale (da sostituire) |
| `models/it5-small-news-summarization/` | Modello attuale (da deprecare) |

---

## 15. Note verbali utente (da preservare)

> «Se offriamo un servizio che è riassunto deve essere un riassunto fatto bene.»

> «5 righe su 600 parole che non spiegano niente — piuttosto rimuovo i riassunti.»

> «La soluzione migliore è LLM locale, a occhi chiusi.»

> «Ci mette poco a fare il testo, ci mette 15 minuti a fare il riassunto — va ragionato per hardware diversi.»

> «Solo CPU, non GPU per ora. Da 16 GB in su possiamo abilitare; sotto no.»

> «L’utente sceglie se farlo perché perde tanto tempo rispetto alla sbobinatura.»

> «Se mi mangia i token in input il riassunto funziona di merda lo stesso — va valutato in modo molto scientifico.»

> «Qwen secondo me fa faville su questo progetto.»

---

*Ultimo aggiornamento: 2026-06-28 — documento di pianificazione, implementazione non avviata.*
