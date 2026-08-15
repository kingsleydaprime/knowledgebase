# Linear Elasticity

**[Intermediate → Advanced]** — Two constants, one linear PDE, and most of structural engineering. The special case that carries the field.

## The assumptions

Linear elasticity stacks four simplifications, and knowing which one you're violating is the skill:

1. **Small strain** — under ~1%, so the linearised strain tensor applies
2. **Small rotation** — reference and deformed geometry are interchangeable
3. **Linear stress–strain** — Hooke's law, fully reversible
4. Usually **isotropic and homogeneous**

What you get in return is enormous: **superposition works**. Solve one load case, solve another, add them. Every closed-form result in structural engineering depends on that.

## Hooke's law

The general anisotropic form:

$$\sigma_{ij} = C_{ijkl}\,\varepsilon_{kl}$$

$C_{ijkl}$ has $3^4 = 81$ components, reduced by symmetries:

- $\sigma_{ij} = \sigma_{ji}$ and $\varepsilon_{ij} = \varepsilon_{ji}$ → 36
- Existence of a strain-energy function ($C_{ijkl} = C_{klij}$) → **21**
- **Isotropy → 2**

That collapse from 21 to 2 is the payoff of [[engineering/01-continuum-mechanics/07-constitutive-models|material symmetry]], and it's why undergraduate mechanics is tractable.

For isotropic materials:

$$\boxed{\sigma_{ij} = \lambda\,\varepsilon_{kk}\,\delta_{ij} + 2\mu\,\varepsilon_{ij}}$$

$\lambda$ and $\mu$ are the **Lamé parameters**; $\mu = G$ is the shear modulus.

Inverted:

$$\varepsilon_{ij} = \frac{1+\nu}{E}\sigma_{ij} - \frac{\nu}{E}\sigma_{kk}\delta_{ij}$$

## The engineering constants

Two independent, but five in common use, and converting between them is a constant chore:

| | Meaning | Steel | Aluminium | Concrete | Rubber |
|---|---|---|---|---|---|
| **$E$** (Young's) | axial stress / axial strain | 200 GPa | 70 GPa | 30 GPa | ~0.01 GPa |
| **$\nu$** (Poisson) | −lateral / axial strain | 0.30 | 0.33 | 0.20 | ~0.4999 |
| **$G$** (shear) | shear stress / shear strain | 80 GPa | 26 GPa | 12 GPa | ~0.003 GPa |
| **$K$** (bulk) | pressure / volume change | 160 GPa | 70 GPa | 17 GPa | ~2 GPa |

The relations:

$$G = \frac{E}{2(1+\nu)} \qquad K = \frac{E}{3(1-2\nu)} \qquad \lambda = \frac{E\nu}{(1+\nu)(1-2\nu)}$$

**Two facts worth carrying:**

**$E$ for steel is ~200 GPa regardless of alloy or heat treatment.** Stiffness comes from atomic bonding, which alloying barely changes. Strength varies by a factor of ten across steels; stiffness doesn't. So **if a part is too flexible, changing steel grade will not help** — you must change geometry. This surprises people constantly.

**$\nu \to 0.5$ means incompressible.** Look at $K = E/3(1-2\nu)$: as $\nu \to 0.5$, $K \to \infty$. Rubber at $\nu = 0.4999$ is essentially incompressible, and that causes **volumetric locking** in finite elements — standard displacement elements go artificially stiff and give nonsense. The fix is mixed or reduced-integration elements, and it's a routine practical problem. → [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]]

**Thermodynamic bounds:** $-1 < \nu < 0.5$. Most materials sit at 0.25–0.35. Cork is ≈0, which is why a cork doesn't bulge when you push it into a bottle. **Auxetic** materials have $\nu < 0$ — they get fatter when stretched, which sounds impossible and is achieved with re-entrant microstructures.

## Navier's equations

Substitute Hooke's law into [[engineering/01-continuum-mechanics/06-conservation-laws|the momentum balance]] and express everything in displacement:

$$\boxed{(\lambda + \mu)\,u_{j,ji} + \mu\,u_{i,jj} + \rho b_i = \rho\,\ddot{u}_i}$$

Three coupled second-order PDEs in three unknowns. **This is the complete statement of linear elastodynamics** — everything else is a special case or a solution technique.

Statically, with no body force, it reduces to a form whose solutions are **biharmonic** ($\nabla^4\phi = 0$), which is why classical elasticity solutions involve Airy stress functions and complex-variable methods.

**Elastic waves** fall straight out, and the two speeds are physically distinct:

$$c_p = \sqrt{\frac{\lambda + 2\mu}{\rho}} \qquad\qquad c_s = \sqrt{\frac{\mu}{\rho}}$$

**P-waves** (pressure, longitudinal) are faster; **S-waves** (shear, transverse) are slower and **cannot travel through fluids**, since fluids have $\mu = 0$.

That last fact is how we know Earth has a liquid outer core: S-waves from earthquakes leave a shadow zone on the far side. A continuum-mechanics result that maps the planet's interior. → [[hardware/README|hardware]] uses the same wave physics for ultrasonic sensing.

## The two-dimensional simplifications

Full 3D is rarely necessary. Two reductions cover most practical work, and **confusing them is a standard error**.

**Plane stress** — a thin plate loaded in its plane. The out-of-plane surfaces are free, so:

$$\sigma_{33} = \sigma_{13} = \sigma_{23} = 0, \qquad \varepsilon_{33} = -\frac{\nu}{E}(\sigma_{11} + \sigma_{22}) \neq 0$$

The plate is free to thin. **Use for:** sheet metal, thin panels, membranes.

**Plane strain** — a long prismatic body, loaded uniformly along its length. The material is constrained axially:

$$\varepsilon_{33} = \varepsilon_{13} = \varepsilon_{23} = 0, \qquad \sigma_{33} = \nu(\sigma_{11} + \sigma_{22}) \neq 0$$

**Use for:** dams, tunnels, retaining walls, a long pipe, a rolling contact line.

> **Thin ⟹ plane stress. Thick or long ⟹ plane strain.** Pick the wrong one and stiffness is off by roughly $1/(1-\nu^2)$ — about 10% for metals, and more importantly the out-of-plane stress is either present or absent, which changes the failure prediction.

The convenient part: the governing equations are identical in form, so **one solution serves both** by substituting $E' = E/(1-\nu^2)$ and $\nu' = \nu/(1-\nu)$ to convert plane stress to plane strain.

**Axisymmetry** is the third reduction — a body of revolution under axisymmetric loading becomes 2D in $(r,z)$. Pressure vessels, pipes, and shafts.

## Saint-Venant's principle

The result that makes engineering practical:

> **Far from the point of load application, the stress distribution depends only on the resultant force and moment, not on the details of how the load was applied.**

Bolt, weld, or clamp a bar — beyond roughly one characteristic dimension from the attachment, the stress field is the same.

**This is why beam theory works.** You don't model the bolt pattern; you apply a resultant and trust that the interesting region is far enough away. It's also why **you must not trust FE stresses at a point load or a fixed constraint** — those are exactly the regions where the principle doesn't apply, and the singular stresses there are artefacts of the idealisation, not predictions.

A point load in a continuum gives infinite stress. Real loads are distributed; the model isn't.

## Stress concentration

Geometry amplifies stress, and the classic result is worth memorising:

An elliptical hole in an infinite plate under uniaxial tension $\sigma_0$ has a maximum stress at the hole edge:

$$\sigma_{max} = \sigma_0\left(1 + \frac{2a}{b}\right)$$

For a **circular hole** ($a = b$), $K_t = 3$. **Three times the nominal stress**, regardless of hole size.

**Two consequences that matter:**

**Size doesn't reduce concentration.** A tiny hole concentrates stress as much as a large one — it's the *shape*, not the scale. (Size matters for fatigue and fracture through other mechanisms, but not for $K_t$.)

**As $b \to 0$ the ellipse becomes a crack and $\sigma_{max} \to \infty$.** Continuum elasticity predicts infinite stress at a crack tip, which is the theory announcing its own limit. Fracture mechanics replaces the stress with the **stress intensity factor** $K$, which is finite and measurable. → [[engineering/01-continuum-mechanics/12-failure-and-yield|Failure and Yield]]

**Design implication:** sharp internal corners are where parts crack. Generous fillets are not cosmetic — going from a sharp corner to a radius can halve the peak stress, and it's the cheapest fix available. Peterson's charts tabulate $K_t$ for standard geometries and are still used daily.

## Strain energy

$$U = \frac{1}{2}\int_V \sigma_{ij}\varepsilon_{ij}\,dV$$

Energy methods give you a second route to every problem, and often a faster one:

**Castigliano's theorem** — deflection at a load point is $\partial U/\partial P$. The quickest way to get a deflection in a frame or truss by hand.

**The principle of minimum potential energy** — the true displacement field minimises total potential energy among all compatible fields. **This is the foundation of the finite element method**, which searches a finite-dimensional space of trial functions for the minimiser. → [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]]

**Virtual work** — the workhorse for deriving element formulations and for hand analysis of frames.

## Uniqueness

For a well-posed problem — a positive-definite stiffness tensor and adequate boundary conditions — **the linear elastic solution is unique** (Kirchhoff's theorem).

That's a strong guarantee and it's why linear elastic FE is reliable: there is one answer, and a converged solution has found it. Nonlinear problems lose this — buckling has multiple equilibria, plasticity is path-dependent, and contact problems can have several solutions. The certainty you get in linear analysis is genuinely special, and it's worth noticing when you leave it behind.

**"Adequate boundary conditions"** means enough to eliminate rigid-body motion. Six constraints in 3D (three translations, three rotations). Fewer, and the stiffness matrix is singular — the most common beginner FE failure, reported as "insufficient boundary conditions" or a solver that simply won't converge.

---

## Related
- [[engineering/01-continuum-mechanics/07-constitutive-models|Constitutive Models]] — where Hooke's law sits among alternatives
- [[engineering/01-continuum-mechanics/09-beams-and-structures|Beams and Structures]] — the engineering specialisations
- [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]] — solving this numerically
- [[engineering/01-continuum-mechanics/README|Continuum mechanics map]]
