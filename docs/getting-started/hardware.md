# Risorse hardware

Le risorse dipendono da **cosa usi**: solo trascrizione, riassunto via API cloud, o riassunto locale offline (Qwen).

## Prerequisiti comuni

| Risorsa | Richiesto |
|---------|-----------|
| **Python** | 3.12+ (installazione nativa; Docker include Python) |
| **ffmpeg** | Obbligatorio — estrae audio da video |
| **CPU** | x64 moderna; elaborazione **sequenziale** (un job alla volta) |
| **GPU NVIDIA** | Opzionale — accelera solo la **trascrizione** ASR |

## Confronto per scenario

| Scenario | RAM sistema | Disco libero | Rete | Modelli su disco |
|----------|-------------|--------------|------|------------------|
| **Solo trascrizione** | **8 GB** min · **16 GB** consigliato | **~6 GB** | Solo al primo setup | Parakeet ~2.5 GB |
| **Trascrizione + riassunto API** | Come sopra | Come sopra | **Sì** durante riassunto | Solo Parakeet |
| **Trascrizione + riassunto locale** | **≥ 16 GB** · **32 GB** ideale | **~8–10 GB** | Solo al primo setup | Parakeet + Qwen ~2 GB |

!!! note "RAM e riassunto locale"
    Prima del riassunto locale la pipeline **scarica il modello ASR dalla RAM**. Serve **≥ 16 GB di RAM fisica totali** (soglia in `MIN_RAM_GB`); sotto questa soglia il motore Qwen è disabilitato.

---

## 1. Solo trascrizione

| Risorsa | Dettaglio |
|---------|-----------|
| **RAM** | Minimo **8 GB**; **16 GB** consigliati per audio lunghi (1 h+). |
| **Disco** | ~2.5 GB ASR + ~3–4 GB dipendenze + output utente → **≥ 6 GB** liberi. |
| **Rete** | Solo download iniziale modello. Uso normale **offline**. |
| **GPU** | Opzionale. Su CPU: ~**2× realtime** (1 min audio ≈ 2 min elaborazione). |

---

## 2. Trascrizione + riassunto API

| Risorsa | Dettaglio |
|---------|-----------|
| **RAM** | Come solo trascrizione — LLM non in locale. |
| **Disco** | Come solo trascrizione — nessun modello riassunto. |
| **Rete** | **Obbligatoria** per le chiamate API durante il riassunto. |
| **API key** | UI `/settings/summary` o `data/.secrets/summary_keys.json`. |

Adatto a PC con **8 GB RAM** se usi solo cloud.

---

## 3. Trascrizione + riassunto locale (Qwen)

| Risorsa | Dettaglio |
|---------|-----------|
| **RAM** | **≥ 16 GB** (verificato all'avvio). **32 GB** consigliati (mini PC, file lunghi). |
| **Disco** | Solo trascrizione **+ ~2 GB** GGUF Qwen. |
| **Rete** | Solo download iniziale Qwen. Poi **offline**. |
| **CPU** | Riassunto **CPU-bound**; testi lunghi: diversi minuti (map-reduce). |
| **Docker** | Auto-download Qwen al primo avvio se RAM ≥ 16 GB (~10–20 min, una tantum). |

Vedi anche [Modelli](models.md) e [Docker](../deployment/docker.md).
