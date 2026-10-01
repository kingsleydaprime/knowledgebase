# SOLID Principles

> **[Beginner→Intermediate]** · Five principles that answer one question — *when requirements change, how much of your code has to change with them?* — and the warning that comes with them.

## Before you start

You can already:

- Write a class and a function that takes another function as an argument, in JavaScript or TypeScript.
- Explain cohesion, coupling and "one reason to change" → [[concepts/04-best-practices/01-clean-code|clean code]].

After this lesson you will be able to:

1. State each of the five principles in one plain sentence and show the code smell it fixes.
2. Explain why a subclass can match every method signature and still break Liskov substitution.
3. Use dependency inversion to test business logic without a real payment provider or email service.
4. Say when applying a principle would be over-engineering.

**Study route.** §1–6 cover the five principles. Run the worked example, then stop at *Check your understanding*. The pitfalls section is not optional reading.

## The kid version

Think of a games console. You can plug in any controller that fits the socket — the official one, a cheap one, a steering wheel — and the console doesn't need to be rebuilt. The console only cares about the *socket*, not the brand of controller. And a steering wheel that plugs in but crashes the console when you press "jump" isn't really a controller, even if it fits.

**SOLID is mostly about sockets**: build parts that do one job, connect them through simple sockets, and make sure anything that fits a socket actually behaves like what it replaced.

**Where the analogy stops working.** Sockets on a console are cheap because millions of people share them. In code, every socket you add is something the next reader has to follow. If only one thing will ever plug in, the socket is cost without benefit — that's the over-engineering warning at the end.

## 1. Why this exists

A checkout supports card and bank transfer. The business adds USSD (paying by dialling a short code, common in Nigeria). To do it you edit the fee `switch`, which also holds the card rule; the checkout class, which creates its own Stripe client, so you can't test it without hitting Stripe; and a `PaymentMethod` base class whose `refund()` the USSD provider doesn't support. **One new payment method, three risky edits to code that already worked.** SOLID is a set of names for the five ways that structure went wrong.

Five design principles, named by Robert C. Martin, that mostly answer one question: **when requirements change, how much of your code has to change with them?** Each one is a different way of saying "put the things that change together in one place, and don't let unrelated things depend on each other."

They're worth knowing for two reasons: they're a shared vocabulary on real teams, and they come up in interviews from junior level upward. They're also routinely over-applied — a small script does not need an interface per collaborator, and the "Common pitfalls" section at the bottom is not optional reading.

## Terms used in this lesson

1. **SOLID**: The letters stand for the five principles: **S**ingle responsibility, **O**pen/closed, **L**iskov substitution, **I**nterface segregation, **D**ependency inversion. The name was coined around Robert C. Martin's principles.
2. **Interface**: This is the set of operations a caller can use on something — its socket. In TypeScript it can be an `interface` declaration; in JavaScript it's the methods a caller relies on, written down or not.
3. **Contract**: This is the interface plus the *behaviour* a caller may rely on — what inputs are accepted, what comes back, and what stays unchanged. Two things can share an interface and break the contract.
4. **Subtype**: This is a type that claims it can be used wherever another type (its **base type**) is expected, for example a subclass.
5. **Abstraction**: In this lesson, this means a description of *what* is needed ("something that can charge a card") without saying *which* thing provides it.
6. **Concretion**: This is a specific implementation, such as `StripeClient`.
7. **Dependency injection**: This is passing a module the things it depends on, instead of it creating them itself. It is the usual way to apply dependency inversion.

## 2. S — Single Responsibility Principle

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

## 3. O — Open/Closed Principle

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

This is the [[concepts/03-design-patterns/03-behavioral-patterns|strategy pattern]] (a behavioural pattern) wearing a principle's name. Note the cost: you've traded one readable `switch` for several files and a lookup. Worth it when variants genuinely keep arriving; overkill when there are three and always will be.

## 4. L — Liskov Substitution Principle

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

## 5. I — Interface Segregation Principle

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

## 6. D — Dependency Inversion Principle

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

## 7. Worked example — adding USSD without touching what works

The situation from §1, fixed with two principles: **open/closed** for fees and **dependency inversion** for checkout. Attempt it first: how would you add a USSD fee so that no existing rule is edited, and test checkout without a payment provider?

```javascript
// fees.mjs — Open/Closed: adding a payment method adds an entry, edits no rule
export const feeRules = {
  card: (amountPence) => Math.round(amountPence * 0.029),
  transfer: () => 50,
};

export function fee(payment, rules = feeRules) {
  const rule = rules[payment.type];
  if (!rule) throw new Error(`no fee rule for ${payment.type}`);
  return rule(payment.amountPence);
}
```

A lookup of functions does the job of the strategy classes in §3 — in JavaScript, a function *is* a one-method interface.

```javascript
// checkout.mjs — Dependency Inversion: the rule asks for what it needs
import { fee } from "./fees.mjs";

export function makeCheckout({ payments, receipts }) {
  return async function checkout(order) {
    const charge = order.totalPence + fee(order.payment);
    const ref = await payments.charge(order.customerId, charge);
    await receipts.send(order.customerId, `Charged ${charge}p (ref ${ref})`);
    return { charge, ref };
  };
}
```

`checkout` never names Stripe or an email vendor. Whoever builds it decides — the real clients in production, fakes in a test:

```javascript
// solid.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { fee, feeRules } from "./fees.mjs";
import { makeCheckout } from "./checkout.mjs";

test("existing fee rules", () => {
  assert.equal(fee({ type: "card", amountPence: 10000 }), 290);
  assert.equal(fee({ type: "transfer", amountPence: 10000 }), 50);
});

test("a new method is added without editing fee()", () => {
  const rules = { ...feeRules, ussd: () => 25 };
  assert.equal(fee({ type: "ussd", amountPence: 10000 }, rules), 25);
});

test("unknown methods fail loudly instead of charging nothing", () => {
  assert.throws(() => fee({ type: "crypto", amountPence: 1 }), /no fee rule for crypto/);
});

test("checkout runs with fakes — no payment provider, no email", async () => {
  const charged = [], sent = [];
  const checkout = makeCheckout({
    payments: { charge: async (id, pence) => { charged.push([id, pence]); return "ref_1"; } },
    receipts: { send: async (id, text) => { sent.push(text); } },
  });
  const result = await checkout({ customerId: "c1", totalPence: 10000, payment: { type: "transfer", amountPence: 10000 } });
  assert.deepEqual(result, { charge: 10050, ref: "ref_1" });
  assert.deepEqual(charged, [["c1", 10050]]);
  assert.equal(sent[0], "Charged 10050p (ref ref_1)");
});

class Rectangle {
  setWidth(w) { this.w = w; }
  setHeight(h) { this.h = h; }
  area() { return this.w * this.h; }
}
class Square extends Rectangle {
  setWidth(w) { this.w = w; this.h = w; }
  setHeight(h) { this.w = h; this.h = h; }
}
function stretch(rect) { rect.setWidth(5); rect.setHeight(4); return rect.area(); }

test("LSP: Square breaks a caller written for Rectangle", () => {
  assert.equal(stretch(new Rectangle()), 20);
  assert.equal(stretch(new Square()), 16);
});
```

**Run it.** Put the three files in an empty folder and, from that folder, run `node --test`. Expected (checked with Node 26):

```
ℹ tests 5
ℹ pass 5
ℹ fail 0
```

The last test passes *because* the violation is real: the same caller gets 20 from a `Rectangle` and 16 from a `Square`.

**What the fix cost.** One `switch` became a lookup and a factory function. That's cheap here because new payment methods really do keep arriving. If there were three methods forever, the `switch` would have been the better code.

## Common pitfalls

- **SOLID assumes change you may never get.** Every one of these buys flexibility by paying in indirection now. If the second variant never arrives, you paid for nothing — you just have more files. YAGNI is not the opposite of SOLID; it's the check on it.
- **DIP is not "inject everything."** A constructor with nine injected dependencies is usually a Single Responsibility failure being papered over.
- **Interfaces with exactly one implementation, forever, are ceremony.** Extract the interface when the second implementation shows up, or when you genuinely need to swap it in a test.
- **These are heuristics, not rules.** They came out of 1990s enterprise OOP; a lot of what they achieve is free in a functional style, where a function taking a function is DIP without the paperwork.
- **"It follows SOLID" is not a defence of a design.** The question is always whether the next change is cheap, not whether the acronym is satisfied.

## Check your understanding

1. State the single responsibility principle using "reason to change", and give its one-sentence test.
2. A `ReadOnlyFile` subclass of `File` throws on `write()`. Which principle does it break, and what's the tell?
3. Why does dependency inversion make `checkout` testable without a network?
4. A class takes nine constructor arguments. Which principle is probably broken, and which one is being used to hide it?
5. **Predict.** If you add `ussd` to `feeRules` in the worked example, which existing tests could possibly break? Why?

<details>
<summary>Answers — after your attempt</summary>

1. A module should have one reason to change. Test: describe it in one sentence without "and".
2. Liskov substitution. Callers of `File` expect `write()` to work; the subclass tightens what's allowed. The tell is a subclass that throws "not supported" or silently ignores a call.
3. `checkout` only knows it receives something with a `charge` method and something with a `send` method. A test passes in fakes that record calls, so no real provider is ever contacted.
4. Single responsibility — the class is doing too much. Dependency injection makes the problem *look* tidy by moving the creation elsewhere.
5. None of the card or transfer tests can break, because their rules weren't edited — only a new entry was added. That's what "closed for modification" buys you.

</details>

## Practice — independent task

**Find two violations in your own code and fix one.** Use the interview bank [[concepts/interview/02-patterns-code-quality-and-review|patterns, code quality and review]] for extra questions afterwards.

1. In one of your projects, find a growing `switch` or `if/else` chain on a type (open/closed) and a class that creates its own database or HTTP client (dependency inversion).
2. For each, write two sentences: what change it makes expensive, and whether that change has actually happened more than once.
3. Fix **only** the one where the change has really recurred. Write a test that runs the business rule with a fake.

**Done when:** the test runs without network or database access, adding a new case requires no edit to existing branches, and you've written one sentence justifying why you *didn't* fix the other one (or why you did).

## Before moving on

You can state each principle in plain words, show its smell in code, and argue when it's not worth applying.

**Recap.** **S** — one reason to change. **O** — add new cases without editing old ones. **L** — subtypes must keep the base type's behaviour, not just its signatures. **I** — don't make callers depend on methods they don't use. **D** — business rules depend on what they need, not on vendors. Every principle buys flexibility with indirection; YAGNI is the check on all five.

**Next.** [[concepts/03-design-patterns/02-structural-patterns|Structural patterns]] — including composition over inheritance, which is the usual fix for a Liskov violation.

## Related
- [[concepts/04-best-practices/01-clean-code|clean code]] — naming, function scope, DRY and its limits
- [[concepts/03-design-patterns/index|design patterns]] — several of these principles *are* patterns
- [[backend/03-structuring-a-backend/index|structuring a backend]] — where DIP and SRP show up architecturally
- [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]] — most SOLID violations are discovered as "this is hard to test"
