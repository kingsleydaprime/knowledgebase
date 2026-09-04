# Habits That Make Change Easier

**[Beginner → Intermediate]** — seven small coding habits that separate code that merely works from code that survives fifty more changes. The kind of thing you absorb working alongside experienced engineers.

## The kid version first

Getting better as a developer isn't mostly about learning another language. Past a point, the biggest gains come from making your code **easier to understand, easier to change, and harder to break** — and experienced engineers rarely do this by writing *cleverer* code. They usually write *simpler* code. These are seven habits with one idea underneath them all: **make the next change easier**, because software gets hard not when you write the first version, but when the next fifty edits become harder than they should be.

This is the practical, at-the-keyboard companion to [[concepts/04-best-practices/01-clean-code|clean code]] and [[concepts/04-best-practices/05-solid-principles|SOLID]].

## 1. Keep the main path easy to follow

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

These are **guard clauses** (early return). The goal isn't to eliminate all nesting — it's to keep the *important path* of a function easy to see → [[foundations/programming-fundamentals/README|control flow]]. A reader should follow what a function *does* without mentally unwinding a pyramid of conditions.

## 2. Name things by their meaning

Avoid `data`, `result`, `item`, `temp` when the actual meaning is more specific. `pendingOrder` and `processOrder()` tell you what you're dealing with; `data` and `process()` send you hunting elsewhere to find out.

**Good names reduce the detective work required to understand a codebase.** You don't need long names for everything — just make the important concepts obvious. This is the cheapest, highest-frequency readability win there is, and it's half of what "self-documenting code" actually means → [[concepts/04-best-practices/01-clean-code|clean code]], [[concepts/04-best-practices/03-documentation-practices|documentation]].

## 3. Keep external systems behind a boundary

Your app talks to things you don't control — payment providers, email services, other APIs. If your code depends *directly* on their field names and shapes, then when they change, that change **ripples through your entire codebase** wherever those fields are used.

**Translate external data into your own model at the boundary**, once:

```
external response  →  [ boundary: map to OUR names/shapes ]  →  our clean model
   (their fields)          the ONE place their change costs us      (used everywhere)
```

This is the **anti-corruption layer**. When the external service changes, you fix one mapping instead of fifty call sites. It's the same instinct as [[cybersecurity/14-api-security/06-the-api-security-lifecycle|not trusting third-party responses]] and [[architecture/03-architectural-patterns/README|hexagonal architecture's ports and adapters]] — keep external complexity contained at the edge instead of spreading it inward.

## 4. Make invalid states harder to represent

A common trap: make almost everything optional/nullable, so every part of the code has to keep asking "does this exist? is it valid? can I do this?"

**Model the state so the invalid combinations can't be built.** If a "paid order" always has an order ID, a payment ID, and a paid status, define the type so those are *expected to exist* — then nothing downstream has to guess:

```
BAD:  Order { id?, paymentId?, status?, paidAt? }   → 16 combinations, most nonsense
GOOD: PaidOrder { id, paymentId, paidAt }           → the type says "this is paid"
```

You won't eliminate every error, but you make incorrect states much harder to create in the first place. **This is type-driven design**, and it's the practical version of what [[languages/08-swift/05-enums-and-pattern-matching|Swift enums]], [[languages/09-kotlin/03-types-and-data-classes|Kotlin sealed types]], [[languages/03-rust/06-structs-enums-and-pattern-matching|Rust's enums]] and [[data-analysis/03-metrics-and-kpis|precise definitions]] all enable — moving a class of bug from runtime to *unrepresentable*.

## 5. Separate decisions from actions

Mixing a business rule together with the database and email operations it triggers makes the *decision* hard to test on its own — you can't check "is this user eligible?" without hitting the database and sending mail.

**Separate the decision from the side effects it controls:**

```
BAD:  function verify(user):
          if user.age >= 18 and user.verified:
              db.grantAccess(user); email.send(...)     ← rule tangled with I/O
GOOD: isEligible(user) → bool                           ← pure. Trivially testable
      if isEligible(user): grantAccess(); sendEmail()   ← actions, separately
```

Now you can test eligibility without touching the database or sending an email. This applies to permissions, pricing, validation, retries, notifications — any business rule. **Make important decisions easy to test without triggering the side effects they control** → [[concepts/04-best-practices/04-testing-fundamentals|testing]], and it's the functional-core/imperative-shell idea.

## 6. Make errors useful

`"Something went wrong"` gives a developer — or a calling system — almost nothing. **Text is for humans; codes are for systems.** Provide a predictable error code alongside the human message, so callers can handle failures consistently:

```
BAD:  throw Error("Something went wrong")
GOOD: throw Error(code: "PAYMENT_DECLINED", message: "Your card was declined")
```

And when you log errors, **include the context that helps investigation** — but **never log passwords, tokens, secrets, or personal data** → [[cybersecurity/10-protecting-yourself/README|don't leak secrets in logs]], [[languages/08-swift/06-error-handling|error handling]]. A useful error is the difference between a five-minute fix and an afternoon of guessing → [[foundations/programming-fundamentals/10-errors-and-debugging|debugging]].

## 7. Keep your changes focused

Not about writing code — about *changing* it. A pull request that adds a feature, refactors a service, changes the database, updates the frontend, and modifies retry logic all at once might work perfectly and still be **impossible to review, test, debug, or roll back.**

**Smaller, focused changes** — one adds the validation, one refactors the payment service, one updates the interface — each with a clear purpose. Easier to review, easier to bisect when something breaks, easier to revert the one piece that was wrong → [[concepts/04-best-practices/02-pr-structure|PR structure]], [[git/README|focused commits]].

## The one idea underneath all seven

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

**These seven habits all reduce to one goal — make the next change easier — and none of them require cleverness; most make the code *simpler*.** Guard clauses keep the main path visible, intent-revealing names cut detective work, boundaries contain external churn, precise types make invalid states unbuildable, separating decisions from actions makes logic testable, coded errors make failures handleable, and focused changes stay reviewable. Experienced engineers write code that's easy to change not because they're smarter in the moment, but because they optimise for the fifty edits that come after — which is the whole game in software that lives.

## Related
- [[concepts/04-best-practices/01-clean-code|clean code]] · [[concepts/04-best-practices/05-solid-principles|SOLID]] · [[concepts/04-best-practices/02-pr-structure|PR structure]]
- [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]] — habit 5 is what makes code testable
- [[architecture/03-architectural-patterns/README|architectural patterns]] — habit 3 (anti-corruption layer) and habit 5 at system scale
- [[languages/08-swift/05-enums-and-pattern-matching|type-driven design]] — habit 4 across languages

*Source: distilled from a "7 coding habits" talk (in [[sources/README|sources/]]). [reference] — Sep 2026.*
