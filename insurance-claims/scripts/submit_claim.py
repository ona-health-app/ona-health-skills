"""Stub submitter for 837P/837I/837D Stedi JSON APIs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from config import BASE_URLS, get_headers


def submit_stub(claim_type: str, payload: Dict[str, Any], test_mode: bool) -> Dict[str, Any]:
    """Return dummy structured output matching expected interface."""
    if test_mode:
        payload["usageIndicator"] = "T"

    _ = get_headers(idempotency_key="dummy-idempotency-key")
    _ = BASE_URLS[claim_type]

    return {
        "status": "SUCCESS",
        "claimType": claim_type,
        "testMode": test_mode,
        "correlationId": "DUMMY-CORRELATION-ID",
        "patientControlNumber": payload.get("claimInformation", {}).get(
            "patientControlNumber", "UNKNOWN-PCN"
        ),
        "errors": [],
        "note": "Dummy output only. API call not implemented yet.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Submit claim (stub).")
    parser.add_argument(
        "--type",
        required=True,
        choices=["professional", "institutional", "dental"],
        help="Claim type to submit.",
    )
    parser.add_argument("--payload", required=True, help="Path to claim JSON payload.")
    parser.add_argument("--test", action="store_true", help="Set usageIndicator=T.")
    args = parser.parse_args()

    payload = json.loads(Path(args.payload).read_text())
    print(json.dumps(submit_stub(args.type, payload, args.test), indent=2))


if __name__ == "__main__":
    main()

