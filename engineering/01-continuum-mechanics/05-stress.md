# Stress

**[Intermediate → Advanced]** — The quantity you cannot measure, why it needs nine components, and the three different stress tensors finite deformation forces on you.

## Traction

Cut an imaginary plane through a loaded body. The material on one side pulls and pushes on the material on the other. The **traction** is that force per unit area:

$$\mathbf{t} = \lim_{\Delta A \to 0} \frac{\Delta \mathbf{F}}{\Delta A}$$

A vector, in N/m² (pascals). It has a component normal to the plane (**normal stress**) and components in the plane (**shear stress**).

**The traction depends on the orientation of the cut.** Same point, different plane, different answer — a horizontal cut through a bent beam sees mostly shear; a vertical cut sees mostly normal stress. That dependence is the entire reason stress is a tensor.

## Cauchy's theorem

The result that makes the field possible:

$$\mathbf{t}(\mathbf{n}) = \boldsymbol{\sigma}\,\mathbf{n} \qquad\qquad t_i = \sigma_{ij}n_j$$

**The traction on *any* plane is a linear function of that plane's normal.** So you don't need infinitely many numbers to describe the stress state at a point — you need nine, and the tensor $\boldsymbol\sigma$ generates the traction on every possible cut.

The proof is the **Cauchy tetrahedron**: take a small tetrahedron with three faces on the coordinate planes and one arbitrary face with normal $\mathbf{n}$. Write force balance. Areas scale as $\ell^2$ and volume as $\ell^3$, so as $\ell \to 0$ the body-force and inertia terms vanish faster than the surface terms — leaving a purely geometric relation. That $\ell^2$ vs $\ell^3$ argument is worth remembering; it's used repeatedly.

## Reading the components

$$\boldsymbol{\sigma} = \begin{bmatrix} \sigma_{11} & \sigma_{12} & \sigma_{13} \\ \sigma_{21} & \sigma_{22} & \sigma_{23} \\ \sigma_{31} & \sigma_{32} & \sigma_{33} \end{bmatrix}$$

**$\sigma_{ij}$ = the force in direction $i$ on the face whose normal is $j$.**

- **Diagonal** — normal stresses. Positive = tension, negative = compression
- **Off-diagonal** — shear stresses

The sign convention matters and differs by field: **solid mechanics takes tension positive**; **geomechanics takes compression positive**, because soil is essentially always in compression and nobody wants to write minus signs all day. Check which convention a source uses.

## Symmetry

$$\sigma_{ij} = \sigma_{ji}$$

**This is not a definition — it's a consequence of angular momentum balance.** Take a small cube and sum moments: if $\sigma_{12} \neq \sigma_{21}$, the net moment is proportional to $\ell^3$ while the rotational inertia is proportional to $\ell^5$, so angular acceleration $\propto \ell^{-2} \to \infty$ as the cube shrinks. An infinitesimal element would spin infinitely fast.

So symmetry is forced, and it reduces nine components to **six independent** ones. → [[engineering/01-continuum-mechanics/06-conservation-laws|Conservation Laws]]

(The exception: **Cosserat / micropolar** continua, which carry couple stresses and have non-symmetric $\boldsymbol\sigma$. Relevant to granular media and materials with microstructure, and out of scope here.)

## Principal stresses

Because $\boldsymbol\sigma$ is symmetric, it has three real eigenvalues and orthogonal eigenvectors. → [[engineering/01-continuum-mechanics/02-index-notation-and-tensors|note 02]]

$$\sigma_{ij}n_j = \sigma\,n_i$$

**In the principal directions there is no shear at all** — only normal stresses $\sigma_1 \geq \sigma_2 \geq \sigma_3$.

Two facts fall out and drive most failure prediction:

**Maximum normal stress is $\sigma_1$.** Brittle materials — cast iron, concrete, glass, ceramics — fail on the plane perpendicular to it. Chalk twisted in torsion breaks along a 45° helix, because that's where the principal tension lies.

**Maximum shear stress is $\tau_{max} = (\sigma_1 - \sigma_3)/2$**, on planes at 45° to the principal directions. Ductile materials yield by shear, so mild steel in torsion fails on a transverse plane. **Same test, different fracture surface, and the orientation tells you the failure mode.** → [[engineering/01-continuum-mechanics/12-failure-and-yield|Failure and Yield]]

**Mohr's circle** is the graphical construction of this in 2D — a circle of centre $(\sigma_1+\sigma_2)/2$ and radius $\tau_{max}$, on which every plane's stress state is a point. It's how this was done before computers, it's still the fastest way to build intuition, and it's still on every exam.

## The volumetric/deviatoric split

$$\sigma_{ij} = \underbrace{-p\,\delta_{ij}}_{\text{hydrostatic}} + \underbrace{s_{ij}}_{\text{deviatoric}} \qquad p = -\tfrac{1}{3}\sigma_{kk}$$

**Pressure changes volume; the deviator changes shape.**

This split does real work:

- **Metals yield on the deviator only.** Hydrostatic pressure doesn't cause plastic flow — a solid steel ball at the bottom of the Mariana Trench is fine, a hollow one implodes. That's why the von Mises criterion is built from $s_{ij}$
- **In fluids, $p$ is the thermodynamic pressure** and $s_{ij}$ is the viscous stress. A fluid at rest has $s_{ij}=0$ and $\boldsymbol\sigma = -p\mathbf{I}$ — pure pressure, no shear, which is the *definition* of a fluid at rest. → [[engineering/01-continuum-mechanics/11-viscous-fluids-and-navier-stokes|Navier–Stokes]]
- **Rubber is nearly incompressible**, so the hydrostatic part is essentially unconstrained by deformation and must be carried as a separate unknown — which is why hyperelastic FE formulations use mixed elements

## Three stress tensors

Under finite deformation the question "force per unit area" becomes ambiguous: **which area — deformed or undeformed?** That question generates three tensors.

**Cauchy stress $\boldsymbol\sigma$ — "true stress."** Current force over *current* area. The physically real one; what a material actually experiences and what failure criteria use. Symmetric. Spatial.

**First Piola–Kirchhoff $\mathbf{P}$ — "nominal / engineering stress."** Current force over *reference* area:

$$\mathbf{P} = J\,\boldsymbol{\sigma}\,\mathbf{F}^{-T}$$

Convenient because the reference area is known, and it's what a tensile machine effectively reports (load ÷ original cross-section). **Not symmetric**, being a two-point tensor like $\mathbf{F}$ — which makes it awkward for constitutive laws.

**Second Piola–Kirchhoff $\mathbf{S}$.** Both force and area pulled back to the reference configuration:

$$\mathbf{S} = J\,\mathbf{F}^{-1}\boldsymbol{\sigma}\,\mathbf{F}^{-T}$$

**Symmetric, fully material, and energy-conjugate to Green–Lagrange strain**:

$$\text{stress power} = \mathbf{S}:\dot{\mathbf{E}} = \mathbf{P}:\dot{\mathbf{F}} = J\,\boldsymbol\sigma:\mathbf{D}$$

It has **no direct physical interpretation** — it's the force pulled back through $\mathbf{F}^{-1}$, which isn't a force you could measure. It exists because the mathematics is clean, and that's enough: hyperelastic constitutive laws are written as $\mathbf{S} = 2\,\partial W/\partial \mathbf{C}$, and FE codes work internally in $\mathbf{S}$ and $\mathbf{E}$, converting to $\boldsymbol\sigma$ only for output.

> **The practical rule: use Cauchy stress for anything physical — failure, reporting, comparison with experiment. Use $\mathbf{S}$ and $\mathbf{E}$ inside a finite-deformation formulation because the pair is symmetric and conjugate.** In small strain all three coincide, which is why undergraduate courses never mention it.

The engineering-vs-true stress distinction on a tensile curve is exactly $\mathbf{P}$ vs $\boldsymbol\sigma$: the engineering curve falls after the UTS because it keeps dividing by the original area while the specimen necks; the true curve keeps rising.

## You cannot measure stress

Worth stating plainly, because it's easy to forget.

There is no stress gauge. What you measure is **force** (a load cell) or **strain** (a gauge or DIC), and stress is *inferred*:

$$\text{measured strain} \xrightarrow{\text{constitutive model}} \text{stress}$$

So every stress number carries the assumptions of the model used to compute it. If the material yielded and you used a linear-elastic relation, your "measured" stress is wrong — and it will look entirely plausible.

Photoelasticity and X-ray diffraction come closest to direct measurement, and both still infer through a physical model.

**This is a good instance of the general point from [[engineering/README|the domain note]]:** the balance laws are certain, the constitutive model is chosen, and that's where the error lives.

## Equilibrium

Static force balance, which is what most of solid mechanics solves:

$$\sigma_{ij,j} + \rho b_i = 0$$

The divergence of the stress tensor plus body force per unit volume equals zero. Three equations, six unknown stress components — **underdetermined**, which is why you need compatibility and a constitutive law to close the system.

With acceleration it's Cauchy's equation of motion, and it's the same equation that becomes Navier–Stokes for a fluid and the Navier equations for an elastic solid. **One equation, two fields.** → [[engineering/01-continuum-mechanics/06-conservation-laws|Conservation Laws]]

---

## Related
- [[engineering/01-continuum-mechanics/04-strain-measures|Strain Measures]] — the conjugate quantity
- [[engineering/01-continuum-mechanics/06-conservation-laws|Conservation Laws]] — where equilibrium comes from
- [[engineering/01-continuum-mechanics/12-failure-and-yield|Failure and Yield]] — what principal stresses predict
- [[engineering/01-continuum-mechanics/README|Continuum mechanics map]]
