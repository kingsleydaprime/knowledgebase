# Partial Fractions

**[Intermediate]** — Splitting a rational function into pieces you already know how to integrate. Algebra in service of calculus.

## Before you start

- You can integrate basic functions, especially $\int\frac{1}{x}dx = \ln|x|$ — [[01-integration-by-parts|integration]].
- You can factorise polynomials — [[03-algebraic-manipulation|algebraic manipulation]].

**What you will be able to do after this lesson:**

1. Explain why a rational function is decomposed before integrating.
2. Decompose a proper fraction with distinct linear factors.
3. Handle repeated factors and irreducible quadratics.
4. Reduce an improper fraction by division before decomposing.

---

## 1. The problem

$$\int \frac{5x - 4}{x^2 - x - 2}\,dx$$

**Nothing in the basic table matches this**, and neither substitution nor parts helps directly.

**But look what happens if it can be split up.** Factor the denominator: $x^2 - x - 2 = (x-2)(x+1)$. Suppose the fraction can be written as

$$\frac{5x-4}{(x-2)(x+1)} = \frac{A}{x-2} + \frac{B}{x+1}$$

**Then the integral is trivial** — each piece is a logarithm:

$$\int\frac{A}{x-2}dx + \int\frac{B}{x+1}dx = A\ln|x-2| + B\ln|x+1| + C$$

**Partial fractions is the algebra that finds $A$ and $B$.** It is not a calculus technique at all — it is a preparation step that turns an unfamiliar integral into familiar ones.

## 2. Distinct linear factors

**Multiply through by the denominator** to clear the fractions:

$$5x - 4 = A(x+1) + B(x-2)$$

**This must hold for every $x$**, which gives two ways to find $A$ and $B$.

**The fast way — substitute the roots**, chosen to kill one term at a time:

- $x = 2$: $\quad 6 = 3A \Rightarrow A = 2$
- $x = -1$: $\quad -9 = -3B \Rightarrow B = 3$

$$\int\frac{5x-4}{x^2-x-2}dx = 2\ln|x-2| + 3\ln|x+1| + C$$

**The systematic way — compare coefficients.** Expanding gives $5x - 4 = (A+B)x + (A - 2B)$, so $A + B = 5$ and $A - 2B = -4$. Solving the pair gives the same answer.

**Use root substitution when the factors are linear; use coefficient comparison when they are not.**

## 3. The three cases

**Case 1 — distinct linear factors.** One term per factor:

$$\frac{f(x)}{(x-a)(x-b)} = \frac{A}{x-a} + \frac{B}{x-b}$$

**Case 2 — a repeated linear factor.** You need a term for *every power* up to the multiplicity:

$$\frac{f(x)}{(x-a)^2} = \frac{A}{x-a} + \frac{B}{(x-a)^2}$$

**Why both terms are needed:** a single $\frac{A}{(x-a)^2}$ cannot produce the $\frac{1}{x-a}$ behaviour that a general numerator requires. Omitting the lower power gives a system with no solution.

**Case 3 — an irreducible quadratic.** A quadratic with no real roots needs a *linear* numerator:

$$\frac{f(x)}{(x^2+1)} = \frac{Ax + B}{x^2+1}$$

**The rule of thumb:** the numerator over each factor has degree one less than that factor.

## 4. Improper fractions must be divided first

**If the numerator's degree is greater than or equal to the denominator's, divide before decomposing.**

$$\frac{x^2}{x-1}$$

Polynomial division gives

$$\frac{x^2}{x-1} = x + 1 + \frac{1}{x-1}$$

and now each piece integrates directly:

$$\int\frac{x^2}{x-1}dx = \frac{x^2}{2} + x + \ln|x-1| + C$$

**Skipping the division produces a system with no solution**, which is the usual symptom that you forgot this step.

> [!NOTE]
> **This is the same idea as improper fractions in arithmetic.** $\frac{7}{3}$ is rewritten as $2 + \frac{1}{3}$ — a whole part plus a proper remainder.
>
> Polynomial division does exactly that for polynomials, and partial fractions then handles the proper part. **The technique has an exact arithmetic analogue**, which is worth holding onto when the algebra feels arbitrary.

## 5. Practice — problems

1. Decompose and integrate: $\int\dfrac{1}{(x-1)(x+2)}dx$.
2. Decompose: $\dfrac{3x+5}{x^2-x-6}$, then integrate.
3. Repeated factor: decompose $\dfrac{2x+3}{(x+1)^2}$ and integrate.
4. Improper: evaluate $\int\dfrac{x^2+1}{x-2}dx$. **What must you do first?**
5. Irreducible quadratic: decompose $\dfrac{x+3}{(x-1)(x^2+1)}$. *(You do not need to integrate it.)*
6. **Explain** why $\frac{A}{(x-2)^2}$ alone cannot represent $\frac{3x+1}{(x-2)^2}$, by trying it and seeing what fails.

<details><summary>Answers — open only after an attempt</summary>

1. $\frac{A}{x-1}+\frac{B}{x+2}$ with $1 = A(x+2)+B(x-1)$. At $x=1$: $A=\frac13$. At $x=-2$: $B=-\frac13$. Integral: $\frac13\ln\left|\frac{x-1}{x+2}\right| + C$.
2. $x^2-x-6 = (x-3)(x+2)$. At $x=3$: $14 = 5A$, $A = \frac{14}{5}$. At $x=-2$: $-1 = -5B$, $B = \frac15$. Integral: $\frac{14}{5}\ln|x-3| + \frac15\ln|x+2| + C$.
3. $\frac{A}{x+1}+\frac{B}{(x+1)^2}$ with $2x+3 = A(x+1)+B$. At $x=-1$: $B=1$. Comparing $x$ coefficients: $A=2$. Integral: $2\ln|x+1| - \frac{1}{x+1} + C$.
4. <strong>Divide first</strong> — the degrees are equal-or-greater. $\frac{x^2+1}{x-2} = x + 2 + \frac{5}{x-2}$. Integral: $\frac{x^2}{2} + 2x + 5\ln|x-2| + C$.
5. $\frac{A}{x-1} + \frac{Bx+C}{x^2+1}$. At $x=1$: $4 = 2A$, so $A=2$. Comparing coefficients gives $B=-2$, $C=-1$: $\frac{2}{x-1} + \frac{-2x-1}{x^2+1}$.
6. Trying $\frac{A}{(x-2)^2}$ requires $A = 3x+1$ — but $A$ is a <em>constant</em> and the right side varies with $x$. No constant works. <strong>The $\frac{A}{x-2}$ term supplies the $x$-dependence</strong>, which is why every power up to the multiplicity is needed.
</details>

## Before moving on

- [ ] Explain why decomposition makes a rational function integrable.
- [ ] Decompose with distinct linear factors, using root substitution.
- [ ] Handle a repeated factor and say why every power is needed.
- [ ] Recognise an improper fraction and divide before decomposing.

**Recap:** Partial fractions splits a rational function into simpler fractions whose integrals are logarithms or arctangents. Distinct linear factors give one term each and are solved fastest by substituting the roots; repeated factors need a term for every power up to the multiplicity; irreducible quadratics need a linear numerator. Improper fractions must be reduced by polynomial division first — the exact analogue of rewriting $\frac{7}{3}$ as $2 + \frac{1}{3}$.

**Next:** [[03-applications|Applications of Integration]] — using integrals to compute quantities rather than to reverse derivatives.

## Related

- [[01-integration-by-parts|Integration and integration by parts]]
- [[03-algebraic-manipulation|Algebraic manipulation]] — the factorisation this depends on
