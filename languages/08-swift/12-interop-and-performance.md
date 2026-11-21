---
id: 91f2327a-3bc8-446d-a159-18e01138e567
---

# Interop and Performance

Interop is Swift's ability to work with code written in other languages, mainly Objective-C and C, and performance is how fast that code runs. Many Apple apps still mix Swift with older Objective-C code. This lesson shows how the languages connect and where Swift's speed actually goes.

## Objective-C interop
<!-- bite: 9b3a387b-3edd-48ff-be70-b8264526952a -->

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
<!-- bite: 2c5c05b2-6ea9-4ffe-b7ca-a1fa108cf103 -->

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

**The scoped-closure pattern is the safe way** — it bounds the pointer's lifetime → [[languages/04-c/index|C]].

## Where Swift's performance actually goes
<!-- bite: 54a5c037-033b-46ea-b061-f9c76f45981a -->

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
<!-- bite: 81fe6cae-6a25-4957-941d-986cc4821991 -->

```swift
let items: [any Shape] = [...]     // each element boxed
let items: [Circle] = [...]        // contiguous, no indirection
```

**`any` allocates a box for values larger than 3 words.** In a large collection this is a real cost, and it's invisible unless you know to look — which is why Swift 5.6 made `any` explicit.

## Optimisation and build settings
<!-- bite: c009de2d-bfc0-4141-a349-7794448f57e6 -->

```text
-Onone          debug — no optimisation, fast builds
-O              release
-O -whole-module-optimization    cross-file inlining. Default for release
```

**Whole-module optimisation lets the compiler devirtualise across files**, which is where a lot of Swift's release-build speed comes from. **Never benchmark a debug build** — the difference is often an order of magnitude, and people draw wrong conclusions from it constantly.

## Practical rules
<!-- bite: c0885c8c-2ed1-4f7d-8222-35a711a154bb -->

- **`final` on classes** that aren't subclassed
- **Structs over classes** unless you need identity
- **`some` over `any`**
- **`reserveCapacity`** when you know the size
- **`lazy` on expensive chains** over large collections
- **`@inlinable`** for cross-module inlining in a library — it exposes the body as API, so use it deliberately
- **Profile before any of this.** Instruments' Time Profiler, on a release build → [[computer-architecture/12-performance|performance method]]

**And for a mobile app, none of this is usually the bottleneck.** Image decoding, main-thread I/O, and network round trips dominate → [[mobile/11-performance-and-battery|performance and battery]]. **Micro-optimising Swift while decoding a 4000px image on the main thread is the wrong order.**

## Key insight
<!-- bite: b0e1cb5b-8cb3-4653-bec9-08ac7c12df49 -->

**Swift's performance model is "fast by default if you use value types and `final`, and quietly slower every time you reach for dynamic behaviour."** Reference counting, existential boxing and dynamic dispatch are each individually small and collectively significant — but in an app, they're almost never what's actually slow, so profile before you act.

## Related
<!-- bite: 989bea40-0a1f-4ca2-8699-5dbf50a5c74d -->
- [[languages/08-swift/02-values-references-and-optionals|value types]] · [[languages/08-swift/04-protocols-and-generics|`some` vs `any`]]
- [[languages/08-swift/03-memory-and-arc|ARC]] — the counting cost
- [[languages/04-c/index|C]] — the interop target
- [[mobile/11-performance-and-battery|mobile performance]] — what actually matters in an app

## About this lesson
<!-- bite: fca4982f-8ce3-4151-86ad-43e6634cae41 -->

**Level:** Advanced. **Covers:** Objective-C, C, and where Swift's costs actually are.
