# What Continuum Mechanics Is

**[Intermediate]** — The one modelling assumption the whole field rests on, when it holds, and why solids and fluids turn out to be the same theory with different closures.

**Source:** `[reference]` — see [[engineering/README|the domain note]] on what that means here.

## The continuum hypothesis

Matter is atoms with space between them. Continuum mechanics ignores that entirely and treats material as **continuously distributed** — every point in a body has a density, a velocity, a stress, and these vary smoothly.

That's obviously false at small enough scale, and it's the assumption that makes the whole field work.

The justification is **separation of scales**. Define density at a point as the mass in a small volume around it, divided by that volume:

$$\rho(\mathbf{x}) = \lim_{\Delta V \to V^*} \frac{\Delta m}{\Delta V}$$

Shrink $\Delta V$ and you see three regimes:

```
density
  │        ╱╲                              ← too small: individual atoms,
  │       ╱  ╲                                wild fluctuations
  │  ╲╱╲╱     ╲___________________         ← the plateau: the REV
  │                              ╲___      ← too large: real variation
  └──────────────────────────────────────→ ΔV
     atomic    representative     body
               elementary volume
```

The plateau is the **representative elementary volume (REV)** — large enough to average over many molecules, small enough to be "a point" relative to the body. The theory works when that plateau exists.

**Where it breaks:**

- **Rarefied gases** — at high altitude the mean free path approaches the body size. The **Knudsen number** $Kn = \lambda / L$ tells you: $Kn \lesssim 0.01$ and continuum is fine; above ~0.1 you need kinetic theory
- **Nanoscale** — a 5 nm film is tens of atoms thick. Molecular dynamics territory
- **Granular materials** — sand is a continuum at the scale of a beach and discrete at the scale of a grain
- **Cracks** — a crack tip has a stress singularity in continuum theory, which is the theory announcing it's outside its domain. Fracture mechanics works around this → [[engineering/01-continuum-mechanics/12-failure-and-yield|Failure and Yield]]

**What you gain** is enormous: the machinery of calculus. Fields, derivatives, integrals, and PDEs instead of $10^{23}$ coupled ODEs.

## Solids and fluids are the same theory

The structural insight worth having early. Both obey the same conservation laws:

$$\text{mass} \quad \text{momentum} \quad \text{angular momentum} \quad \text{energy}$$

Those give you equations relating stress to motion, and they're **the same equations for steel, water, air, blood, and rock**. → [[engineering/01-continuum-mechanics/06-conservation-laws|Conservation Laws]]

The equations are also **underdetermined** — more unknowns than equations. What closes the system is a **constitutive model**: a statement about how *this particular material* responds to deformation. → [[engineering/01-continuum-mechanics/07-constitutive-models|Constitutive Models]]

| | Solid | Fluid |
|---|---|---|
| Responds to | **how much** you deform it (strain) | **how fast** you deform it (strain rate) |
| Constitutive law | $\boldsymbol{\sigma} = f(\boldsymbol{\varepsilon})$ | $\boldsymbol{\sigma} = f(\dot{\boldsymbol{\varepsilon}})$ |
| At rest under shear | holds a deformed shape | keeps flowing |
| Simplest model | Hooke's law | Newtonian viscosity |

**That's the entire distinction.** A fluid is a material that cannot resist shear at rest; a solid can. Everything else — the balance laws, the stress tensor, the kinematics — is shared.

Which is why the same course covers Navier–Stokes and beam bending, and why **viscoelastic** materials (polymers, biological tissue, asphalt) are genuinely awkward: they're both, depending on timescale. Silly putty bounces and also flows.

## The three ingredients

Every problem in this field is assembled from three parts, and knowing which one you're missing is most of getting unstuck:

**1. Kinematics** — the geometry of deformation. How do you describe motion and quantify "how much has this deformed"? No physics, just geometry. → [[engineering/01-continuum-mechanics/03-kinematics-of-deformation|03]], [[engineering/01-continuum-mechanics/04-strain-measures|04]]

**2. Balance laws** — conservation of mass, momentum, energy. Physics, and **material-independent**. → [[engineering/01-continuum-mechanics/06-conservation-laws|06]]

**3. Constitutive models** — how this material relates stress to deformation. Material-specific, and **empirical**. → [[engineering/01-continuum-mechanics/07-constitutive-models|07]]

```
kinematics  +  balance laws  +  constitutive model  =  a solvable problem
 (geometry)      (physics)        (the material)
```

The balance laws are as close to certain as anything in engineering. **The constitutive model is where the modelling error lives**, and it's the part chosen rather than derived. When a simulation is wrong by a factor of three, look there first.

## Why tensors

You cannot avoid them, so it's worth knowing why.

Consider stress. At a point inside a loaded body, cut an imaginary plane and ask what force the material on one side exerts on the other. **The answer depends on which plane you chose.**

A horizontal cut through a beam under bending sees mostly shear. A vertical cut sees mostly normal stress. Same point, different answers.

So stress is not a number and not a vector — it's an object that **takes a plane orientation and returns a traction vector**. That's a linear map from vectors to vectors: a second-order tensor.

$$\mathbf{t}(\mathbf{n}) = \boldsymbol{\sigma}\,\mathbf{n}$$

Nine components in 3D (six independent, by symmetry). Not because someone wanted it complicated — because the physical quantity genuinely has that many degrees of freedom. → [[engineering/01-continuum-mechanics/02-index-notation-and-tensors|Index Notation and Tensors]]

Same for strain, and for the deformation gradient.

## The two viewpoints

A recurring source of confusion, so it's worth naming now.

**Lagrangian (material)** — follow a particle. "Where is *this bit of material* now?" Natural for solids, where you care about a specific piece of steel.

**Eulerian (spatial)** — watch a fixed point in space. "What's the velocity *at this location* right now?" Natural for fluids, where tracking individual water molecules is absurd.

Both describe the same physics. Solid mechanics is usually Lagrangian, fluid mechanics usually Eulerian, and **the translation between them is where a lot of the notation comes from** — the material derivative, the two stress measures, the several strain measures. → [[engineering/01-continuum-mechanics/03-kinematics-of-deformation|Kinematics]]

## The simplifying assumptions

Most engineering practice is continuum mechanics plus assumptions that make it tractable. Knowing which are active is the skill:

**Small strain** — deformations under ~1%. Lets you use the linearised strain tensor and ignore the difference between deformed and undeformed geometry. **This one assumption removes most of the difficulty**, and it's why undergraduate solid mechanics is manageable. → [[engineering/01-continuum-mechanics/10-finite-deformation|Finite Deformation]] is what happens without it.

**Linear elasticity** — stress proportional to strain, fully reversible. True for metals below yield, false for rubber, soil, and anything plastic.

**Isotropy** — same properties in every direction. True for most metals, false for wood, composites, bone, and rolled sheet.

**Homogeneity** — same properties everywhere.

**Incompressibility** — density constant. Excellent for liquids and for gases below Mach 0.3.

Every textbook formula you've used carries some subset of these. **The formula isn't wrong; the assumptions are.** Being able to name them is the difference between using a result and understanding it.

## Where this is used

- **Structural analysis** — will this hold? → beams, plates, FEM
- **Fluid dynamics** — aerodynamics, pipe flow, weather, blood flow
- **Manufacturing** — forming, casting, injection moulding, additive
- **Geomechanics** — soil, rock, earthquakes
- **Biomechanics** — tissue, implants, cardiovascular
- **Computer graphics** — cloth, hair, fluid and soft-body simulation are all this, with speed prioritised over accuracy
- **Robotics** — [[robotics/README|soft robotics]] and compliant mechanisms are continuum problems

## Reading this track

The order is deliberate: **kinematics before stress before balance laws before constitutive models**, because each genuinely needs the previous. Notes 02–06 are the foundation and can't be skipped. After that, 07–13 are applications and you can take what you need.

**The prerequisite is multivariable calculus and linear algebra** — partial derivatives, divergence, gradient, matrices, eigenvalues. [[ai-ml/00-foundations/03-mathematics/README|The vault's maths notes]] cover these at the level ML needs, which is a floor rather than enough; tensor calculus and PDEs are a genuine gap.

---

## Related
- [[engineering/01-continuum-mechanics/02-index-notation-and-tensors|Index Notation and Tensors]] — the language
- [[engineering/01-continuum-mechanics/07-constitutive-models|Constitutive Models]] — where the modelling error lives
- [[hardware/01-electricity|Hardware: Electricity]] — the other physical domain here
- [[engineering/01-continuum-mechanics/README|Continuum mechanics map]]
