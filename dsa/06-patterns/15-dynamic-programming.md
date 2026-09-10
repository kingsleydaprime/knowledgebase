# Pattern: Dynamic Programming

**[Advanced]** — A university-level introduction to the dynamic programming pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You should understand recursion. See [[languages/06-python/04-functions-and-scope|Python functions and scope]] if needed.
- You should understand arrays and basic loops. See [[01-arrays|arrays]] if needed.

**What you will be able to do after this lesson:**

1. Define dynamic programming and explain why it's caching overlapping subproblems.
2. Implement top-down (memoization) and bottom-up (tabulation) DP solutions.
3. Apply the pattern to Fibonacci-style, knapsack, LCS, and edit distance problems.
4. Explain how to find the recurrence relation for a DP problem.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)

Imagine you're computing Fibonacci numbers. The naive recursive approach calls `fib(n-1)` and `fib(n-2)` for each `n`. But `fib(n-1)` also calls `fib(n-2)`, so `fib(n-2)` is computed twice. `fib(n-3)` is computed three times. And so on — the same subproblems get recomputed exponentially many times.

Dynamic programming's entire value proposition is eliminating that redundant recomputation. Break a problem into overlapping subproblems, solve each subproblem exactly once, and reuse those answers instead of recomputing them. DP only applies when a problem has two properties: **overlapping subproblems** (the same smaller question gets asked repeatedly) and **optimal substructure** (the best answer to the big problem is built directly from the best answers to its subproblems). Without both, you just have plain recursion — DP is specifically the _caching_ of that recursion's repeated work.

---

## 2. Definitions and terminology

| Term                        | Plain-English definition                                                             | Example / analogy                                                  |
| --------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| **Overlapping subproblems** | The same smaller question gets asked repeatedly                                      | `fib(3)` is computed multiple times in naive Fibonacci             |
| **Optimal substructure**    | The best answer to the big problem is built from the best answers to its subproblems | The best path to a node depends on the best paths to its neighbors |
| **Memoization**             | Top-down DP: cache results the first time each subproblem is solved                  | Remembering the answer to `fib(3)` so you don't recompute it       |
| **Tabulation**              | Bottom-up DP: build the answer iteratively from the smallest subproblems up          | Filling a table from the base cases up to the final answer         |
| **Recurrence relation**     | How the answer to a state depends on smaller states                                  | `dp[i] = dp[i-1] + dp[i-2]` for Fibonacci                          |

---

## 3. How it works — step by step

### Two ways to apply it

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

### The real skill: finding the recurrence relation

Every DP problem comes down to answering one question: **how does the answer to a state depend on smaller states?** For Fibonacci it's `dp[i] = dp[i-1] + dp[i-2]`. For Climbing Stairs (how many ways to climb n stairs, 1 or 2 steps at a time) it's the _same_ recurrence, because the question is structurally identical: `dp[i] = dp[i-1] + dp[i-2]`. Recognizing that two differently-worded problems share a recurrence is most of what "getting good at DP" actually means.

---

## 4. Implementation — complete runnable example

**Runnable example:** save as `dynamic_programming_lab.py` and run `python3 dynamic_programming_lab.py`. It uses only Python's standard library and creates no external files.

```python
def fib_memo(n, cache=None):
    """Top-down DP: memoized Fibonacci."""
    if cache is None:
        cache = {}
    if n <= 1:
        return n
    if n not in cache:
        cache[n] = fib_memo(n - 1, cache) + fib_memo(n - 2, cache)
    return cache[n]


def fib_tabulation(n):
    """Bottom-up DP: tabulated Fibonacci."""
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]


def rob(nums):
    """House Robber: max sum of non-adjacent elements."""
    prev, curr = 0, 0                       # dp[i-2], dp[i-1]
    for n in nums:
        prev, curr = curr, max(curr, prev + n)
    return curr


def coin_change(coins, amount):
    """Coin Change: fewest coins to make amount."""
    dp = [0] + [float("inf")] * amount      # dp[a] = fewest coins to make a
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], 1 + dp[a - c])
    return dp[amount] if dp[amount] != float("inf") else -1


def length_of_lis(nums):
    """Longest Increasing Subsequence."""
    dp = [1] * len(nums)                    # every element is an LIS of length 1 by itself
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp, default=0)


if __name__ == "__main__":
    # Test case 1: Fibonacci memoization
    result1 = fib_memo(10)
    print(f"Test 1 - fib memo:")
    print(f"fib(10) = {result1}")
    assert result1 == 55, f"Expected 55, got {result1}"

    # Test case 2: Fibonacci tabulation
    result2 = fib_tabulation(10)
    print(f"\nTest 2 - fib tabulation:")
    print(f"fib(10) = {result2}")
    assert result2 == 55, f"Expected 55, got {result2}"

    # Test case 3: House Robber
    nums3 = [2, 7, 9, 3, 1]
    result3 = rob(nums3)
    print(f"\nTest 3 - house robber:")
    print(f"nums={nums3} -> {result3}")
    assert result3 == 12, f"Expected 12, got {result3}"

    # Test case 4: Coin Change
    coins4 = [1, 2, 5]
    amount4 = 11
    result4 = coin_change(coins4, amount4)
    print(f"\nTest 4 - coin change:")
    print(f"coins={coins4}, amount={amount4} -> {result4}")
    assert result4 == 3, f"Expected 3, got {result4}"

    # Test case 5: LIS
    nums5 = [10, 9, 2, 5, 3, 7, 101, 18]
    result5 = length_of_lis(nums5)
    print(f"\nTest 5 - LIS:")
    print(f"nums={nums5} -> {result5}")
    assert result5 == 4, f"Expected 4, got {result5}"

    print("\ndynamic_programming_lab: passed")
```

Expected output:

```
Test 1 - fib memo:
fib(10) = 55

Test 2 - fib tabulation:
fib(10) = 55

Test 3 - house robber:
nums=[2, 7, 9, 3, 1] -> 12

Test 4 - coin change:
coins=[1, 2, 5], amount=11 -> 3

Test 5 - LIS:
nums=[10, 9, 2, 5, 3, 7, 101, 18] -> 4

dynamic_programming_lab: passed
```

---

## 5. Common DP sub-patterns

- **Fibonacci-style** — `dp[i]` depends on a fixed small number of previous states (Climbing Stairs, House Robber).
- **0/1 Knapsack** — choose a subset of items under a capacity constraint, each item used at most once (Partition Equal Subset Sum, Coin Change).
- **Longest Common Subsequence (LCS)** — comparing two sequences, `dp[i][j]` depends on `dp[i-1][j-1]`, `dp[i-1][j]`, `dp[i][j-1]`.
- **Longest Increasing Subsequence (LIS)** — `dp[i]` = best subsequence ending at index i, depends on all `dp[j]` for j < i.
- **Subset Sum** — a Knapsack variant: does _any_ subset sum to a target?
- **Matrix Chain Multiplication** — optimal way to parenthesize/split a sequence, `dp[i][j]` depends on trying every split point between i and j.

Each of these is a distinct recurrence shape — worth its own worked example once you're solving problems, rather than trying to hold all six abstractly at once. NeetCode splits these into **1-D DP** (the state is one index) and **2-D DP** (the state is two indices, usually a grid or a pair of sequences); the split below follows that.

### 1-D DP — the state is a single index

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

**Longest Increasing Subsequence (LIS)** — `dp[i]` = length of the best increasing subsequence _ending at_ i, depending on all earlier j with `nums[j] < nums[i]`: `dp[i] = 1 + max(dp[j])`. That's O(n²); a [[09-modified-binary-search|binary-search]]-on-a-patience-piles trick gets it to O(n log n).

```python
def length_of_lis(nums):
    dp = [1] * len(nums)                    # every element is an LIS of length 1 by itself
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp, default=0)
```

### 2-D DP — the state is two indices

When the answer depends on **two** moving parts — a position in a grid, or an index into _each_ of two sequences — the table becomes 2-D. The recurrence usually reads off a small set of neighbor cells.

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

**Edit Distance** — fewest insert/delete/replace to turn one string into another. Same 2-D shape, but the "no match" case takes `1 + min` of the three neighbors (each corresponding to one edit operation): `dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])`. LCS, Edit Distance, Distinct Subsequences, and Interleaving String are all the _same_ two-sequence grid with different cell rules — recognizing that is the 2-D-DP version of the recurrence-sharing insight above.

Most 2-D DP tables reduce to **two rows** (or one) of space, since each cell only reads the previous row and the current one.

---

## 6. Complexity

Varies by sub-pattern, but the general win is turning an exponential brute-force recursion into polynomial time — usually O(n) or O(n²) for the sub-patterns above, at the cost of O(n) or O(n²) space for the memo table (sometimes reducible to O(1) or O(n) if only the last row/few states are ever needed, as in the Fibonacci example above).

---

## 7. Tradeoffs and limitations

- **Reaching for DP without confirming overlapping subproblems exist first** — if every subproblem is only ever solved once anyway, memoization adds overhead for no benefit; it's just plain recursion/divide-and-conquer (see [[04-sorting|merge sort]] for an example of recursion _without_ overlapping subproblems).
- **Off-by-one errors in the base cases** (`dp[0]`, `dp[1]`) are the most common DP bug — get the smallest 1-2 states right by hand before trusting the recurrence for larger n.
- **Space optimization.** Many DP problems can be optimized to use O(1) or O(n) space instead of O(n²) by only keeping the last row/few states.

---

## 8. Check your understanding (self-assessment)

Attempt these without the note, then compare your reasoning below.

1. **Question:** Given `nums = [2, 7, 9, 3, 1]`, trace through the House Robber DP algorithm step by step.
2. **Question:** Why does the 0/1 Knapsack iterate capacity descending while the unbounded Knapsack iterates capacity outermost?
3. **Question:** What makes a problem suitable for DP?

### Answers — after your attempt

1. `prev=0, curr=0`
   `n=2: prev=0, curr=max(0, 0+2)=2`
   `n=7: prev=2, curr=max(2, 0+7)=7`
   `n=9: prev=7, curr=max(7, 2+9)=11`
   `n=3: prev=11, curr=max(11, 7+3)=11`
   `n=1: prev=11, curr=max(11, 11+1)=12`
   Return 12.
2. The 0/1 Knapsack iterates capacity descending so an item isn't counted twice (each item used at most once). The unbounded Knapsack iterates capacity outermost so items can be reused (each item can be used multiple times).
3. A problem is suitable for DP if it has overlapping subproblems (the same smaller question gets asked repeatedly) and optimal substructure (the best answer to the big problem is built directly from the best answers to its subproblems).

---

## 9. Practice — independent task

**Task:** Implement a function `climbing_stairs(n)` that returns the number of distinct ways to climb to the top of a staircase with `n` steps, where you can take 1 or 2 steps at a time. Use the Fibonacci-style DP pattern. Test it with the following cases:

- `n = 2` → expected `2` (1+1 or 2)
- `n = 3` → expected `3` (1+1+1, 1+2, 2+1)

**Done when:** your function returns the correct number of ways for both test cases.

---

## Practice problems

**In the [[foundations/dsa/neetcode-150/index|NeetCode 150]]** — solved and written up here:

1. [[099-climbing-stairs|Climbing Stairs]] (LeetCode #70) — Fibonacci — the first recurrence to write down.
2. [[100-min-cost-climbing-stairs|Min Cost Climbing Stairs]] (LeetCode #746) — the same shape with a cost attached.
3. [[101-house-robber|House Robber]] (LeetCode #198) — take-it-or-skip-it, in its clearest form.
4. [[102-house-robber-ii|House Robber II]] (LeetCode #213) — a circular constraint, handled by running the linear version twice.
5. [[103-longest-palindromic-substring|Longest Palindromic Substring]] (LeetCode #5) — expand around centres: $O(n^2)$ time, $O(1)$ space.
6. [[104-palindromic-substrings|Palindromic Substrings]] (LeetCode #647) — the same expansion, counting instead of maximising.
7. [[105-decode-ways|Decode Ways]] (LeetCode #91) — the recurrence branches on one digit or two.
8. [[106-coin-change|Coin Change]] (LeetCode #322) — unbounded knapsack, minimising.
9. [[107-maximum-product-subarray|Maximum Product Subarray]] (LeetCode #152) — track a running maximum **and** minimum, because a negative flips them.
10. [[108-word-break|Word Break]] (LeetCode #139) — reachability over string positions.
11. [[109-longest-increasing-subsequence|Longest Increasing Subsequence]] (LeetCode #300) — the $O(n^2)$ DP first, then the $O(n\log n)$ patience-sorting version.
12. [[110-partition-equal-subset-sum|Partition Equal Subset Sum]] (LeetCode #416) — subset-sum to half the total: a boolean knapsack.
13. [[111-unique-paths|Unique Paths]] (LeetCode #62) — the grid recurrence with nothing in the way.
14. [[112-longest-common-subsequence|Longest Common Subsequence]] (LeetCode #1143) — the template every sequence-alignment problem specialises.
15. [[119-edit-distance|Edit Distance]] (LeetCode #72) — three operations, one `min` — the canonical 2-D DP.
16. [[113-best-time-to-buy-and-sell-stock-with-cooldown|Buy/Sell Stock with Cooldown]] (LeetCode #309) — a state machine rather than a grid.
17. [[114-coin-change-ii|Coin Change II]] (LeetCode #518) — counting combinations, where **loop order** decides combinations versus permutations.
18. [[115-target-sum|Target Sum]] (LeetCode #494) — signs become a subset-sum count.
19. [[116-interleaving-string|Interleaving String]] (LeetCode #97) — 2-D reachability.
20. [[118-distinct-subsequences|Distinct Subsequences]] (LeetCode #115) — match adds, mismatch carries.
21. [[120-burst-balloons|Burst Balloons]] (LeetCode #312) — interval DP — think about the **last** balloon, not the first.
22. [[121-regular-expression-matching|Regular Expression Matching]] (LeetCode #10) — the hardest of the set.

**Not in the NeetCode 150** — worth doing on LeetCode directly, since they expose the loop-order and state-machine details the 150 lets you skip:

23. Minimum Path Sum (#64) — #62 with weights; do it immediately after.
24. Perfect Squares (#279) — coin change where the coins are squares.
25. Combination Sum IV (#377) — the loop-order counterpart to #518 — permutations, not combinations.
26. N-th Tribonacci Number (#1137) — a warm-up for state compression.
27. Best Time to Buy and Sell Stock IV (#188) — the general $k$-transaction version of #309.

## Before moving on

You are done with this pattern when you can, closed-book:

- [ ] State the two conditions a problem needs for DP to apply.
- [ ] Convert a recursive solution to a memoised one, then to a tabulated one.
- [ ] Identify the state and the recurrence for a problem you have not seen.
- [ ] Explain the space-optimisation from a 2D table to one or two rows.

**Recap:** Dynamic programming applies when a problem has optimal substructure and overlapping subproblems — the same sub-answer needed repeatedly. Memoisation caches results on the recursive form; tabulation fills a table bottom-up and avoids recursion entirely. The hard part is never the code: it is identifying the state and writing the recurrence.

## 10. Related

- [[01-algorithms|algorithms]] — where the exponential-vs-polynomial framing comes from
- [[14-backtracking|backtracking]] — same recursive-exploration shape, but without reusing overlapping subproblem results
- [[09-modified-binary-search|modified-binary-search]] — the O(n log n) LIS optimization
- [[13-bit-manipulation|bit manipulation]] — the Counting Bits DP recurrence, and bitmask DP over subsets
- [[15-dynamic-programming|dynamic-programming]] — this note

---

## 11. Further reading

The pattern appears in many contexts beyond LeetCode:

- **Bioinformatics:** Sequence alignment (DNA/protein comparison)
- **Natural language processing:** Edit distance for spell checking
- **Operations research:** Resource allocation and scheduling
- **Finance:** Optimal portfolio selection
- **Computer vision:** Image segmentation and object recognition

The core idea — break a problem into overlapping subproblems, solve each subproblem exactly once, and reuse those answers — is a fundamental algorithmic technique that appears whenever you need to optimize a recursive solution by caching repeated work.
