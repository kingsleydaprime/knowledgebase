# Module: Greedy Algorithms (Locally Optimal, Globally Correct)

Welcome to the **Greedy Algorithms** module. A greedy algorithm builds a solution step-by-step by always making the **locally best choice** at each step—with no backtracking and no reconsidering past decisions.

The appeal is speed: greedy solutions are often dramatically faster than dynamic programming or brute-force alternatives. The critical caveat: **greedy is only correct for some problems**, and applying it where it doesn't hold produces a wrong answer *without error or warning*.

---

## Before you start

- You can reason about complexity — [[01-algorithms|complexity analysis]].
- You have seen sorting used as a preprocessing step — [[04-sorting/index|sorting]].
- Helpful: [[03-proof-techniques|proof techniques]], since the interesting part here is *proving* a greedy choice correct.

**After this lesson you will be able to:**

1. State the two properties a problem needs for greedy to work: **greedy choice** and **optimal substructure**.
2. Prove a greedy algorithm correct with an **exchange argument**.
3. **Demonstrate greedy failing**, and say precisely which property was missing.
4. Recognise the shape well enough to know when to reach for dynamic programming instead.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 3 is where greedy breaks.

---

## 1. Real-World Motivation & Physical Metaphors

Imagine navigating a **mountain hiking trail** to maximize altitude gain:

```
Branch at Junction:
           [+150m]
         /
 Start -<
         \
           [+200m] → [−300m]
```

- **Greedy Choice**: Always pick the steeper branch right now → takes `+200m` branch.
- **Result**: Ends at `+200 − 300 = −100m` net gain.
- **Optimal Choice**: Take `+150m` branch → net gain of `+150m`.

The greedy algorithm fails here because a locally attractive choice locks out a better long-term outcome.

### When Greedy Works (and When It Doesn't):
1. ✅ **Activity Selection / Interval Scheduling**: Picking jobs to maximize throughput by always taking the job that finishes earliest.
2. ✅ **Huffman Coding**: Building optimal prefix codes by always merging the two lowest-frequency nodes.
3. ❌ **Coin Change (arbitrary denominations)**: The largest-coin-first strategy fails for denominations like `{1, 3, 4}`.
4. ❌ **0/1 Knapsack**: Taking the highest-value-per-weight item first ignores capacity interactions.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Analogy |
| :--- | :--- | :--- |
| **Greedy Choice** | The locally optimal decision made at each step without reconsidering past choices. | Always eating the biggest slice of pizza first. |
| **Greedy Proof (Exchange Argument)** | Mathematical proof showing that swapping any greedy choice for any alternative can never improve the outcome. | Showing that no alternative seating arrangement can produce a better result. |
| **Greedy Failure** | A case where the locally best choice prevents reaching the global optimum. | A coin-change denomination set that breaks the largest-first heuristic. |
| **Optimal Substructure** | The property that an optimal solution is composed of optimal solutions to subproblems. | Required for both greedy algorithms and dynamic programming. |

---

## 3. The Classic Trap: Coin Changing

**Problem**: Given coin denominations, make a target amount using the fewest coins.

```python
def greedy_coin_change(denominations: list, amount: int) -> list:
    """Greedy: always use the largest denomination that fits."""
    result = []
    for coin in sorted(denominations, reverse=True):
        count, amount = divmod(amount, coin)
        if count > 0:
            result.append((coin, count))
    return result

# Denominations {1, 2, 5}: amount = 11
# Greedy gives: 5 + 5 + 1 = 3 coins  ✓ (CORRECT for this set)

# Denominations {1, 3, 4}: amount = 6
# Greedy gives: 4 + 1 + 1 = 3 coins  ✗ (WRONG! Optimal is 3 + 3 = 2 coins)
```

**Why it fails**: Choosing 4 (greedy best) blocks us from the globally optimal `3+3` combination. Dynamic Programming handles this correctly.

---

## 4. A Provably Correct Greedy: Canoe Pairing

**Problem**: Pair $N$ people (with known weights) into canoes of maximum capacity $k$. Minimize the number of canoes.

**Greedy Strategy**: Always try to pair the **heaviest remaining person** with the **lightest remaining person**. If they exceed capacity $k$, the heaviest person goes alone.

```python
def min_canoes(weights: list, k: int) -> int:
    """O(n log n): Greedy two-pointer canoe pairing."""
    weights.sort()
    canoes = 0
    left, right = 0, len(weights) - 1
    
    while left <= right:
        # Try to pair lightest with heaviest
        if weights[left] + weights[right] <= k:
            left += 1   # Lightest successfully paired with heaviest
        right -= 1      # Heaviest is always seated (paired or alone)
        canoes += 1
        
    return canoes
```

### Why This Greedy is Correct (Exchange Argument):
Consider the heaviest person `H`. If `H` can share with *anyone*, they can definitely share with the **lightest person** `L`—because if some optimal solution pairs `H` with a heavier person `X` instead:
- Swapping `X` and `L` can only maintain or improve the result (L is lighter than X, so it fits anywhere X did).
- Therefore, pairing `H` with `L` is **never worse** than any alternative.

We can safely commit to this greedy choice and reduce the problem to the remaining people—which is exactly the inductive proof structure for correctness.

---

## 5. Greedy vs. Dynamic Programming Decision Guide

| Signal | Use |
| :--- | :--- |
| A locally best choice can be proven **never worse** than alternatives (exchange argument holds). | **Greedy** — fastest when it applies. |
| Choices interact—"best now" can block a better future outcome. | **Dynamic Programming** — guarantees global optimum. |
| Problem is small and you need a correct baseline. | **Brute Force** — enumerate all possibilities. |

> [!TIP]
> **The key test**: Ask "Can I prove that the greedy choice is at least as good as any alternative using an exchange argument?" If yes, greedy is safe. If not, switch to DP.

---

## 6. Time & Space Complexity

Greedy algorithms typically achieve:
- **Time**: $O(n \log n)$ (dominated by sorting to find the locally optimal choice).
- **Space**: $O(1)$ auxiliary (no memoization table needed).

The canoe pairing example is characteristic: sort once in $O(n \log n)$, then a single two-pointer scan in $O(n)$.

---

## Implementation — complete runnable example

**Runnable example:** save as `greedy.py` in any empty directory and run `python3 greedy.py`. Standard library only; writes no files.

```python
"""Greedy: two problems where it is provably right, and two where it is not."""
from functools import lru_cache
from itertools import combinations


def activity_selection(intervals):
    """Take the activity that FINISHES earliest, every time."""
    chosen = []
    last_end = float("-inf")
    for start, end in sorted(intervals, key=lambda p: p[1]):
        if start >= last_end:
            chosen.append((start, end))
            last_end = end
    return chosen


def activity_brute(intervals):
    """Every compatible subset, exhaustively."""
    best = []
    for r in range(len(intervals), 0, -1):
        for combo in combinations(sorted(intervals, key=lambda p: p[1]), r):
            if all(combo[i][1] <= combo[i + 1][0] for i in range(len(combo) - 1)):
                return list(combo)
    return best


def greedy_by_start(intervals):
    """A plausible-looking alternative: take whatever STARTS earliest."""
    chosen, last_end = [], float("-inf")
    for start, end in sorted(intervals):
        if start >= last_end:
            chosen.append((start, end))
            last_end = end
    return chosen


def fractional_knapsack(items, capacity):
    """items: (value, weight). Fractions allowed - greedy by density is optimal."""
    total, taken = 0.0, []
    for value, weight in sorted(items, key=lambda it: it[0] / it[1], reverse=True):
        if capacity <= 0:
            break
        take = min(weight, capacity)
        total += value * take / weight
        taken.append((value, weight, take / weight))
        capacity -= take
    return total, taken


def knapsack_01_greedy(items, capacity):
    """The SAME greedy rule, but fractions are not allowed."""
    total, weight_used = 0, 0
    for value, weight in sorted(items, key=lambda it: it[0] / it[1], reverse=True):
        if weight_used + weight <= capacity:
            total += value
            weight_used += weight
    return total


def knapsack_01_optimal(items, capacity):
    @lru_cache(maxsize=None)
    def best(i, cap):
        if i == len(items) or cap == 0:
            return 0
        value, weight = items[i]
        skip = best(i + 1, cap)
        take = value + best(i + 1, cap - weight) if weight <= cap else 0
        return max(skip, take)
    return best(0, capacity)


def coin_change_greedy(coins, amount):
    used = []
    for c in sorted(coins, reverse=True):
        while amount >= c:
            amount -= c
            used.append(c)
    return (used, 0) if amount == 0 else (None, amount)


def coin_change_optimal(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else None


if __name__ == "__main__":
    print("Block 1 - activity selection: greedy by EARLIEST FINISH is optimal")
    acts = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9), (6, 10), (8, 11), (8, 12)]
    g = activity_selection(acts)
    b = activity_brute(acts)
    print(f"  {len(acts)} activities")
    print(f"    greedy (earliest finish): {g}  -> {len(g)} chosen")
    print(f"    exhaustive search:        {b}  -> {len(b)} chosen")
    assert len(g) == len(b)
    print("  same count as the exhaustive optimum")

    print()
    print("  but the greedy RULE matters - 'earliest start' is not optimal:")
    print(f"    greedy (earliest start):  {greedy_by_start(acts)} -> {len(greedy_by_start(acts))} chosen")
    assert len(greedy_by_start(acts)) < len(g)
    print("  one long early activity blocks everything after it.")
    print("  Earliest-finish works because it leaves the most room for what follows -")
    print("  that is the exchange argument: swapping any other first choice for the")
    print("  earliest-finishing one never makes the remaining problem harder.")

    print()
    print("Block 2 - fractional knapsack: greedy by value density is optimal")
    items = [(60, 10), (100, 20), (120, 30)]
    total, taken = fractional_knapsack(items, 50)
    print(f"  items (value, weight): {items}, capacity 50")
    for v, w, frac in taken:
        print(f"    took {frac*100:5.1f}% of item (value {v}, weight {w})")
    print(f"  total value {total}")
    assert abs(total - 240.0) < 1e-9
    print("  fractions make it work: you can always fill the bag exactly,")
    print("  so taking the densest first is never wrong")

    print()
    print("Block 3 - 0/1 knapsack: the SAME rule now fails")
    items = [(60, 10), (100, 20), (120, 30)]
    g_val = knapsack_01_greedy(items, 50)
    o_val = knapsack_01_optimal(tuple(items), 50)
    print(f"  same items, capacity 50, but NO fractions allowed")
    print(f"    greedy by density: {g_val}")
    print(f"    true optimum:      {o_val}")
    assert g_val < o_val
    print(f"  greedy is short by {o_val - g_val}. The greedy-choice property fails:")
    print("  taking the densest item first can leave capacity that nothing fits into.")
    print("  The subproblem left behind depends on WHICH items you took, not just")
    print("  how much room is left - so you need dynamic programming.")

    print()
    print("Block 4 - coin change: greedy depends on the coin SYSTEM")
    for coins, amount in [([1, 5, 10, 25], 30), ([1, 3, 4], 6), ([1, 5, 10, 25], 63),
                          ([1, 7, 10], 14)]:
        used, left = coin_change_greedy(coins, amount)
        opt = coin_change_optimal(coins, amount)
        n_greedy = len(used) if used else None
        flag = "" if n_greedy == opt else "   <-- greedy is WRONG"
        print(f"  coins {str(coins):16} amount {amount:3}: greedy {n_greedy} coins, "
              f"optimal {opt} coins{flag}")
    used, _ = coin_change_greedy([1, 3, 4], 6)
    assert len(used) == 3 and coin_change_optimal([1, 3, 4], 6) == 2
    print("  with {1,3,4} and amount 6, greedy takes 4+1+1 = 3 coins;")
    print("  the optimum is 3+3 = 2. Real currencies are designed to be 'canonical',")
    print("  which is precisely why greedy feels universally right - it is a")
    print("  property of the coin set, not of the algorithm.")

    print()
    print("Block 5 - the two properties, and how to tell")
    print("   greedy choice property:  a locally optimal choice is part of SOME global optimum")
    print("   optimal substructure:    the rest of the problem is the same problem, smaller")
    print()
    print("   problem                  greedy choice   optimal substructure   greedy works")
    rows = [("activity selection", "yes", "yes", "YES"),
            ("fractional knapsack", "yes", "yes", "YES"),
            ("minimum spanning tree", "yes", "yes", "YES"),
            ("0/1 knapsack", "NO", "yes", "no - use DP"),
            ("coin change {1,3,4}", "NO", "yes", "no - use DP")]
    for a, b, c, d in rows:
        print(f"   {a:24} {b:15} {c:22} {d}")
    print("  optimal substructure alone is not enough - DP needs it too. The greedy")
    print("  choice property is the extra requirement, and the one that usually fails.")

    print()
    print("greedy: passed")
```

Expected output:

```
Block 1 - activity selection: greedy by EARLIEST FINISH is optimal
  9 activities
    greedy (earliest finish): [(1, 4), (5, 7), (8, 11)]  -> 3 chosen
    exhaustive search:        [(1, 4), (5, 7), (8, 11)]  -> 3 chosen
  same count as the exhaustive optimum

  but the greedy RULE matters - 'earliest start' is not optimal:
    greedy (earliest start):  [(0, 6), (6, 10)] -> 2 chosen
  one long early activity blocks everything after it.
  Earliest-finish works because it leaves the most room for what follows -
  that is the exchange argument: swapping any other first choice for the
  earliest-finishing one never makes the remaining problem harder.

Block 2 - fractional knapsack: greedy by value density is optimal
  items (value, weight): [(60, 10), (100, 20), (120, 30)], capacity 50
    took 100.0% of item (value 60, weight 10)
    took 100.0% of item (value 100, weight 20)
    took  66.7% of item (value 120, weight 30)
  total value 240.0
  fractions make it work: you can always fill the bag exactly,
  so taking the densest first is never wrong

Block 3 - 0/1 knapsack: the SAME rule now fails
  same items, capacity 50, but NO fractions allowed
    greedy by density: 160
    true optimum:      220
  greedy is short by 60. The greedy-choice property fails:
  taking the densest item first can leave capacity that nothing fits into.
  The subproblem left behind depends on WHICH items you took, not just
  how much room is left - so you need dynamic programming.

Block 4 - coin change: greedy depends on the coin SYSTEM
  coins [1, 5, 10, 25]   amount  30: greedy 2 coins, optimal 2 coins
  coins [1, 3, 4]        amount   6: greedy 3 coins, optimal 2 coins   <-- greedy is WRONG
  coins [1, 5, 10, 25]   amount  63: greedy 6 coins, optimal 6 coins
  coins [1, 7, 10]       amount  14: greedy 5 coins, optimal 2 coins   <-- greedy is WRONG
  with {1,3,4} and amount 6, greedy takes 4+1+1 = 3 coins;
  the optimum is 3+3 = 2. Real currencies are designed to be 'canonical',
  which is precisely why greedy feels universally right - it is a
  property of the coin set, not of the algorithm.

Block 5 - the two properties, and how to tell
   greedy choice property:  a locally optimal choice is part of SOME global optimum
   optimal substructure:    the rest of the problem is the same problem, smaller

   problem                  greedy choice   optimal substructure   greedy works
   activity selection       yes             yes                    YES
   fractional knapsack      yes             yes                    YES
   minimum spanning tree    yes             yes                    YES
   0/1 knapsack             NO              yes                    no - use DP
   coin change {1,3,4}      NO              yes                    no - use DP
  optimal substructure alone is not enough - DP needs it too. The greedy
  choice property is the extra requirement, and the one that usually fails.

greedy: passed
```

Block 4 is worth sitting with: greedy coin change is correct for British and US coins and **wrong** for $\{1,3,4\}$. The algorithm did not change — the input did.

## 7. Common Pitfalls & Traps

1. **Applying Greedy Without Proof**: The largest-first coin change *feels* obviously correct but fails on certain denomination sets. Always verify with the exchange argument or a counterexample.
2. **Confusing Greedy with Heuristics**: A greedy algorithm is an exact algorithm that produces the globally optimal answer when applicable. It is **not** a heuristic approximation.
3. **Missing the Sort Step**: Most greedy algorithms require first sorting by the greedy criterion (finishing time, weight, cost-per-unit, etc.).

---

## 8. Check Your Understanding (University Self-Assessment)

1. **Question**: Why does the greedy largest-denomination-first coin change algorithm fail for denominations `{1, 3, 4}` when making change for 6?
   - <details><summary>Click for Answer</summary><b>Answer:</b> The greedy picks 4 first (locally largest ≤ 6), leaving 2, which requires two 1-coins → 3 total coins. But choosing 3+3 uses only 2 coins. Taking 4 greedily closes off the 3+3 path.</details>

2. **Question**: What mathematical technique is used to prove that a greedy algorithm is correct?
   - <details><summary>Click for Answer</summary><b>Answer:</b> The <b>exchange argument</b>: show that swapping any greedy choice for any alternative cannot improve the solution. If every greedy choice is at least as good as all alternatives, the full greedy sequence must be optimal.</details>

3. **Question**: What pattern does the canoe pairing solution share with a common two-pointer technique?
   - <details><summary>Click for Answer</summary><b>Answer:</b> The left pointer (lightest remaining) and right pointer (heaviest remaining) converge from both ends of the sorted array—this is the exact <b>Two Pointers</b> pattern applied greedily.</details>

---

## Practice — independent task

Write `is_canonical(coins, limit)` — decide whether greedy coin change is optimal for a given coin system.

1. For every amount from 1 to `limit`, compare the greedy count with the DP optimum. Return the **smallest counterexample**, or `None` if there is none.
2. Test on: US coins $\{1,5,10,25\}$; the classic failure $\{1,3,4\}$; $\{1,7,10\}$; and old British pre-decimal coins $\{1,3,6,12,24,30\}$.
3. **Then find the threshold.** There is a known result that if a system is non-canonical, the smallest counterexample is below a modest bound related to the largest two coins. Search for counterexamples with `limit` growing, and report where each failing system's smallest one appears.
4. Generate random coin systems, classify each, and report **what fraction are canonical**. The answer surprises people who assume greedy usually works.
5. Then design one: find a set of five coins, all under 100, that is canonical and covers every amount with fewer coins on average than the US set. Report your average over amounts 1–99 for both.

**Edge cases:** coin sets without a 1 (some amounts unmakeable — what should greedy return?); a single coin type; duplicate coin values; amount 0.

**Done when:** your classifier gets all four known systems right, your random-system fraction is backed by a number you measured, and your designed set genuinely beats the US average.

## Before moving on

You can state both properties, prove a greedy choice with an exchange argument, and produce a failing case on demand.

**Recap:** greedy needs the **greedy-choice property** (a local optimum is part of some global optimum) *and* **optimal substructure**; prove it with an exchange argument — show any optimal solution can be rewritten to include your greedy choice without getting worse; activity selection by earliest finish, fractional knapsack by density, and MST are all provably optimal; 0/1 knapsack and non-canonical coin systems are not, and need DP; optimal substructure alone is not enough, because DP requires it too.

**Next:** [[09-max-slice-algorithms|Max Slice]] — Kadane's algorithm, which is greedy and DP at the same time.

## Related Modules
- [[04-sorting/index|Sorting Algorithms]] — Most greedy algorithms begin with a sort
- [[02-two-pointers|Two Pointers Pattern]] — Structural shape of the canoe pairing solution
