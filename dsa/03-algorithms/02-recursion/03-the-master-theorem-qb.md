# The Master Theorem — Question Bank

Micro-questions over [[03-the-master-theorem|the Master Theorem module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The idea

**1. What two numbers does a divide-and-conquer recurrence's answer depend on?**

<details><summary>Answer</summary>

1. $n^{\log_b a}$ — the total work at the **leaves**.
2. $f(n)$ — the work at the **root**.

</details>

**2. State the whole theorem in one sentence.**

<details><summary>Answer</summary>

**Compare those two and whichever is bigger wins; if they tie, the answer is their common value times the number of levels.**

</details>

**3. Where is all the precision?**

<details><summary>Answer</summary>

**In what "bigger" has to mean.**

</details>

---

## B. The vocabulary

**4. What is the critical exponent?**

<details><summary>Answer</summary>

$\log_b a$, sometimes the watershed exponent — **the exponent at which leaf work and root work balance**. Everything in the theorem is a comparison against $n^{\log_b a}$.

</details>

**5. What does "polynomially larger" mean?**

<details><summary>Answer</summary>

Larger by a factor of $n^\varepsilon$ for some **fixed $\varepsilon > 0$**.

</details>

**6. Is $n\log n$ polynomially larger than $n$?**

<details><summary>Answer</summary>

**No.** $\log n$ grows slower than $n^\varepsilon$ for every positive $\varepsilon$, however small. **This distinction is the single most important idea in the lesson.**

</details>

**7. What is the regularity condition, in symbols and in words?**

<details><summary>Answer</summary>

$a\,f(n/b) \le c\,f(n)$ for some $c < 1$ and all large $n$. **In words: the total combine work must actually shrink as you go down the tree, by a constant factor.**

</details>

**8. Why does the regularity condition exist?**

<details><summary>Answer</summary>

To **exclude pathological functions that oscillate**. It holds for every polynomial $f$ you will meet in practice.

</details>

**9. What is "the gap"?**

<details><summary>Answer</summary>

The region where the theorem says nothing — when $f(n)$ is larger or smaller than $n^{\log_b a}$ but **only by a logarithmic factor rather than a polynomial one**.

</details>

---

## C. The theorem

**10. State Case 1 in symbols and in words.**

<details><summary>Answer</summary>

$f(n) = O(n^{\log_b a - \varepsilon})$ for some $\varepsilon > 0 \Longrightarrow T(n) = \Theta(n^{\log_b a})$.
**The leaves are polynomially more work, so the leaves dominate.**

</details>

**11. State Case 2.**

<details><summary>Answer</summary>

$f(n) = \Theta(n^{\log_b a}\log^k n)$, $k \ge 0 \Longrightarrow T(n) = \Theta(n^{\log_b a}\log^{k+1} n)$.
**The two match, so every level does about the same work — total is that times the number of levels.**

</details>

**12. State Case 3.**

<details><summary>Answer</summary>

$f(n) = \Omega(n^{\log_b a + \varepsilon})$ for some $\varepsilon > 0$, **and** regularity holds $\Longrightarrow T(n) = \Theta(f(n))$.
**The root is polynomially more work, so the root dominates.**

</details>

**13. What is the $\varepsilon$ doing in Cases 1 and 3?**

<details><summary>Answer</summary>

**All the work.** It is what makes "smaller" and "larger" mean *polynomially* so — exactly what $n\log n$ versus $n$ fails to satisfy.

</details>

---

## D. The decision procedure

**14. Give the five steps in order.**

<details><summary>Answer</summary>

1. **Is the recurrence even of this form?** It needs the input shrinking by a **factor**, not an amount.
2. Compute $\log_b a$.
3. Compare $f(n)$ with $n^{\log_b a}$ → Case 1, 2 or 3.
4. For Case 3 only, check regularity.
5. If the comparison is "larger/smaller but only logarithmically", you are **in the gap** — draw the tree.

</details>

**15. Why does regularity hold automatically for $f(n) = n^d$?**

<details><summary>Answer</summary>

$a(n/b)^d = (a/b^d)n^d$, and Case 3 already requires $d > \log_b a$, which forces $a/b^d < 1$.

</details>

**16. Solve merge sort.**

<details><summary>Answer</summary>

$a=2, b=2, f(n)=n$. $\log_2 2 = 1$, so $n^{\log_b a} = n$. They **match**, $k=0$. Case 2: $\Theta(n\log n)$.

</details>

**17. Solve binary search.**

<details><summary>Answer</summary>

$a=1, b=2, f(n)=1$. $\log_2 1 = 0$, so $n^0 = 1$. They **match**, $k=0$. Case 2: $\Theta(\log n)$.

</details>

**18. Why does binary search surprise people?**

<details><summary>Answer</summary>

**It is Case 2, not Case 1.** People expect the "one branch" recurrence to be special; with $a=1$ the critical exponent is 0, and constant work matches $n^0$ exactly.

</details>

**19. Solve Strassen's algorithm.**

<details><summary>Answer</summary>

$a=7, b=2, f(n)=n^2$. $\log_2 7 \approx 2.807$. Is $n^2$ polynomially smaller? Yes, $\varepsilon = 0.8$. Case 1: $\Theta(n^{2.807})$.

</details>

**20. Why is Strassen famous?**

<details><summary>Answer</summary>

Naive matrix multiplication is $\Theta(n^3)$; **the same $n^2$ combine work with seven subproblems instead of eight drops the exponent to 2.807.**

</details>

---

## E. The trap

**21. $T(n) = 2T(n/2) + n\log n$. Someone says "$n\log n > n$, so Case 3, answer $\Theta(n\log n)$". Find both errors.**

<details><summary>Answer</summary>

**Error one:** Case 3 needs $f(n) = \Omega(n^{1+\varepsilon})$ for fixed $\varepsilon>0$. Here $f(n)/n = \log n$, and $\log n$ eventually falls behind $n^\varepsilon$ for *any* $\varepsilon>0$. No valid $\varepsilon$ exists.
**Error two:** the conclusion is also wrong — falling in the gap does not mean the answer is whatever Case 3 would have said.

</details>

**22. Derive the true answer by tree.**

<details><summary>Answer</summary>

Level $k$: $2^k \cdot \frac{n}{2^k}\log\frac{n}{2^k} = n(\log n - k)$. Summing $k = 0 \dots \log_2 n$:
$$n \cdot \frac{\log n(\log n + 1)}{2} = \Theta(n\log^2 n)$$

</details>

**23. Can Case 2 handle it after all?**

<details><summary>Answer</summary>

Yes — $f(n) = n\log n = \Theta(n^{\log_b a}\log^1 n)$ with $k=1$, giving $\Theta(n\log^2 n)$, the same answer. **The trap is not that the recurrence is unsolvable; it is that reaching for Case 3 because "$f$ looks bigger" gives the wrong answer.**

</details>

---

## F. Where it fails

**24. Failure 1 — what, and why does it matter most in interviews?**

<details><summary>Answer</summary>

**Subtractive shrinking.** $T(n) = 2T(n-1)+1$ has no $b$ at all. It matters because $T(n) = T(n-1)+T(n-2)+O(1)$ — naive Fibonacci — **looks superficially like a divide-and-conquer recurrence and is nothing of the sort.**

</details>

**25. What is the tree answer for $T(n) = 2T(n-1)+1$?**

<details><summary>Answer</summary>

Depth $n$, work doubling per level → $\Theta(2^n)$. Measured: 2,047 nodes at $n=10$, 2,097,151 at $n=20$.

</details>

**26. Failure 3 — what is it, and what is the example?**

<details><summary>Answer</summary>

**Subproblems of different sizes.** $T(n) = T(n/3) + T(2n/3) + n$ — quicksort with a guaranteed 1:2 split. The theorem assumes $a$ identical subproblems of size $n/b$.

</details>

**27. What does the tree give, and what is the useful takeaway?**

<details><summary>Answer</summary>

Every level does $n$ work; the longest path has length $\log_{3/2} n$, so $\Theta(n\log n)$. **Even a lopsided constant-ratio split gives $n\log n$** — quicksort does not need good pivots, only pivots that are not catastrophically bad.

</details>

**28. What generalisation handles unequal splits?**

<details><summary>Answer</summary>

The **Akra–Bazzi method**. Worth knowing the name; not worth memorising the formula.

</details>

---

## G. Traps

**29. Is it $\log_b a$ or $\log_a b$, and what is the sanity check?**

<details><summary>Answer</summary>

$\log_b a$. For $8T(n/2)$ it is $\log_2 8 = 3$, not $1/3$. **Sanity check: more subproblems should give a *larger* exponent.**

</details>

**30. Does Case 2 always contribute exactly one $\log$?**

<details><summary>Answer</summary>

No. With $f(n) = n^{\log_b a}\log^k n$ the answer carries $\log^{k+1} n$. For $k=1$ you get $\log^2 n$.

</details>

**31. When does the theorem give only $O$ rather than $\Theta$?**

<details><summary>Answer</summary>

When your $f(n)$ is itself only an upper bound — if you wrote $O(n)$ for the combine step without knowing it is exactly linear, the conclusion is an upper bound too.

</details>

**32. What does the theorem actually describe?**

<details><summary>Answer</summary>

**The recurrence, not the algorithm.** Derive the recurrence wrongly — miscounting subproblems, or including recursive work in $f(n)$ — and the theorem will faithfully give the right answer to the wrong question.

</details>

**33. Summarise the theorem in one sentence.**

<details><summary>Answer</summary>

Compare root work $f(n)$ against leaf work $n^{\log_b a}$; whichever is **polynomially** bigger is the answer, and a tie costs one extra $\log$ per level.

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

- [[03-the-master-theorem|The Master Theorem]] — the module
- [[02-recursion-trees-and-recurrences-qb|Recursion Trees & Recurrences — Question Bank]] — where the three cases are derived
- [[../03-divide-and-conquer|Divide and Conquer]] — the design pattern it costs
