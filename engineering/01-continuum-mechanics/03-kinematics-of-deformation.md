# Kinematics of Deformation

**[Intermediate → Advanced]** — Describing motion without any physics. Pure geometry, and the source of most of the field's notational baggage.

## The two configurations

A body occupies a region of space. It moves and deforms. To describe that, you need two pictures:

```
   REFERENCE (undeformed)              CURRENT (deformed)
        t = 0                              t = t
    ┌─────────┐                          ╱────────╲
    │  •  X   │        χ(X, t)          ╱   • x    ╲
    │         │      ──────────→       │            │
    └─────────┘                         ╲__________╱

    material coordinates X              spatial coordinates x
```

**$\mathbf{X}$** labels a material particle — its position in the reference configuration. It's a *name* for a bit of material, and it never changes.

**$\mathbf{x}$** is where that particle is *now*.

The **motion** is the map between them:

$$\mathbf{x} = \boldsymbol{\chi}(\mathbf{X}, t)$$

Everything in kinematics is a statement about this map.

**The displacement** is the difference:

$$\mathbf{u}(\mathbf{X}, t) = \mathbf{x} - \mathbf{X}$$

## Lagrangian vs Eulerian

The same field can be written as a function of $\mathbf{X}$ or of $\mathbf{x}$, and the choice is the difference between two whole traditions.

**Lagrangian (material) description** — quantities as functions of $(\mathbf{X}, t)$. *"What is the temperature of this particular particle?"*

Natural for **solids**: you care about a specific piece of steel, the reference configuration is a real remembered state, and the material has a history.

**Eulerian (spatial) description** — quantities as functions of $(\mathbf{x}, t)$. *"What is the temperature at this location?"*

Natural for **fluids**: tracking individual water molecules is absurd, there's no meaningful reference configuration, and you care about the flow field.

> **Solid mechanics is Lagrangian. Fluid mechanics is Eulerian.** That single fact explains most of the notational difference between the two fields, and why they look like separate subjects despite sharing the same balance laws.

## The material derivative

The bridge between the two descriptions, and the first genuinely subtle idea.

Suppose you want the rate of change of temperature **for a given particle**, but temperature is written as a spatial field $T(\mathbf{x}, t)$. The particle is moving, so it samples different locations:

$$\frac{D T}{D t} = \underbrace{\frac{\partial T}{\partial t}}_{\text{local}} + \underbrace{v_j \frac{\partial T}{\partial x_j}}_{\text{convective}}$$

**Local term** — the field is changing at this fixed location.
**Convective term** — the particle is moving into a region where the field differs.

The standard physical example: stand in a river with a thermometer. $\partial T/\partial t$ is the water at your position warming. $\mathbf{v}\cdot\nabla T$ is you drifting downstream into warmer water. The **material derivative** $DT/Dt$ is what the thermometer actually reads.

**Acceleration is the case that matters:**

$$a_i = \frac{Dv_i}{Dt} = \frac{\partial v_i}{\partial t} + v_j\frac{\partial v_i}{\partial x_j}$$

That second term is **nonlinear in velocity**, and it is the reason fluid dynamics is hard. Navier–Stokes would be a manageable linear PDE without it; with it you get turbulence, and a Millennium Prize problem. → [[engineering/01-continuum-mechanics/11-viscous-fluids-and-navier-stokes|Navier–Stokes]]

**Steady flow does not mean zero acceleration.** In a converging nozzle at steady state, $\partial \mathbf{v}/\partial t = 0$ everywhere and fluid still accelerates, because it moves into a region of higher velocity. That's the convective term, and it catches people every time.

## The deformation gradient

**The central object of finite-deformation kinematics.** Everything else is built from it.

$$F_{iJ} = \frac{\partial x_i}{\partial X_J}$$

It maps an infinitesimal material line element from the reference configuration to the current one:

$$d\mathbf{x} = \mathbf{F}\,d\mathbf{X}$$

```
reference                     current
   dX  ────────→  F  ────────→  dx
  (a tiny fibre                (the same fibre,
   of material)                 stretched and rotated)
```

Note the mixed indices — lowercase $i$ for current, uppercase $J$ for reference. **$\mathbf{F}$ is a two-point tensor**, with one foot in each configuration. That's unusual and it's why it doesn't behave like the tensors in note 02 under a single rotation.

In terms of displacement:

$$\mathbf{F} = \mathbf{I} + \frac{\partial \mathbf{u}}{\partial \mathbf{X}} = \mathbf{I} + \nabla_0\mathbf{u}$$

**The Jacobian** is its determinant:

$$J = \det \mathbf{F} = \frac{dV}{dV_0}$$

the ratio of deformed to undeformed volume. Two facts follow immediately:

- **$J > 0$ always.** $J = 0$ means a volume collapsed to nothing; $J < 0$ means the material turned inside out. Both are physically impossible, and a finite-element solver reporting a negative Jacobian is telling you an element has inverted — usually a sign the mesh or the load step is wrong
- **Incompressible ⟺ $J = 1$.** That's the exact statement of incompressibility, and it becomes a constraint you enforce

## Polar decomposition

$\mathbf{F}$ contains both stretch and rotation, mixed together. Separating them is essential, because **rotation must not produce stress** — spinning a body doesn't deform it.

Every $\mathbf{F}$ with $J > 0$ decomposes uniquely:

$$\mathbf{F} = \mathbf{R}\,\mathbf{U} = \mathbf{V}\,\mathbf{R}$$

- $\mathbf{R}$ is a **rotation** (orthogonal, $\det = 1$)
- $\mathbf{U}$ is the **right stretch tensor** (symmetric, positive definite) — stretch first, then rotate
- $\mathbf{V}$ is the **left stretch tensor** — rotate first, then stretch

```
      U (stretch)          R (rotate)
 □ ──────────────→ ▭ ──────────────→ ◊
        or
      R (rotate)           V (stretch)
 □ ──────────────→ ◇ ──────────────→ ◊
```

Same final state, different order.

> **This decomposition is why strain measures are built from $\mathbf{F}^T\mathbf{F}$ rather than $\mathbf{F}$.** Since $\mathbf{F}^T\mathbf{F} = \mathbf{U}^T\mathbf{R}^T\mathbf{R}\mathbf{U} = \mathbf{U}^2$, the rotation cancels — leaving pure stretch. A constitutive law written in terms of $\mathbf{C} = \mathbf{F}^T\mathbf{F}$ automatically produces no stress under rigid rotation, which is the requirement of **material frame indifference**. → [[engineering/01-continuum-mechanics/04-strain-measures|Strain Measures]]

The eigenvalues of $\mathbf{U}$ are the **principal stretches** $\lambda_1, \lambda_2, \lambda_3$ — the stretch ratios along three orthogonal material directions. A stretch of 1 means unchanged; 1.5 means 50% longer.

Computing $\mathbf{R}$ and $\mathbf{U}$ requires a matrix square root, which is why in practice you work with $\mathbf{C} = \mathbf{U}^2$ directly and avoid the decomposition.

## The velocity gradient

The rate-based counterpart, and the one fluids need:

$$L_{ij} = \frac{\partial v_i}{\partial x_j} = \dot{\mathbf{F}}\mathbf{F}^{-1}$$

Split it, using the symmetric/antisymmetric decomposition from [[engineering/01-continuum-mechanics/02-index-notation-and-tensors|note 02]]:

$$\mathbf{L} = \underbrace{\mathbf{D}}_{\text{rate of deformation}} + \underbrace{\mathbf{W}}_{\text{spin}}$$

$$D_{ij} = \tfrac{1}{2}(v_{i,j} + v_{j,i}) \qquad\qquad W_{ij} = \tfrac{1}{2}(v_{i,j} - v_{j,i})$$

**$\mathbf{D}$ is actual deformation rate** — stretching and shearing. **$\mathbf{W}$ is rigid rotation rate** and causes no deformation at all.

**This is the split that makes Newtonian fluids work.** Viscous stress depends on $\mathbf{D}$ and not on $\mathbf{W}$ — a fluid in solid-body rotation (a bucket of water spun up to steady state) has $\mathbf{D} = 0$ and experiences no viscous stress, despite $\mathbf{L} \neq 0$. If viscous stress depended on $\mathbf{L}$, rotating a bucket would heat the water, which it doesn't.

The **vorticity** is the axial vector of $\mathbf{W}$:

$$\boldsymbol{\omega} = \nabla \times \mathbf{v}$$

and $\boldsymbol{\omega} = 2 \times$ the local angular velocity. Vorticity is the central object of much of fluid dynamics — it's what tornadoes, wingtip vortices and turbulent eddies are made of.

## Compatibility

A subtlety worth knowing exists.

If you're given a displacement field $\mathbf{u}$, you can always compute a strain field. **The reverse is not true** — an arbitrary symmetric tensor field is not necessarily the strain of any continuous displacement field.

Six strain components come from three displacement components, so they're over-determined: there are constraints. The **compatibility conditions** (in small strain, $\varepsilon_{ij,kl} + \varepsilon_{kl,ij} - \varepsilon_{ik,jl} - \varepsilon_{jl,ik} = 0$) are what a strain field must satisfy to correspond to a real, gap-free, overlap-free deformation.

**Physically:** an incompatible strain field would tear the material or make it overlap itself.

This matters when you solve in terms of stress rather than displacement, and it's the reason **displacement-based finite elements are the default** — assume a continuous displacement field, and compatibility is satisfied automatically. → [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]]

## The small-strain simplification

Almost everything above collapses when displacement gradients are small ($|\nabla \mathbf{u}| \ll 1$, in practice under ~1%):

- The reference and current configurations become interchangeable — you can write equilibrium on the undeformed geometry
- $\mathbf{F} \approx \mathbf{I}$, and all strain measures coincide
- The material derivative's convective term becomes negligible for solids
- Everything becomes **linear**, so superposition works

**That last point is why linear elasticity is tractable at all** — you can solve for one load case and add. → [[engineering/01-continuum-mechanics/08-linear-elasticity|Linear Elasticity]]

**When it fails:** rubber, biological tissue, metal forming, buckling, and anything with large rotations. A cantilever tip deflecting 30% of its length has small *strains* and large *rotations*, and the small-strain tensor gets it wrong — a rigid rotation registers as spurious strain. That's the case for finite deformation. → [[engineering/01-continuum-mechanics/10-finite-deformation|Finite Deformation]]

---

## Related
- [[engineering/01-continuum-mechanics/04-strain-measures|Strain Measures]] — quantifying what $\mathbf{F}$ describes
- [[engineering/01-continuum-mechanics/06-conservation-laws|Conservation Laws]] — where the material derivative earns its keep
- [[engineering/01-continuum-mechanics/11-viscous-fluids-and-navier-stokes|Navier–Stokes]] — $\mathbf{D}$ in action
- [[engineering/01-continuum-mechanics/README|Continuum mechanics map]]
