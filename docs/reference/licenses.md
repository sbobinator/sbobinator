# Licenze e componenti terzi

## Sbobinator (codice)

Licenza **MIT** — vedi file `LICENSE` nel repository (se presente) o header pyproject.

Puoi usare, modificare e distribuire il software con attribuzione.

---

## Modelli pre-addestrati

I modelli **non** sono inclusi nel repository git. Vengono scaricati separatamente.

### NVIDIA Parakeet TDT 0.6B v3

- **Origine:** [HuggingFace nvidia/parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- **Uso:** Trascrizione ASR
- **Licenza:** Consultare scheda HuggingFace NVIDIA (tipicamente licenza modello NVIDIA con restrizioni uso commerciale da verificare per il tuo caso)

### Google mT5-small

- **Origine:** [HuggingFace google/mt5-small](https://huggingface.co/google/mt5-small)
- **Uso:** Riassunto astrattivo
- **Licenza:** Apache 2.0 (verificare su HuggingFace)

---

## Dipendenze Python principali

| Pacchetto | Licenza tipica |
|-----------|----------------|
| PyTorch | BSD-style |
| nemo_toolkit | Apache 2.0 |
| streamlit | Apache 2.0 |
| transformers | Apache 2.0 |
| typer | MIT |

Per l'elenco completo: `pip-licenses` o `pyproject.toml` / lockfile dopo install.

---

## ffmpeg

Binario esterno **non** distribuito con Sbobinator.

- Licenza: LGPL/GPL a seconda della build
- L'utente deve installare ffmpeg conforme alla propria piattaforma

---

## Note legali

- **Contenuto audio:** sei responsabile dei diritti sui file che elabori.
- **Modelli AI:** rispetta le condizioni d'uso di NVIDIA, Google/HuggingFace e eventuali limiti commerciali.
- **Output:** la trascrizione automatica può contenere errori; non sostituisce revisione umana per uso legale o medico.
