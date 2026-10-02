# Clean Code

> **[Beginner]** · Code is read far more often than it's written, usually by someone with less context than you had. Every practice here serves that one reader.

## Before you start

You can already:

- Write and call functions in JavaScript or TypeScript.
- Run a file with Node (`node file.mjs`). Node 18 or later has the built-in test runner used below; this lesson was checked with Node 26.

After this lesson you will be able to:

1. Say what a module is and name the two properties that make one good or bad.
2. Refactor a tangled function into named, single-purpose pieces **without changing its behaviour**, and prove it with tests.
3. Apply DRY, KISS and YAGNI — and say where each one gives the wrong answer.
4. Tell a useful comment from a useless one.

**Study route.** §1–6 are the ideas. Then attempt the worked example's refactor *yourself* before reading the solution. The practice task links to the interview bank.

## The kid version

Imagine your school bag after a month of never tidying it. Everything you need is in there somewhere, but finding your maths homework means pulling out everything else first. A tidy bag has a pocket for each thing, and each pocket is labelled. **Clean code is a tidy bag for the next person who opens it** — and that person is usually you, three months later, having forgotten everything.

**Where the analogy stops working.** A bag only gets messy if you're careless. Code gets messy even when everyone is careful, because the requirements keep changing under it. Tidying isn't a one-off chore; it's part of every change.

## 1. Why this exists

This function works and has shipped:

```javascript
export function process(o, db, mail) {
  if (o) {
    if (o.items.length > 0) {
      let t = 0;
      for (const i of o.items) t += i.p * i.q;
      if (o.c && o.c.orders > 10) {
        if (o.c.active) {
          t = t - t * 0.1;
        }
      }
      t = Math.round(t * 100); // pence
      db.push({ id: o.id, t });
      mail.push({ to: o.c.email, body: "Your total is " + t });
      return t;
    }
  }
  throw new Error("bad order");
}
```

Now the ticket: *"Loyal customers should need 5 orders, not 10."* Find the rule. Is it `orders > 10` or the `0.1`? What are `p` and `q`? Can you test the loyalty rule without a database and a mailer? **Every question you just had to answer is a cost the next reader pays, every time.** That cost is what this lesson removes.

## Terms used in this lesson

1. **Module**: This is any unit of code with a name and a boundary — a function, a class, a file, a package. It has an inside (how it works) and an outside (how you use it).
2. **Cohesion**: This is how strongly the things inside one module belong together. High cohesion means everything in it serves one purpose.
3. **Coupling**: This is how much one module depends on the inside details of another. Low coupling means you can change one without breaking the other.
4. **Refactoring**: This is changing the structure of code without changing what it does. If behaviour changed, it wasn't a refactor.
5. **Guard clause**: This is an early `return` or `throw` at the top of a function that handles an invalid case and gets it out of the way.
6. **Magic number**: This is a literal value, such as `10` or `0.1`, whose meaning isn't stated in the code.
7. **DRY (don't repeat yourself)**: The letters stand for those three words. It means each piece of *knowledge* — a rule, a formula — should live in one place.
8. **KISS (keep it simple, stupid)**: The letters stand for that phrase. It means preferring the simplest solution that meets the requirement.
9. **YAGNI (you aren't gonna need it)**: The letters stand for that phrase. It means not building for a future requirement until it actually arrives.

## 2. Modules — what makes a good one

Every practice below is about modules, at different sizes. A good module has **high cohesion** — everything inside serves one purpose — and **low coupling** — callers use it through a small outside without knowing its inside.

The test that works at every size: **can you describe what it does in one sentence without "and"?** `calculateTotal` passes. `processOrder` that validates *and* totals *and* saves *and* emails doesn't — that's four modules sharing one name.

A bad module is either a **junk drawer** (low cohesion: `utils.js` with date formatting, retry logic and a currency table) or a **leaky box** (high coupling: callers must know its internals, such as which field it mutates or what order to call things in).

## 3. Naming — the cheapest, highest-leverage improvement available

A well-named variable/function/class explains itself; a poorly-named one requires the reader to hold extra context in their head or go dig through its implementation just to understand a single call site.

```javascript
// unclear — what is `d`? days? a date? a distance?
function calc(d) { return d * 1.5; }

// clear — the name alone tells you what's happening at the call site
function calculateOvertimePay(hoursWorked) { return hoursWorked * 1.5; }
```

Good names remove the need for a comment explaining what a variable holds — if you find yourself writing `// number of days` next to a variable called `d`, renaming `d` to `days` is strictly better than keeping both. The same goes for magic numbers: `LOYAL_CUSTOMER_MIN_ORDERS = 10` turns a guess into a fact.

## 4. Functions should do one thing

A function that does one clearly-named thing is easy to test, easy to reuse, and easy to reason about in isolation. A function that validates input, fetches data, transforms it, and sends an email all in one body is hard to test partially, hard to reuse any single piece of, and hard to change without risking the other unrelated pieces inside it.

**Avoid deep nesting.** Each level of nesting is another condition the reader has to hold in their head. **Guard clauses** flatten it:

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

## 5. DRY, KISS, YAGNI — and where each one is wrong

**DRY.** Duplicated logic means a bug fix has to be found and applied in every copy, and it's easy to miss one. **Where it's wrong:** DRY is about duplicated *knowledge*, not duplicated-looking *code*. Shipping fees and tax both being `amount * rate` today doesn't make them the same rule; merge them and the first time tax changes, shipping breaks. **Wait for the third occurrence**, and ask "would these change for the same reason?"

**KISS.** The simplest thing that works is the easiest to read, test and delete. **Where it's wrong:** "simple" can become an excuse to ignore a real requirement. Storing money as floating-point pounds is simpler than integer pence, until `0.1 + 0.2` is `0.30000000000000004` and the books don't balance. Simple means *no unnecessary* complexity, not *no* complexity.

**YAGNI.** Don't build the plugin system before the second plugin. Most predicted futures don't arrive, and the ones that do arrive differently. **Where it's wrong:** some decisions are expensive to reverse — a public API's shape, a database's primary keys, how money is stored. For those, a little thought about the future is cheap insurance. YAGNI applies to *features*, not to *foundations*.

Notice the three pull against each other: DRY pushes you to abstract, YAGNI and KISS push you not to. **The judgement is the skill; the acronyms only name the forces.**

## 6. Comments — explain *why*, not *what*

Well-named code already explains *what* it does; a comment repeating that adds noise without adding information. A comment earns its place when it explains something the code itself can't — a non-obvious constraint, a workaround for a specific bug, a reason a seemingly-worse approach was deliberately chosen.

```javascript
// bad: repeats what the code already says
// increment count by 1
count += 1;

// good: explains something the code can't show on its own
// Stripe requires amounts in cents, not dollars — hence the *100
const amountInCents = amount * 100;
```

## Worked example — refactor `process` without changing what it does

**Attempt it first.** Take the function from §1 and rewrite it so the loyalty rule can be tested on its own. Don't change behaviour. Then compare with the version below.

**Step 1 — name what's there.** Reading closely, the function does five things: rejects an empty order, sums `price × quantity`, applies a 10% discount to active customers with more than 10 orders, converts pounds to pence, then saves and emails. Five things, so five candidate functions.

**Step 2 — pull out each rule under its real name.** Magic numbers become constants; nesting becomes guard clauses; one-letter names become words. The save-and-email part stays in one coordinating function, because "place an order" genuinely means doing both.

```javascript
// after.mjs
const LOYAL_CUSTOMER_MIN_ORDERS = 10;
const LOYALTY_DISCOUNT = 0.1;

export function validateOrder(order) {
  if (!order || order.items.length === 0) throw new Error("bad order");
}

export function subtotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

export function isLoyal(customer) {
  return customer.active && customer.orderCount > LOYAL_CUSTOMER_MIN_ORDERS;
}

export function applyLoyaltyDiscount(amount, customer) {
  if (!isLoyal(customer)) return amount;
  return amount * (1 - LOYALTY_DISCOUNT);
}

// Store money in whole pence: floating-point pounds drift (0.1 + 0.2 !== 0.3).
export function toPence(pounds) {
  return Math.round(pounds * 100);
}

export function placeOrder(order, { orders, mailer }) {
  validateOrder(order);
  const totalPence = toPence(applyLoyaltyDiscount(subtotal(order.items), order.customer));
  orders.push({ id: order.id, totalPence });
  mailer.push({ to: order.customer.email, body: `Your total is ${totalPence}p` });
  return totalPence;
}
```

The ticket from §1 is now a one-line change to `LOYAL_CUSTOMER_MIN_ORDERS`, and you can find it by its name.

**Step 3 — prove behaviour with tests.** The arrays stand in for a database and a mailer, so nothing external is needed.

```javascript
// after.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { applyLoyaltyDiscount, isLoyal, placeOrder, subtotal, toPence } from "./after.mjs";

const loyal = { active: true, orderCount: 11, email: "a@b.c" };
const newbie = { active: true, orderCount: 2, email: "n@b.c" };

test("subtotal multiplies price by quantity", () => {
  assert.equal(subtotal([{ price: 2.5, quantity: 2 }, { price: 1, quantity: 3 }]), 8);
});

test("loyalty needs more than 10 orders AND an active account", () => {
  assert.equal(isLoyal(loyal), true);
  assert.equal(isLoyal({ ...loyal, orderCount: 10 }), false); // boundary: exactly 10 is not loyal
  assert.equal(isLoyal({ ...loyal, active: false }), false);
});

test("discount applies only to loyal customers", () => {
  assert.equal(applyLoyaltyDiscount(100, loyal), 90);
  assert.equal(applyLoyaltyDiscount(100, newbie), 100);
});

test("toPence rounds away floating-point noise", () => {
  assert.equal(toPence(0.1 + 0.2), 30);
});

test("placeOrder saves and emails the same total", () => {
  const orders = [], mailer = [];
  const total = placeOrder({ id: 1, items: [{ price: 10, quantity: 2 }], customer: loyal }, { orders, mailer });
  assert.equal(total, 1800);
  assert.deepEqual(orders, [{ id: 1, totalPence: 1800 }]);
  assert.equal(mailer[0].body, "Your total is 1800p");
});

test("an empty order is rejected before anything is saved", () => {
  const orders = [];
  assert.throws(() => placeOrder({ id: 2, items: [], customer: newbie }, { orders, mailer: [] }), /bad order/);
  assert.equal(orders.length, 0);
});
```

**Lab:** these files are in [`concepts/04-best-practices/01-clean-code/labs/javascript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/concepts/04-best-practices/01-clean-code/labs/javascript). From the vault root, `python3 labs/run.py clean-code/javascript` runs them and checks this page still shows the same code.

**Run it.** Put both files in an empty folder and run, from that folder:

```bash
node --test
```

Expected output ends with:

```
ℹ tests 6
ℹ pass 6
ℹ fail 0
```

**What changed, and what didn't.** The behaviour is identical — the loyal two-mugs order is 1800p before and after. The field names changed (`p` → `price`, `c` → `customer`), which **is** a change to the function's outside; in a real codebase you'd update the callers in the same commit, or keep the old names at the boundary. That's the honest limit of "refactoring": renaming a public field is a breaking change, even when it's an improvement.

## Common pitfalls

1. **Premature abstraction** — building a generic, configurable solution for a problem that's only shown up once. Three identical lines that are unlikely to diverge are often better than a shared abstraction that has to be understood, and later unwound.
2. **Stale comments.** A comment that no longer matches the code beside it actively misleads. Explaining *what* is the kind that goes stale fastest.
3. **Clever over clear.** A dense one-liner that impresses the author and slows every reader is the opposite of clean.
4. **Refactoring without tests.** Without a test pinning the behaviour, "same behaviour" is a hope. Write the test first, against the old code, then refactor.
5. **Splitting too finely.** Ten three-line functions that are each called once, in order, can be harder to follow than one clear twenty-line function. Split where a piece has its own name and its own reason to change.

## Check your understanding

1. What's the difference between cohesion and coupling? Give an example of a module with low cohesion.
2. Two functions both compute `amount * 0.075`. One is VAT on digital goods, the other is a card processing fee. Should DRY merge them? Why?
3. Give one decision where YAGNI is the wrong advice.
4. Which of these comments is worth keeping: `// loop over users` or `// skip deleted users; the export is for an audit and must match what customers saw`? Why?
5. **Predict.** In the worked example, what does `isLoyal({ active: true, orderCount: 10 })` return, and which line of the original function encodes that boundary?

<details>
<summary>Answers — after your attempt</summary>

1. Cohesion is how well the inside of a module belongs together; coupling is how much one module depends on another's inside. A `utils.js` holding date formatting, retries and a currency table has low cohesion.
2. No. They're the same *code* but different *knowledge*: one changes when tax law changes, the other when the payment provider's pricing changes. Merging them couples two unrelated rules.
3. Anything expensive to reverse — how money is stored, the shape of a public API, primary key types, the data model of a core entity.
4. The second. It explains *why*, which the code can't. The first repeats *what*.
5. `false` — the original says `o.c.orders > 10`, strictly greater, so exactly 10 orders doesn't qualify. That boundary is why the test checks 10 explicitly.

</details>

## Practice — independent task

**Refactor one real function from your own projects.** Pick a function over 30 lines that you'd be nervous to change.

1. Write tests that pin its current behaviour, including at least one boundary case — before touching it.
2. Refactor using guard clauses, named constants, and extracted single-purpose functions.
3. Run the tests after every extraction, not just at the end.

**Done when:** the tests you wrote first still pass unchanged, each extracted function passes the "one sentence, no *and*" test, and there's no comment left that only says *what*.

For interview-style questions on this material, see [[concepts/interview/02-patterns-code-quality-and-review|patterns, code quality and review]].

## Before moving on

You can take messy code, pin it with tests, and refactor it into named pieces — and you can argue both sides of DRY, KISS and YAGNI.

**Recap.** Optimise for the reader. Good modules have high cohesion and low coupling. Name things so comments aren't needed for *what*; comment only for *why*. DRY is about knowledge, not text. KISS means no unnecessary complexity. YAGNI applies to features, not foundations.

**Next.** [[concepts/04-best-practices/08-coupling-and-cohesion/index|Coupling and cohesion]] — the two properties §2 introduced, in depth, with a tool that measures them on your own code.

## Related
- [[concepts/04-best-practices/05-solid-principles/index|SOLID principles]] — the same ideas, formalised
- [[concepts/04-best-practices/04-testing-fundamentals/index|testing fundamentals]]
- [[concepts/04-best-practices/03-documentation-practices|documentation practices]]
- [[concepts/04-best-practices/02-pr-structure|PR structure]]
