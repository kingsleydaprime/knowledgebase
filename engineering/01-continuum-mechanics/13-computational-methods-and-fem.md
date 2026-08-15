# Computational Methods and FEM

**[Advanced]** — How the PDEs actually get solved, and the failure modes that make a plausible-looking result wrong.

## Why numerical methods

[[engineering/01-continuum-mechanics/08-linear-elasticity|Navier's equations]] and [[engineering/01-continuum-mechanics/11-viscous-fluids-and-navier-stokes|Navier–Stokes]] have closed-form solutions only for simple geometries and simple loads. Real parts have holes, fillets, contacts, and mixed materials.

So you discretise: replace a continuous field with a finite set of unknowns, and the PDE with a large algebraic system.

## The finite element method

**The idea in three steps:**

**1. Weak form.** Multiply the governing equation by a test function and integrate by parts. This lowers the required continuity — the strong form needs second derivatives, the weak form needs only first — so you can use simple piecewise-polynomial approximations.

For elasticity, the weak form *is* the **principle of virtual work**:

$$\int_V \sigma_{ij}\,\delta\varepsilon_{ij}\,dV = \int_V \rho b_i\,\delta u_i\,dV + \int_S t_i\,\delta u_i\,dS$$

Internal virtual work = external virtual work, for any admissible virtual displacement.

**2. Discretise.** Divide the domain into elements. Within each, approximate displacement by **shape functions** interpolating nodal values:

$$u_i(\mathbf{x}) = \sum_a N^a(\mathbf{x})\,u_i^a$$

**3. Assemble and solve.** Substituting gives the element stiffness matrix, assembled into a global system:

$$\mathbf{K}\mathbf{u} = \mathbf{f}$$

**A note that connects this to [[engineering/01-continuum-mechanics/03-kinematics-of-deformation|kinematics]]:** because you assume a continuous displacement field, **compatibility is satisfied automatically**. That's the main reason displacement-based elements are the default.

**And the variational view:** the FE solution minimises total potential energy over the space of possible nodal displacements. It's the [[engineering/01-continuum-mechanics/08-linear-elasticity|principle of minimum potential energy]] restricted to a finite-dimensional space — which is why the method converges to the true solution as elements shrink.

## Elements

| | Character |
|---|---|
| **Linear tet (TET4)** | fills any geometry automatically; **overly stiff in bending** |
| **Quadratic tet (TET10)** | mid-side nodes; much better, and the practical default for complex geometry |
| **Linear hex (HEX8)** | superior accuracy per DOF; hard to mesh automatically |
| **Quadratic hex (HEX20)** | best accuracy; expensive to generate |
| **Shell** | thin structures — bending without meshing through thickness |
| **Beam** | 1D members → [[engineering/01-continuum-mechanics/09-beams-and-structures\|Beams]] |

> **Linear tetrahedra are too stiff in bending, and it's a real error, not a subtlety.** A cantilever meshed with TET4 can be 50% too stiff even with a fine mesh, because a constant-strain element cannot represent the linear strain variation bending requires. **Use TET10 or hexahedra for anything where bending matters.** This is one of the most common sources of wrong FE answers, and it's silent.

**Integration** is done numerically at Gauss points. **Full integration** is exact for the polynomial order and can lock. **Reduced integration** is cheaper and fixes locking, at the risk of **hourglassing** — spurious zero-energy deformation modes that look like a wavy mesh pattern in the results. If you see an hourglass pattern, the answer is meaningless.

## The locking family

Three related failures, all producing an artificially stiff result:

**Volumetric locking** — nearly incompressible materials ($\nu \to 0.5$: rubber, plastic metal flow). Elements cannot deform without changing volume, so they lock up. **Fix:** mixed u–p formulations, selective reduced integration, F-bar. → [[engineering/01-continuum-mechanics/10-finite-deformation|Finite Deformation]]

**Shear locking** — thin elements in bending develop spurious shear strain. **Fix:** reduced integration, incompatible modes, or use shell elements.

**Membrane locking** — curved shells, similar mechanism.

**The symptom is always the same: results far stiffer than reality.** If your rubber seal model is inexplicably rigid, or your thin plate deflects a tenth of what hand calculation says, suspect locking before suspecting the physics.

## Verification and validation

The distinction that matters, and the one most often skipped.

**Verification — "am I solving the equations right?"**

- **Mesh convergence.** Refine and re-solve. If the answer changes significantly, you haven't converged. **This is non-negotiable and routinely skipped.** A single-mesh result is an opinion
- Check against analytical solutions for simplified cases
- Check equilibrium: do reaction forces sum to the applied load?
- Check energy balance

**Validation — "am I solving the right equations?"**

- Compare against experiment
- Is the constitutive model valid in the regime you reached?
- Are the boundary conditions physically real?

**A converged solution to the wrong problem is still wrong**, and it will have smooth, professional-looking contours.

### The mesh convergence pattern

```
displacement
    │            ╭──────────  ← converged
    │        ╭───╯
    │    ╭───╯
    │ ╭──╯
    └─────────────────────→  elements
```

Refine until the quantity you care about changes by less than a few percent. **Note that displacement converges much faster than stress** — a mesh that gives good deflection can still be badly wrong on peak stress, because stress is a derivative of the displacement field and derivatives converge more slowly.

**Stress singularities never converge.** At a re-entrant corner or a point load, refining the mesh makes the peak stress climb indefinitely — the continuum solution genuinely is infinite there. Reporting "maximum stress" from such a location is meaningless. Either model the real fillet radius, or use [[engineering/01-continuum-mechanics/12-failure-and-yield|fracture mechanics]], or evaluate stress away from the singularity per [[engineering/01-continuum-mechanics/08-linear-elasticity|Saint-Venant]].

## The other methods

**Finite difference (FDM)** — approximate derivatives on a structured grid. Simple, fast, and poor with complex geometry. Common in wave propagation and some CFD.

**Finite volume (FVM)** — integrate over control volumes, enforcing conservation cell by cell. **Conservative by construction**, which is why it dominates CFD.

**Boundary element (BEM)** — discretise only the boundary. Excellent for infinite domains (acoustics, soil–structure interaction), and it produces dense matrices, so it scales badly.

**Meshfree / SPH** — no mesh, just particles. Suited to extreme deformation, free surfaces, fragmentation. Less accurate, harder to impose boundary conditions.

**Isogeometric analysis** — use the CAD NURBS basis directly as shape functions. Removes the meshing step and the geometry approximation error. Promising, not yet mainstream.

**The split worth remembering: FEM for solids, FVM for fluids.** Both solve continuum equations; the difference is that conservation is structurally guaranteed in FVM, which matters more when the equations are conservation laws in the first place.

## Nonlinear and dynamic solution

**Nonlinear** — Newton–Raphson with load increments, as in [[engineering/01-continuum-mechanics/10-finite-deformation|Finite Deformation]]. The tangent stiffness is reformed each iteration.

**Dynamics** splits into two very different worlds:

**Implicit** (Newmark, HHT) — solve a system each step. **Unconditionally stable**, so large time steps are allowed; each step is expensive. Use for structural dynamics, earthquake response, anything where the response is smooth and the duration is long.

**Explicit** (central difference) — no system solve; each step is cheap. **Conditionally stable** — the step must satisfy the CFL condition:

$$\Delta t < \frac{L_{min}}{c}$$

the time for a wave to cross the smallest element. That's typically microseconds, so it's only viable for short events.

**Use explicit for:** impact, crash, blast, explosive forming, high-rate metal forming.
**Use implicit for:** everything slower.

**The practical consequence of CFL:** one tiny element anywhere in your mesh sets the global time step and can make an explicit analysis a hundred times more expensive. Mesh quality isn't just about accuracy — **in explicit dynamics, one bad element is a runtime cost**. Mass scaling is the usual (and slightly dishonest) workaround.

## Where results go wrong

In rough order of frequency:

1. **Wrong boundary conditions.** Over-constraining creates artificial stiffness and phantom reaction forces; under-constraining gives a singular stiffness matrix. **The most common error by a wide margin**
2. **No mesh convergence study.** A single mesh is an opinion
3. **Reading stress at a singularity.** Point loads, sharp corners, and constraint edges — all meaningless
4. **Wrong element type.** TET4 in bending
5. **Locking**, unrecognised
6. **Material model outside its valid range.** Linear elastic run predicting stress above yield, reported as though it means something
7. **Units.** Especially the mm–N–MPa vs m–N–Pa mix, and mass density in consistent units. A factor of $10^9$ is entirely achievable
8. **Ignoring geometric nonlinearity** where rotations exceed a few degrees → [[engineering/01-continuum-mechanics/10-finite-deformation|note 10]]

> **The habit that catches most of these: do a hand calculation first.** Estimate the deflection with $PL^3/3EI$ and the stress with $My/I$. If FE disagrees by a factor of ten, one of you is wrong — and it's usually the model. **The hand calculation is not obsolete; it's your only independent check.** → [[engineering/01-continuum-mechanics/09-beams-and-structures|Beams and Structures]]

## Tools

**Commercial:** Abaqus (nonlinear, research-grade), ANSYS (broad), LS-DYNA (explicit/crash), COMSOL (multiphysics), Nastran (aerospace heritage).

**Open source:** **CalculiX** (Abaqus-compatible input syntax), **Code_Aster**, **FEniCS** and **deal.II** (write the weak form directly — excellent for learning), **Elmer**, **OpenFOAM** (the CFD standard).

**Learning recommendation:** **FEniCS** lets you write the weak form in near-mathematical notation and get a solution, which makes the connection between the theory and the code unusually direct. Or write a small 2D linear-elastic FE solver yourself — element stiffness, assembly, boundary conditions, solve. It's a few hundred lines and it removes the black box permanently.

That project would fit the [[build-your-own-x/README|build-your-own-x]] format well, and it's a genuine gap in this vault.

## The honest note

Modern FE software will produce a smooth, colourful, professional-looking result for almost any input, including nonsense. There is no warning for a wrong material model, an unconverged mesh, or a boundary condition that doesn't exist in reality.

**The software solves the equations. Deciding whether they were the right equations remains yours**, and it's the part that requires the rest of this track. → [[engineering/README|the domain note]]

---

## Related
- [[engineering/01-continuum-mechanics/08-linear-elasticity|Linear Elasticity]] — the energy principle FEM implements
- [[engineering/01-continuum-mechanics/10-finite-deformation|Finite Deformation]] — nonlinear solution
- [[engineering/01-continuum-mechanics/09-beams-and-structures|Beams and Structures]] — the hand calculations that check FE
- [[foundations/dsa/05-algorithms/01-algorithms|Algorithms]] — the linear solvers underneath
- [[engineering/01-continuum-mechanics/README|Continuum mechanics map]]
