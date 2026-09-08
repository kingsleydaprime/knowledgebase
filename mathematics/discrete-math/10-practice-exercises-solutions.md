# Practice Exercises — Solutions

> **[Beginner → Intermediate]** · Worked answers to [[foundations/discrete-math/09-practice-exercises|note 09]]. **Write yours first.**

Proofs are given in the form you should be writing — prose with the logical skeleton visible, not symbol soup.

---

## Part A — Logic

### 1. Negate carefully

**(a)** "Every student passed at least one exam" is $\forall s\, \exists e\, P(s,e)$. Negation: $\exists s\, \forall e\, \lnot P(s,e)$ — **"Some student failed every exam."**

**(b)** $\exists n\, \forall m\, (n > m)$. Negation: $\forall n\, \exists m\, (m \ge n)$ — **"For every number there is one at least as large."**

**(c)** **"It rained and the match went ahead."**

**(c) is the one that matters.** $\lnot(P \to Q) \equiv P \land \lnot Q$ — the negation of an implication is **not** an implication. To refute "if it rains the match is cancelled" you need a day that rained *and* the match happened. Not "if it rains the match happens."

**This is the most common logical error in engineering discussion.** "We said if load exceeds X we'd scale" is not refuted by "load was low and we didn't scale."

### 2. $P \to Q \equiv \lnot P \lor Q$

The truth table matches on all four rows. The only row where $P \to Q$ is false is $P$ true, $Q$ false — exactly where $\lnot P \lor Q$ is false.

**"If 2+2=5 then I am the Pope" is true** because the antecedent is false, so $\lnot P$ is true, so the disjunction holds. This is **vacuous truth**, and it isn't a defect: it's what makes "all elements of the empty set are prime" true and makes universally quantified statements behave correctly over empty domains. Every `for` loop over an empty list "satisfies" its postcondition for the same reason.

### 3. Contrapositive vs converse

Original: $n^2$ even $\to$ $n$ even. **True.**
- **Converse:** $n$ even $\to n^2$ even. True *here*, but not because of the original
- **Inverse:** $n^2$ odd $\to n$ odd. True, and equivalent to the converse
- **Contrapositive:** $n$ odd $\to n^2$ odd. **True, and always logically equivalent to the original**

**Proof via contrapositive:** let $n$ be odd, $n = 2k+1$. Then $n^2 = 4k^2+4k+1 = 2(2k^2+2k)+1$, odd. ∎

**Only the contrapositive is guaranteed equivalent.** Confusing a statement with its converse is the single most common informal-reasoning error — "all fraud has these signals" does not give you "all these signals are fraud", and that mistake has shipped in real classifiers.

---

## Part B — Proof techniques

### 4. Sum of two odds

Let $a = 2m+1$, $b = 2n+1$. Then $a+b = 2m+2n+2 = 2(m+n+1)$, which is even by definition. ∎

**The whole technique in a line: unfold the definitions, do algebra, fold back into the target definition.**

### 5. $\sqrt2$ irrational — and where it breaks for $\sqrt4$

Suppose $\sqrt2 = a/b$ in lowest terms. Then $a^2 = 2b^2$, so $a^2$ is even, so **$a$ is even** (by exercise 3's contrapositive). Write $a = 2k$: $4k^2 = 2b^2$, so $b^2 = 2k^2$, so $b$ is even too. But then $a/b$ was not in lowest terms — contradiction. ∎

$\sqrt3$ is the same argument with "divisible by 3", relying on: if $3 \mid a^2$ then $3 \mid a$.

**For $\sqrt4$ the argument breaks at exactly one step: "$a^2$ divisible by 4 $\Rightarrow$ $a$ divisible by 4" is false** — take $a=2$, $a^2=4$. That implication holds when the divisor is **prime** (by Euclid's lemma) and fails otherwise.

**That step is doing all the work**, and noticing it is the exercise. The general theorem: $\sqrt n$ is irrational unless $n$ is a perfect square.

### 6. Contrapositive again

Direct attack: assume $n^2$ odd, try to derive $n$ odd — you get stuck immediately, because you can't factor information *out* of $n^2$ easily.

Contrapositive: assume $n$ even, $n = 2k$, so $n^2 = 4k^2 = 2(2k^2)$ — even. ∎

**Two lines instead of an impasse.** The heuristic worth keeping: **when the hypothesis is about a squared/composed quantity and the conclusion about the base, try the contrapositive.**

### 7. Pigeonhole

**(a)** 13 people, 12 months. $\lceil 13/12 \rceil = 2$. ∎

**(b)** Cut the unit square into four quarters of side $\frac12$. Five points, four quarters ⇒ some quarter holds two. The diagonal of a quarter is $\frac{\sqrt2}{2}$, so those two are at most that far apart. ∎

**The construction is the whole difficulty** — the pigeonhole step is trivial once you decide what the holes are.

**(c) Erdős–Szekeres.** For each element, record a pair (length of longest increasing subsequence ending here, length of longest decreasing). If no monotonic subsequence of length $n+1$ exists, both coordinates lie in $\{1,\dots,n\}$ — only $n^2$ possible pairs for $n^2+1$ elements, so two elements share a pair. But any two distinct elements must differ in at least one coordinate (whichever way they compare). Contradiction. ∎

### 8. Counterexamples

**"Every odd ≥ 3 is prime":** 9 = 3×3.

**"$n^2+n+41$ is always prime":** **$n = 40$** gives $1600+40+41 = 1681 = 41^2$.

**And you can see it without searching:** at $n=41$, every term has a factor of 41, so $41^2+41+41 = 41\cdot43$. Working backwards, $n=40$ also fails. **Euler's polynomial is prime for $n = 0..39$** — forty confirming cases, then failure.

**That's the lesson.** No number of verified cases proves a universal claim. This is the difference between testing and proof, and it's why [[concepts/04-best-practices/04-testing-fundamentals|tests]] show the presence of bugs, not their absence.

---

## Part C — Induction

### 9. The classics

**(a)** Base $n=1$: $1 = \frac{1\cdot2}{2}$ ✓. Step: assume $\sum_{i=1}^{k} i = \frac{k(k+1)}{2}$. Then
$$\sum_{i=1}^{k+1} i = \frac{k(k+1)}{2} + (k+1) = \frac{k(k+1) + 2(k+1)}{2} = \frac{(k+1)(k+2)}{2}$$
which is the formula at $k+1$. ∎

**(c)** $2^n > n^2$ for $n \ge 5$. Base $n=5$: $32 > 25$ ✓. Step: assume $2^k > k^2$. Then $2^{k+1} = 2\cdot2^k > 2k^2$, and $2k^2 \ge (k+1)^2 \iff k^2 - 2k - 1 \ge 0$, true for $k \ge 3$. ∎

**Note the base case is 5, not 1** — it fails at $n=2,3,4$. Choosing the right base is part of the proof, and stating a bound "for $n \ge N$" without checking $N$ is a common slip.

### 10. Strong induction

Every $n \ge 2$ has a prime factorisation. If $n$ is prime, done. Otherwise $n = ab$ with $1 < a,b < n$. **Both $a$ and $b$ are smaller than $n$ but neither is necessarily $n-1$** — so we need the hypothesis for *all* smaller values, which is strong induction. Apply it to $a$ and $b$, concatenate. ∎

**Ordinary induction is awkward because the factors aren't the predecessor.** Whenever a recursive structure splits into arbitrary smaller pieces — mergesort, quicksort, divide-and-conquer generally — strong induction is the natural tool → [[foundations/programming-fundamentals/09-recursion-and-the-call-stack|recursion]].

### 11. All horses

**The step fails at $n=1 \to n=2$.**

For $n+1 \ge 3$ horses, removing one horse and then a different one leaves two overlapping sets of size $n \ge 2$, and the **shared** horse forces both sets to the same colour. For $n+1 = 2$, the two sets are $\{H_1\}$ and $\{H_2\}$ — they share **nothing**, so no colour is transmitted between them.

**Most people say the base case is wrong. It isn't** — one horse genuinely is one colour. **The inductive step is invalid for exactly one value of $n$**, and a chain that breaks at its first link never reaches anything.

**The general lesson: an inductive step that relies on an implicit non-emptiness or overlap must be checked at the smallest case.** The same bug appears in real proofs about intervals, intersections and graph connectivity.

### 12. Loop invariant on binary search

**Invariant:** *if the target is in the array, its index lies in $[\textit{lo}, \textit{hi}]$.*

**Initialisation:** $\textit{lo}=0$, $\textit{hi}=n-1$ covers the whole array. ✓
**Maintenance:** the array is sorted. If `a[mid] < target`, everything at index $\le \textit{mid}$ is $<$ target, so discarding them cannot discard the target; symmetric for $>$. ✓
**Termination:** $\textit{hi}-\textit{lo}$ strictly decreases each iteration, so the loop ends; when $\textit{lo} > \textit{hi}$ the range is empty, and by the invariant the target is absent. ∎

```python
while lo <= hi:
    assert not (target in arr) or lo <= arr.index(target) <= hi   # the invariant, checked
```

**Run it on 1000 random arrays.** This is the exercise that makes the course pay: an invariant is a precise statement about a loop that you can *both* prove and assert. **The overflow bug in `mid = (lo + hi) // 2` that lived in the JDK for nine years was an invariant violation nobody had stated** → [[foundations/dsa/README|DSA]].

---

## Part D — Counting, graphs, number theory

### 13. Count four ways

| | Answer | Order? | Reasoning |
|---|---|---|---|
| (a) Committee of 5 | $\binom{12}{5} = 792$ | No | Unordered selection |
| (b) Pres/Sec/Treas | $12 \cdot 11 \cdot 10 = 1320$ | **Yes** | Distinct roles |
| (c) Committee + chair | $\binom{12}{5}\cdot 5 = 3960$ | Partly | Choose, then designate |
| (d) Groups of 5,4,3 | $\frac{12!}{5!\,4!\,3!} = 27{,}720$ | No, within groups | Multinomial |

**(c) has a second route: $12 \cdot \binom{11}{4} = 12 \cdot 330 = 3960$** — pick the chair first, then four others. Two different-looking computations agreeing is a genuine check on a counting argument, and it's the habit worth building.

### 14. Handshake lemma

Each edge has two endpoints and contributes exactly 1 to the degree of each. Summing degrees counts every edge exactly twice: $\sum_v \deg(v) = 2|E|$. ∎

**Corollary:** $2|E|$ is even, so the degree sum is even. Split it into odd-degree and even-degree vertices; the even-degree part is even, so the odd-degree part must be even too. A sum of odd numbers is even only if there are **an even number of them**. ∎

**"Double counting" — count the same thing two ways and equate — is one of the most powerful proof techniques in combinatorics**, and this is its cleanest example.

### 15. Euler paths

**Rule:** a connected graph has an **Euler circuit** iff every vertex has even degree; an **Euler path** (not circuit) iff exactly **two** vertices have odd degree.

| Graph | Degrees | Verdict |
|---|---|---|
| $K_4$ | all 3 (four odd) | **Neither** |
| $K_5$ | all 4 (even) | **Euler circuit** |
| $K_{3,3}$ | all 3 (six odd) | **Neither** |
| Königsberg | 3,3,3,5 (four odd) | **Neither** |

**Königsberg is the origin of graph theory**, and Euler's insight was precisely that the geography is irrelevant — only the degree parity matters. **Four odd vertices, so no walk crosses every bridge once.** A negative result, proved by counting.

### 16. RSA by hand

$p=11$, $q=13$ ⇒ $n = 143$, $\phi(n) = 10 \times 12 = 120$.

$e = 7$; $\gcd(7,120)=1$ ✓. Extended Euclid gives $d = 103$ (check: $7 \times 103 = 721 = 6\times120 + 1$ ✓).

**Encrypt:** $c = 9^7 \bmod 143 = 48$.
**Decrypt:** $m = 48^{103} \bmod 143 = 9$ ✓

**The infeasible step at 300 digits is computing $\phi(n)$, which requires factoring $n$.** Everything else — modular exponentiation by squaring, the extended Euclidean algorithm — is fast at any size.

**RSA's security is exactly the gap between multiplying (easy) and factoring (believed hard).** Note "believed": there is no proof factoring is hard, and Shor's algorithm factors in polynomial time on a quantum computer → [[foundations/theory-of-computation/08-beyond-p-vs-np|beyond P vs NP]] · [[cybersecurity/05-cryptography/README|cryptography]].

## Related
- [[foundations/discrete-math/09-practice-exercises|the exercises]]
- [[foundations/discrete-math/README|the course]]

*Source: [reference] — RSA and counterexample arithmetic verified computationally, August 2026.*
