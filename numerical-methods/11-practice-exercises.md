# Practice Exercises

> **[Intermediate]** · Twelve short scripts. **This domain's failure mode is producing a plausible number that is wrong — and reading about that doesn't build the instinct.**

This course's own honest note lists six of these; the rest fill the gaps. **Every one is a few dozen lines.** Python with `numpy`/`matplotlib` is easiest, but pure Python works for most, and the arithmetic is the same in any language.

Solutions with measured results in [[foundations/numerical-methods/12-practice-exercises-solutions|note 12]].

---

## Part A — Error and conditioning (notes 01–02)

**1. Plot the U-curve.**
Approximate $f'(1)$ for $f(x)=\sin x$ with the forward difference $(f(x+h)-f(x))/h$, for $h = 10^{-1}$ down to $10^{-16}$. Plot absolute error against $h$ on log axes.
**Done when:** you have a clear **V shape**, you can name which error dominates on each arm, and you can predict where the minimum sits from machine epsilon alone — *before* looking at your plot → [[foundations/numerical-methods/02-floating-point-and-error|note 02]].

**2. Break the quadratic formula.**
Solve $x^2 + 10^8 x + 1 = 0$ with the textbook formula. Compare the small root against the algebraically equivalent stable form $x = -2c/(b + \sqrt{b^2-4ac})$.
**Done when:** the naive small root is visibly wrong, you can quantify the relative error, and you can name the mechanism that destroyed it → [[foundations/numerical-methods/02-floating-point-and-error|note 02]].

**3. Lose digits to conditioning.**
Build the $n \times n$ Hilbert matrix $H_{ij} = 1/(i+j+1)$. Set $x = (1,1,\dots,1)$, compute $b = Hx$, then solve $Hx' = b$ and measure $\|x' - x\|_\infty$, for $n = 5, 8, 10, 12$.
**Done when:** you can state roughly how many correct digits survive at each $n$, and relate that number to $\log_{10}\kappa(H)$ → [[foundations/numerical-methods/04-linear-systems|note 04]].

**4. Make addition non-associative.**
Sum $10^7$ copies of `0.1` left-to-right, then in reverse, then sorted ascending, then with Kahan summation. Compare all four against the exact answer.
**Done when:** you have four different results, and can order them by accuracy *and explain the ordering* → [[foundations/numerical-methods/02-floating-point-and-error|note 02]].

---

## Part B — Solving things (notes 03–05)

**5. Race the root-finders.**
Find a root of $x^3 - 2x - 5$ with bisection, Newton, and secant from the same bracket. Count iterations to $10^{-12}$.
**Done when:** you can state the convergence order of each from your own iteration counts — the error should roughly *square* each step for Newton → [[foundations/numerical-methods/03-root-finding|note 03]].

**6. Break Newton three ways.**
Make Newton fail: (a) start where $f'(x_0) \approx 0$, (b) find a cycle, (c) use a root of multiplicity 2 and watch convergence degrade.
**Done when:** you have all three failures reproduced, and for (c) you can say what the convergence order dropped to and why → [[foundations/numerical-methods/03-root-finding|note 03]].

**7. Pivot, or don't.**
Implement Gaussian elimination **without** pivoting. Solve a system whose first pivot is tiny but nonzero (e.g. $10^{-20}x + y = 1$, $x + y = 2$). Then add partial pivoting.
**Done when:** the unpivoted version returns a badly wrong answer on a *well-conditioned* system, which is the point — **this is an algorithm failure, not a conditioning failure** → [[foundations/numerical-methods/04-linear-systems|note 04]].

---

## Part C — Approximation and integration (notes 06–07)

**8. Reproduce Runge's phenomenon.**
Interpolate $f(x) = 1/(1+25x^2)$ on $[-1,1]$ with polynomials through 5, 10, and 20 **equally spaced** points. Plot. Then repeat at **Chebyshev** nodes.
**Done when:** the equally-spaced error *grows* with more points while the Chebyshev error shrinks. **More data made it worse — that's the lesson** → [[foundations/numerical-methods/06-interpolation-and-approximation|note 06]].

**9. Do a convergence study.**
Integrate $\int_0^1 e^x dx$ with the trapezoid rule and with Simpson's, halving $h$ five times. Compute the ratio of successive errors.
**Done when:** the ratios sit near 4 (trapezoid, $O(h^2)$) and 16 (Simpson, $O(h^4)$). **This is the single most useful habit in the domain** — if your ratio isn't what the theory promises, your implementation is wrong → [[foundations/numerical-methods/07-numerical-integration|note 07]].

**10. Defeat a quadrature rule.**
Integrate something with a singularity ($1/\sqrt{x}$ on $[0,1]$) and something oscillatory ($\sin(100x)$) with your fixed-step rules.
**Done when:** you can say *why* each fails and name the class of method that handles it → [[foundations/numerical-methods/07-numerical-integration|note 07]].

---

## Part D — Dynamics and optimisation (notes 08–10)

**11. Hit the stiffness wall.**
Integrate $y' = -1000(y - \cos t) - \sin t$ with explicit RK4 at fixed steps, and with an implicit/adaptive stiff solver. Count steps and compare stability.
**Done when:** the explicit method either explodes or needs orders of magnitude more steps, and you can state the stability condition that forced it → [[foundations/numerical-methods/08-ordinary-differential-equations|note 08]].

**12. Watch conditioning wreck an optimiser.**
Minimise the Rosenbrock function from $(-1.2, 1)$ with plain gradient descent and with a quasi-Newton method (BFGS). Count iterations.
**Done when:** you have both counts, and can explain the difference in terms of the Hessian's condition number rather than "BFGS is better" → [[foundations/numerical-methods/10-numerical-optimisation|note 10]] · [[foundations/numerical-methods/05-eigenvalues|note 05]].

---

## The habit worth keeping

**Every result in this domain deserves the question: how would I know if this were wrong?**

The three cheap answers, and you should reach for one of them by reflex: **a convergence study** (does the error fall at the promised rate?), **a known case** (does it get the analytic answer right?), and **a residual check** (does $\|Ax - b\|$ actually shrink?).

## Related
- [[foundations/numerical-methods/12-practice-exercises-solutions|Solutions]] — with measured results
- [[foundations/numerical-methods/README|the course]]
- [[foundations/computer-architecture/13-practice-exercises|architecture exercises]] — where the floating point lives

*Source: [reference] — built from this course's own "what would close the gap" list. Results in note 12 measured Aug 2026.*
