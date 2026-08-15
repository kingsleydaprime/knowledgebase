# Garbage Collection

**[Advanced]** — Automatic memory management: the algorithms, why generational collection works, and the tradeoff every collector is navigating.

## The problem

A language with closures, objects, or dynamic data structures has values whose lifetime isn't lexically obvious:

```javascript
function makeCounter() {
    let count = 0;
    return () => ++count;      // `count` outlives makeCounter
}
```

Someone must decide when that's freeable. Options: the programmer ([[languages/04-c/07-memory-management|C]] — error-prone), the type system ([[languages/03-rust/03-ownership|Rust]] — restrictive), or the runtime (GC — costs performance and predictability).

**"Garbage" means unreachable**, not unused. A collector can't know you'll never look at something again; it can only prove nothing points at it.

## Reachability

Start from the **roots** — globals, the stack, registers, and in a VM the value stack and call frames. Anything reachable by following pointers is live; everything else is garbage.

```
ROOTS ──→ A ──→ B ──→ C
      └─→ D

    E ──→ F        ← unreachable, even though E points at F. Both are garbage.
```

**This is why reference counting can't collect cycles** — E and F might point at each other with nonzero counts and still be unreachable.

## Reference counting

```rust
struct Object { refcount: usize, data: ... }

fn retain(o: &mut Object) { o.refcount += 1; }
fn release(o: &mut Object) {
    o.refcount -= 1;
    if o.refcount == 0 { free_children(o); free(o); }
}
```

**For:** immediate reclamation (deterministic, and destructors run predictably), no pause, simple, and memory is freed as soon as it's dead — good for cache behaviour.

**Against:**
- **Cycles leak.** Needs a backup tracing collector, or `Weak` references by discipline
- **Every assignment costs** an increment and a decrement
- **Thread safety requires atomics**, which are much more expensive — this is exactly why [[languages/03-rust/12-smart-pointers-and-interior-mutability|`Rc` and `Arc`]] are separate types
- **Cascading frees** can pause you anyway — dropping the head of a million-node list frees a million objects in one go

Used by: CPython (plus a cycle collector), Swift (ARC, with `weak`/`unowned` for cycles), Objective-C, `shared_ptr`, `Rc`/`Arc`.

**Swift's ARC is compiler-inserted reference counting**, not a GC — the compiler emits retain/release calls and elides what it can prove is redundant. Deterministic, and it's why iOS apps have no GC pauses and why retain cycles are a real bug class you handle manually.

## Mark and sweep

The basic tracing collector:

```
1. MARK   — from the roots, traverse and mark every reachable object
2. SWEEP  — walk the whole heap, free anything unmarked, clear marks
```

```rust
fn collect(&mut self) {
    // mark
    for root in self.roots() { self.mark(root); }
    while let Some(obj) = self.gray_stack.pop() { self.blacken(obj); }

    // sweep
    self.objects.retain(|o| {
        if o.marked { o.marked = false; true } else { false }
    });
}
```

**Tri-colour marking** is the standard formulation, and it's what makes concurrent collection possible:

- **White** — not yet visited (garbage, if it stays white)
- **Grey** — visited, but its children haven't been
- **Black** — visited, and its children too

Process greys until none remain; whites are garbage.

**The tri-colour invariant: a black object must never point to a white one.** If the mutator (your program) runs during marking, it can break this — writing a white pointer into a black object hides it from the collector, and it gets freed while live.

**Write barriers** enforce the invariant: a small piece of code on every pointer write that greys the target (or the writer). That's the cost of concurrent collection, and it's why a GC'd language's pointer stores are slightly more expensive than C's.

**For:** collects cycles, no per-assignment cost.
**Against:** stop-the-world pauses proportional to heap size, and it **fragments** — free space is scattered.

## Copying and compaction

**Semi-space copying:** the heap is two halves. Allocate in one; on collection, copy live objects to the other and swap.

- **Allocation is a pointer bump** — faster than any `malloc`
- **Compaction is free** — copying is compaction, so no fragmentation
- **Cost is proportional to live data**, not heap size. A heap that's 95% garbage collects almost instantly
- **Wastes half the memory**, and all pointers must be updated

**Mark-compact** avoids the 2× overhead: mark, then slide live objects together and fix pointers. Slower than copying, no space waste.

Compaction requires **moving objects**, which requires knowing every pointer precisely — so it needs a **precise** GC. C++ and C can't have one, because a `void*` cast makes the pointer set unknowable. That's the fundamental reason `malloc` can't defragment and a JVM can. → [[foundations/os/05-memory-allocation|Memory Allocation]]

## Generational collection

**The generational hypothesis: most objects die young.** Empirically, 80–98% of allocations become garbage almost immediately.

```
┌──────────────────┐  ┌────────────────────────┐
│  YOUNG (nursery) │  │  OLD (tenured)         │
│  collected often │→ │  collected rarely      │
│  copying, fast   │  │  mark-compact          │
└──────────────────┘  └────────────────────────┘
```

Collect the nursery frequently: it's small, mostly garbage, and copying costs only what survives. A minor GC is often **sub-millisecond**. Survivors are promoted after surviving a few collections.

**The catch — old objects pointing at young ones.** They're roots for a minor GC, and scanning the whole old generation to find them would defeat the purpose.

**A write barrier plus a remembered set** solves it: every pointer write into an old object is recorded, so minor collection scans only the remembered set.

That write barrier is a real, permanent cost on every reference store in a generational runtime. It's the price of the hypothesis paying off, and it does pay off — generational collection is the single most effective GC idea and essentially universal.

## Concurrent and incremental

**Incremental** — interleave small marking steps with the program. Bounded pauses, longer total time.

**Concurrent** — mark on separate threads while the program runs. Needs write barriers to maintain the tri-colour invariant.

**Parallel** — use multiple threads for the collection itself. Orthogonal to concurrent.

Modern collectors combine all three:

| | Character |
|---|---|
| **Go's GC** | concurrent mark-sweep, **non-generational**, non-moving. Sub-millisecond pauses; tuned hard for latency → [[languages/02-go/13-performance-and-runtime\|Go]] |
| **JVM G1** | generational, regional, mostly concurrent. The default since 9 |
| **JVM ZGC / Shenandoah** | concurrent **and compacting**, using load barriers and coloured pointers. **Sub-millisecond pauses on terabyte heaps** |
| **V8 Orinoco** | generational, concurrent, parallel |
| **.NET** | generational, background |

**Go's collector being non-generational is a deliberate and unusual choice.** The reasoning: Go's escape analysis puts most short-lived objects on the stack anyway, so the nursery would be less useful, and avoiding a write barrier on every pointer store keeps the common path cheap. The trade is more work in each cycle.

**ZGC's coloured pointers** are worth knowing: metadata is stored in unused pointer bits, and a **load barrier** fixes up references lazily when read. That's what makes concurrent *compaction* possible — you can move an object while the program runs, because any thread reading a stale pointer is corrected on the spot.

## The tradeoff space

Every collector navigates three axes and can optimise at most two:

```
        THROUGHPUT (total work done)
              ▲
              │
              │
    LATENCY ◄─┴─► MEMORY FOOTPRINT
   (pause time)
```

- **Larger heap** → fewer collections → better throughput, more memory
- **Concurrent marking** → shorter pauses → more total CPU (barriers, and racing the mutator)
- **Generational** → better throughput and latency → write-barrier cost on every store

**A GC'd program typically needs 2–5× the live-set size** to perform well. That's the real memory cost, and it's why `GOGC` and `-Xmx` tuning matters: too small a heap means constant collection.

```bash
GOGC=100                     # Go: collect when the heap doubles (default)
GOMEMLIMIT=4GiB              # soft limit — the GC works harder as you approach it
-Xmx4g -XX:MaxGCPauseMillis=100   # JVM
```

`GOMEMLIMIT` and container limits interact directly with [[foundations/os/04-virtual-memory|the OOM killer]] — a runtime that doesn't know its cgroup limit gets killed before its GC feels pressure.

## Precise vs conservative

**Precise** — the runtime knows exactly which words are pointers, via stack maps the compiler emits. Required for moving collection.

**Conservative** — scan the stack and treat anything that *looks* like a pointer as one. Boehm GC does this, and it's how you retrofit GC onto C.

Conservative collection can't move objects (a false positive would be corrupted) and retains occasional garbage (an integer that happens to look like an address). It's a pragmatic hack, and precise is strictly better where you control the compiler.

## Writing one

For a VM you're building, a **mark-and-sweep collector is a few hundred lines** and entirely tractable:

1. **Track every allocation** in a linked list
2. **Trigger** when allocated bytes exceed a threshold; set the next threshold as a multiple of live bytes
3. **Mark** from roots: the value stack, call frames, globals, open upvalues
4. **Sweep** the allocation list
5. **Handle interned strings** — a string table holds references that must be treated as weak, or nothing is ever collected

**The hardest bug is a missed root.** An object reachable only from a local variable in your *interpreter's* C/Rust code — not the VM's value stack — is invisible to the collector and gets freed while in use. The symptom is spectacular and intermittent.

The standard defence: **a stress mode that collects on every allocation**, run against your whole test suite. It converts a rare heisenbug into a deterministic failure. *Crafting Interpreters* makes exactly this point, and it's the single most valuable piece of GC debugging advice.

---

## Related
- [[foundations/compilers/09-bytecode-and-virtual-machines|Bytecode and Virtual Machines]] — the runtime this serves
- [[foundations/os/05-memory-allocation|Memory Allocation]] — the manual alternative, and why `malloc` can't compact
- [[languages/03-rust/03-ownership|Rust: Ownership]] — the type-system alternative
- [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM Internals]] · [[languages/02-go/13-performance-and-runtime|Go's GC]]
- [[foundations/compilers/README|Compilers course map]]
