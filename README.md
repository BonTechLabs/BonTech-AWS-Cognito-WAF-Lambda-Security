# BonTech | AWS Cognito, WAF & Lambda Security Lab

Hands-on AWS cloud security lab: Cognito managed login, a Python pre-sign-up validation trigger, and a regional AWS WAF geo-match rule.

**Exercise dates:** November 23–24, 2026 · **Region:** `us-east-1` · **Status:** partial validation, geo-rule correction pending.

## Exam scenario and intended architecture

A French company uses Amazon Cognito managed login (formerly Hosted UI). It expects users from France but observes fraudulent registrations, predominantly outside France. It needs geographic restrictions and custom validation that accepts or rejects sign-up attempts.

**Answers: A and B**
- **A — Cognito pre-sign-up Lambda trigger:** inspect registration attributes and reject requests that violate custom policy.
- **B — AWS WAF regional Web ACL associated with Cognito:** filter HTTP requests using a geographic match.

```text
Browser -> AWS WAF (regional Web ACL)
             | reject non-FR IPs
             v
         Amazon Cognito managed login
             | signup
             v
         PreSignUp Lambda (Python)
             | custom attributes policy
             +-- error --> reject
             +-- event --> continue Cognito signup
```

> **Important historical finding:** The lab's deployed WAF rule was `BonTech-Block-France` with `FR` + `Block`, **without** negation. That blocks **France**, the opposite of the exam's intended requirement. The corrected configuration is available at [waf/geo-block-non-france.json](waf/geo-block-non-france.json). **It has not been deployed or tested** in the recorded session. A successful US sign-in does not establish that the corrected geo-rule works.

## Actual verified outcomes

| Item | Evidence / status |
|---|---|
| Cognito user pool and app client created | Console screenshots |
| Python Lambda pre-sign-up function deployed | Console screenshot |
| Standalone Lambda allowed-email test | **Succeeded** for `student@example.com` |
| Standalone Lambda blocked-email test | **Expected ValueError** for `attacker@blocked.example` |
| Cognito PreSignUp trigger attached | Console confirmation |
| Real Cognito registration with `attacker@blocked.example` | **Rejected**: `PreSignUp failed ... Registration is not permitted` |
| Regional WAF and one geo-rule deployed | Console confirmation |
| Web ACL associated with Cognito user pool | Console confirmation |
| Web ACL default action | **Allow**, screenshot-verified |
| Real user signed in | Cognito redirect indicated successful sign-in; user was Confirmed, Enabled and email verified |
| France-appropriate geo-rule | **NOT COMPLETE** — historical rule blocks France |
| Live request from France/non-France for corrected policy | **NOT TESTED** |

No SNS, EventBridge, security-analyst notification or WAF full-request logging was needed for the original two-answer question.

## How to reproduce

1. [Full AWS Console click-by-click walkthrough](docs/reproduction-guide.md)
2. [Lambda source code](lambda/lambda_function.py)
3. [Lambda unit tests](tests/test_lambda.py) and [sample events](tests/events/)
4. [Historical WAF rule](waf/geo-block-france-historical.json) and [corrected WAF rule](waf/geo-block-non-france.json)
5. [Test evidence and limitations](docs/test-results.md)

Run the standalone Python unit tests locally (no AWS credentials needed):

```bash
python -m unittest discover -s tests -v
```

**Security note:** Do not commit AWS credentials, app client secrets, access tokens, verification codes, personal email addresses, real user data or unredacted AWS Console screenshots. This repository intentionally avoids the screenshot-derived AWS account identifier and user PII. The full PDF archive remains PRIVACY not uploaded here because it may contain identifying screenshots.

**Cost note:** AWS WAF typically incurs ongoing Web ACL, rule and request-processing charges. Delete lab resources when no longer needed.
