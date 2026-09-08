# Why Numerical Methods

**[Intermediate]** — Computing answers to problems that have no closed form, and the two things that separate a working algorithm from one that returns confident nonsense.

**Source:** `[reference]` — see [[foundations/numerical-methods/README|the domain note]].

## The premise

**Most equations that describe the world cannot be solved exactly.**

You learned to solve $ax^2+bx+c=0$ with a formula. **There is no such formula for a general polynomial of degree 5 or higher** — that's Abel–Ruffini, and it's a theorem, not a gap in the syllabus.

It gets worse quickly:

- **$x = \cos(x)$** — no closed form
- **$\int_0^1 e^{-x^2}dx$** — no elementary antiderivative
- **Navier–Stokes** — existence and smoothness is an open Millennium Prize problem → [[engineering/01-continuum-mechanics/11-viscous-fluids-and-navier-stokes|Navier–Stokes]]
- **A 10,000×10,000 linear system** — Cramer's rule is exact and would take longer than the universe has existed
- **Almost any real PDE** with real boundary conditions

> **So you approximate.** Numerical methods is the discipline of computing an answer close enough to the true one, **fast enough to be useful, with an error you can bound.**
>
> **That last clause is the whole subject.** Anyone can produce a number. The work is knowing how wrong it is.

## Where this already matters to you

**The vault has been leaning on this domain without having it:**

| Already written | Depends on |
|---|---|
| [[engineering/01-continuum-mechanics/13-computational-methods-and-fem\|FEM]] | quadrature, linear solvers, stability |
| [[engineering/02-control-theory/12-digital-control\|digital control]] | discretisation, ODE integration |
| [[robotics/06-inverse-kinematics\|inverse kinematics]] | Newton's method, damped least squares |
| [[robotics/11-state-estimation-and-filtering\|Kalman filters]] | matrix conditioning, numerical stability |
| [[ai-ml/00-foundations/03-mathematics/04-optimization\|ML optimisation]] | gradient descent, conditioning, line search |
| [[engineering/01-continuum-mechanics/README\|continuum mechanics]] | **says so explicitly in its gaps section** |

**`engineering/README` names it outright: *"not yet written; FEM and CFD both need it."*** This track is that.

## The two failure modes

**Every numerical result carries error from two distinct sources, and confusing them is the most common conceptual mistake.**

### Truncation error — the method is approximate

**You replaced an exact operation with an approximate one.**

$$f'(x) \approx \frac{f(x+h) - f(x)}{h}$$

**The true derivative is the limit as $h\to0$.** You used a finite $h$, so you're wrong by $O(h)$ — and Taylor tells you exactly how wrong:

$$\frac{f(x+h)-f(x)}{h} = f'(x) + \frac{h}{2}f''(\xi)$$

**Smaller $h$ means less truncation error.** Obviously.

### Rounding error — the arithmetic is approximate

**Floating point has finite precision**, so every operation introduces relative error around $10^{-16}$ for a `double`. → [[foundations/computer-architecture/02-data-representation|Floating Point]]

**In that same difference quotient**, $f(x+h)$ and $f(x)$ are nearly equal for small $h$. Subtracting them is **catastrophic cancellation** — you lose most of your significant digits, then divide by a tiny $h$, which amplifies what's left.

**Smaller $h$ means *more* rounding error.**

### The two fight

```
 error
   │╲                              ╱
   │ ╲  rounding                ╱  truncation
   │  ╲    O(ε/h)            ╱      O(h)
   │   ╲                  ╱
   │    ╲______________╱
   │         ↑ optimal h ≈ √ε ≈ 1e-8
   └──────────────────────────────→ h (decreasing →)
```

> **You cannot make the error arbitrarily small by shrinking $h$.** Below about $\sqrt{\epsilon} \approx 10^{-8}$, rounding dominates and **the answer gets worse.**
>
> **This is the first genuinely surprising result in the subject**, and it's a five-minute experiment: compute a numerical derivative at $h = 10^{-1}, 10^{-2}, \ldots, 10^{-16}$ and plot the error. **The U-shape is real and you should see it yourself once.**

## Conditioning and stability

**The two words that matter most**, and they describe different things.

**Conditioning is a property of the *problem*.** How much does the answer change when the input changes?

$$\kappa = \frac{\text{relative change in output}}{\text{relative change in input}}$$

**Well-conditioned** — small input perturbations give small output changes. **Ill-conditioned** — small perturbations give large changes.

**Stability is a property of the *algorithm*.** Does it amplify rounding errors beyond what the problem's conditioning requires?

| | Well-conditioned problem | Ill-conditioned problem |
|---|---|---|
| **Stable algorithm** | ✅ accurate | ⚠️ inaccurate — **and that's not the algorithm's fault** |
| **Unstable algorithm** | ⚠️ inaccurate — **fixable** | ❌ hopeless |

> **The distinction is practical, not pedantic.** If your answer is bad, you need to know whether to *fix your code* or *reformulate the problem*. **A stable algorithm on an ill-conditioned problem is doing the best anyone can** — no amount of cleverness helps, and the honest response is to change the problem or accept the uncertainty.

**The classic ill-conditioned example**, Wilkinson's polynomial:

$$p(x) = (x-1)(x-2)\cdots(x-20)$$

**Perturb one coefficient by $2^{-23}$** — about one part in $10^{7}$ — **and the roots move by up to 3.** Some become complex. **The problem is inherently ill-conditioned**; no root-finder can do better.

**Condition numbers you'll meet:**

- **Matrix:** $\kappa(A) = \|A\|\,\|A^{-1}\|$. **$\kappa = 10^k$ means you lose about $k$ digits.** → [[foundations/numerical-methods/04-linear-systems|Linear Systems]]
- **Root finding:** ill-conditioned near a multiple root, where the function is flat
- **Subtraction:** ill-conditioned when the operands are nearly equal — cancellation again

## Orders of convergence

**How fast does the error shrink as you do more work?**

**For iterative methods**, with $e_k$ the error at step $k$:

$$|e_{k+1}| \approx C|e_k|^p$$

| $p$ | Name | Behaviour |
|---|---|---|
| 1 | **linear** | error × constant each step — bisection |
| 1.6 | superlinear | secant method |
| **2** | **quadratic** | **digits double each step** — Newton |

**Quadratic convergence is dramatic:** $10^{-2} \to 10^{-4} \to 10^{-8} \to 10^{-16}$. **Four iterations from 1% error to machine precision.** It's why Newton's method is everywhere.

**For discretisation methods**, error scales with step size:

$$\text{error} = O(h^p)$$

**$p$ is the order of accuracy.** Halving $h$ reduces error by $2^p$ — so a fourth-order method gains 16× from a step-size halving that costs 2× the work. **This is why high-order methods win**, up to the point where rounding takes over.

## The practical mindset

**Six habits that separate people who trust numerical output from people who should:**

**1. Always ask how wrong it is.** A number without an error estimate is a rumour. Many algorithms can give you one cheaply.

**2. Sanity-check against something.** A known analytic case, a coarser method, a conservation law that should hold, or a different library.

**3. Test convergence empirically.** Halve the step size. **Does the error fall by the factor the theory promises?** If not, either your implementation is wrong or your assumptions are.

**4. Watch for the warning signs.** NaN, Inf, a residual that stops decreasing, results that change wildly with a tiny parameter change, a condition number in the millions.

**5. Prefer library implementations.** LAPACK is forty years of accumulated numerical care. **Your Gaussian elimination will be slower and less stable**, and the gap is not small.

**6. Understand the method you're calling.** Not to reimplement it — to know its failure modes, its cost, and what its parameters mean. **That's what this track is for.**

## Reading this track

**02 is the foundation** — floating point and error analysis. Everything else assumes it.

**03–05 are the linear algebra core** — root finding, linear systems, eigenvalues. **04 is the single most used note here**, because almost everything reduces to solving $Ax=b$.

**06–07 are approximation** — interpolation and quadrature.

**08–09 are differential equations** — ODEs then PDEs. **This is what continuum mechanics and control theory need.**

**10 is optimisation**, which is where ML meets this domain.

**Prerequisites:** calculus (Taylor series especially), [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|linear algebra]], and [[foundations/computer-architecture/02-data-representation|floating point]]. **Taylor series is the tool the whole subject runs on** — nearly every method and every error bound comes from truncating one.

---

## Related
- [[foundations/numerical-methods/02-floating-point-and-error|Floating Point and Error]] — the foundation
- [[foundations/numerical-methods/04-linear-systems|Linear Systems]] — the most-used note here
- [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]] — the domain that asked for this
- [[foundations/numerical-methods/README|Numerical methods map]]
