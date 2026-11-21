---
id: e2d052bf-0448-4f82-8d4a-e154c11166ef
---

# Build Tools & Project Structure

**Source:** merged from `record-id-generator-java/learning/02-build-tools-and-architecture.md` and `direct-debit-sandbox-java/learning/07-build-tools-and-project-structure.md`.

## Setting up the JDK
<!-- bite: bfbead70-5a1d-4b67-a8af-631593600d2f -->

```bash
java -version
update-alternatives --list java     # see installed versions
```

Multiple JDKs can coexist. Enterprise Java standardizes on an **LTS (Long Term Support)** release — Java 21 as of this writing. `JAVA_HOME` tells build tools and IDEs which JDK to use:

```bash
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

## Maven vs Gradle
<!-- bite: ba10b98c-03d2-4965-90fa-fbee7ada52f9 -->

Both automate dependency resolution, compilation, testing, and packaging into a runnable `.jar`. They differ in philosophy:

| | Maven | Gradle |
|---|---|---|
| Config file | `pom.xml` (XML) | `build.gradle.kts` (Kotlin DSL) or Groovy |
| Lifecycle | Fixed: validate → compile → test → package → install → deploy | Flexible — real code, loops/conditions allowed |
| Builds | Full rebuild every time | Incremental — only recompiles what changed |
| Caching | None built in | Build cache, even shareable across machines/CI |
| Predictability | Very high — every Maven project builds the same way | Lower — more room for custom behavior |

Maven's rigidity is its strength for large orgs standardizing on one build shape; Gradle's speed (incremental builds + cache) and flexibility (real Kotlin/Groovy) is why it's growing.

```kotlin
// build.gradle.kts
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")
}
```

```bash
./gradlew build          # compile + test + package
./gradlew bootRun         # start a Spring Boot app
./gradlew run             # run a plain application
./gradlew dependencies    # print the dependency tree
```

### The Gradle wrapper

`./gradlew` is not Gradle itself — it's the **wrapper**, three committed files (`gradlew`, `gradlew.bat`, `gradle/wrapper/*`) that download and pin the exact Gradle version a project needs on first run. This guarantees every developer and CI runner builds with an identical Gradle version with zero global install. Never assume Gradle is installed globally; always use the wrapper.

**Gotcha — Gradle/JDK version coupling**: Gradle hooks into internal JDK APIs to compile and manage bytecode, so every Gradle version has a maximum supported JDK version. Running an old Gradle wrapper against a brand-new JDK crashes the daemon with a cryptic version-string error. Fix by upgrading the wrapper (`./gradlew wrapper --gradle-version <newer>`) or pointing Gradle at an older, compatible JDK via `org.gradle.java.home` in `gradle.properties`.

### Bazel — the monorepo build

Beyond Maven and Gradle, **Bazel** (Google's open-sourced build tool, a roadmap.sh node) targets a different problem: very large, **polyglot monorepos**. Its selling points are *hermetic, reproducible* builds (every input is declared, so a build is bit-for-bit identical anywhere) and aggressive **remote caching + remote execution** that scales across a whole engineering org. The cost is steep: `BUILD` files must declare fine-grained dependencies explicitly, and the Java ecosystem's Maven/Gradle conventions don't map onto it cleanly. Reach for Bazel when you have a huge multi-language codebase and build times/reproducibility are an org-wide bottleneck — not for a single-service app, where Maven or Gradle is the right tool.

| | Maven | Gradle | Bazel |
|---|---|---|---|
| Sweet spot | conventional single projects | most projects, fast iteration | huge polyglot monorepos |
| Config | XML | Kotlin/Groovy DSL | Starlark `BUILD` files |
| Reproducibility | good | good | hermetic (strongest) |
| Learning curve | low | medium | high |

## What to commit, what to ignore
<!-- bite: aa145531-f03a-4763-bc72-289030cf9b9a -->

Commit: `build.gradle.kts`, `settings.gradle.kts`, `gradlew`/`gradlew.bat`, `gradle/wrapper/*`, `src/`.
Ignore: `.gradle/` (cache — machine-specific and huge), `build/` (compiled output — Git is for source, not artifacts), any leftover `.mvn/`/`target/` from a prior Maven setup.

## Project structure — three approaches
<!-- bite: 5a7358fc-b07d-49e8-90cd-81638d2dc556 -->

### Package by technical role (simplest, breaks down at scale)

```
com.itc/
├── config/       # DB, RabbitMQ setup
├── model/        # data classes
├── repository/   # database ops
├── service/      # business logic
```

Fine up to ~5 domain concepts. Past that you get 30 files in `model/`, 30 in `repository/`, with no signal of which belong together.

### Package by feature (what experienced teams prefer)

```
com.itc.direct_debit_sandbox/
├── subscriptions/    # everything subscription-related: controller, service, DTOs, models
├── transactions/
├── provision/
```

Rule: **things that change together should live together.** Understanding "how do subscriptions work" means opening one folder instead of jumping across three. Adding a feature touches one folder instead of three.

### Hexagonal / Ports and Adapters (for real scale)

```
com.itc/
├── domain/            # pure business logic, zero framework imports
│   ├── model/
│   ├── port/          # interfaces the domain depends on — "I need something that saves transactions"
│   └── service/
├── application/        # orchestrates domain — use cases (producer/consumer, request handling)
└── infrastructure/     # implements the ports — talks to MySQL, RabbitMQ, etc.
```

The rule: **domain never imports infrastructure.** `IdGeneratorService` has no idea MySQL exists; `FileConsumer` depends on the `TransactionStore` interface, not `TransactionRepository` directly. Swapping MySQL for Postgres means writing a new adapter — nothing in `domain/` or `application/` changes. The "ports" are the interfaces in `domain/port/`; the "adapters" are the `infrastructure/` implementations.

| | Package-by-role | Package-by-feature | Hexagonal |
|---|---|---|---|
| Good up to | ~5 concepts | Any size, single team | Any size, needs discipline |
| Swapping a dependency (e.g. DB) touches | Whole `repository/` | The one feature folder | Only `infrastructure/` |
| Can test business logic without a DB | Hard to mock | Depends | Yes — domain has zero DB dependency |

## Config files and secrets
<!-- bite: 9e4cd811-c24d-4cd7-9aec-c9ec7e5a9e7e -->

```properties
# application.properties — safe to commit
db.url=jdbc:mysql://localhost:3306/itc_db
rabbitmq.host=localhost

# application-local.properties — GITIGNORED
db.user=itc
db.password=itc
```

Never hardcode delays, URLs, or secrets in Java source — put them in properties files so they change without a recompile. Spring loads environment-specific overrides (`application-dev.properties`, etc.) based on `spring.profiles.active`.

## The `.http` request file format
<!-- bite: a3ab3594-5b18-43fa-9677-56b5ea646fd9 -->

IntelliJ and VS Code's REST Client extension both support `.http` files natively — versioned test requests that live in the repo instead of a separate Postman export:

```
@baseUrl = http://localhost:8080

### Subscribe
POST {{baseUrl}}/subscription/subscribe
Content-Type: application/json

{ "merchantId": "MERCH_12345" }
```

`###` separates requests; the blank line between headers and body is required.

## Gotcha — the Spring Security starter locks everything down
<!-- bite: 47897fab-7c0a-4980-bb8c-ac8c0640bc01 -->

Spring Boot configures itself based on what's on the classpath. Adding `spring-boot-starter-security` with zero extra code instantly puts HTTP Basic Auth on **every endpoint** and prints a random generated password to the console at startup. If the app has its own custom header-based auth, this dependency is not needed — remove it rather than fight it.

## Related
<!-- bite: e880fa3d-ffd1-4814-b78b-dbedc2522f49 -->
- [[languages/01-java/01-language/01-fundamentals|Fundamentals]]
- [[backend/frameworks/java/01-spring-boot|Spring Boot & Scheduling]]
- [[languages/01-java/06-applied-systems/04-docker-for-java-apps|Docker for Java Apps]]
- [[concepts/02-design-patterns/index|design patterns]] — Ports and Adapters is one of many
