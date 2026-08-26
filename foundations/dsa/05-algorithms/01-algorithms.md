# Algorithms and Complexity Analysis

An algorithm is a finite, well-defined sequence of steps that takes an input and produces an output. That's the whole definition — a recipe, a set of driving directions, and quicksort are all algorithms in the same technical sense.

What this note is really about is the **vocabulary for comparing them**: given two ways to solve the same problem, how do you say which is better without just running both and hoping your laptop is representative? That vocabulary — Big-O and its relatives — is the measuring system the entire rest of this course is quoted in, so it's worth more time than anything else here.

If counting loop iterations isn't yet automatic, read [[01-loops-and-what-they-cost|loops and what they cost]] first — this note formalises exactly what that one counts.

## Correctness vs efficiency

An algorithm is judged on two separate questions, in this order:

1. **Does it produce the right answer for every valid input**, including the edge cases — empty input, one element, duplicates, already-sorted data, all-negative values? This comes first: **a fast wrong answer is worthless.**
2. **How much time and memory does it use as the input grows?** This is what the notation below describes.

Most people jump to (2) and skip (1). In an interview it's the reverse that impresses — state the brute force, confirm it's *correct*, then optimise it.

## Why we measure growth, not time

The obvious way to compare two algorithms is to time them. That fails for three reasons: the answer depends on your hardware, on the language, and on the particular input you happened to test. Run the same comparison on a faster machine and the numbers all change.

So instead of measuring *how long*, we measure **how the cost grows as the input grows** — a property of the algorithm itself, independent of the machine running it. An algorithm whose cost doubles when the input doubles behaves that way on any hardware, forever.

That's why constants get dropped. `2n` and `100n` are both "linear": as `n` heads for a million, what dominates is the *shape* of the curve, not the multiplier. An O(n²) algorithm eventually loses to an O(n log n) one no matter how large the constant gap, once `n` is big enough.

```python
def contains(arr, target):       # O(n)
    for x in arr:                # the loop runs up to n times
        if x == target:
            return True
    return False

def first_two(arr):              # O(1)
    return arr[0], arr[1]        # constant work regardless of len(arr)
```

## The three notations: O, Ω, Θ

Almost everyone says "Big-O" for all three, but they mean different things, and knowing the difference is the difference between quoting a complexity and understanding one.

They are **bounds on a function**. Let `T(n)` be the algorithm's cost on input size `n`:

| Notation | Name | Means | Everyday phrasing |
|---|---|---|---|
| **O(f)** | Big-O | `T(n)` grows **no faster than** `f(n)` | an **upper** bound — "at worst this shape" |
| **Ω(f)** | Big-Omega | `T(n)` grows **no slower than** `f(n)` | a **lower** bound — "at least this shape" |
| **Θ(f)** | Big-Theta | **both** — `T(n)` grows *exactly* like `f(n)` | a **tight** bound — "precisely this shape" |

Θ is the strongest claim: it says the function is sandwiched between two constant multiples of `f(n)`, so it's neither better nor worse than `f`. **Θ(f) holds exactly when both O(f) and Ω(f) hold.**

Here's the consequence people find surprising. Big-O is only an upper bound, so **it is technically correct to say binary search is O(n²).** It never does more than n² work — the statement is true, just uselessly loose, the way "I'll be there within a year" is true of a five-minute journey. Θ(log n) is the honest, tight answer.

In practice: **when someone says "this is O(n log n)" they almost always mean Θ(n log n)** — the tight bound. The loose usage is universal and you should use it too, since fighting it makes you hard to talk to. But be precise when precision matters, and *know* which one you're claiming. "It's O(n log n), and that's tight" is a sharper sentence than either half alone.

```
Ω(n)  ─────────────  T(n) is at least linear
Θ(n)  ─────────────  T(n) is exactly linear
O(n)  ─────────────  T(n) is at most linear
```

## Best, average, and worst case — a different axis

This is the most common confusion in the whole topic, so it's worth stating flatly: **O/Ω/Θ and best/average/worst are two independent things.**

- **O, Ω, Θ** describe how you're bounding a function.
- **Best / average / worst case** describe *which input* you're measuring on.

You can combine them freely: an algorithm has a best case, and that best case has its own tight Θ bound. Saying "Big-O is the worst case and Big-Omega is the best case" is a widespread misconception — Ω is a lower bound on whichever case you're discussing, not a synonym for "best case".

Linear search for a target in an unsorted array of `n` items:

| Case | Which input | Cost |
|---|---|---|
| **Best** | target is the first element | Θ(1) |
| **Worst** | target is last, or absent | Θ(n) |
| **Average** | target equally likely anywhere | Θ(n) — about n/2 comparisons, and constants drop |

**Worst case is the default** when nobody says otherwise, for a good reason: it's the only one that's a guarantee. Average case depends on assumptions about your input distribution that reality may not honour, and best case is nearly always useless — every algorithm has a lucky input.

Worst case also has a security dimension. A [[03-hash-maps|hash map]] is Θ(1) average and Θ(n) worst case, when every key collides. An attacker who knows your hash function can craft keys that all land in one bucket and turn your O(1) lookups into O(n) — a real denial-of-service class called a **hash-flooding attack**, and the reason languages randomise hash seeds at startup. "Average case is fine" is an assumption an adversary gets a vote on.

In an interview, **"O(n) average, O(n²) worst case"** is a much stronger answer than "O(n)".

## Common complexity classes

| Notation | Name | Example |
|---|---|---|
| O(1) | Constant | array index access, hash map lookup |
| O(log n) | Logarithmic | binary search, balanced BST operations |
| O(n) | Linear | single loop over the input |
| O(n log n) | Linearithmic | merge sort, heapsort, quicksort (average) |
| O(n²) | Quadratic | nested loop over the input (bubble sort, naive pair-checking) |
| O(2ⁿ) | Exponential | brute-force subsets, naive recursive Fibonacci |
| O(n!) | Factorial | brute-force permutations |

```
work
 ^                                                    n!
 |                                            2ⁿ
 |                                  n²
 |                        n log n
 |                n
 |        log n
 |1
 +---------------------------------------------------> n
```

Worth internalising how violent the gap is. At `n = 1,000,000`: log n is 20, n log n is 20 million, and n² is a trillion — about **11 days** at 10⁸ operations per second, versus a fifth of a second. The curve isn't an abstraction; it's the difference between a response and a timeout.

**O(n log n) is the floor for comparison sorting.** No comparison-based sort can beat it — that's a proven lower bound, not a gap waiting to be closed. Getting under it requires not comparing (counting sort, radix sort — see [[04-sorting|sorting]]).

## Deriving a complexity

Count how many times the innermost work happens, as a function of `n`, then drop constants and lower-order terms.

- One loop over `n` → O(n).
- A loop inside a loop, both over `n` → O(n²).
- **Sequential** loops add: `O(n) + O(n) = O(n)`. **Nested** loops multiply: `O(n) × O(n) = O(n²)`.
- Halving the problem each step, recursing into one half → O(log n).
- Halving and recursing into *both* halves with O(n) work to combine → O(n log n).
- Branching into 2 recursive calls with no reduction in problem size → O(2ⁿ).

**Dropping lower-order terms**: `O(n² + n)` is just `O(n²)`. At n = 1,000,000 the n² term contributes a trillion and the n term a million — the smaller one is a rounding error. Keep only the fastest-growing term.

**Watch the hidden work.** `if x in some_list` inside a loop is O(n²), not O(n), because `in` on a list is itself a loop. Count the cost of the *body*, not the lines of it — see [[01-loops-and-what-they-cost|loops and what they cost]].

## Recursive complexity

Loops you can count directly. Recursion needs one extra step: write down the **recurrence** — the cost of a call expressed in terms of smaller calls — then solve it.

```
T(n) = (number of recursive calls) × T(smaller size) + (work done outside the calls)
```

**Merge sort** splits in half, recurses twice, and merges in linear time:

```
T(n) = 2·T(n/2) + O(n)
```

Draw the recursion tree. Each level does O(n) total work (the merges at that level cover every element once), and halving takes log n levels to bottom out. **n work × log n levels = O(n log n).**

```
level 0:            [ n ]                  n work
level 1:       [n/2]     [n/2]             n work
level 2:    [n/4][n/4] [n/4][n/4]          n work
   ...                                     ... log n levels
                                          ─────────
                                          n log n
```

**Binary search** recurses into only one half:

```
T(n) = T(n/2) + O(1)      ->   O(log n)
```

One node per level, log n levels, constant work each.

**Naive Fibonacci** branches twice and shrinks by one:

```python
def fib(n):                  # O(2ⁿ) — two calls per call, nothing reused
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

Two calls per level and n levels deep gives roughly 2ⁿ nodes. The recursion tree recomputes `fib(3)` an exponential number of times, which is precisely the redundancy [[15-dynamic-programming|dynamic programming]] exists to remove — memoising takes the same function to O(n).

**The Master Theorem** is the general shortcut for `T(n) = a·T(n/b) + O(nᵈ)` — compare `d` against `log_b(a)`: the larger side wins, and they tie into an extra log factor. Worth knowing exists; in practice, sketching the recursion tree gets you the answer faster for the handful of recurrences that actually come up.

## Space complexity

The same notation applied to memory. The distinction that matters:

- **Auxiliary space** — extra memory beyond the input. Usually what "space complexity" means.
- **Total space** — auxiliary plus the input itself.

Quote auxiliary unless you say otherwise, and say which you mean when it's ambiguous. **In-place** means O(1) auxiliary space — the algorithm rearranges the input rather than building a copy.

**The call stack is space, and it's the cost people forget.** A function that recurses `n` deep uses O(n) memory even if it allocates nothing explicitly, because every pending call keeps its frame. This is why recursion isn't free, and why [[02-dfs|DFS]] on a deep or unbalanced structure can blow the stack where an iterative version with an explicit stack survives — same O(n) space on paper, but the heap is far larger than the stack and doesn't take the process down when it fills.

Recursion depth is what counts, not the number of calls. Merge sort makes O(n) calls total but is only ever O(log n) deep, so its stack cost is O(log n) — with O(n) for the merge buffers dominating anyway.

**Time and space genuinely trade off.** Memoisation buys time with memory. [[01-prefix-sum|Prefix sums]] spend O(n) space to make range queries O(1). A [[03-hash-maps|hash map]] turns an O(n) scan into an O(1) lookup by storing every key. "Can I afford more memory?" is a real design question, and on constrained hardware the answer is often no.

## Amortized complexity

**Amortized cost is the average cost per operation across a long sequence of operations on the same structure**, when an occasional expensive operation is paid for by many cheap ones.

It is **not** average-case complexity, and conflating them is a classic error:

- **Average case** — averaged over *different possible inputs*, using assumptions about how likely each is. Probabilistic.
- **Amortized** — averaged over a *sequence of operations*, guaranteed by the structure's own mechanics. Not probabilistic at all: it's a worst-case guarantee about the total.

[[02-dynamic-arrays|Dynamic array]] append is the standard example. Usually it writes to a free slot — O(1). Occasionally the array is full and must be reallocated and every element copied — O(n). Yet append is **O(1) amortized**, and the reason is the doubling:

Appending `n` items triggers resizes at capacity 1, 2, 4, 8, …, n, copying `1 + 2 + 4 + … + n` elements. That geometric series sums to **less than 2n** — so all the copying across `n` appends costs O(n) total, or **O(1) per append averaged out**. Every element is copied a constant number of times on average, and it's guaranteed rather than probable.

**This is why growth must be multiplicative.** Grow by a fixed +1 instead of ×2 and every append copies everything: `1 + 2 + 3 + … + n` = n²/2, giving O(n) amortized per append and O(n²) to build the list. The doubling *is* the amortization.

The caveat worth remembering: amortized O(1) means the *total* is bounded, not that any individual call is fast. One unlucky append still stalls for O(n) while it copies — which matters for latency-sensitive and real-time code, where a predictable O(log n) can beat an amortized O(1) with an occasional long pause.

## Reading a constraint and guessing the expected complexity

A reflex worth building, especially under time pressure. Most machines do roughly **10⁸ operations per second**, and problems usually allow 1–10 seconds — so the **input constraint alone tells you the intended complexity**, before you've worked out an approach:

| If n is around... | Expected complexity |
|---|---|
| ≤ 12 | O(n!) — permutations are fine |
| ≤ 25 | O(2ⁿ) — subsets, brute-force recursion |
| ≤ 500 | O(n³) |
| ≤ 10,000 | O(n²) |
| ≤ 1,000,000 | O(n log n) or O(n) |
| > 10,000,000 | O(n) or O(log n) — you can barely afford to read the input |

Seeing `n ≤ 1,000,000` and reaching for a nested loop is the constraint telling you it won't finish. Read it in reverse too: `n ≤ 20` is a strong hint that **exponential is expected** and you should stop hunting for a clever polynomial solution that may not exist.

Rough guides, not guarantees — constant factors vary — but a genuinely useful check on whether your approach is in the right ballpark.

## Gotchas

- **Big-O describes growth, not speed.** An O(n²) algorithm can beat an O(n log n) one for small `n`, because the dropped constants still cost real time at small scale. Insertion sort beats quicksort under ~20 elements, which is why production sorts like Timsort switch to it for small runs.
- **O is an upper bound, not a promise of tightness.** Everything O(n) is also O(n²). Use Θ when you mean exactly.
- **"O(n) space" almost always means auxiliary space.** Be explicit when it matters.
- **Amortized ≠ average case.** One is about a sequence of operations, the other about a distribution of inputs.
- **Complexity is in terms of *something*** — say what. "O(n)" is meaningless when there are two inputs; is it the array length or the string length? Graph work quotes O(V + E) for exactly this reason.
- **Don't drop a variable because it looks small.** O(n·m) is not O(n²) and not O(n); if the inputs can differ, keep both.
- **The constant can matter.** Two O(n) algorithms where one makes three passes and the other one is a 3× difference that Big-O deliberately ignores and your latency budget doesn't.

## Related
- [[01-loops-and-what-they-cost|loops and what they cost]] — the counting this note formalises; read it first
- [[02-dynamic-arrays|dynamic-arrays]] — amortized analysis in the concrete
- [[04-sorting|sorting]] — where O(n log n) vs O(n²) shows up most visibly, and the comparison-sort lower bound
- [[02-dfs|dfs]] — recursive space complexity and stack depth
- [[15-dynamic-programming|dynamic-programming]] — trading space for time to kill exponential recomputation
- [[foundations/theory-of-computation/README|theory of computation]] — what's provably hard, one level up from what's merely slow
