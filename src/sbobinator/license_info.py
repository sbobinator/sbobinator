# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""License URLs and first-run acknowledgment (stored under data/)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from sbobinator.config import data_dir

# Public documentation (GitHub Pages)
DOCS_SITE = "https://sbobinator.github.io/docs"
DOCS_LICENSE_EN = f"{DOCS_SITE}/reference/licenses/"
DOCS_LICENSE_IT = f"{DOCS_SITE}/it/reference/licenses/"
DOCS_COMMERCIAL_EN = f"{DOCS_SITE}/reference/commercial-license/"
DOCS_COMMERCIAL_IT = f"{DOCS_SITE}/it/reference/commercial-license/"

COMMERCIAL_CONTACT_URL = "https://antoniotrento.net"

_ACK_FILE = ".sbobinator_license_ack.json"


def license_ack_path() -> Path:
    return data_dir() / _ACK_FILE


def is_license_acknowledged() -> bool:
    path = license_ack_path()
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return bool(data.get("acknowledged"))
    except (json.JSONDecodeError, OSError):
        return False


def acknowledge_license(*, app_version: str = "") -> None:
    path = license_ack_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "acknowledged": True,
        "acknowledged_at": datetime.now().isoformat(timespec="seconds"),
        "app_version": app_version,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def license_ui_context() -> dict[str, object]:
    return {
        "license_acknowledged": is_license_acknowledged(),
        "docs_license_url_en": DOCS_LICENSE_EN,
        "docs_license_url_it": DOCS_LICENSE_IT,
        "docs_commercial_url_en": DOCS_COMMERCIAL_EN,
        "docs_commercial_url_it": DOCS_COMMERCIAL_IT,
        "commercial_contact_url": COMMERCIAL_CONTACT_URL,
    }
