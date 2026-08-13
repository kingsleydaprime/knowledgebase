# record-id-generator-java — Java & Architecture

From [`../learning/01-java-fundamentals.md`](../learning/01-java-fundamentals.md),
[`02-build-tools-and-architecture.md`](../learning/02-build-tools-and-architecture.md),
[`03-lombok-and-configuration.md`](../learning/03-lombok-and-configuration.md),
[`08-csv-parsing-and-data-quality.md`](../learning/08-csv-parsing-and-data-quality.md).

---

### Q1. [Beginner] 🔥 Why `BigDecimal` for money and never `double`?

**Strong answer covers:** `double` is binary floating point, so decimal fractions like `0.1` have no
exact representation — `0.1 + 0.2 != 0.3`, and errors accumulate across millions of rows.
`BigDecimal` is arbitrary-precision decimal, so the arithmetic matches what an accountant expects.
Two follow-on details worth volunteering: construct from a **String** (`new BigDecimal("0.1")`), not
from a double, or you've already inherited the binary error; and use `compareTo` rather than
`equals` for comparison, because `equals` also compares scale, so `2.0` and `2.00` are unequal.

**Follow-up they may ask:** *"What's the alternative in a high-volume system?"* — store minor units
as a `long` (kobo, cents). Faster and exact, but you own the scaling discipline everywhere.

---

### Q2. [Intermediate] 🔥 `split(",")` on a CSV line — why is that a bug?

**Strong answer covers:** a quoted field can legally contain a comma: `"Lagos, Nigeria"` is one
field, and `split(",")` turns it into two, shifting every subsequent column by one. The failure is
nasty because it's **data-dependent** — most rows parse fine and the corrupted ones look like a
data-quality problem rather than a parser bug. Correct handling needs a parser that tracks whether
the cursor is inside a quoted field (and handles the escaped `""` inside quotes), which is why real
CSV parsing is a state machine, not a string split.

**The generalisable line:** delimiters that can appear inside values need a parser that knows about
quoting state. Same class of problem as "is this comma inside a JSON string?"

---

### Q3. [Intermediate] Why is streaming the CSV essential rather than reading it into a list?

**Strong answer covers:** 5.75M rows will not fit comfortably in memory as objects, and even if it
did, you'd pay the full memory cost before publishing a single message. Streaming with a
`BufferedReader` (or `Files.lines`) keeps memory flat and lets the producer start feeding the queue
immediately, which is what allows producer and consumer to overlap in time. Memory usage becomes a
function of batch size and prefetch, not of file size.

---

### Q4. [Beginner] 🔥 Explain try-with-resources and why it matters in this pipeline.

**Strong answer covers:** any `AutoCloseable` declared in the `try (...)` header is closed
automatically, in reverse order, even on exception — no `finally` block, no leaked handle on the
error path. In this pipeline that covers file readers, JDBC `Connection`s (returning them to the
Hikari pool, not actually closing them), `PreparedStatement`s and `ResultSet`s. The failure it
prevents is the classic one: an exception mid-loop leaks a pooled connection, and after N failures
the pool is exhausted and the app hangs waiting for a connection that will never come back.

**Detail that shows depth:** exceptions thrown by `close()` are added as *suppressed* exceptions
rather than replacing the original — so the real cause isn't hidden by a cleanup failure.

---

### Q5. [Intermediate] What are functional interfaces and where did callbacks show up here?

**Strong answer covers:** an interface with exactly one abstract method, which lets a lambda or
method reference stand in for an implementation (`Runnable`, `Consumer<T>`, `Function<T,R>`, or your
own). In this project the consumer's per-message handling is naturally a callback shape — the
RabbitMQ client hands you a delivery and you supply the behaviour. The value is that the message
loop, the ack policy, and the business logic stay separable.

---

### Q6. [Advanced] 🔥 You hit "local variables referenced from a lambda must be final or effectively final." What was going on, and how did you fix it?

**Strong answer covers:** a lambda captures values, not variables — so it needs the captured local
to never be reassigned, otherwise the lambda and the enclosing method could disagree about the
current value with no synchronisation. It bit while parsing MySQL's error message to find which
specific row in a failed batch collided, because that logic wanted a mutable accumulator inside a
lambda. Fixes: use a field or an array/`AtomicInteger` holder, restructure to a plain loop, or
assign to a new effectively-final local per iteration. The right choice here was restructuring
rather than smuggling mutability through a holder.

---

### Q7. [Advanced] 🔥 When a batch insert fails on a duplicate key, how do you find the *specific* offending row rather than discarding the whole batch?

**Strong answer covers:** the naive recovery is "the batch failed, retry it row by row" — correct
but slow, and at 500 rows per batch that's expensive when one row is at fault. Instead, parse the
MySQL error message, which names the duplicate key value, and use it to locate the exact row. Then
the batch can be re-run without that row.

**The design note worth adding:** the recovery path keeps **three parallel lists** rather than a
map, because the rows must stay index-aligned with the batch's staged parameters — a map loses
ordering and the correspondence between a staged statement and its source record.

**Honest caveat to volunteer:** parsing a database's error *text* is version-coupled and would break
on an upgrade or a locale change. It's a pragmatic choice for a controlled pipeline, not something
to ship into a library.

---

### Q8. [Beginner] Why Gradle with the Kotlin DSL, and what does the wrapper give you?

**Strong answer covers:** Gradle over Maven for a concise, programmable build; the Kotlin DSL for
type-safety and IDE completion in the build file itself, versus Groovy's stringly-typed dynamism.
The **wrapper** (`./gradlew`) pins the Gradle version in the repo, so every machine and CI runner
builds with the same version — the same reproducibility argument as pinning any other tool.

---

### Q9. [Intermediate] Walk me through the layering. Where does each responsibility live?

**Strong answer covers:** a straight pipeline decomposition — a producer that streams the file and
publishes, a consumer that batches and persists, a repository that owns SQL and JDBC, an ID
generator, and configuration read from a properties file. The rule to state: **each layer knows only
the one below it**, so the consumer never builds SQL and the repository never knows a message
broker exists. That's what makes it possible to swap RabbitMQ for something else, or test the
repository against a database with no broker running.

**Follow-up:** *"Where would hexagonal architecture change this?"* — you'd define ports (an
`RecordSink` interface) and adapters (JDBC, in-memory) so the core logic depends on interfaces, not
JDBC. Worth it at scale or with multiple sinks; overhead for a single-purpose loader. Name the
trade-off rather than declaring one universally better.

---

### Q10. [Intermediate] What does Lombok actually generate, and what's the risk of leaning on it?

**Strong answer covers:** `@Data` (getters/setters/`equals`/`hashCode`/`toString`), `@Builder`,
`@Slf4j` (a logger field), `@RequiredArgsConstructor`. It's annotation processing at compile time —
the bytecode has real methods, so there's no runtime cost. The risks worth naming: `@Data` on a
JPA/entity-ish class generates `equals`/`hashCode` over *all* fields, which is wrong for anything
with identity; it requires IDE plugin support, so tooling that doesn't understand it reports phantom
errors; and generated setters quietly make classes mutable when you may have wanted immutability.

---

### Q11. [Beginner] Why a properties file rather than hard-coded configuration?

**Strong answer covers:** the same code has to run against a local Docker MySQL and a real one, and
JDBC URL, credentials, batch size, and thread counts all change per environment. It also keeps
credentials out of source. The related detail from this project: the JDBC URL is where
`rewriteBatchedStatements=true` lives — so a *configuration* value, not a code change, is what
delivered the biggest single performance win. Worth saying out loud, because it's a good argument
for treating config as part of the design rather than an afterthought.

---

### Q12. [Intermediate] Static initializer blocks — where did you use one, and what's the danger?

**Strong answer covers:** a `static { }` block runs once at class-load time, useful for loading a
properties file or initialising a shared immutable structure. The danger: an exception thrown inside
becomes an `ExceptionInInitializerError`, and subsequent access to the class throws
`NoClassDefFoundError` with the *original* cause long gone from the stack trace — a genuinely
confusing failure. Class-loading order also isn't obvious, so anything with real dependencies is
better done explicitly at startup.
