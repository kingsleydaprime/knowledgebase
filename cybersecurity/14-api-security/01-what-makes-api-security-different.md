---
id: 9f14fd0a-7b0e-4a16-9ba0-1105949ad0f6
---

# What Makes API Security Different

**Securing an API means doing everything a browser used to do for free — because the caller is a machine, not a person in a browser.**

## Before you start
<!-- bite: adcc2930-286e-4341-adbf-0e87578e926a -->

You should have:

- The web-security principles this builds on, minus the browser → [[cybersecurity/04-web-security/index|web security]].
- A feel for what an API is — a phone app asking its server for data → [[backend/02-api-design/index|API design]].

After this lesson you will be able to:

1. Name the browser protections an API *loses* and why that enlarges the attack surface.
2. Explain why machine clients change the threat model (untrusted client, raw data, machine-scale abuse).
3. State why authorization — not injection — is the defining API weakness, and read the OWASP API Top 10 as a map.

**Study route.** Read the kid version and why-APIs-are-distinct, then the authorization point and the OWASP map carefully — they frame the whole section.

## What makes API security different
<!-- bite: f16d1140-a4a6-4da0-9024-49b905080fbc -->

Classic web security protects pages rendered for a human in a browser. API security protects raw data served to *other programs* — phone apps, single-page frontends, other companies' backends, scripts. Two things change everything. First, there's no browser, so all the safety machinery it quietly provided (same-origin policy, CORS, cookie flags, CSP) is simply gone, and the API must enforce everything itself on every request. Second, the client is a machine on the attacker's hardware, hitting you thousands of times a second — so abuse, scraping and forged requests are the normal case. And the defining weakness that falls out of this isn't injection; it's authorization, as the rest of the section shows.

## The kid version
<!-- bite: 288666f6-c764-4a7a-8497-76b8db6bbd23 -->

A traditional web app renders pages for a *human* using a *browser*. An API serves raw data to *other programs* — phone apps, single-page frontends, other companies' backends, scripts. **The client is a machine, not a person, and it isn't a browser** — so all the security machinery the browser quietly provided is simply gone, and the whole attack surface is exposed directly.

API security is web security with the browser's safety net removed and the data served up raw.

## Why APIs are a distinct problem
<!-- bite: 66daffd0-853a-48bf-b670-4d61fc4402a1 -->

OWASP maintains a **separate API Security Top 10** from its famous web Top 10 — that split is itself the signal that this is its own discipline. The reasons:

**The browser's protections don't apply.** A huge amount of web security is enforced *by the browser* → [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/index|the same-origin policy]]. The Same-Origin Policy, CORS, cookie flags, CSP — these govern what a *browser* does. An API called by a phone app, a script, or `curl` gets none of that. **There is no browser to enforce anything**, so the API must enforce everything itself, on every request.

**The client is untrusted and inspectable.** A mobile app or SPA runs on the attacker's device → [[mobile/12-security-on-device|the app is on the attacker's hardware]]. They can read its code, watch its traffic, and replay or forge any request. **Any check done in the client is decorative** — the API must re-verify everything server-side.

## More reasons APIs are distinct
<!-- bite: 73aeea7c-0f21-4bdc-b819-c1e5a1094698 -->

**The data is served raw.** A web page returns rendered HTML; an API returns the underlying JSON objects. So flaws like returning too many fields, or trusting the object ID in the URL, expose data *directly* rather than being hidden behind a template → [[cybersecurity/14-api-security/03-authorization-and-bola|excessive data exposure]].

**Machine clients change the threat model.** Humans click a few times a minute; a script hits your endpoint thousands of times a second. **Abuse, scraping, credential stuffing and resource exhaustion are the normal case**, not the exception → [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|rate limiting]].

**The surface is larger and less visible.** A web app has pages you can see; an API has dozens or hundreds of endpoints, versions, and undocumented routes. **You can't secure what you don't know exists** → [[cybersecurity/14-api-security/06-the-api-security-lifecycle|shadow APIs]].

## The one that dominates: authorization
<!-- bite: 9c154dea-9d64-4756-bd9c-86118060ad4b -->

Here's the defining fact of API security, and it's worth stating up front:

> **The top API vulnerabilities are overwhelmingly *authorization* failures, not injection.**

Classic web security's headline threats are injection and XSS. **API security's headline threat is broken authorization** — the API authenticates *who you are* but fails to check *whether you're allowed to touch this specific object*. Change the `123` in `/api/orders/123` to `124` and you see someone else's order. That single class (BOLA) is #1, and authorization failures take three of the top five OWASP API slots → [[cybersecurity/14-api-security/03-authorization-and-bola|authorization]].

**Why:** injection is now well-defended by frameworks and ORMs, but authorization is *per-object, per-endpoint application logic* that no framework can write for you. It's the thing developers forget, on every new endpoint, forever.

## The OWASP API Security Top 10 — the map
<!-- bite: 3a97a2ec-7b42-4326-817a-6c006f15252e -->

The field's standard reference (2023 edition), and the backbone of this folder. Notice how much of it is one colour:

![The OWASP API Security Top 10 (2023) as a coloured list, with API1 Broken Object Level Authorization, API3 Broken Object Property Level Authorization and API5 Broken Function Level Authorization highlighted as the authorization category — three of the top five — alongside broken authentication, resource consumption, business-flow abuse, SSRF, misconfiguration, inventory management and unsafe consumption.](../images/api-owasp-map.svg)

## The Top 10, with where each is covered
<!-- bite: c60cf7ad-64cc-4688-bdb3-d5aea1e7ad0b -->

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
<!-- bite: fd5daf58-2072-4a57-b89d-fe4a68c8b085 -->

API security stitches together three areas you've already met:

- **[[cybersecurity/04-web-security/index|web security]]** — the parent discipline; injection, TLS, and auth principles apply, minus the browser
- **[[backend/05-auth/index|backend/auth]]** and **[[backend/02-api-design/index|API design]]** — the *building* side; this folder is the *attacking-and-defending* side of the same APIs
- **[[cybersecurity/02-ethical-hacking/index|ethical hacking]]** — API testing is a major part of modern web pentesting

This folder doesn't re-teach injection or OAuth from scratch — it covers **what's specific to APIs**, and links to the general treatment for the rest.

## Key insight
<!-- bite: c66a4c40-82a7-4428-a450-dfe75eb77964 -->

**An API is a web application with the browser's entire safety net removed and the data served raw to untrusted machine clients — so it must enforce, on every single request, everything a browser used to enforce for free.** And its defining weakness isn't injection but *authorization*: the API knows who you are and forgets to check whether you're allowed to touch this particular object. Three of OWASP's top five API risks are that one failure, because it's per-object application logic no framework writes for you.

## Terms used in this lesson
<!-- bite: 5bc674f1-8b1b-4cc8-8ee2-3f54d4b32c35 -->

1. **API (Application Programming Interface)**: The interface one program uses to ask another for data or actions. Here, a web API serving JSON to machine clients.
2. **Machine client**: A non-browser caller — a mobile app, SPA, script or another backend — that gets none of the browser's built-in protections.
3. **Same-Origin Policy / CORS**: Browser rules that govern which sites can read which responses. They protect *browsers*; an API called by a script gets no benefit from them.
4. **Authorization (authZ)**: The check that a known user may touch *this specific* object or call *this specific* endpoint — distinct from authentication (who you are).

## Terms used in this lesson: the risks
<!-- bite: a3181390-4cb4-4fbb-9ac1-37a60ff19134 -->

5. **BOLA (Broken Object Level Authorization)**: The #1 API vulnerability — using a request's object ID to fetch data without checking the caller owns it (also called IDOR).
6. **Excessive data exposure**: Returning the whole object and trusting the client to show only safe fields — but the client is untrusted, so the raw JSON leaks the rest.
7. **OWASP API Security Top 10**: The field's standard reference list of the ten most critical API risks (2023 edition), separate from the web Top 10.
8. **Attack surface**: Everything an attacker can reach and try — for an API, every endpoint, version and undocumented route.

## Check your understanding
<!-- bite: 738e428c-3332-41b4-9edf-574525061108 -->

Try each one before you open the answer.

1. <!-- q: mcq id="66a7f2ac" -->
   OWASP maintains a *separate* API Security Top 10 from its web Top 10. What is that split itself signalling?

   - [ ] APIs are less important than web apps
   - [x] The API threat profile is genuinely different — the browser's protections are gone and the dominant risks differ
   - [ ] The web Top 10 was retired
   - [ ] APIs can't be attacked the same way at all

   <details><summary>Answer</summary>

   The separate list is the signal that this is its own discipline. An API is called by machines with no browser, so same-origin policy, CORS and cookie protections don't apply, and the dominant risk shifts from injection/XSS to broken authorization. Same principles, different threat profile.

   </details>

2. <!-- q: mcq id="a1d57704" -->
   Why is "any check done in the client is decorative" for an API?

   - [ ] Clients are too slow to run checks
   - [x] A mobile app or SPA runs on the attacker's own device, so they can read it, watch its traffic, and forge any request — only server-side checks are trustworthy
   - [ ] Clients can't run JavaScript
   - [ ] The API encrypts client checks

   <details><summary>Answer</summary>

   The client is untrusted and inspectable: it's on the attacker's hardware. They can bypass any validation, hide-the-button logic or filtering the client does, and send whatever request they like. The API must re-verify everything server-side — identity, authorization, input, and which fields are returned or accepted.

   </details>

3. <!-- q: gap id="137485e6" answers="authorization|authz" -->
   Classic web security's headline threats are injection and XSS. API security's headline threat is broken ___ — and three of OWASP's top five API risks (API1, API3, API5) are that one failure.

   <details><summary>Answer</summary>

   Authorization. The API authenticates *who* you are but fails to check *whether you may touch this object or call this endpoint*. It dominates because it's per-object, per-endpoint application logic no framework can write for you.

   </details>

4. <!-- q: mcq id="446b3ba1" -->
   Why is authorization "the thing developers forget on every new endpoint, forever," while injection is increasingly well-handled?

   - [ ] Injection is harder to exploit
   - [x] Frameworks and ORMs defend injection generically, but authorization is per-object, per-endpoint business logic that no framework can decide for you
   - [ ] Authorization is a browser feature that APIs lack
   - [ ] Injection only affects databases

   <details><summary>Answer</summary>

   "Is this token valid?" is generic, so libraries handle it. "May *this user* touch *this order*?" is application-specific and must be written on every route. It also hides in testing — the developer tests as themselves, and they *are* allowed — so it only surfaces when someone tries an ID that isn't theirs.

   </details>

5. <!-- q: open id="71139661" -->
   Summarise, in one or two sentences, what an API "loses" compared to a browser-rendered web app, and why that matters.

   <details><summary>Answer</summary>

   An API loses the entire browser safety net — same-origin policy, CORS, cookie flags, CSP — and serves raw JSON objects to untrusted machine clients at machine scale. So it must enforce identity, authorization, input validation, field-level exposure and rate limiting itself, on every single stateless request, because nothing else will — and the attack surface (raw data, many endpoints, automated abuse) is exposed directly rather than hidden behind a rendered page.

   </details>

## Practice — read an API through the attacker's eyes
<!-- bite: 77c3ddb2-d647-4636-8e56-fb319d5843cc -->

Pick an API you can see (your own app's, or a public one with docs) and map its surface.

- Open the browser dev-tools network tab while using an app, and list the API calls it makes: endpoints, methods, what IDs appear in the URLs.
- For each endpoint, ask the three questions: does it check *who* I am, does it check *what* I may touch, and what fields does it return?
- Note any object IDs in URLs (`/orders/123`) — those are BOLA candidates for lesson 03.
- **Done when:** you have a short list of endpoints with, for each, a guess at its biggest risk (authZ, exposure, abuse) drawn from this lesson.

## Before moving on
<!-- bite: abe6f0c9-306b-444a-a62f-2ba66a63ac56 -->

You should be able to name what an API loses versus a browser app, explain why the client is untrusted, and state that authorization — three of the top five OWASP API risks — is the defining weakness. The OWASP map is the backbone; the next lessons walk it, starting with proving identity.

Next: [[cybersecurity/14-api-security/02-authentication-for-apis|authentication for APIs]] — proving *who's calling* without a browser or a session cookie, and the JWT pitfalls that recur endlessly.

## Related
<!-- bite: 1ceb35fb-c1cb-4a15-82e2-31ae9b7011f3 -->
- [[cybersecurity/14-api-security/02-authentication-for-apis|authentication for APIs]] — proving identity without a browser
- [[cybersecurity/14-api-security/03-authorization-and-bola|authorization and BOLA]] — the #1 problem
- [[cybersecurity/04-web-security/index|web security]] — the parent discipline
- [[backend/02-api-design/index|API design]] — the building side

## About this lesson
<!-- bite: 44260870-d190-4da3-a3f9-59f505ea4aa2 -->

**Level:** Intermediate. **Covers:** why APIs need their own security discipline, the protections they *lose* compared to web apps, and the map (the OWASP API Security Top 10).

*Source: [reference] — OWASP API Security Top 10 (2023). Aug 2026.*
