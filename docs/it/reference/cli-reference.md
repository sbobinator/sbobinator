# Riferimento CLI

Comando: **`sbobina`**

## `sbobina` / `sbobina ui`

```
sbobina [OPTIONS]
sbobina ui [--port INTEGER]
```

| Opzione | Default | Descrizione |
|---------|---------|-------------|
| `--port`, `-p` | 8501 | Porta uvicorn |

---

## `sbobina worker`

```
sbobina worker [--interval FLOAT]
```

| Opzione | Default | Descrizione |
|---------|---------|-------------|
| `--interval` | 1.0 | Secondi tra poll coda |

---

## `sbobina transcribe`

```
sbobina transcribe INPUT [OPTIONS]
```

| Opzione | Abbrev | Default | Descrizione |
|---------|--------|---------|-------------|
| `--output` | `-o` | `data/output` | Output (solo legacy) |
| `--model` | `-m` | Parakeet | Modello NeMo |
| `--device` | `-d` | auto | cpu / cuda |
| `--format` | `-f` | txt,srt | Formati (legacy) |
| `--summarize` | `-s` | false | Riassunto |
| `--summary-provider` | | deepseek | local, openai, gemini, claude, deepseek, kimi |
| `--summary-length` | | auto | Lunghezza riassunto |
| `--legacy-output` | | false | Output flat senza job |
| `--verbose` | `-v` | false | Log debug |

---

## `sbobina jobs list`

```
sbobina jobs list [--status TEXT] [--limit INTEGER]
```

| Opzione | Abbrev | Default |
|---------|--------|---------|
| `--status` | | tutti |
| `--limit` | `-n` | 20 |

---

## `sbobina jobs show`

```
sbobina jobs show JOB_ID
```

---

## `sbobina jobs retry`

```
sbobina jobs retry [JOB_ID]
```

Senza `JOB_ID`: ritenta tutti i falliti/annullati.

---

## `sbobina info`

Informazioni versione e sistema.

---

## Codici uscita

| Codice | Significato |
|--------|-------------|
| 0 | Successo |
| 1 | Errore (transcribe fallito, job non trovato, ecc.) |
