# Eigenvalues and Eigenvectors

**[Advanced]** — the directions a transformation does not turn, and the change of basis that makes a matrix diagonal.

## Before you start

- You know that a matrix is a linear map and that its columns are the images of the basis vectors — [[05-linear-transformations/01-linear-transformations|linear transformations]].
- You can compute a $2\times2$ determinant and inverse — [[01-matrices-and-determinants|matrices and determinants]].
- You know what a basis is, and rank–nullity — [[04-vector-spaces/01-vector-spaces|vector spaces]].

**What you will be able to do after this lesson:**

1. Find eigenvalues from the **characteristic equation**, and eigenvectors from the null space of $A - \lambda I$.
2. Explain what an eigenvector *is* geometrically, and give a matrix that has **no real eigenvalues** at all.
3. **Diagonalise** a matrix, and use it to compute $A^{n}$ in a handful of operations rather than $n$ multiplications.
4. Find the steady state of a Markov chain as an eigenvector, and implement **power iteration**.

**Study route:** read 1–5, attempt the prediction in section 3, then run the lab. Block 5 is PageRank in miniature.

---

## 1. Why this exists

A linear map generally does two things to a vector: **stretches** it and **turns** it. The turning is what makes maps hard to reason about, and hard to iterate — apply a matrix ten times and the result is a tangle.

But most maps have special directions where the turning simply does not happen. Along those directions the map is nothing but a stretch by a number. Find them, use them as your coordinate axes, and the matrix becomes **diagonal** — and a diagonal matrix is as easy to work with as a list of numbers.

That is the whole idea, and its consequences are everywhere:

- **PageRank** is the dominant eigenvector of a web-link matrix.
- **Principal component analysis** finds the eigenvectors of a covariance matrix — the directions data varies most along.
- **Stability** of a physical system, a control loop or an iterative numerical method is decided by whether eigenvalue magnitudes exceed $1$.
- **Quantum mechanics** is built on them: observable quantities are eigenvalues of operators.
- The **classification of quadric surfaces** in [[02-quadric-surfaces|quadric surfaces]] was, as flagged there, a statement about the signs of eigenvalues.

## 2. The definition

A non-zero vector $\mathbf{v}$ is an **eigenvector** of $A$ with **eigenvalue** $\lambda$ when:

$$
A\mathbf{v} = \lambda\mathbf{v}
$$

In words: applying the matrix has the same effect as multiplying by a single number. The direction survives; only the length changes, by the factor $\lambda$.

| $\lambda$ | What happens along that direction |
| :--- | :--- |
| $\lambda > 1$ | Stretched |
| $0 < \lambda < 1$ | Shrunk |
| $\lambda = 1$ | Fixed — unchanged |
| $\lambda = 0$ | Collapsed to zero — this direction is in the kernel |
| $\lambda < 0$ | Flipped, and scaled by $\lvert\lambda\rvert$ |

The requirement $\mathbf{v} \neq \mathbf{0}$ matters: $A\mathbf{0} = \lambda\mathbf{0}$ holds for every $\lambda$, so allowing it would make the definition vacuous.

Eigenvectors are never unique either — if $\mathbf{v}$ is one, so is $5\mathbf{v}$ and $-\mathbf{v}$. What is really determined is a **direction**, or more precisely the **eigenspace**: the null space of $A - \lambda I$, which is a subspace.

## 3. Finding them

Rearrange the definition:

$$
A\mathbf{v} = \lambda\mathbf{v} \quad\Longrightarrow\quad A\mathbf{v} - \lambda\mathbf{v} = \mathbf{0} \quad\Longrightarrow\quad (A - \lambda I)\mathbf{v} = \mathbf{0}
$$

The middle step needs the $I$: you cannot subtract a number from a matrix, so $\lambda$ must be written as $\lambda I$.

Now the key move. We need a **non-zero** $\mathbf{v}$ in the null space of $A - \lambda I$. From [[04-vector-spaces/01-vector-spaces|vector spaces]], a non-trivial null space means the matrix is singular, and from [[01-matrices-and-determinants|lesson 1]] singular means zero determinant:

$$
\boxed{\det(A - \lambda I) = 0}
$$

This is the **characteristic equation**, and its left-hand side is a polynomial in $\lambda$ of degree $n$.

**For a $2\times2$ matrix** it takes a memorable form. Writing $A = \begin{pmatrix}a&b\\c&d\end{pmatrix}$:

$$
\det\begin{pmatrix}a-\lambda & b\\ c & d-\lambda\end{pmatrix} = \lambda^2 - (a+d)\lambda + (ad-bc) = \lambda^2 - (\operatorname{tr}A)\lambda + \det A
$$

So for $2\times2$: **the eigenvalues sum to the trace and multiply to the determinant.** A useful check, and often the fastest route.

**Then the eigenvectors:** for each $\lambda$, solve $(A - \lambda I)\mathbf{v} = \mathbf{0}$ by elimination. The matrix is singular by construction, so there will be a free variable — pick a convenient value for it.

### Worked example

$$
A = \begin{pmatrix}4 & 1\\ 2 & 3\end{pmatrix}, \qquad \operatorname{tr}A = 7, \quad \det A = 10
$$

$$
\lambda^2 - 7\lambda + 10 = 0 \quad\Longrightarrow\quad (\lambda-5)(\lambda-2) = 0 \quad\Longrightarrow\quad \lambda = 5,\ 2
$$

For $\lambda = 5$: $A - 5I = \begin{pmatrix}-1&1\\2&-2\end{pmatrix}$, so $-x + y = 0$, giving $\mathbf{v} = (1, 1)$.

For $\lambda = 2$: $A - 2I = \begin{pmatrix}2&1\\2&1\end{pmatrix}$, so $2x + y = 0$, giving $\mathbf{v} = (1, -2)$.

Check: $A(1,1) = (5,5) = 5(1,1)$. ✓ And $A(1,-2) = (2,-4) = 2(1,-2)$. ✓

> [!TIP]
> **Predict before section 4.** Consider the matrix that rotates the plane by $90°$: $\begin{pmatrix}0&-1\\1&0\end{pmatrix}$. Before computing anything — is there any direction a $90°$ rotation leaves pointing the same way? What does that tell you about its real eigenvalues, and what will the characteristic equation look like? Decide before opening the answers.

## 4. Diagonalisation

Suppose $A$ ($n\times n$) has $n$ independent eigenvectors. Put them in the columns of $P$ and the eigenvalues on the diagonal of $D$. Then:

$$
AP = PD \quad\Longrightarrow\quad A = PDP^{-1}
$$

The first equality is just "$A$ applied to each eigenvector is that eigenvector times its eigenvalue", written for all columns at once.

**Read $A = PDP^{-1}$ right to left as a recipe:**

1. $P^{-1}$ — rewrite the input in eigenvector coordinates.
2. $D$ — scale each coordinate by its eigenvalue. This is the whole transformation, and it is just $n$ multiplications.
3. $P$ — convert back to ordinary coordinates.

**The payoff is powers.** Since the middle terms cancel:

$$
A^{n} = PD^{n}P^{-1}
$$

and $D^n$ is just each diagonal entry raised to the $n$th power. Computing $A^{100}$ becomes three matrix multiplications and $n$ exponentiations, instead of 99 matrix multiplications — and, more importantly, you can *see* what happens as $n$ grows: the largest $\lambda$ dominates everything.

**Not every matrix is diagonalisable.** A shear $\begin{pmatrix}1&1\\0&1\end{pmatrix}$ has $\lambda = 1$ twice but only one independent eigenvector, so no basis of eigenvectors exists. Such matrices are called *defective*, and the nearest available simplification is the Jordan form.

**Symmetric matrices are always well behaved.** If $A = A^{T}$, then its eigenvalues are all **real**, and eigenvectors for different eigenvalues are **orthogonal**. This is the spectral theorem, and it is why covariance matrices — symmetric by construction — always yield the clean orthogonal axes that PCA uses.

## 5. Markov chains and power iteration

A **Markov chain** has a transition matrix whose columns are probabilities summing to $1$. Such a matrix always has $\lambda = 1$ as an eigenvalue, and its eigenvector — normalised to sum to $1$ — is the **steady state** the system settles into regardless of where it started.

You do not need the characteristic polynomial to find it. **Power iteration** works:

1. Start with any vector $\mathbf{x}_0$ that is not orthogonal to the dominant eigenvector.
2. Repeatedly set $\mathbf{x}_{k+1} = A\mathbf{x}_k$, normalising each time.
3. It converges to the eigenvector of the **largest-magnitude** eigenvalue.

**Why it works:** write $\mathbf{x}_0$ in the eigenvector basis. Each application multiplies the $i$th component by $\lambda_i$. After $k$ steps the ratio of any other component to the dominant one is $(\lambda_i/\lambda_1)^k \to 0$. Everything but the dominant direction dies out geometrically, at a rate set by $\lvert\lambda_2/\lambda_1\rvert$.

This is PageRank. The matrix is the web's link structure, and the dominant eigenvector is the ranking. Google's original contribution was not the mathematics — it was noticing that the mathematics applied, and making power iteration work at web scale.

## Worked example — runnable

**Runnable example:** save as `eigen.py` in any empty directory and run `python3 eigen.py`. Standard library only; writes no files.

```python
"""Eigenvalues by hand, diagonalisation, fast powers, and power iteration."""
import math

EPS = 1e-9


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))]
            for i in range(len(A))]


def apply(A, v):
    return [sum(A[i][k] * v[k] for k in range(len(v))) for i in range(len(A))]


def inverse2(A):
    d = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    return [[A[1][1] / d, -A[0][1] / d], [-A[1][0] / d, A[0][0] / d]]


def eigen2(A):
    """Eigenvalues of a 2x2 from lambda^2 - (trace)lambda + det = 0."""
    tr = A[0][0] + A[1][1]
    de = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    disc = tr * tr - 4 * de
    if disc < -EPS:
        return []                       # no REAL eigenvalues
    s = math.sqrt(max(0.0, disc))
    return sorted({(tr + s) / 2, (tr - s) / 2}, reverse=True)


def eigenvector2(A, lam):
    """A unit vector in the null space of A - lambda I."""
    a, b = A[0][0] - lam, A[0][1]
    c, d = A[1][0], A[1][1] - lam
    # both rows describe the same line through the origin; use a non-zero one
    v = [-b, a] if (abs(a) > EPS or abs(b) > EPS) else [-d, c]
    # an eigenvector is a DIRECTION, so -v works too; fix the sign for readability
    if v[0] < -EPS or (abs(v[0]) < EPS and v[1] < 0):
        v = [-v[0], -v[1]]
    n = math.hypot(*v)
    return [v[0] / n, v[1] / n]


def power_iteration(A, x0, steps=60):
    x = x0[:]
    for _ in range(steps):
        x = apply(A, x)
        n = math.sqrt(sum(v * v for v in x))
        x = [v / n for v in x]
    lam = sum(x[i] * apply(A, x)[i] for i in range(len(x)))   # Rayleigh quotient
    return x, lam


if __name__ == "__main__":
    A = [[4.0, 1.0], [2.0, 3.0]]

    print("Block 1 - the worked example, verified")
    lams = eigen2(A)
    print(f"  A = {A}")
    print(f"  trace = {A[0][0] + A[1][1]}, det = {A[0][0]*A[1][1] - A[0][1]*A[1][0]}")
    print("  characteristic equation: lambda^2 - 7 lambda + 10 = 0")
    print(f"  eigenvalues: {lams}")
    assert lams == [5.0, 2.0]
    print(f"  they sum to {sum(lams)} (the trace) and multiply to {lams[0]*lams[1]} (the det)")
    for lam in lams:
        v = eigenvector2(A, lam)
        Av = apply(A, v)
        lv = [lam * c for c in v]
        print(f"    lambda={lam}: v = {[round(c, 6) for c in v]}"
              f"   Av = {[round(c, 6) for c in Av]}   lambda*v = {[round(c, 6) for c in lv]}")
        assert all(abs(p - q) < 1e-9 for p, q in zip(Av, lv))

    print()
    print("Block 2 - some matrices have NO real eigenvalues")
    cases = [
        ("rotate 90 degrees", [[0.0, -1.0], [1.0, 0.0]]),
        ("rotate 30 degrees", [[math.cos(math.radians(30)), -math.sin(math.radians(30))],
                               [math.sin(math.radians(30)), math.cos(math.radians(30))]]),
        ("reflect in y=x",    [[0.0, 1.0], [1.0, 0.0]]),
        ("scale by 3",        [[3.0, 0.0], [0.0, 3.0]]),
        ("shear",             [[1.0, 1.0], [0.0, 1.0]]),
        ("projection",        [[1.0, 0.0], [0.0, 0.0]]),
    ]
    for label, M in cases:
        e = eigen2(M)
        print(f"  {label:20} eigenvalues: {[round(x, 6) for x in e] if e else 'none (real)'}")
    assert eigen2([[0.0, -1.0], [1.0, 0.0]]) == []
    print("  a rotation turns EVERY direction, so no real eigenvector can exist")
    print("  the reflection has +1 (the mirror line) and -1 (perpendicular to it)")
    print("  the projection has 1 (the x-axis) and 0 (the y-axis, which is the kernel)")
    assert eigen2([[1.0, 0.0], [0.0, 0.0]]) == [1.0, 0.0]

    print()
    print("Block 3 - diagonalisation, and powers for almost free")
    v1 = eigenvector2(A, 5.0)
    v2 = eigenvector2(A, 2.0)
    P = [[v1[0], v2[0]], [v1[1], v2[1]]]
    D = [[5.0, 0.0], [0.0, 2.0]]
    Pinv = inverse2(P)
    rebuilt = matmul(matmul(P, D), Pinv)
    print(f"  P D P^-1 = {[[round(x, 9) for x in r] for r in rebuilt]}")
    print(f"  A        = {A}")
    for i in range(2):
        for j in range(2):
            assert abs(rebuilt[i][j] - A[i][j]) < 1e-9

    naive = [[1.0, 0.0], [0.0, 1.0]]
    for _ in range(10):
        naive = matmul(naive, A)
    Dn = [[5.0 ** 10, 0.0], [0.0, 2.0 ** 10]]
    fast = matmul(matmul(P, Dn), Pinv)
    print(f"  A^10 by 10 multiplications: {[[round(x, 3) for x in r] for r in naive]}")
    print(f"  A^10 by P D^10 P^-1:        {[[round(x, 3) for x in r] for r in fast]}")
    for i in range(2):
        for j in range(2):
            assert abs(naive[i][j] - fast[i][j]) < 1e-6
    print(f"  5^10 = {5**10:,} dwarfs 2^10 = {2**10:,}: the largest eigenvalue dominates")

    print()
    print("Block 4 - symmetric matrices: real eigenvalues, orthogonal eigenvectors")
    S = [[2.0, 1.0], [1.0, 2.0]]
    se = eigen2(S)
    sv = [eigenvector2(S, l) for l in se]
    print(f"  S = {S}, eigenvalues {se}")
    for l, v in zip(se, sv):
        print(f"    lambda={l}: v = {[round(c, 6) for c in v]}")
    dotp = sv[0][0] * sv[1][0] + sv[0][1] * sv[1][1]
    print(f"  their dot product = {dotp:.9f}  ->  orthogonal, as the spectral theorem promises")
    assert abs(dotp) < 1e-9

    print()
    print("Block 5 - a Markov chain: the steady state is an eigenvector")
    # columns are probabilities: sunny -> (0.9 sunny, 0.1 rainy); rainy -> (0.5, 0.5)
    M = [[0.9, 0.5], [0.1, 0.5]]
    print(f"  transition matrix {M}   (columns sum to 1)")
    print(f"  eigenvalues: {[round(x, 6) for x in eigen2(M)]}   - note the 1")
    assert abs(eigen2(M)[0] - 1.0) < 1e-9

    print("  starting from 'certainly sunny' and iterating:")
    state = [1.0, 0.0]
    for step in range(1, 41):
        state = apply(M, state)
        if step in (1, 2, 3, 5, 10, 20, 40):
            print(f"    after {step:2} steps: sunny {state[0]:.9f}  rainy {state[1]:.9f}")
    print(f"  exact steady state is (5/6, 1/6) = ({5/6:.9f}, {1/6:.9f})")
    assert abs(state[0] - 5 / 6) < 1e-9 and abs(state[1] - 1 / 6) < 1e-9

    print("  and from a completely different start it converges to the same place:")
    other = [0.0, 1.0]
    for _ in range(40):
        other = apply(M, other)
    print(f"    from 'certainly rainy': sunny {other[0]:.9f}  rainy {other[1]:.9f}")
    assert abs(other[0] - 5 / 6) < 1e-9

    print()
    print("Block 6 - power iteration finds the dominant eigenvector without any algebra")
    vec, lam = power_iteration(A, [1.0, 0.0])
    print(f"  starting from (1,0): converged to {[round(c, 6) for c in vec]}, lambda = {lam:.9f}")
    assert abs(lam - 5.0) < 1e-6
    expected = eigenvector2(A, 5.0)
    aligned = abs(vec[0] * expected[0] + vec[1] * expected[1])
    print(f"  |alignment with the true eigenvector| = {aligned:.9f}")
    assert abs(aligned - 1.0) < 1e-6

    print("  convergence rate is set by |lambda2/lambda1| = 2/5 = 0.4 per step:")
    x = [1.0, 0.0]
    for k in range(1, 13):
        x = apply(A, x)
        n = math.sqrt(sum(v * v for v in x))
        x = [v / n for v in x]
        err = 1 - abs(x[0] * expected[0] + x[1] * expected[1])
        if k in (1, 2, 4, 8, 12):
            print(f"    step {k:2}: 1 - alignment = {err:.3e}")

    print()
    print("eigen: passed")
```

Expected output:

```
Block 1 - the worked example, verified
  A = [[4.0, 1.0], [2.0, 3.0]]
  trace = 7.0, det = 10.0
  characteristic equation: lambda^2 - 7 lambda + 10 = 0
  eigenvalues: [5.0, 2.0]
  they sum to 7.0 (the trace) and multiply to 10.0 (the det)
    lambda=5.0: v = [0.707107, 0.707107]   Av = [3.535534, 3.535534]   lambda*v = [3.535534, 3.535534]
    lambda=2.0: v = [0.447214, -0.894427]   Av = [0.894427, -1.788854]   lambda*v = [0.894427, -1.788854]

Block 2 - some matrices have NO real eigenvalues
  rotate 90 degrees    eigenvalues: none (real)
  rotate 30 degrees    eigenvalues: none (real)
  reflect in y=x       eigenvalues: [1.0, -1.0]
  scale by 3           eigenvalues: [3.0]
  shear                eigenvalues: [1.0]
  projection           eigenvalues: [1.0, 0.0]
  a rotation turns EVERY direction, so no real eigenvector can exist
  the reflection has +1 (the mirror line) and -1 (perpendicular to it)
  the projection has 1 (the x-axis) and 0 (the y-axis, which is the kernel)

Block 3 - diagonalisation, and powers for almost free
  P D P^-1 = [[4.0, 1.0], [2.0, 3.0]]
  A        = [[4.0, 1.0], [2.0, 3.0]]
  A^10 by 10 multiplications: [[6510758.0, 3254867.0], [6509734.0, 3255891.0]]
  A^10 by P D^10 P^-1:        [[6510758.0, 3254867.0], [6509734.0, 3255891.0]]
  5^10 = 9,765,625 dwarfs 2^10 = 1,024: the largest eigenvalue dominates

Block 4 - symmetric matrices: real eigenvalues, orthogonal eigenvectors
  S = [[2.0, 1.0], [1.0, 2.0]], eigenvalues [3.0, 1.0]
    lambda=3.0: v = [0.707107, 0.707107]
    lambda=1.0: v = [0.707107, -0.707107]
  their dot product = 0.000000000  ->  orthogonal, as the spectral theorem promises

Block 5 - a Markov chain: the steady state is an eigenvector
  transition matrix [[0.9, 0.5], [0.1, 0.5]]   (columns sum to 1)
  eigenvalues: [1.0, 0.4]   - note the 1
  starting from 'certainly sunny' and iterating:
    after  1 steps: sunny 0.900000000  rainy 0.100000000
    after  2 steps: sunny 0.860000000  rainy 0.140000000
    after  3 steps: sunny 0.844000000  rainy 0.156000000
    after  5 steps: sunny 0.835040000  rainy 0.164960000
    after 10 steps: sunny 0.833350810  rainy 0.166649190
    after 20 steps: sunny 0.833333335  rainy 0.166666665
    after 40 steps: sunny 0.833333333  rainy 0.166666667
  exact steady state is (5/6, 1/6) = (0.833333333, 0.166666667)
  and from a completely different start it converges to the same place:
    from 'certainly rainy': sunny 0.833333333  rainy 0.166666667

Block 6 - power iteration finds the dominant eigenvector without any algebra
  starting from (1,0): converged to [0.707107, 0.707107], lambda = 5.000000000
  |alignment with the true eigenvector| = 1.000000000
  convergence rate is set by |lambda2/lambda1| = 2/5 = 0.4 per step:
    step  1: 1 - alignment = 5.132e-02
    step  2: 1 - alignment = 7.722e-03
    step  4: 1 - alignment = 1.866e-04
    step  8: 1 - alignment = 1.208e-07
    step 12: 1 - alignment = 7.917e-11

eigen: passed
```

Block 5 is the whole idea in one place. Two completely different starting states, forty steps of nothing but matrix–vector multiplication, and both land on $(5/6, 1/6)$ — the eigenvector for $\lambda = 1$, to nine decimal places.

## Common pitfalls and traps

- **Forgetting the $I$.** It is $\det(A - \lambda I) = 0$, not $\det(A - \lambda)$. Subtracting a scalar from a matrix is not defined.
- **Accepting $\mathbf{v} = \mathbf{0}$.** It satisfies the equation for every $\lambda$ and is excluded by definition. When solving $(A-\lambda I)\mathbf{v} = \mathbf{0}$ you want the *non-trivial* null space vectors.
- **Expecting real eigenvalues.** A rotation has none — the characteristic equation has a negative discriminant. Over the complex numbers every $n\times n$ matrix has $n$ eigenvalues counted with multiplicity, which is one of the strongest arguments for complex numbers existing.
- **Assuming every matrix diagonalises.** A repeated eigenvalue may come with too few independent eigenvectors. The shear in block 2 has $\lambda = 1$ twice and only one eigendirection.
- **Using the characteristic polynomial numerically.** For anything beyond $3\times3$, finding polynomial roots is badly conditioned — small coefficient errors move the roots a lot. Real software uses the QR algorithm, never the characteristic polynomial.
- **Expecting power iteration always to converge.** It needs a *strictly* dominant eigenvalue and a starting vector with a component along it. Two eigenvalues of equal magnitude — as with a rotation — make it oscillate instead.

## Check your understanding

1. Find the eigenvalues of $\begin{pmatrix}3&0\\0&-2\end{pmatrix}$ and their eigenvectors, by inspection.
2. A $2\times2$ matrix has trace $6$ and determinant $8$. What are its eigenvalues?
3. What does an eigenvalue of $0$ tell you about a matrix?
4. Why are the eigenvalues of a triangular matrix just its diagonal entries?
5. A Markov transition matrix always has $\lambda = 1$. Why must that be so?

<details><summary>Answers — open only after an attempt</summary>

1. A diagonal matrix acts on each axis separately: $\lambda = 3$ with eigenvector $(1,0)$, and $\lambda = -2$ with eigenvector $(0,1)$. The $-2$ flips that axis as well as stretching it.
2. $\lambda^2 - 6\lambda + 8 = 0$, so $(\lambda-4)(\lambda-2) = 0$: $\lambda = 4$ and $2$. Check: they sum to $6$ and multiply to $8$. ✓
3. There is a non-zero vector with $A\mathbf{v} = \mathbf{0}$, so the null space is non-trivial. Hence $A$ is **singular** — not invertible, determinant zero. In fact $\det A$ is the *product* of the eigenvalues, so a zero eigenvalue forces a zero determinant.
4. Because $A - \lambda I$ is still triangular, and the determinant of a triangular matrix is the product of its diagonal entries. So $\det(A-\lambda I) = \prod_i (a_{ii} - \lambda)$, which vanishes exactly at the diagonal entries.
5. Because each column sums to $1$, so the *row* sums of $A^{T}$ are $1$, meaning $A^{T}$ maps the all-ones vector to itself — an eigenvector with $\lambda = 1$. A matrix and its transpose have the same characteristic polynomial and hence the same eigenvalues, so $A$ has $\lambda = 1$ too. That guarantees a steady state exists.

**And the prediction from section 3:** a $90°$ rotation turns *every* direction, so **no** real eigenvector can exist. The characteristic equation is $\lambda^2 - 0\lambda + 1 = \lambda^2 + 1 = 0$, whose discriminant is $-4 < 0$ — no real roots. The complex roots are $\pm i$, which is the first hint that rotation and complex multiplication are the same operation.
</details>

## Practice — independent task

Implement `pagerank(links, damping=0.85)` — power iteration on a real link structure.

1. Build the transition matrix from an adjacency list: if page $j$ has $k$ outgoing links, each gets probability $1/k$ in column $j$.
2. Handle **dangling nodes** — pages with no outgoing links produce a zero column, which breaks the column-sum property. The standard fix distributes their rank evenly over all pages; implement it and say in a comment why the raw matrix fails without it.
3. Apply damping: $M' = d\,M + \frac{1-d}{n}J$, where $J$ is all-ones. Explain what the damping factor represents and why $d < 1$ guarantees convergence.
4. Run power iteration until the change falls below a tolerance you choose. Report the number of iterations.
5. Verify the result **is** an eigenvector: check $M'\mathbf{r} = \mathbf{r}$ to within `1e-9`, and that the entries sum to $1$.

Then investigate:

6. Build a small graph where one page is linked by many low-ranked pages and another by one high-ranked page. Show which wins, and explain why that is the behaviour Google wanted.
7. Measure how the iteration count varies with $d$ for $d = 0.5, 0.85, 0.95, 0.99$, and relate it to the convergence rate $\lvert\lambda_2/\lambda_1\rvert$ from section 5.

**Edge cases:** a single page; two pages linking only to each other (a "rank sink" — what does damping do about it?); a page linking to itself; a disconnected graph.

**Done when:** your eigenvector check passes, your step-6 example behaves as you predicted before running it, and your step-7 numbers show the trend you expect from the theory rather than one you rationalise afterwards.

## Tradeoffs, limits and extensions

**Never compute eigenvalues from the characteristic polynomial.** Root-finding for polynomials is ill-conditioned: Wilkinson's classic example is a degree-20 polynomial whose roots move by orders of magnitude under a change of $2^{-23}$ in one coefficient. Production libraries use the **QR algorithm**, which is iterative and numerically stable, and compute the polynomial — if at all — from the eigenvalues rather than the reverse.

**Symmetric is a much easier case.** Real eigenvalues, orthogonal eigenvectors, always diagonalisable, and specialised algorithms that are faster and more accurate than the general ones. If your matrix is symmetric, say so to your library. Covariance matrices, adjacency matrices of undirected graphs, and Hessians are all symmetric, which is why PCA and spectral clustering are numerically comfortable.

**The SVD generalises this to non-square matrices.** Eigenvalues need $A$ square, and even then may not give a full basis. The **singular value decomposition** $A = U\Sigma V^{T}$ exists for every matrix, always has orthogonal factors, and is the tool of choice for rank, least squares, compression and pseudo-inverses. Where eigenvalues are the natural object for *iteration*, singular values are the natural object for *approximation*.

## Before moving on

You are done with this lesson when you can:

- Find $2\times2$ eigenvalues from trace and determinant, and eigenvectors from the null space of $A - \lambda I$.
- Explain geometrically why a rotation has no real eigenvectors.
- Diagonalise a matrix and use it to compute a high power cheaply.
- Find a Markov steady state, by algebra and by power iteration, and explain why power iteration works.

**Recap for later lookup:** $A\mathbf{v} = \lambda\mathbf{v}$ with $\mathbf{v}\neq\mathbf{0}$; solve $\det(A-\lambda I) = 0$; for $2\times2$, $\lambda^2 - (\operatorname{tr}A)\lambda + \det A = 0$, so eigenvalues sum to the trace and multiply to the determinant; eigenvectors span the null space of $A - \lambda I$; $A = PDP^{-1}$ gives $A^n = PD^nP^{-1}$; symmetric matrices have real eigenvalues and orthogonal eigenvectors; power iteration converges to the dominant eigenvector at rate $\lvert\lambda_2/\lambda_1\rvert$; a Markov matrix always has $\lambda = 1$, whose eigenvector is the steady state.

**Where next:** this is the last lesson in linear algebra. The natural continuations are [[02-quadric-surfaces|quadric surfaces]], whose classification is a statement about eigenvalue signs, and **06-calculus/04-calculus-3/03-optimization**, where the Hessian's eigenvalues decide whether a stationary point is a maximum, a minimum or a saddle.

## Related

- [[05-linear-transformations/01-linear-transformations|Linear Transformations]] — the change of basis diagonalisation performs
- [[04-vector-spaces/01-vector-spaces|Vector Spaces]] — eigenspaces are null spaces
- [[02-quadric-surfaces|Quadric Surfaces]] — classification by the signs of eigenvalues
- [[ai-ml/index|ai-ml/]] — PCA, spectral methods, and why symmetric matrices matter there
