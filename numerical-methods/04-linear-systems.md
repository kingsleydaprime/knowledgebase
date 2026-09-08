# Linear Systems

**[Intermediate → Advanced]** — Solving $Ax = b$. The most-used algorithm in scientific computing, and the one where conditioning bites hardest.

## Why this note matters most

**Almost everything reduces to a linear solve:**

| Problem | Reduces to |
|---|---|
| [[foundations/numerical-methods/03-root-finding\|Newton's method]] | $J\Delta x = -F$ each iteration |
| [[engineering/01-continuum-mechanics/13-computational-methods-and-fem\|FEM]] | $Ku = f$ — often millions of unknowns |
| [[foundations/numerical-methods/09-partial-differential-equations\|Implicit PDE solvers]] | a linear solve per time step |
| Least squares / regression | the normal equations |
| [[robotics/11-state-estimation-and-filtering\|Kalman filter]] | a solve in the gain computation |
| [[ai-ml/00-foundations/03-mathematics/04-optimization\|Second-order optimisation]] | $H\Delta x = -\nabla f$ |

**If you optimise one thing in a scientific code, it's usually the linear solve.**

## Never invert the matrix

> **The single most important practical rule in this domain:**
>
> $$x = A^{-1}b \quad\text{is how you *write* it}$$
> $$\text{solve}(A, b) \quad\text{is how you *compute* it}$$

**Computing $A^{-1}$ and multiplying is:**

**~3× more expensive** — inversion is $O(n^3)$ with a larger constant than a factor-and-solve.

**Less accurate** — more operations, more rounding, and the explicit inverse can be catastrophically inaccurate for ill-conditioned $A$.

**Destroys sparsity** — **the inverse of a sparse matrix is generally dense.** A tridiagonal $10^6\times10^6$ matrix is cheap to factor and its inverse would not fit in memory.

**In code:** `numpy.linalg.solve(A, b)`, **not** `inv(A) @ b`. `scipy.linalg.solve_triangular`, `cho_solve`, `lu_solve`. MATLAB's `A\b`. **The only legitimate uses of an explicit inverse are when you genuinely need the entries** — a covariance matrix's inverse for a statistical quantity, for instance.

## LU decomposition

**Gaussian elimination, recorded.**

$$PA = LU$$

with $L$ unit lower triangular, $U$ upper triangular, $P$ a permutation.

**Then solving is two cheap triangular solves:**

```
Ly = Pb     forward substitution   O(n²)
Ux = y      back substitution      O(n²)
```

**Cost:** factorisation $O(\frac{2}{3}n^3)$, each solve $O(n^2)$.

> **Which is why you factor once and solve many times.** With 100 right-hand sides, factor-then-solve is ~100× faster than solving from scratch each time. **This comes up constantly** — implicit time-stepping reuses the same $A$ every step, and re-factorising it each time is a common and expensive mistake.

### Pivoting

**Partial pivoting** swaps rows to put the largest available entry on the diagonal.

**Without it, Gaussian elimination is unstable.** The classic demonstration:

$$\begin{bmatrix}10^{-20} & 1\\ 1 & 1\end{bmatrix}$$

**Eliminating with the tiny pivot multiplies the second row by $10^{20}$**, and the original entry is lost to rounding entirely. **The computed answer is wrong by 100%.** Swap the rows first and it's fine.

> **Partial pivoting is why LAPACK's `dgesv` is backward stable in practice and your textbook implementation isn't.** It costs almost nothing — $O(n^2)$ comparisons against $O(n^3)$ arithmetic — and it's not optional. → [[foundations/numerical-methods/02-floating-point-and-error|Backward stability]]

**Complete pivoting** (rows and columns) is more stable and rarely worth the cost.

## Specialised factorisations

**Exploit structure — often a 2× or better win, and better stability.**

**Cholesky** — for symmetric positive definite $A$:

$$A = LL^T$$

**Half the work ($\frac{1}{3}n^3$), half the storage, no pivoting needed**, and unconditionally stable. **Use it whenever $A$ is SPD** — covariance matrices, FEM stiffness matrices, and the normal equations all are.

**Bonus: Cholesky failing is a *test*.** If the factorisation breaks down, $A$ isn't positive definite — which is exactly how you check that a covariance matrix is valid or that a Hessian is at a minimum rather than a saddle.

**QR** — $A = QR$ with $Q$ orthogonal, $R$ upper triangular.

**More expensive than LU ($\frac{4}{3}n^3$) and more stable**, because orthogonal transformations don't amplify error — $\kappa(Q) = 1$. **The right tool for least squares.**

**SVD** — $A = U\Sigma V^T$.

**The most expensive and the most informative.** Gives you rank, condition number, null space, pseudoinverse, and the best low-rank approximation. **When a problem is rank-deficient or nearly so, SVD is what tells you and what handles it.** → [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|Linear Algebra]]

## Conditioning

$$\kappa(A) = \|A\|\,\|A^{-1}\| = \frac{\sigma_{max}}{\sigma_{min}}$$

**The error bound:**

$$\frac{\|\delta x\|}{\|x\|} \leq \kappa(A)\frac{\|\delta b\|}{\|b\|}$$

> **Rule of thumb: $\kappa = 10^k$ means you lose about $k$ digits.**
>
> With a `double`'s 16 digits: $\kappa = 10^8$ leaves you 8 good digits. **$\kappa = 10^{16}$ leaves you none** — the computed answer is uncorrelated with the true one.

**This is a property of the problem, not the algorithm.** A perfectly stable solver on an ill-conditioned system still gives you a bad answer, **and that's not a bug to fix.** → [[foundations/numerical-methods/01-why-numerical-methods|Conditioning vs stability]]

**What causes ill-conditioning:**

**Badly scaled variables** — mixing metres and micrometres. **Fix by non-dimensionalising**, and this is the most common and most fixable cause.

**Nearly-dependent columns** — two nearly-identical features in a regression. **This is multicollinearity**, and it's why regularisation exists.

**The normal equations.** Solving least squares via $A^TAx = A^Tb$ **squares the condition number**: $\kappa(A^TA) = \kappa(A)^2$. **Use QR or SVD instead** — this is the single most common numerical mistake in statistics and ML code, and it silently halves your accuracy.

**Estimating it:** `numpy.linalg.cond(A)`, or `LAPACK`'s condition estimator which is $O(n^2)$ rather than requiring a full SVD.

**A residual is not an error.** A small $\|Ax - b\|$ does **not** imply $x$ is close to the true solution when $\kappa$ is large. **Check the condition number, not just the residual.**

## Sparse systems

**Most large real systems are sparse** — FEM, circuit simulation, PDEs, graphs. A million unknowns with ten nonzeros per row.

**Dense storage would be $10^{12}$ entries. Sparse is $10^7$.**

**Formats:** CSR (row-wise, good for $Ax$), CSC (column-wise), COO (easy to build, convert before computing).

### Direct sparse solvers

**Sparse LU or Cholesky, with reordering.**

**The problem is fill-in** — factorisation creates nonzeros where $A$ had none, and a bad ordering can fill the matrix completely.

**Reordering algorithms** — AMD (approximate minimum degree), METIS nested dissection — **permute rows and columns to minimise fill.** The difference between a good and bad ordering is frequently orders of magnitude in memory and time. **This is what makes sparse direct solvers viable**, and it's why UMFPACK/CHOLMOD/MUMPS are non-trivial software.

### Iterative solvers

**For very large systems where even sparse factorisation is too expensive.**

**They only need $Ax$ products** — never the matrix explicitly, which enables matrix-free methods.

| Method | For |
|---|---|
| **Conjugate Gradient (CG)** | **symmetric positive definite** — the workhorse |
| MINRES | symmetric indefinite |
| **GMRES** | general nonsymmetric |
| BiCGSTAB | nonsymmetric, cheaper than GMRES |

**CG converges in at most $n$ steps in exact arithmetic**, and in practice in far fewer — with error contracting like:

$$\left(\frac{\sqrt{\kappa}-1}{\sqrt{\kappa}+1}\right)^k$$

**Note the $\sqrt{\kappa}$** — CG's convergence depends on the *square root* of the condition number, which is much better than it sounds.

**Preconditioning is what makes iterative methods work.** Solve $M^{-1}Ax = M^{-1}b$ where $M \approx A$ but is cheap to invert:

- **Jacobi** — diagonal. Trivial, weak
- **Incomplete LU/Cholesky (ILU/IC)** — factorise approximately, dropping small fill
- **Multigrid** — **$O(n)$ for elliptic PDEs, which is optimal.** The best preconditioner there is for the right problem
- **Domain decomposition** — parallel-friendly

> **An unpreconditioned iterative solver on a real problem usually doesn't converge in useful time.** **The preconditioner is not an optimisation — it's the algorithm.** Most of the research effort in this area is about preconditioners, not the Krylov methods themselves.

## Choosing

```
Is A small (n < ~1000) and dense?
├── symmetric positive definite? → CHOLESKY
├── general?                     → LU with partial pivoting
├── least squares?               → QR  (never the normal equations)
└── rank-deficient / uncertain?  → SVD

Is A large and sparse?
├── moderately large, direct feasible? → sparse Cholesky/LU + reordering
└── very large?                        → CG (SPD) or GMRES + a preconditioner
```

## Practical notes

**Use LAPACK.** Directly, or through NumPy/SciPy/Eigen/Armadillo. **Forty years of numerical care that you will not reproduce.** Your hand-written elimination will be slower *and* less accurate.

**Factor once, solve many.** Cache the factorisation whenever $A$ is reused.

**Exploit structure.** Symmetric, positive definite, banded, triangular, Toeplitz — **each has a specialised routine that's substantially faster.** Telling the library about structure is free performance.

**Never form the normal equations** for least squares.

**Check $\kappa$** before trusting a result. And check the residual — but know it isn't sufficient.

**Scale your variables** to comparable magnitudes. It's the cheapest conditioning fix available.

**Watch memory on sparse direct solvers.** Fill-in can exceed RAM without warning; that's the signal to switch to iterative.

---

## Related
- [[foundations/numerical-methods/05-eigenvalues|Eigenvalues]] — the other big linear-algebra computation
- [[foundations/numerical-methods/09-partial-differential-equations|PDEs]] — where the huge sparse systems come from
- [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|Linear Algebra]] — the theory
- [[foundations/numerical-methods/README|Numerical methods map]]
