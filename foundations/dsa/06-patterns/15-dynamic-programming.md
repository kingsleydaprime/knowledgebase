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

## The real skill: finding the recurrence relation

Every DP problem comes down to answering one question: **how does the answer to a state depend on smaller states?** For Fibonacci it's `dp[i] = dp[i-1] + dp[i-2]`. For Climbing Stairs (how many ways to climb n stairs, 1 or 2 steps at a time) it's the *same* recurrence, because the question is structurally identical: `dp[i] = dp[i-1] + dp[i-2]`. Recognizing that two differently-worded problems share a recurrence is most of what "getting good at DP" actually means.

## Common DP sub-patterns worth knowing by name

- **Fibonacci-style** — `dp[i]` depends on a fixed small number of previous states (Climbing Stairs, House Robber).
- **0/1 Knapsack** — choose a subset of items under a capacity constraint, each item used at most once (Partition Equal Subset Sum, Coin Change).
- **Longest Common Subsequence (LCS)** — comparing two sequences, `dp[i][j]` depends on `dp[i-1][j-1]`, `dp[i-1][j]`, `dp[i][j-1]`.
- **Longest Increasing Subsequence (LIS)** — `dp[i]` = best subsequence ending at index i, depends on all `dp[j]` for j < i.
- **Subset Sum** — a Knapsack variant: does *any* subset sum to a target?
- **Matrix Chain Multiplication** — optimal way to parenthesize/split a sequence, `dp[i][j]` depends on trying every split point between i and j.

Each of these is a distinct recurrence shape — worth its own worked example once you're solving problems, rather than trying to hold all six abstractly at once.

## Complexity

Varies by sub-pattern, but the general win is turning an exponential brute-force recursion into polynomial time — usually O(n) or O(n²) for the sub-patterns above, at the cost of O(n) or O(n²) space for the memo table (sometimes reducible to O(1) or O(n) if only the last row/few states are ever needed, as in the Fibonacci example above).

## Gotchas

- Reaching for DP without confirming overlapping subproblems exist first — if every subproblem is only ever solved once anyway, memoization adds overhead for no benefit; it's just plain recursion/divide-and-conquer (see [[04-sorting|merge sort]] for an example of recursion *without* overlapping subproblems).
- Off-by-one errors in the base cases (`dp[0]`, `dp[1]`) are the most common DP bug — get the smallest 1-2 states right by hand before trusting the recurrence for larger n.

## Practice problems
1. Climbing Stairs (LeetCode #70)
2. House Robber (LeetCode #198)
3. Coin Change (LeetCode #322)
4. Longest Common Subsequence (LeetCode #1143)
5. Longest Increasing Subsequence (LeetCode #300)
6. Partition Equal Subset Sum (LeetCode #416)

## Related
- [[01-algorithms|algorithms]] — where the exponential-vs-polynomial framing comes from
- [[14-backtracking|backtracking]] — same recursive-exploration shape, but without reusing overlapping subproblem results
