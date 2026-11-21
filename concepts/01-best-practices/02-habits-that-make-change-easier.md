---
id: 5312519b-08be-40e9-9834-f686de529234
---

# Habits That Make Change Easier

**[Beginner → Intermediate]** — seven small coding habits that separate code that merely works from code that survives fifty more changes. The kind of thing you absorb working alongside experienced engineers.

## The kid version first
<!-- bite: cc907852-2609-4b74-bf5d-e5e8984dfdef -->

Getting better as a developer isn't mostly about learning another language. Past a point, the biggest gains come from making your code **easier to understand, easier to change, and harder to break** — and experienced engineers rarely do this by writing *cleverer* code. They usually write *simpler* code. These are seven habits with one idea underneath them all: **make the next change easier**, because software gets hard not when you write the first version, but when the next fifty edits become harder than they should be.

This is the practical, at-the-keyboard companion to [[concepts/01-best-practices/01-clean-code/index|clean code]] and [[concepts/01-best-practices/07-solid-principles/index|SOLID]].

## 1. Keep the main path easy to follow
<!-- bite: c6db5107-7a1f-4227-a203-a6a5da245014 -->

Nesting conditions inside each other buries the actual work three levels deep. **Check the failure cases up front and return early**, so the main operation is visible:

```
BAD:  if user exists:
          if user is active:
              if user has permission:
                  do the actual thing      ← buried
GOOD: if not user exists:      return error
      if not user is active:   return error
      if not user has permission: return error
      do the actual thing                  ← front and centre
```

These are **guard clauses** (early return). The goal isn't to eliminate all nesting — it's to keep the *important path* of a function easy to see → [[programming-fundamentals/index|control flow]]. A reader should follow what a function *does* without mentally unwinding a pyramid of conditions.

## 2. Name things by their meaning
<!-- bite: f2ec80f5-856a-4b89-96b7-e5ab31cf8821 -->

Avoid `data`, `result`, `item`, `temp` when the actual meaning is more specific. `pendingOrder` and `processOrder()` tell you what you're dealing with; `data` and `process()` send you hunting elsewhere to find out.

**Good names reduce the detective work required to understand a codebase.** You don't need long names for everything — just make the important concepts obvious. This is the cheapest, highest-frequency readability win there is, and it's half of what "self-documenting code" actually means → [[concepts/01-best-practices/01-clean-code/index|clean code]], [[concepts/01-best-practices/05-documentation-practices|documentation]].

## 3. Keep external systems behind a boundary
<!-- bite: acf4c758-eca1-4c08-ad21-8639b9729221 -->

Your app talks to things you don't control — payment providers, email services, other APIs. If your code depends *directly* on their field names and shapes, then when they change, that change **ripples through your entire codebase** wherever those fields are used.

**Translate external data into your own model at the boundary**, once:

```
external response  →  [ boundary: map to OUR names/shapes ]  →  our clean model
   (their fields)          the ONE place their change costs us      (used everywhere)
```

This is the **anti-corruption layer**. When the external service changes, you fix one mapping instead of fifty call sites. It's the same instinct as [[cybersecurity/14-api-security/06-the-api-security-lifecycle|not trusting third-party responses]] and [[architecture/03-architectural-patterns/index|hexagonal architecture's ports and adapters]] — keep external complexity contained at the edge instead of spreading it inward.

## 4. Make invalid states harder to represent
<!-- bite: 0bf2be4f-5fe4-46ac-8bb7-70809337731f -->

A common trap: make almost everything optional/nullable, so every part of the code has to keep asking "does this exist? is it valid? can I do this?"

**Model the state so the invalid combinations can't be built.** If a "paid order" always has an order ID, a payment ID, and a paid status, define the type so those are *expected to exist* — then nothing downstream has to guess:

```
BAD:  Order { id?, paymentId?, status?, paidAt? }   → 16 combinations, most nonsense
GOOD: PaidOrder { id, paymentId, paidAt }           → the type says "this is paid"
```

You won't eliminate every error, but you make incorrect states much harder to create in the first place. **This is type-driven design**, and it's the practical version of what [[languages/08-swift/05-enums-and-pattern-matching|Swift enums]], [[languages/09-kotlin/03-types-and-data-classes|Kotlin sealed types]], [[languages/03-rust/06-structs-enums-and-pattern-matching|Rust's enums]] and [[data-analysis/03-metrics-and-kpis|precise definitions]] all enable — moving a class of bug from runtime to *unrepresentable*.

## 5. Separate decisions from actions
<!-- bite: 203a8cdf-0221-46c5-a020-cde9d68572ea -->

Mixing a business rule together with the database and email operations it triggers makes the *decision* hard to test on its own — you can't check "is this user eligible?" without hitting the database and sending mail.

**Separate the decision from the side effects it controls:**

```
BAD:  function verify(user):
          if user.age >= 18 and user.verified:
              db.grantAccess(user); email.send(...)     ← rule tangled with I/O
GOOD: isEligible(user) → bool                           ← pure. Trivially testable
      if isEligible(user): grantAccess(); sendEmail()   ← actions, separately
```

Now you can test eligibility without touching the database or sending an email. This applies to permissions, pricing, validation, retries, notifications — any business rule. **Make important decisions easy to test without triggering the side effects they control** → [[concepts/01-best-practices/03-testing-fundamentals/index|testing]], and it's the functional-core/imperative-shell idea.

## 6. Make errors useful
<!-- bite: fb7403ef-80f1-451d-af1f-472503008e44 -->

`"Something went wrong"` gives a developer — or a calling system — almost nothing. **Text is for humans; codes are for systems.** Provide a predictable error code alongside the human message, so callers can handle failures consistently:

```
BAD:  throw Error("Something went wrong")
GOOD: throw Error(code: "PAYMENT_DECLINED", message: "Your card was declined")
```

And when you log errors, **include the context that helps investigation** — but **never log passwords, tokens, secrets, or personal data** → [[cybersecurity/10-protecting-yourself/index|don't leak secrets in logs]], [[languages/08-swift/06-error-handling|error handling]]. A useful error is the difference between a five-minute fix and an afternoon of guessing → [[programming-fundamentals/10-errors-and-debugging|debugging]].

## 7. Keep your changes focused
<!-- bite: 51dec6ae-82b5-4b3a-906b-3061512db692 -->

Not about writing code — about *changing* it. A pull request that adds a feature, refactors a service, changes the database, updates the frontend, and modifies retry logic all at once might work perfectly and still be **impossible to review, test, debug, or roll back.**

**Smaller, focused changes** — one adds the validation, one refactors the payment service, one updates the interface — each with a clear purpose. Easier to review, easier to bisect when something breaks, easier to revert the one piece that was wrong → [[concepts/01-best-practices/04-pr-structure|PR structure]], [[git/index|focused commits]].

## The one idea underneath all seven
<!-- bite: 9e67a6fc-b58c-4e01-a140-25ca465cb4db -->

Every habit serves the same goal:

> **Make the next change easier.**

- Keep the important logic visible (1)
- Use names that communicate intent (2)
- Keep external dependencies contained (3)
- Make invalid states harder to create (4)
- Separate decisions from side effects (5)
- Make failures understandable (6)
- Keep changes focused (7)

**You don't become a better engineer by writing more code — you become better by writing code that others can understand, change, and trust.** That's the difference between code that works today and code that survives in a real system as it's edited hundreds of times over years. Software's difficulty isn't the first version; it's whether change fifty-one is harder than change one.

## Key insight
<!-- bite: 6884f99e-3e77-4306-a20a-fd9ebb223ccc -->

**These seven habits all reduce to one goal — make the next change easier — and none of them require cleverness; most make the code *simpler*.** Guard clauses keep the main path visible, intent-revealing names cut detective work, boundaries contain external churn, precise types make invalid states unbuildable, separating decisions from actions makes logic testable, coded errors make failures handleable, and focused changes stay reviewable. Experienced engineers write code that's easy to change not because they're smarter in the moment, but because they optimise for the fifty edits that come after — which is the whole game in software that lives.

## Related
<!-- bite: 159e7e0b-7cc4-4f2e-9e99-0df2762ba145 -->
- [[concepts/01-best-practices/01-clean-code/index|clean code]] · [[concepts/01-best-practices/07-solid-principles/index|SOLID]] · [[concepts/01-best-practices/04-pr-structure|PR structure]]
- [[concepts/01-best-practices/03-testing-fundamentals/index|testing fundamentals]] — habit 5 is what makes code testable
- [[architecture/03-architectural-patterns/index|architectural patterns]] — habit 3 (anti-corruption layer) and habit 5 at system scale
- [[languages/08-swift/05-enums-and-pattern-matching|type-driven design]] — habit 4 across languages

*Source: distilled from a "7 coding habits" talk (in [[sources/index|sources/]]). [reference] — Sep 2026.*
