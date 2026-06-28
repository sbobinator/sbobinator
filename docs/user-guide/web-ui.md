# Interfaccia web

L'interfaccia è costruita con **Streamlit** (`src/sbobinator/ui/app.py`), porta predefinita **8501**.

## Avvio

```cmd
sbobina ui
sbobina ui --port 9000
start.bat
python scripts\restart_ui.py
```

## Layout pagina

### Header e statistiche

| Card | Significato |
|------|-------------|
| Device | CPU o CUDA in uso |
| Lingua | IT (fisso) |
| Lavori salvati | Conteggio da `queue.db` |
| In coda | Job attivi (queued + running) |

### Pannello coda

Mostra job in elaborazione o in attesa, con:

- barra di progresso
- messaggio fase (`Caricamento modello NeMo...`, ecc.)
- pulsante **Annulla** (solo job in coda)

Aggiornamento automatico ogni 2 secondi mentre ci sono job attivi.

### Upload file

- Supporta **più file** contemporaneamente
- Formati: MP4, MKV, AVI, MOV, WEBM, WAV, MP3, FLAC, M4A, OGG
- L'uploader è **fuori** dal form Streamlit (altrimenti il bottone resta disabilitato)
- Dopo l'accodamento, file con lo stesso nome già **in coda** vengono saltati

### Risultati

La pagina principale mostra il dettaglio del **job selezionato** (sidebar → "Seleziona lavoro"):

- Tab **Trascrizione** — testo completo
- Tab **Riassunto** — se generato o messaggio errore
- Tab **Download** — percorsi e pulsanti
- Box **File salvati su disco** — path assoluti + "Apri cartella"

!!! note "Un job alla volta in pagina"
    Per vedere altri risultati usa il menu **Seleziona lavoro** nella sidebar. Tutti i file sono comunque su disco in `data/output/jobs/`.

## Sidebar

### Impostazioni

| Opzione | Descrizione |
|---------|-------------|
| Dispositivo | auto / cpu / cuda |
| Modello ASR | ID HuggingFace (default Parakeet) |
| Genera riassunto | on/off |
| Modalità | Estrattivo o mT5 (se modello presente) |
| Lunghezza riassunto | auto, breve, normale, dettagliato |

### I tuoi lavori

Elenco da SQLite — non dalla scansione cartelle. Vedi [Coda e storico](jobs-queue.md).

## Worker in background

All'avvio UI, `start_background_worker()` lancia un **processo separato**:

```text
python -m sbobinator.cli worker
```

NeMo **non** gira nel thread Streamlit (evita crash `lightning.fabric`).

PID salvato in `data/output/jobs/worker.pid`.

## Suggerimenti

- Un solo `restart_ui.py` alla volta — evita più Streamlit sulla porta 8501
- Dopo `clean_output.py`, ricarica la pagina (F5)
- Primo job dopo avvio: 1–2 min per caricare Parakeet in RAM
