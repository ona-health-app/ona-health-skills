---
name: insurance-claims
description: Use this skill for insurance-claims operations with Stedi whenever the user asks to submit claims, validate claim payloads, check claim status, retrieve/interpret 277CA or 835 responses, troubleshoot payer/provider enrollment requirements, or build deterministic claims workflows. Trigger this skill even if the user does not say "Stedi" explicitly but mentions 837/835/277CA/ERA, payer IDs, claim rejection codes, claim resubmission, COB, or healthcare clearinghouse automation.
---

# insurance-claims

Deterministic, API-first insurance claims workflow skill.

## Setup check — do this first

Before doing anything else, silently verify the Stedi API key is available.

The user experience must stay clinician-friendly:

1. Run the key check yourself with tooling. Do not ask the user to run Python, shell, or setup scripts.
2. If the key is present, continue without mentioning setup.
3. If the key is missing, ask in plain language only:
   - "I need your Stedi API key to connect to the insurance clearinghouse. You can find or create it at https://app.stedi.com/app/settings/api-keys. Paste it here and I will set it up for you."
4. When the user shares the key, write it to repo-root `.env` as:
   - `STEDI_API_KEY=<key>`
5. Confirm setup is complete and continue the original claims task.

Do not instruct clinicians to edit `.env`, export env vars, install dependencies, or run terminal commands.

## Operating principles

1. Use **Stedi API + deterministic scripts** for validations, submissions, status checks, and retrieval workflows.
2. Prefer structured JSON inputs/outputs. Avoid ad-hoc, ambiguous steps.
3. Run a **requirements preflight** before claim actions (payer support, enrollment status, provider identifiers).
4. Fail fast with actionable remediation steps when prerequisites are not met.
5. Keep PHI exposure minimal in logs and outputs.

## Read path (progressive disclosure)

Start with:
- `references/stedi-overview.md`

Then read only what is needed:
- Eligibility checks (270/271): `references/stedi-eligibility.md`
- Submission design: `references/stedi-submitting-claims.md`
- Response handling: `references/stedi-claim-responses.md`
- Practical constraints: `references/stedi-best-practices.md`
- Rejections/resubmissions lifecycle: `references/stedi-claim-lifecycle.md`
- Enrollment/payer requirements: `references/stedi-enrollment-and-payers.md`
- Test workflows (only when user explicitly asks for testing/dry run behavior): `references/stedi-testing.md`
- Attachments and MCP context: `references/stedi-attachments-and-mcp.md`
- Provider/payer requirement preflight: `references/provider-requirements.md`

## Deterministic workflow

Follow this sequence unless user explicitly requests otherwise.

1. **Classify task**
   - One of: `check_eligibility`, `validate_claim`, `submit_claim`, `check_claim_status`, `lookup_payer`, `retrieve_277ca`, `retrieve_835era`, `poll_transactions`, `resubmit_or_void`.

2. **Run preflight requirements check**
   - Resolve payer ID.
   - Verify transaction support.
   - Verify enrollment requirement and status.
   - Verify provider identifiers (NPI and any payer-specific requirements).
   - If any check fails, stop and return deterministic remediation.
   - Do not ask clinicians to choose an environment.

3. **Use script stubs/interfaces (or real implementation when present)**
   - `scripts/check_eligibility.py` ← real implementation, makes live API call
   - `scripts/validate_claim.py`
   - `scripts/submit_claim.py`
   - `scripts/check_claim_status.py`
   - `scripts/lookup_payer.py`
   - `scripts/retrieve_277ca.py`
   - `scripts/retrieve_835era.py`
   - `scripts/poll_transactions.py`

4. **Correlate all transactions**
   - Primary key: `patientControlNumber`.
   - Secondary key: Stedi `correlationId`.
   - Line-level key: service-line control number.

5. **Return structured output**
   - Include status summary, key identifiers, and next action suggestions.

### Mode selection rule (user-facing UX)

- Default to production behavior for real claim operations.
- Switch to test behavior only when the user explicitly asks for test mode, dry run, sandbox, or validation-only execution.
- Keep this automatic; do not ask clinicians to choose between technical environments.

## Script usage contract

Use these interfaces unless user requests a different shape.

- `check_eligibility.py` — **real API call** (270/271 eligibility)
  - Quick usage: `python3 check_eligibility.py test` (sandbox, no patient data needed)
  - Live usage: `python3 check_eligibility.py check --payer-id <ID> --npi <NPI> --provider-name <NAME> --member-id <MID> --subscriber-first <F> --subscriber-last <L> --subscriber-dob <YYYYMMDD> [--service-type-codes MH] [--dependent-first <F> --dependent-last <L> --dependent-dob <YYYYMMDD>]`
  - Output:
    ```json
    {
      "coverageActive": true,
      "planName": "...",
      "insuranceType": "PPO",
      "groupNumber": "...",
      "mentalHealth": { "covered": true, "copay": "$30", "coinsurance": null },
      "deductible": { "total": "$1500", "remaining": "$800" },
      "outOfPocketMax": "$4000",
      "raw": {}
    }
    ```
  - On error, returns `{ "coverageActive": false, "errors": [...], "raw": {} }`
  - For payer IDs, service type codes, AAA error codes, and edge cases (Medicare, Medi-Cal, dependents): read `references/stedi-eligibility.md`

- `validate_claim.py`
  - Input: JSON payload path
  - Output:
    ```json
    { "valid": true, "errors": [], "warnings": [] }
    ```

- `submit_claim.py`
  - Input: claim type (`professional|institutional|dental`), payload, optional test flag
  - Output:
    ```json
    {
      "status": "SUCCESS",
      "correlationId": "...",
      "patientControlNumber": "...",
      "errors": []
    }
    ```

- `check_claim_status.py`
  - Output:
    ```json
    {
      "claims": [
        { "statusCategoryCode": "...", "statusCode": "...", "description": "..." }
      ]
    }
    ```

- `lookup_payer.py`
  - Output:
    ```json
    {
      "payers": [
        { "payerId": "...", "name": "...", "aliases": [], "supportedTransactions": [] }
      ]
    }
    ```

- `retrieve_277ca.py` / `retrieve_835era.py` / `poll_transactions.py`
  - Return normalized, parser-friendly objects with deterministic fields.

## Required guardrails

- Authentication: read API key from `STEDI_API_KEY`.
- Always include idempotency keys on submission requests.
- Validate PCN format (alphanumeric, <=17 chars) and uniqueness.
- Avoid reserved delimiter characters in JSON data where applicable.
- Use `usageIndicator: "T"` for test submissions and `"P"` for production.
- Do not claim adjudication outcome from 277CA alone.
- Treat duplicate webhooks/responses as normal; deduplicate by transaction and payment trace keys.

## Resubmission policy

When user asks to fix/retry/cancel claims:
- Use lifecycle rules in `references/stedi-claim-lifecycle.md`.
- Determine if claim entered payer system before choosing frequency code.
- Include PCCN where required for replacement/void flows.
- Generate a new PCN on each resubmission.

## Output format for user responses

When performing claims tasks, return:

1. `What I did` (short)
2. `Result` (status + key IDs)
3. `Why` (if rejected/blocked)
4. `Next actions` (numbered, deterministic)

Example:

```json
{
  "action": "submit_claim",
  "status": "blocked",
  "reason_code": "ENROLLMENT_REQUIRED",
  "context": {
    "providerNpi": "1999999984",
    "payerId": "6400",
    "transactionType": "835"
  },
  "nextActions": [
    "Submit enrollment request for 835",
    "Wait for enrollment status live",
    "Retry submission with same validated payload structure"
  ]
}
```

## What to avoid

- Do not skip preflight checks for payer/provider requirements.
- Do not use vague advice when a deterministic action is possible.
- Do not expose full PHI payloads unless user explicitly requests and context is safe.
- Do not mix test and production assumptions in one run.
