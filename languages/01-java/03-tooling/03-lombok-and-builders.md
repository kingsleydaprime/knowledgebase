# Lombok & the Builder Pattern

**Source:** merged from `record-id-generator-java/learning/03-lombok-and-configuration.md` and `direct-debit-sandbox-java/learning/03-dtos-lombok-builder.md`.

## The boilerplate problem Lombok solves

A plain Java class with 25 fields needs a constructor, 25 getters, 25 setters, `toString()`, `equals()`, and `hashCode()` — 200+ lines that carry zero business logic. Just 5 of those 25 fields, written by hand:

```java
public class Transaction {
    private String id;
    private BigDecimal amount;
    // ... 3 more fields

    public Transaction() {}
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    // ... a getter + setter pair per field
    @Override public String toString() { return "Transaction{id=" + id + ", ...}"; }
    @Override public boolean equals(Object o) { /* ... */ }
    @Override public int hashCode() { return Objects.hash(id, amount /* , ... */); }
}
```

With `@Data`, the equivalent class is just the field declarations:

```java
import lombok.Data;

@Data
public class Transaction {
    private String id;
    private BigDecimal amount;
    // ...
}
```

`@Data` generates a getter for every field, a setter for every non-final field, `toString()`, `equals()`/`hashCode()`, and a required-args constructor — all regenerated automatically on every build, so there's never a stale `toString()` after adding a field.

**How it works**: Lombok is a compiler annotation processor — it injects bytecode during compilation. There is no runtime dependency; it's `compileOnly` in Gradle.

## The core annotations

```java
@Data                     // getters, setters, equals, hashCode, toString
@Builder                  // fluent builder (see below)
@Slf4j                    // generates a `log` field — no manual LoggerFactory.getLogger() boilerplate
@RequiredArgsConstructor  // constructor for every `private final` field — used for DI (see 05-spring-boot-and-scheduling.md)
```

`@Slf4j` replaces `private static final Logger log = LoggerFactory.getLogger(MyClass.class);` with one class-level annotation, then `log.info(...)`/`log.error(...)` works anywhere in the class.

## Why DTOs exist as a separate layer

A **DTO (Data Transfer Object)** is a class whose only job is carrying data across a boundary — typically an HTTP request/response. It's kept separate from the internal storage model because:

- The request shape often differs from the stored shape (server-generated fields like `subscriptionId` aren't sent by the caller)
- Validation annotations belong on the input boundary, not the storage model
- Input and output can evolve independently of internal representation

A project ends up with many small DTOs (`SubscriptionRequestDto`, `UpdateRequest`, `CancelRequest`) — each shaped to exactly what one endpoint needs, not a shared "one model to rule them all."

## The Builder pattern

Constructors with many positional parameters are unreadable and error-prone — nothing stops two adjacent `String` arguments from being silently swapped:

```java
// Which argument is which? Impossible to tell at the call site.
new SubscriptionRecord("SUB123", "MAND456", "MERCH789", "0241234567", "50.00", ...);
```

`@Builder` generates a fluent, named alternative:

```java
SubscriptionRecord record = SubscriptionRecord.builder()
        .subscriptionId("SUB123")
        .mandateId("MAND456")
        .debitAmount("50.00")
        .build();   // required — this is what actually constructs the object
```

Every field is named, optional fields can be skipped, and there's no argument-order footgun. Before `.build()` you're operating on the builder helper, not the real object.

## Partial updates — conditional field preservation

When updating an existing record, the caller usually only sends the fields they're changing. Two idiomatic ways to implement "only overwrite what was explicitly provided":

**Ternary + builder** (for constructing a new object from an existing one plus a request):

```java
ProvisionRecord record = ProvisionRecord.builder()
        .callbackUrl(req.getCallbackUrl())                       // always overwrite
        .retryAttempts(req.getRetryAttempts() != null
                ? req.getRetryAttempts()                          // caller sent a value — use it
                : (existing != null ? existing.getRetryAttempts() : null))  // else keep old value
        .build();
```

**Guarded setters** (for mutating an existing object in place):

```java
if (req.getDebitAmount() != null) existing.setDebitAmount(req.getDebitAmount());
if (req.getDebitDay()    != null) existing.setDebitDay(req.getDebitDay());
```

Both implement the same **partial update / merge** pattern — callers can change one field without wiping out fields they didn't mention. Builder-style suits constructing new objects; setter-style suits patching an existing one in place. Neither is universally correct.

## Response mapping — don't leak internal models

Returning an internal record directly from an endpoint leaks internal field names that may not match the public API contract, and exposes fields that were never meant to be public:

```java
private Map<String, Object> toRetrieveResponse(PreAuthRecord r) {
    Map<String, Object> m = new LinkedHashMap<>();  // preserves insertion order → deterministic JSON
    m.put("preApprovalId", r.getPreApprovalId());
    m.put("debitSource",   r.getChannel());          // renamed for the public contract
    m.put("created",       r.getCreatedAt());        // renamed
    // callbackUrl intentionally omitted — internal only
    return m;
}
```

Use `LinkedHashMap`, not `HashMap`, whenever field order in the output JSON should be stable and match documentation — a plain `HashMap` doesn't guarantee iteration order.

## Related
- [[languages/01-java/01-language/01-fundamentals|Fundamentals]] — what `@Data` is generating under the hood
- [[backend/frameworks/java/01-spring-boot|Spring Boot & Scheduling]] — `@RequiredArgsConstructor` in the context of dependency injection
- [[languages/01-java/04-persistence/01-jdbc-and-data-modeling|Persistence & Data Modeling]] — the fallback-resolution and secondary-index patterns that pair with partial updates
