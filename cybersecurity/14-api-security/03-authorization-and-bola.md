# Authorization and BOLA

**[Intermediate → Advanced]** — the defining vulnerability class of API security: the API knows who you are and forgets to check what you're allowed to touch.

## The kid version first

Authentication proved you're a logged-in user. **Authorization is the separate check that you're allowed to access *this specific thing*.** The classic API bug is skipping it: the app checks you're logged in, then hands you whatever object ID you asked for — so you change `/api/orders/123` to `/api/orders/124` and read a stranger's order.

That single mistake — trusting the ID in the request — is the **number one API vulnerability in the world**, and it's an entire family of related failures.

## Why authorization is *the* API problem

Three of the OWASP API Top 10 are authorization failures (API1, API3, API5), and together they dominate real breaches. The reason is structural:

- **Authentication is generic** — "is this token valid?" — so frameworks and libraries handle it well
- **Authorization is application-specific** — "may *this user* touch *this order*?" — which **no framework can decide for you**. It's per-object, per-endpoint business logic you must write on every route, forever

So authZ is the thing developers forget, on the new endpoint, under deadline, every time. It doesn't show up in testing (the developer tests as themselves, and they *are* allowed) — it only appears when someone tries an ID that isn't theirs.

## API1: Broken Object Level Authorization (BOLA / IDOR)

**The #1 API vulnerability.** The API uses an ID from the request to fetch an object, without checking the caller *owns* or *may access* that object:

```
   GET /api/orders/123        ← my order. Works.
   GET /api/orders/124        ← NOT my order. Also works. ← BOLA.
```

Also called **IDOR** (Insecure Direct Object Reference). It's devastating because it's trivial to find (increment a number) and it exposes *other users' data at scale* — a script walking the IDs dumps the whole database.

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

BOLA is about *objects* ("that order"); **BFLA is about *actions/endpoints*** ("that admin function"). A regular user calls an admin-only endpoint that only *hid* the button, never checked the role:

```
   POST /api/admin/deleteUser     ← the UI hides this from me. The API doesn't check my role.
```

**Client-side hiding is not authorization** → [[mobile/12-security-on-device|the client is untrusted]]. Every privileged endpoint must verify the caller's role/permission server-side. Attackers find these by guessing admin routes, changing HTTP methods (`GET` is checked, `DELETE` isn't), and reading the client's own code for hidden calls.

## API3: Broken Object Property Level Authorization

Authorization at the *field* level — two sides of one coin, both from serving raw objects:

**Excessive Data Exposure** — the API returns the *whole* object and trusts the client to show only the safe fields. But the client is untrusted, so the raw response leaks what the UI hid:
```json
GET /api/users/me
{ "name": "Ada", "email": "...", "passwordHash": "...", "isAdmin": false, "ssn": "..." }
                                    ↑ the app shows name only. The API sent everything.
```
**Fix: return only the fields the caller needs** (explicit response DTOs/serializers, never "dump the model"). Filter on the *server*.

**Mass Assignment** — the inverse: the API blindly binds the request body to the object, so the client sets fields it shouldn't:
```json
PATCH /api/users/me
{ "name": "Ada", "isAdmin": true }      ← the client added isAdmin. The API set it. Privilege escalation.
```
**Fix: allowlist the fields a client may set** (explicit input schemas / DTOs, never `Object.assign(user, req.body)`). Bind only what you meant to expose → [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|input validation]].

## The unifying principle

Every one of these is the same mistake in a different place: **trusting input the client controls, instead of enforcing on the server what the caller is actually allowed to do and see.**

- BOLA — trusts the object *ID*
- BFLA — trusts that the client won't call the *endpoint*
- Mass assignment — trusts the request *body's fields*
- Excessive exposure — trusts the client to *hide* fields

**The server owns authorization. Every object, every function, every field, every request.** Design it as explicit allowlists (which objects this user may access, which fields they may set, which they may see) rather than blocklists you'll forget to update → [[backend/05-auth/02-authorization|authorization patterns]].

## Testing for it

This class is *findable*, which is why pentesters love it and you should self-test:

- **Two accounts** — log in as user A, capture a request, replay it as user B (swap the token, keep A's object ID). If it works, that's BOLA
- **Increment IDs** — walk `/orders/1`, `/2`, `/3`
- **Guess admin routes** and change HTTP methods
- **Diff responses against the UI** — fields in the JSON that the app never shows = excessive exposure
- **Add fields to request bodies** — `isAdmin`, `role`, `verified` — and see if they stick
- Tools: Burp Suite (with the Autorize extension for automated authZ testing) → [[cybersecurity/02-ethical-hacking/08-common-tools|tools]]

## Key insight

**API security's defining weakness is authorization, because it's per-object, per-endpoint, per-field business logic no framework writes for you — so it's the thing forgotten on every new route, invisible in the developer's own testing, and trivial for an attacker to find by changing an ID.** BOLA, BFLA, mass assignment and excessive data exposure are one mistake wearing four hats: trusting client-controlled input instead of enforcing on the server what the caller may do and see. Scope every query to the user and allowlist every field, and most of the OWASP API Top 10 disappears.

## Related
- [[cybersecurity/14-api-security/01-what-makes-api-security-different|what makes API security different]] — why authZ dominates
- [[cybersecurity/14-api-security/04-input-validation-and-injection|input validation and injection]] — the other trust-the-input failures
- [[backend/05-auth/02-authorization|authorization]] — building it right
- [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation concepts]] — broken access control, generally

*Source: [reference] — OWASP API1/API3/API5. Aug 2026.*
