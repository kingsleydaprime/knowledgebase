# Two Pointers — Question Bank

Micro-questions over [[02-two-pointers|the two pointers pattern]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why it exists

**1. What is the naive cost of finding a pair summing to a target?**

<details><summary>Answer</summary>

$O(n^2)$ — for each element, loop through all later ones. **500,000 checks for 1,000 transactions.**

</details>

**2. Give the party analogy.**

<details><summary>Answer</summary>

Start with the person who has the **least** money and the person who has the **most**, and based on whether their combined total is too much or too little, **move one of them inward**.

</details>

**3. Define the pattern.**

<details><summary>Answer</summary>

**Walk two positions through a sorted structure at once, letting their relative movement do the work a nested loop would otherwise do.**

</details>

**4. What does it turn $O(n^2)$ into, and under what conditions?**

<details><summary>Answer</summary>

$O(n)$ — **when the data is sorted and you need pairs (or a small fixed number of elements) satisfying a condition on their sum or difference.**

</details>

---

## B. The mechanism

**5. Where do the two pointers start?**

<details><summary>Answer</summary>

`left = 0` and `right = len(nums) - 1` — the two ends.

</details>

**6. State the movement rule.**

<details><summary>Answer</summary>

**Sum too small → move `left` up** (need a bigger element). **Sum too large → move `right` down** (need a smaller one).

</details>

**7. Trace `[1,2,3,4,6]`, target 6.**

<details><summary>Answer</summary>

`1+6=7 > 6` → `right--`; `1+4=5 < 6` → `left++`; `2+4=6` → **found indices [1, 3]**.

</details>

**8. Why does this work without checking every pair?**

<details><summary>Answer</summary>

**At each step one side of the comparison is eliminated entirely, not just one pair** — moving `left` up rules out every pair that still includes the old, too-small `left` value paired with anything.

</details>

**9. What is convergence here?**

<details><summary>Answer</summary>

The two pointers moving toward each other **until they meet or cross**, which is the loop's termination condition.

</details>

---

## C. Extensions

**10. How does three-sum use the pattern?**

<details><summary>Answer</summary>

**Fix one element with an outer loop, then two-pointer the rest** — $O(n^2)$ overall after the sort.

</details>

**11. How do you avoid duplicate triples?**

<details><summary>Answer</summary>

Skip repeated values at the outer index (`if i > 0 and nums[i] == nums[i-1]: continue`), **and** after a hit, advance both pointers past any equal neighbours.

</details>

**12. Container with most water — what is the area formula?**

<details><summary>Answer</summary>

$\text{area} = \text{width} \times \min(\text{height}_{\text{left}}, \text{height}_{\text{right}})$.

</details>

**13. Which pointer moves, and why is that correct?**

<details><summary>Answer</summary>

**The shorter line moves inward.** Moving the taller one cannot help: the width shrinks and the height is still capped by the shorter line, so every such pair is strictly worse.

</details>

**14. Is the array sorted in container with most water?**

<details><summary>Answer</summary>

**No** — which is worth noticing. The pattern here is driven by a **monotone elimination argument**, not by sortedness.

</details>

---

## D. Trade-offs

**15. What does the sorting requirement cost?**

<details><summary>Answer</summary>

$O(n\log n)$ — **which may be more expensive than the $O(n^2)$ pair check for small $n$.**

</details>

**16. What is the alternative for unsorted data?**

<details><summary>Answer</summary>

A **hash-map version** — $O(n)$ time but $O(n)$ space, **losing the space efficiency** that is two pointers' main advantage.

</details>

**17. How far does the pattern extend?**

<details><summary>Answer</summary>

To three-sum, four-sum and so on — **but the complexity grows with the number of pointers**, roughly $O(n^{k-1})$ for $k$-sum.

</details>

**18. What conditions does it suit, and which does it not?**

<details><summary>Answer</summary>

**Sum and difference conditions.** For product or ratio conditions the pattern may not apply directly, because the monotonicity argument breaks.

</details>

**19. Do duplicates break the basic algorithm?**

<details><summary>Answer</summary>

**No** — it still finds a valid pair. Duplicates only matter when the problem asks for **distinct** results, which is what the skip-duplicates logic is for.

</details>

**20. Summarise the pattern in one sentence.**

<details><summary>Answer</summary>

Start at both ends and move the pointer that can still improve things — each step eliminates a whole side, which is why a nested loop collapses to one pass.

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

- [[02-two-pointers|Two Pointers]] — the pattern
- [[03-sliding-window-qb|Sliding Window — Question Bank]] — two pointers moving the same direction
- [[04-fast-slow-pointers-qb|Fast & Slow Pointers — Question Bank]] — two pointers at different speeds
