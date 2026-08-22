# SOLID Principles

Five design principles, named by Robert C. Martin, that mostly answer one question: **when requirements change, how much of your code has to change with them?** Each one is a different way of saying "put the things that change together in one place, and don't let unrelated things depend on each other."

They're worth knowing for two reasons: they're a shared vocabulary on real teams, and they come up in interviews from junior level upward. They're also routinely over-applied — a small script does not need an interface per collaborator, and the "Gotchas" section at the bottom is not optional reading.

## S — Single Responsibility Principle

**A class or module should have one reason to change.**

"One responsibility" is vaguer than it sounds; "one reason to change" is the usable version. If your billing rules and your PDF layout live in the same class, then a tax-rate change and a design tweak both edit the same file — two unrelated teams, two unrelated release cycles, one merge conflict.

```javascript
// two reasons to change: invoice maths, and how invoices are rendered
class Invoice {
  calculateTotal() { /* tax rules */ }
  renderPdf()      { /* layout, fonts, margins */ }
}

// one reason each
class Invoice     { calculateTotal() { /* tax rules */ } }
class InvoicePdf  { render(invoice)  { /* layout */ } }
```

The practical test: describe what the class does in one sentence. If you need "and", look closer.

## O — Open/Closed Principle

**Open for extension, closed for modification** — you should be able to add a new case without editing existing, working, already-tested code.

The smell is a `switch` that grows a new branch every time the business adds a variant:

```javascript
// every new payment method edits this function — and risks the existing ones
function fee(payment) {
  switch (payment.type) {
    case "card":     return payment.amount * 0.029;
    case "transfer": return 50;
    case "ussd":     return 25;      // ← today's edit
  }
}

// each method owns its own rule; adding one adds a file, edits nothing
const strategies = { card: new CardFee(), transfer: new TransferFee() };
function fee(payment) { return strategies[payment.type].calculate(payment); }
```

This is the [[01-creational-patterns|strategy pattern]] wearing a principle's name. Note the cost: you've traded one readable `switch` for several files and a lookup. Worth it when variants genuinely keep arriving; overkill when there are three and always will be.

## L — Liskov Substitution Principle

**Anywhere you use a base type, any subtype must work without the caller knowing.**

This is the one people get wrong, because it's about *behaviour*, not method signatures. A subclass can satisfy the interface perfectly and still violate LSP:

```javascript
class Rectangle { setWidth(w){this.w=w} setHeight(h){this.h=h} area(){return this.w*this.h} }

class Square extends Rectangle {
  setWidth(w)  { this.w = w; this.h = w; }   // keeps it square
  setHeight(h) { this.w = h; this.h = h; }
}

// caller's perfectly reasonable assumption, now broken
function stretch(rect) {
  rect.setWidth(5); rect.setHeight(4);
  return rect.area();   // expects 20, gets 16 for a Square
}
```

The signatures all match. The *contract* — "setting width leaves height alone" — doesn't. A square is a rectangle in geometry and isn't one in code, which is the standard example precisely because "is-a" intuition misleads you here.

The tell in real code: a subclass that throws `NotSupportedError`, silently ignores a call, or tightens what inputs it accepts.

## I — Interface Segregation Principle

**Don't force a class to depend on methods it doesn't use.**

One fat interface means every implementer carries every method, and every change to the interface ripples to all of them:

```typescript
// a read-only report worker is now obliged to implement all four
interface Worker { start(): void; stop(): void; pause(): void; resume(): void }

// split by what callers actually need
interface Startable { start(): void; stop(): void }
interface Pausable  { pause(): void; resume(): void }
```

The smell is a stack of empty method bodies and `throw new Error("not implemented")`.

## D — Dependency Inversion Principle

**Depend on abstractions, not concretions** — and specifically, high-level policy shouldn't import low-level detail.

```javascript
// the ordering rules now know about Postgres and SendGrid
class OrderService {
  constructor() { this.db = new PostgresClient(); this.mail = new SendGridClient(); }
}

// the rules state what they need; something else decides what supplies it
class OrderService {
  constructor(orderRepo, notifier) { this.orders = orderRepo; this.notify = notifier; }
}
```

The payoff isn't mainly testability (though it's the reason you can test `OrderService` without a database). It's that your business rules stop being welded to a vendor. This is the principle behind [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|dependency injection]] and the whole point of [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|hexagonal architecture]] — the arrows point inward, toward the domain.

## Gotchas

- **SOLID assumes change you may never get.** Every one of these buys flexibility by paying in indirection now. If the second variant never arrives, you paid for nothing — you just have more files. YAGNI is not the opposite of SOLID; it's the check on it.
- **DIP is not "inject everything."** A constructor with nine injected dependencies is usually a Single Responsibility failure being papered over.
- **Interfaces with exactly one implementation, forever, are ceremony.** Extract the interface when the second implementation shows up, or when you genuinely need to swap it in a test.
- **These are heuristics, not rules.** They came out of 1990s enterprise OOP; a lot of what they achieve is free in a functional style, where a function taking a function is DIP without the paperwork.
- **"It follows SOLID" is not a defence of a design.** The question is always whether the next change is cheap, not whether the acronym is satisfied.

## Related
- [[01-clean-code|clean-code]] — naming, function scope, DRY and its limits
- [[concepts/03-design-patterns/README|design patterns]] — several of these principles *are* patterns
- [[backend/03-structuring-a-backend/README|structuring a backend]] — where DIP and SRP show up architecturally
- [[04-testing-fundamentals|testing-fundamentals]] — most SOLID violations are discovered as "this is hard to test"
