# Systems of Linear Equations

**[Intermediate]** — how software actually solves $A\mathbf{x} = \mathbf{b}$, and the one-line change that stops it from being catastrophically wrong.

## Before you start

- You can multiply matrices and compute a determinant — [[01-matrices-and-determinants|matrices and determinants]].
- You can solve two simultaneous equations by elimination — [[01-linear-equations|linear equations]].
- Helpful: planes in space, for the geometric picture — [[01-lines-and-planes|lines and planes]].

**What you will be able to do after this lesson:**

1. Carry out **Gaussian elimination** with back substitution, and state the row operations that are legal and why.
2. Classify a system as having one solution, none, or infinitely many — and say what each looks like geometrically.
3. Explain **partial pivoting**, and demonstrate a system where omitting it gives a completely wrong answer in floating point.
4. Compare the cost of elimination with Cramer's rule, and say why one of them is never used.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 4 is the one that matters — it is a correct algorithm returning a wrong answer.

---

## 1. Why this exists

[[01-matrices-and-determinants|The previous lesson]] ended by saying that $\mathbf{x} = A^{-1}\mathbf{b}$ and Cramer's rule are both the wrong way to solve a system. This lesson is the right way.

The reason matters. Computing an inverse is *more* work than solving the system, and it is less accurate — you would be solving $n$ systems to answer one. Cramer's rule is worse still: with cofactor determinants it is $O(n!)$, which is unusable past about $n = 12$.

Gaussian elimination is what everything actually uses — MATLAB's backslash, NumPy's `solve`, LAPACK, every circuit simulator and structural analysis package. It is the same elimination taught for two equations in two unknowns, made systematic. And it comes with a trap that only shows up in floating point, which is the real subject of section 4.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Coefficient matrix** $A$ | The grid of coefficients | The left-hand sides |
| **Augmented matrix** $[A \mid \mathbf{b}]$ | $A$ with $\mathbf{b}$ stuck on as an extra column | What you actually operate on |
| **Row operation** | Swap two rows; scale a row; add a multiple of one row to another | All three preserve the solution set |
| **Pivot** | The leading non-zero entry used to eliminate below it | One per row, moving right |
| **Row echelon form** | Staircase of zeros below the pivots | What elimination produces |
| **Back substitution** | Solving from the bottom row upwards | The second half of the algorithm |
| **Rank** | The number of pivots — independent equations | Fewer than $n$ means information is missing |
| **Consistent** | Having at least one solution | Inconsistent means none |
| **Free variable** | A column with no pivot | Each one gives a dimension of solutions |

## 3. The algorithm

**Forward elimination.** For each column in turn, use the pivot row to make every entry below the pivot zero:

$$
\text{row}_i \;\leftarrow\; \text{row}_i - \frac{a_{ik}}{a_{kk}}\,\text{row}_k
$$

**Back substitution.** The last row now involves one unknown; solve it. Substitute upwards.

The three row operations are legal because each is reversible and none changes the solution set: swapping equations changes nothing, scaling an equation by a non-zero constant changes nothing, and adding a multiple of one true equation to another gives another true equation.

**Worked example.**

$$
\begin{aligned}
2x + y - z &= 8\\
-3x - y + 2z &= -11\\
-2x + y + 2z &= -3
\end{aligned}
\qquad
\left[\begin{array}{ccc|c}
2 & 1 & -1 & 8\\
-3 & -1 & 2 & -11\\
-2 & 1 & 2 & -3
\end{array}\right]
$$

Eliminate below the first pivot ($2$): add $\tfrac32$ of row 1 to row 2, and add row 1 to row 3:

$$
\left[\begin{array}{ccc|c}
2 & 1 & -1 & 8\\
0 & 0.5 & 0.5 & 1\\
0 & 2 & 1 & 5
\end{array}\right]
$$

Eliminate below the second pivot ($0.5$): subtract $4\times$ row 2 from row 3:

$$
\left[\begin{array}{ccc|c}
2 & 1 & -1 & 8\\
0 & 0.5 & 0.5 & 1\\
0 & 0 & -1 & 1
\end{array}\right]
$$

Back substitute: $-z = 1$ so $z = -1$; then $0.5y + 0.5(-1) = 1$ so $y = 3$; then $2x + 3 + 1 = 8$ so $x = 2$.

## 4. The three outcomes

Each equation in three unknowns is a **plane**. Solving the system means finding where the planes meet — and there are exactly three possibilities:

| Outcome | Geometry | Sign in the echelon form |
| :--- | :--- | :--- |
| **Exactly one** solution | The planes meet at a point | $\operatorname{rank} A = \operatorname{rank}[A\mid\mathbf{b}] = n$ |
| **No** solution | No common point — parallel, or a triangular prism | A row $[\,0\ 0\ 0 \mid c\,]$ with $c \neq 0$ |
| **Infinitely many** | The planes share a line or a whole plane | $\operatorname{rank} A = \operatorname{rank}[A\mid\mathbf{b}] < n$ |

The row $[\,0\ 0\ 0 \mid c\,]$ reads "$0 = c$", which is false. That single row is how inconsistency announces itself.

When the ranks agree but fall short of $n$, the missing pivots are **free variables**: each can take any value, and the solution is a line, a plane, or higher. The number of free variables is $n - \operatorname{rank}A$, which is the rank–nullity theorem previewed — see [[04-vector-spaces/01-vector-spaces|vector spaces]].

> [!TIP]
> **Predict before section 5.** The system $\;10^{-18}x + y = 1,\; x + y = 2\;$ has the obvious solution $x \approx 1$, $y \approx 1$. Run elimination in your head using the first row as the pivot row: the multiplier is $10^{18}$. What happens to the entry $1 - 10^{18}$ in double precision, and what answer will you get for $x$? Decide before opening the answers.

## 5. Partial pivoting

The algorithm as stated divides by $a_{kk}$. Two things go wrong:

- If $a_{kk} = 0$, it divides by zero, even when the system is perfectly solvable — a swap fixes it.
- If $a_{kk}$ is merely **small**, the multiplier is huge, and adding a huge multiple of one row to another destroys the information in the second row. This is not division by zero; it is silent, and the answer is wrong.

**Partial pivoting** fixes both: before eliminating in column $k$, swap in the row whose entry in that column has the **largest absolute value**. That keeps every multiplier at most $1$, so nothing is amplified.

This is one line of code, and it is the difference between a textbook algorithm and a usable one. Block 4 of the lab runs the same system both ways.

**Cost.** Elimination is about $\tfrac{2}{3}n^3$ operations. Cramer's rule with cofactor determinants is $O(n!)$:

| $n$ | Elimination $\approx \tfrac23 n^3$ | Cramer (cofactor), $\approx n!$ |
| ---: | ---: | ---: |
| 5 | 83 | 120 |
| 10 | 666 | 3,628,800 |
| 15 | 2,250 | $1.3\times10^{12}$ |
| 20 | 5,333 | $2.4\times10^{18}$ |

At $n = 20$ the ratio is about $5\times10^{14}$. This is why one of them is a teaching device and the other is in every numerical library.

## Worked example — runnable

**Runnable example:** save as `gaussian.py` in any empty directory and run `python3 gaussian.py`. Standard library only; writes no files.

```python
"""Gaussian elimination, the three outcomes, and why pivoting is not optional."""
from fractions import Fraction

EPS = 1e-12


def eliminate(A, b, pivot=True, exact=False):
    """Forward elimination. Returns (echelon matrix, rhs, swap count)."""
    n = len(A)
    M = [[Fraction(v) if exact else float(v) for v in row] for row in A]
    r = [Fraction(v) if exact else float(v) for v in b]
    swaps = 0
    row = 0
    for col in range(len(M[0])):
        if pivot:
            # choose the row with the largest absolute entry in this column
            best = max(range(row, n), key=lambda i: abs(M[i][col]))
        else:
            # naive: keep the row you are on, and swap ONLY to avoid a literal zero.
            # A tiny-but-non-zero pivot is accepted, which is the whole problem.
            best = row if M[row][col] != 0 else \
                next((i for i in range(row, n) if M[i][col] != 0), row)
        if M[best][col] == 0:
            continue                        # no pivot in this column: a free variable
        if best != row:
            M[row], M[best] = M[best], M[row]
            r[row], r[best] = r[best], r[row]
            swaps += 1
        for i in range(row + 1, n):
            if M[i][col] != 0:
                factor = M[i][col] / M[row][col]
                for j in range(col, len(M[0])):
                    M[i][j] -= factor * M[row][j]
                r[i] -= factor * r[row]
        row += 1
        if row == n:
            break
    return M, r, swaps


def classify(A, b):
    """One solution, none, or infinitely many."""
    M, r, _ = eliminate(A, b, exact=True)
    n_unknowns = len(A[0])
    rank = sum(1 for i, row in enumerate(M) if any(v != 0 for v in row))
    rank_aug = sum(1 for i, row in enumerate(M) if any(v != 0 for v in row) or r[i] != 0)
    if rank_aug > rank:
        return "no solution", rank, rank_aug
    if rank < n_unknowns:
        return f"infinitely many ({n_unknowns - rank} free variable(s))", rank, rank_aug
    return "exactly one", rank, rank_aug


def solve(A, b, pivot=True):
    """Full solve for a square system with a unique solution."""
    M, r, _ = eliminate(A, b, pivot=pivot)
    n = len(M)
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = sum(M[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (r[i] - s) / M[i][i]
    return x


def residual(A, x, b):
    return max(abs(sum(A[i][j] * x[j] for j in range(len(x))) - b[i])
               for i in range(len(A)))


if __name__ == "__main__":
    print("Block 1 - the worked example from section 3")
    A = [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]]
    b = [8, -11, -3]
    x = solve(A, b)
    print(f"  solution: x = {[round(v, 9) for v in x]}   (expected [2, 3, -1])")
    print(f"  largest residual |Ax - b| = {residual(A, x, b):.2e}")
    assert all(abs(g - w) < 1e-9 for g, w in zip(x, [2, 3, -1]))

    print()
    print("Block 2 - the three outcomes")
    systems = [
        ("planes meet at a point", [[2, 1], [1, -1]], [5, 1]),
        ("parallel: no solution",  [[1, 1], [1, 1]], [1, 2]),
        ("same plane twice",       [[1, 1], [2, 2]], [1, 2]),
        ("3 planes, common line",  [[1, 1, 1], [2, 2, 2], [1, 0, -1]], [3, 6, 0]),
        ("3 planes, no point",     [[1, 1, 1], [1, 1, 1], [1, 0, -1]], [3, 4, 0]),
    ]
    for label, M, r in systems:
        kind, rank, rank_aug = classify(M, r)
        print(f"  {label:24} rank {rank}, rank[A|b] {rank_aug}  ->  {kind}")
    assert classify([[1, 1], [1, 1]], [1, 2])[0] == "no solution"
    assert classify([[2, 1], [1, -1]], [5, 1])[0] == "exactly one"
    assert "infinitely many" in classify([[1, 1], [2, 2]], [1, 2])[0]

    print()
    print("Block 3 - row operations do not change the solution set")
    A3 = [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]]
    M, r, swaps = eliminate(A3, b, exact=True)
    print("  echelon form (exact arithmetic):")
    for row, rhs in zip(M, r):
        print("      [" + "  ".join(f"{str(v):>6}" for v in row) + f"  |  {str(rhs):>6}]")
    print(f"  row swaps performed: {swaps}")

    print()
    print("Block 4 - the same system, with and without partial pivoting")
    EPSILON = 1e-18
    A4 = [[EPSILON, 1.0], [1.0, 1.0]]
    b4 = [1.0, 2.0]
    print(f"  system:  {EPSILON}*x + y = 1")
    print(f"                    x + y = 2")
    print("  the true solution is x = 1.000..., y = 1.000... to 18 decimal places")

    without = solve(A4, b4, pivot=False)
    withp = solve(A4, b4, pivot=True)
    print(f"    WITHOUT pivoting: x = {without[0]:.6f}, y = {without[1]:.6f}"
          f"   residual {residual(A4, without, b4):.3e}")
    print(f"    WITH    pivoting: x = {withp[0]:.6f}, y = {withp[1]:.6f}"
          f"   residual {residual(A4, withp, b4):.3e}")
    assert abs(withp[0] - 1.0) < 1e-9 and abs(withp[1] - 1.0) < 1e-9
    assert abs(without[0] - 1.0) > 0.5, "the unpivoted answer should be badly wrong"
    print("  the unpivoted x is wrong by 100%, with no error, warning or exception")
    print("  the multiplier was 1/1e-18 = 1e18, and 1 - 1e18 rounds to exactly -1e18,")
    print("  which throws away the '1' - the only place x's information lived")

    print()
    print("  it is not a special case - here it is across a range of epsilon:")
    print("      epsilon      x without pivoting    x with pivoting")
    for e in (1e-10, 1e-14, 1e-16, 1e-18, 1e-20):
        Ae = [[e, 1.0], [1.0, 1.0]]
        w = solve(Ae, [1.0, 2.0], pivot=False)[0]
        p = solve(Ae, [1.0, 2.0], pivot=True)[0]
        print(f"    {e:9.0e}    {w:18.10f}    {p:15.10f}")

    print()
    print("Block 5 - cost: why Cramer's rule is a teaching device")
    print("       n    elimination ~ (2/3)n^3        Cramer (cofactor) ~ n!")
    fact = 1
    for n in (5, 10, 15, 20):
        for k in range(2, n + 1):
            pass
        fact = 1
        for k in range(2, n + 1):
            fact *= k
        print(f"    {n:4}    {int(2 * n ** 3 / 3):>22,}    {fact:>26,}")

    print()
    print("gaussian: passed")
```

Expected output:

```
Block 1 - the worked example from section 3
  solution: x = [2.0, 3.0, -1.0]   (expected [2, 3, -1])
  largest residual |Ax - b| = 8.88e-16

Block 2 - the three outcomes
  planes meet at a point   rank 2, rank[A|b] 2  ->  exactly one
  parallel: no solution    rank 1, rank[A|b] 2  ->  no solution
  same plane twice         rank 1, rank[A|b] 1  ->  infinitely many (1 free variable(s))
  3 planes, common line    rank 2, rank[A|b] 2  ->  infinitely many (1 free variable(s))
  3 planes, no point       rank 2, rank[A|b] 3  ->  no solution

Block 3 - row operations do not change the solution set
  echelon form (exact arithmetic):
      [    -3      -1       2  |     -11]
      [     0     5/3     2/3  |    13/3]
      [     0       0     1/5  |    -1/5]
  row swaps performed: 2

Block 4 - the same system, with and without partial pivoting
  system:  1e-18*x + y = 1
                    x + y = 2
  the true solution is x = 1.000..., y = 1.000... to 18 decimal places
    WITHOUT pivoting: x = 0.000000, y = 1.000000   residual 1.000e+00
    WITH    pivoting: x = 1.000000, y = 1.000000   residual 0.000e+00
  the unpivoted x is wrong by 100%, with no error, warning or exception
  the multiplier was 1/1e-18 = 1e18, and 1 - 1e18 rounds to exactly -1e18,
  which throws away the '1' - the only place x's information lived

  it is not a special case - here it is across a range of epsilon:
      epsilon      x without pivoting    x with pivoting
        1e-10          1.0000000827       1.0000000001
        1e-14          0.9992007222       1.0000000000
        1e-16          2.2204460493       1.0000000000
        1e-18          0.0000000000       1.0000000000
        1e-20          0.0000000000       1.0000000000

Block 5 - cost: why Cramer's rule is a teaching device
       n    elimination ~ (2/3)n^3        Cramer (cofactor) ~ n!
       5                        83                           120
      10                       666                     3,628,800
      15                     2,250             1,307,674,368,000
      20                     5,333     2,432,902,008,176,640,000

gaussian: passed
```

Block 4 is the one to sit with. The algorithm is correct, the code has no bug, no exception is raised — and the answer is wrong by 100%. The only difference is which row was chosen as the pivot.

## Common pitfalls and traps

- **Omitting pivoting.** The lab is the argument. A textbook implementation without it is not a slightly worse implementation; it is one that silently returns wrong answers on ordinary inputs.
- **Testing a pivot for exact zero.** `if pivot == 0` is not enough — a pivot of $10^{-18}$ passes that test and destroys the answer. Pivot on the largest magnitude, always.
- **Computing $A^{-1}$ to solve one system.** It costs about three times as much as elimination and is less accurate. Solve directly.
- **Reading "no solution" as a bug.** Inconsistent systems are a legitimate outcome — an over-determined measurement set usually has none, which is why least-squares fitting exists.
- **Forgetting to apply operations to the right-hand side.** The augmented column is part of the row. Eliminating in $A$ but not in $\mathbf{b}$ silently changes the problem.
- **Using floating point to classify.** Deciding "is this pivot zero?" is undecidable in floating point. The lab's `classify` uses `Fraction` for exactly this reason, and gets exact ranks; the numerical solver uses floats and a tolerance.

## Check your understanding

1. Solve by elimination: $x + 2y = 7$, $3x - y = 7$.
2. What does a row $[\,0\ 0\ 0 \mid 5\,]$ in an echelon form tell you?
3. A system of 4 equations in 4 unknowns has rank 3, and the augmented matrix also has rank 3. How many solutions?
4. Why does partial pivoting choose the **largest** entry rather than the first non-zero one?
5. Three planes in space pairwise intersect in lines, but the three lines are parallel and distinct. How many solutions does the system have, and what is the tell-tale sign in the echelon form?

<details><summary>Answers — open only after an attempt</summary>

1. From the first, $x = 7 - 2y$. Substituting: $3(7-2y) - y = 7$, so $21 - 7y = 7$, $y = 2$, $x = 3$.
2. The system is **inconsistent** — that row reads $0 = 5$. There is no solution.
3. The ranks agree, so it is consistent; but rank $3 < 4$ unknowns, so there is $4 - 3 = 1$ free variable. **Infinitely many** solutions, forming a line.
4. Because the multiplier is $a_{ik}/a_{kk}$, and a small pivot makes it large. A large multiplier means adding a big multiple of one row to another, which swamps the second row's own entries and loses them to rounding. Choosing the largest available pivot keeps every multiplier at most $1$ in absolute value.
5. **No solution** — this is the "triangular prism" configuration, where each pair of planes meets but all three share no common point. In the echelon form it shows up as a row of zeros on the left with a non-zero right-hand side.

**And the prediction from section 4:** the multiplier is $10^{18}$, so row 2 becomes $1 - 10^{18}$, which in double precision rounds to exactly $-10^{18}$ — the $1$ is below the resolution of a number that size and is discarded. The right-hand side likewise becomes $-10^{18}$. So $y = 1$ exactly, and then $x = (1 - y)/10^{-18} = 0/10^{-18} = \mathbf{0}$ — wrong, since $x$ should be $1$. The lab confirms it.
</details>

## Practice — independent task

Implement `solve_general(A, b)` handling **any** system, not just square ones with unique solutions.

1. Reduce to **reduced** row echelon form (RREF): pivots equal to 1, and zeros above them as well as below.
2. Detect inconsistency and return `None`, distinguishing it clearly from "infinitely many".
3. When there are free variables, return the solution **set**: a particular solution plus a basis for the directions you can move in without leaving the solution set. Verify that adding any multiple of any of those directions still satisfies $A\mathbf{x} = \mathbf{b}$.
4. Assert the rank relation on every test: number of free variables $=$ (number of unknowns) $-$ rank.
5. Test on a **non-square** system: 2 equations in 4 unknowns (expect a 2-dimensional solution set), and 4 equations in 2 unknowns (expect inconsistency for generic data).

**Edge cases:** the all-zero matrix; a zero right-hand side (always consistent — why?); more equations than unknowns but still consistent; a column of all zeros.

**Done when:** step 3's verification passes for at least five under-determined systems, your rank relation holds in every case, and you can say why $A\mathbf{x} = \mathbf{0}$ is never inconsistent.

## Tradeoffs, limits and extensions

**LU decomposition is elimination, saved.** The row operations of forward elimination can be recorded as a lower-triangular matrix $L$, giving $A = LU$. Then solving $A\mathbf{x} = \mathbf{b}$ for a *new* $\mathbf{b}$ costs only $O(n^2)$ instead of $O(n^3)$ — the expensive part is done once. Any application solving repeatedly with the same matrix (a circuit at many time steps, a structure under many loads) uses this.

**Condition number, not determinant.** How much elimination amplifies input error is measured by $\kappa(A) = \lVert A\rVert\lVert A^{-1}\rVert$. A system with $\kappa = 10^{12}$ loses about twelve digits, whatever algorithm is used — that is a property of the *problem*, not the method. Pivoting protects against instability introduced by the algorithm; it cannot rescue an ill-conditioned system.

**Large sparse systems need different methods.** A finite-element mesh may have millions of unknowns, but each equation touches only a handful. Elimination fills in the zeros and exhausts memory. Iterative methods — conjugate gradient, GMRES — never form the matrix explicitly and are what large-scale simulation actually uses.

## Before moving on

You are done with this lesson when you can:

- Run elimination and back substitution by hand on a $3\times3$ system.
- Classify any system from its echelon form and say what it looks like geometrically.
- Explain partial pivoting, and reproduce a case where omitting it gives a wrong answer.
- Say why Cramer's rule and matrix inversion are not used in practice.

**Recap for later lookup:** three legal row operations — swap, scale, add a multiple; forward elimination to echelon form, then back substitution; a row $[\,0\cdots0\mid c\,]$ with $c\neq0$ means inconsistent; $\operatorname{rank}A = \operatorname{rank}[A\mid\mathbf{b}] = n$ means one solution, $< n$ means infinitely many with $n - \operatorname{rank}$ free variables; **always pivot on the largest available entry**; cost $\approx\frac23 n^3$.

**Next:** [[04-vector-spaces/01-vector-spaces|Vector Spaces]] — what "rank", "free variable" and "independent" actually mean.

## Related

- [[01-matrices-and-determinants|Matrices and Determinants]] — where $A\mathbf{x} = \mathbf{b}$ came from
- [[04-vector-spaces/01-vector-spaces|Vector Spaces]] — rank, null space, and the rank–nullity theorem
- [[01-lines-and-planes|Lines and Planes in Space]] — the geometry of the three outcomes
- [[mathematics/07-applied-and-computational/01-numerical-methods/index|numerical-methods/]] — conditioning and iterative solvers
