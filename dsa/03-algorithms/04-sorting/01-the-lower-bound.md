# Module: Sorting and the $\Omega(n\log n)$ Lower Bound

**[Intermediate]** — why no comparison sort can ever beat $n\log n$, and the vocabulary the rest of the folder uses.

## Before you start

- You can read a complexity bound — [[01-algorithms|algorithms and complexity]].
- You know what an array costs to index and to shift — [[01-arrays|arrays]].

**After this lesson you will be able to:**

1. Define **stable**, **in-place**, **adaptive** and **comparison-based**, and say why each matters in practice.
2. **Prove** that any comparison sort needs $\Omega(n\log n)$ comparisons in the worst case.
3. Explain why counting sort does not contradict that proof.
4. Choose a sort from the properties a situation requires, not from a memorised ranking.

**Study route:** read 1–4, attempt the prediction in section 3, then run the lab.

---

## 1. Why this exists

Sorting is the most-studied problem in computing, and it is worth asking why a solved problem needs six algorithms.

Because "sorted" is not the only requirement. You may need the order of equal elements preserved. You may have no spare memory. You may have almost-sorted input. You may be sorting integers in a small range, or strings, or records too large to move. Each constraint rules out different algorithms, and the reason there is no single winner is that the constraints conflict.

There is also a result here that is rare and worth having: a **proof about every possible algorithm**, not just the ones we have thought of. Comparison sorting cannot be done faster than $n\log n$, and no cleverness will change that.

## 2. Terminology

| Term | Plain-English definition | Why it matters |
| :--- | :--- | :--- |
| **Comparison sort** | Decides order only by comparing pairs | The kind the lower bound applies to |
| **Stable** | Equal elements keep their original relative order | Lets you sort by one key, then another |
| **In-place** | Uses $O(1)$ or $O(\log n)$ extra space | Matters when data barely fits |
| **Adaptive** | Faster on partly-sorted input | Real data is often partly sorted |
| **Internal / external** | Fits in memory / does not | External sorting is a different problem |

**Stability, concretely.** Sort employees by name, then by department. If the second sort is stable, people stay alphabetical within each department. If it is not, the first sort was wasted. This is why `sorted()` in Python and `Arrays.sort` for objects in Java are stable, and it is the single most-overlooked property.

## 3. The lower bound

**Claim:** any comparison-based sorting algorithm needs $\Omega(n\log n)$ comparisons in the worst case.

**Proof.** Think of the algorithm as a **decision tree**. Each internal node is one comparison, with two branches for the two outcomes; each leaf is a final ordering the algorithm can output.

- To be correct, the algorithm must be able to produce **every** one of the $n!$ possible permutations. So the tree has at least $n!$ leaves.
- A binary tree of height $h$ has at most $2^h$ leaves.
- Therefore $2^h \ge n!$, so $h \ge \log_2(n!)$.

And by Stirling's approximation, $\log_2(n!) = \Theta(n\log n)$. The height $h$ is the **worst-case number of comparisons** — the longest root-to-leaf path.

$\blacksquare$

Note what the proof did **not** assume: nothing about the strategy, the data structure, or the cleverness. It applies to every comparison sort that exists or ever will.

The lab computes $\log_2(n!)$ against the comparisons that merge sort actually performs, and they track closely — merge sort is essentially optimal.

> [!TIP]
> **Predict before section 4.** Counting sort runs in $O(n + k)$ for integers in the range $0..k$ — which for small $k$ is linear, beating $n\log n$. Does that disprove the theorem? Decide before opening the answers.

## 4. The map

| Algorithm | Best | Average | Worst | Space | Stable | Adaptive |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| Bubble | $n$ | $n^2$ | $n^2$ | $1$ | ✅ | ✅ |
| Selection | $n^2$ | $n^2$ | $n^2$ | $1$ | ❌ | ❌ |
| Insertion | $n$ | $n^2$ | $n^2$ | $1$ | ✅ | ✅ |
| **Merge** | $n\log n$ | $n\log n$ | $n\log n$ | $n$ | ✅ | ❌ |
| **Quick** | $n\log n$ | $n\log n$ | $n^2$ | $\log n$ | ❌ | ❌ |
| Heap | $n\log n$ | $n\log n$ | $n\log n$ | $1$ | ❌ | ❌ |
| Counting | $n+k$ | $n+k$ | $n+k$ | $n+k$ | ✅ | ❌ |
| Radix | $nd$ | $nd$ | $nd$ | $n+k$ | ✅ | ❌ |

**What real libraries do:** almost all use a **hybrid**. Python's Timsort is merge sort exploiting existing runs, falling back to insertion sort on small pieces — stable and adaptive. C++'s `std::sort` is introsort: quicksort, switching to heapsort when recursion goes too deep, so the $n^2$ worst case cannot happen.

Both hybrids exist for the same reason: insertion sort has the smallest constant on tiny inputs, and quicksort's worst case must be prevented rather than hoped against.

## Worked example — runnable

**Runnable example:** save as `lower_bound.py` in any empty directory and run `python3 lower_bound.py`. Standard library only; writes no files.

```python
"""The comparison lower bound, and the properties that separate the sorts."""
import math
import random
from itertools import permutations


def merge_sort_counting(xs, counter):
    if len(xs) <= 1:
        return xs
    mid = len(xs) // 2
    left = merge_sort_counting(xs[:mid], counter)
    right = merge_sort_counting(xs[mid:], counter)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        counter[0] += 1
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:]); out.extend(right[j:])
    return out


def is_stable(sort_fn):
    """Sort (key, tag) pairs by key only; a stable sort keeps tags in order."""
    data = [(1, "a"), (0, "b"), (1, "c"), (0, "d"), (1, "e")]
    result = sort_fn(list(data), key=lambda p: p[0])
    for k in (0, 1):
        tags = [t for kk, t in result if kk == k]
        if tags != sorted(tags):
            return False
    return True


def insertion_sort(xs, key=lambda v: v):
    xs = list(xs)
    for i in range(1, len(xs)):
        cur, j = xs[i], i - 1
        while j >= 0 and key(xs[j]) > key(cur):
            xs[j + 1] = xs[j]
            j -= 1
        xs[j + 1] = cur
    return xs


def selection_sort(xs, key=lambda v: v):
    xs = list(xs)
    for i in range(len(xs)):
        m = min(range(i, len(xs)), key=lambda j: key(xs[j]))
        xs[i], xs[m] = xs[m], xs[i]
    return xs


if __name__ == "__main__":
    print("Block 1 - the bound is about the WORST case")
    rng = random.Random(20260910)
    print("     n     log2(n!)   merge: worst of 200 random   merge: reversed input")
    for n in (4, 8, 16, 64, 256, 1024):
        bound = math.log2(math.factorial(n))
        worst = 0
        for _ in range(200):
            perm = list(range(n))
            rng.shuffle(perm)
            c = [0]
            merge_sort_counting(perm, c)
            worst = max(worst, c[0])
        c = [0]
        merge_sort_counting(list(range(n, 0, -1)), c)
        print(f"  {n:5}   {bound:10.1f}   {worst:26}   {c[0]:21}")
        assert worst >= bound - 1, (n, worst, bound)
    print("  on random input merge sort meets the bound; on REVERSED input it does")
    print("  fewer comparisons than log2(n!) - which is not a contradiction, because")
    print("  reversed is merge sort's BEST case: every merge exhausts one side early.")
    print("  The theorem constrains the worst case, not every case.")

    print("Block 2 - why the tree must have n! leaves")
    for n in (3, 4):
        perms = list(permutations(range(n)))
        needed_height = math.ceil(math.log2(len(perms)))
        print(f"  n={n}: {len(perms)} possible orderings, so the tree needs height "
              f">= ceil(log2({len(perms)})) = {needed_height}")
        assert 2 ** needed_height >= len(perms)
    print("  any correct algorithm must be able to output every one of them,")
    print("  so no comparison sort can always finish in fewer comparisons")

    print()
    print("Block 3 - stability, demonstrated")
    data = [(1, "a"), (0, "b"), (1, "c"), (0, "d"), (1, "e")]
    print(f"  input:               {data}")
    print(f"  insertion (stable):  {insertion_sort(data, key=lambda p: p[0])}")
    print(f"  selection (unstable):{selection_sort(data, key=lambda p: p[0])}")
    assert is_stable(insertion_sort)
    assert not is_stable(selection_sort)
    print("  with insertion, the 1s stay in the order a, c, e; selection scrambles them")

    print()
    print("  why it matters - sort by one key, then another:")
    people = [("Ada", "eng"), ("Bo", "ops"), ("Cy", "eng"), ("Di", "ops")]
    by_name = insertion_sort(people, key=lambda p: p[0])
    by_dept_stable = insertion_sort(by_name, key=lambda p: p[1])
    by_dept_unstable = selection_sort(by_name, key=lambda p: p[1])
    print(f"    stable second sort:   {by_dept_stable}")
    print(f"    unstable second sort: {by_dept_unstable}")
    eng_stable = [n for n, d in by_dept_stable if d == "eng"]
    assert eng_stable == sorted(eng_stable)
    print("    only the stable one keeps names alphabetical within each department")

    print()
    print("Block 4 - adaptive: the same algorithm on sorted vs reversed input")
    print("      n    insertion on sorted   insertion on reversed")
    for n in (10, 50, 200):
        def counted(xs):
            c = [0]
            ys = list(xs)
            for i in range(1, len(ys)):
                cur, j = ys[i], i - 1
                while j >= 0 and ys[j] > cur:
                    c[0] += 1
                    ys[j + 1] = ys[j]
                    j -= 1
                ys[j + 1] = cur
            return c[0]
        s, r = counted(list(range(n))), counted(list(range(n, 0, -1)))
        print(f"  {n:5}    {s:19}   {r:21}")
        assert s == 0 and r == n * (n - 1) // 2
    print("  zero shifts on sorted input, n(n-1)/2 on reversed: that is 'adaptive'")

    print()
    print("lower_bound: passed")
```

Expected output:

```
Block 1 - the bound is about the WORST case
     n     log2(n!)   merge: worst of 200 random   merge: reversed input
      4          4.6                            5                       4
      8         15.3                           17                      12
     16         44.3                           49                      32
     64        296.0                          313                     192
    256       1684.0                         1745                    1024
   1024       8769.0                         9002                    5120
  on random input merge sort meets the bound; on REVERSED input it does
  fewer comparisons than log2(n!) - which is not a contradiction, because
  reversed is merge sort's BEST case: every merge exhausts one side early.
  The theorem constrains the worst case, not every case.
Block 2 - why the tree must have n! leaves
  n=3: 6 possible orderings, so the tree needs height >= ceil(log2(6)) = 3
  n=4: 24 possible orderings, so the tree needs height >= ceil(log2(24)) = 5
  any correct algorithm must be able to output every one of them,
  so no comparison sort can always finish in fewer comparisons

Block 3 - stability, demonstrated
  input:               [(1, 'a'), (0, 'b'), (1, 'c'), (0, 'd'), (1, 'e')]
  insertion (stable):  [(0, 'b'), (0, 'd'), (1, 'a'), (1, 'c'), (1, 'e')]
  selection (unstable):[(0, 'b'), (0, 'd'), (1, 'c'), (1, 'a'), (1, 'e')]
  with insertion, the 1s stay in the order a, c, e; selection scrambles them

  why it matters - sort by one key, then another:
    stable second sort:   [('Ada', 'eng'), ('Cy', 'eng'), ('Bo', 'ops'), ('Di', 'ops')]
    unstable second sort: [('Ada', 'eng'), ('Cy', 'eng'), ('Bo', 'ops'), ('Di', 'ops')]
    only the stable one keeps names alphabetical within each department

Block 4 - adaptive: the same algorithm on sorted vs reversed input
      n    insertion on sorted   insertion on reversed
     10                      0                      45
     50                      0                    1225
    200                      0                   19900
  zero shifts on sorted input, n(n-1)/2 on reversed: that is 'adaptive'

lower_bound: passed
```

## Common pitfalls and traps

- **Thinking the bound applies to all sorting.** It applies to **comparison** sorts. Counting and radix sort read the keys themselves and are not bound by it.
- **Assuming quicksort is always fastest.** It has the best constants in practice and an $O(n^2)$ worst case. Library implementations guard against it.
- **Forgetting stability when sorting twice.** An unstable second sort discards the first sort's work entirely.
- **Reading $O(n\log n)$ as "fast enough".** For $n = 10^9$ it is $3\times10^{10}$ comparisons. Sorting is often the thing to *avoid*, via a hash map or a heap.
- **Sorting to find one element.** Finding the maximum is $O(n)$; the $k$th largest is $O(n)$ by quickselect or $O(n\log k)$ by heap. Sorting first is $O(n\log n)$ and wasteful.

## Check your understanding

1. Why does the decision tree need at least $n!$ leaves?
2. Give a case where an $O(n^2)$ sort beats an $O(n\log n)$ one.
3. Which of insertion, merge, quick, heap are stable?
4. Why is counting sort not a counterexample to the lower bound?
5. You must sort 10 GB of records with 1 GB of RAM. Which family?

<details><summary>Answers — open only after an attempt</summary>

1. Because a correct algorithm must be capable of producing every one of the $n!$ possible orderings, and each ordering must be reachable at some leaf. Fewer leaves means some input's correct answer can never be output.
2. Small $n$, or nearly-sorted input. Insertion sort on an almost-sorted array is close to $O(n)$ with tiny constants — which is exactly why Timsort and introsort fall back to it below a threshold of around 16 elements.
3. **Insertion and merge** are stable. **Quick and heap** are not.
4. Because counting sort is not a **comparison** sort — it never compares two elements. It uses the key as an array index, which is extra information the decision-tree model does not have. The bound only constrains algorithms whose only tool is comparison.
5. **External merge sort.** Split into chunks that fit in RAM, sort each, write them out, then merge the sorted runs with a $k$-way merge. Merge sort is the family that works when the data does not fit, because it accesses data sequentially.

**And the prediction from section 3:** **no**, it does not disprove the theorem. Counting sort is not a comparison sort — it indexes an array by key value rather than comparing pairs. The theorem is a statement about algorithms restricted to comparisons, and counting sort simply is not one of them.
</details>

## Practice — independent task

Build a **sorting test harness** that verifies any sort against the properties in section 2.

1. `check_correct(fn)` — sorts match `sorted()` on random arrays, sorted arrays, reversed arrays, all-equal arrays, arrays with many duplicates, empty, and one element.
2. `check_stable(fn)` — the `(key, tag)` technique from the lab, on inputs with many equal keys.
3. `check_in_place(fn)` — measure peak extra memory, or inspect whether the input list object is mutated rather than replaced. State the limits of your test.
4. `count_comparisons(fn)` — wrap the elements in a class whose `__lt__` increments a counter, and report comparisons for sorted, random and reversed input. This is how you detect adaptivity without reading the source.
5. Run all four against your own implementations of the six comparison sorts, and produce the table from section 4 **from measurements** rather than copying it. Report any row where your measurement disagrees with the table, and explain why.

**Edge cases:** an already-sorted array (which sorts do zero work?); all elements equal (this is quicksort's classic trap — what happens to your partition?); a single element; an array containing `None` or mixed types.

**Done when:** your generated table matches section 4 for every algorithm, your comparison counts identify which sorts are adaptive without looking at the code, and you can explain any disagreement.

## Before moving on

You can define stability, in-place and adaptive; prove the lower bound; and say why counting sort escapes it.

**Recap:** comparison sorts need $\Omega(n\log n)$ in the worst case, by the decision-tree argument — $n!$ leaves need height $\ge \log_2(n!) = \Theta(n\log n)$; stable preserves the order of equal elements and lets you sort by successive keys; in-place means $O(1)$ extra space; adaptive means faster on partly-sorted input; real libraries use hybrids.

**Next:** [[02-elementary-sorts|Elementary Sorts]] — bubble, selection and insertion, and why one of them is still in every production library.

## Related

- [[01-algorithms|Complexity Analysis]] — the notation used throughout
- [[05-searching|Searching]] — what sorting enables
- [[08-heaps|Heaps]] — the structure heapsort is built on
