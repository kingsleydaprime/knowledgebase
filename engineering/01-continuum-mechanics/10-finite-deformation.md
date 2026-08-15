# Finite Deformation

**[Advanced]** — What happens when small strain fails, why the failure is usually about rotation rather than strain, and how rubber is modelled.

## When you need it

Four situations force finite-deformation theory, and only the first is obvious:

**1. Large strains.** Rubber, biological tissue, foams, metal forming. Strains of 100–700%, where the distinction between strain measures is enormous. → [[engineering/01-continuum-mechanics/04-strain-measures|Strain Measures]]

**2. Large rotations with small strains.** The one people miss. A fishing rod, a leaf spring, a deployable structure, a slender cantilever deflecting 30% of its length — strains under 1%, rotations of 0.3 rad, and **small-strain theory reports spurious strain from the rotation alone**. At 0.3 rad that's roughly $-45000\ \mu\varepsilon$, an order of magnitude past steel's yield strain, from a rotation that deformed nothing.

**3. Buckling and post-buckling.** Instability is inherently a geometric-nonlinearity problem — the structure's stiffness changes as it deforms. → [[engineering/01-continuum-mechanics/09-beams-and-structures|Beams and Structures]]

**4. Contact and follower loads.** Pressure that stays normal to a deforming surface, or contact areas that change with load, both depend on current geometry.

> **The criterion is small *rotations*, not small strains.** That's the correction most people need. If any part of your structure rotates more than a few degrees, switch on geometric nonlinearity — the "large displacement" toggle in every FE code — regardless of how small the strains are.

## The three nonlinearities

Worth separating, because they have different causes and different fixes:

| | Source | Example |
|---|---|---|
| **Geometric** | equilibrium on the deformed shape | large rotation, buckling |
| **Material** | nonlinear constitutive law | plasticity, hyperelasticity |
| **Boundary** | contact, friction, follower loads | a seal, a press fit |

They're independent. Rubber under small rotation is materially nonlinear only. A steel cantilever bending elastically through 45° is geometrically nonlinear only. Metal forming is all three at once, which is why it's hard.

## Total vs updated Lagrangian

Two ways to organise the bookkeeping, and every FE code uses one or the other.

**Total Lagrangian** — everything referred to the **original** configuration. Uses $\mathbf{S}$ and $\mathbf{E}$ (the second Piola–Kirchhoff / Green–Lagrange pair), which are symmetric, material, and energy-conjugate. → [[engineering/01-continuum-mechanics/05-stress|Stress]]

Natural for **hyperelasticity**, where a stored-energy function is naturally written in terms of the reference configuration.

**Updated Lagrangian** — the reference is reset to the **last converged** configuration at each step. Uses Cauchy stress and rate quantities.

Natural for **plasticity**, where the material's state evolves and there's no meaningful "original" configuration to refer back to.

They're mathematically equivalent and differ in convenience and conditioning. **Total Lagrangian for rubber; updated Lagrangian for metal forming** is the usual split.

## Hyperelasticity

The constitutive framework for large elastic strain.

**Define a stored-energy function** $W$ per unit reference volume, and derive stress from it:

$$\mathbf{S} = 2\frac{\partial W}{\partial \mathbf{C}}$$

Deriving stress from a potential is what makes the material **path-independent and non-dissipative by construction** — load and unload along any path and you recover exactly the energy you put in. It satisfies the second law automatically. → [[engineering/01-continuum-mechanics/07-constitutive-models|Constitutive Models]]

For an **isotropic** material, $W$ can depend only on the invariants of $\mathbf{C}$ — that's forced by symmetry, not chosen:

$$W = W(I_1, I_2, I_3)$$

### The standard models

**Neo-Hookean** — one parameter, derived from Gaussian polymer chain statistics:

$$W = C_1(I_1 - 3)$$

Good to roughly 50% strain, and the right starting point. It's also what most computer-graphics soft-body simulators use, because it's cheap and stable.

**Mooney–Rivlin** — two parameters:

$$W = C_1(I_1 - 3) + C_2(I_2 - 3)$$

Better range, still simple. The workhorse for moderate strains.

**Ogden** — several parameters, written in principal stretches rather than invariants:

$$W = \sum_{i} \frac{\mu_i}{\alpha_i}\left(\lambda_1^{\alpha_i} + \lambda_2^{\alpha_i} + \lambda_3^{\alpha_i} - 3\right)$$

**Excellent fit for rubber to 700% strain**, and the standard for serious elastomer work. The cost is more parameters to fit and a greater risk of fitting nonsense.

**Arruda–Boyce (8-chain)** — physically motivated rather than phenomenological. Derived from the statistical mechanics of a network of polymer chains, so its parameters mean something (chain length, network density), and it extrapolates more honestly outside the fitted range.

**Yeoh, Gent, Fung** — Yeoh for filled rubbers, Gent for the limiting-chain-extensibility stiffening, **Fung for biological soft tissue**, which stiffens exponentially — that's why skin and arteries feel soft then suddenly firm.

### Incompressibility

Rubber is essentially incompressible — $\nu \approx 0.4999$, bulk modulus thousands of times the shear modulus.

That's not a detail; it changes the formulation. The energy function splits:

$$W = W_{\text{iso}}(\bar{I}_1, \bar{I}_2) + W_{\text{vol}}(J)$$

with $\bar{I}_1 = J^{-2/3}I_1$ the deviatoric (volume-preserving) invariant.

**Numerically, incompressibility causes volumetric locking** — standard displacement elements become artificially stiff and give badly wrong answers. The fixes are mixed **u–p formulations** (pressure as a separate unknown, i.e. a Lagrange multiplier), selective reduced integration, or F-bar methods.

**If a rubber FE model comes out far too stiff, locking is the first thing to check.** → [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]]

## Fitting hyperelastic parameters

The practical warning, and it's a serious one.

**Uniaxial tension data alone does not determine a hyperelastic model.** Multiple parameter sets fit a tension curve nearly identically and then diverge wildly in biaxial tension, planar shear, or compression.

The consequence: an Ogden model fitted only to a tension test can be **badly wrong** in a real multiaxial state — and it will produce smooth, plausible-looking contour plots while being wrong.

**You need at least:**

- Uniaxial tension
- **Equibiaxial tension** (a bulge or inflation test)
- **Planar shear** (a wide, short specimen — "pure shear")

Then fit all three simultaneously. Volumetric data too, if compressibility matters.

**And check stability.** The **Drucker stability** criterion requires the incremental work to be positive; a fitted model can be unstable at strains you'll actually reach, producing negative stiffness and a solver that diverges for no visible reason. Most FE codes will report this if asked — ask.

## Objective rates

The subtlety that catches people implementing finite-strain plasticity.

For a rate-form constitutive law you need a stress *rate*. But $\dot{\boldsymbol\sigma}$ **is not objective** — under superposed rigid rotation it picks up spurious terms, so a law built on it would produce stress from pure rotation.

Several objective rates exist:

- **Jaumann rate** — corrects using the spin tensor $\mathbf{W}$. The most common
- **Green–Naghdi rate** — uses the rotation $\mathbf{R}$ from the polar decomposition
- **Truesdell / Oldroyd rates** — used in fluid mechanics and viscoelasticity

**They give different answers at large strain.** The classic demonstration: simple shear to large strain with the Jaumann rate produces **oscillating stress** — physically absurd, and a well-known artefact. Green–Naghdi doesn't.

The practical advice: for large-strain plasticity, know which rate your code uses, and be suspicious of results at shear strains above ~1. For most engineering problems the difference is negligible; where it isn't, it's dramatic.

## Numerical solution

Finite-deformation problems are **nonlinear**, so there's no single solve. You iterate.

**Newton–Raphson**, incrementally:

```
for each load increment:
    predict displacement
    repeat:
        compute internal forces from current geometry and stress
        residual = external - internal
        if |residual| small: converged, next increment
        form the TANGENT stiffness at the current state
        solve for a correction
```

**The tangent stiffness changes every iteration** because it depends on the current geometry and stress state. It has two parts:

$$\mathbf{K}_T = \underbrace{\mathbf{K}_{\text{material}}}_{\text{constitutive}} + \underbrace{\mathbf{K}_{\text{geometric}}}_{\text{stress stiffening}}$$

**The geometric stiffness is what makes buckling emerge naturally** — compressive stress reduces effective stiffness, and when it drives an eigenvalue to zero, the structure buckles. It falls out of the formulation rather than being added.

**Practical convergence advice:**

- **Smaller load increments** — the single most effective fix for a diverging nonlinear solve
- **Arc-length (Riks) methods** for post-buckling, where load *decreases* as displacement increases and a load-controlled solver cannot follow the path
- **Check the tangent is consistent** with the stress update; an inconsistent tangent still converges, just slowly and unreliably
- **Watch for negative Jacobians** — an inverted element, meaning the mesh or the increment is too aggressive → [[engineering/01-continuum-mechanics/03-kinematics-of-deformation|Kinematics]]

## The honest summary

Finite deformation is where the clean structure of linear elasticity — superposition, uniqueness, closed-form solutions — is lost:

| | Linear | Finite |
|---|---|---|
| Superposition | ✅ | ❌ |
| Unique solution | ✅ | ❌ (buckling has several) |
| Closed-form results | many | very few |
| Solve | one linear system | incremental iteration |
| Geometry for equilibrium | undeformed | current (unknown) |

**Use small strain whenever you legitimately can.** Not laziness — the linear theory is better understood, faster, more reliable, and gives you superposition. Reach for finite deformation when rotations exceed a few degrees, strains exceed a few percent, or instability is the thing you're studying.

---

## Related
- [[engineering/01-continuum-mechanics/04-strain-measures|Strain Measures]] — why small strain fails under rotation
- [[engineering/01-continuum-mechanics/05-stress|Stress]] — the three stress tensors this needs
- [[engineering/01-continuum-mechanics/07-constitutive-models|Constitutive Models]] — hyperelasticity in context
- [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]] — solving these
- [[engineering/01-continuum-mechanics/README|Continuum mechanics map]]
