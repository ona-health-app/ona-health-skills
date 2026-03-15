# Dental Eligibility Mock Requests

Mock requests for testing dental eligibility checks (270/271) with the Stedi API.

Endpoint:
```
POST https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/eligibility/v3
```

**Requirements:**
- Use a **test** API key (prefixed with `test_`).
- `provider`: Any organization name + any valid NPI. Example: `1999999984`.
- `encounter`: Only service type code `35` (Dental Care) is supported for dental mock requests.
- `subscriber`: Must use exact values specified for each payer.

Source: [Stedi Mock Requests](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks)

---

## Dental vs Medical differences

| Aspect | Medical | Dental |
|---|---|---|
| Service type code | `30` (Plan coverage) | `35` (Dental care) |
| Procedure code qualifier | `HC` (HCPCS) or `CJ` (CPT) | `AD` (ADA codes) |
| Common payers | Aetna, Cigna, UHC, etc. | Ameritas, MetLife, Delta Dental, etc. |
| Response structure | Same `benefitsInformation` array | Same structure, dental-specific STCs |

---

## Payer mock requests

### Ameritas

**Payer ID:** Check [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "Ameritas - Mock request".

```json
{
  "tradingPartnerServiceId": "<ameritas-payer-id>",
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
    "serviceTypeCodes": ["35"]
  }
}
```

### Anthem Blue Cross Blue Shield of CA

**Payer ID:** `040`

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "BCBSCA - Mock request" under Dental.

```json
{
  "tradingPartnerServiceId": "040",
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
    "serviceTypeCodes": ["35"]
  }
}
```

### Cigna

**Payer ID:** `62308`

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "Cigna - Mock request" under Dental.

```json
{
  "tradingPartnerServiceId": "62308",
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
    "serviceTypeCodes": ["35"]
  }
}
```

### MetLife

**Payer ID:** Check [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "Metlife - Mock request".

```json
{
  "tradingPartnerServiceId": "<metlife-payer-id>",
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
    "serviceTypeCodes": ["35"]
  }
}
```

### UnitedHealthcare

**Payer ID:** `87726`

Get exact test values from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "UnitedHealthcare - Mock request" under Dental.

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
    "serviceTypeCodes": ["35"]
  }
}
```

---

## Interpreting dental responses

Dental responses use the same `benefitsInformation` structure as medical. Key differences:

- **Service type codes** in responses may include `35` (Dental Care) plus more specific dental STCs.
- **Annual maximums** are common — look for `benefitsInformation` with `code: "F"` (Limitations) or `code: "G"` (Out of Pocket).
- **Frequency limitations** for cleanings, X-rays, etc. appear in `benefitsServiceDelivery`.
- **Waiting periods** may appear in `benefitsDateInformation`.
- **Deductibles** are typically lower than medical (often $50-$150 individual).

### Common dental service type codes in responses

| Code | Description |
|---|---|
| `35` | Dental Care |
| `36` | Dental Crowns |
| `37` | Dental Accident |
| `38` | Orthodontics |
| `39` | Prosthodontics |
| `40` | Oral Surgery |
| `41` | Routine (Preventive) Dental |
| `42` | Non-Routine Dental |

### Checking dental procedure-specific benefits

For procedure-specific checks (production only), use `encounter.procedureCode` with `productOrServiceIDQualifier: "AD"` (American Dental Association codes):

```json
{
  "encounter": {
    "procedureCode": "D0120",
    "productOrServiceIDQualifier": "AD"
  }
}
```

Common ADA codes:
- `D0120` — Periodic oral evaluation
- `D0150` — Comprehensive oral evaluation
- `D0210` — Full mouth X-rays
- `D0274` — Bitewing X-rays
- `D1110` — Prophylaxis (adult cleaning)
- `D2740` — Crown (porcelain/ceramic)
- `D8080` — Comprehensive orthodontic treatment
