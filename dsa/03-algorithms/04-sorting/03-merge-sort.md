# Module: Merge Sort

**[Intermediate]** — divide and conquer, guaranteed $O(n\log n)$, stable, and the only one here that works when the data does not fit in memory.

## Before you start

- You know the lower bound and what stable means — [[01-the-lower-bound|the lower bound]].
- You can trace a recursive call — [[09-recursion-and-the-call-stack|recursion and the call stack]].

**After this lesson you will be able to:**

1. Implement merge sort and explain the **merge** step, which is where all the work happens.
2. Derive its $O(n\log n)$ cost from the recursion tree.
3. Explain why it is **stable**, and exactly which comparison operator that depends on.
4. Explain **external** merge sort, and why it is what you use for data larger than RAM.

**Study route:** read 1–4, attempt the prediction in section 3, then run the lab.

---

## 1. Why this exists

The elementary sorts are quadratic because each element is compared against many others. Merge sort attacks that by splitting: sort two halves independently, then combine them.

The combine step is the insight. **Merging two already-sorted lists is linear** — walk both with one pointer each, always taking the smaller head. No element is ever compared twice against the same one, because progress is made on every comparison.

That gives the guarantee no other common sort provides: $O(n\log n)$ in the **worst** case, not just on average. Quicksort is usually faster in practice and can degrade to $O(n^2)$; merge sort cannot.

## 2. The mechanism

```
        [38, 27, 43, 3, 9, 82, 10]
       /                          \
  [38, 27, 43]                [3, 9, 82, 10]
    /       \                  /          \
 [38]    [27, 43]          [3, 9]      [82, 10]
          /    \            /   \        /    \
       [27]   [43]       [3]   [9]    [82]   [10]

  then merge back up, each merge linear in its two inputs:
       [27, 43]                [3, 9]      [10, 82]
  [27, 38, 43]                [3, 9, 10, 82]
        [3, 9, 10, 27, 38, 43, 82]
```

**The cost, from the tree.** Each level does $O(n)$ total work — every element is touched once per level during merging. The tree has $\log_2 n$ levels, since the size halves each time. So the total is $O(n\log n)$, and this holds for *every* input because the split is by position, not by value.

That last point is what separates it from quicksort, whose split depends on the data and can therefore be unbalanced.

### Why it is stable

In the merge, when the two heads are **equal**, take from the **left**:

```python
if left[i] <= right[j]:      # <= not <, and this is the whole reason
    out.append(left[i])
```

The left half came first in the original array, so preferring it preserves the original relative order. Change `<=` to `<` and the sort becomes unstable — a one-character difference with a real consequence. The lab demonstrates exactly this.

> [!TIP]
> **Predict before section 3.** Merge sort needs a temporary array. If you allocate a fresh one inside every recursive call rather than reusing a single buffer, does the asymptotic complexity change? What about the actual running time? Decide before opening the answers.

## 3. External merge sort

You have 100 GB to sort and 8 GB of RAM. No in-memory algorithm applies.

Merge sort does, because **merging reads sequentially**. The algorithm:

1. Read as much as fits — say 8 GB — sort it in memory, write it out as a sorted *run*. Repeat until the input is consumed. That gives about 13 runs.
2. Open all 13 runs at once and do a **$k$-way merge**: repeatedly take the smallest head across all runs, writing the result out. A [[08-heaps|min-heap]] over the run heads makes each step $O(\log k)$.

Every access is sequential, which matters enormously on disk — sequential reads are orders of magnitude faster than random ones, and this is exactly why quicksort, which jumps around during partitioning, is not used here.

This is what a database does for a large `ORDER BY` that cannot use an index, and what `sort(1)` does on a large file.

## 4. Worked example — runnable

**Runnable example:** save as `merge_sort.py` in any empty directory and run `python3 merge_sort.py`. Standard library only; writes no files.

```python
"""Merge sort: the recursion tree, stability, and a k-way external merge."""
import heapq
import math
import random


class Counter:
    def __init__(self):
        self.comparisons = 0
        self.writes = 0
        self.depth = 0


def merge(left, right, c, stable=True):
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        c.comparisons += 1
        take_left = (left[i] <= right[j]) if stable else (left[i] < right[j])
        if take_left:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
        c.writes += 1
    out.extend(left[i:]); out.extend(right[j:])
    c.writes += len(left) - i + len(right) - j
    return out


def merge_sort(xs, c=None, stable=True, depth=0):
    c = c or Counter()
    c.depth = max(c.depth, depth)
    if len(xs) <= 1:
        return xs, c
    mid = len(xs) // 2
    left, _ = merge_sort(xs[:mid], c, stable, depth + 1)
    right, _ = merge_sort(xs[mid:], c, stable, depth + 1)
    return merge(left, right, c, stable), c


class Item:
    """Compares on key only, so ties cannot silently break on anything else."""

    def __init__(self, key, tag):
        self.key, self.tag = key, tag

    def __lt__(self, other):
        return self.key < other.key

    def __le__(self, other):
        return self.key <= other.key

    def __repr__(self):
        return f"{self.key}{self.tag}"


def external_merge_sort(data, memory):
    """Sort a stream larger than 'memory' by making runs, then k-way merging."""
    runs = []
    for start in range(0, len(data), memory):
        runs.append(sorted(data[start:start + memory]))     # one in-memory sort per run
    merged, reads = [], 0
    heap = [(run[0], ri, 0) for ri, run in enumerate(runs)]
    heapq.heapify(heap)
    while heap:
        val, ri, i = heapq.heappop(heap)
        merged.append(val)
        reads += 1
        if i + 1 < len(runs[ri]):
            heapq.heappush(heap, (runs[ri][i + 1], ri, i + 1))
    return merged, len(runs), reads


if __name__ == "__main__":
    print("Block 1 - correctness, and the recursion depth is log2(n)")
    rng = random.Random(20260910)
    for _ in range(300):
        n = rng.randint(0, 40)
        data = [rng.randint(-30, 30) for _ in range(n)]
        out, _ = merge_sort(data)
        assert out == sorted(data)
    print("  correct on 300 random arrays")
    print("       n    recursion depth    ceil(log2 n)")
    for n in (1, 2, 8, 100, 1000):
        _, c = merge_sort(list(range(n, 0, -1)))
        print(f"  {n:6}    {c.depth:15}    {math.ceil(math.log2(max(n,1))):12}")
        assert c.depth <= math.ceil(math.log2(max(n, 1))) + 1

    print()
    print("Block 2 - the cost is the same whatever the input")
    N = 512
    shapes = {
        "sorted  ": list(range(N)),
        "reversed": list(range(N, 0, -1)),
        "random  ": [rng.randint(0, N) for _ in range(N)],
        "all equal": [7] * N,
    }
    print("   input       comparisons   writes   n*log2(n)")
    for label, data in shapes.items():
        _, c = merge_sort(data)
        print(f"   {label}   {c.comparisons:11,}   {c.writes:6,}   {N*math.log2(N):9.0f}")
    _, c_rand = merge_sort(shapes["random  "])
    _, c_rev = merge_sort(shapes["reversed"])
    assert c_rand.writes == c_rev.writes, "writes are input-independent"
    print("  the WRITE count is identical for every input: the split is by position,")
    print("  never by value, so the recursion tree has the same shape every time")
    print("  (comparisons vary a little, because a merge can exhaust one side early)")

    print()
    print("Block 3 - stability hangs on one character")
    demo = [Item(1, "a"), Item(1, "b"), Item(0, "c"), Item(1, "d"), Item(0, "e")]
    print(f"  input:              {demo}")
    stable_out, _ = merge_sort(demo, stable=True)
    unstable_out, _ = merge_sort(demo, stable=False)
    print(f"  merge with '<=':    {stable_out}   <- stable")
    print(f"  merge with '<' :    {unstable_out}   <- NOT stable")
    assert [it.tag for it in stable_out if it.key == 1] == ["a", "b", "d"]
    assert [it.tag for it in unstable_out if it.key == 1] != ["a", "b", "d"]
    print("  taking from the LEFT on ties is what preserves the original order")

    print()
    print("Block 4 - external merge sort: 10,000 items through 1,000 of memory")
    big = [rng.randint(0, 100000) for _ in range(10000)]
    MEM = 1000
    out, n_runs, reads = external_merge_sort(big, MEM)
    print(f"  memory holds {MEM:,} items, input is {len(big):,}")
    print(f"    -> {n_runs} sorted runs written, then a {n_runs}-way merge")
    print(f"    -> {reads:,} sequential reads during the merge")
    assert out == sorted(big)
    assert n_runs == math.ceil(len(big) / MEM)
    print(f"  result is fully sorted, and no more than {MEM:,} items were ever in memory")
    print(f"  each merge step costs O(log {n_runs}) via the heap, not O({n_runs})")

    print()
    print("merge_sort: passed")
```

Expected output:

```
Block 1 - correctness, and the recursion depth is log2(n)
  correct on 300 random arrays
       n    recursion depth    ceil(log2 n)
       1                  0               0
       2                  1               1
       8                  3               3
     100                  7               7
    1000                 10              10

Block 2 - the cost is the same whatever the input
   input       comparisons   writes   n*log2(n)
   sorted           2,304    4,608        4608
   reversed         2,304    4,608        4608
   random           3,979    4,608        4608
   all equal         2,304    4,608        4608
  the WRITE count is identical for every input: the split is by position,
  never by value, so the recursion tree has the same shape every time
  (comparisons vary a little, because a merge can exhaust one side early)

Block 3 - stability hangs on one character
  input:              [1a, 1b, 0c, 1d, 0e]
  merge with '<=':    [0c, 0e, 1a, 1b, 1d]   <- stable
  merge with '<' :    [0e, 0c, 1d, 1b, 1a]   <- NOT stable
  taking from the LEFT on ties is what preserves the original order

Block 4 - external merge sort: 10,000 items through 1,000 of memory
  memory holds 1,000 items, input is 10,000
    -> 10 sorted runs written, then a 10-way merge
    -> 10,000 sequential reads during the merge
  result is fully sorted, and no more than 1,000 items were ever in memory
  each merge step costs O(log 10) via the heap, not O(10)

merge_sort: passed
```

Block 2 is the guarantee, visible: the write count is **identical** for sorted, reversed, random and all-equal input. Nothing about the data can make merge sort slow, because the split never looks at the values.

## Common pitfalls and traps

- **Using `<` instead of `<=` in the merge.** Silently destroys stability. Block 3 shows both.
- **Allocating a new temporary on every merge.** Correct but wasteful: it makes the constant much worse and stresses the allocator. Real implementations allocate one buffer of size $n$ up front.
- **Forgetting the tail copy.** When one side is exhausted, the rest of the other must still be appended. Omitting it silently drops elements.
- **Expecting it to be in-place.** Standard merge sort needs $O(n)$ extra. In-place variants exist and are markedly slower and much more complex.
- **Using it on small arrays.** Below about 16 elements, insertion sort wins on constants. Timsort switches for exactly this reason.
- **Assuming linked lists behave the same.** Merge sort on a linked list *is* effectively in-place — you relink nodes instead of copying — which makes it the standard choice there.

## Check your understanding

1. Why is merge sort $O(n\log n)$ in the worst case and not just on average?
2. What is the space complexity, and why?
3. Which comparison operator preserves stability, and why that one?
4. Why is merge sort preferred for external sorting?
5. Why is merge sort the usual choice for sorting a linked list?

<details><summary>Answers — open only after an attempt</summary>

1. Because the array is split **by position**, always into halves. The recursion tree therefore has $\log_2 n$ levels regardless of the values, and each level does $O(n)$ merging work. No input can unbalance it.
2. $O(n)$ — the merge cannot be done in place without a large slowdown, so it needs a temporary buffer the size of the input. (Plus $O(\log n)$ of call stack.)
3. `<=` — take from the **left** when the heads are equal. The left half held the earlier elements, so preferring it preserves their original relative order.
4. Because merging accesses every run **sequentially**, which is what disks and network storage are fast at. Quicksort's partitioning jumps around, which is catastrophic on external storage.
5. Because merging linked lists requires only pointer relinking, not copying — so it needs $O(1)$ extra space rather than $O(n)$. And linked lists cannot do the random access that quicksort's partitioning needs.

**And the prediction from section 2:** the **asymptotic complexity does not change** — it is still $O(n\log n)$ time and $O(n)$ peak space. But the **actual running time gets noticeably worse**: you perform $O(n)$ allocations instead of one, and allocation is expensive relative to a comparison. This is a case where the notation hides something that matters.
</details>

## Practice — independent task

Implement **Timsort's core idea**: exploit runs that are already sorted.

1. Write `find_runs(xs)` that scans once and returns the maximal already-sorted stretches, reversing any strictly-descending run in place so it becomes ascending.
2. Merge the runs pairwise until one remains. Assert the result equals `sorted()`.
3. **Extend short runs.** If a natural run is shorter than some `minrun` (Timsort uses 32–64), extend it with binary insertion sort until it reaches that length. Explain in a comment why this helps.
4. Measure comparisons against plain merge sort on: fully random data; already-sorted data; reverse-sorted data; and data made of a handful of long sorted runs concatenated.
5. **The fourth case is the point.** Show that your run-aware version does dramatically fewer comparisons there, and state roughly how much. Then explain why random data shows almost no improvement.

**Edge cases:** an array that is entirely one run; strictly descending input (your reversal must keep the sort **stable** — reversing a run with equal elements breaks stability, so reverse only *strictly* descending runs, and explain why).

**Done when:** your run-aware sort is correct and stable on every test, the concatenated-runs case shows a large comparison reduction, and you can explain the strictly-descending subtlety in step 5's edge case.

## Before moving on

You can implement merge sort, derive its cost from the recursion tree, explain its stability, and describe external sorting.

**Recap:** split by position into halves, sort each, merge linearly; $O(n\log n)$ **worst case** because the split never depends on the data; $O(n)$ extra space; stable if the merge takes from the left on ties (`<=`); the basis of external sorting via sorted runs plus a $k$-way heap merge; the natural choice for linked lists.

**Next:** [[04-quicksort|Quicksort]] — usually faster, in-place, and with a worst case you must actively prevent.

## Related

- [[01-the-lower-bound|The Lower Bound]] — merge sort essentially meets it
- [[08-heaps|Heaps]] — the $k$-way merge's engine
- [[04-linked-lists|Linked Lists]] — where merge sort becomes in-place
