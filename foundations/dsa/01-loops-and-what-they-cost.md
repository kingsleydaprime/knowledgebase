# Loops and What They Cost

**Every complexity claim in this course is really a claim about how many times a loop runs.** Big-O looks like mathematical notation, but underneath it's counting — and the thing being counted is nearly always loop iterations. Getting fluent at that counting is the on-ramp to everything else here, so it goes first.

This note assumes you can already write a loop. If you can't, [[foundations/programming-fundamentals/06-control-flow|control flow]] in Programming Fundamentals covers the syntax properly and language-agnostically; come back here afterward. What follows is the part that note deliberately doesn't cover: **what a loop costs.**

## The two loops, briefly

**`for`** — when you know the number of repetitions up front, or you're walking something that has a definite length:

```python
for i in range(0, 100, 1):   # range(start, stop, step) — stop is exclusive
    print(i)                 # prints 0..99

for item in items:           # once per element, however many there are
    process(item)
```

`range(100)` is the same as `range(0, 100, 1)` — the start and step are optional, but **if you supply a step, you must supply the start too**, so it's `range(0, 100, 2)` and never `range(100, 2)`. (That second one is a valid call, just not the one you meant — it counts from 100 up to 2, so it runs zero times. Silent no-ops like that are worth recognising on sight.)

**`while`** — when the number of repetitions depends on something that changes as you go:

```python
while low <= high:           # runs until the condition stops holding
    ...
```

The distinction that matters for this course: **a `for` loop over `n` items usually announces its cost in its header. A `while` loop hides it in the body** — you have to look at how the variables move to know how many times it runs. Binary search is a three-line `while` loop that runs O(log n) times, and nothing in the header tells you that.

## Counting iterations

Take the loop's iteration count as a function of the input size `n`, then throw away constants:

```python
for i in range(n):           # runs n times          -> O(n)
    print(i)

for i in range(n):           # n times
    for j in range(n):       # ...n times each       -> O(n²)
        print(i, j)
```

The second one runs `n × n` times because the inner loop restarts in full on every pass of the outer one. That multiplication is the entire reason nesting is expensive: at n = 1,000 the first loop does a thousand steps and the second does a million.

**Sequential loops add, nested loops multiply.** Two loops one after another is `n + n = 2n`, which is still O(n). One inside the other is `n × n`. This single distinction accounts for most of the difference between a solution that passes and one that times out.

```python
for i in range(n): ...       # n
for j in range(n): ...       # + n   = 2n  -> O(n)

for i in range(n):           # n
    for j in range(n): ...   # × n   = n²  -> O(n²)
```

## Nested doesn't automatically mean O(n²)

This is where naive counting goes wrong. What matters is **total iterations of the inner body**, not how many `for` keywords are stacked up.

**The triangular loop** — inner starts where the outer is, so it shrinks each pass:

```python
for i in range(n):
    for j in range(i, n):    # n, then n-1, then n-2, ...
        ...
```

The total is `n + (n-1) + ... + 1 = n(n+1)/2 ≈ n²/2`. Constants get dropped, so it's **still O(n²)** — half the work, same growth curve. This is the shape behind checking every pair.

**Inner bound is a constant** — the inner loop doesn't depend on `n` at all:

```python
for i in range(n):
    for direction in [(0,1), (0,-1), (1,0), (-1,0)]:   # always 4
        ...
```

`4n` iterations, so **O(n)**. Two nested loops, linear cost. You'll write exactly this in every grid traversal.

**Both pointers only move forward** — the two-pointer and sliding-window shape:

```python
left = 0
for right in range(n):       # right advances n times total
    while left < right and condition:
        left += 1            # left advances at most n times, ever
```

That's a loop inside a loop, but `left` can only move forward `n` times across the *whole* run, not `n` times per pass. Total work is `2n` → **O(n)**. Counting the *nesting* gives you the wrong answer here; counting the *movement* gives you the right one. This is why [[03-sliding-window|sliding window]] is a linear-time pattern despite looking quadratic.

## Loops that halve

When the loop variable is multiplied or divided rather than incremented, the count is logarithmic:

```python
i = n
while i > 1:
    i = i // 2               # n -> n/2 -> n/4 -> ... -> 1
```

How many halvings does it take to get from `n` to 1? That's what `log₂ n` means. For a million elements that's 20 steps rather than a million — and this gap is the entire reason [[05-searching|binary search]], balanced [[01-trees|trees]], and [[08-heaps|heaps]] are worth their complexity.

| Loop shape | Iterations | Complexity |
|---|---|---|
| `for i in range(n)` | n | O(n) |
| Two sequential `for i in range(n)` | 2n | O(n) |
| `for i in range(n)` / `for j in range(n)` | n² | O(n²) |
| `for i in range(n)` / `for j in range(i, n)` | n²/2 | O(n²) |
| `for i in range(n)` / fixed-size inner | 4n | O(n) |
| Two pointers, both only advancing | 2n | O(n) |
| `while i > 1: i //= 2` | log₂ n | O(log n) |
| `for i in range(n)` / `while j //= 2` | n log n | O(n log n) |

## The hidden loops

Here's the trap, and it's the reason this note exists rather than just a Big-O section: **an operation that doesn't look like a loop may contain one.** Your code shows one level of nesting; the machine runs two.

```python
for x in items:              # n iterations...
    if x in seen_list:       # ...each scanning the whole list -> O(n)
        ...                  # total: O(n²)
```

There's one `for` in that code and it's quadratic. `x in some_list` walks the list. Swap the list for a set or dict and the same code is O(n) — because a [[03-hash-maps|hash map]] lookup doesn't loop, it computes an address. **That one substitution is the most common optimisation in the whole of DSA**, and it's invisible unless you're already thinking about where the hidden loops are.

The same trap in other clothes:

- **`arr[i]` on an [[01-arrays|array]] is O(1)** — the address is computed arithmetically, no walking. **Walking to index `i` of a [[04-linked-lists|linked list]] is O(n)** — there's no arithmetic that finds node `i`, so the operation *is* a loop, hidden behind indexing syntax. Same-looking line, different cost, and it's the whole array-vs-linked-list tradeoff in one sentence.
- `list.insert(0, x)` shifts every existing element — O(n) inside what reads as one call.
- String concatenation in a loop rebuilds the whole string each time, making the loop O(n²) in most languages.
- `sorted(...)` inside a loop is O(n log n) *per iteration*.

**When counting a loop's cost, count the cost of its body — not the number of lines in it.** A loop running `n` times with an O(n) body is O(n²), whatever it looks like.

## Gotchas

- **Off-by-one at the boundaries.** `range(n)` gives `0..n-1`, not `0..n`. Indexing starts at 0, so the last valid index is `len(arr) - 1`. Most "index out of range" crashes are a `<=` that should be a `<`.
- **A `while` loop whose variable doesn't move is an infinite loop.** With `for` the language advances the counter for you; with `while` that's your job, and forgetting it in one branch is the classic hang.
- **Mutating a collection while looping over it** skips elements or crashes, depending on the language. Build a new collection, or iterate over a copy.
- **Don't recompute the bound inside the loop.** `for i in range(len(expensive()))` is fine; `while i < len(expensive())` calls it every single pass.

## Where this goes next

[[01-algorithms|algorithms]] takes this counting and gives it the formal vocabulary — Big-O properly, best/average/worst case, space complexity alongside time, and the trick of reading a problem's input constraints backwards to guess the complexity you're expected to hit. Everything there is built on the counting above.

## Related
- [[foundations/programming-fundamentals/06-control-flow|control flow]] — loop syntax from scratch, if the code above wasn't already comfortable
- [[01-algorithms|algorithms]] — Big-O formalised; read this next
- [[01-arrays|arrays]] and [[04-linked-lists|linked lists]] — the O(1) vs O(n) indexing split described above
- [[03-hash-maps|hash maps]] — how to make the hidden `in` loop disappear
- [[foundations/dsa/06-patterns/README|patterns]] — several of them exist specifically to turn an O(n²) nesting into an O(n) sweep
