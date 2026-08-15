# Viscous Fluids and Navier–Stokes

**[Advanced]** — The same balance laws with a rate-dependent constitutive model, one nonlinear term, and a Millennium Prize problem.

## Newtonian fluids

A fluid cannot sustain shear at rest. So stress depends on the **rate** of deformation, not the amount:

$$\boxed{\sigma_{ij} = -p\,\delta_{ij} + 2\mu D_{ij} + \lambda' D_{kk}\delta_{ij}}$$

where $D_{ij} = \tfrac{1}{2}(v_{i,j} + v_{j,i})$ is the rate of deformation. For incompressible flow, $D_{kk}=0$ and the last term drops:

$$\sigma_{ij} = -p\,\delta_{ij} + 2\mu D_{ij}$$

Compare with [[engineering/01-continuum-mechanics/08-linear-elasticity|Hooke's law]] — identical structure, with strain replaced by strain *rate*. That's the entire solid/fluid distinction. → [[engineering/01-continuum-mechanics/01-what-continuum-mechanics-is|note 01]]

**It depends on $\mathbf{D}$, never on the spin $\mathbf{W}$.** A bucket of water in steady solid-body rotation has $\mathbf{D} = \mathbf{0}$ and experiences no viscous stress — correct, since it isn't deforming. If viscous stress depended on the full velocity gradient, spinning a bucket would heat the water. → [[engineering/01-continuum-mechanics/03-kinematics-of-deformation|Kinematics]]

**Viscosity** $\mu$ in Pa·s. Air ≈ $1.8\times10^{-5}$, water ≈ $10^{-3}$, olive oil ≈ 0.08, honey ≈ 10, pitch ≈ $2\times10^8$. **Kinematic viscosity** $\nu = \mu/\rho$ (m²/s) is what actually appears in the equations — and note air's $\nu$ is about **15× water's**, despite being far less viscous, because it's so much less dense.

## The Navier–Stokes equations

Substitute the Newtonian model into [[engineering/01-continuum-mechanics/06-conservation-laws|the momentum balance]]:

$$\boxed{\rho\left(\frac{\partial v_i}{\partial t} + v_j\frac{\partial v_i}{\partial x_j}\right) = -\frac{\partial p}{\partial x_i} + \mu\frac{\partial^2 v_i}{\partial x_j \partial x_j} + \rho b_i}$$

with incompressibility as a constraint:

$$\frac{\partial v_i}{\partial x_i} = 0$$

Reading the terms:

$$\underbrace{\rho\frac{\partial \mathbf{v}}{\partial t}}_{\text{unsteady}} + \underbrace{\rho(\mathbf{v}\cdot\nabla)\mathbf{v}}_{\textbf{convective — the problem}} = \underbrace{-\nabla p}_{\text{pressure}} + \underbrace{\mu\nabla^2\mathbf{v}}_{\text{viscous}} + \underbrace{\rho\mathbf{b}}_{\text{body force}}$$

**Four equations** (three momentum + continuity), **four unknowns** ($v_1, v_2, v_3, p$). Closed — and unsolved in general.

## The convective term

$(\mathbf{v}\cdot\nabla)\mathbf{v}$ is **quadratic in the unknown**, and it is the source of essentially every difficulty in fluid dynamics.

Without it, Navier–Stokes is a linear PDE with well-understood solutions. With it:

- **No general analytical solution exists.** A handful of exact solutions are known for highly symmetric cases
- **Turbulence.** Energy cascades from large eddies to small, chaotically
- **Sensitivity to initial conditions** — the origin of the "butterfly effect"
- **The Clay Millennium Prize** asks whether smooth solutions exist for all time in 3D. Unsolved

**It also explains steady acceleration.** In a converging nozzle at steady state, $\partial\mathbf{v}/\partial t = 0$ everywhere and fluid still speeds up, because it moves into a region of higher velocity. That's convection, and it catches people constantly. → [[engineering/01-continuum-mechanics/03-kinematics-of-deformation|material derivative]]

## The Reynolds number

Non-dimensionalise and one parameter emerges:

$$\boxed{Re = \frac{\rho V L}{\mu} = \frac{VL}{\nu} = \frac{\text{inertial forces}}{\text{viscous forces}}}$$

**The single most important number in fluid mechanics.**

| $Re$ | Regime |
|---|---|
| $\ll 1$ | **Stokes flow** — viscosity dominates, inertia negligible |
| $\sim 1$–$10^3$ | laminar, both matter |
| $\sim 2300$ | **transition** in a pipe |
| $> 10^4$ | **turbulent** — inertia dominates |

Typical values: bacteria swimming $10^{-5}$ · blood in capillaries $10^{-3}$ · a fish $10^4$ · a car $10^7$ · an airliner $10^8$.

**Dynamic similarity** is why this matters commercially: two flows with the same $Re$ and the same geometry are the *same flow*, scaled. A 1:50 scale model in a wind tunnel at matched $Re$ predicts the full-size behaviour. Every wind tunnel, tow tank and pipe-flow correlation depends on it.

**Low-Reynolds intuition is genuinely alien.** At $Re \ll 1$ the convective term vanishes and Stokes flow is **linear and time-reversible** — reverse the forcing and the fluid retraces its path exactly. That's why bacteria can't swim with a reciprocating motion (Purcell's "scallop theorem") and why they use rotating flagella instead. It's also why stirring dye into glycerine can be un-stirred by reversing the rotation, which is a genuinely startling demonstration.

## Boundary conditions

**The no-slip condition** — fluid velocity at a solid wall equals the wall's velocity:

$$\mathbf{v}_{\text{fluid}} = \mathbf{v}_{\text{wall}} \quad\text{at the surface}$$

Experimentally verified, and it's the origin of viscous drag, boundary layers, and why a fan blade gathers dust rather than blowing it off — the air right at the surface isn't moving.

(It fails for rarefied gases where the Knudsen number is significant, and for some engineered superhydrophobic surfaces, where slip is real and useful.)

**Free surface** — traction continuity, plus surface tension where curvature matters.

**Inlet/outlet** — prescribed velocity or pressure. Outlet conditions are a persistent practical headache in CFD: place the boundary too close to a body and it contaminates the solution.

## Boundary layers

Prandtl's 1904 insight, which created modern aerodynamics.

At high $Re$, viscosity is negligible almost everywhere — **except in a thin layer near a wall**, where no-slip forces the velocity from zero to the free-stream value.

```
free stream  →→→→→→→→→→→→→→→→
                    ↑ δ (boundary layer thickness)
             →→→→→→
             →→→
             →
═══════════════════════════════  wall (v = 0)
```

$$\frac{\delta}{L} \sim \frac{1}{\sqrt{Re}}$$

**This resolves d'Alembert's paradox** — inviscid theory predicts zero drag on any body, which is obviously wrong. The resolution: viscosity matters in a vanishingly thin layer, and that layer determines the drag on the entire body.

**Separation** is the consequence that matters. Against an adverse pressure gradient (pressure rising downstream), the boundary layer can reverse and detach:

- **Attached flow** → low drag, high lift
- **Separated flow** → wake, high pressure drag, **stall**

Nearly all aerodynamic design is about controlling separation. Golf-ball dimples work by **tripping the boundary layer turbulent** — a turbulent layer has more momentum near the wall, resists separation longer, gives a narrower wake, and roughly halves the drag. A dimpled ball flies about twice as far as a smooth one.

## Exact solutions

Very few exist, and they're worth knowing because they anchor intuition.

**Couette flow** — between parallel plates, one moving. **Linear** velocity profile.

**Poiseuille flow** — pressure-driven in a pipe. **Parabolic** profile, giving the Hagen–Poiseuille law:

$$Q = \frac{\pi R^4 \Delta p}{8\mu L}$$

**Flow rate goes as $R^4$.** Halving a pipe's radius cuts flow by a factor of 16 at fixed pressure. That's why arterial narrowing is so dangerous, why a partially blocked pipe is dramatically worse than it looks, and why needle gauge matters so much clinically.

**Stokes flow past a sphere** — drag $F = 6\pi\mu R V$, valid for $Re \ll 1$. This is what terminal velocity for dust, mist and sedimenting particles is computed from.

## Turbulence

The unsolved part.

Above a critical $Re$, flow becomes chaotic — three-dimensional, unsteady, with a wide range of eddy sizes.

**The energy cascade** (Kolmogorov): energy enters at large scales, transfers to progressively smaller eddies, and dissipates as heat at the smallest — the **Kolmogorov microscale** $\eta \sim L\,Re^{-3/4}$.

**Why direct simulation is infeasible:** resolving every scale requires roughly $Re^{9/4}$ grid points. For an airliner at $Re = 10^8$, that's around $10^{18}$ cells. DNS is a research tool for low $Re$, not an engineering method.

**So you model instead:**

| Method | Approach | Cost |
|---|---|---|
| **RANS** | time-average; model *all* turbulence ($k$–$\varepsilon$, $k$–$\omega$ SST) | cheap — the industry workhorse |
| **LES** | resolve large eddies, model the small | expensive |
| **DES / hybrid** | RANS near walls, LES elsewhere | in between |
| **DNS** | resolve everything | research only |

**The closure problem:** time-averaging Navier–Stokes produces the **Reynolds stresses** $-\rho\overline{v_i'v_j'}$ — six new unknowns with no new equations. Every turbulence model is a hypothesis about those terms, and **there is no universally correct one.**

That's the same structural situation as [[engineering/01-continuum-mechanics/07-constitutive-models|constitutive modelling]] in solids: the balance laws are certain, the closure is chosen, and that's where the error lives. Turbulence modelling is arguably the largest single source of uncertainty in engineering CFD.

## Compressible flow

When density varies — above roughly Mach 0.3.

$$M = \frac{V}{c}, \qquad c = \sqrt{\gamma R T}$$

Now the [[engineering/01-continuum-mechanics/06-conservation-laws|energy equation]] couples in, and the mathematics changes character:

- **Subsonic ($M<1$)** — elliptic; disturbances propagate upstream, so the flow "knows" about a body before reaching it
- **Supersonic ($M>1$)** — hyperbolic; **nothing propagates upstream**, and you get shock waves
- **Transonic ($M \approx 1$)** — mixed, and the hardest regime to compute

**Shock waves** are near-discontinuities — a few mean free paths thick, across which pressure, density and temperature jump. They're where the continuum hypothesis is stretched thinnest, and they cause **wave drag**, which is the barrier that made supersonic flight hard.

## Computational fluid dynamics

Practically, you solve numerically. The characteristic difficulty is **pressure–velocity coupling**: for incompressible flow, [[engineering/01-continuum-mechanics/06-conservation-laws|continuity is a constraint, not an evolution equation]], and pressure has no equation of its own — it acts as a Lagrange multiplier enforcing $\nabla\cdot\mathbf{v}=0$.

The algorithms that resolve this — **SIMPLE**, PISO, projection methods — are the core of most CFD codes.

**Practical realities:**

- **Finite volume** dominates CFD (conservative by construction), where **finite element** dominates solid mechanics → [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]]
- **Mesh quality near walls is critical.** The $y^+$ value determines whether your turbulence model's wall treatment is valid, and getting it wrong invalidates the result regardless of how fine the rest of the mesh is
- **CFD results are more uncertain than structural FE results**, and it's worth being blunt about that. Turbulence modelling, mesh dependence, and boundary placement all contribute. Validate against experiment where the answer matters

---

## Related
- [[engineering/01-continuum-mechanics/06-conservation-laws|Conservation Laws]] — where these equations come from
- [[engineering/01-continuum-mechanics/07-constitutive-models|Constitutive Models]] — non-Newtonian fluids
- [[engineering/01-continuum-mechanics/03-kinematics-of-deformation|Kinematics]] — the rate of deformation tensor
- [[engineering/01-continuum-mechanics/README|Continuum mechanics map]]
