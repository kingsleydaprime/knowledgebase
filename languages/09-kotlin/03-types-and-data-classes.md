# Types, Data Classes and Sealed Hierarchies

**[Intermediate]** — modelling data, and the feature that makes exhaustive state handling possible.

## `data class`

```kotlin
data class User(val id: String, val name: String, val age: Int)
```

Generates `equals`, `hashCode`, `toString`, `copy` and `componentN`. **Only properties in the primary constructor count** — one declared in the body is excluded from `equals`, which surprises people.

```kotlin
val older = user.copy(age = 37)         // immutable update — the idiom
val (id, name) = user                   // destructuring
```

**`copy` with named arguments is the pattern for state updates**, and it's what makes immutable state ergonomic enough to actually use.

## `sealed` — the important one

A sealed class or interface has a **known, closed set of subtypes**:

```kotlin
sealed interface UiState {
    data object Loading : UiState
    data class Success(val items: List<Item>) : UiState
    data class Error(val message: String, val retryable: Boolean) : UiState
}
```

```kotlin
val text = when (state) {                    // no `else` needed
    UiState.Loading   -> "Loading…"
    is UiState.Success -> "${state.items.size} items"   // smart cast
    is UiState.Error   -> state.message
}
```

**Exhaustiveness is the point.** Add a case to the sealed interface and **every `when` that doesn't handle it fails to compile.** The compiler hands you the list of places to update.

> **Avoid `else` in a `when` over your own sealed type.** It silences exactly the error you want.

**`sealed interface` over `sealed class`** where you can — it allows multiple inheritance and has no constructor.

**`data object`** for cases carrying no data — it gets a sensible `toString` and a single instance.

**This is the single highest-value pattern in Kotlin application code** → [[mobile/05-state-and-architecture|state modelling]].

## `object` and companions

```kotlin
object Config { val apiUrl = "..." }          // singleton, thread-safe, lazy

class User {
    companion object {
        fun fromJson(s: String): User = ...    // Kotlin's "static"
    }
}
```

**There's no `static`.** `companion object` is the replacement, and it's a real object — so it can implement interfaces, which `static` can't.

## `value class` — a wrapper with no cost

```kotlin
@JvmInline
value class UserId(val value: String)
```

**At runtime it's just a `String`** — no allocation, no boxing. At compile time it's a distinct type:

```kotlin
fun load(id: UserId) { }
load(orderId)     // ❌ compile error, even though both wrap String
```

**This is how you stop passing the wrong ID**, which is a real bug class in any codebase with several string identifiers. **Cheap to adopt, and it catches things.**

## Enums vs sealed

```kotlin
enum class Status { ACTIVE, SUSPENDED, CLOSED }        // fixed set, NO per-case data
```

**Use an enum when the cases carry no data** and you want `values()`, `valueOf` and serialisation. **Use sealed when cases carry different data.** Both are exhaustive in `when`.

**The same mobile caution as Swift:** a strict enum deserialised from a server **breaks when the server adds a value**, and old app versions live for years. **Add an `UNKNOWN` case and map to it** → [[mobile/08-networking-on-mobile|API compatibility]].

## Generics and variance

```kotlin
class Box<T>(val item: T)
fun <T : Comparable<T>> max(a: T, b: T): T = if (a > b) a else b

interface Producer<out T> { fun get(): T }      // covariant — produces T
interface Consumer<in T> { fun accept(t: T) }   // contravariant — consumes T
```

**`out` = "only produces", `in` = "only consumes"** — declaration-site variance, which is nicer than Java's wildcards at every use site. **`List<out T>` is why `List<String>` can be passed where `List<Any>` is expected**, and `MutableList` can't.

**Reified type parameters** — the escape from JVM erasure:

```kotlin
inline fun <reified T> Gson.parse(json: String): T = fromJson(json, T::class.java)
val user: User = gson.parse(text)      // the type is known at runtime
```

**Only works on `inline` functions**, because the type is substituted at the call site.

## Delegation

```kotlin
class Repo(private val cache: Cache) : Cache by cache      // delegate the interface

var name: String by Delegates.observable("") { _, old, new -> log(old, new) }
val config: Config by lazy { load() }
```

**`by` implements an interface by forwarding to another object** — composition without writing forwarding methods, which is a real answer to "prefer composition over inheritance."

## Key insight

**Sealed hierarchies plus exhaustive `when` are Kotlin's best feature for application code**, because they move "did I handle every case" from a code-review question to a compile error. Combined with `data class` immutability and `value class` type safety, you can encode most of your domain's rules in types the compiler checks.

## Related
- [[languages/09-kotlin/02-null-safety|null safety]]
- [[languages/08-swift/05-enums-and-pattern-matching|Swift's enums]] — the direct equivalent
- [[mobile/05-state-and-architecture|state modelling]] — where sealed types pay off
