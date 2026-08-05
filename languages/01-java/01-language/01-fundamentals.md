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

The wrappers also hold the **parsing** utilities — turning a `String` (e.g. a line of user input) into a number, and constants like the type's min/max:

```java
int    n = Integer.parseInt("42");        // "42" → 42; throws NumberFormatException on garbage
double d = Double.parseDouble("3.14");
int    max = Integer.MAX_VALUE;           // 2_147_483_647
```

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

Standard arithmetic (`+ - * / %`), comparison (`== != < > <= >=`), logical (`&& || !`), and the ternary (below). Two gotchas worth internalizing:

- **Integer division truncates**: `7 / 2` is `3`, not `3.5`. Force floating point with a cast or a literal: `7 / 2.0`.
- **`==` on objects compares references, not contents** — `"a" == new String("a")` is `false`; use `.equals()`. This is the single most common beginner bug in Java.

**Order of operations** follows PEMDAS — **P**arentheses, **E**xponents, **M**ultiplication/**D**ivision (left to right), **A**ddition/**S**ubtraction (left to right). `2 + 3 * 4` is `14`, not `20`; parenthesize when in doubt — `(2 + 3) * 4` is `20`. Compound-assignment operators (`+= -= *= /= %=`) and increment/decrement (`x++`, `++x`) are the usual shorthand; pre-increment (`++x`) increments *then* yields the new value, post-increment (`x++`) yields the old value *then* increments.

### The ternary operator

`condition ? valueIfTrue : valueIfFalse` is an **expression** (it returns a value), so it's a compact `if/else` for assignments and inline choices — not a replacement for multi-branch logic:

```java
int score = 68;
String grade = score >= 60 ? "Pass" : "Fail";   // "Pass"
String parity = (n % 2 == 0) ? "even" : "odd";
```

### The Math class

`Math` holds the numeric toolkit — access every member statically off the class name:

```java
Math.PI              // 3.141592653589793 — and Math.E for Euler's number
Math.pow(2, 3)       // 8.0  — base to a power (returns double)
Math.sqrt(9)         // 3.0
Math.abs(-5)         // 5    — distance from zero; also the idiom for a non-negative bucket: Math.abs(x.hashCode()) % n
Math.max(10, 20)     // 20   — and Math.min(10, 20) → 10
Math.round(3.14)     // 3    — nearest whole; Math.ceil(3.14) → 4.0 (up), Math.floor(3.99) → 3.0 (down)
Math.random()        // a double in [0.0, 1.0) — see Random below for bounded ints
```

`Math.floorMod` is the one non-obvious member — unlike `%`, it never returns a negative result, so it's the correct modulo for wrapping indices. A worked example — the **hypotenuse of a right triangle**, `c = √(a² + b²)`:

```java
double a = 3, b = 4;
double c = Math.sqrt(Math.pow(a, 2) + Math.pow(b, 2));   // 5.0
```

### Random numbers

`java.util.Random` generates pseudo-random values. Construct one, then pull values by type:

```java
Random random = new Random();
int die   = random.nextInt(1, 7);    // 1..6 — lower-inclusive, upper-EXCLUSIVE (so 7, not 6)
int pct   = random.nextInt(100);     // legacy single-arg form: 0..99
double d  = random.nextDouble();     // [0.0, 1.0)
boolean b = random.nextBoolean();    // coin flip
```

The exclusive upper bound is the classic off-by-one trap: `nextInt(1, 6)` never yields 6. Passing a fixed **seed** (`new Random(42)`) makes the sequence reproducible — invaluable for tests. For concurrent code prefer `ThreadLocalRandom`, and for anything security-sensitive (tokens, keys) use `SecureRandom` — see [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation]].

## Console I/O — reading input and formatting output

Most beginner programs follow one shape: **read input → process → print output**. `Scanner` handles the input half.

### Scanner — reading user input

`Scanner` wraps an input source (`System.in` for the keyboard) and hands back typed values. It lives in `java.util`, so `import java.util.Scanner;`:

```java
Scanner scanner = new Scanner(System.in);

System.out.print("Enter your name: ");
String name = scanner.nextLine();     // reads a whole line, spaces included

System.out.print("Enter your age: ");
int age = scanner.nextInt();          // reads one int; nextDouble()/nextBoolean() for other types

scanner.close();                      // release the resource when done
```

The read methods mirror the primitive types: `nextInt()`, `nextDouble()`, `nextBoolean()`, `next()` (one whitespace-delimited token), and `nextLine()` (the rest of the line). Two traps:

- **`next()` vs `nextLine()`** — `next()` stops at the first space (`"Kingsley Ihe"` → `"Kingsley"`); `nextLine()` takes the whole line.
- **The leftover-newline trap** — `nextInt()`/`nextDouble()` consume the number but *leave the trailing newline in the buffer*, so the next `nextLine()` reads an empty string. The fix is to consume that dangling newline with a throwaway `scanner.nextLine();` right after the numeric read:

```java
int qty = scanner.nextInt();
scanner.nextLine();                   // discard the leftover newline
String note = scanner.nextLine();     // now reads real input, not ""
```

Because `Scanner` is a resource, the idiomatic form is **try-with-resources**, which closes it automatically ([[languages/01-java/01-language/06-exceptions|Exceptions]]):

```java
try (Scanner scanner = new Scanner(System.in)) {
    System.out.print("Enter two words for a Mad Libs: ");
    String noun = scanner.next();
    String verb = scanner.next();
    System.out.printf("The %s likes to %s.%n", noun, verb);
}   // scanner.close() runs automatically
```

### printf — formatted output

`System.out.printf` (and its string-returning twin `String.format`) formats output with `%`-placeholders instead of `+` concatenation. Each placeholder is `%` + optional flags/width/precision + a **conversion character**:

| Specifier | For | Example → output |
|---|---|---|
| `%s` | string | `printf("%s", "Bob")` → `Bob` |
| `%d` | integer | `printf("%d", 30)` → `30` |
| `%f` | floating point | `printf("%f", 9.5)` → `9.500000` |
| `%c` | char | `printf("%c", 'A')` → `A` |
| `%b` | boolean | `printf("%b", true)` → `true` |
| `%n` | platform newline | (portable `\n`) |

`printf` does **not** add a newline — end lines with `%n` yourself. Arguments are comma-separated and fill the placeholders left to right:

```java
System.out.printf("%s is %d years old%n", name, age);   // Bob is 30 years old
```

Between the `%` and the specifier you can add, in order, **flags → width → precision**:

- **Precision** `%.2f` — digits after the decimal (rounds): `printf("%.2f", 9.999)` → `10.00`. Essential for money and the compound-interest project.
- **Width** `%5d` — minimum field width, right-justified; `%-5d` left-justifies; `%05d` zero-pads (`1` → `00001`). Used to align columns of IDs.
- **Flags** — `+` forces a sign on positives, `,` adds thousands grouping (`%,d` → `1,000,000`), `(` wraps negatives in parentheses, space reserves a leading space for the sign.

```java
System.out.printf("%-10s $%,.2f%n", "Total:", 1234567.5);   // Total:     $1,234,567.50
```

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

`StringBuilder` is the mutable, single-threaded builder (`StringBuffer` is its synchronized, rarely-needed cousin). The common method surface:

```java
String s = "Hello World";
s.length();                 // 11 — a method, unlike array.length (a field)
s.charAt(0);                // 'H'
s.indexOf("World");         // 6  — first index of a substring, or -1 if absent
s.toUpperCase();            // "HELLO WORLD"  — and toLowerCase()
s.trim();                   // strips leading/trailing whitespace (strip() is the Unicode-aware modern form)
s.replace("World", "Java"); // "Hello Java"
s.contains("ell");          // true
s.split(" ");               // ["Hello", "World"] — splits on a regex
s.equals("hello");          // false — case-sensitive; equalsIgnoreCase() ignores case
s.isEmpty();                // false; isBlank() is true for whitespace-only
```

**`substring`** extracts a slice. `substring(begin)` runs from `begin` to the end; `substring(begin, end)` is **begin-inclusive, end-exclusive** — the same half-open convention as most Java ranges, so `end - begin` is the length of the result:

```java
String email = "Kingsley@gmail.com";
int at = email.indexOf("@");              // 8
String user   = email.substring(0, at);   // "Kingsley"  — indices 0..7
String domain = email.substring(at + 1);  // "gmail.com"  — index 9 to the end
```

For multi-line strings, use **text blocks** ([[languages/01-java/01-language/07-modern-java|Modern Java]]) — triple-quoted `"""..."""`, ideal for the ASCII art the beginner dice-roller project builds:

```java
String dieFace = """
    -------
    |     |
    |  o  |
    |     |
    -------""";
```

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

Arrays nest to form **2D arrays** (arrays of arrays), the natural shape for grids, matrices, and the beginner quiz/telephone-pad projects:

```java
int[][] pad = {
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9},
};
int middle = pad[1][1];         // 5 — [row][column]
for (int[] row : pad)           // outer loop walks rows
    for (int cell : row)        // inner loop walks columns
        System.out.print(cell);
```

### Varargs — a variable number of arguments

A parameter written `Type... name` lets a method accept **zero or more** arguments of that type; inside the method it's just an array. Only one varargs parameter is allowed, and it must be **last**:

```java
static double sum(double... numbers) {   // numbers is a double[]
    double total = 0;
    for (double n : numbers) total += n;
    return total;
}

sum();               // 0.0  — zero arguments is legal
sum(1.5, 2.5);       // 4.0
sum(1, 2, 3, 4, 5);  // 15.0
```

Varargs is what lets `String.format`, `printf`, and `List.of(...)` accept any number of arguments. You can still pass an actual array where varargs is expected.

## Control flow

`if`/`else if`/`else` chains, and four loop forms:

```java
for (int i = 0; i < 5; i++) { ... }      // classic — init; condition; update
for (var x : xs) { ... }                  // enhanced for-each — read-only walk over a collection/array
while (condition) { ... }                 // check-then-run — may run zero times
do { ... } while (condition);             // run-then-check — always runs at least once
```

`break` exits the enclosing loop entirely; `continue` skips to that loop's next iteration. **Nested `if`** and **nested loops** compose the same way — an `if` inside an `if`, or a loop inside a loop (the 2D-array walk above is a nested loop). The modern `switch` is covered in [[languages/01-java/01-language/07-modern-java|Modern Java]] (it's now an expression that returns a value).

A worked example tying loops, `Random`, and `break` together — the beginner **number-guessing game**:

```java
Scanner scanner = new Scanner(System.in);
int target = new Random().nextInt(1, 101);   // 1..100
int guess, attempts = 0;
do {
    System.out.print("Guess (1-100): ");
    guess = scanner.nextInt();
    attempts++;
    if (guess > target)      System.out.println("Too high");
    else if (guess < target) System.out.println("Too low");
} while (guess != target);
System.out.println("Correct in " + attempts + " attempts!");
scanner.close();
```

## Methods

A **method** is a named, reusable block of code. Its signature is `returnType name(parameters)`; `void` means it returns nothing, any other type requires a `return` of that type. Callers pass **arguments** that bind to the **parameters**:

```java
static int add(int a, int b) {        // returns an int
    return a + b;
}
static void greet(String name) {      // returns nothing
    System.out.println("Hello " + name);
}

int sum = add(3, 4);                   // 7 — call and use the returned value
greet("Kingsley");                     // call for its side effect
```

Parameters are passed **by value** (see [Pass-by-value](#pass-by-value--always) below). **Overloading** lets several methods share a name with different parameter lists — the compiler picks by argument types ([[languages/01-java/01-language/02-oop|OOP]]). Methods that don't need an object are `static` (below); the rest are called on an instance.

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

## Worked beginner projects

These small programs combine everything above (Scanner, `printf`, `Math`, `Random`, control flow) and match the classic beginner-course project set. Projects that lean on a topic with its own file live there instead: the **calculator** (enhanced `switch`) in [[languages/01-java/01-language/07-modern-java|Modern Java]], the **slot machine** (`HashMap`) in [[languages/01-java/01-language/04-collections|Collections]], the **array-of-objects / banking-with-objects / animals / shapes** in [[languages/01-java/01-language/02-oop|OOP]], and the **audio player, hangman, countdown timer, and alarm clock** in [[languages/01-java/01-language/08-core-apis|Core APIs]].

**Temperature converter** — Scanner input, a branch, `printf` precision:

```java
try (Scanner scanner = new Scanner(System.in)) {
    System.out.print("C to F, or F to C? ");
    String mode = scanner.next();
    System.out.print("Temperature: ");
    double temp = scanner.nextDouble();
    if (mode.equalsIgnoreCase("C")) {
        System.out.printf("%.1f°C = %.1f°F%n", temp, temp * 9 / 5 + 32);
    } else {
        System.out.printf("%.1f°F = %.1f°C%n", temp, (temp - 32) * 5 / 9);
    }
}
```

Note `temp * 9 / 5` uses `double` arithmetic — with `int`s, `9 / 5` would truncate to `1` (the integer-division trap above).

**Compound interest** — `Math.pow` and money-friendly formatting (`A = P(1 + r/n)^(nt)`):

```java
double principal = 1000, rate = 0.05;
int timesPerYear = 12, years = 10;
double amount = principal * Math.pow(1 + rate / timesPerYear, timesPerYear * years);
System.out.printf("After %d years: $%,.2f%n", years, amount);   // After 10 years: $1,647.01
```

(For real money, compute with `BigDecimal`, not `double` — see the [BigDecimal](#bigdecimal-for-money--never-double) section.)

**Shopping-cart total** — accumulating in a loop over user input:

```java
try (Scanner scanner = new Scanner(System.in)) {
    double total = 0;
    String item;
    System.out.print("Item (or 'done'): ");
    while (!(item = scanner.nextLine()).equalsIgnoreCase("done")) {
        System.out.print("Price: ");
        double price = scanner.nextDouble();
        System.out.print("Quantity: ");
        int qty = scanner.nextInt();
        scanner.nextLine();                      // clear the leftover newline before the next nextLine()
        total += price * qty;
        System.out.print("Item (or 'done'): ");
    }
    System.out.printf("Total: $%.2f%n", total);
}
```

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
