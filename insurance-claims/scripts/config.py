"""Shared configuration helpers for Stedi script stubs."""

from __future__ import annotations

import os
from typing import Dict, Optional

STEDI_API_KEY_ENV = "STEDI_API_KEY"

BASE_URLS = {
    "professional": "https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/professionalclaims/v3/submission",
    "institutional": "https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/institutionalclaims/v2/submission",
    "dental": "https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/dentalclaims/v2/submission",
    "claim_status": "https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/claimstatus/v3/submission",
}


def get_api_key() -> str:
    """Return STEDI_API_KEY from environment, raising if unset."""
    api_key = os.getenv(STEDI_API_KEY_ENV, "").strip()
    if not api_key:
        raise RuntimeError(
            f"{STEDI_API_KEY_ENV} is not set. Export it before running scripts."
        )
    return api_key


def get_headers(idempotency_key: Optional[str] = None) -> Dict[str, str]:
    """Build default headers for JSON API requests."""
    headers = {
        "Authorization": get_api_key(),
        "Content-Type": "application/json",
    }
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    return headers

