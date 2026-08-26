# Pattern: Dynamic Programming

Break a problem into overlapping subproblems, solve each subproblem exactly once, and reuse those answers instead of recomputing them. DP only applies when a problem has two properties: **overlapping subproblems** (the same smaller question gets asked repeatedly) and **optimal substructure** (the best answer to the big problem is built directly from the best answers to its subproblems). Without both, you just have plain recursion — DP is specifically the *caching* of that recursion's repeated work.

## Why plain recursion isn't enough — naive Fibonacci

```python
def fib(n):                     # O(2^n) — see algorithms.md
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

`fib(5)` calls `fib(3)` twice, `fib(2)` three times, and so on — the same subproblems get recomputed exponentially many times. DP's entire value proposition is eliminating that redundant recomputation.

## Two ways to apply it

**Top-down (memoization)** — keep the natural recursive structure, but cache results the first time each subproblem is solved:

```python
def fib_memo(n, cache={}):
    if n <= 1:
        return n
    if n not in cache:
        cache[n] = fib_memo(n - 1, cache) + fib_memo(n - 2, cache)
    return cache[n]
```

**Bottom-up (tabulation)** — build the answer iteratively from the smallest subproblems up, no recursion at all:

```python
def fib_tabulation(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]     # this is the recurrence relation
    return dp[n]
```

Both are O(n) — the exponential blowup is gone the moment repeated subproblems stop being recomputed. Bottom-up avoids recursion's call-stack overhead entirely (see the space-complexity note in [[01-algorithms|algorithms]]); top-down is often easier to derive first, since it mirrors the natural recursive definition of the problem.

Fibonacci specifically can go even faster than O(n) — O(log n) via matrix exponentiation (`[[1,1],[1,0]]^n` encodes the recurrence), or a closed-form (Binet's formula, using the golden ratio). Neither is worth reaching for by default — they're a well-known footnote once O(n) DP stops being fast enough, not the normal answer.

## The real skill: finding the recurrence relation

Every DP problem comes down to answering one question: **how does the answer to a state depend on smaller states?** For Fibonacci it's `dp[i] = dp[i-1] + dp[i-2]`. For Climbing Stairs (how many ways to climb n stairs, 1 or 2 steps at a time) it's the *same* recurrence, because the question is structurally identical: `dp[i] = dp[i-1] + dp[i-2]`. Recognizing that two differently-worded problems share a recurrence is most of what "getting good at DP" actually means.

## Common DP sub-patterns worth knowing by name

- **Fibonacci-style** — `dp[i]` depends on a fixed small number of previous states (Climbing Stairs, House Robber).
- **0/1 Knapsack** — choose a subset of items under a capacity constraint, each item used at most once (Partition Equal Subset Sum, Coin Change).
- **Longest Common Subsequence (LCS)** — comparing two sequences, `dp[i][j]` depends on `dp[i-1][j-1]`, `dp[i-1][j]`, `dp[i][j-1]`.
- **Longest Increasing Subsequence (LIS)** — `dp[i]` = best subsequence ending at index i, depends on all `dp[j]` for j < i.
- **Subset Sum** — a Knapsack variant: does *any* subset sum to a target?
- **Matrix Chain Multiplication** — optimal way to parenthesize/split a sequence, `dp[i][j]` depends on trying every split point between i and j.

Each of these is a distinct recurrence shape — worth its own worked example once you're solving problems, rather than trying to hold all six abstractly at once. NeetCode splits these into **1-D DP** (the state is one index) and **2-D DP** (the state is two indices, usually a grid or a pair of sequences); the split below follows that.

## 1-D DP — the state is a single index

**House Robber** — max sum of non-adjacent elements. At each house you either rob it (and skip the previous) or skip it: `dp[i] = max(dp[i-1], dp[i-2] + nums[i])`. Only the last two states matter, so it collapses to O(1) space:

```python
def rob(nums):
    prev, curr = 0, 0                       # dp[i-2], dp[i-1]
    for n in nums:
        prev, curr = curr, max(curr, prev + n)
    return curr
```

**Coin Change** — fewest coins to make `amount`, each coin reusable. This is the **unbounded knapsack** shape (items reusable, unlike 0/1): `dp[a] = 1 + min(dp[a - c])` over every coin `c ≤ a`.

```python
def coin_change(coins, amount):
    dp = [0] + [float("inf")] * amount      # dp[a] = fewest coins to make a
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], 1 + dp[a - c])
    return dp[amount] if dp[amount] != float("inf") else -1
```

The 0/1 vs unbounded distinction is entirely in the loop order: reuse-allowed iterates capacity outermost (as here); each-item-once iterates items outermost and capacity **descending** so an item isn't counted twice.

**Longest Increasing Subsequence (LIS)** — `dp[i]` = length of the best increasing subsequence *ending at* i, depending on all earlier j with `nums[j] < nums[i]`: `dp[i] = 1 + max(dp[j])`. That's O(n²); a [[09-modified-binary-search|binary-search]]-on-a-patience-piles trick gets it to O(n log n).

```python
def length_of_lis(nums):
    dp = [1] * len(nums)                    # every element is an LIS of length 1 by itself
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp, default=0)
```

## 2-D DP — the state is two indices

When the answer depends on **two** moving parts — a position in a grid, or an index into *each* of two sequences — the table becomes 2-D. The recurrence usually reads off a small set of neighbor cells.

**Unique Paths** (grid, only right/down moves): each cell is reached from above or from the left → `dp[r][c] = dp[r-1][c] + dp[r][c-1]`, base case the first row/column = 1.

**Longest Common Subsequence (LCS)** — compare two strings char by char. If the characters match, extend the diagonal; otherwise take the better of dropping one character from either string:

```python
def lcs(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            if a[i] == b[j]:
                dp[i][j] = 1 + dp[i + 1][j + 1]     # match -> take the diagonal
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])   # skip a char in a or b
    return dp[0][0]
```

**Edit Distance** — fewest insert/delete/replace to turn one string into another. Same 2-D shape, but the "no match" case takes `1 + min` of the three neighbors (each corresponding to one edit operation): `dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])`. LCS, Edit Distance, Distinct Subsequences, and Interleaving String are all the *same* two-sequence grid with different cell rules — recognizing that is the 2-D-DP version of the recurrence-sharing insight above.

Most 2-D DP tables reduce to **two rows** (or one) of space, since each cell only reads the previous row and the current one.

## Complexity

Varies by sub-pattern, but the general win is turning an exponential brute-force recursion into polynomial time — usually O(n) or O(n²) for the sub-patterns above, at the cost of O(n) or O(n²) space for the memo table (sometimes reducible to O(1) or O(n) if only the last row/few states are ever needed, as in the Fibonacci example above).

## Gotchas

- Reaching for DP without confirming overlapping subproblems exist first — if every subproblem is only ever solved once anyway, memoization adds overhead for no benefit; it's just plain recursion/divide-and-conquer (see [[04-sorting|merge sort]] for an example of recursion *without* overlapping subproblems).
- Off-by-one errors in the base cases (`dp[0]`, `dp[1]`) are the most common DP bug — get the smallest 1-2 states right by hand before trusting the recurrence for larger n.

## Practice problems

Every problem below is written up in the [[foundations/dsa/neetcode-150/README|NeetCode 150]] — DP is the one pattern the 150 covers essentially completely.

**1-D DP** — [[099-climbing-stairs|Climbing Stairs]] (#70), [[100-min-cost-climbing-stairs|Min Cost Climbing Stairs]] (#746), [[101-house-robber|House Robber]] (#198) and [[102-house-robber-ii|House Robber II]] (#213, circular), [[106-coin-change|Coin Change]] (#322), [[107-maximum-product-subarray|Maximum Product Subarray]] (#152), [[108-word-break|Word Break]] (#139), [[109-longest-increasing-subsequence|Longest Increasing Subsequence]] (#300), [[110-partition-equal-subset-sum|Partition Equal Subset Sum]] (#416), [[105-decode-ways|Decode Ways]] (#91), [[103-longest-palindromic-substring|Longest Palindromic Substring]] (#5).

**2-D DP** — [[111-unique-paths|Unique Paths]] (#62), [[112-longest-common-subsequence|Longest Common Subsequence]] (#1143), [[114-coin-change-ii|Coin Change II]] (#518), [[115-target-sum|Target Sum]] (#494), [[119-edit-distance|Edit Distance]] (#72), [[116-interleaving-string|Interleaving String]] (#97), [[118-distinct-subsequences|Distinct Subsequences]] (#115), [[113-best-time-to-buy-and-sell-stock-with-cooldown|Best Time to Buy/Sell with Cooldown]] (#309), [[117-longest-increasing-path-in-a-matrix|Longest Increasing Path in a Matrix]] (#329).

## Related
- [[01-algorithms|algorithms]] — where the exponential-vs-polynomial framing comes from
- [[14-backtracking|backtracking]] — same recursive-exploration shape, but without reusing overlapping subproblem results
- [[09-modified-binary-search|modified-binary-search]] — the O(n log n) LIS optimization
- [[13-bit-manipulation|bit manipulation]] — the Counting Bits DP recurrence, and bitmask DP over subsets
