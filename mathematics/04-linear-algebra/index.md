# Linear Algebra

**The mathematics of things that add and scale.** Written to [[COURSE-STANDARD|the course standard]]: prerequisites, observable outcomes, worked derivations, a runnable lab whose output was generated from an actual run, practice with hidden answers, and a demonstrable finish line.

This umbrella merges both curricula — SS3 matrices, determinants and vectors from the [[ss1-ss3-course-outline|NERDC outline]], and the Year 1–2 [[uni-math-course-outline|university track]] — so each subject appears once, secondary treatment first.

> **The one idea:** a matrix is not a table of numbers, it is a **function**. Everything else follows. The multiplication rule is function composition; the determinant is the area it scales by; the column space is what it can output; the null space is what it destroys; and eigenvectors are the directions it does not turn. Learning the table without the function is why linear algebra feels arbitrary.

## Reading order

Dependencies are strict. Matrices before systems, systems before vector spaces, vector spaces before eigenvalues.

1. [[01-matrices-and-determinants/01-matrices-and-determinants|Matrices and Determinants]] — **[Intermediate]** — the operations, and what a determinant actually **measures**: the factor by which area is scaled
2. [[02-vectors/01-vectors|Vectors]] — **[Intermediate]** — the algebra that works identically in 2 or 50,000 dimensions, Cauchy–Schwarz derived, and why cosine similarity compares documents
3. [[03-systems-of-linear-equations/01-gaussian-elimination|Systems of Linear Equations]] — **[Intermediate]** — how software really solves $A\mathbf{x}=\mathbf{b}$, and the one-line change without which it returns wrong answers silently
4. [[04-vector-spaces/01-vector-spaces|Vector Spaces]] — **[Advanced]** — the abstraction that makes polynomials vectors, and the rank–nullity theorem
5. [[05-linear-transformations/01-linear-transformations|Linear Transformations]] — **[Advanced]** — why the multiplication rule is what it is, derived rather than asserted
6. [[06-eigenvalues/01-eigenvalues-and-eigenvectors|Eigenvalues and Eigenvectors]] — **[Advanced]** — the directions a map leaves alone, diagonalisation, and PageRank in miniature

## The thread through the course

Three questions are asked in lesson 1 and answered in lesson 5:

| Asked | Answered |
| :--- | :--- |
| Why is multiplication row-times-column rather than elementwise? | It is function composition, written down — [[05-linear-transformations/01-linear-transformations|lesson 5, section 4]] |
| Why is $AB \neq BA$? | Because "rotate then scale" is not "scale then rotate" |
| Why does $\det A = 0$ mean no inverse? | The map crushes area to zero, so information is destroyed and cannot be recovered |

And two more run the length of the course: **rank** appears as a pivot count in lesson 3, as a dimension in lesson 4, and as the size of an image in lesson 5 — the same number, three descriptions. **The null space** is a solution set in lesson 3, a subspace in lesson 4, a kernel in lesson 5, and an eigenspace in lesson 6.

## Where the two curricula meet

| Lesson | Secondary source | University source |
| :--- | :--- | :--- |
| Matrices and determinants | SS3 T1 — $2\times2$ operations, determinants, inverses | Y1S2 — general matrices, Cramer's rule |
| Vectors | SS3 T1 — components, magnitude, scalar product | Y1S2 — vector algebra, $n$ dimensions |
| Systems of linear equations | — | Y1S2 — Gaussian elimination, inverse matrices |
| Vector spaces | — | Y2S1 — subspaces, independence, bases, dimension |
| Linear transformations | — | Y2S1 — kernel and image |
| Eigenvalues | — | Y2S1 — eigenvalues and eigenvectors |

## What is verified

Every lab was executed and its "Expected output" block generated from that run. Several check a claim the prose makes rather than illustrating it:

- **The determinant is an area factor** — six transformations applied to the unit square, and the image area equals $\lvert\det\rvert$ every time, including a shear (area unchanged) and a singular matrix (area zero).
- **Pivoting is not optional** — the same $2\times2$ system solved both ways: without pivoting $x = 0$, with pivoting $x = 1$. No error, no warning, 100% wrong.
- **Rank + nullity = columns** — verified across five matrices including a $2\times5$ of zeros.
- **Differentiation is a matrix** — polynomials as a vector space, with "the only functions with zero derivative are the constants" computed as a null space.
- **Rotation matrices multiply by adding angles** — which *is* the trigonometric addition formula, recovered independently of [[02-graphs-and-identities|its derivation in trigonometry]].
- **A Markov chain forgets where it started** — two opposite initial states, both landing on $(5/6, 1/6)$ to nine decimal places.

## How to study this

1. **Attempt the prediction before reading on.** Every lesson stops once and asks you to commit. Answers are at the end of *Check your understanding*, never beside the question.
2. **Hold the function picture from the start.** If a rule seems arbitrary, ask what it means for the map rather than for the table.
3. **Do the labs and break them.** Each is standard library only, self-contained, and writes no files. The pivoting lab in particular is worth running with your own matrices.
4. **Watch for exact versus floating-point arithmetic.** Lessons 4 and 5 use `Fraction` deliberately, because "is this pivot zero?" cannot be answered honestly in floats — a point lesson 3 demonstrates the hard way.

## Related

- [[foundations/mathematics/index|mathematics/]] — the parent course and the full topic map
- [[01-lines-and-planes|Lines and Planes in Space]] — vectors, geometrically
- [[02-quadric-surfaces|Quadric Surfaces]] — a classification that is really about eigenvalue signs
- [[foundations/ai-ml/index|ai-ml/]] — where PCA, embeddings and gradient methods use all of this
- [[foundations/numerical-methods/index|numerical-methods/]] — conditioning, stability and iterative solvers
- [[COURSE-STANDARD|Course standard]] — the teaching shape these lessons follow
