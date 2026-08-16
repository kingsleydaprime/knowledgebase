# Eigenvalues

**[Advanced]** — Computing $Av = \lambda v$ when the characteristic polynomial is useless, and why this is harder than solving a linear system.

## Why not the characteristic polynomial

**You were taught to solve $\det(A - \lambda I) = 0$.** Do not do this numerically.

**Two reasons, and the second is fatal:**

**Computing the determinant symbolically is $O(n!)$** by cofactor expansion.

**Polynomial roots are catastrophically ill-conditioned in the coefficients.** [[foundations/numerical-methods/01-why-numerical-methods|Wilkinson's polynomial]] is the demonstration — perturb a coefficient by one part in $10^7$ and roots move by 3.

> **So the direction is reversed in practice.** MATLAB's `roots()` and NumPy's `np.roots()` **build a companion matrix and compute its eigenvalues** — because eigenvalue algorithms are stable and polynomial root-finding from coefficients isn't. **The "hard" problem is used to solve the "easy" one.**

**And a structural fact worth knowing:** by Abel–Ruffini there's no closed form for polynomial roots above degree 4, so **every eigenvalue algorithm must be iterative.** There is no direct method, ever.

## Where eigenvalues matter

| Domain | Meaning |
|---|---|
| [[engineering/02-control-theory/08-state-space\|Control theory]] | **eigenvalues of $A$ *are* the poles** — stability |
| [[engineering/01-continuum-mechanics/02-index-notation-and-tensors\|Continuum mechanics]] | principal stresses and strains |
| Structural analysis | **vibration modes and natural frequencies** |
| [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README\|PCA]] | eigenvectors of the covariance matrix |
| [[foundations/discrete-math/07-graph-theory\|Graphs]] | PageRank is a dominant eigenvector; spectral clustering |
| Quantum mechanics | energy levels |
| [[foundations/numerical-methods/04-linear-systems\|Iterative solvers]] | convergence rates depend on the spectrum |

## The power method

**The simplest thing that works**, and it's the seed of everything else.

```
v ← random vector
repeat:
    v ← Av
    v ← v / ‖v‖          # normalise, or it overflows
λ ≈ vᵀAv                  # Rayleigh quotient
```

**Why it converges:** write $v_0$ in the eigenvector basis. Each multiplication by $A$ scales component $i$ by $\lambda_i$, so **the largest eigenvalue's component grows fastest** and eventually dominates.

$$\text{convergence rate} \propto \left|\frac{\lambda_2}{\lambda_1}\right|^k$$

**Fast when the top two eigenvalues are well separated, painfully slow when they're close.**

**Limitations:** finds only the dominant eigenvalue; fails if $|\lambda_1| = |\lambda_2|$; needs $v_0$ to have a component along $v_1$ (random almost always does).

> **PageRank is the power method**, on the web's link matrix. Google's original contribution was less the algorithm than making it work at that scale — plus the damping factor, which guarantees a unique dominant eigenvector. → [[foundations/discrete-math/07-graph-theory|Graph Theory]]

**Two useful variants:**

**Inverse iteration** — apply the power method to $(A - \sigma I)^{-1}$ (as a *solve*, not an inverse). **Converges to the eigenvalue nearest $\sigma$**, which is how you target a specific one.

**Rayleigh quotient iteration** — update $\sigma$ to the current Rayleigh quotient each step. **Cubic convergence** — spectacularly fast, at the cost of a fresh factorisation per iteration.

## The QR algorithm

**The workhorse**, and one of the top algorithms of the 20th century.

```
A₀ = A
repeat:
    Qₖ Rₖ = Aₖ          # QR factorise
    Aₖ₊₁ = Rₖ Qₖ         # multiply back in REVERSE order
```

**$A_{k+1}$ is similar to $A_k$** (same eigenvalues), and **it converges to upper triangular** — with the eigenvalues on the diagonal.

**That it works at all is remarkable**, and the connection is that it's implicitly doing the power method on all eigenvectors simultaneously.

**Practical QR needs three refinements**, and without them it's useless:

**Reduce to Hessenberg form first** (upper triangular plus one subdiagonal). **Drops each iteration from $O(n^3)$ to $O(n^2)$** — a one-time $O(n^3)$ cost that pays for itself immediately. For symmetric $A$ this becomes **tridiagonal**, and iterations are $O(n)$.

**Shifts.** Run QR on $A - \sigma I$ with $\sigma$ near an eigenvalue. **Turns linear convergence into cubic.** Wilkinson shifts are the standard choice.

**Deflation.** Once a subdiagonal entry is negligible, split the problem and continue on the smaller blocks.

**With all three: $O(n^3)$ total**, and it's what LAPACK's `dgeev`/`dsyev` do.

## Symmetric is much easier

**A genuinely important special case**, because so many real matrices are symmetric.

$$A = A^T \implies \text{real eigenvalues, orthogonal eigenvectors}$$

**Consequences:**

**Perfectly conditioned eigenvalues.** For symmetric matrices, $|\delta\lambda| \leq \|\delta A\|$ — **a perturbation moves eigenvalues by at most its own size.** No amplification at all.

**Roughly half the work**, and specialised algorithms: divide-and-conquer, MRRR, Jacobi.

**The Rayleigh quotient is accurate to second order** — an eigenvector accurate to $10^{-8}$ gives an eigenvalue accurate to $10^{-16}$.

> **Use `eigh` not `eig` when your matrix is symmetric.** Faster, more accurate, and it returns real values rather than complex ones with tiny imaginary parts you then have to explain. **`numpy.linalg.eigh`, `scipy.linalg.eigh`** — and this is a very common and free win, since covariance matrices, Hessians, stiffness matrices and Laplacians are all symmetric.

**Nonsymmetric eigenvalues can be badly conditioned.** The sensitivity is $1/|y^Tx|$ for left and right eigenvectors — **near-defective matrices (with nearly-parallel eigenvectors) have eigenvalues that move enormously under tiny perturbations.** This is a real hazard in control theory, where $A$ is generally nonsymmetric.

## Large sparse problems

**When $n$ is millions and you want a handful of eigenvalues**, dense QR is impossible.

**Krylov subspace methods** — build $\text{span}\{v, Av, A^2v, \ldots\}$ and extract approximate eigenvalues from it.

**Lanczos** (symmetric) and **Arnoldi** (general). **Only need matrix–vector products**, so matrix-free works.

**They converge to *extremal* eigenvalues first** — largest and smallest — which is usually exactly what you want: the dominant mode, the spectral gap, the lowest vibration frequency.

**For interior eigenvalues, use shift-and-invert** — apply the method to $(A-\sigma I)^{-1}$, which requires a factorisation but converges to eigenvalues near $\sigma$.

**Lanczos loses orthogonality in floating point**, producing spurious duplicate eigenvalues. **Practical implementations reorthogonalise**, which is most of what makes ARPACK non-trivial.

**In practice:** `scipy.sparse.linalg.eigsh` / `eigs` (ARPACK), SLEPc for large parallel problems.

## The SVD

**Related, more stable, and often what you actually want.**

$$A = U\Sigma V^T$$

**Always exists, for any matrix — rectangular, singular, anything.** Singular values are always real and non-negative.

**Computed via the eigendecomposition of $A^TA$ *conceptually*, but never that way in practice** — squaring the condition number, same mistake as the normal equations. **Golub–Kahan bidiagonalisation** then an implicit QR-like iteration is the real algorithm.

**Use SVD rather than eigendecomposition when:**

- $A$ isn't square or isn't symmetric
- You need **rank** — count singular values above a tolerance
- You need the **condition number** — $\sigma_{max}/\sigma_{min}$
- You need a **pseudoinverse** or a least-squares solution
- You want the **best low-rank approximation** — truncating the SVD is provably optimal (Eckart–Young), which is the basis of PCA, latent semantic analysis, and image compression

**Truncated/randomised SVD** — for a few components of a huge matrix, randomised methods (Halko–Martinsson–Tropp) are dramatically faster and come with probabilistic error bounds. **`sklearn`'s `TruncatedSVD` and `randomized_svd` use this**, and it's what makes PCA on large datasets feasible.

## Practical notes

**Use `eigh` for symmetric matrices.** The single most common free win here.

**Ask for only what you need.** `eigvals` skips eigenvectors and is much cheaper. `eigsh(k=10)` for the top 10 of a sparse matrix.

**Eigenvectors are only defined up to sign** (and up to rotation within a degenerate subspace). **Two libraries can return validly different eigenvectors** — don't test for equality, and normalise the sign yourself if you need reproducibility.

**Check for defectiveness** in nonsymmetric problems. Near-parallel eigenvectors mean ill-conditioned eigenvalues.

**Scale first.** Balancing (LAPACK does this automatically in `dgeev`) improves accuracy substantially for badly-scaled nonsymmetric matrices.

**For stability analysis you often don't need eigenvalues at all** — you need to know whether any lie in the right half plane, and [[engineering/02-control-theory/05-stability-and-root-locus|Routh–Hurwitz]] answers that without computing them.

**Beware the matrix exponential.** $e^{At}$ via eigendecomposition fails for defective matrices. **Use `scipy.linalg.expm`** (scaling and squaring with Padé) — the classic paper is titled *"Nineteen Dubious Ways to Compute the Exponential of a Matrix"*, which tells you how delicate it is. → [[engineering/02-control-theory/08-state-space|State Space]]

---

## Related
- [[foundations/numerical-methods/04-linear-systems|Linear Systems]] — used inside shift-and-invert
- [[engineering/02-control-theory/08-state-space|State Space]] — where eigenvalues are the poles
- [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|Linear Algebra]] — the theory
- [[foundations/numerical-methods/README|Numerical methods map]]
