---
id: 4fac4f06-abef-48ae-acb2-d87d825db47a
---

# Authentication for APIs

**Authentication is proving who's making a request — and with no browser to carry a cookie, every API request must carry its own proof, like a key or a token.**

## Before you start
<!-- bite: f9b98ab0-0762-4e49-938a-69d63f3fe1e0 -->

You should have:

- Why there's no browser and the client is untrusted → [[cybersecurity/14-api-security/01-what-makes-api-security-different|what makes API security different]].
- The general auth principles this specialises → [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]], [[backend/05-auth/index|backend auth]].
- A feel for a signature making a token trustworthy → [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|signatures and PKI]].

After this lesson you will be able to:

1. Pick the right mechanism — API key, JWT, OAuth/OIDC, mTLS, session cookie — for a given caller.
2. Avoid the recurring JWT pitfalls (`alg:none`, algorithm confusion, unverified signatures).
3. Store a token safely on mobile, SPA and server-to-server clients.

**Study route.** Read the kid version and the mechanisms, then study the JWT pitfalls checklist — it prevents most real incidents. The practice task is a JWT review.

## What API authentication is
<!-- bite: 1f35ba23-1508-47e6-803d-b15b5b9e6ec6 -->

Authentication (authN) answers "who are you"; authorization (authZ) answers "what may you do." This lesson is authN. Because an API request stands alone — no browser, no automatic session cookie — the caller must attach proof of identity to *every single request*: an API key, a signed token, a certificate. Getting that proof right means issuing it, validating it, expiring it and revoking it, and the most common mistakes are in the *validation*. The next lesson is authZ, where the bigger bugs live — but a broken authN (especially JWT) hands an attacker the identity those authZ checks rely on.

## The kid version
<!-- bite: 32a9b65c-e444-47c1-b8c0-ba89fe35e4fb -->

A website remembers you with a cookie the browser sends automatically. An API has no browser, so the caller must **attach proof of identity to every single request** — an API key, or a token — because each request stands alone. Getting that proof right (issuing it, validating it, expiring it, revoking it) is API authentication, and the most common mistakes are in the *validation*.

**Authentication (authN) is "who are you"; authorization (authZ) is "what may you do."** This note is authN; [[cybersecurity/14-api-security/03-authorization-and-bola|the next]] is authZ — and authZ is where the bigger bugs live.

## The mechanisms, and when each fits
<!-- bite: 869c574b-482d-43a5-bb86-84e3d952b950 -->

**API keys** — a long random string identifying the *application* (not a user):
```text
GET /api/data
Authorization: Bearer sk_live_a1b2c3...
```
Simple, good for server-to-server and identifying a *project/tenant*. **But a key is a bearer credential** — whoever holds it *is* the caller — so it must be secret, scoped, rotatable, and never in client-side code → [[mobile/12-security-on-device|no secrets in the app]]. Keys don't expire on their own; you must rotate them.

**JWT (JSON Web Tokens)** — a signed token carrying claims (who, what roles, when it expires), so the server can verify it *without a database lookup*:
```text
header.payload.signature   ← base64url. The signature is what makes it trustworthy
```
The appeal is **stateless auth** — the server trusts the signature and reads the claims, no session store. The cost is **revocation is hard** (a valid unexpired token works even after you "log someone out") and the pitfalls below are legion.

## Mechanisms: OAuth, mTLS and sessions
<!-- bite: 65d48b5d-8a91-441a-8374-5495f0cc5141 -->

**OAuth 2.0 / OIDC** — the framework for *delegated* access ("let this app act for this user") and third-party login → [[backend/05-auth/03-oauth-provider-integrations|OAuth integrations]]. **OAuth is authorization delegation; OIDC adds an identity layer on top.** Access tokens (short-lived, sent on each request) + refresh tokens (long-lived, exchanged for new access tokens). **The standard for user-facing APIs**, and mandatory PKCE for public clients (mobile, SPA) → [[mobile/12-security-on-device|PKCE]].

**mTLS (mutual TLS)** — both sides present certificates. Strong, common in **service-to-service** and high-security B2B (open banking, internal microservices). Heavier to operate.

**Sessions** — a server-side session with a cookie still works for a same-site SPA, and is often *simpler and safer* than JWT for that case → [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]]. **Don't reach for JWT reflexively; a session cookie is the right default for a web frontend.**

## The JWT pitfalls — a checklist, because they recur endlessly
<!-- bite: a6808beb-9c3b-4ecc-89b9-8555dc96d26f -->

JWT is powerful and *dangerous* — its failures are famous because everyone reimplements validation and gets it wrong. The recurring ones:

- **`alg: none`** — the classic. A JWT header can claim the algorithm is "none," and a naive library then accepts an *unsigned* token as valid. **Attackers set `alg:none` and forge any claims.** Reject it explicitly
- **Algorithm confusion (RS256 → HS256)** — a token signed with RSA (public/private) can be tricked into being *verified* with HMAC using the **public** key as the HMAC secret — which is public. **Pin the expected algorithm**; never let the token dictate it
- **Not actually verifying the signature** — decoding a JWT (base64) and reading claims *without checking the signature*. Shockingly common. The payload is **not encrypted, just encoded** — anyone can read *and* rewrite it unless you verify the signature
## JWT pitfalls, continued
<!-- bite: 2911fdd9-7581-4747-9458-f695a4bf62c0 -->

The rest of the recurring list:

- **Weak HMAC secret** — a short/guessable HS256 secret is brute-forceable offline, then the attacker signs their own tokens. Use long random secrets → [[cybersecurity/05-cryptography/06-cryptographic-attacks-and-best-practices|weak keys]]
- **No expiry, or ignoring `exp`** — a token that never expires is a permanent credential if stolen. Set short expiries and *check* them
- **Sensitive data in the payload** — since it's just base64, **never put secrets, passwords or PII in a JWT**. It's readable by anyone who has it
- **No revocation plan** — stateless means you can't easily kill a token. Use short expiries + refresh tokens, or a revocation/deny list for the "log out everywhere" case

**Use a vetted library, pin the algorithm, verify the signature, check expiry.** That sentence prevents most JWT disasters → [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|signatures]].

## Where the token lives — the storage problem
<!-- bite: fd0fddde-f674-428c-bbbe-e585e0881035 -->

A stolen token *is* the user, so how the client stores it matters:

- **Mobile** — the Keychain/Keystore, never plain storage → [[mobile/12-security-on-device|secure storage]]
- **SPA / browser** — the hard case. `localStorage` is readable by any XSS → a single script steals the token. An **httpOnly cookie** isn't readable by JS (XSS-resistant) but is sent automatically → CSRF-exposed. **The modern answer leans to httpOnly cookies + CSRF protection, or short-lived in-memory tokens with a refresh flow** → [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/index|CSRF]]
- **Server-to-server** — a secret manager, never in code or committed config → [[devops/06-secret-management/index|secret management]]

## Common authentication failures (OWASP API2)
<!-- bite: 4cfe7cc2-5c71-4938-af90-666343a0f386 -->

Beyond the JWT list, the API-authN failures that get systems breached:

- **Weak or missing auth on some endpoints** — `/api/v2/` is protected but the forgotten `/api/v1/` or `/internal/` isn't → [[cybersecurity/14-api-security/06-the-api-security-lifecycle|shadow APIs]]
- **No rate limit on login** → credential stuffing and brute force → [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|rate limiting]], [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|why reuse is the problem]]
- **Credentials or keys in the URL** — they land in logs, browser history, referer headers. Use headers, never query strings
- **No account lockout / weak password reset** — the reset flow is often the weakest auth path

## Key insight
<!-- bite: fb4882b6-6d00-4d04-8023-0bc4ec757ea9 -->

**API authentication is proving identity on every stateless request without a browser to help — and the failures cluster in two places: token *validation* (especially JWT, where "verify the signature and pin the algorithm" prevents most disasters) and *storage* (a stolen bearer token is the user).** Don't reach for JWT by reflex; a session cookie is often the safer default for a web frontend, and OAuth/OIDC is the standard for user-facing APIs. Authentication only proves *who* — the harder, more-breached problem is *what they're allowed to do*, which is next.

## Terms used in this lesson
<!-- bite: 926f30cd-48e5-4416-a351-fb46972c779b -->

1. **Authentication (authN)**: Proving *who* is making a request, distinct from authorization (what they may do).
2. **API key**: A long random string identifying the calling *application* (not a user). A bearer credential: whoever holds it is the caller, so it must be secret, scoped and rotatable.
3. **Bearer credential**: Any token where mere possession grants access — so a stolen one *is* the user.
4. **JWT (JSON Web Token)**: A signed token carrying claims (who, roles, expiry) the server verifies by signature without a database lookup. Stateless, but hard to revoke.

## Terms used in this lesson: tokens and delegation
<!-- bite: 0913b451-5e39-4e49-8912-1d148049b406 -->

5. **Claim**: A field inside a JWT payload (e.g. `sub`, `exp`, `role`). Base64-encoded, *not* encrypted — readable by anyone holding the token.
6. **OAuth 2.0 / OIDC**: The standard for delegated access (OAuth) plus an identity layer (OIDC); uses short-lived access tokens and long-lived refresh tokens.
7. **PKCE**: An OAuth extension that protects public clients (mobile, SPA) from having their authorization code stolen. Mandatory for those clients.
8. **mTLS (mutual TLS)**: Authentication where both sides present certificates — strong, common for service-to-service and high-security B2B.

## Check your understanding
<!-- bite: 40b8a11c-0c6a-4057-b3eb-cbcb172a2d2a -->

Try each one before you open the answer.

1. <!-- q: mcq id="a7826f44" -->
   A JWT arrives with a header claiming `"alg": "none"`. What's the danger, and the fix?

   - [ ] None — `alg:none` means the token is encrypted
   - [x] A naive library accepts the *unsigned* token as valid, so an attacker forges any claims — reject `alg:none` and pin the expected algorithm
   - [ ] It makes the token expire immediately
   - [ ] It doubles the signature length

   <details><summary>Answer</summary>

   `alg:none` tells the verifier there's no signature to check, so a careless implementation treats a forged, unsigned token as authentic — the attacker sets any `sub`/`role` they like. The fix is to never let the token dictate the algorithm: pin the expected one server-side and reject `none`.

   </details>

2. <!-- q: mcq id="83072014" -->
   Why must you *pin the algorithm* rather than trust the JWT's own `alg` field (the RS256→HS256 confusion)?

   - [ ] HS256 is always weaker than RS256
   - [x] An RSA-signed token can be tricked into being *verified* with HMAC using the public key as the secret — which is public, so the attacker can forge valid tokens
   - [ ] The algorithms produce different token lengths
   - [ ] RS256 tokens can't expire

   <details><summary>Answer</summary>

   If the verifier obeys the token's `alg`, an attacker switches it from RS256 to HS256 and signs with HMAC using your *public* RSA key as the secret. Since the public key is, well, public, the forged token verifies. Pinning the expected algorithm server-side stops the token from choosing how it's checked.

   </details>

3. <!-- q: gap id="400c0a27" answers="signature" -->
   A JWT payload is base64-encoded, not encrypted, so anyone holding the token can read *and rewrite* the claims — which is why you must verify the ___ on every request, not just decode and trust the claims.

   <details><summary>Answer</summary>

   Signature. Decoding is not verifying. Because the payload is only encoded, the single thing that makes a JWT trustworthy is checking its signature against your pinned algorithm and key; skipping that lets an attacker rewrite the claims freely.

   </details>

4. <!-- q: mcq id="81e82947" -->
   For a same-site single-page app, what's the lesson's recommended default — and why not reach for JWT reflexively?

   - [ ] localStorage JWT, because it's simplest
   - [x] A server-side session cookie (often simpler and safer); JWT's statelessness buys little here and adds storage/revocation problems
   - [ ] An API key embedded in the JS bundle
   - [ ] No authentication; rely on CORS

   <details><summary>Answer</summary>

   For a web frontend talking to its own backend, a session cookie is frequently the right default: revocation is easy and there's no token to leak via XSS from `localStorage`. JWT shines for stateless, cross-service or third-party scenarios; reaching for it reflexively on a same-site SPA adds the storage and revocation headaches without the benefit.

   </details>

5. <!-- q: open id="7d7277f3" -->
   A stolen token "is the user." What does that imply about where tokens are stored on mobile, in a browser SPA, and server-to-server?

   <details><summary>Answer</summary>

   Because possession equals identity, storage is a security decision. On **mobile**, use the platform Keychain/Keystore, never plain storage. In a **browser SPA**, it's the hard case: `localStorage` is readable by any XSS (one script steals it), while an httpOnly cookie resists XSS but is sent automatically (CSRF-exposed) — so the modern lean is httpOnly cookies plus CSRF protection, or short-lived in-memory tokens with a refresh flow. **Server-to-server**, keep secrets in a secret manager, never in code or committed config. The common thread: minimise where a bearer token can be read or replayed.

   </details>

## Practice — review a JWT setup
<!-- bite: 867091d0-02b0-4579-b314-5a3ddb391b10 -->

Audit real token validation against the checklist, using a benign token.

- Grab a JWT from an app you control (dev-tools → network, or mint one), and decode it on [jwt.io](https://jwt.io) — note that you can *read* every claim without any secret.
- Check your backend's verification code against the list: is the algorithm pinned? Is the signature actually verified? Is `exp` checked? Is the HMAC secret long and random?
- Confirm no secrets or PII sit in the payload.
- **Done when:** you can point to the exact line that verifies the signature and pins the algorithm, and you've confirmed `exp` is enforced.

## Before moving on
<!-- bite: 19d72786-afd5-4912-a613-c04d87bb4973 -->

You should be able to choose a mechanism per caller, recite the JWT failure modes and their one-line fixes ("verify the signature, pin the algorithm, check expiry"), and store a token safely per client. Authentication only proves *who* — the harder, more-breached problem is *what they may do*, which is next.

Next: [[cybersecurity/14-api-security/03-authorization-and-bola|authorization and BOLA]] — the #1 API vulnerability and the family of authorization failures around it.

## Related
<!-- bite: 70656025-8021-417e-8acb-843e34502e91 -->
- [[cybersecurity/14-api-security/03-authorization-and-bola|authorization and BOLA]] — the harder half
- [[backend/05-auth/index|backend/auth]] — building these flows
- [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|signatures and PKI]] — what makes a JWT trustworthy
- [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]] — the general principles

## About this lesson
<!-- bite: ac9c46e8-f512-4568-af15-d6aad58aa37b -->

**Level:** Intermediate → Advanced. **Covers:** proving *who's calling* when there's no browser and no session cookie, and the token pitfalls that keep appearing.

*Source: [reference] — Aug 2026.*
