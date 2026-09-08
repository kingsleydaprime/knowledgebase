# Module: Greedy Algorithms (Locally Optimal, Globally Correct)

Welcome to the **Greedy Algorithms** module. A greedy algorithm builds a solution step-by-step by always making the **locally best choice** at each step—with no backtracking and no reconsidering past decisions.

The appeal is speed: greedy solutions are often dramatically faster than dynamic programming or brute-force alternatives. The critical caveat: **greedy is only correct for some problems**, and applying it where it doesn't hold produces a wrong answer *without error or warning*.

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

## Related Modules
- [[04-sorting|Sorting Algorithms]] — Most greedy algorithms begin with a sort
- [[02-two-pointers|Two Pointers Pattern]] — Structural shape of the canoe pairing solution
