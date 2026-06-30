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
Regole:
- Scrivi in italiano corretto e chiaro.
- Riassumi in prosa (non elenco puntato a meno che non serva).
- Includi: chi parla (se noto), contesto, punti principali in ordine logico.
- NON inventare fatti assenti nel testo.
- NON ribaltare il significato del parlante.
- Se il testo è un'intervista o un monologo, mantieni il filo narrativo."""


def user_prompt(transcript: str, length: SummaryLength) -> str:
    return (
        f"{length_instruction(length)}\n\n"
        "Trascrizione da riassumere:\n\n"
        f"{transcript.strip()}"
    )


def merge_prompt(partial_summaries: str, length: SummaryLength) -> str:
    return (
        f"{length_instruction(length)}\n\n"
        "Unisci i seguenti riassunti parziali in un unico riassunto coerente "
        "senza ripetizioni e senza perdere i punti chiave:\n\n"
        f"{partial_summaries.strip()}"
    )
