# Prefix Sum — Question Bank

Micro-questions over [[01-prefix-sum|the prefix sum pattern]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The idea

**1. State the pattern in one sentence, using the bank analogy.**

<details><summary>Answer</summary>

**A bank statement does not store "how much did I spend in June" — it stores the running balance after every transaction, and you get June by subtracting the balance on 1 June from the balance on 30 June.**

</details>

**2. State it without the analogy.**

<details><summary>Answer</summary>

**Do not store the answers to ranges; store the totals up to each point, and subtract.**

</details>

**3. Why is summing a range directly "fine — once"?**

<details><summary>Answer</summary>

Because the work is $O(\text{days})$ **per query**, and **the queries are the thing you have a lot of**. A dashboard re-adds the same numbers hundreds of times a second as the slider moves.

</details>

**4. Why does the subtraction work exactly?**

<details><summary>Answer</summary>

**Everything before the start got counted into both totals, so subtracting cancels it out exactly**, and what survives is precisely the slice you asked for.

</details>

**5. What is the cost of a query, and what does it depend on?**

<details><summary>Answer</summary>

**Two array lookups and a subtraction** — and it does not matter whether the range is 4 days or 4 years.

</details>

---

## B. The vocabulary

**6. What is a sentinel here, and what does it buy?**

<details><summary>Answer</summary>

A leading 0 meaning **"nothing so far"**, so index 0 needs no special case. The opening balance.

</details>

**7. What is preprocessing?**

<details><summary>Answer</summary>

Work done once up front so later queries are cheap.

</details>

**8. What is a summed-area table?**

<details><summary>Answer</summary>

The 2-D version — totals from the origin to each cell.

</details>

**9. What is inclusion–exclusion?**

<details><summary>Answer</summary>

Subtracting overlapping regions, **then adding back what was removed twice**.

</details>

**10. What is this operation called in parallel computing?**

<details><summary>Answer</summary>

**Scan.**

</details>

---

## C. Where it shows up

**11. Where is it in SQL?**

<details><summary>Answer</summary>

`SUM(revenue) OVER (ORDER BY date)` — running totals, cohort charts and burndown charts are all prefix sums, and time-series databases pre-materialise them.

</details>

**12. What is an integral image, and what famous thing used it?**

<details><summary>Answer</summary>

The summed-area table in image processing — sum of pixels in **any** rectangle in constant time. Box blur uses it, and so did the **Viola–Jones face detector**, which is why real-time face detection worked on 2001 hardware.

</details>

**13. How does weighted random selection use it?**

<details><summary>Answer</summary>

Take prefix sums of the weights, pick a random number in $[0, \text{total})$, and **binary search for where it lands** — $O(\log n)$, proportional to weight. Ad bidding, game loot tables and weighted A/B bucketing.

</details>

**14. Why is the parallel version surprising?**

<details><summary>Answer</summary>

**It looks hopelessly sequential** — each total depends on the one before — **yet it parallelises in $O(\log n)$ depth**, underpinning stream compaction, radix sort and parallel memory allocation.

</details>

---

## D. The mechanics

**15. Define `P[i]` in the sentinel convention.**

<details><summary>Answer</summary>

**The sum of everything *before* index `i`.** So `P[0] = 0`.

</details>

**16. Write the range query.**

<details><summary>Answer</summary>

```python
def range_sum(prefix, i, j):   # nums[i..j] inclusive
    return prefix[j + 1] - prefix[i]
```

</details>

**17. Write the 2-D build step and explain its last term.**

<details><summary>Answer</summary>

```python
S[r][c] = grid[r][c] + S[r-1][c] + S[r][c-1] - S[r-1][c-1]
```

The corner block is included in **both** the "above" and "left" totals, so it is subtracted once.

</details>

**18. Write the 2-D rectangle query.**

<details><summary>Answer</summary>

```
sum = S[r2][c2] - S[r1-1][c2] - S[r2][c1-1] + S[r1-1][c1-1]
```

The `+` is there because **the top-left block got subtracted twice — once by each strip.**

</details>

---

## E. The hash-map variant

**19. What question do plain prefix sums answer, and what is the harder reverse?**

<details><summary>Answer</summary>

Plain: *"what is the sum of this range I am naming?"* Reverse: ***"is there any range summing to $k$?"*** — Subarray Sum Equals K.

</details>

**20. Do the rearrangement.**

<details><summary>Answer</summary>

$$\text{prefix}[j] - \text{prefix}[i] = k \iff \text{prefix}[i] = \text{prefix}[j] - k$$

</details>

**21. What does that turn the question into?**

<details><summary>Answer</summary>

**"Have I seen the prefix sum $\text{prefix}[j] - k$ before, and how many times?"** — a hash-map lookup, not a search.

</details>

**22. Why does `seen` start as `{0: 1}`?**

<details><summary>Answer</summary>

**The empty prefix**, so subarrays starting at index 0 are counted.

</details>

**23. What replaced the array, and why?**

<details><summary>Answer</summary>

A **hash map of prefix sum → count**, because **you no longer care *where* the prefixes were, only that they existed.**

</details>

**24. Re-skin 1: longest subarray with equal 0s and 1s.**

<details><summary>Answer</summary>

**Count each 0 as $-1$**, so "equal counts" becomes "sum is zero", which becomes "this prefix sum has appeared before". Store the **first** index each sum was seen at; the distance between sightings is the subarray.

</details>

**25. Re-skin 2: subarray sums divisible by $k$.**

<details><summary>Answer</summary>

Store `running % k` instead of `running`. **Two positions with the same remainder bracket a subarray divisible by $k$.**

</details>

**26. State the general shape.**

<details><summary>Answer</summary>

**Transform the elements so the property you want becomes "sum is 0" or "sums are equal", then let the hash map find repeats.**

</details>

---

## F. Complexity and gotchas

**27. Give the costs.**

<details><summary>Answer</summary>

$O(n)$ to build, **$O(1)$ per query**. For $q$ queries that is $O(n + q)$ instead of $O(n \cdot q)$. Space $O(n)$ — or a scalar plus a map in the streaming variants.

</details>

**28. What is the number-one bug?**

<details><summary>Answer</summary>

**Inclusive vs exclusive off-by-ones.** Pick the sentinel-padded convention and stay in it; mixing conventions mid-problem is how `range_sum` quietly returns a number one element too big.

</details>

**29. Which operations can prefix sums handle, and which cannot?**

<details><summary>Answer</summary>

**Invertible ones** — sum, XOR, count — because you can subtract off the part you do not want. **Max and min cannot**: knowing `max(A[0..5])` and `max(A[0..1])` tells you nothing about `max(A[2..5])`.

</details>

**30. So what do you use for range max?**

<details><summary>Answer</summary>

A **sparse table or segment tree** — or, as in Trapping Rain Water, **directional prefix/suffix maxima arrays** that you read rather than subtract.

</details>

**31. What happens if the array can be updated?**

<details><summary>Answer</summary>

**One update to `nums[i]` invalidates every prefix sum from `i` onward.** With frequent updates use a **Fenwick tree or segment tree** — $O(\log n)$ for both update and query.

</details>

**32. What is the overflow risk?**

<details><summary>Answer</summary>

**The prefix sums grow to the total of the whole array**, which can exceed `int` even when every element is small. Use 64-bit.

</details>

**33. When should you not use the pattern?**

<details><summary>Answer</summary>

**With only one query to answer.** Preprocessing costs $O(n)$ and a single range sum also costs $O(n)$ — it only pays amortised over many queries.

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

- [[01-prefix-sum|Prefix Sum]] — the pattern
- [[03-sliding-window-qb|Sliding Window — Question Bank]] — what it cannot replace when values go negative
- [[dsa/02-data-structures/03-hash-maps-qb|Hash Maps — Question Bank]]
