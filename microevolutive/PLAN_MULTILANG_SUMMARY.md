# Piano microevolutivo — Riassunto LLM multilingua

> **Data**: 2026-06-26 · **Stato**: 📋 pianificato  
> **Obiettivo**: l’utente sceglie la **lingua di output** del riassunto (indipendente
> dalla lingua parlata nell’audio). Stesso comportamento per provider cloud e Qwen locale.  
> **Non obiettivo**: traduzione professionale del trascritto integrale (solo riassunto).

---

## 0. Cosa esiste già (da riusare)

| Pezzo | File | Note |
|-------|------|------|
| Prompt riassunto | `src/sbobinator/summarize_providers/prompt.py` | Solo italiano, regole anti-meta-frasi |
| Registry provider | `summarize_providers/registry.py` | DeepSeek, OpenAI, Claude, Gemini, Kimi, Qwen |
| Settings UI | `ui/templates/settings_summary.html` | API key, test motori |
| Job fields | `jobs.py` → `summary_provider`, `summary_length`, … | Manca `summary_language` |
| Benchmark qualità | `docs/summary-benchmark/` | Campioni IT — estendere con EN/DE smoke |

**Considerazione:** questo è il punto **più veloce** del pacchetto multilingua.
Non tocca NeMo né i ~2.5 GB del modello ASR. Si può rilasciare da solo.

---

## 1. Modello concettuale

Due lingue distinte (non confonderle in UI):

| Concetto | Esempio | Dove si configura |
|----------|---------|-------------------|
| **Lingua audio / ASR** | Parlato in italiano | Vedi `PLAN_MULTILANG_ASR.md` |
| **Lingua riassunto** | Summary in inglese per capitolato EU | Questo piano |

Casi d’uso tipici:

1. Audio IT → riassunto IT (default attuale)
2. Audio IT → riassunto EN (report per cliente estero)
3. Audio EN → riassunto IT (intervista internazionale, note in italiano)
4. Audio DE/FR/… → riassunto nella stessa lingua o in IT

---

## 2. Decisioni da NON cambiare

1. **Estrattivo** resta senza LLM — nessuna “lingua” da passare (solo statistiche sul testo).
2. **Un prompt template** parametrizzato — no copia-incolla di 10 file per lingua.
3. **Fallback**: se lingua non supportata dal provider, errore chiaro in UI (non summary silenzioso in italiano).
4. **Locale first**: Qwen locale deve funzionare offline anche per EN/DE (i modelli instruct sono multilingue).

---

## 3. Design tecnico

### 3.1 Enum e persistenza

```python
# config.py (bozza)
class SummaryLanguage(str, Enum):
    it = "it"
    en = "en"
    de = "de"
    fr = "fr"
    es = "es"
    auto = "auto"  # inferisce dal trascritto (fase 2, opzionale)
```

- `JobRecord.summary_language: str = "it"`
- Migrazione SQLite in `jobs.py` (`ALTER TABLE` o rebuild come già fatto per altre colonne)
- Default globale in settings: `data/.secrets/summary_config.json` o estensione `summary_config.py`

### 3.2 Prompt

`prompt.py` → funzioni con parametro `language: SummaryLanguage`:

```python
def system_prompt(language: SummaryLanguage) -> str: ...
def user_prompt(transcript: str, length: SummaryLength, language: SummaryLanguage) -> str: ...
```

Regole per lingua (template):

| Lingua | Istruzione chiave nel system prompt |
|--------|-------------------------------------|
| `it` | Testo attuale (invariato) |
| `en` | "Write in clear English. Start directly with content…" |
| `de` | "Schreibe auf Deutsch…" |
| `fr` | "Rédige en français…" |
| `es` | "Escribe en español…" |

Mantenere le stesse **regole di qualità** (no meta-frasi, no invenzioni, prudenza su errori ASR).

### 3.3 Provider

Ogni provider in `summarize_providers/*.py` riceve `language` e chiama `system_prompt(language)`.

Nessun cambio alle API esterne: la lingua è solo nel prompt.

### 3.4 UI

| Schermata | Modifica |
|-----------|----------|
| Home upload | Select "Lingua riassunto" (visibile solo se riassunto attivo) |
| `/settings/summary` | Default lingua riassunto |
| `/jobs/{id}` | Mostra lingua usata; riprocessa con altra lingua |

Label UI in italiano per utenti IT; valori interni `it`/`en`/…

---

## 4. Fasi

### Fase 1 — IT + EN (MVP) — **settimana 1**

| # | Task | DoD |
|---|------|-----|
| 1.1 | `SummaryLanguage` + colonna job | Job salvato con lingua |
| 1.2 | `prompt.py` parametrizzato IT/EN | Test manuale su campione benchmark |
| 1.3 | Wire tutti i provider abstractive | Summary EN su job di test |
| 1.4 | UI select IT/EN | Upload + settings |
| 1.5 | Docs EN/IT una pagina | MkDocs aggiornato |

**Definition of Done:** job con audio IT → riassunto EN scaricabile; Qwen locale produce EN senza API key.

### Fase 2 — DE, FR, ES — **settimana 2**

| # | Task |
|---|------|
| 2.1 | Estendere enum + prompt |
| 2.2 | Smoke test per lingua (1 campione ciascuna) |
| 2.3 | Benchmark opzionale in `docs/summary-benchmark/` |

### Fase 3 — `auto` (opzionale) — **backlog**

- Heuristica leggera: primi N caratteri del trascritto → lingua dominante (langdetect o fastText)
- Solo se richiesto dagli utenti; rischio errori su audio misto

---

## 5. Test e qualità

| Test | Come |
|------|------|
| Regressione IT | Campioni esistenti `campione-italiano-*` — score invariato |
| EN smoke | Trascritto IT lungo → summary EN, controllo manuale: no italiano nel body |
| Provider matrix | Almeno DeepSeek + un provider OpenAI-compat + Qwen locale |
| Job reprocess | Cambio lingua → nuovo `summary.md` senza ritrascrivere |

Documentare in `bug-fix/` solo se emergono regressioni (es. meta-frasi in EN).

---

## 6. Rischi

| Rischio | Mitigazione |
|---------|-------------|
| Provider ignora lingua | System prompt esplicito + verifica smoke |
| Qwen locale più lento su prompt lunghi EN | Stesso chunking già usato per trascritti lunghi |
| Utente confonde lingua ASR e summary | UI: due label distinte "Lingua audio" / "Lingua riassunto" |

---

## 7. Stima effort

| Fase | Effort |
|------|--------|
| Fase 1 (IT+EN) | **S** (2–4 giorni) |
| Fase 2 (+3 lingue) | **S** (1–2 giorni) |
| Fase 3 (auto) | **M** |

---

## 8. Riferimenti codice

```
src/sbobinator/summarize_providers/prompt.py   ← cuore modifica
src/sbobinator/summarize_providers/*.py      ← pass language
src/sbobinator/jobs.py                       ← summary_language
src/sbobinator/ui/templates/index.html
src/sbobinator/ui/templates/settings_summary.html
src/sbobinator/summary_config.py
```
