# Kotlin

**Java's ecosystem with twenty years of language-design hindsight applied to the syntax.** Android's official language since 2017, Kotlin-first since 2019.

**8 notes, built Aug 2026** alongside [[mobile/README|the mobile track]]. `[reference]`.

> **The one idea:** Kotlin inverts Java's defaults — **final instead of open, non-null instead of nullable, properties instead of fields, expressions instead of statements, coroutines instead of threads.** Every inversion is a lesson from twenty years of Java, and the platform underneath is unchanged.

## Why this exists

[[languages/README|languages/README]] listed Kotlin as a track that "would slot in if notes got written." They hadn't been — despite Kotlin being **the** Android language, and Android being half of [[mobile/README|mobile]].

**Note this is deliberately shorter than the other language courses**, because [[languages/01-java/README|the Java course]] already covers the JVM, GC, the memory model and the collections framework — all of which apply unchanged. **This covers what Kotlin adds.**

## Reading order

**02 and 05 are the load-bearing ones.** Null safety is what Kotlin is known for; coroutines are what takes longest to learn properly.

1. [[languages/09-kotlin/01-why-kotlin-and-the-toolchain|why-kotlin-and-the-toolchain]] — **[Beginner]** — what transfers from Java (most of it), what changes, and Gradle
2. [[languages/09-kotlin/02-null-safety|null-safety]] — **[Beginner → Intermediate]** — nullability in the type system, the safe-call/Elvis/smart-cast toolkit, and **platform types, which is the hole**
3. [[languages/09-kotlin/03-types-and-data-classes|types-and-data-classes]] — **[Intermediate]** — `data class`, **sealed hierarchies and exhaustive `when` (the highest-value pattern here)**, `value class`, and variance
4. [[languages/09-kotlin/04-functions-and-idioms|functions-and-idioms]] — **[Intermediate]** — **extension functions**, the five scope functions demystified, `inline`, and the collection API
5. [[languages/09-kotlin/05-coroutines-and-flow|coroutines-and-flow]] — **[Advanced]** — **the most important note here.** Structured concurrency, dispatchers, cooperative cancellation, `StateFlow` vs `SharedFlow`
6. [[languages/09-kotlin/06-classes-objects-and-interop|classes-objects-and-interop]] — **[Intermediate]** — the object model, `by` delegation, and the `@Jvm*` annotations Java callers need
7. [[languages/09-kotlin/07-serialisation-and-testing|serialisation-and-testing]] — **[Intermediate]** — kotlinx.serialization (**and why `ignoreUnknownKeys` isn't optional**), `runTest`'s virtual clock, Turbine, and fakes over mocks
8. [[languages/09-kotlin/08-multiplatform-and-performance|multiplatform-and-performance]] — **[Advanced]** — KMP's bet, and where Kotlin's costs actually are

## If you only take three things

1. **Model state as a sealed hierarchy**, so the compiler forces you to handle every case ([[languages/09-kotlin/03-types-and-data-classes|03]]).
2. **Never swallow `CancellationException`** in a generic catch — it breaks structured concurrency ([[languages/09-kotlin/05-coroutines-and-flow|05]]).
3. **`ignoreUnknownKeys = true`**, or adding a field to your API crashes every installed app ([[languages/09-kotlin/07-serialisation-and-testing|07]]).

## Related
- [[languages/01-java/README|Java]] — the platform underneath, and it still applies
- [[mobile/frameworks/android/README|Android]] — the main destination
- [[mobile/README|mobile]] — the course this was written alongside
- [[languages/README|languages]] · [[languages/projects|projects]]
