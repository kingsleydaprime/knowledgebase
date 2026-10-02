# Creational Patterns

> **[Beginner]** · How objects get created — moving the decision of *which* class, *how configured*, and *how many* into one place instead of scattering `new SomeClass()` everywhere. And why the most famous one, singleton, is usually a mistake.

## Before you start

You can already:

- Write TypeScript classes and interfaces.
- Explain dependency inversion — passing in what a module needs → [[concepts/04-best-practices/05-solid-principles|SOLID]].

After this lesson you will be able to:

1. Use a factory to choose an implementation from configuration.
2. Decide between a builder and a plain options object, and write a builder whose `build()` enforces rules across fields.
3. **Demonstrate** — with a failing pair of tests — why a singleton leaks state, and replace it with a factory plus injection.

**Study route.** §1–5 are the patterns. Make the prediction in the worked example before running it; that test pair is the point of the lesson.

## The kid version

A bakery doesn't let every customer walk into the kitchen and bake their own bread. You ask at the counter — "one loaf, sliced" — and the bakery decides which oven, which recipe, how to slice it. **Creational patterns are the counter**: one place that knows how things get made, so nobody else has to.

And the singleton? That's a bakery with exactly one mixing bowl that every baker shares and nobody washes. Convenient on day one — then someone's cake tastes of yesterday's garlic bread.

**Where the analogy stops working.** A bakery's counter is a person who can use judgement. A factory function only does what its code says, so every new kind of product means changing that code — the "counter" moves the change into one place, it doesn't remove it.

## 1. Why this exists

`new StripeClient(process.env.STRIPE_KEY)` appears in fourteen files. The business adds Paystack for Nigerian customers. Now each of the fourteen places needs an `if`, and three of them get missed. Separately, an `OtpLimiter.getInstance()` singleton makes the test suite pass when run alone and fail when run together, because one test's counts carry into the next. **Both problems come from object creation being spread out or hidden.** Creational patterns pull it into one visible place.

## Terms used in this lesson

1. **Instantiate**: This means create an object from a class, usually with `new`.
2. **Concrete class**: This is an actual class you can instantiate, such as `StripeProcessor`, as opposed to the interface it implements.
3. **Factory**: This is a function or method whose job is to create objects and decide which concrete class to use.
4. **Builder**: This is an object that collects the parts of a complex object step by step, then produces it with a final `build()` call that can check the whole thing.
5. **Singleton**: This is a class that ensures only one instance exists and provides a global way to reach it.
6. **Global state**: This is data reachable from anywhere in the program without being passed in. Anything can change it, so it is hard to reason about.
7. **Prototype**: In this pattern, this is an existing object used as a template that new objects are copied from.

## 2. Factory — delegate the decision of *which* class to instantiate

Instead of calling a constructor directly, call a function that decides which concrete class to instantiate based on some input — callers depend on an interface/abstract type, not a specific concrete class.

```typescript
interface PaymentProcessor { charge(amount: number): void; }
class StripeProcessor implements PaymentProcessor { charge(amount: number) { /* ... */ } }
class PaypalProcessor implements PaymentProcessor { charge(amount: number) { /* ... */ } }

function createPaymentProcessor(provider: string): PaymentProcessor {
  if (provider === "stripe") return new StripeProcessor();
  if (provider === "paypal") return new PaypalProcessor();
  throw new Error("Unknown provider");
}

const processor = createPaymentProcessor(config.paymentProvider);   // caller doesn't know or care which concrete class this is
processor.charge(100);
```

Useful the moment "which concrete class to use" depends on runtime configuration or input, rather than being hardcoded — adding a new payment provider means adding a new branch in one factory function, not hunting down every place `new StripeProcessor()` was called directly throughout the codebase.

## 3. Builder — constructing a complex object step by step

When an object needs many optional parameters, a constructor with ten optional arguments (or an object literal with ten optional fields, easy to get subtly wrong) is hard to read and easy to misuse. A builder provides a fluent, step-by-step way to construct it instead.

```typescript
class RequestBuilder {
  private headers: Record<string, string> = {};
  private body?: unknown;

  setHeader(key: string, value: string) { this.headers[key] = value; return this; }
  setBody(body: unknown) { this.body = body; return this; }
  build() { return { headers: this.headers, body: this.body }; }
}

const request = new RequestBuilder()
  .setHeader("Content-Type", "application/json")
  .setBody({ name: "Kingsley" })
  .build();
```

Each method returns `this`, which is what enables the chained, readable call style — and each step is self-documenting (`.setHeader(...)` is clearer at the call site than a positional constructor argument would be).

**In TypeScript, an options object usually beats a builder.** `createRequest({ headers, body })` with typed optional fields gives the same readability with no class. A builder earns its place when **`build()` can check the whole object** — rules that involve several fields at once, which a type can't express. The worked example shows one.

## 4. Singleton — exactly one instance, globally accessible

Ensures a class has only one instance across the entire application, with a single, well-known way to access it — commonly used for things that are genuinely singular in nature: a database connection pool, an application-wide configuration object, a logger.

```typescript
class ConfigManager {
  private static instance: ConfigManager;
  private constructor(private settings: Record<string, string>) {}

  static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager(loadSettingsFromEnv());
    }
    return ConfigManager.instance;
  }
}

const config = ConfigManager.getInstance();   // always the same instance, everywhere it's called
```

Singleton is also the most commonly *overused* pattern on this list — reached for reflexively for things that don't actually need global uniqueness, at the cost of hidden global state that makes testing harder (a singleton's state persists across tests unless deliberately reset) and creates implicit dependencies that aren't visible in a class's constructor signature. Worth confirming a genuine "exactly one, globally" requirement exists before reaching for it, rather than defaulting to it out of habit.

## 5. Prototype — cloning an existing object instead of building one from scratch

Creates new objects by copying an existing "prototype" instance rather than instantiating from a class definition each time — useful when object creation is expensive (significant setup work, data loaded from disk/network) and a very similar object is needed repeatedly, or when the specific concrete type to copy is only known at runtime.

```typescript
interface Cloneable<T> { clone(): T; }
class EnemyTemplate implements Cloneable<EnemyTemplate> {
  constructor(public health: number, public damage: number, public sprite: string) {}
  clone() { return new EnemyTemplate(this.health, this.damage, this.sprite); }
}

const goblinTemplate = new EnemyTemplate(50, 5, "goblin.png");
const goblin1 = goblinTemplate.clone();   // cheap copy instead of expensive re-initialization
const goblin2 = goblinTemplate.clone();
```

## 6. Worked example — the leaking singleton, and the builder that checks

**Part 1 — singleton versus factory.** The same OTP rate limiter, written both ways. It allows three OTPs per user.

```ts
// limiter.ts — the same rate limiter, as a singleton and as a factory

// ---- Singleton: one hidden, global instance ----
export class SingletonLimiter {
  static instance: SingletonLimiter | undefined;
  used = new Map<string, number>();
  limit = 3;
  private constructor() {}
  static getInstance(): SingletonLimiter {
    SingletonLimiter.instance ??= new SingletonLimiter();
    return SingletonLimiter.instance;
  }
  allow(userId: string): boolean {
    const n = (this.used.get(userId) ?? 0) + 1;
    this.used.set(userId, n);
    return n <= this.limit;
  }
}

// Business code that reaches for the global — its dependency is invisible in its signature.
export function sendOtpWithSingleton(userId: string): "sent" | "rate-limited" {
  return SingletonLimiter.getInstance().allow(userId) ? "sent" : "rate-limited";
}

// ---- Factory + injection: create as many as you need, pass them in ----
export type Limiter = { allow(userId: string): boolean };

export function createLimiter(limit: number): Limiter {
  const used = new Map<string, number>();
  return {
    allow(userId) {
      const n = (used.get(userId) ?? 0) + 1;
      used.set(userId, n);
      return n <= limit;
    },
  };
}

export function sendOtp(limiter: Limiter, userId: string): "sent" | "rate-limited" {
  return limiter.allow(userId) ? "sent" : "rate-limited";
}
```

**Predict before running.** The test file below has two identical singleton tests, "A" and "B". Each sends three OTPs to `u1`. Will B see `"sent"` three times?

**Part 2 — a builder whose `build()` checks across fields.** A type can say `to` is a `string[]`; it can't say "at least one recipient" or "nobody in both `to` and `cc`".

```ts
// builder.ts — a builder earns its place when build() can check the whole object
export type Email = { to: string[]; subject: string; text: string; cc: string[]; replyTo?: string };

export class EmailBuilder {
  #to: string[] = [];
  #cc: string[] = [];
  #subject = "";
  #text = "";
  #replyTo: string | undefined;

  to(address: string) { this.#to.push(address); return this; }
  cc(address: string) { this.#cc.push(address); return this; }
  subject(value: string) { this.#subject = value; return this; }
  text(value: string) { this.#text = value; return this; }
  replyTo(address: string) { this.#replyTo = address; return this; }

  build(): Email {
    if (this.#to.length === 0) throw new Error("an email needs at least one recipient");
    if (!this.#subject) throw new Error("an email needs a subject");
    const overlap = this.#cc.filter((a) => this.#to.includes(a));
    if (overlap.length) throw new Error(`in both to and cc: ${overlap.join(", ")}`);
    return { to: [...this.#to], cc: [...this.#cc], subject: this.#subject, text: this.#text, replyTo: this.#replyTo };
  }
}
```

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { createLimiter, sendOtp, sendOtpWithSingleton } from "./limiter.ts";
import { EmailBuilder } from "./builder.ts";

// These two tests are identical. With the singleton, the second one inherits the first one's state.
test("singleton, test A: first three OTPs are sent", () => {
  assert.deepEqual([1, 2, 3].map(() => sendOtpWithSingleton("u1")), ["sent", "sent", "sent"]);
});
test("singleton, test B: same test, but state leaked from A", () => {
  assert.deepEqual([1, 2, 3].map(() => sendOtpWithSingleton("u1")), ["rate-limited", "rate-limited", "rate-limited"]);
});

test("factory, test A: first three OTPs are sent", () => {
  const limiter = createLimiter(3);
  assert.deepEqual([1, 2, 3].map(() => sendOtp(limiter, "u1")), ["sent", "sent", "sent"]);
});
test("factory, test B: a fresh limiter, so the same result", () => {
  const limiter = createLimiter(3);
  assert.deepEqual([1, 2, 3, 4].map(() => sendOtp(limiter, "u1")), ["sent", "sent", "sent", "rate-limited"]);
});

test("builder: build() rejects an incomplete or contradictory email", () => {
  assert.throws(() => new EmailBuilder().subject("Hi").build(), /at least one recipient/);
  assert.throws(() => new EmailBuilder().to("a@x.com").cc("a@x.com").subject("Hi").build(), /in both to and cc: a@x.com/);
  const email = new EmailBuilder().to("a@x.com").subject("Receipt").text("Thanks").build();
  assert.deepEqual(email, { to: ["a@x.com"], cc: [], subject: "Receipt", text: "Thanks", replyTo: undefined });
});
```

**Lab:** these files are in `labs/creational-patterns/typescript/`. From the vault root, `python3 labs/run.py creational-patterns/typescript` runs them and checks this page still shows the same code.

**Run it.** Put the three files in one folder and run `node --test` from it (Node 23.6 or later; checked with Node 26). Expected:

```
ℹ tests 5
ℹ pass 5
ℹ fail 0
```

**The answer to the prediction: no.** B gets `"rate-limited"` three times, and the test file *asserts* that, to make the leak visible. The singleton's counts survived from A because there's only one instance for the whole process. In a real suite, that shows up as tests that pass alone and fail together, or that fail only when run in a certain order. The factory version gives each test a fresh limiter, so A and B are independent. It also shows the dependency in `sendOtp`'s signature, where a reader can see it.

**When "exactly one" is genuinely right**, such as one database pool per process, create it **once in the composition root** and pass it in. You get one instance without the global access. That's [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|dependency injection]], the next lesson.

## Common pitfalls

- These patterns are solutions to *specific* recurring problems, not a checklist to apply everywhere — using a Builder for an object with two simple, always-required fields adds indirection with no real payoff; a plain constructor is simply the right tool there.
- Singleton's hidden global state is a common source of hard-to-track bugs and testing pain specifically — worth defaulting to explicit dependency injection (passing an instance in, rather than reaching for a global accessor) unless a singleton's specific guarantee (exactly one instance) is actually required.
- Recognizing "this codebase already has an ad-hoc version of the Factory/Builder pattern, just not named that" is often more valuable day to day than being able to implement every pattern from scratch — the vocabulary itself is what makes discussing and recognizing these shapes efficient.

## Check your understanding

1. What problem does a factory solve that `new` scattered across the codebase doesn't?
2. When does a builder beat an options object in TypeScript?
3. Give two concrete ways a singleton makes testing harder.
4. You need exactly one database connection pool. How do you get "exactly one" without a singleton?
5. **Predict.** In the worked example, what would `sendOtpWithSingleton("u2")` return if called at the end of test B? Why?

<details>
<summary>Answers — after your attempt</summary>

1. The decision of which concrete class to create lives in one place, so adding a provider or changing configuration is one edit, not a hunt.
2. When `build()` must check rules that involve several fields together — at least one recipient, no address in both `to` and `cc` — which the type system can't express.
3. State persists between tests unless deliberately reset, so tests depend on run order; and the dependency is hidden inside the function body, so you can't pass a fake without patching the global.
4. Create it once at startup — in the composition root — and pass it to everything that needs it.
5. `"sent"`. The limit is per user, and `u2` has no count yet — the leak is per key, which makes it even harder to spot.

</details>

## Practice — independent task

**Remove a singleton from your own code.** Search one of your projects with `grep -rn "getInstance\|static instance" src/` — or for a module that creates a client at import time, such as `export const db = new Pool()`.

1. Write a test that demonstrates the hidden dependency: either state leaking between two tests, or a function you can't test without touching the real client.
2. Replace it with a factory called once in the composition root and passed in.
3. Write the same test again with a fake passed in.

**Done when:** the new test runs in isolation and in any order, the function's signature shows what it depends on, and the app still creates exactly one real instance at startup.

## Before moving on

You can choose an implementation with a factory, justify a builder over an options object, and show — with tests — why singletons leak state.

**Recap.** **Factory**: one place decides which class. **Builder**: step-by-step construction with a checking `build()`. **Singleton**: one global instance — usually replace with "create once, pass in". **Prototype**: copy a template instead of rebuilding.

**Next.** [[concepts/03-design-patterns/03-behavioral-patterns|Behavioural patterns]] — how the objects you've created talk to each other.

## Related
- [[concepts/03-design-patterns/02-structural-patterns|structural patterns]]
- [[concepts/03-design-patterns/03-behavioral-patterns|behavioural patterns]]
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|dependency injection]] — the usual replacement for a singleton
