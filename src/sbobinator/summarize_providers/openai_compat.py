# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""Client OpenAI-compatible per chat completion."""

from __future__ import annotations

from sbobinator.http_ssl import ensure_ssl


def chat_complete(
    *,
    api_key: str,
    model: str,
    system: str,
    user: str,
    base_url: str | None = None,
    timeout: float = 180.0,
) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            "Provider cloud richiede il pacchetto openai. Installa con:\n"
            "  pip install -e '.[summarize]'"
        ) from exc

    ensure_ssl()
    kwargs: dict = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        timeout=timeout,
    )
    choice = response.choices[0].message.content
    return (choice or "").strip()
