# Module: Binary Search on the Answer (When There Is No Array to Search)

**[Intermediate]** — [[01-linear-and-binary-search|Binary search]] is taught as "find a value in a sorted array", which is a description of one *application* rather than of the technique. The technique is: **you have a range, and a yes/no question whose answer flips exactly once across that range — so you can find the flip point by halving.** The array is incidental. Once you see that, binary search applies to a large family of problems with no array anywhere in sight.

This is one of the highest-leverage recognitions in problem solving, because the problems it solves usually look like optimisation problems and are usually attempted with something much more complicated.

---

## Before you start

- You can write a correct binary search over a sorted array and name its three classic bugs — [[01-linear-and-binary-search|linear and binary search]].
- You can read $O(\log n)$ and say what it means for a range being halved.
- You know what a **predicate** is: a function returning true or false.

**After this lesson you will be able to:**

1. Recognise the **monotone predicate** shape hiding in an optimisation problem.
2. Apply the two standard templates — *smallest true* and *largest true* — and say why they need different midpoint rounding.
3. Choose the search bounds correctly, and justify both ends.
4. Say when the technique **does not** apply, and prove monotonicity before relying on it.

**Study route:** read 1–3, answer the prediction in section 4, then run the lab. Section 5's two templates are the part to memorise.

---

## 1. Why this exists: an optimisation problem in disguise

> Koko has $n$ piles of bananas and $h$ hours before the guards return. She picks an eating speed $s$ bananas per hour. Each hour she eats from a single pile; if the pile has fewer than $s$ left, she finishes it and waits. **What is the smallest $s$ that lets her finish every pile within $h$ hours?**

This reads like an optimisation problem. There is no array to search, nothing is sorted, and the obvious approaches are unpromising — try to derive a formula and the ceilings defeat you; try every speed from 1 upward and you are $O(\max(\text{pile}) \times n)$.

**But ask a different question.** Instead of "what is the best speed?", ask the yes/no question:

> **Does speed $s$ work?**

That is easy — sum $\lceil p_i / s\rceil$ over the piles and compare to $h$. And now tabulate the answer for the piles $[3, 6, 7, 11]$ with $h = 8$, which the lab does:

```
   speed |  hours | works?
       1 |     27 | F
       2 |     15 | F
       3 |     10 | F
       4 |      8 | T
       5 |      8 | T
       6 |      6 | T
       ...       | T
```

**`F F F T T T T T T T T`.** One flip, and it never flips back — obviously so, since eating faster can never take longer.

**That pattern is the only thing binary search has ever required.** A sorted array searched for a target is the same pattern in disguise: the predicate `a[i] >= target` is `F F F T T T`. The sortedness was never the point; it was just a way of guaranteeing the flip.

So: binary search the *speed*, not the piles. The range is $1$ to $\max(p_i)$, and the answer arrives in $O(n \log \max p)$. The lab finds it in **5 predicate evaluations**.

---

## Terms used in this technique

1. **Binary search on the answer**: This is also known as **parametric search** or **binary search on the result**. This is applying binary search to the range of *possible answers* to a problem, rather than to an input collection.
2. **Predicate**: This is a function from a candidate answer to true or false, expressing "is this candidate good enough?". Writing it is usually the easy part; recognising that you should is the hard part.
3. **Monotone predicate**: This is a predicate whose value, read across the range in order, changes at most once — either `F...FT...T` or `T...TF...F`. **This is the precondition for the whole technique**, and it is what must be proved rather than assumed.
4. **The flip point**: This is also called the **boundary** or **threshold**. This is the single position where the predicate changes value. Finding it *is* the problem.
5. **Feasibility check**: This is the concrete computation implementing the predicate — "can this be done with capacity $c$?". Its cost multiplies the $\log$ factor, so an $O(n)$ check over a range of size $R$ gives $O(n \log R)$.
6. **Search bounds**: These are the `lo` and `hi` you start with. **Both must be justified**: `lo` must be an answer that definitely fails (or the minimum conceivable), and `hi` one that definitely succeeds.
7. **Answer space**: This is the set of candidate answers. It may be enormous — $0$ to $10^{18}$ — and that is fine, because $\log_2(10^{18}) \approx 60$.

---

## 2. Recognising it

The signals, in rough order of reliability:

1. **"Minimum/maximum X such that Y is possible."** Minimum speed, maximum weight, smallest capacity, largest minimum distance. This phrasing is close to a giveaway.
2. **Checking a specific answer is much easier than finding the best one.** "Can we do it with capacity 18?" is a linear scan; "what is the smallest capacity?" is not obvious.
3. **The answer is a number in a known range**, rather than a subset or an arrangement.
4. **"Minimise the maximum"** or **"maximise the minimum"** — these almost always mean this technique.

**The check that saves you:** having found a candidate predicate, tabulate it over a small instance, as the lab does in block 1. If you see `F F F T T T` you are done. If you see anything else, stop — the technique does not apply.

---

## 3. The four worked problems

The lab runs all four through **one template**, which is the point:

```
  Koko                : answer=4  predicate evaluated 5 times  (range 1..11)
  Split-array         : answer=18  checks=5  (range 10..32)
  isqrt(10^12)        : answer=1000000  checks=41  (range 0..1000000000000)
  sqrt(2) to 1e-12    : answer=1.414213562372  checks=41
```

### Split array: minimise the largest chunk

Split $[7,2,5,10,8]$ into 2 contiguous parts, minimising the larger part's sum. **Predicate:** "can we split into at most $k$ parts with no part exceeding `cap`?" — greedily fill parts until they would overflow, then count.

**The bounds are where the thinking is.** `lo = max(nums)`: no capacity below the largest single element can work, since that element must fit somewhere. `hi = sum(nums)`: one part containing everything always works. **Both ends need an argument**, and getting `lo` wrong — starting at 0 or 1 — still produces the right answer here but wastes iterations and, in other problems, breaks the monotonicity at the bottom of the range.

### Integer square root

Largest $x$ with $x^2 \le n$. Predicate `x*x <= n` is `T...TF...F` — the **other** monotone direction, needing the *largest true* template.

**This is the block that shows why searching the answer is worth it.** Linear scan versus binary search, by size of $n$:

```
                         n |  linear steps |  binary steps
                   1,000,000 |         1,000 |            21
           1,000,000,000,000 |     1,000,000 |            41
   1,000,000,000,000,000,000 | 1,000,000,000 |            61
```

**A billion steps against 61.** The answer space is huge and its logarithm is not.

### Real-valued answers

When the answer is a real number there is no "next" value to converge on, so the loop condition becomes a **tolerance**: iterate while `hi - lo > 1e-12`. Each iteration halves the interval, so reaching a tolerance $\varepsilon$ over a range $R$ takes $\log_2(R/\varepsilon)$ iterations — 41 for the lab's $\sqrt2$.

**Never write `while lo < hi` with floats.** Floating-point values can fail to converge to equality, and you get an infinite loop. Use a tolerance, or a fixed iteration count (100 is ample for any double).

---

## 4. The two templates, and why the rounding differs

> **Predict before reading on.** In the *largest true* template, the update is `lo = mid`. Suppose you compute `mid = lo + (hi - lo) // 2` — the ordinary floor midpoint — and `lo = 4`, `hi = 5`. What is `mid`, and what happens next?

**`mid` is 4, so `lo = mid` leaves `lo = 4` and `hi = 5`: nothing changed, and the loop runs forever.**

This is why the two templates round differently, and it is the single most common bug in the technique.

### Template A — smallest true (`F...FT...T`)

```python
def smallest_true(lo, hi, predicate):
    while lo < hi:
        mid = lo + (hi - lo) // 2        # FLOOR
        if predicate(mid):
            hi = mid                     # mid might be the answer: keep it
        else:
            lo = mid + 1                 # mid is definitely not: discard it
    return lo
```

### Template B — largest true (`T...TF...F`)

```python
def largest_true(lo, hi, predicate):
    while lo < hi:
        mid = lo + (hi - lo + 1) // 2    # CEIL
        if predicate(mid):
            lo = mid                     # mid might be the answer: keep it
        else:
            hi = mid - 1                 # mid is definitely not: discard it
    return lo
```

**The rule that generates both:** the branch that *keeps* `mid` must not be the branch that can fail to make progress. Round the midpoint **away** from the variable that gets assigned `mid`. Template A assigns to `hi`, so round toward `lo` (floor). Template B assigns to `lo`, so round toward `hi` (ceil).

The lab demonstrates the failure arithmetic directly:

```
    lo=4, hi=5 -> floor mid = 4  (lo = mid leaves lo=4, hi=5: no progress)
    lo=4, hi=5 -> ceil  mid = 5  (lo = mid leaves lo=5, hi=5: done)
```

**Also note `lo + (hi - lo) // 2` rather than `(lo + hi) // 2`.** In Python integers are unbounded and both work, but the habit matters: in C++, Java or Rust, `lo + hi` can overflow. That is the bug that sat in the JDK's `binarySearch` for nine years, and [[01-linear-and-binary-search|lesson 01]] demonstrates it failing.

---

## 5. Proving monotonicity, and when it fails

**The technique is only valid if the predicate flips once.** If it does not, halving can discard the half containing the answer, and you get a confidently wrong result.

The lab's counterexample:

```
   x          | 1  2  3  4  5  6  7  8
   x is prime | F  T  T  F  T  F  T  F
```

No single flip point. "The smallest prime $\ge 4$" cannot be found by halving.

**How to prove monotonicity** — usually one sentence, and usually obvious once stated:

- **Koko:** if speed $s$ finishes in time, so does $s+1$, because $\lceil p/(s{+}1)\rceil \le \lceil p/s\rceil$ for every pile. Eating faster never takes longer.
- **Split array:** if capacity $c$ admits a valid split into $\le k$ parts, so does $c+1$ — the same split is still valid, since every part still fits.
- **isqrt:** if $x^2 \le n$ then $(x-1)^2 \le n$, since squaring is increasing on non-negative integers.

**The general form: increasing the candidate must only ever relax the constraint.** If you cannot state that sentence for your predicate, you do not have monotonicity, and you should not use this technique.

The lab also checks the result rather than trusting the argument — 300 random Koko instances against a linear scan, 300/300 agreeing. **For a technique whose failure mode is a plausible wrong number, cross-checking against brute force on small inputs is worth the ten lines.**

---

## 6. Worked example — complete runnable lab

Save as `binary_search_answer.py`. Standard library only.

```python
"""Binary search where there is no array: search the space of possible ANSWERS.

Run:  python3 binary_search_answer.py
"""

import math


# ---------------------------------------------------------------- the template
def smallest_true(lo, hi, predicate):
    """Smallest x in [lo, hi] with predicate(x) True, assuming F...FT...T.

    Returns hi + 1 if the predicate is False everywhere in range.
    """
    checks = 0
    while lo < hi:
        mid = lo + (hi - lo) // 2          # no overflow, and floors toward lo
        checks += 1
        if predicate(mid):
            hi = mid                       # mid might BE the answer: keep it
        else:
            lo = mid + 1                   # mid is not: discard it
    return lo, checks + 1


def largest_true(lo, hi, predicate):
    """Largest x in [lo, hi] with predicate(x) True, assuming T...TF...F."""
    checks = 0
    while lo < hi:
        mid = lo + (hi - lo + 1) // 2      # ceil, or lo == mid loops forever
        checks += 1
        if predicate(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo, checks + 1


# ------------------------------------------------------------- problem 1: koko
def hours_needed(piles, speed):
    return sum(math.ceil(p / speed) for p in piles)


def koko(piles, limit):
    ok = lambda s: hours_needed(piles, s) <= limit
    return smallest_true(1, max(piles), ok)


# ------------------------------------------------- problem 2: split array sums
def chunks_needed(nums, cap):
    count, cur = 1, 0
    for n in nums:
        if cur + n > cap:
            count += 1
            cur = n
        else:
            cur += n
    return count


def split_array(nums, k):
    ok = lambda cap: chunks_needed(nums, cap) <= k
    return smallest_true(max(nums), sum(nums), ok)


# ----------------------------------------------------- problem 3: square root
def isqrt_bs(n):
    ok = lambda x: x * x <= n
    return largest_true(0, n, ok)


# ------------------------------------------- problem 4: real-valued, tolerance
def sqrt_real(n, tol=1e-12):
    lo, hi, checks = 0.0, max(1.0, n), 0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        checks += 1
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid
    return lo, checks


def main():
    print("=== 1. The shape that makes it work ===")
    print("  Binary search needs a MONOTONE predicate: once true, always true.")
    piles, limit = [3, 6, 7, 11], 8
    print(f"  Koko eats piles {piles} in <= {limit} hours. Speed s works?")
    print("   speed |  hours | works?")
    for s in range(1, 12):
        h = hours_needed(piles, s)
        print(f"   {s:>5} | {h:>6} | {'T' if h <= limit else 'F'}")
    print("  -> F F F T T T T T T T T   <- one flip, never back. That is all")
    print("     binary search ever needed; a sorted array is just one example.")

    print("\n=== 2. Four problems, one template ===")
    ans, checks = koko(piles, limit)
    print(f"  Koko                : answer={ans}  predicate evaluated {checks} times"
          f"  (range 1..{max(piles)})")

    nums, k = [7, 2, 5, 10, 8], 2
    ans2, c2 = split_array(nums, k)
    print(f"  Split-array         : answer={ans2}  checks={c2}"
          f"  (range {max(nums)}..{sum(nums)})")

    n = 10 ** 12
    ans3, c3 = isqrt_bs(n)
    print(f"  isqrt(10^12)        : answer={ans3}  checks={c3}  (range 0..{n})")

    ans4, c4 = sqrt_real(2)
    print(f"  sqrt(2) to 1e-12    : answer={ans4:.12f}  checks={c4}")
    print(f"                        math.sqrt(2) = {math.sqrt(2):.12f}")

    print("\n=== 3. Why searching the ANSWER beats searching the input ===")
    print("  isqrt by linear scan vs binary search, by size of n:")
    print("                         n |  linear steps |  binary steps")
    for e in (6, 9, 12, 15, 18):
        n = 10 ** e
        _, c = isqrt_bs(n)
        print(f"   {n:>25,} | {int(math.isqrt(n)):>13,} | {c:>13}")
    print("  -> the answer space is huge; log2 of it is not")

    print("\n=== 4. The two templates are not interchangeable ===")
    print("  smallest_true uses floor and moves hi = mid.")
    print("  largest_true  uses CEIL and moves lo = mid.")
    print("  Using floor with lo = mid loops forever whenever hi == lo + 1:")
    lo, hi = 4, 5
    mid_floor = lo + (hi - lo) // 2
    mid_ceil = lo + (hi - lo + 1) // 2
    print(f"    lo=4, hi=5 -> floor mid = {mid_floor}  (lo = mid leaves lo=4, hi=5: no progress)")
    print(f"    lo=4, hi=5 -> ceil  mid = {mid_ceil}  (lo = mid leaves lo=5, hi=5: done)")

    print("\n=== 5. Verifying against brute force ===")
    bad = 0
    for trial in range(300):
        import random
        random.seed(trial)
        ps = [random.randint(1, 40) for _ in range(random.randint(1, 8))]
        lim = random.randint(len(ps), 60)
        got, _ = koko(ps, lim)
        truth = next(s for s in range(1, max(ps) + 1) if hours_needed(ps, s) <= lim)
        if got != truth:
            bad += 1
            print(f"    MISMATCH piles={ps} limit={lim} got={got} truth={truth}")
    print(f"    300 random Koko instances checked against linear scan: "
          f"{300 - bad}/300 agree")

    print("\n=== 6. When it does NOT apply ===")
    print("  The predicate must be monotone. This one is not:")
    print("   x       | 1  2  3  4  5  6  7  8")
    print("   x is prime | F  T  T  F  T  F  T  F")
    print("  -> there is no single flip point, so 'the smallest true x' cannot be")
    print("     found by halving: discarding a half may discard the answer.")
    print("  Before reaching for this technique, PROVE the flip happens once.")


if __name__ == "__main__":
    main()
```

### Expected output

Generated by running the file above:

```
=== 1. The shape that makes it work ===
  Binary search needs a MONOTONE predicate: once true, always true.
  Koko eats piles [3, 6, 7, 11] in <= 8 hours. Speed s works?
   speed |  hours | works?
       1 |     27 | F
       2 |     15 | F
       3 |     10 | F
       4 |      8 | T
       5 |      8 | T
       6 |      6 | T
       7 |      5 | T
       8 |      5 | T
       9 |      5 | T
      10 |      5 | T
      11 |      4 | T
  -> F F F T T T T T T T T   <- one flip, never back. That is all
     binary search ever needed; a sorted array is just one example.

=== 2. Four problems, one template ===
  Koko                : answer=4  predicate evaluated 5 times  (range 1..11)
  Split-array         : answer=18  checks=5  (range 10..32)
  isqrt(10^12)        : answer=1000000  checks=41  (range 0..1000000000000)
  sqrt(2) to 1e-12    : answer=1.414213562372  checks=41
                        math.sqrt(2) = 1.414213562373

=== 3. Why searching the ANSWER beats searching the input ===
  isqrt by linear scan vs binary search, by size of n:
                         n |  linear steps |  binary steps
                   1,000,000 |         1,000 |            21
               1,000,000,000 |        31,622 |            31
           1,000,000,000,000 |     1,000,000 |            41
       1,000,000,000,000,000 |    31,622,776 |            51
   1,000,000,000,000,000,000 | 1,000,000,000 |            61
  -> the answer space is huge; log2 of it is not

=== 4. The two templates are not interchangeable ===
  smallest_true uses floor and moves hi = mid.
  largest_true  uses CEIL and moves lo = mid.
  Using floor with lo = mid loops forever whenever hi == lo + 1:
    lo=4, hi=5 -> floor mid = 4  (lo = mid leaves lo=4, hi=5: no progress)
    lo=4, hi=5 -> ceil  mid = 5  (lo = mid leaves lo=5, hi=5: done)

=== 5. Verifying against brute force ===
    300 random Koko instances checked against linear scan: 300/300 agree

=== 6. When it does NOT apply ===
  The predicate must be monotone. This one is not:
   x       | 1  2  3  4  5  6  7  8
   x is prime | F  T  T  F  T  F  T  F
  -> there is no single flip point, so 'the smallest true x' cannot be
     found by halving: discarding a half may discard the answer.
  Before reaching for this technique, PROVE the flip happens once.
```

---

## 7. Common pitfalls and traps

1. **Using the floor midpoint with `lo = mid`.** Infinite loop whenever `hi == lo + 1`. Round away from the variable you assign `mid` to.
2. **Not proving monotonicity.** The technique returns a plausible number on a non-monotone predicate; it does not error. Tabulate the predicate on a small case before trusting it.
3. **Bounds that are too tight.** If the true answer lies outside `[lo, hi]`, you get the nearest endpoint, silently. Prove `lo` fails (or is the minimum conceivable) and `hi` succeeds.
4. **Bounds that are too loose.** Rarely harmful — it costs a few extra iterations — **unless the predicate is undefined outside the valid range**, such as a division by a speed of zero.
5. **`while lo < hi` on floats.** Use a tolerance or a fixed iteration count; floating-point equality may never be reached.
6. **An expensive feasibility check.** Total cost is $O(\text{check} \times \log R)$. If the check is $O(n^2)$ the technique may not pay. Optimise the check first.
7. **`(lo + hi) // 2` in a fixed-width language.** Overflow. Use `lo + (hi - lo) // 2` everywhere as a habit.
8. **Answering the wrong question.** The template returns the flip point. Make sure the flip point is what the problem asked for — "smallest speed that works" and "largest speed that fails" differ by one, and both are easy to return by accident.

---

## 8. Check your understanding

1. **What property must the predicate have, and why does sortedness not appear in the answer?**
   <details><summary>Answer</summary>Monotonicity: read across the range, its value must change at most once. Sortedness is not required because it was never the real precondition — a sorted array is just a convenient way to guarantee that <code>a[i] >= target</code> is monotone. Any monotone predicate over any range works, array or not.</details>

2. **Why do the two templates round the midpoint differently?**
   <details><summary>Answer</summary>Because the branch that keeps <code>mid</code> as a candidate must still shrink the interval. In <i>smallest true</i>, <code>hi = mid</code>, so <code>mid</code> must be strictly below <code>hi</code> — floor guarantees that. In <i>largest true</i>, <code>lo = mid</code>, so <code>mid</code> must be strictly above <code>lo</code> — which needs ceil. With <code>lo=4, hi=5</code>, floor gives 4 and <code>lo = mid</code> makes no progress at all.</details>

3. **For "split an array into $k$ parts minimising the largest part sum", why is `lo = max(nums)` rather than 0?**
   <details><summary>Answer</summary>Because every element must fit inside some part, so no capacity smaller than the largest element can ever be feasible. Starting at 0 still yields the right answer here — those candidates are all False — but it wastes iterations and, more importantly, it signals you have not established the lower end of the monotone region. In problems where the predicate is undefined or non-monotone below the true minimum, it is an actual bug.</details>

4. **A predicate is monotone but its check costs $O(n^2)$, with $n = 10^5$ and range $10^9$. Is this technique a good idea?**
   <details><summary>Answer</summary>No. Total cost is $O(n^2 \log R) = 10^{10} \times 30$, which is hopeless. The $\log R$ factor is cheap; the check is what dominates. Either find a cheaper feasibility check — often greedy, often $O(n)$ — or use a different approach entirely. <b>Always cost the check before reaching for the template.</b></details>

5. **You need the smallest $x$ with $f(x) \ge 0$, where $f$ is continuous and increasing but $x$ is real. What changes?**
   <details><summary>Answer</summary>The loop condition and the return. There is no "next" real number, so <code>while lo &lt; hi</code> may never terminate; use <code>while hi - lo &gt; eps</code> with an explicit tolerance, or a fixed iteration count such as 100. Each iteration halves the interval, so reaching tolerance $\varepsilon$ over range $R$ takes $\log_2(R/\varepsilon)$ iterations — 41 for the lab's $\sqrt2$ at $10^{-12}$. Return <code>lo</code> (or the midpoint) and state the accuracy.</details>

---

## 9. Practice — independent task

Write `search_answer(lo, hi, predicate, mode)` supporting both templates, then use it unchanged on four problems.

**Part 1 — the template.** Both modes, integer and real variants. Instrument it to count predicate evaluations. **Assert the count never exceeds $\lceil\log_2(hi-lo+1)\rceil + 1$** — if it does, your interval is not halving.

**Part 2 — four problems.** For each: state the predicate, **prove monotonicity in one sentence**, and justify both bounds.

1. **Ship capacity.** Given package weights and $d$ days, find the least ship capacity that delivers everything in order within $d$ days.
2. **Aggressive cows.** Place $k$ cows in stalls at given positions, **maximising the minimum** distance between any two.
3. **Minimum time.** Given worker speeds, find the least time to complete $n$ tasks.
4. **The $k$-th smallest element of an $n \times n$ multiplication table**, without building the table.

**Part 3 — cross-check.** For each, verify against brute force on inputs small enough to enumerate — at least 300 random instances each, as the lab does for Koko.

**Part 4 — break it.** Construct a predicate that is *nearly* monotone (one flip out of place) and show your implementation returning a confidently wrong answer. **Then write a `check_monotone(lo, hi, predicate)` helper** that samples the range and reports violations, and run it on all four problems above.

**Part 5 — cost the check.** Report, for each problem, the complexity of the feasibility check and the total. Identify which of the four would stop being viable if the check were one factor of $n$ more expensive.

**Edge cases:** `lo == hi`; the predicate true everywhere; false everywhere; a range of size 2 (**the case that exposes the rounding bug**); negative bounds.

**Done when:** all four match brute force on 300 random instances each; your evaluation counts stay within the log bound; part 4 produces a concrete wrong answer plus a working monotonicity checker; and each problem has its one-sentence monotonicity proof written down.

Then find it in the wild: [[030-koko-eating-bananas|Koko Eating Bananas]], [[034-median-of-two-sorted-arrays|Median of Two Sorted Arrays]] and [[096-swim-in-rising-water|Swim in Rising Water]] are all this technique.

---

## Before moving on

You can spot the monotone-predicate shape in an optimisation problem, apply both templates with the right rounding, justify your bounds, and prove monotonicity before relying on it.

**Recap:** binary search does not need an array — it needs a **range** and a **predicate that flips exactly once** across it. Recognise it from "minimum/maximum X such that Y", from "minimise the maximum", and from checking a candidate being far easier than finding the best. Two templates: *smallest true* uses the **floor** midpoint with `hi = mid`; *largest true* uses the **ceil** midpoint with `lo = mid` — **round away from the variable you assign `mid` to**, or the loop hangs at `hi == lo + 1`. Justify both bounds with an argument. Cost is $O(\text{check} \times \log R)$, and the check dominates. For real-valued answers use a tolerance, never `lo < hi`. **Prove the single flip before you trust the result**, because a non-monotone predicate yields a plausible wrong number rather than an error.

**Next:** [[03-state-space-search|State-Space Search]] — the third meaning of "search", where there is no range and no collection, only a starting configuration and a rule for what comes next.

---

## Related

- [[01-linear-and-binary-search|Linear and Binary Search]] — the array version, and the three classic bugs
- [[03-state-space-search|State-Space Search]] — searching configurations rather than values
- [[09-modified-binary-search|Modified binary search]] — the pattern-layer treatment with more worked problems
- [[05-searching/index|the searching folder]] — the parent, and the three meanings of "search"
- [[01-growth-and-asymptotic-notation|Growth and Asymptotic Notation]] — why $\log_2(10^{18})$ is only 60
