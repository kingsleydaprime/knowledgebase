# Why Kotlin, and the Toolchain

**[Beginner]** — what Kotlin is for, and what transfers from Java.

## What Kotlin is

**A JVM language designed to fix Java's ergonomics without abandoning its ecosystem.** JetBrains built it, Google made it Android's official language in 2017 and Kotlin-first in 2019.

**Where it's used:**
- **Android** — this is the main answer. New Android is essentially all Kotlin
- **Server-side** — Ktor, Spring Boot with Kotlin. Real and growing
- **Kotlin Multiplatform** — shared logic across iOS, Android, web, desktop → [[mobile/14-native-vs-cross-platform|KMP]]

**The design goal:** concise, null-safe, and **100% interoperable with Java.** You can call Java from Kotlin and Kotlin from Java, in the same file tree, which is why adoption could be incremental.

## What transfers from Java

**A great deal.** The JVM, the memory model, garbage collection, the collections framework, the entire library ecosystem, and most of the tooling → [[languages/01-java/README|the Java course]].

**What Kotlin changes is the language surface**, not the platform:

| Java | Kotlin |
|---|---|
| `null` everywhere | **Nullability in the type system** |
| Getters, setters, boilerplate | Properties, `data class` |
| Checked exceptions | None |
| Statements | **Expressions** — `if`, `when`, `try` all return values |
| Threads, `CompletableFuture` | **Coroutines** |
| Utility classes | **Extension functions** |

## The toolchain

```bash
./gradlew build
./gradlew test
kotlinc hello.kt -include-runtime -d hello.jar     # rarely used directly
```

**Gradle with the Kotlin DSL** (`build.gradle.kts`) is standard — and Gradle is the most-complained-about part of Android development. **Use version catalogs** (`libs.versions.toml`) to keep dependency declarations sane.

**IntelliJ IDEA / Android Studio** — both JetBrains, and the Kotlin support is excellent because they're the same company that makes the language. **The Java-to-Kotlin converter** (paste Java into a `.kt` file) is genuinely useful for learning.

## The syntax, briefly

```kotlin
fun greet(name: String, greeting: String = "Hello"): String = "$greeting, $name"

val x = 5              // immutable — PREFER THIS
var y = 5              // mutable

data class User(val id: String, val name: String)   // equals, hashCode, toString, copy — free

val result = when (status) {                        // an EXPRESSION
    Status.ACTIVE -> "running"
    Status.CLOSED -> "done"
}
```

**`val` over `var` is the strong convention** — and unlike Java's `final`, it's short enough that people actually use it.

**Everything is an expression**, which removes a lot of Java's ceremony: no ternaries needed, no assigning in every branch.

## `data class` — the feature you'll notice first

```kotlin
data class User(val id: String, val name: String, val age: Int)

val u = User("1", "Ada", 36)
val older = u.copy(age = 37)          // immutable update
val (id, name, _) = u                 // destructuring
```

**`equals`, `hashCode`, `toString`, `copy` and `componentN` are generated.** A Java equivalent is 40 lines and gets `equals`/`hashCode` wrong regularly. **Java records cover some of this now**, but `copy` with named arguments is still better.

## What Kotlin doesn't fix

Being honest:

- **It's still the JVM** — startup time, memory footprint, GC pauses → [[languages/01-java/README|JVM internals]]
- **Gradle is still Gradle**
- **Compile times are slower than Java's**, noticeably, especially with annotation processing (KSP is faster than kapt — use it)
- **Null safety stops at the Java boundary.** Platform types (`String!`) are Kotlin admitting it doesn't know, and they can still NPE

## Key insight

**Kotlin is Java's ecosystem with twenty years of language-design hindsight applied to the syntax.** Everything about the platform transfers; what changes is that null is in the type system, boilerplate is generated, everything is an expression, and concurrency is coroutines instead of threads. **If you know Java, you're productive in a week** — and the remaining month is learning coroutines properly.

## Related
- [[languages/09-kotlin/README|the Kotlin course]]
- [[languages/01-java/README|Java]] — the platform underneath, and it still applies
- [[mobile/frameworks/android/README|Android]] — the main destination
