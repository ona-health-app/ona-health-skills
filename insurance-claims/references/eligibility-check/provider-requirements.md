# Provider-Specific Eligibility Requirements

Per-payer quirks, requirements, and behaviors for eligibility checks.

---

## Table of Contents

- [Aetna](#aetna)
- [Ambetter](#ambetter)
- [Anthem BCBS CA](#anthem-bcbs-ca)
- [BCBS Texas](#bcbs-texas)
- [BCBS (general)](#bcbs-general)
- [Cigna](#cigna)
- [CMS / Medicare](#cms--medicare)
- [Humana](#humana)
- [Kaiser Permanente](#kaiser-permanente)
- [Medi-Cal / Medicaid](#medi-cal--medicaid)
- [MetLife](#metlife)
- [Oscar Health](#oscar-health)
- [UnitedHealthcare](#unitedhealthcare)
- [Ameritas](#ameritas)

---

## Aetna

| Property | Value |
|---|---|
| Payer ID | `60054` |
| Enrollment required | No (for eligibility) |
| Supported STCs | `30`, `35`, and many specialty codes |

**Behaviors:**
- Dependent information is returned in the `dependents` array (standard behavior).
- Supports comprehensive benefit breakdowns including place-of-service-specific copays.
- Returns plan name in `benefitsInformation` with `code: "1"` via the `planCoverage` field.

**Test data:** Confirmed Aetna subscriber mock: memberId `AETNA12345`, Jane Doe, DOB `20040404`.

---

## Ambetter

| Property | Value |
|---|---|
| Payer ID | `AMB01` |
| Enrollment required | Check payer |
| Supported STCs | `30` confirmed |

**Behaviors:**
- Standard response format.
- Test mock request available on Stedi docs.

---

## Anthem BCBS CA

| Property | Value |
|---|---|
| Payer ID | `040` |
| Enrollment required | No (for eligibility) |
| Supported STCs | `30`, `35` |

**Behaviors:**
- Dependent information is returned in the `dependents` array.
- Supports both medical and dental eligibility checks.
- Part of the BCBS network — see [BCBS general notes](#bcbs-general).

---

## BCBS Texas

| Property | Value |
|---|---|
| Payer ID | `84980` |
| Enrollment required | No (for eligibility) |
| Supported STCs | `30` confirmed |

**Behaviors:**
- Dependent information is returned in the `dependents` array.
- Part of the BCBS network — see [BCBS general notes](#bcbs-general).

---

## BCBS (general)

Blue Cross Blue Shield plans are state-specific. Each state BCBS plan has its own payer ID.

**Key BCBS behavior:**
- For out-of-state BCBS members, responses include a `benefitsRelatedEntities` entry with `entityIdentifier: "Party Performing Verification"` — this identifies the patient's **home plan** that actually verified coverage.
- Always use the correct state-specific payer ID for the patient's plan.
- Some BCBS plans use different payer IDs for medical vs. dental.

**Common BCBS payer IDs:**

| Plan | Payer ID |
|---|---|
| Anthem BCBS CA | `040` |
| BCBS Texas | `84980` |
| BCBS Illinois | `G00621` |
| BCBS Florida | Check Stedi payer list |

---

## Cigna

| Property | Value |
|---|---|
| Payer ID | `62308` |
| Enrollment required | No (for eligibility) |
| Supported STCs | `30`, `35`, and many specialty codes |

**Behaviors:**
- **Critical quirk:** For dependent checks, Cigna may return the dependent's information in the `subscriber` object with no `dependents` array, even though the patient is a dependent. Always check both objects.
- Provides 7 different mock request variants for testing diverse response shapes.
- Returns comprehensive benefit data including mental health (A4, A6, A7, A8), anesthesia, and place-of-service breakdowns.
- May include `eligibilityAdditionalInformation` with place-of-service codes (`11` Office, `22` Outpatient Hospital, `02` Telehealth).

---

## CMS / Medicare

| Property | Value |
|---|---|
| Payer ID | `CMS` |
| Enrollment required | **Yes** — multi-step, can take hours |
| Supported STCs | `30` confirmed |

**Requirements:**
1. **Provider enrollment** with CMS must be active before submitting checks.
2. **MBI required** — use the patient's Medicare Beneficiary Identifier as `memberId`.
3. **X-Forwarded-For header** — required since November 8, 2025. Include comma-separated upstream IP addresses.
4. **MBI lookup** — when patients don't know their MBI, perform a lookup first:
   - With SSN: submit to payer ID `CMS` with `subscriber.ssn` and `subscriber.address`.
   - Without SSN: submit to payer ID `MBILUNOSSN` with `subscriber.address.state`.

**Important distinctions:**
- `CMS` payer ID is for traditional/original Medicare (Parts A & B).
- Medicare Advantage plans (Part C) use the plan's own payer ID (e.g., UHC `87726`, Aetna `60054`, Humana `61101`).
- Medicare Part D (prescription) uses the Part D plan's payer ID.

---

## Humana

| Property | Value |
|---|---|
| Payer ID | `61101` |
| Enrollment required | Check payer |
| Supported STCs | `30` confirmed |

**Behaviors:**
- Standard response format.
- Also handles some Medicare Advantage plans.

---

## Kaiser Permanente

| Property | Value |
|---|---|
| Payer ID | Regional (Northern California has its own) |
| Enrollment required | Check payer |
| Supported STCs | `30` confirmed |

**Behaviors:**
- Kaiser operates as an integrated system (insurer + provider).
- Payer ID may vary by region (Northern CA, Southern CA, etc.).
- Standard response format.

---

## Medi-Cal / Medicaid

| Property | Value |
|---|---|
| Payer ID | `100065` (Medi-Cal) |
| Enrollment required | Varies by state |
| Supported STCs | Varies |

**Requirements:**
- **Portal credentials required:** Must include `portalUsername` and `portalPassword` in the request body. These are the provider's Medi-Cal/Medicaid portal login credentials.
- **Dependents usually not supported:** Most Medicaid plans don't support the `dependents` array. Sending it may cause errors or the payer may ignore it.
- **Alternative ID lookups:** Some Medicaid programs support SSN-based lookups instead of member ID.
- **ID card number:** Medicaid often uses `idCard` field in addition to or instead of `memberId`.
- **Medicaid recipient ID:** Use `medicaidRecipientIdentificationNumber` when the recipient ID differs from the member ID.

**Request with portal credentials:**
```json
{
  "tradingPartnerServiceId": "100065",
  "portalUsername": "<provider-portal-username>",
  "portalPassword": "<provider-portal-password>",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1234567893"
  },
  "subscriber": {
    "memberId": "<medicaid-id>",
    "firstName": "Jane",
    "lastName": "Doe",
    "dateOfBirth": "19900101"
  },
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

---

## MetLife

| Property | Value |
|---|---|
| Payer ID | Check Stedi payer list |
| Enrollment required | Check payer |
| Supported STCs | `35` (dental) confirmed |

**Behaviors:**
- Primarily a dental insurance provider.
- Standard response format.
- Mock request available for dental eligibility.

---

## Oscar Health

| Property | Value |
|---|---|
| Payer ID | `OSCAR` |
| Enrollment required | No (for eligibility) |
| Supported STCs | `30` confirmed |

**Behaviors:**
- Dependent information is returned in the `dependents` array (standard behavior).
- Relatively new to the Stedi network.

---

## UnitedHealthcare

| Property | Value |
|---|---|
| Payer ID | `87726` |
| Enrollment required | No (for eligibility) |
| Supported STCs | `30`, `35`, and many specialty codes |

**Behaviors:**
- Dependent information is returned in the `dependents` array.
- Supports both medical and dental eligibility.
- Provides both active and inactive coverage mock requests for testing.
- UMR (UHC's third-party administrator) uses payer ID `39026`.
- Some UHC Medicare Advantage plans may route through `87726` rather than `CMS`.

---

## Ameritas

| Property | Value |
|---|---|
| Payer ID | Check Stedi payer list |
| Enrollment required | Check payer |
| Supported STCs | `35` (dental) confirmed |

**Behaviors:**
- Primarily a dental insurance provider.
- Standard response format.
- Mock request available for dental eligibility.

---

## General best practices across all payers

1. **Name matching:** Enter names exactly as on the insurance card, including apostrophes, hyphens, and spaces.
2. **Member ID format:** Include the full ID as printed on the card. Some payers use prefixes or suffixes.
3. **Date of birth:** Always include when available. Many payers require it.
4. **One STC per request:** Unless you've confirmed the payer supports multiple.
5. **Don't re-check same day:** Many payers throttle repeated lookups for the same patient.
6. **Test before production:** Use mock requests with a test API key before going live.
7. **Handle non-compliant values:** Payers sometimes return non-standard values. Don't break on unexpected codes.
