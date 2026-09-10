# Module: Quicksort

**[Advanced]** — usually the fastest comparison sort, in-place, and carrying an $O(n^2)$ worst case you must actively prevent.

## Before you start

- You know merge sort and the recursion-tree argument — [[03-merge-sort|merge sort]].
- You know what in-place and stable mean — [[01-the-lower-bound|the lower bound]].

**After this lesson you will be able to:**

1. Implement **Lomuto** and **Hoare** partitioning, and say why Hoare is the one libraries use.
2. Explain the $O(n^2)$ worst case, **trigger it deliberately**, and prevent it.
3. Explain why quicksort is not stable, and why it is still the default in most libraries.
4. Handle the duplicate-keys trap with **three-way partitioning**.

**Study route:** read 1–4, attempt the prediction in section 3, then run the lab. Block 3 breaks the naive version on purpose.

---

## 1. Why this exists

Merge sort guarantees $O(n\log n)$ and needs $O(n)$ extra memory. Quicksort has the same average cost, needs only $O(\log n)$ of stack, and in practice runs faster despite doing a similar number of comparisons.

The reason is memory, not operation count. Partitioning sweeps the array **sequentially** and swaps in place, which is friendly to CPU caches and prefetchers. Merge sort copies into and out of a separate buffer, doubling memory traffic. Constants win.

The price is a genuine worst case. Merge sort's split is by position and cannot be unbalanced; quicksort's split is by **value**, so an adversarial or merely unlucky input can make every partition maximally lopsided, giving $O(n^2)$.

## 2. Partitioning

Choose a **pivot**. Rearrange so everything smaller is left of it and everything larger is right. The pivot is now in its final position. Recurse on both sides.

### Lomuto (simpler, slower)

Pivot is the last element. Walk with `i` marking the boundary of the "smaller" region.

```python
def lomuto(a, lo, hi):
    pivot = a[hi]
    i = lo - 1
    for j in range(lo, hi):
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
    a[i + 1], a[hi] = a[hi], a[i + 1]
    return i + 1
```

Easy to get right, and it degrades badly on arrays of **equal elements**: every element satisfies `<= pivot`, so every partition is maximally lopsided and the sort goes quadratic on input that is already trivially sorted.

### Hoare (the one that is used)

Two pointers move towards each other, swapping out-of-place pairs.

Hoare does about **three times fewer swaps** on average and handles duplicates far better, because elements equal to the pivot can end up on either side, which keeps partitions balanced. Its index handling is fiddlier, which is the only reason Lomuto is taught first.

## 3. The worst case, and preventing it

The recursion depth is what matters:

- **Balanced** splits give depth $\log_2 n$ and $O(n\log n)$.
- **Maximally lopsided** splits — one side empty every time — give depth $n$ and $O(n^2)$.

With a **last-element pivot**, already-sorted input is the worst case: the pivot is always the maximum, so one side gets everything. That is not a rare adversarial input; it is the most common input shape there is.

**The fixes, in order of what libraries actually do:**

| Fix | What it does |
| :--- | :--- |
| **Median-of-three** | Pivot on the median of first, middle and last — kills the sorted-input case cheaply |
| **Randomised pivot** | No fixed input is worst-case; an adversary cannot predict it |
| **Introsort** | Count recursion depth; past $2\log n$, switch to **heapsort** — a hard $O(n\log n)$ ceiling |
| **Three-way partition** | Split into `< = >`; makes arrays of duplicates linear |
| **Insertion sort below ~16** | Better constants on the small partitions |

`std::sort` in C++ is introsort with all of these. That is why the standard library never exhibits the worst case even though the underlying algorithm has one.

> [!TIP]
> **Predict before running the lab.** With a last-element pivot, which input is worse: a random array, a reverse-sorted array, or an array where every element is identical? Rank all three before opening the answers.

## 4. Why it is not stable

Partitioning swaps elements across long distances. Two equal elements can be exchanged with each other or jumped past one another, and their original order is lost.

Making it stable requires extra space, which surrenders quicksort's main advantage. So libraries offer a choice: `sort` (quicksort-family, unstable, fast) and `stable_sort` (merge-family, stable, $O(n)$ memory). Python's `list.sort` is Timsort and always stable, which is a deliberate different trade.

## Worked example — runnable

**Runnable example:** save as `quicksort.py` in any empty directory and run `python3 quicksort.py`. Standard library only; writes no files.

```python
"""Quicksort: two partition schemes, the worst case, and how to prevent it."""
import random
import sys

sys.setrecursionlimit(30000)


class Counter:
    def __init__(self):
        self.comparisons = 0
        self.swaps = 0
        self.depth = 0


def lomuto(a, lo, hi, c):
    pivot = a[hi]
    i = lo - 1
    for j in range(lo, hi):
        c.comparisons += 1
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
            c.swaps += 1
    a[i + 1], a[hi] = a[hi], a[i + 1]
    c.swaps += 1
    return i + 1


def hoare(a, lo, hi, c):
    pivot = a[(lo + hi) // 2]
    i, j = lo - 1, hi + 1
    while True:
        i += 1
        while a[i] < pivot:
            c.comparisons += 1
            i += 1
        c.comparisons += 1
        j -= 1
        while a[j] > pivot:
            c.comparisons += 1
            j -= 1
        c.comparisons += 1
        if i >= j:
            return j
        a[i], a[j] = a[j], a[i]
        c.swaps += 1


def quicksort(a, scheme=lomuto, lo=0, hi=None, c=None, depth=0):
    c = c or Counter()
    hi = len(a) - 1 if hi is None else hi
    c.depth = max(c.depth, depth)
    if lo < hi:
        if scheme is lomuto:
            p = lomuto(a, lo, hi, c)
            quicksort(a, scheme, lo, p - 1, c, depth + 1)
            quicksort(a, scheme, p + 1, hi, c, depth + 1)
        else:
            p = hoare(a, lo, hi, c)
            quicksort(a, scheme, lo, p, c, depth + 1)
            quicksort(a, scheme, p + 1, hi, c, depth + 1)
    return a, c


def median_of_three(a, lo, hi, c):
    mid = (lo + hi) // 2
    trio = sorted([(a[lo], lo), (a[mid], mid), (a[hi], hi)])
    _, m = trio[1]
    a[m], a[hi] = a[hi], a[m]
    c.swaps += 1
    return lomuto(a, lo, hi, c)


def quicksort_m3(a, lo=0, hi=None, c=None, depth=0):
    c = c or Counter()
    hi = len(a) - 1 if hi is None else hi
    c.depth = max(c.depth, depth)
    if lo < hi:
        p = median_of_three(a, lo, hi, c)
        quicksort_m3(a, lo, p - 1, c, depth + 1)
        quicksort_m3(a, p + 1, hi, c, depth + 1)
    return a, c


def quicksort3(a, lo=0, hi=None, c=None, depth=0):
    """Three-way partition: < pivot, == pivot, > pivot."""
    c = c or Counter()
    hi = len(a) - 1 if hi is None else hi
    c.depth = max(c.depth, depth)
    if lo >= hi:
        return a, c
    pivot = a[(lo + hi) // 2]
    lt, i, gt = lo, lo, hi
    while i <= gt:
        c.comparisons += 1
        if a[i] < pivot:
            a[lt], a[i] = a[i], a[lt]
            c.swaps += 1
            lt += 1; i += 1
        elif a[i] > pivot:
            a[gt], a[i] = a[i], a[gt]
            c.swaps += 1
            gt -= 1
        else:
            i += 1
    quicksort3(a, lo, lt - 1, c, depth + 1)
    quicksort3(a, gt + 1, hi, c, depth + 1)
    return a, c


if __name__ == "__main__":
    rng = random.Random(20260910)

    print("Block 1 - both schemes are correct")
    for name, scheme in [("lomuto", lomuto), ("hoare", hoare)]:
        for _ in range(300):
            n = rng.randint(0, 40)
            data = [rng.randint(-20, 20) for _ in range(n)]
            out, _ = quicksort(list(data), scheme)
            assert out == sorted(data), (name, data)
        print(f"  {name:8} correct on 300 random arrays")

    print()
    print("Block 2 - Hoare does far fewer swaps than Lomuto")
    N = 500
    data = [rng.randint(0, N) for _ in range(N)]
    for name, scheme in [("lomuto", lomuto), ("hoare", hoare)]:
        _, c = quicksort(list(data), scheme)
        print(f"  {name:8} comparisons {c.comparisons:7,}   swaps {c.swaps:7,}"
              f"   depth {c.depth}")
    _, cl = quicksort(list(data), lomuto)
    _, ch = quicksort(list(data), hoare)
    assert ch.swaps < cl.swaps
    print(f"  Hoare uses {cl.swaps/ch.swaps:.1f}x fewer swaps on the same input")

    print()
    print("Block 3 - the worst case, triggered on purpose (last-element pivot)")
    print("      input            n    comparisons   recursion depth   n^2/2")
    for label, make in [("random  ", lambda n: [rng.randint(0, n) for _ in range(n)]),
                        ("sorted  ", lambda n: list(range(n))),
                        ("reversed", lambda n: list(range(n, 0, -1))),
                        ("all equal", lambda n: [5] * n)]:
        n = 400
        _, c = quicksort(make(n), lomuto)
        print(f"   {label}   {n:6}   {c.comparisons:11,}   {c.depth:15}   {n*n//2:7,}")
    _, c_sorted = quicksort(list(range(400)), lomuto)
    _, c_random = quicksort([rng.randint(0, 400) for _ in range(400)], lomuto)
    assert c_sorted.depth > 300, "sorted input drives the recursion linear"
    assert c_sorted.comparisons > 10 * c_random.comparisons
    print("  sorted input is the WORST case for a last-element pivot: the pivot is")
    print("  always the maximum, so one side of every partition is empty.")
    print("  All-equal input is just as bad for Lomuto: every element is <= the pivot.")

    print()
    print("Block 4 - median-of-three fixes the sorted case")
    print("      input        naive comparisons   naive depth   m3 comparisons   m3 depth")
    for label, make in [("sorted  ", lambda n: list(range(n))),
                        ("reversed", lambda n: list(range(n, 0, -1)))]:
        n = 400
        _, cn = quicksort(make(n), lomuto)
        _, cm = quicksort_m3(make(n))
        print(f"   {label}    {cn.comparisons:17,}   {cn.depth:11}   "
              f"{cm.comparisons:14,}   {cm.depth:8}")
    _, cm = quicksort_m3(list(range(400)))
    assert cm.depth < 20, "median-of-three keeps the recursion logarithmic"
    print("  depth drops from ~400 to under 20: the recursion is logarithmic again")

    print()
    print("Block 5 - three-way partitioning makes duplicates linear")
    print("      distinct values      2-way comparisons   3-way comparisons")
    n = 2000
    for distinct in (2, 10, 100, 2000):
        data = [rng.randint(0, distinct - 1) for _ in range(n)]
        _, c2 = quicksort(list(data), hoare)
        _, c3 = quicksort3(list(data))
        print(f"   {distinct:15}      {c2.comparisons:17,}   {c3.comparisons:17,}")
    data = [rng.randint(0, 1) for _ in range(n)]
    _, c2 = quicksort(list(data), hoare)
    _, c3 = quicksort3(list(data))
    assert c3.comparisons < c2.comparisons
    assert sorted(quicksort3(list(data))[0]) == sorted(data)
    print("  with few distinct values the 3-way version does far less work, because")
    print("  everything equal to the pivot is finished in a single pass")

    print()
    print("Block 6 - quicksort is not stable")
    class Item:
        def __init__(self, key, tag):
            self.key, self.tag = key, tag
        def __lt__(self, o): return self.key < o.key
        def __le__(self, o): return self.key <= o.key
        def __gt__(self, o): return self.key > o.key
        def __repr__(self): return f"{self.key}{self.tag}"

    demo = [Item(1, "a"), Item(1, "b"), Item(0, "c"), Item(1, "d"), Item(0, "e")]
    out, _ = quicksort(list(demo), lomuto)
    print(f"  input:     {demo}")
    print(f"  quicksort: {out}")
    tags = [it.tag for it in out if it.key == 1]
    print(f"  the 1s came out in order {tags}, not ['a','b','d']")
    assert tags != ["a", "b", "d"]
    print("  partitioning swaps across long distances, so equal elements get reordered")

    print()
    print("quicksort: passed")
```

Expected output:

```
Block 1 - both schemes are correct
  lomuto   correct on 300 random arrays
  hoare    correct on 300 random arrays

Block 2 - Hoare does far fewer swaps than Lomuto
  lomuto   comparisons   5,444   swaps   2,735   depth 23
  hoare    comparisons   6,484   swaps   1,133   depth 21
  Hoare uses 2.4x fewer swaps on the same input

Block 3 - the worst case, triggered on purpose (last-element pivot)
      input            n    comparisons   recursion depth   n^2/2
   random        400         3,420                16    80,000
   sorted        400        79,800               399    80,000
   reversed      400        79,800               399    80,000
   all equal      400        79,800               399    80,000
  sorted input is the WORST case for a last-element pivot: the pivot is
  always the maximum, so one side of every partition is empty.
  All-equal input is just as bad for Lomuto: every element is <= the pivot.

Block 4 - median-of-three fixes the sorted case
      input        naive comparisons   naive depth   m3 comparisons   m3 depth
   sorted                 79,800           399            2,698          8
   reversed               79,800           399            4,502         17
  depth drops from ~400 to under 20: the recursion is logarithmic again

Block 5 - three-way partitioning makes duplicates linear
      distinct values      2-way comparisons   3-way comparisons
                 2                 26,108               2,999
                10                 26,658               6,042
               100                 31,396              16,114
              2000                 31,996              23,582
  with few distinct values the 3-way version does far less work, because
  everything equal to the pivot is finished in a single pass

Block 6 - quicksort is not stable
  input:     [1a, 1b, 0c, 1d, 0e]
  quicksort: [0c, 0e, 1a, 1d, 1b]
  the 1s came out in order ['a', 'd', 'b'], not ['a','b','d']
  partitioning swaps across long distances, so equal elements get reordered

quicksort: passed
```

Block 3 is the point of the lesson: the naive version is not slow on *weird* input, it is slow on **sorted** input — the single most common shape real data arrives in. Block 4 shows a three-line change fixing it.

## Common pitfalls and traps

- **Shipping a last-element pivot.** Sorted or nearly-sorted input is extremely common, and it is precisely the worst case. Use median-of-three or randomise.
- **Lomuto on duplicate-heavy data.** Every element is `<=` the pivot, so partitions are maximally lopsided. Use Hoare, or three-way.
- **Off-by-one in Hoare's return.** Hoare returns `j` and recurses on `[lo, j]` and `[j+1, hi]` — **not** `[lo, j-1]`. Getting this wrong causes infinite recursion.
- **Expecting stability.** It is not stable, and making it so costs the memory advantage.
- **Ignoring stack depth.** Worst-case recursion is $O(n)$ deep and can blow the stack. Recurse into the smaller side and loop on the larger, capping depth at $O(\log n)$.
- **Assuming randomisation makes the worst case impossible.** It makes it *improbable* and input-independent. It is still reachable, just not by an adversary choosing the input.

## Check your understanding

1. Why is quicksort usually faster than merge sort despite the same average complexity?
2. What input is worst-case for a last-element pivot, and why?
3. Why does Lomuto degrade on all-equal input while three-way partitioning does not?
4. What does introsort do, and what does it guarantee?
5. Why is quicksort not stable?

<details><summary>Answers — open only after an attempt</summary>

1. **Memory behaviour.** It partitions in place with sequential scans, which suits caches and prefetchers, while merge sort copies into and out of a separate $O(n)$ buffer. The comparison counts are similar; the memory traffic is not.
2. **Already-sorted input.** The last element is always the maximum, so every partition puts $n-1$ elements on one side and none on the other. Depth becomes $n$ and cost $O(n^2)$.
3. Lomuto tests `a[j] <= pivot`, which is true for **every** element when all are equal, so the partition point lands at one end each time. Three-way partitioning collects everything equal to the pivot into a middle band and never recurses into it, so identical elements are finished in one pass.
4. It runs quicksort while tracking recursion depth, and switches to **heapsort** once depth exceeds about $2\log n$. That gives a hard $O(n\log n)$ worst-case guarantee while keeping quicksort's speed in the normal case.
5. Because partitioning swaps elements across long distances, so two equal elements can be reordered relative to each other. Preserving order would need extra space, which removes its main advantage over merge sort.

**And the prediction from section 3:** with a last-element pivot, **sorted and all-equal are both worst case** ($O(n^2)$), and **random is by far the best** of the three. Reverse-sorted is also quadratic with Lomuto. The lab measures all four: sorted and all-equal both hit roughly $n^2/2$ comparisons while random stays near $n\log n$.
</details>

## Practice — independent task

Implement **quickselect** — find the $k$th smallest element without sorting.

1. Partition as in quicksort, but recurse into **only** the side containing position $k$. Average $O(n)$, not $O(n\log n)$: derive why from the sum $n + n/2 + n/4 + \cdots$
2. Implement it iteratively so it uses $O(1)$ stack.
3. Verify against `sorted(xs)[k]` on hundreds of random arrays, including duplicates and $k$ at both extremes.
4. **Count operations** and compare with sorting-then-indexing at $n = 10^4$. Report the ratio.
5. Then break it: construct input that makes naive quickselect $O(n^2)$, show the blow-up, and fix it with a random pivot. Optionally implement **median-of-medians** for a guaranteed $O(n)$, and measure how much its better guarantee costs you in the average case — this is the trade real implementations decline to make.

**Edge cases:** $k$ out of range; an empty array; all elements equal (quickselect must still terminate — check yours does); $k = 0$ and $k = n-1$.

**Done when:** quickselect matches the sorted answer every time, your operation count beats full sorting by the margin you predicted, and you can state why median-of-medians is rarely used despite its better guarantee.

## Before moving on

You can implement both partition schemes, trigger and prevent the worst case, and explain the stability and memory trades.

**Recap:** partition around a pivot, recurse both sides; average $O(n\log n)$, worst $O(n^2)$ when partitions are lopsided; last-element pivot makes **sorted input** the worst case; fix with median-of-three, randomisation, or introsort's heapsort fallback; Hoare beats Lomuto on swaps and duplicates; three-way partitioning makes duplicate-heavy input linear; not stable; $O(\log n)$ stack if you recurse into the smaller side.

**Next:** [[05-non-comparison-sorts|Non-Comparison Sorts]] — counting, radix and bucket sort, and how they get under the $\Omega(n\log n)$ bound.

## Related

- [[03-merge-sort|Merge Sort]] — the guaranteed alternative
- [[08-heaps|Heaps]] — heapsort, introsort's fallback
- [[01-the-lower-bound|The Lower Bound]] — what quicksort's average case meets
