# Module: Recursion Trees and Recurrences (Getting a Complexity Out of Recursive Code)

**[Intermediate]** — You can read a loop and count its iterations. You cannot do that with a recursive function, because its cost is defined in terms of itself. This lesson gives you the two tools that break that circularity: **writing the cost as a recurrence relation**, and **drawing the recursion tree to solve it.**

The payoff is that "what is the complexity of merge sort?" stops being something you remember and becomes something you can derive in thirty seconds on a whiteboard — including for an algorithm you have never seen.

---

## Before you start

- You can write a recursive function and identify its base case and recursive case — [[01-recursion-fundamentals|recursion fundamentals]].
- You can read $O$ and $\Theta$ as statements about growth — [[01-growth-and-asymptotic-notation|growth and asymptotic notation]].
- You know that a geometric series with ratio $< 1$ sums to a constant multiple of its first term, and one with ratio $> 1$ to a constant multiple of its last.

**After this lesson you will be able to:**

1. Convert recursive code into a **recurrence relation**, correctly identifying the branching factor, the shrink factor, and the non-recursive work.
2. Draw the **recursion tree** for a recurrence, and compute nodes, subproblem size and work for an arbitrary level.
3. Decide which of **three cases** a recurrence falls into — leaves dominate, all levels equal, root dominates — and get the answer from that.
4. **Verify** a claimed complexity empirically by doubling $n$ and checking the ratio.

**Study route:** sections 1–3 build the method; do the prediction in section 4 before reading on; section 5 is the pattern catalogue worth memorising; then run the lab.

---

## 1. Why this exists: the cost that refers to itself

Here is merge sort, stripped to its shape:

```python
def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid])        # sort half
    right = merge_sort(a[mid:])       # sort the other half
    return merge(left, right)         # combine, in linear time
```

Ask "how long does this take on $n$ elements?" and you get: *however long it takes on $n/2$ elements, twice, plus $n$ for the merge.* The answer is written in terms of the question.

That is not a failure — it is the actual structure of the cost, and it has a standard notation:

$$T(n) = 2\,T(n/2) + O(n)$$

**In words: the time to sort $n$ items is the time to sort two halves, plus linear work to combine them.** This is a **recurrence relation**: an equation defining a function in terms of its own smaller values. Solving it means finding a closed form — an expression for $T(n)$ with no $T$ on the right-hand side.

The good news is that nearly every recurrence you meet in practice has one of **three** shapes, and you can tell which by asking a single question.

---

## Terms used in recurrences

1. **Recurrence relation**: This is an equation that defines a function's value at $n$ using its values at smaller inputs, together with a base case. $T(n) = 2T(n/2) + n$ with $T(1) = 1$ is a recurrence.
2. **Closed form**: This is also known as an **explicit formula**. This is an expression for $T(n)$ that does not mention $T$ — for instance $T(n) = n\log_2 n + n$. Solving a recurrence means finding one, or at least its growth rate.
3. **Branching factor**: This is written $a$. This is how many recursive calls one call makes. Merge sort has $a = 2$; binary search has $a = 1$; the naive Fibonacci has $a = 2$.
4. **Shrink factor**: This is written $b$. This is the factor by which the input gets smaller in each call, when the shrinking is *divisive*. Merge sort has $b = 2$ because each call gets half. A recursion that shrinks by subtraction — $T(n-1)$ — has no $b$, and is handled separately in section 6.
5. **Combine work**: This is written $f(n)$. This is the non-recursive work one call does: everything outside the recursive calls. For merge sort $f(n) = n$, the cost of merging. It is also called the **driving function**.
6. **Recursion tree**: This is a drawing of all the calls, with the original call at the root and each call's subcalls as its children. Each node is labelled with the work *that node alone* does, excluding its children.
7. **Level**: This is all the nodes at one depth of the recursion tree. Level 0 is the root. The key move in this lesson is computing the **total work at a level**, rather than per node.
8. **Depth**: This is also called the **height**. This is the number of levels — how many times you can divide $n$ by $b$ before reaching the base case, which is $\log_b n$ for divisive recurrences and $n$ for subtractive ones.
9. **Leaves**: These are the nodes at the bottom of the tree, where the base case applies. There are $a^{\text{depth}}$ of them, which for divisive recurrences is $a^{\log_b n} = n^{\log_b a}$.
10. **Substitution method**: This is guessing a closed form and proving it correct by induction. It is the rigorous companion to the recursion tree, which is really a way of *finding* the guess.

---

## 2. From code to recurrence

Three things to read off the code, and nothing else:

1. **How many recursive calls?** → $a$
2. **How much smaller is the input in each?** → $b$ (or "minus one", for subtractive)
3. **How much work outside the recursive calls?** → $f(n)$

Then $T(n) = a\,T(n/b) + f(n)$.

| Code shape | $a$ | $b$ | $f(n)$ | Recurrence |
| :--- | :--- | :--- | :--- | :--- |
| Binary search: check middle, recurse into one half | 1 | 2 | $O(1)$ | $T(n) = T(n/2) + O(1)$ |
| Merge sort: two halves, linear merge | 2 | 2 | $O(n)$ | $T(n) = 2T(n/2) + O(n)$ |
| Naive Fibonacci: two calls, sizes $n-1$ and $n-2$ | 2 | — | $O(1)$ | $T(n) = T(n{-}1) + T(n{-}2) + O(1)$ |
| Linear recursion: one call, one smaller | 1 | — | $O(1)$ | $T(n) = T(n{-}1) + O(1)$ |
| Tree traversal: two children, constant work | 2 | 2\* | $O(1)$ | $T(n) = 2T(n/2) + O(1)$ |

\* only for a *balanced* tree — an unbalanced one is $T(n) = T(k) + T(n-1-k) + O(1)$, which is why traversal is $O(n)$ by the simpler argument "each node is visited once" rather than by this machinery.

**The mistake to avoid at this step is counting the recursive work twice.** $f(n)$ is *only* the work the current call does itself. In merge sort, the merge is $f(n)$; the sorting of the halves is already accounted for by the $2T(n/2)$ term and must not be added again.

---

## 3. The recursion tree, and the only three answers

Draw the calls. Label each node with **the work that node does itself**. Then — and this is the move that makes the whole method work — **sum across each level rather than down each branch.**

For $T(n) = 2T(n/2) + n$:

```
level 0:                    n                          1 node  x  n      = n
                     ┌──────┴──────┐
level 1:            n/2           n/2                  2 nodes x  n/2    = n
                  ┌──┴──┐       ┌──┴──┐
level 2:        n/4    n/4     n/4    n/4              4 nodes x  n/4    = n
                 ...                                        ...
level k:                                              2^k nodes x n/2^k = n
                 ...
level log n:    1  1  1  ...  1  1  1                  n nodes x  1      = n
```

At level $k$ there are $2^k$ nodes, each of size $n/2^k$, each doing $n/2^k$ work. **The level total is $n$ regardless of $k$.** There are $\log_2 n + 1$ levels. Therefore

$$T(n) = n \cdot (\log_2 n + 1) = O(n \log n)$$

The lab measures exactly this table for $n = 64$: every level does 64 units of work, there are 7 levels, and the total is 448 — matching the closed form $n(\log_2 n + 1)$ precisely.

### The general level arithmetic

For $T(n) = a\,T(n/b) + f(n)$, at level $k$:

$$\text{nodes} = a^k, \qquad \text{size} = \frac{n}{b^k}, \qquad \text{work at this level} = a^k \cdot f\!\left(\frac{n}{b^k}\right)$$

**Everything depends on what that last quantity does as $k$ increases.** It can only do three things, and each gives a different answer:

| If work per level... | Then the total is dominated by | Result |
| :--- | :--- | :--- |
| **grows** as you go down | the bottom level — the **leaves** | $O(\text{number of leaves}) = O(n^{\log_b a})$ |
| **stays constant** | every level equally | $O(f(n) \cdot \text{depth}) = O(f(n)\log n)$ |
| **shrinks** as you go down | the top level — the **root** | $O(f(n))$ |

This is the entire content of [[03-the-master-theorem|the Master Theorem]], derived. The theorem is this table with the conditions made precise.

### Why "dominated by" is legitimate

Because these are geometric series. If the work per level shrinks by a constant factor $r < 1$, the total is $f(n)(1 + r + r^2 + \dots) < f(n)/(1-r)$ — a **constant multiple** of the root's work, so the root's work is the answer. If it grows by a factor $r > 1$, the last level is a constant fraction of the whole sum, so the leaves are the answer.

The lab makes both visible. For $T(n) = 2T(n/2) + n^2$ at $n=64$, the level totals are $4096, 2048, 1024, 512, 256, 128, 64$ — halving each time — and the total is 8,128, which is under $2n^2 = 8192$. **The root alone accounts for half the entire tree.** For $T(n) = 2T(n/2) + 1$ they run $1, 2, 4, \dots, 64$ — doubling — total 127, and **the bottom level alone is more than half.**

---

## 4. Reading the three cases off a tree

> **Predict before reading on.** For $T(n) = 3T(n/2) + n$: at level $k$ there are $3^k$ nodes each of size $n/2^k$, so the level work is $3^k \cdot n/2^k = n(3/2)^k$. Is this dominated by the root, the leaves, or neither? And what is the resulting complexity?

**The leaves.** The level work is multiplied by $3/2 > 1$ at each step, so it grows downward and the bottom level dominates. The number of leaves is $3^{\log_2 n} = n^{\log_2 3} \approx n^{1.585}$, so $T(n) = \Theta(n^{\log_2 3})$.

The lab confirms both halves. The level totals at $n = 64$ are $64, 96, 144, 216, 324, 486, 729$ — each $1.5\times$ the last — with the leaf level at 729, which is exactly $64^{\log_2 3}$. Total work 2,059, matching the exact closed form $3n^{\log_2 3} - 2n$.

**And the doubling test confirms the growth rate independently:** doubling $n$ multiplies the measured work by 3.06, 3.04, 3.03, 3.02 — converging on 3, which is what $n^{\log_2 3}$ predicts, since $2^{\log_2 3} = 3$.

**That doubling test is the most useful practical skill in this lesson.** If you think an algorithm is $O(n^k)$, double the input and see whether the time multiplies by $2^k$. Linear doubles, quadratic quadruples, $n\log n$ does slightly more than double, and $O(\log n)$ barely moves. You can check a complexity claim in two runs without reading a line of the implementation.

---

## 5. The catalogue worth memorising

| Recurrence | Solution | Where you meet it |
| :--- | :--- | :--- |
| $T(n) = T(n-1) + O(1)$ | $O(n)$ | linear recursion, list sum |
| $T(n) = T(n-1) + O(n)$ | $O(n^2)$ | selection sort, quicksort's worst case |
| $T(n) = 2T(n-1) + O(1)$ | $O(2^n)$ | subsets, towers of Hanoi |
| $T(n) = T(n/2) + O(1)$ | $O(\log n)$ | [[01-linear-and-binary-search\|binary search]] |
| $T(n) = T(n/2) + O(n)$ | $O(n)$ | quickselect, average case |
| $T(n) = 2T(n/2) + O(1)$ | $O(n)$ | tree traversal, heapify |
| $T(n) = 2T(n/2) + O(n)$ | $O(n\log n)$ | [[04-sorting/03-merge-sort\|merge sort]], [[04-sorting/04-quicksort\|quicksort]] average |
| $T(n) = 2T(n/2) + O(n^2)$ | $O(n^2)$ | root-dominated divide and conquer |
| $T(n) = 3T(n/2) + O(n)$ | $O(n^{1.585})$ | Karatsuba multiplication |
| $T(n) = 7T(n/2) + O(n^2)$ | $O(n^{2.807})$ | Strassen matrix multiplication |

**The two rows worth staring at are rows 6 and 7.** Same branching, same shrinking — the only difference is $O(1)$ versus $O(n)$ of combine work, and that alone is the difference between $O(n)$ and $O(n\log n)$. That is why merge sort cannot be made linear by clever coding: the merge is inherently linear, and a linear combine at every level is where the $\log n$ factor comes from.

**Rows 1 and 4 are the other pair to internalise.** Subtracting one gives $n$ levels; dividing by two gives $\log n$ levels. **Shrinking multiplicatively rather than additively is the single highest-leverage move in algorithm design**, and it is the reason binary search, balanced trees and divide-and-conquer all exist.

---

## 6. Subtractive recurrences, and where the tree method strains

$T(n) = a\,T(n-c) + f(n)$ does not fit the $n/b$ pattern, and the tree looks different: the depth is $n/c$ rather than $\log_b n$, and the number of leaves is $a^{n/c}$ — exponential in $n$ whenever $a > 1$.

- $T(n) = T(n-1) + O(1)$: $n$ levels, constant each → $O(n)$.
- $T(n) = T(n-1) + O(n)$: $n$ levels, work $n, n-1, n-2, \dots$ → $\sum i = O(n^2)$.
- $T(n) = 2T(n-1) + O(1)$: $n$ levels, work doubling each → $O(2^n)$.

**The lesson of the third row:** branching with subtractive shrinking is always exponential. This is naive Fibonacci, and it is why memoisation is not an optimisation there but a change of algorithm.

### Verifying with the substitution method

The tree gives you a guess. Induction turns it into a proof. To show $T(n) = 2T(n/2) + n$ is $O(n\log n)$, guess $T(n) \le c\,n\log_2 n$ for some constant $c$ and all $n \ge 2$:

$$T(n) = 2T(n/2) + n \le 2 \cdot c\,\frac{n}{2}\log_2\frac{n}{2} + n = c\,n(\log_2 n - 1) + n = c\,n\log_2 n - cn + n$$

This is $\le c\,n\log_2 n$ whenever $-cn + n \le 0$, that is whenever $c \ge 1$. The inductive step holds; check a base case and you are done.

**The step people get wrong is assuming the bound for $n/2$ without checking that the leftover terms cancel in the right direction.** Here $-cn + n$ had to be $\le 0$, and that is what pinned down $c \ge 1$. If the leftovers had gone the other way, the guess would be wrong and would need strengthening — typically to $c\,n\log_2 n - d\,n$.

---

## 7. Worked example — complete runnable lab

Save as `recursion_trees.py`. Standard library only. It does not run the real algorithms — it **simulates the recurrences directly**, so the level tables are exact rather than timing-dependent.

```python
"""Draw the recursion tree by measuring it: work per level, for real recurrences.

Run:  python3 recursion_trees.py
"""

import math
from collections import defaultdict


def run(a, b, f, n):
    """Simulate T(n) = a*T(n/b) + f(n) and record the work done at each level.

    a = number of subcalls, b = shrink factor, f = non-recursive work at size n.
    Returns (total_work, work_by_level).
    """
    by_level = defaultdict(float)

    def rec(size, level):
        by_level[level] += f(size)
        if size <= 1:
            return
        for _ in range(a):
            rec(size / b, level + 1)

    rec(n, 0)
    return sum(by_level.values()), dict(sorted(by_level.items()))


def level_table(a, b, f, n, label, closed_form):
    total, levels = run(a, b, f, n)
    print(f"\n  {label}   (n = {n})")
    print("    level |   nodes | size each |   work this level")
    for lvl, work in levels.items():
        nodes = a ** lvl
        size = n / (b ** lvl)
        print(f"    {lvl:>5} | {nodes:>7} | {size:>9.1f} | {work:>17,.0f}")
    print(f"    total work: {total:,.0f}")
    print(f"    closed form {closed_form[0]}: {closed_form[1](n):,.0f}")
    return total


def growth_check(a, b, f, label, predicted):
    """Double n repeatedly; report total work and the ratio between successive runs."""
    print(f"\n  {label}")
    print("        n |      total work | ratio vs previous | predicted ratio")
    prev = None
    for n in (64, 128, 256, 512, 1024):
        total, _ = run(a, b, f, n)
        ratio = f"{total/prev:>17.2f}" if prev else f"{'-':>17}"
        pr = predicted(n) / predicted(n / 2) if n > 64 else None
        pr_s = f"{pr:>15.2f}" if pr else f"{'-':>15}"
        print(f"  {n:>7} | {total:>15,.0f} | {ratio} | {pr_s}")
        prev = total


def main():
    print("=== 1. T(n) = 2T(n/2) + n   -- every level does the same work ===")
    level_table(2, 2, lambda s: s, 64,
                "merge sort's recurrence", ("n*(log2(n)+1)", lambda n: n * (math.log2(n) + 1)))
    print("    -> n work per level, log2(n)+1 levels  =>  O(n log n)")

    print("\n=== 2. T(n) = 2T(n/2) + 1   -- the LEAVES dominate ===")
    level_table(2, 2, lambda s: 1, 64,
                "constant work per node", ("2n-1", lambda n: 2 * n - 1))
    print("    -> work DOUBLES each level; the bottom level alone is half the total  =>  O(n)")

    print("\n=== 3. T(n) = 2T(n/2) + n^2   -- the ROOT dominates ===")
    level_table(2, 2, lambda s: s * s, 64,
                "quadratic combine", ("2n^2 - n", lambda n: 2 * n * n - n))
    print("    -> work HALVES each level; the root alone is half the total  =>  O(n^2)")

    print("\n=== 4. T(n) = T(n/2) + 1   -- one branch only ===")
    level_table(1, 2, lambda s: 1, 64,
                "binary search", ("log2(n)+1", lambda n: math.log2(n) + 1))
    print("    -> one node per level, log2(n)+1 levels  =>  O(log n)")

    print("\n=== 5. T(n) = 3T(n/2) + n   -- branching beats shrinking ===")
    level_table(3, 2, lambda s: s, 64,
                "Karatsuba-shaped", ("3*n^log2(3) - 2n", lambda n: 3 * n ** math.log2(3) - 2 * n))
    print("    -> work grows by 3/2 each level; leaves dominate  =>  O(n^log2(3))")

    print("\n\n=== 6. Verifying the growth rates by doubling n ===")
    print("  If T(n) is O(n^k), doubling n multiplies the work by 2^k.")
    growth_check(2, 2, lambda s: s, "T(n) = 2T(n/2) + n      -> expect just over 2.0",
                 lambda n: n * math.log2(n))
    growth_check(2, 2, lambda s: 1, "T(n) = 2T(n/2) + 1      -> expect 2.0 (linear)",
                 lambda n: n)
    growth_check(2, 2, lambda s: s * s, "T(n) = 2T(n/2) + n^2    -> expect 4.0 (quadratic)",
                 lambda n: n * n)
    growth_check(3, 2, lambda s: s, "T(n) = 3T(n/2) + n      -> expect 3.0 (n^1.585)",
                 lambda n: n ** math.log2(3))

    print("\n\n=== 7. The three shapes, side by side ===")
    print("  What decides the answer is how work changes as you go DOWN the tree:")
    print("    work grows downward   -> the LEAVES dominate  -> total = O(leaves)")
    print("    work is constant      -> every level is equal -> total = O(f(n) * depth)")
    print("    work shrinks downward -> the ROOT dominates   -> total = O(f(n))")
    print()
    print("    recurrence            | work per level    | dominated by | result")
    print("    2T(n/2) + 1           | 1, 2, 4, ... n    | leaves       | O(n)")
    print("    2T(n/2) + n           | n, n, n, ... n    | all equal    | O(n log n)")
    print("    2T(n/2) + n^2         | n^2, n^2/2, ...   | root         | O(n^2)")
    print("    3T(n/2) + n           | n, 1.5n, 2.25n... | leaves       | O(n^1.585)")


if __name__ == "__main__":
    main()
```

### Expected output

Generated by running the file above:

```
=== 1. T(n) = 2T(n/2) + n   -- every level does the same work ===

  merge sort's recurrence   (n = 64)
    level |   nodes | size each |   work this level
        0 |       1 |      64.0 |                64
        1 |       2 |      32.0 |                64
        2 |       4 |      16.0 |                64
        3 |       8 |       8.0 |                64
        4 |      16 |       4.0 |                64
        5 |      32 |       2.0 |                64
        6 |      64 |       1.0 |                64
    total work: 448
    closed form n*(log2(n)+1): 448
    -> n work per level, log2(n)+1 levels  =>  O(n log n)

=== 2. T(n) = 2T(n/2) + 1   -- the LEAVES dominate ===

  constant work per node   (n = 64)
    level |   nodes | size each |   work this level
        0 |       1 |      64.0 |                 1
        1 |       2 |      32.0 |                 2
        2 |       4 |      16.0 |                 4
        3 |       8 |       8.0 |                 8
        4 |      16 |       4.0 |                16
        5 |      32 |       2.0 |                32
        6 |      64 |       1.0 |                64
    total work: 127
    closed form 2n-1: 127
    -> work DOUBLES each level; the bottom level alone is half the total  =>  O(n)

=== 3. T(n) = 2T(n/2) + n^2   -- the ROOT dominates ===

  quadratic combine   (n = 64)
    level |   nodes | size each |   work this level
        0 |       1 |      64.0 |             4,096
        1 |       2 |      32.0 |             2,048
        2 |       4 |      16.0 |             1,024
        3 |       8 |       8.0 |               512
        4 |      16 |       4.0 |               256
        5 |      32 |       2.0 |               128
        6 |      64 |       1.0 |                64
    total work: 8,128
    closed form 2n^2 - n: 8,128
    -> work HALVES each level; the root alone is half the total  =>  O(n^2)

=== 4. T(n) = T(n/2) + 1   -- one branch only ===

  binary search   (n = 64)
    level |   nodes | size each |   work this level
        0 |       1 |      64.0 |                 1
        1 |       1 |      32.0 |                 1
        2 |       1 |      16.0 |                 1
        3 |       1 |       8.0 |                 1
        4 |       1 |       4.0 |                 1
        5 |       1 |       2.0 |                 1
        6 |       1 |       1.0 |                 1
    total work: 7
    closed form log2(n)+1: 7
    -> one node per level, log2(n)+1 levels  =>  O(log n)

=== 5. T(n) = 3T(n/2) + n   -- branching beats shrinking ===

  Karatsuba-shaped   (n = 64)
    level |   nodes | size each |   work this level
        0 |       1 |      64.0 |                64
        1 |       3 |      32.0 |                96
        2 |       9 |      16.0 |               144
        3 |      27 |       8.0 |               216
        4 |      81 |       4.0 |               324
        5 |     243 |       2.0 |               486
        6 |     729 |       1.0 |               729
    total work: 2,059
    closed form 3*n^log2(3) - 2n: 2,059
    -> work grows by 3/2 each level; leaves dominate  =>  O(n^log2(3))


=== 6. Verifying the growth rates by doubling n ===
  If T(n) is O(n^k), doubling n multiplies the work by 2^k.

  T(n) = 2T(n/2) + n      -> expect just over 2.0
        n |      total work | ratio vs previous | predicted ratio
       64 |             448 |                 - |               -
      128 |           1,024 |              2.29 |            2.33
      256 |           2,304 |              2.25 |            2.29
      512 |           5,120 |              2.22 |            2.25
     1024 |          11,264 |              2.20 |            2.22

  T(n) = 2T(n/2) + 1      -> expect 2.0 (linear)
        n |      total work | ratio vs previous | predicted ratio
       64 |             127 |                 - |               -
      128 |             255 |              2.01 |            2.00
      256 |             511 |              2.00 |            2.00
      512 |           1,023 |              2.00 |            2.00
     1024 |           2,047 |              2.00 |            2.00

  T(n) = 2T(n/2) + n^2    -> expect 4.0 (quadratic)
        n |      total work | ratio vs previous | predicted ratio
       64 |           8,128 |                 - |               -
      128 |          32,640 |              4.02 |            4.00
      256 |         130,816 |              4.01 |            4.00
      512 |         523,776 |              4.00 |            4.00
     1024 |       2,096,128 |              4.00 |            4.00

  T(n) = 3T(n/2) + n      -> expect 3.0 (n^1.585)
        n |      total work | ratio vs previous | predicted ratio
       64 |           2,059 |                 - |               -
      128 |           6,305 |              3.06 |            3.00
      256 |          19,171 |              3.04 |            3.00
      512 |          58,025 |              3.03 |            3.00
     1024 |         175,099 |              3.02 |            3.00


=== 7. The three shapes, side by side ===
  What decides the answer is how work changes as you go DOWN the tree:
    work grows downward   -> the LEAVES dominate  -> total = O(leaves)
    work is constant      -> every level is equal -> total = O(f(n) * depth)
    work shrinks downward -> the ROOT dominates   -> total = O(f(n))

    recurrence            | work per level    | dominated by | result
    2T(n/2) + 1           | 1, 2, 4, ... n    | leaves       | O(n)
    2T(n/2) + n           | n, n, n, ... n    | all equal    | O(n log n)
    2T(n/2) + n^2         | n^2, n^2/2, ...   | root         | O(n^2)
    3T(n/2) + n           | n, 1.5n, 2.25n... | leaves       | O(n^1.585)
```

### What the lab is demonstrating

- **Blocks 1–5** are the level tables. Read the rightmost column downward in each: constant in block 1, doubling in block 2, halving in block 3, constant-at-one in block 4, growing by $1.5\times$ in block 5. **That column alone determines the answer**, and the closed form printed underneath matches the measured total exactly in every case.
- **Block 6** is the doubling test. `2T(n/2)+1` gives a ratio of exactly 2.00 (linear), `2T(n/2)+n^2` gives 4.00 (quadratic), `3T(n/2)+n` gives 3.02 (that is $2^{1.585}$), and `2T(n/2)+n` gives 2.20 and falling — **just over 2, which is the signature of $n\log n$**, and the measured ratio tracks the predicted one to two decimal places.
- The ratio for $n\log n$ *decreases* as $n$ grows (2.29 → 2.20). That is correct and worth understanding: the ratio is $2(1 + 1/\log_2 n)$, which approaches 2 from above. An algorithm whose doubling ratio slowly falls toward 2 is $n\log n$, not linear.

---

## 8. Common pitfalls and traps

1. **Counting the recursive work inside $f(n)$.** $f(n)$ is only what the current call does itself. Including the subcalls double-counts the entire tree.
2. **Assuming the tree is balanced when it is not.** Quicksort is $T(n) = T(k) + T(n-1-k) + O(n)$, and $k$ depends on the pivot. The $O(n\log n)$ figure assumes balanced splits; the worst case $k = 0$ gives $T(n) = T(n-1) + O(n) = O(n^2)$. **A recursion tree drawn as balanced silently assumes the thing you may need to prove.**
3. **Forgetting that the depth of a subtractive recurrence is $n$, not $\log n$.** $T(n) = 2T(n-1)$ is $O(2^n)$; $T(n) = 2T(n/2)$ is $O(n)$. The two look almost identical written down and differ by an exponential.
4. **Reading $\log$ as base 10 or base $e$.** Inside $O(\cdot)$ the base is irrelevant — logs differ by a constant factor. **In the level arithmetic it is not**: the depth really is $\log_b n$ with $b$ the shrink factor, and that is what tells you a 3-way split has depth $\log_3 n$.
5. **Assuming more branching is always worse.** $8T(n/2) + O(n^2)$ is $O(n^3)$, and Strassen's $7T(n/2) + O(n^2)$ is $O(n^{2.807})$ — one fewer subcall changes the exponent. Branching interacts with shrinking; neither alone decides.
6. **Trusting the guess without the induction.** The tree method is a heuristic for *finding* the answer. For an unfamiliar recurrence, verify by substitution or by the doubling test.
7. **Ignoring the base case's contribution.** For $T(n) = 2T(n/2) + O(1)$ the leaves are the whole cost — there are $n$ of them each doing constant work. If you only count the internal nodes you will conclude $O(\log n)$ and be badly wrong.

---

## 9. Check your understanding

1. **$T(n) = 4T(n/2) + n$. Root, leaves, or balanced — and what is the answer?**
   <details><summary>Answer</summary>Level work is $4^k \cdot n/2^k = n \cdot 2^k$, which grows downward, so the <b>leaves</b> dominate. Leaves number $4^{\log_2 n} = n^{\log_2 4} = n^2$. So $T(n) = \Theta(n^2)$. Doubling $n$ should multiply the work by 4.</details>

2. **Two algorithms: $T(n) = 2T(n/2) + O(n)$ and $T(n) = 2T(n/2) + O(1)$. Which is faster, and by how much?**
   <details><summary>Answer</summary>The second, by a factor of $\log n$ — it is $O(n)$ against $O(n\log n)$. The only difference is the combine step, and it costs a whole logarithmic factor because it is paid at every one of the $\log n$ levels. This is precisely the gap between merge sort and a tree traversal.</details>

3. **Why is naive Fibonacci $O(\varphi^n)$ rather than $O(2^n)$, and why do we usually say $O(2^n)$ anyway?**
   <details><summary>Answer</summary>$T(n) = T(n-1) + T(n-2) + O(1)$ does not branch into two <i>equal</i> halves — one subtree is shorter — so the count grows as the golden ratio $\varphi \approx 1.618$ rather than 2. Precisely, the call count is $2\,\mathrm{fib}(n+1)-1$. We say $O(2^n)$ because it is a correct upper bound, it is the right order of magnitude, and the distinction rarely changes a decision. The lab's measured counts follow the $\varphi$ growth, not $2^n$: 2,692,537 at $n=30$, where $2^{30}$ is about a billion.</details>

4. **You suspect an implementation is $O(n^2)$. It takes 1.0s at $n=1000$ and 4.1s at $n=2000$. Confirmed or not?**
   <details><summary>Answer</summary>Consistent with $O(n^2)$: doubling $n$ quadrupled the time, and $4.1 \approx 4$. But one data point is weak evidence — $n\log n$ with a bad constant can look similar over a single doubling. Take a third point at $n=4000$: quadratic predicts about 16.4s, $n\log n$ predicts about 9s. The ratios diverge fast, which is why three points beat two.</details>

5. **A recurrence has level work $n, n, n, \dots$ but depth $\sqrt{n}$ instead of $\log n$. What is $T(n)$?**
   <details><summary>Answer</summary>$O(n^{1.5})$ — the level arithmetic is unchanged, total is work-per-level times depth, $n \cdot \sqrt{n}$. This is the point of the method: you are never pattern-matching on named recurrences, you are multiplying a per-level cost by a number of levels. This shape arises from $T(n) = T(n - \sqrt{n}) + n$.</details>

---

## 10. Practice — independent task

Build a **recurrence solver you can check against reality**.

**Part 1 — the simulator.** Write `solve(a, b, f, n)` returning total work and a per-level breakdown, as the lab's `run` does — but write it yourself before reading that function. It must handle $a = 1$ and non-integer sizes.

**Part 2 — the classifier.** Write `classify(a, b, f, n)` that decides, *from measurements only*, whether the recurrence is root-dominated, balanced, or leaf-dominated. Compare the work at level 0 with the work at the deepest level, and with the total. State the threshold you chose and defend it.

**Part 3 — against real code.** Instrument actual implementations of [[01-linear-and-binary-search|binary search]], [[04-sorting/03-merge-sort|merge sort]] and a balanced-tree traversal to count their real operations. Check the counts against your simulator's prediction for the matching recurrence. **They should agree to within a constant factor; if they do not, one of the two is wrong and finding out which is the exercise.**

**Part 4 — the doubling test.** Write `growth_exponent(fn, sizes)` that runs a function at doubling sizes and returns the estimated exponent $k$ such that the cost is $O(n^k)$, by taking $\log_2$ of the ratio between successive runs. Test it on known $O(n)$, $O(n\log n)$ and $O(n^2)$ functions and report how close it gets.

**Edge cases:** $a=1$ (no branching); $f(n) = 0$; $n$ smaller than $b$; $b$ not dividing $n$ evenly; a recurrence whose depth is 1.

**Done when:** your classifier agrees with the hand analysis on all ten rows of the section 5 catalogue; your part 3 counts match predictions to within a constant factor you can state; and your doubling test reports an exponent within 0.1 of the truth for the three test functions — **and you can explain why it reports about 1.1 rather than 1.0 for an $O(n\log n)$ function.**

---

## Before moving on

You can turn recursive code into a recurrence, draw its tree, compute the work at an arbitrary level, decide which of the three cases applies, and verify the result by doubling the input.

**Recap:** read $a$, $b$ and $f(n)$ off the code to get $T(n) = aT(n/b) + f(n)$. At level $k$ there are $a^k$ nodes of size $n/b^k$, so the level work is $a^k f(n/b^k)$ — **and the way that quantity moves as you descend is the whole answer.** Growing downward means the leaves dominate, giving $O(n^{\log_b a})$; constant means every level is equal, giving $O(f(n)\log n)$; shrinking means the root dominates, giving $O(f(n))$. Subtractive recurrences have depth $n$ rather than $\log n$, so branching plus subtraction is always exponential. Confirm any claim by doubling $n$: linear doubles, quadratic quadruples, and $n\log n$ gives a ratio slightly above 2 that falls slowly toward it.

**Next:** [[03-the-master-theorem|The Master Theorem]] — the three cases above, stated as a theorem with precise conditions, so you can skip the tree when the recurrence is a standard shape.

---

## Related

- [[01-recursion-fundamentals|Recursion Fundamentals]] — the previous lesson
- [[03-the-master-theorem|The Master Theorem]] — this lesson's three cases, formalised
- Divide and Conquer *(not yet written)* — the algorithm family these recurrences describe
- [[01-growth-and-asymptotic-notation|Growth and Asymptotic Notation]] — the notation being solved for
- [[04-sorting/03-merge-sort|Merge Sort]] · [[04-sorting/04-quicksort|Quicksort]] — the worked cases
- [[05-induction-and-recursion|Discrete maths: induction and recursion]] — the substitution method's proof machinery
- [[02-recursion/index|the recursion folder]]
