# Functional Programming

**Source:** consolidated from the streams/lambdas/`Optional` material that used to live in `fundamentals`, drawn from both projects' real usage (the `SubscriptionService` stream filters and `OptionalInt` config lookups are actual code), plus the [roadmap.sh Java](https://roadmap.sh/java) functional nodes (higher-order functions, composition) the projects didn't name explicitly.

## Functional interfaces and lambdas

A **functional interface** has exactly one abstract method, so a lambda can stand in for an instance of it. This is the bridge between Java's OO core and functional style:

```java
@FunctionalInterface
public interface DeliverCallback { void handle(String tag, Delivery msg) throws IOException; }

DeliverCallback cb = (tag, delivery) -> process(delivery);   // lambda replaces an anonymous class
```

The `java.util.function` package supplies the general-purpose ones you'll use constantly:

| Interface | Shape | Typical use |
|---|---|---|
| `Function<T,R>` | `T -> R` | transform/map |
| `Predicate<T>` | `T -> boolean` | filter/test |
| `Consumer<T>` | `T -> void` | side effect (`forEach`) |
| `Supplier<T>` | `() -> T` | lazy/deferred value |
| `BiFunction<T,U,R>` | `(T,U) -> R` | two-arg transform |

A lambda captures surrounding local variables, which must be **effectively final** (assigned once) — the same rule from [[languages/01-java/01-language/01-fundamentals|Fundamentals]], and why loop bodies sometimes copy a counter into a `final` local before using it in a lambda.

## Method references

When a lambda just calls one existing method, a **method reference** says so more directly — four forms:

```java
list.forEach(System.out::println);              // instance method of an arbitrary object
names.stream().map(String::toUpperCase)          // instance method on the stream element
     .map(Transaction::new)                      // constructor reference
     .sorted(Comparator.comparing(Transaction::getAmount));   // getter reference
```

`Transaction::getAmount` reads as "the function that, given a Transaction, returns its amount" — the same thing as `t -> t.getAmount()`, just without the noise.

## The Stream API

A **stream** is a pipeline over a data source: a lazy chain of intermediate operations (`filter`, `map`, `sorted`, `distinct`, `limit`) ending in one terminal operation (`collect`, `toList`, `count`, `reduce`, `findFirst`, `anyMatch`) that actually runs the pipeline:

```java
List<SubscriptionRecord> active = subscriptions.values().stream()
        .filter(s -> s.getDebitAccount().equals(account))   // intermediate — lazy
        .filter(s -> "ACTIVE".equals(s.getStatus()))
        .sorted(Comparator.comparing(SubscriptionRecord::getCreatedAt))
        .toList();                                            // terminal — triggers execution
```

**Laziness matters**: nothing runs until the terminal op, and short-circuiting terminals (`findFirst`, `anyMatch`) stop early instead of processing the whole source. `Collectors` build richer results — `groupingBy`, `toMap`, `joining`, `counting`:

```java
Map<String, List<Transaction>> byCurrency =
        txns.stream().collect(Collectors.groupingBy(Transaction::getCurrency));
```

**When *not* to reach for a stream**: a simple index-based loop, or one that mutates external state, is often clearer as a plain `for`. Streams shine for declarative transform/filter/aggregate pipelines, not for everything. And a parallel stream (`.parallelStream()`) is rarely the right lever — it splits work across the common ForkJoinPool and only helps for large, CPU-bound, side-effect-free workloads; on small or IO-bound data it's slower and riskier than a plain loop.

## Higher-order functions and composition

A **higher-order function** takes or returns a function — `map`, `filter`, and `Comparator.comparing` all are. `Function` and `Predicate` compose, which lets you build complex behavior from small named pieces:

```java
Predicate<Transaction> isLarge  = t -> t.getAmount().compareTo(THRESHOLD) > 0;
Predicate<Transaction> isGhs    = t -> "GHS".equals(t.getCurrency());
Predicate<Transaction> flag     = isLarge.and(isGhs);            // combine predicates

Function<Transaction, String> describe =
        ((Function<Transaction,BigDecimal>) Transaction::getAmount)
                .andThen(BigDecimal::toPlainString);            // f.andThen(g) = g(f(x))
```

`Comparator` composition (`comparing(...).thenComparing(...).reversed()`) is the most common real use — see [[languages/01-java/01-language/04-collections|Collections]].

## Method chaining and fluent APIs

Returning `this` (or a new immutable copy) from each method lets calls chain into a readable pipeline — the basis of builders, streams, and `Optional`:

```java
SubscriptionRecord.builder().subscriptionId("SUB1").debitAmount("50.00").build();
```

The design principle is that each step returns something the next step can act on. Builders are covered in [[languages/01-java/03-tooling/03-lombok-and-builders|Lombok & Builders]].

## Optional — absence as a type

`Optional<T>` makes "might be missing" explicit in the signature instead of relying on `null` and hoping callers check:

```java
public Optional<CountryDialingCode> fromIso(String iso) {
    return Arrays.stream(values()).filter(c -> c.matches(iso)).findFirst();
}

// Consuming it — no null check, no NPE:
String prefix = fromIso(country)
        .map(CountryDialingCode::prefix)
        .orElse("unknown");
```

Key operations: `map` / `flatMap` (transform if present), `filter`, `orElse` / `orElseGet` / `orElseThrow`, `ifPresent`. `OptionalInt`/`OptionalLong`/`OptionalDouble` are the primitive-specialized versions that avoid boxing — the payment sandbox uses `OptionalInt` for reading a numeric config value that might be absent:

```java
OptionalInt retryAttempts = getConfigIntValue(config, "retryAttempts");
if (retryAttempts.isPresent() && retryAttempts.getAsInt() > 1) { /* validation error */ }
```

Style rule: use `Optional` as a **return type** to signal optionality; don't use it for fields or method parameters (it adds allocation and awkwardness there).

## Related
- [[languages/01-java/01-language/03-generics|Generics]] — the `<T,R>` type parameters on every functional interface
- [[languages/01-java/01-language/04-collections|Collections]] — what streams flow over
- [[languages/01-java/01-language/07-modern-java|Modern Java]] — pattern matching pairs with functional style
