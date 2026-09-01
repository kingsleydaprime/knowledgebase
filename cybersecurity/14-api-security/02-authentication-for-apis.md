# Authentication for APIs

**[Intermediate → Advanced]** — proving *who's calling* when there's no browser and no session cookie, and the token pitfalls that keep appearing.

## The kid version first

A website remembers you with a cookie the browser sends automatically. An API has no browser, so the caller must **attach proof of identity to every single request** — an API key, or a token — because each request stands alone. Getting that proof right (issuing it, validating it, expiring it, revoking it) is API authentication, and the most common mistakes are in the *validation*.

**Authentication (authN) is "who are you"; authorization (authZ) is "what may you do."** This note is authN; [[cybersecurity/14-api-security/03-authorization-and-bola|the next]] is authZ — and authZ is where the bigger bugs live.

## The mechanisms, and when each fits

**API keys** — a long random string identifying the *application* (not a user):
```
GET /api/data
Authorization: Bearer sk_live_a1b2c3...
```
Simple, good for server-to-server and identifying a *project/tenant*. **But a key is a bearer credential** — whoever holds it *is* the caller — so it must be secret, scoped, rotatable, and never in client-side code → [[mobile/12-security-on-device|no secrets in the app]]. Keys don't expire on their own; you must rotate them.

**JWT (JSON Web Tokens)** — a signed token carrying claims (who, what roles, when it expires), so the server can verify it *without a database lookup*:
```
header.payload.signature   ← base64url. The signature is what makes it trustworthy
```
The appeal is **stateless auth** — the server trusts the signature and reads the claims, no session store. The cost is **revocation is hard** (a valid unexpired token works even after you "log someone out") and the pitfalls below are legion.

**OAuth 2.0 / OIDC** — the framework for *delegated* access ("let this app act for this user") and third-party login → [[backend/05-auth/03-oauth-provider-integrations|OAuth integrations]]. **OAuth is authorization delegation; OIDC adds an identity layer on top.** Access tokens (short-lived, sent on each request) + refresh tokens (long-lived, exchanged for new access tokens). **The standard for user-facing APIs**, and mandatory PKCE for public clients (mobile, SPA) → [[mobile/12-security-on-device|PKCE]].

**mTLS (mutual TLS)** — both sides present certificates. Strong, common in **service-to-service** and high-security B2B (open banking, internal microservices). Heavier to operate.

**Sessions** — a server-side session with a cookie still works for a same-site SPA, and is often *simpler and safer* than JWT for that case → [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]]. **Don't reach for JWT reflexively; a session cookie is the right default for a web frontend.**

## The JWT pitfalls — a checklist, because they recur endlessly

JWT is powerful and *dangerous* — its failures are famous because everyone reimplements validation and gets it wrong. The recurring ones:

- **`alg: none`** — the classic. A JWT header can claim the algorithm is "none," and a naive library then accepts an *unsigned* token as valid. **Attackers set `alg:none` and forge any claims.** Reject it explicitly
- **Algorithm confusion (RS256 → HS256)** — a token signed with RSA (public/private) can be tricked into being *verified* with HMAC using the **public** key as the HMAC secret — which is public. **Pin the expected algorithm**; never let the token dictate it
- **Not actually verifying the signature** — decoding a JWT (base64) and reading claims *without checking the signature*. Shockingly common. The payload is **not encrypted, just encoded** — anyone can read *and* rewrite it unless you verify the signature
- **Weak HMAC secret** — a short/guessable HS256 secret is brute-forceable offline, then the attacker signs their own tokens. Use long random secrets → [[cybersecurity/05-cryptography/06-cryptographic-attacks-and-best-practices|weak keys]]
- **No expiry, or ignoring `exp`** — a token that never expires is a permanent credential if stolen. Set short expiries and *check* them
- **Sensitive data in the payload** — since it's just base64, **never put secrets, passwords or PII in a JWT**. It's readable by anyone who has it
- **No revocation plan** — stateless means you can't easily kill a token. Use short expiries + refresh tokens, or a revocation/deny list for the "log out everywhere" case

**Use a vetted library, pin the algorithm, verify the signature, check expiry.** That sentence prevents most JWT disasters → [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|signatures]].

## Where the token lives — the storage problem

A stolen token *is* the user, so how the client stores it matters:

- **Mobile** — the Keychain/Keystore, never plain storage → [[mobile/12-security-on-device|secure storage]]
- **SPA / browser** — the hard case. `localStorage` is readable by any XSS → a single script steals the token. An **httpOnly cookie** isn't readable by JS (XSS-resistant) but is sent automatically → CSRF-exposed. **The modern answer leans to httpOnly cookies + CSRF protection, or short-lived in-memory tokens with a refresh flow** → [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|CSRF]]
- **Server-to-server** — a secret manager, never in code or committed config → [[devops/09-secret-management/README|secret management]]

## Common authentication failures (OWASP API2)

Beyond the JWT list, the API-authN failures that get systems breached:

- **Weak or missing auth on some endpoints** — `/api/v2/` is protected but the forgotten `/api/v1/` or `/internal/` isn't → [[cybersecurity/14-api-security/06-the-api-security-lifecycle|shadow APIs]]
- **No rate limit on login** → credential stuffing and brute force → [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|rate limiting]], [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|why reuse is the problem]]
- **Credentials or keys in the URL** — they land in logs, browser history, referer headers. Use headers, never query strings
- **No account lockout / weak password reset** — the reset flow is often the weakest auth path

## Key insight

**API authentication is proving identity on every stateless request without a browser to help — and the failures cluster in two places: token *validation* (especially JWT, where "verify the signature and pin the algorithm" prevents most disasters) and *storage* (a stolen bearer token is the user).** Don't reach for JWT by reflex; a session cookie is often the safer default for a web frontend, and OAuth/OIDC is the standard for user-facing APIs. Authentication only proves *who* — the harder, more-breached problem is *what they're allowed to do*, which is next.

## Related
- [[cybersecurity/14-api-security/03-authorization-and-bola|authorization and BOLA]] — the harder half
- [[backend/05-auth/README|backend/auth]] — building these flows
- [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|signatures and PKI]] — what makes a JWT trustworthy
- [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]] — the general principles

*Source: [reference] — Aug 2026.*
