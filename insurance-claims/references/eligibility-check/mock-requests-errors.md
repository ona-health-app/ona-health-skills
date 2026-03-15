# AAA Error Mock Requests & Troubleshooting

Mock requests that return common AAA (Application Advice/Acknowledgment) errors for testing error handling in eligibility checks.

Endpoint:
```
POST https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/eligibility/v3
```

Use a **test** API key. Get exact payloads from the [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks).

Source: [Stedi Eligibility Troubleshooting](https://www.stedi.com/docs/healthcare/eligibility-troubleshooting)

---

## Quick reference

| AAA Code | Name | Severity | Typical cause |
|---|---|---|---|
| `42` | Unable to Respond at Current Time | Transient | Payer system down or throttling |
| `43` | Invalid/Missing Provider Identification | Fixable | NPI not registered with payer |
| `72` | Invalid/Missing Subscriber/Insured ID | Fixable | Wrong member ID |
| `73` | Invalid/Missing Subscriber/Insured Name | Fixable | Name mismatch |
| `75` | Subscriber/Insured Not Found | Fixable | Patient not in payer database |
| `79` | Invalid Participant Identification | Escalate | Connection problem with payer |

---

## Error 42 — Unable to Respond at Current Time

**What it means:** The payer's system is temporarily unavailable. This could be a brief outage, extended maintenance, or the payer throttling your requests.

**Mock request:** Get exact payload from [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "42 - AAA Error - Mock request".

**Response pattern:**
```json
{
  "errors": [
    {
      "code": "42",
      "description": "Unable to Respond at Current Time",
      "followupAction": "Please Wait 30 Days and Resubmit",
      "possibleResolutions": "..."
    }
  ]
}
```

**Resolution steps:**
1. Wait 5-15 minutes and retry.
2. If persistent, check [Stedi status page](https://status.stedi.com/) for payer outages.
3. If it continues beyond 30 minutes, try the request through a different channel or contact the payer directly.
4. Do NOT retry aggressively — payers may throttle you further.

---

## Error 43 — Invalid/Missing Provider Identification

**What it means:** The provider's NPI is not registered with the payer, is not registered correctly, or the payer requires a specific agreement or enrollment.

**Mock request:** Get exact payload from [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "43 - AAA Error - Mock request".

**Response pattern:**
```json
{
  "errors": [
    {
      "code": "43",
      "description": "Invalid/Missing Provider Identification",
      "followupAction": "Please Correct and Resubmit",
      "possibleResolutions": "..."
    }
  ]
}
```

**Resolution steps:**
1. Verify the NPI is correct and passes check digit validation.
2. Check if the provider is enrolled/registered with this specific payer.
3. Some payers require enrollment before eligibility checks (e.g., CMS).
4. Verify the NPI is for the correct provider type (individual vs. organization).
5. If using an organization NPI, ensure `organizationName` matches the NPI registry.
6. If the provider recently got their NPI, it may take time to propagate to payer systems.

---

## Error 72 — Invalid/Missing Subscriber/Insured ID

**What it means:** The member ID in the request doesn't match payer records, doesn't meet the payer's format requirements, or there's another unidentified error in the request data.

**Mock request:** Get exact payload from [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "72 - AAA Error - Mock request".

**Response pattern:**
```json
{
  "errors": [
    {
      "code": "72",
      "description": "Invalid/Missing Subscriber/Insured ID",
      "followupAction": "Please Correct and Resubmit",
      "possibleResolutions": "..."
    }
  ]
}
```

**Resolution steps:**
1. Verify the member ID against the patient's insurance card exactly as printed.
2. Check for leading zeros, suffixes (01, 02), or formatting differences.
3. Some payers require the full ID including prefix/suffix; others require just the base number.
4. Try with and without the member ID suffix.
5. If the patient has multiple insurance cards, try the most recent one.
6. Verify `tradingPartnerServiceId` matches the correct payer for this insurance plan.

---

## Error 73 — Invalid/Missing Subscriber/Insured Name

**What it means:** The subscriber name submitted doesn't match payer records. Could be misspelled, missing, formatted incorrectly, or doesn't meet the payer's requirements.

**Mock request:** Get exact payload from [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "73 - AAA Error - Mock request".

**Response pattern:**
```json
{
  "errors": [
    {
      "code": "73",
      "description": "Invalid/Missing Subscriber/Insured Name",
      "followupAction": "Please Correct and Resubmit",
      "possibleResolutions": "..."
    }
  ]
}
```

**Resolution steps:**
1. Enter the name exactly as on the insurance card (including hyphens, apostrophes, spaces).
2. Check for common issues: maiden name vs. married name, legal name vs. preferred name.
3. Try the name without suffixes (Jr., III) — use the `suffix` field separately.
4. Verify first and last names aren't swapped.
5. Try with just `lastName` and `dateOfBirth` if the first name is causing issues.
6. Some payers are sensitive to middle names — try with and without `middleName`.

---

## Error 75 — Subscriber/Insured Not Found

**What it means:** The payer cannot find the subscriber in their database using the combination of fields you provided.

**Mock request:** Get exact payload from [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "75 - AAA Error - Mock request".

**Response pattern:**
```json
{
  "errors": [
    {
      "code": "75",
      "description": "Subscriber/Insured Not Found",
      "followupAction": "Please Correct and Resubmit",
      "possibleResolutions": "..."
    }
  ]
}
```

**Resolution steps:**
1. Try different combinations of search fields:
   - `memberId` + `dateOfBirth`
   - `memberId` + `lastName`
   - `firstName` + `lastName` + `dateOfBirth`
   - `memberId` + `firstName` + `lastName` + `dateOfBirth` (all four)
2. Verify the patient's coverage hasn't been terminated.
3. Check if the patient recently switched plans — they may have a new member ID.
4. Verify you're using the correct payer ID for the patient's specific plan.
5. For BCBS plans, verify you're using the correct state-specific BCBS payer ID.
6. The patient may be listed under a different subscriber (spouse/parent) — try as a dependent.

---

## Error 79 — Invalid Participant Identification

**What it means:** There's a connectivity or routing problem between Stedi and the payer. This is not typically something you can fix on your end.

**Mock request:** Get exact payload from [Stedi mock requests page](https://www.stedi.com/docs/healthcare/api-reference/mock-requests-eligibility-checks) — expand "79 - AAA Error - Mock request".

**Response pattern:**
```json
{
  "errors": [
    {
      "code": "79",
      "description": "Invalid Participant Identification",
      "followupAction": "Do Not Resubmit; Inquiry Initiated to a Third Party",
      "possibleResolutions": "..."
    }
  ]
}
```

**Resolution steps:**
1. Contact Stedi support — this is typically a payer connection issue.
2. Check the [Stedi status page](https://status.stedi.com/) for known issues.
3. Do NOT keep retrying — the error may indicate a routing misconfiguration.

---

## Complete AAA error code reference

Beyond the common errors above, the full list of possible AAA codes:

| Code | Description |
|---|---|
| `04` | Authorized Quantity Exceeded |
| `15` | Required Application Data Missing |
| `33` | Input Errors |
| `35` | Out of Network |
| `41` | Authorization/Access Restrictions |
| `42` | Unable to Respond at Current Time |
| `43` | Invalid/Missing Provider Identification |
| `44` | Invalid/Missing Provider Name |
| `45` | Invalid/Missing Provider Specialty |
| `46` | Invalid/Missing Provider Phone Number |
| `47` | Invalid/Missing Provider State |
| `48` | Invalid/Missing Referring Provider ID Number |
| `49` | Provider is Not Primary Care Physician |
| `50` | Provider Ineligible for Inquiries |
| `51` | Provider Not on File |
| `52` | Service Dates Not Within Provider Plan Enrollment |
| `53` | Inquired Benefit Inconsistent with Provider Type |
| `54` | Inappropriate Product/Service ID Qualifier |
| `55` | Inappropriate Product/Service ID |
| `56` | Inappropriate Date |
| `57` | Invalid/Missing Date(s) of Service |
| `58` | Invalid/Missing Date-of-Birth |
| `60` | Date of Birth Follows Date(s) of Service |
| `61` | Date of Death Precedes Date(s) of Service |
| `62` | Date of Service Not Within Allowable Inquiry Period |
| `63` | Date of Service in Future |
| `69` | Inconsistent with Patient's Age |
| `70` | Patient Gender Mismatch |
| `71` | Patient Birth Date Does Not Match That for the Patient on the Database |
| `72` | Invalid/Missing Subscriber/Insured ID |
| `73` | Invalid/Missing Subscriber/Insured Name |
| `74` | Invalid/Missing Subscriber/Insured Gender Code |
| `75` | Subscriber/Insured Not Found |
| `76` | Duplicate Subscriber/Insured ID Number |
| `78` | Subscriber/Insured Not in Group/Plan Identified |
| `79` | Invalid Participant Identification |
| `80` | No Response received - Transaction Terminated |
| `97` | Invalid or Missing Provider Address |
| `98` | Experimental Service or Procedure |
| `AA` | Authorization Number Not Found |
| `AE` | Not available at this time |
| `AF` | Invalid/Missing Diagnosis Code(s) |
| `AG` | Invalid/Missing Procedure Code(s) |
| `AO` | Additional Patient Info Required |
| `CI` | Certification Information Does Not Match Patient |
| `MA` | Certification Expired |
| `T4` | Payer Name or Payer Identifier Missing |

---

## Follow-up action codes

Each AAA error includes a `followupAction` indicating what you can do:

| Action | Meaning |
|---|---|
| `Please Correct and Resubmit` | Fix the identified issue and try again. |
| `Resubmission Allowed` | You may resubmit as-is (e.g., after a payer outage). |
| `Resubmission Not Allowed` | Do not resubmit — contact the payer. |
| `Do Not Resubmit; Inquiry Initiated to a Third Party` | Stedi or the payer is investigating. |
| `Please Wait 30 Days and Resubmit` | Temporary issue — wait and retry. |
| `Please Resubmit Original Transaction` | Resubmit the same request. |

---

## Programmatic error handling pattern

```python
def handle_eligibility_response(response):
    errors = response.get("errors", [])
    if not errors:
        return parse_benefits(response)

    for error in errors:
        code = error.get("code")
        if code == "42":
            # Transient — schedule retry
            return {"retry": True, "wait_minutes": 5}
        elif code in ("72", "73", "75"):
            # Data quality — needs correction
            return {"retry": False, "fix_required": True, "error": error}
        elif code == "43":
            # Provider registration issue
            return {"retry": False, "enrollment_required": True, "error": error}
        elif code == "79":
            # Escalate to support
            return {"retry": False, "escalate": True, "error": error}
        else:
            return {"retry": False, "unknown_error": True, "error": error}
```
