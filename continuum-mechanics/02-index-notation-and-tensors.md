---
id: c7c3b2d3-fce5-4f0f-a0dd-ad87e6b2efbb
---

# Index Notation and Tensors

Index notation is a short way of writing equations that involve many numbers at once, using small letters under the symbols to say which numbers go together. A tensor is a quantity that needs a whole table of numbers to describe it, like the push and pull inside a loaded bridge, and almost every equation in this course is written this way.

## Why index notation
<!-- bite: 73821156-68de-4510-ba75-a4ad0349e7ff -->

Vector notation runs out. You can write $\mathbf{a} \cdot \mathbf{b}$ and $\mathbf{a} \times \mathbf{b}$, but there's no clean symbol for the double contraction of a fourth-order stiffness tensor with a strain tensor.

Index notation writes components and lets bookkeeping rules do the work:

$$\mathbf{a} \cdot \mathbf{b} = a_i b_i \qquad\qquad \sigma_{ij} = C_{ijkl}\,\varepsilon_{kl}$$

The second one is the general form of Hooke's law. Vector notation can write it as $\boldsymbol\sigma = \mathbb{C} : \boldsymbol\varepsilon$, but that hides which indices pair up with which, and that pairing is exactly what you need when you work with it.

> **Tensor algebra is the language of continuum mechanics.** Stress, strain, the deformation gradient, the stiffness of a material: all of them are tensors. This note builds that language from the bottom: vectors and bases first, then the shorthand, then the three ways to multiply vectors, then tensors.

## Vectors, bases and linear independence
<!-- bite: b0e25094-03ab-4d30-a370-d59c1ea365d8 -->

### A vector is a sum of components

A vector is an arrow: it has a length and a direction, and it exists whether or not you draw axes. Once you **do** pick axes, you can describe the arrow as a recipe: "go this far along the first axis, this far along the second, this far along the third."

In the familiar Cartesian orthonormal basis, with unit vectors $\mathbf{i}, \mathbf{j}, \mathbf{k}$:

$$\mathbf{f} = \alpha\,\mathbf{i} + \beta\,\mathbf{j} + \gamma\,\mathbf{k}$$

The numbers $\alpha, \beta, \gamma$ are the **components** (the scaling factors). The unit vectors $\mathbf{i}, \mathbf{j}, \mathbf{k}$ are the **basis**. The vector is the sum of each component times its basis vector.

"Orthonormal" packs two conditions into one word. **Ortho**: the basis vectors are at right angles to each other. **Normal**: each one has length 1.

### Linear independence

A set of vectors is **linearly independent** when you can't build any one of them out of the others. No amount of stretching and adding $\mathbf{i}$ and $\mathbf{j}$ will give you $\mathbf{k}$, so $\mathbf{i}, \mathbf{j}, \mathbf{k}$ are independent.

The formal version: the only way to make

$$c_1\mathbf{v}_1 + c_2\mathbf{v}_2 + c_3\mathbf{v}_3 = \mathbf{0}$$

is to set every $c$ to zero. If some non-zero choice of $c$'s gives zero, then one vector can be written using the others, and the set is **dependent**.

Examples in 2D:

1. $(1, 0)$ and $(0, 1)$ are independent. One points along x, one along y, and neither is a stretched copy of the other.
2. $(1, 2)$ and $(2, 4)$ are dependent, because the second is just twice the first. They point along the same line.
3. **Any three vectors in 2D are dependent.** There's only room for two independent directions in a plane, so the third can always be built from the first two.

### Independence defines dimension

That last example is the key idea. **The dimension of a space is the maximum number of linearly independent vectors it can hold.**

1. A 1D space (a line) holds at most 1 independent vector.
2. A 2D space (a plane) holds at most 2.
3. A 3D space holds at most 3, for example $\mathbf{i}, \mathbf{j}, \mathbf{k}$.

A **basis** is any set of that maximum size that is independent. Any vector in the space can then be written as a sum of basis vectors, in exactly one way.

### Renaming the basis: parsimony

Now change the naming. Instead of $\mathbf{i}, \mathbf{j}, \mathbf{k}$, call the basis vectors $\mathbf{e}_1, \mathbf{e}_2, \mathbf{e}_3$. Instead of $\alpha, \beta, \gamma$, call the components $a_1, a_2, a_3$:

$$\mathbf{f} = a_1\mathbf{e}_1 + a_2\mathbf{e}_2 + a_3\mathbf{e}_3 = \sum_{i=1}^{3} a_i\,\mathbf{e}_i$$

The trick is **mixing a letter with a number**: the letter says *what kind* of thing it is (a component $a$, or a basis vector $\mathbf{e}$), and the subscript number says *which one*. This achieves **parsimony**, which means saying the same thing with fewer symbols.

1. **Fewer symbols.** The Cartesian form needs 6 different letters ($\alpha, \beta, \gamma, \mathbf{i}, \mathbf{j}, \mathbf{k}$). The indexed form needs 2 ($a$ and $\mathbf{e}$).
2. **It scales.** In a 10D space, the old way needs 10 component letters plus 10 basis letters, about 20 symbols, and you'd run out of Greek. The indexed way still needs just 2: $\mathbf{f} = \sum_{i=1}^{10} a_i\mathbf{e}_i$.
3. **It works for any basis.** The $\mathbf{e}_i$ don't have to be $\mathbf{i}, \mathbf{j}, \mathbf{k}$. They can be any independent set, which matters as soon as you rotate the axes (see "Changing basis" below). **From here on, the basis is always orthonormal** (rotated or not), because the shortcuts below, especially $\mathbf{e}_i\cdot\mathbf{e}_j = \delta_{ij}$, only hold for orthonormal bases.

### Standard summation, before Einstein

What we have above is **standard summation**: the $\sum$ sign is written out. The same style writes a matrix times a vector like this:

$$y_i = \sum_{j=1}^{3} a_{ij}\,x_j, \qquad i = 1, 2, 3$$

Read it as: "for each $i$ from 1 to 3, add up $a_{ij}x_j$ over $j$." That's three equations:

$$y_1 = a_{11}x_1 + a_{12}x_2 + a_{13}x_3$$
$$y_2 = a_{21}x_1 + a_{22}x_2 + a_{23}x_3$$
$$y_3 = a_{31}x_1 + a_{32}x_2 + a_{33}x_3$$

> **Watch the left-hand side.** It's $y_i$, not $y_{ij}$. Once $j$ has been summed away it no longer exists, so it can't appear on the left. This is the first of the index rules below, and it's an easy slip when copying from the board.

Notice something about every one of these sums: **the index being summed always appears twice in the term**, and the other index appears once. Einstein noticed the same thing and dropped the $\sum$ sign.

## The summation convention
<!-- bite: e2660bc7-1eaa-499e-bdad-7324b05424dc -->

**A repeated index in a term is summed over.** Einstein's convention, and it removes an enormous amount of $\sum$ clutter. It is the standard notation for vectors and tensors, and every text in this field assumes it without saying so.

$$a_i b_i \equiv \sum_{i=1}^{3} a_i b_i = a_1b_1 + a_2b_2 + a_3b_3$$

So $\mathbf{f} = \sum_i a_i\mathbf{e}_i$ becomes just $\mathbf{f} = a_i\mathbf{e}_i$, and $y_i = \sum_j a_{ij}x_j$ becomes $y_i = a_{ij}x_j$.

### What a "term" is

The convention says "repeated **in a term**", so the word matters. A **term** is one piece of an expression separated from the others by $+$, $-$ or $=$. Everything multiplied together inside that piece belongs to the same term.

1. $a_{ij}x_j$ is one term. $j$ appears twice in it, so it's summed.
2. $a_i b_i + c_i d_i$ has two terms. $i$ is repeated in each one separately, so each term is its own sum: $(a_1b_1 + a_2b_2 + a_3b_3) + (c_1d_1 + c_2d_2 + c_3d_3)$.
3. $a_i + b_i$ has two terms, and $i$ appears **once** in each, so there's no sum. $i$ is free, and it's the same free index in both terms, which is required.

Two kinds of index:

**Dummy (repeated)** — summed over, and its name is arbitrary. $a_i b_i = a_k b_k$.

**Free (appears once)** — ranges over 1,2,3, and **must match on both sides of an equation**.

$$c_i = A_{ij} b_j$$

Here $j$ is dummy (summed), $i$ is free. This is three equations, one per value of $i$ — a matrix–vector product written in four characters.

**The rules that catch errors:**

1. **Free indices must match on both sides.** $c_i = A_{ij}b_j$ ✓. $c_i = A_{ij}b_i$ ✗ — on the right, $i$ is repeated (so summed) and $j$ is left free, so the left's free index is $i$ but the right's is $j$
2. **An index may appear at most twice per term.** $a_i b_i c_i$ is meaningless
3. **Rename dummy indices freely**, but never to collide with a free index

> **Index-matching is your unit check.** If the free indices don't balance, the equation is wrong — no physics required to see it. This catches most algebra errors in the field.

### How to read an index equation

Take

$$a_{ij}\,a_{jk} = b_{ik}$$

Read it in three steps.

1. **Find the repeated index.** $j$ appears twice in the left-hand term, so there is a sum over $j$.
2. **Find the free indices.** $i$ and $k$ each appear once, on both sides. They balance, so the equation is well-formed.
3. **Count the equations.** Each free index takes the values 1, 2, 3. Two free indices give $3 \times 3 = 9$ equations, one for each pair $(i, k)$.

**Expanded**, one of the nine (pick $i = 1$, $k = 2$) is:

$$b_{12} = a_{11}a_{12} + a_{12}a_{22} + a_{13}a_{32}$$

That's row 1 of $\mathbf{A}$ multiplied entry by entry with column 2 of $\mathbf{A}$, then added up. It is exactly how you'd compute entry $(1,2)$ of the matrix product $\mathbf{A}\mathbf{A}$. So the index equation **is** the matrix equation $\mathbf{A}\mathbf{A} = \mathbf{B}$, written one entry at a time.

The general pattern: **a repeated index on the inside** (the second index of the first factor and the first index of the second factor, like the $j$ in $a_{ij}a_{jk}$) is a matrix product. Move the repeated index and the meaning changes. $a_{ji}a_{jk}$ sums down column $i$ against column $k$, which is $\mathbf{A}^\mathsf{T}\mathbf{A}$.

## The Kronecker delta
<!-- bite: a7599ad4-4d79-45b2-8caf-387249361390 -->

### Where it comes from

Take two basis vectors from an orthonormal basis and dot them together. Two different ones are at right angles, so they give 0. A basis vector with itself has length 1, so it gives 1:

$$\mathbf{e}_1\cdot\mathbf{e}_1 = 1, \qquad \mathbf{e}_1\cdot\mathbf{e}_2 = 0, \qquad \mathbf{e}_2\cdot\mathbf{e}_3 = 0, \;\ldots$$

That's 9 facts. The Kronecker delta is just a name for all 9 at once:

$$\mathbf{e}_i\cdot\mathbf{e}_j = \delta_{ij} = \begin{cases} 1 & i = j \\ 0 & i \neq j \end{cases}$$

Write the 9 values in a grid and you get the identity matrix. **$\delta_{ij}$ is the identity matrix written in index form.** That's all it is.

### What it does: index substitution

Its useful property is that it **swaps one index for another**:

$$\delta_{ij}\,a_j = a_i$$

Why? $j$ is repeated, so expand the sum:

$$\delta_{ij}a_j = \delta_{i1}a_1 + \delta_{i2}a_2 + \delta_{i3}a_3$$

Pick $i = 2$. Then $\delta_{21} = 0$, $\delta_{22} = 1$, $\delta_{23} = 0$, and the whole thing collapses to $a_2$. Whatever $i$ is, only the term where $j$ equals $i$ survives. So the delta "kills" the sum and replaces $j$ with $i$.

Think of $\delta_{ij}$ as a filter: **"keep only the term where the two indices are equal."** The same reasoning gives:

$$\delta_{ij}\,\delta_{jk} = \delta_{ik} \qquad\qquad \delta_{ii} = \delta_{11} + \delta_{22} + \delta_{33} = 3$$

That last one is a common slip — it's summed, so it's 3 in three dimensions, not 1.

## The Levi-Civita (alternating) symbol
<!-- bite: a226ab78-3a39-4c41-bea2-2e1bb5c51da8 -->

### What it is

The Levi-Civita symbol $\epsilon_{ijk}$, also called the **alternating symbol** or **permutation symbol**, is a **three-index symbol**. Each index runs over 1, 2, 3, so there are $3\times3\times3 = 27$ possible combinations. Every one of them is $+1$, $-1$ or $0$, by this rule:

$$\epsilon_{ijk} = \begin{cases} +1 & (i,j,k) \text{ is a cyclic arrangement of } 1,2,3 \\ -1 & (i,j,k) \text{ is an acyclic (anticyclic) arrangement} \\ 0 & \text{any index repeats} \end{cases}$$

### Cyclic and acyclic arrangements

Write 1, 2, 3 around a circle, clockwise.

```text
        1
      ↗   ↘
     3  ←  2
```

1. **Cyclic** means reading **with** the arrows: 1→2→3, 2→3→1, 3→1→2. These are $(1,2,3)$, $(2,3,1)$, $(3,1,2)$, and $\epsilon = +1$ for each.
2. **Acyclic** means reading **against** the arrows: $(1,3,2)$, $(3,2,1)$, $(2,1,3)$. $\epsilon = -1$ for each.
3. **Any repeat** gives 0: $\epsilon_{112} = \epsilon_{333} = \epsilon_{121} = 0$, and so on.

So only 6 of the 27 are non-zero: three $+1$s and three $-1$s. The other 21 are zero. Another way to say the same thing: **swapping any two indices flips the sign**. $\epsilon_{123} = +1$; swap the first two and $\epsilon_{213} = -1$.

### Why it exists: the cross product

The delta captured what the dot product does to basis vectors. Epsilon captures what the **cross product** does to them. With a right-handed basis:

$$\mathbf{e}_1\times\mathbf{e}_2 = \mathbf{e}_3, \qquad \mathbf{e}_2\times\mathbf{e}_3 = \mathbf{e}_1, \qquad \mathbf{e}_2\times\mathbf{e}_1 = -\mathbf{e}_3, \qquad \mathbf{e}_1\times\mathbf{e}_1 = \mathbf{0}$$

Cyclic order gives $+$, reversed gives $-$, a vector crossed with itself gives zero. That's exactly epsilon's rule, so all 9 facts collapse to one line:

$$\mathbf{e}_i\times\mathbf{e}_j = \epsilon_{ijk}\,\mathbf{e}_k$$

It also gives the determinant of a $3\times3$ matrix:

$$\det(\mathbf{A}) = \epsilon_{ijk}A_{1i}A_{2j}A_{3k}$$

### Products of alternating symbols

When two epsilons multiply, the result can always be written with deltas. The general rule is a determinant of deltas:

$$\epsilon_{ijk}\,\epsilon_{lmn} = \det\begin{bmatrix} \delta_{il} & \delta_{im} & \delta_{in} \\ \delta_{jl} & \delta_{jm} & \delta_{jn} \\ \delta_{kl} & \delta_{km} & \delta_{kn} \end{bmatrix}$$

You rarely need that full form. Sharing indices (contracting) gives the versions you actually use:

1. **One shared index** (the $\epsilon$-$\delta$ identity):
$$\epsilon_{ijk}\,\epsilon_{imn} = \delta_{jm}\delta_{kn} - \delta_{jn}\delta_{km}$$
A way to remember it: with the shared index first in both, pair "first with first, second with second", minus "first with second, second with first".
2. **Two shared indices:** $\epsilon_{ijk}\,\epsilon_{ijn} = 2\,\delta_{kn}$. (Set $m = j$ in the line above: $\delta_{jj}\delta_{kn} - \delta_{jn}\delta_{kj} = 3\delta_{kn} - \delta_{kn}$.)
3. **All three shared:** $\epsilon_{ijk}\,\epsilon_{ijk} = 6$. That's just counting: the 6 non-zero entries, each squared to 1.

**Check one by hand** to trust it. Put $j = 2, k = 3, m = 2, n = 3$ into the first identity. Left: $\epsilon_{i23}\epsilon_{i23}$, and only $i = 1$ survives, giving $1 \times 1 = 1$. Right: $\delta_{22}\delta_{33} - \delta_{23}\delta_{32} = 1 - 0 = 1$. ✓

Memorise the first one — it's how you prove $\nabla \times (\nabla \times \mathbf{v}) = \nabla(\nabla\cdot\mathbf{v}) - \nabla^2\mathbf{v}$, which appears in both elasticity and fluid dynamics.

## Three ways to multiply two vectors
<!-- bite: 2d111413-d805-4eec-bbae-705afd84bd77 -->

These three get mixed up constantly, so here they are side by side. Each one is worked out by writing both vectors as sums of components and letting the basis vectors do the work.

| Product | Symbol | Result | Component form | Also called |
| --- | --- | --- | --- | --- |
| Dot | $\mathbf{a}\cdot\mathbf{b}$ | scalar (a number) | $a_i b_i$ | scalar product, **inner product** |
| Cross | $\mathbf{a}\times\mathbf{b}$ | vector | $\epsilon_{ijk}a_j b_k$ (component $i$) | vector product |
| Dyad | $\mathbf{a}\otimes\mathbf{b}$ | second-order tensor | $a_i b_j$ | dyadic product, **outer product**, tensor product |

> **Keep the outputs straight:** the **dot** product gives a scalar and is the inner product; the **cross** product gives a vector. When the two are chained, order matters — see the [[#The scalar triple product|scalar triple product]] below.

### Dot product in component form

$$\mathbf{a}\cdot\mathbf{b} = (a_i\mathbf{e}_i)\cdot(b_j\mathbf{e}_j) = a_i b_j\,(\mathbf{e}_i\cdot\mathbf{e}_j) = a_i b_j\,\delta_{ij} = a_i b_i$$

Two different dummy letters ($i$ and $j$) are used on purpose, so no index appears more than twice. The delta then substitutes $j \to i$. Result: $a_1b_1 + a_2b_2 + a_3b_3$, a single number. Geometrically, $|\mathbf{a}||\mathbf{b}|\cos\theta$: how much the two vectors point the same way.

### Cross product in component form

$$\mathbf{a}\times\mathbf{b} = (a_j\mathbf{e}_j)\times(b_k\mathbf{e}_k) = a_j b_k\,(\mathbf{e}_j\times\mathbf{e}_k) = \epsilon_{jki}\,a_j b_k\,\mathbf{e}_i$$

So component $i$ is $(\mathbf{a}\times\mathbf{b})_i = \epsilon_{ijk}a_j b_k$ (using $\epsilon_{jki} = \epsilon_{ijk}$, since moving the last index to the front is a cyclic shift). Expand component 1 to see it is the formula you already know:

$$(\mathbf{a}\times\mathbf{b})_1 = \epsilon_{123}a_2b_3 + \epsilon_{132}a_3b_2 = a_2b_3 - a_3b_2$$

Every other term has a repeated index, so it's zero. The result is a vector at right angles to both $\mathbf{a}$ and $\mathbf{b}$. The cross product only exists in 3D.

### The scalar triple product

Chain the two products: **cross first, then dot**.

$$\mathbf{a}\cdot(\mathbf{b}\times\mathbf{c})$$

1. **Cross product first.** $\mathbf{b}\times\mathbf{c}$ gives a vector, with components $\epsilon_{ijk}b_jc_k$.
2. **Then the inner (dot) product.** Dotting $\mathbf{a}$ with that vector gives a **scalar**.

In index form the whole thing is one term:

$$\mathbf{a}\cdot(\mathbf{b}\times\mathbf{c}) = a_i\,\epsilon_{ijk}b_jc_k = \epsilon_{ijk}\,a_ib_jc_k$$

All three indices are repeated, so nothing is free and the result is a number. Geometrically, it's the **signed volume** of the box (parallelepiped) with edges $\mathbf{a}, \mathbf{b}, \mathbf{c}$: positive when the three form a right-handed set, negative when left-handed, and zero when they lie in one plane (that is, when they are linearly dependent). It equals the determinant of the matrix with those three vectors as rows.

**Why the order is forced.** $(\mathbf{a}\cdot\mathbf{b})\times\mathbf{c}$ is meaningless: $\mathbf{a}\cdot\mathbf{b}$ is a scalar, and you can't cross a scalar with a vector. So the cross product must happen first, and the brackets are often dropped: $\mathbf{a}\cdot\mathbf{b}\times\mathbf{c}$.

Because $\epsilon_{ijk}$ doesn't change under a cyclic shift, neither does the triple product: $\mathbf{a}\cdot(\mathbf{b}\times\mathbf{c}) = \mathbf{b}\cdot(\mathbf{c}\times\mathbf{a}) = \mathbf{c}\cdot(\mathbf{a}\times\mathbf{b})$. Swapping any two vectors flips the sign.

### The dyad (dyadic product, outer product)

The third product keeps **everything**. Nothing is summed:

$$\mathbf{a}\otimes\mathbf{b} = (a_i\mathbf{e}_i)\otimes(b_j\mathbf{e}_j) = a_i b_j\;\mathbf{e}_i\otimes\mathbf{e}_j$$

Two free indices means 9 components, so the result is a **second-order tensor**. It's often written $\mathbf{ab}$ with no symbol between, which is where the name **dyad** (a pair) comes from.

**What a dyad does.** A dyad is a machine that eats a vector and returns a vector:

$$(\mathbf{a}\otimes\mathbf{b})\cdot\mathbf{c} = \mathbf{a}\,(\mathbf{b}\cdot\mathbf{c})$$

It measures how much $\mathbf{c}$ lines up with $\mathbf{b}$ (a number), then returns $\mathbf{a}$ scaled by that number. Whatever you feed in, the output always points along $\mathbf{a}$.

**Order matters.** $\mathbf{a}\otimes\mathbf{b} \neq \mathbf{b}\otimes\mathbf{a}$. Swapping them swaps the indices, $a_ib_j$ versus $b_ia_j$, which gives the transpose.

## Dyads and matrices
<!-- bite: 37550888-1325-47e1-b04f-a06b6c84d348 -->

Write the 9 components of $\mathbf{a}\otimes\mathbf{b}$ in a grid. Row $i$, column $j$ holds $a_ib_j$:

$$[\mathbf{a}\otimes\mathbf{b}] = \begin{bmatrix} a_1 \\ a_2 \\ a_3 \end{bmatrix}\begin{bmatrix} b_1 & b_2 & b_3 \end{bmatrix} = \begin{bmatrix} a_1b_1 & a_1b_2 & a_1b_3 \\ a_2b_1 & a_2b_2 & a_2b_3 \\ a_3b_1 & a_3b_2 & a_3b_3 \end{bmatrix}$$

A column times a row. Compare the dot product, which is a row times a column, $[\mathbf{a}]^\mathsf{T}[\mathbf{b}]$, and gives a single number. **Inner product: row × column → 1×1. Outer product: column × row → 3×3.**

**Every second-order tensor is a sum of dyads.** The 9 basis dyads $\mathbf{e}_i\otimes\mathbf{e}_j$ act as a basis for second-order tensors, just as $\mathbf{e}_i$ are a basis for vectors:

$$\mathbf{T} = T_{ij}\;\mathbf{e}_i\otimes\mathbf{e}_j$$

Same idea as $\mathbf{f} = a_i\mathbf{e}_i$, one level up. A single dyad is a very special tensor (every row is a multiple of $\mathbf{b}$, so its matrix has rank 1), but adding dyads together builds any tensor at all, the stress tensor included.

### Trace of a dyad

The **trace** is the sum of the diagonal entries, $\operatorname{tr}\mathbf{T} = T_{ii}$. For a dyad, the diagonal is $a_1b_1, a_2b_2, a_3b_3$, so:

$$\operatorname{tr}(\mathbf{a}\otimes\mathbf{b}) = a_ib_i = \mathbf{a}\cdot\mathbf{b}$$

**The trace of the outer product is the inner product.** That's the link between the two: setting the two free indices of $a_ib_j$ equal (a contraction) sums them away and leaves a scalar. The trace doesn't change when you rotate the axes, which is why the pressure, $p = -\tfrac{1}{3}\sigma_{kk}$, comes out the same in any coordinate system.

## Changing basis: coordinate transformations
<!-- bite: b510d381-7978-4cb9-a308-66abb217355f -->

Stay in Euclidean space (ordinary flat 3D) and use two orthonormal bases: the old one $\mathbf{e}_j$ and a rotated one $\mathbf{e}'_i$. One arrow $\mathbf{v}$ can be written in either:

$$\mathbf{v} = v_j\,\mathbf{e}_j = v'_i\,\mathbf{e}'_i$$

To get the new components, dot both sides with $\mathbf{e}'_i$:

$$v'_i = (\mathbf{e}'_i\cdot\mathbf{e}_j)\,v_j = Q_{ij}\,v_j, \qquad Q_{ij} = \mathbf{e}'_i\cdot\mathbf{e}_j$$

Each $Q_{ij}$ is the cosine of the angle between new axis $i$ and old axis $j$. $\mathbf{Q}$ is orthogonal, $Q_{ik}Q_{jk} = \delta_{ij}$, which in matrix form says $\mathbf{Q}\mathbf{Q}^\mathsf{T} = \mathbf{I}$: rotations keep lengths and angles.

**2D example.** Rotate the axes by $\theta$:

$$\mathbf{Q} = \begin{bmatrix} \cos\theta & \sin\theta \\ -\sin\theta & \cos\theta \end{bmatrix}$$

The vector with old components $(1, 0)$ gets new components $(\cos\theta, -\sin\theta)$. **The arrow didn't move. Only the numbers describing it changed.**

**Dyads tell you how tensors transform.** Each vector in a dyad picks up its own $Q$:

$$a'_ib'_j = (Q_{ik}a_k)(Q_{jl}b_l) = Q_{ik}Q_{jl}\,(a_kb_l)$$

Since every second-order tensor is a sum of dyads, every one transforms the same way: $T'_{ij} = Q_{ik}Q_{jl}T_{kl}$, or $[\mathbf{T}'] = [\mathbf{Q}][\mathbf{T}][\mathbf{Q}]^\mathsf{T}$. That's where the "one $Q$ per index" rule in the next section comes from.

## Vectors are not matrices
<!-- bite: 07715ba4-bf55-4613-94b4-94ede1eacf11 -->

**Matrices are algebraic constructs. Vectors and tensors are geometric constructs.** They are related, but they are not the same thing.

1. A **vector** is an arrow. It exists without any axes.
2. A **column of three numbers** is that arrow's components **in one particular basis**.
3. Change the basis and the column changes, while the arrow stays put (the 2D example above).

So when someone calls a matrix "a vector" or "a tensor", they are quietly assuming a basis. If that assumption is wrong, everything goes haywire.

**A concrete way it goes wrong.** Let $\mathbf{v}$ have components $(1, 0)$ in the standard basis. Let $\mathbf{w}$ have components $(1, 0)$ in a basis rotated by 90°, whose first axis points along the old $y$. Add the columns and you get $(2, 0)$, an arrow along $x$ of length 2. But $\mathbf{w}$ actually points along $y$, so the true sum is $(1, 1)$ in the standard basis. The matrix arithmetic was flawless; the answer is wrong, because the two columns were in different bases.

**The rule:** you may only add, multiply or compare component arrays when they are written in the **same** basis. Index notation makes this safe by keeping the basis implied and fixed throughout an equation.

## What a tensor actually is
<!-- bite: 48d2a727-8bdc-48d5-87a9-efc2f5de85b6 -->

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

This is also the deep reason [[machine-learning/00-foundations/03-mathematics/01-linear-algebra/02-matrices|"tensor" in machine learning]] means something looser: a PyTorch tensor is an n-dimensional array with no transformation law attached. Same word, different concept, and it's worth keeping straight.

## Operations
<!-- bite: 0018715b-1789-44ef-a316-e88931f27c4f -->

```text
aᵢbᵢ                    inner product          → scalar
aᵢbⱼ                    outer product          → order 2
σᵢⱼnⱼ                   contraction            → vector
σᵢⱼεᵢⱼ                  double contraction     → scalar
σᵢᵢ                     trace                  → scalar (invariant)
```

**Contraction lowers the order by two**, once per summed pair. That's why $C_{ijkl}\varepsilon_{kl}$ (order 4 contracted with order 2 over two indices) gives order 2.

**Symmetric and antisymmetric parts.** Any second-order tensor splits uniquely:

$$A_{ij} = \underbrace{\tfrac{1}{2}(A_{ij} + A_{ji})}_{\text{symmetric}} + \underbrace{\tfrac{1}{2}(A_{ij} - A_{ji})}_{\text{antisymmetric}}$$

This split is physically meaningful and appears repeatedly: the velocity gradient splits into **rate of deformation** (symmetric — actual stretching) and **spin** (antisymmetric — rigid rotation). Only the symmetric part causes stress in a fluid. → [[continuum-mechanics/03-kinematics-of-deformation|Kinematics]]

A symmetric 3×3 tensor has **6 independent components**, an antisymmetric one has 3 (which is why it can be represented as a vector — the axial vector).

**The volumetric/deviatoric split** is the other decomposition that matters:

$$\sigma_{ij} = \underbrace{\tfrac{1}{3}\sigma_{kk}\,\delta_{ij}}_{\text{hydrostatic}} + \underbrace{s_{ij}}_{\text{deviatoric}}$$

Pressure changes volume; the deviator changes shape. **Metals yield on the deviatoric part alone** — hydrostatic pressure doesn't cause plastic flow, which is why deep-sea pressure crushes a hollow sphere but doesn't yield a solid one. → [[continuum-mechanics/12-failure-and-yield|Failure and Yield]]

## Eigenvalues, principal values, invariants
<!-- bite: 332e96aa-5462-4df4-a3e7-f02fe8364de5 -->

For a symmetric tensor, the eigenvalue problem

$$\sigma_{ij}n_j = \lambda\, n_i$$

has three real eigenvalues and mutually orthogonal eigenvectors.

**Physically:** there exists an orientation in which the stress tensor is diagonal — **no shear**, only normal stresses. Those are the **principal stresses** $\sigma_1 \geq \sigma_2 \geq \sigma_3$ and the eigenvectors are the principal directions.

That's why a brittle material fails on a plane perpendicular to the maximum principal stress, and it's the basis of most failure criteria.

The characteristic equation gives three **invariants** — quantities unchanged by rotation:

$$I_1 = \sigma_{kk} \qquad I_2 = \tfrac{1}{2}(\sigma_{ii}\sigma_{jj} - \sigma_{ij}\sigma_{ij}) \qquad I_3 = \det(\boldsymbol\sigma)$$

**Invariants are how you write a physical law that doesn't depend on orientation.** An isotropic material's response can only depend on invariants — that's not a convenience, it's forced by the symmetry. → [[continuum-mechanics/07-constitutive-models|Constitutive Models]]

The von Mises stress is built from the second deviatoric invariant, which is why it's a single number you can compare against a yield stress regardless of how the load is oriented.

## Tensor calculus
<!-- bite: b14d7f57-505f-4dc4-b70e-cef2bc1a65c8 -->

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

Every balance law in this field is derived by writing it as a surface plus volume integral, applying this, and arguing that since the volume is arbitrary the integrand must vanish. **That derivation pattern appears four times in note 06** — learn it once. → [[continuum-mechanics/06-conservation-laws|Conservation Laws]]

## Practical advice
<!-- bite: 212c8e6f-0b94-4e07-b582-3695e8d28a62 -->

1. **Check free indices on both sides.** It's free error detection
2. **$\delta_{ii} = 3$, not 1**
3. **Never let an index appear three times.** Rename the dummy
4. **Learn the $\epsilon$-$\delta$ identity** — it resolves most curl manipulations
5. **Symmetric ⟹ 6 components, real eigenvalues, orthogonal eigenvectors.** Almost every tensor here is symmetric
6. **When a law must be orientation-independent, write it in invariants**
7. **Cartesian only, for now.** These notes assume rectangular coordinates, where covariant and contravariant components coincide and you can ignore the distinction. Curvilinear coordinates (cylindrical, spherical) reintroduce it along with Christoffel symbols — necessary for shells and for general relativity, and out of scope here

## Words used in this note
<!-- bite: c6246248-6d2e-44df-ae45-f16773c75e24 -->

1. A **vector** is a quantity with a length and a direction, like an arrow, which exists independently of any axes.
2. A **component** is one of the numbers that says how far a vector goes along one basis direction.
3. A **basis** is a set of linearly independent vectors, as many as the dimension of the space, that every other vector can be built from.
4. An **orthonormal** basis is one whose vectors are at right angles to each other and each have length 1.
5. Vectors are **linearly independent** when none of them can be built by stretching and adding the others.
6. The **dimension** of a space is the largest number of linearly independent vectors it can hold.
7. **Parsimony** means saying the same thing with fewer symbols, which is what indexed names like $a_i$ and $\mathbf{e}_i$ achieve.
8. A **term** is one piece of an expression separated from the rest by a plus, minus or equals sign.
9. A **dummy index** is an index repeated within one term; it is summed over, and its letter can be renamed freely.
10. A **free index** is an index that appears once in a term; it ranges over 1, 2, 3 and must appear in every term of the equation.
11. The **Kronecker delta** $\delta_{ij}$ is 1 when its two indices are equal and 0 otherwise; it is the identity matrix in index form.
12. The **Levi-Civita symbol** $\epsilon_{ijk}$ is $+1$ for a cyclic arrangement of 1, 2, 3, $-1$ for an acyclic one, and 0 when an index repeats.
13. The **dot product** (inner product) multiplies two vectors to give a scalar.
14. The **cross product** (vector product) multiplies two 3D vectors to give a vector at right angles to both.
15. A **dyad** (outer product, tensor product) multiplies two vectors to give a second-order tensor, without summing anything.
16. A **tensor** is a geometric object whose components change by a fixed rule, one $Q$ per index, when the basis is rotated.
17. The **trace** of a second-order tensor is the sum of its diagonal components, and it does not change under rotation.
18. A **contraction** sets two indices equal and sums over them, which lowers the order of a tensor by two.

## Check yourself
<!-- bite: 7785fef3-fde4-46e0-b98f-28d5f8157a22 -->

Try these on paper before looking anything up.

1. Are $(1, 1, 0)$, $(0, 1, 1)$ and $(1, 2, 1)$ linearly independent? What does your answer say about the space they span?
2. In $c_i = A_{ji}b_j$, which index is free and which is dummy? Write out $c_2$ in full. Is this $\mathbf{A}\mathbf{b}$ or $\mathbf{A}^\mathsf{T}\mathbf{b}$?
3. What's wrong with $a_ib_ic_i$, and with $y_{ij} = a_{ij}x_j$?
4. Evaluate $\delta_{ij}\delta_{ij}$ and $\epsilon_{312}$, $\epsilon_{321}$, $\epsilon_{311}$.
5. Use the $\epsilon$-$\delta$ identity to show $\mathbf{a}\times(\mathbf{b}\times\mathbf{c}) = \mathbf{b}(\mathbf{a}\cdot\mathbf{c}) - \mathbf{c}(\mathbf{a}\cdot\mathbf{b})$.
6. For $\mathbf{a} = (1, 2, 0)$ and $\mathbf{b} = (3, 0, 1)$, write the matrix of $\mathbf{a}\otimes\mathbf{b}$ and check its trace equals $\mathbf{a}\cdot\mathbf{b}$.
7. Explain in two sentences why a column of numbers is not, by itself, a vector.

---

## Related
<!-- bite: 4bdff31d-dc0b-4dcd-b240-6b14d29a02ba -->
- [[continuum-mechanics/03-kinematics-of-deformation|Kinematics of Deformation]] — the first real use
- [[continuum-mechanics/05-stress|Stress]] — the tensor that motivates all of this
- [[machine-learning/00-foundations/03-mathematics/01-linear-algebra/index|Linear Algebra]] — eigenvalues, at the level ML needs
- [[continuum-mechanics/index|Continuum mechanics map]]

## About this lesson
<!-- bite: 6adce663-20fd-4eb3-be8f-f0fb65bd5c9b -->

**Level:** Intermediate → Advanced. **Covers:** The language the whole field is written in. An afternoon spent here saves weeks of confusion later.
