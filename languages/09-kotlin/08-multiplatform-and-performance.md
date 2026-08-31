# Multiplatform and Performance

**[Advanced]** — KMP, and where Kotlin's costs are.

## Kotlin Multiplatform

**Share logic, not UI.** Write networking, database, business rules and view models once in Kotlin; write the UI natively in SwiftUI and Compose.

```
     commonMain          ← shared Kotlin: models, repositories, view models
    /     |      \
androidMain iosMain jvmMain     ← platform-specific implementations
```

```kotlin
// commonMain
expect class Platform { val name: String }

// androidMain
actual class Platform { actual val name = "Android ${Build.VERSION.SDK_INT}" }

// iosMain
actual class Platform { actual val name = UIDevice.currentDevice.systemName() }
```

**`expect`/`actual` is the mechanism** — declare the shape in common code, implement per platform.

**The ecosystem:** Ktor (networking), SQLDelight or Room KMP (database), kotlinx.serialization, kotlinx.coroutines, Koin (DI). **All multiplatform, all mature enough.**

**Why it's the interesting middle option:** the UI stays genuinely native on both platforms, and **adoption is incremental** — add a shared module to an existing app rather than rewriting → [[mobile/14-native-vs-cross-platform|native vs cross-platform]].

**The friction, honestly:**
- **Swift interop is workable, not seamless.** Kotlin sealed classes, generics and `suspend` functions don't map cleanly to Swift. SKIE improves this significantly; the raw experience is clunkier
- **iOS developers must build Kotlin**, which means Gradle in their workflow
- **You still write two UIs**, so the saving is smaller than Flutter's
- **Tooling is younger** — debugging shared code from Xcode is improving but not effortless

**Compose Multiplatform** shares UI too, including on iOS. **Stable, and a different bet** — you're back to non-native widgets, so it's Flutter's trade with Kotlin's language.

## Performance

**It's the JVM, so [[languages/01-java/README|everything in the Java course]] applies** — GC, JIT, escape analysis, the memory model. Kotlin's own costs are on top of that.

**Where Kotlin adds overhead:**

**1. Boxing from generics.** JVM generics are erased, so `List<Int>` boxes every element into `Integer`. **Use `IntArray` rather than `List<Int>`** in hot numeric code.

**2. Lambdas that aren't inlined.** A non-inline higher-order function allocates a `Function` object per call. **Standard-library collection operations are `inline`**, so `map`/`filter` don't allocate the lambda — but your own higher-order functions do unless you mark them.

**3. Intermediate collections.** `list.map { }.filter { }.take(5)` allocates a full list per step. **`asSequence()` makes it lazy** and short-circuits — worth it on large collections, slower on small ones.

**4. Null checks.** The compiler inserts `Intrinsics.checkNotNull` at Java boundaries. Negligible individually, occasionally visible in a tight loop.

**5. `data class` `copy` in a loop** allocates each time.

**And the things that are free:**
- **Extension functions** — static method calls
- **`value class`** — erased to the underlying type
- **Coroutines** — a suspended coroutine is a state-machine object, far cheaper than a thread. **Thousands are fine**

## Compile time

**Kotlin compiles more slowly than Java**, noticeably on a large module.

- **Use KSP, not kapt.** KSP is substantially faster, and most annotation processors (Room, Hilt, Moshi) now support it
- **Modularise.** Gradle rebuilds only changed modules; one huge module rebuilds everything
- **The K2 compiler** (Kotlin 2.0) is meaningfully faster — be on it
- **Enable Gradle's configuration cache and build cache**

## Android-specific

- **R8** shrinks and optimises. **Test your release build** — R8 with reflection-based libraries can strip things you need. Keep rules matter
- **Coroutines are cheap; `Dispatchers.IO` threads are not.** It's a bounded pool; blocking it starves other work
- **Watch APK size** from dependency bloat → [[mobile/11-performance-and-battery|app size]]

## Key insight

**KMP's bet is that the UI is the part worth writing twice and the logic isn't** — which is the opposite of Flutter's bet, and defensible for exactly the apps where platform feel matters. On performance, Kotlin's own costs are small and predictable (boxing, non-inlined lambdas, intermediate collections); **the JVM underneath is still the dominant factor**, and profiling beats guessing about either.

## Related
- [[mobile/14-native-vs-cross-platform|native vs cross-platform]] — where KMP fits
- [[languages/01-java/README|Java]] — the JVM performance model
- [[languages/09-kotlin/05-coroutines-and-flow|coroutines]] — cheap concurrency
- [[foundations/computer-architecture/12-performance|performance method]]
