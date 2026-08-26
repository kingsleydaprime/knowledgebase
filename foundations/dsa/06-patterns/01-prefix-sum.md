# Pattern: Prefix Sum

Preprocess an [[01-arrays|array]] once so that any range-sum query afterward is O(1) instead of O(n). The trade is a single O(n) pass and O(n) extra space up front, paid once, to make every query after that nearly free.

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

## Practice problems

**In the [[foundations/dsa/neetcode-150/README|NeetCode 150]]** — solved and written up here:

1. [[007-product-of-array-except-self|Product of Array Except Self]] (LeetCode #238) — the multiplicative sibling: prefix products from the left, suffix products from the right, meet at each index.
2. [[014-trapping-rain-water|Trapping Rain Water]] (LeetCode #42) — prefix/suffix *maxima* instead of sums. Same "combine information from both directions" shape, and a good illustration of the non-invertibility gotcha above.
3. [[122-maximum-subarray|Maximum Subarray]] (LeetCode #53) — Kadane's algorithm is prefix-sum reasoning in disguise: the best subarray ending at `j` is `prefix[j]` minus the smallest prefix before it, so track the running minimum instead of an array.
4. [[015-best-time-to-buy-and-sell-stock|Best Time to Buy and Sell Stock]] (LeetCode #121) — literally "current value minus the smallest prefix value seen so far"; the same running-minimum move as #3.

**Not in the NeetCode 150** — worth doing on LeetCode directly, since they drill the core pattern more squarely than anything in the 150 does:

5. Range Sum Query - Immutable (#303) — the pattern in its purest form; if the dashboard example above made sense, this is that problem.
6. Subarray Sum Equals K (#560) — the hash-map variant, written out above. Do this one.
7. Contiguous Array (#525) — the `0 → -1` re-skin.
8. Range Sum Query 2D - Immutable (#304) — summed-area tables, the version image filters actually use.

## Related
- [[01-arrays|arrays]] — the underlying structure and why contiguous storage makes the O(1) lookup real
- [[03-hash-maps|hash maps]] — what the prefix array becomes in the "find a subarray summing to k" variant
- [[03-sliding-window|sliding-window]] — the other main tool for contiguous-subarray questions; prefer it when the array has no negatives and you need a window, prefer prefix sums when you need arbitrary ranges or the values can be negative
- [[09-max-slice-algorithms|max-slice algorithms]] — Kadane and friends, where the running-prefix idea gets its own family
- [[foundations/gpu-and-parallel-computing/04-parallel-patterns|parallel patterns]] — prefix sum as *scan*, and why it parallelises despite looking sequential
- [[01-algorithms|algorithms]]
