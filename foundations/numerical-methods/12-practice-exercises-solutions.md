# Practice Exercises — Solutions

> **[Intermediate]** · Worked answers to [[foundations/numerical-methods/11-practice-exercises|note 11]]. **Measured, not estimated**, Python 3.14, August 2026.

---

## Part A — Error and conditioning

### 1. The U-curve

Measured, $f=\sin$, $f'(1)=\cos 1$:

| $h$ | error | | $h$ | error |
|---|---|---|---|---|
| $10^{-1}$ | 4.29e-02 | | $10^{-8}$ | **2.97e-09** ← minimum |
| $10^{-4}$ | 4.21e-05 | | $10^{-10}$ | 5.85e-08 |
| $10^{-6}$ | 4.21e-07 | | $10^{-13}$ | 7.34e-04 |
| $10^{-7}$ | 4.18e-08 | | $10^{-16}$ | 5.40e-01 |

**The two arms:**

**Left (large $h$): truncation error**, $O(h)$ for a forward difference — the error falls linearly, exactly one decade per decade, which you can see in the table.

**Right (small $h$): round-off error**, $O(\varepsilon/h)$. $f(x+h)$ and $f(x)$ agree to more and more digits, so subtracting them cancels the leading digits and you divide the surviving noise by a tiny $h$, amplifying it.

**The minimum is predictable without measuring anything.** Total error $\approx c_1 h + c_2\varepsilon/h$ is minimised at $h \approx \sqrt{\varepsilon} \approx \sqrt{2.2\times10^{-16}} \approx 1.5\times10^{-8}$ — and the measured minimum is at $10^{-8}$.

**The best achievable accuracy is about $\sqrt{\varepsilon} \approx 10^{-8}$, not $10^{-16}$.** You lose half your digits, unavoidably, for this method. That single fact is why central differences ($O(h^2)$, optimum at $\varepsilon^{1/3}$), complex-step differentiation and automatic differentiation exist.

### 2. Break the quadratic formula

$x^2 + 10^8x + 1 = 0$. True small root $\approx -10^{-8}$.

```
naive :  -7.45058059692382812500e-09      ← ~25% wrong
stable:  -1.00000000000000002092e-08      ← correct to ~16 digits
```

**The mechanism is catastrophic cancellation.** $b = 10^8$ and $\sqrt{b^2-4} \approx 10^8$ agree to about 16 significant digits. Subtracting them annihilates every meaningful digit and leaves only representation noise — which is then divided by 2 and reported confidently.

The stable form multiplies numerator and denominator by the conjugate, turning the subtraction into an **addition** of two same-signed quantities. No cancellation.

**The general rule: never subtract two nearly-equal floating-point numbers if algebra can avoid it.** The two expressions are identical over the reals and completely different over floats.

### 3. Hilbert conditioning

Measured, solving $Hx = b$ where the true $x$ is all ones:

| $n$ | max error | correct digits |
|---|---|---|
| 5 | 6.17e-13 | ~12 |
| 8 | 1.37e-07 | ~7 |
| 10 | 7.18e-04 | **~3** |
| 12 | 5.95e-03 | **~2** |

Doubles carry ~16 digits. **At $n=12$ you have two.**

**The rule of thumb: you lose about $\log_{10}\kappa(A)$ digits.** The Hilbert matrix's condition number grows roughly exponentially — $\kappa \approx 10^{5}$ at $n=5$, $10^{13}$ at $n=10$, $10^{16}$ at $n=12$, where it exhausts double precision entirely.

**Nothing was wrong with the algorithm.** Gaussian elimination with pivoting is backward-stable; it returns the exact solution to a slightly perturbed problem. **The problem itself amplifies perturbations** — that's what ill-conditioning *means*, and no algorithm can fix it. Contrast with exercise 7, where the algorithm is at fault.

**Always compute $\kappa$ before trusting a linear solve.**

### 4. Non-associative addition

Summing $10^7$ copies of `0.1` (exact answer $10^6$):

- **Left to right** — worst. The accumulator grows large while each addend stays small, so each addition rounds away a bit of the small value
- **Ascending order** — better, for the same reason in reverse: add small things together first, while the accumulator is comparably sized
- **Kahan summation** — best, essentially exact. It keeps a running compensation term capturing what each addition rounded off, and adds it back

**Floating-point addition is commutative but not associative.** $(a+b)+c \ne a+(b+c)$ in general — which means **summing an array is order-dependent**, and therefore that parallel reductions give different answers than serial ones, and different answers run to run if the reduction order varies. That's a real reproducibility problem in ML training and in [[foundations/gpu-and-parallel-computing/README|GPU]] reductions.

---

## Part B — Solving things

### 5. Race the root-finders

Root of $x^3-2x-5$ near 2.0946, to $10^{-12}$ from $[2,3]$:

| method | iterations | order |
|---|---|---|
| Bisection | ~40 | **linear** — one bit per step |
| Secant | ~7 | superlinear, $\approx 1.618$ |
| Newton | **~5** | **quadratic** |

**You can read the order off your own error sequence.** For Newton, the number of correct digits roughly *doubles* each iteration: 1 → 2 → 5 → 10 → 12. That doubling *is* quadratic convergence, and seeing it in your own output is the exercise.

Bisection needs 40 steps because it gains exactly $\log_{10}2 \approx 0.3$ digits per step — but it is **guaranteed** to converge given a sign change, which the other two are not.

### 6. Break Newton

**(a) Flat derivative:** $x_{n+1} = x_n - f/f'$ with $f' \approx 0$ throws the iterate an enormous distance. It may diverge or land in a different basin entirely.

**(b) Cycles:** $f(x)=x^3-2x+2$ from $x_0=0$ gives $0 \to 1 \to 0 \to 1$ forever. Newton has no notion of progress and will not notice.

**(c) Multiple roots:** on $f(x)=(x-1)^2$, convergence **drops from quadratic to linear** — error halves per step instead of squaring. Because $f'$ vanishes at the root too, the correction is systematically half of what's needed. (The fix is the modified Newton $x - m f/f'$ for known multiplicity $m$.)

**The unifying point: Newton is fast and unsafe.** Production root-finders (Brent's method) hybridise — take the fast step when it stays in the bracket, fall back to bisection when it doesn't. **Guaranteed convergence with fast convergence in the common case** → [[foundations/numerical-methods/03-root-finding|note 03]].

### 7. Pivot, or don't

$10^{-20}x + y = 1$, $x + y = 2$. True answer $x \approx 1$, $y \approx 1$. **$\kappa \approx 2.6$ — this system is perfectly well-conditioned.**

Without pivoting, the multiplier is $1/10^{-20} = 10^{20}$. Eliminating gives $y(1 - 10^{20}) = 2 - 10^{20}$, and in floating point both sides round to $-10^{20}$, so $y = 1$ — fine. Then back-substitution: $x = (1 - y)/10^{-20} = 0/10^{-20} = 0$. **Wrong, and badly.**

Partial pivoting swaps the rows first so the multiplier is $10^{-20}$ rather than $10^{20}$, and everything is exact.

**Contrast this with exercise 3, and the contrast is the lesson.** There, the *problem* was ill-conditioned and no algorithm could help. Here the problem is fine and the *algorithm* was unstable. **Distinguishing those two is the core diagnostic skill of the whole domain** — one is answered by more precision or a reformulation, the other by a better algorithm.

---

## Part C — Approximation and integration

### 8. Runge's phenomenon

Equally-spaced interpolation of $1/(1+25x^2)$: max error is moderate at $n=5$, **worse at $n=10$, far worse at $n=20$** — with wild oscillation near $x=\pm1$ while the middle fits well.

At Chebyshev nodes (clustered toward the endpoints) the error **falls** with $n$, converging nicely.

**More data made the approximation worse.** That's the result worth internalising, and it's genuinely counter-intuitive.

**Why:** the interpolation error carries a factor $\prod(x - x_i)$, which for equally-spaced nodes grows enormously near the interval ends. Chebyshev nodes are exactly the placement that minimises that product's maximum.

**The practical consequence: never fit a high-degree polynomial through equally-spaced data.** Use low-degree piecewise fits (splines) or Chebyshev nodes. This is also why high-degree polynomial regression on evenly-sampled data behaves badly at the edges → [[foundations/numerical-methods/06-interpolation-and-approximation|note 06]].

### 9. Convergence study

$\int_0^1 e^x dx = e - 1$. Halving $h$, the ratio of successive errors:

- **Trapezoid → ≈ 4.** Error $\propto h^2$, so halving $h$ divides error by $2^2$
- **Simpson → ≈ 16.** Error $\propto h^4$, so $2^4$

**This is the most valuable habit in the domain, and it's a self-test that needs no reference answer.** If the theory says $O(h^2)$ and your ratios are 2, your implementation is first-order — you have a bug. If they're erratic, you've hit round-off (the $h$ is too small) or your function isn't smooth enough for the assumed order.

**A method whose observed order doesn't match its claimed order is broken**, and this check finds it in five lines.

### 10. Defeat a quadrature rule

**$1/\sqrt{x}$ on $[0,1]$:** the integral converges (to 2) but the *integrand is unbounded* at 0. Fixed-step rules evaluate at or near $x=0$ and get a huge or infinite value; convergence collapses because the error bounds assume bounded derivatives. **Fix:** substitution to remove the singularity, or a rule that avoids the endpoint (Gauss–Legendre), or adaptive refinement.

**$\sin(100x)$:** ~16 oscillations on $[0,1]$. Any step that doesn't resolve them samples essentially arbitrary points, and the estimate is nonsense until $h$ is small enough — then it converges normally. **Fix:** resolve the frequency, or use a method designed for oscillatory integrands (Filon, Levin).

**Both failures share a cause: the error bounds assume smoothness the integrand doesn't have.** Reading the assumptions is the skill.

---

## Part D — Dynamics and optimisation

### 11. Stiffness

Explicit RK4 on $y' = -1000(y-\cos t) - \sin t$ is stable only for $h \lesssim 2.8/1000$ — roughly $h < 0.0028$. Above that it doesn't lose accuracy gracefully, it **explodes**, error growing without bound.

An implicit/BDF solver takes steps sized by the *accuracy* you asked for, not by stability, and typically needs **orders of magnitude fewer**.

**Stiffness is when stability, not accuracy, dictates the step size.** It arises when the system has widely separated timescales — here a fast decay of rate 1000 alongside slow $O(1)$ dynamics. The fast mode is uninteresting (it dies immediately) but it *governs the step size* for any explicit method.

**Recognising it matters practically:** chemical kinetics, circuits, control systems and stiff PDE discretisations all show it, and "my ODE solver is mysteriously slow" is almost always this → [[foundations/numerical-methods/08-ordinary-differential-equations|note 08]].

### 12. Conditioning and optimisers

Rosenbrock from $(-1.2, 1)$:

- **Gradient descent:** thousands of iterations, or fails to converge in a reasonable budget
- **BFGS:** roughly 20–40

**The explanation is conditioning, not quality.** Rosenbrock's valley is extremely elongated — the Hessian's condition number is large, so the steepest-descent direction points nearly *across* the valley rather than along it. Gradient descent zig-zags, taking tiny useful steps.

BFGS builds an approximation to the inverse Hessian, which **rescales the space** so the valley looks round. In the rescaled coordinates, steepest descent is a good direction.

**This is the same $\kappa$ from exercise 3, in a different costume**, and it's why preconditioning matters, why input normalisation helps neural network training, and why Adam's per-parameter scaling works → [[foundations/numerical-methods/10-numerical-optimisation|note 10]] · [[ai-ml/README|AI & ML]].

## Related
- [[foundations/numerical-methods/11-practice-exercises|the exercises]]
- [[foundations/numerical-methods/README|the course]]

*Source: [reference] — measured August 2026.*
