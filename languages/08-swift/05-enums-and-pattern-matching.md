# Enums and Pattern Matching

**[Intermediate]** — Swift's enums carry data, and that changes how you model everything.

## Not the enums you know

In C or Java an enum is a named integer. **In Swift an enum is a sum type — each case can carry different data:**

```swift
enum LoadState {
    case idle
    case loading
    case success([Item])                    // carries a list
    case failure(Error, retryable: Bool)    // carries two values
}
```

**This is the most useful feature in the language for application code**, because it makes invalid states unrepresentable:

```swift
// BAD — 16 combinations, most meaningless
var isLoading = false
var error: Error?
var items: [Item]?

// GOOD — exactly 4 states, all valid
var state: LoadState
```

With booleans you will eventually render a spinner over an error over stale data, because nothing stopped you. **With an enum the compiler stops you** → [[mobile/05-state-and-architecture|state modelling]].

## `switch` must be exhaustive

```swift
switch state {
case .idle:                       showPlaceholder()
case .loading:                    showSpinner()
case .success(let items):         show(items)
case .failure(let e, let retry):  showError(e, canRetry: retry)
}
```

**No `default` needed — and that's the point.** Add a new case to the enum and **every `switch` that doesn't handle it fails to compile.** The compiler hands you the list of places to update.

> **Avoid `default:` in switches over your own enums.** It silences exactly the error you want.

## Pattern matching goes further than you'd expect

```swift
switch point {
case (0, 0):                      "origin"
case (let x, 0):                  "on x-axis at \(x)"
case (let x, let y) where x == y: "diagonal"
case (-2...2, -2...2):            "near origin"        // ranges
default:                          "elsewhere"
}
```

```swift
if case .success(let items) = state, !items.isEmpty { }   // match one case inline
for case .success(let items) in states { }                // filter while iterating
guard case .failure(let e, _) = state else { return }
```

**`if case` and `guard case` are heavily used** and worth being fluent in — they're how you extract one case without a full `switch`.

## Recursive enums

```swift
indirect enum Expr {
    case number(Int)
    case add(Expr, Expr)
    case multiply(Expr, Expr)
}

func eval(_ e: Expr) -> Int {
    switch e {
    case .number(let n):      n
    case .add(let a, let b):  eval(a) + eval(b)
    case .multiply(let a, let b): eval(a) * eval(b)
    }
}
```

**`indirect` adds the box needed for recursion.** This is how you'd write an AST → [[foundations/compilers/04-asts-and-semantic-analysis|ASTs]].

## Raw values and `CaseIterable`

```swift
enum Status: String, Codable, CaseIterable {
    case active, suspended, closed
}

Status.allCases                       // [.active, .suspended, .closed]
Status(rawValue: "active")            // Optional(.active) — failable, correctly
```

**`String`-backed enums conforming to `Codable` are free JSON parsing** with validation — an unknown value returns nil rather than producing a broken object.

**A real-world caution:** if the server can add new enum values, a strict enum **fails to decode** and breaks old app versions. **Add an `unknown` case with a custom decoder**, or decode as `String` and map — this is a genuine production issue in mobile, where old versions live for years → [[mobile/08-networking-on-mobile|API compatibility]].

## `Result`, and where it fits

```swift
enum Result<Success, Failure: Error> {
    case success(Success)
    case failure(Failure)
}
```

Just an enum, in the standard library. **Mostly superseded by `async`/`throws`** for new code, but still common in callback-based APIs and for storing an outcome to handle later → [[languages/08-swift/06-error-handling|error handling]].

## Enums with methods

Enums can have computed properties and methods, which keeps behaviour next to the data:

```swift
extension LoadState {
    var isTerminal: Bool {
        switch self {
        case .success, .failure: true
        case .idle, .loading:    false
        }
    }
}
```

## Key insight

**Swift enums are algebraic data types, and using them properly is the single biggest quality improvement available in application code.** Any time you find yourself with several booleans or optionals that only make sense in certain combinations, that's an enum — and converting it moves a class of bug from runtime to compile time.

## Related
- [[languages/08-swift/06-error-handling|error handling]] — `throws` and `Result`
- [[languages/03-rust/06-structs-enums-and-pattern-matching|Rust's enums]] — the same idea, same power
- [[mobile/05-state-and-architecture|state modelling]] — where this pays off most
- [[foundations/programming-language-theory/04-type-systems-formally|type systems]] — sum types formally
