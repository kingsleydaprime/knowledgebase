# Dependency Injection & Wiring

**[Intermediate]** — how the layers actually get connected, and why the answer isn't "just import it."

## Before you start

You can already:

- Split code into controller, service and repository → [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|layers]].
- Explain why a singleton makes testing hard → [[concepts/03-design-patterns/01-creational-patterns|creational patterns]].

After this lesson you will be able to:

1. Write a composition root that builds an app's object graph by hand.
2. Choose constructor injection and say what field injection hides.
3. **Reproduce and fix the scope bug** — per-request data stored on a shared instance — two ways.
4. Decide when an interface earns its place and when a container is worth adopting.

**Study route.** The kid version and §1–4, then the worked example. The failure modes in §6 come up in real incidents; don't skip them.

## The kid version first

A chef needs an oven.

- **Option A:** the chef *builds their own oven* the moment they need one. Now the chef can only ever work in a kitchen where they can build that exact oven. Want to test the recipe without a real oven? You can't.
- **Option B:** the chef is *handed* an oven when they start their shift. They don't care where it came from. Hand them a real one in production, a pretend one in a test.

That's it. Dependency injection is "be handed your tools instead of making them." Everything else is plumbing.

**Where the analogy stops working.** An oven is one physical thing per kitchen. In code, the same object can be handed to a thousand requests at once — so if the chef scribbles today's customer's name on the oven door, the next customer's meal gets the wrong name. That's the scope bug in the worked example.

```ts
// Option A — the service constructs its own dependency
class OrderService {
  private db = new PostgresClient(process.env.DATABASE_URL);  // welded to Postgres, and to env vars
}

// Option B — it's handed in
class OrderService {
  constructor(private readonly db: Database) {}               // works with anything that is a Database
}
```

## 1. Why this exists

`OrderService` creates its own `PostgresClient` from `process.env.DATABASE_URL`. To test a pricing rule you now need a database running, the right environment variable set, and a clean table. And when you want one shared connection pool, every class that called `new PostgresClient()` has made its own. **Creating dependencies inside the class welds it to one implementation and spreads configuration everywhere.** Dependency injection moves both into one place.

## Terms used in this lesson

1. **Dependency**: This is anything a piece of code needs in order to work — a database client, another service, a logger, configuration.
2. **DI (dependency injection)**: The letters stand for those two words. It means giving a class its dependencies from outside, usually through its constructor, rather than letting it create or fetch them.
3. **Composition root**: This is the one place, at startup, where concrete objects are created and connected. It is the only code that knows every concrete type.
4. **Container**: This is also known as an **IoC (inversion of control) container**. It is a library that builds the object graph for you from declarations or type information — NestJS's injector, Spring, `tsyringe`.
5. **Scope**: This is how long an injected instance lives and who shares it. A **singleton scope** means one instance for the whole app; a **request scope** means a new instance for each request.
6. **Service locator**: This is an anti-pattern where code asks a global registry for its dependencies at runtime (`container.get("Thing")`), which hides them again.
7. **AsyncLocalStorage**: This is a Node.js API that keeps a value — such as the current user — attached to one chain of asynchronous work, so concurrent requests each see their own.

## 2. What it actually buys you

The usual answer is "decoupling," which is too vague to act on. The concrete wins:

1. **Testing without a framework or a database.** `new OrderService(fakeDb)` — no container, no HTTP, no Docker. This is the biggest practical payoff by a wide margin.
2. **One place that knows how things are built.** Connection strings, pool sizes, retry policies live at the composition root rather than scattered through every class that needs a client.
3. **Lifecycle management.** One shared database pool, one logger, a new instance per request where needed. The container handles ordering and shutdown.
4. **Honest feedback about design.** A constructor with nine parameters is telling you the class does too much. That signal is valuable — and it's exactly the signal that field injection hides.

## 3. Constructor injection, and why not the alternatives

```ts
// ✅ constructor injection
class OrderService {
  constructor(
    private readonly orders: OrderRepository,
    private readonly inventory: InventoryService,
  ) {}
}
```

- Dependencies can be `final`/`readonly` → immutable, thread-safe.
- **The object is never in a half-built state.** With field injection the instance exists before its dependencies are set, so anything touching it in between sees `undefined`.
- You can construct it in a plain unit test with `new`. No container required.
- The parameter count is visible pressure toward smaller classes.

**Field/property injection** (`@Autowired` on a field, `@Inject()` on a property) hides dependencies from the constructor signature, permits circular dependencies to *appear* to work, and makes plain instantiation impossible. **Setter injection** is for genuinely optional dependencies, which are rare.

## 4. Interfaces: when they earn their keep

The purist position is "always depend on an interface." That's over-applied. An interface earns its place when:

- **There will genuinely be more than one implementation** — a real one and a fake, or Stripe and PayPal.
- **You're crossing an architectural boundary** — the port in [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|ports and adapters]].
- **You need to break a compile-time dependency cycle** between modules.

It does *not* earn its place when there's exactly one implementation and always will be, and your test framework can mock a concrete class anyway. `IOrderServiceImpl` implementing `IOrderService` with identical methods is ceremony. **In TypeScript especially, structural typing means a plain object often satisfies the shape without any interface declaration at all.**

## 5. How frameworks do the wiring

The concept is universal; the mechanism differs, and knowing which you're using matters:

| Approach | Example | Wiring happens |
|---|---|---|
| **Manual composition root** | plain Node/Go/Rust — construct everything in `main` | compile/startup, fully explicit |
| **Reflection/decorator container** | Spring, NestJS, `tsyringe` | runtime, by type metadata |
| **Compile-time DI** | Dagger, Wire (Go), Koin | build time — errors surface at compile, no runtime reflection |

**Manual wiring is underrated.** For a small or medium service, a single `composition-root.ts` that news everything up in order is explicit, greppable, has no magic, and no startup-order surprises:

```ts
// composition root — the ONLY place that knows concrete types
const db        = new PostgresDatabase(config.databaseUrl);
const orders    = new OrderRepository(db);
const inventory = new InventoryService(db);
const service   = new OrderService(orders, inventory);
const controller= new OrderController(service);
```

Reach for a container when the graph is large enough that this becomes tedious, or when your framework assumes one.

## 6. The failure modes

- **Circular dependencies.** `A` needs `B`, `B` needs `A`. Constructor injection makes this a *hard error* — which is correct, because it's a design problem. The fix is not `forwardRef()`; it's extracting the shared logic into a third thing, or having one side emit an event instead of calling directly. **`forwardRef` is a smell, not a solution.**
- **The container as a service locator.** Injecting the container itself and calling `container.get('Thing')` inside a method throws away every benefit — dependencies are hidden again, and now they fail at runtime instead of at construction.
- **Scope confusion.** Injecting a request-scoped thing (the current user) into a singleton means every request sees whoever arrived first. This is a real, nasty, intermittent production bug. Pass request data as a *method argument*, or use `AsyncLocalStorage` for genuinely ambient context like a trace ID.
- **Over-abstracting the database.** Wrapping your ORM in a repository interface *and* a service interface *and* a unit-of-work interface, for one implementation, is architecture as ritual.

## 7. Worked example — the scope bug, reproduced and fixed

The failure mode most likely to reach production: **per-request data stored on an instance that every request shares.** Here it is, deliberately, with two fixes.

```ts
// app.ts — a manual composition root, and the scope bug it makes visible
import { AsyncLocalStorage } from "node:async_hooks";

const tick = () => new Promise((resolve) => setTimeout(resolve, 5));

// ---- the dependencies ----
export type AuditLog = { entries: string[] };

// BUG: built once at startup, but holds per-request data.
export class AuditServiceWithUserField {
  log: AuditLog;
  currentUser = "nobody";
  constructor(log: AuditLog) {
    this.log = log;
  }
  setUser(user: string) {
    this.currentUser = user;
  }
  async record(action: string) {
    await tick(); // any await lets another request run in between
    this.log.entries.push(`${this.currentUser}: ${action}`);
  }
}

// FIX 1: request data is a method argument.
export class AuditService {
  log: AuditLog;
  constructor(log: AuditLog) {
    this.log = log;
  }
  async record(user: string, action: string) {
    await tick();
    this.log.entries.push(`${user}: ${action}`);
  }
}

// FIX 2: ambient per-request context, for things every layer needs (trace IDs, the current user).
export const requestContext = new AsyncLocalStorage<{ user: string }>();
export class ContextAuditService {
  log: AuditLog;
  constructor(log: AuditLog) {
    this.log = log;
  }
  async record(action: string) {
    await tick();
    this.log.entries.push(`${requestContext.getStore()?.user ?? "nobody"}: ${action}`);
  }
}

// ---- the composition root: the only place that knows concrete types ----
export function compose() {
  const log: AuditLog = { entries: [] };
  return {
    log,
    buggy: new AuditServiceWithUserField(log),
    audit: new AuditService(log),
    contextAudit: new ContextAuditService(log),
  };
}
```

**Predict before running.** Two requests, from `ada` and `bayo`, arrive at the same time and both go through the buggy service. What are the two audit entries?

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { compose, requestContext } from "./app.ts";

test("BUG: a per-request field on a shared instance records the wrong user", async () => {
  const { log, buggy } = compose();
  const handle = async (user: string) => {
    buggy.setUser(user);
    await buggy.record("viewed invoice");
  };
  await Promise.all([handle("ada"), handle("bayo")]); // two requests at once
  assert.deepEqual(log.entries, ["bayo: viewed invoice", "bayo: viewed invoice"]);
});

test("FIX 1: pass request data as an argument", async () => {
  const { log, audit } = compose();
  await Promise.all([audit.record("ada", "viewed invoice"), audit.record("bayo", "viewed invoice")]);
  assert.deepEqual(log.entries.sort(), ["ada: viewed invoice", "bayo: viewed invoice"]);
});

test("FIX 2: AsyncLocalStorage gives each request its own context", async () => {
  const { log, contextAudit } = compose();
  const handle = (user: string) => requestContext.run({ user }, () => contextAudit.record("viewed invoice"));
  await Promise.all([handle("ada"), handle("bayo")]);
  assert.deepEqual(log.entries.sort(), ["ada: viewed invoice", "bayo: viewed invoice"]);
});
```

**Lab:** these files are in `labs/dependency-injection/typescript/`. From the vault root, `python3 labs/run.py dependency-injection/typescript` runs them and checks this page still shows the same code.

**Run it.** Both files in one folder; `node --test` from it (Node 23.6 or later; checked with Node 26). Expected:

```
ℹ tests 3
ℹ pass 3
ℹ fail 0
```

**The answer: `bayo` twice.** Ada's request sets the user, reaches `await`, and pauses. Bayo's request then sets the user to `bayo` on the *same object*. When Ada's request resumes, it reads `bayo`. The first test asserts this wrong result on purpose, so the bug is visible. In production it's intermittent — it needs two requests close enough in time — which is why it survives code review and testing.

**Choosing between the fixes.** Pass it as an argument (fix 1) whenever you can: the dependency is visible in the signature. Use `AsyncLocalStorage` (fix 2) for genuinely ambient data that every layer needs and that would otherwise be threaded through dozens of signatures — a trace ID, the current tenant.

**What NestJS does instead.** Nest can make a provider request-scoped (`@Injectable({ scope: Scope.REQUEST })`), creating a new instance per request. It's correct, but that scope spreads to everything that injects it, and it costs an allocation per request. Most Nest codebases pass the user as an argument instead.

## Check your understanding

1. What's the difference between dependency injection and a DI container?
2. Give two things field injection hides that constructor injection shows.
3. Two services need each other. Why is `forwardRef()` the wrong fix, and what are the right ones?
4. Why is injecting the container itself and calling `container.get()` worse than not using DI at all?
5. **Predict.** In the buggy service, if `record` had no `await` in it, would the two requests still mix up users? Why?

<details>
<summary>Answers — after your attempt</summary>

1. DI is the rule — be handed your dependencies. A container is an optional tool that automates the handing for large object graphs. You can do DI with plain constructors.
2. Any two of: how many dependencies the class has (the "too big" signal); that the object can exist half-built; that it can't be constructed with plain `new` in a test.
3. A cycle is a design problem; `forwardRef` hides it. Extract the shared logic into a third service both depend on, or have one side publish an event instead of calling the other.
4. Dependencies are hidden again, as with a singleton, and a missing one fails at the moment it's used instead of at startup.
5. No. JavaScript runs one piece of synchronous code at a time, so `setUser` and the push would run back-to-back with no chance for the other request to interleave. The bug needs an `await` between setting and reading — which real code nearly always has: a database call, an HTTP call.

</details>

## Practice — independent task

**Write a composition root for one of your projects** — or for the worked example in [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|layers]].

1. Create a single `compose()` function that builds every service, repository and client in dependency order and returns what the HTTP layer needs.
2. Write an integration-style test that calls `compose()` with fake clients for every external service — database, email, payments.
3. Search for any per-request value stored on a long-lived object: `grep -rn "this.currentUser\|this.user =\|this.tenant" src/`. Fix any you find with an argument or `AsyncLocalStorage`, with a concurrent test like the one above.

**Done when:** `compose()` is the only file that calls `new` on a client or service, the fake-wired test runs with no network, and your concurrency test fails before the fix and passes after.

## Before moving on

You can wire an app by hand, explain what a container automates, and reproduce and fix the scope bug.

**Recap.** Be handed your tools; don't make them. Constructor injection keeps dependencies visible and objects never half-built. One composition root knows the concrete types. Request data belongs in arguments or request context, never on a shared instance.

**Next.** [[backend/03-structuring-a-backend/05-modular-monolith-to-services|Modular monolith to services]] — the same boundaries, at the scale of a whole system (week 4).

## Key insight

DI is not a framework, a container, or an annotation — it's the single rule that **a class should declare what it needs and be given it, rather than going out and getting it.** You can follow that rule with plain constructors and twenty lines in `main`. Everything else — containers, decorators, autowiring — is convenience for when the object graph gets big. Teams that learn the container before the rule end up with magic they can't test.

## Related
- [[backend/03-structuring-a-backend/03b-dependency-injection-in-other-languages|Dependency injection in other languages]] — Python, Go, Java, Rust, C, C++ and C#, and what each does about the scope bug
- [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|Layers]] — what's being wired together
- [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|Hexagonal & Clean Architecture]] — where interfaces genuinely earn their place
- [[languages/01-java/03-tooling/02-dependency-injection|Dependency Injection (Java)]] — Spring's implementation
- [[backend/frameworks/javascript/03-nest/index|NestJS]] — a decorator-based container in practice
