# Module: What Makes a Problem Dynamic Programming (The Two Properties)

**[Intermediate]** — Dynamic programming is not a data structure, an algorithm, or a kind of loop. **It is what you do when a recursion keeps solving the same subproblem over and over.** That is the whole idea, and the rest of this folder is technique.

But it only works on problems with two specific properties, and being able to *check* for them — rather than recognising a problem from having seen it before — is what separates someone who can do DP from someone who can do the DP problems they have memorised.

---

## Before you start

- You can write a recursive function and identify its base case, recursive case and cost — [[01-recursion-fundamentals|recursion fundamentals]].
- You know what **memoisation** is, and have seen naive Fibonacci go from 2,692,537 calls to 59 — same lesson.
- You can distinguish [[03-divide-and-conquer|divide and conquer]] from a plain recursion.
- You have met [[01-when-greedy-works|greedy algorithms]] and know they are not always correct.

**After this lesson you will be able to:**

1. Test a recursion for **overlapping subproblems** by measurement, not intuition.
2. State what **optimal substructure** means and give a problem that lacks it.
3. Place any problem in the two-by-two grid of *overlapping* × *optimal substructure* and name the right technique.
4. Explain why greedy fails on coin change even though the problem has optimal substructure.

**Study route:** read 1–3, answer the prediction in section 4, then run the lab. Its first block gives you a test you can apply mechanically to anything.

---

## 1. Why this exists: the same subproblem, thousands of times

[[01-recursion-fundamentals|The recursion lesson]] showed naive Fibonacci making 2,692,537 calls for $n = 30$ and a memoised version making 59. The gap was not cleverness — it was that the naive version solved `fib(25)` thousands of separate times and threw the answer away each time.

**That is dynamic programming in one sentence: recognise that a recursion is recomputing, and stop it.**

The technique is trivial once you see it. **The skill is deciding whether it applies**, and for that there are exactly two questions.

---

## Terms used in dynamic programming

1. **Dynamic programming**: This is the technique of solving a problem by solving its subproblems once each and reusing the stored answers. The name is historical and unhelpful — Richard Bellman chose "dynamic programming" in the 1950s partly because it sounded impressive to a research sponsor. **It means neither "dynamic" nor "programming".** Read it as "careful recursion with a cache".
2. **Subproblem**: This is a smaller instance of the same problem. For Fibonacci, `fib(k)` for each $k < n$. Identifying what counts as a subproblem is the same act as choosing the **state**, covered in [[02-memoisation-and-tabulation|lesson 02]].
3. **Overlapping subproblems**: This means the recursion solves the *same* subproblem more than once. **It is measurable**: count total recursive calls and distinct arguments, and compare. Without overlap there is nothing to cache.
4. **Optimal substructure**: This means an optimal solution to the whole problem is built out of optimal solutions to its subproblems. Without it, caching sub-answers is useless because the sub-answers cannot legitimately be combined.
5. **Memoisation**: This is caching results as the recursion runs — **top-down**. The recursion's shape is unchanged; you add a dictionary.
6. **Tabulation**: This is filling a table of subproblem answers in a deliberate order with loops — **bottom-up**. Same answers, no recursion.
7. **State space**: This is the set of distinct subproblems. **Its size times the cost of one transition is the complexity of the DP**, which is why counting states is how you predict the cost before writing anything.

---

## 2. Property one: overlapping subproblems — and how to measure it

Do not guess. **Instrument the recursion, count total calls and distinct arguments, and divide.** The lab does exactly this:

```
  problem                     |    calls | distinct | redundancy
  fib(20)                     |   21,891 |       21 |    1042.4x
  fib(25)                     |  242,785 |       26 |    9337.9x
  fib(30)                     | 2,692,537 |       31 |   86856.0x
  grid paths 8x8              |    6,863 |       63 |     108.9x
  grid paths 12x12            | 1,410,863 |      143 |    9866.2x
  merge sort n=1024           |    2,047 |    2,047 |       1.0x
```

**Read the last row against the others.** Merge sort's redundancy is exactly 1.0 — every recursive call receives a different slice, so no subproblem is ever repeated. **Memoising merge sort would add hashing and storage and save nothing.** That is why merge sort is [[03-divide-and-conquer|divide and conquer]] and not dynamic programming, despite both being recursive.

Fibonacci at $n=30$ has 31 distinct subproblems and makes 2.7 million calls — a redundancy of 86,856×. Caching converts the second number into the first.

**The test, stated once:** if distinct subproblems $\ll$ total calls, you have overlap, and memoisation collapses the exponential tree into a linear (or polynomial) walk over the state space.

---

## 3. Property two: optimal substructure

**Optimal substructure means: an optimal solution to the whole contains optimal solutions to its parts.** It sounds like it must always be true. It is not, and the counterexample is worth knowing because it shows what can go wrong.

Take this graph, with all edges weight 1:

```
      A ─── B
      │ ╲   │ ╲
      │   ╲ │   ╲
      C ─── D
      (edges: A-B, A-C, B-C, B-D, C-D)
```

**Shortest path has optimal substructure.** The lab computes:

```
    shortest A->D = 2  via A->B->D
    shortest A->B = 1  via A->B
    shortest B->D = 1  via B->D
    A->B then B->D = 2, and the true A->D is 2: consistent.
```

Every subpath of a shortest path is itself a shortest path — if it were not, you could substitute the better subpath and improve the whole, contradicting optimality. **That property is precisely what lets [[02-dijkstra|Dijkstra]] and [[04-floyd-warshall|Floyd–Warshall]] compose sub-answers.**

**Longest *simple* path does not.** Same graph:

```
    longest A->D = 3  via A->B->C->D
    longest A->B = 3  via A->C->D->B
    longest B->D = 3  via B->A->C->D
    composing them: 3 + 3 = 6, but the true longest A->D is 3.
    The composed walk is A->C->D->B->A->C->D, which repeats a vertex.
```

**The sub-answers are each optimal and they are mutually incompatible.** The best route from A to B uses up C and D; the best route from B to D needs them again. There is no way to combine optimal sub-answers into an optimal whole, so no DP formulation exists — and indeed longest simple path is NP-hard.

**The test:** take an optimal solution and cut it in half. Is each half optimal *for the subproblem it solves*? If forcing a half to be optimal can make the whole worse, you do not have optimal substructure.

---

## 4. The grid, and where greedy fits

> **Predict before reading on.** Coin change with coins $\{1, 3, 4\}$, making amount 6. Greedy takes the largest coin that fits, repeatedly: $4$, then $1$, then $1$ — three coins. Is three optimal? And if not, does that mean coin change lacks optimal substructure?

**Three is not optimal — $3 + 3$ is two coins.** But coin change **does** have optimal substructure, and understanding why both are true is the point.

Optimal substructure says: if the optimal solution for amount 6 uses a coin $c$, then the rest of that solution is an optimal solution for amount $6 - c$. **That is true here** — the optimal 2-coin solution uses a 3, and $\{3\}$ is indeed the optimal solution for amount 3.

What greedy assumes is something *stronger and false*: that you can determine **which** coin to use by a local rule, without solving the subproblems. Optimal substructure tells you the sub-answers compose; it does not tell you which sub-answer to compose with. **DP tries every coin and lets the table decide; greedy guesses and commits.**

The lab measures it, with the DP asserted against brute force rather than merely printed:

```
   coins          | amount | greedy |  DP  | brute | greedy right?
   [1, 5, 10, 25] |     63 |      6 |    6 |     6 | yes
   [1, 3, 4]      |      6 |      3 |    2 |     2 | NO
   [1, 7, 10]     |     14 |      5 |    2 |     2 | NO
   [2, 5]         |      3 |     -1 |   -1 |    -1 | yes
```

**Greedy is right for US coins and wrong for $\{1,3,4\}$** — and nothing about the problem statement tells you which case you are in. That is why "greedy feels right" is not an argument.

### The grid

| Overlapping? | Optimal substructure? | Technique |
| :--- | :--- | :--- |
| no | yes | **[[03-divide-and-conquer\|divide and conquer]]** — merge sort, binary search |
| **yes** | **yes** | **dynamic programming** |
| yes | no | no efficient method known — longest simple path, NP-hard |
| no | no | brute force or [[14-backtracking\|backtracking]] |

**And a fifth case sits inside row two:** when a *local* rule provably picks the right subproblem, you can skip the table entirely and use a [[01-when-greedy-works|greedy algorithm]] — faster, but it needs a proof, not a feeling.

---

## 5. Worked example — complete runnable lab

Save as `dp_what_makes_it.py`. Standard library only.

```python
"""The two properties a problem needs before dynamic programming applies.

Run:  python3 dp_what_makes_it.py
"""

import itertools


# ============================== 1. OVERLAPPING SUBPROBLEMS ==================
def fib_calls(n):
    """Count total calls and distinct subproblems for naive Fibonacci."""
    total = [0]
    seen = set()

    def go(k):
        total[0] += 1
        seen.add(k)
        if k < 2:
            return k
        return go(k - 1) + go(k - 2)

    go(n)
    return total[0], len(seen)


def grid_calls(r, c):
    """Same measurement for 'count paths through an r x c grid'."""
    total = [0]
    seen = set()

    def go(i, j):
        total[0] += 1
        seen.add((i, j))
        if i == 0 or j == 0:
            return 1
        return go(i - 1, j) + go(i, j - 1)

    go(r - 1, c - 1)
    return total[0], len(seen)


def mergesort_calls(n):
    """A recursion with NO overlap: every call gets a different slice."""
    total = [0]
    seen = set()

    def go(lo, hi):
        total[0] += 1
        seen.add((lo, hi))
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        go(lo, mid)
        go(mid, hi)

    go(0, n)
    return total[0], len(seen)


# ============================== 2. OPTIMAL SUBSTRUCTURE =====================
# A graph where the LONGEST SIMPLE PATH breaks optimal substructure.
GRAPH = {
    "A": {"B": 1, "C": 1},
    "B": {"A": 1, "C": 1, "D": 1},
    "C": {"A": 1, "B": 1, "D": 1},
    "D": {"B": 1, "C": 1},
}


def all_simple_paths(graph, s, t, path=None):
    path = path or [s]
    if s == t:
        yield list(path)
        return
    for nb in graph[s]:
        if nb not in path:
            path.append(nb)
            yield from all_simple_paths(graph, nb, t, path)
            path.pop()


def shortest_path(graph, s, t):
    return min(((len(p) - 1, p) for p in all_simple_paths(graph, s, t)), key=lambda x: x[0])


def longest_path(graph, s, t):
    return max(((len(p) - 1, p) for p in all_simple_paths(graph, s, t)), key=lambda x: x[0])


# ============================== 3. DOES MEMOISATION HELP? ===================
def measure(fn, *args):
    """Run a counting recursion with and without a cache."""
    plain_total, distinct = fn(*args)
    return plain_total, distinct, plain_total / max(distinct, 1)


# ============================== 4. A DP AND A NON-DP SIDE BY SIDE ===========
def coin_change_dp(coins, amount):
    INF = float("inf")
    best = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and best[a - c] + 1 < best[a]:
                best[a] = best[a - c] + 1
    return best[amount] if best[amount] != INF else -1


def coin_change_brute(coins, amount):
    for k in range(0, amount + 1):
        for combo in itertools.combinations_with_replacement(coins, k):
            if sum(combo) == amount:
                return k
    return -1


def coin_change_greedy(coins, amount):
    """The locally-optimal rule. Correct for some coin systems, not all."""
    left, used = amount, 0
    for c in sorted(coins, reverse=True):
        take = left // c
        used += take
        left -= take * c
    return used if left == 0 else -1


def main():
    print("=" * 74)
    print("PROPERTY 1: OVERLAPPING SUBPROBLEMS")
    print("  Does the recursion solve the SAME subproblem more than once?")
    print("=" * 74)
    print("\n  problem                     |    calls | distinct | redundancy")
    for label, fn, args in (
        ("fib(20)", fib_calls, (20,)),
        ("fib(25)", fib_calls, (25,)),
        ("fib(30)", fib_calls, (30,)),
        ("grid paths 8x8", grid_calls, (8, 8)),
        ("grid paths 12x12", grid_calls, (12, 12)),
        ("merge sort n=1024", mergesort_calls, (1024,)),
    ):
        total, distinct, ratio = measure(fn, *args)
        print(f"  {label:<27} | {total:>8,} | {distinct:>8,} | {ratio:>9.1f}x")
    print("\n  -> fib and grid-paths re-solve the same subproblem thousands of times.")
    print("     Merge sort's redundancy is 1.0x: every call gets a DIFFERENT slice,")
    print("     so there is nothing to cache and memoisation would be pure overhead.")
    print("  -> THE TEST: count distinct subproblems. If it is far below the call")
    print("     count, you have overlap, and caching converts one into the other.")

    print("\n" + "=" * 74)
    print("PROPERTY 2: OPTIMAL SUBSTRUCTURE")
    print("  Is an optimal solution built from optimal solutions to subproblems?")
    print("=" * 74)
    print("\n  Graph:  A-B  A-C  B-C  B-D  C-D   (all edges weight 1)")
    print("\n  SHORTEST path has optimal substructure:")
    d_ad, p_ad = shortest_path(GRAPH, "A", "D")
    d_ab, p_ab = shortest_path(GRAPH, "A", "B")
    d_bd, p_bd = shortest_path(GRAPH, "B", "D")
    print(f"    shortest A->D = {d_ad}  via {'->'.join(p_ad)}")
    print(f"    shortest A->B = {d_ab}  via {'->'.join(p_ab)}")
    print(f"    shortest B->D = {d_bd}  via {'->'.join(p_bd)}")
    print(f"    A->B then B->D = {d_ab + d_bd}, and the true A->D is {d_ad}: consistent.")
    print("    Every subpath of a shortest path is itself a shortest path. That is")
    print("    why Dijkstra and Floyd-Warshall can compose sub-answers.")

    print("\n  LONGEST SIMPLE path does NOT:")
    l_ad, lp_ad = longest_path(GRAPH, "A", "D")
    l_ab, lp_ab = longest_path(GRAPH, "A", "B")
    l_bd, lp_bd = longest_path(GRAPH, "B", "D")
    print(f"    longest A->D = {l_ad}  via {'->'.join(lp_ad)}")
    print(f"    longest A->B = {l_ab}  via {'->'.join(lp_ab)}")
    print(f"    longest B->D = {l_bd}  via {'->'.join(lp_bd)}")
    print(f"    composing them: {l_ab} + {l_bd} = {l_ab + l_bd}, but the true longest A->D is {l_ad}.")
    print(f"    The composed walk is {'->'.join(lp_ab)} + {'->'.join(lp_bd[1:])}"
          f" = {'->'.join(lp_ab + lp_bd[1:])},")
    print("    which repeats a vertex -- so it is not a simple path at all.")
    print("    -> the sub-answers are optimal but INCOMPATIBLE. No DP formulation")
    print("       exists for longest simple path; it is NP-hard.")

    print("\n" + "=" * 74)
    print("BOTH PROPERTIES TOGETHER")
    print("=" * 74)
    print("\n  overlapping | optimal substructure | technique")
    print("  ------------|----------------------|---------------------------")
    print("      no      |         yes          | divide and conquer")
    print("      yes     |         yes          | DYNAMIC PROGRAMMING")
    print("      yes     |         no           | no efficient method known")
    print("      no      |         no           | brute force / backtracking")

    print("\n" + "=" * 74)
    print("WORKED: coin change -- why greedy is not enough")
    print("=" * 74)
    cases = [
        ([1, 5, 10, 25], 63, "US coins"),
        ([1, 3, 4], 6, "the classic counterexample"),
        ([1, 7, 10], 14, "another"),
        ([2, 5], 3, "impossible"),
    ]
    print("\n   coins          | amount | greedy |  DP  | brute | greedy right?")
    for coins, amount, label in cases:
        g = coin_change_greedy(coins, amount)
        d = coin_change_dp(coins, amount)
        b = coin_change_brute(coins, amount)
        assert d == b, f"DP disagrees with brute force on {coins}/{amount}"
        print(f"   {str(coins):<14} | {amount:>6} | {g:>6} | {d:>4} | {b:>5} | "
              f"{'yes' if g == d else 'NO'}")
    print("\n  -> DP agrees with brute force every time (asserted, not just printed).")
    print("     Greedy fails on {1,3,4} at 6: it takes 4+1+1 = 3 coins where 3+3 = 2.")
    print("     Optimal substructure holds, but the LOCAL choice is not part of it --")
    print("     you must consider every coin, which is exactly what the DP does.")


if __name__ == "__main__":
    main()
```

### Expected output

Generated by running the file above:

```
==========================================================================
PROPERTY 1: OVERLAPPING SUBPROBLEMS
  Does the recursion solve the SAME subproblem more than once?
==========================================================================

  problem                     |    calls | distinct | redundancy
  fib(20)                     |   21,891 |       21 |    1042.4x
  fib(25)                     |  242,785 |       26 |    9337.9x
  fib(30)                     | 2,692,537 |       31 |   86856.0x
  grid paths 8x8              |    6,863 |       63 |     108.9x
  grid paths 12x12            | 1,410,863 |      143 |    9866.2x
  merge sort n=1024           |    2,047 |    2,047 |       1.0x

  -> fib and grid-paths re-solve the same subproblem thousands of times.
     Merge sort's redundancy is 1.0x: every call gets a DIFFERENT slice,
     so there is nothing to cache and memoisation would be pure overhead.
  -> THE TEST: count distinct subproblems. If it is far below the call
     count, you have overlap, and caching converts one into the other.

==========================================================================
PROPERTY 2: OPTIMAL SUBSTRUCTURE
  Is an optimal solution built from optimal solutions to subproblems?
==========================================================================

  Graph:  A-B  A-C  B-C  B-D  C-D   (all edges weight 1)

  SHORTEST path has optimal substructure:
    shortest A->D = 2  via A->B->D
    shortest A->B = 1  via A->B
    shortest B->D = 1  via B->D
    A->B then B->D = 2, and the true A->D is 2: consistent.
    Every subpath of a shortest path is itself a shortest path. That is
    why Dijkstra and Floyd-Warshall can compose sub-answers.

  LONGEST SIMPLE path does NOT:
    longest A->D = 3  via A->B->C->D
    longest A->B = 3  via A->C->D->B
    longest B->D = 3  via B->A->C->D
    composing them: 3 + 3 = 6, but the true longest A->D is 3.
    The composed walk is A->C->D->B + A->C->D = A->C->D->B->A->C->D,
    which repeats a vertex -- so it is not a simple path at all.
    -> the sub-answers are optimal but INCOMPATIBLE. No DP formulation
       exists for longest simple path; it is NP-hard.

==========================================================================
BOTH PROPERTIES TOGETHER
==========================================================================

  overlapping | optimal substructure | technique
  ------------|----------------------|---------------------------
      no      |         yes          | divide and conquer
      yes     |         yes          | DYNAMIC PROGRAMMING
      yes     |         no           | no efficient method known
      no      |         no           | brute force / backtracking

==========================================================================
WORKED: coin change -- why greedy is not enough
==========================================================================

   coins          | amount | greedy |  DP  | brute | greedy right?
   [1, 5, 10, 25] |     63 |      6 |    6 |     6 | yes
   [1, 3, 4]      |      6 |      3 |    2 |     2 | NO
   [1, 7, 10]     |     14 |      5 |    2 |     2 | NO
   [2, 5]         |      3 |     -1 |   -1 |    -1 | yes

  -> DP agrees with brute force every time (asserted, not just printed).
     Greedy fails on {1,3,4} at 6: it takes 4+1+1 = 3 coins where 3+3 = 2.
     Optimal substructure holds, but the LOCAL choice is not part of it --
     you must consider every coin, which is exactly what the DP does.
```

---

## 6. Common pitfalls and traps

1. **Assuming any recursion with repeated-looking work is DP.** Measure it. Merge sort recurses heavily and has 1.0× redundancy; caching it is pure loss.
2. **Assuming optimal substructure because the problem sounds similar to one that has it.** Shortest path has it; longest simple path does not, and they differ by one word.
3. **Trusting greedy because it works on your examples.** It works on US coins and fails on $\{1,3,4\}$. Either prove the exchange argument or use the table.
4. **Confusing "the subproblems are optimal" with "I know which subproblem to use".** Optimal substructure guarantees composition is valid; it says nothing about which option to pick, which is why DP tries all of them.
5. **Calling divide and conquer "DP with no repeats".** The distinction is real and decides whether a cache helps. If the recursion never revisits a subproblem, it is not DP.
6. **Forgetting that DP's cost is states × transition.** If the state space is exponential, memoising an exponential recursion gives you an exponential DP. Caching does not create efficiency; it only removes redundancy.

---

## 7. Check your understanding

1. **Why would memoising merge sort not help?**
   <details><summary>Answer</summary>Because it has no overlapping subproblems. Every recursive call receives a distinct slice of the array, so no cache entry is ever read back. The lab measures 2,047 calls and 2,047 distinct arguments — a redundancy of exactly 1.0×. You would pay hashing and memory for zero hits.</details>

2. **Shortest path has optimal substructure; longest simple path does not. What exactly breaks?**
   <details><summary>Answer</summary>The sub-answers stop being combinable. The longest A→B path and the longest B→D path are each optimal for their own subproblem, but they reuse vertices, so joining them produces a walk that revisits a vertex — not a simple path at all. With shortest paths this cannot happen: a subpath of a shortest path must itself be shortest, or you could substitute a better one and improve the whole.</details>

3. **Coin change has optimal substructure but greedy fails on it. Are those consistent?**
   <details><summary>Answer</summary>Yes. Optimal substructure says: <i>if</i> the optimal answer for amount $a$ uses coin $c$, then the remainder is the optimal answer for $a - c$. It does not say which $c$ that is. Greedy assumes the largest fitting coin is always the right choice, which is an extra claim and a false one — on $\{1,3,4\}$ at 6, greedy takes 4 and needs three coins where $3+3$ needs two. DP evaluates every $c$ and lets the table decide.</details>

4. **A recursion has 10^6 calls and 10^6 distinct arguments. What does that tell you?**
   <details><summary>Answer</summary>There is no overlap, so memoisation cannot help — every cache write would be followed by no reads. Either it is a divide-and-conquer recursion, or your state is carrying too much information and is accidentally distinguishing subproblems that are really the same. <b>The second possibility is worth checking</b>: including a depth counter or a path in the state is a classic way to destroy overlap that genuinely exists.</details>

5. **Name a problem in each cell of the two-by-two grid.**
   <details><summary>Answer</summary>No overlap + substructure: merge sort, binary search. Overlap + substructure: Fibonacci, coin change, LCS, knapsack. Overlap + no substructure: longest simple path (NP-hard). Neither: generating all permutations — there is nothing to optimise and nothing repeats, so it is plain enumeration.</details>

---

## 8. Practice — independent task

Write a **DP detector** and apply it to problems you have not classified yet.

**Part 1 — the instrument.** Write a decorator that wraps a recursive function and records total calls and distinct argument tuples, returning the redundancy ratio.

**Part 2 — classify six recursions.** Apply it to: Fibonacci, grid paths, merge sort, quicksort, computing $n!$, and generating all subsets of a set. Report each redundancy ratio and **predict it before measuring**.

**Part 3 — destroy the overlap deliberately.** Take grid paths and add a useless `depth` parameter to the state. Measure the redundancy again. **Explain in one sentence why it collapsed**, and connect that to the advice about choosing a minimal state.

**Part 4 — optimal substructure by experiment.** For a small weighted graph, compute shortest and longest simple paths between all pairs by brute force. For every triple $(u, v, w)$, check whether `best(u,w) + best(w,v)` equals `best(u,v)` when $w$ lies on an optimal $u \to v$ route. Report how often it holds for each problem.

**Part 5 — when is greedy safe?** For coin systems $\{1,5,10,25\}$, $\{1,3,4\}$, $\{1,7,10\}$ and $\{1,2,5,10,20,50\}$, compare greedy against DP for every amount from 1 to 200. Report the smallest amount where each first fails, or that it never does.

**Edge cases:** a recursion with no recursive calls; one where every call has identical arguments; an empty input; a coin system without a 1 coin (where some amounts are impossible).

**Done when:** every part-2 prediction matches the measurement or you can explain the gap; part 3 explains the collapse; part 4 reports concrete hold-rates for both path problems; and part 5 gives the exact first failing amount for each greedy-unsafe system.

---

## Before moving on

You can measure overlap rather than guess at it, state what optimal substructure means and produce a problem that lacks it, place a problem in the two-by-two grid, and explain why greedy's failure on coin change is not a failure of optimal substructure.

**Recap:** dynamic programming is *recursion plus a cache*, and it applies exactly when two properties hold. **Overlapping subproblems** is measurable — count total calls against distinct arguments; Fibonacci at $n=30$ scores 86,856× and merge sort scores 1.0×, which is why one is DP and the other is divide and conquer. **Optimal substructure** means optimal sub-answers compose into an optimal whole; shortest path has it, longest simple path does not, and the sub-answers there are individually optimal yet mutually incompatible. Both properties → dynamic programming. Substructure without overlap → divide and conquer. Overlap without substructure → no efficient method known. **Greedy is the special case where a local rule provably picks the right subproblem** — it needs a proof, and on coins $\{1,3,4\}$ at amount 6 it is simply wrong.

**Next:** [[02-memoisation-and-tabulation|Memoisation and Tabulation]] — the two ways to build the table, how to define a state and a transition, and how to cut the memory afterwards.

---

## Related

- [[02-memoisation-and-tabulation|Memoisation and Tabulation]] — the next lesson: how to actually write one
- [[01-recursion-fundamentals|Recursion Fundamentals]] — where memoisation first appears
- [[03-divide-and-conquer|Divide and Conquer]] — the technique for when subproblems do *not* overlap
- [[01-when-greedy-works|Greedy Algorithms]] — when a local rule is provably enough
- [[04-floyd-warshall|Floyd–Warshall]] — a DP over graphs, and optimal substructure in action
- [[06-dynamic-programming/index|the dynamic programming folder]]
