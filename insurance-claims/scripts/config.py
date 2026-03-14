"""Shared configuration helpers for Stedi script stubs."""

from __future__ import annotations

import os
import pathlib
from typing import Dict, Optional

STEDI_API_KEY_ENV = "STEDI_API_KEY"

def _load_dotenv() -> None:
    """Load .env from repo root (two levels above this file) if dotenv is available."""
    env_path = pathlib.Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv(env_path, override=False)
    except ImportError:
        # dotenv not installed — fall back to manual parse so the .env file
        # still works without requiring an extra dependency
        with env_path.open() as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value

_load_dotenv()

BASE_URLS = {
    "professional": "https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/professionalclaims/v3/submission",
    "institutional": "https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/institutionalclaims/v2/submission",
    "dental": "https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/dentalclaims/v2/submission",
    "claim_status": "https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/claimstatus/v3/submission",
}


def get_api_key() -> str:
    """Return STEDI_API_KEY from environment or .env file, raising if unset."""
    api_key = os.getenv(STEDI_API_KEY_ENV, "").strip()
    if not api_key:
        raise RuntimeError(
            f"{STEDI_API_KEY_ENV} is not set.\n"
            "Add it to the .env file at the repo root:\n"
            "  STEDI_API_KEY=your-key-here\n"
            "You can create or copy an existing key at https://app.stedi.com/app/settings/api-keys"
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

