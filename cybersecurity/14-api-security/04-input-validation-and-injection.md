# Input Validation and Injection

**[Intermediate → Advanced]** — the injection classes as they hit APIs, and SSRF — the API-era vulnerability that turns your server into the attacker's proxy.

## The kid version first

An API takes input from untrusted callers and does things with it — queries a database, calls other services, builds responses. **If it trusts that input, the caller can make it do things it shouldn't:** run their SQL, fetch a URL they chose, or crash it with a malicious payload.

Most of this is the same injection story as [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|web security]] — with two API-specific twists: **schema validation matters more** (you're parsing structured data, not form fields), and **SSRF** has become a signature API vulnerability.

## Validate the whole request, by schema

APIs receive structured data (JSON, usually), and the first defence is refusing anything that doesn't match the expected shape:

- **Validate against a schema** — types, required fields, ranges, formats, enums. JSON Schema, OpenAPI validation, or your framework's DTO validation (Pydantic, Zod, Bean Validation) → [[backend/02-api-design/README|API design]]
- **Allowlist, don't blocklist** — define what's *valid* and reject everything else, rather than trying to enumerate what's *bad*
- **Check `Content-Type`** and parse accordingly — mismatches are a classic bypass
- **Bound everything** — string lengths, array sizes, number ranges, nesting depth. An unbounded array or deeply-nested JSON is a denial-of-service → [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|resource consumption]]

**Schema validation at the edge catches a huge amount before it reaches your logic** — and it's the API-native version of input validation. But it is *not* a substitute for the specific defences below.

## The injection classes — same story, API surface

Injection is injection: **untrusted input is treated as code/commands instead of data.** The classes and their real fixes, which are the same as [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|web security]] and [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation concepts]]:

- **SQL injection** → **parameterised queries.** Never string-concatenate input into SQL → [[databases/sql-reference|SQL]]. An ORM helps but doesn't make you immune (raw queries, some query builders)
- **NoSQL injection** — the API twist. JSON APIs over MongoDB et al. let attackers inject *operators*: `{"password": {"$ne": null}}` bypasses a login that expected a string. **Validate types** — a password field must be a *string*, not an object
- **Command injection** → don't pass input to a shell; use library calls with argument arrays, never string interpolation → [[build-your-own-shit/07-your-own-shell|how shells parse]]
- **XSS** — matters when API data is rendered by a browser client. **Output-encode at render** (the frontend's job), and set `Content-Type: application/json` so responses aren't interpreted as HTML → [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|CSP]]
- **XXE (XML External Entity)** — if you parse XML, disable external entities. Less common now JSON dominates, still lurking in SOAP and file uploads

**The through-line:** keep data and code separate — parameterise, use safe APIs, encode at the boundary. Validation reduces the attack surface; **these specific fixes are what actually stop injection.**

## SSRF — the signature API vulnerability (API7)

**Server-Side Request Forgery** is the one that earned its own OWASP API slot, because modern APIs constantly fetch URLs — webhooks, image-from-URL, link previews, importing from a remote source, calling microservices. **If the caller controls the URL, they make *your server* send requests on their behalf:**

```
   POST /api/import { "url": "https://example.com/data.json" }   ← intended
   POST /api/import { "url": "http://169.254.169.254/latest/meta-data/" }
                                    ↑ the cloud metadata endpoint → CREDENTIALS
```

**Why SSRF is devastating in the cloud:** your server sits *inside* the trusted network. An attacker who makes it fetch a URL can reach:
- **The cloud metadata service** (`169.254.169.254`) — on misconfigured setups this hands out **IAM credentials**, and SSRF-to-metadata was the mechanism of the **2019 Capital One breach** (100M+ records) → [[cybersecurity/09-cloud-security/README|cloud security]]
- **Internal services** with no external auth (databases, admin panels, other microservices) that trusted the network perimeter → [[cybersecurity/03-network-security/README|network segmentation]]
- **`localhost`** and link-local ranges

**The defences (layer them — no single one is enough):**
- **Allowlist destinations** — only permit the specific domains/IPs the feature needs. The strongest control
- **Block internal ranges** — reject `169.254.169.254`, `127.0.0.1`, `10.x`, `172.16.x`, `192.168.x`, `::1`, and cloud metadata IPs. **But beware bypasses** — DNS rebinding, redirects to internal IPs, IPv6, decimal/octal IP encodings. Validate the *resolved* IP, and re-validate after redirects
- **Use IMDSv2** on AWS (requires a token, defeating basic SSRF-to-metadata) — the direct fix for the Capital One class
- **Network-level egress filtering** — the server shouldn't be *able* to reach the metadata endpoint or internal admin services
- **Don't return the raw response** to the caller (limits blind SSRF exfiltration)

**Any feature where a user supplies a URL is an SSRF risk. Treat it as such by default.**

## Other input-driven API risks

- **Deserialization** — turning attacker-controlled bytes into objects can execute code (Java, Python `pickle`, .NET). **Never deserialize untrusted data with an unsafe deserializer**; use JSON with a schema → [[languages/06-python/README|Python]]'s pickle warning
- **File uploads** — validate type by *content* not extension, store outside the web root, scan, and never execute
- **GraphQL depth/complexity** — a nested query can be a resource-exhaustion attack; limit depth and complexity → [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|resource consumption]]

## Key insight

**Input-driven API attacks are the same "treat data as code" failure as web security — fixed the same way (parameterise, use safe APIs, allowlist by schema) — plus SSRF, which is the API era's signature vulnerability because servers now constantly fetch caller-supplied URLs from inside the trusted network.** Schema validation at the edge shrinks the surface, but the specific defences (parameterised queries, disabled XXE, SSRF allowlists + IMDSv2 + egress filtering) are what actually stop the attacks. When a user supplies a URL, assume SSRF; Capital One is the reminder of the stakes.

## Related
- [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|input validation and output encoding]] — the general treatment
- [[cybersecurity/09-cloud-security/README|cloud security]] — the SSRF-to-metadata attack path
- [[cybersecurity/14-api-security/03-authorization-and-bola|authorization]] — the other "trust the input" family
- [[backend/02-api-design/README|API design]] — schema validation while building

*Source: [reference] — OWASP API7 (SSRF). Aug 2026.*
