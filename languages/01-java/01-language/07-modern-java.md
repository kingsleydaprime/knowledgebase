# Modern Java

**Source:** text blocks and switch expressions are real project code (SQL statements and the `ScenarioEngine`); records, sealed classes, pattern matching, and `var` are **[reference]** — the projects predated or didn't adopt them, but they're the current idiomatic language and directly relevant to the Lombok-heavy DTO code the projects *did* write.

Java ships a new release every six months now, with an LTS every two years (8, 11, 17, 21, 25…). "Modern Java" here means the features that have genuinely changed how idiomatic code reads since Java 8.

## `var` — local type inference

`var` lets the compiler infer a local variable's type from its initializer. It's still **statically typed** — `var` is not `Object` and not dynamic; the type is fixed at compile time, just not spelled out:

```java
var subscriptions = new HashMap<String, SubscriptionRecord>();   // inferred as HashMap<String, SubscriptionRecord>
var total = BigDecimal.ZERO;
```

Use it where the type is obvious from the right-hand side (cuts noise on verbose generics); avoid it where it hurts readability (`var x = getThing()` hides what `x` is). Locals only — not fields, not method parameters or return types.

## Text blocks

Multi-line string literals (`"""`), Java 15+ — they replace fragile concatenation for SQL, JSON, HTML. Leading whitespace common to all lines is stripped based on the closing delimiter's indentation:

```java
String sql = """
        INSERT INTO transactions (id, amount)
        VALUES (?, ?)
        """;
```

Real project use: every JDBC SQL statement and the OpenAPI description Markdown. `\s` at line-end forces a trailing space that would otherwise be trimmed.

## Switch expressions

Modern `switch` is an **expression** that produces a value — arrow labels, no fall-through, no `break`, and the compiler can enforce exhaustiveness:

```java
String message = switch (responseCode) {
    case "01"        -> "Success";
    case "100", "101" -> "Failed";        // multiple labels
    default          -> "Unknown";
};
```

The payment sandbox's `ScenarioEngine` maps account suffixes to outcomes this way. A `yield` statement returns a value from a multi-line `{ }` case body.

## Records — the data carrier

A `record` is an immutable data class where the compiler generates the constructor, private final fields, accessors, `equals`, `hashCode`, and `toString` from a one-line declaration:

```java
public record CancelRequest(String subscriptionId, String reason) {}
```

That single line replaces exactly the boilerplate Lombok's `@Data` generates — which is the honest connection to the projects: they used `@Data` because records either didn't exist yet or weren't adopted. **Records are the language's built-in answer to the same problem Lombok solves**, with no annotation processor and no dependency:

| | Lombok `@Data` class | `record` |
|---|---|---|
| Mutability | mutable (has setters) | **immutable** (no setters, final fields) |
| Dependency | Lombok (compile-time) | none — pure language |
| `equals`/`hashCode`/`toString` | generated | generated |
| Inheritance | can extend a class | cannot extend (can implement interfaces) |
| Best for | mutable entities/records | DTOs, value objects, tuples |

For a request/response DTO — inherently immutable, value-based — a record is the better modern default. See [[languages/01-java/03-tooling/03-lombok-and-builders|Lombok & Builders]] for where Lombok still earns its place (mutable entities, `@Builder`, `@Slf4j`).

You can add validation in a **compact canonical constructor**:

```java
public record Money(BigDecimal amount, String currency) {
    public Money {                                  // compact constructor — no parameter list
        if (amount.signum() < 0) throw new IllegalArgumentException("negative amount");
    }
}
```

## Sealed classes

A `sealed` type restricts *which* classes may extend or implement it — the hierarchy is closed and known to the compiler:

```java
public sealed interface PaymentEvent permits Authorized, Declined, Refunded {}
public record Authorized(String id) implements PaymentEvent {}
public record Declined(String id, String reason) implements PaymentEvent {}
public record Refunded(String id, BigDecimal amount) implements PaymentEvent {}
```

The payoff is exhaustiveness: because the compiler knows the complete set of subtypes, a `switch` over a sealed type needs **no `default`** and will fail to compile if you add a new subtype and forget to handle it — turning "did I cover every case?" from a runtime hope into a compile-time guarantee. This pairs directly with pattern matching.

## Pattern matching

**`instanceof` patterns** bind the cast variable in one step, killing the classic test-then-cast dance:

```java
// Old
if (o instanceof Transaction) { Transaction t = (Transaction) o; use(t); }
// Pattern matching
if (o instanceof Transaction t) { use(t); }        // t is in scope and typed when the test passes
```

**Pattern matching in `switch`** dispatches on type and deconstructs records in one expression — combined with sealed types, it's exhaustive:

```java
String describe(PaymentEvent e) {
    return switch (e) {
        case Authorized a          -> "authorized " + a.id();
        case Declined(var id, var reason) -> "declined " + id + ": " + reason;   // record deconstruction
        case Refunded r            -> "refunded " + r.amount();
        // no default needed — the sealed hierarchy is complete
    };
}
```

This trio — sealed types + records + pattern-matching switch — is Java's answer to algebraic data types and the modern alternative to the visitor pattern for closed hierarchies.

## Why this matters even against a Lombok/JDBC codebase

The projects this domain is built from used `@Data` DTOs and hand-written type checks because that was the idiom at the time. Knowing records/sealed/pattern-matching is what lets you *modernize* that code with judgment — swapping an immutable DTO to a record, or replacing a chain of `instanceof`-and-cast with an exhaustive switch — rather than cargo-culting the old style forward.

## Related
- [[languages/01-java/03-tooling/03-lombok-and-builders|Lombok & Builders]] — the library records partly supersede
- [[languages/01-java/01-language/02-oop|OOP]] — sealed types close an inheritance hierarchy
- [[languages/01-java/01-language/05-functional-programming|Functional Programming]] — pattern matching pairs with functional dispatch
