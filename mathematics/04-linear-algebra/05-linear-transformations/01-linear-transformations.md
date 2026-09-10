# Linear Transformations

**[Advanced]** — a matrix is a function, its columns are where the basis vectors land, and that single fact makes the multiplication rule inevitable.

## Before you start

- You can multiply matrices and compute determinants — [[01-matrices-and-determinants|matrices and determinants]].
- You know bases, column space and null space — [[04-vector-spaces/01-vector-spaces|vector spaces]].
- Helpful: rotation and the addition formulas — [[02-graphs-and-identities|graphs and identities]]. Section 5 recovers them.

**What you will be able to do after this lesson:**

1. Test whether a map is **linear**, and give concrete examples of familiar maps that are not.
2. Build the matrix of a linear map by asking **where the basis vectors go**, and explain why that determines everything.
3. Show that **composition of maps is multiplication of matrices**, and hence why the row-times-column rule is what it is.
4. Identify kernel and image with null space and column space, and read a determinant as an area factor.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 4 derives a trigonometric identity from matrix algebra.

---

## 1. Why this exists

[[01-matrices-and-determinants|Lesson 1]] asserted that matrix multiplication is defined the way it is because it represents composing functions, and postponed the argument. This is the argument.

The shift in view is the point. Stop reading

$$
A\mathbf{x} = \mathbf{b}
$$

as "a grid of coefficients times a column of unknowns" and start reading it as "the function $A$, applied to the input $\mathbf{x}$, gives the output $\mathbf{b}$". Then:

- The **column space** is the set of achievable outputs — the *image*.
- The **null space** is the set of inputs crushed to zero — the *kernel*.
- Solving $A\mathbf{x} = \mathbf{b}$ is asking whether $\mathbf{b}$ is in the image, and if so what maps to it.
- $\det A$ is the factor by which the function scales area.

None of these are new facts. They are the same facts, in the language that explains them.

## 2. The definition

A map $T$ is **linear** when it respects the two vector-space operations:

$$
T(\mathbf{u} + \mathbf{v}) = T(\mathbf{u}) + T(\mathbf{v}), \qquad T(k\mathbf{v}) = k\,T(\mathbf{v})
$$

Equivalently, in one condition: $T(a\mathbf{u} + b\mathbf{v}) = aT(\mathbf{u}) + bT(\mathbf{v})$. In words: **it does not matter whether you combine first and then transform, or transform first and then combine.**

Setting $k = 0$ gives $T(\mathbf{0}) = \mathbf{0}$ — a linear map always fixes the origin. That is the quickest disqualifier, exactly as it was for subspaces.

| Term | Plain-English definition |
| :--- | :--- |
| **Linear map** | A function respecting addition and scaling |
| **Kernel** | Everything sent to $\mathbf{0}$ — the null space of its matrix |
| **Image** | Everything that is hit — the column space of its matrix |
| **Standard basis** | $\mathbf{e}_1 = (1,0,\dots)$, $\mathbf{e}_2 = (0,1,\dots)$, and so on |
| **Affine map** | A linear map followed by a translation | 

### What is *not* linear

- **Translation**, $T(\mathbf{v}) = \mathbf{v} + \mathbf{c}$ for fixed $\mathbf{c} \neq \mathbf{0}$. It moves the origin, so it fails immediately. This is why graphics uses **homogeneous coordinates**: adding a fourth coordinate lets translation be expressed as a $4\times4$ matrix multiplication, and the whole pipeline stays multiplicative.
- **Squaring**, $T(x) = x^2$. $T(2x) = 4x^2 \neq 2T(x)$.
- $T(x) = x + 1$, despite being called a "linear function" in school. Its graph is a straight line; it is not a linear *map*. The two uses of the word are genuinely different, and this one is affine.

## 3. The columns are the images of the basis vectors

This is the theorem that makes everything computable.

Write any vector in the standard basis:

$$
\mathbf{x} = x_1\mathbf{e}_1 + x_2\mathbf{e}_2 + \cdots + x_n\mathbf{e}_n
$$

Apply $T$ and use linearity:

$$
T(\mathbf{x}) = x_1T(\mathbf{e}_1) + x_2T(\mathbf{e}_2) + \cdots + x_nT(\mathbf{e}_n)
$$

So $T$ is **completely determined by the $n$ vectors $T(\mathbf{e}_i)$**. Knowing where the basis goes tells you where everything goes.

And that expression is exactly matrix-times-vector, if you build the matrix whose **columns are the $T(\mathbf{e}_i)$**:

$$
A = \Big[\, T(\mathbf{e}_1) \;\Big|\; T(\mathbf{e}_2) \;\Big|\; \cdots \;\Big|\; T(\mathbf{e}_n) \,\Big]
$$

So: **every linear map from $\mathbb{R}^n$ to $\mathbb{R}^m$ is a matrix, and every matrix is a linear map.** They are the same thing seen twice.

To find the matrix of any transformation, ask only: *where does $(1,0)$ go, and where does $(0,1)$ go?* Those two answers are the columns.

| Transformation | $T(\mathbf{e}_1)$ | $T(\mathbf{e}_2)$ | Matrix |
| :--- | :--- | :--- | :--- |
| Rotate by $\theta$ | $(\cos\theta, \sin\theta)$ | $(-\sin\theta, \cos\theta)$ | $\begin{pmatrix}\cos\theta & -\sin\theta\\ \sin\theta & \cos\theta\end{pmatrix}$ |
| Scale by $k$ | $(k, 0)$ | $(0, k)$ | $kI$ |
| Reflect in the $x$-axis | $(1, 0)$ | $(0, -1)$ | $\begin{pmatrix}1&0\\0&-1\end{pmatrix}$ |
| Shear by $s$ | $(1, 0)$ | $(s, 1)$ | $\begin{pmatrix}1&s\\0&1\end{pmatrix}$ |
| Project onto the $x$-axis | $(1, 0)$ | $(0, 0)$ | $\begin{pmatrix}1&0\\0&0\end{pmatrix}$ |

## 4. Composition is multiplication

Apply $B$, then $A$. What single matrix does that?

$$
(A \circ B)(\mathbf{x}) = A(B\mathbf{x})
$$

By section 3, the matrix of the composite has as its $j$th column the image of $\mathbf{e}_j$ — which is $A(B\mathbf{e}_j)$. And $B\mathbf{e}_j$ is just the $j$th column of $B$. So the $j$th column of the composite is $A$ applied to the $j$th column of $B$, whose $i$th entry is:

$$
\sum_k a_{ik}\,b_{kj}
$$

**That is the definition of matrix multiplication**, arrived at rather than assumed. Both of lesson 1's loose ends close at once:

- **Not commutative**, because "rotate then reflect" is not "reflect then rotate" — function composition does not commute.
- **Associative**, because $(f\circ g)\circ h = f\circ(g\circ h)$ for any functions at all.

> [!TIP]
> **Predict before section 5.** The matrix for rotating by $\theta$ is in the table above. Multiply the matrix for rotating by $\alpha$ by the matrix for rotating by $\beta$. Geometrically the result must be rotation by $\alpha + \beta$. What identity does that force on the entries — and where have you seen it before? Decide before opening the answers.

## 5. Kernel, image, and the determinant

For the map with matrix $A$:

- $\ker T = N(A)$, the null space. $T$ is **one-to-one** exactly when the kernel is $\{\mathbf{0}\}$ — nothing but zero is crushed.
- $\operatorname{im} T = C(A)$, the column space. $T$ is **onto** exactly when the image is everything.
- Rank–nullity now reads: $\dim(\text{image}) + \dim(\text{kernel}) = \dim(\text{domain})$. Whatever dimension the map loses to the kernel, it loses from the image.

And $\det A$ is the area (or volume) scale factor, from [[01-matrices-and-determinants|lesson 1]]. A zero determinant means the map collapses space onto something lower-dimensional — a non-trivial kernel — which is the same statement as "not invertible", now with a reason attached.

A projection makes all of this visible at once: projecting the plane onto the $x$-axis has kernel the $y$-axis (1-dimensional), image the $x$-axis (1-dimensional), $1 + 1 = 2$, and determinant $0$ because all area is destroyed.

## Worked example — runnable

**Runnable example:** save as `transformations.py` in any empty directory and run `python3 transformations.py`. Standard library only; writes no files.

```python
"""Linear maps: the linearity test, columns as images, and composition."""
import math

EPS = 1e-9


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))]
            for i in range(len(A))]


def apply(A, v):
    return tuple(sum(A[i][k] * v[k] for k in range(len(v))) for i in range(len(A)))


def det2(A):
    return A[0][0] * A[1][1] - A[0][1] * A[1][0]


def is_linear(T, samples, scalars=(0.0, 2.0, -3.5)):
    """Check T(au + bv) = aT(u) + bT(v) on a fixed set of probes."""
    for u in samples:
        for v in samples:
            for a in scalars:
                for b in scalars:
                    combined = tuple(a * x + b * y for x, y in zip(u, v))
                    lhs = T(combined)
                    rhs = tuple(a * x + b * y for x, y in zip(T(u), T(v)))
                    if any(abs(p - q) > 1e-9 for p, q in zip(lhs, rhs)):
                        return False, (u, v, a, b, lhs, rhs)
    return True, None


def matrix_of(T, n):
    """Section 3: the columns are the images of the standard basis vectors."""
    cols = []
    for j in range(n):
        e = tuple(1.0 if i == j else 0.0 for i in range(n))
        cols.append(T(e))
    return [[cols[j][i] for j in range(n)] for i in range(len(cols[0]))]


def rotation(theta_deg):
    t = math.radians(theta_deg)
    return [[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]]


if __name__ == "__main__":
    PROBES = [(1.0, 0.0), (0.0, 1.0), (2.0, -3.0), (-1.5, 4.0), (0.0, 0.0)]

    print("Block 1 - which of these maps are linear?")
    maps = [
        ("rotate 30 degrees",   lambda v: apply(rotation(30), v)),
        ("scale by 3",          lambda v: (3 * v[0], 3 * v[1])),
        ("project onto x-axis", lambda v: (v[0], 0.0)),
        ("shear",               lambda v: (v[0] + 2 * v[1], v[1])),
        ("translate by (1,1)",  lambda v: (v[0] + 1, v[1] + 1)),
        ("square each entry",   lambda v: (v[0] ** 2, v[1] ** 2)),
        ("swap and negate",     lambda v: (-v[1], v[0])),
    ]
    for label, T in maps:
        ok, why = is_linear(T, PROBES)
        origin_fixed = all(abs(c) < EPS for c in T((0.0, 0.0)))
        note = "" if ok else ("  (moves the origin)" if not origin_fixed else "  (fails scaling)")
        print(f"  {label:22} {'linear' if ok else 'NOT linear':12}{note}")
    assert is_linear(maps[0][1], PROBES)[0]
    assert not is_linear(maps[4][1], PROBES)[0]     # translation
    assert not is_linear(maps[5][1], PROBES)[0]     # squaring

    print()
    print("Block 2 - the matrix is read off from where the basis vectors go")
    for label, T in maps:
        ok, _ = is_linear(T, PROBES)
        if not ok:
            continue
        M = matrix_of(T, 2)
        e1, e2 = T((1.0, 0.0)), T((0.0, 1.0))
        print(f"  {label:22} T(e1)={tuple(round(x,4) for x in e1)}"
              f"  T(e2)={tuple(round(x,4) for x in e2)}  det={det2(M):7.4f}")
        # the matrix built from the basis images must reproduce T everywhere
        for v in PROBES + [(7.0, -2.0), (0.5, 0.25)]:
            assert all(abs(p - q) < 1e-9 for p, q in zip(apply(M, v), T(v))), label
    print("  each matrix reproduces its map on every probe vector tested")

    print()
    print("Block 3 - composition of maps IS multiplication of matrices")
    A = rotation(30)
    B = [[2.0, 0.0], [0.0, 0.5]]                 # stretch x, squash y
    composite = matmul(A, B)                      # apply B first, then A
    for v in [(1.0, 0.0), (0.0, 1.0), (3.0, -2.0), (1.5, 1.5)]:
        step_by_step = apply(A, apply(B, v))
        one_matrix = apply(composite, v)
        assert all(abs(p - q) < 1e-9 for p, q in zip(step_by_step, one_matrix))
    print("  A(Bx) == (AB)x for every vector tried")
    print(f"  and order matters: AB = {[[round(x,4) for x in r] for r in composite]}")
    print(f"                     BA = {[[round(x,4) for x in r] for r in matmul(B, A)]}")
    assert matmul(A, B) != matmul(B, A)
    print("  'stretch then rotate' is not 'rotate then stretch'")

    print()
    print("Block 4 - composing rotations recovers the angle addition formulas")
    for a, b in [(30, 45), (17, 128), (200, -95)]:
        product = matmul(rotation(a), rotation(b))
        direct = rotation(a + b)
        for i in range(2):
            for j in range(2):
                assert abs(product[i][j] - direct[i][j]) < 1e-9
        ra, rb = math.radians(a), math.radians(b)
        print(f"  R({a}) R({b}) == R({a + b}):  entry [0][0] is "
              f"{product[0][0]:9.6f} = cos{a}cos{b} - sin{a}sin{b} = "
              f"{math.cos(ra)*math.cos(rb) - math.sin(ra)*math.sin(rb):9.6f}")
    print("  the [0][0] entry says cos(a+b) = cos a cos b - sin a sin b,")
    print("  and the [1][0] entry says sin(a+b) = sin a cos b + cos a sin b -")
    print("  the addition formulas, falling out of the requirement that")
    print("  rotating by a then by b is rotating by a+b")

    print()
    print("Block 5 - kernel, image and the determinant of a projection")
    P = [[1.0, 0.0], [0.0, 0.0]]                  # project onto the x-axis
    print(f"  projection matrix {P}, det = {det2(P)}")
    print(f"    (0,1) -> {apply(P, (0.0, 1.0))}   the whole y-axis is the kernel")
    print(f"    (3,7) -> {apply(P, (3.0, 7.0))}   the image is the x-axis")
    assert apply(P, (0.0, 5.0)) == (0.0, 0.0)
    assert abs(det2(P)) < EPS
    print("  dim(image) 1 + dim(kernel) 1 = 2 = dim(domain), and det = 0:")
    print("  all area is destroyed, so the map cannot be undone")

    print()
    print("  a rotation loses nothing: det = 1, kernel is just the origin")
    R = rotation(37)
    print(f"    det(R) = {det2(R):.9f}")
    assert abs(det2(R) - 1) < EPS
    print(f"  and a reflection flips orientation: det = {det2([[1,0],[0,-1]])}")

    print()
    print("transformations: passed")
```

Expected output:

```
Block 1 - which of these maps are linear?
  rotate 30 degrees      linear      
  scale by 3             linear      
  project onto x-axis    linear      
  shear                  linear      
  translate by (1,1)     NOT linear    (moves the origin)
  square each entry      NOT linear    (fails scaling)
  swap and negate        linear      

Block 2 - the matrix is read off from where the basis vectors go
  rotate 30 degrees      T(e1)=(0.866, 0.5)  T(e2)=(-0.5, 0.866)  det= 1.0000
  scale by 3             T(e1)=(3.0, 0.0)  T(e2)=(0.0, 3.0)  det= 9.0000
  project onto x-axis    T(e1)=(1.0, 0.0)  T(e2)=(0.0, 0.0)  det= 0.0000
  shear                  T(e1)=(1.0, 0.0)  T(e2)=(2.0, 1.0)  det= 1.0000
  swap and negate        T(e1)=(-0.0, 1.0)  T(e2)=(-1.0, 0.0)  det= 1.0000
  each matrix reproduces its map on every probe vector tested

Block 3 - composition of maps IS multiplication of matrices
  A(Bx) == (AB)x for every vector tried
  and order matters: AB = [[1.7321, -0.25], [1.0, 0.433]]
                     BA = [[1.7321, -1.0], [0.25, 0.433]]
  'stretch then rotate' is not 'rotate then stretch'

Block 4 - composing rotations recovers the angle addition formulas
  R(30) R(45) == R(75):  entry [0][0] is  0.258819 = cos30cos45 - sin30sin45 =  0.258819
  R(17) R(128) == R(145):  entry [0][0] is -0.819152 = cos17cos128 - sin17sin128 = -0.819152
  R(200) R(-95) == R(105):  entry [0][0] is -0.258819 = cos200cos-95 - sin200sin-95 = -0.258819
  the [0][0] entry says cos(a+b) = cos a cos b - sin a sin b,
  and the [1][0] entry says sin(a+b) = sin a cos b + cos a sin b -
  the addition formulas, falling out of the requirement that
  rotating by a then by b is rotating by a+b

Block 5 - kernel, image and the determinant of a projection
  projection matrix [[1.0, 0.0], [0.0, 0.0]], det = 0.0
    (0,1) -> (0.0, 0.0)   the whole y-axis is the kernel
    (3,7) -> (3.0, 0.0)   the image is the x-axis
  dim(image) 1 + dim(kernel) 1 = 2 = dim(domain), and det = 0:
  all area is destroyed, so the map cannot be undone

  a rotation loses nothing: det = 1, kernel is just the origin
    det(R) = 1.000000000
  and a reflection flips orientation: det = -1

transformations: passed
```

Block 4 is the lesson's best moment. The trigonometric addition formulas — derived in [[02-graphs-and-identities|graphs and identities]] by computing one distance two ways — reappear as nothing more than the statement that rotating by $\alpha$ and then by $\beta$ is rotating by $\alpha+\beta$. Two independent derivations, one identity.

## Common pitfalls and traps

- **Calling $y = mx + c$ a linear map.** With $c \neq 0$ it is affine: it moves the origin. School usage and linear-algebra usage genuinely differ here.
- **Forgetting that composition applies right to left.** $AB$ means "do $B$ first". Reversed, you get a different transformation.
- **Building the matrix with the basis images as rows.** They are the **columns**. Doing it wrong gives the transpose, which is a different map (though the same one for symmetric matrices, which hides the bug).
- **Assuming a matrix determines a map independently of basis.** The matrix depends on the basis chosen. The *map* does not. Two different-looking matrices can be the same transformation in different coordinates — which is exactly what diagonalisation exploits in [[06-eigenvalues/01-eigenvalues-and-eigenvectors|eigenvalues]].
- **Reading a zero determinant as merely "not invertible".** It says something stronger and more useful: the map collapses dimensions, so a whole subspace maps to zero and information is irrecoverably lost.
- **Testing linearity on too few probes.** The map $T(x,y) = (x, 0)$ and the map $T(x,y) = (x, y - y)$ agree everywhere, but a map like $T(x,y)=(x,\,y\cdot\lfloor y\rfloor)$ passes at integer probes and fails elsewhere. Probes give evidence, not proof.

## Check your understanding

1. Is $T(x, y) = (2x - y,\; x + 3y)$ linear? Give its matrix.
2. Is $T(x, y) = (x + 1,\; y)$ linear? Why?
3. Write the matrix that reflects the plane in the line $y = x$. What is its determinant, and why that sign?
4. If $T$ has matrix $A$ and $S$ has matrix $B$, what is the matrix of "apply $T$, then $S$"?
5. A linear map $\mathbb{R}^3 \to \mathbb{R}^3$ has a 2-dimensional image. What is the dimension of its kernel, and what is its determinant?

<details><summary>Answers — open only after an attempt</summary>

1. **Yes.** $T(1,0) = (2,1)$ and $T(0,1) = (-1,3)$, so the matrix is $\begin{pmatrix}2&-1\\1&3\end{pmatrix}$.
2. **No.** $T(0,0) = (1,0) \neq (0,0)$, and a linear map must fix the origin. It is affine — a translation.
3. Reflection in $y=x$ swaps the coordinates: $(1,0)\mapsto(0,1)$ and $(0,1)\mapsto(1,0)$, giving $\begin{pmatrix}0&1\\1&0\end{pmatrix}$. Its determinant is $-1$: negative because a reflection **reverses orientation**, and magnitude $1$ because it preserves area.
4. $BA$ — not $AB$. The rightmost matrix acts first, so "apply $A$, then $B$" is $BA$.
5. By rank–nullity, $2 + \text{nullity} = 3$, so the kernel is 1-dimensional. Since the kernel is non-trivial the map is not invertible, so its determinant is $0$ — consistent with squashing $\mathbb{R}^3$ into a plane, which destroys all volume.

**And the prediction from section 4:** multiplying the two rotation matrices gives, in the top-left entry, $\cos\alpha\cos\beta - \sin\alpha\sin\beta$; and since the product must equal $R(\alpha+\beta)$ whose top-left entry is $\cos(\alpha+\beta)$, the two must be equal. That is exactly the **cosine addition formula**, and the bottom-left entry gives the sine one. You met both in [[02-graphs-and-identities|graphs and identities]], derived there by computing a distance two ways.
</details>

## Practice — independent task

Implement a small 2-D graphics pipeline using **homogeneous coordinates**, so that translation becomes a matrix.

1. Represent a point $(x, y)$ as the 3-vector $(x, y, 1)$. Write $3\times3$ matrices for translation, rotation about the origin, scaling and reflection. Verify each acts correctly on several points.
2. Confirm the translation matrix is **linear on the 3-vectors** even though translation is not linear on the 2-vectors. Explain in a comment where the extra dimension "hides" the constant.
3. Build **rotation about an arbitrary point** $p$ as the composite: translate $p$ to the origin, rotate, translate back. Assert that $p$ itself is a fixed point, and that a point at distance $d$ from $p$ stays at distance $d$.
4. Verify order matters: show that translate-then-rotate and rotate-then-translate give different results for the same inputs, and describe the difference geometrically.
5. Check that the top-left $2\times2$ block's determinant predicts the area scaling of a polygon under your transforms — reuse the shoelace formula from [[01-plane-shapes|plane shapes]].

**Edge cases:** rotation by $0$ and by $360°$ (must be the identity to within tolerance); scaling by $0$ (singular — what happens to your polygon's area?); a reflection composed with itself.

**Done when:** step 3's fixed point holds to `1e-9` for at least five centres, step 5's predicted and measured areas agree, and you can explain why graphics hardware uses $4\times4$ matrices for 3-D rather than $3\times3$.

## Tradeoffs, limits and extensions

**Changing basis changes the matrix, not the map.** If $P$ has a new basis as its columns, the same transformation is $P^{-1}AP$ in the new coordinates. Choosing a basis in which the matrix is as simple as possible — ideally diagonal — is exactly what [[06-eigenvalues/01-eigenvalues-and-eigenvectors|eigenvalues]] is for, and it is why eigenvectors matter: they are the directions in which the map is just a stretch.

**Linearity is a strong restriction, and that is the point.** Most functions are not linear. The reason linear algebra is so useful is not that the world is linear, but that non-linear things are **locally** linear — the derivative of a multivariable function is precisely the linear map best approximating it near a point. That is developed in [[01-partial-derivatives|partial derivatives]], and it is why linear algebra underpins optimisation and machine learning.

**Probing is not proving.** The lab's `is_linear` checks a finite set of vectors and scalars. That is strong evidence and not a proof; a map could agree on every probe and differ elsewhere. To prove linearity you argue algebraically, as section 3 does.

## Before moving on

You are done with this lesson when you can:

- Test linearity, and explain why translation fails it.
- Build a transformation's matrix by asking where the basis vectors land.
- Derive matrix multiplication from function composition.
- Read kernel, image and determinant off a map and connect them by rank–nullity.

**Recap for later lookup:** linear means $T(a\mathbf{u}+b\mathbf{v}) = aT(\mathbf{u})+bT(\mathbf{v})$, which forces $T(\mathbf{0})=\mathbf{0}$; the matrix's **columns are the images of the basis vectors**; composition is matrix multiplication, right-to-left; kernel $=$ null space, image $=$ column space; $\det$ is the area scale factor, and $\det = 0$ means dimensions collapse; translation is affine, not linear, and homogeneous coordinates make it multiplicative.

**Next:** [[06-eigenvalues/01-eigenvalues-and-eigenvectors|Eigenvalues and Eigenvectors]] — the directions a transformation does not turn, and the basis that makes a matrix diagonal.

## Related

- [[01-matrices-and-determinants|Matrices and Determinants]] — the multiplication rule this lesson explains
- [[04-vector-spaces/01-vector-spaces|Vector Spaces]] — kernel and image under their other names
- [[02-graphs-and-identities|Graphs and Identities]] — the addition formulas block 4 recovers
- [[foundations/computer-graphics/index|computer-graphics/]] — where homogeneous coordinates are used in earnest
