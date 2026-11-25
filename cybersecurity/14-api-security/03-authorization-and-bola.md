---
id: 91c7789e-00eb-4bec-81de-86be8d7129d9
---

# Authorization and BOLA

**Authorization is checking whether a logged-in user may see or change one particular thing — and forgetting that check is the most common API bug in the world.**

## Before you start
<!-- bite: a1fc8be5-df00-4cb5-b2ab-01ceb03e5151 -->

You should have:

- Why authorization dominates the OWASP API Top 10 → [[cybersecurity/14-api-security/01-what-makes-api-security-different|what makes API security different]].
- Authentication, since authZ builds on a proven identity → [[cybersecurity/14-api-security/02-authentication-for-apis|authentication for APIs]].
- The general authorization patterns → [[backend/05-auth/02-authorization|authorization]].

After this lesson you will be able to:

1. Explain why authorization is application-specific logic no framework writes for you.
2. Recognise the four failures — BOLA, BFLA, mass assignment, excessive data exposure — as one mistake in four places.
3. Apply the reliable fixes: scope every query to the user, allowlist every settable and returned field.

**Study route.** Read the kid version and why-authZ-is-the-problem, then each named failure, then the unifying principle — that's the one idea to keep. The practice task is a two-account BOLA test.

## What authorization is, and why it's the API problem
<!-- bite: 9ac66380-dadf-45e7-8944-382346c976e3 -->

Authentication proves you're a logged-in user; authorization is the *separate* check that you're allowed to access *this specific* thing. It's the defining weakness of API security because it's application-specific: "is this token valid?" is generic and frameworks handle it, but "may *this user* touch *this order*?" is per-object, per-endpoint business logic you must write on every route, forever. It doesn't show up in the developer's own testing — they test as themselves, and they *are* allowed — so it only appears when someone tries an ID that isn't theirs. Three of the OWASP API Top 10 (API1, API3, API5) are this one failure, wearing different hats.

## The kid version
<!-- bite: 2f1aed21-feba-47b0-9475-d129073c6bc8 -->

Authentication proved you're a logged-in user. **Authorization is the separate check that you're allowed to access *this specific thing*.** The classic API bug is skipping it: the app checks you're logged in, then hands you whatever object ID you asked for — so you change `/api/orders/123` to `/api/orders/124` and read a stranger's order.

That single mistake — trusting the ID in the request — is the **number one API vulnerability in the world**, and it's an entire family of related failures.

## Why authorization is *the* API problem
<!-- bite: e8118c3c-5d3a-4b94-bf5a-97d3cfccd1f1 -->

Three of the OWASP API Top 10 are authorization failures (API1, API3, API5), and together they dominate real breaches. The reason is structural:

- **Authentication is generic** — "is this token valid?" — so frameworks and libraries handle it well
- **Authorization is application-specific** — "may *this user* touch *this order*?" — which **no framework can decide for you**. It's per-object, per-endpoint business logic you must write on every route, forever

So authZ is the thing developers forget, on the new endpoint, under deadline, every time. It doesn't show up in testing (the developer tests as themselves, and they *are* allowed) — it only appears when someone tries an ID that isn't theirs.

## API1: Broken Object Level Authorization (BOLA / IDOR)
<!-- bite: 60f9a636-f224-4d93-b1b4-46579849a4e0 -->

**The #1 API vulnerability.** The API uses an ID from the request to fetch an object, without checking the caller *owns* or *may access* that object:

```text
   GET /api/orders/123        ← my order. Works.
   GET /api/orders/124        ← NOT my order. Also works. ← BOLA.
```

Also called **IDOR** (Insecure Direct Object Reference). It's devastating because it's trivial to find (increment a number) and it exposes *other users' data at scale* — a script walking the IDs dumps the whole database.

## Fixing BOLA
<!-- bite: a793ed6d-45b7-4956-934a-c1f41ba7413d -->

**The fix — and it must be on every object access:**
```python
order = db.get_order(order_id)
if order.owner_id != current_user.id:      # ← THE CHECK. On every endpoint.
    return 403
```

**Two things that don't fix it:**
- **UUIDs instead of sequential IDs** — harder to *guess*, but the check is still missing; a leaked or referenced UUID still works. **Unguessable IDs are defence in depth, not authorization.** Add the check anyway
- **Hiding the endpoint** — obscurity isn't authorization

**The reliable pattern: scope the query to the user.** `db.get_order(order_id, owner_id=current_user.id)` returns nothing if it isn't theirs — the check is *inside the data access*, so it can't be forgotten per-endpoint. Enforce ownership at the query layer, not as an easily-skipped `if`.

## API5: Broken Function Level Authorization (BFLA)
<!-- bite: 1712c079-2a7b-4959-8554-a1e3b6b85a40 -->

BOLA is about *objects* ("that order"); **BFLA is about *actions/endpoints*** ("that admin function"). A regular user calls an admin-only endpoint that only *hid* the button, never checked the role:

```text
   POST /api/admin/deleteUser     ← the UI hides this from me. The API doesn't check my role.
```

**Client-side hiding is not authorization** → [[mobile/12-security-on-device|the client is untrusted]]. Every privileged endpoint must verify the caller's role/permission server-side. Attackers find these by guessing admin routes, changing HTTP methods (`GET` is checked, `DELETE` isn't), and reading the client's own code for hidden calls.

## API3: Broken Object Property Level Authorization
<!-- bite: 3ab4e53e-73d3-450f-a7a1-f4f6097661c9 -->

Authorization at the *field* level — two sides of one coin, both from serving raw objects:

**Excessive Data Exposure** — the API returns the *whole* object and trusts the client to show only the safe fields. But the client is untrusted, so the raw response leaks what the UI hid:
```json
GET /api/users/me
{ "name": "Ada", "email": "...", "passwordHash": "...", "isAdmin": false, "ssn": "..." }
                                    ↑ the app shows name only. The API sent everything.
```
**Fix: return only the fields the caller needs** (explicit response DTOs/serializers, never "dump the model"). Filter on the *server*.

## API3: Mass Assignment
<!-- bite: 25ac5f02-668f-4fe5-b97f-16929527fef2 -->

**Mass Assignment** — the inverse of excessive exposure: the API blindly binds the request body to the object, so the client sets fields it shouldn't:
```json
PATCH /api/users/me
{ "name": "Ada", "isAdmin": true }      ← the client added isAdmin. The API set it. Privilege escalation.
```
**Fix: allowlist the fields a client may set** (explicit input schemas / DTOs, never `Object.assign(user, req.body)`). Bind only what you meant to expose → [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index|input validation]].

## The unifying principle
<!-- bite: da2e32fb-aca6-44e3-bed0-ca0804b44d00 -->

Every one of these is the same mistake in a different place: **trusting input the client controls, instead of enforcing on the server what the caller is actually allowed to do and see.**

- BOLA — trusts the object *ID*
- BFLA — trusts that the client won't call the *endpoint*
- Mass assignment — trusts the request *body's fields*
- Excessive exposure — trusts the client to *hide* fields

## One mistake, four places
<!-- bite: 36c72e4a-eb79-4112-9b4b-8c9b9183578a -->

![The four API authorization failures as one root cause in four places: BOLA trusts the object ID in the request, BFLA trusts that the client won't call a privileged endpoint, mass assignment trusts the fields in the request body, and excessive data exposure trusts the client to hide fields — all four are the server trusting client-controlled input instead of enforcing what the caller may do and see.](../images/api-authz-family.svg)

**The server owns authorization. Every object, every function, every field, every request.** Design it as explicit allowlists — which objects this user may access, which fields they may set, which they may see — rather than blocklists you'll forget to update → [[backend/05-auth/02-authorization|authorization patterns]].

## Testing for it
<!-- bite: f7ac42b9-8c60-45ce-a549-0c0237da3714 -->

This class is *findable*, which is why pentesters love it and you should self-test:

- **Two accounts** — log in as user A, capture a request, replay it as user B (swap the token, keep A's object ID). If it works, that's BOLA
- **Increment IDs** — walk `/orders/1`, `/2`, `/3`
- **Guess admin routes** and change HTTP methods
- **Diff responses against the UI** — fields in the JSON that the app never shows = excessive exposure
- **Add fields to request bodies** — `isAdmin`, `role`, `verified` — and see if they stick
- Tools: Burp Suite (with the Autorize extension for automated authZ testing) → [[cybersecurity/02-ethical-hacking/08-common-tools|tools]]

## Key insight
<!-- bite: 491e47c6-84c2-4835-9817-53ac6e760198 -->

**API security's defining weakness is authorization, because it's per-object, per-endpoint, per-field business logic no framework writes for you — so it's the thing forgotten on every new route, invisible in the developer's own testing, and trivial for an attacker to find by changing an ID.** BOLA, BFLA, mass assignment and excessive data exposure are one mistake wearing four hats: trusting client-controlled input instead of enforcing on the server what the caller may do and see. Scope every query to the user and allowlist every field, and most of the OWASP API Top 10 disappears.

## Terms used in this lesson
<!-- bite: c8b9e61a-1511-4be3-9a80-2ed6adc4888a -->

1. **Authorization (authZ)**: The check that a specific authenticated user may access a specific object, endpoint or field.
2. **BOLA / IDOR**: Broken Object Level Authorization (a.k.a. Insecure Direct Object Reference) — fetching an object by a request ID without checking the caller owns it. The #1 API bug.
3. **BFLA**: Broken Function Level Authorization — calling a privileged endpoint whose access was only hidden in the UI, never checked server-side.
4. **Mass assignment**: Binding a request body straight onto an object so the client can set fields it shouldn't (e.g. `isAdmin: true`).

## Terms used in this lesson: the fixes
<!-- bite: 295c6a4a-2b94-4666-98e9-fb020a875c5a -->

5. **Excessive data exposure**: Returning the whole object and trusting the client to show only safe fields, so the raw JSON leaks the rest.
6. **DTO / serializer**: An explicit shape for what a request may set (input DTO) or a response may return (serializer) — the allowlist that prevents mass assignment and over-exposure.
7. **Scope the query to the user**: Enforcing ownership *inside* the data access (`get_order(id, owner_id=current_user.id)`) so it can't be forgotten per-endpoint.
8. **Allowlist**: Defining explicitly what's permitted (fields, objects, actions) and rejecting everything else — the opposite of a blocklist you'll forget to update.

## Check your understanding
<!-- bite: 61024936-85f0-4617-b312-8120f800cd60 -->

Try each one before you open the answer.

1. <!-- q: mcq id="40cead8c" -->
   An endpoint `GET /api/invoices/{id}` checks you're logged in, then returns the invoice with that id. You change your id to a neighbouring number and see someone else's invoice. What is this, and what's the *reliable* fix?

   - [ ] XSS; output-encode the response
   - [x] BOLA; scope the query to the user so ownership is enforced inside the data access
   - [ ] Rate-limiting failure; add a throttle
   - [ ] CSRF; add a token

   <details><summary>Answer</summary>

   It's BOLA (IDOR) — the API trusts the object ID without checking ownership. The reliable fix is to scope the query to the user (`get_invoice(id, owner_id=current_user.id)`), so a non-owned id returns nothing. An `if owner != me` check works too but is easy to forget on the next endpoint; enforcing it at the query layer can't be skipped.

   </details>

2. <!-- q: mcq id="1410fe45" -->
   A developer switches sequential IDs to random UUIDs to "fix" BOLA. Why is that insufficient?

   - [ ] UUIDs are slower
   - [x] The ownership check is still missing — a leaked, logged or referenced UUID still returns the object; unguessable IDs are defence in depth, not authorization
   - [ ] UUIDs can't be used in URLs
   - [ ] It breaks the database

   <details><summary>Answer</summary>

   UUIDs make IDs harder to *guess*, but BOLA isn't a guessing problem — it's a missing-check problem. Any UUID that leaks (in a referrer, a log, a shared link, another API response) still works, because the server never verifies ownership. Add the check; treat unguessable IDs as a bonus layer, not the fix.

   </details>

3. <!-- q: gap id="d13b3fd2" answers="mass assignment|mass-assignment" -->
   An API binds the JSON body straight onto the user model, so a client that adds `"isAdmin": true` to its profile update becomes an admin. This privilege-escalation bug is called ___, and the fix is to allowlist the fields a client may set.

   <details><summary>Answer</summary>

   Mass assignment. The server trusted the request body's fields. The fix is an explicit input DTO / allowlist of settable fields, never `Object.assign(user, req.body)` — bind only what you meant to expose.

   </details>

4. <!-- q: mcq id="d22351e9" -->
   BOLA, BFLA, mass assignment and excessive data exposure are described as "one mistake wearing four hats." What is the single underlying mistake?

   - [ ] Weak encryption
   - [x] Trusting client-controlled input instead of enforcing on the server what the caller may do and see
   - [ ] Missing rate limits
   - [ ] Using JSON instead of XML

   <details><summary>Answer</summary>

   Each trusts something the client controls: BOLA the object ID, BFLA that the client won't call the endpoint, mass assignment the body's fields, excessive exposure the client to hide fields. The server owns authorization — every object, function, field and request — and the cure is explicit allowlists of what this user may access, set and see.

   </details>

5. <!-- q: open id="4b4c2991" -->
   Why do authorization bugs survive the developer's own testing but get caught by a pentester with two accounts?

   <details><summary>Answer</summary>

   The developer tests as themselves, requesting their own objects and endpoints — and they *are* authorized, so everything works and the missing check is invisible. The bug only manifests when someone accesses an object or function that isn't theirs. A pentester logs in as user A, captures a request, then replays it as user B keeping A's object ID (or guesses admin routes): if it succeeds, the server never checked ownership or role. That's why two-account, cross-user testing is essential and why automated scanners — which don't know who *should* access what — are worst at this class.

   </details>

## Practice — the two-account BOLA test
<!-- bite: 7eedadd5-8d14-4d4f-82e4-37f343d1fe9c -->

The signature API-security test, on an app you own or are authorised to test.

- Create two accounts, A and B, each with some data (an order, a profile, a document).
- Log in as A, capture a request that fetches A's object (note the object ID in the URL).
- Replay it with B's token but A's object ID (Burp's Autorize extension automates this). If B gets A's data, that's BOLA.
- Try adding `isAdmin`/`role` to a profile-update body (mass assignment), and diff a response's JSON against what the UI shows (excessive exposure).
- **Done when:** you've confirmed whether the app scopes queries to the user, and you can name any field the API returns or accepts that it shouldn't.

## Before moving on
<!-- bite: 213ac042-f6ae-4381-a54f-b67275a91ae4 -->

You should be able to explain why authorization is application-specific, recognise the four failures as one root cause, and apply the two reliable fixes — scope every query to the user, allowlist every field. Hold the unifying principle (the server owns authorization: every object, function, field, request) and most of the OWASP API Top 10 disappears.

Next: [[cybersecurity/14-api-security/04-input-validation-and-injection|input validation and injection]] — the *other* trust-the-input family, and SSRF, the API era's signature vulnerability.

## Related
<!-- bite: 6e783adc-b0b8-4b21-af6a-eee4313ef05e -->
- [[cybersecurity/14-api-security/01-what-makes-api-security-different|what makes API security different]] — why authZ dominates
- [[cybersecurity/14-api-security/04-input-validation-and-injection|input validation and injection]] — the other trust-the-input failures
- [[backend/05-auth/02-authorization|authorization]] — building it right
- [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation concepts]] — broken access control, generally

## About this lesson
<!-- bite: a52e1955-4845-41f4-a699-43cb609d3771 -->

**Level:** Intermediate → Advanced. **Covers:** the defining vulnerability class of API security: the API knows who you are and forgets to check what you're allowed to touch.

*Source: [reference] — OWASP API1/API3/API5. Aug 2026.*
