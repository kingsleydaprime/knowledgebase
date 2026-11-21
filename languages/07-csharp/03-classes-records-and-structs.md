---
id: 216fedb6-9503-4ff8-b5c3-f186240de0f9
---

# Classes, Records and Structs

Classes, records and structs are the three main ways C# lets you define your own types. A class suits things with behaviour, like a player in a game, a record suits plain data, like an order receipt, and a struct suits small values, like a point on a screen. This lesson shows how each one works and which to reach for.

## Classes
<!-- bite: 9254ab88-acc6-42e3-8bda-a6879039336a -->

Reference types, the workhorse. Standard OOP → [[programming-fundamentals/13-objects-and-classes|objects and classes]].

```csharp
public class Account
{
    private decimal _balance;
    public string Owner { get; }                       // get-only
    public decimal Balance => _balance;                // expression-bodied

    public Account(string owner, decimal opening = 0)
    {
        if (opening < 0) throw new ArgumentException("negative opening balance");
        Owner = owner; _balance = opening;
    }

    public void Deposit(decimal amount)
    {
        if (amount <= 0) throw new ArgumentOutOfRangeException(nameof(amount));
        _balance += amount;
    }
}
```

**Properties are the thing to notice.** C# has real properties, so there is no getter/setter boilerplate and no cost to starting with a field-like property and adding logic later:

```csharp
public string Name { get; set; }              // auto-property
public string Name { get; init; }             // settable only during construction
public decimal Total => Price * Quantity;     // computed, read-only
```

**`init` is the one that changed practice.** It gives you object-initialiser syntax *and* immutability, which previously required a constructor with ten parameters.

**Primary constructors** (C# 12) cut the ceremony further:

```csharp
public class Account(string owner)
{
    public string Owner { get; } = owner;
}
```

## Records — use these for data
<!-- bite: 046e455b-4836-4d17-86db-5b17e5e48b25 -->

**A record is a class (or struct) with value-based equality generated for you.**

```csharp
public record Point(int X, int Y);
```

That single line gives you: a constructor, `init`-only properties, **`Equals`/`GetHashCode` comparing values**, `ToString()` printing the contents, deconstruction, and `with` expressions.

```csharp
var a = new Point(1, 2);
var b = new Point(1, 2);
a == b                      // true  ← value equality, not reference
var c = a with { Y = 99 };  // non-destructive mutation
Console.WriteLine(a);       // Point { X = 1, Y = 2 }
```

**Compare the class equivalent**: ~40 lines of `Equals`, `GetHashCode`, `ToString` and a copy constructor, all of which drift when a field is added.

**Use a record when the type is data** — DTOs, API models, domain values, events, configuration. **Use a class when the type has behaviour and identity** — a service, a controller, an entity with a database id.

**The equality point matters more than it looks:** two `Point` classes with the same coordinates are *different objects*; two `Point` records are *equal*. For value-like concepts, reference equality is almost always the wrong default, and getting it right by hand is exactly the `__eq__`/`__hash__` contract people forget → [[languages/06-python/05-classes-and-the-object-model|Python note 05]].

## Structs
<!-- bite: 858b10dc-b141-4f78-a838-dbb887bda9cc -->

Value types → [[languages/07-csharp/02-the-type-system|note 02]]. Copied on assignment, stored inline.

```csharp
public readonly record struct Vector2(float X, float Y)
{
    public float Length => MathF.Sqrt(X * X + Y * Y);
    public static Vector2 operator +(Vector2 a, Vector2 b) => new(a.X + b.X, a.Y + b.Y);
}
```

**`readonly record struct` is the modern default for small value types** — value semantics, value equality, no defensive copies, and no heap allocation.

**The rules:**
- **Keep them small** — every assignment and every argument pass copies the whole thing
- **Make them `readonly`.** A mutable struct is a genuine footgun: `list[0].X = 5` on a `List<MutableStruct>` mutates a *copy* and silently does nothing
- **Watch for boxing** — passing one as `object` or a non-generic interface allocates
- **A struct always has a parameterless default** (`default(T)`, all fields zeroed) that you cannot prevent

**This is why game code is full of structs**: an array of 10,000 `Vector3` structs is one contiguous 120 KB block; the class version is 10,000 heap objects with terrible locality → [[game-development/02-engines-and-the-game-loop|ECS]].

## Interfaces
<!-- bite: bf1270b8-db44-48ef-9749-c7f9cdc1f6c8 -->

```csharp
public interface IRepository<T>
{
    Task<T?> GetAsync(int id);
    Task SaveAsync(T item);

    async Task<T> GetRequiredAsync(int id)          // default implementation (C# 8+)
        => await GetAsync(id) ?? throw new KeyNotFoundException();
}
```

**Interfaces are how you get substitutability**, and C# leans on them heavily — dependency injection is built into ASP.NET Core around them → [[concepts/interview/02-patterns-code-quality-and-review|why Singleton is global state]].

**Prefer interfaces to abstract classes** unless you genuinely need shared state. A type can implement many interfaces and inherit one class.

## Inheritance, briefly
<!-- bite: 1f5d7e61-c675-4e71-9eac-59668876da86 -->

C# has single inheritance, `virtual`/`override`, and `sealed`.

**The modern consensus applies here as everywhere: prefer composition** → [[programming-fundamentals/13-objects-and-classes|note 13]]. Deep hierarchies age badly, and C#'s records, interfaces with default implementations, and generics cover most of what inheritance used to be reached for.

**`sealed` is worth using deliberately** — it documents intent and lets the JIT devirtualise calls, which is a small real performance win.

## Which to reach for
<!-- bite: f264e312-c26b-462d-9fb0-43114016462b -->

| The type is… | Use |
|---|---|
| Data, immutable, compared by value | **`record`** |
| Small value, performance-sensitive | **`readonly record struct`** |
| Behaviour, identity, injected | **`class`** |
| A contract | **`interface`** |

## Related
<!-- bite: 3476fac0-faba-4d90-9f55-ad208735ad2f -->
- [[languages/07-csharp/02-the-type-system|the type system]] — value vs reference
- [[languages/07-csharp/10-pattern-matching-and-modern-csharp|pattern matching]] — records exist partly to be matched on
- [[programming-fundamentals/13-objects-and-classes|objects and classes]]

## About this lesson
<!-- bite: 3d836f0e-e4fc-4f85-aa4d-f134e59e6008 -->

**Level:** Beginner → Intermediate. **Covers:** Three ways to define a type, and the modern C# defaults that changed which one you should reach for.

*Source: [reference] — from the C# language reference, Aug 2026.*
