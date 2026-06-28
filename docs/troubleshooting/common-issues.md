# Problemi comuni

## UI e avvio

### ImportError `data_dir` / moduli da `sbobinator.config`

**Causa:** Istanza Streamlit **vecchia** ancora in esecuzione con moduli Python in cache (tipico dopo `git pull` o aggiornamento codice senza riavvio).

**Soluzione:**

```cmd
python scripts\restart_ui.py
```

Non basta F5 nel browser. `restart_ui.py` termina tutti i processi su porta 8501 e pulisce `__pycache__`.

Verifica in sidebar: deve comparire `Sbobinator v0.3.0` e il path Python corretto.

---

### ImportError / moduli mancanti (generico)

```
ImportError: cannot import name '...' from 'sbobinator.jobs'
```

**Causa:** Istanze Streamlit vecchie o `pip install` non allineato.

**Soluzione:**

```cmd
python scripts\restart_ui.py
pip install -e ".[local]"
```

Ctrl+F5 **non** basta — serve riavvio processo Python.

---

### Più istanze su porta 8501

**Sintomi:** Comportamento incoerente, job che falliscono a caso.

**Soluzione:**

```cmd
python scripts\restart_ui.py
```

Verifica una sola riga LISTENING:

```cmd
netstat -ano | findstr :8501
```

---

### Bottone "Accoda" disabilitato

**Causa:** File uploader dentro `st.form` (risolto in v0.3+) o nessun file selezionato.

**Soluzione:** Ricarica file, F5, riprova.

---

## Trascrizione

### `Dipendenze ASR mancanti`

```cmd
pip install -e ".[local]"
python scripts\download_model.py
```

---

### `lightning.fabric` / circular import

**Causa:** NeMo caricato in thread Streamlit (vecchio bug).

**Soluzione:** Aggiorna a v0.3+ con worker subprocess. `restart_ui.py`.

---

### `ffmpeg non trovato`

Installa ffmpeg, riapri terminale, verifica `ffmpeg -version`.

---

## Riassunto

### "Riassunto richiesto ma non generato"

**Causa:** mT5 non scaricato o errore durante summarize.

**Soluzione:**

```cmd
python scripts\download_summary_model.py
```

Usa **estrativo** se non serve mT5.

La trascrizione è comunque in `trascrizione.txt`.

---

### Opzione mT5 non visibile in sidebar

Normale se `models/mt5-small/` incompleto. Completa il download.

---

## Coda

### Job bloccati in `running`

```cmd
sbobina jobs retry
python scripts\restart_ui.py
```

---

### Job falliti tutti insieme

Controlla `sbobina jobs show ID` per errore. Spesso modello mancante o worker multipli.

---

## Storico

### Vedo job in UI ma file mancanti

Hai cancellato cartelle ma non `queue.db`. Usa `clean_output.py` o ignora quei job.

### Ricarico stesso file

Se job **completato** → nuovo job, nuova cartella. Se **in coda** → saltato.

---

## Performance

CPU lenta su file lunghi è normale. Usa GPU o attendi. Vedi [Benchmark](../operations/benchmark.md).

Per SSL Windows vedi [pagina dedicata](ssl-windows.md).
