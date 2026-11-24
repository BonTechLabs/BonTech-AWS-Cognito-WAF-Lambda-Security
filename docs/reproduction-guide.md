# AWS Console walkthrough — reproduce the certification lab

**Session:** November 23–24, 2026. **Region:** US East (N. Virginia), `us-east-1`.

## Requirement: only AWS Cognito + Lambda pre-sign-up + AWS WAF

A French company uses Cognito managed login for registration and authentication. Its expected audience is in France, but fraudulent registrations mainly originate elsewhere. Choose **A (pre-sign-up Lambda)** and **B (AWS WAF geographic match Web ACL on Cognito)**. The exam does not require SNS, EventBridge, email alerts, ALB, or full WAF logging.

> The first lab run mistakenly blocked **France** rather than **outside France**. Follow the **corrected** step below on replay, and do not present the old WAF configuration as achieving the requirement.

### 1. Cognito pool and application
1. AWS Console → region picker → **US East (N. Virginia)**.
2. Search **Amazon Cognito** → **User pools** → **Create user pool** or **Get started**.
3. Select web-app setup and name the application `BonTech-France-Secure-Registration`.
4. Choose **Email** for sign-in; enable self-registration and email as a required attribute.
5. Review and click **Create**. Record the newly generated pool name (historical lab: `User pool - yq450b`). Do not assume pool IDs stay the same.
6. From **User pools** → your pool → **Applications** → **App clients** → your app client → **Login pages** → **View login page**.
7. Click **Create an account** to inspect sign-up. Do not enter sensitive real-user data until you have set controls.

### 2. Lambda function
1. Search **Lambda** → **Functions** → **Create function** → **Author from scratch**.
2. Function name `BonTech-Cognito-PreSignUp`; choose a currently supported **Python** runtime; basic execution role.
3. **Create function** → **Code** → `lambda_function.py` → paste [Lambda source](../lambda/lambda_function.py) → **Deploy**.
4. **Test** → **Create new event** → name `AllowedRegistration` → paste [allowed event JSON](../tests/events/allowed-registration.json) → **Save** → **Test**.
5. Expected **Succeeded**, input event returned. This is a standalone Lambda test, not a real registration.
6. **Test** → **Create new event** → name `BlockedRegistration` → paste [blocked event JSON](../tests/events/blocked-registration.json) → **Save** → **Test**.
7. Expected intentional `ValueError: Registration is not permitted` for `attacker@blocked.example`.

### 3. Connect Lambda to Cognito
1. **Amazon Cognito** → **User pools** → your existing pool → **Extensions** → **Lambda triggers**.
2. **Add Lambda trigger** → **Sign-up** → **Pre sign-up trigger** → select `BonTech-Cognito-PreSignUp`.
3. Click **Add Lambda trigger**; verify the function appears.
4. In the managed sign-up page try `attacker@blocked.example` with a unique throwaway password. The recorded attempt displayed: `PreSignUp failed ... Registration is not permitted`.
5. Cognito will not create a user for this rejected sign-up.

### 4. Create and configure AWS WAF Web ACL
1. Search **WAF & Shield** → **Protection packs (web ACLs)** → **Create protection pack (web ACL)**.
2. Under **Tell us about your app**, choose the appropriate business category, with **Both API and web** as applicable.
3. Under **Select resources to protect**, click **Add resources** → **Add regional resources**.
4. Check your **Amazon Cognito user pool** → **Add**; verify resource count = 1.
5. Under **Choose initial protections**, choose **Build your own pack**.
6. **Add rules** → **Custom rule** → **Next** → **Geo-based rule** → **Next**.
7. Set **Action = Block**, **Rule name = BonTech-Block-Outside-France**, **Statement = Country**, **France (FR)**.
8. **Crucial: check `Negate statement results` (NOT)** under **Rule configuration** to match sources **outside France**. Choose **Source IP address**.
9. Review generated JSON. Expected rule structure: `Statement.NotStatement.Statement.GeoMatchStatement.CountryCodes: ["FR"]`. See [corrected WAF JSON](../waf/geo-block-non-france.json).
10. **Validate** (if offered) → **Add rule**.
11. Under **Name and describe**, enter `BonTech-Cognito-WAF` and a suitable description.
12. Do not add paid managed rules, unrelated logging, SNS or EventBridge for this exam exercise.
13. Review the AWS price estimate and select **Create protection pack (web ACL)**.
14. Confirm Web ACL association success for the correct **Cognito user pool**.
15. Under **Manage rules**, verify the country match plus **NOT** and **Block**; under **Manage details**, verify **Default action = Allow**.

### 5. Validate the intended policy

| Scenario | Expected result |
|---|---|
| HTTP request from a French-geolocated IP | WAF allows onward to Cognito |
| HTTP request from a non-French-geolocated IP | WAF blocks before Cognito |
| Sign-up from allowed origin with `attacker@blocked.example` | Cognito invokes Lambda; Lambda rejects |
| Allowed-origin user with permitted email | Cognito signup proceeds subject to email verification |
| Existing user sign-in from allowed origin | Normal Cognito authentication; no PreSignUp trigger |

**Recorded limitation:** The actual deployed rule lacked NOT and blocked France. The corrected rule has *not* been deployed or empirically verified. The observed US sign-in is consistent with the historical inverted rule.

### 6. Cleanup and security

AWS WAF incurs recurring and request-based costs. After demonstrating the lab, disassociate and delete the Web ACL, remove test users/pool and Lambda if no longer required. Never publish AWS account IDs, credentials, client secrets, verification tokens, personal emails or unredacted screenshots.

### Engineering notes

- **User pool:** identity directory; **App client:** authentication configuration, not custom security validation.
- **Lambda PreSignUp:** a synchronous registration-time handler; raising an exception rejects the event; returning the event allows normal processing.
- **AWS WAF:** evaluates supported HTTP traffic before Cognito handles the request; geographic rules use apparent IP origin and may be bypassed using VPNs/proxies.
- **Default Allow:** passes nonmatching traffic onward, but does not authenticate or authorize it.
- **Web ACL vs rule:** ACL is the rule container attached to a resource; each rule defines its match and action.
- **CloudWatch WAF request logging:** helpful for investigations but not required by the original question.
