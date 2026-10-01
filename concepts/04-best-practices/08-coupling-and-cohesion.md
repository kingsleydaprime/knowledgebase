# Coupling and Cohesion

> **[Beginner→Intermediate]** · The two measures under nearly every design principle: how much one module depends on another's insides, and how well the insides of one module belong together. With a tool that measures the first on your own code.

## Before you start

You can already:

- Split code into functions, files and folders, and import between them.
- Recognise a module that does too much → [[concepts/04-best-practices/01-clean-code|clean code]].

After this lesson you will be able to:

1. Define coupling and cohesion, and say why you want low coupling and high cohesion.
2. Name the common kinds of coupling from worst to best, and refactor control and stamp coupling away.
3. Name the kinds of cohesion that show up as `utils.js` and `init()` junk drawers.
4. Measure fan-in, fan-out and instability for the modules of a real project, and find import cycles.

**Study route.** The kid version and §1–4 are the ideas. §5 is the measurement; run the lab on the sample, then on one of your own projects. Stop at *Check your understanding* before reading the answers.

## The kid version

Think of a group project at school. A **good group** is one where each person has a clear job — one researches, one writes, one makes the poster — and they only need to talk at a few agreed moments. That's **high cohesion** (each person's work hangs together) and **low coupling** (they don't need to keep interrupting each other).

A **bad group** is one where the writer can't start until the poster-maker tells them which colour pen to use, and the researcher keeps rewriting the writer's sentences. Every change by one person breaks someone else's work.

**Where the analogy stops working.** In a group project you can see who's interrupting whom. In code, a dependency is one `import` line, easy to add and easy to miss — so you need a tool, not just good intentions, to see how tangled things have got. That's what §5 is for.

## 1. Why this exists

You rename a field on the `User` object from `name` to `fullName`. The profile page breaks — expected. So do the invoice PDF, the admin export, two email templates and a fraud check, because each of them was handed the whole `User` and reached into it. **One harmless-looking change, six broken places, none of which the author of the change knew about.** Coupling is the name for that hidden reach, and cohesion is the name for whether the code you had to change was in one place or six.

## Terms used in this lesson

1. **Module**: This is any unit with a name and a boundary — a function, a class, a file, a folder. In §5 it means a top-level folder under `src/`.
2. **Coupling**: This is how much one module depends on another. Low coupling means you can change one without changing — or even reading — the other.
3. **Cohesion**: This is how strongly the parts inside one module belong together. High cohesion means everything in it serves one purpose and changes for the same reasons.
4. **Fan-in**: This is also known as **afferent coupling**, written **Ca**. It is the number of other modules that depend on this one.
5. **Fan-out**: This is also known as **efferent coupling**, written **Ce**. It is the number of other modules this one depends on.
6. **Instability**: This is a number between 0 and 1 describing how easily a module is pushed to change by the modules it depends on. It is defined in §5.
7. **Cycle**: This is also known as a **circular dependency**. It means a chain of imports that leads back to where it started — A imports B and B imports A, directly or through others.

## 2. The kinds of coupling, worst first

These names come from 1970s structured design and are still the clearest vocabulary for *what kind* of dependency you're looking at. All examples here are fragments.

**Content coupling — reaching into another module's insides.** The worst kind: you depend on something the other module never promised.

```js
// orders reaches into the cart's private storage
cart._items.length = 0;           // breaks the moment cart changes how it stores items
// better: ask the module to do it
cart.clear();
```

**Common coupling — sharing mutable global state.** Every module that reads or writes the global is coupled to every other one, invisibly. The singleton in [[concepts/03-design-patterns/01-creational-patterns|creational patterns]] is this.

```js
// config.js
export const settings = { currency: "NGN" };
// anywhere, at any time
settings.currency = "GBP";        // now every module's prices change, and nobody called anyone
```

**Control coupling — a flag that tells the callee which path to take.** The caller has to know the callee's internal branches.

```js
// the caller decides what happens inside
sendReceipt(order, true);         // what does `true` mean? you have to read sendReceipt
// better: two functions with honest names
sendReceiptEmail(order);
sendReceiptSms(order);
```

**Stamp coupling — passing a whole structure when you need one part.** The callee now depends on the shape of the whole thing — which is the `User.name` incident from §1.

```js
function greeting(user) { return `Hello, ${user.name}`; }   // depends on all of User
function greeting(name) { return `Hello, ${name}`; }        // depends on one string
```

**Data coupling — passing only the values needed.** The healthy default: the dependency is exactly what's in the signature, and nothing else.

Two modern additions worth naming:

- **Temporal coupling** — calls that must happen in a certain order (`init()` before `start()`) with nothing in the code enforcing it. Fix by making the wrong order impossible: `start()` takes what `init()` returns.
- **Deployment coupling** — two services that must be released together. That's a distributed monolith → [[backend/03-structuring-a-backend/05-modular-monolith-to-services|modular monolith to services]].

## 3. The kinds of cohesion, worst first

**Coincidental** — things grouped for no reason except that they had to go somewhere: `utils.js` with date formatting, retry logic and a currency table. Changes for many unrelated reasons.

**Logical** — things grouped because they're the *same kind* of thing, picked between by a flag: one `export(type)` function that does CSV, PDF and Excel with a big `switch`. Often comes with control coupling.

**Temporal** — things grouped because they happen at the *same time*: an `init()` that opens the database, warms the cache, registers cron jobs and sends a Slack message. Unrelated, except by clock.

**Functional** — everything in the module contributes to one well-defined job: `calculateShipping`, a `payments` module. The goal.

(The full list also has procedural, communicational and sequential cohesion, between logical and functional. Knowing the two ends is what matters day to day.)

## 4. Why "low coupling, high cohesion" is one idea

They are two views of the same question: **when something changes, how much else has to change with it?** High cohesion puts the things that change together in one place. Low coupling stops that change spreading beyond it. A module can't have high cohesion and still need half the codebase to change with it — if it does, the boundary is in the wrong place.

This is the idea underneath most of week 2: "one reason to change" in [[concepts/04-best-practices/05-solid-principles|SOLID]], the layers in [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|controllers, services, repositories]], and feature folders in [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|layer vs feature]].

## 5. Measuring coupling — fan-in, fan-out, instability

You can't measure cohesion well with a script, but you can measure the coupling *between* modules from their imports.

For each module, count:

- **Fan-in (Ca)** — how many other modules import it.
- **Fan-out (Ce)** — how many other modules it imports.

A module's **instability** is the share of its connections that point outward: the number of modules it depends on, divided by the total number of modules it depends on or that depend on it.

$$I = \frac{C_e}{C_a + C_e}$$

At **0**, nothing it depends on can force it to change, and many things depend on it — so it's **stable**, and expensive to change, because every dependent feels it. At **1**, it depends on others and nobody depends on it — **unstable**, and cheap to change. Neither is bad. The rule (Robert C. Martin's **stable dependencies principle**) is about direction: **depend towards stability.** `shared/` should be near 0; a feature that only the app uses can sit near 1. A stable module importing an unstable one is the warning sign — and a **cycle** is worse, because it makes every module in it as hard to change as the hardest one.

## Worked example — measure a small shop

The lab is a script that reads every `.js`/`.ts` file under a folder, treats each top-level subfolder as a module, follows relative and `@/` imports (packages like `express` are skipped), and prints fan-in, fan-out, instability and cycles.

```js
// coupling.mjs — measure coupling between the top-level modules of a src/ folder.
// Usage: node coupling.mjs path/to/src
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";

const SOURCE = /\.(m?[jt]sx?)$/;
const IMPORT = /(?:import|export)\s[^'"]*?from\s*["']([^"']+)["']|import\s*\(\s*["']([^"']+)["']\s*\)|import\s+["']([^"']+)["']/g;

function filesUnder(dir) {
  return readdirSync(dir).flatMap((name) => {
    const full = path.join(dir, name);
    if (name === "node_modules") return [];
    return statSync(full).isDirectory() ? filesUnder(full) : SOURCE.test(name) ? [full] : [];
  });
}

// The module a path belongs to is its first folder under src/ ("orders/x.ts" -> "orders").
// An import of a folder ("../users") belongs to that folder's module too.
function moduleOf(src, file) {
  const parts = path.relative(src, file).split(path.sep);
  const isFolder = existsSync(file) && statSync(file).isDirectory();
  return parts.length > 1 || isFolder ? parts[0] : "(root)";
}

// Turn an import string into a path under src/, or null for packages like "express".
function resolve(src, fromFile, specifier) {
  if (specifier.startsWith("@/")) return path.join(src, specifier.slice(2));
  if (specifier.startsWith(".")) return path.resolve(path.dirname(fromFile), specifier);
  return null;
}

export function analyse(src) {
  src = path.resolve(src);
  const edges = new Map(); // module -> Set of modules it imports
  const modules = new Set();
  for (const file of filesUnder(src)) {
    const from = moduleOf(src, file);
    modules.add(from);
    edges.set(from, edges.get(from) ?? new Set());
    for (const match of readFileSync(file, "utf8").matchAll(IMPORT)) {
      const target = resolve(src, file, match[1] ?? match[2] ?? match[3]);
      if (!target || path.relative(src, target).startsWith("..")) continue;
      const to = moduleOf(src, target);
      if (to !== from) edges.get(from).add(to);
    }
  }

  const rows = [...modules].sort().map((name) => {
    const efferent = edges.get(name).size; // Ce: modules this one depends on
    const afferent = [...edges.values()].filter((deps) => deps.has(name)).length; // Ca: modules depending on it
    const instability = afferent + efferent === 0 ? null : efferent / (afferent + efferent);
    return { module: name, afferent, efferent, instability };
  });
  return { rows, cycles: cycles(edges) };
}

// Tarjan's algorithm: every strongly connected component bigger than one module is a cycle.
function cycles(edges) {
  let index = 0;
  const stack = [], onStack = new Set(), indexOf = new Map(), low = new Map(), found = [];
  const visit = (v) => {
    indexOf.set(v, index); low.set(v, index); index++;
    stack.push(v); onStack.add(v);
    for (const w of edges.get(v) ?? []) {
      if (!indexOf.has(w)) { visit(w); low.set(v, Math.min(low.get(v), low.get(w))); }
      else if (onStack.has(w)) low.set(v, Math.min(low.get(v), indexOf.get(w)));
    }
    if (low.get(v) === indexOf.get(v)) {
      const component = [];
      let w;
      do { w = stack.pop(); onStack.delete(w); component.push(w); } while (w !== v);
      if (component.length > 1) found.push(component.sort());
    }
  };
  for (const v of [...edges.keys()].sort()) if (!indexOf.has(v)) visit(v);
  return found;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const src = process.argv[2] ?? "src";
  const { rows, cycles: found } = analyse(src);
  console.log("module".padEnd(16) + "Ca  Ce  instability");
  for (const r of rows) {
    const i = r.instability === null ? "  -" : r.instability.toFixed(2);
    console.log(r.module.padEnd(16) + String(r.afferent).padStart(2) + String(r.efferent).padStart(4) + "  " + i);
  }
  console.log(found.length ? `\ncycles: ${found.map((c) => c.join(" <-> ")).join("; ")}` : "\nno cycles");
}
```

The sample project has four modules. Two of its files, so you can trace the numbers:

```ts
import { db } from "@/shared/db";
import { formatKobo } from "../shared/money";
import { findUser } from "../users";
import { charge } from "../payments";
import express from "express"; // a package, not a module of ours: ignored
export const markPaid = (id: string) => db.rows.push(id);
export const checkout = (userId: string, id: string) => [findUser(userId), charge(id), formatKobo(500), express];
```

```ts
import { db } from "../shared/db";
import { markPaid } from "../orders"; // payments reaches back into orders: a cycle
export const charge = (orderId: string) => { markPaid(orderId); return db; };
```

`users` imports only `shared/db`, and `shared` imports nothing.

**Predict before running.** Work out Ca, Ce and instability for `orders` and for `shared`. Is there a cycle?

**Lab:** these files are in `labs/coupling-and-cohesion/`. From the vault root, `python3 labs/run.py coupling-and-cohesion` runs them and checks this page still shows the same code.

**Run it.** From `labs/coupling-and-cohesion/`:

```bash
node coupling.mjs sample/src
```

Expected:

```
module          Ca  Ce  instability
orders           1   3  0.75
payments         1   2  0.67
shared           3   0  0.00
users            1   1  0.50

cycles: orders <-> payments
```

**Tracing it.** `orders` imports `shared` (twice, via `@/shared/db` and `../shared/money` — still one module), `users` and `payments`: **Ce = 3**. Only `payments` imports `orders`: **Ca = 1**. So I = 3 / (1 + 3) = 0.75. `shared` is imported by the other three and imports nothing: Ca = 3, Ce = 0, **I = 0** — as stable as it gets, which is right for shared code. The cycle exists because `payments` reaches back to call `markPaid` in `orders`. The usual fix is the one from [[concepts/03-design-patterns/03-behavioral-patterns|behavioural patterns]]: `payments` publishes `PaymentSucceeded`, and `orders` subscribes — `payments` no longer imports `orders` at all.

The tests pin these numbers:

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { analyse } from "./coupling.mjs";

const { rows, cycles } = analyse("sample/src");
const byName = Object.fromEntries(rows.map((r) => [r.module, r]));

test("shared is depended on by everyone and depends on nothing: maximally stable", () => {
  assert.deepEqual(byName.shared, { module: "shared", afferent: 3, efferent: 0, instability: 0 });
});

test("orders depends on three modules and is depended on by one", () => {
  assert.deepEqual(byName.orders, { module: "orders", afferent: 1, efferent: 3, instability: 0.75 });
});

test("the orders <-> payments cycle is found; packages and aliases are handled", () => {
  assert.deepEqual(cycles, [["orders", "payments"]]);
  assert.equal(byName.users.efferent, 1); // only shared — "express" is not one of our modules
});
```

**Pointing it at your own code.** Give it the folder *whose children are your modules*. For a feature-folder React app that's `src/features`, not `src`, otherwise every feature counts as one module called `features`.

**What it can't see.** Dependencies that aren't imports — a shared database table, an event name two modules agree on, an HTTP call between services. Those are real coupling, invisible to any import graph. That's why "no shared tables" is a separate rule in [[backend/03-structuring-a-backend/05-modular-monolith-to-services|the modular monolith]].

## Common pitfalls

1. **Treating zero coupling as the goal.** Modules have to work together; the goal is coupling that is *few*, *explicit* and *pointing toward stable things*.
2. **Fixing coincidental cohesion by splitting `utils.js` into `utils/` with twelve files.** The cure is moving each helper next to the code that uses it.
3. **Breaking a cycle by moving the shared bit into `shared/`** when it's actually business logic belonging to one side. Use an event or an interface owned by the stable side instead.
4. **Reading the numbers without the direction.** An instability of 1.0 isn't bad; a stable module depending on an unstable one is.
5. **Stamp coupling through "just pass the user".** Convenient, and it's how a field rename breaks six places.

## Check your understanding

1. Define coupling and cohesion in one sentence each.
2. `formatAddress(customer)` only uses `customer.address`. What kind of coupling is that, and how do you reduce it?
3. A `notify(user, mode)` function does email when `mode === 1` and SMS when `mode === 2`. Name the coupling and the cohesion problem.
4. Module A has Ca = 6, Ce = 0. Module B has Ca = 0, Ce = 4. Which is stable? Which one should be cheap to change?
5. **Predict.** In the sample, if you replace `payments`' import of `orders` with an event, what happens to the cycle, and to `orders`' fan-in?

<details>
<summary>Answers — after your attempt</summary>

1. Coupling is how much one module depends on another; cohesion is how well the parts inside one module belong together.
2. Stamp coupling — it depends on the whole customer's shape. Pass `customer.address` instead, so it depends only on what it uses.
3. Control coupling (the caller passes a flag that picks the path) and logical cohesion (two different jobs grouped because they're both "notifying"). Split into `sendEmail(user)` and `sendSms(user)`.
4. A is stable (I = 0): many depend on it and it depends on nothing, so changing it is expensive. B (I = 1) depends on others and nothing depends on it — it's the one that should be cheap to change.
5. The cycle disappears. `orders`' fan-in drops to 0 — nothing imports it any more — so its instability rises to 1.0. Both modules now depend on the event bus in `shared/` instead of on each other.

</details>

## Practice — independent task

**Measure one of your own projects, then improve one number.**

1. Run `node labs/coupling-and-cohesion/coupling.mjs <your-project>/src` (or `src/features`, or `src/modules`). Save the output.
2. Find either a cycle or the module whose instability most violates "depend towards stability" — a low-instability module that imports a high-instability one.
3. Fix it with one of: an event, moving an interface to the stable side, or passing data instead of a whole object.
4. Run it again and save the new output.

**Done when:** you have before-and-after output, the cycle is gone or the dependency now points toward the more stable module, and you can explain in two sentences why the new direction is cheaper to change.

## Before moving on

You can name the kinds of coupling and cohesion in real code, compute fan-in, fan-out and instability by hand, and use the lab to find cycles in your own projects.

**Recap.** Coupling: how much a module depends on others. Cohesion: how well a module's insides belong together. Aim for few, explicit dependencies pointing toward stable modules, and modules that change for one reason. Content, common, control and stamp coupling are the kinds to refactor away; data coupling is the healthy default.

**Next.** [[concepts/04-best-practices/05-solid-principles|SOLID]] — "one reason to change" and "depend on what you need" as five named principles, and where they become over-engineering.

## Related
- [[concepts/04-best-practices/08b-coupling-and-cohesion-in-other-languages|Coupling and Cohesion in Other Languages]] — which dependency cycles each language's toolchain refuses
- [[concepts/04-best-practices/01-clean-code|Clean code]] — modules, and the one-sentence test
- [[concepts/04-best-practices/05-solid-principles|SOLID]] — the same ideas as five principles
- [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|Layer vs feature]] — enforcing which imports are allowed

*Source: [reference] — the coupling and cohesion kinds are from Yourdon and Constantine's structured design; instability and the stable dependencies principle are Robert C. Martin's.*
