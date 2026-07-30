# Record ID Generator — Java Fundamentals

Split out from the original single-file `learning.md` (a beginner-to-advanced guide built from
processing a 1.46GB CSV, generating unique 12-digit IDs, pushing records through RabbitMQ, and
persisting to MySQL — all in Java). See also `02-build-tools-and-architecture.md`,
`03-lombok-and-configuration.md`, `04-database-mysql-flyway.md`, `05-rabbitmq-messaging.md`,
`06-concurrency-and-threads.md`, `07-id-generation-and-idempotency.md`,
`08-csv-parsing-and-data-quality.md`, `09-logging-and-observability.md`, and
`10-docker-and-performance-tuning.md`.

---

## 1. Why Java?

Java is the dominant language in enterprise and fintech. It is statically typed, compiled to bytecode, and runs on the JVM (Java Virtual Machine). Every major bank, payment processor, and fintech company (like ITC) has Java at its core.

Key traits:
- **Strongly typed** — every variable has a declared type
- **Compiled** — caught at compile time, not runtime
- **Object-oriented** — everything lives in classes
- **Platform-independent** — write once, run anywhere (JVM handles it)

---


---

## 5. Java Basics You Need to Know

### Classes and Objects
```java
// A class is a blueprint
public class Transaction {
    private String id;       // field
    private BigDecimal amount;

    // Constructor
    public Transaction(String id, BigDecimal amount) {
        this.id = id;
        this.amount = amount;
    }

    // Getter
    public String getId() { return id; }
}

// Create an object (instance of the class)
Transaction t = new Transaction("123456789012", new BigDecimal("34.02"));
```

### Access Modifiers
- `public` — accessible everywhere
- `private` — only within the same class
- `protected` — within package and subclasses

### Static vs Instance
```java
// Static — belongs to the class, not an object
public static void main(String[] args) { }

// Instance — belongs to an object
public String getId() { return this.id; }
```

### Common Types
```java
String name = "Kingsley";
int year = 2026;
long bigNumber = 100000000L;
double price = 34.02;
BigDecimal precise = new BigDecimal("34.02"); // Use for money, never double
boolean active = true;
LocalDateTime now = LocalDateTime.now();
```

### Exception Handling
```java
try {
    // risky operation
    transactionRepository.save(transaction);
} catch (SQLIntegrityConstraintViolationException e) {
    // handle duplicate ID — regenerate
} catch (SQLException e) {
    // handle other DB errors
} finally {
    // always runs
}
```

---


---

## 18. Static Initializer Blocks

A `static { }` block runs **once, when the class is first loaded by the JVM** — before any object is created or any static method is called. It's used to set up shared state that needs to happen exactly once.

In this project, both `DatabaseConfig` and `RabbitMQConfig` use it to establish a single shared connection:

```java
public class DatabaseConfig {
    private static HikariDataSource dataSource;  // shared across all threads

    static {
        // runs once at class load time
        Properties props = new Properties();
        // ... load config ...
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(props.getProperty("db.url"));
        // ...
        dataSource = new HikariDataSource(config);  // one pool for the whole app
    }

    public static Connection getConnection() throws SQLException {
        return dataSource.getConnection();  // borrows from the pool
    }
}
```

Why not do this in a constructor? Because you'd create a new connection pool every time you write `new DatabaseConfig()`. The static block ensures exactly one pool exists, no matter how many times the class is referenced.

If the static block throws an unchecked exception, the class fails to load and the JVM throws `ExceptionInInitializerError` — your app crashes immediately on startup rather than failing silently later.

---

## 19. Try-With-Resources

Java requires that external resources (file handles, DB connections, network channels) be **explicitly closed** after use. If you forget, you leak memory, file descriptors, or DB connections until the process dies.

Try-with-resources automates this. Any object that implements `AutoCloseable` (which has a single `close()` method) can be declared in the `try (...)` header:

```java
// Without try-with-resources — easy to forget the close, or miss it on exception
Connection conn = DatabaseConfig.getConnection();
PreparedStatement stmt = conn.prepareStatement(sql);
try {
    stmt.executeUpdate();
} finally {
    stmt.close();  // must manually close both
    conn.close();
}

// With try-with-resources — close() is called automatically, even if an exception is thrown
try (Connection conn = DatabaseConfig.getConnection();
     PreparedStatement stmt = conn.prepareStatement(sql)) {
    stmt.executeUpdate();
}
// conn and stmt are closed here, no matter what
```

Multiple resources can be declared in one `try (...)`, separated by semicolons. They are closed in **reverse order** of declaration (stmt first, then conn — important because closing a connection before its statement would cause issues).

In this project it's used everywhere: `FileProducer` (Channel + BufferedReader), `TransactionRepository` (Connection + PreparedStatement), `LogRepository`, and both config classes (InputStream).

---

## 20. Text Blocks (Multi-line Strings)

Introduced in Java 15, text blocks let you write multi-line strings with triple quotes (`"""`). Before this, SQL had to be concatenated across many lines with `+` and explicit newlines — error-prone and hard to read.

```java
// Old way — fragile, easy to forget a space or newline
String sql = "INSERT INTO transactions (" +
             "    id, payment_type_id, amount" +
             ") VALUES (?, ?, ?)";

// Text block — the SQL looks exactly like SQL
String sql = """
        INSERT INTO transactions (
            id, payment_type_id, amount
        ) VALUES (?, ?, ?)
        """;
```

The leading whitespace common to all lines is automatically stripped (based on the closing `"""`'s indentation), so your SQL isn't padded with spaces. You can still use `?` placeholders normally — text blocks are just a string literal, nothing special at runtime.

Used in `TransactionRepository` and `LogRepository` for all SQL statements.

---

## 21. Functional Interfaces and Callbacks

A **functional interface** is any interface that has exactly one abstract method. Java allows you to replace it with a lambda anywhere that interface is expected.

`DeliverCallback` from the RabbitMQ library is one such interface:

```java
// What DeliverCallback looks like under the hood (simplified):
@FunctionalInterface
public interface DeliverCallback {
    void handle(String consumerTag, Delivery message) throws IOException;
}
```

Because it has one method, you can write a lambda instead of a full class:

```java
// Full anonymous class (old style):
DeliverCallback callback = new DeliverCallback() {
    @Override
    public void handle(String consumerTag, Delivery delivery) throws IOException {
        String line = new String(delivery.getBody());
        // process...
    }
};

// Lambda (modern style — same thing, less noise):
DeliverCallback callback = (consumerTag, delivery) -> {
    String line = new String(delivery.getBody());
    // process...
};
```

The lambda is **asynchronous** here — `channel.basicConsume(...)` returns immediately. The callback is stored and invoked later by RabbitMQ's internal thread whenever a message arrives. This is why the consumer thread never appears to "do" anything in a loop — it just registers the callback and stays alive.

Other functional interfaces you'll see constantly in Java:
- `Runnable` — `() -> { ... }` (used for threads)
- `Comparator<T>` — `(a, b) -> a.value - b.value`
- `Predicate<T>` — `x -> x > 0`

---

## 22. LocalDateTime ↔ JDBC Timestamp

Java's date/time API (`LocalDateTime`, `LocalDate`, `ZonedDateTime`) was introduced in Java 8. JDBC (the database connection API) predates this — it uses `java.sql.Timestamp`, `java.sql.Date`, etc. from the 1990s.

When you try to store a `LocalDateTime` in a database via a `PreparedStatement`, you can't call `stmt.setLocalDateTime(...)` — that method doesn't exist. You must convert:

```java
// LocalDateTime → java.sql.Timestamp (for PreparedStatement.setTimestamp)
stmt.setTimestamp(5, Timestamp.valueOf(t.getSourceDateCreated()));

// java.sql.Timestamp → LocalDateTime (when reading back from ResultSet)
LocalDateTime dt = resultSet.getTimestamp("source_date_created").toLocalDateTime();
```

`Timestamp.valueOf(localDateTime)` treats the `LocalDateTime` as a local time (no timezone). This is fine when your app and database are in the same timezone. If they're not, use `ZonedDateTime` and `Timestamp.from(zonedDateTime.toInstant())` instead.

---

## 23. Why BigDecimal for Money (Not double)

`double` and `float` use [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754) binary floating-point, which **cannot exactly represent most decimal fractions**. This is a fundamental property of how binary works:

```java
double a = 0.1;
double b = 0.2;
System.out.println(a + b);  // prints 0.30000000000000004 — not 0.3
```

This is not a Java bug. It's the same in every language using IEEE 754 (Python, JavaScript, C, etc.).

For financial calculations, even a sub-cent rounding error compounds across millions of transactions:

```java
// Scenario: charge 1000 customers GHS 34.10
double total = 0;
for (int i = 0; i < 1000; i++) total += 34.10;
System.out.println(total);  // 34100.000000000985 — 0.001 off

BigDecimal exactTotal = BigDecimal.ZERO;
for (int i = 0; i < 1000; i++) exactTotal = exactTotal.add(new BigDecimal("34.10"));
System.out.println(exactTotal);  // 34100.00 — exact
```

`BigDecimal` stores numbers in decimal (base 10) internally, so `0.1` is represented exactly. Always construct it from a **String**, not a double:

```java
new BigDecimal("34.10")  // correct — exact decimal
new BigDecimal(34.10)    // wrong — inherits the double's imprecision
```

In the database, use `DECIMAL(18, 2)` for money columns — MySQL's equivalent of BigDecimal.

---

