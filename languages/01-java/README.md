# Java

**[Beginner → Advanced]** — the language, the JVM, and the backend ecosystem built on top of it. Part of the [[languages/README|languages]] course.

The reading order runs top to bottom through six themed sections: the **language** itself → how it **runs** (JVM + concurrency) → the **tooling** around it → **persistence** → **web/API** → **applied systems** built from real projects.

## Where the content comes from

Two threads run through this domain, and it's worth being honest about which is which:

- **Project-grounded** notes are distilled from two things actually built during SIWES @ IT Consortium: a Spring Boot payment sandbox (`direct-debit-sandbox-java`) and a high-throughput CSV→MySQL pipeline over RabbitMQ (`record-id-generator-java`). These carry a **Source** line and real code. The full project-embedded originals (with debugging narratives this domain trims) still live under [[projects/record-id-generator-java/learning/01-java-fundamentals|record-id-generator-java/learning/]] and [[projects/direct-debit-sandbox-java/learning/01-java-fundamentals|direct-debit-sandbox-java/learning/]].
- **Reference** notes fill the [roadmap.sh Java](https://roadmap.sh/java) topics the two projects never exercised (generics, the collections framework, GC internals, testing, ORM, virtual threads, …). These are marked **[reference — not yet exercised]** where honest, and tied back to project code wherever the link is genuine rather than forced. Reading about them is not the same as having reps — see the [[languages/01-java/02-jvm-and-concurrency/exercises/README|concurrency exercises]] for where that distinction bites.

## Sections

### [[languages/01-java/01-language/README|01 — Language]]
The language itself, beginner to fluent.
1. [[languages/01-java/01-language/01-fundamentals|Fundamentals]] — syntax, types, variables, operators, strings, arrays, control flow, packages, access modifiers, `static`/`final`, pass-by-value, `null`, `BigDecimal`
2. [[languages/01-java/01-language/02-oop|OOP]] — classes/objects, the four pillars, inheritance, interfaces vs abstract classes, overloading/overriding, static vs dynamic binding, nested classes, `equals`/`hashCode`
3. [[languages/01-java/01-language/03-generics|Generics]] — type parameters, bounded types, wildcards, type erasure
4. [[languages/01-java/01-language/04-collections|Collections]] — `List`/`Set`/`Map`/`Queue`/`Deque`, implementation tradeoffs + Big-O, `Iterator`, `Comparable`/`Comparator`
5. [[languages/01-java/01-language/05-functional-programming|Functional Programming]] — functional interfaces, lambdas, method references, the Stream API, higher-order functions, `Optional`
6. [[languages/01-java/01-language/06-exceptions|Exceptions]] — checked vs unchecked, the hierarchy, custom exceptions, try-with-resources
7. [[languages/01-java/01-language/07-modern-java|Modern Java]] — records, sealed classes, pattern matching, `var`, text blocks, switch expressions
8. [[languages/01-java/01-language/08-core-apis|Core APIs]] — date/time, regex, IO/NIO, files, networking, modules, annotations, cryptography

### [[languages/01-java/02-jvm-and-concurrency/README|02 — JVM & Concurrency]]
How Java actually runs — the section that matters most for a low-latency/systems target.
1. [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM Internals]] — class loading, bytecode, JIT, memory areas, garbage collection, tuning
2. [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] — threads, the memory model, `java.util.concurrent`, locks, atomics/CAS, shutdown
3. [[languages/01-java/02-jvm-and-concurrency/03-virtual-threads|Virtual Threads]] — Project Loom, structured concurrency
- [[languages/01-java/02-jvm-and-concurrency/exercises/README|Exercises]] — unsolved, runnable reps (bounded blocking queue, token-bucket rate limiter)

### [[languages/01-java/03-tooling/README|03 — Tooling]]
Building, wiring, testing, and observing.
1. [[languages/01-java/03-tooling/01-build-tools|Build Tools]] — Maven, Gradle, Bazel, the wrapper, project structure
2. [[languages/01-java/03-tooling/02-dependency-injection|Dependency Injection]] — IoC, DI styles, Spring's container
3. [[languages/01-java/03-tooling/03-lombok-and-builders|Lombok & Builders]] — `@Data`/`@Builder`, DTOs, the builder pattern
4. [[languages/01-java/03-tooling/04-testing|Testing]] — JUnit, Mockito, and the TestNG/Cucumber/REST Assured/JMeter landscape
5. [[languages/01-java/03-tooling/05-logging-and-observability|Logging & Observability]] — SLF4J, Logback, Log4j2, the log-table pattern, metrics

### [[languages/01-java/04-persistence/README|04 — Persistence]]
1. [[languages/01-java/04-persistence/01-jdbc-and-data-modeling|JDBC & Data Modeling]] — HikariCP, Flyway, SQL, primary-key design, normalization
2. [[languages/01-java/04-persistence/02-orm-jpa-hibernate|ORM: JPA & Hibernate]] — JPA, Hibernate, Spring Data JPA, Ebean

### 05 — Web & API → [[backend/frameworks/java/README|moved to backend/frameworks/java/]]
These three notes were **moved, not duplicated** — `languages/` teaches the language, `backend/frameworks/` teaches the frameworks built on it. [[languages/01-java/05-web-and-api/README|Signpost page]].
1. [[backend/frameworks/java/01-spring-boot|Spring Boot]] — DI, the controller/service layering, validation, `@Async`, `@Scheduled`
2. [[backend/frameworks/java/02-web-frameworks|Web Frameworks]] — the Spring/Quarkus/Javalin/Play landscape
3. [[backend/frameworks/java/03-api-design-and-documentation|API Design & Documentation]] — RestTemplate, config-resolution patterns, OpenAPI/springdoc

### [[languages/01-java/06-applied-systems/README|06 — Applied Systems]]
The project-grounded high-throughput work — the strongest "real engineering" signal in the domain.
1. [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ]] — queues, DLQs, backpressure, competing consumers
2. [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation & Idempotency]] — collision math, UUID/Snowflake/ULID, idempotent pipelines
3. [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing & Performance]] — streaming vs batching, JDBC batch inserts, bulk-load tuning
4. [[languages/01-java/06-applied-systems/04-docker-for-java-apps|Docker for Java Apps]] — multi-stage builds, dev compose, resource limits

## Related
- [[languages/README|languages course map]]
- [[backend/README|backend]] — the Node.js/Express/Nest equivalent
- [[foundations/dsa/README|DSA]] — language-agnostic algorithms behind [[languages/01-java/01-language/04-collections|collections]]
- [[concepts/03-design-patterns/README|design patterns]]
- [[devops/02-docker/README|Docker]]
