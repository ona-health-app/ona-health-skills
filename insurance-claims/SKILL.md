---
name: insurance-claims
description: Use this skill for insurance-claims operations with Stedi whenever the user asks to check patient eligibility, verify insurance coverage, submit claims, validate claim payloads, check claim status, retrieve/interpret 277CA or 835 responses, troubleshoot payer/provider enrollment requirements, or build deterministic claims workflows. Trigger this skill even if the user does not say "Stedi" explicitly but mentions eligibility checks, 270/271, insurance verification, benefits lookup, member coverage, deductible/copay/coinsurance inquiries, 837/835/277CA/ERA, payer IDs, claim rejection codes, claim resubmission, COB, or healthcare clearinghouse automation.
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

1. Use **Stedi API calls directly** (via HTTP requests with your available tools) for validations, submissions, status checks, and retrieval workflows.
2. Prefer structured JSON inputs/outputs. Avoid ad-hoc, ambiguous steps.
3. Run a **requirements preflight** before claim actions (payer support, enrollment status, provider identifiers).
4. Fail fast with actionable remediation steps when prerequisites are not met.
5. Keep PHI exposure minimal in logs and outputs.

## Read path (progressive disclosure)

Start with:
- `references/stedi-overview.md`

Then read only what is needed:

### Eligibility checking (270/271) — deep reference tree

When the user asks to check eligibility, verify coverage, or anything related to 270/271:

1. **Always start with:** `references/stedi-eligibility.md` — quick-reference for payer IDs, STCs, response parsing, and the API call interface.

2. **For building or debugging raw API calls:** `references/eligibility-check/eligibility-api-reference.md` — comprehensive endpoint docs including every request field, response field, and interpretation guide.

3. **For constructing test requests:** Choose based on check type:
   - Medical (subscriber or dependent): `references/eligibility-check/mock-requests-medical.md`
   - Dental: `references/eligibility-check/mock-requests-dental.md`
   - Error simulation: `references/eligibility-check/mock-requests-errors.md`

4. **For payer-specific quirks and requirements:** `references/eligibility-check/provider-requirements.md` — per-payer behaviors, enrollment needs, and gotchas (Cigna dependent response quirk, CMS MBI/X-Forwarded-For, Medi-Cal portal credentials, BCBS home plan routing, etc.).

5. **For payload templates:** Use the JSON templates in `assets/eligibility-check/`:
   - `subscriber_check_template.json` — subscriber-only medical check
   - `dependent_check_template.json` — dependent on subscriber's plan
   - `dental_check_template.json` — dental eligibility check
   - `mbi_lookup_template.json` — Medicare MBI lookup via SSN
   - `medicaid_check_template.json` — Medicaid with portal credentials

### Claims and other workflows

- Submission design: `references/stedi-submitting-claims.md`
- Response handling: `references/stedi-claim-responses.md`
- Practical constraints: `references/stedi-best-practices.md`
- Rejections/resubmissions lifecycle: `references/stedi-claim-lifecycle.md`
- Enrollment/payer requirements: `references/stedi-enrollment-and-payers.md`
- Test workflows (only when user explicitly asks for testing/dry run behavior): `references/stedi-testing.md`
- Attachments and MCP context: `references/stedi-attachments-and-mcp.md`
- Provider/payer requirement preflight: `references/provider-requirements.md`

## Eligibility check workflow

When the task is `check_eligibility`, follow this sequence:

### 1. Gather required information

Collect from the user (or from available context):
- **Payer ID** — resolve from insurance card or payer name. Use `references/stedi-eligibility.md` for common IDs, or call the Payers API (`GET https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/payers`) to search.
- **Provider NPI** — 10-digit National Provider Identifier.
- **Provider name** — organization or individual name.
- **Patient info** — at minimum: `memberId`, `firstName`, `lastName`, `dateOfBirth`. All four together guarantee a payer response.
- **Service type** — default `30` (general), use `MH` for mental health, `35` for dental, etc.

### 2. Determine check type and select template

| Scenario | Template | Key difference |
|---|---|---|
| Patient is the policyholder | `assets/eligibility-check/subscriber_check_template.json` | Patient info in `subscriber` |
| Patient is a dependent (child/spouse) | `assets/eligibility-check/dependent_check_template.json` | Policyholder in `subscriber`, patient in `dependents` |
| Dental coverage | `assets/eligibility-check/dental_check_template.json` | STC `35` instead of `30` |
| Medicare (need MBI first) | `assets/eligibility-check/mbi_lookup_template.json` | SSN + address, payer `CMS` |
| Medicaid | `assets/eligibility-check/medicaid_check_template.json` | Requires `portalUsername`/`portalPassword` |

### 3. Check payer-specific requirements

Read `references/eligibility-check/provider-requirements.md` for the target payer. Key things to verify:
- Does this payer require enrollment before eligibility checks? (CMS does)
- Does this payer need portal credentials? (Medi-Cal does)
- Does this payer need special headers? (CMS needs `X-Forwarded-For`)
- Any known quirks? (Cigna returns dependents in the subscriber object)

### 4. Execute the check

Make a direct HTTP POST to the Stedi eligibility endpoint using the appropriate template from `assets/eligibility-check/`. Refer to `references/eligibility-check/eligibility-api-reference.md` for full field details and advanced scenarios.

### 5. Interpret the response

Follow the interpretation steps in `references/eligibility-check/eligibility-api-reference.md`:
1. Check `errors` array first — if non-empty, handle AAA errors per `references/eligibility-check/mock-requests-errors.md`.
2. Confirm active coverage: look for `benefitsInformation` with `code: "1"`.
3. Extract financials: deductible (`C`), OOP max (`G`), copay (`B`), coinsurance (`A`).
4. Filter by `inPlanNetworkIndicatorCode: "Y"` for in-network values.
5. Check `timeQualifierCode`: `23` = total, `29` = remaining.
6. Check prior auth: `authOrCertIndicator: "Y"` means prior auth required.

### 6. Return structured result

Present the eligibility summary in the standard output format (see Output format section below).

---

## Deterministic workflow

Follow this sequence unless user explicitly requests otherwise.

1. **Classify task**
   - One of: `check_eligibility`, `validate_claim`, `submit_claim`, `check_claim_status`, `lookup_payer`, `retrieve_277ca`, `retrieve_835era`, `poll_transactions`, `resubmit_or_void`.
   - For `check_eligibility`, follow the Eligibility check workflow above.

2. **Run preflight requirements check**
   - Resolve payer ID.
   - Verify transaction support.
   - Verify enrollment requirement and status.
   - Verify provider identifiers (NPI and any payer-specific requirements).
   - For eligibility checks, also verify payer-specific requirements from `references/eligibility-check/provider-requirements.md`.
   - If any check fails, stop and return deterministic remediation.
   - Do not ask clinicians to choose an environment.

3. **Execute via direct Stedi API calls**
   - Make HTTP requests using your available tools (e.g., `curl`, `fetch`, or any HTTP client).
   - Use the endpoint, headers, and payload structure documented in the relevant reference files.
   - For eligibility: `POST https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/eligibility/v3`
   - For claims: use the appropriate endpoint per claim type (see `references/stedi-submitting-claims.md`)
   - For payer lookup: `GET https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/payers`
   - For claim status, 277CA retrieval, 835 ERA retrieval, and polling: use the corresponding Stedi API endpoints.

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

## Expected response formats

When presenting results to the user, normalize API responses into these structured shapes unless the user requests a different format.

- **Eligibility check** (270/271):
  - Parse the raw Stedi response and present:
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
  - On error: `{ "coverageActive": false, "errors": [...], "raw": {} }`
  - For payer IDs, service type codes, AAA error codes, and edge cases (Medicare, Medi-Cal, dependents): read `references/stedi-eligibility.md`

- **Claim validation** (pre-submission):
  - Validate the JSON payload locally against the required fields and format rules before calling the API.
  - Present: `{ "valid": true, "errors": [], "warnings": [] }`

- **Claim submission**:
  - Present:
    ```json
    {
      "status": "SUCCESS",
      "correlationId": "...",
      "patientControlNumber": "...",
      "errors": []
    }
    ```

- **Claim status check**:
  - Present:
    ```json
    {
      "claims": [
        { "statusCategoryCode": "...", "statusCode": "...", "description": "..." }
      ]
    }
    ```

- **Payer lookup**:
  - Present:
    ```json
    {
      "payers": [
        { "payerId": "...", "name": "...", "aliases": [], "supportedTransactions": [] }
      ]
    }
    ```

- **277CA / 835 ERA retrieval / transaction polling**:
  - Present normalized, parser-friendly objects with deterministic fields.

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
