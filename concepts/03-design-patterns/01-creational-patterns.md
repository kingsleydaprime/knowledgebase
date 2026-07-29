# Creational Patterns

Creational patterns are about **how objects get created** — abstracting away the raw `new SomeClass()` call so that construction logic (which concrete class to instantiate, how to configure a complex object, how to reuse expensive-to-create objects) lives in one place instead of scattered everywhere an object gets created.

## Factory — delegate the decision of *which* class to instantiate

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

## Builder — constructing a complex object step by step

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

## Singleton — exactly one instance, globally accessible

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

## Prototype — cloning an existing object instead of building one from scratch

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

## Gotchas

- These patterns are solutions to *specific* recurring problems, not a checklist to apply everywhere — using a Builder for an object with two simple, always-required fields adds indirection with no real payoff; a plain constructor is simply the right tool there.
- Singleton's hidden global state is a common source of hard-to-track bugs and testing pain specifically — worth defaulting to explicit dependency injection (passing an instance in, rather than reaching for a global accessor) unless a singleton's specific guarantee (exactly one instance) is actually required.
- Recognizing "this codebase already has an ad-hoc version of the Factory/Builder pattern, just not named that" is often more valuable day to day than being able to implement every pattern from scratch — the vocabulary itself is what makes discussing and recognizing these shapes efficient.

## Related
- [[02-structural-patterns|structural-patterns]]
- [[03-behavioral-patterns|behavioral-patterns]]
