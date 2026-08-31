# Serialisation and Testing

**[Intermediate]** — kotlinx.serialization, and the testing stack.

## kotlinx.serialization

Compile-time generated, no reflection:

```kotlin
@Serializable
data class User(
    val id: String,
    @SerialName("display_name") val displayName: String,
    val tags: List<String> = emptyList(),      // default = optional in JSON
)

val user = Json.decodeFromString<User>(text)
val text = Json.encodeToString(user)
```

**Configure the parser once, deliberately:**

```kotlin
val json = Json {
    ignoreUnknownKeys = true        // ← ESSENTIAL. Without it, a new server field CRASHES old apps
    coerceInputValues = true        // null → default for non-null properties
    explicitNulls = false           // omit nulls when encoding
}
```

**`ignoreUnknownKeys = true` is not optional in a mobile app.** Old app versions live for years, and the default (throw on unknown keys) means **adding a field to your API breaks every installed client** → [[mobile/08-networking-on-mobile|API compatibility]].

**Polymorphic types** map cleanly onto sealed hierarchies:

```kotlin
@Serializable
sealed interface Event {
    @Serializable @SerialName("click") data class Click(val x: Int, val y: Int) : Event
    @Serializable @SerialName("scroll") data class Scroll(val offset: Int) : Event
}
```

**vs Gson and Moshi:** Gson uses reflection, doesn't respect Kotlin's null safety (**it will happily put `null` in a non-null property**, producing an NPE far from the cause), and doesn't understand default values. **Moshi with its Kotlin codegen is fine.** kotlinx.serialization is the Kotlin-native choice and the one to prefer for new code.

## Unknown enum values

Same trap as everywhere:

```kotlin
@Serializable
enum class Status {
    @SerialName("active") ACTIVE,
    @SerialName("closed") CLOSED,
    UNKNOWN;                                    // fallback
}

val json = Json { coerceInputValues = true }    // unknown → the default/UNKNOWN
```

## Testing

```kotlin
class UserRepositoryTest {
    private val api = FakeApi()
    private val repo = UserRepository(api)

    @Test
    fun `returns cached user without hitting the network`() = runTest {
        repo.get("1")
        repo.get("1")
        assertEquals(1, api.callCount)
    }
}
```

**Backtick test names** are idiomatic Kotlin and make failure output readable.

**`runTest`** (from `kotlinx-coroutines-test`) runs suspending code with a **virtual clock** — `delay(30_000)` completes instantly. **This is what makes testing coroutine code practical**; without it you're either sleeping or racing.

```kotlin
@Test fun `retries with backoff`() = runTest {
    repo.fetchWithRetry()
    advanceTimeBy(60_000)          // skip an hour of backoff instantly
    assertEquals(3, api.attempts)
}
```

**Testing Flow:**

```kotlin
@Test fun `emits loading then success`() = runTest {
    viewModel.state.test {                      // Turbine
        assertEquals(Loading, awaitItem())
        assertEquals(Success(items), awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

**Turbine is the standard library for this** — collecting a `Flow` in a test without it is awkward and flaky.

## The stack

| | |
|---|---|
| **JUnit 5** / **kotlin.test** | The runner |
| **Turbine** | Testing Flow |
| **kotlinx-coroutines-test** | `runTest`, virtual time |
| **MockK** | **Kotlin-aware mocking** — handles final classes, coroutines, objects |
| **Fakes** | **Often better than mocks** — a real in-memory implementation |
| **Kotest** | Property-based testing, if you want it |
| **Robolectric** | Android framework classes on the JVM, fast |

**Prefer fakes over mocks.** A `FakeUserRepository` backed by a `MutableMap` is more readable than five `every { … } returns …` lines, and it doesn't break when you refactor the interface. **Mock at boundaries you don't own; fake the ones you do.**

**MockK over Mockito** in Kotlin — Kotlin classes are final by default, and MockK handles that plus `suspend` functions natively.

## What to actually test

Same as [[mobile/05-state-and-architecture|the architecture note]]:

- **ViewModels heavily** — pure logic, fake repository, milliseconds
- **Repositories** — caching, merging, conflict handling
- **Serialisation** against real API payloads, including malformed ones
- **A few instrumented UI tests** for critical flows only

## Key insight

**`runTest`'s virtual clock is what makes coroutine-heavy code genuinely testable** — retries, timeouts and polling become instant and deterministic rather than slow and flaky. Combined with fakes over mocks, the valuable tests (view-model logic) become cheap enough that you'll actually write them.

## Related
- [[languages/09-kotlin/05-coroutines-and-flow|coroutines and Flow]]
- [[mobile/frameworks/android/README|Android]] — Robolectric and instrumented tests
- [[languages/09-kotlin/03-types-and-data-classes|sealed types]] — polymorphic serialisation
