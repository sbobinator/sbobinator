# Licenses and third-party components

## Sbobinator (application code)

**Proprietary license** — Copyright © 2024-2026 [Antonio Trento](https://antoniotrento.net).

See the [`LICENSE`](../../LICENSE) file in the repository root.

| Use type | Conditions |
|----------|------------|
| Personal, study, documentable non-profit | Free |
| Companies, public sector, professionals, commercial or internal organizational use | **Paid commercial license** |

Redistribution of the Software without written authorization is not permitted.

For commercial licenses: https://antoniotrento.net

See **[Commercial licensing](commercial-license.md)** for who must pay, how to buy, and roadmap (desktop apps).

!!! note "Previous MIT versions"
    Any releases already distributed under the MIT license remain usable under the MIT terms valid at the time of distribution. Current and future versions follow the proprietary license in `LICENSE`.

---

## Pre-trained models

Models are **not** included in the git repository. They are downloaded separately.

### NVIDIA Parakeet TDT 0.6B v3

- **Source:** [HuggingFace nvidia/parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- **Use:** ASR transcription
- **License:** See NVIDIA HuggingFace card (commercial use restrictions to verify for your case)

### Qwen2.5-3B-Instruct (GGUF, optional)

- **Source:** HuggingFace / llama.cpp
- **Use:** Local summarization
- **License:** See Qwen model card on HuggingFace

### Deprecated: Google mT5-small

No longer used as the product summary engine. Any remaining files are legacy.

---

## Main Python dependencies

| Package | Typical license |
|---------|-----------------|
| PyTorch | BSD-style |
| nemo_toolkit | Apache 2.0 |
| FastAPI | MIT |
| uvicorn | BSD |
| typer | MIT |
| llama-cpp-python | MIT |

For the full list: `pip-licenses` after install.

Use of these libraries is subject to their respective open source licenses; the Sbobinator license does not extend rights to third-party packages.

---

## ffmpeg

External binary **not** distributed with Sbobinator.

- License: LGPL/GPL depending on the build
- The user must install ffmpeg compliant with their platform

---

## Legal notes

- **Audio content:** you are responsible for rights on the files you process.
- **AI models:** respect NVIDIA, HuggingFace terms of use and any commercial limits **in addition to** the Sbobinator license.
- **Output:** automatic transcription may contain errors; it does not replace human review for legal or medical use.
- **Not legal advice:** for corporate compliance consult a qualified lawyer.
