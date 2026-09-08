# Practice Exercises

> **[Beginner → Intermediate]** · Sixteen problems, mostly with paper. **Discrete maths is learned by doing proofs, and this course showed you worked ones without ever making you write one.**

That's this course's own diagnosis: *"reading a proof is to writing one what reading code is to writing it — you follow along, it all seems reasonable, and then a blank page defeats you."*

**Rules of engagement:**
- **Paper first.** Typing a proof and writing one are different activities
- **A proof is finished when someone else could follow it**, not when you're convinced
- **Get stuck for at least ten minutes before looking.** The stuck part is the exercise
- Solutions in [[foundations/discrete-math/10-practice-exercises-solutions|note 10]]

**Optional but strongly recommended:** work through Lean's [Natural Number Game](https://adam.math.hhu.de/) alongside these. **It will not let you skip a step**, which is exactly the discipline a blank page doesn't enforce.

---

## Part A — Logic (note 02)

**1. Negate carefully.**
Write the negation of each, in plain English, with no leading "it is not the case that":
(a) *Every student passed at least one exam.*
(b) *There is a number larger than all others.*
(c) *If it rains, the match is cancelled.*
**Done when:** (c) is **not** an if-then statement, and you can say why → [[foundations/discrete-math/02-logic|note 02]].

**2. Show two statements are the same.**
Prove $P \to Q \equiv \lnot P \lor Q$ with a truth table, then explain in one sentence why "if" behaving this way makes *"if 2+2=5 then I am the Pope"* true.

**3. Contrapositive vs converse.**
For *"if $n^2$ is even then $n$ is even"*: write the converse, the inverse and the contrapositive. Determine which are true.
**Done when:** you can state which one is **always** logically equivalent to the original, and have proved the original using it.

---

## Part B — Proof techniques (note 03)

**4. Direct proof.** Prove: the sum of two odd integers is even.

**5. Contradiction.** Prove $\sqrt 2$ is irrational. **Do this without looking.** Then prove $\sqrt 3$ is irrational, and identify precisely where the argument would break for $\sqrt 4$.
**Done when:** you can point at the exact step that fails for a perfect square — **that's the step doing the real work** → [[foundations/discrete-math/03-proof-techniques|note 03]].

**6. Contrapositive.** Prove: if $n^2$ is odd then $n$ is odd. Try it directly first, get stuck, then switch. **The getting-stuck is deliberate.**

**7. Pigeonhole.**
(a) In any group of 13 people, two share a birth month.
(b) Any 5 points in a unit square include two within $\frac{\sqrt2}{2}$ of each other.
(c) In any sequence of $n^2+1$ distinct reals there is a monotonic subsequence of length $n+1$. *(hard)*

**8. Counterexample.** Disprove: *"every odd number ≥ 3 is prime"*, and *"$n^2 + n + 41$ is prime for all $n \ge 0$"*.
**Done when:** you found the second counterexample **by reasoning about the expression**, not by brute force.

---

## Part C — Induction (note 05)

**9. The classics.** Prove by induction:
(a) $\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$
(b) $\sum_{i=1}^{n} i^2 = \frac{n(n+1)(2n+1)}{6}$
(c) $2^n > n^2$ for $n \ge 5$
(d) $n! > 2^n$ for $n \ge 4$

**10. Strong induction.** Prove every integer $\ge 2$ has a prime factorisation. Then explain why ordinary induction is awkward here.

**11. Find the bug.**
Here is a "proof" that all horses are the same colour. Base case $n=1$: trivially true. Inductive step: given any $n+1$ horses, remove one — the remaining $n$ are the same colour by hypothesis; remove a different one — those $n$ are too; so all $n+1$ match.
**Done when:** you can name the exact value of $n$ at which the step fails, and why. **Most people find the flaw in the wrong place** → [[foundations/discrete-math/05-induction-and-recursion|note 05]].

**12. Loop invariant on real code.**
Take binary search **as you would actually write it**. State the invariant, prove initialisation, maintenance and termination. Then **instrument the code with an assertion checking it** and run it on 1000 random inputs.
**Done when:** the assertion holds — or you've found a real bug. This is the exercise that connects the whole course to code you ship.

---

## Part D — Counting, graphs, number theory (notes 06–08)

**13. Count four ways.** From a class of 12: (a) how many ways to pick a committee of 5? (b) a president, secretary and treasurer? (c) a committee of 5 with a designated chair? (d) split into groups of 5, 4 and 3?
**Done when:** you can say for each whether order matters and whether repetition is allowed, **before computing** → [[foundations/discrete-math/06-combinatorics-and-counting|note 06]].

**14. Prove the handshake lemma.** $\sum_{v} \deg(v) = 2|E|$. Then use it to prove the number of odd-degree vertices is always even → [[foundations/discrete-math/07-graph-theory|note 07]].

**15. Euler paths.** Determine which of these have an Euler circuit, an Euler path, or neither, and state the rule you used: $K_4$, $K_5$, $K_{3,3}$, and the Königsberg bridge graph.

**16. RSA by hand.** With $p=11$, $q=13$: compute $n$, $\phi(n)$, choose $e=7$, find $d$ with the extended Euclidean algorithm. Encrypt $m=9$ and decrypt it back.
**Done when:** you recover 9, and can say which step would be infeasible if $p$ and $q$ were 300 digits → [[foundations/discrete-math/08-number-theory-and-modular-arithmetic|note 08]].

---

## Where to go next

**[Project Euler](https://projecteuler.net)** for number theory and combinatorics — the answers are checkable, which is the property paper proofs lack. **Velleman's *How to Prove It*** is the book that actually teaches proof technique rather than assuming it.

## Related
- [[foundations/discrete-math/10-practice-exercises-solutions|Solutions]]
- [[foundations/discrete-math/README|the course]]
- [[foundations/theory-of-computation/09-practice-exercises|ToC exercises]] — proofs, applied to computation

*Source: [reference] — built from this course's own "what would close the gap" list.*
