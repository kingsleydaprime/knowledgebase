# Greedy Algorithms

> Added after reviewing Codility's own course PDFs in `pdfs/` (Chapter 16, `14-GreedyAlgorithms.pdf`) — not covered anywhere in this vault as its own technique, despite being one of the standard categories problems get classified into (alongside dynamic programming, divide-and-conquer, brute force).

Part of [[foundations/dsa/README|DSA fundamentals]]. A **greedy algorithm** builds a solution step by step, always making whichever choice looks best *right now*, with no backtracking and no reconsidering earlier choices once made. The appeal is speed — greedy solutions are usually much faster than the dynamic-programming or brute-force alternatives for the same problem. The catch, and the entire reason greedy needs its own note rather than being an obvious default: **greedy is only correct for some problems, not all** — and using it where it doesn't actually apply silently produces a wrong (suboptimal) answer, not a crash or an error.

---

## The trap, illustrated: coin changing

**Problem:** given a set of coin denominations, pay a given amount using the fewest coins possible. The greedy approach: always take the largest denomination that doesn't exceed what's left, repeat until done.

```python
def greedy_coin_changing(denominations, amount):
    result = []
    for coin in sorted(denominations, reverse=True):
        count, amount = divmod(amount, coin)
        result.append((coin, count))
    return result
```

For denominations `{1, 2, 5}`, this greedy approach happens to always find the true minimum. **For `{1, 3, 4}`, it doesn't:** paying 6 greedily takes the largest coin first (4), leaving 2, paid as two 1s — three coins total (4+1+1). The actual optimal answer is two coins (3+3). Same algorithm, same style of problem, and it silently returns a wrong answer for one denomination set while being perfectly correct for another — **this is the entire reason greedy can't be applied on faith.** Before using a greedy approach on a new problem, you need either a proof it's correct for this specific problem, or a known result that it is (dynamic programming — see [[foundations/dsa/06-patterns/15-dynamic-programming|dynamic-programming]] — is the fallback when greedy can't be proven correct, or is proven wrong).

**How correctness gets proven when greedy does work:** by induction — show that if an optimal solution exists that's consistent with every choice made *so far*, an optimal solution also exists consistent with the *next* choice. If that chain holds all the way through, the greedy sequence of "obviously best right now" choices is provably the same as some genuinely optimal solution, not just a plausible-looking one.

---

## A worked example where greedy is provably correct

**Problem:** seat `n` canoeists (given weights) into the minimum number of two-person canoes, where each canoe has a maximum combined weight `k`.

```python
def min_canoes(weights, k):
    weights.sort()
    canoes = 0
    i, j = 0, len(weights) - 1
    while i <= j:
        if weights[i] + weights[j] <= k:
            i += 1          # lightest fits with heaviest — pair them
        j -= 1               # heaviest is seated either way (paired, or alone)
        canoes += 1
    return canoes
```
The greedy choice: always try to pair the **heaviest remaining** person with the **lightest remaining** person. If they fit together, both are seated in one canoe; if not, the heaviest goes alone, and you try the same heaviest-with-lightest pairing on what's left. Every iteration seats at least one person, so this runs in **O(n)** (after an O(n log n) sort) — no per-canoeist backtracking or reconsideration needed.

**Why this greedy choice is actually correct** (not just a good heuristic): consider the heaviest person, `h`. If `h` can share a canoe with anyone at all, they can share it with the *lightest* person `l` specifically — because if some optimal solution pairs `h` with a different, heavier passenger `x` instead, swapping `x` and `l` never makes things worse (`l` is light enough to fit anywhere `x` did, and `x`, being heavier than `l` but still ≤ the person `l` would have partnered with, still fits its new spot too). Since pairing `h` with `l` is never worse than any alternative, it's safe to commit to that choice and reduce the problem to the remaining canoeists — which is exactly the inductive argument from the coin-changing section, applied concretely.

This pairing pattern — sort, then converge from both ends — is the same shape as [[foundations/dsa/06-patterns/02-two-pointers|two-pointers]]; greedy problems and the two-pointers pattern overlap often, since "always handle the current extreme (largest/smallest) first" is a natural fit for a two-pointer sweep.

---

## When to reach for greedy vs. its alternatives

| Signal | Approach |
|---|---|
| You can prove the locally-best choice is never worse than any alternative | Greedy — fastest option when it applies |
| Choices interact in ways where "best right now" can lock out a better later outcome | [[foundations/dsa/06-patterns/15-dynamic-programming|dynamic-programming]] |
| Problem is small enough, or you need a guaranteed-correct baseline to check other approaches against | Brute force |

## Related
- [[foundations/dsa/06-patterns/02-two-pointers|two-pointers]] — the canoeist solution's actual mechanical shape
- [[foundations/dsa/06-patterns/15-dynamic-programming|dynamic-programming]] — the fallback whenever greedy can't be proven correct
