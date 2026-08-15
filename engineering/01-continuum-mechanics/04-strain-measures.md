# Strain Measures

**[Intermediate → Advanced]** — Why there are several definitions of "how much has this deformed", which to use when, and the one that quietly breaks under rotation.

## The requirement

Strain must measure **deformation only**. Translate a body across the room and rotate it — nothing has deformed, and every strain measure must return zero.

That sounds obvious and it's exactly where the naive definition fails.

The natural building block is the change in length of a material fibre. Take $d\mathbf{X}$ in the reference configuration; it becomes $d\mathbf{x} = \mathbf{F}\,d\mathbf{X}$. Compare squared lengths:

$$|d\mathbf{x}|^2 = d\mathbf{X}^T\mathbf{F}^T\mathbf{F}\,d\mathbf{X}$$

**Squared lengths, because that avoids a square root and keeps everything polynomial in $\mathbf{F}$.**

## The Cauchy–Green tensors

$$\mathbf{C} = \mathbf{F}^T\mathbf{F} \qquad \text{right Cauchy–Green (material)}$$
$$\mathbf{b} = \mathbf{F}\mathbf{F}^T \qquad \text{left Cauchy–Green (spatial)}$$

From the [[engineering/01-continuum-mechanics/03-kinematics-of-deformation|polar decomposition]] $\mathbf{F} = \mathbf{R}\mathbf{U}$:

$$\mathbf{C} = \mathbf{U}^T\mathbf{R}^T\mathbf{R}\mathbf{U} = \mathbf{U}^2$$

> **The rotation cancels.** That single line is why every finite-strain measure is built from $\mathbf{C}$ or $\mathbf{b}$ rather than from $\mathbf{F}$ directly, and it's the mechanism that guarantees rigid rotation produces no strain — and therefore no stress.

$\mathbf{C} = \mathbf{I}$ exactly when there is no deformation.

## Green–Lagrange strain

The standard finite-strain measure in solid mechanics:

$$\mathbf{E} = \tfrac{1}{2}(\mathbf{C} - \mathbf{I}) = \tfrac{1}{2}(\mathbf{F}^T\mathbf{F} - \mathbf{I})$$

The $\tfrac{1}{2}$ and the $-\mathbf{I}$ are chosen so that $\mathbf{E} = \mathbf{0}$ for no deformation and $\mathbf{E}$ reduces to the familiar engineering strain when deformations are small.

In terms of displacement:

$$E_{IJ} = \tfrac{1}{2}\left(\frac{\partial u_I}{\partial X_J} + \frac{\partial u_J}{\partial X_I} + \frac{\partial u_K}{\partial X_I}\frac{\partial u_K}{\partial X_J}\right)$$

**The third term is the nonlinear one**, and it's the entire difference between finite and small-strain theory. Drop it and you get the infinitesimal strain tensor.

**Properties:** referred to the reference configuration (material), symmetric, exactly zero under rigid rotation, and **energy-conjugate to the second Piola–Kirchhoff stress** — meaning $\mathbf{S}:\dot{\mathbf{E}}$ is the stress power, which is what makes the pair useful. → [[engineering/01-continuum-mechanics/05-stress|Stress]]

The spatial counterpart is the **Almansi–Euler strain** $\mathbf{e} = \tfrac{1}{2}(\mathbf{I} - \mathbf{b}^{-1})$, used when working in the current configuration.

## Infinitesimal strain

Drop the quadratic term:

$$\varepsilon_{ij} = \tfrac{1}{2}\left(\frac{\partial u_i}{\partial x_j} + \frac{\partial u_j}{\partial x_i}\right) = \tfrac{1}{2}(u_{i,j} + u_{j,i})$$

**This is "strain" in every undergraduate course**, and it's what you use unless something forces otherwise.

Written out:

$$\varepsilon_{11} = \frac{\partial u_1}{\partial x_1} \quad\text{(normal strain: fractional length change)}$$
$$\varepsilon_{12} = \tfrac{1}{2}\left(\frac{\partial u_1}{\partial x_2} + \frac{\partial u_2}{\partial x_1}\right) \quad\text{(shear strain: half the angle change)}$$

**Dimensionless.** Usually reported in microstrain ($\mu\varepsilon = 10^{-6}$), because real strains in metals are tiny — steel yields around 0.2%, i.e. 2000 $\mu\varepsilon$.

### The engineering shear strain trap

$$\gamma_{12} = 2\varepsilon_{12}$$

**Engineering shear strain $\gamma$ is twice the tensor shear strain $\varepsilon_{12}$.**

$\gamma$ is the *total* angle change between two initially perpendicular fibres, which is the physically intuitive quantity and what a strain gauge rosette reports. $\varepsilon_{12}$ is the tensor component, which is half of it because the tensor splits the angle change symmetrically between the two directions.

> **This factor of two causes more errors than anything else in elasticity.** It's why Voigt notation (which packs the symmetric tensor into a 6-vector for matrix computation) uses $[\varepsilon_{11}, \varepsilon_{22}, \varepsilon_{33}, \gamma_{23}, \gamma_{13}, \gamma_{12}]$ with $\gamma$ not $\varepsilon$ in the shear slots — and why the compliance and stiffness matrices in Voigt form are *not* simple inverses of each other unless you're careful. Check the convention of any formula, table, or FE code you use.

### Where infinitesimal strain breaks

The important failure, and it's not where people expect. Consider a **pure rigid rotation** by angle $\theta$ about the 3-axis:

$$\mathbf{F} = \begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1\end{bmatrix}$$

Green–Lagrange gives $\mathbf{E} = \tfrac{1}{2}(\mathbf{F}^T\mathbf{F} - \mathbf{I}) = \mathbf{0}$ exactly. Correct — nothing deformed.

Infinitesimal strain gives $\varepsilon_{11} = \cos\theta - 1 \approx -\theta^2/2$.

**Spurious compressive strain, purely from rotating.** At $\theta = 0.1$ rad (5.7°) that's $-5000\ \mu\varepsilon$ — larger than the yield strain of steel, from a rotation that deformed nothing.

**So the criterion is small *rotations*, not just small strains.** A cantilever beam whose tip deflects 20% of its length has strains under 1% and rotations of ~0.2 rad — small strain gets it visibly wrong. That's a common and genuinely surprising failure, and it's why FE codes have a "large displacement / nonlinear geometry" switch that you should turn on more often than you might think.

## The other measures

Several exist because different problems make different ones natural:

| Measure | Definition | Used for |
|---|---|---|
| **Stretch ratio** | $\lambda = \ell/\ell_0$ | rubber, biomechanics — the raw quantity |
| **Engineering / nominal** | $\varepsilon_e = (\ell - \ell_0)/\ell_0 = \lambda - 1$ | tensile test reporting |
| **True / logarithmic (Hencky)** | $\varepsilon_t = \ln(\ell/\ell_0) = \ln\lambda$ | plasticity, metal forming |
| **Green–Lagrange** | $E = \tfrac{1}{2}(\lambda^2 - 1)$ | finite-strain solid mechanics |
| **Almansi** | $e = \tfrac{1}{2}(1 - \lambda^{-2})$ | spatial formulations |

All agree to first order for small strain. They diverge fast:

| $\lambda$ | eng. | true | Green |
|---|---|---|---|
| 1.01 | 0.010 | 0.010 | 0.010 |
| 1.1 | 0.100 | 0.095 | 0.105 |
| 1.5 | 0.500 | 0.405 | 0.625 |
| 2.0 | 1.000 | 0.693 | 1.500 |

**True strain is additive and symmetric**, which is why plasticity uses it. Stretch from 1 to 2 then back to 1: true strain gives $+0.693$ then $-0.693$, summing to zero. Engineering strain gives $+1.0$ then $-0.5$, which doesn't. For a process with many increments — rolling, drawing, forging — that additivity is essential.

It's also why a **true stress–true strain** curve keeps rising past the ultimate tensile strength while the engineering curve turns over: the engineering curve divides by the original area while the specimen is necking down.

## Reading a strain state

The same tools as any symmetric tensor. → [[engineering/01-continuum-mechanics/02-index-notation-and-tensors|note 02]]

**Principal strains** — eigenvalues of $\boldsymbol{\varepsilon}$. In principal directions there is **no shear**, only stretching. Brittle materials crack perpendicular to the maximum principal strain, so those directions predict crack orientation.

**Volumetric strain** — the trace:

$$\varepsilon_v = \varepsilon_{kk} = \frac{\Delta V}{V_0}$$

**Incompressible ⟺ $\varepsilon_{kk} = 0$**, which is the small-strain version of $J = 1$.

**The deviatoric split:**

$$\varepsilon_{ij} = \tfrac{1}{3}\varepsilon_{kk}\delta_{ij} + e_{ij}$$

Volume change plus shape change. **Metals yield on $e_{ij}$ alone** — hydrostatic compression doesn't cause plastic flow, which is why a solid steel ball is unharmed at the bottom of the ocean while a hollow one implodes. → [[engineering/01-continuum-mechanics/12-failure-and-yield|Failure and Yield]]

## Measuring it

Strain is one of the few quantities here you measure directly.

**Strain gauges** — a foil resistor bonded to the surface; stretching it changes resistance. Reports strain in one direction, so a **rosette** (three gauges at 0°/45°/90°) is needed to reconstruct the in-plane state. Reads $\gamma$, not $\varepsilon_{12}$ — the factor-of-two trap again. → [[hardware/01-electricity|Hardware: Electricity]] for the Wheatstone bridge that makes the tiny resistance change measurable.

**Digital image correlation (DIC)** — spray a speckle pattern, photograph before and after, and track the pattern computationally. Gives a **full field** rather than points, and it's become the standard experimental method.

**Extensometers** — direct length measurement across a gauge length. What a tensile test uses.

**You cannot measure stress.** You measure strain (or force and area) and *infer* stress through a constitutive model. That inference is where the modelling assumption enters, and it's worth being conscious of — a "measured stress" is always a computed one. → [[engineering/01-continuum-mechanics/07-constitutive-models|Constitutive Models]]

---

## Related
- [[engineering/01-continuum-mechanics/03-kinematics-of-deformation|Kinematics of Deformation]] — where $\mathbf{F}$ comes from
- [[engineering/01-continuum-mechanics/05-stress|Stress]] — the conjugate quantity
- [[engineering/01-continuum-mechanics/08-linear-elasticity|Linear Elasticity]] — strain's first real use
- [[engineering/01-continuum-mechanics/10-finite-deformation|Finite Deformation]] — when small strain fails
- [[engineering/01-continuum-mechanics/README|Continuum mechanics map]]
