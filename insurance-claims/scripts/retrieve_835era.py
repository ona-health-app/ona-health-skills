"""Stub for retrieving/parsing 835 ERA reports."""

from __future__ import annotations

import argparse
import json
from config import get_headers


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve 835 ERA report (stub).")
    parser.add_argument("--transaction-id", required=True)
    args = parser.parse_args()

    _ = get_headers()
    _ = args.transaction_id

    result = {
        "transactionId": args.transaction_id,
        "paymentSummary": {
            "claimPaymentStatus": "PAID",
            "totalPaidAmount": "109.20",
        },
        "serviceLines": [{"lineItemControlNumber": "LINECTRL001", "paidAmount": "109.20"}],
        "note": "Dummy output only. API call not implemented yet.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

