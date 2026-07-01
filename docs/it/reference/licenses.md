# Licenze e componenti terzi

## Sbobinator (codice applicativo)

**Licenza proprietaria** — Copyright © 2024-2026 [Antonio Trento](https://antoniotrento.net).

Vedi file [`LICENSE`](../../LICENSE) nella root del repository.

| Tipo di uso | Condizioni |
|-------------|------------|
| Personale, studio, no-profit documentabile | Gratuito |
| Aziende, PA, professionisti, uso commerciale o interno organizzativo | **Licenza commerciale a pagamento** |

Non è consentita la ridistribuzione del Software senza autorizzazione scritta.

Per licenze commerciali: https://antoniotrento.net

Vedi **[Licenza commerciale](commercial-license.md)** (chi deve pagare, come acquistare, roadmap desktop).

!!! note "Versioni precedenti MIT"
    Eventuali release già distribuite sotto licenza MIT restano utilizzabili secondo i termini MIT validi al momento della distribuzione. Le versioni attuali e future seguono la licenza proprietaria in `LICENSE`.

---

## Modelli pre-addestrati

I modelli **non** sono inclusi nel repository git. Vengono scaricati separatamente.

### NVIDIA Parakeet TDT 0.6B v3

- **Origine:** [HuggingFace nvidia/parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- **Uso:** Trascrizione ASR
- **Licenza:** Consultare scheda HuggingFace NVIDIA (restrizioni uso commerciale da verificare per il tuo caso)

### Qwen2.5-3B-Instruct (GGUF, opzionale)

- **Origine:** HuggingFace / llama.cpp
- **Uso:** Riassunto locale
- **Licenza:** Verificare scheda modello Qwen su HuggingFace

### Deprecato: Google mT5-small

Non più usato come motore di riassunto prodotto. Eventuali file residui sono legacy.

---

## Dipendenze Python principali

| Pacchetto | Licenza tipica |
|-----------|----------------|
| PyTorch | BSD-style |
| nemo_toolkit | Apache 2.0 |
| FastAPI | MIT |
| uvicorn | BSD |
| typer | MIT |
| llama-cpp-python | MIT |

Per l'elenco completo: `pip-licenses` dopo install.

L'uso di queste librerie è soggetto alle rispettive licenze open source; la licenza di Sbobinator non estende diritti sui pacchetti di terzi.

---

## ffmpeg

Binario esterno **non** distribuito con Sbobinator.

- Licenza: LGPL/GPL a seconda della build
- L'utente deve installare ffmpeg conforme alla propria piattaforma

---

## Note legali

- **Contenuto audio:** sei responsabile dei diritti sui file che elabori.
- **Modelli AI:** rispetta le condizioni d'uso di NVIDIA, HuggingFace e eventuali limiti commerciali **oltre** alla licenza Sbobinator.
- **Output:** la trascrizione automatica può contenere errori; non sostituisce revisione umana per uso legale o medico.
- **Non è consulenza legale:** per conformità aziendale consulta un legale qualificato.
