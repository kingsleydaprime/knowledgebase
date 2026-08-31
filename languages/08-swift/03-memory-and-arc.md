# Memory and ARC

**[Intermediate]** — deterministic memory management without a garbage collector, and the one bug it doesn't prevent.

## What ARC is

**Automatic Reference Counting.** Every class instance has a count of strong references to it. When the count hits zero, it's deallocated **immediately**.

```swift
var a = Node()      // count 1
var b = a           // count 2
a = nil             // count 1
b = nil             // count 0 → deinit runs RIGHT HERE
```

**The compiler inserts the retain/release calls**, so it's automatic — but it isn't a garbage collector:

| | ARC | GC (Java, Go, Kotlin) |
|---|---|---|
| When freed | **Immediately** at zero | Eventually, when the collector runs |
| Pauses | **None** | Pause or background cost |
| Cycles | **Leaked — your problem** | Collected automatically |
| Overhead | Counting on every ref change | Periodic scanning |

**Deterministic deallocation is the win** — `deinit` runs at a predictable moment, so releasing a file handle or a socket in it actually works. **Reference cycles are the price.**

**Note that structs aren't reference counted at all** — they're copied, and their memory is stack-allocated or inline. **Which is another argument for preferring structs** → [[languages/08-swift/02-values-references-and-optionals|value types]].

## Reference cycles — the one real hazard

Two objects holding strong references to each other never reach zero:

```swift
class Person { var apartment: Apartment? }
class Apartment { var tenant: Person? }

let p = Person()
let a = Apartment()
p.apartment = a
a.tenant = p          // ← cycle. Neither is EVER deallocated
```

**Nothing crashes. Nothing warns you. Memory just grows.** This is the bug ARC doesn't solve, and it's why iOS apps leak.

## `weak` and `unowned`

```swift
class Apartment {
    weak var tenant: Person?      // does NOT increase the count
}
```

| | Behaviour | Use when |
|---|---|---|
| `strong` (default) | Keeps it alive | Ownership |
| **`weak`** | **Optional**, becomes `nil` automatically when deallocated | **The reference may outlive the target** |
| **`unowned`** | **Non-optional**, **crashes** if accessed after deallocation | You're certain it outlives you |

**`weak` is the safe default.** Use `unowned` only when the lifetimes genuinely guarantee it — the cost of being wrong is a crash.

**The ownership rule: the parent owns the child strongly; the child refers back weakly.** A view model owns its data; a delegate reference points back weakly.

**Delegates are almost always `weak`** — this is the single most common place cycles appear in UIKit code.

## Closures capture strongly — the commonest leak in Swift

```swift
class ViewController {
    var name = "x"

    func setup() {
        service.onComplete = {
            self.update(self.name)     // ← captures `self` STRONGLY
        }                              //   service holds the closure
    }                                  //   closure holds self
}                                      //   → cycle
```

**The fix — a capture list:**

```swift
service.onComplete = { [weak self] in
    guard let self else { return }
    self.update(self.name)
}
```

**`[weak self]` then `guard let self` is the standard idiom**, and you'll write it constantly.

**When you don't need it:** a closure that isn't stored — `DispatchQueue.main.async { }`, or a `map`/`filter` body — runs and is discarded, so there's no cycle. **Adding `[weak self]` everywhere is noise**; add it where the closure is *retained* by something you own.

## Finding leaks

- **Xcode's Memory Graph Debugger** — pause, click the graph icon, and it **shows cycles visually with the retain chain.** This is the tool; learn it
- **Instruments → Leaks and Allocations**
- **A `deinit` with a print** during development — if it never fires when a screen closes, you have a leak. **Crude and extremely effective**

**The habit worth building:** navigate to a screen and back several times, then check the Memory Graph for multiple instances of that view controller or view model. **Repeated instances of a screen you closed is the signature of a leak.**

## Beyond cycles

- **Retaining large data** — an image cache with no eviction is not a "leak" but will get you killed by the OS → [[mobile/11-performance-and-battery|memory]]
- **Timers and observers.** A repeating `Timer` retains its target; **you must invalidate it.** Same for notification observers in older code
- **`autoreleasepool`** for tight loops creating many temporary objects — rarely needed, occasionally essential

## Key insight

**ARC trades GC pauses for one bug you have to think about.** Deterministic deallocation is genuinely valuable — `deinit` fires when you expect — and the cost is that cycles are invisible and permanent. **In practice this reduces to one habit: `[weak self]` in closures you store, and `weak` on delegates and back-references.** Get those two right and Swift memory management mostly disappears.

## Related
- [[languages/08-swift/02-values-references-and-optionals|value types]] — structs avoid this entirely
- [[foundations/compilers/10-garbage-collection|garbage collection]] — the alternative approach
- [[languages/07-csharp/08-memory-gc-and-spans|C# memory]] — a GC'd comparison
- [[mobile/11-performance-and-battery|performance]] — leaks as a mobile problem
