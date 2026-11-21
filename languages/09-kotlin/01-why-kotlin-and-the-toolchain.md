---
id: b4a314d6-1480-48eb-b472-32cd3082852b
---

# Why Kotlin, and the Toolchain

Kotlin is a programming language that runs wherever Java runs and is now Google's preferred language for building Android apps. Many of the Android apps on your phone are written in it. This lesson covers what Kotlin is, what it keeps from Java, and the tools you need to start.

## What Kotlin is
<!-- bite: fa1284b7-9814-4977-8cda-e0a5419aa261 -->

**A JVM language designed to fix Java's ergonomics without abandoning its ecosystem.** JetBrains built it, Google made it Android's official language in 2017 and Kotlin-first in 2019.

**Where it's used:**
- **Android** — this is the main answer. New Android is essentially all Kotlin
- **Server-side** — Ktor, Spring Boot with Kotlin. Real and growing
- **Kotlin Multiplatform** — shared logic across iOS, Android, web, desktop → [[mobile/14-native-vs-cross-platform|KMP]]

**The design goal:** concise, null-safe, and **100% interoperable with Java.** You can call Java from Kotlin and Kotlin from Java, in the same file tree, which is why adoption could be incremental.

## What transfers from Java
<!-- bite: 9514c152-ef84-4083-8509-8da2462a2886 -->

**A great deal.** The JVM, the memory model, garbage collection, the collections framework, the entire library ecosystem, and most of the tooling → [[languages/01-java/index|the Java course]].

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
<!-- bite: 0a1c3a8b-7786-4558-a2a5-bc5d166f9d77 -->

```bash
./gradlew build
./gradlew test
kotlinc hello.kt -include-runtime -d hello.jar     # rarely used directly
```

**Gradle with the Kotlin DSL** (`build.gradle.kts`) is standard — and Gradle is the most-complained-about part of Android development. **Use version catalogs** (`libs.versions.toml`) to keep dependency declarations sane.

**IntelliJ IDEA / Android Studio** — both JetBrains, and the Kotlin support is excellent because they're the same company that makes the language. **The Java-to-Kotlin converter** (paste Java into a `.kt` file) is genuinely useful for learning.

## The syntax, briefly
<!-- bite: 5f1a2e29-857e-4983-9f5b-e9ad0cb33408 -->

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
<!-- bite: dc5ae03f-46f9-4ea2-8897-edf81fd29c63 -->

```kotlin
data class User(val id: String, val name: String, val age: Int)

val u = User("1", "Ada", 36)
val older = u.copy(age = 37)          // immutable update
val (id, name, _) = u                 // destructuring
```

**`equals`, `hashCode`, `toString`, `copy` and `componentN` are generated.** A Java equivalent is 40 lines and gets `equals`/`hashCode` wrong regularly. **Java records cover some of this now**, but `copy` with named arguments is still better.

## What Kotlin doesn't fix
<!-- bite: 2a24afa2-25b5-4ebe-8d57-d43c8ec40c02 -->

Being honest:

- **It's still the JVM** — startup time, memory footprint, GC pauses → [[languages/01-java/index|JVM internals]]
- **Gradle is still Gradle**
- **Compile times are slower than Java's**, noticeably, especially with annotation processing (KSP is faster than kapt — use it)
- **Null safety stops at the Java boundary.** Platform types (`String!`) are Kotlin admitting it doesn't know, and they can still NPE

## Key insight
<!-- bite: 7be38628-a635-4a35-adca-c8a6aaf04752 -->

**Kotlin is Java's ecosystem with twenty years of language-design hindsight applied to the syntax.** Everything about the platform transfers; what changes is that null is in the type system, boilerplate is generated, everything is an expression, and concurrency is coroutines instead of threads. **If you know Java, you're productive in a week** — and the remaining month is learning coroutines properly.

## Related
<!-- bite: 11d6e58c-58ec-4cab-b656-6ead83a45331 -->
- [[languages/09-kotlin/index|the Kotlin course]]
- [[languages/01-java/index|Java]] — the platform underneath, and it still applies
- [[mobile/frameworks/android/index|Android]] — the main destination

## About this lesson
<!-- bite: fcfc9dff-e3aa-41fe-98f3-f687055500c7 -->

**Level:** Beginner. **Covers:** what Kotlin is for, and what transfers from Java.
