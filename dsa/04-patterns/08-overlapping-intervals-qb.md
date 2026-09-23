# Overlapping Intervals — Question Bank

Micro-questions over [[08-overlapping-intervals|the intervals pattern]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why it exists

**1. What does the naive pairwise check cost?**

<details><summary>Answer</summary>

$O(n^2)$ — for each interval, compare against all later ones. **500,000 checks for 1,000 intervals.**

</details>

**2. What does sorting by start time buy?**

<details><summary>Answer</summary>

**You can process in order and merge as you go** — the first interval sets the initial block, and each subsequent one either extends it or starts a new one.

</details>

**3. What does the pattern turn $O(n^2)$ into?**

<details><summary>Answer</summary>

$O(n\log n)$ — **the sort dominates; the merge itself is linear.**

</details>

---

## B. The overlap condition

**4. When do `[a,b]` and `[c,d]` overlap, once sorted by start?**

<details><summary>Answer</summary>

**When `b >= c`** — the first interval has not ended before the second begins.

</details>

**5. Do `[1,3]` and `[3,5]` overlap?**

<details><summary>Answer</summary>

**In most problem definitions, yes** — which is why the check is `start <= last_end`, not `<`. **Check the specific problem; this is a common off-by-one trap.**

</details>

**6. Why must you compare against the *last merged* interval and not the previous input one?**

<details><summary>Answer</summary>

**After a merge, the effective end time may have grown past what the original list showed.**

</details>

---

## C. The merge

**7. Write the loop.**

<details><summary>Answer</summary>

```python
intervals.sort(key=lambda p: p[0])
merged = [intervals[0]]
for start, end in intervals[1:]:
    last_start, last_end = merged[-1]
    if start <= last_end:
        merged[-1] = [last_start, max(last_end, end)]
    else:
        merged.append([start, end])
```

</details>

**8. Why `max(last_end, end)` rather than just `end`?**

<details><summary>Answer</summary>

**The new interval may be entirely contained** within the merged one — e.g. `[1,10]` then `[2,3]` — in which case taking `end` would shrink the block.

</details>

**9. Trace `[[1,3],[2,6],[8,10],[15,18]]`.**

<details><summary>Answer</summary>

`[1,3]` → `[2,6]` overlaps (2 ≤ 3) → `[1,6]` → `[8,10]` does not (8 > 6) → new block → `[15,18]` does not → new block. **Result `[[1,6],[8,10],[15,18]]`.**

</details>

---

## D. Variants

**10. Meeting Rooms II — what is the algorithm?**

<details><summary>Answer</summary>

**Sort starts and ends separately.** Sweep the starts: if the next start is before the current earliest end, you need another room; otherwise advance the end pointer.

</details>

**11. Why does that work?**

<details><summary>Answer</summary>

It counts the **peak number of simultaneously active intervals**, which is exactly the number of rooms needed.

</details>

**12. Employee free time — how do you build it?**

<details><summary>Answer</summary>

**Flatten all schedules, merge them, then take the gaps between consecutive merged intervals.**

</details>

**13. Minimum removals to make non-overlapping — what changes?**

<details><summary>Answer</summary>

**You sort by END time**, not start — this is the same greedy as interval scheduling, keeping the interval that finishes earliest.

</details>

**14. State the sorting rule across variants.**

<details><summary>Answer</summary>

**Different problems need different sort keys: merging needs start time, minimum removals needs end time.** Getting the key wrong is the defining bug of this pattern.

</details>

---

## E. Costs

**15. What is the complexity, and what dominates?**

<details><summary>Answer</summary>

$O(n\log n)$, **dominated by the sort**; the merge pass is $O(n)$.

</details>

**16. What other patterns share this shape?**

<details><summary>Answer</summary>

Most patterns needing sorted input first — modified binary search, and the sorting-based greedy algorithms.

</details>

**17. Summarise the pattern in one sentence.**

<details><summary>Answer</summary>

Sort by the right endpoint for the question being asked, then sweep once comparing each interval only against the running block.

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

- [[08-overlapping-intervals|Overlapping Intervals]] — the pattern
- [[dsa/03-algorithms/10-greedy-algorithms/02-selection-and-scheduling-qb|Selection & Scheduling — Question Bank]] — where the sort key is proved
