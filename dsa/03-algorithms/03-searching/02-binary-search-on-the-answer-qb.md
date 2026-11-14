# Binary Search on the Answer — Question Bank

Micro-questions over [[02-binary-search-on-the-answer|the parametric search module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The reframing

**1. State the Koko problem.**

<details><summary>Answer</summary>

$n$ piles of bananas, $h$ hours. She picks a speed $s$; each hour she eats from one pile, finishing early if it has fewer than $s$ left. **What is the smallest $s$ that finishes every pile within $h$ hours?**

</details>

**2. Why do the obvious approaches fail?**

<details><summary>Answer</summary>

Deriving a formula is defeated by the ceilings; trying every speed from 1 upward is $O(\max(\text{pile}) \times n)$.

</details>

**3. What different question do you ask instead?**

<details><summary>Answer</summary>

**"Does speed $s$ work?"** — which is easy: sum $\lceil p_i/s \rceil$ and compare to $h$.

</details>

**4. What does tabulating that answer reveal?**

<details><summary>Answer</summary>

`F F F T T T T T…` — **one flip, and it never flips back**, obviously so since eating faster can never take longer.

</details>

**5. State the realisation about binary search itself.**

<details><summary>Answer</summary>

**That pattern is the only thing binary search has ever required.** A sorted array searched for a target is the same pattern in disguise — `a[i] >= target` is `F F F T T T`. **The sortedness was never the point; it was just a way of guaranteeing the flip.**

</details>

---

## B. The vocabulary

**6. What is binary search on the answer?**

<details><summary>Answer</summary>

Also parametric search — applying binary search to the range of **possible answers**, rather than to an input collection.

</details>

**7. What is a predicate here?**

<details><summary>Answer</summary>

A function from a candidate answer to true/false: "is this candidate good enough?". **Writing it is usually the easy part; recognising that you should is the hard part.**

</details>

**8. What is a monotone predicate, and what is its status?**

<details><summary>Answer</summary>

One whose value, read across the range in order, changes **at most once** — `F...FT...T` or `T...TF...F`. **It is the precondition for the whole technique, and it must be proved rather than assumed.**

</details>

**9. What is the flip point?**

<details><summary>Answer</summary>

The single position where the predicate changes value. **Finding it *is* the problem.**

</details>

**10. What determines the total cost?**

<details><summary>Answer</summary>

The feasibility check multiplied by the log: an $O(n)$ check over a range of size $R$ gives $O(n\log R)$.

</details>

**11. What must be true of `lo` and `hi`?**

<details><summary>Answer</summary>

**Both must be justified.** `lo` must definitely fail (or be the minimum conceivable), and `hi` must definitely succeed.

</details>

**12. Is a huge answer space a problem?**

<details><summary>Answer</summary>

No — $\log_2(10^{18}) \approx 60$.

</details>

---

## C. Recognising it

**13. Give the four signals in order of reliability.**

<details><summary>Answer</summary>

1. **"Minimum/maximum X such that Y is possible."** — close to a giveaway.
2. **Checking a specific answer is much easier than finding the best one.**
3. The answer is **a number in a known range**, not a subset or arrangement.
4. **"Minimise the maximum"** or **"maximise the minimum"**.

</details>

**14. What is the check that saves you?**

<details><summary>Answer</summary>

**Tabulate the predicate over a small instance.** If you see `F F F T T T` you are done. Anything else, stop — the technique does not apply.

</details>

---

## D. Worked problems

**15. Split array — what is the predicate?**

<details><summary>Answer</summary>

"Can we split into at most $k$ parts with no part exceeding `cap`?" — greedily fill parts until they would overflow, then count.

</details>

**16. Justify both bounds for split array.**

<details><summary>Answer</summary>

`lo = max(nums)`: no capacity below the largest single element can work, since that element must fit somewhere. `hi = sum(nums)`: one part containing everything always works.

</details>

**17. What happens if you set `lo` too low here?**

<details><summary>Answer</summary>

Here it still produces the right answer but wastes iterations — **and in other problems it breaks the monotonicity at the bottom of the range**.

</details>

**18. Integer square root — what is the predicate and which direction is it?**

<details><summary>Answer</summary>

`x*x <= n`, which is `T...TF...F` — **the other monotone direction**, needing the *largest true* template.

</details>

**19. Linear versus binary steps for isqrt at $n = 10^{18}$?**

<details><summary>Answer</summary>

**A billion steps against 61.** The answer space is huge and its logarithm is not.

</details>

**20. How does the loop change for a real-valued answer?**

<details><summary>Answer</summary>

There is no "next" value, so the condition becomes a **tolerance**: `while hi - lo > 1e-12`. Reaching tolerance $\varepsilon$ over range $R$ takes $\log_2(R/\varepsilon)$ iterations.

</details>

**21. Why must you never write `while lo < hi` with floats?**

<details><summary>Answer</summary>

**Floating-point values can fail to converge to equality**, giving an infinite loop. Use a tolerance or a fixed iteration count — 100 is ample for any double.

</details>

---

## E. The two templates

**22. In the largest-true template with `lo = mid`, `lo = 4`, `hi = 5` and a floor midpoint — what happens?**

<details><summary>Answer</summary>

`mid` is 4, so `lo = mid` leaves `lo = 4, hi = 5`: **nothing changed, and the loop runs forever.**

</details>

**23. Write Template A (smallest true).**

<details><summary>Answer</summary>

```python
while lo < hi:
    mid = lo + (hi - lo) // 2        # FLOOR
    if predicate(mid): hi = mid      # might be the answer: keep it
    else:              lo = mid + 1  # definitely not: discard it
return lo
```

</details>

**24. Write Template B (largest true).**

<details><summary>Answer</summary>

```python
while lo < hi:
    mid = lo + (hi - lo + 1) // 2    # CEIL
    if predicate(mid): lo = mid      # might be the answer: keep it
    else:              hi = mid - 1  # definitely not: discard it
return lo
```

</details>

**25. State the rule that generates both.**

<details><summary>Answer</summary>

**The branch that *keeps* `mid` must not be the branch that can fail to make progress.** Round the midpoint **away** from the variable that gets assigned `mid` — A assigns to `hi` so round toward `lo` (floor); B assigns to `lo` so round toward `hi` (ceil).

</details>

**26. Why `lo + (hi - lo) // 2` even in Python?**

<details><summary>Answer</summary>

Habit. In C++, Java or Rust `lo + hi` can overflow — **the bug that sat in the JDK's `binarySearch` for nine years.**

</details>

---

## F. Monotonicity

**27. What goes wrong if the predicate does not flip exactly once?**

<details><summary>Answer</summary>

**Halving can discard the half containing the answer**, giving a confidently wrong result.

</details>

**28. Give the counterexample.**

<details><summary>Answer</summary>

"$x$ is prime" over $1..8$: `F T T F T F T F`. No single flip point — "the smallest prime $\ge 4$" cannot be found by halving.

</details>

**29. Prove monotonicity for Koko.**

<details><summary>Answer</summary>

If speed $s$ finishes in time, so does $s+1$, because $\lceil p/(s{+}1)\rceil \le \lceil p/s\rceil$ for every pile. **Eating faster never takes longer.**

</details>

**30. Prove it for split array.**

<details><summary>Answer</summary>

If capacity $c$ admits a valid split into $\le k$ parts, so does $c+1$ — the same split is still valid, since every part still fits.

</details>

---

## G. Traps

**31. Bounds too tight — what happens?**

<details><summary>Answer</summary>

If the true answer lies outside `[lo, hi]` you get **the nearest endpoint, silently**.

</details>

**32. Bounds too loose — when is it actually harmful?**

<details><summary>Answer</summary>

Rarely — it costs a few extra iterations — **unless the predicate is undefined outside the valid range**, such as dividing by a speed of zero.

</details>

**33. When does the technique not pay?**

<details><summary>Answer</summary>

When the feasibility check is expensive. Total cost is $O(\text{check} \times \log R)$ — if the check is $O(n^2)$, **optimise the check first**.

</details>

**34. What is the "answering the wrong question" trap?**

<details><summary>Answer</summary>

The template returns **the flip point**. "Smallest speed that works" and "largest speed that fails" differ by one, and **both are easy to return by accident**.

</details>

**35. Summarise the technique in one sentence.**

<details><summary>Answer</summary>

When checking an answer is easy but finding it is not, binary search the answer space on a predicate you have proved flips exactly once.

</details>

---

## Scorecard

| Pass | Date | Got it | Close | Blank | Questions missed |
| :--- | :--- | :----- | :---- | :---- | :--------------- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Related

- [[02-binary-search-on-the-answer|Binary Search on the Answer]] — the module
- [[01-linear-and-binary-search-qb|Linear & Binary Search — Question Bank]] — the special case
- [[dsa/04-patterns/09-modified-binary-search|Modified Binary Search]] — the pattern
