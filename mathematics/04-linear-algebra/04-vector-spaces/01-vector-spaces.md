# Vector Spaces

**[Advanced]** — the abstraction that lets polynomials, matrices and functions all be vectors, and the theorem that ties rank to solution count.

## Before you start

- You can run Gaussian elimination and read off a rank — [[03-systems-of-linear-equations/01-gaussian-elimination|systems of linear equations]].
- You are comfortable with vector arithmetic in $n$ dimensions — [[02-vectors/01-vectors|vectors]].
- Helpful: [[03-proof-techniques|proof techniques]], since this lesson is about checking axioms.

**What you will be able to do after this lesson:**

1. State what a **vector space** is, and check whether a given set is one — including sets whose elements are not arrows.
2. Test a list of vectors for **linear independence**, and extract a **basis** and a **dimension**.
3. Compute the **column space** and **null space** of a matrix, and give a basis for each.
4. State and verify the **rank–nullity theorem**, and use it to predict the shape of a solution set before solving.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 5 is the one that justifies the abstraction.

---

## 1. Why this exists

So far a vector has been a list of numbers. Here is the observation that changes the subject.

Consider polynomials of degree at most 2: things like $3 + 2x - x^2$. You can **add** two of them and get another. You can **multiply** one by a number and get another. Addition is commutative and associative, there is a zero, every polynomial has a negative, and the scalar rules all hold.

Now consider $2\times2$ matrices. Same story. Continuous functions on $[0,1]$: same story. Solutions of $y'' + y = 0$: same story again.

Every theorem proved using only "you can add them and scale them" is therefore **simultaneously** a theorem about arrows, about polynomials, about matrices, about functions, and about solutions of differential equations. That is not a philosophical nicety — it is why the same code diagonalises a matrix and solves a differential equation, and why "the space of solutions is 2-dimensional" is a meaningful and useful statement about an ODE.

A vector space is the minimal structure making that work. "Vector" stops meaning *arrow* and starts meaning **anything that behaves like one**.

## 2. The definition

A **vector space** over the real numbers is a set $V$ with an addition and a scalar multiplication, satisfying:

**Closure** — the two that do the real work:

1. $\mathbf{u} + \mathbf{v} \in V$ for all $\mathbf{u}, \mathbf{v} \in V$
2. $k\mathbf{v} \in V$ for all real $k$ and $\mathbf{v} \in V$

**The arithmetic** — the ones that are almost always obvious:

3. $\mathbf{u}+\mathbf{v} = \mathbf{v}+\mathbf{u}$ and $(\mathbf{u}+\mathbf{v})+\mathbf{w} = \mathbf{u}+(\mathbf{v}+\mathbf{w})$
4. There is a zero vector with $\mathbf{v} + \mathbf{0} = \mathbf{v}$
5. Every $\mathbf{v}$ has a negative with $\mathbf{v} + (-\mathbf{v}) = \mathbf{0}$
6. $k(\mathbf{u}+\mathbf{v}) = k\mathbf{u}+k\mathbf{v}$, $(k+m)\mathbf{v} = k\mathbf{v}+m\mathbf{v}$, $k(m\mathbf{v}) = (km)\mathbf{v}$, $1\mathbf{v} = \mathbf{v}$

In practice, axioms 3–6 are inherited from ordinary arithmetic and need no checking. **The two closure axioms are what you actually verify**, and a failure is nearly always there.

### Subspaces

A **subspace** is a subset that is itself a vector space. The test is short:

> $W \subseteq V$ is a subspace if it contains $\mathbf{0}$, and is closed under addition and scalar multiplication.

Containing $\mathbf{0}$ is the quickest disqualifier. A line through the origin in $\mathbb{R}^2$ is a subspace; the same line shifted upwards is **not** — it misses the origin, and adding two of its points lands off the line. Block 1 of the lab checks both.

| Term | Plain-English definition |
| :--- | :--- |
| **Span** | All linear combinations of a set of vectors |
| **Linearly independent** | No vector in the set is a combination of the others |
| **Basis** | An independent set that spans the whole space |
| **Dimension** | The number of vectors in a basis — the same for every basis |
| **Column space** | The span of a matrix's columns; everything $A\mathbf{x}$ can equal |
| **Null space** (kernel) | Every $\mathbf{x}$ with $A\mathbf{x} = \mathbf{0}$ |
| **Rank** | The dimension of the column space — the number of pivots |
| **Nullity** | The dimension of the null space — the number of free variables |

## 3. Independence, basis, dimension

Vectors $\mathbf{v}_1,\dots,\mathbf{v}_k$ are **linearly independent** when the only solution of

$$
c_1\mathbf{v}_1 + \cdots + c_k\mathbf{v}_k = \mathbf{0}
$$

is $c_1 = \cdots = c_k = 0$. Any other solution exhibits one vector as a combination of the others, so it carries no new direction.

That is a homogeneous system, so **testing independence is running Gaussian elimination** — put the vectors in a matrix, eliminate, and count pivots. If every vector gives a pivot, they are independent.

A **basis** is independent *and* spanning: enough vectors to reach everything, with none wasted. Every vector then has **exactly one** representation in terms of that basis, and those coefficients are its **coordinates**.

The crucial fact, which needs proof but is intuitive: **every basis of a given space has the same number of vectors.** That number is the **dimension**, and it is well defined because of this.

## 4. The two spaces of a matrix

Every $m\times n$ matrix comes with two subspaces:

- **Column space** $C(A) \subseteq \mathbb{R}^m$ — the span of the columns. Since $A\mathbf{x}$ is a combination of the columns with weights $\mathbf{x}$, this is precisely the set of $\mathbf{b}$ for which $A\mathbf{x} = \mathbf{b}$ has a solution.
- **Null space** $N(A) \subseteq \mathbb{R}^n$ — all $\mathbf{x}$ with $A\mathbf{x} = \mathbf{0}$. It is never empty: $\mathbf{x} = \mathbf{0}$ always works, which is why a homogeneous system is never inconsistent.

**Rank–nullity theorem:**

$$
\operatorname{rank}(A) + \operatorname{nullity}(A) = n \quad (\text{the number of \textbf{columns}})
$$

The proof is elimination, read carefully: each column either gets a pivot or does not. Pivot columns contribute to the rank; the rest are free variables, and each free variable contributes one dimension to the null space. Every column is counted exactly once.

This is the [[03-systems-of-linear-equations/01-gaussian-elimination|three-outcomes table]] restated: the solution set of $A\mathbf{x} = \mathbf{b}$, when non-empty, is a shifted copy of the null space, so its dimension is the nullity.

> [!TIP]
> **Predict before running the lab.** A $3\times4$ matrix has three rows and four columns. What is the largest its rank could possibly be? Therefore what is the **smallest** its nullity could be — and what does that tell you about whether $A\mathbf{x} = \mathbf{0}$ can have only the zero solution? Decide before opening the answers.

## 5. The abstraction earning its keep

Polynomials of degree at most $2$ form a vector space. Take the set $\{1, x, x^2\}$:

- **Spanning:** every such polynomial is $a\cdot1 + b\cdot x + c\cdot x^2$.
- **Independent:** if $a + bx + cx^2$ is the zero polynomial, then $a = b = c = 0$.

So it is a **basis**, and the space is **3-dimensional** — which means it is structurally the same as $\mathbb{R}^3$, with $a + bx + cx^2$ corresponding to $(a, b, c)$.

That correspondence is not a metaphor. Differentiation sends polynomials to polynomials, respects addition and scaling, and is therefore a **linear map** with a matrix in these coordinates. Once written down, questions about calculus become questions about a $3\times3$ matrix — its null space is the constants, which is exactly "the functions whose derivative is zero". Block 5 does this explicitly, and [[05-linear-transformations/01-linear-transformations|linear transformations]] takes it further.

## Worked example — runnable

**Runnable example:** save as `vector_spaces.py` in any empty directory and run `python3 vector_spaces.py`. Standard library only; writes no files.

```python
"""Subspaces, independence, bases, and rank-nullity - in exact arithmetic."""
from fractions import Fraction


def rref(matrix):
    """Reduced row echelon form, exactly. Returns (rref, pivot column indices)."""
    M = [[Fraction(v) for v in row] for row in matrix]
    rows, cols = len(M), len(M[0])
    pivots, r = [], 0
    for c in range(cols):
        p = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        M[r] = [v / M[r][c] for v in M[r]]          # scale the pivot to 1
        for i in range(rows):                        # clear the column, above and below
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
        if r == rows:
            break
    return M, pivots


def rank(matrix):
    return len(rref(matrix)[1])


def is_independent(vectors):
    """Independent exactly when every vector contributes a pivot."""
    as_columns = [[v[i] for v in vectors] for i in range(len(vectors[0]))]
    return rank(as_columns) == len(vectors)


def column_space_basis(A):
    """The ORIGINAL columns at the pivot positions - not the rref columns."""
    _, pivots = rref(A)
    return [[row[c] for row in A] for c in pivots]


def null_space_basis(A):
    """One basis vector per free column."""
    R, pivots = rref(A)
    cols = len(A[0])
    free = [c for c in range(cols) if c not in pivots]
    basis = []
    for f in free:
        v = [Fraction(0)] * cols
        v[f] = Fraction(1)
        for r, p in enumerate(pivots):
            v[p] = -R[r][f]                          # from the rref row: x_p + R[r][f]*x_f = 0
        basis.append(v)
    return basis


def matvec(A, x):
    return [sum(Fraction(A[i][j]) * x[j] for j in range(len(x))) for i in range(len(A))]


if __name__ == "__main__":
    print("Block 1 - the subspace test, where the zero vector does the work")
    checks = [
        ("line y = 2x through origin", lambda p: p[1] == 2 * p[0]),
        ("line y = 2x + 1 (shifted)",  lambda p: p[1] == 2 * p[0] + 1),
        ("first quadrant x,y >= 0",    lambda p: p[0] >= 0 and p[1] >= 0),
        ("the whole plane",            lambda p: True),
    ]
    for label, member in checks:
        has_zero = member((0, 0))
        # closure under scaling: try -1 on a member
        sample = next(p for p in [(1, 2), (1, 3), (2, 4), (3, 6), (1, 1)] if member(p))
        neg = (-sample[0], -sample[1])
        closed_scale = member(neg)
        verdict = "subspace" if (has_zero and closed_scale) else "NOT a subspace"
        why = "" if verdict == "subspace" else (
            " (misses the origin)" if not has_zero else f" (contains {sample} but not {neg})")
        print(f"  {label:28} {verdict}{why}")
    assert not checks[1][1]((0, 0))          # shifted line misses the origin
    assert checks[2][1]((1, 1)) and not checks[2][1]((-1, -1))   # quadrant not closed

    print()
    print("Block 2 - independence is just counting pivots")
    sets = [
        ("(1,0,0) (0,1,0) (0,0,1)", [(1, 0, 0), (0, 1, 0), (0, 0, 1)]),
        ("(1,2) (2,4)",             [(1, 2), (2, 4)]),
        ("(1,1,0) (1,0,1) (0,1,1)", [(1, 1, 0), (1, 0, 1), (0, 1, 1)]),
        ("(1,1,0) (2,2,0) (0,0,1)", [(1, 1, 0), (2, 2, 0), (0, 0, 1)]),
        ("four vectors in R^3",     [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)]),
    ]
    for label, vs in sets:
        ind = is_independent(vs)
        print(f"  {label:28} {'independent' if ind else 'DEPENDENT':12}"
              f" ({len(vs)} vectors in R^{len(vs[0])})")
    assert is_independent([(1, 0, 0), (0, 1, 0), (0, 0, 1)])
    assert not is_independent([(1, 2), (2, 4)])                  # second is twice the first
    assert not is_independent([(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)])
    print("  four vectors in R^3 can never be independent: dimension caps the count")

    print()
    print("Block 3 - the two spaces of a matrix")
    A = [[1, 2, 0, 1],
         [0, 0, 1, 3],
         [1, 2, 1, 4]]                      # row 3 = row 1 + row 2
    R, pivots = rref(A)
    print("  A =")
    for row in A:
        print("      " + str(row))
    print("  rref(A) =")
    for row in R:
        print("      [" + "  ".join(f"{str(v):>4}" for v in row) + "]")
    print(f"  pivot columns: {pivots}   rank = {len(pivots)}")

    cbasis = column_space_basis(A)
    print(f"  column space basis (original columns {pivots}): {cbasis}")
    nbasis = null_space_basis(A)
    print(f"  null space basis:")
    for v in nbasis:
        print(f"      {[str(x) for x in v]}   ->  A v = {[str(x) for x in matvec(A, v)]}")
        assert all(x == 0 for x in matvec(A, v)), "null space vectors must map to zero"
    print("  every null space basis vector maps to the zero vector, as required")

    print()
    print("Block 4 - rank + nullity = number of COLUMNS")
    mats = [
        ("the A above (3x4)", A),
        ("identity 3x3",      [[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
        ("all zeros 2x5",     [[0] * 5 for _ in range(2)]),
        ("2x3 rank 2",        [[1, 0, 2], [0, 1, 3]]),
        ("4x2 rank 2",        [[1, 0], [0, 1], [1, 1], [2, 3]]),
    ]
    print("      matrix              cols   rank   nullity   sum")
    for label, M in mats:
        cols = len(M[0])
        rk = rank(M)
        nul = len(null_space_basis(M))
        print(f"  {label:22} {cols:4} {rk:6} {nul:9} {rk + nul:5}")
        assert rk + nul == cols, (label, rk, nul, cols)
    print("  the sum is the column count every time - that is the theorem")

    print()
    print("Block 5 - polynomials are vectors, and differentiation is a matrix")
    # a + b x + c x^2  <->  coordinates (a, b, c) in the basis {1, x, x^2}
    def poly_str(v):
        parts = []
        for power, coeff in enumerate(v):
            if coeff == 0:
                continue
            term = "1" if power == 0 else ("x" if power == 1 else f"x^{power}")
            parts.append(f"{coeff}*{term}" if coeff != 1 or power == 0 else term)
        return " + ".join(parts) if parts else "0"

    D = [[0, 1, 0],       # d/dx sends (a,b,c) -> (b, 2c, 0)
         [0, 0, 2],
         [0, 0, 0]]
    for coords in [[3, 2, -1], [0, 0, 5], [7, 0, 0]]:
        image = matvec(D, [Fraction(c) for c in coords])
        print(f"  d/dx [{poly_str(coords):>14}] = {poly_str([int(v) for v in image])}")
    # differentiating 3 + 2x - x^2 gives 2 - 2x
    assert [int(v) for v in matvec(D, [Fraction(c) for c in [3, 2, -1]])] == [2, -2, 0]

    print(f"  rank(D) = {rank(D)}, nullity(D) = {len(null_space_basis(D))}")
    print(f"  null space basis: {[[str(x) for x in v] for v in null_space_basis(D)]}")
    print("  the null space is spanned by (1,0,0) = the constant polynomial 1:")
    print("  'the functions whose derivative is zero are the constants', as a matrix fact")
    assert rank(D) + len(null_space_basis(D)) == 3
    assert null_space_basis(D) == [[Fraction(1), Fraction(0), Fraction(0)]]

    print()
    print("vector_spaces: passed")
```

Expected output:

```
Block 1 - the subspace test, where the zero vector does the work
  line y = 2x through origin   subspace
  line y = 2x + 1 (shifted)    NOT a subspace (misses the origin)
  first quadrant x,y >= 0      NOT a subspace (contains (1, 2) but not (-1, -2))
  the whole plane              subspace

Block 2 - independence is just counting pivots
  (1,0,0) (0,1,0) (0,0,1)      independent  (3 vectors in R^3)
  (1,2) (2,4)                  DEPENDENT    (2 vectors in R^2)
  (1,1,0) (1,0,1) (0,1,1)      independent  (3 vectors in R^3)
  (1,1,0) (2,2,0) (0,0,1)      DEPENDENT    (3 vectors in R^3)
  four vectors in R^3          DEPENDENT    (4 vectors in R^3)
  four vectors in R^3 can never be independent: dimension caps the count

Block 3 - the two spaces of a matrix
  A =
      [1, 2, 0, 1]
      [0, 0, 1, 3]
      [1, 2, 1, 4]
  rref(A) =
      [   1     2     0     1]
      [   0     0     1     3]
      [   0     0     0     0]
  pivot columns: [0, 2]   rank = 2
  column space basis (original columns [0, 2]): [[1, 0, 1], [0, 1, 1]]
  null space basis:
      ['-2', '1', '0', '0']   ->  A v = ['0', '0', '0']
      ['-1', '0', '-3', '1']   ->  A v = ['0', '0', '0']
  every null space basis vector maps to the zero vector, as required

Block 4 - rank + nullity = number of COLUMNS
      matrix              cols   rank   nullity   sum
  the A above (3x4)         4      2         2     4
  identity 3x3              3      3         0     3
  all zeros 2x5             5      0         5     5
  2x3 rank 2                3      2         1     3
  4x2 rank 2                2      2         0     2
  the sum is the column count every time - that is the theorem

Block 5 - polynomials are vectors, and differentiation is a matrix
  d/dx [3*1 + 2*x + -1*x^2] = 2*1 + -2*x
  d/dx [         5*x^2] = 10*x
  d/dx [           7*1] = 0
  rank(D) = 2, nullity(D) = 1
  null space basis: [['1', '0', '0']]
  the null space is spanned by (1,0,0) = the constant polynomial 1:
  'the functions whose derivative is zero are the constants', as a matrix fact

vector_spaces: passed
```

Block 5 is the abstraction paying off. Differentiation — an operation from calculus — is a $3\times3$ matrix, and "the only functions with zero derivative are the constants" is its null space, computed by the same elimination used on everything else.

## Common pitfalls and traps

- **Forgetting to check that $\mathbf{0}$ is in the set.** It is the fastest disqualifier, and a set missing the origin can never be a subspace no matter how linear it looks.
- **Taking the rref columns as a basis for the column space.** Row operations **change** the column space; they preserve only which columns are independent. Take the **original** columns at the pivot positions, as the lab does.
- **Confusing the row space with the column space.** They have the same dimension — that is why "rank" is unambiguous — but they live in different spaces, $\mathbb{R}^n$ and $\mathbb{R}^m$.
- **Applying rank–nullity with the row count.** It is the number of **columns**. For a $3\times4$ matrix the sum is $4$, not $3$.
- **Assuming more vectors means more span.** Any set of more than $n$ vectors in an $n$-dimensional space is automatically dependent. The extra ones add nothing.
- **Testing independence in floating point.** "Is this pivot zero?" cannot be answered reliably in floats. The lab uses `Fraction` throughout for exactly this reason; a numerical version needs the SVD and a tolerance, not an equality test.

## Check your understanding

1. Is the set of vectors $(x, y)$ with $x + y = 0$ a subspace of $\mathbb{R}^2$? What about $x + y = 1$?
2. Are $(1, 2, 3)$, $(2, 4, 6)$ and $(1, 0, 0)$ independent?
3. A $5\times7$ matrix has rank 4. What is its nullity?
4. What is the dimension of the space of $2\times3$ matrices? Give a basis.
5. Why is $A\mathbf{x} = \mathbf{0}$ never inconsistent, and what does that mean about the null space?

<details><summary>Answers — open only after an attempt</summary>

1. $x + y = 0$ **is** a subspace: it contains $(0,0)$, and if $x_1+y_1 = 0$ and $x_2+y_2=0$ then their sum and any scalar multiple also satisfy it. $x + y = 1$ is **not**: it fails at the origin, since $0 + 0 \neq 1$.
2. **No.** $(2,4,6) = 2(1,2,3)$, so the first two are already dependent — the third is irrelevant.
3. Rank–nullity uses the **column** count: $4 + \text{nullity} = 7$, so nullity $= 3$.
4. **6.** A basis is the six matrices with a single $1$ and zeros elsewhere. The space is structurally $\mathbb{R}^6$.
5. Because $\mathbf{x} = \mathbf{0}$ always satisfies it. So the null space is never empty — it always contains at least the zero vector, and is therefore always a genuine subspace (possibly the trivial one, $\{\mathbf{0}\}$, when the nullity is zero).

**And the prediction from section 4:** rank cannot exceed either dimension, so for a $3\times4$ matrix the maximum rank is $3$. By rank–nullity, nullity $= 4 - \text{rank} \ge 4 - 3 = 1$. So the null space is **always at least 1-dimensional**, meaning $A\mathbf{x} = \mathbf{0}$ *always* has a non-zero solution. More generally, a homogeneous system with more unknowns than equations always has infinitely many solutions.
</details>

## Practice — independent task

Implement `coordinates(vector, basis)` returning the coordinates of a vector with respect to a given basis — and prove those coordinates are unique.

1. Set it up as a linear system: solving $c_1\mathbf{b}_1 + \cdots + c_n\mathbf{b}_n = \mathbf{v}$ means solving $B\mathbf{c} = \mathbf{v}$ with the basis vectors as columns of $B$.
2. **Reject inputs that are not a basis** — if the vectors are dependent, or do not span, say which and refuse. Use rank to decide.
3. Verify round-tripping: rebuild the vector from its coordinates and check it matches exactly. Use `Fraction`, so "exactly" means exactly.
4. Demonstrate that coordinates depend on the basis: express the same vector in two different bases of $\mathbb{R}^3$ and show the coordinate lists differ while the vector does not.
5. **Prove uniqueness in a comment**, and back it with code: show that if two coordinate lists represented the same vector, their difference would be a non-zero element of the null space of $B$ — impossible when the columns are independent.

**Edge cases:** the zero vector (coordinates all zero, in every basis); a basis given in a different order (coordinates permute); a vector outside the span, when the basis spans a proper subspace.

**Done when:** your round-trip is exact for at least five vectors in three different bases, your rejection path fires correctly for a dependent set, and your step-5 argument is written out rather than asserted.

## Tradeoffs, limits and extensions

**Exact versus numerical rank.** Everything here uses `Fraction`, so ranks are exact. Real data is not exact, and "is this pivot zero?" becomes "is it smaller than the noise?" — a question with no clean answer. The standard tool is the **singular value decomposition**, which produces singular values whose magnitudes let you set a principled threshold. Numerical rank is a judgement, not a fact.

**Infinite-dimensional spaces behave differently.** Continuous functions on $[0,1]$ form a vector space, but it has no finite basis. Much of the finite-dimensional theory then fails or needs heavy repair; the subject that does the repairing is functional analysis, and it underlies Fourier series — where "expressing a function in a basis" becomes an infinite sum needing a convergence argument.

**Other scalar fields.** Nothing here used a property of real numbers beyond ordinary arithmetic, so the theory works over the rationals, the complex numbers, or the two-element field $\{0, 1\}$. That last one is not a curiosity: linear algebra over $\mathbb{F}_2$ is exactly what [[06-error-correcting-codes|error-correcting codes]] are built from, and the null space of a parity-check matrix is the set of valid codewords.

## Before moving on

You are done with this lesson when you can:

- Check the subspace conditions and spot the zero-vector failure immediately.
- Test independence by elimination and extract a basis and a dimension.
- Compute both a column space basis and a null space basis, and say which space each lives in.
- State rank–nullity with the right count, and use it to predict a solution set's dimension.

**Recap for later lookup:** a vector space is a set closed under addition and scalar multiplication with the usual arithmetic; a subspace must contain $\mathbf{0}$; independence means the only vanishing combination is trivial; a basis is independent and spanning, and all bases have the same size — the dimension; $C(A)$ is the span of the columns, $N(A)$ is $\{\mathbf{x} : A\mathbf{x} = \mathbf{0}\}$; **rank + nullity = number of columns**; use the *original* columns at pivot positions for a column space basis.

**Next:** [[05-linear-transformations/01-linear-transformations|Linear Transformations]] — why a matrix is a function, and why that makes the multiplication rule inevitable.

## Related

- [[03-systems-of-linear-equations/01-gaussian-elimination|Systems of Linear Equations]] — the elimination every computation here runs on
- [[05-linear-transformations/01-linear-transformations|Linear Transformations]] — kernel and image are the null and column spaces
- [[06-eigenvalues/01-eigenvalues-and-eigenvectors|Eigenvalues]] — where dimension arguments do the heavy lifting
- **Abstract Algebra** *(reserved)* — vector spaces as one algebraic structure among many
