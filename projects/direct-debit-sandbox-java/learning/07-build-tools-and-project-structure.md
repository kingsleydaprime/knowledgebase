# Direct Debit Sandbox — Build Tools & Project Structure

Split out from the original single-file `learning.md`. Covers the `.http` request file format,
Maven vs Gradle, feature-based project folder structure, Gradle/Java version compatibility,
where dependencies live, what to commit to Git, and the hidden danger of the Spring Security
starter. See also `02-spring-boot-basics.md`.

---

## 37. The .http request file format

The [requests.http](requests.http) file is an **HTTP client script** supported natively by IntelliJ IDEA and by the REST Client extension in VS Code.

**Variables** are declared at the top:
```
@baseUrl = http://localhost:8080
@merchantId = MERCH_12345
```

And used anywhere with `{{variableName}}`:
```
POST {{baseUrl}}/subscription/subscribe
```

**A single request** looks like this:
```
POST {{baseUrl}}/provision
Content-Type: application/json
x-transflowId: {{transflowId}}
x-key: {{apiKey}}

{
  "merchantId": "{{merchantId}}"
}
```

The blank line between headers and body is **required** — it tells the parser "headers are done, body starts here."

**Requests are separated** by `###`. Everything between two `###` lines is one request.

```
### First request
GET {{baseUrl}}/health

### Second request
POST {{baseUrl}}/provision
...
```

The `###` line can also include a description that shows up as the request name in the IDE.

Why use `.http` files instead of Postman? They live **inside the repository** — anyone who clones the project gets the test requests immediately, with no import/export steps.

---


---

## 39. Build tools: Maven vs Gradle

A **build tool** automates the repetitive tasks every Java project needs:
- Downloading dependencies (libraries your code uses)
- Compiling your source files
- Running tests
- Packaging everything into a runnable `.jar` file

Without a build tool, you would have to do all of that by hand for every change. Both Maven and Gradle solve this problem — they just approach it differently.

### Maven (what this project started with)

Maven uses an XML file called `pom.xml` ("Project Object Model"). It looks like this:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

Maven has a strict, rigid lifecycle: `validate → compile → test → package → install → deploy`. Every project follows the same steps in the same order. This predictability is Maven's biggest strength — experienced Java developers know exactly how any Maven project builds.

The downside: it is verbose, XML is unpleasant to write, and you cannot easily customise the build without writing plugins.

### Gradle (what this project now uses)

Gradle uses either a Groovy DSL or a **Kotlin DSL** (`build.gradle.kts`). Kotlin is a modern language that your IDE understands — you get autocomplete, type checking, and error highlighting:

```kotlin
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")
}
```

Gradle's three core advantages over Maven:

**1. Incremental builds** — Gradle tracks which files changed. If you change one file, it only recompiles files that depend on it. Maven recompiles everything. On large projects, this can mean seconds vs minutes.

**2. Build cache** — Gradle can cache build outputs and reuse them even across machines (with a remote cache). If your CI server already built a module, developers can download the cached output instead of rebuilding from scratch.

**3. Flexibility** — Gradle's build scripts are real code. You can write loops, conditions, and functions. Maven forces you to use predefined lifecycle phases and XML plugins for everything custom.

### The Gradle wrapper

When you run `./gradlew build`, you are not running Gradle directly — you are running the **Gradle wrapper**. The wrapper is three files committed to the repository:

```
gradlew                          ← shell script (Unix)
gradlew.bat                      ← batch script (Windows)
gradle/wrapper/gradle-wrapper.jar        ← small bootstrap JAR
gradle/wrapper/gradle-wrapper.properties ← points to the Gradle version to download
```

The first time anyone runs `./gradlew`, it reads the `.properties` file, downloads exactly the right version of Gradle, caches it in `~/.gradle/wrapper/dists/`, and uses it. This means **every developer and every CI server automatically uses the same Gradle version** without needing to install anything.

This is the right approach. Never assume Gradle is installed globally.

### Key Gradle commands

```bash
./gradlew build            # compile + test + package
./gradlew bootRun          # start the Spring Boot app
./gradlew test             # run tests only
./gradlew dependencies     # print the full dependency tree
./gradlew clean            # delete build output
./gradlew tasks            # list all available tasks
```

### What `build.gradle.kts` means

The `.kts` extension means **Kotlin Script**. It is Kotlin, but executed as a script by Gradle rather than compiled into a standalone program. The standard extension without `.kts` uses Groovy. Kotlin is preferred in new projects because it has better IDE support.

---

## 40. Project folder structure explained

When you open this project, the folders can look overwhelming. Here is what each one is for and why it is organised that way.

### The standard Maven/Gradle Java layout

```
project-root/
├── build.gradle.kts         ← Gradle build config (dependencies, plugins, Java version)
├── settings.gradle.kts      ← Gradle project name
├── gradlew / gradlew.bat    ← Gradle wrapper scripts
├── gradle/wrapper/          ← Gradle wrapper JAR and properties
├── src/
│   ├── main/
│   │   ├── java/            ← All your application source code
│   │   └── resources/       ← Config files (application.properties, etc.)
│   └── test/
│       ├── java/            ← Test source code
│       └── resources/       ← Test config
└── build/                   ← Generated output (compiled classes, .jar). Never commit this.
```

This layout is a **convention**. Maven and Gradle both expect `src/main/java` for source and `src/main/resources` for config. If you follow the convention, the tools need zero extra configuration to find your files.

### Inside `src/main/java/com/itc/direct_debit_sandbox/`

The package path (`com.itc.direct_debit_sandbox`) mirrors the directory path. Inside that root, the code is split by **feature**:

```
direct_debit_sandbox/
├── callbacks/           ← CallbackService: fires HTTP callbacks to merchant webhooks
├── config/              ← App-wide config: thread pool, RestTemplate, SandboxConfig
├── provision/           ← /provision endpoint: merchant registration
├── scenarios/           ← ScenarioEngine: maps account suffixes to outcomes
├── store/               ← In-memory data: all the records and the store interface
├── subscriptions/       ← /subscription/* endpoints: the core domain
└── transactions/        ← /transaction/* endpoints: status checks
```

This is called **feature-based packaging** (also called "package by feature"). The alternative is **layer-based packaging**:

```
controllers/   ← all controllers in one folder
services/      ← all services in one folder
repositories/  ← all repositories in one folder
```

Layer-based is what most tutorials show. Feature-based is what experienced engineers prefer. Here is why:

| Scenario | Layer-based | Feature-based |
|----------|-------------|---------------|
| You want to understand how subscriptions work | Jump between 3 folders | Everything is in `subscriptions/` |
| You want to add a new endpoint | Touch 3 separate folders | Add to one folder |
| A junior asks "where does this all live?" | "spread across the whole project" | "it's all in `subscriptions/`" |

The rule: **things that change together should live together**. `SubscriptionController`, `SubscriptionService`, `SubscriptionRecord`, and the DTOs all change when subscription behaviour changes — so they belong in one folder.

### The `store/` folder as a special case

`store/` is shared infrastructure, not a feature. It holds:
- `Store.java` — the interface (the contract)
- `InMemoryStore.java` — the implementation
- `SubscriptionRecord.java`, `TransactionRecord.java`, etc. — data models

In a real project with a database, `store/` would contain JPA repositories and entities. The feature packages (`subscriptions/`, `transactions/`) would call those repositories. The separation keeps features independent of each other — `subscriptions/` does not import from `transactions/` and vice versa.

### What to put in `resources/`

`src/main/resources/application.properties` is where Spring Boot looks for configuration:

```properties
sandbox.callback-delay-preapproval=2000
sandbox.callback-delay-transaction=7000
```

You can also have `application-dev.properties`, `application-prod.properties` for environment-specific overrides. Spring loads the right one based on the active profile (`spring.profiles.active=dev`).

Never hardcode values like delay times or URLs directly in Java code. Put them in `application.properties` so they can be changed without recompiling.


---

## 41. Gradle and Java Version Compatibility

Even though Java is designed to be backwards compatible, Gradle actually hooks deeply into Java's internal APIs to compile code, manage its daemon process, and read bytecode. 

Whenever a new major version of Java is released (like Java 25), it brings changes to the bytecode format and internal APIs. Because of this, **every specific version of Gradle has a maximum supported Java version**. 

If your project's Gradle wrapper (e.g., `8.14`) was released before a new Java version (like Java 25) was fully supported, starting the Gradle daemon with that newer Java version will cause an immediate crash (often showing a cryptic version string error like `25.0.2`). 

To fix this, you either:
1. Upgrade the Gradle wrapper to a newer version that supports the Java version you have installed (`./gradlew wrapper --gradle-version <newer-version>`).
2. Force Gradle to use an older, compatible Java version (like the Long-Term Support Java 21) by setting `org.gradle.java.home=/path/to/java-21` in your `gradle.properties`.

---

## 42. Where do installed packages live?

In Maven, your dependencies are listed in `pom.xml`. In Gradle, they live in the **`build.gradle.kts`** file inside the `dependencies { ... }` block.
It looks like this:
```kotlin
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
}
```
Whenever you add a new line here, Gradle automatically downloads the package from Maven Central and makes it available to your code.

---

## 43. What to commit to Git (and what to ignore)

When working with Java build tools, a lot of temporary files are generated locally. You must **never commit these to Git** because they bloat the repository and cause conflicts.

**Files you SHOULD commit:**
- `build.gradle.kts` and `settings.gradle.kts` (your build instructions)
- `gradle.properties` (local project configuration)
- `gradlew` and `gradlew.bat` (wrapper scripts so others can run gradle without installing it)
- `gradle/wrapper/gradle-wrapper.jar` and `gradle-wrapper.properties`
- `src/` (all your actual code)

**Files you MUST IGNORE (add to `.gitignore`):**
- `.gradle/` — This is a hidden folder where Gradle caches downloaded dependencies, build outputs, and daemon state. It is massive and specific to your computer.
- `build/` — The compiled output (e.g., your `.class` and `.jar` files). Git is for source code, not compiled output.
- `.mvn/` and `target/` — If you switched from Maven to Gradle, these are leftovers.

If you accidentally commit `.gradle/`, you can un-track it without deleting it from your computer by running:
`git rm -r --cached .gradle`

---

## 44. The hidden danger of Spring Security dependency

Spring Boot embraces "convention over configuration," which means it automatically configures things based on what dependencies are on your classpath.

If you add:
```kotlin
implementation("org.springframework.boot:spring-boot-starter-security")
```
Spring Boot assumes you want a secure application. Without any extra code, it instantly locks down **every single endpoint** behind HTTP Basic Authentication. It even generates a random password and prints it to the console when you start the app: `Using generated security password: d9f15...`

If your API uses its own custom authentication (like checking `x-transflowId` and `x-key` headers), you don't need this dependency. Simply removing it from `build.gradle.kts` disables the automatic Basic Auth lockdown.

---

