---
id: 5345ba83-cce7-482a-acf3-53d1bf629972
---

# Concurrency and Actors

**[Advanced]** — structured concurrency, and Swift 6's data-race safety.

## async/await
<!-- bite: 85be550d-a37f-455f-b9af-511f93414c44 -->

```swift
func loadProfile(id: String) async throws -> Profile {
    let user = try await api.user(id: id)
    let posts = try await api.posts(for: id)     // sequential — waits for user first
    return Profile(user: user, posts: posts)
}
```

**`await` is a suspension point** — the thread is released to do other work, and your function resumes later, possibly on a different thread. **It is not blocking.**

## Running things in parallel
<!-- bite: ed66f9ed-ab68-4e27-ac5c-a114f88f7940 -->

The code above is sequential. To overlap independent work:

```swift
async let user = api.user(id: id)          // starts immediately
async let posts = api.posts(for: id)       // starts immediately
return Profile(user: try await user, posts: try await posts)
```

Or for a dynamic number:

```swift
let results = try await withThrowingTaskGroup(of: Item.self) { group in
    for id in ids { group.addTask { try await api.item(id) } }
    return try await group.reduce(into: []) { $0.append($1) }
}
```

**`async let` for a fixed known set; a task group for a variable number.** Using sequential `await`s where the work is independent is the most common performance mistake here.

## Structured concurrency
<!-- bite: 155f734d-e8b8-4729-928f-2ba62a8abdbe -->

**Child tasks cannot outlive their parent.** When the scope exits — normally, by throwing, or by cancellation — **all children are cancelled and awaited.**

That's the guarantee that makes this different from raw threads or unstructured callbacks: **no orphaned work, no leaked tasks.** It's the same insight as `defer` and RAII, applied to concurrency.

## Cancellation is cooperative
<!-- bite: 69b44164-0c99-47d8-a7b1-27984d4bbcfc -->

```swift
for item in items {
    try Task.checkCancellation()          // throws CancellationError
    await process(item)
}
```

**Nothing forcibly stops your task.** You must check. Most `async` standard-library functions check for you, so an `await`-heavy loop is usually fine — but **a long synchronous loop ignores cancellation entirely.**

**Don't swallow `CancellationError`** with `try?` — you'll keep working for a screen the user left → [[mobile/11-performance-and-battery|battery]].

## Actors
<!-- bite: dd44b93d-5a48-4e7f-aa50-49062b3aa634 -->

An actor protects its mutable state — only one task touches it at a time:

```swift
actor ImageCache {
    private var storage: [URL: Image] = [:]

    func image(for url: URL) -> Image? { storage[url] }
    func store(_ image: Image, for url: URL) { storage[url] = image }
}

let cached = await cache.image(for: url)   // `await` — crossing into the actor
```

**Calls from outside are `async`**, because you may have to wait your turn. **Inside the actor, code is synchronous** and can touch state freely.

**Actor reentrancy is the subtle part:** an actor releases its lock at every `await` inside its own methods, so another task can enter. **State you read before an `await` may have changed after it.** Re-check invariants across suspension points — this is the actor equivalent of a check-then-act race.

## `@MainActor`
<!-- bite: 91097e58-b4f1-42f5-bf23-f29b61d18a6d -->

```swift
@MainActor
final class FeedViewModel: ObservableObject {
    @Published private(set) var items: [Item] = []

    func load() async {
        let fetched = await repository.fetch()   // off the main actor
        items = fetched                          // back on main, guaranteed
    }
}
```

**UI updates must be on the main thread**, and `@MainActor` makes that a compile-time guarantee instead of a runtime crash. **Annotate view models and UI-facing types** → [[mobile/frameworks/ios/index|iOS]].

## `Sendable` and Swift 6
<!-- bite: 5ff9b587-7061-40ac-9186-1421d70e961b -->

`Sendable` marks a type as safe to pass across concurrency boundaries. Value types of `Sendable` parts are automatically `Sendable`; classes generally are not unless they're immutable or internally synchronised.

**Swift 6's strict concurrency checking turns data races into compile errors.** That's a genuinely significant guarantee — data races are among the hardest bugs to reproduce — and **migrating an existing codebase is substantial work**, mostly consisting of auditing shared mutable state you'd forgotten about.

**Enable it incrementally**, module by module, rather than all at once.

## What replaced what
<!-- bite: 86869b60-690b-4306-8c9e-fbe57cc25cfa -->

| Old | Now |
|---|---|
| `DispatchQueue.async` | `Task { }` / `async let` |
| Completion handlers | `async throws` |
| `DispatchQueue.main.async` | `@MainActor` |
| `NSLock`, serial queues | `actor` |
| `DispatchGroup` | `withTaskGroup` |
| Combine (for one-shot) | `async/await` |

**Combine is still used** for streams and in existing codebases, but `AsyncSequence` covers much of it, and Apple's direction is clear.

## Key insight
<!-- bite: f97c048b-be50-4314-b2f2-72178265bedc -->

**Swift's concurrency model makes the compiler responsible for what used to be discipline** — structured concurrency means no orphaned tasks, `@MainActor` means no wrong-thread UI updates, and `Sendable` means no data races. The cost is that the compiler now argues with you about ownership of shared state, which is the same trade Rust makes and worth the same acceptance.

## Related
<!-- bite: c8197edd-30ab-4bee-bf4c-b41b37ed79c3 -->
- [[languages/08-swift/06-error-handling|error handling]] — cancellation is an error
- [[languages/09-kotlin/index|Kotlin coroutines]] — the same problem, similar shape
- [[os/06-concurrency-primitives|concurrency primitives]] — what's underneath
- [[languages/03-rust/13-concurrency|Rust's Send/Sync]] — the direct analogue of `Sendable`
