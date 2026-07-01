# CLI reference

Command: **`sbobina`**

## `sbobina` / `sbobina ui`

```
sbobina [OPTIONS]
sbobina ui [--port INTEGER]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--port`, `-p` | 8501 | uvicorn port |

---

## `sbobina worker`

```
sbobina worker [--interval FLOAT]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--interval` | 1.0 | Seconds between queue polls |

---

## `sbobina transcribe`

```
sbobina transcribe INPUT [OPTIONS]
```

| Option | Abbrev | Default | Description |
|--------|--------|---------|-------------|
| `--output` | `-o` | `data/output` | Output (legacy only) |
| `--model` | `-m` | Parakeet | NeMo model |
| `--device` | `-d` | auto | cpu / cuda |
| `--format` | `-f` | txt,srt | Formats (legacy) |
| `--summarize` | `-s` | false | Summary |
| `--summary-provider` | | deepseek | local, openai, gemini, claude, deepseek, kimi |
| `--summary-length` | | auto | Summary length |
| `--legacy-output` | | false | Flat output without job |
| `--verbose` | `-v` | false | Debug log |

---

## `sbobina jobs list`

```
sbobina jobs list [--status TEXT] [--limit INTEGER]
```

| Option | Abbrev | Default |
|--------|--------|---------|
| `--status` | | all |
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

Without `JOB_ID`: retries all failed/cancelled jobs.

---

## `sbobina info`

Version and system information.

---

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (transcribe failed, job not found, etc.) |
