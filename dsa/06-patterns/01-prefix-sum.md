# Pattern: Prefix Sum

Preprocess an [[01-arrays|array]] once so that any range-sum query afterward is O(1) instead of O(n). The trade is a single O(n) pass and O(n) extra space up front, paid once, to make every query after that nearly free.

**[Beginner]** — A university-level introduction to the prefix-sum pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You can index an array and reason about its memory layout. See [[01-arrays|arrays]] if needed.
- You know what a hash map is and that lookups are O(1) on average. See [[03-hash-maps|hash maps]] for the variant below.
- You can read Big-O notation. See [[01-algorithms|algorithms and complexity]].

**What you will be able to do after this lesson:**

1. Explain why preprocessing an array once turns every later range query from O(n) into O(1).
2. Build a prefix-sum array with a sentinel and query any range without an off-by-one.
3. Extend the idea to two dimensions with a summed-area table.
4. Recognise the hash-map variant, and say why a sliding window cannot replace it when values may be negative.

**Study route:** read the motivation and mechanism, run the lab, then attempt the independent task before opening the answers.

## The idea in one sentence

**A bank statement doesn't store "how much did I spend in June" — it stores the running balance after every transaction, and you get June by subtracting the balance on 1 June from the balance on 30 June.** That subtraction *is* the prefix-sum pattern. Everything below is that one move, applied in different costumes.

## A concrete example: the analytics dashboard

Say you're building the revenue dashboard for a shop. You have three years of daily revenue — about 1,100 numbers:

```
day:      0    1    2    3    4    5   ...
revenue: 120  340   90  210  400  150  ...
```

The dashboard has a date-range picker. A user asks: *"How much did we make from day 2 to day 5?"* The obvious answer is to loop from day 2 to day 5 and add. That's fine — once.

But a real dashboard doesn't ask once. It asks:

- "Revenue this week" — one range
- "Same week last year" — another range
- "Month to date", "last month", "quarter to date", "same quarter last year" — six more
- ...times 12 widgets on the page, times every user who loads it, times every time someone drags the date slider

Each of those is a fresh loop over up to 1,100 numbers. Drag the slider and you're re-adding the same numbers hundreds of times a second. The work is O(days) **per query**, and the queries are the thing you have a lot of.

So do the summing **once**, at load, and store the running total:

```
day:               0    1    2    3    4    5
revenue:          120  340   90  210  400  150
total through day: 120  460  550  760 1160 1310    <- prefix sums
```

Now "day 2 through day 5" is:

```
total through day 5  =  1310     (everything from day 0 to day 5)
total through day 1  =   460     (everything before day 2)
                        ------
revenue for days 2-5 =   850     90 + 210 + 400 + 150 -> 850 ✓
```

**Two array lookups and a subtraction.** It doesn't matter whether the range is 4 days or 4 years — the cost is identical. Everything before day 2 got counted into both totals, so subtracting cancels it out exactly, and what survives is precisely the slice you asked for.

That's the whole pattern: *don't store the answers to the ranges, store the totals up to each point, and subtract.*

## Definitions and terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **Prefix sum** | The running total of everything up to a point | A bank balance after each transaction |
| **Sentinel** | A leading  meaning "nothing so far", so index 0 needs no special case | The opening balance |
| **Range query** | "What is the total between these two positions?" | Revenue for days 2–5 |
| **Preprocessing** | Work done once up front so later queries are cheap | Building the statement |
| **Summed-area table** | The 2-D version: totals from the origin to each cell | — |
| **Inclusion–exclusion** | Subtracting overlapping regions, then adding back what was removed twice | — |
| **Scan** | The same operation's name in parallel computing | — |

## Where this actually shows up

Not just interview problems — this is load-bearing infrastructure in a few places:

- **SQL and analytics.** `SUM(revenue) OVER (ORDER BY date)` is a prefix sum, computed by the database. Cumulative/running-total columns, cohort charts, and burndown charts are all prefix sums. Time-series databases pre-materialise these rollups so range queries don't touch raw rows.
- **Image processing — the summed-area table (a.k.a. integral image).** The 2-D version, below. It lets you compute the sum of pixels inside *any* rectangle in constant time regardless of the rectangle's size. Box blur uses it; so did the Viola–Jones face detector, which is why real-time face detection was possible on 2001-era hardware.
- **Weighted random selection.** Given items with weights `[5, 1, 3, 1]`, take the prefix sums `[5, 6, 9, 10]`, pick a random number in `[0, 10)`, and [[05-searching|binary search]] for where it lands. Each item is chosen in proportion to its weight, in O(log n). This is how ad servers pick a bid, how loot tables work in games, and how weighted A/B bucketing gets done.
- **Parallel and GPU computing**, where it's called **scan**. Despite looking hopelessly sequential (each total depends on the one before it), it parallelises in O(log n) depth — and it's the primitive underneath stream compaction, radix sort, and parallel memory allocation. See [[foundations/gpu-and-parallel-computing/04-parallel-patterns|parallel patterns]] for why that's surprising.
- **Rate limiting and scheduling** — "how many requests in the last N seconds", "is this booking window free" — anything phrased as *aggregate over a contiguous span* of a fixed timeline.

## How it works

Build an array `P` where `P[i]` = the sum of everything before index `i`. Padding with a leading `0` (a sentinel) is worth doing — it makes `P[0]` mean "nothing so far" and kills the `i == 0` special case:

```
A →     [1, 2, 3, 4,  5,  6]
P →  [0, 1, 3, 6, 10, 15, 21]
      ^ sentinel: sum of the empty prefix
```

Each entry is the previous entry plus one element, so building it is a single pass:

```python
def build_prefix_sums(nums):
    prefix = [0] * (len(nums) + 1)   # prefix[0] = 0 sentinel avoids the i==0 special case
    for i, num in enumerate(nums):
        prefix[i + 1] = prefix[i] + num
    return prefix

def range_sum(prefix, i, j):          # sum of nums[i..j] inclusive
    return prefix[j + 1] - prefix[i]
```

With the sentinel, `range_sum(P, 0, 2)` = `P[3] - P[0]` = `6 - 0` = 6 — no branch needed for a range that starts at the beginning.

## The 2-D version: summed-area tables

Same trick on a grid. `S[r][c]` = sum of the whole rectangle from the top-left corner down to `(r, c)`. Building it reuses the three neighbours already computed:

```python
S[r][c] = grid[r][c] + S[r-1][c] + S[r][c-1] - S[r-1][c-1]
#                      ^ above     ^ left      ^ added twice, subtract once
```

And any rectangle `(r1,c1)..(r2,c2)` comes out in four lookups by inclusion–exclusion:

```
sum = S[r2][c2] - S[r1-1][c2] - S[r2][c1-1] + S[r1-1][c1-1]
```

The `+ S[r1-1][c1-1]` is there because the top-left block got subtracted twice — once by each of the two strips. Constant time for a 3×3 window or a 3000×3000 one, which is exactly why image filters use it.

## The hash-map variant — the one that trips people up

Plain prefix sums answer *"what's the sum of this range I'm naming?"* The harder question is the reverse: *"is there **any** range summing to k?"* — that's **Subarray Sum Equals K** (LeetCode #560), and the mechanical trick is worth internalising because it recurs constantly.

Rearrange the definition. A subarray ending at `j` sums to `k` when:

```
prefix[j] - prefix[i] == k      ->      prefix[i] == prefix[j] - k
```

So while sweeping, at each position you already know `prefix[j]` and `k`. The question "does a valid subarray end here?" becomes **"have I seen the prefix sum `prefix[j] - k` before, and how many times?"** — a hash-map lookup, not a search.

```python
def subarray_sum(nums, k):
    seen = {0: 1}          # the empty prefix, so subarrays starting at index 0 count
    running = 0
    count = 0
    for num in nums:
        running += num
        count += seen.get(running - k, 0)   # every earlier prefix that closes a k-sum here
        seen[running] = seen.get(running, 0) + 1
    return count
```

The array of prefix sums became a **[[03-hash-maps|hash map]] of prefix sum → how many times seen**, because you no longer care *where* the prefixes were, only that they existed. O(n) time, one pass.

Two common re-skins of the same move:

- **Contiguous Array** — longest subarray with equal 0s and 1s. Count each `0` as `-1`, and "equal counts" becomes "sum is zero", which becomes "this prefix sum has appeared before". Store the *first* index each prefix sum was seen at, and the distance between the two sightings is a valid subarray.
- **Subarray sums divisible by k** — store `running % k` instead of `running`. Two positions with the same remainder bracket a subarray divisible by `k`.

The general shape: **transform the elements so the property you want becomes "sum is 0" or "sums are equal", then let the hash map find repeats.**

## Complexity

O(n) to build, O(1) per query — versus O(n) per query if you sum the range directly every time. For q queries, that's O(n + q) total instead of O(n·q). Space is O(n) for the prefix array, though the streaming variants above keep only a running scalar plus a map.

## Gotchas

- **Inclusive vs exclusive off-by-ones** are the number-one bug here. Pick the sentinel-padded convention (`P[i]` = sum of everything *before* `i`) and stay in it; mixing conventions mid-problem is how `range_sum` quietly returns a number one element too big.
- **Prefix sums only work for invertible operations.** Sum, XOR, and count are invertible — you can subtract off the part you don't want. **Max and min are not**: knowing `max(A[0..5])` and `max(A[0..1])` tells you nothing about `max(A[2..5])`. That's why range-max needs a sparse table or segment tree instead, and why [[014-trapping-rain-water|Trapping Rain Water]] builds *directional* prefix/suffix maxima arrays and reads them, rather than subtracting.
- **The array has to be static.** One update to `nums[i]` invalidates every prefix sum from `i` onward. If updates are frequent, you want a Fenwick tree (binary indexed tree) or segment tree — O(log n) for both update and query — rather than an O(n) rebuild each time.
- **Overflow** in fixed-width languages: the prefix sums grow to the total of the whole array, which can exceed `int` even when every element is small. Use a 64-bit type.
- **Reaching for it with only one query to answer.** Preprocessing costs O(n); a single range sum also costs O(n). It only pays when the cost is amortised over many queries.

## Implementation — complete runnable example

**Runnable example:** save as `prefix_sum_lab.py` and run `python3 prefix_sum_lab.py`. Standard library only; writes no files. Every result is checked against a brute-force computation.

```python
def build_prefix(values):
    """P[i] = sum of everything BEFORE index i. The leading 0 is a sentinel
    that removes the i == 0 special case from every query."""
    prefix = [0]
    for v in values:
        prefix.append(prefix[-1] + v)
    return prefix

def range_sum(prefix, lo, hi):
    """Sum of values[lo..hi] inclusive -- two lookups and a subtraction."""
    return prefix[hi + 1] - prefix[lo]

def build_prefix_2d(grid):
    """Summed-area table: S[r][c] = sum of the rectangle from (0,0) to (r-1,c-1)."""
    rows, cols = len(grid), len(grid[0])
    s = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(cols):
            s[r+1][c+1] = (grid[r][c] + s[r][c+1] + s[r+1][c] - s[r][c])
    return s

def rect_sum(s, r1, c1, r2, c2):
    """Inclusion-exclusion: whole - top - left + the corner counted twice."""
    return s[r2+1][c2+1] - s[r1][c2+1] - s[r2+1][c1] + s[r1][c1]

def subarrays_summing_to(values, target):
    """The hash-map variant. Counts subarrays whose sum is exactly `target`.

    If prefix[j] - prefix[i] == target, then prefix[i] == prefix[j] - target,
    so count how many earlier prefixes had that value."""
    seen, running, count = {0: 1}, 0, 0
    for v in values:
        running += v
        count += seen.get(running - target, 0)
        seen[running] = seen.get(running, 0) + 1
    return count

if __name__ == "__main__":
    revenue = [120, 340, 90, 210, 400, 150]
    prefix = build_prefix(revenue)
    print(f"revenue: {revenue}")
    print(f"prefix:  {prefix}   <- one longer, leading sentinel")
    print()
    print("range queries, each O(1) regardless of width:")
    for lo, hi in [(2, 5), (0, 0), (0, 5), (3, 3)]:
        got = range_sum(prefix, lo, hi)
        want = sum(revenue[lo:hi+1])
        print(f"  days {lo}..{hi}: {got:5d}   (brute force {want})")
        assert got == want

    print()
    print("2D summed-area table:")
    grid = [[1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]]
    s = build_prefix_2d(grid)
    for r1, c1, r2, c2 in [(0, 0, 2, 2), (1, 1, 2, 2), (0, 1, 1, 2)]:
        got = rect_sum(s, r1, c1, r2, c2)
        want = sum(grid[r][c] for r in range(r1, r2+1) for c in range(c1, c2+1))
        print(f"  rect ({r1},{c1})..({r2},{c2}) = {got:3d}   (brute force {want})")
        assert got == want

    print()
    print("hash-map variant -- subarrays summing to a target:")
    for values, target in [([1, 1, 1], 2), ([1, 2, 3], 3), ([3, 4, 7, 2, -3, 1, 4, 2], 7)]:
        got = subarrays_summing_to(values, target)
        want = sum(1 for i in range(len(values)) for j in range(i, len(values))
                   if sum(values[i:j+1]) == target)
        print(f"  {str(values):32s} target {target}: {got} subarrays  (brute force {want})")
        assert got == want

    print()
    print("  note the negative number in the last case -- the hash-map variant")
    print("  handles it, but a sliding window would NOT: it assumes growing the")
    print("  window only increases the sum, which negatives break.")
    print()
    print("prefix_sum_lab: passed")
```

Expected output:

```
revenue: [120, 340, 90, 210, 400, 150]
prefix:  [0, 120, 460, 550, 760, 1160, 1310]   <- one longer, leading sentinel

range queries, each O(1) regardless of width:
  days 2..5:   850   (brute force 850)
  days 0..0:   120   (brute force 120)
  days 0..5:  1310   (brute force 1310)
  days 3..3:   210   (brute force 210)

2D summed-area table:
  rect (0,0)..(2,2) =  45   (brute force 45)
  rect (1,1)..(2,2) =  28   (brute force 28)
  rect (0,1)..(1,2) =  16   (brute force 16)

hash-map variant -- subarrays summing to a target:
  [1, 1, 1]                        target 2: 2 subarrays  (brute force 2)
  [1, 2, 3]                        target 3: 2 subarrays  (brute force 2)
  [3, 4, 7, 2, -3, 1, 4, 2]        target 7: 4 subarrays  (brute force 4)

  note the negative number in the last case -- the hash-map variant
  handles it, but a sliding window would NOT: it assumes growing the
  window only increases the sum, which negatives break.

prefix_sum_lab: passed
```

## Check your understanding (self-assessment)

Attempt these before opening the answers.

1. **Why does the prefix array have one more element than the input?**
   <details><summary>Answer</summary>
   The leading <code>0</code> is a <strong>sentinel</strong> meaning "the sum of the empty prefix". Without it, a query starting at index 0 would need <code>prefix[hi]</code> with no <code>prefix[-1]</code> to subtract, forcing an <code>if lo == 0</code> special case into every query. One extra element removes that branch everywhere.
   </details>

2. **Given , write the prefix array and use it to find the sum of indices 1 to 2.**
   <details><summary>Answer</summary>
   <code>P = [0, 2, 6, 12, 20]</code>. Sum of indices 1..2 is <code>P[3] - P[1] = 12 - 2 = 10</code>, and indeed <code>4 + 6 = 10</code>.
   </details>

3. **Why does the 2-D version subtract two rectangles and then add one back?**
   <details><summary>Answer</summary>
   <strong>Inclusion–exclusion.</strong> Removing the strip above and the strip to the left removes their overlapping corner <em>twice</em>, so it must be added back once. That is the <code>+ s[r1][c1]</code> term.
   </details>

4. **Could you use a sliding window instead of the hash-map variant to count subarrays summing to k?**
   <details><summary>Answer</summary>
   <strong>Only if every value is non-negative.</strong> A sliding window assumes that growing the window can only increase the sum, so shrinking from the left is a valid response to overshooting. Negative numbers break that monotonicity — the sum can fall as the window grows — and the window may skip valid answers.<br>
   The lab's last test case includes <code>-3</code> for exactly this reason. The prefix-sum-plus-hash-map approach makes no monotonicity assumption and handles negatives correctly.
   </details>

## Practice problems

**In the [[foundations/dsa/neetcode-150/index|NeetCode 150]]** — solved and written up here:

1. [[007-product-of-array-except-self|Product of Array Except Self]] (LeetCode #238) — the multiplicative sibling: prefix products from the left, suffix products from the right, meet at each index.
2. [[014-trapping-rain-water|Trapping Rain Water]] (LeetCode #42) — prefix/suffix *maxima* instead of sums. Same "combine information from both directions" shape, and a good illustration of the non-invertibility gotcha above.
3. [[122-maximum-subarray|Maximum Subarray]] (LeetCode #53) — Kadane's algorithm is prefix-sum reasoning in disguise: the best subarray ending at `j` is `prefix[j]` minus the smallest prefix before it, so track the running minimum instead of an array.
4. [[015-best-time-to-buy-and-sell-stock|Best Time to Buy and Sell Stock]] (LeetCode #121) — literally "current value minus the smallest prefix value seen so far"; the same running-minimum move as #3.

**Not in the NeetCode 150** — worth doing on LeetCode directly, since they drill the core pattern more squarely than anything in the 150 does:

5. Range Sum Query - Immutable (#303) — the pattern in its purest form; if the dashboard example above made sense, this is that problem.
6. Subarray Sum Equals K (#560) — the hash-map variant, written out above. Do this one.
7. Contiguous Array (#525) — the `0 → -1` re-skin.
8. Range Sum Query 2D - Immutable (#304) — summed-area tables, the version image filters actually use.

## Before moving on

You are done with this pattern when you can, closed-book:

- [ ] Explain why the sentinel exists and what breaks without it.
- [ ] Build a prefix array and answer a range query with no off-by-one.
- [ ] Derive the inclusion–exclusion formula for the 2-D case.
- [ ] Explain why the hash-map variant handles negatives and a sliding window does not.

**Recap:** Prefix sums trade one O(n) preprocessing pass and O(n) space for O(1) range queries thereafter. Each entry stores the total up to that point, so subtracting two entries cancels everything before the range and leaves exactly the slice you asked for. The 2-D form uses inclusion–exclusion; the hash-map form counts subarrays with a given sum and, unlike a sliding window, works with negative values.

**Next:** [[02-two-pointers|two-pointers]] — the other pattern built on preprocessing a sequence, this time by sorting it so two indices can converge.

## Related
- [[01-arrays|arrays]] — the underlying structure and why contiguous storage makes the O(1) lookup real
- [[03-hash-maps|hash maps]] — what the prefix array becomes in the "find a subarray summing to k" variant
- [[03-sliding-window|sliding-window]] — the other main tool for contiguous-subarray questions; prefer it when the array has no negatives and you need a window, prefer prefix sums when you need arbitrary ranges or the values can be negative
- [[09-max-slice-algorithms|max-slice algorithms]] — Kadane and friends, where the running-prefix idea gets its own family
- [[foundations/gpu-and-parallel-computing/04-parallel-patterns|parallel patterns]] — prefix sum as *scan*, and why it parallelises despite looking sequential
- [[01-algorithms|algorithms]]
