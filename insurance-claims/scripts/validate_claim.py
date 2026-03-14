"""Stub validator for Stedi claim payloads."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

RESERVED_X12_DELIMS = {"~", "*", ":", "^"}
PCN_REGEX = re.compile(r"^[A-Za-z0-9]{1,17}$")


def _load_payload(payload_path: str) -> Dict[str, Any]:
    return json.loads(Path(payload_path).read_text())


def validate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    claim_info = payload.get("claimInformation", {})
    pcn = claim_info.get("patientControlNumber")
    if not pcn:
        errors.append("Missing claimInformation.patientControlNumber")
    elif not PCN_REGEX.match(str(pcn)):
        errors.append("patientControlNumber must be alphanumeric and <= 17 chars")

    claim_charge = claim_info.get("claimChargeAmount")
    service_lines = claim_info.get("serviceLines", [])
    if claim_charge and service_lines:
        try:
            total = sum(float(s["professionalService"]["lineItemChargeAmount"]) for s in service_lines if "professionalService" in s and "lineItemChargeAmount" in s["professionalService"])
            if abs(float(claim_charge) - total) > 0.001:
                errors.append("claimChargeAmount does not match service line totals")
        except Exception:
            warnings.append("Could not evaluate service line totals (stub parser)")

    payload_str = json.dumps(payload)
    for ch in RESERVED_X12_DELIMS:
        if ch in payload_str:
            warnings.append(f"Payload contains reserved delimiter character '{ch}'")
            break

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate claim payload (stub).")
    parser.add_argument("--payload", required=True, help="Path to JSON claim payload.")
    args = parser.parse_args()

    payload = _load_payload(args.payload)
    print(json.dumps(validate_payload(payload), indent=2))


if __name__ == "__main__":
    main()

