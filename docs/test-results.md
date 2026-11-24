# Test report: observed facts vs intended outcomes

**Lab dates:** November 23–24, 2026. Based on the screenshots and saved archive from the exercise.

| Check | Input / setting | Observed result | Status |
|---|---|---|---|
| Lambda deployment | `BonTech-Cognito-PreSignUp` | AWS console reported successful deployment | Verified |
| Standalone Lambda allow | `student@example.com` | Lambda execution succeeded and returned event | Verified |
| Standalone Lambda rejection | `attacker@blocked.example` | Expected ValueError: `Registration is not permitted` | Verified |
| Cognito + Lambda sign-up rejection | `attacker@blocked.example` | Sign-up UI displayed `PreSignUp failed ... Registration is not permitted` | Verified |
| Web ACL deployment | `BonTech-Cognito-WAF` | AWS console reported creation success | Verified |
| User pool association | Regional Cognito user pool | AWS console reported association success | Verified |
| Existing WAF geo-rule | Block France, `FR`, negation unchecked | Configuration screenshots confirm the rule | Verified **but wrong for exam scenario** |
| Web ACL default action | Allow | Visible in Manage details | Verified |
| Legitimate user sign-in | Real mailbox | Managed login redirected to "Successfully signed in" | Verified |
| Cognito user status | User pool Users | One user, email verified, Confirmed, Enabled | Verified |
| Correct WAF geo-rule | Block non-France: NOT(GeoMatch FR) | Not deployed in original run | **Pending** |
| Real geo-block traffic test | Non-France egress | No real WAF block-response test in archive | **Pending** |

The recorded screenshot of the actual Lambda handler used logging, normalized the email, rejected missing emails and `@blocked.example`, and raised `ValueError("Registration is not permitted")`. The repository `lambda/lambda_function.py` preserves that handler. Test JSON files reproduce the standalone console inputs.

**Privacy:** Screenshots show account identifiers and a private test email, so the original screenshot archive/PDF is not posted to this public repository. Keep that PDF privately unless you first redact all sensitive fields.

**Not part of the original exam question:** SNS, EventBridge, analyst alerts/remediation, WAF detailed logging, ALB and bot protection. They were discussed as potential extensions, not implemented/verified here.
