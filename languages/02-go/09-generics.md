# Generics

**[Intermediate]** — Type parameters, constraints, and the honest answer to when you should actually use them.

## Why they arrived late

Go shipped without generics in 2009 and got them in **1.18 (March 2022)** — thirteen years of the single most-requested feature being refused. The team's position was that they hadn't found a design worth the complexity cost, and they'd rather have no generics than bad ones.

The result of that wait is visible in the design: type parameters are deliberately less powerful than Java's or Rust's. No variance, no specialisation, no higher-kinded types, no operator constraints beyond a fixed set.

## Syntax

```go
func Map[T, U any](in []T, f func(T) U) []U {
    out := make([]U, 0, len(in))
    for _, v := range in { out = append(out, f(v)) }
    return out
}

lengths := Map(names, func(s string) int { return len(s) })  // T, U inferred
lengths := Map[string, int](names, func(s string) int { ... })  // explicit
```

Type parameters go in square brackets before the value parameters. Inference usually works from the arguments; you only annotate when it can't.

## Constraints

A constraint is an interface used as a type bound:

```go
type Number interface {
    ~int | ~int8 | ~int16 | ~int32 | ~int64 | ~float32 | ~float64
}

func Sum[T Number](nums []T) T {
    var total T          // zero value of whatever T is
    for _, n := range nums { total += n }
    return total
}
```

Two new things in that interface:

**`|` is a union** — "any of these types". An interface with type elements can only be used as a constraint, never as a variable type.

**`~` means "with this underlying type"** — so `~int` matches `int` *and* `type UserID int`. Without the tilde, your carefully-distinct named types from [[languages/02-go/02-language-fundamentals|the type system]] wouldn't satisfy the constraint, which would make the feature much less useful.

Built-in constraints:

```go
any                 // no constraint (alias for interface{})
comparable          // supports == and != ; required for map keys

// from golang.org/x/exp/constraints
constraints.Ordered    // supports < <= > >=  — numbers and strings
constraints.Integer
constraints.Float
```

A constraint can require **methods and types together**:

```go
type Stringish interface {
    ~string
    Len() int
}
```

## Generic types

```go
type Stack[T any] struct{ items []T }

func (s *Stack[T]) Push(v T) { s.items = append(s.items, v) }

func (s *Stack[T]) Pop() (T, bool) {
    var zero T                       // how you produce a zero value of T
    if len(s.items) == 0 { return zero, false }
    v := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return v, true
}

s := &Stack[int]{}
```

`var zero T` is the idiom for "the zero value of the type parameter" — you can't write `nil` or `0`, because you don't know which it is.

**Methods cannot introduce new type parameters.** `func (s *Stack[T]) MapTo[U any](...)` doesn't compile. This is the limitation you'll hit first, and the workaround is a package-level function taking the receiver as an argument. It's why `Map` above is a function rather than a method — and why Go has no fluent `.map().filter().reduce()` chain.

## What the standard library got

Generics made these possible, and they're the main day-to-day benefit:

```go
import ("slices"; "maps")     // Go 1.21+

slices.Contains(s, v)
slices.Index(s, v)
slices.Sort(s)                          // for constraints.Ordered
slices.SortFunc(s, func(a, b T) int)
slices.Max(s) / slices.Min(s)
slices.Reverse(s)
slices.Clone(s)                         // the fix for the aliasing trap
slices.Equal(a, b)
slices.BinarySearch(s, v)

maps.Keys(m) / maps.Values(m)           // iterators in 1.23+
maps.Clone(m)

min(a, b) / max(a, b)                   // builtins since 1.21
cmp.Or(a, b, c)                         // first non-zero value
```

`slices.SortFunc` returning an `int` comparator (negative/zero/positive) rather than a `bool` less-function is a small but real improvement over `sort.Slice`, and it's the one to reach for now.

## When to actually use them

The community norm, which is stricter than in most languages:

**Use generics when:**
- You're writing a **container** — a stack, set, cache, queue — that genuinely works for any element type
- You'd otherwise write the **same function three times** for `int`, `float64`, `string`
- You'd otherwise use `any` and type-assert, which moves a compile-time error to runtime

**Don't use generics when:**
- **An interface expresses it better.** If you only need behaviour, not the concrete type, take an interface. `func Write(w io.Writer)` beats `func Write[T Writer](w T)` every time — this is the most common misuse.
- You have **one** implementation. Write it concretely; generalise when the second appears.
- It makes the signature unreadable. Two type parameters and a constraint interface to save twenty lines of duplication is a bad trade in a language that values being readable at 3am.

> The Go proverb still applies: *"A little copying is better than a little dependency."* Duplication is cheaper here than in most languages, and generics don't change that.

## The performance note

Go implements generics with **GC shape stinting** — a hybrid of monomorphisation and boxing. Types sharing a memory layout (all pointer types, say) share one generated function, with type info passed in a hidden dictionary.

The practical consequence: generic code is usually **not faster** than the `interface{}` version, and can be marginally slower than a hand-written concrete one. Generics in Go are for **type safety and avoiding duplication**, not for performance. If you're reaching for them to eliminate boxing the way you would in Rust or C++, you'll be disappointed.

---

## Related
- [[languages/02-go/04-methods-and-interfaces|Methods and Interfaces]] — usually the better tool
- [[languages/02-go/03-composite-types|Composite Types]] — what `slices` and `maps` operate on
- [[languages/01-java/01-language/03-generics|Java: Generics]] — erasure, wildcards, and variance, for contrast
- [[languages/02-go/README|Go course map]]
