# Structural Patterns

> **[Intermediate]** · How objects are **composed** into larger structures — adapting an interface you don't control, adding behaviour without editing a class, controlling access, and hiding a complicated subsystem. Plus the principle underneath all four: **composition over inheritance**.

## Before you start

You can already:

- Write a TypeScript class that `implements` an interface.
- Explain Liskov substitution and dependency inversion → [[concepts/04-best-practices/05-solid-principles|SOLID]].

After this lesson you will be able to:

1. Explain composition over inheritance, and show the subclass explosion it prevents.
2. Recognise adapter, decorator, proxy and facade, and say what problem each solves.
3. Stack wrappers around one interface and predict how the **order** of wrapping changes behaviour.

**Study route.** §1–2 are the core idea; §3–6 are the four patterns. Run the worked example, and make the prediction before you run it.

## The kid version

Lego beats a toy that's moulded in one piece. With a moulded fire engine, if you want one with a longer ladder you need a whole new toy. With Lego, you take the fire engine and **clip on** a longer ladder, then clip on a siren. **Building by clipping pieces together is composition; making a new moulded toy for every variation is inheritance.** The four patterns in this lesson are four ways of clipping things together.

**Where the analogy stops working.** Lego pieces don't care what order you clip them in. Software wrappers do — a cache outside a retry behaves differently from a retry outside a cache, and the worked example shows exactly how.

## 1. Why this exists

Your app fetches exchange rates from an HTTP API. You need retries because the API is flaky, caching because it's rate-limited, and logging for debugging. With inheritance you write `RetryingRates extends Rates`, then `CachingRetryingRates extends RetryingRates`, then `LoggingCachingRetryingRates`... and a test that wants caching *without* retries needs another subclass. **Three features, up to seven subclasses, and the order is fixed at compile time.** Composition gives you three small wrappers you can combine any way you like at runtime.

## Terms used in this lesson

1. **Inheritance**: This is when a class gets behaviour by extending another class (`class B extends A`). The relationship is fixed when the code is written.
2. **Composition**: This is when an object gets behaviour by *holding* other objects and calling them. The relationship is decided when the objects are created, so it can vary.
3. **Wrapper**: This is an object that holds another object of the same interface and forwards calls to it, doing something before or after. Decorator and proxy are both wrappers.
4. **Adapter**: This is a wrapper that changes an interface you don't control into the interface your code expects.
5. **Decorator**: This is a wrapper that adds behaviour — logging, retries, timing — while keeping the same interface.
6. **Proxy**: This is a stand-in with the same interface that controls *access* to the real object — creating it lazily, caching its answers, or checking permissions.
7. **Facade**: This is a new, simple interface over several collaborating parts, so callers make one call instead of coordinating many.

## 2. Composition over inheritance

**Prefer giving an object behaviour by holding collaborators, not by extending a parent class.** Inheritance isn't banned — it's the right tool for a genuine "is-a" with a stable contract, such as a custom `Error` subclass. But it has three costs composition avoids:

1. **Combinatorial explosion.** Each independent feature doubles the possible subclasses. Wrappers add one class per feature.
2. **Fixed at compile time.** A subclass can't be un-subclassed at runtime; a wrapper can be left off in tests or configuration.
3. **Fragile base classes.** A subclass depends on the *inside* of its parent — which methods call which. Changing the parent can break children that never changed. That's high coupling, and it's where most [[concepts/04-best-practices/05-solid-principles|Liskov violations]] come from.

The rest of this lesson is four named shapes of composition.

## 3. Adapter — making an incompatible interface fit

Wraps an object with an interface your code doesn't expect, exposing the interface your code *does* expect, translating calls between the two underneath. The classic use case: integrating a third-party library or legacy code whose interface doesn't match what the rest of your codebase expects, without modifying that third-party code at all.

```typescript
// third-party library's interface — not something you control or want to change
class LegacyLogger {
  writeLog(msg: string, level: number) { /* ... */ }
}

// the interface your application actually expects
interface Logger { info(msg: string): void; error(msg: string): void; }

class LegacyLoggerAdapter implements Logger {
  constructor(private legacy: LegacyLogger) {}
  info(msg: string) { this.legacy.writeLog(msg, 1); }
  error(msg: string) { this.legacy.writeLog(msg, 3); }
}

const logger: Logger = new LegacyLoggerAdapter(new LegacyLogger());
logger.info("app started");   // rest of the app only ever sees the clean `Logger` interface
```

## 4. Decorator — adding behavior without modifying the original class

Wraps an object to add new behavior, transparently, without changing the original class's code — and multiple decorators can be stacked, each adding its own layer.

```typescript
interface Coffee { cost(): number; description(): string; }
class SimpleCoffee implements Coffee {
  cost() { return 2; }
  description() { return "Coffee"; }
}
class MilkDecorator implements Coffee {
  constructor(private coffee: Coffee) {}
  cost() { return this.coffee.cost() + 0.5; }
  description() { return this.coffee.description() + " + Milk"; }
}

let order: Coffee = new SimpleCoffee();
order = new MilkDecorator(order);   // stack another decorator the same way for "+ Sugar", etc.
console.log(order.description(), order.cost());   // "Coffee + Milk" 2.5
```

This is the same underlying idea as Python's `@decorator` syntax or a middleware chain (see [[backend/01-foundations/02-http-servers|HTTP servers]]) — wrapping a thing with additional behavior, transparently, without the wrapped thing needing to know it's been wrapped.

## 5. Proxy — controlling access to an object

Provides a stand-in for another object, controlling access to it — adding lazy loading (don't create the expensive real object until it's actually needed), access control, caching, or logging, transparently, from the caller's perspective.

```typescript
interface Image { display(): void; }
class RealImage implements Image {
  constructor(private filename: string) { this.loadFromDisk(); }   // expensive
  private loadFromDisk() { console.log(`Loading ${this.filename}`); }
  display() { console.log(`Displaying ${this.filename}`); }
}
class LazyImageProxy implements Image {
  private realImage?: RealImage;
  constructor(private filename: string) {}
  display() {
    if (!this.realImage) this.realImage = new RealImage(this.filename);   // only loads on first actual use
    this.realImage.display();
  }
}
```

JavaScript's built-in `Proxy` object is a direct, language-level implementation of this exact pattern — intercepting property access/assignment on an object transparently.

## 6. Facade — a simple interface over a complex subsystem

Provides one simple, unified interface hiding a more complex set of underlying classes/subsystems working together — the caller interacts with one simple method instead of coordinating several underlying components' interactions itself.

```typescript
class VideoConverterFacade {
  convert(filename: string, format: string) {
    const codec = new CodecFactory().extract(filename);      // several underlying subsystems
    const buffer = new BitrateReader().read(filename, codec);
    const result = new AudioMixer().fix(buffer);
    return new FileWriter().write(result, format);
  }
}

// caller's perspective: one simple call, complexity hidden underneath
new VideoConverterFacade().convert("video.mp4", "avi");
```

The distinction from Adapter: an Adapter makes an *existing* interface compatible with what you need; a Facade creates a *new*, simpler interface over a genuinely complex set of subsystems, purely for ease of use.

## 7. Worked example — retries, caching and logging as wrappers

One interface, `RateSource`, and five classes that all implement it: a flaky API, three wrappers, and an adapter for a third-party client with the wrong shape.

```ts
// rates.ts — one interface, one real source, three wrappers that compose
export interface RateSource {
  rate(from: string, to: string): Promise<number>;
}

// Stands in for a slow, flaky HTTP API. Fails the first `failures` calls.
export class FlakyApi implements RateSource {
  calls = 0;
  failures: number;
  constructor(failures: number) {
    this.failures = failures;
  }
  async rate(from: string, to: string) {
    this.calls++;
    if (this.calls <= this.failures) throw new Error("503 from rates API");
    return from === "GBP" && to === "NGN" ? 2000 : 1;
  }
}

// Decorator: adds retries. Same interface in, same interface out.
export class Retrying implements RateSource {
  inner: RateSource;
  attempts: number;
  constructor(inner: RateSource, attempts: number) {
    this.inner = inner;
    this.attempts = attempts;
  }
  async rate(from: string, to: string) {
    let lastError: unknown;
    for (let i = 0; i < this.attempts; i++) {
      try {
        return await this.inner.rate(from, to);
      } catch (err) {
        lastError = err;
      }
    }
    throw lastError;
  }
}

// Proxy: controls access — answers from memory when it can.
export class Caching implements RateSource {
  inner: RateSource;
  cache = new Map<string, number>();
  constructor(inner: RateSource) {
    this.inner = inner;
  }
  async rate(from: string, to: string) {
    const key = `${from}->${to}`;
    const hit = this.cache.get(key);
    if (hit !== undefined) return hit;
    const value = await this.inner.rate(from, to);
    this.cache.set(key, value);
    return value;
  }
}

// Decorator: adds logging.
export class Logging implements RateSource {
  inner: RateSource;
  log: string[];
  constructor(inner: RateSource, log: string[]) {
    this.inner = inner;
    this.log = log;
  }
  async rate(from: string, to: string) {
    const value = await this.inner.rate(from, to);
    this.log.push(`${from}->${to} = ${value}`);
    return value;
  }
}

// Adapter: a third-party client with the wrong shape, made to fit RateSource.
export class ThirdPartyFx {
  async getQuote(pair: { base: string; quote: string }) {
    return { pair: `${pair.base}/${pair.quote}`, mid: pair.base === "USD" ? 1500 : 1 };
  }
}
export class ThirdPartyFxAdapter implements RateSource {
  client: ThirdPartyFx;
  constructor(client: ThirdPartyFx) {
    this.client = client;
  }
  async rate(from: string, to: string) {
    const quote = await this.client.getQuote({ base: from, quote: to });
    return quote.mid;
  }
}
```

**Predict before running.** The API fails its first two calls. With `new Logging(new Caching(new Retrying(api, 3)), log)`, and `rate("GBP", "NGN")` called twice — how many times is the real API called, and how many log lines are there? Then: with `new Retrying(new Caching(new FlakyApi(5)), 3)`, does the call succeed?

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { Caching, FlakyApi, Logging, Retrying, ThirdPartyFx, ThirdPartyFxAdapter } from "./rates.ts";

test("composed: log(cache(retry(api))) — two failures, then cached", async () => {
  const api = new FlakyApi(2);
  const log: string[] = [];
  const rates = new Logging(new Caching(new Retrying(api, 3)), log);

  assert.equal(await rates.rate("GBP", "NGN"), 2000); // fails twice, third attempt succeeds
  assert.equal(await rates.rate("GBP", "NGN"), 2000); // served from cache
  assert.equal(api.calls, 3);
  assert.deepEqual(log, ["GBP->NGN = 2000", "GBP->NGN = 2000"]);
});

test("order matters: retry(cache(api)) with too few attempts still fails", async () => {
  const rates = new Retrying(new Caching(new FlakyApi(5)), 3);
  await assert.rejects(rates.rate("GBP", "NGN"), /503/);
});

test("adapter: a client with the wrong shape plugs into the same stack", async () => {
  const rates = new Caching(new ThirdPartyFxAdapter(new ThirdPartyFx()));
  assert.equal(await rates.rate("USD", "NGN"), 1500);
});
```

**Lab:** these files are in `labs/structural-patterns/`. From the vault root, `python3 labs/run.py structural-patterns` runs them and checks this page still shows the same code.

**Run it.** Save both files in one folder and, from it, run `node --test` (Node 23.6 or later; checked with Node 26). Expected:

```
ℹ tests 3
ℹ pass 3
ℹ fail 0
```

**The answers.** The API is called **3 times**: twice failing and once succeeding, all inside the first `rate()` call. The second call is answered by the cache, so the API isn't touched. There are **2 log lines**, because logging is the outermost wrapper and sees both calls. For the second stack: five failures and three attempts means the call still fails. The cache can't help, because there's nothing cached yet. **The order of wrapping is behaviour**: put logging inside the cache and you'd see one line, not two.

**The cost to name.** Five classes where one could have done it all. That's worth it here because each wrapper is reused and tested alone, and the combination changes per environment — no retries in tests, say. For a one-off script, a single function with a `try` and a `Map` is clearer.

## Common pitfalls

- Adapter and Facade solve genuinely different problems despite feeling similar — Adapter is about compatibility with an interface you don't control; Facade is about simplifying a complex interface you do control (or that's simply made up of many pieces).
- Overusing Decorator by stacking many layers can make it hard to reason about the final combined behavior/cost at a glance — readable up to a point, then a source of confusion past it; worth naming/documenting common decorator combinations if a codebase leans on this pattern heavily.
- Proxy's transparency is the whole point — a proxy that doesn't genuinely implement the same interface as the real object it stands in for defeats the pattern's purpose, since callers should be able to use either interchangeably without caring which they have.

## Check your understanding

1. Give two costs of inheritance that composition avoids.
2. You need to use a payments SDK whose method is `makePayment({ kobo, email })`, but your code calls `charge(customerId, amount)`. Which pattern? Decorator or adapter?
3. What's the difference between a decorator and a proxy, if both wrap an object with the same interface?
4. When is a facade *not* an adapter?
5. In the worked example, if you swap to `new Caching(new Logging(new Retrying(api, 3), log))`, how many log lines do two identical calls produce?

<details>
<summary>Answers — after your attempt</summary>

1. Any two of: combinatorial explosion of subclasses; behaviour fixed at compile time; fragile base classes (children depend on the parent's internals).
2. Adapter — the problem is a mismatched interface, not missing behaviour.
3. Intent. A decorator *adds* behaviour (logging, retries). A proxy *controls access* to the real object (lazy creation, caching, permission checks). Structurally they can look identical.
4. When it doesn't make one existing interface fit another, but creates a new, simpler interface over several parts — usually parts you control.
5. One. The cache is now outside the logger, so the second call is answered before it reaches the logging wrapper.

</details>

## Practice — independent task

**Add a timeout wrapper and a facade.**

1. Write `WithTimeout implements RateSource`, which rejects with `Error("timeout")` if the inner call takes longer than a given number of milliseconds. Test it with a slow fake.
2. Decide where `WithTimeout` belongs in the stack relative to `Retrying` — should each attempt time out, or the whole retry loop? Write one sentence on why, and a test that demonstrates your choice.
3. Write a `Pricing` facade with one method, `priceIn(currency, amountGbp)`, that hides building the wrapper stack and converting the amount.

**Done when:** all tests pass, no existing class was edited, and you can explain without notes why swapping the order of two wrappers changes behaviour.

For interview-style questions, see [[concepts/interview/02-patterns-code-quality-and-review|patterns, code quality and review]].

## Before moving on

You can explain composition over inheritance, identify the four structural patterns in real code, and predict how wrapper order changes behaviour.

**Recap.** Prefer composing objects to extending classes. **Adapter** makes an interface fit; **decorator** adds behaviour; **proxy** controls access; **facade** simplifies a subsystem. Wrappers sharing one interface can be stacked — and their order is part of the behaviour.

**Next.** [[concepts/03-design-patterns/01-creational-patterns|Creational patterns]] — how the objects you're composing get built (week 3).

## Related
- [[concepts/03-design-patterns/02b-structural-patterns-in-other-languages|Structural Patterns in Other Languages]] — decorators, proxies and adapters as each language does them
- [[concepts/03-design-patterns/01-creational-patterns|creational patterns]]
- [[concepts/03-design-patterns/03-behavioral-patterns|behavioural patterns]]
- [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|hexagonal architecture]] — adapters at the scale of a whole system
