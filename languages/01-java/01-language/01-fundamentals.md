# Java Fundamentals

**Source:** the ground-floor material merged from both projects' `01-java-fundamentals.md`, expanded to cover the "Learn the Basics" topics ([roadmap.sh Java](https://roadmap.sh/java)) the projects didn't exercise (type casting, operator/scoping details, `final`, pass-by-value). The deeper topics this file used to bundle now have dedicated homes — see the handoffs below.

## Why Java looks the way it does

Java is **statically typed** — every variable's type is declared and checked at compile time, not discovered at runtime:

```java
String name = "Kingsley";   // type declared up front
name = 42;                  // compile error — a String variable can't hold an int
```

It is **compiled** to bytecode before it runs, so a whole class of errors surfaces at compile time instead of in production. It is **verbose** on purpose — the braces, semicolons, and explicit types make large, multi-author codebases easier to read at the cost of being slower to write. That tradeoff (verbosity for readability-at-scale) is why Java dominates enterprise and fintech: every bank needs codebases many engineers can safely modify years after the original author left.

A `.java` file is compiled by `javac` into `.class` bytecode, which the JVM loads and runs — "write once, run anywhere," because the bytecode is portable and the JVM is what's platform-specific. What the JVM actually does with that bytecode (loading, JIT-compiling, garbage-collecting) is [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|its own topic]].

## The program's entry point

```java
public class Hello {
    public static void main(String[] args) {   // the JVM calls this to start the program
        System.out.println("Hello");
    }
}
```

`main` must be `public static void` with a `String[]` parameter — `static` because the JVM calls it without constructing an object first (see [static vs instance](#static-vs-instance) below). Every file's public class name must match the filename exactly (`Hello.java` ↔ `class Hello`).

## Packages and imports

Every file opens with a package declaration — a namespace mirroring the folder path, in reverse-domain notation for global uniqueness:

```java
package com.itc.direct_debit_sandbox.subscriptions;
// lives in src/main/java/com/itc/direct_debit_sandbox/subscriptions/
```

To use a type from another package, `import` it. `java.lang` (String, Integer, System, …) is imported implicitly.

## Variables, scope, and `final`

A variable's **scope** is the block `{ }` it's declared in — it exists from its declaration to the closing brace, and referencing it outside is a compile error. This is why loop counters don't leak and why you can reuse a name in a sibling block.

`final` means a variable can be assigned exactly once and never reassigned:

```java
final int MAX = 100;
MAX = 200;   // compile error
```

`final` on a **reference** freezes the reference, not the object it points at — `final List<String> xs = new ArrayList<>()` still allows `xs.add(...)`, just not `xs = somethingElse`. This distinction matters for lambdas and threads, which require captured local variables to be *effectively final* (see [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]]).

## Data types: primitives vs objects

Java has eight **primitives** (stored as raw values, never null) and everything else is an **object** (a reference, which can be null):

```java
int    count = 5;          // 32-bit integer
long   big   = 100_000L;    // 64-bit — note the L suffix and _ digit separators
double price = 34.02;       // 64-bit floating point
float  f     = 1.5f;        // 32-bit — note the f suffix
boolean ok   = true;
char   c     = 'A';         // single 16-bit UTF-16 unit
byte, short                 // 8-bit, 16-bit integers

Integer boxedCount = 5;     // object wrapper — can be null, needed for generics/collections
```

Each primitive has an object **wrapper** (`int`↔`Integer`, `boolean`↔`Boolean`, …). **Autoboxing** converts between them automatically, but two traps follow from it: a `null` `Integer` unboxed into an `int` throws `NullPointerException`, and `==` on two wrapper objects compares references, not values (use `.equals()` or unbox first). See [`Boolean.TRUE.equals()`](#null-and-nullpointerexception) below for the null-safe idiom.

### Type casting

**Widening** (smaller → larger) is implicit; **narrowing** (larger → smaller) needs an explicit cast and can lose data:

```java
int i = 100;
long l = i;             // widening — automatic
int back = (int) l;     // narrowing — explicit cast required
int truncated = (int) 3.99;   // 3 — the fractional part is dropped, not rounded
```

For objects, a cast asserts a subtype relationship the compiler can't prove; if wrong at runtime it throws `ClassCastException` (which modern **pattern matching** makes safer — see [[languages/01-java/01-language/07-modern-java|Modern Java]]).

## Operators and math

Standard arithmetic (`+ - * / %`), comparison (`== != < > <= >=`), logical (`&& || !`), and the ternary `condition ? a : b`. Two gotchas worth internalizing:

- **Integer division truncates**: `7 / 2` is `3`, not `3.5`. Force floating point with a cast or a literal: `7 / 2.0`.
- **`==` on objects compares references, not contents** — `"a" == new String("a")` is `false`; use `.equals()`. This is the single most common beginner bug in Java.

The `Math` class holds the rest (`Math.abs`, `Math.max`, `Math.pow`, `Math.floorMod`, …). `Math.abs` matters more than it looks — `hashCode()` can return a negative int, so `Math.abs(x.hashCode()) % n` is the idiom for mapping a hash into a bucket range.

## Strings

`String` is **immutable** — every operation that "changes" a string returns a new one; the original is untouched. This makes strings safe to share across threads but means building a string in a loop with `+` creates a new object every iteration (O(n²) garbage):

```java
// Wrong for loops — allocates a new String each iteration
String s = "";
for (String part : parts) s += part;

// Right — StringBuilder mutates one buffer
StringBuilder sb = new StringBuilder();
for (String part : parts) sb.append(part);
String s = sb.toString();
```

`StringBuilder` is the mutable, single-threaded builder (`StringBuffer` is its synchronized, rarely-needed cousin). Common methods: `.length()`, `.charAt(i)`, `.substring(a, b)`, `.split(regex)`, `.trim()`/`.strip()`, `.equals()` / `.equalsIgnoreCase()`, `.contains()`, `.replace()`. For multi-line strings, use **text blocks** ([[languages/01-java/01-language/07-modern-java|Modern Java]]).

## Arrays

A fixed-length, indexed, homogeneous sequence — length is set at creation and never changes:

```java
int[] nums = new int[5];        // five zeros
int[] xs = {1, 2, 3};           // literal
xs[0] = 10;
int n = xs.length;              // a field, not a method (unlike String.length())
int[][] grid = new int[3][4];   // 2D
```

For a growable sequence, reach for `ArrayList` ([[languages/01-java/01-language/04-collections|Collections]]) — `array-vs-ArrayList` is a classic interview question: arrays are fixed-size and can hold primitives directly; `ArrayList` grows dynamically but only holds objects (boxed primitives).

## Control flow

`if`/`else if`/`else`, the classic `for`, the enhanced for-each (`for (var x : xs)`), `while`, and `do/while`. `break` exits a loop, `continue` skips to the next iteration. The modern `switch` is covered in [[languages/01-java/01-language/07-modern-java|Modern Java]] (it's now an expression that returns a value).

## Access modifiers

| Modifier | Visible to |
|---|---|
| `public` | Anyone, anywhere |
| `private` | Only the same class |
| `protected` | Same class + subclasses + same package |
| *(none — package-private)* | Only the same package |

Rule of thumb: default to `private`; widen only when something outside genuinely needs it. Encapsulation ([[languages/01-java/01-language/02-oop|OOP]]) is built on this.

## Static vs instance

```java
public class Counter {
    static int total;        // one copy, shared by the whole class
    int value;               // one copy per object

    static void reset() { total = 0; }   // called as Counter.reset()
    int get() { return value; }          // called on an object: c.get()
}
```

`static` members belong to the class itself, not to any object — accessed via the class name, and unable to reference instance fields (there's no `this`). A **static initializer block** (`static { ... }`) runs once when the class is first loaded, before any object exists — used for one-time shared setup like a connection pool:

```java
public class DatabaseConfig {
    private static HikariDataSource dataSource;
    static {
        dataSource = new HikariDataSource(buildConfig());   // one pool, however many times the class is referenced
    }
}
```

If a static initializer throws, the class fails to load and the JVM throws `ExceptionInInitializerError` — the app dies at startup rather than failing subtly later.

## Pass-by-value — always

Java is **always pass-by-value**, with no exceptions — a classic interview trap because it *looks* like pass-by-reference for objects. What's passed by value is the **reference** (the pointer), not the object. So a method can mutate the object a reference points to, but reassigning the parameter doesn't affect the caller's variable:

```java
void mutate(List<String> list) { list.add("x"); }   // caller sees "x" added — same object
void reassign(List<String> list) { list = new ArrayList<>(); }   // caller unaffected — only the local copy of the reference changed
```

For primitives it's unambiguous — the value is copied, and the method can't touch the caller's variable at all.

## null and NullPointerException

`null` means "no object," and any object-typed variable can hold it. Calling a method on a null reference throws `NullPointerException` (NPE) — the most common Java runtime error:

```java
Record r = store.get(id);
if (r == null) return error();   // guard before use
r.getStatus();
```

The `Boolean`-under-null idiom: comparing a boxed `Boolean` directly (`if (flag == true)`) throws NPE when it's null. `Boolean.TRUE.equals(flag)` is null-safe — `false` for null, false, or non-Boolean, never throwing:

```java
.triggerDebitStatus(Boolean.TRUE.equals(req.getTriggerDebitStatus()))
```

Modern Java's `Optional` ([[languages/01-java/01-language/05-functional-programming|Functional Programming]]) is the type-level answer to "this might be absent."

## BigDecimal for money — never double

`double`/`float` use IEEE 754 binary floating point, which cannot exactly represent most decimal fractions — `0.1 + 0.2` prints `0.30000000000000004` in every language that uses it. For money, sub-cent errors compound across millions of transactions:

```java
BigDecimal total = BigDecimal.ZERO;
for (int i = 0; i < 1000; i++) total = total.add(new BigDecimal("34.10"));
// 34100.00 — exact
```

Always construct `BigDecimal` from a **String** (`new BigDecimal("34.10")`), never a double (`new BigDecimal(34.10)` inherits the double's imprecision). The MySQL counterpart is `DECIMAL(18,2)` — see [[languages/01-java/04-persistence/01-jdbc-and-data-modeling|JDBC & Data Modeling]].

## Handoffs — where the rest of "the basics" went

This file is deliberately the ground floor. The topics it used to bundle now have dedicated treatment:

- Classes, objects, inheritance, interfaces, the four OOP pillars → [[languages/01-java/01-language/02-oop|OOP]]
- `try`/`catch`/`finally`, try-with-resources, checked vs unchecked → [[languages/01-java/01-language/06-exceptions|Exceptions]]
- `List`/`Map`/`Set` and friends → [[languages/01-java/01-language/04-collections|Collections]]
- Streams, lambdas, `Optional` → [[languages/01-java/01-language/05-functional-programming|Functional Programming]]
- `switch` expressions, text blocks, records, `var` → [[languages/01-java/01-language/07-modern-java|Modern Java]]
- Date/time, regex, files, networking, annotations → [[languages/01-java/01-language/08-core-apis|Core APIs]]

## Related
- [[languages/01-java/01-language/02-oop|OOP]] — the next step up
- [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM Internals]] — what runs the bytecode this file compiles to
- [[foundations/dsa/README|DSA]] — language-agnostic algorithms and data structures
