# Index Notation and Tensors

**[Intermediate → Advanced]** — The language the whole field is written in. An afternoon spent here saves weeks of confusion later.

## Why index notation

Vector notation runs out. You can write $\mathbf{a} \cdot \mathbf{b}$ and $\mathbf{a} \times \mathbf{b}$, but there's no clean symbol for the double contraction of a fourth-order stiffness tensor with a strain tensor.

Index notation writes components and lets bookkeeping rules do the work:

$$\mathbf{a} \cdot \mathbf{b} = a_i b_i \qquad\qquad \sigma_{ij} = C_{ijkl}\,\varepsilon_{kl}$$

The second one is the general form of Hooke's law. There is no vector-notation equivalent that's readable.

## The summation convention

**A repeated index in a term is summed over.** Einstein's convention, and it removes an enormous amount of $\sum$ clutter.

$$a_i b_i \equiv \sum_{i=1}^{3} a_i b_i = a_1b_1 + a_2b_2 + a_3b_3$$

Two kinds of index:

**Dummy (repeated)** — summed over, and its name is arbitrary. $a_i b_i = a_k b_k$.

**Free (appears once)** — ranges over 1,2,3, and **must match on both sides of an equation**.

$$c_i = A_{ij} b_j$$

Here $j$ is dummy (summed), $i$ is free. This is three equations, one per value of $i$ — a matrix–vector product written in four characters.

**The rules that catch errors:**

1. **Free indices must match on both sides.** $c_i = A_{ij}b_j$ ✓. $c_i = A_{ij}b_i$ ✗ — the left has one free index, the right has none
2. **An index may appear at most twice per term.** $a_i b_i c_i$ is meaningless
3. **Rename dummy indices freely**, but never to collide with a free index

> **Index-matching is your unit check.** If the free indices don't balance, the equation is wrong — no physics required to see it. This catches most algebra errors in the field.

## Kronecker delta and permutation symbol

Two objects that do all the work.

$$\delta_{ij} = \begin{cases} 1 & i = j \\ 0 & i \neq j \end{cases}$$

The identity matrix. Its useful property is **index substitution**:

$$\delta_{ij}\,a_j = a_i \qquad \delta_{ij}\,\delta_{jk} = \delta_{ik} \qquad \delta_{ii} = 3$$

That last one is a common slip — it's summed, so it's 3 in three dimensions, not 1.

$$\epsilon_{ijk} = \begin{cases} +1 & (i,j,k) \text{ a cyclic permutation of } 1,2,3 \\ -1 & \text{anticyclic} \\ 0 & \text{any repeated index} \end{cases}$$

The permutation (Levi-Civita) symbol, which encodes the cross product and the determinant:

$$(\mathbf{a} \times \mathbf{b})_i = \epsilon_{ijk}a_j b_k \qquad\qquad \det(\mathbf{A}) = \epsilon_{ijk}A_{1i}A_{2j}A_{3k}$$

And the identity that resolves most cross-product manipulations:

$$\epsilon_{ijk}\epsilon_{ilm} = \delta_{jl}\delta_{km} - \delta_{jm}\delta_{kl}$$

Memorise that one — it's how you prove $\nabla \times (\nabla \times \mathbf{v}) = \nabla(\nabla\cdot\mathbf{v}) - \nabla^2\mathbf{v}$, which appears in both elasticity and fluid dynamics.

## What a tensor actually is

Not "a multidimensional array". That's the *representation*, and confusing the two causes real trouble.

> **A tensor is a physical or geometric object whose components transform in a specific way when you change coordinate systems.**

The defining property is the transformation rule. Under a rotation $Q_{ij}$ (an orthogonal matrix taking old axes to new):

$$\text{scalar (order 0):} \quad \phi' = \phi$$
$$\text{vector (order 1):} \quad a'_i = Q_{ij}a_j$$
$$\text{order 2:} \quad \sigma'_{ij} = Q_{ik}Q_{jl}\,\sigma_{kl}$$
$$\text{order 4:} \quad C'_{ijkl} = Q_{im}Q_{jn}Q_{ko}Q_{lp}\,C_{mnop}$$

**One $Q$ per index.** That's the whole pattern.

**Why this matters physically:** a tensor represents something real, so it must not depend on your choice of axes. The stress state at a point is a fact about the material; the nine numbers you write down depend on how you oriented your coordinate system. The transformation rule is what guarantees both descriptions mean the same thing.

**A 3×3 array of numbers is not automatically a tensor.** If it doesn't transform correctly, it's just an array — and any equation you write with it isn't a physical law, because it would say something different in rotated coordinates.

This is also the deep reason [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/02-matrices|"tensor" in machine learning]] means something looser: a PyTorch tensor is an n-dimensional array with no transformation law attached. Same word, different concept, and it's worth keeping straight.

## Operations

```
aᵢbᵢ                    inner product          → scalar
aᵢbⱼ                    outer product          → order 2
σᵢⱼnⱼ                   contraction            → vector
σᵢⱼεᵢⱼ                  double contraction     → scalar
σᵢᵢ                     trace                  → scalar (invariant)
```

**Contraction lowers the order by two**, once per summed pair. That's why $C_{ijkl}\varepsilon_{kl}$ (order 4 contracted with order 2 over two indices) gives order 2.

**Symmetric and antisymmetric parts.** Any second-order tensor splits uniquely:

$$A_{ij} = \underbrace{\tfrac{1}{2}(A_{ij} + A_{ji})}_{\text{symmetric}} + \underbrace{\tfrac{1}{2}(A_{ij} - A_{ji})}_{\text{antisymmetric}}$$

This split is physically meaningful and appears repeatedly: the velocity gradient splits into **rate of deformation** (symmetric — actual stretching) and **spin** (antisymmetric — rigid rotation). Only the symmetric part causes stress in a fluid. → [[engineering/01-continuum-mechanics/03-kinematics-of-deformation|Kinematics]]

A symmetric 3×3 tensor has **6 independent components**, an antisymmetric one has 3 (which is why it can be represented as a vector — the axial vector).

**The volumetric/deviatoric split** is the other decomposition that matters:

$$\sigma_{ij} = \underbrace{\tfrac{1}{3}\sigma_{kk}\,\delta_{ij}}_{\text{hydrostatic}} + \underbrace{s_{ij}}_{\text{deviatoric}}$$

Pressure changes volume; the deviator changes shape. **Metals yield on the deviatoric part alone** — hydrostatic pressure doesn't cause plastic flow, which is why deep-sea pressure crushes a hollow sphere but doesn't yield a solid one. → [[engineering/01-continuum-mechanics/12-failure-and-yield|Failure and Yield]]

## Eigenvalues, principal values, invariants

For a symmetric tensor, the eigenvalue problem

$$\sigma_{ij}n_j = \lambda\, n_i$$

has three real eigenvalues and mutually orthogonal eigenvectors.

**Physically:** there exists an orientation in which the stress tensor is diagonal — **no shear**, only normal stresses. Those are the **principal stresses** $\sigma_1 \geq \sigma_2 \geq \sigma_3$ and the eigenvectors are the principal directions.

That's why a brittle material fails on a plane perpendicular to the maximum principal stress, and it's the basis of most failure criteria.

The characteristic equation gives three **invariants** — quantities unchanged by rotation:

$$I_1 = \sigma_{kk} \qquad I_2 = \tfrac{1}{2}(\sigma_{ii}\sigma_{jj} - \sigma_{ij}\sigma_{ij}) \qquad I_3 = \det(\boldsymbol\sigma)$$

**Invariants are how you write a physical law that doesn't depend on orientation.** An isotropic material's response can only depend on invariants — that's not a convenience, it's forced by the symmetry. → [[engineering/01-continuum-mechanics/07-constitutive-models|Constitutive Models]]

The von Mises stress is built from the second deviatoric invariant, which is why it's a single number you can compare against a yield stress regardless of how the load is oriented.

## Tensor calculus

Derivatives in index notation. The comma convention is standard and worth adopting:

$$\phi_{,i} \equiv \frac{\partial \phi}{\partial x_i}$$

$$\text{gradient of a scalar:} \quad (\nabla \phi)_i = \phi_{,i}$$
$$\text{divergence of a vector:} \quad \nabla \cdot \mathbf{v} = v_{i,i}$$
$$\text{gradient of a vector:} \quad (\nabla \mathbf{v})_{ij} = v_{i,j}$$
$$\text{divergence of a tensor:} \quad (\nabla \cdot \boldsymbol\sigma)_i = \sigma_{ij,j}$$
$$\text{Laplacian:} \quad \nabla^2\phi = \phi_{,ii}$$

**The divergence of the stress tensor is the one that matters** — $\sigma_{ij,j}$ is the net internal force per unit volume, and it's the heart of the momentum balance.

**The divergence theorem** converts surface integrals to volume integrals:

$$\int_S \sigma_{ij}n_j\,dS = \int_V \sigma_{ij,j}\,dV$$

Every balance law in this field is derived by writing it as a surface plus volume integral, applying this, and arguing that since the volume is arbitrary the integrand must vanish. **That derivation pattern appears four times in note 05** — learn it once. → [[engineering/01-continuum-mechanics/06-conservation-laws|Conservation Laws]]

## Practical advice

1. **Check free indices on both sides.** It's free error detection
2. **$\delta_{ii} = 3$, not 1**
3. **Never let an index appear three times.** Rename the dummy
4. **Learn the $\epsilon$-$\delta$ identity** — it resolves most curl manipulations
5. **Symmetric ⟹ 6 components, real eigenvalues, orthogonal eigenvectors.** Almost every tensor here is symmetric
6. **When a law must be orientation-independent, write it in invariants**
7. **Cartesian only, for now.** These notes assume rectangular coordinates, where covariant and contravariant components coincide and you can ignore the distinction. Curvilinear coordinates (cylindrical, spherical) reintroduce it along with Christoffel symbols — necessary for shells and for general relativity, and out of scope here

---

## Related
- [[engineering/01-continuum-mechanics/03-kinematics-of-deformation|Kinematics of Deformation]] — the first real use
- [[engineering/01-continuum-mechanics/05-stress|Stress]] — the tensor that motivates all of this
- [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|Linear Algebra]] — eigenvalues, at the level ML needs
- [[engineering/01-continuum-mechanics/README|Continuum mechanics map]]
