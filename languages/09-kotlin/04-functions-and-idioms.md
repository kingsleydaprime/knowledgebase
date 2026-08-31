# Functions and Idioms

**[Intermediate]** — extension functions, scope functions, and the shortcuts that define idiomatic Kotlin.

## Functions

```kotlin
fun greet(name: String, greeting: String = "Hello"): String = "$greeting, $name"

greet("Ada")                          // "Hello, Ada"
greet(name = "Ada", greeting = "Hi")  // named arguments, any order
```

**Default and named arguments remove the need for overloads and builders**, which is one of the biggest ergonomic wins over Java.

**Expression bodies** (`= ...`) for anything that's one expression — very common, and the return type can be inferred.

## Extension functions

Add methods to types you don't own:

```kotlin
fun String.isValidEmail(): Boolean = contains("@") && contains(".")
"a@b.com".isValidEmail()

fun <T> List<T>.second(): T = this[1]
```

**These are resolved statically** — compiled to a static method with the receiver as the first parameter. So:

- **No runtime cost**
- **No dynamic dispatch** — an extension is not overridden by a subclass. If a member function with the same signature exists, **the member wins**
- **They can't access private members**

**Extensions are everywhere in Kotlin** — most of the standard library's collection operations are extension functions, and Android's KTX libraries are almost entirely this. **It's the mechanism that lets Kotlin improve Java APIs without changing them.**

## The scope functions

Five small functions that cause more confusion than anything else in Kotlin. **The distinction is only two questions: what's the receiver called, and what does it return?**

| | Receiver | Returns | Use for |
|---|---|---|---|
| `let` | `it` | lambda result | **Null checks**, transforming |
| `run` | `this` | lambda result | Compute with an object |
| `apply` | `this` | **the object** | **Configuring** an object |
| `also` | `it` | **the object** | **Side effects** in a chain |
| `with` | `this` | lambda result | Multiple calls on one object |

```kotlin
// let — the most common: do this only if not null
user?.let { sendEmail(it.email) }

// apply — configure and return
val intent = Intent().apply {
    action = Intent.ACTION_VIEW
    putExtra("id", id)
}

// also — a side effect without breaking the chain
val users = repo.load()
    .also { log("loaded ${it.size}") }
    .filter { it.isActive }
```

**In practice you'll use `let` and `apply` constantly and the others rarely.** Learn those two properly and pick up the rest as you meet them.

**Don't nest them.** Nested `let { it.let { } }` blocks are unreadable — name the variable instead.

## Higher-order functions and `inline`

```kotlin
inline fun measure(block: () -> Unit) {
    val start = System.nanoTime()
    block()
    println(System.nanoTime() - start)
}
```

**`inline` substitutes the function body at the call site**, which avoids allocating a lambda object. **That's why the standard library's collection operations are inline** — `list.map { }` allocates nothing for the lambda.

**It also enables `reified` type parameters and non-local returns:**

```kotlin
inline fun <reified T> parse(s: String): T = ...     // T known at runtime
```

**Don't mark large functions `inline`** — you're duplicating the body at every call site, and bytecode size matters on Android.

## Collections

```kotlin
val names   = users.map { it.name }
val adults  = users.filter { it.age >= 18 }
val byCity  = users.groupBy { it.city }
val total   = prices.sumOf { it.amount }
val first   = users.firstOrNull { it.isAdmin }
val (a, b)  = users.partition { it.isActive }
users.associateBy { it.id }                          // List → Map keyed by id
```

**`it` is the implicit single parameter** — the equivalent of Swift's `$0`.

**Mutability is in the type:**

```kotlin
val list: List<String>          // read-only VIEW
val list: MutableList<String>   // mutable
```

**`List` is read-only, not immutable** — the underlying object may be mutable and held elsewhere. **`kotlinx.collections.immutable` provides genuinely immutable collections** if you need the guarantee.

**Sequences for large chains:**

```kotlin
list.asSequence().map(expensive).filter(test).first()   // lazy, short-circuits
```

**Kotlin collection operations are eager and allocate an intermediate list per step.** For long chains on large data, `asSequence()` makes it lazy — and for short chains on small lists it's slower. **Measure.**

## Idioms worth adopting

```kotlin
require(age >= 0) { "age must be non-negative" }        // argument validation → IllegalArgumentException
check(state == Ready) { "not ready" }                   // state validation → IllegalStateException
requireNotNull(user) { "no user for $id" }

val result = runCatching { risky() }.getOrElse { fallback }

repeat(3) { retry() }
```

**`require`/`check` beat manual `if (…) throw`** — they read better and carry the message lazily.

## Key insight

**Extension functions are Kotlin's most-used feature and the reason the language could improve Java's ecosystem without replacing it** — you add the API you wish existed, at zero runtime cost. Combined with `inline` lambdas and default arguments, that's most of what makes Kotlin feel lighter than Java while running on exactly the same platform.

## Related
- [[languages/09-kotlin/03-types-and-data-classes|types and data classes]]
- [[languages/09-kotlin/05-coroutines-and-flow|coroutines]] — built on `inline` and suspending lambdas
- [[languages/01-java/README|Java]] — what these idioms replace
