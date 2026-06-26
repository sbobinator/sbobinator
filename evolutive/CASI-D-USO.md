# Casi d'uso — cosa serve e cosa manca

Analisi degli scenari reali per capire **perché** le evolutive non sono optional.

---

## CU-01 — Podcast settimanale (utente singolo, PC Windows)

**Chi:** Creatore contenuti, 1 episodio/settimana, 45–90 minuti.

**Oggi:**
1. Apre UI, carica MP3
2. Attende 1–2 min caricamento modello + N minuti trascrizione
3. Scarica TXT, riassunto, SRT

**Dolori attuali:**
| Problema | Gravità |
|----------|---------|
| UI bloccata per tutta la durata | Alta |
| Nessun avviso a fine lavoro se chiude il tab | Media |
| File lungo: progress generico, non % reale | Media |
| Non può fare altro nel frattempo (secondo file) | Alta |

**Serve:**
- Coda job in background
- Notifica desktop / email opzionale a completamento
- Progress per chunk su file lunghi
- Storico con ricerca per nome file

---

## CU-02 — Riunioni aziendali (batch, mini PC sempre acceso)

**Chi:** Ufficio, registrazioni Teams/Zoom salvate in cartella condivisa.

**Oggi:**
- Deve caricare un file alla volta via browser
- Nessuna integrazione con cartella di rete
- Mini PC AMD pensato come server Docker ma UI non ottimizzata per headless

**Dolori attuali:**
| Problema | Gravità |
|----------|---------|
| Un file per volta | Critica |
| Nessun watch folder | Critica |
| Nessuna API per automazione | Alta |
| Docker non allineato all'ultima UI/jobs | Media |

**Serve:**
- Watch folder: `data/input/inbox/` → sbobina → `data/output/jobs/`
- Batch: seleziona N file o intera cartella
- API REST minima (`POST /jobs`, `GET /jobs/{id}`)
- Deploy stabile su mini PC 32 GB RAM CPU-only

---

## CU-03 — Studente / ricerca (editing e export)

**Chi:** Interviste, tesi, citazioni da correggere.

**Oggi:**
- Testo in textarea read-only
- Export TXT e SRT
- Nessun editor, nessun timestamp cliccabile

**Dolori attuali:**
| Problema | Gravità |
|----------|---------|
| Non può correggere errori ASR in app | Alta |
| SRT senza player video sincronizzato | Media |
| Nessun export DOCX/PDF con formattazione | Media |
| Nessuna ricerca nel testo tra più lavori | Bassa |

**Serve:**
- Editor trascrizione con salvataggio versioni
- Player audio/video + highlight frase corrente
- Export DOCX, PDF, VTT
- Tag / note per lavoro ("intervista Prof. Rossi")

---

## CU-04 — Operatore multitasking (coda + storico)

**Chi:** Chi sbobina 5–10 file al giorno, non sempre scarica subito.

**Oggi (dopo fix storico):**
- Ogni lavoro salvato in cartella univoca ✅
- Storico in sidebar ✅
- Ma: avviare lavoro 2 mentre 1 gira **non è possibile** in UI

**Dolori attuali:**
| Problema | Gravità |
|----------|---------|
| Nessuna coda: un job alla volta | Critica |
| Upload perso dopo `st.rerun()` | Bassa (storico compensa) |
| Nessun ZIP export lavoro | Media |
| Nessun "elimina lavoro" | Bassa |

**Serve:**
- Coda FIFO con stati: `in_coda` → `in_elaborazione` → `completato` / `errore`
- Pannello coda visibile (posizione, ETA stimata)
- Download ZIP (txt + srt + riassunto + job.json)
- Elimina / rinomina lavoro

---

## CU-05 — Ambiente offline / SSL rotto (Windows)

**Chi:** Utente con antivirus/proxy che blocca HuggingFace.

**Oggi:**
- Parakeet: script `download-model.ps1` + caricamento locale ✅
- mT5 riassunto "Qualità": spesso fallisce ❌
- Primo avvio confuso ("pronto" vs "modello scaricato")

**Serve:**
- Wizard primo avvio: verifica ffmpeg, modello ASR, modello riassunto
- Bundle offline completo (ASR + estrattivo sempre; mT5 opzionale con script dedicato)
- Modalità "solo estrattivo" come default su Windows

---

## CU-06 — Hardware misto (laptop 16 GB + mini PC 32 GB + GPU opzionale)

**Chi:** Sviluppo su laptop, produzione su server domestico.

**Oggi:**
- Device `auto/cpu/cuda` in sidebar
- Nessun concetto di "nodo" o delega remota
- Modello in RAM globale nel processo Streamlit

**Serve:**
- Profili hardware: `leggero` (CPU, chunk piccoli) vs `server` (più RAM, batch)
- Opzione futura: client UI leggero → worker su mini PC
- Documentazione chiara RAM/VRAM per durata file

---

## Matrice priorità casi d'uso

| Caso | Frequenza stimata | Impatto business | Priorità evolutiva |
|------|-------------------|------------------|-------------------|
| CU-04 Coda multitasking | Alta | Alto | **P0** |
| CU-02 Batch / watch folder | Media | Alto | **P0** |
| CU-01 File lunghi + progress | Alta | Medio | **P1** |
| CU-05 Offline completo | Alta (Windows) | Medio | **P1** |
| CU-03 Editor + export | Media | Medio | **P2** |
| CU-06 Deploy multi-macchina | Bassa (fase 2) | Alto | **P2** |

---

## Criterio "è abbastanza?"

Sbobinator è **utilizzabile** per demo e file singoli brevi.  
Non è **affidabile come strumento di lavoro** finché mancano:

1. **Coda** — non perdere intento né bloccare l'utente
2. **Batch** — più file senza ripetere upload manuale
3. **Feedback** — sapere dove siamo su file lunghi e a fine job
4. **Un solo backend** — UI e CLI sullo stesso registro `jobs/`

Questi quattro punti definiscono la **Fase 1** della roadmap.
