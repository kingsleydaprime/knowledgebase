# Dependency Injection & Wiring

**[Intermediate]** — how the layers actually get connected, and why the answer isn't "just import it."

## The kid version first

A chef needs an oven.

- **Option A:** the chef *builds their own oven* the moment they need one. Now the chef can only ever work in a kitchen where they can build that exact oven. Want to test the recipe without a real oven? You can't.
- **Option B:** the chef is *handed* an oven when they start their shift. They don't care where it came from. Hand them a real one in production, a pretend one in a test.

That's it. Dependency injection is "be handed your tools instead of making them." Everything else is plumbing.

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

## What it actually buys you

The usual answer is "decoupling," which is too vague to act on. The concrete wins:

1. **Testing without a framework or a database.** `new OrderService(fakeDb)` — no container, no HTTP, no Docker. This is the biggest practical payoff by a wide margin.
2. **One place that knows how things are built.** Connection strings, pool sizes, retry policies live at the composition root rather than scattered through every class that needs a client.
3. **Lifecycle management.** One shared database pool, one logger, a new instance per request where needed. The container handles ordering and shutdown.
4. **Honest feedback about design.** A constructor with nine parameters is telling you the class does too much. That signal is valuable — and it's exactly the signal that field injection hides.

## Constructor injection, and why not the alternatives

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

## Interfaces: when they earn their keep

The purist position is "always depend on an interface." That's over-applied. An interface earns its place when:

- **There will genuinely be more than one implementation** — a real one and a fake, or Stripe and PayPal.
- **You're crossing an architectural boundary** — the port in [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|ports and adapters]].
- **You need to break a compile-time dependency cycle** between modules.

It does *not* earn its place when there's exactly one implementation and always will be, and your test framework can mock a concrete class anyway. `IOrderServiceImpl` implementing `IOrderService` with identical methods is ceremony. **In TypeScript especially, structural typing means a plain object often satisfies the shape without any interface declaration at all.**

## How frameworks do the wiring

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

## The failure modes

- **Circular dependencies.** `A` needs `B`, `B` needs `A`. Constructor injection makes this a *hard error* — which is correct, because it's a design problem. The fix is not `forwardRef()`; it's extracting the shared logic into a third thing, or having one side emit an event instead of calling directly. **`forwardRef` is a smell, not a solution.**
- **The container as a service locator.** Injecting the container itself and calling `container.get('Thing')` inside a method throws away every benefit — dependencies are hidden again, and now they fail at runtime instead of at construction.
- **Scope confusion.** Injecting a request-scoped thing (the current user) into a singleton means every request sees whoever arrived first. This is a real, nasty, intermittent production bug. Pass request data as a *method argument*, or use `AsyncLocalStorage` for genuinely ambient context like a trace ID.
- **Over-abstracting the database.** Wrapping your ORM in a repository interface *and* a service interface *and* a unit-of-work interface, for one implementation, is architecture as ritual.

## Key insight

DI is not a framework, a container, or an annotation — it's the single rule that **a class should declare what it needs and be given it, rather than going out and getting it.** You can follow that rule with plain constructors and twenty lines in `main`. Everything else — containers, decorators, autowiring — is convenience for when the object graph gets big. Teams that learn the container before the rule end up with magic they can't test.

## Related
- [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|Layers]] — what's being wired together
- [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|Hexagonal & Clean Architecture]] — where interfaces genuinely earn their place
- [[languages/01-java/03-tooling/02-dependency-injection|Dependency Injection (Java)]] — Spring's implementation
- [[backend/frameworks/javascript/03-nest/README|NestJS]] — a decorator-based container in practice
