# Interpolation and Approximation

**[Intermediate]** — Fitting a function through data, why high-degree polynomials fail, and the difference between passing through points and getting close to them.

## Two different jobs

**Interpolation** — the curve **passes exactly through** every data point. *Use when the data is exact* — a lookup table, geometric control points, values computed from a known function.

**Approximation / fitting** — the curve **gets close** to the points without passing through them. *Use when the data is noisy* — measurements, experiments, anything with error.

> **Interpolating noisy data is a mistake, and a common one.** You force the curve to reproduce the noise, and it oscillates wildly between points. **If your data has error bars, fit — don't interpolate.**

## Polynomial interpolation

**Through $n+1$ points there is exactly one polynomial of degree $\leq n$.** Unique, guaranteed.

**Lagrange form** is the clean statement:

$$p(x) = \sum_i y_i \prod_{j\neq i}\frac{x-x_j}{x_i-x_j}$$

**Elegant, and numerically poor** — $O(n^2)$ per evaluation and it doesn't update cheaply when you add a point.

**Newton's divided-difference form** builds incrementally and is better conditioned.

**Barycentric form** is what you should actually use: $O(n)$ per evaluation after $O(n^2)$ setup, and **numerically stable.**

### The Runge phenomenon

**The result that kills naive high-degree interpolation.**

Interpolate $f(x) = \frac{1}{1+25x^2}$ at **equally spaced** points on $[-1,1]$:

```
      │      ╱╲                    ╱╲
      │     ╱  ╲                  ╱  ╲     ← interpolant oscillates
      │    ╱    ╲                ╱    ╲       wildly near the ends
   ───┼───╱──────╲──────────────╱──────╲───
      │  ╱        ╲____________╱        ╲
      │ ╱              f(x)             ╲
```

> **The error grows *without bound* as you add points.** Degree 20 is worse than degree 10, which is worse than degree 5. **More data makes it worse** — which is deeply counterintuitive and is why "just fit a higher-degree polynomial" is bad advice.

**Two fixes, and they're different:**

**Chebyshev nodes** — cluster the points near the ends:

$$x_k = \cos\left(\frac{k\pi}{n}\right)$$

**This makes polynomial interpolation converge**, and Chebyshev interpolation is genuinely excellent — near-optimal in the minimax sense, and the basis of `chebfun` and of spectral methods. **The problem was never polynomials; it was equally-spaced points.**

**Splines** — use many low-degree pieces instead of one high-degree polynomial. **The right answer when you don't control where the data sits.**

## Splines

**Piecewise polynomials, joined smoothly.**

**Cubic splines** are the standard: cubic on each interval, with continuous value, first and second derivative at every knot.

**That's $4n$ unknowns and $4n-2$ conditions**, so two more are needed:

- **Natural** — second derivative zero at the ends
- **Clamped** — specified first derivatives at the ends
- **Not-a-knot** — third derivative continuous at the second and penultimate knots. **The usual default** (SciPy, MATLAB)

**Why cubic specifically:** it's the lowest degree giving $C^2$ continuity, and **$C^2$ is what the eye perceives as smooth** — a curvature discontinuity is visible. It's also the minimum-curvature interpolant, which is where the name comes from (a draughtsman's flexible spline).

**Solving for a cubic spline is a tridiagonal system** — $O(n)$, trivially fast. → [[foundations/numerical-methods/04-linear-systems|Linear Systems]]

**Variants worth knowing:**

**Monotone / PCHIP** — preserves monotonicity in the data. **Cubic splines overshoot**; if your data is monotone and physically must stay so (a concentration, a probability), PCHIP is the correct choice.

**B-splines** — a basis with local support, so moving one control point affects only a local region. **The foundation of CAD and of font outlines.**

**NURBS** — rational B-splines, which can represent conic sections exactly. **The standard in CAD and 3D modelling.** → [[foundations/computer-graphics/README|Computer Graphics]]

**Bézier curves** — the graphics/design form, defined by control points the curve generally doesn't pass through. **Every vector graphics tool and font format uses these.**

## Least squares

**For noisy data — minimise the sum of squared residuals.**

$$\min_\beta \|A\beta - y\|^2$$

**Solve with QR or SVD.** → [[foundations/numerical-methods/04-linear-systems|Linear Systems]]

> **Never form the normal equations $A^TA\beta = A^Ty$.** It squares the condition number and halves your accuracy. **This is the single most common numerical error in statistics and ML code**, and the fix is one function call — `numpy.linalg.lstsq`, not `inv(A.T@A)@A.T@y`.

**Why squared errors specifically:** it has a closed-form solution, it's the maximum-likelihood estimator under Gaussian noise, and it's differentiable. **The cost is sensitivity to outliers** — a single bad point can dominate, because the penalty is quadratic.

**Robust alternatives** when outliers are real: $L_1$ (least absolute deviations), Huber loss (quadratic near zero, linear in the tails), or RANSAC. → [[ai-ml/02-ml-engineer/03-classical-ml/README|Classical ML]]

**Regularisation** when the fit is ill-conditioned or over-fitting:

$$\min_\beta \|A\beta - y\|^2 + \lambda\|\beta\|^2 \qquad\text{(ridge / Tikhonov)}$$

**This is exactly the damping in [[robotics/07-jacobians-and-singularities|damped least squares]]** — adding $\lambda I$ bounds the solution near a singularity. Same mathematics, different field's vocabulary.

## Choosing a fit

**The question people skip: what should the model be?**

**Polynomials** — fine for low degree over a small range. **Terrible for extrapolation** — they diverge to $\pm\infty$ immediately outside the data.

**Splines** — excellent interpolation and smoothing. **Meaningless for extrapolation.**

**Physically-motivated forms** — exponential decay, power law, logistic. **Fit these when you know the mechanism**, because the parameters mean something and extrapolation is defensible.

**Fourier / trigonometric** — for periodic data, and **spectrally accurate** for smooth periodic functions.

**Radial basis functions** — scattered data in higher dimensions, where splines get awkward.

> **Extrapolation is a different activity from interpolation, and much more dangerous.** Interpolation is bounded by your data; extrapolation is a claim about the world. **A model that fits perfectly inside the data range tells you nothing about outside it** — which is the numerical-methods version of the point made in [[research/06-analyzing-and-interpreting-results|Analysing Results]].

## Multidimensional

**Regular grids:** bilinear/trilinear (fast, $C^0$ — visible faceting), bicubic ($C^1$, smooth, standard for image resizing).

**Scattered data:** Delaunay triangulation plus linear interpolation, radial basis functions, or kriging (Gaussian process regression) when you want uncertainty estimates too.

**The curse of dimensionality bites hard.** A grid with $m$ points per axis has $m^d$ points — **10 points per axis in 10 dimensions is $10^{10}$.** Above ~4 dimensions, grid methods are dead and you need scattered methods, sparse grids, or a learned model. → [[ai-ml/02-ml-engineer/README|ML]]

## Practical notes

**Plot the fit against the data.** Always. **Residual plots reveal structure the $R^2$ hides** — systematic curvature in the residuals means your model form is wrong, regardless of how good the fit statistic looks.

**Never fit a high-degree polynomial to equally-spaced data.** Runge. Use splines.

**Watch for overshoot** near sharp transitions — cubic splines ring. PCHIP if monotonicity matters.

**Normalise your inputs before fitting a polynomial.** Fitting in $x$ ranging over $[1000, 1010]$ produces a Vandermonde matrix with $\kappa \approx 10^{20}$. **Shift and scale to $[-1,1]$ first** — this alone fixes most polynomial-fitting failures.

**Use the library.** `scipy.interpolate` (`CubicSpline`, `PchipInterpolator`, `interp1d`, `RBFInterpolator`), `numpy.polynomial.chebyshev` — and note `numpy.polyfit` warns about conditioning for a reason.

**Count your parameters.** Fitting 10 parameters to 12 points is not a fit, it's memorisation. → [[ai-ml/02-ml-engineer/04-model-evaluation/README|Model Evaluation]]

---

## Related
- [[foundations/numerical-methods/07-numerical-integration|Numerical Integration]] — built on interpolation
- [[foundations/numerical-methods/04-linear-systems|Linear Systems]] — least squares solved properly
- [[ai-ml/02-ml-engineer/03-classical-ml/README|Classical ML]] — regression as statistical fitting
- [[foundations/numerical-methods/README|Numerical methods map]]
