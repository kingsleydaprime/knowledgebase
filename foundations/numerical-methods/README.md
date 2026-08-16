# Numerical Methods

Computing answers to problems that have no closed form — and knowing how wrong the answer is. **The gap three domains in this vault explicitly said they needed.**

**~14,500 words across 10 notes.** Built August 2026. `[reference]`.

> **The premise:** most equations describing the world can't be solved exactly. No formula for a general quintic, no antiderivative for $e^{-x^2}$, no closed form for Navier–Stokes. **So you approximate — and the discipline is producing an answer close enough, fast enough, with an error you can bound.**
>
> **That last clause is the subject.** Anyone can produce a number; the work is knowing how wrong it is.

## Why this exists

**The vault asked for it by name.** `engineering/README` said *"numerical methods — not yet written; FEM and CFD both need it."* Continuum mechanics listed *"quadrature, linear solvers, stability analysis"* in its gaps. Control theory needs discretisation. ML optimisation runs on conditioning. **The original CS-curriculum audit flagged it as "thin".**

| Already written | Was leaning on this |
|---|---|
| [[engineering/01-continuum-mechanics/13-computational-methods-and-fem\|FEM]] | quadrature, sparse solvers, stability |
| [[engineering/02-control-theory/12-digital-control\|digital control]] | discretisation, ODE integration |
| [[robotics/06-inverse-kinematics\|inverse kinematics]] | Newton's method, damped least squares |
| [[robotics/11-state-estimation-and-filtering\|Kalman filters]] | conditioning, numerical stability |
| [[ai-ml/00-foundations/03-mathematics/04-optimization\|ML optimisation]] | conditioning, line search, convergence |

## Reading order

**02 is the foundation** — everything assumes it. **03–05 are the core**, and **04 is the most-used note here** because almost everything reduces to a linear solve. **06–07 are approximation. 08–09 are differential equations** — what the engineering tracks need. **10 is where ML meets this domain.**

1. [[foundations/numerical-methods/01-why-numerical-methods|Why Numerical Methods]] — **[Intermediate]** — truncation vs rounding error, **conditioning vs stability**, orders of convergence, and why smaller steps eventually make things worse
2. [[foundations/numerical-methods/02-floating-point-and-error|Floating Point and Error]] — **[Intermediate]** — machine epsilon, **catastrophic cancellation**, Kahan summation, forward vs backward error
3. [[foundations/numerical-methods/03-root-finding|Root Finding]] — **[Intermediate]** — bisection, Newton, secant, and **why Brent's method is what you should actually call**
4. [[foundations/numerical-methods/04-linear-systems|Linear Systems]] — **[Intermediate → Advanced]** — **never invert the matrix.** LU, Cholesky, QR, SVD, conditioning, sparse direct vs iterative, preconditioning
5. [[foundations/numerical-methods/05-eigenvalues|Eigenvalues]] — **[Advanced]** — why not the characteristic polynomial, the power method, the QR algorithm, and **why `eigh` beats `eig` for free**
6. [[foundations/numerical-methods/06-interpolation-and-approximation|Interpolation and Approximation]] — **[Intermediate]** — **the Runge phenomenon**, splines, least squares done properly
7. [[foundations/numerical-methods/07-numerical-integration|Numerical Integration]] — **[Intermediate]** — Newton–Cotes, **Gaussian quadrature's factor-of-two**, adaptive rules, Monte Carlo and when dimension forces it
8. [[foundations/numerical-methods/08-ordinary-differential-equations|Ordinary Differential Equations]] — **[Intermediate → Advanced]** — RK4, adaptive stepping, **stiffness**, and why orbital mechanics uses Verlet instead
9. [[foundations/numerical-methods/09-partial-differential-equations|Partial Differential Equations]] — **[Advanced]** — elliptic/parabolic/hyperbolic, **the CFL condition**, finite difference vs volume vs element, and the method of manufactured solutions
10. [[foundations/numerical-methods/10-numerical-optimisation|Numerical Optimisation]] — **[Intermediate → Advanced]** — gradient descent's conditioning dependence, line search, quasi-Newton, SGD and Adam, convexity

## The things worth carrying

1. **Conditioning is a property of the problem; stability is a property of the algorithm.** If your answer is bad, that distinction tells you whether to fix the code or reformulate → [[foundations/numerical-methods/01-why-numerical-methods|01]]
2. **Smaller step sizes eventually make things worse.** Truncation error falls, rounding error rises, and the optimum is around $\sqrt{\epsilon}$ → [[foundations/numerical-methods/01-why-numerical-methods|01]]
3. **Multiplication and division never lose relative precision; subtraction of near-equals can lose all of it.** Most reformulations in this track are rewriting a subtraction away → [[foundations/numerical-methods/02-floating-point-and-error|02]]
4. **Never invert a matrix. Solve.** 3× cheaper, more accurate, and it preserves sparsity → [[foundations/numerical-methods/04-linear-systems|04]]
5. **Never form the normal equations for least squares** — it squares the condition number. Use QR or SVD. **The most common numerical mistake in ML and statistics code** → [[foundations/numerical-methods/04-linear-systems|04]]
6. **$\kappa = 10^k$ means you lose about $k$ digits**, and a small residual doesn't imply a small error → [[foundations/numerical-methods/04-linear-systems|04]]
7. **Never fit a high-degree polynomial to equally-spaced data.** Runge — more points makes it worse → [[foundations/numerical-methods/06-interpolation-and-approximation|06]]
8. **An $n$-point Gaussian rule is exact to degree $2n-1$** — twice what equal spacing buys. It's why FEM uses 2×2 Gauss points → [[foundations/numerical-methods/07-numerical-integration|07]]
9. **Stiffness means the fastest mode dictates your step even after it's died out.** Switch to an implicit method before optimising anything else → [[foundations/numerical-methods/08-ordinary-differential-equations|08]]
10. **CFL: information must not travel more than one cell per time step** — and the heat equation's $\Delta t \propto \Delta x^2$ makes explicit refinement brutally expensive → [[foundations/numerical-methods/09-partial-differential-equations|09]]
11. **Slow gradient descent is usually a conditioning problem, not a learning-rate problem.** Which is why feature scaling matters → [[foundations/numerical-methods/10-numerical-optimisation|10]]
12. **Method of manufactured solutions** — pick the answer, derive the source term, test the whole code against it. The most rigorous verification available → [[foundations/numerical-methods/09-partial-differential-equations|09]]

## Where this connects

| | |
|---|---|
| [[engineering/README\|engineering/]] | **The domain that asked.** FEM, CFD, control discretisation |
| [[ai-ml/00-foundations/03-mathematics/04-optimization\|ML optimisation]] | Note 10 is the numerical view of the same subject |
| [[foundations/computer-architecture/02-data-representation\|data representation]] | IEEE 754, which note 02 builds on |
| [[robotics/README\|robotics/]] | IK, Kalman filtering, dynamics integration |
| [[foundations/gpu-and-parallel-computing/README\|GPU and parallel]] | Where the big linear algebra actually runs |

## The honest note

**`[reference]`, and this domain has a specific failure mode: it is very easy to produce a plausible number that is wrong.**

Unlike a compiler error or a failing test, **a bad numerical result looks exactly like a good one.** The whole discipline is about not being fooled by that, and reading about it doesn't build the instinct.

**The good news is that the reps here are cheap** — every one of these is a short script:

1. **Plot the finite-difference error U-curve.** Compute $f'(x)$ at $h = 10^{-1}$ down to $10^{-16}$ and plot the error. **The V shape is the whole of note 01 in one picture**, and it takes five minutes
2. **Break the quadratic formula.** Solve $x^2 + 10^8x + 1 = 0$ naively and with the stable form. Compare against the true roots
3. **Watch conditioning bite.** Build a Hilbert matrix ($\kappa \approx 10^{10}$ at $n=10$), solve, and measure how many digits survive
4. **Reproduce Runge's phenomenon.** Interpolate $1/(1+25x^2)$ at 5, 10, 20 equally-spaced points and plot. **Then do it at Chebyshev nodes and watch it converge**
5. **Hit a stiffness wall.** Integrate a stiff system with `RK45` and with `BDF`. Compare step counts — it's usually orders of magnitude
6. **Do a convergence study.** Halve the step on anything here and check the error falls at the promised rate. **This is the single most useful habit in the domain**
7. **The books:** Trefethen & Bau's *Numerical Linear Algebra* (outstanding, and readable); Press et al.'s *Numerical Recipes* (dated on some algorithms, excellent on judgement); LeVeque for finite differences and PDEs; Nocedal & Wright for optimisation

**What's missing here:** exercises, complex analysis and contour methods, FFT and spectral methods in depth (only mentioned), interval arithmetic, arbitrary-precision arithmetic, numerical linear algebra at scale (communication-avoiding algorithms), and uncertainty quantification.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Related
- [[engineering/README|Engineering]] — the domain that needed this
- [[foundations/computer-architecture/02-data-representation|Data Representation]] — the floating point underneath
- [[ai-ml/00-foundations/03-mathematics/README|The maths notes]] — linear algebra and calculus at the level ML needs
- [[BUILD-PLAN|Build Plan]]
