# Swift

**Apple's language, and the only first-class way onto iOS.** Statically typed, memory-safe, value-oriented, with a modern type system and structured concurrency.

**~12 notes, built Aug 2026** alongside [[mobile/README|the mobile track]]. `[reference]`.

> **The one idea:** Swift is *safe by making unsafety explicit.* You cannot accidentally use nil, accidentally alias a collection, accidentally update the UI off the main thread, or (in Swift 6) accidentally race. **The escape hatches all exist — `!`, `class`, `Unsafe`, `@unchecked` — and every one of them is deliberately noisy.** Read the language through that and its design stops feeling fussy.

## Why this exists

The vault had [[game-development/engines/unity|C# for Unity]] and no Swift — so it covered Apple's ecosystem nowhere, despite iOS being half of [[mobile/README|mobile]]. This closes that.

**The honest scope note:** Swift is a genuinely well-designed language locked to one vendor's platforms. **Learn it to ship on Apple platforms** — as a general-purpose skill it doesn't compete with Go or Python outside that world.

## Reading order

**01–03 are the model** and are worth reading in order. 04–09 are the language's features. 10–12 are the runtime and the tooling.

1. [[languages/08-swift/01-why-swift-and-the-toolchain|why-swift-and-the-toolchain]] — **[Beginner]** — what it's for, SPM, and an honest word about Xcode
2. [[languages/08-swift/02-values-references-and-optionals|values-references-and-optionals]] — **[Beginner → Intermediate]** — **the two defining ideas.** Structs copy, classes share; there is no null, and absence is a type
3. [[languages/08-swift/03-memory-and-arc|memory-and-arc]] — **[Intermediate]** — deterministic deallocation without a GC, and **the one bug it doesn't prevent**: retain cycles, and `[weak self]`
4. [[languages/08-swift/04-protocols-and-generics|protocols-and-generics]] — **[Intermediate → Advanced]** — protocol extensions instead of base classes, and **`some` vs `any`, which is where the performance lives**
5. [[languages/08-swift/05-enums-and-pattern-matching|enums-and-pattern-matching]] — **[Intermediate]** — sum types, and **the single biggest quality improvement available in application code**
6. [[languages/08-swift/06-error-handling|error-handling]] — **[Intermediate]** — `throws`, the three `try`s, typed throws, and where `try?` costs you
7. [[languages/08-swift/07-closures-and-collections|closures-and-collections]] — **[Intermediate]** — the `$0` syntax that makes SwiftUI readable, laziness, `@escaping`, and why strings aren't arrays
8. [[languages/08-swift/08-structs-classes-and-initialisation|structs-classes-and-initialisation]] — **[Intermediate]** — the initialiser rules, property observers, and **what `@State` actually is**
9. [[languages/08-swift/09-codable-and-json|codable-and-json]] — **[Intermediate]** — free serialisation, and the two things you must customise: **dates, and unknown enum values**
10. [[languages/08-swift/10-concurrency-and-actors|concurrency-and-actors]] — **[Advanced]** — structured concurrency, actors and reentrancy, `@MainActor`, and **Swift 6 making data races a compile error**
11. [[languages/08-swift/11-testing-and-tooling|testing-and-tooling]] — **[Intermediate]** — Swift Testing, what's worth testing, the sanitizers, and **the Xcode rituals that aren't your fault**
12. [[languages/08-swift/12-interop-and-performance|interop-and-performance]] — **[Advanced]** — Objective-C and C, and where Swift's costs actually are

## If you only take three things

1. **Prefer structs.** Value semantics remove a whole class of aliasing bugs, and copy-on-write makes them cheap ([[languages/08-swift/02-values-references-and-optionals|02]]).
2. **`[weak self]` in closures you store.** That plus `weak` delegates is 90% of Swift memory management ([[languages/08-swift/03-memory-and-arc|03]]).
3. **Model state as an enum, not several booleans.** The compiler then makes invalid states unrepresentable ([[languages/08-swift/05-enums-and-pattern-matching|05]]).

## Related
- [[mobile/frameworks/ios/README|iOS]] — the platform this language exists for
- [[mobile/README|mobile]] — the course this was written alongside
- [[languages/README|languages]] · [[languages/projects|projects]]
- [[languages/03-rust/README|Rust]] — the nearest comparison: same safety instincts, stricter enforcement
