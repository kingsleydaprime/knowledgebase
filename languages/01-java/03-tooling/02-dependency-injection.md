# Dependency Injection

**Source:** the payment sandbox uses Spring DI throughout (`@Service` + `@RequiredArgsConstructor` is real code — see [[languages/01-java/05-web-and-api/01-spring-boot|Spring Boot]]); this file pulls the *concept* out from under the framework, since roadmap.sh lists it as its own topic and it's worth understanding independently of Spring.

## Inversion of Control — the idea

Normally a class creates the things it needs:

```java
public class SubscriptionService {
    private final Store store = new InMemoryStore();   // the class chooses and builds its own dependency
}
```

**Inversion of Control (IoC)** flips that: the class *declares* what it needs and something external supplies it. **Dependency Injection (DI)** is the most common form of IoC — dependencies are handed in rather than constructed internally:

```java
public class SubscriptionService {
    private final Store store;
    public SubscriptionService(Store store) { this.store = store; }   // supplied from outside
}
```

## Why bother

- **Decoupling** — `SubscriptionService` depends on the `Store` *interface*, not `InMemoryStore`. Swap the implementation (in-memory → database-backed) with zero change to the service. This is the [[languages/01-java/01-language/02-oop|polymorphism]] payoff made structural.
- **Testability** — a test injects a *fake* or *mock* `Store` ([[languages/01-java/03-tooling/04-testing|Testing]]) instead of a real database. A class that `new`s its own dependencies can't be tested in isolation; a class that receives them can.
- **Single source of truth** — one shared `Store` instance, not accidental duplicates each holding different data.

## The three injection styles

```java
// 1. Constructor injection — PREFERRED
public SubscriptionService(Store store) { this.store = store; }

// 2. Setter injection — for genuinely optional dependencies
public void setStore(Store store) { this.store = store; }

// 3. Field injection — convenient, discouraged
@Autowired private Store store;
```

**Prefer constructor injection.** It lets the field be `final` (immutable, can't be reassigned mid-request), makes dependencies explicit in the signature (a constructor with ten parameters is a visible "this class does too much" smell), and needs no framework to construct in a test — you just call `new`. Field injection hides dependencies and can't be `final`, and a field-injected class can't be instantiated without the framework's reflection.

## How Spring does it

Spring is an **IoC container**: at startup it scans for classes annotated as components, instantiates them as **beans**, and wires each bean's dependencies by matching types:

```java
@Service                       // "manage this class as a bean"
@RequiredArgsConstructor       // Lombok generates a constructor for every `private final` field
public class SubscriptionService {
    private final Store store;             // Spring injects the registered Store bean
    private final CallbackService callbacks;
}
```

`@RequiredArgsConstructor` + `final` fields is the idiomatic modern pattern — it *is* constructor injection, with Lombok writing the constructor. Spring sees that constructor and calls it with the beans it manages. Component stereotypes (`@Component`, `@Service`, `@Repository`, `@Configuration`) all register a bean; `@Bean` methods register one explicitly. When two beans satisfy the same type, `@Qualifier` or `@Primary` disambiguates.

The container also owns each bean's **lifecycle** and **scope** (singleton by default — one shared instance — or `prototype`/`request`/`session`). Spring's whole framework, and everything in [[languages/01-java/05-web-and-api/01-spring-boot|Spring Boot]], is built on this container.

Beyond Spring, the same idea appears as **CDI** (Jakarta EE / `@Inject`), **Guice** (Google's standalone injector), and **Dagger** (compile-time DI, popular on Android for zero reflection overhead) — but the concept is identical: declare dependencies, let a container supply them.

## Related
- [[languages/01-java/05-web-and-api/01-spring-boot|Spring Boot]] — DI applied across a real service
- [[languages/01-java/03-tooling/04-testing|Testing]] — injecting mocks is why DI makes code testable
- [[languages/01-java/01-language/02-oop|OOP]] — depending on interfaces, the abstraction DI exploits
- [[concepts/03-design-patterns/README|Design Patterns]] — DI vs the Factory/Service Locator patterns
