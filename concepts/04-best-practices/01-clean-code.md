# Clean Code

"Clean code" isn't a style preference — it's optimizing for the actual bottleneck in most software work: code is read far more often than it's written, usually by someone (often future-you) with less context than the original author had. Every practice below serves that one goal.

## Naming — the cheapest, highest-leverage improvement available

A well-named variable/function/class explains itself; a poorly-named one requires the reader to hold extra context in their head or go dig through its implementation just to understand a single call site.

```javascript
// unclear — what is `d`? days? a date? a distance?
function calc(d) { return d * 1.5; }

// clear — the name alone tells you what's happening at the call site
function calculateOvertimePay(hoursWorked) { return hoursWorked * 1.5; }
```

Good names remove the need for a comment explaining what a variable holds — if you find yourself writing `// number of days` next to a variable called `d`, renaming `d` to `days` is strictly better than keeping both.

## Functions should do one thing

A function that does one clearly-named thing is easy to test, easy to reuse, and easy to reason about in isolation. A function that validates input, fetches data, transforms it, and sends an email all in one body is hard to test partially, hard to reuse any single piece of, and hard to change without risking the other unrelated pieces inside it.

```javascript
// does everything at once — hard to test any single piece independently
function processOrder(order) {
  if (!order.items.length) throw new Error("Empty order");
  const total = order.items.reduce((sum, i) => sum + i.price, 0);
  db.save({ ...order, total });
  emailService.send(order.customerEmail, `Order total: ${total}`);
}

// same behavior, decomposed — each piece is independently testable and reusable
function validateOrder(order) { if (!order.items.length) throw new Error("Empty order"); }
function calculateTotal(order) { return order.items.reduce((sum, i) => sum + i.price, 0); }
function processOrder(order) {
  validateOrder(order);
  const total = calculateTotal(order);
  db.save({ ...order, total });
  emailService.send(order.customerEmail, `Order total: ${total}`);
}
```

## DRY (Don't Repeat Yourself) — and its limits

Duplicated logic means a bug fix or behavior change has to be found and applied in every duplicate, and it's easy to miss one. The important caveat: DRY applies to duplicated *logic/knowledge*, not merely duplicated-looking code — two pieces of code that happen to look similar today but represent genuinely different business rules that could reasonably diverge later shouldn't be forced into one shared abstraction just because they currently look alike. Premature abstraction to avoid superficial duplication is its own, opposite mistake (see the gotchas below).

## Comments — explain *why*, not *what*

Well-named code already explains *what* it does; a comment repeating that adds noise without adding information. A comment earns its place when it explains something the code itself can't — a non-obvious constraint, a workaround for a specific bug, a reason a seemingly-worse approach was deliberately chosen.

```javascript
// bad: repeats what the code already says
// increment count by 1
count += 1;

// good: explains something the code can't show on its own
// Stripe requires amounts in cents, not dollars — hence the *100
const amountInCents = amount * 100;
```

## Avoiding deep nesting

Deeply nested conditionals are hard to trace mentally — each level of nesting is another condition the reader has to hold in their head simultaneously. **Guard clauses** (returning/throwing early for invalid cases) flatten this considerably.

```javascript
// deeply nested
function getDiscount(user) {
  if (user) {
    if (user.isActive) {
      if (user.orders.length > 10) {
        return 0.1;
      }
    }
  }
  return 0;
}

// flattened with guard clauses — each condition handled and dismissed immediately
function getDiscount(user) {
  if (!user) return 0;
  if (!user.isActive) return 0;
  if (user.orders.length <= 10) return 0;
  return 0.1;
}
```

## Gotchas

- Premature abstraction — building a generic, configurable solution for a problem that's only ever shown up once — is a common overcorrection to DRY; three genuinely identical, unlikely-to-diverge lines of code is often better than a premature shared abstraction that has to be understood, and then unwound later if the cases turn out to actually differ.
- Over-commenting stale, easily-outdated explanations of *what* code does is worse than no comment at all — a comment that no longer matches the code it sits next to actively misleads the next reader.
- "Clean" isn't a synonym for "clever" — code that shows off a dense, clever one-liner at the expense of a reader's ability to quickly understand it is usually the opposite of clean, regardless of how impressive it looks.

## Related
- [[04-testing-fundamentals|testing-fundamentals]]
- [[03-documentation-practices|documentation-practices]]
- [[02-pr-structure|pr-structure]]
