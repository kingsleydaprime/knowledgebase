---
id: 21cbf801-af77-4491-8275-164b9c8c0cdc
---

# Authentication Flows

This note is about the *architectural shapes* authentication takes in a backend system — session-based vs token-based, how OAuth actually works, when an API key is the right tool. The security mechanics underneath each (password hashing, MFA, JWT signature verification) are covered in depth in [[02-secure-authentication|secure-authentication]] — this note assumes that foundation and focuses on how the pieces fit into an actual system design.

## Session-based authentication
<!-- bite: 4233a3a0-8ab0-48a0-8393-0d9629c54fbc -->

On login, the server creates a session record (server-side state) and gives the client an opaque session ID via a cookie. Every subsequent request includes that cookie; the server looks up the session ID against its own store to identify the user.

```text
Login -> server creates session {id: "abc123", userId: 42} in a store (Redis, DB)
       -> server sets cookie: session=abc123

Later request -> cookie sent automatically by browser -> server looks up "abc123" -> finds userId 42
```

Simple to reason about and easy to invalidate (delete the session record, and it's immediately dead everywhere) — but requires server-side state, which complicates horizontal scaling: every server instance needs access to the same session store (a shared Redis instance, commonly) rather than keeping sessions in each instance's own memory.

## Token-based authentication (JWT)
<!-- bite: e1621671-f3d3-47e0-b7a2-7f451dfda547 -->

On login, the server issues a signed token (see [[05-digital-signatures-and-pki|digital-signatures-and-pki]] for the signing mechanism) containing the user's identity directly in its payload. The server verifies the signature on each request but doesn't need to look anything up in a session store — the token itself carries everything needed.

```text
Login -> server signs a token: { userId: 42, exp: <timestamp> }, signed with server's secret/private key
       -> client stores token (commonly in memory or a cookie), sends it with every request

Later request -> server verifies the signature is valid and not expired -> trusts the payload, no DB lookup needed
```

Stateless — any server instance can verify a token without needing shared state, which is why this pattern is common in horizontally-scaled and microservice architectures. The tradeoff: a token can't be individually revoked before it expires without adding back some form of server-side state (a blocklist of revoked token IDs) — which partially reintroduces the statefulness this approach was meant to avoid, and is a common design wrinkle in real systems.

## OAuth 2.0 — delegated authorization, not just "login with X"
<!-- bite: 65792fb3-8410-4ae5-993a-1f4a84549f05 -->

OAuth solves a different problem than "who is this user": it lets a user grant a third-party application limited access to their data on another service, without ever sharing their actual password with that third party. "Login with Google" is OAuth used specifically for identity (technically layered with OpenID Connect on top of OAuth for that identity piece).

**Authorization Code flow** (the standard for a server-side web app):
```text
1. User clicks "Login with Google" -> redirected to Google's login/consent screen
2. User approves -> Google redirects back to your app with a temporary authorization code
3. Your server exchanges that code (server-to-server, using a client secret) for an access token
4. Your server uses the access token to fetch the user's profile info from Google's API
```

The authorization code is exchanged for a token in a direct server-to-server call specifically so the actual access token never passes through the user's browser, where it would be more exposed. This is the detail that separates the secure Authorization Code flow from less secure, largely deprecated alternatives (the old Implicit flow returned the token directly to the browser).

**Client Credentials flow** — for service-to-service authentication with no user involved at all: a backend service authenticates directly using its own client ID/secret to get a token representing itself, not a user.

## API keys — simple, coarse-grained authentication
<!-- bite: 8ff45c48-47d8-44dd-b7b1-1832585b07ea -->

A static, long-lived secret string identifying a calling application (not an individual user), sent with each request, commonly used for server-to-server API access where the OAuth flow's user-consent step doesn't apply. Coarse-grained by nature — an API key typically identifies "which application/client is calling," not "which specific user," and doesn't expire the way a token does, which is exactly why leaked API keys are a common, serious incident category (see key management in [[06-cryptographic-attacks-and-best-practices|cryptographic-attacks-and-best-practices]]).

## Single Sign-On (SSO)
<!-- bite: 0099edee-485b-4c97-bd6f-6bbbfcdaa637 -->

Lets a user authenticate once and gain access across multiple related applications/services without logging in separately to each — commonly built on top of OAuth/OpenID Connect or SAML, with a central identity provider that every application trusts and delegates authentication to, rather than each application managing its own user credentials independently.

## Choosing between session-based and token-based
<!-- bite: b36d1280-3189-4317-9049-b3ecc28ad203 -->

| | Session-based | Token-based (JWT) |
|---|---|---|
| Server state | Required (session store) | Stateless (verify signature only) |
| Revocation | Immediate (delete the record) | Hard without adding back state |
| Horizontal scaling | Needs a shared session store | Naturally scales — any instance can verify |
| Common fit | Traditional server-rendered apps | APIs, microservices, mobile/SPA clients |

## Gotchas
<!-- bite: 1c4ad149-bd6d-427a-87cf-d019e1f85b3f -->

- Storing a JWT in `localStorage` instead of an `HttpOnly` cookie exposes it to theft via any XSS vulnerability (see [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index|input-validation-and-output-encoding]]) — a genuinely common, serious real-world mistake covered from the cookie-flag side in [[02-secure-authentication|secure-authentication]].
- Treating a JWT's *expiration* as the only thing standing between a stolen token and account takeover is a real risk — short expiration times plus a refresh-token pattern (a separate, longer-lived token used only to obtain new short-lived access tokens) limits the exposure window of a stolen access token.
- OAuth's Authorization Code flow requires validating the `state` parameter to prevent CSRF-style attacks against the login flow itself — skipping this check is a known, concrete vulnerability class in OAuth implementations.

## Related
<!-- bite: 3af38fd5-b716-4ad4-9683-e3fc7c17aceb -->
- [[backend/05-auth/02-authorization|authorization]]
- [[02-secure-authentication|secure-authentication]]
- [[05-digital-signatures-and-pki|digital-signatures-and-pki]]

## Seen in the wild
<!-- bite: 02778dc6-188a-4b57-98cb-b82c0362604e -->
- [[projects/nextvibe/learning/backend/02-auth|nextvibe]] — auth built out on NestJS
- [[projects/arete/learning/backend/04-auth|arete]] — the same problem, different constraints
- [[concepts/interview/01-apis-auth-and-practices|Interview: Q3–Q4]] — sessions vs JWT, OAuth + PKCE
