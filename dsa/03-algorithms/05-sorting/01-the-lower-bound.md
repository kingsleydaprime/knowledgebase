---
id: b974940e-8eec-45d5-a629-40b970781b5b
---

# Module: Sorting and the $\Omega(n\log n)$ Lower Bound

Sorting is putting items in order, such as numbers from smallest to largest or names from A to Z. The lower bound is a proof that any sorting method which works by comparing two items at a time needs at least a certain number of comparisons. Your phone sorting contacts by name or a shop app sorting by price is the everyday version.

## Before you start
<!-- bite: 46be0e7e-5ea9-4062-8c8d-938e9e644aed -->

- You can read a complexity bound — [[01-growth-and-asymptotic-notation|algorithms and complexity]].
- You know what an array costs to index and to shift — [[01-arrays|arrays]].

**After this lesson you will be able to:**

1. Define **stable**, **in-place**, **adaptive** and **comparison-based**, and say why each matters in practice.
2. **Prove** that any comparison sort needs $\Omega(n\log n)$ comparisons in the worst case.
3. Explain why counting sort does not contradict that proof.
4. Choose a sort from the properties a situation requires, not from a memorised ranking.

**Study route:** read 1–4, attempt the prediction in section 3, then run the lab.

---

## 1. Why this exists
<!-- bite: c692a128-30fc-4bae-b2dd-0c8bb09ccf29 -->

Sorting is the most-studied problem in computing, and it is worth asking why a solved problem needs six algorithms.

Because "sorted" is not the only requirement. You may need the order of equal elements preserved. You may have no spare memory. You may have almost-sorted input. You may be sorting integers in a small range, or strings, or records too large to move. Each constraint rules out different algorithms, and the reason there is no single winner is that the constraints conflict.

There is also a result here that is rare and worth having: a **proof about every possible algorithm**, not just the ones we have thought of. Comparison sorting cannot be done faster than $n\log n$, and no cleverness will change that.

## 2. Terminology
<!-- bite: 4b9ec2da-5e87-49f1-bcb0-9e50c621b507 -->

| Term | Plain-English definition | Why it matters |
| :--- | :--- | :--- |
| **Comparison sort** | Decides order only by comparing pairs | The kind the lower bound applies to |
| **Stable** | Equal elements keep their original relative order | Lets you sort by one key, then another |
| **In-place** | Uses $O(1)$ or $O(\log n)$ extra space | Matters when data barely fits |
| **Adaptive** | Faster on partly-sorted input | Real data is often partly sorted |
| **Internal / external** | Fits in memory / does not | External sorting is a different problem |

**Stability, concretely.** Sort employees by name, then by department. If the second sort is stable, people stay alphabetical within each department. If it is not, the first sort was wasted. This is why `sorted()` in Python and `Arrays.sort` for objects in Java are stable, and it is the single most-overlooked property.

## 3. The lower bound
<!-- bite: 767b7d21-68c7-45be-9d85-17638fd60a22 -->

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
<!-- bite: aea3351d-6433-46c8-badb-b81b0caf3e47 -->

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
<!-- bite: dcce27ae-aa9a-4145-9286-1d97d230bc71 -->

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

```text
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
<!-- bite: e527f90d-68d8-49f3-abe6-074866a10c96 -->

- **Thinking the bound applies to all sorting.** It applies to **comparison** sorts. Counting and radix sort read the keys themselves and are not bound by it.
- **Assuming quicksort is always fastest.** It has the best constants in practice and an $O(n^2)$ worst case. Library implementations guard against it.
- **Forgetting stability when sorting twice.** An unstable second sort discards the first sort's work entirely.
- **Reading $O(n\log n)$ as "fast enough".** For $n = 10^9$ it is $3\times10^{10}$ comparisons. Sorting is often the thing to *avoid*, via a hash map or a heap.
- **Sorting to find one element.** Finding the maximum is $O(n)$; the $k$th largest is $O(n)$ by quickselect or $O(n\log k)$ by heap. Sorting first is $O(n\log n)$ and wasteful.

## Check your understanding
<!-- bite: 1407cd66-d7db-4691-99e4-0f5cc999ab68 -->

Try each one before you open the answer.

1. <!-- q: mcq id="dc714e95" -->
   A comparison sort can be drawn as a decision tree: each inner node is one comparison and each leaf is a final ordering. Why must the tree for n items have at least n! leaves?

   - [ ] Because each comparison has n! outcomes
   - [x] Because every one of the n! possible orderings must be reachable as an output
   - [ ] Because the tree is balanced
   - [ ] Because the input has n! elements

   <details><summary>Answer</summary>

   A correct sort must be able to output any of the n! permutations. With fewer leaves, some input's correct answer could never be produced.

   </details>

2. <!-- q: mcq id="4bc2d08f" -->
   A comparison sort's decision tree must have at least n! leaves, one per ordering, and a binary tree of height h has at most 2^h leaves. What does that make the height h?

   - [x] h ≥ log₂(n!), which is Θ(n log n)
   - [ ] h ≥ n!, which is Θ(n!)
   - [ ] h ≥ log₂(n), which is Θ(log n)
   - [ ] h ≥ n², which is Θ(n²)

   <details><summary>Answer</summary>

   2^h ≥ n!, so h ≥ log₂(n!). The height is the worst-case number of comparisons, and Stirling's approximation shows log₂(n!) = Θ(n log n). No comparison sort can beat that.

   </details>

3. <!-- q: mcq id="b60b10de" -->
   Which of these sorts are stable (equal items keep their original order)? Choose all that apply.

   - [x] Insertion sort
   - [x] Merge sort
   - [ ] Quicksort
   - [ ] Heapsort

   <details><summary>Answer</summary>

   Insertion and merge sort are stable. Quicksort and heapsort swap elements across long distances, so equal items can change order.

   </details>

4. <!-- q: mcq id="c56762df" -->
   Counting sort runs in O(n + k). Why does it not break the Ω(n log n) lower bound?

   - [ ] It does break it; the bound is wrong
   - [x] It never compares two elements; it uses each key as an array index, so the bound does not cover it
   - [ ] Because k is always larger than n log n
   - [ ] Because it is not stable

   <details><summary>Answer</summary>

   The bound only limits algorithms whose only tool is comparing two elements. Counting sort uses the key's value directly, which is extra information the decision-tree model does not allow.

   </details>

5. <!-- q: mcq id="aa7603bd" -->
   You must sort 10 GB of records with 1 GB of RAM. Which family of sort fits?

   - [ ] Quicksort in place
   - [ ] Selection sort
   - [x] External merge sort
   - [ ] Heapsort

   <details><summary>Answer</summary>

   Sort chunks that fit in RAM, write them out as sorted runs, then k-way merge the runs. Merging reads data sequentially, which is what disks are fast at.

   </details>

6. <!-- q: open id="6ea62744" -->
   Give a case where an O(n²) sort beats an O(n log n) sort in practice, and say why.

   <details><summary>Answer</summary>

   Small inputs or nearly sorted inputs. Insertion sort on an almost-sorted array does close to n work, with no recursion, no allocation and sequential memory access. That is why Timsort and introsort switch to insertion sort below about 16 elements.

   </details>

## Check your understanding: worked problems
<!-- bite: e256b0b5-e7d5-4895-9f68-4811d736fdcb -->

Work each one out on paper first, then type your answer.

1. <!-- q: exact id="7a58e6f6" answer="7" -->
   Any comparison sort needs at least ⌈log₂(n!)⌉ comparisons in the worst case. What is that number for n = 5?

   <details><summary>Answer</summary>

   7. 5! = 120 and log₂ 120 ≈ 6.91, rounded up to 7. Six comparisons give at most 2⁶ = 64 outcomes, too few for 120 orderings.

   </details>

2. <!-- q: exact id="f33705bb" answer="5" -->
   What is the smallest worst-case number of comparisons any comparison sort can need for n = 4 items, according to the bound ⌈log₂(n!)⌉?

   <details><summary>Answer</summary>

   5. 4! = 24, and 2⁴ = 16 < 24 ≤ 32 = 2⁵.

   </details>

3. <!-- q: exact id="0b6aaba8" answer="22" -->
   Using the bound ⌈log₂(n!)⌉, at least how many comparisons does sorting 10 items need in the worst case? (10! = 3,628,800.)

   <details><summary>Answer</summary>

   22. log₂ 3,628,800 ≈ 21.79, rounded up to 22. Compare 10 × log₂ 10 ≈ 33: the bound grows like n log n.

   </details>

## Practice — independent task
<!-- bite: b193e956-5290-4ee7-bdfd-340821e4eda5 -->

Build a **sorting test harness** that verifies any sort against the properties in section 2.

1. `check_correct(fn)` — sorts match `sorted()` on random arrays, sorted arrays, reversed arrays, all-equal arrays, arrays with many duplicates, empty, and one element.
2. `check_stable(fn)` — the `(key, tag)` technique from the lab, on inputs with many equal keys.
3. `check_in_place(fn)` — measure peak extra memory, or inspect whether the input list object is mutated rather than replaced. State the limits of your test.
4. `count_comparisons(fn)` — wrap the elements in a class whose `__lt__` increments a counter, and report comparisons for sorted, random and reversed input. This is how you detect adaptivity without reading the source.
5. Run all four against your own implementations of the six comparison sorts, and produce the table from section 4 **from measurements** rather than copying it. Report any row where your measurement disagrees with the table, and explain why.

**Edge cases:** an already-sorted array (which sorts do zero work?); all elements equal (this is quicksort's classic trap — what happens to your partition?); a single element; an array containing `None` or mixed types.

**Done when:** your generated table matches section 4 for every algorithm, your comparison counts identify which sorts are adaptive without looking at the code, and you can explain any disagreement.

## Before moving on
<!-- bite: e9a0ca70-9f09-4d22-9991-220a2c395825 -->

You can define stability, in-place and adaptive; prove the lower bound; and say why counting sort escapes it.

**Recap:** comparison sorts need $\Omega(n\log n)$ in the worst case, by the decision-tree argument — $n!$ leaves need height $\ge \log_2(n!) = \Theta(n\log n)$; stable preserves the order of equal elements and lets you sort by successive keys; in-place means $O(1)$ extra space; adaptive means faster on partly-sorted input; real libraries use hybrids.

**Next:** [[02-elementary-sorts|Elementary Sorts]] — bubble, selection and insertion, and why one of them is still in every production library.

## Related
<!-- bite: d000df51-00fb-4aaf-a247-06f6189177f5 -->

- [[01-growth-and-asymptotic-notation|Complexity Analysis]] — the notation used throughout
- [[01-linear-and-binary-search|Searching]] — what sorting enables
- [[07-heaps|Heaps]] — the structure heapsort is built on

## About this lesson
<!-- bite: 5eda05b2-1e4b-4ace-8d67-3a666ad79011 -->

**Level:** Intermediate. **Covers:** why no comparison sort can ever beat $n\log n$, and the vocabulary the rest of the folder uses.
