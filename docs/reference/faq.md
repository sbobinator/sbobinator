# FAQ

## Generale

### Sbobinator invia i miei audio su internet?

No. Dopo il download iniziale dei modelli, l'elaborazione è **100% locale**. Nessun upload a cloud durante trascrizione o riassunto.

### Quali lingue supporta?

Parakeet TDT 0.6B v3 è ottimizzato per l'**italiano**. Funziona anche su altre lingue con qualità variabile.

### Posso usare solo la CLI senza interfaccia web?

Sì. `sbobina transcribe file.wav` oppure `sbobina worker` per coda headless.

---

## Modelli

### Quanto spazio occupano i modelli?

| Modello | Dimensione circa |
|---------|------------------|
| Parakeet ASR | ~2.5 GB |
| mT5-small | ~1.1 GB |

### Devo riscaricare i modelli ad ogni aggiornamento?

No, se restano in `models/`. Aggiorna solo se cambia versione modello nelle release notes.

### Docker scarica i modelli a ogni avvio?

No. Sono **nell'immagine** al build. Solo `data/` è montato dal host.

---

## Coda e job

### Perché elabora un file alla volta?

Il worker processa la coda **FIFO** per limitare RAM (NeMo + mT5 sono pesanti).

### Posso elaborare lo stesso file due volte?

Sì, se il job precedente è `completed`. Viene creata una **nuova cartella** con nuovo timestamp.

### Cosa succede se chiudo il browser?

Il worker continua in background. Riapri `http://localhost:8501` per vedere lo stato.

### Cancello una cartella job a mano — cosa succede?

Il record resta in `queue.db`. L'UI mostra il job ma i file mancano. Usa `clean_output.py` per reset completo.

---

## Interfaccia

### Perché vedo un solo job nel pannello principale?

La sidebar seleziona un job alla volta. La **coda** in alto elenca tutti. Miglioramento multi-risultati è in roadmap (`evolutive/`).

### Il worker parte da solo?

Sì. Ogni avvio UI chiama `start_background_worker()` che lancia un subprocess se non già attivo.

---

## Riassunto

### Differenza estrattivo vs astrattivo?

| Modalità | Velocità | Qualità | Requisiti |
|----------|----------|---------|-----------|
| Estrattivo | Istantaneo | Frasi originali selezionate | Nessun modello extra |
| Astrattivo (mT5) | Lento | Testo riformulato | `models/mt5-small/` completo |

### La trascrizione è ok ma il riassunto fallisce

Normale se mT5 mancante o errore SSL. Il testo è in `trascrizione.txt`. Vedi [SSL Windows](../troubleshooting/ssl-windows.md).

---

## Performance

### Quanto è veloce su CPU?

Dipende da hardware. Su i5 mobile ~**2× realtime** (1 min audio ≈ 2 min elaborazione). GPU NVIDIA riduce molto i tempi ASR.

### Perché il primo job è più lento?

Caricamento modello NeMo in RAM alla prima trascrizione.

---

## Sviluppo e deploy

### Perché niente script PowerShell?

Scelta progetto: compatibilità antivirus e approccio multipiattaforma con Python + `cmd`.

### Come pubblico la documentazione?

Push su `main` → GitHub Actions builda MkDocs e pubblica su `gh-pages`.
