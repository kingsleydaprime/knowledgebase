# Java Interview — Language & Collections

From [[languages/01-java/01-language/README|01-language/]]. The screening round — get these fast and clean so the conversation can move to the interesting parts.

🔥 marks questions that come up constantly.

---

### Q1. [Beginner] 🔥 `==` vs `.equals()`, and what's the contract you must not break?

**Strong answer covers:** `==` compares references for objects (identity), values for primitives. `.equals()` compares logical equality as the class defines it.

**The contract, which is the actual question:** if you override `equals`, you **must** override `hashCode`, because "equal objects must have equal hash codes." Break it and your object silently misbehaves in every `HashMap` and `HashSet` — you put it in, then can't find it, because lookup goes to a different bucket. It's silent data loss, not an exception.

**Detail worth adding:** `equals` must also be reflexive, symmetric, transitive, and consistent. The classic symmetry violation is a subclass adding a field to the comparison, so `a.equals(b)` and `b.equals(a)` disagree. `record` types generate both correctly, which is one good reason to reach for them.

**The Integer cache trap:** `Integer a = 127, b = 127; a == b` is `true`; at `128` it's `false`, because `Integer.valueOf` caches −128..127. Never compare boxed types with `==`.

---

### Q2. [Beginner] 🔥 `ArrayList` vs `LinkedList` — when would you actually use `LinkedList`?

**Strong answer covers:** `ArrayList` is a backing array — O(1) random access, O(n) middle insert, amortised O(1) append (with a resize-and-copy at the boundary). `LinkedList` is a doubly-linked list — O(1) insert/remove *given a node*, but O(n) to *find* it, and O(n) random access.

**The honest answer, and the one that scores:** **almost never.** Even for frequent middle inserts, `ArrayList` usually wins because its elements are contiguous, so it's cache-friendly, while `LinkedList` chases pointers all over the heap and carries a node object of overhead per element. The theoretical complexity favours `LinkedList`; the memory hierarchy overrules it. If you need queue semantics, use `ArrayDeque` — it beats both.

**This is a mechanical-sympathy question in disguise.** Saying "O(1) insert so LinkedList" is the wrong answer; saying "big-O ignores the constant factor and cache behaviour dominates at realistic sizes" is the right one.

---

### Q3. [Intermediate] 🔥 How does `HashMap` work internally?

**Strong answer covers:** an array of buckets; index = `hash(key)` spread and masked to the table size. Collisions chain in a linked list, and **since Java 8 a bucket converts to a red-black tree at 8 entries** (back to a list at 6), so worst-case lookup degrades to O(log n) rather than O(n). Resize doubles the table at the load factor (0.75) and rehashes.

**Detail worth adding:** the table size is always a power of two so the index is a cheap `hash & (n-1)` rather than a modulo. And `HashMap` applies its own spreading function (`h ^ (h >>> 16)`) because a bad `hashCode` that only varies in high bits would otherwise collide constantly.

**The security angle:** the treeify behaviour was added partly to blunt **hash-collision DoS**, where an attacker submits keys engineered to land in one bucket and turns every lookup into O(n).

**The concurrency trap:** a `HashMap` resized concurrently by two threads could historically form a **circular linked list**, making a subsequent `get` spin forever at 100% CPU. Not a data race you'll ever see in a test — use `ConcurrentHashMap`.

---

### Q4. [Intermediate] Checked vs unchecked exceptions — what's your actual policy?

**Strong answer covers:** checked extend `Exception` and must be declared or caught; unchecked extend `RuntimeException` and needn't be. The intent was "checked = recoverable."

**Have an opinion, because they're asking for one:** checked exceptions largely failed in practice — they don't compose with lambdas/streams, they leak implementation details up through interfaces, and they push people into `catch (Exception e) {}`. Most modern Java leans unchecked, with checked reserved for genuinely recoverable, caller-actionable conditions. Spring and most modern libraries wrap checked exceptions into unchecked ones for exactly this reason.

**The rules regardless of policy:** never swallow an exception silently; always preserve the cause when wrapping (`new XException(msg, e)`) or you destroy the stack trace; don't use exceptions for control flow (they're expensive, mostly from stack-trace capture).

---

### Q5. [Intermediate] 🔥 What does `final` mean in each place it can appear?

**Strong answer covers:** `final` **variable** = can't be reassigned (**but the object it points at is still mutable** — `final List` can still be `add`ed to; this is the distinction they're testing). `final` **method** = can't be overridden. `final` **class** = can't be extended.

**Detail worth adding:** `final` fields have a real **memory-model** guarantee — a properly constructed object's final fields are visible to other threads without synchronisation, provided the reference doesn't escape during construction. That's why immutability is a genuine concurrency strategy rather than just a style preference. → [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM internals]]

---

### Q6. [Intermediate] Explain generics and type erasure. What does erasure cost you?

**Strong answer covers:** generics are compile-time only — the compiler checks types and inserts casts, then **erases** the parameter to its bound (usually `Object`). `List<String>` and `List<Integer>` are the same class at runtime.

**What erasure costs:** you can't do `new T[]`, can't `instanceof List<String>`, can't overload on `List<String>` vs `List<Integer>` (same erased signature), and you need `Class<T>` tokens or a `TypeReference` to recover type info at runtime (which is why Jackson's API looks the way it does).

**Why they did it:** migration compatibility — pre-generics code had to keep working. A deliberate trade of runtime power for adoption, and worth naming as such.

**Bonus — PECS:** `? extends T` to read (Producer), `? super T` to write (Consumer). "Producer Extends, Consumer Super."

---

### Q7. [Intermediate] 🔥 What's the difference between a stream and a collection, and when do streams hurt?

**Strong answer covers:** a collection *holds* elements; a stream *describes a computation over* them. Streams are lazy (nothing happens until a terminal operation), single-use, and don't mutate the source.

**When they hurt — have a real answer here:** on hot paths, streams allocate (lambdas, boxed values, intermediate objects) and are harder for the JIT to inline than a plain loop, so a tight numeric loop is usually faster written plainly. And `parallelStream()` is a trap — it uses the common `ForkJoinPool`, so one slow parallel stream can starve every other user of it, and it only pays off with large datasets and genuinely CPU-bound, side-effect-free work.

**Given a low-latency target, say this:** in allocation-sensitive code you avoid streams on the hot path entirely, for the same reason you avoid boxing — it's GC pressure, and GC pressure is p99 latency. → [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|GC]]

---

### Q8. [Intermediate] What are records, sealed types, and pattern matching for?

**Strong answer covers:** `record` = a transparent immutable data carrier, with generated constructor/accessors/`equals`/`hashCode`/`toString`. `sealed` = an explicitly closed set of permitted subtypes. Pattern matching (`instanceof` patterns, switch patterns) destructures them.

**The point they're driving at:** together these bring **algebraic data types** and exhaustive matching to Java. Sealed + switch patterns means the *compiler* tells you when you've missed a case — which turns a class of runtime bug into a compile error, and makes modelling a domain as data far more pleasant than the visitor-pattern gymnastics it used to require. → [[languages/01-java/01-language/07-modern-java|modern java]]

---

### Q9. [Beginner→Intermediate] String immutability — why, and what's the interning trap?

**Strong answer covers:** `String` is immutable, so it's safe to share across threads, safe as a `HashMap` key (its hash can be cached), and safe to pass without defensive copying. String literals are **interned** in a pool, so identical literals are the same object — which is exactly why `==` sometimes appears to work on strings and then breaks the moment a string comes from user input or concatenation at runtime. Always `.equals()`.

**Detail worth adding:** string concatenation in a loop creates a new object each iteration (O(n²)); use `StringBuilder`. Since Java 9, `+` on strings compiles to `invokedynamic` with `StringConcatFactory`, which is faster than the old `StringBuilder` desugaring — but still not free in a loop.

---

### Q10. [Advanced] Why is `Optional` recommended as a return type but not a field or parameter?

**Strong answer covers:** `Optional` was designed to express "this method may not return a value" at the API boundary, so callers can't ignore it the way they ignore the possibility of `null`. As a **field** it's wasteful (an extra object per instance) and isn't `Serializable`. As a **parameter** it just moves the null check without removing it — callers now have to construct an `Optional` to pass nothing.

**The anti-patterns to name:** `optional.get()` without `isPresent()` is just a worse NPE; `Optional.of(maybeNull)` throws (use `ofNullable`); and returning `Optional<List<T>>` is almost always wrong — return an empty list.
