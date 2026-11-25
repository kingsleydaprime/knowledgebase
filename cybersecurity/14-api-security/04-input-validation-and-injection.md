---
id: 1a2f2695-b4c8-4564-9f6b-81ebd5af6e39
---

# Input Validation and Injection

**Skip input validation and a caller's data gets treated as a command — and the API-era twist is SSRF, the server fetching URLs an attacker chose.**

## Before you start
<!-- bite: 55e06882-b051-4530-b0a1-2ae3595c3b53 -->

You should have:

- The general injection and output-encoding treatment → [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index|input validation and output encoding]].
- The cloud metadata / SSRF-to-credentials path → [[cybersecurity/09-cloud-security/index|cloud security]].
- The "client is untrusted" framing → [[cybersecurity/14-api-security/01-what-makes-api-security-different|what makes API security different]].

After this lesson you will be able to:

1. Validate a whole request by schema, and say why that shrinks but doesn't replace specific defences.
2. Apply the real injection fixes on an API surface (parameterise, type-check, safe APIs, disable XXE).
3. Recognise and defend SSRF — the API era's signature vulnerability — in layers.

**Study route.** Read the kid version and schema validation, then the injection classes, then SSRF carefully — it's the one that earned its own OWASP slot. The practice task is an SSRF defence review.

## What this lesson covers
<!-- bite: 7bcc3112-dffa-4784-a25c-e84bc7b86839 -->

An API takes input from untrusted callers and does things with it — queries a database, calls other services, builds responses. If it trusts that input, the caller can make it run their SQL, fetch a URL they chose, or crash it with a malicious payload. Most of this is the same injection story as web security, with two API-specific twists: schema validation matters more (you're parsing structured JSON, not form fields), and **SSRF** — tricking your server into fetching attacker-chosen URLs — has become a signature API vulnerability because modern APIs constantly fetch URLs. Schema validation at the edge shrinks the attack surface, but the specific fixes below are what actually stop the attacks.

## The kid version
<!-- bite: 600df6e3-c702-49e0-919b-3342c33ae64e -->

An API takes input from untrusted callers and does things with it — queries a database, calls other services, builds responses. **If it trusts that input, the caller can make it do things it shouldn't:** run their SQL, fetch a URL they chose, or crash it with a malicious payload.

Most of this is the same injection story as [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index|web security]] — with two API-specific twists: **schema validation matters more** (you're parsing structured data, not form fields), and **SSRF** has become a signature API vulnerability.

## Validate the whole request, by schema
<!-- bite: 78a2824a-9bdb-44d6-b75d-ab6bd90b41b8 -->

APIs receive structured data (JSON, usually), and the first defence is refusing anything that doesn't match the expected shape:

- **Validate against a schema** — types, required fields, ranges, formats, enums. JSON Schema, OpenAPI validation, or your framework's DTO validation (Pydantic, Zod, Bean Validation) → [[backend/02-api-design/index|API design]]
- **Allowlist, don't blocklist** — define what's *valid* and reject everything else, rather than trying to enumerate what's *bad*
- **Check `Content-Type`** and parse accordingly — mismatches are a classic bypass
- **Bound everything** — string lengths, array sizes, number ranges, nesting depth. An unbounded array or deeply-nested JSON is a denial-of-service → [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|resource consumption]]

**Schema validation at the edge catches a huge amount before it reaches your logic** — and it's the API-native version of input validation. But it is *not* a substitute for the specific defences below.

## The injection classes — same story, API surface
<!-- bite: cfa187b8-e6d5-4d4e-b43b-17d8b3377997 -->

Injection is injection: **untrusted input is treated as code/commands instead of data.** The classes and their real fixes, which are the same as [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index|web security]] and [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation concepts]]:

- **SQL injection** → **parameterised queries.** Never string-concatenate input into SQL → [[databases/sql-reference|SQL]]. An ORM helps but doesn't make you immune (raw queries, some query builders)
- **NoSQL injection** — the API twist. JSON APIs over MongoDB et al. let attackers inject *operators*: `{"password": {"$ne": null}}` bypasses a login that expected a string. **Validate types** — a password field must be a *string*, not an object
- **Command injection** → don't pass input to a shell; use library calls with argument arrays, never string interpolation → [[build-your-own-shit/07-your-own-shell|how shells parse]]

## Injection classes: XSS and XXE
<!-- bite: 693b2d81-72b5-4fb4-a81d-35aa056c064e -->

- **XSS** — matters when API data is rendered by a browser client. **Output-encode at render** (the frontend's job), and set `Content-Type: application/json` so responses aren't interpreted as HTML → [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/index|CSP]]
- **XXE (XML External Entity)** — if you parse XML, disable external entities. Less common now JSON dominates, still lurking in SOAP and file uploads

**The through-line:** keep data and code separate — parameterise, use safe APIs, encode at the boundary. Validation reduces the attack surface; **these specific fixes are what actually stop injection.**

## SSRF — the signature API vulnerability (API7)
<!-- bite: 76d55b42-746f-4a7f-bb70-a2bf21baac30 -->

**Server-Side Request Forgery** is the one that earned its own OWASP API slot, because modern APIs constantly fetch URLs — webhooks, image-from-URL, link previews, importing from a remote source, calling microservices. **If the caller controls the URL, they make *your server* send requests on their behalf:**

```text
   POST /api/import { "url": "https://example.com/data.json" }   ← intended
   POST /api/import { "url": "http://169.254.169.254/latest/meta-data/" }
                                    ↑ the cloud metadata endpoint → CREDENTIALS
```

## Why SSRF is devastating in the cloud
<!-- bite: b59d6b1e-63b1-4b0e-add2-19a72042aa71 -->

Your server sits *inside* the trusted network, so an attacker who makes it fetch a URL reaches things they never could directly:

![An SSRF attack: the attacker sends a request whose URL points at an internal address; the API server, trusting it, fetches that URL from inside the cloud network and reaches the metadata service at 169.254.169.254 which hands out IAM credentials (the 2019 Capital One breach), internal services with no external auth, and localhost — none of which the attacker could reach from outside.](../images/api-ssrf.svg)

- **The cloud metadata service** (`169.254.169.254`) — on misconfigured setups this hands out **IAM credentials**, and SSRF-to-metadata was the mechanism of the **2019 Capital One breach** (100M+ records) → [[cybersecurity/09-cloud-security/index|cloud security]]
- **Internal services** with no external auth (databases, admin panels, other microservices) that trusted the network perimeter → [[cybersecurity/03-network-security/index|network segmentation]]
- **`localhost`** and link-local ranges

## Defending against SSRF
<!-- bite: ce931fbd-0cd4-4a3b-95f4-874d29ec487d -->

**The defences (layer them — no single one is enough):**
- **Allowlist destinations** — only permit the specific domains/IPs the feature needs. The strongest control
- **Block internal ranges** — reject `169.254.169.254`, `127.0.0.1`, `10.x`, `172.16.x`, `192.168.x`, `::1`, and cloud metadata IPs. **But beware bypasses** — DNS rebinding, redirects to internal IPs, IPv6, decimal/octal IP encodings. Validate the *resolved* IP, and re-validate after redirects
- **Use IMDSv2** on AWS (requires a token, defeating basic SSRF-to-metadata) — the direct fix for the Capital One class
- **Network-level egress filtering** — the server shouldn't be *able* to reach the metadata endpoint or internal admin services
- **Don't return the raw response** to the caller (limits blind SSRF exfiltration)

**Any feature where a user supplies a URL is an SSRF risk. Treat it as such by default.**

## Other input-driven API risks
<!-- bite: 8929ebe0-ae5f-4704-b7cf-34c3e5d245b5 -->

- **Deserialization** — turning attacker-controlled bytes into objects can execute code (Java, Python `pickle`, .NET). **Never deserialize untrusted data with an unsafe deserializer**; use JSON with a schema → [[languages/06-python/index|Python]]'s pickle warning
- **File uploads** — validate type by *content* not extension, store outside the web root, scan, and never execute
- **GraphQL depth/complexity** — a nested query can be a resource-exhaustion attack; limit depth and complexity → [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|resource consumption]]

## Key insight
<!-- bite: 0fa8762c-15b9-44f2-9912-7e8ca394d01d -->

**Input-driven API attacks are the same "treat data as code" failure as web security — fixed the same way (parameterise, use safe APIs, allowlist by schema) — plus SSRF, which is the API era's signature vulnerability because servers now constantly fetch caller-supplied URLs from inside the trusted network.** Schema validation at the edge shrinks the surface, but the specific defences (parameterised queries, disabled XXE, SSRF allowlists + IMDSv2 + egress filtering) are what actually stop the attacks. When a user supplies a URL, assume SSRF; Capital One is the reminder of the stakes.

## Terms used in this lesson
<!-- bite: 2b5b4019-f1a6-45b6-8860-b71fa250c80c -->

1. **Schema validation**: Rejecting any request that doesn't match an expected shape — types, required fields, ranges, formats, enums — at the API edge (JSON Schema, Pydantic, Zod).
2. **Allowlist (vs blocklist)**: Defining what's *valid* and rejecting everything else, rather than trying to enumerate what's bad.
3. **Parameterised query**: Sending SQL and user data separately so input is never parsed as SQL — the real fix for SQL injection.
4. **NoSQL operator injection**: The API twist — a JSON body injecting query operators (`{"$ne": null}`) to bypass logic; fixed by validating that a field is a *string*, not an object.

## Terms used in this lesson: SSRF and the cloud
<!-- bite: c945885e-7de4-4779-812a-90c5a8006004 -->

5. **XXE (XML External Entity)**: An XML-parsing attack that reads files or makes requests via external entities; fixed by disabling external entities.
6. **SSRF (Server-Side Request Forgery)**: Making the server fetch an attacker-chosen URL, reaching internal services and cloud metadata from inside the trusted network. API7.
7. **Cloud metadata service**: The `169.254.169.254` endpoint that, on misconfigured setups, hands out IAM credentials — the SSRF target in the Capital One breach.
8. **IMDSv2**: AWS's token-required metadata service, which defeats basic SSRF-to-metadata — the direct fix for the Capital One class.

## Check your understanding
<!-- bite: e8d46ee9-175a-4a26-a3ba-ebbe5f0be40d -->

Try each one before you open the answer.

1. <!-- q: mcq id="9ad495e9" -->
   A login endpoint expects `{"user": "...", "password": "..."}`. An attacker sends `{"user": "admin", "password": {"$ne": null}}` and logs in. What happened, and what's the fix?

   - [ ] SQL injection; use an ORM
   - [x] NoSQL operator injection; validate that `password` is a *string*, not an object
   - [ ] SSRF; block internal IPs
   - [ ] XSS; output-encode

   <details><summary>Answer</summary>

   The JSON API passed the body straight into a MongoDB-style query, so `{"$ne": null}` became a query operator meaning "password not null" — true for any user. The API-specific fix is type validation: a password field must be a string. Schema validation at the edge catches this whole class.

   </details>

2. <!-- q: mcq id="553eabed" -->
   Why is schema validation at the edge valuable but *not* a substitute for parameterised queries and disabled XXE?

   - [ ] Schema validation is slower
   - [x] It shrinks the attack surface by rejecting malformed input, but the specific defences are what actually keep data and code separate for well-formed malicious input
   - [ ] Parameterised queries are obsolete
   - [ ] Schema validation only works on XML

   <details><summary>Answer</summary>

   A perfectly well-formed string can still be a SQL-injection payload or carry an XXE entity. Schema validation rejects the obviously-malformed and reduces surface, but injection is stopped by keeping data and code separate — parameterise queries, disable external entities, use safe APIs. Do both: validate the shape, then defend the specific sink.

   </details>

3. <!-- q: gap id="8d1d678e" answers="SSRF|server-side request forgery" -->
   Any API feature where a user supplies a URL — webhooks, image-from-URL, link previews, imports — should be treated as a ___ risk, because the server can be made to fetch internal addresses from inside the trusted network.

   <details><summary>Answer</summary>

   SSRF (Server-Side Request Forgery). It earned its own OWASP API slot because modern APIs constantly fetch URLs. When the caller controls the URL, your server becomes their proxy into the internal network and cloud metadata.

   </details>

4. <!-- q: mcq id="5679105c" -->
   In the 2019 Capital One breach, SSRF was used to reach `169.254.169.254`. What did that give the attacker, and which control directly addresses that class?

   - [ ] The password database; stronger hashing
   - [x] IAM credentials from the cloud metadata service; IMDSv2 (token-required metadata), plus destination allowlisting and egress filtering
   - [ ] The TLS private key; certificate pinning
   - [ ] Admin cookies; the SameSite flag

   <details><summary>Answer</summary>

   The metadata endpoint handed out IAM credentials because the server could reach it and it required no token. IMDSv2 requires a token, defeating basic SSRF-to-metadata; layer it with allowlisting destinations, blocking internal ranges (validating the *resolved* IP and re-checking after redirects), and network egress filtering so the server can't reach the metadata endpoint at all.

   </details>

5. <!-- q: open id="51f75d93" -->
   Why is blocking internal IP ranges, by itself, a fragile SSRF defence? Name two bypasses and the better layered approach.

   <details><summary>Answer</summary>

   A denylist of internal ranges is easy to slip past: an attacker can use **DNS rebinding** (a hostname that resolves to an allowed IP on first check, then to an internal one when fetched), a **redirect** from an allowed URL to an internal address, **IPv6** forms, or **decimal/octal/encoded** representations of the same IP. So you must validate the *resolved* IP (not the string) and re-validate after each redirect. Better still, layer it: allowlist the specific destinations the feature needs (the strongest control), use IMDSv2, add network-level egress filtering so the server can't reach the metadata or internal admin services, and don't return the raw response to the caller (limiting blind-SSRF exfiltration).

   </details>

## Practice — SSRF-proof a URL-fetching feature
<!-- bite: 76e51989-6f58-4cf3-91fe-5dadd9ab6d30 -->

Find or build a feature that fetches a user-supplied URL, and review it.

- Identify one: a webhook registration, an image-from-URL, a link preview, an import.
- Check the defences: is there a destination *allowlist*? Does it validate the *resolved* IP and re-check after redirects? Is `169.254.169.254` reachable from the server at all (try it from the box, on a system you own)?
- On AWS, confirm IMDSv2 is enforced. Separately, add schema validation and confirm a non-string where a string is expected is rejected.
- **Done when:** you can state, for the feature, which of the layered SSRF defences are present and which are missing.

## Before moving on
<!-- bite: b0edcd1e-6928-4fb0-be55-2554d5a752bc -->

You should be able to validate a request by schema, apply the real injection fixes on an API, and defend SSRF in layers. One line to keep: when a user supplies a URL, assume SSRF — Capital One is the reminder of the stakes.

Next: [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|rate limiting and abuse]] — machine-scale abuse, resource consumption, and business-flow abuse that uses the API exactly as designed.

## Related
<!-- bite: 07e48c8c-46f4-4bf3-893d-1452e961a96c -->
- [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index|input validation and output encoding]] — the general treatment
- [[cybersecurity/09-cloud-security/index|cloud security]] — the SSRF-to-metadata attack path
- [[cybersecurity/14-api-security/03-authorization-and-bola|authorization]] — the other "trust the input" family
- [[backend/02-api-design/index|API design]] — schema validation while building

## About this lesson
<!-- bite: 00b3902d-afcf-4fa1-8786-69316e76e905 -->

**Level:** Intermediate → Advanced. **Covers:** the injection classes as they hit APIs, and SSRF — the API-era vulnerability that turns your server into the attacker's proxy.

*Source: [reference] — OWASP API7 (SSRF). Aug 2026.*
