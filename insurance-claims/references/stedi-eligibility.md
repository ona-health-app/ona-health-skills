# Stedi Eligibility Check Reference

Real-time insurance eligibility checks via the Stedi 270/271 API.

**Endpoint:**
```
POST https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/eligibility/v3
```

**Auth:** `Authorization: <STEDI_API_KEY>` header. Test keys start with `test_` and only accept the pre-approved sandbox payload.

---

## Required fields

| Field | Source | Notes |
|---|---|---|
| `tradingPartnerServiceId` | Insurance card / EHR | Payer ID — see table below |
| `provider.npi` | Practice record | 10-digit NPI |
| `provider.organizationName` | Practice record | Billing provider name |
| `subscriber.memberId` | Patient insurance card | Most important field |
| `subscriber.firstName` / `lastName` | Patient record | Must match insurance card exactly |
| `subscriber.dateOfBirth` | Patient record | Format: `YYYYMMDD` |
| `encounter.serviceTypeCodes` | Visit type | See STC table below |

---

## Common payer IDs

| Insurance | `tradingPartnerServiceId` |
|---|---|
| Aetna | `60054` |
| Cigna | `62308` |
| UnitedHealthcare | `87726` |
| Humana | `61101` |
| Medicare (CMS) | `CMS` |
| Anthem BCBS CA | `040` |
| Blue Shield CA | `100935` |
| Medi-Cal | `100065` |
| BCBS Texas | `84980` |
| BCBS Illinois | `G00621` |
| Oscar Health | `OSCAR` |
| UMR | `39026` |

Full payer list: `GET https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/payers`

---

## Service type codes (STCs)

| Code | Meaning |
|---|---|
| `30` | General / Plan coverage (default, always works) |
| `MH` | Mental health — use for therapy/psychiatry |
| `UC` | Urgent care |
| `98` | Professional office visit |
| `86` | Emergency services |
| `35` | Dental |

Include at most one STC per request. For ona.health mental health visits, always use `MH`.

---

## Sandbox test payload

Use with a `test_` API key. Do NOT change subscriber values — Stedi's PII detection will reject any changes with error code `33`.

```json
{
  "tradingPartnerServiceId": "60054",
  "provider": { "organizationName": "Provider Name", "npi": "1999999984" },
  "subscriber": {
    "memberId": "AETNA12345",
    "firstName": "Jane",
    "lastName": "Doe",
    "dateOfBirth": "20040404"
  },
  "encounter": { "serviceTypeCodes": ["30"] }
}
```

To test, POST this exact payload to the eligibility endpoint with a `test_` API key.

---

## Response structure

### 1. Check for errors first

```
response.status === "ERROR"           → top-level API/network error
response.subscriber.aaaErrors[]       → payer rejected the member lookup
```

Common AAA error codes:

| Code | Meaning | Action |
|---|---|---|
| `42` | Payer temporarily unavailable | Retry in a few minutes |
| `43` | Provider NPI not registered with this payer | Enroll NPI with payer |
| `72` | Wrong member ID | Verify card |
| `73` | Name mismatch | Check spelling vs. insurance card exactly |
| `75` | Member not found | Try different field combos or call payer |

### 2. Check active coverage

```
response.planStatus[].statusCode === "1"   → active coverage
```

### 3. Parse `benefitsInformation` array

Each object has a `code` field:

| `code` | Meaning | Key fields |
|---|---|---|
| `1` | Active coverage | `serviceTypeCodes`, `insuranceType` |
| `C` | Deductible | `benefitAmount`, `timeQualifierCode` (`25`=total, `29`=remaining), `inPlanNetworkIndicator` |
| `G` | Out-of-pocket max | Same as deductible |
| `B` | Copay | `benefitAmount`, `serviceTypeCodes` |
| `A` | Coinsurance | `benefitPercent` (0.2 = 20%), `serviceTypeCodes` |

Filter by `inPlanNetworkIndicator: "Yes"` to get in-network numbers.

`timeQualifierCode` values: `25` = calendar year total, `29` = remaining.

---

## Structured output format

```json
{
  "coverageActive": true,
  "planName": "Aetna Choice POS II",
  "insuranceType": "PPO",
  "groupNumber": "0123456",
  "mentalHealth": {
    "covered": true,
    "copay": "$30",
    "coinsurance": "20%"
  },
  "deductible": {
    "total": "$1500",
    "remaining": "$800"
  },
  "outOfPocketMax": "$4000",
  "raw": { "...": "full Stedi response" }
}
```

---

## Edge cases

### Dependent patient (on parent's or spouse's plan)

Move the patient to the `dependents` array; the policyholder stays in `subscriber`. Use the dependent check template from `assets/eligibility-check/dependent_check_template.json` and fill in the policyholder fields in `subscriber` and the patient fields in `dependents`.

### Medicare (payer ID: `CMS`)

- Requires enrollment first — multi-step process, can take hours to activate.
- Use patient's MBI (Medicare Beneficiary Identifier) as `memberId`.
- Must include `X-Forwarded-For` header with upstream IPs.
- For Medicare Advantage plans, use the plan's actual payer ID (e.g. UnitedHealthcare `87726`), not `CMS`.

### Medi-Cal (payer ID: `100065`)

Requires `portalUsername` and `portalPassword` in the request body — these are the provider's Medi-Cal portal credentials.

### Payer timeout / retries

Stedi holds requests open for 120 seconds and retries automatically. If a request times out, check `aaaErrors` before retrying manually.

---

## When to re-check eligibility

- At appointment booking (initial check)
- Day before the visit (coverage may have lapsed)
- When patient reports an insurance change
- After a claim denial — reverify before resubmitting

Do NOT re-check on the same day — many payers throttle repeated lookups.
