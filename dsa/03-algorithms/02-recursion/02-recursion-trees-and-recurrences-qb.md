# Recursion Trees & Recurrences — Question Bank

Micro-questions over [[02-recursion-trees-and-recurrences|the recurrences module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The cost that refers to itself

**1. Ask "how long does merge sort take on $n$ elements?" — what is the answer?**

<details><summary>Answer</summary>

However long it takes on $n/2$ elements, twice, plus $n$ for the merge. **The answer is written in terms of the question.**

</details>

**2. Write that as a recurrence.**

<details><summary>Answer</summary>

$$T(n) = 2\,T(n/2) + O(n)$$

</details>

**3. What is a recurrence relation?**

<details><summary>Answer</summary>

An equation defining a function's value at $n$ using its values at smaller inputs, **together with a base case**.

</details>

**4. What does "solving" one mean?**

<details><summary>Answer</summary>

Finding a **closed form** — an expression for $T(n)$ with no $T$ on the right-hand side — or at least its growth rate.

</details>

---

## B. The vocabulary

**5. What is the branching factor $a$?**

<details><summary>Answer</summary>

How many recursive calls one call makes. Merge sort $a = 2$; binary search $a = 1$; naive Fibonacci $a = 2$.

</details>

**6. What is the shrink factor $b$?**

<details><summary>Answer</summary>

The factor by which the input gets smaller when the shrinking is **divisive**. Merge sort has $b=2$. A recursion that shrinks by subtraction has no $b$ at all.

</details>

**7. What is $f(n)$?**

<details><summary>Answer</summary>

The **combine work** (or driving function) — the non-recursive work one call does, everything outside the recursive calls. For merge sort it is the merge, $f(n) = n$.

</details>

**8. In a recursion tree, what is each node labelled with?**

<details><summary>Answer</summary>

**The work that node alone does, excluding its children.**

</details>

**9. What is the depth of a divisive recurrence? A subtractive one?**

<details><summary>Answer</summary>

$\log_b n$ for divisive; $n$ (or $n/c$) for subtractive.

</details>

**10. How many leaves does a divisive recurrence have?**

<details><summary>Answer</summary>

$a^{\text{depth}} = a^{\log_b n} = n^{\log_b a}$.

</details>

**11. What is the substitution method?**

<details><summary>Answer</summary>

Guessing a closed form and **proving it correct by induction**. It is the rigorous companion to the recursion tree, which is really a way of *finding* the guess.

</details>

---

## C. From code to recurrence

**12. What three things do you read off the code?**

<details><summary>Answer</summary>

1. How many recursive calls → $a$.
2. How much smaller the input is → $b$ (or "minus one").
3. How much work outside the recursive calls → $f(n)$.

Then $T(n) = a\,T(n/b) + f(n)$.

</details>

**13. Give the recurrence for binary search, merge sort, and naive Fibonacci.**

<details><summary>Answer</summary>

Binary search: $T(n) = T(n/2) + O(1)$.
Merge sort: $T(n) = 2T(n/2) + O(n)$.
Naive Fibonacci: $T(n) = T(n{-}1) + T(n{-}2) + O(1)$.

</details>

**14. What is the mistake to avoid at this step?**

<details><summary>Answer</summary>

**Counting the recursive work twice.** $f(n)$ is *only* what the current call does itself — in merge sort the merge, never the sorting of the halves, which the $2T(n/2)$ term already covers.

</details>

**15. Why is tree traversal not honestly $T(n) = 2T(n/2) + O(1)$?**

<details><summary>Answer</summary>

That assumes a **balanced** tree. An unbalanced one is $T(n) = T(k) + T(n-1-k) + O(1)$ — which is why traversal is argued $O(n)$ by "each node is visited once" rather than by this machinery.

</details>

---

## D. The recursion tree

**16. What is the key move that makes the tree method work?**

<details><summary>Answer</summary>

**Sum across each level rather than down each branch.**

</details>

**17. For $T(n) = 2T(n/2)+n$, what is the work at level $k$?**

<details><summary>Answer</summary>

$2^k$ nodes each of size $n/2^k$ doing $n/2^k$ work — **level total $n$, regardless of $k$.**

</details>

**18. Finish the derivation.**

<details><summary>Answer</summary>

$\log_2 n + 1$ levels, each doing $n$, so $T(n) = n(\log_2 n + 1) = O(n\log n)$. At $n=64$: 7 levels × 64 = 448.

</details>

**19. Give the general level arithmetic.**

<details><summary>Answer</summary>

$$\text{nodes} = a^k, \quad \text{size} = \frac{n}{b^k}, \quad \text{level work} = a^k f\!\left(\frac{n}{b^k}\right)$$

</details>

**20. What are the only three things that quantity can do, and what does each give?**

<details><summary>Answer</summary>

| Work per level | Dominated by | Result |
| :--- | :--- | :--- |
| **grows** downward | the leaves | $O(n^{\log_b a})$ |
| **stays constant** | every level equally | $O(f(n)\log n)$ |
| **shrinks** downward | the root | $O(f(n))$ |

</details>

**21. What is that table?**

<details><summary>Answer</summary>

**The entire content of [[03-the-master-theorem|the Master Theorem]], derived.** The theorem is this table with the conditions made precise.

</details>

**22. Why is "dominated by" legitimate?**

<details><summary>Answer</summary>

**Because these are geometric series.** If work shrinks by a factor $r<1$, the total is $< f(n)/(1-r)$ — a constant multiple of the root. If it grows by $r>1$, the last level is a constant fraction of the whole sum.

</details>

**23. For $T(n)=2T(n/2)+n^2$ at $n=64$, what do the level totals do?**

<details><summary>Answer</summary>

$4096, 2048, 1024, \dots, 64$ — **halving**. Total 8,128, under $2n^2$. **The root alone accounts for half the entire tree.**

</details>

**24. And for $T(n)=2T(n/2)+1$?**

<details><summary>Answer</summary>

$1, 2, 4, \dots, 64$ — **doubling**. Total 127, and **the bottom level alone is more than half.**

</details>

---

## E. Worked case

**25. For $T(n) = 3T(n/2) + n$, what is the level work?**

<details><summary>Answer</summary>

$3^k \cdot n/2^k = n(3/2)^k$ — multiplied by $3/2 > 1$ each step, so it **grows downward**.

</details>

**26. So what dominates, and what is the complexity?**

<details><summary>Answer</summary>

**The leaves.** There are $3^{\log_2 n} = n^{\log_2 3} \approx n^{1.585}$ of them, so $T(n) = \Theta(n^{\log_2 3})$.

</details>

**27. What is the doubling test?**

<details><summary>Answer</summary>

If you think an algorithm is $O(n^k)$, **double the input and see whether the time multiplies by $2^k$.** Linear doubles, quadratic quadruples, $n\log n$ does slightly more than double, $O(\log n)$ barely moves.

</details>

**28. Why is it the most useful practical skill here?**

<details><summary>Answer</summary>

**You can check a complexity claim in two runs without reading a line of the implementation.**

</details>

**29. What does the doubling test predict for $n^{\log_2 3}$, and what was measured?**

<details><summary>Answer</summary>

$2^{\log_2 3} = 3$, and the measurements converge on 3.06, 3.04, 3.03, 3.02.

</details>

---

## F. The catalogue

**30. Give the solutions for the four subtractive recurrences.**

<details><summary>Answer</summary>

$T(n-1)+O(1) \to O(n)$; $T(n-1)+O(n) \to O(n^2)$; $2T(n-1)+O(1) \to O(2^n)$.

</details>

**31. Give the solutions for the divisive ones.**

<details><summary>Answer</summary>

$T(n/2)+O(1) \to O(\log n)$; $T(n/2)+O(n) \to O(n)$; $2T(n/2)+O(1) \to O(n)$; $2T(n/2)+O(n) \to O(n\log n)$; $2T(n/2)+O(n^2) \to O(n^2)$; $3T(n/2)+O(n) \to O(n^{1.585})$; $7T(n/2)+O(n^2) \to O(n^{2.807})$.

</details>

**32. Compare $2T(n/2)+O(1)$ with $2T(n/2)+O(n)$ — what is the lesson?**

<details><summary>Answer</summary>

Same branching, same shrinking; only $O(1)$ versus $O(n)$ combine work — and that alone is $O(n)$ versus $O(n\log n)$. **Merge sort cannot be made linear by clever coding: a linear combine at every level is where the $\log n$ comes from.**

</details>

**33. Compare $T(n-1)+O(1)$ with $T(n/2)+O(1)$ — what is the lesson?**

<details><summary>Answer</summary>

Subtracting one gives $n$ levels; dividing by two gives $\log n$. **Shrinking multiplicatively rather than additively is the single highest-leverage move in algorithm design** — it is why binary search, balanced trees and divide-and-conquer all exist.

</details>

**34. What is the lesson of $2T(n-1)+O(1)$?**

<details><summary>Answer</summary>

**Branching with subtractive shrinking is always exponential.** This is naive Fibonacci — and why memoisation there is not an optimisation but a change of algorithm.

</details>

---

## G. Substitution

**35. Prove $T(n) = 2T(n/2)+n$ is $O(n\log n)$ by substitution.**

<details><summary>Answer</summary>

Guess $T(n) \le c\,n\log_2 n$. Then
$$T(n) \le 2c\frac{n}{2}\log_2\frac{n}{2} + n = c\,n\log_2 n - cn + n$$
which is $\le c\,n\log_2 n$ whenever $c \ge 1$.

</details>

**36. Which step do people get wrong?**

<details><summary>Answer</summary>

**Assuming the bound for $n/2$ without checking the leftover terms cancel in the right direction.** Here $-cn + n \le 0$ is what pinned down $c \ge 1$. If the leftovers went the other way, the guess needs strengthening — typically to $c\,n\log_2 n - d\,n$.

</details>

---

## H. Traps

**37. Is the base of the logarithm irrelevant?**

<details><summary>Answer</summary>

**Inside $O(\cdot)$, yes** — logs differ by a constant factor. **In the level arithmetic, no**: the depth really is $\log_b n$, which is what tells you a 3-way split has depth $\log_3 n$.

</details>

**38. Is more branching always worse?**

<details><summary>Answer</summary>

No. $8T(n/2)+O(n^2)$ is $O(n^3)$; Strassen's $7T(n/2)+O(n^2)$ is $O(n^{2.807})$ — **one fewer subcall changes the exponent**. Branching interacts with shrinking; neither alone decides.

</details>

**39. What does drawing a balanced tree silently assume?**

<details><summary>Answer</summary>

**The thing you may need to prove.** Quicksort is $T(k)+T(n-1-k)+O(n)$; balanced splits give $O(n\log n)$ and $k=0$ gives $O(n^2)$.

</details>

**40. For $T(n) = 2T(n/2) + O(1)$, what happens if you only count internal nodes?**

<details><summary>Answer</summary>

You conclude $O(\log n)$ and are **badly wrong**. The leaves are the whole cost — there are $n$ of them each doing constant work.

</details>

**41. Summarise the method in one sentence.**

<details><summary>Answer</summary>

Read $a$, $b$ and $f(n)$ off the code, compute the work per level, and ask whether it grows, stays flat, or shrinks — the answer is the leaves, every level, or the root.

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

- [[02-recursion-trees-and-recurrences|Recursion Trees & Recurrences]] — the module
- [[03-the-master-theorem-qb|The Master Theorem — Question Bank]] — this table made precise
- [[01-recursion-fundamentals-qb|Recursion Fundamentals — Question Bank]]
