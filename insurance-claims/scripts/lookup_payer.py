"""Stub for payer lookup via Stedi APIs."""

from __future__ import annotations

import argparse
import json
from config import get_headers


def main() -> None:
    parser = argparse.ArgumentParser(description="Lookup payer (stub).")
    parser.add_argument("--query", required=True, help="Payer name or ID fragment.")
    args = parser.parse_args()

    _ = get_headers()
    _ = args.query

    result = {
        "payers": [
            {
                "payerId": "6400",
                "name": "Example Payer",
                "aliases": ["EXAMPLE", "PAYER6400"],
                "supportedTransactions": ["837P", "835", "277", "276"],
            }
        ],
        "note": "Dummy output only. API call not implemented yet.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

