"""Real-time insurance eligibility check via Stedi 270/271 API."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from config import ELIGIBILITY_URL, get_api_key

# ---------------------------------------------------------------------------
# Sandbox payload — only valid with a test_ API key.
# Stedi's PII detection is strict; do NOT change subscriber values.
# ---------------------------------------------------------------------------
SANDBOX_PAYLOAD: Dict[str, Any] = {
    "tradingPartnerServiceId": "60054",
    "provider": {
        "organizationName": "Provider Name",
        "npi": "1999999984",
    },
    "subscriber": {
        "memberId": "AETNA12345",
        "firstName": "Jane",
        "lastName": "Doe",
        "dateOfBirth": "20040404",
    },
    "encounter": {
        "serviceTypeCodes": ["30"],
    },
}


# ---------------------------------------------------------------------------
# Payload builder
# ---------------------------------------------------------------------------

def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "tradingPartnerServiceId": args.payer_id,
        "provider": {
            "organizationName": args.provider_name,
            "npi": args.npi,
        },
        "subscriber": {
            "memberId": args.member_id,
            "firstName": args.subscriber_first,
            "lastName": args.subscriber_last,
            "dateOfBirth": args.subscriber_dob,
        },
        "encounter": {
            "serviceTypeCodes": args.service_type_codes,
        },
    }

    # Dependent case: patient is on someone else's plan.
    # Policy holder stays in subscriber; patient moves to dependents.
    if args.dependent_first:
        if not (args.dependent_last and args.dependent_dob):
            raise ValueError(
                "--dependent-first requires --dependent-last and --dependent-dob"
            )
        payload["dependents"] = [
            {
                "firstName": args.dependent_first,
                "lastName": args.dependent_last,
                "dateOfBirth": args.dependent_dob,
            }
        ]

    return payload


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------

def _find_benefit(
    benefits: List[Dict[str, Any]],
    code: str,
    stc: Optional[str] = None,
    time_qual: Optional[str] = None,
    in_network: bool = True,
) -> Optional[Dict[str, Any]]:
    for b in benefits:
        if b.get("code") != code:
            continue
        if stc and stc not in (b.get("serviceTypeCodes") or []):
            continue
        if time_qual and b.get("timeQualifierCode") != time_qual:
            continue
        if in_network and b.get("inPlanNetworkIndicator") != "Yes":
            continue
        return b
    return None


def parse_response(data: Dict[str, Any]) -> Dict[str, Any]:
    # Top-level API error (bad request, unknown payer, etc.)
    if data.get("status") == "ERROR":
        return {
            "coverageActive": False,
            "errors": data.get("errors", []),
            "raw": data,
        }

    # Payer-level AAA errors (member not found, name mismatch, etc.)
    aaa_errors: List[Any] = (data.get("subscriber") or {}).get("aaaErrors") or []
    if aaa_errors:
        return {
            "coverageActive": False,
            "errors": aaa_errors,
            "raw": data,
        }

    plan_status: List[Dict[str, Any]] = data.get("planStatus") or []
    is_active = any(s.get("statusCode") == "1" for s in plan_status)

    benefits: List[Dict[str, Any]] = data.get("benefitsInformation") or []

    mh_copay = _find_benefit(benefits, "B", stc="MH")
    mh_coinsurance = _find_benefit(benefits, "A", stc="MH")
    deductible_total = _find_benefit(benefits, "C", time_qual="25")
    deductible_remaining = _find_benefit(benefits, "C", time_qual="29")
    oop_max = _find_benefit(benefits, "G", time_qual="25")
    active_coverage = _find_benefit(benefits, "1")

    mh_covered = any(
        b.get("code") == "1" and "MH" in (b.get("serviceTypeCodes") or [])
        for b in benefits
    )

    plan_info: Dict[str, Any] = data.get("planInformation") or {}
    plan_name = plan_info.get("planDescription") or (
        plan_status[0].get("planDetails") if plan_status else None
    )

    def _fmt_amount(b: Optional[Dict[str, Any]]) -> Optional[str]:
        if b and b.get("benefitAmount"):
            return f"${b['benefitAmount']}"
        return None

    def _fmt_pct(b: Optional[Dict[str, Any]]) -> Optional[str]:
        if b and b.get("benefitPercent"):
            try:
                return f"{round(float(b['benefitPercent']) * 100)}%"
            except (ValueError, TypeError):
                return b["benefitPercent"]
        return None

    return {
        "coverageActive": is_active,
        "planName": plan_name,
        "insuranceType": (active_coverage or {}).get("insuranceType"),
        "groupNumber": (data.get("subscriber") or {}).get("groupNumber"),
        "mentalHealth": {
            "covered": mh_covered,
            "copay": _fmt_amount(mh_copay),
            "coinsurance": _fmt_pct(mh_coinsurance),
        },
        "deductible": {
            "total": _fmt_amount(deductible_total),
            "remaining": _fmt_amount(deductible_remaining),
        },
        "outOfPocketMax": _fmt_amount(oop_max),
        "raw": data,
    }


# ---------------------------------------------------------------------------
# HTTP call
# ---------------------------------------------------------------------------

def check_eligibility(payload: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ELIGIBILITY_URL,
        data=body,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return parse_response(data)
    except urllib.error.HTTPError as exc:
        try:
            error_body = json.loads(exc.read().decode("utf-8"))
        except Exception:
            error_body = {}
        return {
            "coverageActive": False,
            "errors": [
                {
                    "httpStatus": exc.code,
                    "reason": exc.reason,
                    "detail": error_body,
                }
            ],
            "raw": error_body,
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check insurance eligibility via Stedi 270/271 API."
    )
    sub = parser.add_subparsers(dest="mode")

    # -- test subcommand --
    sub.add_parser(
        "test",
        help="Run with the Stedi sandbox payload (Aetna / Jane Doe). Requires a test_ API key.",
    )

    # -- check subcommand --
    chk = sub.add_parser("check", help="Run a real eligibility check.")
    chk.add_argument("--payer-id", required=True, help="Stedi trading partner ID (e.g. 60054).")
    chk.add_argument("--npi", required=True, help="Billing provider NPI (10 digits).")
    chk.add_argument("--provider-name", required=True, help="Billing provider organization name.")
    chk.add_argument("--member-id", required=True, help="Patient member/subscriber ID from insurance card.")
    chk.add_argument("--subscriber-first", required=True, help="Policyholder first name.")
    chk.add_argument("--subscriber-last", required=True, help="Policyholder last name.")
    chk.add_argument("--subscriber-dob", required=True, help="Policyholder date of birth (YYYYMMDD).")
    chk.add_argument(
        "--service-type-codes",
        nargs="+",
        default=["MH"],
        metavar="STC",
        help="Service type code(s). Default: MH (mental health). Use 30 for general coverage.",
    )
    # Dependent fields — used when the patient is on someone else's plan.
    chk.add_argument("--dependent-first", help="Patient first name (if patient != policyholder).")
    chk.add_argument("--dependent-last", help="Patient last name (if patient != policyholder).")
    chk.add_argument("--dependent-dob", help="Patient date of birth YYYYMMDD (if patient != policyholder).")

    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        return

    api_key = get_api_key()

    if args.mode == "test":
        payload = SANDBOX_PAYLOAD
    else:
        payload = build_payload(args)

    result = check_eligibility(payload, api_key)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
