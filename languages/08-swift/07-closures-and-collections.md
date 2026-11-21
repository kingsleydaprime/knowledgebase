---
id: 873b7be8-07be-4c4b-b1ea-acb3fb5bddb7
---

# Closures and Collections

## Closure syntax, from verbose to idiomatic
<!-- bite: 0864a1a3-44ee-4261-9d17-86f69223ca89 -->

```swift
items.sorted(by: { (a: Item, b: Item) -> Bool in return a.price < b.price })
items.sorted(by: { a, b in a.price < b.price })       // types inferred, return implicit
items.sorted { a, b in a.price < b.price }            // trailing closure
items.sorted { $0.price < $1.price }                  // shorthand arguments
```

**All four are the same code.** The last is idiomatic — and `$0`/`$1` is the thing that makes Swift look unreadable to newcomers and completely natural after a week.

**Trailing closure syntax** is why SwiftUI reads the way it does: when the last parameter is a closure, it moves outside the parentheses.

## The collection operations
<!-- bite: 06b49e1e-f33c-4409-9ce9-964f2d9e3877 -->

```swift
let names   = users.map(\.name)                        // key-path shorthand
let adults  = users.filter { $0.age >= 18 }
let total   = prices.reduce(0, +)
let byCity  = Dictionary(grouping: users, by: \.city)
let first   = users.first { $0.isAdmin }               // Optional
let sorted  = users.sorted { $0.age < $1.age }
let flat    = nested.flatMap { $0 }
let valid   = strings.compactMap(Int.init)             // map + drop nils
```

**`compactMap` is the one to know** — map and discard failures in one pass. `["1", "x", "3"].compactMap(Int.init)` gives `[1, 3]`.

**`Dictionary(grouping:by:)`** replaces a surprising amount of manual loop code.

**Key paths (`\.name`)** work anywhere a closure taking one argument and reading a property would.

## Laziness
<!-- bite: 7b39f15a-2cc5-4899-9ff6-0cc310c3c48c -->

```swift
let result = hugeArray.map(expensive).filter(test).first
// ↑ maps EVERY element, then filters ALL of them, then takes one

let result = hugeArray.lazy.map(expensive).filter(test).first
// ↑ evaluates only until the first match
```

**Swift's collection operations are eager by default.** `.lazy` makes the chain pull-based. **Worth reaching for on large collections with expensive transforms**, and unnecessary otherwise — laziness has its own overhead.

## Escaping closures
<!-- bite: e48fc17f-9c4b-43ed-b2f5-bde4099f86da -->

```swift
func run(_ work: () -> Void) { work() }                 // non-escaping (default)
func store(_ work: @escaping () -> Void) { saved = work }  // outlives the call
```

**`@escaping` means the closure is kept beyond the function's return** — stored, or passed to async work. That's exactly when it can create a retain cycle, which is why `@escaping` is the signal to think about `[weak self]` → [[languages/08-swift/03-memory-and-arc|ARC]].

**Non-escaping is the default and it's faster** — the compiler can stack-allocate it.

## Capture semantics
<!-- bite: 1f37088b-b3ad-455a-bef7-4851a7b4a320 -->

```swift
var count = 0
let increment = { count += 1 }      // captures by REFERENCE
increment(); increment()
print(count)                        // 2

var x = 0
let printX = { [x] in print(x) }    // captures the VALUE at creation time
x = 99
printX()                            // 0
```

**Closures capture variables, not values, unless you use a capture list.** The `[x]` form snapshots.

## The important protocols
<!-- bite: 4774c332-d16a-42e7-b60b-4b3ea7fe6aeb -->

```swift
Sequence        // can be iterated once
Collection      // can be iterated repeatedly, has count and indices
```

Conform to `Sequence` and you get `map`, `filter`, `reduce`, `first(where:)` and the rest **free** — that's protocol extensions doing the work → [[languages/08-swift/04-protocols-and-generics|protocols]].

**Complexity is worth knowing:** `Array` index access is O(1) but `insert(at: 0)` is O(n). `Set` and `Dictionary` are O(1) average. **`Array.contains` is O(n)** — if you're calling it in a loop, you want a `Set` → [[dsa/index|DSA]].

## Strings are not arrays
<!-- bite: 2ac93815-68f0-499e-a1e4-6739743e6dab -->

```swift
let s = "héllo"
s.count            // 5  — but this is O(n), not O(1)
s[0]               // ❌ doesn't compile
s[s.startIndex]    // ✅
```

**Swift strings are collections of grapheme clusters**, not bytes or code points — so `"👨‍👩‍👧"` has `count == 1`, which is correct and surprises everyone. **The price is no integer subscripting and O(n) counting**, which is a deliberate trade for Unicode correctness.

For heavy text processing, work with `s.utf8` or index-based traversal rather than repeatedly converting.

## Key insight
<!-- bite: 983cd539-fb66-42bf-85ab-325667409a65 -->

**Swift's functional operations come free from protocol extensions on `Sequence`**, which is protocol-oriented design paying off visibly. The syntax compresses aggressively — `$0`, trailing closures, key paths — and that compression is what makes SwiftUI readable, so learning to read it is worth the early discomfort.

## Related
<!-- bite: 5b939614-9154-4920-89ec-2f38ec05aa3a -->
- [[languages/08-swift/04-protocols-and-generics|protocols]] — where these methods come from
- [[languages/08-swift/03-memory-and-arc|ARC]] — closures and retain cycles
- [[dsa/index|DSA]] — the complexity behind the collections

## About this lesson
<!-- bite: 3c6da169-f6dc-4114-8638-0e6a988f3ac6 -->

**Level:** Intermediate. **Covers:** the functional layer, and the syntax shortcuts that make Swift look cryptic until they don't.
