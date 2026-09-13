# Module: Classic One-Dimensional DP (The State Is a Single Index)

**[Intermediate]** — Three problems that between them cover most of what one-dimensional dynamic programming does: **house robber**, **coin change** and **longest increasing subsequence**. Each is worked with its state named as a sentence, its table traced cell by cell, and its answer checked against brute force on hundreds of random inputs.

The third one is the important one. Its obvious state definition does not work, and understanding *why* is worth more than the other two combined.

---

## Before you start

- You can name a state, transition and base case, and write either a memoised or a tabulated implementation — [[02-memoisation-and-tabulation|memoisation and tabulation]].
- You know that a DP's complexity is *states × transition cost* — same lesson.
- You have seen [[10-greedy-algorithms|greedy]] fail on coin change — [[01-what-makes-a-problem-dp|what makes a problem DP]].

**After this lesson you will be able to:**

1. Derive the state and transition for a 1-D DP you have not seen, by asking "what decision do I make at index $i$?".
2. Explain why the LIS state must be *"ending at $i$"* rather than *"within $0..i$"*.
3. Reconstruct the actual solution — which houses, which coins, which subsequence — rather than only its value.
4. Recognise when a $O(n^2)$ DP has a better non-DP algorithm hiding behind it.

**Study route:** work through 1 and 2, then stop at the prediction in section 3 before reading on. Section 3 is the lesson.

---

## 1. House robber — the decision at each index

> Houses in a row, each with some money. You cannot rob two adjacent houses. Maximise the total.

**The question that produces the state: at house $i$, what are my options?** Rob it, or skip it. That is the entire problem, and it gives:

- **STATE:** `best[i]` = the most money obtainable from houses $0 \dots i$.
- **TRANSITION:** `best[i] = max(best[i-1], best[i-2] + nums[i])` — skipping house $i$ leaves the best for $0..i-1$; robbing it adds `nums[i]` to the best for $0..i-2$, since $i-1$ is now forbidden.
- **BASE:** `best[0] = nums[0]`, `best[1] = max(nums[0], nums[1])`.

Traced on `[2, 7, 9, 3, 1]`:

```
     after |  0  1  2  3  4
      base |  2  7  0  0  0
       i=2 |  2  7 11  0  0
       i=3 |  2  7 11 11  0
       i=4 |  2  7 11 11 12
```

Answer 12, by robbing houses 0, 2 and 4: $2 + 9 + 1$. The lab confirms it against brute force over all $2^n$ subsets, and on **400 random inputs**.

**Note `best[3] = 11`, unchanged from `best[2]`.** House 3 holds 3, and robbing it would mean giving up house 2's 9 — so the max carried the previous value forward. **A cell whose value equals its predecessor is the table telling you "skip" won.** That observation is what makes reconstruction possible.

Since the transition reaches back only two cells, the whole array collapses to two variables:

```python
def rob(nums):
    prev2 = prev1 = 0
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1
```

**This version also handles the empty list and the single-element list without special cases**, which the array version needs explicit guards for — a small illustration that space optimisation occasionally simplifies rather than complicates.

---

## 2. Coin change — the transition tries every option

> Coins of given denominations, unlimited supply. Make an exact amount with the fewest coins, or report that it is impossible.

**The decision at amount $a$ is: which coin do I use last?** You do not know, so you try all of them.

- **STATE:** `best[a]` = the fewest coins summing to exactly $a$.
- **TRANSITION:** `best[a] = 1 + min(best[a - c])` over every coin $c \le a$.
- **BASE:** `best[0] = 0`. Everything else starts at infinity, meaning "not yet known to be reachable".

Traced on coins $\{1, 3, 4\}$, amount 6:

```
         a |   0   1   2   3   4   5   6
   best[a] |   0   1   2   1   1   2   2
```

The answer is 2 coins — $3 + 3$ — where [[10-greedy-algorithms|greedy]] takes $4 + 1 + 1$ and gets 3. Verified against brute force here and on **300 random inputs**.

**The infinity sentinel matters.** For coins $\{2, 5\}$ and amount 3, no combination works, and `best[3]` stays infinite — which is how the algorithm reports impossibility rather than returning a wrong small number. Use a real infinity or a value provably larger than any valid answer (`amount + 1` works), **never zero**.

### Reconstruction: which coins, not just how many

Record, alongside each cell, the coin that produced it:

```python
if c <= a and best[a - c] + 1 < best[a]:
    best[a] = best[a - c] + 1
    choice[a] = c              # <- remember the decision
```

Then walk backwards from `amount`, subtracting each recorded coin. **This pattern — store the decision, walk it backwards — is how every DP recovers a solution rather than a value**, and it costs one array and no extra time.

**Complexity:** $n$ states × $O(c)$ transition = $O(n \cdot c)$ for amount $n$ and $c$ coins. Note this is **pseudo-polynomial** — linear in the *value* of the amount, not in its digit count — so an amount of $10^9$ is infeasible even though it is a small input to type.

---

## 3. Longest increasing subsequence — where the obvious state fails

> Find the length of the longest strictly increasing subsequence. Elements need not be adjacent.

> **Predict before reading on.** The natural first attempt is **`lis[i]` = the length of the longest increasing subsequence within `nums[0..i]`**. Try to write the transition for it. **What goes wrong?**

**You cannot write the transition.** To decide whether `nums[i]` extends the best subsequence found in `0..i-1`, you need to know **what that subsequence's last element was** — and the state does not record it. Two different subsequences of the same length end at different values, and which one you kept determines whether the next element can extend it.

**The state is not wrong because it is imprecise. It is wrong because it is not enough information to compute the next state from.** That is the general test for a candidate state, and it is the single most transferable idea in this folder.

The fix is to make the last element part of the state's *definition*:

- **STATE:** `lis[i]` = the length of the longest increasing subsequence **ending exactly at index $i$**.
- **TRANSITION:** `lis[i] = 1 + max(lis[j])` over all $j < i$ with `nums[j] < nums[i]`; if no such $j$ exists, `lis[i] = 1`.
- **BASE:** every `lis[i]` starts at 1 — the element by itself.
- **ANSWER:** `max(lis)`, **not** `lis[n-1]`. The best subsequence need not end at the last element.

Traced on `[10, 9, 2, 5, 3, 7, 101, 18]`:

```
     index |    0    1    2    3    4    5    6    7
     value |   10    9    2    5    3    7  101   18
    lis[i] |    1    1    1    2    2    3    4    4
```

Answer 4 — `[2, 5, 7, 101]`. Verified against brute force over all subsequences, and on 300 random inputs.

**The "answer is `max(lis)` not `lis[n-1]`" point is worth pausing on.** Because the state pins the ending position, no single cell holds the global answer; you scan for it. That is a recurring consequence of pinning something in the state, and forgetting it is a common bug.

**Complexity:** $n$ states × $O(n)$ transition = $O(n^2)$.

### The $O(n \log n)$ version, and what it is not

There is a better algorithm — patience sorting — maintaining an array `tails`, where `tails[k]` is the **smallest possible tail value** of any increasing subsequence of length $k+1$. For each element, binary-search its position and overwrite. The answer is `len(tails)`.

The lab runs both:

```
   O(n^2) answer: 4  sequence [2, 5, 7, 101]
   O(n log n) answer: 4  (tails array [2, 3, 7, 18])
```

**Read those two outputs carefully. `[2, 3, 7, 18]` is not an increasing subsequence of the input** — `3` appears before `5` in the LIS but after it in the array, and `18` comes after `101`. **Only the *length* of `tails` is meaningful.** Recovering the actual subsequence from the $O(n\log n)$ version needs an extra predecessor array; the $O(n^2)$ DP gives it directly.

**This is the general lesson of section 3's second half:** an asymptotically better algorithm is not automatically the one to use. If you need the subsequence and $n$ is small, the $O(n^2)$ DP is simpler and gives you more.

---

## 4. The pattern across all four 1-D problems

| Problem | State | Transition |
| :--- | :--- | :--- |
| Climbing stairs | ways to reach step $i$ | $w[i] = w[i-1] + w[i-2]$ |
| House robber | best money from houses $0..i$ | $b[i] = \max(b[i-1],\ b[i-2] + v_i)$ |
| Coin change | fewest coins making amount $a$ | $c[a] = 1 + \min(c[a - \text{coin}])$ |
| LIS | longest subsequence **ending at** $i$ | $l[i] = 1 + \max(l[j]),\ j < i$ |

**Every one is: define what one cell means, then build it from cells with a smaller index.** The differences are only in what "smaller" means and how many earlier cells the transition consults — two for the stairs, all of them for LIS.

**And the question that generates the state each time is the same: *what decision do I make at index $i$, and what do I need to know to make it?*** For house robber: rob or skip, and you need the best totals two steps back. For coin change: which coin last, and you need every smaller amount. For LIS: extend or start fresh, and you need the last element — which is why it goes into the state.

---

## 5. Worked example — complete runnable lab

Save as `dp_1d.py`. Standard library only. **Every answer is checked against brute force**, not merely printed.

```python
"""One-dimensional DP: the state is a single index.

House robber, coin change, longest increasing subsequence -- each with its
state, transition and base case named, its table traced, and its answer
checked against brute force.

Run:  python3 dp_1d.py
"""

import itertools
from bisect import bisect_left

INF = float("inf")


# ============================================================ HOUSE ROBBER
#   STATE      best[i] = most money obtainable from houses 0..i
#   TRANSITION best[i] = max(best[i-1],            skip house i
#                            best[i-2] + nums[i])  rob house i
#   BASE       best[0] = nums[0]; best[1] = max(nums[0], nums[1])
def rob(nums):
    if not nums:
        return 0, []
    if len(nums) == 1:
        return nums[0], [list(nums)]
    best = [0] * len(nums)
    best[0] = nums[0]
    best[1] = max(nums[0], nums[1])
    rows = [list(best)]
    for i in range(2, len(nums)):
        best[i] = max(best[i - 1], best[i - 2] + nums[i])
        rows.append(list(best))
    return best[-1], rows


def rob_brute(nums):
    n = len(nums)
    best = 0
    for mask in range(1 << n):
        chosen = [i for i in range(n) if mask >> i & 1]
        if any(b - a == 1 for a, b in zip(chosen, chosen[1:])):
            continue                      # adjacent houses: not allowed
        best = max(best, sum(nums[i] for i in chosen))
    return best


def rob_space_optimised(nums):
    prev2 = prev1 = 0
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1


# ============================================================ COIN CHANGE
#   STATE      best[a] = fewest coins summing to exactly a
#   TRANSITION best[a] = 1 + min(best[a - c]) over coins c <= a
#   BASE       best[0] = 0
def coin_change(coins, amount):
    best = [0] + [INF] * amount
    choice = [None] * (amount + 1)
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and best[a - c] + 1 < best[a]:
                best[a] = best[a - c] + 1
                choice[a] = c
    if best[amount] == INF:
        return -1, [], best
    used, a = [], amount
    while a > 0:
        used.append(choice[a])
        a -= choice[a]
    return best[amount], sorted(used, reverse=True), best


def coin_change_brute(coins, amount):
    for k in range(amount + 1):
        for combo in itertools.combinations_with_replacement(coins, k):
            if sum(combo) == amount:
                return k
    return -1


# ======================================== LONGEST INCREASING SUBSEQUENCE
#   STATE      lis[i] = length of the longest increasing subsequence ENDING at i
#   TRANSITION lis[i] = 1 + max(lis[j]) over j < i with nums[j] < nums[i]
#   BASE       lis[i] = 1 (the element alone)
def lis_quadratic(nums):
    if not nums:
        return 0, []
    n = len(nums)
    length = [1] * n
    prev = [-1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i] and length[j] + 1 > length[i]:
                length[i] = length[j] + 1
                prev[i] = j
    best_i = max(range(n), key=lambda i: length[i])
    seq, i = [], best_i
    while i != -1:
        seq.append(nums[i])
        i = prev[i]
    return length[best_i], list(reversed(seq))


def lis_nlogn(nums):
    """Patience sorting: tails[k] = smallest possible tail of an LIS of length k+1."""
    tails = []
    for x in nums:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails), tails


def lis_brute(nums):
    best = 0
    n = len(nums)
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            vals = [nums[i] for i in combo]
            if all(a < b for a, b in zip(vals, vals[1:])):
                best = max(best, r)
    return best


def main():
    print("=" * 78)
    print("1. HOUSE ROBBER -- rob houses in a row, never two adjacent")
    print("=" * 78)
    nums = [2, 7, 9, 3, 1]
    print(f"\n   houses: {nums}")
    print("   STATE      best[i] = most money from houses 0..i")
    print("   TRANSITION best[i] = max(best[i-1], best[i-2] + nums[i])")
    print("   BASE       best[0] = nums[0], best[1] = max(nums[0], nums[1])")
    total, rows = rob(nums)
    print("\n     after |" + "".join(f"{i:>3}" for i in range(len(nums))))
    print(f"   {'base':>7} |" + "".join(f"{v:>3}" for v in rows[0]))
    for k, row in enumerate(rows[1:], start=2):
        print(f"   {'i=' + str(k):>7} |" + "".join(f"{v:>3}" for v in row))
    print(f"\n   answer: {total}   (rob houses 0, 2, 4 -> 2 + 9 + 1 = 12)")
    print(f"   brute force over all 2^{len(nums)} subsets: {rob_brute(nums)}")
    print(f"   space-optimised (two variables): {rob_space_optimised(nums)}")

    print("\n   Checking DP against brute force on 400 random inputs...")
    import random
    bad = 0
    for t in range(400):
        random.seed(t)
        a = [random.randint(0, 30) for _ in range(random.randint(0, 12))]
        if rob(a)[0] != rob_brute(a) or rob_space_optimised(a) != rob_brute(a):
            bad += 1
    print(f"   agreed on {400 - bad}/400")

    print("\n" + "=" * 78)
    print("2. COIN CHANGE -- fewest coins summing to an amount")
    print("=" * 78)
    coins, amount = [1, 3, 4], 6
    print(f"\n   coins: {coins}   amount: {amount}")
    print("   STATE      best[a] = fewest coins summing to exactly a")
    print("   TRANSITION best[a] = 1 + min(best[a - c]) over coins c <= a")
    print("   BASE       best[0] = 0")
    n_coins, used, table = coin_change(coins, amount)
    print("\n         a |" + "".join(f"{i:>4}" for i in range(amount + 1)))
    print("   best[a] |" + "".join(f"{('inf' if v == INF else v):>4}" for v in table))
    print(f"\n   answer: {n_coins} coins -> {used}")
    print(f"   greedy would take 4+1+1 = 3 coins. DP finds 3+3 = 2.")
    print(f"   brute force: {coin_change_brute(coins, amount)}")

    print("\n   Checking against brute force on 300 random inputs...")
    bad = 0
    for t in range(300):
        random.seed(t + 1000)
        cs = sorted(random.sample(range(1, 12), random.randint(1, 4)))
        amt = random.randint(0, 25)
        if coin_change(cs, amt)[0] != coin_change_brute(cs, amt):
            bad += 1
    print(f"   agreed on {300 - bad}/300")

    print("\n" + "=" * 78)
    print("3. LONGEST INCREASING SUBSEQUENCE")
    print("=" * 78)
    seq = [10, 9, 2, 5, 3, 7, 101, 18]
    print(f"\n   input: {seq}")
    print("   STATE      lis[i] = length of the longest increasing subsequence")
    print("              ENDING AT index i  <- the 'ending at' is essential")
    print("   TRANSITION lis[i] = 1 + max(lis[j]) for j < i with nums[j] < nums[i]")
    print("   BASE       lis[i] = 1")
    n = len(seq)
    length = [1] * n
    for i in range(n):
        for j in range(i):
            if seq[j] < seq[i]:
                length[i] = max(length[i], length[j] + 1)
    print("\n     index |" + "".join(f"{i:>5}" for i in range(n)))
    print("     value |" + "".join(f"{v:>5}" for v in seq))
    print("    lis[i] |" + "".join(f"{v:>5}" for v in length))
    q_len, q_seq = lis_quadratic(seq)
    p_len, tails = lis_nlogn(seq)
    print(f"\n   O(n^2) answer: {q_len}  sequence {q_seq}")
    print(f"   O(n log n) answer: {p_len}  (tails array {tails})")
    print(f"   brute force over all subsequences: {lis_brute(seq)}")
    print("   NOTE: the tails array is NOT itself an increasing subsequence of the")
    print("         input -- only its LENGTH is meaningful.")

    print("\n   Checking all three against each other on 300 random inputs...")
    bad = 0
    for t in range(300):
        random.seed(t + 2000)
        a = [random.randint(0, 20) for _ in range(random.randint(0, 10))]
        if not (lis_quadratic(a)[0] == lis_nlogn(a)[0] == lis_brute(a)):
            bad += 1
    print(f"   agreed on {300 - bad}/300")

    print("\n" + "=" * 78)
    print("4. THE PATTERN IN ALL THREE")
    print("=" * 78)
    print("""
   problem          | state                          | transition
   -----------------|--------------------------------|---------------------------
   climbing stairs  | ways to reach step i           | w[i] = w[i-1] + w[i-2]
   house robber     | best money from houses 0..i    | b[i] = max(b[i-1], b[i-2]+v)
   coin change      | fewest coins making amount a   | c[a] = 1 + min(c[a-coin])
   LIS              | longest subsequence ENDING at i| l[i] = 1 + max(l[j]), j<i

   -> every one is: define what ONE cell means, then say how it is built from
      cells with a SMALLER index. That is the entire method.
   -> the LIS state is the instructive one. 'Longest subsequence in 0..i' does
      NOT work as a state, because it does not tell you what the last element
      was, so you cannot decide whether the next element may extend it.
      Choosing a state that carries enough information IS the hard part.""")


if __name__ == "__main__":
    main()
```

### Expected output

Generated by running the file above:

```
==============================================================================
1. HOUSE ROBBER -- rob houses in a row, never two adjacent
==============================================================================

   houses: [2, 7, 9, 3, 1]
   STATE      best[i] = most money from houses 0..i
   TRANSITION best[i] = max(best[i-1], best[i-2] + nums[i])
   BASE       best[0] = nums[0], best[1] = max(nums[0], nums[1])

     after |  0  1  2  3  4
      base |  2  7  0  0  0
       i=2 |  2  7 11  0  0
       i=3 |  2  7 11 11  0
       i=4 |  2  7 11 11 12

   answer: 12   (rob houses 0, 2, 4 -> 2 + 9 + 1 = 12)
   brute force over all 2^5 subsets: 12
   space-optimised (two variables): 12

   Checking DP against brute force on 400 random inputs...
   agreed on 400/400

==============================================================================
2. COIN CHANGE -- fewest coins summing to an amount
==============================================================================

   coins: [1, 3, 4]   amount: 6
   STATE      best[a] = fewest coins summing to exactly a
   TRANSITION best[a] = 1 + min(best[a - c]) over coins c <= a
   BASE       best[0] = 0

         a |   0   1   2   3   4   5   6
   best[a] |   0   1   2   1   1   2   2

   answer: 2 coins -> [3, 3]
   greedy would take 4+1+1 = 3 coins. DP finds 3+3 = 2.
   brute force: 2

   Checking against brute force on 300 random inputs...
   agreed on 300/300

==============================================================================
3. LONGEST INCREASING SUBSEQUENCE
==============================================================================

   input: [10, 9, 2, 5, 3, 7, 101, 18]
   STATE      lis[i] = length of the longest increasing subsequence
              ENDING AT index i  <- the 'ending at' is essential
   TRANSITION lis[i] = 1 + max(lis[j]) for j < i with nums[j] < nums[i]
   BASE       lis[i] = 1

     index |    0    1    2    3    4    5    6    7
     value |   10    9    2    5    3    7  101   18
    lis[i] |    1    1    1    2    2    3    4    4

   O(n^2) answer: 4  sequence [2, 5, 7, 101]
   O(n log n) answer: 4  (tails array [2, 3, 7, 18])
   brute force over all subsequences: 4
   NOTE: the tails array is NOT itself an increasing subsequence of the
         input -- only its LENGTH is meaningful.

   Checking all three against each other on 300 random inputs...
   agreed on 300/300

==============================================================================
4. THE PATTERN IN ALL THREE
==============================================================================

   problem          | state                          | transition
   -----------------|--------------------------------|---------------------------
   climbing stairs  | ways to reach step i           | w[i] = w[i-1] + w[i-2]
   house robber     | best money from houses 0..i    | b[i] = max(b[i-1], b[i-2]+v)
   coin change      | fewest coins making amount a   | c[a] = 1 + min(c[a-coin])
   LIS              | longest subsequence ENDING at i| l[i] = 1 + max(l[j]), j<i

   -> every one is: define what ONE cell means, then say how it is built from
      cells with a SMALLER index. That is the entire method.
   -> the LIS state is the instructive one. 'Longest subsequence in 0..i' does
      NOT work as a state, because it does not tell you what the last element
      was, so you cannot decide whether the next element may extend it.
      Choosing a state that carries enough information IS the hard part.
```

---

## 6. Common pitfalls and traps

1. **A state that does not carry enough information.** LIS is the canonical case: "longest within $0..i$" cannot produce a transition. **Test a candidate state by trying to write the transition** — if you need a fact the state does not record, the state is wrong.
2. **Returning the last cell when the state pins an ending position.** LIS's answer is `max(lis)`, not `lis[n-1]`.
3. **Initialising an unreachable state to 0 instead of infinity.** Coin change would then report 0 coins for impossible amounts. Use infinity, or a value provably above any valid answer.
4. **Forgetting that coin change is pseudo-polynomial.** $O(n \cdot c)$ is linear in the *value* of the amount. An amount of $10^9$ is hopeless, however few coins there are.
5. **Space-optimising before you know whether you need the solution.** Two variables cannot tell you which houses were robbed.
6. **Off-by-one in the base cases.** House robber needs `best[1] = max(nums[0], nums[1])`, not `nums[1]` — with one house you take it, with two you take the better. The rolling version sidesteps this by starting both accumulators at 0.
7. **Assuming a $O(n^2)$ DP is the best known.** LIS has an $O(n\log n)$ algorithm that is not a DP at all. Conversely, do not reach for it reflexively — it does not hand you the subsequence.
8. **Reading the `tails` array as an answer.** It is a scaffold. Its length is the answer; its contents are not a subsequence of the input.

---

## 7. Check your understanding

1. **Why must the LIS state be "ending at $i$"?**
   <details><summary>Answer</summary>Because the transition must decide whether <code>nums[i]</code> can extend an earlier subsequence, and that depends on the earlier subsequence's <i>last element</i>. A state recording only a length over a prefix does not carry that, so the transition cannot be written. Pinning the ending index makes the last element known — it is <code>nums[i]</code> — at the cost of needing <code>max(lis)</code> rather than the final cell for the answer.</details>

2. **House robber's transition reaches back two cells. What does that buy you?**
   <details><summary>Answer</summary>$O(1)$ space. Only <code>best[i-1]</code> and <code>best[i-2]</code> are ever read, so two variables suffice and the array is unnecessary. The cost is that reconstruction becomes impossible — you can report 12, but not that it came from houses 0, 2 and 4.</details>

3. **Coin change is $O(n \cdot c)$. Why is that not polynomial in the input size?**
   <details><summary>Answer</summary>Because $n$ is the <i>value</i> of the amount, and the input size is the number of digits needed to write it — about $\log_{10} n$. So the running time is exponential in the input length. That is what "pseudo-polynomial" means, and it is why an amount of $10^9$ is infeasible while an amount of $10^4$ is instant.</details>

4. **House robber's transition is `max(best[i-1], best[i-2] + nums[i])`. Why are those two options exhaustive — why is there no third case?**
   <details><summary>Answer</summary>Because the only decision at house $i$ is rob it or skip it, and each choice fully determines what the rest of the problem is. If you <b>skip</b> $i$, the constraint on $i-1$ disappears, so the best obtainable is exactly <code>best[i-1]</code>. If you <b>rob</b> $i$, then $i-1$ is forbidden and everything from $0..i-2$ is unconstrained, so the best is <code>best[i-2] + nums[i]</code>. There is no third option because there is no third thing you can do with house $i$. <b>Checking that your cases are exhaustive is the standard way to verify a transition</b> — a missing case is the most common source of a DP that is almost right.</details>

5. **When would you use the $O(n^2)$ LIS over the $O(n\log n)$ one?**
   <details><summary>Answer</summary>When you need the actual subsequence and not just its length, and $n$ is small enough that $n^2$ is affordable. The DP stores a predecessor per index, so reconstruction is a backwards walk. The patience-sorting version's <code>tails</code> array is a scaffold whose contents are not a subsequence at all, so recovering one needs extra bookkeeping.</details>

---

## 8. Practice — independent task

Four problems. For each: **write the state as a full sentence, the transition, and the base case before coding**, and predict the complexity from states × transition.

1. **Min cost climbing stairs.** Each step has a cost; you may start at step 0 or 1 and climb 1 or 2 at a time. Minimise total cost to get past the top.
2. **House robber II** — the houses are in a **circle**, so the first and last are adjacent. *Hint after you have attempted it: solve the linear version twice.*
3. **Word break.** Given a string and a dictionary, can the string be segmented into dictionary words? Then: return one such segmentation.
4. **Decode ways.** `"A"→1 … "Z"→26`. Count the decodings of a digit string. **The edge cases are the problem here** — handle `"0"`, `"06"`, `"10"`, `"27"`.

**For each, also:**

- Verify against brute force on at least 300 random inputs.
- Implement the space-optimised version and confirm it agrees.
- Implement reconstruction where the problem has a solution to recover, and **state explicitly which version cannot do it**.

**Then one harder pair:**

5. **Longest increasing subsequence, both ways**, with reconstruction for each. For the $O(n\log n)$ version you will need a predecessor array — work out why the naive attempt at reconstruction from `tails` gives a wrong sequence, and **produce a concrete input where it does**.
6. **Maximum product subarray.** Kadane's does not transfer directly. Work out why a single running maximum is insufficient, and what the state must become.

**Edge cases throughout:** empty input; a single element; all elements equal; all negative; an impossible instance.

**Done when:** every problem agrees with brute force on 300 inputs; every predicted complexity matches; you have a concrete wrong sequence for part 5; and you can state in one sentence what problem 6's state must carry that Kadane's does not.

Then find them worked: [[100-min-cost-climbing-stairs|Min Cost Climbing Stairs]], [[102-house-robber-ii|House Robber II]], [[108-word-break|Word Break]], [[105-decode-ways|Decode Ways]], [[109-longest-increasing-subsequence|LIS]], [[107-maximum-product-subarray|Maximum Product Subarray]].

---

## Before moving on

You can derive a state by asking what decision happens at index $i$; explain why LIS needs "ending at $i$"; reconstruct the actual solution from a decision array; and recognise when a better non-DP algorithm exists.

**Recap:** a 1-D DP defines one cell per index and builds it from smaller indices. **House robber** — rob or skip — reaches back two cells, so it collapses to $O(1)$ space at the cost of reconstruction. **Coin change** tries every coin in its transition, needs an infinity sentinel to report impossibility, and is **pseudo-polynomial**: $O(n \cdot c)$ in the *value* of the amount. **LIS** is the instructive one: the obvious state cannot produce a transition, because deciding whether to extend needs the previous subsequence's last element — so pin the ending index, and then remember the answer is `max(lis)` rather than the final cell. Reconstruct any of them by storing the decision that produced each cell and walking it backwards. And an $O(n\log n)$ alternative existing does not make the $O(n^2)$ DP obsolete: patience sorting's `tails` array is not a subsequence, and only its length means anything.

**Next:** [[04-classic-two-dimensional|Classic Two-Dimensional DP]] — LCS, 0/1 knapsack and edit distance, where the state is a pair of indices and the table becomes a grid.

---

## Related

- [[02-memoisation-and-tabulation|Memoisation and Tabulation]] — the previous lesson: state, transition, base case
- [[04-classic-two-dimensional|Classic 2-D DP]] — the next dimension
- [[10-greedy-algorithms|Greedy Algorithms]] — why greedy coin change fails
- [[09-max-slice-algorithms|Max Slice / Kadane's]] — a 1-D scan that is DP in disguise
- [[15-dynamic-programming|The DP pattern note]] — the recognition layer above this folder
- [[06-dynamic-programming/index|the dynamic programming folder]]
