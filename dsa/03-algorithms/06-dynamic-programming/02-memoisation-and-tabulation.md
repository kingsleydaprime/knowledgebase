# Module: Memoisation and Tabulation (Writing the DP)

**[Intermediate]** — [[01-what-makes-a-problem-dp|Lesson 01]] decided *whether* dynamic programming applies. This lesson is *how to write one*, and it reduces to naming three things: **the state, the transition, and the base case.** Get those right and the code is mechanical. Get the state wrong and no amount of debugging the loop will save you.

There are two ways to fill the table — top-down with a cache, bottom-up with loops — and a third step most people skip, which is throwing most of the table away afterwards.

---

## Before you start

- You can test a problem for overlapping subproblems and optimal substructure — [[01-what-makes-a-problem-dp|what makes a problem DP]].
- You can write a recursive function and know that Python's recursion limit is about 1,000 frames — [[01-recursion-fundamentals|recursion fundamentals]].
- You can read a complexity as *states × transition cost* — [[01-growth-and-asymptotic-notation|growth and asymptotic notation]].

**After this lesson you will be able to:**

1. Name the **state**, **transition** and **base case** for a problem, and write either implementation from them.
2. Choose between **memoisation** and **tabulation** from the problem's properties rather than by habit.
3. Determine the correct **fill order** from the transition, and demonstrate what a wrong order produces.
4. Reduce a DP's memory by a whole dimension when the transition allows it.

**Study route:** read 1–4, answer the prediction in section 5, then run the lab. Section 6's memory discussion is the part that is usually missing from tutorials.

---

## 1. The three things you must name

Every dynamic program, without exception, is these three declarations plus a loop:

1. **STATE** — what one cell of the table *means*. Written as a sentence, not a variable name.
2. **TRANSITION** — how a cell is computed from cells with smaller indices. This is the recurrence.
3. **BASE CASE** — the cells you fill in directly, because there is nothing smaller to build them from.

Take climbing stairs — you can climb 1 or 2 steps at a time; how many distinct ways to reach step $n$?

- **STATE:** `ways[i]` = the number of distinct ways to reach step $i$.
- **TRANSITION:** `ways[i] = ways[i-1] + ways[i-2]` — you arrived at step $i$ either from $i-1$ with a 1-step, or from $i-2$ with a 2-step, and those are disjoint.
- **BASE:** `ways[0] = 1` (one way to stand still), `ways[1] = 1`.

**Write those three lines down before writing any code.** They are the design; everything after is transcription.

**The state is the hard one, and the hardest part of the state is making it a complete sentence.** "`dp[i]` is about index `i`" is not a state. "`dp[i]` is the number of ways to reach step `i`" is. If you cannot finish the sentence, you do not yet have a DP.

---

## Terms used here

1. **State**: This is one subproblem, identified by its parameters. The **state space** is the set of all of them, and its size is the first factor in the complexity.
2. **Transition**: This is also called the **recurrence** or the **recurrence relation**. This is the rule computing one state's answer from other states' answers. Its cost is the second factor in the complexity.
3. **Base case**: This is a state whose answer is known outright and needs no transition.
4. **Memoisation**: This is also called **top-down DP**. This is writing the recursion naturally and adding a cache, so a state is computed the first time it is requested and looked up thereafter.
5. **Tabulation**: This is also called **bottom-up DP**. This is filling the table with explicit loops in an order you choose, with no recursion.
6. **Fill order**: This is the sequence in which tabulation computes cells. **It is dictated by the transition**: every cell a transition reads must already hold its final value.
7. **Rolling array**: This is also called **space optimisation**. This is keeping only the last row (or the last few cells) of a table, when the transition never reaches further back than that.
8. **Reconstruction**: This is recovering the actual solution — the path, the subset, the string — rather than just its value, usually by walking the table backwards from the answer cell.

---

## 2. Filling the table, one cell at a time

The lab traces climbing stairs for $n = 8$:

```
     after |  0  1  2  3  4  5  6  7  8
      base |  1  1  0  0  0  0  0  0  0
       i=2 |  1  1  2  0  0  0  0  0  0
       i=3 |  1  1  2  3  0  0  0  0  0
       i=4 |  1  1  2  3  5  0  0  0  0
       i=5 |  1  1  2  3  5  8  0  0  0
       i=6 |  1  1  2  3  5  8 13  0  0
       i=7 |  1  1  2  3  5  8 13 21  0
       i=8 |  1  1  2  3  5  8 13 21 34
```

**Every new cell reads only cells already filled.** That single requirement is what fixes the fill order, and it is the whole of what "bottom-up" means.

(The values are Fibonacci numbers. That is not a coincidence — the recurrence is identical. Climbing stairs *is* Fibonacci with different base cases, which is worth noticing because it means the same table shape solves problems that sound unrelated.)

---

## 3. Four implementations, same recurrence

The lab runs naive recursion, memoisation, tabulation and a space-optimised loop, counting operations:

```
        n |     naive |  memoised | tabulated | rolling | answer agrees
       10 |       177 |        19 |         9 |       9 | True
       20 |    21,891 |        39 |        19 |      19 | True
       25 |   242,785 |        49 |        24 |      24 | True
       30 | 2,692,537 |        59 |        29 |      29 | True
```

**Naive is exponential; the other three are linear.** Memoisation's count is about $2n$ because each state is entered once as a miss and once as a hit; tabulation's is $n$ because there are no lookups at all.

### Memoisation — top-down

```python
def climb(n, memo=None):
    if memo is None:
        memo = {}
    if n <= 1:
        return 1
    if n in memo:
        return memo[n]
    memo[n] = climb(n - 1, memo) + climb(n - 2, memo)
    return memo[n]
```

**The recursion is unchanged from the naive version.** Three lines were added. This is why memoisation is the right first move: you write the recurrence exactly as you reasoned about it, then cache.

> **Use `memo=None` and create the dict inside.** `def climb(n, memo={})` shares one dictionary across every call for the lifetime of the process, including calls from unrelated code — a classic Python trap.

### Tabulation — bottom-up

```python
def climb(n):
    ways = [0] * (n + 1)
    ways[0] = 1
    if n >= 1:
        ways[1] = 1
    for i in range(2, n + 1):
        ways[i] = ways[i - 1] + ways[i - 2]
    return ways[n]
```

Same recurrence, written as a loop, with the order made explicit by you rather than by the call stack.

---

## 4. Which one to use

| | Memoisation (top-down) | Tabulation (bottom-up) |
| :--- | :--- | :--- |
| Write it as | the recurrence, directly | a loop |
| Computes | only states actually **needed** | **every** state |
| Fill order | handled by the call stack | **you** choose it |
| Depth limit | yes — about 1,000 frames in CPython | none |
| Space optimisation | awkward | easy |
| Debugging | print on cache miss | print the table |

The lab makes the depth limit concrete:

```
   memoised(50,000)     : RecursionError -- the recursion depth, not the cache
   tabulated(50,000)    : fine -- it is a loop. Answer has ~10,450 digits
```

**The rule:** if the state space is **sparse** — you only need a small fraction of reachable states — memoise, because tabulation would compute all of them. If it is **dense**, or the recursion would be deeper than ~1,000, tabulate.

**A practical order of work:** write the memoised version first, because it is the recurrence you already reasoned about and it is hard to get the order wrong. Convert to tabulation only if you need the depth or the space optimisation.

---

## 5. Fill order is not a detail

> **Predict before reading on.** Tabulating climbing stairs, suppose you fill the array from right to left instead of left to right — `for i in range(n, 1, -1)`. Every cell still uses the same transition. **Does it produce the right answer, a wrong answer, or an error?**

**A wrong answer, silently.** The lab:

```
   n=  5: correct order =    8   reversed order =    0   WRONG
   n=  8: correct order =   34   reversed order =    0   WRONG
   n= 12: correct order =  233   reversed order =    0   WRONG
```

Filling right-to-left computes `ways[n]` first, which reads `ways[n-1]` and `ways[n-2]` — both still zero, because they have not been computed. The zeros propagate and the answer is 0. **No exception, no warning.**

**The rule, and it generates the order for every DP you will ever write:** *the transition dictates the order — every cell a transition reads must already be final.* Read your recurrence, note which indices it reads, and choose the loop direction that guarantees those come first.

This is the one thing tabulation asks of you that memoisation handles automatically: **the call stack cannot get the order wrong**, because it computes a dependency at the moment it is needed.

---

## 6. Cutting the memory

Most DP tutorials stop at a working table. **The step after is noticing how little of it you still need.**

Climbing stairs reads only `ways[i-1]` and `ways[i-2]` — never anything further back. So the whole array is unnecessary; two variables suffice:

```python
def climb(n):
    if n == 0:
        return 1
    prev2, prev1 = 1, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1
```

$O(n)$ space becomes $O(1)$.

**The same move in two dimensions.** Unique grid paths has `table[i][j] = table[i-1][j] + table[i][j-1]` — it reads the row above and the cell to the left, never anything higher. So one row suffices:

```python
def grid(r, c):
    row = [1] * c
    for _ in range(1, r):
        for j in range(1, c):
            row[j] += row[j - 1]        # row[j] is still the row ABOVE; row[j-1] is the NEW row
    return row[c - 1]
```

The lab confirms all three give identical answers:

```
        grid | memoised | tabulated | rolling row | answer
      3x3    |        9 |         4 |           4 | 6
     18x18   |      579 |       289 |         289 | 2,333,606,220
```

$O(r \times c)$ space becomes $O(c)$.

**The general rule: if the transition reaches back at most $k$ rows, you need $k+1$ rows, not all of them.** And the price is real — **you lose the ability to reconstruct the solution**, because reconstruction walks the full table backwards. Optimise the space only when you need the value and not the path.

---

## 7. Worked example — complete runnable lab

Save as `dp_memo_tab.py`. Standard library only.

```python
"""The same recurrence four ways: naive, memoised, tabulated, space-optimised.

Run:  python3 dp_memo_tab.py
"""

import sys
import time

sys.setrecursionlimit(10000)


# ------------------------------------------------ the problem: climbing stairs
# You can climb 1 or 2 steps at a time. How many distinct ways to reach step n?
#   STATE      ways[i] = number of ways to reach step i
#   TRANSITION ways[i] = ways[i-1] + ways[i-2]
#   BASE       ways[0] = 1 (one way to stand still), ways[1] = 1

def naive(n, counter):
    counter[0] += 1
    if n <= 1:
        return 1
    return naive(n - 1, counter) + naive(n - 2, counter)


def memoised(n, counter, memo=None):
    if memo is None:
        memo = {}
    counter[0] += 1
    if n <= 1:
        return 1
    if n in memo:
        return memo[n]
    memo[n] = memoised(n - 1, counter, memo) + memoised(n - 2, counter, memo)
    return memo[n]


def tabulated(n, counter):
    ways = [0] * (n + 1)
    ways[0] = 1
    if n >= 1:
        ways[1] = 1
    for i in range(2, n + 1):
        counter[0] += 1
        ways[i] = ways[i - 1] + ways[i - 2]
    return ways[n]


def space_optimised(n, counter):
    prev2, prev1 = 1, 1
    if n == 0:
        return 1
    for _ in range(2, n + 1):
        counter[0] += 1
        prev2, prev1 = prev1, prev1 + prev2
    return prev1


# --------------------------------------------------- table trace, for teaching
def trace_table(n):
    ways = [0] * (n + 1)
    ways[0], ways[1] = 1, 1
    rows = [("base", list(ways))]
    for i in range(2, n + 1):
        ways[i] = ways[i - 1] + ways[i - 2]
        rows.append((f"i={i}", list(ways)))
    return rows


# ----------------------------------------- a case where fill ORDER goes wrong
def tabulate_wrong_order(n):
    """Fill right-to-left: reads cells that have not been computed yet."""
    ways = [0] * (n + 1)
    ways[0], ways[1] = 1, 1
    for i in range(n, 1, -1):          # WRONG direction
        ways[i] = ways[i - 1] + ways[i - 2]
    return ways[n]


# ----------------------------------------------------- 2-D: unique grid paths
def grid_memo(r, c, counter):
    memo = {}

    def go(i, j):
        counter[0] += 1
        if i == 0 or j == 0:
            return 1
        if (i, j) in memo:
            return memo[(i, j)]
        memo[(i, j)] = go(i - 1, j) + go(i, j - 1)
        return memo[(i, j)]

    return go(r - 1, c - 1)


def grid_tab(r, c, counter):
    table = [[1] * c for _ in range(r)]
    for i in range(1, r):
        for j in range(1, c):
            counter[0] += 1
            table[i][j] = table[i - 1][j] + table[i][j - 1]
    return table[r - 1][c - 1]


def grid_rolling(r, c, counter):
    row = [1] * c
    for _ in range(1, r):
        for j in range(1, c):
            counter[0] += 1
            row[j] += row[j - 1]
    return row[c - 1]


def main():
    print("=== 1. The three parts of any DP, named ===")
    print("   STATE       what one cell of the table MEANS")
    print("               ways[i] = number of ways to reach step i")
    print("   TRANSITION  how a cell is built from earlier cells")
    print("               ways[i] = ways[i-1] + ways[i-2]")
    print("   BASE CASE   the cells you fill in by hand")
    print("               ways[0] = 1, ways[1] = 1")
    print("   Get these three right and the code is mechanical. Get the STATE")
    print("   wrong and no amount of debugging will save the transition.")

    print("\n=== 2. Filling the table, one cell at a time (n = 8) ===")
    print("        step |  0  1  2  3  4  5  6  7  8")
    for label, row in trace_table(8):
        cells = "".join(f"{v:>3}" for v in row)
        print(f"   {label:>9} | {cells}")
    print("   -> each new cell reads only cells already filled. That requirement")
    print("      is what fixes the fill ORDER.")

    print("\n=== 3. Four implementations, same answer, different cost ===")
    print("        n |     naive |  memoised | tabulated | rolling | answer agrees")
    for n in (10, 20, 25, 30):
        cn, cm, ct, cs = [0], [0], [0], [0]
        a = naive(n, cn)
        b = memoised(n, cm)
        c = tabulated(n, ct)
        d = space_optimised(n, cs)
        print(f"   {n:>6} | {cn[0]:>9,} | {cm[0]:>9,} | {ct[0]:>9,} | {cs[0]:>7,} "
              f"| {a == b == c == d}")
    print("   (columns are operation counts, not answers)")
    print("   -> naive is exponential; the other three are all linear.")

    print("\n=== 4. What each one costs in MEMORY ===")
    n = 1000
    ct, cs = [0], [0]
    tabulated(n, ct)
    space_optimised(n, cs)
    print(f"   tabulated(n={n})      : array of {n+1} ints      -> O(n) space")
    print(f"   space_optimised(n={n}): 2 ints                -> O(1) space")
    print("   memoised             : dict + O(n) call stack -> O(n) space, and the")
    print("                          stack is the part that breaks first")
    try:
        memoised(50_000, [0])
        print("   memoised(50,000)     : succeeded")
    except RecursionError:
        print("   memoised(50,000)     : RecursionError -- the recursion depth, not the cache")
    big = tabulated(50_000, [0])
    digits = int(big.bit_length() * 0.30103) + 1
    print(f"   tabulated(50,000)    : fine -- it is a loop. Answer has ~{digits:,} digits")

    print("\n=== 5. Top-down or bottom-up? ===")
    print("   MEMOISATION (top-down)                TABULATION (bottom-up)")
    print("   - write the recurrence directly       - write a loop")
    print("   - only computes states it NEEDS       - computes every state")
    print("   - order handled by the call stack     - YOU choose the fill order")
    print("   - limited by recursion depth          - no depth limit")
    print("   - easy to add to existing recursion   - easy to optimise space")
    print("   -> sparse state space: memoise. Dense, or deep: tabulate.")

    print("\n=== 6. Fill order is not a detail ===")
    for n in (5, 8, 12):
        right = tabulated(n, [0])
        wrong = tabulate_wrong_order(n)
        print(f"   n={n:>3}: correct order = {right:>4}   reversed order = {wrong:>4}   "
              f"{'MATCH' if right == wrong else 'WRONG'}")
    print("   -> filling right-to-left reads ways[i-1] before it has been computed,")
    print("      so it silently uses a 0 and produces nonsense. The transition")
    print("      dictates the order: every cell it reads must already be final.")

    print("\n=== 7. The same three techniques in 2-D (unique grid paths) ===")
    print("        grid | memoised | tabulated | rolling row | answer")
    for r, c in ((3, 3), (8, 8), (15, 15), (18, 18)):
        cm, ct, cs = [0], [0], [0]
        a = grid_memo(r, c, cm)
        b = grid_tab(r, c, ct)
        d = grid_rolling(r, c, cs)
        assert a == b == d
        print(f"   {r:>4}x{c:<3} | {cm[0]:>8,} | {ct[0]:>9,} | {cs[0]:>11,} | {a:,}")
    print("   -> the rolling row keeps ONE row instead of the whole grid:")
    print("      O(c) space instead of O(r*c), because the transition only ever")
    print("      reads the row above and the cell to the left.")


if __name__ == "__main__":
    main()
```

### Expected output

Generated by running the file above:

```
=== 1. The three parts of any DP, named ===
   STATE       what one cell of the table MEANS
               ways[i] = number of ways to reach step i
   TRANSITION  how a cell is built from earlier cells
               ways[i] = ways[i-1] + ways[i-2]
   BASE CASE   the cells you fill in by hand
               ways[0] = 1, ways[1] = 1
   Get these three right and the code is mechanical. Get the STATE
   wrong and no amount of debugging will save the transition.

=== 2. Filling the table, one cell at a time (n = 8) ===
        step |  0  1  2  3  4  5  6  7  8
        base |   1  1  0  0  0  0  0  0  0
         i=2 |   1  1  2  0  0  0  0  0  0
         i=3 |   1  1  2  3  0  0  0  0  0
         i=4 |   1  1  2  3  5  0  0  0  0
         i=5 |   1  1  2  3  5  8  0  0  0
         i=6 |   1  1  2  3  5  8 13  0  0
         i=7 |   1  1  2  3  5  8 13 21  0
         i=8 |   1  1  2  3  5  8 13 21 34
   -> each new cell reads only cells already filled. That requirement
      is what fixes the fill ORDER.

=== 3. Four implementations, same answer, different cost ===
        n |     naive |  memoised | tabulated | rolling | answer agrees
       10 |       177 |        19 |         9 |       9 | True
       20 |    21,891 |        39 |        19 |      19 | True
       25 |   242,785 |        49 |        24 |      24 | True
       30 | 2,692,537 |        59 |        29 |      29 | True
   (columns are operation counts, not answers)
   -> naive is exponential; the other three are all linear.

=== 4. What each one costs in MEMORY ===
   tabulated(n=1000)      : array of 1001 ints      -> O(n) space
   space_optimised(n=1000): 2 ints                -> O(1) space
   memoised             : dict + O(n) call stack -> O(n) space, and the
                          stack is the part that breaks first
   memoised(50,000)     : RecursionError -- the recursion depth, not the cache
   tabulated(50,000)    : fine -- it is a loop. Answer has ~10,450 digits

=== 5. Top-down or bottom-up? ===
   MEMOISATION (top-down)                TABULATION (bottom-up)
   - write the recurrence directly       - write a loop
   - only computes states it NEEDS       - computes every state
   - order handled by the call stack     - YOU choose the fill order
   - limited by recursion depth          - no depth limit
   - easy to add to existing recursion   - easy to optimise space
   -> sparse state space: memoise. Dense, or deep: tabulate.

=== 6. Fill order is not a detail ===
   n=  5: correct order =    8   reversed order =    0   WRONG
   n=  8: correct order =   34   reversed order =    0   WRONG
   n= 12: correct order =  233   reversed order =    0   WRONG
   -> filling right-to-left reads ways[i-1] before it has been computed,
      so it silently uses a 0 and produces nonsense. The transition
      dictates the order: every cell it reads must already be final.

=== 7. The same three techniques in 2-D (unique grid paths) ===
        grid | memoised | tabulated | rolling row | answer
      3x3   |        9 |         4 |           4 | 6
      8x8   |       99 |        49 |          49 | 3,432
     15x15  |      393 |       196 |         196 | 40,116,600
     18x18  |      579 |       289 |         289 | 2,333,606,220
   -> the rolling row keeps ONE row instead of the whole grid:
      O(c) space instead of O(r*c), because the transition only ever
      reads the row above and the cell to the left.
```

---

## 8. Common pitfalls and traps

1. **A state you cannot write as a sentence.** If "`dp[i]` is..." has no natural ending, the state is wrong. Most failed DP attempts are this, presenting as a transition that "almost works".
2. **A mutable default argument as the cache.** `def f(n, memo={})` shares one dict across the whole process. Use `memo=None`.
3. **Getting the fill order wrong.** Silent zeros and a wrong answer, as section 5 shows. Derive the order from the transition; do not guess.
4. **Tabulating when the state space is sparse.** If only 200 of $10^6$ states are reachable, tabulation does 5,000× the necessary work. Memoise.
5. **Memoising when the recursion is deep.** `RecursionError` at around 1,000 frames. Convert to a loop rather than raising the limit.
6. **Optimising space before the DP is correct.** The rolling array is harder to debug and destroys reconstruction. Get the full table right first, then shrink it.
7. **Forgetting you need the solution, not just its value.** Space optimisation and reconstruction are mutually exclusive. Decide which you need before choosing.
8. **Not counting the state space first.** Complexity is *states × transition cost*. If that product is too big, no implementation detail rescues it — you need a different state.

---

## 9. Check your understanding

1. **Why is memoisation's operation count roughly $2n$ where tabulation's is $n$?**
   <details><summary>Answer</summary>Every state is entered twice in the memoised version: once as a cache miss that computes it, and once (or more) as a hit that returns it. Tabulation has no lookups — each cell is written exactly once by the loop. The lab shows 59 versus 29 at $n=30$. Both are $O(n)$; the constant differs.</details>

2. **When is memoisation strictly better than tabulation?**
   <details><summary>Answer</summary>When the reachable state space is much smaller than the full one. Tabulation fills every cell; memoisation computes only those actually requested. For a knapsack with capacity $10^9$ where only a few hundred distinct remaining-capacities ever arise, tabulation is impossible and memoisation is routine. The reverse case is depth: a recursion 50,000 states deep blows the stack, and a loop does not.</details>

3. **The fill order gave 0 instead of 34. Why no error?**
   <details><summary>Answer</summary>Because reading an uncomputed cell is not an error — the array was initialised to zeros, and zero is a perfectly valid integer. The transition computed $0 + 0 = 0$ and stored it. <b>Silent wrong answers are the standard failure mode of a bad fill order</b>, which is why the order is derived from the transition rather than chosen.</details>

4. **You have a working $O(n \times m)$ DP and need the actual subsequence, not just its length. Can you use the rolling-array optimisation?**
   <details><summary>Answer</summary>No. Reconstruction walks the completed table backwards from the answer cell, asking at each step which neighbour produced the value — and the rolling array has thrown those rows away. You need the full table, or Hirschberg's algorithm, which recovers the sequence in $O(\min(n,m))$ space by re-solving halves with divide and conquer at the cost of doubling the time.</details>

5. **How do you predict a DP's complexity before writing it?**
   <details><summary>Answer</summary>Count the states and multiply by the cost of one transition. Climbing stairs: $n$ states, $O(1)$ transition → $O(n)$. Coin change: $n$ amounts × $O(c)$ to try every coin → $O(nc)$. LCS: $n \times m$ states, $O(1)$ each → $O(nm)$. <b>This is also the design tool</b>: if states × transition is too large, change the state — no implementation trick will fix it.</details>

---

## 10. Practice — independent task

Build one problem four ways and measure every claim in this lesson.

**The problem: minimum path sum.** Given a grid of non-negative costs, find the cheapest path from top-left to bottom-right, moving only right or down.

**Part 1 — the three declarations.** Write the state as a full sentence, the transition, and the base cases, **before any code**. Predict the complexity from states × transition.

**Part 2 — four implementations.** Naive recursion, memoised, tabulated, and rolling-row. Instrument each with an operation counter. Confirm all four agree on 300 random grids, and that the counts match your prediction.

**Part 3 — break the fill order.** Tabulate right-to-left and bottom-to-top. Report what each produces and explain it in terms of which cells were read before being written.

**Part 4 — the depth wall.** Find the grid size at which the memoised version raises `RecursionError`. Report it, and confirm the tabulated version handles a grid ten times larger.

**Part 5 — reconstruction versus space.** Extend the tabulated version to return the actual path. Then attempt it with the rolling row. **Explain precisely what information is missing** and what your options are.

**Part 6 — sparse states.** Modify the problem so movement is right, down, or a "jump" of exactly 7 cells right. On a 1000×1000 grid, measure how many states memoisation actually visits versus the $10^6$ tabulation would fill.

**Edge cases:** a 1×1 grid; a single row; a single column; a grid containing zeros; a non-rectangular input, which you should reject.

**Done when:** all four implementations agree on 300 grids; your predicted complexity matches the measured counts; part 3 explains both wrong answers mechanically; part 4 reports both numbers; part 5 states exactly what is lost; and part 6 gives the two state counts with a ratio.

Then apply it: [[111-unique-paths|Unique Paths]], [[099-climbing-stairs|Climbing Stairs]] and [[100-min-cost-climbing-stairs|Min Cost Climbing Stairs]] are the same table with different transitions.

---

## Before moving on

You can name a state, transition and base case and write either implementation from them; choose between top-down and bottom-up on evidence; derive the fill order from the transition; and cut a dimension of memory when the transition allows it.

**Recap:** every DP is three declarations — **state** (what one cell means, as a sentence), **transition** (how a cell is built from smaller ones), **base case** (what you fill by hand) — plus a loop. **Memoisation** is the recurrence with a cache: natural to write, computes only needed states, limited by recursion depth. **Tabulation** is a loop: no depth limit, easy to space-optimise, but it computes every state and *you* own the fill order. **The transition dictates the order** — every cell it reads must already be final, and getting this wrong yields silent zeros rather than an error. **Complexity is states × transition cost**, and that product is how you evaluate a state before writing code. Finally, if the transition reaches back at most $k$ rows, keep $k+1$ rows and not the whole table — at the cost of losing reconstruction.

**Next:** [[03-classic-one-dimensional|Classic One-Dimensional DP]] — house robber, coin change and longest increasing subsequence, each with its state named and its answer checked against brute force.

---

## Related

- [[01-what-makes-a-problem-dp|What Makes a Problem DP]] — the previous lesson
- [[03-classic-one-dimensional|Classic 1-D DP]] · [[04-classic-two-dimensional|Classic 2-D DP]] — the worked problems
- [[01-recursion-fundamentals|Recursion Fundamentals]] — where memoisation is introduced
- [[15-dynamic-programming|The DP pattern note]] — the problem-recognition layer above this folder
- [[06-dynamic-programming/index|the dynamic programming folder]]
