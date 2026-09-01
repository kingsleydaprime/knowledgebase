# The API Security Lifecycle

**[Intermediate]** — the operational half: knowing what APIs you have, configuring them safely, consuming others' APIs carefully, and testing the lot.

## The kid version first

The previous notes were about *individual* vulnerabilities. This one is about the *program* around them: **you can't secure APIs you don't know exist, defaults are usually insecure, the third-party APIs you call can hurt you too, and none of it stays fixed without testing.** These are the remaining OWASP API risks (API8, API9, API10) plus the tooling that ties everything together.

## API9: Improper Inventory Management — the shadow API problem

**You cannot secure what you don't know exists**, and organisations accumulate forgotten APIs constantly:

- **Shadow APIs** — undocumented endpoints, built by a team, never registered, never security-reviewed
- **Zombie APIs** — old versions (`/api/v1/`) left running after `/v2/` shipped, unpatched and forgotten. **The classic breach: v2 is hardened, v1 has the old BOLA bug and is still live**
- **Staging/debug endpoints** exposed to production — `/debug`, `/actuator`, `/swagger` with no auth, internal admin routes reachable from outside

**Why this is the sneaky one:** every other vulnerability in this folder assumes you're *looking* at the endpoint. Shadow and zombie APIs are the ones nobody's looking at — so they're unpatched, unmonitored, and often the actual way in.

**The defences:**
- **Maintain an inventory** — every API, every version, its owner, its data sensitivity, its auth. Automated discovery tools (and gateway logs) find endpoints you forgot
- **Version and deprecate deliberately** — a sunset plan, not just leaving old versions running forever
- **Document with OpenAPI/Swagger** — an accurate spec is both documentation and a security artefact (it's the allowlist of what *should* exist)
- **Scan your own external surface** — find what's actually reachable, which is usually more than you think

## API8: Security Misconfiguration

The catch-all for insecure defaults and sloppy setup — and it's common because secure-by-default is still rare:

- **Verbose errors** leaking stack traces, SQL, internal paths, versions → attacker reconnaissance. Return generic errors to clients; log detail server-side
- **Missing security headers** and **overly-permissive CORS** — `Access-Control-Allow-Origin: *` on an authenticated API lets any site call it → [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|CORS and headers]]
- **Unnecessary HTTP methods** enabled (`PUT`, `DELETE`, `TRACE`) where not needed
- **Default credentials** on admin interfaces, databases, dashboards
- **Missing TLS**, or accepting weak ciphers → [[cybersecurity/04-web-security/03-https-and-tls|TLS]]
- **Debug mode on in production** — the framework default that leaks everything
- **Unpatched dependencies** — the API framework and its libraries → [[devops/README|dependency management]]

**The defence is discipline, not cleverness:** harden defaults, minimise the surface, automate configuration (so prod matches a reviewed baseline), and scan for drift → [[devops/07-infrastructure-as-code/README|infrastructure as code]].

## API10: Unsafe Consumption of APIs

The inversion: **you're not just an API *provider*, you're a *consumer* — and the third-party APIs you call are an attack surface too.** Developers trust external APIs far more than user input, and that trust is exploitable:

- **Trusting third-party responses** — you validate user input rigorously, then pipe a partner API's response straight into your database or logic unvalidated. **If their API is compromised or malicious, so are you** → [[web3/05-beyond-ethereum/06-bridges-and-interoperability|the same trust problem]]
- **Following redirects blindly** to a third-party endpoint (→ SSRF-adjacent) → [[cybersecurity/14-api-security/04-input-validation-and-injection|SSRF]]
- **No timeout / no error handling** on outbound calls — a slow or failing dependency cascades into your own outage → [[architecture/04-distributed-systems/README|cascading failures]]
- **Secrets sent to the wrong place** — leaking your API keys to a compromised partner

**Validate data from other APIs as carefully as data from users, use timeouts and circuit breakers, and pin/verify who you're talking to** (TLS, and ideally certificate/host validation).

## The tooling and controls

The infrastructure that enforces the previous notes:

- **API Gateway** — the front door: centralised authN, rate limiting, request validation, logging, routing. **The single best place to enforce cross-cutting controls** consistently instead of per-service (Kong, cloud API gateways, Apigee) → [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|rate limiting]]
- **WAF (Web Application Firewall)** — pattern-based filtering of known attacks; a useful layer, **not a substitute** for fixing the code (WAFs are bypassable)
- **Secrets management** — API keys and tokens in a vault, never in code or config → [[devops/09-secret-management/README|secret management]]
- **Logging and monitoring** — log auth failures, authZ denials, rate-limit hits, and anomalies; feed them to detection → [[cybersecurity/07-security-operations/README|security operations]]
- **mTLS between internal services** — don't trust the network perimeter alone → [[cybersecurity/03-network-security/README|zero trust]]

## Testing APIs — because none of this stays fixed

Security is a state you fall out of. Build testing in:

- **In CI:** schema validation, dependency scanning (SCA), SAST, and secrets scanning on every commit → [[devops/06-ci-cd/README|CI/CD]]
- **DAST / API scanners** — automated scanning against a running API (OWASP ZAP, Burp)
- **Manual API pentesting** — **Burp Suite** and **Postman** are the workhorses. The highest-value manual tests are the ones tools miss: **BOLA** (two accounts, swap IDs) and **BFLA** (guess admin routes) → [[cybersecurity/14-api-security/03-authorization-and-bola|testing authZ]], [[cybersecurity/02-ethical-hacking/08-common-tools|tools]]
- **The OpenAPI spec as a test oracle** — anything reachable that *isn't* in the spec is a shadow endpoint; anything in the spec without auth is a finding

**Authorization bugs (BOLA/BFLA) are the ones automated scanners are worst at**, because they require understanding *who should access what* — which is exactly why they're the #1 API vulnerability and why manual testing with multiple accounts is essential.

## Key insight

**The operational half of API security is the unglamorous part that determines whether the rest holds: you can't secure APIs you've forgotten (shadow/zombie endpoints are the ones nobody patches), defaults are insecure until hardened, the third-party APIs you *call* are an attack surface too, and none of it survives without testing built into CI.** A gateway is the best place to enforce cross-cutting controls consistently, an accurate OpenAPI spec doubles as a security artefact, and the authorization bugs that dominate the API Top 10 are precisely the ones scanners miss — so manual testing with two accounts stays essential.

## Related
- [[cybersecurity/14-api-security/README|the API security course]]
- [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|rate limiting]] — enforced at the gateway
- [[cybersecurity/07-security-operations/README|security operations]] — logging and detection
- [[devops/06-ci-cd/README|CI/CD]] — where testing lives · [[devops/09-secret-management/README|secret management]]

*Source: [reference] — OWASP API8/API9/API10. Aug 2026.*
