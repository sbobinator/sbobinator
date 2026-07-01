# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""SSL per richieste HTTPS su Windows (certificate store di sistema)."""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)

_configured = False


def ensure_ssl() -> None:
    """Usa il trust store OS se truststore è installato (fix Python 3.13 su Windows)."""
    global _configured
    if _configured:
        return
    try:
        import truststore

        truststore.inject_into_ssl()
    except ImportError:
        if sys.platform == "win32":
            logger.warning(
                "truststore non installato: le API cloud (OpenAI, DeepSeek, Gemini, …) "
                "possono fallire con «Connection error». "
                "Esegui: pip install -r requirements/local.txt"
            )
    _configured = True
