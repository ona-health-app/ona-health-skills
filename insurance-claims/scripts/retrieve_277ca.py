"""Stub for retrieving/parsing 277CA reports."""

from __future__ import annotations

import argparse
import json
from config import get_headers


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve 277CA report (stub).")
    parser.add_argument("--transaction-id", required=True)
    args = parser.parse_args()

    _ = get_headers()
    _ = args.transaction_id

    result = {
        "transactionId": args.transaction_id,
        "statusSummary": "accepted",
        "errors": [],
        "claimCorrelation": {"patientControlNumber": "DUMMY-PCN"},
        "note": "Dummy output only. API call not implemented yet.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

