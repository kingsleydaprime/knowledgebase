---
id: 0cb2b969-b1d9-40de-bce7-db6b8f0c302d
---

# The API Security Lifecycle

**The API security lifecycle is the program around an API — inventory, safe configuration, careful consumption and testing — because security never stays fixed on its own.**

## Before you start
<!-- bite: bb6f3f48-f023-4f1c-b79e-53a0856f0c99 -->

You should have:

- The individual vulnerabilities this operationalises → the rest of this section, especially [[cybersecurity/14-api-security/03-authorization-and-bola|authorization and BOLA]].
- Where logging and detection go → [[cybersecurity/07-security-operations/index|security operations]].
- Where testing lives → [[devops/05-ci-cd/index|CI/CD]].

After this lesson you will be able to:

1. Explain the shadow/zombie API problem and why it's the sneaky one.
2. Name the common misconfigurations (API8) and the unsafe-consumption risks (API10).
3. Place the cross-cutting controls (gateway, WAF, secrets, logging) and build testing in — and say why BOLA needs manual testing.

**Study route.** Read the kid version and the inventory problem, then misconfiguration, consumption, the tooling, and testing. This lesson closes the section, so the practice task is a whole-API review.

## What the API security lifecycle is
<!-- bite: 3d172110-d45a-4520-b4cf-27ca069867f4 -->

The previous lessons were about *individual* vulnerabilities. This one is the *program* around them — the operational, unglamorous half that decides whether the rest holds. Four ideas: you can't secure APIs you don't know exist (shadow and zombie endpoints), defaults are insecure until hardened, the third-party APIs you *call* are an attack surface too, and none of it survives without testing built into CI. These are the remaining OWASP API risks (API8, API9, API10) plus the gateway, secrets, logging and testing that tie everything together.

## The kid version
<!-- bite: 183d9861-db6c-4188-a077-6f66270c81a5 -->

The previous notes were about *individual* vulnerabilities. This one is about the *program* around them: **you can't secure APIs you don't know exist, defaults are usually insecure, the third-party APIs you call can hurt you too, and none of it stays fixed without testing.** These are the remaining OWASP API risks (API8, API9, API10) plus the tooling that ties everything together.

## API9: Improper Inventory Management — the shadow API problem
<!-- bite: a3cf3e2f-1444-4f75-a5f2-351489a88c40 -->

**You cannot secure what you don't know exists**, and organisations accumulate forgotten APIs constantly:

- **Shadow APIs** — undocumented endpoints, built by a team, never registered, never security-reviewed
- **Zombie APIs** — old versions (`/api/v1/`) left running after `/v2/` shipped, unpatched and forgotten. **The classic breach: v2 is hardened, v1 has the old BOLA bug and is still live**
- **Staging/debug endpoints** exposed to production — `/debug`, `/actuator`, `/swagger` with no auth, internal admin routes reachable from outside

**Why this is the sneaky one:** every other vulnerability in this folder assumes you're *looking* at the endpoint. Shadow and zombie APIs are the ones nobody's looking at — so they're unpatched, unmonitored, and often the actual way in.

## Fixing the inventory problem
<!-- bite: 42341120-c027-4dab-a8c7-1c6536e79d40 -->

**The defences:**
- **Maintain an inventory** — every API, every version, its owner, its data sensitivity, its auth. Automated discovery tools (and gateway logs) find endpoints you forgot
- **Version and deprecate deliberately** — a sunset plan, not just leaving old versions running forever
- **Document with OpenAPI/Swagger** — an accurate spec is both documentation and a security artefact (it's the allowlist of what *should* exist)
- **Scan your own external surface** — find what's actually reachable, which is usually more than you think

## API8: Security Misconfiguration
<!-- bite: e702d84b-486c-4082-8435-0c88fc350a8d -->

The catch-all for insecure defaults and sloppy setup — and it's common because secure-by-default is still rare:

- **Verbose errors** leaking stack traces, SQL, internal paths, versions → attacker reconnaissance. Return generic errors to clients; log detail server-side
- **Missing security headers** and **overly-permissive CORS** — `Access-Control-Allow-Origin: *` on an authenticated API lets any site call it → [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/index|CORS and headers]]
- **Unnecessary HTTP methods** enabled (`PUT`, `DELETE`, `TRACE`) where not needed
- **Default credentials** on admin interfaces, databases, dashboards
- **Missing TLS**, or accepting weak ciphers → [[cybersecurity/04-web-security/03-https-and-tls|TLS]]
- **Debug mode on in production** — the framework default that leaks everything
- **Unpatched dependencies** — the API framework and its libraries → [[devops/index|dependency management]]

**The defence is discipline, not cleverness:** harden defaults, minimise the surface, automate configuration (so prod matches a reviewed baseline), and scan for drift → [[devops/09-infrastructure-as-code/index|infrastructure as code]].

## API10: Unsafe Consumption of APIs
<!-- bite: 20158274-ccf5-40f1-8789-166990170e83 -->

The inversion: **you're not just an API *provider*, you're a *consumer* — and the third-party APIs you call are an attack surface too.** Developers trust external APIs far more than user input, and that trust is exploitable:

- **Trusting third-party responses** — you validate user input rigorously, then pipe a partner API's response straight into your database or logic unvalidated. **If their API is compromised or malicious, so are you** → [[web3/05-beyond-ethereum/06-bridges-and-interoperability|the same trust problem]]
- **Following redirects blindly** to a third-party endpoint (→ SSRF-adjacent) → [[cybersecurity/14-api-security/04-input-validation-and-injection|SSRF]]
- **No timeout / no error handling** on outbound calls — a slow or failing dependency cascades into your own outage → [[architecture/04-distributed-systems/index|cascading failures]]
- **Secrets sent to the wrong place** — leaking your API keys to a compromised partner

**Validate data from other APIs as carefully as data from users, use timeouts and circuit breakers, and pin/verify who you're talking to** (TLS, and ideally certificate/host validation).

## The tooling and controls
<!-- bite: 568c593c-6e2e-4bbd-bc7a-f8a5de49b42b -->

The infrastructure that enforces the previous notes:

- **API Gateway** — the front door: centralised authN, rate limiting, request validation, logging, routing. **The single best place to enforce cross-cutting controls** consistently instead of per-service (Kong, cloud API gateways, Apigee) → [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|rate limiting]]
- **WAF (Web Application Firewall)** — pattern-based filtering of known attacks; a useful layer, **not a substitute** for fixing the code (WAFs are bypassable)
- **Secrets management** — API keys and tokens in a vault, never in code or config → [[devops/06-secret-management/index|secret management]]
- **Logging and monitoring** — log auth failures, authZ denials, rate-limit hits, and anomalies; feed them to detection → [[cybersecurity/07-security-operations/index|security operations]]
- **mTLS between internal services** — don't trust the network perimeter alone → [[cybersecurity/03-network-security/index|zero trust]]

## Testing APIs — because none of this stays fixed
<!-- bite: ecd0a93a-4bbb-4446-bfc2-63c2a2cfc09a -->

Security is a state you fall out of. Build testing in:

- **In CI:** schema validation, dependency scanning (SCA), SAST, and secrets scanning on every commit → [[devops/05-ci-cd/index|CI/CD]]
- **DAST / API scanners** — automated scanning against a running API (OWASP ZAP, Burp)
- **Manual API pentesting** — **Burp Suite** and **Postman** are the workhorses. The highest-value manual tests are the ones tools miss: **BOLA** (two accounts, swap IDs) and **BFLA** (guess admin routes) → [[cybersecurity/14-api-security/03-authorization-and-bola|testing authZ]], [[cybersecurity/02-ethical-hacking/08-common-tools|tools]]
- **The OpenAPI spec as a test oracle** — anything reachable that *isn't* in the spec is a shadow endpoint; anything in the spec without auth is a finding

**Authorization bugs (BOLA/BFLA) are the ones automated scanners are worst at**, because they require understanding *who should access what* — which is exactly why they're the #1 API vulnerability and why manual testing with multiple accounts is essential.

## Key insight
<!-- bite: 23cfb016-5609-4141-85f6-564499de2e39 -->

**The operational half of API security is the unglamorous part that determines whether the rest holds: you can't secure APIs you've forgotten (shadow/zombie endpoints are the ones nobody patches), defaults are insecure until hardened, the third-party APIs you *call* are an attack surface too, and none of it survives without testing built into CI.** A gateway is the best place to enforce cross-cutting controls consistently, an accurate OpenAPI spec doubles as a security artefact, and the authorization bugs that dominate the API Top 10 are precisely the ones scanners miss — so manual testing with two accounts stays essential.

## Terms used in this lesson
<!-- bite: 9eda026c-aed8-44fa-8e27-57632e4d5ac1 -->

1. **Shadow API**: An undocumented endpoint, built by a team and never registered or security-reviewed.
2. **Zombie API**: An old version (`/api/v1/`) left running after a newer one shipped — unpatched and forgotten, often still carrying old bugs.
3. **API inventory**: A maintained list of every API, version, owner, data sensitivity and auth — you can't secure what you don't know exists.
4. **OpenAPI / Swagger spec**: A machine-readable API description that doubles as a security artefact — the allowlist of what *should* exist, and a test oracle.

## Terms used in this lesson: config, consumption and tooling
<!-- bite: b19dc05f-f14d-4e07-a7f0-37e162a93b9d -->

5. **Security misconfiguration (API8)**: Insecure defaults and sloppy setup — verbose errors, permissive CORS, default credentials, debug mode in production.
6. **Unsafe consumption (API10)**: Trusting third-party APIs you *call* more than user input, so a compromised or malicious partner response flows into your system.
7. **API gateway**: The front door that centralises authN, rate limiting, request validation, logging and routing — the best place to enforce cross-cutting controls.
8. **WAF (Web Application Firewall)**: A pattern-based filter of known attacks; a useful layer, but bypassable and not a substitute for fixing the code.
9. **SAST / DAST / SCA**: Static analysis of code, dynamic scanning of a running API, and dependency (software-composition) scanning — the automated tests that run in CI.

## Check your understanding
<!-- bite: 7656578b-abff-423c-98e7-262054629bca -->

Try each one before you open the answer.

1. <!-- q: mcq id="d2b5d031" -->
   Why are shadow and zombie APIs described as "the sneaky one," more dangerous than they look?

   - [ ] They run faster than documented APIs
   - [x] They're the endpoints nobody is looking at — unpatched, unmonitored — so an old version often still carries a bug (like BOLA) that the current version fixed
   - [ ] They can't be scanned at all
   - [ ] They only exist in staging

   <details><summary>Answer</summary>

   Every other vulnerability assumes you're looking at the endpoint. Shadow (undocumented) and zombie (old-version) APIs are exactly the ones nobody reviews or monitors, so they stay unpatched. The classic breach: `/v2/` is hardened, but `/v1/` is still live with the old BOLA bug. You can't secure what you don't know exists.

   </details>

2. <!-- q: mcq id="cbe695c0" -->
   An accurate OpenAPI spec is called "both documentation and a security artefact." How does it help security specifically?

   - [ ] It encrypts the API traffic
   - [x] It's the allowlist of what *should* exist, so anything reachable but not in the spec is a shadow endpoint, and anything in it without auth is a finding
   - [ ] It rate-limits requests automatically
   - [ ] It replaces authentication

   <details><summary>Answer</summary>

   The spec defines the intended surface. Used as a test oracle, it turns inventory into a check: reachable-but-not-in-spec = a shadow endpoint to investigate; in-spec-but-unauthenticated = a finding. That's how you catch the endpoints that otherwise go unmonitored.

   </details>

3. <!-- q: gap id="156909c3" answers="CORS" -->
   A common API8 misconfiguration is setting `Access-Control-Allow-Origin: *` on an authenticated API — an overly-permissive ___ policy that lets any website call it on a logged-in user's behalf.

   <details><summary>Answer</summary>

   CORS (Cross-Origin Resource Sharing). A wildcard origin on an authenticated API removes the cross-origin protection, letting any site make credentialed calls. Scope allowed origins explicitly to the sites that should have access.

   </details>

4. <!-- q: mcq id="a6f992f6" -->
   API10 (Unsafe Consumption) points out that you're also an API *consumer*. What's the core mistake?

   - [ ] Calling too many third-party APIs
   - [x] Trusting a third-party API's response far more than user input — piping it unvalidated into your database or logic, so a compromised partner compromises you
   - [ ] Using HTTPS for outbound calls
   - [ ] Caching third-party responses

   <details><summary>Answer</summary>

   Developers rigorously validate user input, then trust a partner API's response implicitly. If that partner is compromised or malicious, its response flows straight into your system. Validate data from other APIs as carefully as data from users, use timeouts and circuit breakers, and verify who you're talking to (TLS, host/cert validation).

   </details>

5. <!-- q: open id="815be9a9" -->
   The lesson says "authorization bugs are the ones automated scanners are worst at." Why, and what does that imply for how you test?

   <details><summary>Answer</summary>

   Scanners are good at pattern-matchable flaws (injection strings, missing headers, known CVEs) but authorization is about *who should access what* — business context a scanner doesn't have. It can't know that user B shouldn't see order 123, because that requires understanding ownership and roles. So BOLA/BFLA need **manual testing with multiple accounts**: log in as A, replay A's request as B, guess admin routes, change HTTP methods. Build the automatable checks into CI (schema validation, SCA, SAST, secrets scanning, DAST), but keep human two-account testing for the authorization class that dominates the API Top 10 and that tools miss.

   </details>

## Practice — a whole-API review
<!-- bite: 24f0b26d-3aaf-45aa-9902-9e3d257ed0f0 -->

Tie the section together on an API you own or are authorised to test.

- **Inventory:** list every endpoint and version actually reachable (from the gateway logs or a scan), and compare against the OpenAPI spec. Flag anything reachable but undocumented (shadow) or an old version still live (zombie).
- **Config:** check for verbose errors, wildcard CORS on authenticated routes, default credentials, and debug mode in production.
- **Consumption:** pick one outbound third-party call and check it has a timeout, error handling, and validates the response.
- **Testing:** confirm CI runs dependency scanning and secrets scanning; then do one manual two-account BOLA test by hand.
- **Done when:** you have a short findings list spanning inventory, configuration, consumption and a manual authZ test — the operational picture, not just one bug.

## Before moving on
<!-- bite: 4075d487-d543-4338-8149-a3341379e435 -->

You should be able to explain the shadow/zombie problem, name the common misconfigurations and consumption risks, place the cross-cutting controls, and say why BOLA needs manual testing. This closes the API-security section — and the cybersecurity curriculum's offensive-technical trio with binary exploitation and Active Directory.

From here, feed API logs and anomalies into [[cybersecurity/07-security-operations/index|security operations]], and build the hands-on skill on the PortSwigger and crAPI labs → [[cybersecurity/projects|cybersecurity projects]].

## Related
<!-- bite: 3b8a45b4-4f74-440d-af6e-c95d4a8e89fc -->
- [[cybersecurity/14-api-security/index|the API security course]]
- [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|rate limiting]] — enforced at the gateway
- [[cybersecurity/07-security-operations/index|security operations]] — logging and detection
- [[devops/05-ci-cd/index|CI/CD]] — where testing lives · [[devops/06-secret-management/index|secret management]]

## About this lesson
<!-- bite: 6df4d435-d166-484f-ba84-e537702c06f2 -->

**Level:** Intermediate. **Covers:** the operational half: knowing what APIs you have, configuring them safely, consuming others' APIs carefully, and testing the lot.

*Source: [reference] — OWASP API8/API9/API10. Aug 2026.*
