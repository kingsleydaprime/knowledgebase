# Core APIs

**Source:** the date/time↔JDBC bridging and the quoted-CSV regex/parsing are real project code; the rest (NIO, networking, modules, annotations, cryptography beyond SHA-256) is **[reference]** — roadmap.sh Java nodes the projects didn't exercise, covered here as an orientation map rather than deep dives, with pointers to where the applied versions live.

## Date and Time (`java.time`)

The Java 8 `java.time` API replaced the broken, mutable, not-thread-safe legacy `Date`/`Calendar`. The core types are **immutable** and each models one concept precisely:

| Type | Represents |
|---|---|
| `LocalDate` | a date, no time, no zone (`2026-07-30`) |
| `LocalTime` | a time of day, no date |
| `LocalDateTime` | date + time, **no** zone |
| `ZonedDateTime` | date + time + zone — the one to use for absolute instants across zones |
| `Instant` | a point on the UTC timeline (epoch-based) |
| `Duration` / `Period` | an amount of time / calendar amount |

```java
LocalDate start = LocalDate.parse("2026-07-30");        // ISO-8601 by default
if (!end.isAfter(start)) throw new IllegalArgumentException("end must be after start");
```

**The JDBC bridge** is real project friction: `java.time` postdates JDBC's `java.sql.Timestamp` by two decades, so you convert at the boundary:

```java
stmt.setTimestamp(5, Timestamp.valueOf(localDateTime));               // write
LocalDateTime dt = resultSet.getTimestamp("col").toLocalDateTime();  // read
```

`Timestamp.valueOf` treats the value as local (no zone) — fine only when app and DB share a timezone; otherwise go through `Instant`/`ZonedDateTime`.

## Regular expressions

`Pattern` compiles a regex; `Matcher` runs it. Compile once and reuse for anything hot — compilation isn't free:

```java
private static final Pattern DUP_ID =
        Pattern.compile("Duplicate entry '(.+?)' for key 'PRIMARY'");   // compiled once

Matcher m = DUP_ID.matcher(sqlErrorMessage);
if (m.find()) String id = m.group(1);   // extract the colliding key from a MySQL error
```

That's real code from the pipeline's PK-collision handler. `String.split`, `matches`, and `replaceAll` all take regexes — which is exactly the trap in the CSV parser ([[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing]]): `split(",")` breaks on commas inside quoted fields, so a quote-aware parser is needed instead.

## IO and NIO

Two generations of file/stream APIs:

- **Classic IO** (`java.io`) — stream-based: `InputStream`/`OutputStream` (bytes), `Reader`/`Writer` (chars), wrapped in `BufferedReader`/`BufferedWriter` for efficiency. The pipeline streams a 1.5GB CSV line-by-line through a `BufferedReader` — flat memory regardless of file size (see [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing]]).
- **NIO.2** (`java.nio.file`) — the modern path/file API: `Path`, `Files.readAllLines`, `Files.lines` (a lazy `Stream<String>`), `Files.newBufferedReader`, `Files.deleteIfExists`. Prefer it for new code.

```java
try (BufferedReader r = Files.newBufferedReader(Path.of(filePath))) {
    r.lines().forEach(this::process);   // streaming — never loads the whole file
}
```

Always wrap resources in try-with-resources ([[languages/01-java/01-language/06-exceptions|Exceptions]]).

## Networking

`java.net` for sockets (`Socket`, `ServerSocket`) and the modern `java.net.http.HttpClient` (Java 11+) for HTTP:

```java
HttpClient client = HttpClient.newHttpClient();
HttpResponse<String> resp = client.send(
        HttpRequest.newBuilder(URI.create(url)).GET().build(),
        HttpResponse.BodyHandlers.ofString());
```

In a Spring app you'd typically use `RestTemplate`/`WebClient` instead ([[languages/01-java/05-web-and-api/03-api-design-and-documentation|API Design]]) — the payment sandbox fires callbacks with `RestTemplate`. Raw sockets matter mostly for low-level/latency-sensitive work, which is where the JVM-internals and concurrency material earns its keep.

## Annotations

Metadata attached to code, readable at compile time or runtime. You *consume* them everywhere (`@Override`, `@FunctionalInterface`, Spring's `@Service`, JPA's `@Entity`); occasionally you *define* one:

```java
@Retention(RetentionPolicy.RUNTIME)   // available via reflection at runtime
@Target(ElementType.METHOD)
public @interface RateLimited { int perSecond() default 10; }
```

`@Retention` controls whether the annotation survives to runtime (`RUNTIME`) or is discarded (`SOURCE`/`CLASS`); `@Target` restricts where it can be applied. Frameworks read runtime-retained annotations via **reflection** to wire behavior — how Spring finds `@Service` beans and springdoc builds the OpenAPI spec ([[languages/01-java/05-web-and-api/03-api-design-and-documentation|API Design]]). Reflection also underlies Lombok's compile-time processing and mocking libraries ([[languages/01-java/03-tooling/04-testing|Testing]]).

## Modules (JPMS)

The Java Platform Module System (Java 9+) adds a layer above packages: a `module-info.java` declares what a module `exports` and what it `requires`, giving strong encapsulation across jar boundaries:

```java
module com.itc.pipeline {
    requires java.sql;
    exports com.itc.pipeline.api;   // only this package is visible to other modules
}
```

Most application code (including both projects) runs fine on the unnamed classpath without modules; JPMS matters most for large libraries and for building slim custom runtimes with `jlink`. **[reference — not used in either project]**

## Cryptography

`java.security` / `javax.crypto`: `MessageDigest` (hashing), `Cipher` (encryption), `SecureRandom` (CSPRNG), `KeyGenerator`. The pipeline uses two of these for real:

```java
MessageDigest md = MessageDigest.getInstance("SHA-256");
String hash = HexFormat.of().formatHex(md.digest(input.getBytes(StandardCharsets.UTF_8)));   // idempotency key
SecureRandom random = new SecureRandom();   // unpredictable IDs — never plain Random for anything security-adjacent
```

SHA-256 as an idempotency fingerprint is in [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation]]; `SecureRandom` for ID generation is there too. For actual encryption, prefer vetted higher-level libraries over hand-assembling `Cipher` — the deeper cryptography material lives in [[cybersecurity/05-cryptography/README|cybersecurity/cryptography]].

## Related
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing & Performance]] — streaming IO and the CSV/regex parsing in anger
- [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation & Idempotency]] — `MessageDigest` and `SecureRandom` applied
- [[cybersecurity/05-cryptography/README|Cryptography (cybersecurity)]] — the crypto primitives in depth
