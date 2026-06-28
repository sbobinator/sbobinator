# Variabili d'ambiente

## `SBOBINATOR_DATA`

Cartella radice dati (input + output).

| Valore | Effetto |
|--------|---------|
| Non impostata | `{project_root}/data` |
| `/data` (Docker) | `jobs` in `/data/output/jobs` |
| Path assoluto | Usato così com'è |
| Path relativo | Relativo a `project_root` |

Funzioni: `data_dir()`, `input_dir()`, `output_dir()`, `jobs_root()`.

---

## `NEMO_CACHE_DIR`

Cartella modelli (Parakeet `.nemo` e `it5-small-news-summarization/`).

| Valore | Effetto |
|--------|---------|
| Non impostata | `{project_root}/models` |
| `/models` (Docker) | Modelli nell'immagine |

Funzioni: `models_dir()`, `local_model_path()`, `summary_model_dir()`.

---

## `PYTHONUNBUFFERED`

Impostata nei Dockerfile (`1`) per log immediati.

---

## `SBOBINATOR_UI_HOST`

Host su cui uvicorn espone l'interfaccia web.

| Valore | Effetto |
|--------|---------|
| Non impostata | `127.0.0.1` (solo localhost — Windows/Linux locale) |
| `0.0.0.0` | Tutte le interfacce — **obbligatorio in Docker** per `ports: 8501:8501` |

---

## Esempio Docker Compose

```yaml
environment:
  - NEMO_CACHE_DIR=/models
  - SBOBINATOR_DATA=/data
  - SBOBINATOR_UI_HOST=0.0.0.0
volumes:
  - ../data:/data
```

---

## Esempio sviluppo locale

Nessuna variabile necessaria — default `data/` e `models/` nella root del repo.

---

## Verifica path attivi

```python
from sbobinator.config import data_dir, models_dir, jobs_root
print(data_dir(), models_dir(), jobs_root())
```

Oppure:

```cmd
sbobina info
```
