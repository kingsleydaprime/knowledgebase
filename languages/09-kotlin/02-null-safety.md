# Null Safety

**[Beginner → Intermediate]** — the feature Kotlin is best known for, and the hole in it.

## Nullability is in the type system

```kotlin
var name: String  = "Ada"     // can NEVER be null
var maybe: String? = null     // nullable

name = null                   // ❌ compile error
maybe.length                  // ❌ compile error — must handle null first
```

**`String` and `String?` are different types.** The compiler will not let you dereference the nullable one without handling the null case — which eliminates NullPointerException as a category in pure Kotlin code.

**Same idea as [[languages/08-swift/02-values-references-and-optionals|Swift's optionals]]**, arrived at independently, and it's now the consensus design for new languages.

## Handling null

```kotlin
// 1. Safe call — returns null instead of throwing
val len: Int? = maybe?.length

// 2. Chained
val city = user?.address?.city

// 3. Elvis — supply a default, or return early
val len = maybe?.length ?: 0
val user = repo.find(id) ?: return null
val user = repo.find(id) ?: throw NotFoundException()

// 4. Smart cast — the compiler tracks it
if (maybe != null) {
    println(maybe.length)     // no ?. needed — the compiler KNOWS
}

// 5. let, for "do this only if not null"
maybe?.let { println(it.length) }

// 6. Not-null assertion — THROWS if null
val len = maybe!!.length
```

**Smart casts are the pleasant part** — after a null check, the compiler narrows the type automatically, so you don't repeat `?.` everywhere.

**Smart casts don't work on `var` properties of other classes**, because another thread could change them between the check and the use. **Copy into a local `val` first** — that's the standard workaround, and the reason for it is worth understanding.

## `!!` — the operator to justify

**`!!` says "I guarantee this isn't null" and throws NPE if you're wrong.** It's deliberately ugly.

**Legitimate uses are rare.** Almost every `!!` in real code should be a `?:` with a sensible default, a `requireNotNull` with a message, or a restructure so the value can't be null in the first place.

```kotlin
val user = requireNotNull(repo.find(id)) { "No user for $id" }   // better than !!
```

**A `!!` that throws gives you a stack trace and no explanation.** `requireNotNull` gives you the same trace plus the reason.

## The hole: platform types

**Kotlin cannot know whether Java code returns null.** So Java types become **platform types**, written `String!`:

```kotlin
val s = javaObject.getName()      // String! — Kotlin doesn't know
s.length                          // compiles. May NPE at runtime.
```

**This is where NPEs still come from in Kotlin**, and it's most of Android's older framework surface.

**What to do:**
- **Declare the type explicitly at the boundary** — `val s: String? = javaObject.getName()` forces you to handle it
- **Annotate your Java** with `@Nullable`/`@NonNull` — Kotlin respects these and the platform type disappears
- **Treat every Java boundary as suspect**

## `lateinit`

For properties genuinely initialised after construction — dependency injection, Android's `onCreate`:

```kotlin
lateinit var repository: Repository

if (::repository.isInitialized) { }      // check, if you must
```

**Throws `UninitializedPropertyAccessException` if read too early** — a clearer error than an NPE, at least. **Only for `var`, only for non-null non-primitives.**

**Prefer `by lazy` where you can:**

```kotlin
val expensive: Config by lazy { loadConfig() }    // computed once, on first access
```

`lazy` is thread-safe by default and needs no initialisation ceremony.

## Nullable collections

Three distinct things, and mixing them up is common:

```kotlin
List<String>?     // the list may be null
List<String?>     // the list holds nullable strings
List<String?>?    // both
```

```kotlin
val clean: List<String> = maybeNulls.filterNotNull()
```

## Key insight

**Kotlin didn't remove null — it moved it into the type system so the compiler can check it.** The guarantee is genuine and holds completely within Kotlin, and **it stops at the Java boundary**, where platform types silently reintroduce the risk. So the discipline that remains is: annotate your Java, declare types explicitly at boundaries, and treat `!!` as something you have to justify.

## Related
- [[languages/09-kotlin/03-types-and-data-classes|types and data classes]]
- [[languages/08-swift/02-values-references-and-optionals|Swift's optionals]] — the same idea
- [[languages/01-java/README|Java]] — where the platform types come from
