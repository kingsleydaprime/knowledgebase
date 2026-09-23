# The Leader Algorithm — Question Bank

Micro-questions over [[08-leader-algorithm|the leader/majority module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The problem

**1. What is a leader (majority element)?**

<details><summary>Answer</summary>

A value appearing **strictly more than $\lfloor N/2 \rfloor$** times — an election candidate winning over 50%.

</details>

**2. How many leaders can a sequence have, and why?**

<details><summary>Answer</summary>

**At most one.** If two values each appeared more than half the time, their combined count would exceed 100% of the array length.

</details>

**3. Name three real applications.**

<details><summary>Answer</summary>

Distributed consensus (Raft leader election), data-stream majority detection without buffering, and sensor fusion consensus.

</details>

---

## B. Brute force and sorting

**4. Describe the brute force, and its cost.**

<details><summary>Answer</summary>

For every candidate value, scan the whole array and count. $N$ candidates × $N$ elements = **$O(N^2)$**.

</details>

**5. Where must a leader sit in the sorted array?**

<details><summary>Answer</summary>

**At the middle index `A[n // 2]`** — a value occupying more than $N/2$ positions must cover the midpoint once values are packed together.

</details>

**6. What is the cost of the sorting approach?**

<details><summary>Answer</summary>

$O(n\log n)$ time, $O(1)$ extra if you sort in place (or $O(n)$ if you copy to avoid mutating the input).

</details>

---

## C. Boyer-Moore voting

**7. State the core insight.**

<details><summary>Answer</summary>

**If you remove any pair of two *different* values, the leader remains the leader of what is left.** A matched pair contains at most one leader occurrence, so **the leader's proportion only grows.**

</details>

**8. Describe phase 1.**

<details><summary>Answer</summary>

Keep a candidate and a count. If the count is 0, adopt the current value with count 1. If the value matches the candidate, increment. Otherwise **decrement** — cancelling one occurrence.

</details>

**9. What is the cost?**

<details><summary>Answer</summary>

$O(n)$ time and **$O(1)$ space** — one pass, two variables.

</details>

**10. Trace it on `[A,B,A,A,C,A,B,A,A]`.**

<details><summary>Answer</summary>

Counts: 1, 0, 1, 2, 1, 2, 1, 2, 3. Candidate ends as **A** with count 3 — confirmed at 6/9 > 4.

</details>

**11. What is phase 2, and is it optional?**

<details><summary>Answer</summary>

**Verification — a second pass counting the candidate's actual occurrences. It is not optional.**

</details>

**12. Why is it mandatory?**

<details><summary>Answer</summary>

**Boyer-Moore always produces a candidate even when no majority element exists.** Without the check you return a confident wrong answer.

</details>

---

## D. Comparison

**13. Give the three approaches with time and space.**

<details><summary>Answer</summary>

| Approach | Time | Space | Idea |
| :--- | :--- | :--- | :--- |
| Brute force | $O(n^2)$ | $O(1)$ | rescan per candidate |
| Sort + middle | $O(n\log n)$ | $O(1)$ | leader lands at midpoint |
| Boyer-Moore | **$O(n)$** | **$O(1)$** | pairwise cancellation |

</details>

**14. Why not just use a hash map counter?**

<details><summary>Answer</summary>

It is also $O(n)$ time but **$O(n)$ space**. Boyer-Moore's whole distinction is achieving it in constant space — which is what makes it viable on a stream.

</details>

---

## E. Traps

**15. Distinguish leader from mode.**

<details><summary>Answer</summary>

**A leader requires a strict majority (> 50%).** The mode — most common element — might appear only 30% of the time and is not a leader.

</details>

**16. Does Boyer-Moore only work on integers?**

<details><summary>Answer</summary>

No — **it works for any comparable type**; it only ever tests equality.

</details>

**17. Summarise the algorithm in one sentence.**

<details><summary>Answer</summary>

Cancel unequal pairs as you sweep and whatever survives is the only possible majority — then verify it, because something always survives.

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

- [[08-leader-algorithm|The Leader Algorithm]] — the module
- [[09-max-slice-algorithms-qb|Max Slice Algorithms — Question Bank]] — the other one-pass classic
