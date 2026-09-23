# Growth & Asymptotic Notation — Question Bank

Micro-questions over [[01-growth-and-asymptotic-notation|the growth and asymptotics module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why growth rate

**1. Method A takes 2.5s on a gaming laptop, Method B takes 5.0s on a cheap server. Is A the better algorithm?**

<details><summary>Answer</summary>

**Not necessarily.** Runtime in seconds depends on hardware speed, language overhead and CPU load — none of which are properties of the algorithm.

</details>

**2. What does computer science measure instead?**

<details><summary>Answer</summary>

**How the workload grows as input size $n$ scales to infinity.**

</details>

**3. At $n = 10^6$, contrast $O(n^2)$ with $O(n \log n)$.**

<details><summary>Answer</summary>

$O(n^2)$ takes about **11 days**; $O(n \log n)$ finishes in **0.2 seconds** — on the exact same computer.

</details>

**4. Why is that comparison the whole argument for the subject?**

<details><summary>Answer</summary>

Because no hardware upgrade closes an 11-days-to-0.2-seconds gap. **Growth rate beats constant factors at scale, always.**

</details>

---

## B. The three asymptotics

**5. What does $O(f(n))$ mean, formally and plainly?**

<details><summary>Answer</summary>

Formally $T(n) \le c \cdot f(n)$. Plainly: an **upper bound** — at worst, work grows no faster than $f(n)$.

</details>

**6. What does $\Omega(f(n))$ mean?**

<details><summary>Answer</summary>

$T(n) \ge c \cdot f(n)$ — a **lower bound**. At best, work grows no slower than $f(n)$.

</details>

**7. What does $\Theta(f(n))$ mean?**

<details><summary>Answer</summary>

$c_1 f(n) \le T(n) \le c_2 f(n)$ — a **tight bound**. Work grows exactly like $f(n)$.

</details>

**8. State the tight bound rule.**

<details><summary>Answer</summary>

$\Theta(f(n))$ holds **if and only if** both $O(f(n))$ and $\Omega(f(n))$ hold simultaneously.

</details>

**9. Is it correct to say bubble sort is $O(n^3)$?**

<details><summary>Answer</summary>

**Technically yes** — Big-O is an upper bound and $n^2 \le n^3$. It is just useless. This is why $\Theta$ exists: it forbids a loose claim.

</details>

---

## C. Cases versus bounds

**10. What are best, average and worst case?**

<details><summary>Answer</summary>

Best: the input needing the minimum operations. Average: expected work over all probable inputs. Worst: the input causing maximum work.

</details>

**11. What is the relationship between the three cases and the three notations?**

<details><summary>Answer</summary>

**They are independent.** $O$, $\Omega$ and $\Theta$ are mathematical bounds on a function; best/average/worst choose *which* function you are bounding. You can state a $\Theta$ for the best case.

</details>

**12. Give the search example for best and worst case.**

<details><summary>Answer</summary>

Searching for an item at index 0 is $\Theta(1)$ (best); searching for a missing item is $\Theta(n)$ (worst).

</details>

**13. Why is worst case the production standard?**

<details><summary>Answer</summary>

Because attackers choose the input. A hash map is $\Theta(1)$ average and $\Theta(n)$ worst case, and **hash-flooding denial of service** deliberately triggers the gap.

</details>

---

## D. Recurrences

**14. Give the merge sort recurrence and solve it by tree.**

<details><summary>Answer</summary>

$T(n) = 2T(n/2) + O(n)$. Tree height $\log_2 n$, work per level $O(n)$, total $O(n \log n)$.

</details>

**15. Give the binary search recurrence and solve it.**

<details><summary>Answer</summary>

$T(n) = T(n/2) + O(1)$. Height $\log_2 n$, work per level $O(1)$, total $O(\log n)$.

</details>

**16. What is the structural difference between those two?**

<details><summary>Answer</summary>

Merge sort **recurses into both halves**; binary search **discards one**. Same height, completely different total.

</details>

---

## E. Amortised analysis

**17. What does amortised analysis measure?**

<details><summary>Answer</summary>

The average cost per operation across a **guaranteed sequence** of operations, where rare expensive steps are paid for by many cheap ones.

</details>

**18. Walk through the dynamic array append example.**

<details><summary>Answer</summary>

Normal push $O(1)$; resize push $O(n)$. Because capacity doubles, appending $N$ items totals $1+2+4+\dots+N/2 = N-1$ copies, so
$$\frac{O(N)}{N} = O(1) \text{ amortised.}$$

</details>

**19. How does amortised differ from average case?**

<details><summary>Answer</summary>

**Average case is a statement about the distribution of inputs; amortised is a guarantee about a sequence regardless of input.** Amortised does not assume anything is random.

</details>

---

## F. Reading constraints

**20. Give the constraint → complexity table.**

<details><summary>Answer</summary>

| $N \le$ | Allowed | Family |
| :--- | :--- | :--- |
| 12 | $O(N!)$ | permutations, backtracking |
| 25 | $O(2^N)$ | subsets, bitmask DP |
| 500 | $O(N^3)$ | Floyd–Warshall, triple loops |
| 10,000 | $O(N^2)$ | quadratic sorts, double loops |
| 1,000,000 | $O(N \log N)$ / $O(N)$ | merge sort, hash maps, two pointers |
| $> 10^7$ | $O(\log N)$ / $O(1)$ | binary search, math, bitwise |

</details>

**21. What is this table actually for?**

<details><summary>Answer</summary>

**Reading the intended solution off the constraints** before you start — in interviews and competitive programming, $N \le 25$ is a near-explicit instruction to enumerate subsets.

</details>

---

## G. Space complexity

**22. Distinguish total space from auxiliary space.**

<details><summary>Answer</summary>

**Total** includes the input arrays. **Auxiliary** is the extra temporary memory the algorithm allocates, excluding the input.

</details>

**23. What is an in-place algorithm?**

<details><summary>Answer</summary>

One with $O(1)$ auxiliary space — it modifies data directly inside the input array.

</details>

**24. What is the hidden call stack trap?**

<details><summary>Answer</summary>

Recursive functions consume auxiliary memory proportional to recursion depth $h$. **A recursive function that allocates nothing still takes $O(h)$ space.**

</details>

**25. Is a recursive in-order traversal in-place?**

<details><summary>Answer</summary>

No — it uses $O(h)$ call stack, which is $O(\log n)$ balanced and $O(n)$ degenerate. Only an iterative Morris traversal is genuinely $O(1)$.

</details>

---

## H. Traps

**26. Simplify $O(n^2 + n)$.**

<details><summary>Answer</summary>

$O(n^2)$ — $n^2$ completely dominates $n$ for large inputs.

</details>

**27. An algorithm processes an array of length $N$ and a string of length $M$. What is the complexity?**

<details><summary>Answer</summary>

$O(N \cdot M)$ — **not** $O(N^2)$. Different variables must stay different.

</details>

**28. When does an $O(n^2)$ algorithm beat an $O(n \log n)$ one?**

<details><summary>Answer</summary>

At small inputs — around $N < 20$, insertion sort beats quicksort on constant overhead. This is why real sort implementations switch to insertion sort for small subarrays.

</details>

**29. Summarise the module in one sentence.**

<details><summary>Answer</summary>

Measure growth rather than seconds, bound it above ($O$), below ($\Omega$) or tightly ($\Theta$), design against the worst case, and read the constraints to know which family is expected.

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

- [[01-growth-and-asymptotic-notation|Growth & Asymptotic Notation]] — the module
- [[02-amortized-analysis-qb|Amortized Analysis — Question Bank]] — the next bank
- [[dsa/02-data-structures/02-dynamic-arrays-qb|Dynamic Arrays — Question Bank]] — the worked amortised example
