---
id: f82ba550-ddf7-49f7-9f2e-94333e899107
---

# Module: Classic Two-Dimensional DP (The State Is a Pair of Indices)

Once you see that, you have a template rather than three memorised solutions. And the knapsack lesson contains the single most-failed detail in all of DP: the direction of the inner loop.

---

## Before you start
<!-- bite: 8cfd4b0b-f4e8-43ff-a128-f594131c940c -->

- You can name a state, transition and base case, and derive the fill order from the transition — [[02-memoisation-and-tabulation|memoisation and tabulation]].
- You have worked at least one 1-D DP with reconstruction — [[03-classic-one-dimensional|classic 1-D DP]].
- You know why space optimisation and reconstruction are mutually exclusive — lesson 02.

**After this lesson you will be able to:**

1. Set up a 2-D table with correct base rows and columns, and say what each cell means.
2. **Reconstruct** the subsequence, the chosen items, or the edit script by walking the table backwards.
3. Explain why the 0/1 knapsack's rolling array must iterate **downwards**, and demonstrate the upward version solving a different problem.
4. Reduce a 2-D table to one row, and say precisely what you give up.

**Study route:** read 1 and 2, answer the prediction in section 3 before continuing — it is the knapsack loop-direction question, and it is the one that costs people interviews.

---

## 1. Longest common subsequence — the template
<!-- bite: 27c609b9-b08d-41a8-9315-f1ae2dc7a4bd -->

> Given two sequences, find the longest sequence appearing in both, in order but not necessarily contiguously.

**The decision: look at the last character of each. Do they match?**

- **STATE:** `L[i][j]` = the length of the LCS of `a[:i]` and `b[:j]` — the first $i$ characters of `a` against the first $j$ of `b`.
- **TRANSITION:**
  - if `a[i-1] == b[j-1]`: `L[i][j] = L[i-1][j-1] + 1` — the match extends the LCS of both shorter prefixes.
  - else: `L[i][j] = max(L[i-1][j], L[i][j-1])` — one of the two characters cannot be in the LCS, and you take the better of dropping each.
- **BASE:** `L[0][j] = L[i][0] = 0` — an empty sequence shares nothing with anything.

For `a = "ABCBDAB"`, `b = "BDCABA"`:

```text
   L[i][j]  (rows = a, cols = b)
              B   D   C   A   B   A
      --------------------------------
      - |   0   0   0   0   0   0   0
      A |   0   0   0   0   1   1   1
      B |   0   1   1   1   1   2   2
      C |   0   1   1   2   2   2   2
      B |   0   1   1   2   2   3   3
      D |   0   1   2   2   2   3   3
      A |   0   1   2   2   3   3   4
      B |   0   1   2   2   3   4   4
```

**The answer is the bottom-right cell: 4.** The lab confirms it against brute force over all subsequences.

**The `+1` on the diagonal is the only place the table grows.** Everywhere else it copies the better neighbour. That is why the diagonal steps, traced backwards, spell out the subsequence.

### Reconstruction

Start at the bottom-right and walk backwards, asking at each cell which rule produced it:

```python
out, i, j = [], n, m
while i > 0 and j > 0:
    if a[i-1] == b[j-1]:
        out.append(a[i-1]); i -= 1; j -= 1     # diagonal: this char is in the LCS
    elif L[i-1][j] >= L[i][j-1]:
        i -= 1                                  # came from above
    else:
        j -= 1                                  # came from the left
```

Giving `'BCBA'`. **There can be several LCSs of the same length** — `'BDAB'` and `'BCAB'` are also valid here — and the tie-break in that `>=` decides which one you get. If a problem demands a specific one (lexicographically smallest, say), that comparison is where you control it.

---

## 2. 0/1 knapsack — the decision is take or skip
<!-- bite: 75a0fc63-530d-40f9-b583-04b203bc1457 -->

> Items with weights and values, a capacity. Each item may be taken **at most once**. Maximise value.

- **STATE:** `K[i][w]` = the best value using only the first $i$ items, within capacity $w$.
- **TRANSITION:** `K[i][w] = max(K[i-1][w], K[i-1][w - wt[i]] + val[i])` — skip item $i$, or take it and give up its weight from the capacity available to the earlier items.
- **BASE:** `K[0][w] = 0` — no items, no value, at any capacity.

Weights `[1,3,4,5]`, values `[1,4,5,7]`, capacity 7:

```text
        w |   0   1   2   3   4   5   6   7
      ------------------------------------
     none |   0   0   0   0   0   0   0   0
     +it0 |   0   1   1   1   1   1   1   1
     +it1 |   0   1   1   4   5   5   5   5
     +it2 |   0   1   1   4   5   6   6   9
     +it3 |   0   1   1   4   5   7   8   9
```

Best value 9, from items 1 and 2 — weights $3+4 = 7$, values $4+5 = 9$. Checked against brute force over all $2^n$ subsets, and on **300 random instances**.

**The `K[i-1][...]` on both branches is the "0/1" part.** Both options consult the row *above* — the state with item $i$ not yet considered — which is exactly what stops the item being used twice.

### Reconstruction

`K[i][w] != K[i-1][w]` means the value changed when item $i$ became available, so item $i$ was taken. Subtract its weight and continue up. **This is the same backwards walk as LCS**, asking a different question at each cell.

---

## 3. The loop direction — the detail that decides correctness
<!-- bite: 528216e5-76f3-419f-83bb-40855531c213 -->

> **Predict before reading on.** The knapsack table only ever reads the row above, so it can be collapsed to one row. Here are two versions of the inner loop:
>
> ```python
> for w in range(cap, wt - 1, -1):   # downwards
>     row[w] = max(row[w], row[w - wt] + val)
>
> for w in range(wt, cap + 1):       # upwards
>     row[w] = max(row[w], row[w - wt] + val)
> ```
>
> **One is correct 0/1 knapsack. Which, and what does the other compute?**

**Downwards is correct. Upwards allows each item to be used unlimited times.**

The reason is precise. With a single row, `row[w - wt]` means "the best value at capacity $w - wt$" — but *from which row?* Going **downwards**, larger indices are written first, so when you read `row[w - wt]` (a smaller index) it has not yet been touched this iteration and still holds the **previous** row's value — the state *before* item $i$ was available. Correct.

Going **upwards**, `row[w - wt]` was already updated *this* iteration, so it may already include item $i$. Adding `val` again uses the item twice.

The lab measures it on four instances:

```text
     weights      values       cap | 2-D | roll down | roll UP | brute (0/1)
     [1, 3, 4, 5] [1, 4, 5, 7]   7 |   9 |         9 |       9 |           9
     [2, 3]       [3, 4]         6 |   7 |         7 |       9 |           7   <- WRONG
     [3]          [5]            9 |   5 |         5 |      15 |           5   <- WRONG
     [2, 5]       [4, 9]        10 |  13 |        13 |      20 |          13   <- WRONG
```

**The first row hides the bug by coincidence** — that instance happens to have the same answer either way, which is exactly how this survives casual testing. Rows 2–4 expose it: `[3]` with value 5 and capacity 9 gives 5 for 0/1 and **15** for the upward loop, which has used the single item three times.

**And the upward loop is not simply broken — it is the correct solution to the *unbounded* knapsack**, where items may be reused. Two problems, one line of difference, and the line is a loop direction. This is why "which way does the loop go?" is a real interview question rather than a trivia one.

---

## 4. Edit distance — three operations, one minimum
<!-- bite: 3a7b89f2-4bcf-4f4d-9298-8bf516cdcb66 -->

> Fewest single-character insertions, deletions and replacements to turn one string into another. (Levenshtein distance — what spell-checkers and `diff` are built on.)

- **STATE:** `D[i][j]` = the edits needed to turn `a[:i]` into `b[:j]`.
- **TRANSITION:**
  - if `a[i-1] == b[j-1]`: `D[i][j] = D[i-1][j-1]` — the characters already agree, free.
  - else: `D[i][j] = 1 + min(D[i-1][j], D[i][j-1], D[i-1][j-1])` — delete from `a`, insert from `b`, or replace.
- **BASE:** `D[i][0] = i` (delete everything), `D[0][j] = j` (insert everything).

**The base cases here carry real content**, unlike LCS's row of zeros. Turning `"kit"` into `""` costs 3 deletions, so the first column counts upward.

```text
   D[i][j]  (rows = kitten, cols = sitting)
              s   i   t   t   i   n   g
      ------------------------------------
      - |   0   1   2   3   4   5   6   7
      k |   1   1   2   3   4   5   6   7
      i |   2   2   1   2   3   4   5   6
      t |   3   3   2   1   2   3   4   5
      t |   4   4   3   2   1   2   3   4
      e |   5   5   4   3   2   2   3   4
      n |   6   6   5   4   3   3   2   3
```

Distance 3, and walking backwards recovers the script:

```text
     - replace 'k' with 's'
     - replace 'e' with 'i'
     - insert 'g'
```

Verified against an independent memoised brute force on 300 random short strings.

**Which of the three neighbours a cell came from is which operation** — above is a deletion, left is an insertion, diagonal is a replacement (or a free match). That correspondence is what turns a number into a usable edit script, which is what `diff` prints.

---

## 5. The shared shape
<!-- bite: 3800477b-fff5-4811-ad7d-2b2bb0989fa6 -->

| Problem | State | Cost | Space after optimisation |
| :--- | :--- | :--- | :--- |
| LCS | LCS of `a[:i]` and `b[:j]` | $O(nm)$ | $O(\min(n,m))$ |
| 0/1 knapsack | best value, first $i$ items, capacity $w$ | $O(n \cdot \text{cap})$ | $O(\text{cap})$ |
| Edit distance | edits from `a[:i]` to `b[:j]` | $O(nm)$ | $O(\min(n,m))$ |

**All three fill an $(n{+}1) \times (m{+}1)$ grid whose row 0 and column 0 are base cases, and every cell reads only cells above and to the left.**

**That read pattern is exactly why one row suffices**: by the time you overwrite a cell, the only value from it you still need is the one diagonally above, which fits in a single variable. And it is exactly why reconstruction needs the full table — the backwards walk visits cells the rolling version has discarded.

**When you meet an unfamiliar 2-D DP, the questions are always the same:** what do the two indices range over; what decision happens at `(i, j)`; which neighbours does that decision consult; and what do row 0 and column 0 mean?

---

## 6. Worked example — complete runnable lab
<!-- bite: 981e8b2f-aab5-4891-bcb5-e4f4ade58386 -->

Save as `dp_2d.py`. Standard library only. Every result is checked against brute force.

```python
"""Two-dimensional DP: the state is a pair of indices.

LCS, 0/1 knapsack and edit distance -- table traces, answer reconstruction,
space optimisation, and brute-force verification.

Run:  python3 dp_2d.py
"""

import itertools
import random


# ==================================== LONGEST COMMON SUBSEQUENCE
#   STATE      L[i][j] = length of the LCS of a[:i] and b[:j]
#   TRANSITION if a[i-1] == b[j-1]: L[i][j] = L[i-1][j-1] + 1
#              else:                L[i][j] = max(L[i-1][j], L[i][j-1])
#   BASE       L[0][j] = L[i][0] = 0   (an empty string shares nothing)
def lcs(a, b):
    n, m = len(a), len(b)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
    # walk backwards through the table to recover the subsequence itself
    out, i, j = [], n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1]); i -= 1; j -= 1
        elif L[i - 1][j] >= L[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return L[n][m], "".join(reversed(out)), L


def lcs_brute(a, b):
    best = 0
    for r in range(len(a), -1, -1):
        for combo in itertools.combinations(range(len(a)), r):
            sub = "".join(a[i] for i in combo)
            if is_subsequence(sub, b):
                return len(sub)
    return best


def is_subsequence(s, t):
    it = iter(t)
    return all(ch in it for ch in s)


# ==================================================== 0/1 KNAPSACK
#   STATE      K[i][w] = best value using the first i items within capacity w
#   TRANSITION K[i][w] = max(K[i-1][w],                       skip item i
#                            K[i-1][w-wt[i]] + val[i])        take item i
#   BASE       K[0][w] = 0
def knapsack(weights, values, cap):
    n = len(weights)
    K = [[0] * (cap + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(cap + 1):
            K[i][w] = K[i - 1][w]
            if weights[i - 1] <= w:
                K[i][w] = max(K[i][w], K[i - 1][w - weights[i - 1]] + values[i - 1])
    taken, w = [], cap
    for i in range(n, 0, -1):
        if K[i][w] != K[i - 1][w]:        # value changed => item i was taken
            taken.append(i - 1)
            w -= weights[i - 1]
    return K[n][cap], sorted(taken), K


def knapsack_rolling(weights, values, cap):
    """One row instead of n+1. The inner loop MUST go downwards."""
    row = [0] * (cap + 1)
    for wt, val in zip(weights, values):
        for w in range(cap, wt - 1, -1):          # downwards
            row[w] = max(row[w], row[w - wt] + val)
    return row[cap]


def knapsack_rolling_wrong(weights, values, cap):
    """The same, but the inner loop goes upwards -- which reuses an item."""
    row = [0] * (cap + 1)
    for wt, val in zip(weights, values):
        for w in range(wt, cap + 1):              # upwards: WRONG for 0/1
            row[w] = max(row[w], row[w - wt] + val)
    return row[cap]


def knapsack_brute(weights, values, cap):
    n = len(weights)
    best = 0
    for mask in range(1 << n):
        w = sum(weights[i] for i in range(n) if mask >> i & 1)
        if w <= cap:
            best = max(best, sum(values[i] for i in range(n) if mask >> i & 1))
    return best


# ================================================== EDIT DISTANCE
#   STATE      D[i][j] = edits to turn a[:i] into b[:j]
#   TRANSITION if a[i-1] == b[j-1]: D[i][j] = D[i-1][j-1]
#              else: D[i][j] = 1 + min(D[i-1][j],    delete
#                                      D[i][j-1],    insert
#                                      D[i-1][j-1])  replace
#   BASE       D[i][0] = i (delete everything), D[0][j] = j (insert everything)
def edit_distance(a, b):
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        D[i][0] = i
    for j in range(m + 1):
        D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                D[i][j] = D[i - 1][j - 1]
            else:
                D[i][j] = 1 + min(D[i - 1][j], D[i][j - 1], D[i - 1][j - 1])
    ops, i, j = [], n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] and D[i][j] == D[i - 1][j - 1]:
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and D[i][j] == D[i - 1][j - 1] + 1:
            ops.append(f"replace {a[i-1]!r} with {b[j-1]!r}"); i, j = i - 1, j - 1
        elif i > 0 and D[i][j] == D[i - 1][j] + 1:
            ops.append(f"delete {a[i-1]!r}"); i -= 1
        else:
            ops.append(f"insert {b[j-1]!r}"); j -= 1
    return D[n][m], list(reversed(ops)), D


def show_table(T, a, b, title, rowlabel="", collabel=""):
    print(f"\n   {title}")
    header = "        " + "".join(f"{ch:>4}" for ch in ("-" + b))
    print(f"        {'':>3}" + "".join(f"{ch:>4}" for ch in b))
    print("      " + "-" * (4 * (len(b) + 2)))
    for i, row in enumerate(T):
        label = "-" if i == 0 else a[i - 1]
        print(f"    {label:>3} |" + "".join(f"{v:>4}" for v in row))


def main():
    print("=" * 78)
    print("1. LONGEST COMMON SUBSEQUENCE")
    print("=" * 78)
    a, b = "ABCBDAB", "BDCABA"
    print(f"\n   a = {a!r}   b = {b!r}")
    print("   STATE      L[i][j] = length of the LCS of a[:i] and b[:j]")
    print("   TRANSITION match -> L[i-1][j-1] + 1;  else max(L[i-1][j], L[i][j-1])")
    print("   BASE       L[0][j] = L[i][0] = 0")
    n, sub, L = lcs(a, b)
    show_table(L, a, b, "L[i][j]  (rows = a, cols = b)")
    print(f"\n   LCS length: {n}   one LCS: {sub!r}")
    print(f"   brute force over all subsequences of a: {lcs_brute(a, b)}")
    print("   -> the answer is the bottom-right cell; the SUBSEQUENCE is recovered")
    print("      by walking backwards, taking a diagonal step on every match.")

    print("\n" + "=" * 78)
    print("2. 0/1 KNAPSACK")
    print("=" * 78)
    weights = [1, 3, 4, 5]
    values = [1, 4, 5, 7]
    cap = 7
    print(f"\n   weights {weights}   values {values}   capacity {cap}")
    print("   STATE      K[i][w] = best value from the first i items within capacity w")
    print("   TRANSITION K[i][w] = max(skip: K[i-1][w],  take: K[i-1][w-wt] + val)")
    print("   BASE       K[0][w] = 0")
    best, taken, K = knapsack(weights, values, cap)
    print("\n        w |" + "".join(f"{w:>4}" for w in range(cap + 1)))
    print("      " + "-" * (4 * (cap + 2)))
    for i, row in enumerate(K):
        label = "none" if i == 0 else f"+it{i-1}"
        print(f"   {label:>6} |" + "".join(f"{v:>4}" for v in row))
    print(f"\n   best value: {best}   items taken (0-indexed): {taken}")
    print(f"   -> weights {[weights[i] for i in taken]} = {sum(weights[i] for i in taken)} <= {cap}, "
          f"values {[values[i] for i in taken]} = {best}")
    print(f"   brute force over all 2^{len(weights)} subsets: {knapsack_brute(weights, values, cap)}")

    print("\n   The rolling-array version, and why its loop runs BACKWARDS:")
    print("     weights      values       cap | 2-D | roll down | roll UP | brute (0/1)")
    demos = [
        ([1, 3, 4, 5], [1, 4, 5, 7], 7),
        ([2, 3],       [3, 4],       6),
        ([3],          [5],          9),
        ([2, 5],       [4, 9],      10),
    ]
    for ws, vs, c in demos:
        two_d = knapsack(ws, vs, c)[0]
        down = knapsack_rolling(ws, vs, c)
        up = knapsack_rolling_wrong(ws, vs, c)
        truth = knapsack_brute(ws, vs, c)
        flag = "" if up == truth else "   <- WRONG"
        print(f"     {str(ws):<13}{str(vs):<13}{c:>3} | {two_d:>3} | {down:>9} "
              f"| {up:>7} | {truth:>11}{flag}")
    print("   -> going upwards, row[w - wt] may ALREADY include the current item,")
    print("      so the item gets used again. Row 1 hides it by coincidence; rows")
    print("      2-4 do not. That upward loop is not a bug in general -- it is")
    print("      exactly the UNBOUNDED knapsack, which is a different problem.")

    print("\n   Checking DP against brute force on 300 random instances...")
    bad = 0
    for t in range(300):
        random.seed(t + 5000)
        k = random.randint(0, 10)
        ws = [random.randint(1, 12) for _ in range(k)]
        vs = [random.randint(1, 20) for _ in range(k)]
        c = random.randint(0, 25)
        truth = knapsack_brute(ws, vs, c)
        if knapsack(ws, vs, c)[0] != truth or knapsack_rolling(ws, vs, c) != truth:
            bad += 1
    print(f"   agreed on {300 - bad}/300  (both the 2-D table and the rolling array)")

    print("\n" + "=" * 78)
    print("3. EDIT DISTANCE (Levenshtein)")
    print("=" * 78)
    a2, b2 = "kitten", "sitting"
    print(f"\n   {a2!r} -> {b2!r}")
    print("   STATE      D[i][j] = edits to turn a[:i] into b[:j]")
    print("   TRANSITION match -> D[i-1][j-1];  else 1 + min(delete, insert, replace)")
    print("   BASE       D[i][0] = i,  D[0][j] = j")
    d, ops, D = edit_distance(a2, b2)
    show_table(D, a2, b2, "D[i][j]  (rows = kitten, cols = sitting)")
    print(f"\n   edit distance: {d}")
    for op in ops:
        print(f"     - {op}")

    print("\n   Checking against a brute-force search on short strings...")
    def brute_edit(x, y):
        from functools import lru_cache
        @lru_cache(maxsize=None)
        def go(i, j):
            if i == len(x):
                return len(y) - j
            if j == len(y):
                return len(x) - i
            if x[i] == y[j]:
                return go(i + 1, j + 1)
            return 1 + min(go(i + 1, j), go(i, j + 1), go(i + 1, j + 1))
        return go(0, 0)
    bad = 0
    alphabet = "abc"
    for t in range(300):
        random.seed(t + 9000)
        x = "".join(random.choice(alphabet) for _ in range(random.randint(0, 6)))
        y = "".join(random.choice(alphabet) for _ in range(random.randint(0, 6)))
        if edit_distance(x, y)[0] != brute_edit(x, y):
            bad += 1
    print(f"   agreed on {300 - bad}/300")

    print("\n" + "=" * 78)
    print("4. THE SHARED SHAPE")
    print("=" * 78)
    print("""
   problem        | state                        | cost        | space after
                  |                              |             | optimisation
   ---------------|------------------------------|-------------|-------------
   LCS            | LCS of a[:i] and b[:j]       | O(n*m)      | O(min(n,m))
   0/1 knapsack   | best value, first i items,   | O(n*cap)    | O(cap)
                  | capacity w                   |             |
   edit distance  | edits from a[:i] to b[:j]    | O(n*m)      | O(min(n,m))

   -> all three fill an (n+1) x (m+1) grid where row 0 and column 0 are the
      base cases, and every cell reads only cells ABOVE and to the LEFT.
   -> that read pattern is exactly why one row suffices: by the time you
      overwrite a cell, the only value you still need from it is the one
      diagonally above, which you can carry in a single variable.
   -> reconstruction always works the same way: start at the bottom-right
      and walk backwards, asking at each cell WHICH neighbour produced it.""")


if __name__ == "__main__":
    main()
```

### Expected output

Generated by running the file above:

```text
==============================================================================
1. LONGEST COMMON SUBSEQUENCE
==============================================================================

   a = 'ABCBDAB'   b = 'BDCABA'
   STATE      L[i][j] = length of the LCS of a[:i] and b[:j]
   TRANSITION match -> L[i-1][j-1] + 1;  else max(L[i-1][j], L[i][j-1])
   BASE       L[0][j] = L[i][0] = 0

   L[i][j]  (rows = a, cols = b)
              B   D   C   A   B   A
      --------------------------------
      - |   0   0   0   0   0   0   0
      A |   0   0   0   0   1   1   1
      B |   0   1   1   1   1   2   2
      C |   0   1   1   2   2   2   2
      B |   0   1   1   2   2   3   3
      D |   0   1   2   2   2   3   3
      A |   0   1   2   2   3   3   4
      B |   0   1   2   2   3   4   4

   LCS length: 4   one LCS: 'BCBA'
   brute force over all subsequences of a: 4
   -> the answer is the bottom-right cell; the SUBSEQUENCE is recovered
      by walking backwards, taking a diagonal step on every match.

==============================================================================
2. 0/1 KNAPSACK
==============================================================================

   weights [1, 3, 4, 5]   values [1, 4, 5, 7]   capacity 7
   STATE      K[i][w] = best value from the first i items within capacity w
   TRANSITION K[i][w] = max(skip: K[i-1][w],  take: K[i-1][w-wt] + val)
   BASE       K[0][w] = 0

        w |   0   1   2   3   4   5   6   7
      ------------------------------------
     none |   0   0   0   0   0   0   0   0
     +it0 |   0   1   1   1   1   1   1   1
     +it1 |   0   1   1   4   5   5   5   5
     +it2 |   0   1   1   4   5   6   6   9
     +it3 |   0   1   1   4   5   7   8   9

   best value: 9   items taken (0-indexed): [1, 2]
   -> weights [3, 4] = 7 <= 7, values [4, 5] = 9
   brute force over all 2^4 subsets: 9

   The rolling-array version, and why its loop runs BACKWARDS:
     weights      values       cap | 2-D | roll down | roll UP | brute (0/1)
     [1, 3, 4, 5] [1, 4, 5, 7]   7 |   9 |         9 |       9 |           9
     [2, 3]       [3, 4]         6 |   7 |         7 |       9 |           7   <- WRONG
     [3]          [5]            9 |   5 |         5 |      15 |           5   <- WRONG
     [2, 5]       [4, 9]        10 |  13 |        13 |      20 |          13   <- WRONG
   -> going upwards, row[w - wt] may ALREADY include the current item,
      so the item gets used again. Row 1 hides it by coincidence; rows
      2-4 do not. That upward loop is not a bug in general -- it is
      exactly the UNBOUNDED knapsack, which is a different problem.

   Checking DP against brute force on 300 random instances...
   agreed on 300/300  (both the 2-D table and the rolling array)

==============================================================================
3. EDIT DISTANCE (Levenshtein)
==============================================================================

   'kitten' -> 'sitting'
   STATE      D[i][j] = edits to turn a[:i] into b[:j]
   TRANSITION match -> D[i-1][j-1];  else 1 + min(delete, insert, replace)
   BASE       D[i][0] = i,  D[0][j] = j

   D[i][j]  (rows = kitten, cols = sitting)
              s   i   t   t   i   n   g
      ------------------------------------
      - |   0   1   2   3   4   5   6   7
      k |   1   1   2   3   4   5   6   7
      i |   2   2   1   2   3   4   5   6
      t |   3   3   2   1   2   3   4   5
      t |   4   4   3   2   1   2   3   4
      e |   5   5   4   3   2   2   3   4
      n |   6   6   5   4   3   3   2   3

   edit distance: 3
     - replace 'k' with 's'
     - replace 'e' with 'i'
     - insert 'g'

   Checking against a brute-force search on short strings...
   agreed on 300/300

==============================================================================
4. THE SHARED SHAPE
==============================================================================

   problem        | state                        | cost        | space after
                  |                              |             | optimisation
   ---------------|------------------------------|-------------|-------------
   LCS            | LCS of a[:i] and b[:j]       | O(n*m)      | O(min(n,m))
   0/1 knapsack   | best value, first i items,   | O(n*cap)    | O(cap)
                  | capacity w                   |             |
   edit distance  | edits from a[:i] to b[:j]    | O(n*m)      | O(min(n,m))

   -> all three fill an (n+1) x (m+1) grid where row 0 and column 0 are the
      base cases, and every cell reads only cells ABOVE and to the LEFT.
   -> that read pattern is exactly why one row suffices: by the time you
      overwrite a cell, the only value you still need from it is the one
      diagonally above, which you can carry in a single variable.
   -> reconstruction always works the same way: start at the bottom-right
      and walk backwards, asking at each cell WHICH neighbour produced it.
```

---

## 7. Common pitfalls and traps
<!-- bite: 742f2159-3e94-49e0-82e3-e36a7a38c235 -->

1. **The knapsack rolling loop going upwards.** Silently solves the unbounded problem. The lab shows `[3]`/value 5/capacity 9 returning **15** instead of 5.
2. **Off-by-one between the table and the strings.** The table is $(n{+}1) \times (m{+}1)$, so `L[i][j]` concerns `a[i-1]` and `b[j-1]`. Mixing the two conventions mid-function is the most common source of a table that is almost right.
3. **Base cases of zero when they should count.** LCS's row 0 is all zeros; edit distance's is `0,1,2,3,...`. Copying one problem's base row into the other's solution produces a plausible wrong table.
4. **Space-optimising when you need the answer's content.** Reconstruction walks cells the rolling array threw away. Decide first.
5. **Assuming the LCS is unique.** Several may share the maximum length; your tie-break picks one. If the problem wants a particular one, that comparison is the lever.
6. **Confusing LCS with longest common substring.** Substring must be contiguous, and it is a different recurrence — on a mismatch the value resets to 0 rather than taking a max, and the answer is the largest cell anywhere rather than the bottom-right.
7. **Treating knapsack as polynomial.** $O(n \cdot \text{cap})$ is pseudo-polynomial, linear in the capacity's *value*. A capacity of $10^9$ is infeasible. 0/1 knapsack is NP-hard.
8. **Testing on an instance that hides the bug.** The lab's first knapsack row gives 9 for both loop directions. **One passing example is not a test** — this is why the lab runs 300 random instances against brute force.

---

## Check your understanding
<!-- bite: a1860897-2f0f-4c94-a5fd-c3888668bbf4 -->

Try each one before you open the answer.

1. <!-- q: mcq id="0a82addb" -->
   0/1 knapsack's transition is `K[i][w] = max(K[i-1][w], K[i-1][w-wt] + val)`. Why does the take branch read row i−1, not row i?

   - [ ] It is faster
   - [x] Taking item i must build on the best using only earlier items, so item i cannot be used twice
   - [ ] Row i is not allocated yet
   - [ ] It makes the answer smaller

   <details><summary>Answer</summary>

   Reading K[i][w − wt] would allow item i to be already in that sub-answer, which is the unbounded knapsack, not 0/1.

   </details>

2. <!-- q: mcq id="b9663c18" -->
   The one-row (rolling) 0/1 knapsack loops capacity downwards. Why?

   - [x] So that row[w − wt] still holds the previous item's value when row[w] is computed
   - [ ] So it stops early
   - [ ] Because capacities are sorted descending
   - [ ] It does not matter; upwards works too

   <details><summary>Answer</summary>

   Going down, smaller indices are written after larger ones, so row[w − wt] is still "without this item". Going up, you might read a cell this item already updated and take it twice.

   </details>

3. <!-- q: gap id="0445b531" answers="0;i" -->
   Fill in the gaps. In the LCS table the first column is all ___, because an empty string shares nothing. In the edit distance table the cell for "first i characters vs empty string" is ___, because it takes that many deletions.

   <details><summary>Answer</summary>

   0 and i. LCS counts what is shared; edit distance counts work. The base row says what an empty input means for the question being asked.

   </details>

4. <!-- q: mcq id="3f66e0ad" -->
   What single change turns the LCS recurrence into longest common substring (contiguous)?

   - [ ] Add 2 on a match instead of 1
   - [x] On a mismatch set the cell to 0, and take the maximum over the whole table
   - [ ] Loop the columns backwards
   - [ ] Use min instead of max

   <details><summary>Answer</summary>

   Setting a mismatch to 0 breaks the run, which is what "contiguous" requires. The answer is then the largest cell anywhere, not the bottom-right one.

   </details>

5. <!-- q: open id="047d6ed9" -->
   You need the LCS length of two 100,000-character strings. Is the standard O(nm) table usable?

   <details><summary>Answer</summary>

   Not as it stands. 10¹⁰ cells is too slow, and a full table would need tens of gigabytes. A rolling row fixes the memory (O(min(n, m))), but not the time. If the strings are similar, use a band-limited DP or Myers' diff algorithm instead.

   </details>

## Check your understanding: worked problems
<!-- bite: d3f2775a-1336-40c8-81b0-63c4231afa6d -->

Work each one out on paper first, then type your answer.

1. <!-- q: exact id="33a2bf19" answer="4" -->
   What is the length of the longest common subsequence of BANANA and ATANA? (A subsequence keeps order but may skip characters.)

   <details><summary>Answer</summary>

   4, for example AANA: A, A, N, A appear in this order in both strings. The table L[i][j] = L[i−1][j−1] + 1 on a match, else max of the cell above and the cell to the left, ends at 4.

   </details>

2. <!-- q: gap id="608bb54c" answers="7;3;4;7" -->
   Fill in the gaps. 0/1 knapsack, capacity 5:

   | item | weight | value |
   |---|---|---|
   | 1 | 2 | 3 |
   | 2 | 3 | 4 |
   | 3 | 4 | 5 |
   | 4 | 5 | 6 |

   The best value is ___. After items 1 and 2 only, the row for capacities 2, 3, 5 is K[2][2] = ___, K[2][3] = ___, K[2][5] = ___.

   <details><summary>Answer</summary>

   Best is 7, taking items 1 and 2 (weight 5). Row 2 is [0, 0, 3, 4, 4, 7]: capacity 2 fits item 1 (3), capacity 3 fits item 2 (4), and capacity 5 fits both (7).

   </details>

3. <!-- q: gap id="d2d63e19" answers="3;9" -->
   Fill in the gaps. One item, weight 2 and value 3, capacity 6. The correct 0/1 knapsack answer is ___. The one-row version with the capacity loop running UPWARDS (`for w in range(2, 7): row[w] = max(row[w], row[w-2] + 3)`) returns ___.

   <details><summary>Answer</summary>

   3 and 9. Looping upwards reads cells this item already updated, so it takes the single item three times. Looping downwards gives the correct 3.

   </details>

4. <!-- q: exact id="f5d4c0af" answer="3" -->
   Edit distance counts the fewest single-character inserts, deletes and replacements to turn one string into another. What is the edit distance from "sunday" to "saturday"?

   <details><summary>Answer</summary>

   3: insert a, insert t, and replace n with r. The DP fills D[i][j] = D[i−1][j−1] on a match, else 1 + min(delete, insert, replace).

   </details>

## 9. Practice — independent task
<!-- bite: 20fb480f-4f56-4577-afba-fcb28687d4e0 -->

**Part 1 — the three from this lesson.** Implement LCS, 0/1 knapsack and edit distance with full tables **and** reconstruction. Verify each against brute force on 300 random inputs.

**Part 2 — the loop direction, proved.** Implement the rolling knapsack both ways. Find the **smallest** instance (fewest items, smallest capacity) where they disagree, and explain the disagreement by tracing the row.

**Part 3 — unbounded knapsack.** Implement it deliberately, using the upward loop. Verify against a brute force that allows repeats. **Write one sentence on why these two problems differ by a loop direction** — that sentence is the point of the exercise.

**Part 4 — four more 2-D problems.** For each, write the state as a sentence and the transition before coding:

1. **Longest common substring** (contiguous). Note where the answer lives.
2. **Distinct subsequences** — how many times does `t` appear as a subsequence of `s`?
3. **Interleaving string** — can `s3` be formed by interleaving `s1` and `s2` while preserving order?
4. **Longest palindromic substring**, as a 2-D DP over `(start, end)`. **The fill order is the interesting part** — work out why the usual row-by-row order does not work here.

**Part 5 — space versus reconstruction.** Take LCS. Implement: full table with reconstruction; rolling row returning length only; and Hirschberg's algorithm, which recovers the sequence in $O(\min(n,m))$ space. Measure peak memory and time for all three at $n = m = 2000$ and report the trade.

**Edge cases:** one or both inputs empty; identical inputs; no common characters at all; a knapsack capacity of 0; an item heavier than the whole capacity; duplicate items.

**Done when:** everything agrees with brute force on 300 inputs; part 2 names the minimal disagreeing instance with a trace; part 4.4 explains its fill order; and part 5 reports three measured memory/time pairs.

Then find them worked: [[112-longest-common-subsequence|LCS]], [[119-edit-distance|Edit Distance]], [[110-partition-equal-subset-sum|Partition Equal Subset Sum]] (a knapsack in disguise), [[118-distinct-subsequences|Distinct Subsequences]], [[116-interleaving-string|Interleaving String]], [[103-longest-palindromic-substring|Longest Palindromic Substring]].

---

## Before moving on
<!-- bite: 33ee5c36-fcd8-42d8-9ca8-a908e7de1fe5 -->

You can set up a 2-D table with correct base rows, reconstruct the solution by walking backwards, explain the knapsack loop direction from an invariant, and say what space optimisation costs you.

**Recap:** a 2-D DP indexes prefixes of two inputs, and all three classics fill an $(n{+}1)\times(m{+}1)$ grid where row 0 and column 0 are base cases and every cell reads only **above and to the left**. **LCS** grows only on a diagonal match, and the diagonal steps traced backwards spell the subsequence. **0/1 knapsack** reads `K[i-1][...]` on *both* branches, which is what stops an item being reused — and its rolling array must iterate **downwards** so that `row[w-wt]` still holds the previous row; iterating upwards silently solves the *unbounded* knapsack, returning 15 where the answer is 5. **Edit distance** has base cases that count rather than zero, and each neighbour direction corresponds to one operation, which is how you recover an edit script. The above-and-left read pattern is why one row suffices, and equally why reconstruction needs the full table. Both knapsack and coin change are **pseudo-polynomial**.

**Before moving on from the folder:** you can now test whether DP applies, name a state/transition/base case, choose top-down or bottom-up, derive a fill order, optimise space, and reconstruct solutions in one and two dimensions. The [[15-dynamic-programming|DP pattern note]] is the recognition layer above this, and the [[dsa/neetcode-150/index|NeetCode 150]] DP section is where you build fluency.

---

## Related
<!-- bite: 16222f58-3834-42c1-be45-9238b3af4054 -->

- [[03-classic-one-dimensional|Classic 1-D DP]] — the previous lesson
- [[02-memoisation-and-tabulation|Memoisation and Tabulation]] — state, transition, fill order, space
- [[01-what-makes-a-problem-dp|What Makes a Problem DP]] — the two properties
- [[04-floyd-warshall|Floyd–Warshall]] — a 2-D DP over a graph, filled in a third dimension
- [[15-dynamic-programming|The DP pattern note]] — the recognition layer
- [[07-dynamic-programming/index|the dynamic programming folder]]

## About this lesson
<!-- bite: 40e925c2-36a8-4bc6-9ae7-67f67e2d8946 -->

**Level:** Intermediate → Advanced. **Covers:** Three problems that between them are most of what two-dimensional dynamic programming does: **longest common subsequence**, **0/1 knapsack**, and **edit distance**. They look unrelated — comparing strings, packing a bag, spell-checking — and they fill the same grid with the same read pattern.
