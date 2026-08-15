# Constitutive Models

**[Advanced]** — The six missing equations. Where the physics stops being universal, where the modelling error lives, and the rules that separate a model from a curve fit.

## The closure problem

[[engineering/01-continuum-mechanics/06-conservation-laws|The balance laws]] give four equations for ten unknowns. The gap is closed by a **constitutive equation** — a relation between stress and deformation that describes *this particular material*.

$$\boldsymbol{\sigma} = \mathcal{F}(\text{deformation, rate, history, temperature, } \dots)$$

**This is the only part of the theory that is chosen rather than derived.** Conservation of momentum is as close to certain as engineering gets. Whether steel obeys $\boldsymbol\sigma = \mathbf{C}:\boldsymbol\varepsilon$ is an empirical claim with a limited domain of validity.

> When a simulation is wrong by a factor of three, look here first. Not at the mesh, not at the solver — at whether the material model was ever valid for what you asked it to do.

## The rules a model must obey

Not anything goes. Four restrictions, and they eliminate most proposals.

### 1. Material frame indifference (objectivity)

**The response cannot depend on the observer.** Rotate the whole experiment — or watch it from a rotating frame — and the material must behave identically.

Formally, under a superposed rigid motion $\mathbf{x}^* = \mathbf{Q}(t)\mathbf{x} + \mathbf{c}(t)$, the stress must transform as $\boldsymbol\sigma^* = \mathbf{Q}\boldsymbol\sigma\mathbf{Q}^T$.

The practical consequences:

- **A law cannot depend on $\mathbf{F}$ directly** — it must go through $\mathbf{C} = \mathbf{F}^T\mathbf{F}$ or $\mathbf{b} = \mathbf{F}\mathbf{F}^T$, where the rotation cancels. → [[engineering/01-continuum-mechanics/04-strain-measures|Strain Measures]]
- **A law cannot depend on velocity $\mathbf{v}$**, only on the rate of deformation $\mathbf{D}$ — never the spin $\mathbf{W}$. A fluid in rigid rotation must feel no viscous stress
- **Ordinary time derivatives of stress are not objective.** $\dot{\boldsymbol\sigma}$ picks up spurious terms under rotation, which is why finite-strain plasticity needs **objective rates** — Jaumann, Green–Naghdi, Truesdell. Using the wrong one produces oscillating stress under simple shear, a famous and genuinely confusing failure

### 2. Thermodynamic admissibility

The Clausius–Duhem inequality must hold for **every** conceivable deformation path. → [[engineering/01-continuum-mechanics/06-conservation-laws|note 06]]

This forces viscosity positive, conductivity positive, moduli positive definite, and hyperelastic stress to derive from a stored-energy potential. The **Coleman–Noll procedure** extracts these systematically.

### 3. Material symmetry

If the material has symmetries, the model must respect them. **Isotropy** — no preferred direction — is the strongest and most useful:

> An isotropic material's response can depend only on the **invariants** of the deformation.

That's not a convenience, it's forced. And it's remarkably restrictive: it takes the 81 components of a general fourth-order stiffness tensor down to **two independent constants**. → [[engineering/01-continuum-mechanics/08-linear-elasticity|Linear Elasticity]]

| Symmetry | Independent elastic constants |
|---|---|
| Fully anisotropic (triclinic) | 21 |
| Orthotropic (3 orthogonal planes) | **9** — wood, rolled sheet, unidirectional composite |
| Transversely isotropic | **5** — fibre composites, muscle, bone |
| **Isotropic** | **2** — most metals, glass, unfilled polymers |

### 4. Determinism and local action

Stress at a point depends on the history of deformation *at that point* (and its immediate neighbourhood), not on what's happening across the body. **Non-local** models exist — they're needed for strain-softening and damage, where local models produce mesh-dependent nonsense — but they're a deliberate departure.

## The classification

The useful way to organise the zoo: **what does stress depend on?**

| Class | Depends on | Examples |
|---|---|---|
| **Elastic** | current strain only | steel below yield, rubber |
| **Viscous** | strain *rate* only | water, air, oil |
| **Viscoelastic** | strain and rate, with memory | polymers, tissue, asphalt |
| **Plastic** | strain **history** — irreversible | metals past yield |
| **Viscoplastic** | history and rate | creep, high-rate forming |

**Elastic ⟹ reversible and path-independent.** Load and unload and you return along the same curve, with no energy lost. That's the defining property, and it's what fails for everything else.

## Elasticity

**Linear (Hooke):**

$$\sigma_{ij} = C_{ijkl}\,\varepsilon_{kl}$$

Valid for small strain, and enormously useful precisely because it's linear — superposition works, and you can solve one load case and add. → [[engineering/01-continuum-mechanics/08-linear-elasticity|Linear Elasticity]]

**Hyperelastic** — for large elastic strain, defined by a stored-energy function $W$:

$$\mathbf{S} = 2\frac{\partial W}{\partial \mathbf{C}}$$

Deriving stress from a potential is what makes the material **path-independent and non-dissipative by construction** — it satisfies the second law automatically. → [[engineering/01-continuum-mechanics/10-finite-deformation|Finite Deformation]]

The common forms, in increasing sophistication: **neo-Hookean** (one parameter, good to ~50% strain), **Mooney–Rivlin** (two, better range), **Ogden** (several, excellent fit for rubber to 700%), **Arruda–Boyce** (physically motivated, based on polymer chain statistics rather than curve-fitting).

## Viscosity

**Newtonian:**

$$\sigma_{ij} = -p\,\delta_{ij} + 2\mu D_{ij} \quad (\text{incompressible})$$

Stress proportional to **rate** of deformation. Water, air, thin oils, and most gases. → [[engineering/01-continuum-mechanics/11-viscous-fluids-and-navier-stokes|Navier–Stokes]]

**Non-Newtonian** — apparent viscosity varies with shear rate, and the everyday examples are worth knowing because they make the concept concrete:

- **Shear-thinning (pseudoplastic)** — viscosity drops with shear rate. Paint (brushes easily, doesn't run), blood, ketchup, polymer melts. The most common non-Newtonian behaviour by far
- **Shear-thickening (dilatant)** — viscosity rises. Cornstarch in water, which you can run across
- **Bingham plastic** — behaves as a solid below a yield stress, flows above. Toothpaste, drilling mud, mayonnaise

The **power law** $\mu_{\text{eff}} = K\dot\gamma^{n-1}$ covers thinning ($n<1$) and thickening ($n>1$) with two parameters, and it's the workhorse model.

## Plasticity

The genuinely hard one, because **stress depends on history**, not on the current state.

Three ingredients:

**1. A yield criterion** — when does plastic flow start?

$$f(\boldsymbol\sigma) = 0$$

**von Mises** is the standard for metals, built on the second deviatoric invariant. → [[engineering/01-continuum-mechanics/12-failure-and-yield|Failure and Yield]]

**2. A flow rule** — in what direction does plastic strain develop?

$$\dot{\varepsilon}^p_{ij} = \dot{\lambda}\frac{\partial g}{\partial \sigma_{ij}}$$

**Associated flow** takes $g = f$, so plastic strain is normal to the yield surface. Correct for metals; wrong for soils and concrete, where dilatancy requires a separate plastic potential.

**3. A hardening law** — how does the yield surface evolve?

- **Isotropic hardening** — the surface expands uniformly. Fine for monotonic loading
- **Kinematic hardening** — the surface translates. **Necessary for cyclic loading**, because it captures the **Bauschinger effect**: a metal yielded in tension yields *earlier* in subsequent compression. Isotropic hardening cannot represent that, and using it for fatigue gives wrong answers

The strain decomposes additively (in small strain):

$$\varepsilon_{ij} = \varepsilon^e_{ij} + \varepsilon^p_{ij}$$

with only the elastic part generating stress. Numerically, plasticity is solved by **return mapping**: take an elastic trial step, and if it lands outside the yield surface, project back onto it.

**Path dependence is the practical consequence.** You cannot jump to the answer — you must integrate the loading history in increments, which is why plastic FE analysis is so much more expensive than elastic.

## Viscoelasticity

Both elastic and viscous, with **memory**. Polymers, biological tissue, asphalt, and the reason silly putty both bounces and flows.

Built from springs and dashpots:

- **Maxwell** (spring + dashpot in series) — models **stress relaxation**: hold strain constant, stress decays
- **Kelvin–Voigt** (parallel) — models **creep**: hold stress constant, strain grows
- **Standard linear solid** (three elements) — captures both, and is the minimum useful model
- **Prony series** — many Maxwell elements in parallel, fitted to data. What FE codes actually use

The general form is a **hereditary integral** — stress depends on the entire strain history, weighted by a decaying relaxation function:

$$\sigma(t) = \int_{-\infty}^{t} E(t-\tau)\,\frac{d\varepsilon}{d\tau}\,d\tau$$

**Time–temperature superposition** is the practically important trick: for many polymers, raising temperature is equivalent to slowing the test. The WLF equation quantifies it, and it's how a short high-temperature test predicts decades of room-temperature creep.

## Getting the parameters

Every model has constants, and they come from experiments:

| Test | Gives |
|---|---|
| Uniaxial tension | $E$, yield stress, hardening curve, UTS |
| Compression | asymmetry (concrete, soils, and some polymers differ in tension) |
| Torsion | $G$ directly, and large shear strains without necking |
| Biaxial / bulge | essential for **rubber** — uniaxial data alone badly under-determines hyperelastic parameters |
| Creep and relaxation | viscoelastic constants |
| Split-Hopkinson bar | high strain-rate response |
| Nanoindentation | local properties, thin films |

**Two honest warnings:**

**Fitting uniaxial data does not determine a multiaxial model.** This is the classic rubber mistake — an Ogden model fitted only to a tension test can be wildly wrong in biaxial or shear states, and it will still produce smooth, plausible-looking results.

**Parameters have a validity range.** Fitted to 0–5% strain, at 20 °C, at 0.001/s. Used at 40% strain, 200 °C, and 100/s, they are extrapolation dressed as data.

## The practical advice

1. **Start with the simplest model that could work.** Linear elastic isotropic answers more questions than people expect
2. **Know which assumption you're leaning on**, and check whether the result violates it. If a linear-elastic run predicts stress above yield, the answer is not "the part yields a bit" — it's "this analysis is invalid, rerun it plastic"
3. **Match the model to the loading.** Cyclic loading needs kinematic hardening. Long duration needs creep. High rate needs rate dependence
4. **Rubber needs multiaxial data.** Non-negotiable
5. **Sanity-check against a hand calculation.** A beam formula, an equilibrium check, an energy balance
6. **Report the model and its parameters** alongside any result. A stress number without its constitutive assumptions isn't a result, it's a number

> **The balance laws are physics. The constitutive model is a hypothesis.** Keeping those categories separate is the single most useful habit in this field.

---

## Related
- [[engineering/01-continuum-mechanics/06-conservation-laws|Conservation Laws]] — the equations this closes
- [[engineering/01-continuum-mechanics/08-linear-elasticity|Linear Elasticity]] — the simplest case, in full
- [[engineering/01-continuum-mechanics/12-failure-and-yield|Failure and Yield]] — yield criteria in depth
- [[engineering/01-continuum-mechanics/README|Continuum mechanics map]]
