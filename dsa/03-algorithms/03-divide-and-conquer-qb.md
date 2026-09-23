# Divide and Conquer — Question Bank

Micro-questions over [[03-divide-and-conquer|the divide and conquer module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The design question

**1. Everyone can state "divide, conquer, combine". What makes it a technique rather than a slogan?**

<details><summary>Answer</summary>

**You chose $a$, $b$ and $f$ in $T(n) = a\,T(n/b) + f(n)$.** The design question is not "should I use divide and conquer?" but **"what values of $a$, $b$ and $f$ can I get away with?"**

</details>

**2. What does reducing $a$ buy?**

<details><summary>Answer</summary>

It changes the **exponent** $n^{\log_b a}$. Karatsuba: 4 → 3 multiplications, $n^2 \to n^{1.585}$.

</details>

**3. What does reducing $f(n)$ buy?**

<details><summary>Answer</summary>

**A log factor, or nothing.** Merge sort's $O(n)$ merge is what the $\log n$ costs.

</details>

**4. State the single most useful design insight.**

<details><summary>Answer</summary>

**Reducing $a$ is worth far more than reducing $f$.** Strassen and Karatsuba are famous because they cut $a$; **nobody is famous for a faster merge.**

</details>

---

## B. The vocabulary

**5. Define the divide, conquer and combine steps.**

<details><summary>Answer</summary>

**Divide**: how the input is split — usually trivial, its cost part of $f(n)$. **Conquer**: the $a$ recursive calls on inputs of size $n/b$. **Combine**: the work turning sub-answers into the whole answer.

</details>

**6. Which step matters most?**

<details><summary>Answer</summary>

The **combine** — it is where almost all divide-and-conquer algorithms do their real work, and where the interesting ones do something clever.

</details>

**7. What does "independent subproblems" mean, and what does it distinguish?**

<details><summary>Answer</summary>

No subproblem's answer is needed for another's, and no two solve the same instance. **Independence is what distinguishes divide and conquer from dynamic programming** — when subproblems overlap, you memoise instead.

</details>

**8. Why does a balanced split matter?**

<details><summary>Answer</summary>

Balanced splits give $\log_b n$ depth; unbalanced ones degrade to depth $n$ — exactly quicksort's worst case.

</details>

**9. What is a base-case threshold, and what is a typical value?**

<details><summary>Answer</summary>

The size below which you stop recursing and use a simple method. **Real merge sorts switch to insertion sort at around 10–30 elements**, because recursion's constant factors dominate below that.

</details>

---

## C. The catalogue

**10. Compare tree traversal with merge sort.**

<details><summary>Answer</summary>

Identical $a$ and $b$. Only difference: $O(1)$ combine versus $O(n)$ combine — and **that is the entire difference between $O(n)$ and $O(n\log n)$.**

</details>

**11. Why can merge sort never be made linear?**

<details><summary>Answer</summary>

**Any correct merge must look at every element**, so the $O(n)$ combine is irreducible, and it is paid once per level across $\log n$ levels.

</details>

**12. What do binary search and fast power have in common?**

<details><summary>Answer</summary>

**Only one recursive call**, so no branching — the tree is a path and the result is simply the depth. Any algorithm that discards a constant fraction each step and recurses once is $O(\log n)$.

</details>

---

## D. Counting inversions

**13. What is an inversion, and what is it used for?**

<details><summary>Answer</summary>

A pair $(i, j)$ with $i < j$ and $a_i > a_j$ — a pair out of order. It measures how unsorted a list is, and is used in rank correlation statistics and collaborative filtering.

</details>

**14. What is the brute force cost?**

<details><summary>Answer</summary>

$O(n^2)$ — check every pair.

</details>

**15. State the merge insight.**

<details><summary>Answer</summary>

When you take an element from the **right** half because it is smaller, the left half is sorted — so that element is smaller than **every remaining element of the left half**, all `len(left) - i` of them. That is `len(left) - i` inversions counted **in one operation**.

</details>

**16. Write the line.**

<details><summary>Answer</summary>

```python
inv += len(left) - i
```

</details>

**17. State the general design lesson.**

<details><summary>Answer</summary>

**The combine step you already needed for another reason turns out to compute the thing you wanted.**

</details>

---

## E. When it is the wrong tool

**18. Max subarray has a clean $O(n\log n)$ divide-and-conquer solution. Is it a good algorithm for the problem?**

<details><summary>Answer</summary>

**No** — the problem is solvable in $O(n)$ by Kadane's, so the D&C solution is a $\log n$ factor worse while being considerably longer. Measured: ~20× slower at $n = 64{,}000$, and the ratio grows.

</details>

**19. What exactly does the D&C solution throw away?**

<details><summary>Answer</summary>

**The best subarray ending at position $i$ is computable from the one ending at $i-1$.** Divide and conquer splits because it does not know anything else about the problem.

</details>

**20. State the lesson.**

<details><summary>Answer</summary>

**Being applicable is not the same as being right.** A technique that ignores structure loses to one that uses it.

</details>

**21. Give the three conditions for reaching for it.**

<details><summary>Answer</summary>

1. The problem splits into **independent** subproblems of the same kind.
2. Combining is **cheaper** than solving the whole directly.
3. The split is **balanced**, or you can make it so.

</details>

**22. Give the four conditions for not reaching for it.**

<details><summary>Answer</summary>

1. **Subproblems overlap** → dynamic programming.
2. **A single linear pass suffices.**
3. **The combine costs as much as brute force** — recursion overhead for nothing.
4. **The subproblems are not independent** — the recursion is not well-formed.

</details>

---

## F. Reducing $a$

**23. Write the obvious split for multiplying two $n$-digit numbers.**

<details><summary>Answer</summary>

$$(a\cdot10^m + b)(c\cdot10^m + d) = ac\cdot10^{2m} + (ad+bc)\cdot10^m + bd$$

Four multiplications: $ac$, $ad$, $bc$, $bd$.

</details>

**24. What does that give, and what is the verdict?**

<details><summary>Answer</summary>

$T(n) = 4T(n/2)+O(n)$, $\log_2 4 = 2$, so $\Theta(n^2)$ — **exactly the schoolbook method, with extra steps.** Divide and conquer bought nothing.

</details>

**25. State Karatsuba's observation.**

<details><summary>Answer</summary>

You do not need $ad$ and $bc$ separately, only their **sum** — and
$$ad + bc = (a+b)(c+d) - ac - bd$$
You already have $ac$ and $bd$, so one extra multiplication yields the middle term.

</details>

**26. What is the resulting recurrence and complexity?**

<details><summary>Answer</summary>

$T(n) = 3T(n/2) + O(n) \implies \Theta(n^{\log_2 3}) = \Theta(n^{1.585})$.

</details>

**27. Why do real bignum libraries only use Karatsuba above a few hundred digits?**

<details><summary>Answer</summary>

Each level pays **additions and shifts** that schoolbook does not, so the wall-clock crossover comes much later than the operation-count crossover.

</details>

**28. State Strassen as the same move.**

<details><summary>Answer</summary>

The obvious block decomposition needs 8 multiplications → $\log_2 8 = 3$ → $\Theta(n^3)$. Strassen found a way with **7** → $\Theta(n^{\log_2 7}) = \Theta(n^{2.807})$.

</details>

**29. State the shared insight in one sentence.**

<details><summary>Answer</summary>

**An extra addition is cheap; a multiplication is a whole recursive subproblem.** Trading additions for multiplications changes the exponent, and nothing you do to the combine step will.

</details>

---

## G. Traps

**30. What is wrong with writing merge sort using `arr[:mid]`?**

<details><summary>Answer</summary>

Slices **copy**, adding $O(n)$ extra work per level and $O(n\log n)$ total memory. Pass indices instead.

</details>

**31. How do you bound recursion depth at $O(\log n)$ even with an unbalanced split?**

<details><summary>Answer</summary>

**Recurse on the smaller side and loop on the larger.** The recursed side at most halves each time, so the depth is $O(\log n)$ regardless.

</details>

**32. Summarise divide and conquer in one sentence.**

<details><summary>Answer</summary>

Split into independent pieces, recurse, and combine — where the design work is cutting the number of recursive calls, not speeding up the combine.

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

- [[03-divide-and-conquer|Divide and Conquer]] — the module
- [[02-recursion/03-the-master-theorem-qb|The Master Theorem — Question Bank]] — what each choice of $a, b, f$ costs
- [[09-max-slice-algorithms|Max Slice Algorithms]] — Kadane's, the linear alternative
