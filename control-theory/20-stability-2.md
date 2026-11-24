---
id: a176f59b-0648-4e5e-a9e5-3c28cdcc2eeb
---

# Stability 2: Routh's Special Cases and Stability Design

Routh's table can break in two ways, each with a fix, and with a parameter left as a letter it becomes a design tool.

## Before you start
<!-- bite: 71fa73a0-e8f0-4cec-9076-3235f279f472 -->

You should have read [[control-theory/19-stability-1|19 — Stability 1: What Stability Means and Routh–Hurwitz]], and be able to build a Routh array.

After this lesson you will be able to:

1. handle a zero in the first column with the epsilon method;
2. handle a row of zeros with the auxiliary polynomial, and find the imaginary-axis poles;
3. find the range of a gain or parameter that keeps a system stable;
4. find the frequency at which a marginally stable system oscillates.

## What can go wrong with the Routh array
<!-- bite: 2f2cc2b5-32c2-4b2f-a22c-cfe06736f414 -->

Each new row of the Routh array is built by dividing by the first entry of the row above. Two things stop that working:

1. **A zero appears in the first column**, but the rest of its row isn't zero. You can't divide by zero.
2. **A whole row is zero.** There's nothing left to build the next row from.

Both have standard fixes, from the course notes' chapter 9, and the second one turns out to tell you something useful.

## The kid version
<!-- bite: 023fd2c2-49cb-4132-994d-129b9b4b8d1d -->

You're building a tower of blocks where each layer is cut to fit the one below. If one block comes out with zero width, you can't cut the next layer from it. Trick one: pretend it's a hair's width instead of zero, and carry on. Trick two: if a whole layer vanishes, rebuild it from the shape of the layer just above, which is secretly telling you about a wobble in the tower.

**Where the analogy stops working.** A real tower with a zero-width block just falls. In Routh's array the "hair's width" really works, because the sign changes don't depend on how tiny it is.

## Case 1: a zero in the first column
<!-- bite: 92eefc65-10d5-46ad-9c0b-ff642275ee8d -->

Replace the zero by a tiny positive number $\epsilon$, carry on building the array, then look at the signs as $\epsilon \to 0^+$.

Worked: $s^5 + 2s^4 + 3s^3 + 6s^2 + 5s + 3 = 0$.

| | | | |
| --- | --- | --- | --- |
| $s^5$ | 1 | 3 | 5 |
| $s^4$ | 2 | 6 | 3 |
| $s^3$ | $0 \to \epsilon$ | 3.5 | |
| $s^2$ | $(6\epsilon - 7)/\epsilon$ | 3 | |
| $s^1$ | positive | | |
| $s^0$ | 3 | | |

As $\epsilon \to 0^+$, the $s^2$ entry tends to $-7/\epsilon$: hugely negative. So the first column goes $+, +, +, -, +, +$: **two sign changes, two right-half-plane poles**. (The roots are $-1.67$, $-0.51 \pm 0.70j$ and $0.34 \pm 1.51j$: two on the right, as predicted.)

## Case 2: a row of zeros
<!-- bite: 6556318f-c8d2-4876-9c37-4455f08cf57a -->

A whole row of zeros happens when the polynomial has roots placed **symmetrically about the origin**: pairs like $\pm a$ or $\pm j\omega$. The fix:

1. Take the row **above** the zero row. Its entries are the coefficients of the **auxiliary polynomial** $P(s)$, using every other power of $s$.
2. Differentiate: $dP/ds$.
3. Use the coefficients of $dP/ds$ as the replacement row, and carry on.
4. The roots of $P(s)$ are the symmetric roots of the original polynomial.

## Case 2 worked
<!-- bite: 35ad698a-5d97-40d1-afd4-4160b694c815 -->

$s^5 + 7s^4 + 6s^3 + 42s^2 + 8s + 56 = 0$. The $s^4$ row is $7, 42, 56$, which divided by 7 is $1, 6, 8$. Then the $s^3$ row comes out $0, 0$.

1. Auxiliary polynomial from the $s^4$ row: $P(s) = s^4 + 6s^2 + 8$.
2. $dP/ds = 4s^3 + 12s$, so the new $s^3$ row is $4, 12$ (or $1, 3$).
3. Continue: $s^2$ row $3, 8$; $s^1$ row $1/3$; $s^0$ row $8$. **No sign changes**: no right-half-plane poles.
4. But $P(s) = (s^2 + 2)(s^2 + 4)$, so there are poles at $\pm j\sqrt2$ and $\pm 2j$, on the imaginary axis.

So the system is **marginally stable**, with oscillations at 1.414 and 2 rad/s. The fifth root is $-7$. That's exactly what happened at $K = 6$ in lesson 19.

## Stability design with a parameter
<!-- bite: 89c0aca7-4624-452a-b14f-59a81a3b4584 -->

Leave the design parameter as a letter, build the array, and require every first-column entry to be positive. Lesson 19 did it for a gain $K$. The same works for any parameter.

Back to Block Diagrams 2's nested-loop example, whose characteristic equation was $s^3 + (17 + T)s^2 + (17T + 9)s + 153 = 0$. For which $T$ is it stable? For a cubic, all coefficients must be positive and $a_2a_1 > a_0$:

$$(17 + T)(17T + 9) > 153 \quad\Longleftrightarrow\quad 17T^2 + 298T > 0$$

With the coefficients positive ($T > -9/17$), that means **$T > 0$**. At $T = 0$ the loop sits right on the edge: $(17)(9) = 153$. A quick numerical check agrees: at $T = -0.1$ the largest real part of a root is $+0.05$, at $T = 0.01$ it's $-0.005$.

## Common pitfalls
<!-- bite: 6dcc5342-85e8-42fd-b6e3-359a3145c0db -->

1. **Using $\epsilon < 0$.** The convention is a small positive number; either works if you're consistent, but positive avoids confusion.
2. **Taking the auxiliary polynomial from the zero row.** Use the row *above* it.
3. **Calling a system with a zero row "stable".** Its symmetric roots may sit on the imaginary axis: marginal at best.
4. **Forgetting the coefficient condition.** Every first-column entry must be positive, including those from the original coefficients.

## Check your understanding
<!-- bite: 57ea0d2c-0687-4307-93b1-86bffc96fc45 -->

Try each one before you open the answer.

1. <!-- q: exact id="3b8f0e64" answer="2" -->
   For $s^3 + 2s^2 + 4s + 8$, the $s^1$ row of the Routh array is all zeros. The auxiliary polynomial from the $s^2$ row is $2s^2 + 8$. At what frequency (rad/s) does the system oscillate?

   <details><summary>Answer</summary>

   $2s^2 + 8 = 0$ gives $s = \pm 2j$, so it oscillates at 2 rad/s.

   </details>

2. <!-- q: exact id="d9e15a37" answer="2" -->
   The Routh array of $s^4 + s^3 + 2s^2 + 2s + 3$ has a zero at the start of the $s^2$ row; using $\epsilon$, the first column becomes $1, 1, \epsilon, (2\epsilon - 3)/\epsilon, 3$. How many right-half-plane poles are there?

   <details><summary>Answer</summary>

   As $\epsilon \to 0^+$, the fourth entry tends to $-\infty$. Signs $+, +, +, -, +$: two changes, two right-half-plane poles.

   </details>

3. <!-- q: gap id="6f2a9c81" answers="-6|−6;60" -->
   The characteristic equation $s^3 + 6s^2 + 11s + 6 + K = 0$ is stable for ___ $< K <$ ___.

   <details><summary>Answer</summary>

   Positive coefficients need $K > -6$; the cubic condition $6 \times 11 > 6 + K$ gives $K < 60$.

   </details>

4. <!-- q: exact id="a0c7d3e2" answer="3.3166" sigfigs="3" -->
   For the same system, $s^3 + 6s^2 + 11s + 6 + K = 0$, at $K = 60$ it oscillates. Using the auxiliary polynomial $6s^2 + 66$, at what frequency?

   <details><summary>Answer</summary>

   $s^2 = -11$, so $\omega = \sqrt{11} = 3.32$ rad/s.

   </details>

5. <!-- q: open id="1e8b5f90" -->
   What does a row of zeros in a Routh array tell you about the polynomial's roots, and why is that useful?

   <details><summary>Answer</summary>

   That the polynomial has roots placed symmetrically about the origin, such as $\pm j\omega$ pairs. The auxiliary polynomial (from the row above) contains exactly those roots, so solving it gives any imaginary-axis poles and therefore the frequency of a sustained oscillation, which is how the ultimate period for Ziegler–Nichols is found on paper.

   </details>

## Before moving on
<!-- bite: cdf35ad9-ef42-4b68-a2b5-1c2dc1ec8982 -->

You can handle both special cases and design a parameter for stability. **Next:** [[control-theory/21-root-locus-1|21 — Root Locus 1: Sketching the Locus]], which shows the poles moving as the gain changes.

## Related
<!-- bite: 3cffb58b-ad7c-4261-afdf-598c4fc6c188 -->

- [[control-theory/18-pid-control-2|18 — PID Control 2: Tuning and Implementation]]: the ultimate gain and period.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: e3e96e76-4f7b-42be-9cf3-8c7204094b46 -->

**Level:** Intermediate. **Covers:** the epsilon method, the auxiliary polynomial, imaginary-axis poles, and stability design with a gain or parameter.

**Where it sits:** lesson 20 of 58, part 2 of 2 on Routh's test, before the root locus.

**Source:** the author's course notes, A. M. Hussein, *Control Engineering*, Benha University, chapter 9 (sections 3 to 6); special-case polynomials after N. S. Nise. Roots checked in `scripts/diagrams/control_theory.py`.
