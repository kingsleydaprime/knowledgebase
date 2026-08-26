# The Type System

> **[Beginner → Intermediate]** · Value types vs reference types, and nullable reference types — the two things that cause most C# surprises.

## Value types and reference types

**The distinction Java doesn't really have, and it matters constantly in C#.**

**Value types** (`struct`, `int`, `bool`, `double`, `enum`, and every primitive) hold their data **directly**. Assignment **copies**.

**Reference types** (`class`, `interface`, `string`, arrays, delegates) hold a **reference**. Assignment copies the reference — both names point at one object.

```csharp
struct Point { public int X, Y; }
class  Box   { public int X, Y; }

var p1 = new Point { X = 1 }; var p2 = p1; p2.X = 99;
// p1.X == 1   ← copied

var b1 = new Box { X = 1 };   var b2 = b1; b2.X = 99;
// b1.X == 99  ← shared
```

**This is the same names-and-objects distinction as [[foundations/programming-fundamentals/05-variables-and-types|programming fundamentals]]** — except C# lets *you* choose which behaviour a type has.

**Where value types live:** on the stack when local, **inline inside their container** when a field. That's the performance argument — an array of 1,000 structs is one contiguous block; an array of 1,000 class instances is 1,000 scattered heap objects plus a pointer array → [[foundations/computer-architecture/09-caches-in-depth|caches]]. **This is why game code uses structs for vectors and particles.**

**When to use a struct:** small (roughly ≤16 bytes), logically a single value, immutable, short-lived. `Vector3`, `Complex`, `DateTime`.

**When not to:** anything large (copying costs), anything mutable (copies diverge confusingly), anything with identity.

**Boxing** is the trap: assigning a value type to `object` or a non-generic interface **allocates a heap box and copies into it**. In a hot loop this is invisible allocation pressure and a real cause of GC spikes in Unity → [[languages/07-csharp/08-memory-gc-and-spans|note 08]].

## Nullable reference types

**C#'s best recent feature, and it's opt-in.** With `<Nullable>enable</Nullable>`:

```csharp
string  name;    // NOT nullable — the compiler warns if it could be null
string? maybe;   // explicitly nullable
```

The compiler performs **flow analysis** and warns when you dereference something that might be null:

```csharp
void Greet(string? name)
{
    Console.WriteLine(name.Length);      // ⚠ warning: may be null
    if (name is null) return;
    Console.WriteLine(name.Length);      // ✓ narrowed — no warning
}
```

**Three things to know:**

**It's warnings, not errors, and it's erased at runtime.** Nothing stops null arriving from an un-annotated library, from reflection, or from deserialisation. **`<WarningsAsErrors>Nullable</WarningsAsErrors>` is how you make it bite.**

**`!` is the null-forgiving operator** — `name!.Length` tells the compiler "trust me". **Every use is a claim you're making**; they should be rare and justified, exactly like `as` casts in TypeScript → [[frontend/interview/02-javascript-and-typescript|TS]].

**Adopt incrementally.** Turning it on in a large legacy codebase produces thousands of warnings, nobody triages them, and it gets switched off — the same failure as strict mypy → [[languages/06-python/08-typing-and-type-hints|typing]]. Enable per-file with `#nullable enable`, or per-project as you touch things.

**The null-handling operators worth knowing:**

```csharp
var len   = name?.Length;              // null-conditional → int?
var value = name ?? "default";         // null-coalescing
name    ??= "default";                 // null-coalescing assignment
```

## `var`, and what it isn't

`var` is **type inference, not dynamic typing.** The type is fixed at compile time; `var` just saves you writing it.

```csharp
var list = new List<string>();     // List<string>, statically
list.Add(42);                      // compile error
```

**`dynamic` is the actually-dynamic one** — it defers binding to runtime, and it's rare and usually a smell.

## Generics — and why they're better than Java's

C# generics are **reified**: the type argument survives to runtime.

```csharp
var list = new List<int>();
typeof(List<int>) != typeof(List<string>);      // true — distinct runtime types
```

**Java erases generics; C# doesn't.** The consequences:

- **`List<int>` stores unboxed ints** in a contiguous array. Java's `List<Integer>` stores boxed objects — a real performance difference
- You can do `typeof(T)`, `new T()` (with a constraint), and overload on generic arity
- No need for the `Class<T>` token-passing that Java code is full of

**This is a genuine and underappreciated advantage** → [[languages/01-java/README|Java]] · [[languages/07-csharp/05-generics-and-constraints|note 05]].

## Related
- [[languages/07-csharp/03-classes-records-and-structs|classes, records and structs]]
- [[languages/07-csharp/08-memory-gc-and-spans|memory, GC and spans]] — where boxing bites
- [[foundations/programming-fundamentals/05-variables-and-types|variables and types]] — the language-agnostic version

*Source: [reference] — from the C# language reference, Aug 2026.*
