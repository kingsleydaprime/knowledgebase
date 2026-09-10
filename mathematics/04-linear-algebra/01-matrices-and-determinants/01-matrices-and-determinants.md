# Matrices and Determinants

**[Intermediate]** — a table of numbers that *does something*, and the single number that says whether it can be undone.

## Before you start

- You can solve simultaneous linear equations by substitution or elimination — [[01-linear-equations|linear equations]].
- Helpful but not required: the dot product — [[01-lines-and-planes|lines and planes in space]]. Matrix multiplication is built from it.

**What you will be able to do after this lesson:**

1. Add, scale and **multiply** matrices, and explain why multiplication is defined by that strange row-times-column rule rather than element by element.
2. Compute a determinant for $2\times2$ and $3\times3$, and say what it **measures**.
3. Decide whether a matrix has an inverse, find it for $2\times2$, and explain what a zero determinant means geometrically.
4. State why matrix multiplication is not commutative, with a concrete counterexample.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 3 is the one that explains what a determinant *is*.

---

## 1. Why this exists

Solve this by hand:

$$
2x + 3y = 8, \qquad x - y = -1
$$

Straightforward. Now do it for **twelve** equations in twelve unknowns — a circuit with twelve nodes, or a structure with twelve joints. The algebra is identical in kind and unmanageable in practice, because the bookkeeping swamps the mathematics.

A matrix is that bookkeeping, separated out. Write the coefficients in a grid, the unknowns in a column, and the whole system becomes:

$$
A\mathbf{x} = \mathbf{b}
$$

which looks exactly like $ax = b$, and can be manipulated with the same instincts. That compression is the first reason matrices exist.

The second reason is bigger, and it is why this lesson is in a course rather than a reference card: **a matrix is not really a table, it is a function.** It takes a vector in and gives a vector out. Every rotation, scaling and projection in a graphics engine is a matrix; so is every step of a neural network. The table is how the function is stored. [[05-linear-transformations/01-linear-transformations|Linear transformations]] develops that properly — but it is worth knowing from the start, because it is what makes the multiplication rule sensible instead of arbitrary.

## 2. Terminology

| Term | Plain-English definition | Example |
| :--- | :--- | :--- |
| **Matrix** | A rectangular array of numbers | $\begin{pmatrix}1&2\\3&4\end{pmatrix}$ |
| **Order** (dimensions) | Rows $\times$ columns, in that order | A $2\times3$ matrix has 2 rows, 3 columns |
| **Element** $a_{ij}$ | The entry in row $i$, column $j$ | Row first, always |
| **Square matrix** | Same number of rows and columns | Only these can have inverses |
| **Identity** $I$ | Ones on the diagonal, zeros elsewhere | The matrix that changes nothing |
| **Transpose** $A^{T}$ | Rows and columns swapped | $(A^T)_{ij} = a_{ji}$ |
| **Determinant** $\det A$ | One number summarising a square matrix | Zero means "not invertible" |
| **Inverse** $A^{-1}$ | The matrix undoing $A$, so $AA^{-1} = I$ | Exists only when $\det A \neq 0$ |
| **Singular** | Having no inverse — determinant zero | Information was destroyed |

## 3. Operations

**Addition and scalar multiplication** are elementwise, and unsurprising:

$$
(A + B)_{ij} = a_{ij} + b_{ij}, \qquad (kA)_{ij} = k\,a_{ij}
$$

Both require the matrices to be the same size.

**Multiplication is not elementwise.** The rule is:

$$
(AB)_{ij} = \sum_{k} a_{ik}\,b_{kj}
$$

— the **dot product of row $i$ of $A$ with column $j$ of $B$**. For this to make sense, the number of columns in $A$ must equal the number of rows in $B$:

$$
(m \times n)(n \times p) = (m \times p)
$$

The inner dimensions must match and they vanish; the outer ones survive.

### Why that rule, and not elementwise?

Elementwise multiplication exists and is occasionally useful, but it is not what "matrix multiplication" means, because it does not correspond to anything.

The row-times-column rule is exactly what you get by asking: *if $A$ and $B$ are functions, what table represents "do $B$, then do $A$"?* Work through applying $B$ to a vector and then $A$ to the result, and the coefficients that fall out are $\sum_k a_{ik}b_{kj}$. Matrix multiplication is **composition of functions**, written down.

Two consequences follow immediately:

- **It is not commutative.** $AB \neq BA$ in general — because "rotate then scale" is not "scale then rotate". The lab gives a two-line counterexample.
- **It is associative.** $(AB)C = A(BC)$, because composing functions is associative.

## 4. The determinant

For a $2\times2$ matrix:

$$
\det\begin{pmatrix}a & b\\ c& d\end{pmatrix} = ad - bc
$$

For a $3\times3$, expand along any row or column with alternating signs (cofactor expansion):

$$
\det\begin{pmatrix}a&b&c\\d&e&f\\g&h&i\end{pmatrix} = a(ei-fh) - b(di-fg) + c(dh-eg)
$$

### What it measures

This is the part usually left out, and without it the formula is unmemorable.

> **The determinant is the factor by which the matrix scales area (in 2-D) or volume (in 3-D).**

Take the unit square with corners $(0,0), (1,0), (1,1), (0,1)$ — area $1$. Apply the matrix to each corner. You get a parallelogram, and its area is exactly $\lvert\det A\rvert$. Block 3 of the lab measures this directly with the shoelace formula from [[01-plane-shapes|plane shapes]].

Everything else about determinants follows from that reading:

- **$\det A = 0$ means the area is crushed to zero.** The matrix squashes the plane onto a line (or a point). That destroys information — many inputs map to the same output — so it cannot be undone, which is exactly why a zero determinant means **no inverse**.
- **$\det(AB) = \det(A)\det(B)$.** Do one transformation, then another; the area factors multiply. This identity is a chore to prove algebraically and obvious from the geometry.
- **A negative determinant** means the orientation was flipped — the plane was reflected as well as stretched.

### The inverse of a $2\times2$

$$
A^{-1} = \frac{1}{\det A}\begin{pmatrix}d & -b\\ -c & a\end{pmatrix}
$$

Swap the diagonal, negate the off-diagonal, divide by the determinant. The division is why $\det A = 0$ breaks it.

> [!TIP]
> **Predict before running the lab.** $A$ scales everything by $3$ in both directions. $B$ rotates by $90°$. Before computing: what is $\det A$? What is $\det B$? And is $AB = BA$ for *these two particular* matrices, even though matrix multiplication is not commutative in general? Decide before opening the answers.

## 5. Solving $A\mathbf{x} = \mathbf{b}$

With an inverse in hand:

$$
A\mathbf{x} = \mathbf{b} \quad\Longrightarrow\quad \mathbf{x} = A^{-1}\mathbf{b}
$$

**Cramer's rule** gives each unknown as a ratio of determinants:

$$
x_i = \frac{\det A_i}{\det A}
$$

where $A_i$ is $A$ with column $i$ replaced by $\mathbf{b}$.

Both are fine for $2\times2$ and $3\times3$, and both are **the wrong way to solve a real system**. Cramer's rule on an $n\times n$ system costs $O(n!)$ if determinants are computed by cofactor expansion — for $n = 20$ that is more operations than there are atoms in your body. Gaussian elimination costs $O(n^3)$, and is what every library actually does. That is the subject of [[03-systems-of-linear-equations/01-gaussian-elimination|systems of linear equations]].

## Worked example — runnable

**Runnable example:** save as `matrices.py` in any empty directory and run `python3 matrices.py`. Standard library only; writes no files.

```python
"""Matrix arithmetic, determinants, and what a determinant measures."""
import math
from fractions import Fraction

EPS = 1e-9


def shape(A):
    return (len(A), len(A[0]))


def matmul(A, B):
    """Row i of A dotted with column j of B."""
    ra, ca = shape(A)
    rb, cb = shape(B)
    if ca != rb:
        raise ValueError(f"cannot multiply {ra}x{ca} by {rb}x{cb}")
    return [[sum(A[i][k] * B[k][j] for k in range(ca)) for j in range(cb)]
            for i in range(ra)]


def identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def det(A):
    """Cofactor expansion along the first row. Fine for small n, awful for large."""
    n = len(A)
    if n == 1:
        return A[0][0]
    if n == 2:
        return A[0][0] * A[1][1] - A[0][1] * A[1][0]
    total = 0
    for j in range(n):
        minor = [row[:j] + row[j+1:] for row in A[1:]]
        total += ((-1) ** j) * A[0][j] * det(minor)
    return total


def inverse2(A):
    d = det(A)
    if abs(d) < EPS:
        return None                      # singular: area crushed to zero
    return [[A[1][1] / d, -A[0][1] / d],
            [-A[1][0] / d, A[0][0] / d]]


def apply(A, v):
    return [sum(A[i][k] * v[k] for k in range(len(v))) for i in range(len(A))]


def shoelace(points):
    """Area of a polygon, from the plane-shapes lesson."""
    n = len(points)
    return abs(sum(points[i][0] * points[(i+1) % n][1]
                   - points[(i+1) % n][0] * points[i][1] for i in range(n))) / 2


def show(name, A):
    print(f"  {name} =")
    for row in A:
        print("      [" + "  ".join(f"{v:7.3f}" if isinstance(v, float) else f"{v:7}"
                                    for v in row) + "]")


if __name__ == "__main__":
    A = [[2, 3], [1, -1]]
    B = [[1, 0], [4, 5]]

    print("Block 1 - multiplication is row-times-column, and order matters")
    show("A", A); show("B", B)
    show("AB", matmul(A, B))
    show("BA", matmul(B, A))
    assert matmul(A, B) != matmul(B, A), "these should differ"
    print("  AB != BA: matrix multiplication does not commute")
    # but it IS associative
    C = [[0, 1], [1, 1]]
    assert matmul(matmul(A, B), C) == matmul(A, matmul(B, C))
    print("  (AB)C == A(BC): it is associative, because composing functions is")

    print()
    print("  dimensions must line up, and the inner ones vanish:")
    P = [[1, 2, 3], [4, 5, 6]]           # 2x3
    Q = [[1, 0], [0, 1], [1, 1]]         # 3x2
    print(f"    {shape(P)} times {shape(Q)} -> {shape(matmul(P, Q))}")
    print(f"    {shape(Q)} times {shape(P)} -> {shape(matmul(Q, P))}")
    try:
        matmul(P, P)
    except ValueError as e:
        print(f"    {shape(P)} times {shape(P)} -> refused: {e}")

    print()
    print("Block 2 - the identity changes nothing, and the inverse undoes")
    I = identity(2)
    assert matmul(A, I) == A and matmul(I, A) == A
    print(f"  AI == IA == A")
    Ainv = inverse2(A)
    show("A^-1", Ainv)
    product = matmul(A, Ainv)
    show("A A^-1", product)
    for i in range(2):
        for j in range(2):
            assert abs(product[i][j] - I[i][j]) < EPS

    singular = [[2, 4], [1, 2]]          # row 2 is row 1 halved
    print(f"  det of [[2,4],[1,2]] = {det(singular)}  ->  inverse: {inverse2(singular)}")
    assert inverse2(singular) is None

    print()
    print("Block 3 - the determinant IS the area scale factor")
    unit_square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    print(f"  the unit square has area {shoelace(unit_square):.6f}")
    print("      matrix                    det     image area   ratio")
    tests = [
        ("scale by 3",        [[3, 0], [0, 3]]),
        ("scale x only",      [[5, 0], [0, 1]]),
        ("rotate 90 degrees", [[0, -1], [1, 0]]),
        ("shear",             [[1, 2], [0, 1]]),
        ("reflect in y=x",    [[0, 1], [1, 0]]),
        ("singular",          [[2, 4], [1, 2]]),
    ]
    for label, M in tests:
        image = [tuple(apply(M, list(p))) for p in unit_square]
        area = shoelace(image)
        d = det(M)
        ratio = "n/a" if abs(d) < EPS else f"{area / abs(d):.4f}"
        print(f"  {label:20} {d:8.3f}   {area:9.4f}   {ratio}")
        assert abs(area - abs(d)) < EPS, (label, area, d)
    print("  image area equals |det| every time - that is what a determinant means")
    print("  the shear has det 1: it slants the square without changing its area")
    print("  the singular one has det 0: the square is crushed onto a line")

    print()
    print("Block 4 - det(AB) = det(A)det(B), because area factors multiply")
    for M, N in [(A, B), (B, C), ([[3, 1], [2, 4]], [[0, -2], [5, 1]])]:
        lhs, rhs = det(matmul(M, N)), det(M) * det(N)
        print(f"  det(MN) = {lhs:8.3f}   det(M)det(N) = {rhs:8.3f}")
        assert abs(lhs - rhs) < EPS

    print()
    print("Block 5 - a 3x3 determinant, and Cramer's rule")
    M3 = [[2, -1, 3], [1, 4, -2], [3, 0, 1]]
    show("M3", M3)
    print(f"  det(M3) = {det(M3)}")
    b = [5, 1, 8]
    solution = []
    for i in range(3):
        Mi = [row[:] for row in M3]
        for r in range(3):
            Mi[r][i] = b[r]
        solution.append(Fraction(det(Mi), det(M3)))
    print(f"  Cramer's rule gives x = {[str(v) for v in solution]}")
    check = apply(M3, [float(v) for v in solution])
    print(f"  M3 x = {[round(v, 9) for v in check]}   (should be {b})")
    for got, want in zip(check, b):
        assert abs(got - want) < EPS

    print()
    print("  why Cramer's rule is not used in practice - cofactor cost:")
    ops = 1
    for n in range(2, 13):
        ops *= n
        if n in (3, 5, 10, 12):
            print(f"    n={n:3}: about {ops:>12,} multiplications, versus n^3 = {n**3:,}")

    print()
    print("matrices: passed")
```

Expected output:

```
Block 1 - multiplication is row-times-column, and order matters
  A =
      [      2        3]
      [      1       -1]
  B =
      [      1        0]
      [      4        5]
  AB =
      [     14       15]
      [     -3       -5]
  BA =
      [      2        3]
      [     13        7]
  AB != BA: matrix multiplication does not commute
  (AB)C == A(BC): it is associative, because composing functions is

  dimensions must line up, and the inner ones vanish:
    (2, 3) times (3, 2) -> (2, 2)
    (3, 2) times (2, 3) -> (3, 3)
    (2, 3) times (2, 3) -> refused: cannot multiply 2x3 by 2x3

Block 2 - the identity changes nothing, and the inverse undoes
  AI == IA == A
  A^-1 =
      [  0.200    0.600]
      [  0.200   -0.400]
  A A^-1 =
      [  1.000   -0.000]
      [  0.000    1.000]
  det of [[2,4],[1,2]] = 0  ->  inverse: None

Block 3 - the determinant IS the area scale factor
  the unit square has area 1.000000
      matrix                    det     image area   ratio
  scale by 3              9.000      9.0000   1.0000
  scale x only            5.000      5.0000   1.0000
  rotate 90 degrees       1.000      1.0000   1.0000
  shear                   1.000      1.0000   1.0000
  reflect in y=x         -1.000      1.0000   1.0000
  singular                0.000      0.0000   n/a
  image area equals |det| every time - that is what a determinant means
  the shear has det 1: it slants the square without changing its area
  the singular one has det 0: the square is crushed onto a line

Block 4 - det(AB) = det(A)det(B), because area factors multiply
  det(MN) =  -25.000   det(M)det(N) =  -25.000
  det(MN) =   -5.000   det(M)det(N) =   -5.000
  det(MN) =  100.000   det(M)det(N) =  100.000

Block 5 - a 3x3 determinant, and Cramer's rule
  M3 =
      [      2       -1        3]
      [      1        4       -2]
      [      3        0        1]
  det(M3) = -21
  Cramer's rule gives x = ['59/21', '-2/3', '-3/7']
  M3 x = [5.0, 1.0, 8.0]   (should be [5, 1, 8])

  why Cramer's rule is not used in practice - cofactor cost:
    n=  3: about            6 multiplications, versus n^3 = 27
    n=  5: about          120 multiplications, versus n^3 = 125
    n= 10: about    3,628,800 multiplications, versus n^3 = 1,000
    n= 12: about  479,001,600 multiplications, versus n^3 = 1,728

matrices: passed
```

Block 3 is the lesson. Six different matrices, and in every case the transformed square's area equals $\lvert\det\rvert$ — including the shear, which slants the square without changing its area at all, and the singular matrix, which flattens it to nothing.

## Common pitfalls and traps

- **Multiplying elementwise.** The rule is row-times-column. Elementwise multiplication (the Hadamard product) is a different operation with a different purpose.
- **Assuming $AB = BA$.** It usually is not. Worse, $AB$ can be defined while $BA$ is not, if the dimensions only line up one way.
- **Cancelling matrices.** From $AB = AC$ you may **not** conclude $B = C$ unless $A$ is invertible. If $A$ crushes information, different inputs can give the same output.
- **Expecting $(AB)^{-1} = A^{-1}B^{-1}$.** The order reverses: $(AB)^{-1} = B^{-1}A^{-1}$. To undo "put on socks, then shoes", take off the shoes first.
- **Reading a zero determinant as a computational failure.** It is a fact about the matrix: it collapses dimensions. The system either has no solution or infinitely many, never exactly one.
- **Using the cofactor determinant on anything large.** It is $O(n!)$. The lab prints the numbers; for $n = 12$ it is already about 479 million multiplications against $1{,}728$ for elimination.

## Check your understanding

1. For $A = \begin{pmatrix}1&2\\3&4\end{pmatrix}$ and $B = \begin{pmatrix}0&1\\1&0\end{pmatrix}$, compute $AB$ and $BA$.
2. Find $\det\begin{pmatrix}4&7\\2&6\end{pmatrix}$ and its inverse.
3. A $2\times2$ matrix has determinant $-2$. What does the sign tell you, and what happens to a shape of area $5$?
4. If $A$ is $3\times4$ and $B$ is $4\times2$, what are the dimensions of $AB$? Is $BA$ defined?
5. Why does $\det A = 0$ mean $A\mathbf{x} = \mathbf{b}$ cannot have exactly one solution?

<details><summary>Answers — open only after an attempt</summary>

1. $AB = \begin{pmatrix}2&1\\4&3\end{pmatrix}$ (swaps the columns), $BA = \begin{pmatrix}3&4\\1&2\end{pmatrix}$ (swaps the rows). Different, as expected.
2. $\det = 4(6) - 7(2) = 24 - 14 = 10$. Inverse $= \frac{1}{10}\begin{pmatrix}6&-7\\-2&4\end{pmatrix} = \begin{pmatrix}0.6&-0.7\\-0.2&0.4\end{pmatrix}$.
3. The negative sign means the orientation is **flipped** — the plane is reflected as well as stretched. A shape of area $5$ becomes area $\lvert-2\rvert \times 5 = 10$.
4. $AB$ is $3\times2$ — inner dimensions $4$ and $4$ match and vanish. $BA$ is **not defined**: $B$ has $2$ columns, $A$ has $3$ rows.
5. A zero determinant means $A$ crushes space onto a lower-dimensional set. So either $\mathbf{b}$ is not in the image — no solution — or it is, and a whole line (or plane) of inputs maps to it — infinitely many solutions. Exactly one is impossible.

**And the prediction from section 4:** $\det A = 9$, since scaling by $3$ in both directions multiplies area by $3 \times 3$. $\det B = 1$, since rotation preserves area. And for *these two* matrices $AB = BA$ **does** hold — scaling uniformly by 3 commutes with everything, because $A = 3I$ and $3I$ is just multiplication by a number. Non-commutativity is the general rule, not a universal one.
</details>

## Practice — independent task

Implement `matrix_power(A, n)` computing $A^n$ by **exponentiation by squaring**, then use it on a real problem.

1. Implement it in $O(\log n)$ matrix multiplications rather than $n$, using $A^n = (A^{n/2})^2$ for even $n$. Handle $n = 0$ (the identity) and reject negative $n$ unless you also implement the inverse.
2. Verify against naive repeated multiplication for $n$ up to $20$.
3. **Apply it to Fibonacci.** The matrix $\begin{pmatrix}1&1\\1&0\end{pmatrix}$ raised to the $n$th power has $F_{n+1}, F_n$ in its first row. Verify against a directly computed Fibonacci sequence for $n$ up to $40$.
4. Count the multiplications each method uses for $n = 1000$, and report both numbers.
5. Then the interesting part: compute $\det\!\left(\begin{pmatrix}1&1\\1&0\end{pmatrix}^n\right)$ for several $n$, and use $\det(AB) = \det A\det B$ to **prove** the identity you observe. It is a known Fibonacci identity — state it.

**Edge cases:** $n = 0$ and $n = 1$; a singular matrix raised to a power; a $1\times1$ matrix.

**Done when:** your fast version matches the naive one for every $n$ tested, your Fibonacci check passes to $n = 40$, and you can state and prove the determinant identity from step 5 rather than just observing it.

## Tradeoffs, limits and extensions

**Determinants are a poor numerical test for invertibility.** A matrix can have a determinant of $10^{-18}$ and be perfectly well-conditioned, or a determinant of $1$ and be nearly singular — scaling a matrix by $k$ multiplies its determinant by $k^n$, so the value carries no absolute meaning. Numerical libraries use the **condition number** instead, which measures how much an input error is amplified. "Is $\det A$ close to zero?" is the wrong question.

**Cofactor expansion is only for teaching.** Real determinants are computed by doing Gaussian elimination and multiplying the pivots — $O(n^3)$, the same cost as solving the system, and the determinant falls out as a by-product.

**Multiplication is faster than it looks.** The definition costs $O(n^3)$. Strassen's algorithm achieves about $O(n^{2.81})$ by trading multiplications for additions, and the theoretical record is lower still, though those algorithms are numerically fragile and rarely used below very large sizes.

## Before moving on

You are done with this lesson when you can:

- Multiply matrices without hesitating over which dimension must match.
- State what a determinant measures, and explain a zero determinant geometrically.
- Invert a $2\times2$ and say why the formula fails when the determinant vanishes.
- Give a concrete counterexample to $AB = BA$.

**Recap for later lookup:** $(AB)_{ij}$ is row $i$ of $A$ dotted with column $j$ of $B$; $(m\times n)(n\times p) = (m\times p)$; multiplication is associative but **not** commutative; $\det\begin{pmatrix}a&b\\c&d\end{pmatrix} = ad-bc$ and equals the area scale factor; $\det(AB) = \det A\det B$; $A^{-1} = \frac{1}{\det A}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$; $\det A = 0$ means singular, no inverse, never exactly one solution; $(AB)^{-1} = B^{-1}A^{-1}$.

**Next:** [[02-vectors/01-vectors|Vectors]] — the objects matrices act *on*, developed algebraically and in any number of dimensions.

## Related

- [[01-linear-equations|Linear Equations]] — the systems matrices were invented to manage
- [[03-systems-of-linear-equations/01-gaussian-elimination|Systems of Linear Equations]] — how they are actually solved
- [[05-linear-transformations/01-linear-transformations|Linear Transformations]] — why the multiplication rule is what it is
- [[01-plane-shapes|Plane Shapes]] — the shoelace formula the lab uses to measure area
