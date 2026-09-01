# API Security

**Web security with the browser's entire safety net removed and the data served raw to untrusted machine clients.** APIs are how modern software actually talks — phone apps, SPAs, microservices, third-party integrations — and OWASP maintains a **separate API Security Top 10** because the threat profile is genuinely different from web apps.

> **The one idea:** an API must enforce, on every stateless request, everything a browser used to enforce for free — and its defining weakness isn't injection but **authorization**: the API knows *who* you are and forgets to check *what you're allowed to touch*. Three of OWASP's top five API risks are that one failure.

## Why this exists — and what it doesn't re-teach

The vault covered [[cybersecurity/04-web-security/README|web security]] and [[backend/05-auth/README|backend auth]], but API-specific security was a gap — despite APIs being where most modern attacks land. **This folder covers what's *specific to APIs* and cross-links the rest:** it doesn't re-teach injection or OAuth from scratch, it shows how they change when the client is a machine and the browser is gone. It's the attacking-and-defending counterpart to [[backend/02-api-design/README|API design]].

## Reading order

Built around the **OWASP API Security Top 10 (2023)**. Read 01 for the map, then 03 is the heart of it.

1. [[cybersecurity/14-api-security/01-what-makes-api-security-different|what-makes-api-security-different]] — **[Intermediate]** — the protections APIs *lose*, why machine clients change the threat model, and **why authorization dominates**. The OWASP API Top 10 as a map
2. [[cybersecurity/14-api-security/02-authentication-for-apis|authentication-for-apis]] — **[Intermediate → Advanced]** — API keys, JWT (**and its recurring pitfalls**), OAuth/OIDC, mTLS, and the token-storage problem
3. [[cybersecurity/14-api-security/03-authorization-and-bola|authorization-and-bola]] — **[Intermediate → Advanced]** — **the #1 API vulnerability (BOLA/IDOR)**, plus BFLA, mass assignment and excessive data exposure: one mistake wearing four hats
4. [[cybersecurity/14-api-security/04-input-validation-and-injection|input-validation-and-injection]] — **[Intermediate → Advanced]** — schema validation, the injection classes on an API surface, and **SSRF — the API era's signature vulnerability** (Capital One)
5. [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|rate-limiting-and-abuse]] — **[Intermediate]** — machine-scale abuse, resource consumption, and **business-flow abuse that uses the API exactly as designed** (which a rate limit alone can't catch)
6. [[cybersecurity/14-api-security/06-the-api-security-lifecycle|the-api-security-lifecycle]] — **[Intermediate]** — **shadow/zombie APIs**, misconfiguration, consuming third-party APIs safely, gateways, and testing (why BOLA needs manual testing)

## If you only take three things

1. **Authorization is the #1 problem** — scope every query to the user and check ownership on every object, because no framework does it for you ([[cybersecurity/14-api-security/03-authorization-and-bola|03]]).
2. **The client is untrusted** — a mobile app or SPA runs on the attacker's device, so every check must be re-done server-side ([[cybersecurity/14-api-security/01-what-makes-api-security-different|01]]).
3. **When a user supplies a URL, assume SSRF** — it can reach your cloud metadata and internal services ([[cybersecurity/14-api-security/04-input-validation-and-injection|04]]).

## Practice

- **PortSwigger Web Security Academy** — has dedicated **API testing**, **access control (IDOR/BOLA)**, and **SSRF** labs. Free, and the best place to build this → [[cybersecurity/projects|cybersecurity projects]]
- **crAPI** (OWASP's deliberately-vulnerable API) and **VAmPI** — purpose-built API-security practice targets
- **Burp Suite** (+ the Autorize extension) and **Postman** — the workhorse tools for testing your own APIs → [[cybersecurity/02-ethical-hacking/08-common-tools|tools]]

## Related
- [[cybersecurity/README|cybersecurity curriculum map]] · [[cybersecurity/04-web-security/README|web security]] — the parent discipline
- [[backend/02-api-design/README|API design]] · [[backend/05-auth/README|backend/auth]] — the building side
- [[cybersecurity/02-ethical-hacking/README|ethical hacking]] — API testing as modern web pentesting
- [[cybersecurity/09-cloud-security/README|cloud security]] — the SSRF-to-metadata path
