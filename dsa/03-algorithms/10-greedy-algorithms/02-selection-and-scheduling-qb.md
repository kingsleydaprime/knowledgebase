# Selection & Scheduling — Question Bank

Micro-questions over [[02-selection-and-scheduling|the selection and scheduling module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Hire K workers

**1. State the problem.**

<details><summary>Answer</summary>

Hire $K$ people. Each has a **quality** and a **minimum wage**. Everyone hired is paid the same **rate per unit of quality**, and nobody may be paid below their own minimum. **Which $K$ cost least in total?**

</details>

**2. What is the instinctive answer, and why is it wrong?**

<details><summary>Answer</summary>

"Take the $K$ cheapest advertised wages." Wrong because **one expensive-per-unit person raises the rate for everybody**.

</details>

**3. Work the example: A(10, 70), B(20, 140), C(5, 60), $K=2$.**

<details><summary>Answer</summary>

Ratios 7.00, 7.00, 12.00. A+B = $7 \times 30 = 210$. A+C = $12 \times 15 = 180$. B+C = $12 \times 25 = 300$. **A+C wins, despite containing the worst rate.**

</details>

**4. Why does the cheap rate of A+B lose?**

<details><summary>Answer</summary>

**B's high quality.** You pay for quality you do not need.

</details>

**5. State the whole difficulty in one sentence.**

<details><summary>Answer</summary>

**The cost of a group is not the sum of its members' costs** — it is a product of two things that pull in opposite directions.

</details>

**6. Give the cost formula.**

<details><summary>Answer</summary>

$$\text{cost}(S) = \left(\max_{i \in S}\frac{w_i}{q_i}\right) \times \sum_{i\in S} q_i$$

</details>

**7. Say it in words.**

<details><summary>Answer</summary>

**The bill is the group's worst rate multiplied by the group's total quality.** One person sets the price; everyone contributes to the volume.

</details>

**8. Give the greedy in five steps.**

<details><summary>Answer</summary>

1. Sort everyone by **ratio, ascending**.
2. The worker you are at has the **largest ratio seen so far**, so they set the rate.
3. Given that rate, you want the $K$ **smallest qualities** among those seen.
4. Maintain them with a **max-heap of size $K$** — push, and pop the largest when it exceeds $K$.
5. Once the heap holds exactly $K$, candidate cost = `rate × sum_of_heap`. Keep the minimum.

</details>

**9. Why is it correct?**

<details><summary>Answer</summary>

**Every group has some member with the maximum ratio.** Fixing that member fixes the rate, leaving only the choice of which $K-1$ others — for which you obviously want the smallest qualities. **Iterating over every possible rate-setter considers every group that could be optimal.**

</details>

**10. What is the cost?**

<details><summary>Answer</summary>

$O(n\log n)$ to sort plus $O(n\log k)$ to sweep.

</details>

**11. How often is "take the $K$ cheapest wages" wrong?**

<details><summary>Answer</summary>

**130 of 400 random instances — nearly a third.** Not an exotic corner case.

</details>

---

## B. Interval scheduling

**12. State the problem.**

<details><summary>Answer</summary>

Given meetings with start and end times, **fit in as many non-overlapping meetings as possible**.

</details>

**13. Which sort key is correct?**

<details><summary>Answer</summary>

**Earliest END time.**

</details>

**14. Why does earliest START fail?**

<details><summary>Answer</summary>

It takes the meeting running 0–10 and is then **blocked for the whole day** — one meeting instead of two.

</details>

**15. Why does shortest DURATION fail?**

<details><summary>Answer</summary>

On `[(0,5),(4,6),(5,10)]` the short middle meeting **blocks both long ones** — one instead of two.

</details>

**16. What is the testing lesson here?**

<details><summary>Answer</summary>

Shortest-duration **ties with the correct answer on the first example** and fails on the second. **Each wrong key fails on some input and ties on others; only "earliest end" survives both.**

</details>

**17. Give the exchange argument.**

<details><summary>Answer</summary>

Let $g_1$ be the earliest-finishing meeting. Take any optimal solution sorted by end time; $g_1$ ends no later than $o_1$, so **replacing $o_1$ with $g_1$ leaves every later meeting still compatible**. The modified set is valid and **the same size**, so still optimal. Recurse.

</details>

**18. State the intuition in one sentence.**

<details><summary>Answer</summary>

**Finishing earliest leaves the most room for everything else, and nothing is lost by preferring it.**

</details>

---

## C. Select the most vs cover them all

**19. What is the opposite problem, over the same input?**

<details><summary>Answer</summary>

**How many rooms do you need to hold all of them?** Section 2 discards conflicting meetings; this one pays for them.

</details>

**20. What is the answer?**

<details><summary>Answer</summary>

**The peak number of simultaneous meetings.**

</details>

**21. Describe the sweep.**

<details><summary>Answer</summary>

Build events: $+1$ at every start, $-1$ at every end. **Sort so that $-1$ precedes $+1$ at the same instant.** Accumulate and track the maximum.

</details>

**22. Why must $-1$ precede $+1$?**

<details><summary>Answer</summary>

**A meeting ending at 10 and another starting at 10 need one room, not two.**

</details>

---

## D. Traps

**23. What problem shape has the "worst member sets the price" structure?**

<details><summary>Answer</summary>

**Any problem where one member's constraint applies to the whole group.** The naive per-member sum is wrong there.

</details>

**24. Why negate when using Python's `heapq` here?**

<details><summary>Answer</summary>

`heapq` is a **min-heap**, and in the hiring sweep you are discarding the **largest** qualities — so the heap must surrender its maximum. Negation inverts it.

</details>

**25. What is the floating-point ratio trap, and the fix?**

<details><summary>Answer</summary>

**Two candidates with equal ratios can compare unequal after division.** Compare $w_i q_j$ against $w_j q_i$ to stay in integers.

</details>

**26. Hire-K is greedy. What similar-looking problem is not?**

<details><summary>Answer</summary>

**The assignment problem** — one person per job, each pair with its own cost. Greedy is wrong for it; it needs the Hungarian algorithm or min-cost max-flow.

</details>

**27. What should you do if you cannot write the exchange argument?**

<details><summary>Answer</summary>

**Use dynamic programming.** A greedy that passes your tests without an argument is a guess — **slower and correct beats fast and wrong.**

</details>

**28. Summarise the module in one sentence.**

<details><summary>Answer</summary>

The sort key *is* the greedy algorithm — and choosing it correctly means proving an exchange argument, not testing one example.

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

- [[02-selection-and-scheduling|Selection & Scheduling]] — the module
- [[01-when-greedy-works-qb|When Greedy Works — Question Bank]]
- [[dsa/04-patterns/08-overlapping-intervals|Overlapping Intervals]] — the pattern
