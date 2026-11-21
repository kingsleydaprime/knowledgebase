---
id: d67a466d-8d5f-4969-b300-7102ae8603f3
---

# Classes, Objects and Java Interop

Classes and objects are how Kotlin lets you define your own types, and interop is how Kotlin code works side by side with Java code. Most Android projects mix the two languages. This lesson covers Kotlin's class features and what to watch for when calling Java.

## Classes
<!-- bite: b1f89b6c-75d4-4d5a-bd6b-badceaf7fb9e -->

```kotlin
class User(
    val id: String,                   // property, declared in the constructor
    var name: String,
    private val secret: String,
) {
    val displayName: String
        get() = name.ifBlank { "Anonymous" }      // computed

    init { require(id.isNotBlank()) }              // runs at construction
}
```

**Constructor parameters with `val`/`var` become properties.** No field declaration, no assignment, no getter or setter. That alone removes most of a Java class's body.

**Everything is `final` by default.** To allow subclassing:

```kotlin
open class Base { open fun render() {} }
class Child : Base() { override fun render() {} }
```

**`open` rather than Java's `final`-by-omission** is a deliberate inversion — inheritance is opt-in, because subclassing something not designed for it is how fragile hierarchies happen.

**`override` is mandatory**, so you can't accidentally shadow or accidentally fail to override.

## Visibility
<!-- bite: b5a99ccd-d6ba-4db1-a69f-0f3759511da5 -->

|             |                                                                                                 |
| ----------- | ----------------------------------------------------------------------------------------------- |
| `public`    | Default                                                                                         |
| `internal`  | **Visible within the module** — no Java equivalent, and genuinely useful for library boundaries |
| `protected` | Subclasses only                                                                                 |
| `private`   | The file (top-level) or the class                                                               |

**`internal` is the one Java lacks.** It lets a library have implementation classes that are visible across its own source set but not to consumers.

## Interfaces
<!-- bite: e85b2cd3-995b-4ccd-acb1-ec9847a1bb6f -->

```kotlin
interface Repository {
    val name: String                       // abstract PROPERTY — Java can't do this
    fun get(id: String): User?
    fun exists(id: String) = get(id) != null    // default implementation
}
```

**Interfaces can declare properties and provide default implementations**, but hold no state.

## Delegation with `by`
<!-- bite: b1650a2e-ce01-4dc7-a591-9ddddd89143e -->

```kotlin
class LoggingRepo(private val inner: Repository) : Repository by inner {
    override fun get(id: String): User? {
        log("get $id")
        return inner.get(id)
    }
}
```

**Implement an interface by forwarding to another object**, overriding only what you want to change. **This is composition without writing forwarding methods**, and it's a genuine answer to "prefer composition over inheritance" that most languages don't provide.

## Java interop — what to know
<!-- bite: f18f470a-473f-4f5e-9510-38c82f16c2f8 -->

**Calling Java from Kotlin** mostly just works, with two frictions:

**1. Platform types.** Java's return types become `String!` — Kotlin doesn't know if they're null. **Declare the type explicitly at the boundary** → [[languages/09-kotlin/02-null-safety|null safety]].

**2. SAM conversion.** A Java single-abstract-method interface accepts a lambda:

```kotlin
button.setOnClickListener { doThing() }
```

**Calling Kotlin from Java** needs more care, and these annotations exist for it:

```kotlin
@JvmStatic          // companion function → a real static method
@JvmOverloads       // generates overloads for default arguments (Java has none)
@JvmName("check")   // rename in the bytecode
@JvmField           // expose the field directly, no getter
@Throws(IOException::class)   // declare a checked exception Java can catch
```

**`@JvmOverloads` is the one you'll need most** — Java callers can't use default arguments, so without it they must pass every parameter. **Essential on custom Android Views**, whose constructors are called from XML.

**Kotlin has no checked exceptions**, so a Kotlin function that throws `IOException` looks safe to Java. `@Throws` fixes the signature.

## Things that don't map
<!-- bite: 2e522134-3086-4b56-bdc2-5e35fbf6294a -->

- **Kotlin's `Nothing`** — the type of an expression that never returns. `TODO()` returns it, which is why `val x: String = TODO()` compiles
- **`Unit`** vs Java's `void` — `Unit` is a real singleton type, so it can be a generic parameter
- **Inline classes** are erased to their underlying type in Java
- **Coroutines** — a `suspend` function seen from Java takes an extra `Continuation` parameter and is unpleasant to call. **Provide a callback or `CompletableFuture` wrapper** at the boundary

## Key insight
<!-- bite: 926900e2-4a49-4eb3-a448-b13b1aadbb3a -->

**Kotlin's object model is Java's with the defaults inverted** — final instead of open, non-null instead of nullable, properties instead of fields, composition (`by`) made as cheap as inheritance. Every one of those inversions is a lesson learned from twenty years of Java, and the interop annotations exist because the two must still coexist in the same codebase.

## Related
<!-- bite: 78511de1-b2eb-4058-82d6-db2d211fd183 -->

- [[languages/09-kotlin/02-null-safety|null safety]] — platform types
- [[languages/01-java/index|Java]] — the platform and the contrast
- [[languages/09-kotlin/03-types-and-data-classes|data and sealed classes]]

## About this lesson
<!-- bite: c370d14e-6b06-4870-bcf2-506f83ab75b1 -->

**Level:** Intermediate. **Covers:** the object model, and living alongside Java.
