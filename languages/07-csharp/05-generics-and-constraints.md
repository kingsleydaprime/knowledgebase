# Generics and Constraints

> **[Intermediate]** · Reified generics, constraints, and variance — the parts that make C#'s version genuinely better than Java's.

```csharp
public class Repository<T> where T : class, IEntity, new()
{
    private readonly List<T> _items = [];
    public T? Find(int id) => _items.FirstOrDefault(x => x.Id == id);
    public T Create() => new();            // possible because of the new() constraint
}
```

## Reified — the difference that matters

**C# generics survive to runtime.** Java erases them → [[languages/01-java/README|Java]].

```csharp
typeof(List<int>) != typeof(List<string>);     // true — distinct runtime types
var t = typeof(T);                             // works
var x = new T();                               // works, given new()
```

**Three practical consequences:**

**`List<int>` stores unboxed ints** in a contiguous `int[]`. Java's `List<Integer>` stores boxed objects on the heap. **For numeric collections this is a large, real performance gap** → [[foundations/computer-architecture/09-caches-in-depth|caches]].

**No type tokens.** Java code is full of `Class<T> clazz` parameters passed purely to recover the erased type. C# doesn't need them.

**You can overload on generic arity** — `Foo<T>` and `Foo<T,U>` coexist.

## Constraints

Without constraints, `T` is only `object` — you can barely do anything with it.

| Constraint | Means |
|---|---|
| `where T : class` | Reference type |
| `where T : struct` | Non-nullable value type |
| `where T : notnull` | Not nullable |
| `where T : IComparable<T>` | Implements the interface |
| `where T : BaseClass` | Derives from it |
| `where T : new()` | Has a public parameterless constructor |
| `where T : U` | Related to another parameter |
| `where T : unmanaged` | No references — safe for pointers/`Span` |

**Constraints are how a generic method becomes useful:**

```csharp
public static T Max<T>(T a, T b) where T : IComparable<T>
    => a.CompareTo(b) >= 0 ? a : b;
```

**Generic maths (C# 11+)** finally allowed arithmetic on `T`:

```csharp
public static T Sum<T>(IEnumerable<T> values) where T : INumber<T>
{
    T total = T.Zero;
    foreach (var v in values) total += v;
    return total;
}
```

**This closed a twenty-year gap.** Before `INumber<T>`, writing one `Sum` that worked for `int`, `double` and `decimal` was impossible without duplication or boxing — the interfaces now expose **static abstract members**, which is what makes `T.Zero` legal.

## Variance

**Where generic types can substitute for each other**, and the source of "cannot convert `List<Dog>` to `List<Animal>`".

**`out` — covariance.** `IEnumerable<out T>`: an `IEnumerable<Dog>` **is** an `IEnumerable<Animal>`, because you only ever get values *out*.

**`in` — contravariance.** `IComparer<in T>`: an `IComparer<Animal>` **can** compare dogs, because it only takes values *in*.

**Invariant by default**, and `List<T>` is invariant for a good reason:

```csharp
List<Animal> animals = new List<Dog>();   // ✗ — and thank goodness
animals.Add(new Cat());                   // would corrupt the List<Dog>
```

**Arrays are the historical mistake:** `Animal[] a = new Dog[10]` compiles, and `a[0] = new Cat()` throws at *runtime*. Array covariance is unsound and predates generics — **a real language wart, kept for compatibility**, and worth knowing because it turns a compile-time error into a runtime one.

**The mnemonic: `out` for producers, `in` for consumers.**

## Generic methods and inference

```csharp
public static void Swap<T>(ref T a, ref T b) { (a, b) = (b, a); }

int x = 1, y = 2;
Swap(ref x, ref y);           // T inferred as int — no <int> needed
```

**Inference works from arguments, not from the return type.** `var x = Parse<int>("42")` needs the explicit argument because there's nothing to infer from.

## Where generics stop

- **You cannot constrain to "has operator +"** — that's what `INumber<T>` fixed
- **You cannot inherit from a type parameter**
- **Static members are per-constructed-type**: `Cache<int>.Items` and `Cache<string>.Items` are different fields. Occasionally useful, frequently surprising

## Related
- [[languages/07-csharp/02-the-type-system|the type system]]
- [[languages/07-csharp/04-collections-and-linq|collections and LINQ]] — generics' biggest consumer
- [[foundations/programming-language-theory/04-type-systems-formally|type systems]] — variance, formally

*Source: [reference] — from the C# language reference, Aug 2026.*
