# Ordinary Differential Equations

**[Intermediate → Advanced]** — Stepping a system forward in time, why RK4 is the default, and what stiffness is.

## The problem

$$\frac{d\mathbf{y}}{dt} = \mathbf{f}(t, \mathbf{y}), \qquad \mathbf{y}(t_0) = \mathbf{y}_0$$

**An initial value problem.** Given the state now and a rule for how it changes, find the state later.

**This is what simulation *is*:**

- **[[engineering/02-control-theory/08-state-space|Control systems]]** — $\dot{x} = Ax + Bu$
- **[[robotics/08-dynamics|Robot dynamics]]** — $M\ddot{q} + C\dot{q} + g = \tau$
- **Orbital mechanics, molecular dynamics, chemical kinetics**
- **Circuit simulation** — SPICE is an ODE solver
- **Epidemic models, population dynamics**
- **Neural ODEs**, and the training dynamics of gradient flow

**Higher-order ODEs become first-order systems** by introducing variables:

$$\ddot{x} + c\dot{x} + kx = 0 \quad\Longrightarrow\quad \begin{cases}\dot{y}_1 = y_2\\ \dot{y}_2 = -cy_2 - ky_1\end{cases}$$

**Which is exactly the [[engineering/02-control-theory/08-state-space|state-space form]]** — same conversion, and every solver assumes it.

## Euler's method

**The simplest thing that works, and the baseline everything is measured against.**

$$y_{n+1} = y_n + h\,f(t_n, y_n)$$

**Take the slope where you are and follow it for a step.**

**Local error $O(h^2)$ per step; global error $O(h)$** over a fixed interval — **first order.** Halving the step halves the error, which is poor.

**Don't use it in production**, but understand it: **every method here is a smarter version of "estimate the slope, take a step".**

**Backward (implicit) Euler:**

$$y_{n+1} = y_n + h\,f(t_{n+1}, y_{n+1})$$

**$y_{n+1}$ appears on both sides** — you must solve an equation each step, usually with [[foundations/numerical-methods/03-root-finding|Newton's method]]. **Much more expensive per step, and unconditionally stable**, which turns out to matter enormously.

## Runge–Kutta

**Evaluate the slope at several points within the step and combine.**

**RK4** — the classic, and the default for non-stiff problems:

$$\begin{aligned}
k_1 &= f(t_n, y_n)\\
k_2 &= f(t_n + h/2,\ y_n + hk_1/2)\\
k_3 &= f(t_n + h/2,\ y_n + hk_2/2)\\
k_4 &= f(t_n + h,\ y_n + hk_3)\\
y_{n+1} &= y_n + \tfrac{h}{6}(k_1 + 2k_2 + 2k_3 + k_4)
\end{aligned}$$

**Fourth-order: global error $O(h^4)$.**

> **Halving the step reduces error by 16×, at 2× the cost.** That's the trade that makes high-order methods win, and it's why RK4 has been the workhorse since 1901. **Four function evaluations per step for four orders of accuracy** — the sweet spot; above order 4 you need more evaluations than orders.

**The weights $(1,2,2,1)/6$ are Simpson's rule.** RK4 is [[foundations/numerical-methods/07-numerical-integration|Simpson's quadrature]] applied to the integral form of the ODE — the connection is exact, not an analogy.

## Adaptive step size

**What production solvers actually do.**

**Compute the step two ways at different orders, compare, and adjust:**

$$\text{err} = |y_{n+1}^{(p)} - y_{n+1}^{(p+1)}| \quad\Longrightarrow\quad h_{new} = h\left(\frac{\text{tol}}{\text{err}}\right)^{1/(p+1)}$$

**Embedded pairs** get the second estimate almost free by reusing the same $k_i$ with different weights:

- **RKF45** (Fehlberg) — the classic
- **Dormand–Prince (DOPRI5)** — **`ode45` in MATLAB, `RK45` in SciPy.** The default everywhere

> **Adaptive stepping is not an optimisation, it's a correctness feature.** A fixed step small enough for the fastest transient wastes enormous effort during the smooth parts; a step sized for the smooth parts misses the transient entirely. **Let the solver choose.**

**Always set both `rtol` and `atol`.** Relative tolerance handles large values, absolute handles components passing through zero — **a pure relative tolerance is meaningless when a state variable is 0.**

## Stiffness

**The concept that determines which solver you need**, and it's poorly explained almost everywhere.

> **A problem is stiff when it contains dynamics on very different timescales, and the fast ones have already died out but still force a tiny step size.**

**The classic example** — a chemical reaction where one species decays in microseconds and another in hours. **After the first microsecond the fast mode is gone**, but an explicit solver must keep taking microsecond steps or it goes unstable.

**The test:** look at the eigenvalues of the Jacobian $\partial f/\partial y$. **The stiffness ratio is $|\lambda_{max}|/|\lambda_{min}|$.** Above ~$10^3$, treat it as stiff. → [[foundations/numerical-methods/05-eigenvalues|Eigenvalues]]

**Why explicit methods fail:**

**Explicit methods have a bounded stability region.** For Euler on $\dot y = \lambda y$, stability requires $|1 + h\lambda| < 1$ — so **$h < 2/|\lambda|$**, set by the *fastest* mode regardless of whether it's still active.

```
 explicit: h limited by the FASTEST timescale
           → millions of steps for a slow simulation

 implicit: h limited by ACCURACY only
           → step at the timescale you care about
```

**Implicit methods are unconditionally stable** (A-stable) — backward Euler is stable for any $h$ on any decaying mode. **You pay a nonlinear solve per step and it's overwhelmingly worth it.**

**The stiff solvers:**

**BDF** (backward differentiation formulae) — multistep, implicit, orders 1–5. **LSODA, CVODE, `scipy`'s `BDF`.**

**Radau IIA** — implicit Runge–Kutta, order 5, **excellent for very stiff problems.**

**Rosenbrock** — linearly implicit; one linear solve per step rather than a full Newton iteration. **Cheaper, good for moderate stiffness.**

**LSODA switches automatically** between stiff and non-stiff modes by detecting stiffness at runtime — **`scipy.integrate.solve_ivp(method='LSODA')` is the right call when you don't know.**

> **The practical tell that you have a stiff problem:** your simulation is taking absurdly small steps, or blowing up, for a system you know is physically stable and slow. **Switch to an implicit method before you optimise anything else.**

## Structure-preserving methods

**Sometimes accuracy per step isn't what you want — you want a conserved quantity to stay conserved.**

**For Hamiltonian systems** (orbits, molecular dynamics, ideal pendulums), a general-purpose solver **drifts in energy** over long integrations. RK4 on a planetary orbit slowly spirals in or out — the *shape* of the solution decays even though each step is accurate.

**Symplectic integrators** preserve phase-space volume and keep energy bounded (oscillating around the true value) **for arbitrarily long integrations.**

**Velocity Verlet** is the standard, and it's remarkably simple:

```
v(t + h/2) = v(t) + (h/2)·a(t)
x(t + h)   = x(t) + h·v(t + h/2)
a(t + h)   = f(x(t + h))
v(t + h)   = v(t + h/2) + (h/2)·a(t + h)
```

**Second-order, time-reversible, symplectic, and one force evaluation per step.**

> **This is why molecular dynamics and orbital mechanics use Verlet rather than RK4** despite RK4 being higher-order. **Long-term qualitative correctness beats short-term accuracy** when you're integrating for millions of steps. Game physics engines use it for the same reason.

**Note symplectic methods require a fixed step** — adaptive stepping destroys the symplectic property.

## Boundary value problems

**Different problem: conditions at both ends rather than an initial state.**

$$y'' = f(x,y,y'), \qquad y(a)=\alpha,\ y(b)=\beta$$

**Beam deflection, steady-state heat, optimal control trajectories.**

**Shooting method** — guess $y'(a)$, integrate as an IVP, and root-find on the mismatch at $b$. **Simple, reuses your IVP solver**, and it can be unstable for sensitive problems.

**Finite differences / collocation** — discretise the whole domain and solve the resulting system simultaneously. **More robust**, and it's what `scipy.integrate.solve_bvp` does. → [[foundations/numerical-methods/09-partial-differential-equations|PDEs]]

## Practical notes

**Use a library.** `scipy.integrate.solve_ivp`, SUNDIALS (CVODE/IDA), DifferentialEquations.jl. **They handle adaptivity, stiffness detection, event location and dense output** — all things you'd get subtly wrong.

**Default to `RK45`. Switch to `BDF` or `LSODA` when it crawls.** That single decision covers most cases.

**Set tolerances explicitly**, both relative and absolute. Defaults are often looser than you want.

**Non-dimensionalise.** A system mixing seconds and nanoseconds is stiff by construction; scaling can remove artificial stiffness entirely.

**Use event detection** rather than checking after each step — solvers can find the exact time a condition is met (a bounce, a threshold crossing) by root-finding on the dense output. `solve_ivp`'s `events` parameter.

**Verify with a conserved quantity.** Energy, momentum, mass. **If it drifts, your step is too large or your method is inappropriate** — and this is the cheapest correctness check available for a simulation.

**Check convergence.** Halve the tolerance; the answer should change by less than the tolerance. **If it doesn't, don't trust it.**

**Beware discontinuities.** A force that switches abruptly (contact, friction reversal, a control saturating) breaks the smoothness every high-order method assumes. **Detect the event, stop, restart** — don't integrate through it. This is a common source of mysterious inaccuracy in [[robotics/09-robot-control|robot simulation]].

---

## Related
- [[foundations/numerical-methods/09-partial-differential-equations|PDEs]] — the same, with space as well as time
- [[engineering/02-control-theory/12-digital-control|Digital Control]] — discretisation from the control side
- [[robotics/08-dynamics|Robot Dynamics]] — what gets integrated
- [[foundations/numerical-methods/README|Numerical methods map]]
