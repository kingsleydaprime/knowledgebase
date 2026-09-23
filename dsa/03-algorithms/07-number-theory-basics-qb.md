# Number Theory Basics — Question Bank

Micro-questions over [[07-number-theory-basics|the number theory module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why it exists

**1. Give the alarm clock illustration.**

<details><summary>Answer</summary>

Alarm A rings every 12 minutes, B every 18. They first coincide at **LCM(12, 18) = 36 minutes**.

</details>

**2. What asymmetry does RSA rest on?**

<details><summary>Answer</summary>

**Multiplying two 500-digit primes is instant; factoring the 1000-digit result takes thousands of years of supercomputer brute force.**

</details>

---

## B. The vocabulary

**3. What is a prime number?**

<details><summary>Answer</summary>

An integer $> 1$ with no positive divisors other than 1 and itself.

</details>

**4. What is a composite number?**

<details><summary>Answer</summary>

An integer $> 1$ with **more than two** divisors.

</details>

**5. Are 0 and 1 prime?**

<details><summary>Answer</summary>

**Neither prime nor composite.** Always handle $N \le 1$ explicitly as `False`.

</details>

**6. Define GCD and LCM.**

<details><summary>Answer</summary>

**GCD**: the largest number dividing both $a$ and $b$ — GCD(24, 36) = 12. **LCM**: the smallest number that is a multiple of both — LCM(12, 18) = 36.

</details>

---

## C. Primality testing

**7. State the $\sqrt{N}$ symmetric factor rule.**

<details><summary>Answer</summary>

Every factor pair $(a, b)$ satisfies $a \times b = N$. **If both exceeded $\sqrt N$ their product would exceed $N$** — so **at least one factor of every pair must be $\le \sqrt N$**.

</details>

**8. What follows for the algorithm?**

<details><summary>Answer</summary>

You only need to test divisors up to $\sqrt N$ — **$O(\sqrt N)$**.

</details>

**9. Quantify the saving at $N = 10^9$.**

<details><summary>Answer</summary>

A billion operations versus **31,622** — about a 30,000× speedup.

</details>

**10. Why write `while i * i <= n` rather than `i <= sqrt(n)`?**

<details><summary>Answer</summary>

It avoids floating-point entirely — **no rounding error at the boundary**, and integer multiplication is exact.

</details>

---

## D. The sieve

**11. What does testing each number individually cost, and what does the sieve cost?**

<details><summary>Answer</summary>

Individually: $N \times O(\sqrt N) = O(N\sqrt N)$. **Sieve: $O(N \log\log N)$** — near-linear.

</details>

**12. Describe the mechanism.**

<details><summary>Answer</summary>

Mark everything prime, then for each surviving $i$, **cross out its multiples**.

</details>

**13. Where should the crossing-out start, and why?**

<details><summary>Answer</summary>

At **$i^2$**. Multiples of $i$ smaller than $i^2$ — $2i$, $3i$ — **have already been crossed out by smaller primes**.

</details>

**14. What is its space cost?**

<details><summary>Answer</summary>

$O(N)$ — a boolean per number, which is the sieve's real constraint at large $N$.

</details>

---

## E. Euclid

**15. State the Euclidean identity.**

<details><summary>Answer</summary>

$$\gcd(a, b) = \gcd(b,\ a \bmod b)$$

</details>

**16. Write the loop.**

<details><summary>Answer</summary>

```python
while b:
    a, b = b, a % b
return a
```

</details>

**17. What is its complexity?**

<details><summary>Answer</summary>

$O(\log(\min(a,b)))$.

</details>

**18. How do you get LCM from GCD?**

<details><summary>Answer</summary>

$$\text{lcm}(a,b) = \frac{a \times b}{\gcd(a,b)}$$

</details>

**19. What is the overflow trap in that formula, and the fix?**

<details><summary>Answer</summary>

In C++ or Java, `a * b` can overflow a 32-bit integer before the division. **Fix: divide first** — `(a // gcd(a,b)) * b`.

</details>

---

## F. Costs

**20. Give the four complexities.**

<details><summary>Answer</summary>

Primality check $O(\sqrt N)$, $O(1)$ space. Divisor counting $O(\sqrt N)$, $O(1)$. Sieve $O(N\log\log N)$, $O(N)$. Euclidean GCD $O(\log\min(a,b))$, $O(1)$.

</details>

**21. When do you use the sieve rather than repeated primality checks?**

<details><summary>Answer</summary>

**When you need all primes up to $N$**, or many primality queries in the same range. For one number, $O(\sqrt N)$ with $O(1)$ space wins.

</details>

**22. Summarise the module in one sentence.**

<details><summary>Answer</summary>

Factors pair up around $\sqrt N$, multiples of a prime can be crossed out from its square, and GCD falls out of repeated modulo — three small facts that make the rest cheap.

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

- [[07-number-theory-basics|Number Theory Basics]] — the module
- [[11-bit-manipulation-qb|Bit Manipulation — Question Bank]]
- [[12-math-and-geometry-qb|Math & Geometry — Question Bank]]
