# 05 — Auth

Two different questions that get collapsed into one word: **authentication** (who are you) and **authorization** (what may you do). Different failure modes, different status codes, different places in [[backend/01-foundations/03-the-request-lifecycle|the request lifecycle]].

1. [[backend/05-auth/01-authentication-flows|Authentication Flows]] — **[Intermediate]** — sessions vs tokens, JWT's real tradeoffs, password storage
2. [[backend/05-auth/02-authorization|Authorization]] — **[Intermediate]** — RBAC/ABAC/ReBAC, and why authz ≠ authn
3. [[backend/05-auth/03-oauth-provider-integrations|OAuth Provider Integrations]] — **[Advanced]** — the flows in practice

## The three rules
1. **Authorise at the data layer, on every request.** Hiding a button is UX. The most common real authorization bug is **IDOR** — accepting a resource ID from the user and returning it without checking ownership.
2. **Sessions vs JWT is a revocation-vs-lookup tradeoff.** Sessions revoke instantly and cost a lookup; JWTs need no lookup and **cannot be revoked** before expiry. Most applications should use sessions; JWTs shine for service-to-service and short-lived access tokens paired with a revocable refresh token.
3. **Pin the JWT algorithm server-side.** Never trust the token's own `alg` header — that's `alg: none` and algorithm-confusion attacks. And a JWT is **signed, not encrypted**: anyone can read the payload.

## Related
- [[backend/README|Backend course]]
- [[concepts/interview/01-apis-auth-and-practices|Interview: auth questions]] — sessions vs JWT, OAuth + PKCE, password storage
- [[cybersecurity/04-web-security/README|Web Security]] · [[foundations/networking/12-tls-and-transport-security|TLS]]
- [[projects/gees-arise/learning/04-supabase|gees-arise: Postgres RLS]] — authorization enforced at the data layer, for real
