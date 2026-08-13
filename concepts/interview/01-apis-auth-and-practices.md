# Concepts Interview — APIs, Auth & Practices

From [[concepts/01-backend/README|01-backend]], [[concepts/03-design-patterns/README|03-design-patterns]], [[concepts/04-best-practices/README|04-best-practices]].

---

### Q1. [Beginner→Intermediate] 🔥 What makes an API RESTful, and does it matter?

**Strong answer covers:** resources identified by URIs, standard methods with their standard meanings, stateless requests, and representations. Most "REST" APIs are really RPC over HTTP with nice URLs — actual HATEOAS is rare and mostly not worth it.

**Have an opinion:** the parts of REST that genuinely pay off are **using HTTP correctly** — right status codes, right methods, cacheability, and idempotency semantics — because that's what lets every intermediary (browsers, CDNs, proxies, client libraries) behave sensibly without knowing your domain. The parts that don't pay off are the purity arguments.

**Status codes worth getting right:** 200 vs 201 (created, with a `Location`) vs 204 (no content); **400 vs 422** (malformed vs semantically invalid); **401 vs 403** (not authenticated vs authenticated-but-not-allowed — mixed up constantly); 409 (conflict); 429 (rate limited, with `Retry-After`).

---

### Q2. [Intermediate] 🔥 Which methods are safe and idempotent, and why does it matter operationally?

**Strong answer covers:** **safe** (no side effects): `GET`, `HEAD`, `OPTIONS`. **Idempotent** (N calls = 1 call): `GET`, `HEAD`, `PUT`, `DELETE`. **Neither:** `POST`, `PATCH`.

**Why it matters:** it determines what clients, proxies, and load balancers may **retry automatically**. And a retry is not optional — a network failure after the server processed the request is indistinguishable from one before it. So the client *must* retry, and the server *must* make retrying safe.

**The mechanism to name:** **idempotency keys.** The client sends a unique key; the server stores key → result on first execution and replays the stored result on retry. This is why Stripe's API works the way it does, and it's the practical form of "exactly-once is impossible; use at-least-once plus an idempotent receiver." → [[architecture/04-distributed-systems/10-distributed-transactions|distributed transactions]]

---

### Q3. [Intermediate] 🔥 Sessions vs JWT — which and why?

**Strong answer covers the actual tradeoff, which is *revocation vs. lookup*:**

- **Server-side sessions** — the client holds an opaque ID; state lives on the server. **Revocation is instant** (delete the row). Costs a lookup per request, and needs shared storage across instances.
- **JWT** — the token *is* the state, signed. No lookup needed, so it scales statelessly across services. **But you cannot revoke it** — it's valid until it expires, so a stolen token is usable for its whole lifetime, and a logout doesn't actually log anyone out.

**The honest position:** most applications should use **sessions**. JWTs are popular far beyond the cases that need them. They genuinely shine for service-to-service auth and short-lived access tokens paired with a refresh token — where the refresh token *is* revocable, so you get statelessness with a revocation point.

**Mistakes to name:**
- Accepting the `alg` header from the token (`alg: none`, or algorithm confusion where an RS256 verifier is tricked into HMAC with the public key). **Pin the algorithm server-side.**
- Putting sensitive data in the payload — a JWT is **signed, not encrypted**; anyone can base64-decode it.
- Storing tokens in `localStorage`, which is readable by any XSS. `httpOnly` cookies with `SameSite` are safer, at the cost of needing CSRF protection.

---

### Q4. [Intermediate] 🔥 Explain the OAuth authorization code flow with PKCE. What problem does PKCE solve?

**Strong answer covers:** the user is redirected to the provider, authenticates there, and the provider redirects back with a short-lived **authorization code**; the client then exchanges that code (plus its secret) for tokens on a **back channel**. The point of the two-step dance is that the access token never travels through the browser's address bar or history.

**PKCE:** a public client (mobile app, SPA) can't hold a secret — anyone can decompile the app. So an attacker who intercepts the redirect could exchange the code themselves. PKCE fixes it: the client generates a random `code_verifier`, sends its hash (`code_challenge`) with the initial request, and must present the original verifier at exchange time. The intercepted code alone is useless.

**PKCE is now recommended for *all* clients, including confidential ones.** The implicit flow is deprecated — it returned tokens directly in the URL fragment.

**Distinction to make:** **OAuth is authorisation** (delegated access to a resource); **OIDC is authentication** (who the user is) layered on top, adding the `id_token`. "Login with Google" is OIDC. Getting this wrong is a common tell.

---

### Q5. [Intermediate] Authentication vs authorization, and how do you model authorization?

**Strong answer covers:** authn = *who are you*; authz = *what may you do*. Separate concerns, separate failure modes: 401 vs 403.

**Models:** **RBAC** (roles → permissions) — simple, most common, degrades into role explosion when rules get contextual. **ABAC** (rules over attributes of user/resource/environment) — expressive, harder to reason about and audit. **ReBAC** (relationship-based, Google Zanzibar / OpenFGA) — "can edit if in the document's editor set" — the right model for anything with sharing and hierarchies.

**The rule that matters more than the model:** **authorise on the server, at the data access layer, every time.** Hiding a button is UX, not security. The single most common real-world authorization bug is **IDOR** — accepting a resource ID from the user and returning it without checking ownership. → [[cybersecurity/04-web-security/README|web security]]

---

### Q6. [Intermediate] 🔥 How do you store passwords?

**Strong answer covers:** a **slow, salted, memory-hard hash** — **Argon2id** preferred, then **scrypt** or **bcrypt**. Never MD5/SHA-256 (far too fast — a GPU does billions per second), never encryption (reversible by definition), never plaintext.

- **Salt** (unique per user, stored alongside) defeats rainbow tables and stops identical passwords producing identical hashes.
- **Work factor** is tunable so you can raise the cost as hardware improves.
- **Memory-hardness** (Argon2/scrypt) is what specifically defeats GPU and ASIC cracking, which is why it's preferred over bcrypt now.

**Details that score:** compare with a **constant-time** comparison to avoid timing attacks. Check candidate passwords against a breached-password list (HIBP's k-anonymity API) — that's far more effective than complexity rules, which mostly produce `Password1!`. And the login response must not reveal whether the *username* existed — same message, same timing.

---

### Q7. [Intermediate] Which design patterns do you actually use, and which are overrated?

**Strong answer covers real usage:** **Strategy** (swap an algorithm — usually just a lambda now), **Adapter** (wrap a third-party API so it doesn't leak through your codebase), **Factory** (non-trivial construction), **Observer** (events), **Decorator** (layered behaviour — middleware is this), **Builder** (many optional parameters).

**Overrated, and say so with a reason:** **Singleton** — it's global mutable state with better PR; it makes testing hard and hides dependencies. Dependency injection gives you one instance without the coupling. **Visitor** — largely obsolete now that sealed types plus pattern matching express the same thing directly.

**The framing that scores:** patterns are **vocabulary for structures that already exist**, not a shopping list. Applying a pattern you don't need is how you get an `AbstractSingletonProxyFactoryBean`. The right instinct is to notice you've written a pattern, then name it — not to choose one up front.

---

### Q8. [Intermediate] 🔥 What's your testing philosophy?

**Strong answer covers:** many fast unit tests, fewer integration tests, few end-to-end tests — but **the reason** matters more than the shape: fast tests get run, and a test suite people skip is worth nothing.

**Opinions worth holding:**
- **Test behaviour, not implementation.** A test that breaks on every refactor is a liability — it's asserting *how* rather than *what*.
- **Mock what you don't own** (external APIs); **use the real thing for what you do** (your database, via Testcontainers). Over-mocking gives you a suite that passes while the system is broken.
- **Coverage is a smoke detector, not a goal.** 100% coverage with no assertions is possible; 60% on the code that handles money beats 95% spread evenly.
- **Every bug fix gets a test that fails before the fix.** That's how a suite accumulates value tied to real failures rather than imagined ones.

**Bonus:** property-based testing (jqwik/QuickCheck) for anything with an invariant — it generates the edge cases you didn't think of, which is precisely the class you keep shipping.

---

### Q9. [Beginner→Intermediate] What makes a good pull request?

**Strong answer covers:** **small and single-purpose** — one logical change. A 2,000-line PR gets rubber-stamped; a 200-line PR gets read, and being read is the entire point.

The description says **why**, not what (the diff already shows what) — the problem, the approach, what was considered and rejected. Self-review before requesting review. Keep refactors in separate commits (or PRs) from behaviour changes, so the reviewer isn't diffing formatting against logic.

**As a reviewer:** distinguish blocking issues from preferences (say which). Ask questions rather than issuing commands — *"what happens if this is null?"* teaches; *"add a null check"* doesn't. Approve when it's better than what's on main, not when it's perfect. → [[concepts/04-best-practices/02-pr-structure|PR structure]]

---

### Q10. [Intermediate] What's your approach to error handling in an API?

**Strong answer covers:** fail fast and loudly internally; return something useful and non-leaky externally.

- **Consistent error shape** across every endpoint — a machine-readable code, a human message, and a request/correlation ID the user can quote in a support ticket. RFC 9457 (`application/problem+json`) is a reasonable standard to point at.
- **Never leak internals** — a stack trace in a response is an information-disclosure vulnerability and tells an attacker your framework and version.
- **Distinguish client errors from server errors properly.** Returning 200 with `{"error": ...}` breaks every client library, retry policy, and monitor.
- **Log with context** — correlation ID, user, inputs. An error log without enough context to reproduce the request is noise.
- **Don't swallow exceptions.** The most expensive bugs are the ones that were caught and ignored.
