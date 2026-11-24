---
id: 53992400-1b82-4ac0-977d-7a02ffb76e14
---

# Concurrency Primitives

Concurrency primitives are the basic tools that stop two threads from changing the same data at the same time and messing it up. Picture two people updating the same bank balance at the same moment, where one update gets lost. The locks in every programming language are built from a few small tools the processor and operating system provide, and this lesson shows them.

## The layer under everything
<!-- bite: 32f44834-b9ae-4bef-99f1-2dbdb861f3e5 -->

Java's `synchronized`, Go's `sync.Mutex`, Rust's `Mutex<T>`, C++'s `std::mutex`, Python's GIL — all of them bottom out in the same two things: **atomic instructions** provided by the CPU, and **futexes** provided by the kernel.

Understanding this layer explains why uncontended locks are nearly free, why contended ones are catastrophic, and why `volatile` is not a threading primitive.

## Atomic instructions
<!-- bite: b0406523-1a39-4f88-b1fe-baa4b339e418 -->

The hardware guarantee: an operation that cannot be interrupted halfway.

```text
lock cmpxchg    compare-and-swap (CAS)  — the universal primitive
lock xadd       fetch-and-add
lock xchg       atomic exchange
```

The `lock` prefix on x86 makes the operation atomic across all cores — historically by asserting a bus lock, now by holding the cache line in exclusive state for the duration.

**Compare-and-swap is the primitive everything else is built from:**

```c
// atomically: if (*ptr == expected) { *ptr = desired; return true; } else return false;
bool __atomic_compare_exchange_n(int *ptr, int *expected, int desired, ...);
```

A lock-free counter, in full:

```c
int old;
do {
    old = counter;
} while (!__atomic_compare_exchange_n(&counter, &old, old + 1, ...));
```

Read, compute, try to swap; if someone else changed it, retry. **This is the shape of every lock-free algorithm** — optimistic, with a retry loop.

Cost: an uncontended atomic is ~10–20ns, roughly a cache-line access. Under contention it's much worse, because the cache line ping-pongs between cores.

### The ABA problem

Thread A reads value `X`. Thread B changes it to `Y` and back to `X`. Thread A's CAS succeeds — but the world changed underneath it.

This breaks lock-free stacks and queues, where the pointer is the same but the node was freed and reallocated. Solutions: tagged pointers (a version counter in unused bits), hazard pointers, or epoch-based reclamation. It's the reason writing correct lock-free data structures is genuinely hard, and why you should use someone else's.

## Memory barriers
<!-- bite: 05502b2c-4216-4571-abc8-5e373e570f51 -->

The part that surprises people: **the CPU and the compiler both reorder memory operations.**

```c
// thread A
data = 42;
ready = 1;

// thread B
while (!ready) {}
assert(data == 42);        // CAN FAIL — B may see ready=1 before data=42
```

Every level reorders: the compiler moves stores for register pressure, the CPU executes out of order, and store buffers make writes visible to other cores in a different order than issued.

**A memory barrier constrains the reordering:**

```c
__atomic_thread_fence(__ATOMIC_ACQUIRE);   // no later access moves before this
__atomic_thread_fence(__ATOMIC_RELEASE);   // no earlier access moves after this
__atomic_thread_fence(__ATOMIC_SEQ_CST);   // full barrier, total global order
```

The **acquire/release pair** is the fundamental idiom:

```c
// thread A
data = 42;
__atomic_store_n(&ready, 1, __ATOMIC_RELEASE);   // everything before is published

// thread B
if (__atomic_load_n(&ready, __ATOMIC_ACQUIRE)) { // ...and visible after this
    assert(data == 42);                           // guaranteed
}
```

This is exactly the model exposed by [[languages/03-rust/13-concurrency|Rust's `Ordering`]], [[languages/05-cpp/13-concurrency|C++'s `std::memory_order`]], and Java's `volatile` — all four descend from the C++11 memory model, which is why the vocabulary is shared.

> **Use sequential consistency unless you can prove you need weaker.** The orderings are hard, the performance difference is usually irrelevant, and a mistake produces bugs that appear only on ARM, only under load, only in production. x86 is strongly ordered enough to hide most acquire/release mistakes; ARM is not, which is why "it worked on my laptop, it breaks on the server" is a real memory-ordering story now.

**`volatile` is not a memory barrier.** In C and C++ it prevents the *compiler* caching a value in a register — nothing more. No atomicity, no ordering guarantee, no cross-core visibility. It's correct for memory-mapped hardware registers and signal handlers, and wrong for threading. (Java's `volatile` is different, and does imply barriers.) → [[languages/04-c/04-types-and-integers|C: volatile]]

## Futexes
<!-- bite: fa9727ac-182b-4de0-b603-58bfda00809f -->

The kernel primitive that makes user-space locks fast.

**futex = fast userspace mutex.** The insight: an uncontended lock needs no kernel involvement at all.

```c
// uncontended acquire — pure user space, ~20ns
if (CAS(&lock, 0, 1)) return;             // got it, no syscall

// contended — now ask the kernel to sleep us
syscall(SYS_futex, &lock, FUTEX_WAIT, 1, NULL, NULL, 0);
```

```c
// release
if (atomic_dec(&lock) != 0)                // someone was waiting
    syscall(SYS_futex, &lock, FUTEX_WAKE, 1, NULL, NULL, 0);
```

**The syscall happens only on contention.** That's why:

| | Cost |
|---|---|
| Uncontended mutex lock/unlock | ~20ns (one atomic) |
| Contended, with sleep and wake | ~1–10µs (two syscalls + context switch) |

**A 100–500× difference.** It's the single most important fact about lock performance, and it explains why "just add a mutex" is fine at low contention and disastrous at high contention.

It also explains the tuning advice everywhere: **shorten critical sections.** You're not trying to avoid the lock, you're trying to avoid *contention*.

```bash
perf lock record ./prog && perf lock report      # contention by lock
strace -c -e futex ./prog                        # futex syscalls = contention
```

Lots of `futex` syscalls in `strace -c` is the signature of a contended lock, and it's a quick diagnosis.

## Spinlocks vs mutexes
<!-- bite: 95dd673a-fc0d-424f-b63e-e776ccde6366 -->

**Spinlock** — busy-wait in a loop until the lock frees. No syscall, no sleep.

```c
while (!CAS(&lock, 0, 1)) { __builtin_ia32_pause(); }   // PAUSE hints the CPU
```

**Correct only when the critical section is shorter than a context switch (~1µs)** and the waiter can't be preempted. That's true in kernel code with interrupts disabled; it's usually false in user space, where the lock holder can be descheduled and you'll spin uselessly for a whole time slice.

Most user-space mutexes are **adaptive**: spin briefly, then fall back to a futex wait. That gets both the fast uncontended path and the correct behaviour under real contention.

**Never write a raw spinlock in user-space application code.** Use the platform mutex, which already does the adaptive thing.

## The primitives
<!-- bite: 3c78f570-f3e5-43fe-a5f6-74d1438a67be -->

**Mutex** — mutual exclusion. One holder.

**Reader-writer lock** — many readers or one writer. Worth it only when reads genuinely dominate and critical sections are non-trivial; the bookkeeping makes it slower than a plain mutex under mixed load, and writer starvation is a real failure mode.

**Semaphore** — a counter. `wait` decrements (blocking at zero), `post` increments. Models a pool of N resources; a mutex is a semaphore with N=1 plus ownership semantics.

**Condition variable** — wait for a *condition*, not just a lock:

```c
pthread_mutex_lock(&mu);
while (!condition) {                        // WHILE, not if
    pthread_cond_wait(&cv, &mu);            // atomically unlocks, sleeps, relocks
}
// condition is true, and we hold the lock
pthread_mutex_unlock(&mu);
```

**The `while` loop is mandatory**, for two reasons: **spurious wakeups** (a wait may return without a signal, permitted by the standard and real in practice) and the fact that another thread may have taken the condition between your wake and your relock. Code using `if` here is broken, and it fails rarely enough to reach production.

**Barrier** — N threads wait until all arrive, then all proceed.

**RCU (read-copy-update)** — the kernel's technique for read-mostly data: readers take **no lock at all** and pay nothing; writers copy, modify, and swap a pointer, then wait for all pre-existing readers to finish before freeing the old version. Extremely fast reads, complex reclamation. It's why kernel routing-table lookups are cheap.

## Deadlock
<!-- bite: e0a28a73-d424-456c-bbc2-038f52d30b41 -->

Four conditions, all required:

1. **Mutual exclusion** — resources aren't shareable
2. **Hold and wait** — hold one, wait for another
3. **No preemption** — can't forcibly take a lock away
4. **Circular wait** — A waits for B waits for A

Break any one and deadlock is impossible. **Breaking circular wait is the practical answer: impose a global lock ordering and always acquire in that order.**

```c
// always lock the lower address first — a simple total order
if (&a < &b) { lock(&a); lock(&b); } else { lock(&b); lock(&a); }
```

C++'s `std::scoped_lock` does this for you across multiple mutexes, which is why it's preferred over nesting `lock_guard`s. → [[languages/05-cpp/13-concurrency|C++: Concurrency]]

```bash
gdb -p <pid>  →  thread apply all bt        # where is every thread stuck?
cat /proc/<pid>/task/*/stack                 # kernel stacks
gcc -fsanitize=thread                        # TSan detects lock-order inversions
```

**TSan finds lock-order inversions before they deadlock**, which is far better than diagnosing one at 3am. Run it in CI.

## Lock-free, and whether it's worth it
<!-- bite: 8736e32f-899b-4ecf-a4c7-cf3867af6e80 -->

Lock-free algorithms guarantee that *some* thread makes progress. Wait-free guarantees *every* thread does.

They avoid deadlock, priority inversion, and convoy effects. They're also **hard to get right** — ABA, memory reclamation, and subtle ordering bugs — and often **slower** than a good mutex under moderate contention, because the retry loops burn CPU.

> **Use a mutex. If profiling shows lock contention is genuinely the bottleneck, first shorten the critical section, then shard the lock, then consider a well-tested lock-free structure from a library. Write your own last, if ever.**

Sharding is the underrated middle step: replacing one lock with 64 locks keyed by hash removes most contention with none of the difficulty.

---

## Check your understanding
<!-- bite: f92b4584-1883-402c-bcab-18a6762bab66 -->

Try each one before you open the answer.

1. <!-- q: mcq id="409c04a7" -->
   Thread A runs `data = 42; ready = 1;` with plain variables. Thread B loops until `ready == 1`, then reads `data`. Can B see `data` as something other than 42?

   - [ ] No, statements always run in order
   - [x] Yes; the compiler and CPU may reorder the stores, so `ready` can become visible before `data`
   - [ ] Only on single-core machines
   - [ ] Only if `data` is a float

   <details><summary>Answer</summary>

   Yes. Use a release store to `ready` in A and an acquire load in B. That pair guarantees everything A wrote before the release is visible after B's acquire.

   </details>

2. <!-- q: mcq id="2e6f13ed" -->
   What does `volatile` do in C and C++?

   - [ ] Makes a variable safe to share between threads
   - [ ] Adds a full memory barrier
   - [x] Stops the compiler caching the value in a register, and nothing more
   - [ ] Makes reads and writes atomic

   <details><summary>Answer</summary>

   Only that. It gives no atomicity, no ordering and no visibility guarantee across cores. It's for memory-mapped hardware registers, not threading. (Java's `volatile` is different and does give ordering.)

   </details>

3. <!-- q: exact id="5adabdbc" answer="250" -->
   An uncontended mutex lock and unlock costs about 20 ns. A contended one that has to sleep and be woken costs about 5 µs. How many times more expensive is the contended case?

   <details><summary>Answer</summary>

   250 times (5,000 ns ÷ 20 ns). A futex only makes a system call when there is contention, so the goal is to shorten critical sections and avoid contention, not to avoid locks.

   </details>

4. <!-- q: open id="39df93d2" -->
   Why must a condition-variable wait be inside a `while` loop rather than an `if`?

   <details><summary>Answer</summary>

   Two reasons. A wait can return with no signal (a spurious wakeup), and even after a real signal, another thread may have taken the condition before this one got the lock back. Rechecking the condition in a loop handles both.

   </details>

5. <!-- q: mcq id="f8a707bb" -->
   Deadlock needs four conditions at once. Which one does "always take locks in the same global order" break?

   - [ ] Mutual exclusion
   - [ ] Hold and wait
   - [ ] No preemption
   - [x] Circular wait

   <details><summary>Answer</summary>

   Circular wait. If everyone takes lock A before lock B, nobody can hold B while waiting for A. `std::scoped_lock` does this ordering for you, and TSan detects lock-order inversions before they deadlock.

   </details>

6. <!-- q: open id="cad51549" -->
   Profiling shows one mutex around a shared cache is the bottleneck. What should you try before writing a lock-free structure?

   <details><summary>Answer</summary>

   First shorten the critical section, doing as little as possible while holding the lock. Then shard it: replace one lock with, say, 64 locks chosen by hashing the key, which removes most contention with little difficulty. Only then consider a well-tested lock-free structure from a library.

   </details>

## Related
<!-- bite: 04d26f80-2a6d-4f44-b360-efb24e0de956 -->
- [[os/03-scheduling|Scheduling]] — priority inversion, and why spinning is usually wrong
- [[os/02-processes-and-threads|Processes and Threads]] — what shares what
- [[languages/03-rust/13-concurrency|Rust: Concurrency]] — these primitives with the races made impossible
- [[architecture/04-distributed-systems/03-time-and-ordering|Time and Ordering]] — the same problems, without shared memory
- [[os/index|OS course map]]

## About this lesson
<!-- bite: b1e897c6-3e6f-429c-80bc-f3467871092d -->

**Level:** Advanced. **Covers:** What a mutex actually is, why an uncontended lock costs nothing, and the memory barriers underneath every concurrency abstraction you use.
