# Medical Eligibility Mock Requests

Mock requests for testing medical eligibility checks (270/271) with the Stedi API.

All mock requests go to:
```
POST https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/eligibility/v3
```

**Requirements:**
- Use a **test** API key (prefixed with `test_`).
- `provider`: Any organization name + any valid NPI (must pass check digit validation). Example NPI: `1999999984`.
- `encounter`: Only service type code `30` is supported for medical mock requests.
- `subscriber`: Must use the exact values specified for each payer. Any deviation returns errors.

Source: [Stedi Mock Requests](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks)

## Table of Contents

- [Subscriber-only requests](#subscriber-only-requests)
  - [Aetna](#aetna-subscriber)
  - [Ambetter](#ambetter-subscriber)
  - [Cigna (7 variants)](#cigna-subscriber)
  - [Humana](#humana-subscriber)
  - [Kaiser Permanente](#kaiser-permanente-subscriber)
  - [CMS (Medicare)](#cms-medicare-subscriber)
  - [UnitedHealthcare](#unitedhealthcare-subscriber)
- [Dependent requests](#dependent-requests)
  - [Aetna](#aetna-dependent)
  - [Anthem BCBS CA](#anthem-bcbs-ca-dependent)
  - [BCBS Texas](#bcbs-texas-dependent)
  - [Cigna](#cigna-dependent)
  - [Oscar Health](#oscar-health-dependent)
  - [UnitedHealthcare](#unitedhealthcare-dependent)
- [MBI lookup for CMS](#mbi-lookup-for-cms)
- [Inactive coverage](#inactive-coverage)

---

## Subscriber-only requests

These request benefits for the subscriber only. The subscriber's information goes in the `subscriber` object; no `dependents` array.

### Aetna (subscriber)

**Payer ID:** `60054`

```json
{
  "tradingPartnerServiceId": "60054",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "memberId": "AETNA12345",
    "firstName": "Jane",
    "lastName": "Doe",
    "dateOfBirth": "20040404"
  },
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

**Notes:**
- Aetna is one of the most commonly used payers for testing.
- Response includes plan name, deductible, OOP max, copay, and coinsurance details.

### Ambetter (subscriber)

**Payer ID:** `AMB01`

Ambetter mock requests use a specific test subscriber. Get the exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand the "Ambetter - Mock request 1" section.

**Structure:**
```json
{
  "tradingPartnerServiceId": "AMB01",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "memberId": "<exact-test-value>",
    "firstName": "<exact-test-value>",
    "lastName": "<exact-test-value>",
    "dateOfBirth": "<exact-test-value>"
  },
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

### Cigna (subscriber)

**Payer ID:** `62308`

Cigna provides 7 different mock request variants, each testing different subscriber scenarios. Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks).

**Structure (all 7 variants):**
```json
{
  "tradingPartnerServiceId": "62308",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "memberId": "<variant-specific-value>",
    "firstName": "<variant-specific-value>",
    "lastName": "<variant-specific-value>",
    "dateOfBirth": "<variant-specific-value>"
  },
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

**Variant notes:**
- Mock requests 1-7 each use different subscriber data to test various response shapes.
- This is useful for testing how your parser handles diverse Cigna response formats.

### Humana (subscriber)

**Payer ID:** `61101`

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "Humana - Mock request 1".

**Structure:**
```json
{
  "tradingPartnerServiceId": "61101",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "memberId": "<exact-test-value>",
    "firstName": "<exact-test-value>",
    "lastName": "<exact-test-value>",
    "dateOfBirth": "<exact-test-value>"
  },
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

### Kaiser Permanente (subscriber)

**Payer ID:** Kaiser Permanente Northern California

Get exact payer ID and test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "Kaiser Permanente - Mock request 1".

**Structure:**
```json
{
  "tradingPartnerServiceId": "<kaiser-payer-id>",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "memberId": "<exact-test-value>",
    "firstName": "<exact-test-value>",
    "lastName": "<exact-test-value>",
    "dateOfBirth": "<exact-test-value>"
  },
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

### CMS / Medicare (subscriber)

**Payer ID:** `CMS`

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "CMS - Mock request 1".

**Structure:**
```json
{
  "tradingPartnerServiceId": "CMS",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "memberId": "<MBI-value>",
    "firstName": "<exact-test-value>",
    "lastName": "<exact-test-value>",
    "dateOfBirth": "<exact-test-value>"
  },
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

**CMS-specific requirements (production):**
- `memberId` must be the patient's Medicare Beneficiary Identifier (MBI).
- Include `X-Forwarded-For` header with upstream IP addresses.
- Provider must be enrolled with CMS.
- For Medicare Advantage plans, use the plan's actual payer ID, not `CMS`.

### UnitedHealthcare (subscriber)

**Payer ID:** `87726`

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "UHC - Mock request 1".

**Structure:**
```json
{
  "tradingPartnerServiceId": "87726",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "memberId": "<exact-test-value>",
    "firstName": "<exact-test-value>",
    "lastName": "<exact-test-value>",
    "dateOfBirth": "<exact-test-value>"
  },
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

---

## Dependent requests

These check eligibility for a dependent on the subscriber's plan. The subscriber info goes in `subscriber`, the dependent info goes in the `dependents` array.

**General guidance:**
- Always include the dependent's `dateOfBirth` in the request.
- If the dependent has their own unique member ID, put them in `subscriber` instead and leave `dependents` empty.
- Response format varies by payer — some return dependent info in `dependents`, others in `subscriber`.

### Aetna (dependent)

**Payer ID:** `60054`

Dependent Jordan is subscriber John's **child**. Jordan's information is returned in the `dependents` array in the response.

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "Aetna - Mock request 1" under Dependent.

**Structure:**
```json
{
  "tradingPartnerServiceId": "60054",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "memberId": "<subscriber-member-id>",
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": "<subscriber-dob>"
  },
  "dependents": [
    {
      "firstName": "Jordan",
      "lastName": "Doe",
      "dateOfBirth": "<dependent-dob>",
      "individualRelationshipCode": "19"
    }
  ],
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

### Anthem BCBS CA (dependent)

**Payer ID:** `040`

Dependent John is subscriber Jane's **spouse**. John's information is returned in the `dependents` array.

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "Anthem BCBSCA - Mock request 1".

**Structure:**
```json
{
  "tradingPartnerServiceId": "040",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "memberId": "<subscriber-member-id>",
    "firstName": "Jane",
    "lastName": "Doe",
    "dateOfBirth": "<subscriber-dob>"
  },
  "dependents": [
    {
      "firstName": "John",
      "lastName": "Doe",
      "dateOfBirth": "<dependent-dob>",
      "individualRelationshipCode": "01"
    }
  ],
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

### BCBS Texas (dependent)

**Payer ID:** `84980`

Dependent Jane is subscriber John's **child**. Jane's information is returned in the `dependents` array.

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "BCBSTX - Mock request 1".

**Structure:**
```json
{
  "tradingPartnerServiceId": "84980",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "memberId": "<subscriber-member-id>",
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": "<subscriber-dob>"
  },
  "dependents": [
    {
      "firstName": "Jane",
      "lastName": "Doe",
      "dateOfBirth": "<dependent-dob>",
      "individualRelationshipCode": "19"
    }
  ],
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

### Cigna (dependent)

**Payer ID:** `62308`

Dependent Jordan is the subscriber's **child**. **Important:** In the response, Jordan is returned in the `subscriber` object with no `dependents` array, even though they are a dependent. This is Cigna-specific behavior.

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "Cigna - Mock request 1" under Dependent.

**Structure:**
```json
{
  "tradingPartnerServiceId": "62308",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "memberId": "<subscriber-member-id>",
    "firstName": "<subscriber-first>",
    "lastName": "<subscriber-last>",
    "dateOfBirth": "<subscriber-dob>"
  },
  "dependents": [
    {
      "firstName": "Jordan",
      "lastName": "<dependent-last>",
      "dateOfBirth": "<dependent-dob>",
      "individualRelationshipCode": "19"
    }
  ],
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

**Cigna quirk:** Always check both `subscriber` and `dependents` in the response — Cigna may return the dependent's data in the `subscriber` object.

### Oscar Health (dependent)

**Payer ID:** `OSCAR`

Dependent Jane is subscriber John's **child**. Jane's information is returned in the `dependents` array.

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "Oscar Health - Mock request 1".

**Structure:**
```json
{
  "tradingPartnerServiceId": "OSCAR",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "memberId": "<subscriber-member-id>",
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": "<subscriber-dob>"
  },
  "dependents": [
    {
      "firstName": "Jane",
      "lastName": "Doe",
      "dateOfBirth": "<dependent-dob>",
      "individualRelationshipCode": "19"
    }
  ],
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

### UnitedHealthcare (dependent)

**Payer ID:** `87726`

Dependent Jane is subscriber John's **spouse**. Jane's information is returned in the `dependents` array.

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "UnitedHealthcare - Mock request 1" under Dependent.

**Structure:**
```json
{
  "tradingPartnerServiceId": "87726",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "memberId": "<subscriber-member-id>",
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": "<subscriber-dob>"
  },
  "dependents": [
    {
      "firstName": "Jane",
      "lastName": "Doe",
      "dateOfBirth": "<dependent-dob>",
      "individualRelationshipCode": "01"
    }
  ],
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

---

## MBI lookup for CMS

For Medicare eligibility checks, the patient's MBI is required. When patients don't know their MBI, perform an MBI lookup first.

**Method:** Submit an eligibility check to payer ID `CMS` with the patient's SSN instead of MBI.

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "MBI lookup mock request".

**Structure:**
```json
{
  "tradingPartnerServiceId": "CMS",
  "provider": {
    "organizationName": "Provider Name",
    "npi": "1999999984"
  },
  "subscriber": {
    "firstName": "<exact-test-value>",
    "lastName": "<exact-test-value>",
    "dateOfBirth": "<exact-test-value>",
    "ssn": "<exact-test-value>",
    "address": {
      "address1": "<exact-test-value>",
      "city": "<exact-test-value>",
      "state": "<exact-test-value>",
      "postalCode": "<exact-test-value>"
    }
  },
  "encounter": {
    "serviceTypeCodes": ["30"]
  }
}
```

**MBI lookup notes:**
- SSN-based lookup requires `subscriber.address` with at least `address1` and `city`.
- MBI lookup without SSN (payer ID `MBILUNOSSN`) only requires `state` in the address.
- The response will contain the MBI in the subscriber's member ID or in `planInformation.hicNumber`.
- After obtaining the MBI, submit a regular eligibility check to `CMS` with the MBI as `memberId`.

---

## Inactive coverage

### UnitedHealthcare (inactive)

**Payer ID:** `87726`

This mock request returns an inactive coverage response, useful for testing how your system handles patients whose coverage has lapsed.

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "UHC - Mock request 1" under Medical - Inactive coverage.

**Structure:** Same as UHC subscriber-only, but with different subscriber data that triggers an inactive response.

**Expected response:** `benefitsInformation` will contain `code: "6"` (Inactive) instead of `code: "1"` (Active Coverage).
