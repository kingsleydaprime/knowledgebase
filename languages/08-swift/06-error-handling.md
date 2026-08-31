# Error Handling

**[Intermediate]** — typed throws, `try` in its three forms, and the rule about which to use.

## `throws` and `try`

```swift
enum NetworkError: Error {
    case notFound
    case serverError(code: Int)
}

func fetch(id: String) throws -> User {
    guard let u = cache[id] else { throw NetworkError.notFound }
    return u
}

do {
    let user = try fetch(id: "1")
} catch NetworkError.notFound {
    showEmpty()
} catch let NetworkError.serverError(code) where code >= 500 {
    showRetry()
} catch {
    log(error)                     // `error` is bound implicitly
}
```

**`try` is required at every call site**, which makes fallibility visible when reading code — unlike Java's unchecked exceptions or Go's easily-ignored second return.

**Errors are just values** — anything conforming to `Error`, usually an enum → [[languages/08-swift/05-enums-and-pattern-matching|enums]].

## The three `try`s

```swift
let a = try fetch(id: "1")      // propagate — the caller must handle it
let b = try? fetch(id: "1")     // User? — error DISCARDED
let c = try! fetch(id: "1")     // CRASH on error
```

**`try?` is the one to be careful with.** It converts a rich error into `nil`, which is how you get a bug report saying "it just doesn't work" with no diagnostics.

**Use `try?` only when you genuinely don't care why it failed** — an optional cache read. **Never for a network call whose failure you'd want to see.**

**`try!` is for genuine impossibilities** — parsing a regex literal you wrote, loading a bundled resource. Same discipline as force-unwrapping.

## Typed throws (Swift 6)

Historically `throws` was untyped — a function could throw anything, so `catch` was always partly guesswork. Swift 6 added:

```swift
func fetch(id: String) throws(NetworkError) -> User { ... }
```

Now the compiler knows exactly what can be thrown, and **`catch` can be exhaustive**. **Use it where the error set is genuinely closed and meaningful to callers.** For library boundaries and anything that wraps other errors, untyped `throws` is still right — a typed throw is a public API commitment you have to keep.

## `defer`

Runs when scope exits, however it exits:

```swift
func process() throws {
    let handle = open()
    defer { handle.close() }        // runs on return, on throw, on early exit
    try doWork(handle)
}
```

**Cleanup next to acquisition**, which is the property that makes it reliable. Multiple `defer`s run in reverse order.

## What isn't `throws`

**Programmer errors don't use error handling** — they crash, deliberately:

- Array index out of range
- Force-unwrapping nil
- Integer overflow (`&+` opts into wrapping)
- `assert` / `precondition` / `fatalError`

**This is a deliberate design line:** `throws` is for *expected* failures — the network is down, the file is missing, the input is invalid. **Bugs crash**, because continuing with a broken invariant is worse than stopping.

**`assert` is debug-only; `precondition` runs in release.** Use `precondition` for invariants that must hold in production.

## Errors users will see

```swift
enum AppError: LocalizedError {
    case offline
    var errorDescription: String? {
        switch self {
        case .offline: String(localized: "You appear to be offline.")
        }
    }
}
```

**Two distinct audiences, and conflating them is the common mistake:** the *user* needs "what happened and what can I do", and the *developer* needs the underlying cause. **Log the technical detail; show the human one** — and make sure something actionable reaches the user rather than a silent failure → [[mobile/05-state-and-architecture|error states]].

## Async errors

`async throws` composes naturally:

```swift
func load() async throws -> [Item] {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode([Item].self, from: data)
}
```

**Cancellation is an error too** — `CancellationError` is thrown when a task is cancelled, so `try await` propagates it. **Don't swallow it with `try?`**, or you'll do work for a screen the user has already left → [[languages/08-swift/10-concurrency-and-actors|concurrency]].

## Key insight

**Swift makes fallibility visible at every call site** — `try` is required, so you can't accidentally ignore an error the way you can in Go, and you can't be surprised by one the way you can in Java. **The discipline that remains is choosing between the three `try`s honestly**, and `try?` on anything whose failure you'd want to debug is the one that costs you later.

## Related
- [[languages/08-swift/05-enums-and-pattern-matching|enums]] — how errors are modelled
- [[languages/08-swift/10-concurrency-and-actors|concurrency]] — async errors and cancellation
- [[languages/03-rust/07-option-and-result|Rust's Result]] — the comparison
- [[languages/02-go/README|Go's errors-as-values]] — the other approach
