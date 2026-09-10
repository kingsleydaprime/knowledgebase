# Mathematics

**The language the rest of this vault is written in.** Not a subject to admire — a toolkit, built in the order the tools become necessary.

> **The one idea:** every extension of mathematics exists because the previous version **could not answer a question**. Naturals cannot express debt, so integers appear. Integers cannot divide evenly, so rationals appear. Rationals leave gaps on the number line, so reals appear. **Nothing here was invented for its own sake**, and knowing which question each idea answers is the difference between understanding it and memorising it.

## Status — read this first

This course is **partly written**, and the table below is honest about which parts.

| Section | State |
| :--- | :--- |
| **Foundations** (numbers → scientific notation) | ✅ **written**, with problems and worked answers |
| **Number bases** (binary, decimal, hex) | ✅ **written**, with a runnable lab |
| **Discrete mathematics** | ✅ **written** — logic, proof, sets, induction, combinatorics, graphs, number theory |
| **Geometry and trigonometry** | ✅ **written** — 16 lessons, deductive geometry through to quadric surfaces |
| **Linear algebra** | ✅ **written** — 6 lessons, matrices through to eigenvalues and PageRank |
| **Calculus** | ✅ **written** — limits, continuity, derivatives, integration, multivariable |

**Every lesson linked below is written**, with prerequisites, worked examples, problems and hidden answers. The gaps that remain are *topics not yet started* — listed at the bottom — rather than empty files.

## Structure

This course **merges the two curricula** rather than keeping them apart. Each numbered folder is an **umbrella for one subject**, and it collects that subject's topics from *both* the [[ss1-ss3-course-outline|SS1–SS3 NERDC outline]] and the [[uni-math-course-outline|university track]] — secondary treatment first, university treatment after. Calculus at SS3 and Calculus I–III at university are the same subject, so they live in one place: `06-calculus`.

The order is dependency order. Calculus is **last** because it needs the algebra, the trigonometry, and the limit-of-a-sequence ideas that come before it.

```
mathematics/
|- 01-core/                       numbers and algebra - bases through to groups and rings
|- 02-discrete-math/              logic, proof, counting, graphs                    [written]
|- 03-geometry-trigonometry/      deductive -> circle -> trig -> mensuration     [written]
|- 04-linear-algebra/             matrices -> systems -> spaces -> eigenvalues     [written]
|- 05-probability-statistics/     descriptive stats through to inference
|- 06-calculus/                   intro -> Calculus 1-3 -> ODE/PDE -> analysis      [1-3 written]
|- 07-applied-and-computational/  numerical methods, optimisation, control
\- 08-exam-practice/              WAEC/NECO and JAMB/UTME revision
```

**Empty folders are reserved slots.** They exist so the shape of the whole curriculum stays visible, and so nothing from either outline is homeless. The full mapping is at the bottom.

## 01-core — Foundations

What the curriculum assumes. Read first if any of it is shaky.

1. [[01-core/00-foundations/01-number-systems|Number Systems]] - **[Beginner]** - naturals to integers to rationals to reals, and the question each one answers
2. [[01-core/00-foundations/02-variables|Variables]] - **[Beginner]** - naming the unknown, and why `=` means something different in code
3. [[01-core/00-foundations/03-algebraic-manipulation|Algebraic Manipulation]] - **[Beginner]** - expanding, factorising, and why an identical expression can compute better
4. [[01-core/00-foundations/04-approximation-and-standard-form|Approximation and Standard Form]] - **[Beginner]** - scientific notation, significant figures, order-of-magnitude estimation

## 01-core — Numbers *(SS1 Term 1)*

- [[01-core/01-numbers/01-number-bases/01-introduction|Number Bases]] - **[Beginner]** - place value in any base, conversion both ways, arithmetic, **with a runnable lab**
  - [[01-core/01-numbers/01-number-bases/02-binary|Binary]] - bits, bytes, powers of two, and the kilobyte problem
  - [[01-core/01-numbers/01-number-bases/03-decimal|Decimal]] - why ten, which fractions terminate, and why $0.999\ldots = 1$
  - [[01-core/01-numbers/01-number-bases/04-hexadecimal|Hexadecimal]] - why $16 = 2^4$ is the entire reason it exists
- **Modular arithmetic** *(SS1 T1)* - reserved here; the university treatment is already written in [[02-discrete-math/08-number-theory-and-modular-arithmetic|02-discrete-math]]
- [[01-core/01-numbers/03-indices-and-logarithms/01-indices-and-logarithms|Indices and Logarithms]] - **[Beginner]** - the laws *derived* rather than memorised, and why complexity analysis omits the base
- [[01-core/01-numbers/04-sets/01-sets|Sets]] - **[Beginner]** - notation, operations, Venn diagrams, inclusion-exclusion

## 01-core — Algebra *(SS1 Term 2 onward)*

- **Logical reasoning** *(SS1 T2)* - not reserved, **relocated**: it is the same subject as university logic, so it lives written-in-full in [[02-discrete-math/02-logic|02-discrete-math/logic]]
- [[01-core/02-algebra/02-linear-equations/01-linear-equations|Linear Equations]] - **[Beginner]** - solving, simultaneous equations, changing the subject
- **Variations, quadratics, simultaneous linear-and-quadratic, inequalities, algebraic fractions, sequences and series, binomial theorem, polynomials, abstract algebra** - reserved; see the topic map below for exactly what each folder is to hold

## 02-discrete-math

**The most complete part of this course**, and the one computing draws on most.

→ [[02-discrete-math/index|discrete-math/]] — logic and truth tables, proof techniques, sets and relations, induction and recursion, combinatorics, graph theory, number theory and modular arithmetic, plus exercises and solutions.

## 03-geometry-trigonometry

**Written in full — 16 lessons.** Shape and measurement, from angle chasing to three-dimensional surfaces, merging the SS1–SS3 geometry and trigonometry strands with the university vectors-and-analytic-geometry course.

→ [[03-geometry-trigonometry/index|geometry-trigonometry/]] — deductive geometry and constructions, circle theorems and tangents, coordinate geometry, trigonometry from ratios through bearings to hyperbolic functions, mensuration, latitude and longitude, and lines, planes and quadric surfaces in space.

Highlights worth knowing are there: **SSA producing two different triangles** from identical data, **Archimedes bracketing $\pi$** with polygons, **Cavalieri's derivation of the sphere**, why a **polar route beats flying due east**, and a curved surface — the cooling tower — **built entirely from straight lines**.

## 04-linear-algebra

**Written in full — 6 lessons.** Matrices, vectors, elimination, vector spaces, transformations and eigenvalues, merging the SS3 matrices-and-vectors strand with the university Year 1–2 course.

→ [[04-linear-algebra/index|linear-algebra/]] — the running theme is that **a matrix is a function**: the multiplication rule is function composition, the determinant is an area factor, and eigenvectors are the directions the function does not turn.

## 06-calculus

Calculus 1–3 are written in full; the SS3 introduction, ODEs, PDEs and the analysis strand are reserved. Read in order; each lesson names its prerequisites.

**Calculus 1 — limits and derivatives**

1. [[06-calculus/02-calculus-1/01-preview/01-preview|Preview]] — the two problems calculus exists to solve, and the one idea underneath both
2. [[06-calculus/02-calculus-1/02-limit-of-function/01-definition|The Limit of a Function]] — why the value *at* a point is irrelevant to the limit *near* it
3. [[06-calculus/02-calculus-1/03-limit-laws/01-laws|Limit Laws]] — the rules, the indeterminate forms, and the Squeeze Theorem
4. [[06-calculus/02-calculus-1/04-continuity/01-definition|Continuity]] — what makes substitution legal, and the theorem behind `git bisect`
5. [[06-calculus/02-calculus-1/05-precise-definition/01-epsilon-delta|The Precise Definition]] — **[Advanced]** — $\varepsilon$–$\delta$, and why rigour arrived 150 years late
6. [[06-calculus/02-calculus-1/06-defining-derivative/01-definition|Defining the Derivative]] — one limit, from which all of differential calculus follows
7. [[06-calculus/02-calculus-1/07-derivative-rules/01-rules|Derivative Rules]] — each derived, and the chain rule that backpropagation is built on
8. [[06-calculus/02-calculus-1/08-applications/01-related-rates|Applications]] — related rates and optimisation

**Calculus 2 — integration**

9. [[06-calculus/03-calculus-2/01-integration-by-parts|Integration and Integration by Parts]] — antidifferentiation, the Fundamental Theorem, and why integration is harder
10. [[06-calculus/03-calculus-2/02-partial-fractions|Partial Fractions]] — algebra in service of calculus
11. [[06-calculus/03-calculus-2/03-applications|Applications of Integration]] — volumes, arc length, averages, probability

**Calculus 3 — multivariable**

12. [[06-calculus/04-calculus-3/01-partial-derivatives|Partial Derivatives]] — the gradient, and why gradient descent works
13. [[06-calculus/04-calculus-3/02-multiple-integrals|Multiple Integrals]] — accumulation over a region, and the Jacobian factor
14. [[06-calculus/04-calculus-3/03-optimization|Multivariable Optimisation]] — saddle points, and why they dominate in high dimensions

## The two curricula this follows

- [[ss1-ss3-course-outline|Senior Secondary (SS1–SS3)]] — the Nigerian NERDC curriculum. The foundations sequence and number bases cover its early terms.
- [[uni-math-course-outline|University Mathematics & Engineering Mathematics]] — a combined pure and applied degree track. Almost entirely unwritten; discrete mathematics is the exception.

**These outlines are the plan, not the progress.** Read them for where this is going.

## Where this is used

| This course | Feeds |
| :--- | :--- |
| Number bases | [[foundations/how-computers-work/index\|How Computers Work]], [[foundations/computer-architecture/02-data-representation\|data representation]] |
| Exponents, logarithms | [[foundations/dsa/05-algorithms/01-algorithms\|complexity analysis]] — every $\log n$ |
| Sets, logic, proof | [[foundations/mathematics/02-discrete-math/index\|discrete-math]], [[foundations/theory-of-computation/index\|theory of computation]] |
| Combinatorics | [[foundations/dsa/index\|DSA]] — counting arrangements in backtracking and DP |
| Graph theory | [[foundations/dsa/04-data-structures/06-graphs\|graphs]], [[foundations/networking/index\|networking]] |
| Modular arithmetic | [[foundations/cybersecurity/05-cryptography/index\|cryptography]], hashing |
| Calculus | [[foundations/ai-ml/index\|ai-ml]] — gradients and backpropagation |

## How to study this

1. **Do the problems.** Reading mathematics produces the feeling of understanding without the substance. Every lesson here ends with problems whose answers are hidden for that reason.
2. **Derive rather than memorise.** [[01-core/01-numbers/03-indices-and-logarithms/01-indices-and-logarithms|Indices and Logarithms]] shows the pattern: $a^0 = 1$ is not a convention to remember, it is forced by requiring the division law to keep working. Anything you can derive, you cannot forget.
3. **Follow the "why does this exist" thread.** Each topic answers a question the previous one could not.
4. **Go in order.** Unlike most of this vault, the dependencies here are strict — you cannot manipulate equations before you can substitute into expressions.

## The complete topic map

Every topic in both outlines, and the folder it belongs to. ✅ = written, everything else is a reserved slot.

### `01-core` — numbers and algebra

| Folder | Collects | From |
| :--- | :--- | :--- |
| `00-foundations/` ✅ | number systems, variables, algebraic manipulation, approximation and standard form, percentage error | precedes both; SS2 T1 |
| `01-numbers/01-number-bases/` ✅ | conversion, arithmetic in binary and other bases | SS1 T1 |
| `01-numbers/02-modular-arithmetic/` | operations, clock and calendar cycles | SS1 T1 |
| `01-numbers/03-indices-and-logarithms/` ✅ | laws of indices, logs, antilogs, logs below 1, characteristic and mantissa | SS1 T1, SS2 T1 |
| `01-numbers/04-sets/` ✅ | notation, operations, Venn diagrams to 3 sets | SS1 T1 |
| `01-numbers/05-surds/` | rationalising denominators, operations on irrationals | SS3 T1 |
| `01-numbers/06-complex-numbers/` | complex arithmetic, De Moivre's theorem | Uni Y1S1 |
| `02-algebra/02-linear-equations/` ✅ | linear and simultaneous equations, changing the subject | SS1 T2 |
| `02-algebra/03-variations/` | direct, inverse, joint, partial | SS1 T2 |
| `02-algebra/04-quadratic-equations/` | factorisation, completing the square, the formula, roots, graphs | SS1 T3, SS2 T1 |
| `02-algebra/05-simultaneous-equations/` | one linear and one quadratic | SS2 T2 |
| `02-algebra/06-inequalities/` | one and two variables, graphical solutions | SS2 T2 |
| `02-algebra/07-algebraic-fractions/` | simplification, the four operations, substitution | SS2 T2 |
| `02-algebra/08-sequences-and-series/` | arithmetic and geometric progressions (AP and GP), $n$-th term, sums; convergence tests later | SS2 T1, Uni Y2S2 |
| `02-algebra/09-binomial-theorem/` | binomial expansion | Uni Y1S1 |
| `02-algebra/10-polynomials/` | theory of polynomial equations | Uni Y1S1 |
| `03-abstract-algebra/` | binary operations, groups, subgroups, cyclic and permutation groups, Lagrange's theorem, rings | Uni Y3S1 |

### `02-discrete-math` ✅ — written in full

| Collects | From |
| :--- | :--- |
| logical reasoning: antecedents, consequents, connectives, truth tables | SS1 T2 |
| propositions, quantifiers, proof by direct / contradiction / contrapositive | Uni Y1S1 |
| sets, relations and functions; induction and recursion | Uni Y1S1 |
| combinatorics and counting; graph theory | Uni |
| number theory and modular arithmetic | Uni |

### `03-geometry-trigonometry`

| Folder | Collects | From |
| :--- | :--- | :--- |
| `01-deductive-geometry/` ✅ | angles on a line, parallel lines, triangle properties, constructions of $30°, 45°, 60°, 90°$ | SS1 T2 |
| `02-circle-geometry/` ✅ | chords, angles at centre and circumference, cyclic quadrilaterals, tangents, alternate segments | SS2 T2, SS2 T3 |
| `03-coordinate-geometry/` ✅ | midpoint, gradient, distance, equation of a straight line | SS2 T3 |
| `04-trigonometry/` ✅ | sine, cosine, tangent, graphs, elevation and depression, sine and cosine rules, bearings, hyperbolic functions | SS1 T3, SS2 T3, Uni Y1S1 |
| `05-mensuration/` ✅ | perimeter and area of plane shapes, surface area and volume of solids | SS1 T3 |
| `06-latitude-and-longitude/` ✅ | great circles, parallels of latitude, distances | SS3 T1 |
| `07-analytic-geometry-3d/` ✅ | lines and planes in space, quadric surfaces | Uni Y1S2 |

### `04-linear-algebra`

| Folder | Collects | From |
| :--- | :--- | :--- |
| `01-matrices-and-determinants/` ✅ | addition, scalar multiplication, determinants and inverses of $2\times2$; general matrices, Cramer's rule | SS3 T1, Uni Y1S2 |
| `02-vectors/` ✅ | components, magnitude, direction, scalar product; vector algebra in 2D and 3D, dot and cross products | SS3 T1, Uni Y1S2 |
| `03-systems-of-linear-equations/` ✅ | Gaussian elimination, inverse matrices | Uni Y1S2 |
| `04-vector-spaces/` ✅ | subspaces, linear independence, bases, dimension | Uni Y2S1 |
| `05-linear-transformations/` ✅ | kernel and image | Uni Y2S1 |
| `06-eigenvalues/` ✅ | eigenvalues and eigenvectors | Uni Y2S1 |

### `05-probability-statistics`

| Folder | Collects | From |
| :--- | :--- | :--- |
| `01-descriptive-statistics/` | frequency tables, bar charts, histograms, pie charts, mean, median, mode | SS1 T3 |
| `02-dispersion-and-cumulative-frequency/` | ogives, range, variance, standard deviation | SS2 T3 |
| `03-probability/` | basic probability; mutually exclusive and independent events, tree diagrams | SS2 T3, SS3 T2 |
| `04-random-variables-and-distributions/` | probability spaces, random variables, Normal, Binomial, Poisson, joint distributions | Uni Y3S2 |
| `05-inference-and-estimation/` | central limit theorem, parameter estimation | Uni Y3S2 |
| `06-stochastic-processes/` | Markov chains, Poisson processes | Uni Y4S2 |

### `06-calculus`

| Folder | Collects | From |
| :--- | :--- | :--- |
| `01-intro-calculus/` | differentiation as rate of change, integration as area, for basic polynomials | SS3 T1 |
| `02-calculus-1/` ✅ | limits, continuity, the derivative, differentiation techniques, optimisation, MVT | Uni Y1S1 |
| `03-calculus-2/` ✅ | by parts, trigonometric substitution, partial fractions, improper integrals, volumes, arc length | Uni Y1S2 |
| `04-calculus-3/` ✅ | partial derivatives, chain rule, gradients, Lagrange multipliers, multiple integrals | Uni Y2S1 |
| `05-ode/` | ordinary differential equations: first-order, second-order linear, undetermined coefficients, R-L-C and mass-spring applications | Uni Y2S1 |
| `06-pde/` | partial differential equations: the heat equation, the wave equation, Laplace's equation, separation of variables | Uni Y3S1 |
| `07-vector-calculus/` | vector fields, curl, divergence, line and surface integrals, Green's, Stokes', Divergence theorems | Uni Y2S2 |
| `08-real-analysis/` | the real number system, topology of $\mathbb{R}$, sequences and series, convergence, uniform continuity; Lebesgue theory | Uni Y2S2, Y4S1 |
| `09-complex-analysis/` | analytic functions, Cauchy-Riemann, contour integration, Taylor and Laurent series, residues, conformal mapping | Uni Y3S1 |
| `10-fourier-and-transforms/` | Fourier series, even and odd expansions, boundary value problems, Laplace and Fourier transforms, convolution | Uni Y2S2, Y3S2 |

### `07-applied-and-computational`

| Folder | Collects | From |
| :--- | :--- | :--- |
| `01-numerical-methods/` | Newton-Raphson, Simpson's and trapezoidal rules, Euler and Runge-Kutta, interpolation | Uni Y3S2 |
| `02-numerical-pdes/` | finite difference and finite element methods, stability and convergence | Uni Y4S1 |
| `03-optimization-and-operations-research/` | linear programming and the simplex method, non-linear optimisation, duality, Kuhn-Tucker, dynamic programming | Uni Y4S1 |
| `04-control-theory/` | state-space representation, Lyapunov stability, feedback loops | Uni Y4S2 |
| `05-fluid-dynamics-and-continuum-mechanics/` | fluid kinematics, Navier-Stokes, inviscid flow, stress and strain tensors | Uni Y4S2 |
| `06-capstone-project/` | the final-year project or thesis: applying the theory to a real engineering problem | Uni Y4S2 |

### `08-exam-practice`

| Folder | Collects | From |
| :--- | :--- | :--- |
| `01-waec-neco/` | structural essays and multiple choice from past papers | SS3 T2-T3 |
| `02-jamb-utme/` | timed testing across SS1-SS3 | SS3 T2-T3 |

## Related

- [[foundations/mathematics/02-discrete-math/index|discrete-math/]] — the written continuation
- [[foundations/numerical-methods/index|numerical-methods/]] — what happens when exact answers are unavailable
- [[foundations/how-computers-work/index|How Computers Work]] — the course this one feeds most directly
- [[COURSE-STANDARD|Course standard]] — the teaching shape these lessons follow
