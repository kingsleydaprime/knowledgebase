# Interop and Performance

**[Advanced]** — Objective-C, C, and where Swift's costs actually are.

## Objective-C interop

**You will meet Objective-C** — much of Apple's older framework surface, and any codebase more than a few years old.

```swift
@objc final class Analytics: NSObject {
    @objc func track(_ name: String) { }
}
```

**`@objc` exposes Swift to the Objective-C runtime**, which is required for selectors, KVO, and older delegate protocols. **`dynamic`** forces dispatch through that runtime.

**What doesn't bridge:** structs, enums with associated values, generics, protocols with associated types, tuples. **If Objective-C needs to see it, it must be a class inheriting from `NSObject`.**

**Bridging headers** expose C and Objective-C to Swift. A Swift package can do this with a C target.

**The performance consequence:** `@objc dynamic` dispatch is a message send, not a direct call — **meaningfully slower**, and it defeats inlining. Don't add `@objc` for style; add it when the runtime requires it.

## C interop

Swift calls C directly, no wrapper needed:

```swift
import Darwin
let result = sqrt(2.0)
```

C pointers map to `UnsafePointer<T>` and friends. **The `Unsafe` prefix is deliberate** — you're outside the safety guarantees, and use-after-free is back on the table.

```swift
data.withUnsafeBytes { raw in
    // valid ONLY inside this closure. Escaping the pointer is undefined behaviour
}
```

**The scoped-closure pattern is the safe way** — it bounds the pointer's lifetime → [[languages/04-c/README|C]].

## Where Swift's performance actually goes

**The three costs that matter, in order:**

**1. Dynamic dispatch.** Class methods go through a vtable; `@objc dynamic` goes through the Objective-C runtime; **`final` and `private` let the compiler devirtualise and inline.**

> **Mark classes `final` unless they're designed for subclassing.** It's free performance and better design.

**Structs and protocol witnesses with `some` are statically dispatched** — another argument for value types → [[languages/08-swift/04-protocols-and-generics|`some` vs `any`]].

**2. Reference counting.** Every strong reference assignment is an atomic increment/decrement. **Atomics are not free**, and in a hot loop over class instances this shows up. Value types skip it entirely.

**3. Copy-on-write triggering unexpectedly.** Arrays and dictionaries are cheap to pass — **until you mutate one that has another reference**, which copies the whole buffer. In a loop, that's O(n²).

```swift
// reserveCapacity avoids repeated reallocation
var result = [Item]()
result.reserveCapacity(items.count)
```

## Existentials and boxing

```swift
let items: [any Shape] = [...]     // each element boxed
let items: [Circle] = [...]        // contiguous, no indirection
```

**`any` allocates a box for values larger than 3 words.** In a large collection this is a real cost, and it's invisible unless you know to look — which is why Swift 5.6 made `any` explicit.

## Optimisation and build settings

```
-Onone          debug — no optimisation, fast builds
-O              release
-O -whole-module-optimization    cross-file inlining. Default for release
```

**Whole-module optimisation lets the compiler devirtualise across files**, which is where a lot of Swift's release-build speed comes from. **Never benchmark a debug build** — the difference is often an order of magnitude, and people draw wrong conclusions from it constantly.

## Practical rules

- **`final` on classes** that aren't subclassed
- **Structs over classes** unless you need identity
- **`some` over `any`**
- **`reserveCapacity`** when you know the size
- **`lazy` on expensive chains** over large collections
- **`@inlinable`** for cross-module inlining in a library — it exposes the body as API, so use it deliberately
- **Profile before any of this.** Instruments' Time Profiler, on a release build → [[foundations/computer-architecture/12-performance|performance method]]

**And for a mobile app, none of this is usually the bottleneck.** Image decoding, main-thread I/O, and network round trips dominate → [[mobile/11-performance-and-battery|performance and battery]]. **Micro-optimising Swift while decoding a 4000px image on the main thread is the wrong order.**

## Key insight

**Swift's performance model is "fast by default if you use value types and `final`, and quietly slower every time you reach for dynamic behaviour."** Reference counting, existential boxing and dynamic dispatch are each individually small and collectively significant — but in an app, they're almost never what's actually slow, so profile before you act.

## Related
- [[languages/08-swift/02-values-references-and-optionals|value types]] · [[languages/08-swift/04-protocols-and-generics|`some` vs `any`]]
- [[languages/08-swift/03-memory-and-arc|ARC]] — the counting cost
- [[languages/04-c/README|C]] — the interop target
- [[mobile/11-performance-and-battery|mobile performance]] — what actually matters in an app
