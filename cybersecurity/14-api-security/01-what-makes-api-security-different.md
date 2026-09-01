# What Makes API Security Different

**[Intermediate]** — why APIs need their own security discipline, the protections they *lose* compared to web apps, and the map (the OWASP API Security Top 10).

## The kid version first

A traditional web app renders pages for a *human* using a *browser*. An API serves raw data to *other programs* — phone apps, single-page frontends, other companies' backends, scripts. **The client is a machine, not a person, and it isn't a browser** — so all the security machinery the browser quietly provided is simply gone, and the whole attack surface is exposed directly.

API security is web security with the browser's safety net removed and the data served up raw.

## Why APIs are a distinct problem

OWASP maintains a **separate API Security Top 10** from its famous web Top 10 — that split is itself the signal that this is its own discipline. The reasons:

**The browser's protections don't apply.** A huge amount of web security is enforced *by the browser* → [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|the same-origin policy]]. The Same-Origin Policy, CORS, cookie flags, CSP — these govern what a *browser* does. An API called by a phone app, a script, or `curl` gets none of that. **There is no browser to enforce anything**, so the API must enforce everything itself, on every request.

**The client is untrusted and inspectable.** A mobile app or SPA runs on the attacker's device → [[mobile/12-security-on-device|the app is on the attacker's hardware]]. They can read its code, watch its traffic, and replay or forge any request. **Any check done in the client is decorative** — the API must re-verify everything server-side.

**The data is served raw.** A web page returns rendered HTML; an API returns the underlying JSON objects. So flaws like returning too many fields, or trusting the object ID in the URL, expose data *directly* rather than being hidden behind a template → [[cybersecurity/14-api-security/03-authorization-and-bola|excessive data exposure]].

**Machine clients change the threat model.** Humans click a few times a minute; a script hits your endpoint thousands of times a second. **Abuse, scraping, credential stuffing and resource exhaustion are the normal case**, not the exception → [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|rate limiting]].

**The surface is larger and less visible.** A web app has pages you can see; an API has dozens or hundreds of endpoints, versions, and undocumented routes. **You can't secure what you don't know exists** → [[cybersecurity/14-api-security/06-the-api-security-lifecycle|shadow APIs]].

## The one that dominates: authorization

Here's the defining fact of API security, and it's worth stating up front:

> **The top API vulnerabilities are overwhelmingly *authorization* failures, not injection.**

Classic web security's headline threats are injection and XSS. **API security's headline threat is broken authorization** — the API authenticates *who you are* but fails to check *whether you're allowed to touch this specific object*. Change the `123` in `/api/orders/123` to `124` and you see someone else's order. That single class (BOLA) is #1, and authorization failures take three of the top five OWASP API slots → [[cybersecurity/14-api-security/03-authorization-and-bola|authorization]].

**Why:** injection is now well-defended by frameworks and ORMs, but authorization is *per-object, per-endpoint application logic* that no framework can write for you. It's the thing developers forget, on every new endpoint, forever.

## The OWASP API Security Top 10 — the map

The field's standard reference (2023 edition), and the backbone of this folder:

| | | Covered in |
|---|---|---|
| **API1** | **Broken Object Level Authorization (BOLA)** — the #1 API bug | [[cybersecurity/14-api-security/03-authorization-and-bola\|03]] |
| **API2** | Broken Authentication | [[cybersecurity/14-api-security/02-authentication-for-apis\|02]] |
| **API3** | Broken Object *Property* Level Authorization (mass assignment, excessive data) | [[cybersecurity/14-api-security/03-authorization-and-bola\|03]] |
| **API4** | Unrestricted Resource Consumption (rate limiting, DoS) | [[cybersecurity/14-api-security/05-rate-limiting-and-abuse\|05]] |
| **API5** | Broken Function Level Authorization | [[cybersecurity/14-api-security/03-authorization-and-bola\|03]] |
| **API6** | Unrestricted Access to Sensitive Business Flows | [[cybersecurity/14-api-security/05-rate-limiting-and-abuse\|05]] |
| **API7** | Server-Side Request Forgery (SSRF) | [[cybersecurity/14-api-security/04-input-validation-and-injection\|04]] |
| **API8** | Security Misconfiguration | [[cybersecurity/14-api-security/06-the-api-security-lifecycle\|06]] |
| **API9** | Improper Inventory Management (shadow/zombie APIs) | [[cybersecurity/14-api-security/06-the-api-security-lifecycle\|06]] |
| **API10** | Unsafe Consumption of APIs | [[cybersecurity/14-api-security/06-the-api-security-lifecycle\|06]] |

**Notice API1, API3 and API5 are all authorization.** That's the whole story in one observation.

## Where this sits in the vault

API security stitches together three areas you've already met:

- **[[cybersecurity/04-web-security/README|web security]]** — the parent discipline; injection, TLS, and auth principles apply, minus the browser
- **[[backend/05-auth/README|backend/auth]]** and **[[backend/02-api-design/README|API design]]** — the *building* side; this folder is the *attacking-and-defending* side of the same APIs
- **[[cybersecurity/02-ethical-hacking/README|ethical hacking]]** — API testing is a major part of modern web pentesting

This folder doesn't re-teach injection or OAuth from scratch — it covers **what's specific to APIs**, and links to the general treatment for the rest.

## Key insight

**An API is a web application with the browser's entire safety net removed and the data served raw to untrusted machine clients — so it must enforce, on every single request, everything a browser used to enforce for free.** And its defining weakness isn't injection but *authorization*: the API knows who you are and forgets to check whether you're allowed to touch this particular object. Three of OWASP's top five API risks are that one failure, because it's per-object application logic no framework writes for you.

## Related
- [[cybersecurity/14-api-security/02-authentication-for-apis|authentication for APIs]] — proving identity without a browser
- [[cybersecurity/14-api-security/03-authorization-and-bola|authorization and BOLA]] — the #1 problem
- [[cybersecurity/04-web-security/README|web security]] — the parent discipline
- [[backend/02-api-design/README|API design]] — the building side

*Source: [reference] — OWASP API Security Top 10 (2023). Aug 2026.*
