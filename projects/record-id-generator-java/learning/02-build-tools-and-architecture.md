# Java Zero to Hero — Record ID Generator

A complete guide built from real experience: processing a 1.46GB CSV, generating unique 12-digit IDs, pushing records through RabbitMQ, and persisting to MySQL — all in Java.

---

# Record ID Generator — Build Tools, Project Structure & Architecture

Split out from the original single-file `learning.md`. Covers Java setup, Gradle vs Maven, the
project's layered/hexagonal architecture, the full pipeline diagram, and a running summary of
changes made across the project. See also `01-java-fundamentals.md` and the other domain files
in this folder.

---

## 2. Setting Up Java

### Check your Java version
```bash
java -version
```

Multiple versions can coexist on the same machine. Enterprise Java uses **Java 21 (LTS)**. LTS = Long Term Support — stable, supported for years.

### Set JAVA_HOME
When multiple versions exist, tell your system which one to use:

```bash
# Find available versions
update-alternatives --list java

# Add to ~/.zshrc
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# Apply
source ~/.zshrc
```

`JAVA_HOME` is an environment variable that tells tools (Maven, Gradle, IDEs) where Java lives.

---

## 3. Build Tools — Maven vs Gradle

Java projects need a **build tool** to manage dependencies (external libraries), compile code, and run tests.

| | Maven | Gradle |
|---|---|---|
| Config file | `pom.xml` | `build.gradle` or `build.gradle.kts` |
| Language | XML | Groovy or Kotlin DSL |
| Default in enterprise | Yes | Growing fast |
| Android/Kotlin | No | Yes |

### Gradle with Kotlin DSL (what we used)

```bash
mkdir my-project && cd my-project
gradle init --type java-application --dsl kotlin
```

This generates:
- `app/src/main/java/` — your source code
- `app/src/test/java/` — your tests
- `build.gradle.kts` — dependency config
- `gradlew` — wrapper script (use this, not `gradle` directly)

### Adding dependencies

In `build.gradle.kts`:
```kotlin
dependencies {
    implementation("com.rabbitmq:amqp-client:5.21.0")
    implementation("com.mysql:mysql-connector-j:8.3.0")
    implementation("com.zaxxer:HikariCP:5.1.0")
    implementation("org.flywaydb:flyway-core:10.15.0")
    implementation("org.flywaydb:flyway-mysql:10.15.0")
    compileOnly("org.projectlombok:lombok:1.18.32")
    annotationProcessor("org.projectlombok:lombok:1.18.32")
    implementation("org.slf4j:slf4j-api:2.0.13")
    implementation("ch.qos.logback:logback-classic:1.5.6")
}
```

### Running your app
```bash
./gradlew run
./gradlew build
./gradlew test
```

---

## 4. Java Project Structure

```
record-id-generator/
├── app/src/main/java/com/itc/
│   ├── Main.java               # Entry point
│   ├── config/                 # DB, RabbitMQ, Flyway setup
│   ├── model/                  # Data classes (Transaction, Log)
│   ├── repository/             # Database operations
│   ├── service/                # Business logic (ID generation)
│   ├── producer/               # Reads file → pushes to queue
│   └── consumer/               # Reads queue → writes to DB
├── app/src/main/resources/
│   ├── application.properties  # Config
│   └── db/migration/           # SQL migration files
└── app/src/test/java/com/itc/ # Tests
```

**Package naming convention:** `com.companyname.projectname` — reverse domain notation, globally unique.

This structure works fine for a small project. It groups files by **technical role** (config, model, repository). Every real file in this project has a clear place.

### For Scale — Layered / Hexagonal Architecture

As a codebase grows, grouping by technical role breaks down. You end up with 30 files in `model/`, 30 in `repository/`, and no way to tell which ones belong to the same feature. The scalable approach is to group by **business domain** first, then by technical role inside that.

```
com.itc/
├── domain/                     # Pure business logic — zero framework imports
│   ├── model/                  #   Transaction, Log, and other core types
│   ├── port/                   #   Interfaces your domain depends on
│   │   ├── TransactionStore.java   #     "I need something that can save transactions"
│   │   └── IdGenerator.java        #     "I need something that generates IDs"
│   └── service/                #   Business rules (ID generation, validation)
│       └── IdGeneratorService.java
│
├── application/                # Orchestrates domain — knows about use cases
│   ├── producer/               #   File reading, publishing to queue
│   │   └── FileProducer.java
│   └── consumer/               #   Message processing, batch coordination
│       └── FileConsumer.java
│
├── infrastructure/             # Implements the domain's ports — talks to the outside world
│   ├── db/                     #   MySQL implementation of TransactionStore
│   │   ├── DatabaseConfig.java
│   │   ├── TransactionRepository.java   # implements TransactionStore
│   │   └── LogRepository.java
│   ├── messaging/              #   RabbitMQ wiring
│   │   └── RabbitMQConfig.java
│   └── migration/              #   Flyway
│       └── FlywayConfig.java
│
└── Main.java                   # Wires everything together and starts the app
```

The key rule: **domain never imports infrastructure**. `IdGeneratorService` has no idea MySQL exists. `FileConsumer` depends on the `TransactionStore` interface, not `TransactionRepository` directly. This means you can swap MySQL for PostgreSQL by writing a new `TransactionRepository` — nothing in `domain/` or `application/` changes.

This pattern is called **Hexagonal Architecture** (also known as Ports and Adapters). The "ports" are the interfaces in `domain/port/`. The "adapters" are the implementations in `infrastructure/`.

| | Small project (this one) | At scale |
|---|---|---|
| Grouped by | Technical role | Business domain + role |
| Fine up to | ~5 domain concepts | Any size |
| Changes to MySQL affect | Only `repository/` | Only `infrastructure/db/` |
| Can test domain without DB | No — hard to mock | Yes — domain has no DB dependency |

---


---

## 16. The Full Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Java Application                   │
│                                                      │
│  Thread 1 (Producer)      Thread 2 (Consumer)        │
│  ┌─────────────────┐      ┌──────────────────────┐   │
│  │  FileProducer   │      │   FileConsumer        │   │
│  │                 │      │                       │   │
│  │ Read CSV line   │      │ Receive message       │   │
│  │ Publish to      │      │ Parse CSV line        │   │
│  │ RabbitMQ        │      │ Generate 12-digit ID  │   │
│  └────────┬────────┘      │ Save to MySQL         │   │
│           │               │ Log errors to logs    │   │
└───────────┼───────────────┴──────────┬────────────┘
            │                          │
            ▼                          ▼
      ┌──────────┐              ┌──────────┐
      │ RabbitMQ │─────────────▶│  MySQL   │
      │  Queue   │              │ itc_db   │
      └──────────┘              └──────────┘
```

---

## 17. Key Takeaways

| Concept | What You Learned |
|---|---|
| Java setup | JAVA_HOME, multiple JDK versions, LTS versions |
| Gradle | Kotlin DSL, dependencies, `./gradlew run` |
| Project structure | Layered architecture: model → repository → service → producer/consumer |
| Lombok | `@Data` eliminates boilerplate |
| Properties | `application.properties` for config, `application-local.properties` for secrets |
| HikariCP | Connection pooling — never open a new DB connection per operation |
| Flyway | Schema migrations — versioned SQL, auto-applied on startup |
| Prepared statements | Always parameterize SQL — never concatenate |
| RabbitMQ | Decouples producers and consumers; durable queues survive restarts |
| Threads | `new Thread(() -> {}).start()` — run tasks concurrently |
| ID generation | `SecureRandom` + digit alphabet + DB unique constraint + retry |
| CSV at scale | `BufferedReader` line by line — never load the whole file into memory |
| Logging | SLF4J + Logback — levels: DEBUG, INFO, WARN, ERROR |
| Log table | Always have one for data pipelines — payload, stack trace, timestamp |
| Docker | Dev vs prod compose; multi-stage Dockerfile |
| Static initializer | `static { }` runs once at class load — used for shared connections |
| Try-with-resources | `try (Resource r = ...)` — auto-closes anything that implements `AutoCloseable` |
| Text blocks | `"""..."""` — multi-line strings without concatenation or escape clutter |
| Functional interfaces | Any interface with one method can be replaced with a lambda |
| LocalDateTime ↔ JDBC | `Timestamp.valueOf(localDateTime)` bridges Java 8 date types to JDBC |
| BigDecimal precision | IEEE 754 floating point cannot represent 0.1 exactly — never use double for money |
| Graceful shutdown | `thread.join()` waits for a thread to finish — missing it causes silent data loss |
| Streaming vs chunking | `BufferedReader` already streams — the real bottleneck is one INSERT per message |
| Batch inserts | `addBatch()` + `executeBatch()` — 50–100x faster than one row at a time |
| ID strategies | Timestamp+random hybrid, UUID v4/v7, Snowflake, ULID, hash-based — each fits different needs |
| Idempotent pipeline | SHA-256 `source_hash` as a secondary UNIQUE constraint — re-runs skip duplicates safely |
| Dead Letter Queue | `basicNack` failed messages instead of acking — lets you replay them after fixing the bug |
| Observability | Track messages/sec, batch latency, duplicate rate, queue depth — fly with instruments, not blind |
| PK design | Generated ID = surrogate key (row identity); `source_hash` = business key (deduplication) |

---


---

## 44. Summary of Changes — This Session

The table below is a condensed record of what changed, why, and what you would look for in the code.

| Change | File | Why | What to look for |
|---|---|---|---|
| `source_hash` computation commented out | `FileConsumer.java` | Clean data — hash overhead not needed | `// transaction.setSourceHash(...)` |
| `source_hash` removed from all INSERTs | `TransactionRepository.java` | Matches above — no hash, no column | 24 params instead of 25 in `setParams` |
| INSERT IGNORE → plain INSERT | `TransactionRepository.java` | No dedup needed; surfacing real errors | `INSERT INTO` not `INSERT IGNORE INTO` |
| PK collision: parse error, fix one row, retry batch | `FileConsumer.java` | 1 collision shouldn't cost 9,999 rows | `parseDuplicateId()`, loop in `flushBatch()` |
| Shared `Connection` → per-consumer `Connection` | `RabbitMQConfig.java` | One reader thread was a bottleneck | `factory.newConnection()` inside `createChannel()` |
| `NUM_CONSUMERS` 6 → 10 | `Main.java` | More parallel inserts — 10 ran stably | `private static final int NUM_CONSUMERS = 10` |
| HikariCP pool 20 → 30 | `DatabaseConfig.java` | Cover 10 consumers with headroom | `config.setMaximumPoolSize(30)` |
| `batchLock` + `synchronized` | `FileConsumer.java` | Scheduler + callback on different threads | `private final Object batchLock` |
| `ScheduledExecutorService scheduler` | `FileConsumer.java` | Tail-end partial batches never flushed | `Executors.newSingleThreadScheduledExecutor()` |
| `basicQos(BATCH_SIZE)` → `basicQos(BATCH_SIZE * 2)` | `FileConsumer.java` | Eliminate idle gap between inserts | `channel.basicQos(BATCH_SIZE * 2)` |
| `Thread.currentThread().join()` in drain mode | `Main.java` | JVM was exiting before consumers finished | In the `else` branch of `if (args.length > 0)` |
| `declareQueues` moved to `Main.java` | `Main.java` / `FileConsumer.java` | 10 threads simultaneously declaring the same queue caused a silent deadlock | `try (Channel setup = ...) { declareQueues(setup); }` before consumer loop |
| `splitCsv()` replaces `split(",")` | `FileConsumer.java` | Quoted fields containing commas shifted all column indices | `splitCsv(line)` in `parseLine()` |
| Shovel plugin for DLQ replay | RabbitMQ container | Move failed messages back to main queue after fixing the bug | `docker exec <container> rabbitmq-plugins enable rabbitmq_shovel rabbitmq_shovel_management` |

---

*Built during SIWES @ ITC, Accra — June 2026*
