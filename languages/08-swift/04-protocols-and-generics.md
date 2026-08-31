# Protocols and Generics

**[Intermediate → Advanced]** — Swift's abstraction mechanism, and why it's used instead of inheritance.

## Protocols

A protocol is a set of requirements a type can satisfy — an interface, with more reach:

```swift
protocol Identifiable {
    var id: String { get }
}

protocol Fetchable {
    associatedtype Item                        // a generic hole
    func fetch(id: String) async throws -> Item
}
```

**Unlike a Java interface, protocols apply to structs and enums too**, not just classes. That's what makes "protocol-oriented programming" possible — you get polymorphism without giving up value semantics → [[languages/08-swift/02-values-references-and-optionals|value types]].

## Protocol extensions — the distinctive feature

You can provide **default implementations** on the protocol itself:

```swift
protocol Greeter {
    var name: String { get }
    func greet() -> String
}

extension Greeter {
    func greet() -> String { "Hello, \(name)" }   // free for every conformer
}

struct Person: Greeter { let name: String }        // gets greet() automatically
```

**This is Swift's answer to base classes**, and it's better in one specific way: **a type can conform to many protocols, but inherit from only one class.** So behaviour composes instead of forming a hierarchy.

**The gotcha:** if a method is declared *only* in the extension and not in the protocol, dispatch is **static** — the concrete type's override won't be called through a protocol reference. **Declare a method in the protocol if you want conformers to be able to override it meaningfully.** This trips up people who expect Java's dynamic dispatch.

## `some` and `any` — the distinction to learn

```swift
func makeView() -> some View { Text("hi") }   // ONE specific type, hidden. Fast
func process(_ x: any Fetchable) { }          // ANY type. Existential — boxed, slower
```

| | `some` (opaque) | `any` (existential) |
|---|---|---|
| Type | One concrete type, name hidden | Any conforming type |
| Dispatch | **Static — can be inlined** | Dynamic, through a box |
| Cost | **Zero** | Allocation + indirection |
| Can hold mixed types? | No | Yes |

**Prefer `some`.** It gives you abstraction with no runtime cost, which is why SwiftUI's `body` returns `some View`. Reach for `any` only when you genuinely need a heterogeneous collection.

**Swift 5.6 made `any` explicit** precisely because the cost was invisible before — you'd write `[Fetchable]` and silently get boxing.

## Generics

```swift
func firstMatch<T: Equatable>(_ items: [T], equal to: T) -> T? {
    items.first { $0 == to }
}

struct Cache<Key: Hashable, Value> {
    private var storage: [Key: Value] = [:]
}
```

**Swift generics are monomorphised where possible** — the compiler generates specialised code per type, so there's no boxing and no dynamic dispatch. **Like Rust and C++ templates, not like Java's erasure** → [[languages/03-rust/10-generics-and-trait-bounds|Rust generics]].

**`where` clauses** express constraints that don't fit in the angle brackets:

```swift
extension Array where Element: Numeric {
    var total: Element { reduce(0, +) }
}
```

**This pattern — extending a generic type only when its elements satisfy something — is extremely idiomatic Swift**, and it's how the standard library is built.

## Associated types

The generic hole in a protocol:

```swift
protocol Repository {
    associatedtype Model
    func get(id: String) async throws -> Model
}

struct UserRepo: Repository {
    func get(id: String) async throws -> User { ... }   // Model = User, inferred
}
```

**This is what makes `Collection` and `Sequence` work.** It also makes protocols with associated types harder to use as existentials — the historic "protocol can only be used as a generic constraint" error. **Swift 5.7's primary associated types (`any Repository<User>`) largely fixed this.**

## Result builders

The mechanism behind SwiftUI's syntax:

```swift
VStack {
    Text("a")        // no commas, no return — this is a result builder
    Text("b")
}
```

`@resultBuilder` transforms a block of statements into a single value. **Worth knowing it exists** so SwiftUI stops looking like magic; writing your own is rarely necessary.

## Key insight

**Swift replaced inheritance with protocols plus extensions**, which composes rather than forming a hierarchy — and because protocols apply to structs, you get polymorphism without giving up value semantics. **The `some` vs `any` distinction is where the performance lives**: `some` is abstraction the compiler erases entirely, `any` is abstraction you pay for at runtime.

## Related
- [[languages/08-swift/02-values-references-and-optionals|value types]] — what protocols let you keep
- [[languages/03-rust/09-traits|Rust traits]] — the closest analogue
- [[languages/01-java/README|Java interfaces]] — the contrast
- [[mobile/frameworks/ios/README|SwiftUI]] — result builders in practice
