# Pattern Matching and Modern C#

> **[Intermediate]** · The features that make current C# feel like a different language from the one people remember.

## Pattern matching

C# has accumulated a genuinely powerful pattern-matching system, and it changed idiomatic style substantially.

```csharp
// type pattern + declaration
if (shape is Circle c) return Math.PI * c.Radius * c.Radius;

// switch EXPRESSION — returns a value, exhaustiveness-checked
var area = shape switch
{
    Circle c            => Math.PI * c.Radius * c.Radius,
    Rectangle r         => r.Width * r.Height,
    Triangle { Base: var b, Height: var h } => 0.5 * b * h,
    null                => throw new ArgumentNullException(nameof(shape)),
    _                   => throw new NotSupportedException($"{shape.GetType()}")
};

// property patterns
var discount = order switch
{
    { Customer.IsVip: true, Total: > 1000 } => 0.20m,
    { Total: > 500 }                        => 0.10m,
    _                                       => 0m
};

// relational and logical patterns
var band = temp switch
{
    < 0        => "freezing",
    >= 0 and < 15 => "cold",
    >= 15 and < 25 => "mild",
    _          => "hot"
};

// list patterns (C# 11)
var describe = numbers switch
{
    []             => "empty",
    [var single]   => $"one: {single}",
    [var first, .., var last] => $"{first} … {last}",
};
```

**Why this matters beyond brevity:** a `switch` **expression** must produce a value on every path, so the compiler warns when a case is unhandled. **It moves a class of bug from runtime to compile time**, and it composes — patterns nest arbitrarily.

**Records exist partly to be matched on** → [[languages/07-csharp/03-classes-records-and-structs|note 03]]. `record` + `switch` expression is C#'s answer to algebraic data types, and it's the same shape as [[languages/03-rust/README|Rust's `match`]] — with the notable gap that **C# has no closed union type**, so exhaustiveness over a type hierarchy can't be fully proven and you still need a `_` arm.

## The syntax that removed the ceremony

**Top-level statements** — no class, no `Main`:
```csharp
Console.WriteLine("Hello");
```

**File-scoped namespaces** — one less level of indentation across every file:
```csharp
namespace MyApp.Services;
```

**Global usings** — declare once, available everywhere:
```csharp
global using System.Text.Json;
```
With `<ImplicitUsings>enable</ImplicitUsings>`, the common namespaces are already there.

**Target-typed `new`:**
```csharp
Dictionary<string, List<int>> map = new();      // type not repeated
```

**Collection expressions** (C# 12):
```csharp
int[] a = [1, 2, 3];
List<int> b = [..a, 4, 5];          // spread
```

**Raw string literals** — no escaping, which is transformative for JSON and SQL:
```csharp
var json = """
    { "name": "Ada", "path": "C:\Users" }
    """;
```

**Primary constructors** (C# 12):
```csharp
public class Service(ILogger logger, IRepository repo)
{
    public void Run() => logger.LogInformation("{Count}", repo.Count);
}
```

**That last one deletes the field-declare-assign triplet** that made C# constructors verbose for twenty years.

## Deconstruction and tuples

```csharp
var (name, age) = person;                        // deconstruct a record
(int min, int max) MinMax(int[] xs) => (xs.Min(), xs.Max());
var (lo, hi) = MinMax(numbers);
(a, b) = (b, a);                                 // swap
```

**Value tuples are structs**, so they don't allocate — genuinely useful for multiple return values without defining a type.

**Use them for local, private returns.** For anything crossing a public API boundary, a `record` gives you names that survive and can gain members later.

## What this adds up to

**C# written in 2026 looks substantially different from C# written in 2015.** The verbosity that gave it a reputation — `public class Program { public static void Main(string[] args) { ... } }`, explicit types everywhere, hand-written equality — is mostly gone.

**The practical warning:** most C# tutorials, Stack Overflow answers and existing codebases predate these features. You'll read old style constantly, and Unity's older language versions won't accept much of this → [[languages/07-csharp/01-why-csharp-and-the-toolchain|note 01]].

## Related
- [[languages/07-csharp/03-classes-records-and-structs|records]] — what you match on
- [[languages/03-rust/README|Rust]] — where the pattern matching came from
- [[foundations/programming-language-theory/04-type-systems-formally|type systems]] — exhaustiveness

*Source: [reference] — from the C# language reference, Aug 2026.*
