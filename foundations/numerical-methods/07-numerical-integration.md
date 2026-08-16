# Numerical Integration

**[Intermediate]** — Quadrature. Computing $\int f$ when there's no antiderivative, and why Gaussian rules are twice as good as they look.

## Why

**Most integrals have no elementary antiderivative.** $\int e^{-x^2}dx$, $\int \frac{\sin x}{x}dx$, $\int\sqrt{1+x^3}\,dx$ — none of them.

**And in practice $f$ is often not a formula at all** — it's a table of measurements, or the output of a simulation you can only evaluate pointwise.

**Where it appears here:**

- **[[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]]** — every element stiffness matrix is a quadrature. **This is the single biggest consumer**
- **Probability** — expectations, normalising constants, Bayesian evidence → [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/README|Probability]]
- **[[foundations/numerical-methods/08-ordinary-differential-equations|ODE solvers]]** — each step integrates the derivative
- Areas, volumes, centroids, moments of inertia
- **[[foundations/computer-graphics/README|Rendering]]** — the rendering equation is an integral over incoming light

## Newton–Cotes rules

**Interpolate $f$ at equally-spaced points, integrate the interpolant exactly.** That's the whole derivation — it's [[foundations/numerical-methods/06-interpolation-and-approximation|interpolation]] with an integral on top.

**Rectangle (midpoint):** $\int_a^b f \approx (b-a)f\!\left(\frac{a+b}{2}\right)$ — error $O(h^2)$

**Trapezoid:** $\frac{h}{2}(f_0 + 2f_1 + \cdots + 2f_{n-1} + f_n)$ — error $O(h^2)$

**Simpson's:** $\frac{h}{3}(f_0 + 4f_1 + 2f_2 + 4f_3 + \cdots + f_n)$ — **error $O(h^4)$**

> **Simpson's is free accuracy.** Same number of function evaluations as the trapezoid rule, two orders better. **Halving $h$ cuts the error by 16× instead of 4×.**
>
> And a pleasing detail: Simpson's fits a *quadratic* through three points but integrates **cubics** exactly. The odd-order error terms cancel by symmetry — **you get one degree more than you paid for.** The same cancellation is why the midpoint rule matches the trapezoid rule despite using one point instead of two.

**Don't use high-order Newton–Cotes.** Above about degree 8 the weights go negative and the rule becomes unstable — **Runge's phenomenon again**, in integral form. **Use composite low-order rules or Gaussian quadrature instead.**

## Gaussian quadrature

**The insight: don't use equally-spaced points. Choose the points too.**

$$\int_{-1}^{1}f(x)dx \approx \sum_{i=1}^{n} w_i f(x_i)$$

**With $n$ points you have $2n$ free parameters** ($n$ nodes and $n$ weights), so you can make the rule exact for polynomials up to degree $2n-1$.

> **An $n$-point Gaussian rule is exact for degree $2n-1$**, versus degree $n$ for Newton–Cotes with the same count. **Twice the accuracy for the same number of evaluations** — and function evaluations are usually the entire cost.

**The nodes are the roots of the Legendre polynomial $P_n$.** Tabulated, or computed via the Golub–Welsch algorithm (an eigenvalue problem — [[foundations/numerical-methods/05-eigenvalues|note 05]] again).

**Two points integrates cubics exactly. Three points integrates quintics exactly.**

**This is why FEM uses Gauss points.** A quadratic element's stiffness integrand is degree 4-ish, so **2×2 Gauss points suffice in 2D** — and that's exactly what FEM codes use. → [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]]

**Variants for awkward integrands:** Gauss–Chebyshev, Gauss–Laguerre (infinite range with $e^{-x}$ weight), Gauss–Hermite ($e^{-x^2}$ weight — **used for Gaussian expectations in ML and in the [[robotics/11-state-estimation-and-filtering|unscented Kalman filter]]**).

**Gauss–Kronrod** extends an $n$-point Gauss rule with $n+1$ more points, **reusing the originals**, giving a higher-order estimate and therefore an error estimate for free. **This is what adaptive quadrature routines are built on** — `scipy.integrate.quad` is QUADPACK, which is Gauss–Kronrod.

## Adaptive quadrature

**Put the effort where the function is difficult.**

```
integrate(f, a, b, tol):
    coarse = rule(f, a, b)
    m = (a+b)/2
    fine = rule(f, a, m) + rule(f, m, b)
    if |fine - coarse| < tol:
        return fine
    else:
        return integrate(f,a,m,tol/2) + integrate(f,m,b,tol/2)
```

**Recursively subdivide where the estimate disagrees.** A function that's smooth over most of its range and sharp in one place gets refined only where it matters.

**This is what you should call.** `scipy.integrate.quad` handles subdivision, error estimation, singularities and infinite ranges. **Writing your own is an exercise, not a plan.**

**Watch the recursion depth** — a genuine singularity subdivides forever. Cap it and return a status.

## Special cases

**Singularities** — $\int_0^1 \frac{1}{\sqrt{x}}dx$ converges but the integrand is unbounded. **Fixes:** substitution to remove it ($x = t^2$ here), a rule that avoids the endpoint (Gauss doesn't evaluate at endpoints — a real advantage), or **tanh-sinh (double exponential) quadrature**, which handles endpoint singularities remarkably well.

**Infinite ranges** — substitute ($x = t/(1-t)$), or use Gauss–Laguerre/Hermite, or truncate where the integrand is negligible and bound the tail.

**Oscillatory integrands** — standard rules need many points per oscillation and get expensive. **Filon-type methods and Levin's method** handle high frequency specifically.

**Periodic functions** — the **trapezoid rule is spectrally accurate** on a full period. Error decays faster than any power of $h$. **This is genuinely surprising** and it's why FFT-based spectral methods are so effective on periodic domains.

## Monte Carlo

**When dimension defeats everything else.**

$$\int_\Omega f \approx \frac{V}{N}\sum_{i=1}^{N} f(x_i), \qquad x_i \sim \text{Uniform}(\Omega)$$

**Error is $O(N^{-1/2})$** — slow, and **independent of dimension.**

> **That independence is the entire point.** A grid method in $d$ dimensions costs $O(N^{-p/d})$ — it degrades exponentially with dimension. **Monte Carlo doesn't care.**
>
> **Crossover is around $d = 4$–8.** Below that, use quadrature. Above it, Monte Carlo is the only option — which is why it dominates in finance (high-dimensional payoffs), rendering (light paths), and Bayesian inference (posterior integrals over many parameters).

**Variance reduction** is where the practical work is, since $O(N^{-1/2})$ means 100× the samples for 10× the accuracy:

**Importance sampling** — sample where $|f|$ is large, reweight. **The biggest win available.**

**Stratified sampling** — subdivide the domain and sample each region.

**Control variates** — subtract a correlated function you can integrate exactly.

**Quasi-Monte Carlo** — low-discrepancy sequences (Sobol, Halton) instead of random points. **Error approaches $O(N^{-1})$** for smooth integrands. Used heavily in finance and rendering.

**MCMC** for sampling from a distribution you can only evaluate up to a constant — Metropolis–Hastings, HMC, NUTS. **The foundation of practical Bayesian inference.** → [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/README|Probability]]

## Numerical differentiation, briefly

**The opposite operation, and it's worth contrasting because the error behaviour is reversed.**

$$f'(x) \approx \frac{f(x+h)-f(x-h)}{2h} \qquad O(h^2)\text{, central difference}$$

> **Integration is well-conditioned; differentiation is not.** Integration averages, which **smooths noise**. Differentiation amplifies it — noise of size $\eta$ produces derivative error $\eta/h$.
>
> **So there's an optimal $h$** balancing truncation against rounding — around $\sqrt[3]{\epsilon} \approx 10^{-5}$ for central differences — **and you cannot do better.** → [[foundations/numerical-methods/02-floating-point-and-error|The error U-curve]]

**The better options when you need derivatives:**

**Automatic differentiation** — exact to machine precision, no step size. **This is what every ML framework does**, and it's why gradients in PyTorch are trustworthy in a way finite differences aren't. → [[ai-ml/02-ml-engineer/05-deep-learning/README|Deep Learning]]

**Complex-step differentiation** — $f'(x) \approx \text{Im}[f(x+ih)]/h$. **No subtraction, so no cancellation**, and you can take $h = 10^{-200}$. Requires $f$ to accept complex input, and it's a genuinely elegant trick worth knowing.

**Symbolic differentiation** — SymPy, when the expression is manageable.

## Practical notes

**Use `scipy.integrate.quad`** for 1-D. It's QUADPACK, it's adaptive, and it returns an error estimate. **Read that estimate** — it's the whole point.

**Check the error estimate**, don't just take the value.

**Transform away singularities and infinite ranges** before integrating, or use a routine that handles them (`quad` accepts `np.inf`).

**Exploit smoothness.** Gaussian quadrature converges spectacularly on smooth integrands and no better than anything else on rough ones. **If $f$ has a kink, split the interval at the kink** — one line of code, and it recovers the full convergence rate.

**Above ~4 dimensions, switch to Monte Carlo** and invest in variance reduction rather than raw sample count.

**Test on something you know.** Integrate a polynomial your rule should handle exactly and confirm you get the exact answer to machine precision. **It catches implementation errors immediately.**

---

## Related
- [[foundations/numerical-methods/06-interpolation-and-approximation|Interpolation]] — quadrature rules are integrated interpolants
- [[foundations/numerical-methods/08-ordinary-differential-equations|ODEs]] — integration in time
- [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]] — the biggest consumer of Gauss points
- [[foundations/numerical-methods/README|Numerical methods map]]
