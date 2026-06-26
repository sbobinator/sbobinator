# Evolutive — Sbobinator

Pianificazione delle **evoluzioni prodotto** oltre lo stato attuale (v0.2).

Lo strumento oggi funziona per il caso base — un file, una trascrizione, storico su disco — ma resta un **prototipo operativo**, non un flusso di lavoro completo per chi sbobina spesso o in volume.

## Documenti

| File | Contenuto |
|------|-----------|
| [ROADMAP-EVOLUTIVE.md](./ROADMAP-EVOLUTIVE.md) | Documento principale: visione, lacune, pilastri, fasi, priorità |
| [ARCHITETTURA-FUTURA.md](./ARCHITETTURA-FUTURA.md) | Ragionamento tecnico: coda job, worker, API, deploy multi-macchina |
| [CASI-D-USO.md](./CASI-D-USO.md) | Scenari utente reali e cosa manca per supportarli |

## Relazione con altre cartelle

- **bug-fix/** — correzioni e debito tecnico (cosa è rotto oggi)
- **evolutive/** — cosa serve domani (funzionalità, architettura, prodotto)

## Prossimo passo consigliato

Leggere [ROADMAP-EVOLUTIVE.md](./ROADMAP-EVOLUTIVE.md) sezione **Fase 1** e decidere se partire da:

1. **Coda job vera** (accodare senza bloccare la UI)
2. **Batch + cartella input** (più file in un colpo)
3. **Allineamento CLI ↔ registro lavori**

Tutti e tre sono collegati; la Fase 1 nel documento principale propone un ordine.
