# Root Finding

**[Intermediate]** — Solving $f(x)=0$ when there's no formula, and why Newton's method is everywhere despite being unreliable.

## The problem

$$\text{Find } x \text{ such that } f(x) = 0$$

**Enormously more general than it looks**, because *any* equation rearranges into this form. $x = \cos x$ becomes $x - \cos x = 0$.

**Where it shows up in this vault:**

- **[[robotics/06-inverse-kinematics|Inverse kinematics]]** — find joint angles where the pose error is zero
- **[[engineering/02-control-theory/05-stability-and-root-locus|Root locus]]** — roots of the characteristic equation
- **Implicit ODE solvers** — each step solves a nonlinear equation → [[foundations/numerical-methods/08-ordinary-differential-equations|ODEs]]
- **[[ai-ml/00-foundations/03-mathematics/04-optimization|Optimisation]]** — minimising $f$ means finding a root of $f'$
- Internal rate of return, equilibrium points, break-even analysis

## Bisection

**The one that always works.**

**Requires a bracket:** $f(a)$ and $f(b)$ with opposite signs. By the intermediate value theorem, a root lies between them.

```python
while (b - a) > tol:
    c = (a + b) / 2
    if sign(f(c)) == sign(f(a)):  a = c
    else:                          b = c
```

**Each iteration halves the interval.** Error after $n$ steps: $(b-a)/2^n$.

**Guaranteed convergence, linear rate.** To reach $10^{-15}$ from an interval of 1 takes ~50 iterations.

| | |
|---|---|
| **Good** | **cannot fail** if bracketed; needs only sign evaluations; no derivative |
| **Bad** | **slow**; needs a bracket; can't find even-multiplicity roots (no sign change); doesn't generalise to higher dimensions |

> **Use `c = a + (b-a)/2`, not `(a+b)/2`.** The second can overflow for large values and is less accurate. **Same bug as [[foundations/computer-architecture/02-data-representation|binary search]]** — and it's the same fix.

## Newton's method

**The one everybody uses.**

$$x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$$

**The geometry:** follow the tangent line at $x_n$ down to the $x$-axis. That's your next guess.

```
        │    ╱ f(x)
        │   ╱
        │  ╱ ●  ← x_n
        │ ╱ ╱ tangent
   ─────┼────●──────  x_{n+1}
        │
```

**Quadratic convergence** near a simple root:

$$|e_{n+1}| \approx \frac{|f''|}{2|f'|}|e_n|^2$$

**Digits double every iteration.** $10^{-2} \to 10^{-4} \to 10^{-8} \to 10^{-16}$ — **four steps from a rough guess to machine precision**, which is why it dominates.

**And why it fails, which matters just as much:**

**Bad initial guess** → divergence, or convergence to a different root than you wanted.

**$f'(x_n) \approx 0$** → the tangent is nearly flat, the step is enormous, and you're thrown across the number line.

**Cycling** — $f(x) = x^3 - 2x + 2$ from $x_0 = 0$ oscillates between 0 and 1 forever.

**Multiple roots** degrade it to *linear* convergence. (Fixable: $x_{n+1} = x_n - m f/f'$ if you know the multiplicity $m$.)

**Needs $f'$** — analytically, or by automatic differentiation, or approximated.

> **Newton is fast and unreliable. Bisection is slow and certain.** That trade is the whole design space, and **the practical answer is to combine them** — which is what every production root-finder does.

**Newton's fractal** is the vivid demonstration: colour each starting point in the complex plane by which root it converges to, and you get a fractal boundary. **Arbitrarily close starting points converge to different roots.** Sensitivity to the initial guess isn't a rough edge; it's structural.

## Secant method

**Newton without the derivative** — approximate it from the last two points:

$$x_{n+1} = x_n - f(x_n)\frac{x_n - x_{n-1}}{f(x_n) - f(x_{n-1})}$$

**Superlinear convergence**, order $\phi \approx 1.618$ — the golden ratio, which is a pleasing bit of trivia and follows from the error recurrence.

**One function evaluation per step instead of two** (Newton needs $f$ and $f'$), so **in evaluations-per-digit it often beats Newton** when derivatives are expensive.

**Watch for cancellation** in the denominator as the points converge — $f(x_n) - f(x_{n-1})$ is exactly the near-equal subtraction from [[foundations/numerical-methods/02-floating-point-and-error|note 02]].

## Hybrid methods — what to actually use

> **Brent's method is the answer for one-dimensional root finding.** It maintains a bracket (so it **cannot diverge**), and uses inverse quadratic interpolation or the secant method when they're behaving, falling back to bisection when they aren't.
>
> **Superlinear convergence with a guarantee.** This is what `scipy.optimize.brentq`, MATLAB's `fzero`, and Boost's `toms748` implement, and **you should call one of them rather than writing your own.**

**Ridders' method** is a simpler alternative with similar behaviour and is easier to implement if you must.

**The general principle worth carrying beyond this note:** a fast method that can fail, wrapped in a slow method that can't, gives you both. **The same pattern appears in [[engineering/02-control-theory/07-nyquist-and-robustness|robust control]] and in optimisation line searches.**

## Systems of equations

**In $n$ dimensions**, $\mathbf{F}(\mathbf{x}) = \mathbf{0}$, Newton becomes:

$$J(\mathbf{x}_n)\,\Delta\mathbf{x} = -\mathbf{F}(\mathbf{x}_n), \qquad \mathbf{x}_{n+1} = \mathbf{x}_n + \Delta\mathbf{x}$$

**with $J$ the Jacobian.** Note you **solve a linear system each iteration** — you don't invert $J$. → [[foundations/numerical-methods/04-linear-systems|Linear Systems]]

**Everything gets harder:**

**No bracketing exists in $n$ dimensions.** The intermediate value theorem doesn't generalise, so **there's no safety net** — this is the fundamental reason multidimensional root finding is harder than 1-D.

**The Jacobian is $n^2$ evaluations** if approximated by finite differences.

**Near-singular $J$** — the same problem as [[robotics/07-jacobians-and-singularities|singularities in robotics]], and the same fix: **damped least squares / Levenberg–Marquardt**, adding $\lambda I$ to keep the step bounded.

**The practical variants:**

**Line search** — take the Newton *direction* but a shorter step: $\mathbf{x}_{n+1} = \mathbf{x}_n + \alpha\Delta\mathbf{x}$, choosing $\alpha$ so the residual actually decreases. **Turns divergent Newton into convergent Newton**, and costs almost nothing.

**Trust region** — restrict the step to a region where the linear model is believed, adapting the radius based on how well it predicted.

**Broyden's method** — the multidimensional secant: update an approximate Jacobian rather than recomputing it. **Much cheaper per step**, superlinear.

**Continuation / homotopy** — solve an easy problem and deform it into the hard one, tracking the solution. **Genuinely useful when you have no good initial guess**, and it's how hard nonlinear systems in engineering get solved.

## Practical notes

**Bracket if you possibly can.** A guaranteed method is worth a lot, and in 1-D you usually can — plot the function, or scan a grid for sign changes.

**Plot it first.** Ten seconds of plotting reveals multiple roots, flat regions, discontinuities and asymptotes — all things that break solvers silently.

**Set a sensible convergence test.** Three options, and they're not equivalent:
- $|f(x)| < \epsilon_f$ — the residual. **Meaningless if $f$ is badly scaled**
- $|x_{n+1}-x_n| < \epsilon_x$ — the step. Can trigger early if convergence stalls
- **Both**, with relative tolerances. What production solvers do

**Always cap the iterations**, and **return a status.** A solver that silently returns garbage on failure is worse than one that errors.

**Scale your variables** so they're $O(1)$. A solver working on a variable of magnitude $10^9$ and one of $10^{-6}$ simultaneously will have tolerance problems.

**Watch for multiple roots** — convergence degrades to linear and the achievable accuracy drops to about $\sqrt{\epsilon}$, because the function is flat near the root. **You cannot do better; the problem is ill-conditioned.** → [[foundations/numerical-methods/01-why-numerical-methods|Conditioning]]

**Use the library.** `brentq` for bracketed 1-D, `newton` when you have a derivative and a good guess, `fsolve`/`root` for systems, `least_squares` for over-determined problems.

---

## Related
- [[foundations/numerical-methods/04-linear-systems|Linear Systems]] — solved inside every Newton step
- [[foundations/numerical-methods/10-numerical-optimisation|Numerical Optimisation]] — minimisation is root-finding on the gradient
- [[robotics/06-inverse-kinematics|Inverse Kinematics]] — this, applied
- [[foundations/numerical-methods/README|Numerical methods map]]
