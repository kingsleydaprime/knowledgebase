# Loops and What They Cost — Question Bank

Micro-questions over [[01-loops-and-what-they-cost|the loops module]]. Answer in a full sentence before opening the toggle. Format explained in [[02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why loop counting matters

**1. What is Big-O, at heart?**

<details><summary>Answer</summary>

**Simply counting how many times a loop repeats.**

</details>

**2. Give the 1,000-guest illustration of a single pass.**

<details><summary>Answer</summary>

Handing a badge to each guest — 1,000 repetitions, **about 15 minutes**.

</details>

**3. And the pairwise comparison?**

<details><summary>Answer</summary>

Every guest introducing themselves to every other — $\approx \frac{1000 \times 1000}{2} = 500{,}000$ handshakes, **over 300 hours**.

</details>

**4. What is the point of the comparison?**

<details><summary>Answer</summary>

**Both operate on the exact same 1,000 guests**, but the nested loop takes 500× longer.

</details>

---

## B. The vocabulary

**5. What is input size $n$?**

<details><summary>Answer</summary>

**The number of items your code has to process.**

</details>

**6. Define linear, quadratic and logarithmic time by what doubling does.**

<details><summary>Answer</summary>

**Linear $O(n)$**: doubling the input doubles the time. **Quadratic $O(n^2)$**: doubling multiplies the time by 4. **Logarithmic $O(\log n)$**: 1,000 items → 10 steps; 1,000,000 → 20 steps.

</details>

**7. What is the difference between a `for` and a `while` loop, in counting terms?**

<details><summary>Answer</summary>

**A `for` loop announces its iteration count upfront in its header.** A `while` loop's total depends on how variables change **inside** the body.

</details>

---

## C. The four rules

**8. Rule 1 — what do sequential loops do?**

<details><summary>Answer</summary>

**They add.** $n + n = 2n$, and **constant multipliers are dropped**, so it is $O(n)$.

</details>

**9. Rule 2 — what do nested loops do, and why?**

<details><summary>Answer</summary>

**They multiply** — **the inner loop restarts completely for every single step of the outer loop.** $O(n) \times O(n) = O(n^2)$.

</details>

**10. At $n = 1000$, what does nesting cost?**

<details><summary>Answer</summary>

**1,000,000 iterations** — which is why nesting is the number-one source of slow code.

</details>

**11. Rule 3 — what about a triangular loop, `for j in range(i, n)`?**

<details><summary>Answer</summary>

Total $n + (n-1) + \dots + 1 = \frac{n(n+1)}{2}$. **Half as many steps as the full square, but dropping constants still leaves $O(n^2)$.**

</details>

**12. Rule 4 — what makes a loop logarithmic?**

<details><summary>Answer</summary>

**The loop variable being divided (or multiplied) by 2 each step**, cutting the problem in half.

</details>

**13. Give the three data points for why that is a superpower.**

<details><summary>Answer</summary>

$n = 10^3$ → **10 steps**; $n = 10^6$ → **20 steps**; $n = 10^9$ → **30 steps**.

</details>

**14. What does halving make fast?**

<details><summary>Answer</summary>

**Binary search, balanced trees and heaps.**

</details>

---

## D. The hidden loop trap

**15. State the warning.**

<details><summary>Answer</summary>

**An operation that reads as a single line of code may contain a secret loop under the hood.**

</details>

**16. What is hidden inside `if item in seen_list:`?**

<details><summary>Answer</summary>

**`in` on a list scans element by element — $O(n)$.** Nested inside a `for` over $n$ items, the whole thing is $O(n^2)$.

</details>

**17. What is the fix?**

<details><summary>Answer</summary>

**Swap the `list` for a `set` or `dict`** — an $O(1)$ lookup.

</details>

**18. What is hidden inside `list.insert(0, item)`?**

<details><summary>Answer</summary>

**Every existing element shifts right by one — $O(n)$.**

</details>

**19. What is hidden inside `str += char` in a loop?**

<details><summary>Answer</summary>

**It rebuilds the entire string in memory each time** — $O(n^2)$ total. Fix: append to a list and `''.join()` at the end.

</details>

**20. What do all three hidden loops have in common?**

<details><summary>Answer</summary>

**They look like one operation and are actually a full pass** — so the cost is invisible at the call site and only shows up in the total.

</details>

---

## E. Traps

**21. What causes an infinite `while` loop?**

<details><summary>Answer</summary>

**Forgetting to update the loop condition variable inside the body.**

</details>

**22. What is the `range(n)` off-by-one?**

<details><summary>Answer</summary>

It produces indices `0` to `n-1`. **Accessing `arr[n]` triggers an `IndexError`.**

</details>

**23. What happens if you modify a collection while iterating it?**

<details><summary>Answer</summary>

**You skip elements or get unpredictable crashes** — the iterator's position no longer means what it did.

</details>

**24. Summarise the module in one sentence.**

<details><summary>Answer</summary>

Count the repetitions: sequential loops add, nested loops multiply, halving loops are logarithmic — and check whether the one-line operations inside are loops too.

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

- [[01-loops-and-what-they-cost|Loops and What They Cost]] — the module
- [[03-algorithms/01-complexity-analysis/01-growth-and-asymptotic-notation-qb|Growth & Asymptotic Notation — Question Bank]]
- [[02-data-structures/03-hash-maps-qb|Hash Maps — Question Bank]] — what removes the hidden lookup loop
