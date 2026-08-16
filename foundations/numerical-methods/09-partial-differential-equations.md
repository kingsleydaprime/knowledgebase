# Partial Differential Equations

**[Advanced]** — Discretising space as well as time. The CFL condition, and the three method families.

## Classification decides everything

**Second-order PDEs in two variables classify by the discriminant $B^2-4AC$**, and **the class determines which methods work.** This is not taxonomy for its own sake.

| Type | Example | Character |
|---|---|---|
| **Elliptic** ($<0$) | Laplace $\nabla^2u=0$ | **equilibrium** — no time. Information travels everywhere instantly |
| **Parabolic** ($=0$) | heat $u_t = \alpha u_{xx}$ | **diffusion** — smooths out, infinite propagation speed |
| **Hyperbolic** ($>0$) | wave $u_{tt}=c^2u_{xx}$ | **propagation** — finite speed, sharp features **persist** |

**What follows practically:**

**Elliptic** — no marching in time. **Solve one big linear system** for the whole domain at once. → [[foundations/numerical-methods/04-linear-systems|Linear Systems]]

**Parabolic** — march in time, and **diffusion smooths everything**, so solutions are nice. Implicit methods pay off because of stiffness.

**Hyperbolic** — march in time, **shocks and discontinuities survive and can form spontaneously**. Needs special care to avoid spurious oscillations.

> **Navier–Stokes is mixed** — the viscous term is parabolic, the convective term hyperbolic, and the pressure equation elliptic. **That's most of why CFD is hard**, and why solvers are built around operator splitting. → [[engineering/01-continuum-mechanics/11-viscous-fluids-and-navier-stokes|Navier–Stokes]]

## Finite differences

**Replace derivatives with difference quotients on a grid.**

$$u_{xx} \approx \frac{u_{i+1} - 2u_i + u_{i-1}}{\Delta x^2}$$

**The heat equation, explicitly:**

$$u_i^{n+1} = u_i^n + \frac{\alpha\Delta t}{\Delta x^2}\left(u_{i+1}^n - 2u_i^n + u_{i-1}^n\right)$$

**Simple to write, easy to reason about, and restricted to structured grids** — which means simple geometry.

### The CFL condition

**The stability constraint that governs explicit time-stepping**, and the single most important practical fact in this note.

**For the explicit heat equation:**

$$\frac{\alpha\Delta t}{\Delta x^2} \leq \frac{1}{2}$$

**For the explicit wave/advection equation:**

$$C = \frac{c\,\Delta t}{\Delta x} \leq 1$$

> **The physical reading of CFL: information must not travel more than one grid cell per time step.** If it does, the numerical scheme cannot see where the information came from, and the solution blows up — not gradually, but exponentially.
>
> **The heat equation's $\Delta x^2$ is brutal.** Halving the grid spacing requires **quartering** the time step, so refining the mesh by 10× costs 10× the cells and **100× the steps — 1000× the work.** This is exactly the [[foundations/numerical-methods/08-ordinary-differential-equations|stiffness]] problem, and it's why implicit methods dominate diffusion problems.

**Implicit schemes remove the constraint.** Backward Euler in time is unconditionally stable — you solve a linear system each step and can take $\Delta t$ as large as accuracy permits.

**Crank–Nicolson** (average of forward and backward) is **second-order in time and unconditionally stable** — the standard choice for diffusion. Its one flaw: it can produce oscillations for very large steps with sharp initial data, since it's only *A*-stable, not *L*-stable.

## Finite volume

**Integrate the PDE over each cell, and work with fluxes across faces.**

$$\frac{d}{dt}\int_{V}u\,dV + \oint_{\partial V}\mathbf{F}\cdot\mathbf{n}\,dS = 0$$

> **The key property: what leaves one cell enters the next, exactly.** Mass, momentum and energy are conserved **to machine precision, by construction** — not approximately, and not dependent on mesh quality.
>
> **This is why finite volume dominates CFD.** For a conservation law, a method that doesn't conserve is producing physically meaningless answers however accurate its local truncation error looks.

**Handles unstructured meshes and complex geometry naturally**, and shocks correctly (Rankine–Hugoniot conditions are satisfied automatically).

**The difficulty is the flux function.** Upwinding, Riemann solvers (Godunov, Roe, HLLC), and flux limiters to avoid oscillations near discontinuities. **Godunov's theorem** says any linear scheme above first order will oscillate near a discontinuity — **so all practical high-resolution schemes are nonlinear**, which is what TVD and ENO/WENO schemes are for.

## Finite elements

**Multiply by a test function, integrate by parts, and solve in a finite-dimensional function space.**

**The weak form** reduces the derivative order — a second-order PDE becomes first-order requirements on the solution, so **you can use simpler basis functions.**

**Assemble** element contributions into a global system $Ku = f$, then solve.

**Why it dominates structural mechanics:**

**Arbitrary geometry** via unstructured meshes.

**Natural boundary conditions** — Neumann conditions fall out of the integration by parts rather than being imposed.

**A rigorous error theory**, with provable convergence rates and a posteriori estimators driving adaptive refinement.

**Higher-order elements** are straightforward — just richer basis functions on the same mesh (*p*-refinement).

**Full treatment in [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|Computational Methods and FEM]]** — this note is the numerical-methods view of where it sits.

**The numerical ingredients FEM needs**, all from earlier notes: **[[foundations/numerical-methods/07-numerical-integration|Gauss quadrature]]** for element integrals, **[[foundations/numerical-methods/04-linear-systems|sparse linear solvers]]** for $Ku=f$, **[[foundations/numerical-methods/05-eigenvalues|eigenvalue solvers]]** for modal analysis, and **[[foundations/numerical-methods/08-ordinary-differential-equations|ODE integrators]]** for transient problems.

## Choosing

| | Finite difference | Finite volume | Finite element |
|---|---|---|---|
| Geometry | **simple only** | arbitrary | **arbitrary** |
| Conservation | not automatic | **exact** | not automatic |
| Discontinuities | poor | **excellent** | needs care |
| Error theory | Taylor-based | moderate | **rigorous** |
| Typical use | simple domains, prototyping | **CFD, shocks** | **structures, elliptic** |
| Ease of implementation | **easiest** | moderate | hardest |

**Spectral methods** deserve a mention: represent the solution in a Fourier or Chebyshev basis. **Exponential ("spectral") accuracy for smooth solutions on simple domains** — dramatically better than any of the above. **Useless for discontinuities** (Gibbs oscillations) and awkward for complex geometry. Used heavily in turbulence research and weather modelling.

## Boundary conditions

**Getting these wrong is the most common source of a wrong-but-plausible answer.**

**Dirichlet** — the value is specified. $u = g$ on the boundary.

**Neumann** — the flux/derivative is specified. $\partial u/\partial n = g$.

**Robin** — a combination. Convective heat transfer is the standard example.

**Periodic** — the domain wraps.

**Two things that catch people:**

**Pure Neumann problems are singular.** If you specify only fluxes, the solution is determined **only up to an additive constant** — the linear system is rank-deficient by one. **You must pin one value or add a constraint**, and forgetting to produces a solver failure that looks mysterious.

**Artificial boundaries need care.** Truncating an infinite domain introduces a boundary that isn't physical. **A naive condition reflects waves back into the domain** and corrupts the solution. Absorbing/non-reflecting boundary conditions or perfectly matched layers (PML) are the fix — standard in electromagnetics and acoustics.

## Verifying a PDE solution

**A plausible picture is not a correct answer**, and this domain makes it easy to produce beautiful wrong results.

**Check conservation.** Total mass/energy should be conserved to the precision your method promises. **The single best sanity check.**

**Mesh refinement study.** Halve $\Delta x$; the error should fall at the theoretical rate. **If it doesn't, something is wrong** — a boundary condition, an order-of-accuracy loss, or a bug.

**Method of manufactured solutions** — the most rigorous practical technique available:

> **Pick a solution you want** — say $u = \sin(\pi x)e^{-t}$. **Substitute it into your PDE** to compute the source term $f$ that would produce it. **Now run your solver with that $f$ and compare against the exact answer you chose.**
>
> **This tests the whole code — discretisation, boundaries, solver, time stepping — against an exact reference, on an arbitrary domain.** It's the standard verification method in computational science and it's underused outside it.

**Compare against an analytic case.** Most classical PDEs have exact solutions for simple geometries.

**Check the CFL number** if explicit. Instability that looks like "the physics blew up" is usually a violated CFL.

## Practical notes

**Use an established solver.** FEniCS/Firedrake (FEM, and remarkably close to writing the weak form directly), deal.II, OpenFOAM (finite volume CFD), PETSc/Trilinos for the linear algebra underneath. **Writing a research-grade PDE solver is a career, not a project.**

**Start in 1D.** Debug the method on a problem you can solve by hand before going to 3D.

**Watch memory in 3D.** A $1000^3$ grid is $10^9$ cells — that's tens of gigabytes per stored field, and you'll have several.

**Prefer implicit for diffusion**, explicit for wave propagation. Diffusion is stiff; hyperbolic problems have a CFL limit set by physics anyway, so explicit is natural.

**Mesh quality matters enormously** in FEM and FV. Highly distorted or high-aspect-ratio elements degrade accuracy and conditioning. **Check element quality metrics before blaming the solver.**

**Non-dimensionalise.** Reynolds number, Péclet number, Courant number — **the dimensionless groups tell you which regime you're in and which terms dominate**, and the discretisation should follow.

---

## Related
- [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]] — the applied treatment, and the domain that asked for this
- [[foundations/numerical-methods/08-ordinary-differential-equations|ODEs]] — time stepping, which PDEs reuse
- [[foundations/numerical-methods/04-linear-systems|Linear Systems]] — the huge sparse solves these produce
- [[foundations/numerical-methods/README|Numerical methods map]]
