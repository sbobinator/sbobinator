# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""Prompt unificato per riassunto di trascritti parlati in italiano."""

from __future__ import annotations

from sbobinator.config import SummaryLength

_LENGTH_HINT = {
    SummaryLength.short: "Breve (circa 5-8 frasi).",
    SummaryLength.normal: "Normale (circa 8-15 frasi).",
    SummaryLength.detailed: "Dettagliato (circa 15-25 frasi, copri tutti i temi principali).",
    SummaryLength.auto: "Lunghezza proporzionata al testo (né troppo corto né eccessivo).",
}


def length_instruction(length: SummaryLength) -> str:
    return _LENGTH_HINT.get(length, _LENGTH_HINT[SummaryLength.auto])


SYSTEM_PROMPT = """Sei un assistente che riassume trascrizioni di audio parlato in italiano.

Regole obbligatorie:
- Scrivi in italiano corretto e chiaro, in prosa (non elenco puntato salvo casi eccezionali).
- Inizia DIRETTAMENTE con il contenuto: chi parla (se noto), contesto, punti principali in ordine logico.
- NON usare meta-frasi: vietato iniziare o parlare di "questa trascrizione", "il testo", "l'intervista", "il documento", "l'autore spiega che".
- NON inventare fatti, nomi, date o collegamenti assenti nel testo.
- Se il trascritto contiene parole probabilmente errate (errori ASR), non correggerle inventando: ometti o usa formulazioni prudenti ("secondo il trascritto...").
- NON ripetere la stessa informazione in paragrafi diversi.
- NON ribaltare il significato del parlante.
- Mantieni il filo narrativo su monologhi e interviste."""


def user_prompt(transcript: str, length: SummaryLength) -> str:
    return (
        f"{length_instruction(length)}\n\n"
        "Trascrizione da riassumere:\n\n"
        f"{transcript.strip()}"
    )


def merge_prompt(partial_summaries: str, length: SummaryLength) -> str:
    return (
        f"{length_instruction(length)}\n\n"
        "Unisci i seguenti riassunti parziali in un unico riassunto coerente. "
        "Elimina ripetizioni, mantieni tutti i punti chiave, senza meta-frasi "
        '(non dire "questo riassunto", "il testo", ecc.):\n\n'
        f"{partial_summaries.strip()}"
    )
