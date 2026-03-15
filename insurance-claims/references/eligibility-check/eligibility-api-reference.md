# Eligibility Check API Reference

Comprehensive reference for calling the Stedi Real-Time Eligibility Check (270/271) JSON API.

Source: [Stedi API Reference](https://www.stedi.com/docs/healthcare/api-reference/post-healthcare-eligibility)

## Table of Contents

- [Endpoint](#endpoint)
- [Authentication](#authentication)
- [Headers](#headers)
- [Request body](#request-body)
  - [provider (required)](#provider-required)
  - [subscriber (required)](#subscriber-required)
  - [dependents](#dependents)
  - [encounter](#encounter)
  - [tradingPartnerServiceId (required)](#tradingpartnerserviceid-required)
  - [Optional top-level fields](#optional-top-level-fields)
- [Response structure](#response-structure)
  - [Top-level response fields](#top-level-response-fields)
  - [benefitsInformation array](#benefitsinformation-array)
  - [planDateInformation](#plandateinformation)
  - [planInformation](#planinformation)
  - [subscriber response object](#subscriber-response-object)
  - [dependents response array](#dependents-response-array)
  - [payer response object](#payer-response-object)
  - [errors array](#errors-array)
- [Interpreting benefits data](#interpreting-benefits-data)
- [Error handling](#error-handling)
- [CMS-specific requirements](#cms-specific-requirements)

---

## Endpoint

```
POST https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/eligibility/v3
```

Content-Type: `application/json`

---

## Authentication

Include the Stedi API key in the `Authorization` header:

```
Authorization: <STEDI_API_KEY>
```

- **Production keys** submit real eligibility checks to payers. These are billed.
- **Test keys** (prefixed with `test_`) only accept the pre-defined mock request payloads. Free of charge.

---

## Headers

| Header | Required | Description |
|---|---|---|
| `Authorization` | Yes | Stedi API key |
| `Content-Type` | Yes | `application/json` |
| `X-Forwarded-For` | CMS only | Comma-separated list of upstream IP addresses from the request's point of origin. Required by CMS since November 8, 2025. |

---

## Request body

### provider (required)

The entity requesting the eligibility check (practitioner, medical group, hospital, etc.).

| Field | Type | Required | Description |
|---|---|---|---|
| `organizationName` | string (1-60) | Yes (if org) | Business name. Required if provider is not an individual. |
| `firstName` | string (1-35) | Yes (if individual) | Provider's first name. Required if provider is an individual. |
| `lastName` | string (1-60) | Yes (if individual) | Provider's last name. Required if provider is an individual. |
| `npi` | string (10 digits) | Recommended | National Provider Identifier. Required for all providers eligible for an NPI. Must pass check digit validation. |
| `taxId` | string (9 digits) | Rare | Federal Taxpayer ID (EIN). Only if payer requires it. |
| `address` | object | Rare | Only when payer requires location identification. Contains `address1`, `city`, `state`, `postalCode`. |
| `providerCode` | string | Rare | Provider's role code (e.g., `AD` Admitting, `AT` Attending, `RF` Referring). Only when payer requires. |
| `referenceIdentification` | string | Rare | Provider taxonomy code. Only when relevant to the inquiry. |
| `contractNumber` | string (1-50) | Rare | Contract number with payer. |
| `medicaidProviderNumber` | string (1-50) | Rare | Medicaid provider number. |
| `medicareProviderNumber` | string (1-50) | Rare | Medicare provider number. |
| `stateLicenceNumber` | string (1-50) | Rare | State license number (requires `informationReceiverAdditionalIdentifierState`). |
| `ssn` | string (9 digits) | Very rare | Provider SSN. Only for non-traditional providers without NPI. |

**Minimal provider example:**
```json
{
  "organizationName": "Ona Health Services",
  "npi": "1234567893"
}
```

### subscriber (required)

The primary policyholder OR a dependent with a unique member ID.

| Field | Type | Required | Description |
|---|---|---|---|
| `memberId` | string (2-80) | Recommended | Member ID from insurance card. Alphanumeric, hyphens, and spaces allowed. |
| `firstName` | string (1-35) | Recommended | Must match insurance card exactly, including apostrophes, hyphens, spaces. |
| `lastName` | string (1-60) | Recommended | Must match insurance card exactly. Do NOT include suffixes (use `suffix` field). |
| `dateOfBirth` | string | Recommended | Format: `YYYYMMDD`. Strongly recommended — many payers error without it. |
| `gender` | string | Optional | `M` or `F`. |
| `middleName` | string (1-25) | Optional | Middle name or initial. |
| `suffix` | string (1-10) | Optional | Name suffix (Jr., Sr., III). No professional titles. |
| `groupNumber` | string (1-50) | Optional | Group number from insurance card. |
| `ssn` | string (9 digits) | Rare | SSN. Some Medicaid programs accept as member lookup alternative. |
| `address` | object | Rare | Subscriber address. Required for MBI lookup. Contains `address1`, `city`, `state`, `postalCode`. |
| `idCard` | string (1-50) | Rare | ID card number when different from member ID (common in Medicaid). |
| `medicaidRecipientIdentificationNumber` | string (1-50) | Rare | Medicaid recipient ID when different from member ID. |
| `additionalIdentification` | object | Rare | Additional IDs: `patientAccountNumber`, `insurancePolicyNumber`, `planNumber`, etc. |

**Minimum required:** At least one of `memberId`, `dateOfBirth`, or `lastName`. When you provide all four of `memberId`, `dateOfBirth`, `firstName`, and `lastName`, payers are required to return a response.

**Minimal subscriber example:**
```json
{
  "memberId": "ABC123456",
  "firstName": "Jane",
  "lastName": "Doe",
  "dateOfBirth": "19900115"
}
```

### dependents

Use when the patient is a dependent on the subscriber's plan AND the payer cannot uniquely identify them outside the subscriber's policy.

- Only one dependent per eligibility check.
- If the dependent has their own unique member ID, put them in `subscriber` instead.
- Most Medicaid plans don't support dependents.
- Always include the dependent's date of birth when available.

| Field | Type | Required | Description |
|---|---|---|---|
| `firstName` | string (1-35) | Recommended | Dependent's first name. |
| `lastName` | string (1-60) | Recommended | Dependent's last name. |
| `dateOfBirth` | string | Strongly recommended | Format: `YYYYMMDD`. Many payers require this. |
| `gender` | string | Optional | `M` or `F`. |
| `individualRelationshipCode` | string | Optional | `01` Spouse, `19` Child, `34` Other Adult. |
| `middleName` | string (1-25) | Optional | Middle name or initial. |
| `suffix` | string (1-10) | Optional | Name suffix. |
| `groupNumber` | string (1-50) | Optional | Group number. |
| `ssn` | string (9 digits) | Rare | Dependent's SSN. |
| `address` | object | Rare | Dependent's address. |

**Dependent example:**
```json
{
  "dependents": [
    {
      "firstName": "Jordan",
      "lastName": "Doe",
      "dateOfBirth": "20100515",
      "individualRelationshipCode": "19"
    }
  ]
}
```

**Response behavior varies by payer:** Some return dependent info in the `dependents` array, others return it in the `subscriber` object. Always check both.

### encounter

Details about what eligibility/benefit information you're requesting.

| Field | Type | Required | Description |
|---|---|---|---|
| `serviceTypeCodes` | string[] (1-99) | Optional | Service type codes. Defaults to `["30"]` (general plan coverage). |
| `dateOfService` | string | Optional | Single date `YYYYMMDD`. Payer defaults to current date if omitted. |
| `beginningDateOfService` | string | Optional | Start of date range (requires `endDateOfService`). |
| `endDateOfService` | string | Optional | End of date range (requires `beginningDateOfService`). |
| `procedureCode` | string (1-48) | Optional | Specific procedure code. |
| `productOrServiceIDQualifier` | string | With procedureCode | `AD` ADA, `CJ` CPT, `HC` HCPCS, `ID` ICD-9-CM, `IV` HIEC, `N4` NDC, `ZZ` Mutually Defined. |
| `procedureModifiers` | string[] (1-4) | Optional | Procedure modifiers. |
| `industryCode` | string | Optional | Place of service code (e.g., `11` Office, `22` Outpatient Hospital). |
| `priorAuthorizationOrReferralNumber` | string | Optional | Prior auth or referral number. |
| `referenceIdentificationQualifier` | string | With prior auth | `9F` Referral Number, `G1` Prior Auth Number. |
| `medicalProcedures` | object[] (1-98) | Rare | Multiple procedure codes in one request. |

**Common service type codes:**

| Code | Description | Use case |
|---|---|---|
| `30` | Health Benefit Plan Coverage | Default; general coverage check |
| `MH` | Mental Health | Therapy, psychiatry visits |
| `UC` | Urgent Care | Urgent care visits |
| `98` | Professional (Physician) Visit | Office visits |
| `86` | Emergency Services | ER visits |
| `35` | Dental Care | Dental services |
| `47` | Hospital | Hospital services |
| `88` | Pharmacy | Prescription drug coverage |
| `AL` | Vision (Optometry) | Eye care |
| `1` | Medical Care | General medical |
| `2` | Surgical | Surgical procedures |
| `4` | Diagnostic X-Ray | Imaging |
| `5` | Diagnostic Lab | Lab work |
| `7` | Anesthesia | Anesthesia services |
| `A4` | Psychiatric | Psychiatric care |
| `A6` | Psychotherapy | Psychotherapy sessions |
| `A7` | Psychiatric - Inpatient | Inpatient psych |
| `A8` | Psychiatric - Outpatient | Outpatient psych |

**Recommendations:**
- One STC per request unless the payer is confirmed to support multiple.
- When checking for today, omit `dateOfService` for consistent behavior.
- Dates up to 12 months past or end of current month are safe. Some payers (like CMS) support further future dates.

### tradingPartnerServiceId (required)

The payer ID. Use the primary payer ID, Stedi payer ID, or any alias.

See `references/stedi-eligibility.md` for common payer IDs. Full list via:
```
GET https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/payers
```

### Optional top-level fields

| Field | Type | Description |
|---|---|---|
| `externalPatientId` | string (max 36) | Unique patient ID for correlating historical checks. Recommended in all requests. |
| `portalUsername` | string (1-50) | Provider's login username for payer portal. Required by some payers (e.g., Medi-Cal). |
| `portalPassword` | string (1-50) | Provider's login password for payer portal. Required by some payers (e.g., Medi-Cal). |
| `tradingPartnerName` | string (1-60) | Payer name (e.g., "Cigna"). Informational. |

---

## Response structure

### Top-level response fields

| Field | Description |
|---|---|
| `id` | Globally unique ID: `ec_<uuid>`. Use for tracking and portal deep links. |
| `controlNumber` | Payer's response identifier. |
| `tradingPartnerServiceId` | Payer ID (may differ from request — reflects payer's internal ID). |
| `benefitsInformation` | Array of benefit objects (primary data). |
| `planDateInformation` | Dates for the subscriber/dependent's plan. |
| `planInformation` | Plan identification details (group number, plan number, etc.). |
| `subscriber` | Subscriber information from payer. |
| `dependents` | Dependent information (if applicable). |
| `payer` | Payer details and contact info. |
| `provider` | Provider info echoed from request. |
| `errors` | Centralized array of all AAA errors from any level. |
| `warnings` | Non-fatal issues with the check. |
| `meta` | Metadata (trace IDs, application mode). |
| `x12` | Raw X12 EDI 271 response (or 999 acknowledgment on validation error). |

### benefitsInformation array

Each object represents a specific benefit detail. Key fields:

| Field | Description |
|---|---|
| `code` | Benefit type code (see table below). |
| `name` | Full name of the benefit code. |
| `serviceTypeCodes` | STCs this benefit applies to. |
| `serviceTypes` | Human-readable STC names. |
| `coverageLevelCode` | `IND` Individual, `FAM` Family, `EMP` Employee Only, etc. |
| `coverageLevel` | Full name of coverage level. |
| `inPlanNetworkIndicatorCode` | `Y` In-network, `N` Out-of-network, `U` Unknown, `W` Not Applicable (applies to both). |
| `inPlanNetworkIndicator` | Full name of network indicator. |
| `benefitAmount` | Dollar amount (decimal string, e.g., `"250.00"`). |
| `benefitPercent` | Percentage (decimal, e.g., `"0.20"` = 20%). |
| `benefitQuantity` | Quantity (e.g., number of visits). |
| `quantityQualifier` | What the quantity measures. |
| `timeQualifierCode` | Period: `23` Calendar Year, `24` Plan Year, `25` Contract, `27` Visit, `29` Remaining, `26` Episode. |
| `timeQualifier` | Full name of time qualifier. |
| `authOrCertIndicator` | Prior auth required: `Y` Yes, `N` No, `U` Unknown. |
| `planCoverage` | Plan name (e.g., "Gold 1-2-3"). |
| `insuranceTypeCode` | Insurance type code. |
| `additionalInformation` | Array of `{description}` free-text messages. |
| `benefitsDateInformation` | Benefit-specific dates (override `planDateInformation`). |
| `benefitsRelatedEntities` | Related entities (PCP, other orgs, crossover carrier). |
| `compositeMedicalProcedureIdentifier` | Procedure codes relevant to this benefit. |
| `eligibilityAdditionalInformationList` | Place of service, nature of injury codes. |
| `benefitsServiceDelivery` | Delivery patterns (frequency, quantity limits). |

**Benefit code reference:**

| Code | Name | Key field | Interpretation |
|---|---|---|---|
| `1` | Active Coverage | — | Patient has active coverage for these STCs. |
| `6` | Inactive | — | Coverage is NOT active. |
| `I` | Non-Covered | — | Service is excluded from plan. |
| `C` | Deductible | `benefitAmount` | Dollar deductible. `timeQualifierCode` 23=total, 29=remaining. |
| `G` | Out of Pocket (Stop Loss) | `benefitAmount` | OOP max. Same time qualifier logic. |
| `B` | Co-Payment | `benefitAmount` | Copay amount per visit/service. |
| `A` | Co-Insurance | `benefitPercent` | Patient's percentage responsibility (0.20 = 20%). |
| `F` | Limitations | — | Benefit has limitations (check `additionalInformation`). |
| `CB` | Coverage Basis | — | Coverage policy details. |
| `D` | Benefit Description | — | Descriptive info about the benefit. |
| `J` | Cost Containment | `benefitAmount` | Cost containment amount. |
| `Y` | Spend Down | `benefitAmount` | Medicaid spend-down amount. |
| `R` | Other or Additional Payor | — | Coordination of benefits info. |

### planDateInformation

Dates for the overall plan. These apply to all benefits unless overridden by `benefitsDateInformation`.

| Field | Description |
|---|---|
| `planBegin` | Plan coverage start date. |
| `planEnd` | Plan coverage end date. |
| `eligibilityBegin` | Date patient first eligible. |
| `eligibilityEnd` | Date patient no longer eligible. |
| `plan` | Plan effective dates (single date or range). |
| `eligibility` | Eligibility dates (single or range). |
| `enrollment` | Enrollment date. |
| `policyEffective` | Policy effective date. |
| `policyExpiration` | Policy expiration date. |
| `dateOfLastUpdate` | Last plan info update. |
| `service` | Service dates. |
| `admission` | Admission dates. |
| `cobraBegin` / `cobraEnd` | COBRA coverage period. |
| `dateOfDeath` | Returned for deceased subscribers/dependents. |

**Date format:** `YYYYMMDD` for single dates, `YYYYMMDD-YYYYMMDD` for ranges.

### planInformation

Additional plan identification:

| Field | Description |
|---|---|
| `groupNumber` | Insurance group number. |
| `groupDescription` | Group name. |
| `planNumber` | Plan number. |
| `planDescription` | Plan name. |
| `policyNumber` | Policy number. |
| `memberId` | Member ID (Workers' Comp / P&C only). |
| `hicNumber` | Health insurance claim number (may contain MBI for Medicare/Medicaid crossover). |
| `medicaidRecipientIdNumber` | Medicaid recipient ID. |
| `priorAuthorizationNumber` | Prior auth number. |
| `referralNumber` | Referral number. |
| `socialSecurityNumber` | SSN. |

### subscriber response object

Always includes at least name or member ID:

| Field | Description |
|---|---|
| `firstName`, `lastName`, `middleName`, `suffix` | Name fields. |
| `dateOfBirth` | DOB in `YYYYMMDD`. |
| `gender` | `M`, `F`, or `U`. |
| `memberId` | Member ID. |
| `groupNumber` | Group number. |
| `address` | Address object. |
| `entityIdentifier` | Always `"Insured or Subscriber"`. |
| `relationToSubscriber` | Always `"Self"`. |
| `aaaErrors` | Array of rejection errors at subscriber level. |

### dependents response array

When the patient is a dependent, contains a single object with:

| Field | Description |
|---|---|
| `firstName`, `lastName`, `middleName`, `suffix` | Name fields. |
| `dateOfBirth` | DOB. |
| `gender` | Gender code. |
| `relationToSubscriber` | `Spouse`, `Child`, `Employee`, `Unknown`, etc. |
| `relationToSubscriberCode` | `01` Spouse, `19` Child, `20` Employee, etc. |
| `aaaErrors` | Rejection errors at dependent level. |

### payer response object

| Field | Description |
|---|---|
| `name` | Payer business name. |
| `entityIdentifier` | `Payer`, `Third-Party Administrator`, etc. |
| `federalTaxpayersIdNumber` | Payer's EIN. |
| `npi` | Payer NPI (if applicable). |
| `contactInformation` | Contains `contacts` array with phone, fax, email, URL. |
| `aaaErrors` | Rejection errors at payer level. |

### errors array

Centralized collection of ALL AAA errors from payer, provider, subscriber, and dependent levels. Each error:

| Field | Description |
|---|---|
| `code` | AAA error code (e.g., `42`, `72`). |
| `description` | Error description. |
| `followupAction` | Recommended action (e.g., `"Please Correct and Resubmit"`). |
| `possibleResolutions` | Stedi-provided resolution guidance. |
| `location` | Location in X12 EDI response. |

---

## Interpreting benefits data

### Step 1: Check for errors

```
response.errors.length > 0  →  Check error codes and resolve
```

### Step 2: Confirm active coverage

Look for `benefitsInformation` objects where `code` is `1` (Active Coverage):

```json
{
  "code": "1",
  "name": "Active Coverage",
  "serviceTypeCodes": ["30"],
  "planCoverage": "Open Access Plus"
}
```

If `code` is `6` (Inactive), the patient does not have active coverage.

### Step 3: Extract financial details

Filter `benefitsInformation` by `inPlanNetworkIndicatorCode: "Y"` for in-network amounts:

- **Deductible** (`code: "C"`): `benefitAmount` with `timeQualifierCode` 23 (total) or 29 (remaining).
- **Out-of-pocket max** (`code: "G"`): same pattern.
- **Copay** (`code: "B"`): `benefitAmount` per visit.
- **Coinsurance** (`code: "A"`): `benefitPercent` (0.10 = patient pays 10%).

### Step 4: Check prior authorization

`authOrCertIndicator: "Y"` means prior auth is required. `"U"` means unknown — check `additionalInformation` and contact payer.

### Step 5: Verify plan dates

Check `planDateInformation.planEnd` or `planDateInformation.eligibilityEnd` against the service date. If the service date is after the earliest ending date, coverage may have lapsed.

---

## Error handling

See `references/eligibility-check/mock-requests-errors.md` for detailed AAA error reference.

**Quick reference:**

| Code | Meaning | Action |
|---|---|---|
| `42` | Payer temporarily unavailable | Retry in a few minutes |
| `43` | Provider NPI not registered with payer | Enroll NPI with payer |
| `72` | Invalid/missing subscriber ID | Verify member ID from card |
| `73` | Invalid/missing subscriber name | Check spelling vs. card |
| `75` | Subscriber not found | Try different field combos |
| `79` | Invalid participant identification | Contact Stedi support |

---

## CMS-specific requirements

Medicare eligibility checks to `CMS` payer ID require:

1. **X-Forwarded-For header** with upstream IP addresses.
2. **MBI as memberId** (Medicare Beneficiary Identifier).
3. **Provider enrollment** with CMS — can take hours to activate.

For patients who don't know their MBI, use the MBI lookup endpoint. See `references/eligibility-check/mock-requests-medical.md` for MBI lookup mock request details.

For Medicare Advantage plans, use the plan's actual payer ID (e.g., UnitedHealthcare `87726`), not `CMS`.
