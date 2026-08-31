# Values, References and Optionals

**[Beginner → Intermediate]** — the two ideas that define Swift, and the source of most of its behaviour.

## Value types vs reference types

```swift
struct Point { var x: Int }          // VALUE type — copied
class  Node  { var x: Int = 0 }      // REFERENCE type — shared
```

```swift
var a = Point(x: 1)
var b = a          // a COPY
b.x = 99
print(a.x)         // 1  ← unchanged

let c = Node()
let d = c          // the SAME object
d.x = 99
print(c.x)         // 99 ← changed
```

**Swift's default is `struct`, and that's the significant choice.** Most languages default to reference semantics; Swift pushes you toward values, and the whole standard library follows — **`Array`, `Dictionary`, `Set` and `String` are all structs.**

```swift
var list1 = [1, 2, 3]
var list2 = list1     // a copy, conceptually
list2.append(4)
print(list1)          // [1, 2, 3]  ← unchanged. Surprises Java and Python developers
```

**Why this matters:** value semantics eliminate a whole class of bugs — nobody else can mutate your array while you're iterating it, and there's no aliasing to reason about. **This is one of the strongest reasons to like Swift.**

**Copy-on-write** makes it affordable: the copy is lazy, and the actual duplication happens only when one side is mutated. **So passing a large array is cheap** — you don't need to avoid it for performance.

**When to use a class:** you need identity (this *specific* object), you need inheritance, you're interoperating with Objective-C, or the thing genuinely is shared mutable state (a view model, a cache). **Otherwise use a struct.**

## `let` and `var`, and the mutation rule

```swift
let x = 5           // constant
var y = 5           // variable

let p = Point(x: 1)
p.x = 2             // ❌ COMPILE ERROR — the struct is a value, and it's constant

let n = Node()
n.x = 2             // ✅ fine — the reference is constant, the object isn't
```

**`let` on a struct makes the whole value immutable; `let` on a class makes only the reference immutable.** That difference catches everyone once.

**Prefer `let`.** The compiler warns when a `var` is never mutated, and the ecosystem treats mutability as something to justify.

## Optionals — the other defining idea

**There is no `null`.** A value that might be absent has a *different type*:

```swift
var name: String  = "Ada"     // ALWAYS a String
var maybe: String? = nil      // String? — a String, or nothing
```

`String?` is genuinely a distinct type. **You cannot use it as a `String` without handling the nil case**, and the compiler enforces that. This eliminates null-pointer exceptions as a category.

**Unwrapping, in order of preference:**

```swift
// 1. if let / guard let — the normal way
if let name { print(name.count) }              // shorthand, Swift 5.7+

guard let name else { return }                 // early exit; `name` is non-optional after
print(name.count)

// 2. Optional chaining — nil propagates
let n = user?.profile?.name?.count             // Int?

// 3. Nil-coalescing — supply a default
let display = name ?? "Anonymous"

// 4. Force unwrap — CRASHES if nil
let n2 = name!                                 // ← justify every use
```

**`guard let` is the idiomatic Swift shape.** It handles the failure case first and leaves the happy path unindented, which is why Swift code has notably less nesting than equivalent code elsewhere.

## Force unwrapping

`!` says "I guarantee this isn't nil." **If you're wrong, the app crashes.**

**Legitimate uses:** a resource you ship in the bundle, a value you just assigned, `@IBOutlet`s. **Everything else is a crash waiting for a user.**

**The worst offender is `try!` and implicitly unwrapped optionals (`String!`)** — they push the failure further from its cause. **A crash on force-unwrap is genuinely better than a silent wrong value**, which is the design intent — but a `guard` with a real error path is better than both.

## Key insight

**Value semantics and optionals are the same idea applied twice: make the dangerous thing impossible to do accidentally.** Structs remove aliasing bugs by copying; optionals remove null-pointer bugs by making absence a type. In both cases the escape hatch exists (`class`, `!`) and is deliberately noisy — **you can do the unsafe thing, but never by accident.**

## Related
- [[languages/08-swift/03-memory-and-arc|memory and ARC]] — what reference types cost
- [[languages/08-swift/06-error-handling|error handling]] — the other absence-shaped problem
- [[languages/03-rust/03-ownership|Rust's ownership]] — a stricter answer to the same question
