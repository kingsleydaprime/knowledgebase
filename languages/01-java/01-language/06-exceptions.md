---
id: c597b1e3-e884-4ae5-846b-9d3a19d0739b
---

# Exceptions

**Source:** the try-with-resources and catch-and-handle material is real project code (the JDBC and RabbitMQ paths in [[languages/01-java/04-persistence/01-jdbc-and-data-modeling|JDBC & Data Modeling]] and [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging]]); the checked/unchecked hierarchy and custom-exception design are filled in from [roadmap.sh Java](https://roadmap.sh/java).

## The exception hierarchy
<!-- bite: bd3e0f88-d65c-4033-ad44-a42bd9ffffc0 -->

Everything throwable descends from `Throwable`, which splits into two branches:

```text
Throwable
├── Error                      — JVM-level, unrecoverable (OutOfMemoryError, StackOverflowError). Don't catch.
└── Exception
    ├── RuntimeException        — UNCHECKED (NullPointerException, IllegalArgumentException, ...)
    └── (everything else)       — CHECKED (IOException, SQLException, ...)
```

The checked/unchecked split is the distinction that matters:

- **Checked** exceptions must be either caught or declared in the method's `throws` clause — the compiler enforces it. They model recoverable, expected failures at a boundary (a DB call, a file read): `SQLException`, `IOException`.
- **Unchecked** (`RuntimeException` and subclasses) need no declaration — they model programming errors that generally shouldn't be caught-and-continued: `NullPointerException`, `IllegalArgumentException`, `IllegalStateException`, `ClassCastException`.

## try / catch / finally
<!-- bite: 42fdbde8-d194-4cba-b171-36edfed8df57 -->

```java
try {
    repository.save(record);
} catch (SQLIntegrityConstraintViolationException e) {
    // most specific first — a duplicate key: regenerate and retry
} catch (SQLException e) {
    // more general DB error
} finally {
    // runs no matter what — success, caught exception, or uncaught
}
```

Order catch blocks **most-specific first**; a broader type before a narrower one is a compile error (the narrower one would be unreachable). `finally` always runs — even if the `try` or a `catch` returns — which historically made it the place to close resources. That job now belongs to try-with-resources.

Multi-catch collapses identical handling: `catch (IOException | TimeoutException e)`.

## Try-with-resources — automatic cleanup
<!-- bite: 762fba46-4a66-4640-9d4a-a15ad53027d3 -->

Anything implementing `AutoCloseable` declared in the `try (...)` header is closed automatically when the block exits, in **reverse** declaration order, even on exception — no `finally` needed:

```java
try (Connection conn = DatabaseConfig.getConnection();
     PreparedStatement stmt = conn.prepareStatement(sql)) {
    stmt.executeUpdate();
}   // stmt.close() then conn.close(), guaranteed
```

This is strictly better than a manual `finally { conn.close(); }`, which is easy to get wrong (forgetting to null-check, or an exception *inside* `close()` masking the original). Try-with-resources also correctly handles the "exception during close" case by attaching it as a *suppressed* exception rather than losing the primary one. The projects use it everywhere JDBC connections, statements, and file readers are opened.

## Custom exceptions
<!-- bite: 9f05c502-3b7e-48dc-bbb5-739f5bbb701d -->

Define your own when a failure is meaningful to the domain and callers might handle it specifically. Extend `RuntimeException` for unchecked (the common modern default — checked exceptions are increasingly seen as caller-burden), or `Exception` for checked:

```java
public class DuplicateReferenceException extends RuntimeException {
    public DuplicateReferenceException(String reference) {
        super("Subscription already exists for reference: " + reference);
    }
}
```

**Always preserve the cause** when wrapping a lower-level exception, or you throw away the stack trace that tells you what actually broke:

```java
catch (SQLException e) {
    throw new DataAccessException("failed to save transaction", e);   // e is the cause — chained, not discarded
}
```

## Practical rules
<!-- bite: 72135954-1b87-4fbc-b557-f48803ecb52a -->

- **Catch specific, not `Exception` / `Throwable`** — a blanket catch swallows bugs (an NPE from a typo) alongside the failure you meant to handle. The projects' consumer catches the *specific* constraint-violation to distinguish a retryable duplicate from a real error.
- **Never swallow silently** — an empty `catch { }` is how failures vanish. At minimum log it with the throwable (`log.error("...", e)`) so the stack trace survives (see [[languages/01-java/03-tooling/05-logging-and-observability|Logging]]).
- **Don't use exceptions for control flow** — they're expensive (stack capture) and obscure intent; a null check or an `Optional` is cheaper than catching an NPE.
- **Fail fast on programmer error** — validate arguments and throw `IllegalArgumentException`/`IllegalStateException` early, close to the mistake, rather than letting a bad value propagate into a confusing failure later.

The message-queue consumer is a worked example of *deliberate* exception strategy: a transient failure is retried, a permanent one is routed to a Dead Letter Queue, and the raw payload is logged for replay — see [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ]].

## Related
<!-- bite: 96a8dd37-b40b-431f-9d66-1a5699115f20 -->
- [[languages/01-java/01-language/01-fundamentals|Fundamentals]] — where try-with-resources first appears
- [[languages/01-java/03-tooling/05-logging-and-observability|Logging & Observability]] — logging a throwable with its stack trace
- [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ]] — exceptions as a pipeline failure-handling strategy
