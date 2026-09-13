# Module: Greedy Selection and Scheduling (Sort by the Right Key, Then Sweep)

**[Intermediate → Advanced]** — [[01-when-greedy-works|The previous lesson]] established when a greedy algorithm is *allowed*. This one is the family that shows up most in interviews and in real systems: **choosing a subset — of people, of meetings, of jobs — to minimise a cost or maximise a count.**

Nearly every algorithm here has the same shape: **sort by one key, then sweep once.** Finding the key is the problem. Proving it is the other half — and the cost problem below has a key that almost nobody guesses first time.

---

## Before you start

- You know what makes a greedy choice safe, and have seen coin change $\{1,3,4\}$ defeat the obvious rule — [[01-when-greedy-works|when greedy works]].
- You can use a [[08-heaps|heap]] as a priority queue, and know `heapq` is a **min**-heap.
- You know what an [[01-what-makes-a-problem-dp|exchange argument]] is, or are willing to meet one here.

**After this lesson you will be able to:**

1. Solve the **hire-K-workers** problem, and explain why the cheapest-looking candidates are often the wrong ones.
2. Apply the **sort-then-sweep** template, and say which sort key each classic problem needs.
3. Distinguish **"select the most"** from **"cover them all"** — two questions about the same data with opposite answers.
4. Prove a greedy correct with an **exchange argument**, rather than testing it and hoping.

**Study route:** work section 1 carefully and answer its prediction before reading on — it is the one that catches people. Sections 2 and 3 are faster once the template is visible.

---

## 1. Hire K workers: the cost problem

> You are hiring **K** people from a pool. Each candidate has a **quality** (how much work they do) and a **minimum wage** they will accept. Company policy — and in many countries, law — says people doing the same job must be paid **in proportion to their contribution**. So whatever group you hire, everyone is paid at the same *rate per unit of quality*, and nobody may be paid below their own minimum.
>
> **Which K people cost you the least in total?**

### Why the obvious answer is wrong

The instinct is: sort by advertised wage, take the K cheapest. Consider:

| person | quality | min wage | ratio (wage ÷ quality) |
| :--- | ---: | ---: | ---: |
| A | 10 | 70 | 7.00 |
| B | 20 | 140 | 7.00 |
| C | 5 | 60 | 12.00 |

Hiring **K = 2**, the two lowest advertised wages are A (70) and C (60) — apparently 130.

**It is not 130.** C demands 60 for only 5 quality, a rate of 12.00 per unit. If C is in the group, *everyone* is paid at 12.00. So A — who would have accepted 70 — must now be paid $12.00 \times 10 = 120$, and the real bill is $12.00 \times (10 + 5) = 180$.

> **Predict before reading on.** Given that, is A + B better or worse than A + C? A and B both have ratio 7.00, so the rate is only 7.00 — but B's quality is 20. **Work out both totals before continuing.**

The lab enumerates all three groups:

```
     ['A', 'B']  rate  7.00 x quality  30  =  210.00
     ['A', 'C']  rate 12.00 x quality  15  =  180.00
     ['B', 'C']  rate 12.00 x quality  25  =  300.00
```

**A + C wins at 180**, despite containing the person with the worst rate. The cheap rate of A + B is more than cancelled by B's high quality, because **you pay for quality you do not need.**

**That is the whole difficulty: the cost of a group is not the sum of its members' costs.** It is a product of two things that pull in opposite directions.

### The formula

For a group $S$ paid at rate $r$: every member needs $r \times q_i \ge w_i$, so $r \ge w_i / q_i$ for all of them, and the cheapest legal rate is the **largest ratio in the group**:

$$\text{cost}(S) = \left(\max_{i \in S} \frac{w_i}{q_i}\right) \times \sum_{i \in S} q_i$$

**State that in words before trusting it: the bill is the group's worst rate multiplied by the group's total quality.** One person sets the price; everyone contributes to the volume.

### The greedy

The formula splits the problem in a way that makes a greedy possible:

1. **Sort everyone by ratio, ascending.**
2. Walk the list. The worker you are currently at has the **largest ratio seen so far**, so if they are in the group, they set the rate.
3. Given that rate, you want the $K$ **smallest qualities** among everyone seen so far — because total quality is the other factor and you are minimising it.
4. Maintain those with a **max-heap of size K**: push each quality, and when the heap exceeds $K$, pop the largest.
5. Once the heap holds exactly $K$, the candidate cost is `rate × sum_of_heap`. Keep the minimum over all positions.

```python
workers = sorted(range(n), key=lambda i: wage[i] / quality[i])
heap, qsum, best = [], 0, float("inf")
for idx in workers:
    heapq.heappush(heap, -quality[idx])      # max-heap via negation
    qsum += quality[idx]
    if len(heap) > k:
        qsum += heapq.heappop(heap)          # popped value is negative
    if len(heap) == k:
        best = min(best, (wage[idx] / quality[idx]) * qsum)
```

**Cost:** $O(n \log n)$ to sort, $O(n \log k)$ to sweep.

**Why it is correct:** every group has *some* member with the maximum ratio. Fixing that member fixes the rate, and the only remaining freedom is which $K-1$ others to take — for which you obviously want the smallest qualities available. Iterating over every possible rate-setter therefore considers every group that could be optimal.

The lab checks it against exhaustive search on **400 random instances — 400/400 agree** — and also measures how often the naive rule fails:

```
   Checking greedy against brute force on 400 random instances...
   agreed on 400/400

   And how often is 'take the k cheapest wages' wrong?
   wrong on 130/400 random instances
```

**Nearly a third.** Not an exotic corner case — the naive rule is simply wrong, often.

---

## 2. Interval scheduling: the sort key *is* the algorithm

> You have a list of meetings with start and end times. Fit in **as many non-overlapping meetings as possible.**

Three plausible sort keys. Only one is correct, and the lab runs all three:

```
   meetings (start, end): [(1, 3), (2, 5), (4, 7), (6, 8), (0, 10)]
   brute force optimum: 2 meetings [(1, 3), (4, 7)]

   sort key                      | picked | meetings
   earliest END time   (correct) |      2 | [(1, 3), (4, 7)]
   earliest START time (wrong)   |      1 | [(0, 10)]   <- SUBOPTIMAL
   shortest DURATION   (wrong)   |      2 | [(1, 3), (6, 8)]
```

**Earliest start** takes the meeting running from 0 to 10 and is then blocked for the whole day.

**Shortest duration** ties here, which is exactly how a wrong rule survives casual testing — so the lab runs a second input:

```
   meetings: [(0, 5), (4, 6), (5, 10)]   brute force optimum: 2 [(0, 5), (5, 10)]
   earliest END time   (correct) |      2 | [(0, 5), (5, 10)]
   earliest START time (wrong)   |      2 | [(0, 5), (5, 10)]
   shortest DURATION   (wrong)   |      1 | [(4, 6)]   <- SUBOPTIMAL
```

The short meeting in the middle blocks **both** long ones. **Each wrong key fails on some input and ties on others; only "earliest end" survives both.**

### The exchange argument

**Claim:** taking the earliest-finishing compatible meeting at each step is optimal.

**Proof sketch.** Let $g_1$ be the meeting the greedy picks first — the one that ends earliest overall. Take any optimal solution $O = \{o_1, o_2, \dots\}$, sorted by end time. By definition $g_1$ ends no later than $o_1$. So replacing $o_1$ with $g_1$ leaves every later meeting in $O$ still compatible — they all start after $o_1$ ends, which is at or after when $g_1$ ends. The modified set is still valid and **the same size**, so it is still optimal. Now recurse on what remains.

**In one sentence: finishing earliest leaves the most room for everything else, and nothing is lost by preferring it.** That is the whole intuition, and the formal version is just that sentence made careful.

Checked against brute force on **300 random inputs — 300/300**.

---

## 3. "Select the most" versus "cover them all"

> Same meetings. Now: **how many rooms do you need to hold all of them?**

This *sounds* like the same problem and is its opposite. Section 2 discards conflicting meetings; this one pays for them.

**The answer is the peak number of simultaneous meetings.** Sweep the timeline, $+1$ at every start, $-1$ at every end, and track the maximum:

```python
events = [(s, 1) for s, e in intervals] + [(e, -1) for s, e in intervals]
events.sort(key=lambda x: (x[0], x[1]))   # -1 before +1 at the same instant
cur = peak = 0
for _, delta in events:
    cur += delta
    peak = max(peak, cur)
```

**The `(x[0], x[1])` sort key is doing real work.** At an instant where one meeting ends and another begins, the end must be processed first — otherwise you book a second room for a meeting that could reuse the one just freed. Since $-1 < +1$, sorting by the delta as the tiebreak gets this right automatically.

```
   fewest rooms (sweep line) : 3
   peak overlap (brute force): 3
```

Checked on **300 random inputs — 300/300**.

**Recognising which question you are being asked is the actual skill here.** "Fit in the most", "use the fewest rooms", "remove the fewest meetings to eliminate conflicts" are three different problems over one input, and only the first two are greedy in the same way. (The third is section 2 in disguise: removing the fewest is keeping the most.)

---

## 4. The template

| Problem | Sort / order by | Then |
| :--- | :--- | :--- |
| Hire K workers | wage/quality **ratio** | max-heap of $k$ qualities |
| Most non-overlapping meetings | **end** time | take it if it starts after the last one ended |
| Fewest rooms | time, **ends before starts** | running count, track the peak |
| [[06-minimum-spanning-tree\|Minimum spanning tree]] | edge **weight** | [[10-union-find\|union-find]] (Kruskal's) |
| [[06-minimum-spanning-tree\|MST]], other form | **cheapest edge leaving the tree** | min-heap (Prim's) |
| Coin change $\{1,3,4\}$ | — *no key works* — | [[06-dynamic-programming/index\|dynamic programming]] |

**A greedy algorithm is almost always "sort by the right key, then sweep once".** The code is short and boring. The key is the insight, and the proof is what separates a guess from an algorithm.

**And the last row is the reason [[01-when-greedy-works|lesson 01]] exists.** The template is seductive: it *always* produces an answer, quickly, and the answer is often right. When no valid key exists, you get a confident wrong number rather than a failure.

---

## 5. Worked example — complete runnable lab

Save as `greedy_selection.py`. Standard library only. **Every greedy is checked against exhaustive search**, not merely demonstrated.

```python
"""Greedy selection and scheduling: when sorting by the right key IS the algorithm.

Run:  python3 greedy_selection.py
"""

import heapq
import itertools
import random


# ==================================================== HIRE K WORKERS
# Each worker has a quality and a minimum wage they will accept.
# Rules for any group you hire:
#   1. everyone is paid in proportion to their quality
#   2. everyone is paid at least their own minimum wage
# So if you pay rate r per unit of quality, you need r >= wage[i]/quality[i]
# for every hired worker -- meaning r is the MAXIMUM ratio in the group, and
#   total cost = (max ratio in group) x (sum of qualities in group)
# One expensive person raises the rate for everybody.

def cost_of_group(quality, wage, group):
    rate = max(wage[i] / quality[i] for i in group)
    return rate * sum(quality[i] for i in group)


def hire_brute(quality, wage, k):
    n = len(quality)
    best, best_group = float("inf"), None
    for group in itertools.combinations(range(n), k):
        c = cost_of_group(quality, wage, group)
        if c < best:
            best, best_group = c, group
    return best, best_group


def hire_greedy(quality, wage, k):
    """Sort by ratio; the current worker sets the rate, so keep the k
    cheapest-quality workers seen so far."""
    workers = sorted(range(len(quality)), key=lambda i: wage[i] / quality[i])
    heap, qsum = [], 0
    best, best_group = float("inf"), None
    for idx in workers:
        heapq.heappush(heap, -quality[idx])     # max-heap via negation
        qsum += quality[idx]
        if len(heap) > k:
            qsum += heapq.heappop(heap)         # popped value is negative
        if len(heap) == k:
            rate = wage[idx] / quality[idx]     # this worker has the largest ratio so far
            if rate * qsum < best:
                best = rate * qsum
                best_group = tuple(sorted(-q for q in heap))
    return best, best_group


def hire_naive_cheapest(quality, wage, k):
    """The obvious wrong answer: take the k lowest advertised wages."""
    order = sorted(range(len(quality)), key=lambda i: wage[i])[:k]
    return cost_of_group(quality, wage, order), tuple(sorted(order))


# ============================================== INTERVAL SCHEDULING
def max_non_overlapping(intervals, key):
    chosen, last_end = [], float("-inf")
    for s, e in sorted(intervals, key=key):
        if s >= last_end:
            chosen.append((s, e))
            last_end = e
    return chosen


def max_non_overlapping_brute(intervals):
    best = []
    for r in range(len(intervals), -1, -1):
        for combo in itertools.combinations(sorted(intervals), r):
            if all(a[1] <= b[0] for a, b in zip(combo, combo[1:])):
                return list(combo)
    return best


def min_rooms(intervals):
    """Sweep the timeline: +1 at every start, -1 at every end."""
    events = []
    for s, e in intervals:
        events.append((s, 1))
        events.append((e, -1))
    events.sort(key=lambda x: (x[0], x[1]))   # an end at time t frees the room before a start at t
    cur = peak = 0
    for _, delta in events:
        cur += delta
        peak = max(peak, cur)
    return peak


def min_rooms_brute(intervals):
    """Peak overlap, checked point by point at every start time."""
    peak = 0
    for s, _ in intervals:
        peak = max(peak, sum(1 for a, b in intervals if a <= s < b))
    return peak


def main():
    print("=" * 76)
    print("1. HIRE K WORKERS -- pay the least, and the obvious answer is wrong")
    print("=" * 76)
    quality = [10, 20, 5]
    wage = [70, 140, 60]
    names = "ABC"
    k = 2
    print("\n   person   quality   min wage   ratio (wage/quality)")
    for i, nm in enumerate(names):
        print(f"     {nm}        {quality[i]:>3}       {wage[i]:>3}       "
              f"{wage[i]/quality[i]:>5.2f}")
    print(f"\n   Hire K = {k}.")
    print("   Rule: everyone in the group is paid the SAME rate per unit of quality,")
    print("         and nobody may be paid below their own minimum. So the rate is")
    print("         the LARGEST ratio in the group, and it applies to everyone.")

    nv, ng = hire_naive_cheapest(quality, wage, k)
    print(f"\n   'Take the two cheapest advertised wages' -> {[names[i] for i in ng]}")
    print(f"     A wants 70 and C wants 60, so it looks like 130.")
    print(f"     But C's ratio is 12.00, which becomes everyone's rate:")
    print(f"     total = 12.00 x (10 + 5) = {nv:.2f}")

    bv, bg = hire_brute(quality, wage, k)
    gv, _ = hire_greedy(quality, wage, k)
    print(f"\n   every group of {k}, by brute force:")
    for group in itertools.combinations(range(3), k):
        rate = max(wage[i] / quality[i] for i in group)
        qs = sum(quality[i] for i in group)
        print(f"     {[names[i] for i in group]}  rate {rate:>5.2f} x quality {qs:>3}"
              f"  = {cost_of_group(quality, wage, group):>7.2f}")
    print(f"\n   optimal: {[names[i] for i in bg]} at {bv:.2f}")
    print(f"   greedy  : {gv:.2f}   agrees: {abs(gv - bv) < 1e-9}")

    print("\n   The greedy: sort by RATIO ascending. Walking the list, the current")
    print("   worker has the largest ratio so far, so they set the rate -- and you")
    print("   want the k SMALLEST qualities among everyone seen so far, which a")
    print("   max-heap of size k maintains in O(log k) per step.")

    print("\n   Checking greedy against brute force on 400 random instances...")
    bad = 0
    for t in range(400):
        random.seed(t)
        n = random.randint(1, 9)
        q = [random.randint(1, 20) for _ in range(n)]
        w = [random.randint(1, 60) for _ in range(n)]
        kk = random.randint(1, n)
        if abs(hire_greedy(q, w, kk)[0] - hire_brute(q, w, kk)[0]) > 1e-9:
            bad += 1
    print(f"   agreed on {400 - bad}/400")

    print("\n   And how often is 'take the k cheapest wages' wrong?")
    wrong = 0
    for t in range(400):
        random.seed(t)
        n = random.randint(2, 9)
        q = [random.randint(1, 20) for _ in range(n)]
        w = [random.randint(1, 60) for _ in range(n)]
        kk = random.randint(1, n)
        if abs(hire_naive_cheapest(q, w, kk)[0] - hire_brute(q, w, kk)[0]) > 1e-9:
            wrong += 1
    print(f"   wrong on {wrong}/400 random instances")

    print("\n" + "=" * 76)
    print("2. INTERVAL SCHEDULING -- the sort key IS the algorithm")
    print("=" * 76)
    meetings = [(1, 3), (2, 5), (4, 7), (6, 8), (0, 10)]
    print(f"\n   meetings (start, end): {meetings}")
    print("   Goal: fit in as many non-overlapping meetings as possible.")

    strategies = [
        ("earliest END time   (correct)", lambda x: x[1]),
        ("earliest START time (wrong)", lambda x: x[0]),
        ("shortest DURATION   (wrong)", lambda x: x[1] - x[0]),
    ]
    truth = max_non_overlapping_brute(meetings)
    print(f"\n   brute force optimum: {len(truth)} meetings {truth}")
    print("\n   sort key                      | picked | meetings")
    for label, key in strategies:
        got = max_non_overlapping(meetings, key)
        mark = "" if len(got) == len(truth) else "   <- SUBOPTIMAL"
        print(f"   {label:<29} | {len(got):>6} | {got}{mark}")
    print("\n   'shortest duration' happens to tie here. It does not on this one:")
    trap = [(0, 5), (4, 6), (5, 10)]
    truth2 = max_non_overlapping_brute(trap)
    print(f"   meetings: {trap}   brute force optimum: {len(truth2)} {truth2}")
    for label, key in strategies:
        got = max_non_overlapping(trap, key)
        mark = "" if len(got) == len(truth2) else "   <- SUBOPTIMAL"
        print(f"   {label:<29} | {len(got):>6} | {got}{mark}")
    print("   -> the short meeting in the middle blocks BOTH long ones. Duration")
    print("      is not the right key; only the END time is.")

    print("\n   -> sorting by end time works because finishing earliest leaves the")
    print("      most room for everything after it. That is the exchange argument:")
    print("      swap any optimal solution's first meeting for the earliest-ending")
    print("      one and it is still valid, and still the same size.")

    print("\n   Checking 'earliest end' against brute force on 300 random inputs...")
    bad = 0
    for t in range(300):
        random.seed(t + 77)
        iv = []
        for _ in range(random.randint(0, 8)):
            s = random.randint(0, 15)
            iv.append((s, s + random.randint(1, 6)))
        if len(max_non_overlapping(iv, lambda x: x[1])) != len(max_non_overlapping_brute(iv)):
            bad += 1
    print(f"   agreed on {300 - bad}/300")

    print("\n" + "=" * 76)
    print("3. A DIFFERENT QUESTION ABOUT THE SAME MEETINGS")
    print("=" * 76)
    print(f"\n   meetings: {meetings}")
    print("   'How many rooms do I need to hold ALL of them?' is not the same")
    print("   question, and it is not solved by the same greedy.")
    print(f"\n   fewest rooms (sweep line) : {min_rooms(meetings)}")
    print(f"   peak overlap (brute force): {min_rooms_brute(meetings)}")
    print("   -> the answer is the PEAK number of simultaneous meetings. Sweep the")
    print("      timeline, +1 at each start and -1 at each end, and track the max.")
    print("   -> 'select the most' and 'cover them all' are opposite problems:")
    print("      one discards conflicts, the other pays for them.")

    print("\n   Checking the sweep against brute force on 300 random inputs...")
    bad = 0
    for t in range(300):
        random.seed(t + 500)
        iv = []
        for _ in range(random.randint(1, 9)):
            s = random.randint(0, 15)
            iv.append((s, s + random.randint(1, 6)))
        if min_rooms(iv) != min_rooms_brute(iv):
            bad += 1
    print(f"   agreed on {300 - bad}/300")

    print("\n" + "=" * 76)
    print("4. THE SHAPE OF EVERY GREEDY IN THIS LESSON")
    print("=" * 76)
    print("""
   problem                  | sort / order by        | then
   -------------------------|------------------------|---------------------------
   hire k workers           | wage/quality RATIO     | max-heap of k qualities
   most non-overlapping     | END time               | take if it starts after
   fewest rooms             | time, ends before starts| running count, track peak
   minimum spanning tree    | edge weight            | union-find (Kruskal)
   coin change {1,3,4}      | -- no order works --   | use dynamic programming

   -> a greedy algorithm is almost always 'sort by the right key, then sweep'.
      Finding the key is the whole problem, and PROVING it is the other half.
   -> the proof is nearly always an EXCHANGE ARGUMENT: take any optimal
      solution, show you can swap in the greedy's first choice without making
      it worse, and induct.""")


if __name__ == "__main__":
    main()
```

### Expected output

Generated by running the file above:

```
============================================================================
1. HIRE K WORKERS -- pay the least, and the obvious answer is wrong
============================================================================

   person   quality   min wage   ratio (wage/quality)
     A         10        70        7.00
     B         20       140        7.00
     C          5        60       12.00

   Hire K = 2.
   Rule: everyone in the group is paid the SAME rate per unit of quality,
         and nobody may be paid below their own minimum. So the rate is
         the LARGEST ratio in the group, and it applies to everyone.

   'Take the two cheapest advertised wages' -> ['A', 'C']
     A wants 70 and C wants 60, so it looks like 130.
     But C's ratio is 12.00, which becomes everyone's rate:
     total = 12.00 x (10 + 5) = 180.00

   every group of 2, by brute force:
     ['A', 'B']  rate  7.00 x quality  30  =  210.00
     ['A', 'C']  rate 12.00 x quality  15  =  180.00
     ['B', 'C']  rate 12.00 x quality  25  =  300.00

   optimal: ['A', 'C'] at 180.00
   greedy  : 180.00   agrees: True

   The greedy: sort by RATIO ascending. Walking the list, the current
   worker has the largest ratio so far, so they set the rate -- and you
   want the k SMALLEST qualities among everyone seen so far, which a
   max-heap of size k maintains in O(log k) per step.

   Checking greedy against brute force on 400 random instances...
   agreed on 400/400

   And how often is 'take the k cheapest wages' wrong?
   wrong on 130/400 random instances

============================================================================
2. INTERVAL SCHEDULING -- the sort key IS the algorithm
============================================================================

   meetings (start, end): [(1, 3), (2, 5), (4, 7), (6, 8), (0, 10)]
   Goal: fit in as many non-overlapping meetings as possible.

   brute force optimum: 2 meetings [(1, 3), (4, 7)]

   sort key                      | picked | meetings
   earliest END time   (correct) |      2 | [(1, 3), (4, 7)]
   earliest START time (wrong)   |      1 | [(0, 10)]   <- SUBOPTIMAL
   shortest DURATION   (wrong)   |      2 | [(1, 3), (6, 8)]

   'shortest duration' happens to tie here. It does not on this one:
   meetings: [(0, 5), (4, 6), (5, 10)]   brute force optimum: 2 [(0, 5), (5, 10)]
   earliest END time   (correct) |      2 | [(0, 5), (5, 10)]
   earliest START time (wrong)   |      2 | [(0, 5), (5, 10)]
   shortest DURATION   (wrong)   |      1 | [(4, 6)]   <- SUBOPTIMAL
   -> the short meeting in the middle blocks BOTH long ones. Duration
      is not the right key; only the END time is.

   -> sorting by end time works because finishing earliest leaves the
      most room for everything after it. That is the exchange argument:
      swap any optimal solution's first meeting for the earliest-ending
      one and it is still valid, and still the same size.

   Checking 'earliest end' against brute force on 300 random inputs...
   agreed on 300/300

============================================================================
3. A DIFFERENT QUESTION ABOUT THE SAME MEETINGS
============================================================================

   meetings: [(1, 3), (2, 5), (4, 7), (6, 8), (0, 10)]
   'How many rooms do I need to hold ALL of them?' is not the same
   question, and it is not solved by the same greedy.

   fewest rooms (sweep line) : 3
   peak overlap (brute force): 3
   -> the answer is the PEAK number of simultaneous meetings. Sweep the
      timeline, +1 at each start and -1 at each end, and track the max.
   -> 'select the most' and 'cover them all' are opposite problems:
      one discards conflicts, the other pays for them.

   Checking the sweep against brute force on 300 random inputs...
   agreed on 300/300

============================================================================
4. THE SHAPE OF EVERY GREEDY IN THIS LESSON
============================================================================

   problem                  | sort / order by        | then
   -------------------------|------------------------|---------------------------
   hire k workers           | wage/quality RATIO     | max-heap of k qualities
   most non-overlapping     | END time               | take if it starts after
   fewest rooms             | time, ends before starts| running count, track peak
   minimum spanning tree    | edge weight            | union-find (Kruskal)
   coin change {1,3,4}      | -- no order works --   | use dynamic programming

   -> a greedy algorithm is almost always 'sort by the right key, then sweep'.
      Finding the key is the whole problem, and PROVING it is the other half.
   -> the proof is nearly always an EXCHANGE ARGUMENT: take any optimal
      solution, show you can swap in the greedy's first choice without making
      it worse, and induct.
```

---

## 6. Common pitfalls and traps

1. **Assuming a group's cost is the sum of its members' costs.** In the hiring problem it is a *product*: worst rate × total quality. Any problem where one member's constraint applies to the whole group has this shape — and the naive per-member sum is wrong on ~⅓ of random instances.
2. **Sorting by the wrong key and testing on one input.** Shortest-duration ties with the correct answer on the lab's first example and fails on the second. **One passing example is not evidence.**
3. **Using a min-heap where you need a max-heap.** Python's `heapq` is a min-heap; negate to invert. In the hiring sweep you are discarding the *largest* qualities, so the heap must surrender its maximum.
4. **Processing starts before ends at the same instant.** A meeting ending at 10 and another starting at 10 need one room, not two. Sort the events so $-1$ precedes $+1$.
5. **Confusing "select the most" with "cover them all".** Opposite problems over the same input, with different algorithms and different answers.
6. **Not proving it.** A greedy that passes your tests and has no exchange argument is a guess. If you cannot write the argument, use [[06-dynamic-programming/index|dynamic programming]] — slower and correct beats fast and wrong.
7. **Forgetting floating-point comparison on ratios.** Two candidates with equal ratios can compare unequal after division. Compare $w_i q_j$ against $w_j q_i$ to stay in integers where it matters.
8. **Assuming greedy generalises.** Hire-K is greedy; the *assignment problem* — one person per job, each pair with its own cost — looks similar and greedy is wrong for it. That one needs the Hungarian algorithm or min-cost max-flow.

---

## 7. Check your understanding

1. **Why is "take the K lowest wages" wrong?**
   <details><summary>Answer</summary>Because the wage a person accepts is not the wage they will be <i>paid</i>. Everyone in the group is paid at the group's worst ratio, so a candidate with a low absolute wage but poor quality (C: 60 for only 5 quality, a rate of 12.00) drags the whole group's rate up. Cost is <b>worst rate × total quality</b>, not a sum of advertised wages. The lab measures the naive rule failing on 130 of 400 random instances.</details>

2. **The greedy sorts by ratio ascending and keeps a max-heap of qualities. What is the heap for?**
   <details><summary>Answer</summary>To hold the $K$ <i>smallest</i> qualities seen so far. Once the current worker fixes the rate, the only remaining freedom is which others to take, and you want minimum total quality. A max-heap of size $K$ maintains exactly that set: push each new quality, and when the size exceeds $K$, evict the largest. It costs $O(\log k)$ per step rather than re-sorting.</details>

3. **Prove or disprove: sorting meetings by shortest duration maximises how many you fit in.**
   <details><summary>Answer</summary>Disproved by <code>[(0,5), (4,6), (5,10)]</code>. Shortest duration picks <code>(4,6)</code> — length 2 — which overlaps both others, giving 1 meeting. The optimum is <code>(0,5)</code> and <code>(5,10)</code>, giving 2. A short meeting positioned across a boundary can block two long compatible ones. Only earliest-end has an exchange argument.</details>

4. **You are asked for the fewest rooms. Can you reuse the earliest-end greedy?**
   <details><summary>Answer</summary>No — different question. Earliest-end <i>selects</i> a maximum compatible subset and discards the rest; here you must accommodate everything. The answer is the peak simultaneous overlap, found with a sweep: $+1$ at each start, $-1$ at each end, track the maximum. Watch the tie at a shared instant — the end must be processed first, or you book a room that was about to be freed.</details>

5. **When should you stop looking for a greedy and write a DP?**
   <details><summary>Answer</summary>When you cannot state the exchange argument. Concretely: if you cannot finish "taking the greedy choice first never makes the solution worse, because…", you do not have a proof, and the template will still hand you a plausible wrong number. Coin change with $\{1,3,4\}$ is the standing example — no sort key works, and the failure is silent.</details>

---

## 8. Practice — independent task

**Part 1 — hire K workers.** Implement the greedy and a brute force. Verify on 500 random instances. Then: **return the actual people hired**, not just the cost, and assert the returned group really does cost what you reported.

**Part 2 — where does the naive rule fail?** Instrument "take the K cheapest wages" and characterise the instances where it loses. Does the failure rate depend on $K$? On the spread of qualities? **Produce a plot or a table, and state the pattern in one sentence.**

**Part 3 — the scheduling family.** Implement, each verified against brute force on 300 inputs:
   1. Maximum non-overlapping meetings.
   2. Fewest rooms.
   3. Minimum meetings to *remove* so none overlap. **Predict its relationship to (1) before coding.**
   4. Maximum **weighted** non-overlapping meetings, where each has a value. **This one is not greedy** — work out why the earliest-end argument collapses, then write the DP.

**Part 4 — exchange arguments in writing.** For each greedy in part 3 that *is* greedy, write the argument out properly: take an optimal solution, swap in the greedy's first choice, show it is still valid and no smaller.

**Part 5 — the one that is not greedy.** Implement the assignment problem (N people, N jobs, a cost per pair) with (a) a greedy that repeatedly takes the cheapest remaining cell and (b) brute force over all permutations. **Find the smallest instance where greedy loses**, and report by how much.

**Edge cases:** $K$ equal to the pool size; $K = 1$; candidates with identical ratios; zero-length meetings; meetings that touch exactly at an endpoint; an empty input.

**Done when:** parts 1 and 3 agree with brute force on every instance; part 2 states the pattern; part 4 has four written arguments; and part 5 names a concrete instance with the gap measured.

Then find them worked: [[133-meeting-rooms|Meeting Rooms]], [[134-meeting-rooms-ii|Meeting Rooms II]], [[132-non-overlapping-intervals|Non-overlapping Intervals]], [[068-task-scheduler|Task Scheduler]], [[126-hand-of-straights|Hand of Straights]].

---

## Before moving on

You can solve hire-K-workers and explain why the cheapest candidates are often wrong; apply sort-then-sweep and name the key each classic needs; tell "select the most" from "cover them all"; and prove a greedy with an exchange argument.

**Recap:** the greedy selection family is nearly always **sort by one key, then sweep once** — the code is short and the key is the insight. **Hire K workers** is the trap: a group's cost is not a sum but a product, $(\max \text{ratio}) \times (\sum \text{quality})$, so one bad rate is charged to everybody. Sort by ratio, let each worker in turn set the rate, and keep the $K$ smallest qualities in a max-heap — $O(n\log n)$, and verified 400/400 against brute force, while "take the K cheapest wages" is wrong on 130/400. **Interval scheduling** needs the **end** time; earliest-start and shortest-duration each fail on some input and tie on others, which is how wrong keys survive testing. The **exchange argument** is the proof: finishing earliest leaves the most room, so swapping it into any optimal solution keeps it valid and the same size. **Fewest rooms is the opposite question** — peak overlap via a sweep, with ends processed before starts at a shared instant. And when no key admits an exchange argument, stop: that is [[06-dynamic-programming/index|dynamic programming]]'s job, and greedy will return a confident wrong number instead of failing.

---

## Related

- [[01-when-greedy-works|When Greedy Works]] — the previous lesson: the coin-change trap and the conditions
- [[06-dynamic-programming/index|Dynamic Programming]] — what to use when no greedy key exists
- [[08-heaps|Heaps]] — the max-heap-of-size-K trick, and why `heapq` needs negation
- [[06-minimum-spanning-tree|Minimum Spanning Tree]] — the same template on a graph
- [[08-overlapping-intervals|Overlapping intervals pattern]] — the recognition layer for the scheduling half
- [[07-top-k-elements|Top-K pattern]] — the heap-of-size-K idea in general
- [[10-greedy-algorithms/index|the greedy folder]]
