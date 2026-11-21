---
id: e1794138-e55b-4c6e-893e-ff664e0b1906
---

# Validation and DTOs

**Every byte entering your process from outside is untrusted and untyped.** A JSON body, a query string, a header, a file, a message from a queue. Your type system believes whatever you tell it about that data, and it is wrong until something checks.

## Parse, don't validate
<!-- bite: 2531facc-acf0-4f78-b923-379617942a64 -->

**The distinction that makes everything else follow:**

```text
validate:  is this data ok?   → returns bool, data stays untyped
parse:     turn this into a trusted type, or fail  → returns Order | Error
```

**Validation throws information away.** You checked that `email` was present, and afterwards you still have an untyped blob — so the next function checks again, and the one after that forgets to.

**Parsing preserves it.** After parsing you hold an `Order`, and the type system carries the guarantee for you.

```ts
const parsed = OrderSchema.safeParse(req.body);   // ✓ Order | Error
if (!parsed.success) return res.status(400).json(problem(parsed.error));
create(parsed.data);                              // typed from here on
```

**The practical test: after your check, can a downstream function still receive bad data?** If yes, you validated. If it's a type error to even try, you parsed.

## The boundary is the only place
<!-- bite: ea8f97a0-db26-44ec-b059-46e4a1537f54 -->

**Do it once, at the edge, and never again.** Every layer that re-checks is a layer that can disagree with the others.

```text
HTTP request → [PARSE HERE] → typed command → service → repository → DB
```

**This is why type annotations alone are not enough**, in any language:

- **TypeScript** — `const u: User = await res.json()` is a lie the compiler believes → [[frontend/interview/02-javascript-and-typescript|TS]]
- **Python** — hints are erased at runtime → [[languages/06-python/08-typing-and-type-hints|typing]]
- **C#** — nullable reference types are warnings, not enforcement → [[languages/07-csharp/02-the-type-system|note 02]]
- **Go / Rust** — `json.Unmarshal` and `serde` populate zero values or fail; **you still need range and business rules**

**The one framework where this is structural:** FastAPI, because the Pydantic model that validates *is* the model that generates the schema, so they cannot drift → [[backend/frameworks/fastapi/01-fastapi|FastAPI]].

## What a DTO is for
<!-- bite: 89fe1cae-accd-49f9-94c6-483881b59946 -->

**A DTO is the shape of the wire, not the shape of your domain.** Keeping them separate buys you three things:

**You can change the domain without breaking clients.** Rename a field internally; the DTO mapping absorbs it.

**You can't leak what you didn't mean to.** Returning your database entity directly is how `passwordHash`, `internalNotes` and `isAdmin` end up in a public response. **This is a genuine and common breach path** → [[cybersecurity/04-web-security/index|web security]].

**Input and output shapes differ, and should.** `CreateOrder` has no `id`; `Order` does. One type doing both means optional fields everywhere and no useful guarantees.

**Mass assignment** is the attack this prevents: binding a request body straight onto an entity lets a caller set `role: "admin"` if you forgot to exclude it. **An explicit DTO makes the omission impossible rather than merely unlikely.**

## What to actually check
<!-- bite: a00f0d46-a9dd-44f5-ab2d-2299ffc13224 -->

**Structural** — required fields, types, shapes.
**Range** — lengths, bounds, formats, enum membership.
**Business rules** — "delivery date is in the future", "quantity ≤ stock".

**The split that matters:** structural and range checks belong at the boundary. **Business rules that need database state belong in the service**, because the boundary shouldn't be querying.

**And decide what "unknown field" means.** Silently ignoring extra fields is forgiving and hides client bugs; rejecting them is strict and breaks on additive changes. **Pick deliberately** — most public APIs ignore, most internal ones reject.

## Error responses
<!-- bite: 92df31dc-9fe8-4e94-bf7f-b5fdd9951c16 -->

**One shape, everywhere** — [[backend/06-cross-cutting/03-error-handling|note 03]] covers the mechanism. For validation specifically:

```json
{
  "type": "https://example.com/problems/validation",
  "title": "Validation failed",
  "status": 400,
  "errors": { "email": ["is not a valid address"], "quantity": ["must be > 0"] }
}
```

**Report every failure at once**, not the first. A client that must submit five times to discover five problems is a bad API — and a form that can only highlight one field at a time is a bad UI.

**Never echo the input back in the error message** without encoding it. That's reflected XSS in an error handler, which is a real and frequently-missed vector.

## Related
<!-- bite: 106415f4-80db-4269-80b8-2ffa21b7787c -->
- [[backend/06-cross-cutting/03-error-handling|error handling]] — the response shape
- [[backend/02-api-design/index|API design]] — contracts
- [[backend/frameworks/cross-language-recipes|cross-language recipes]] — this in six stacks
- [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index|input validation]] — the security view

## About this lesson
<!-- bite: 0bbf9973-2c24-4f65-994e-e9c2d818a07d -->

**Level:** Intermediate. **Covers:** Parse, don't validate — and why the boundary is the only place this can be done.

*Source: [reference] — written Aug 2026.*
