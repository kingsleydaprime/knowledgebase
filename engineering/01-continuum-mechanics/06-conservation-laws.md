# Conservation Laws

**[Advanced]** — The four balance principles, one derivation pattern used four times, and why the resulting system is deliberately underdetermined.

## The pattern

Every balance law here has the same shape:

> **rate of change of X inside a region = flux of X across its boundary + production of X inside**

And every one is derived the same way:

1. Write the statement as integrals over an arbitrary material volume
2. Convert surface integrals to volume integrals with the **divergence theorem**
3. Collect everything under one integral
4. Argue that since the volume is *arbitrary*, the integrand must vanish pointwise

Step 4 is the move that converts a global statement into a PDE. **Learn the pattern once and all four derivations are the same exercise.** → [[engineering/01-continuum-mechanics/02-index-notation-and-tensors|Index Notation]]

Two tools recur:

**The divergence theorem:** $\displaystyle\int_S a_i n_i\,dS = \int_V a_{i,i}\,dV$

**Reynolds transport theorem** — how to differentiate an integral over a *moving* material volume:

$$\frac{D}{Dt}\int_V \phi\,dV = \int_V \left(\frac{\partial \phi}{\partial t} + (\phi v_i)_{,i}\right)dV$$

That's the material derivative from [[engineering/01-continuum-mechanics/03-kinematics-of-deformation|note 03]], applied to an integral. It's the bridge between "follow the material" and "watch a fixed region".

## 1. Conservation of mass

Mass is neither created nor destroyed.

$$\frac{D}{Dt}\int_V \rho\,dV = 0$$

Apply the pattern:

$$\boxed{\frac{\partial \rho}{\partial t} + (\rho v_i)_{,i} = 0}$$

The **continuity equation**. Equivalently $\dfrac{D\rho}{Dt} + \rho\,v_{i,i} = 0$.

**Incompressible flow** means $D\rho/Dt = 0$, which forces

$$v_{i,i} = \nabla \cdot \mathbf{v} = 0$$

A divergence-free velocity field. This is a **constraint, not an evolution equation** — nothing tells you how it evolves, it must simply hold at every instant. That's what makes incompressible Navier–Stokes awkward to solve numerically: pressure becomes a Lagrange multiplier enforcing the constraint rather than a thermodynamic variable, and you get a saddle-point problem. → [[engineering/01-continuum-mechanics/11-viscous-fluids-and-navier-stokes|Navier–Stokes]]

In Lagrangian (solid) form, mass conservation is simply

$$\rho_0 = J\rho$$

reference density equals Jacobian times current density. Cleaner, and it's one reason solid mechanics prefers the material description.

## 2. Balance of linear momentum

Newton's second law for a continuum. Forces come in two kinds:

- **Body forces** $\rho b_i$ — gravity, electromagnetic, acting throughout the volume
- **Surface tractions** $t_i = \sigma_{ij}n_j$ — contact forces on the boundary

$$\frac{D}{Dt}\int_V \rho v_i\,dV = \int_V \rho b_i\,dV + \int_S \sigma_{ij}n_j\,dS$$

Apply the pattern:

$$\boxed{\sigma_{ij,j} + \rho b_i = \rho\,\frac{Dv_i}{Dt}}$$

**Cauchy's equation of motion**, and the single most important equation in the field.

Everything specialises from it:

| Set | Get |
|---|---|
| $\dfrac{Dv_i}{Dt} = 0$ | **static equilibrium** $\sigma_{ij,j} + \rho b_i = 0$ — most of solid mechanics |
| $\boldsymbol\sigma$ = Newtonian fluid | **Navier–Stokes** |
| $\boldsymbol\sigma$ = Hooke's law | **Navier's equations** of elastodynamics |
| $\boldsymbol\sigma = -p\mathbf{I}$ | **Euler's equations** — inviscid flow |

> **One equation, every material.** The balance law is universal; what changes is the constitutive model you substitute for $\boldsymbol\sigma$. That's the structural point of [[engineering/01-continuum-mechanics/01-what-continuum-mechanics-is|note 01]] made concrete.

Expanding the material derivative gives the nonlinear convective term:

$$\rho\left(\frac{\partial v_i}{\partial t} + v_j v_{i,j}\right) = \sigma_{ij,j} + \rho b_i$$

That $v_j v_{i,j}$ is why fluid dynamics is hard.

## 3. Balance of angular momentum

Moments balance too. Running the same derivation on $\displaystyle\frac{D}{Dt}\int_V \rho\,\epsilon_{ijk}x_j v_k\,dV$ and subtracting the linear-momentum result leaves:

$$\epsilon_{ijk}\,\sigma_{jk} = 0 \quad\Longrightarrow\quad \boxed{\sigma_{ij} = \sigma_{ji}}$$

**Angular momentum balance is exactly the statement that the stress tensor is symmetric.** It contributes no new differential equation — it constrains the stress tensor instead, cutting nine components to six.

That's a genuinely elegant result: a conservation law that shows up as an algebraic symmetry rather than a PDE. → [[engineering/01-continuum-mechanics/05-stress|Stress]]

(In micropolar continua with distributed couples it *does* give an extra equation and $\boldsymbol\sigma$ is non-symmetric — relevant to granular media, out of scope here.)

## 4. Conservation of energy

The first law of thermodynamics for a continuum:

$$\boxed{\rho\,\frac{De}{Dt} = \sigma_{ij}D_{ij} - q_{i,i} + \rho r}$$

where $e$ is internal energy per unit mass, $q_i$ the heat flux, $r$ a heat source, and $D_{ij}$ the rate of deformation.

**The term $\sigma_{ij}D_{ij}$ is the stress power** — the rate at which mechanical work converts to internal energy. It's the reason:

- Repeatedly bending a paperclip heats it — plastic work becomes heat
- Viscous fluids dissipate energy and warm up
- High-speed metal forming needs thermal coupling in the simulation
- Damping in a vibrating structure is energy leaving mechanically and arriving thermally

**Where energy balance matters:** thermo-mechanical coupling (thermal stress, forming, welding), compressible flow (where pressure, density and temperature are linked), and anything where dissipation is significant.

**Where it doesn't:** isothermal small-strain elasticity — which is most of undergraduate solid mechanics, and why the energy equation often goes unmentioned.

## The second law

The **Clausius–Duhem inequality** — entropy production is non-negative:

$$\rho\,\frac{D\eta}{Dt} + \left(\frac{q_i}{T}\right)_{,i} - \frac{\rho r}{T} \geq 0$$

This is *not* a balance law you solve. It's a **restriction on admissible constitutive models.**

Any material law you propose must satisfy it for every conceivable deformation, and that's a genuinely strong filter:

- Viscosity must be **positive** — a "material" with negative viscosity would create energy
- Thermal conductivity must be positive — heat cannot spontaneously flow up a gradient
- Elastic moduli must be positive definite
- Hyperelastic materials must derive stress from a **stored energy potential** — which is what makes them path-independent and non-dissipative

The **Coleman–Noll procedure** is the systematic way to extract these restrictions, and it's why constitutive modelling is a discipline rather than curve-fitting. → [[engineering/01-continuum-mechanics/07-constitutive-models|Constitutive Models]]

## Counting: why the system is underdetermined

The crucial bookkeeping.

**Unknowns** (isothermal, 3D):

| | count |
|---|---|
| density $\rho$ | 1 |
| velocity $v_i$ | 3 |
| stress $\sigma_{ij}$ (symmetric) | 6 |
| **total** | **10** |

**Equations:**

| | count |
|---|---|
| mass | 1 |
| linear momentum | 3 |
| angular momentum | 0 (used up as symmetry) |
| **total** | **4** |

**Six equations short.**

> **The balance laws are universal and therefore incomplete.** They apply equally to steel and water precisely because they say nothing about what the material *is*. The missing six equations are the **constitutive model**, and they are material-specific, empirical, and where every modelling decision lives.

That deficit is not a flaw in the theory — it's the theory correctly separating what is certain (conservation) from what is chosen (material response).

Adding temperature adds one unknown ($T$) and one equation (energy), plus a constitutive law for heat flux (Fourier's law) — the same structure repeats.

## Boundary and initial conditions

A PDE system needs them, and the classification matters:

**Dirichlet (essential)** — prescribed displacement or velocity on part of the boundary. A fixed support.

**Neumann (natural)** — prescribed traction. An applied pressure, or a free surface where $\mathbf{t} = \mathbf{0}$.

**Mixed / Robin** — a relation between them. An elastic foundation, or convective heat transfer.

**Every point of the boundary needs exactly one condition per direction** — you cannot prescribe both displacement and traction in the same direction at the same point, and you must not leave a direction unspecified. Under-constraining is the classic FE error: a model with a rigid-body mode has a singular stiffness matrix, and the solver reports it as "insufficient boundary conditions" or simply fails to converge.

The "essential/natural" naming comes from the variational formulation, where essential conditions must be built into the trial space while natural ones fall out of the weak form automatically. → [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]]

---

## Related
- [[engineering/01-continuum-mechanics/05-stress|Stress]] — what the momentum balance is written in
- [[engineering/01-continuum-mechanics/07-constitutive-models|Constitutive Models]] — the six missing equations
- [[engineering/01-continuum-mechanics/11-viscous-fluids-and-navier-stokes|Navier–Stokes]] — the fluid specialisation
- [[engineering/01-continuum-mechanics/README|Continuum mechanics map]]
