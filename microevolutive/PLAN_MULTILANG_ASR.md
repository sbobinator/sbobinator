# Piano microevolutivo — Trascrizione multilingua (NeMo)

> **Data**: 2026-06-26 · **Stato**: 📋 pianificato  
> **Obiettivo**: scegliere la **lingua parlata** per ogni job e migliorare la qualità
> ASR su audio non italiano, **senza** moltiplicare i download da 2.5 GB se non serve.  
> **Correlato:** `PLAN_MULTILANG_SUMMARY.md` (lingua del riassunto — indipendente).

---

## 0. Cosa esiste già

| Pezzo | Stato |
|-------|--------|
| Modello unico `nvidia/parakeet-tdt-0.6b-v3` | ✅ ~2.5 GB, multilingue EU (25 lingue) |
| `scripts/download_model.py` | ✅ Un solo `.nemo` |
| `TranscribeConfig` in `config.py` | Solo `model_name`, device, chunking |
| `transcribe.py` | Nessun `language_id` passato a NeMo |
| `JobRecord.model_name` | ✅ Persistito; **manca** `asr_language` |
| UI / messaggi | Copy "italiano" ovunque — da generalizzare |

**Considerazione chiave:** Parakeet v3 **non è un modello solo-italiano**.
Il 90% del lavoro è **esporre la lingua** a NeMo e all’utente, non scaricare
N modelli diversi. Modelli aggiuntivi vanno valutati **solo** se i test mostrano
qualità insufficiente su una lingua target (fase 3 opzionale).

---

## 1. Lingue supportate (v1)

Allineamento al modello NVIDIA Parakeet TDT 0.6B v3 (EU):

| Codice | Lingua | Priorità prodotto |
|--------|--------|-------------------|
| `it` | Italiano | **Default** — mercato primario |
| `en` | Inglese | Alta |
| `de` | Tedesco | Media |
| `fr` | Francese | Media |
| `es` | Spagnolo | Media |
| `pt` | Portoghese | Bassa |
| `nl`, `pl`, … | Altre EU | Lista completa in settings avanzate |

**UI v1:** IT, EN, DE, FR, ES in select; resto in "Altre (EU)" o file config.

---

## 2. Architettura

```
Upload UI / CLI
      │
      ▼
 JobRecord.asr_language  ──►  pipeline.py
      │                            │
      ▼                            ▼
 TranscribeConfig.language   transcribe.py
      │                            │
      ▼                            ▼
 NeMo ASRModel.transcribe(..., language_id=?)   ← da verificare su API NeMo 2.x
```

### 2.1 Un modello, più lingue (default)

```
models/
  parakeet-tdt-0.6b-v3.nemo    ← unico file
```

`download_model.py` invariato per la fase 1.

### 2.2 Più modelli (solo se necessario — fase 3)

Registro opzionale in `config.py`:

```python
ASR_MODELS = {
    "parakeet-v3": "nvidia/parakeet-tdt-0.6b-v3",
    # "canary-1b": "nvidia/canary-1b-v2",  # esempio futuro
}
```

UI: "Modello ASR" avanzato + `scripts/download_model.py --model …`.

**Non implementare subito** — evita gestione disco e RAM doppia senza benchmark.

---

## 3. Modifiche codice (fase 1)

### 3.1 Config

```python
@dataclass(frozen=True)
class TranscribeConfig:
    model_name: str = DEFAULT_MODEL
    language: str = "it"   # BCP-47 semplificato: it, en, de, ...
    ...
```

### 3.2 `transcribe.py`

1. Accettare `language` in `transcribe_file()` / path chunk.
2. Passare hint a NeMo (da documentare dopo spike):
   - `model.transcribe(paths, language_id='it')` **oppure**
   - decoder config / `prompt` multilingue se richiesto dalla versione NeMo installata.
3. **Spike obbligatorio (0.5 giorni):** script `scripts/spike_nemo_language.py` con
   WAV campione IT + EN → confronto con/senza language_id.

### 3.3 `jobs.py`

- Colonna `asr_language TEXT DEFAULT 'it'`
- `register_job(..., asr_language=...)`
- Reprocess: opzione "Ritrascrivere con altra lingua" (nuovo job o stesso job fase transcribe)

### 3.4 UI

| Dove | Modifica |
|------|----------|
| `index.html` | Select "Lingua audio" (default da settings utente) |
| `jobs.html` | Colonna/filtro lingua |
| `job_detail_page.html` | Badge lingua ASR |
| Settings (nuova o in license/summary) | Lingua ASR predefinita |

### 3.5 CLI

```powershell
sbobina transcribe video.mp4 --language en
```

### 3.6 Docs + sito

- MkDocs: pagina "Lingue supportate ASR"
- Homepage: "Italian first, EU languages supported" (non solo IT)

---

## 4. Fasi

### Fase 0 — Spike NeMo language API — **prima di tutto**

| Output | Criterio |
|--------|----------|
| `scripts/spike_nemo_language.py` | Log WER qualitativo o diff testo IT vs EN su stesso modello |
| Nota in questo file § "Esito spike" | Go/no-go su language_id |

**Se NeMo non espone language_id su questa build:** alternative documentate (prompt iniziale, modello alternativo, o accettare auto-detect del modello).

### Fase 1 — Lingua per job (IT + EN) — **settimana 1–2**

| # | Task | DoD |
|---|------|-----|
| 1.1 | Spike completato | Decisione tecnica scritta |
| 1.2 | `asr_language` su job + pipeline | Job EN trascritto con hint EN |
| 1.3 | UI + CLI | Select funzionante |
| 1.4 | Test campione EN (podcast breve) | `transcript.txt` leggibile |
| 1.5 | Docs | Pagina lingue |

### Fase 2 — Estensione DE, FR, ES + copy UI — **settimana 2**

- Select completa
- Messaggi errore localizzati (UI resta IT per utenti italiani; docs bilingue)

### Fase 3 — Modelli ASR aggiuntivi (opzionale) — **solo con dati**

Trigger per aprire fase 3:

- WER/qualità percepita insufficiente su lingua commerciale target
- Richiesta cliente pagante

Deliverable: registry modelli, download selettivo, job `model_name` + `asr_language`.

---

## 5. Cosa NON fare (v1)

| Non fare | Perché |
|----------|--------|
| Scaricare un `.nemo` per ogni lingua | Parakeet v3 è già multilingue |
| Traduzione automatica del trascritto | Out of scope — vedi summary multilingua |
| Training / fine-tuning | Escluso in `evolutive/ROADMAP` |
| Rilevamento lingua automatico obbligatorio | Utile in v2; v1 = scelta esplicita (meno sorprese) |

---

## 6. Rischi

| Rischio | Mitigazione |
|---------|-------------|
| API NeMo diversa tra versioni | Pin versione in `requirements/` + spike |
| Utente sceglie lingua sbagliata | Hint in UI + riprocessa job |
| RAM con modello unico già al limite | Invariato — un solo modello in memoria |
| Docker mini PC | Nessun cambio immagine se un solo `.nemo` |

---

## 7. Stima effort

| Fase | Effort |
|------|--------|
| Fase 0 spike | **XS** (mezza giornata) |
| Fase 1 | **M** (3–5 giorni) |
| Fase 2 | **S** (1–2 giorni) |
| Fase 3 modelli extra | **L** (solo se serve) |

---

## 8. Ordine rispetto ad altri piani

```
PLAN_MULTILANG_SUMMARY (fase 1)   ← può partire in parallelo
        ‖
PLAN_MULTILANG_ASR (fase 0 spike) ← iniziare subito lo spike
        ↓
PLAN_MULTILANG_ASR (fase 1)
```

Dopo entrambi: prodotto "multilingua" coerente (audio EN → transcript EN → summary EN o IT).

---

## 9. Esito spike NeMo

> **Da compilare dopo `scripts/spike_nemo_language.py`**

| Domanda | Risposta |
|---------|----------|
| Parametro language in `transcribe()`? | _TBD_ |
| Versione NeMo testata | _TBD_ |
| Go per fase 1 | _TBD_ |
