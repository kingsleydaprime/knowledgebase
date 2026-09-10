# Sorting

**Five lessons, because there is no single best sort.** Written to [[COURSE-STANDARD|the course standard]] — prerequisites, observable outcomes, worked derivations, a runnable lab whose output was generated from an actual run, practice with hidden answers, and a demonstrable finish line.

> **Why this is a folder and not one note.** "Sorting" is not one algorithm; it is a family with genuinely different trade-offs. Merge sort guarantees $O(n\log n)$ and costs $O(n)$ memory. Quicksort is faster in practice and has a quadratic worst case on the most common input shape there is. Counting sort is linear but needs small integer keys. Choosing well means knowing which property each one buys and what it charges.

## Reading order

1. [[01-the-lower-bound|Sorting and the $\Omega(n\log n)$ Lower Bound]] — **[Intermediate]** — stable, in-place, adaptive; the decision-tree **proof** that no comparison sort can do better; the master comparison table
2. [[02-elementary-sorts|Elementary Sorts]] — **[Beginner]** — bubble, selection, insertion, each with its loop **invariant**; why insertion sort is inside every production library
3. [[03-merge-sort|Merge Sort]] — **[Intermediate]** — divide and conquer, guaranteed $O(n\log n)$, stable, and the basis of **external** sorting when data exceeds memory
4. [[04-quicksort|Quicksort]] — **[Advanced]** — Lomuto and Hoare partitioning, the worst case **triggered on purpose**, median-of-three, introsort, three-way partitioning
5. [[05-non-comparison-sorts|Non-Comparison Sorts]] — **[Intermediate]** — counting, radix and bucket sort, and how they legitimately get under the bound

## The comparison table

| Algorithm | Best | Average | Worst | Space | Stable | Adaptive | Use it when |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| Bubble | $n$ | $n^2$ | $n^2$ | $1$ | ✅ | ✅ | Teaching only |
| Selection | $n^2$ | $n^2$ | $n^2$ | $1$ | ❌ | ❌ | **Writes** are expensive |
| Insertion | $n$ | $n^2$ | $n^2$ | $1$ | ✅ | ✅ | $n < 32$, or nearly sorted |
| Merge | $n\log n$ | $n\log n$ | $n\log n$ | $n$ | ✅ | ❌ | Guarantee needed; linked lists; **external** |
| Quick | $n\log n$ | $n\log n$ | $n^2$ | $\log n$ | ❌ | ❌ | General in-memory default |
| Heap | $n\log n$ | $n\log n$ | $n\log n$ | $1$ | ❌ | ❌ | Guarantee **and** no extra memory |
| Counting | $n+k$ | $n+k$ | $n+k$ | $n+k$ | ✅ | ❌ | Small integer key range |
| Radix | $nd$ | $nd$ | $nd$ | $n+k$ | ✅ | ❌ | Fixed-width integer or string keys |

## Choosing, in one page

- **Just sort it** → your language's built-in. Python's Timsort is stable and adaptive; C++'s introsort is fast with a hard $O(n\log n)$ ceiling.
- **Need stability** → merge family. Never quicksort or heapsort.
- **No spare memory** → heapsort, or quicksort with tail-recursion elimination.
- **Need a worst-case guarantee** → merge or heap. Quicksort only with introsort's fallback.
- **Data larger than RAM** → external merge sort.
- **Small integer keys** → counting or radix, and beat the bound.
- **Nearly sorted already** → insertion, or Timsort, which detects runs.
- **Only need the $k$th element** → do not sort. Quickselect is $O(n)$.

## What is verified

Every lab was executed and its expected output generated from that run. Several test a claim rather than illustrate one:

- **The lower bound is about the worst case** — merge sort on random input exceeds $\log_2(n!)$, while on *reversed* input it does fewer comparisons, which is a best case, not a contradiction.
- **Loop invariants asserted on every pass** of all three elementary sorts, over 200 random arrays each.
- **Selection sort's instability shown**, using a class that compares on the key alone — comparing plain tuples would make every sort look stable.
- **Merge sort's write count is identical** for sorted, reversed, random and all-equal input.
- **Stability turns on one character** — `<=` versus `<` in the merge.
- **Quicksort's worst case triggered deliberately**: 79,800 comparisons and depth 399 on sorted input against 3,420 and depth 16 on random, then fixed by median-of-three.
- **Radix sort with an unstable inner sort produces an unsorted array**, demonstrating why that dependency is load-bearing.
- **Bucket sort collapsing** on clustered input: 4,996 items in one bucket against a uniform 122.

## Related

- [[index|03-algorithms]] — the parent folder
- [[01-algorithms|Complexity Analysis]] — the notation used throughout
- [[05-searching|Searching]] — what sorting enables
- [[08-heaps|Heaps]] — heapsort, and the $k$-way merge's engine
- [[04-patterns/index|04-patterns]] — where sorting shows up as a problem-solving move
