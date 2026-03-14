"""Stub for polling inbound claim response transactions."""

from __future__ import annotations

import argparse
import json
from config import get_headers


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll transactions (stub).")
    parser.add_argument("--since", required=True, help="ISO datetime cursor")
    parser.add_argument("--type", choices=["277", "835", "all"], default="all")
    args = parser.parse_args()

    _ = get_headers()
    _ = args

    transactions = [
        {
            "transactionId": "TXN-DUMMY-001",
            "type": "277",
            "direction": "INBOUND",
        },
        {
            "transactionId": "TXN-DUMMY-002",
            "type": "835",
            "direction": "INBOUND",
        },
    ]

    if args.type != "all":
        transactions = [t for t in transactions if t["type"] == args.type]

    print(
        json.dumps(
            {
                "transactions": transactions,
                "note": "Dummy output only. API call not implemented yet.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

