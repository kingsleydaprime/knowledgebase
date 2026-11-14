# Mathematics

## What this course is about

**Mathematics is the language the rest of computing is written in: counting, measuring, reasoning about change and chance, and proving that something is always true.**

You use it more than you might think. Binary and hexadecimal are how computers store numbers. Logarithms are why a search through a million items takes only about 20 steps. Logic and proof are how you know a program is correct. Matrices move and rotate every shape in a game. Probability is how spam filters and medical tests make decisions. Calculus is how machine learning models learn.

Every part of mathematics was invented to answer a question the earlier parts couldn't. Whole numbers can't show debt, so negative numbers were invented. Whole numbers can't always be divided evenly, so fractions were invented. Knowing which question each idea answers is the difference between understanding it and memorising it.

This course follows two curricula at once: the Nigerian secondary school syllabus (SS1–SS3) and a university mathematics degree. Each subject collects both levels in one place, school level first.

## What you'll be able to do

Depending on how far you go, you'll be able to:
- work with numbers in any base, with powers and logarithms, and with algebra;
- reason logically, write proofs, count possibilities, and work with graphs (networks of connected points);
- solve geometry and trigonometry problems, from triangles to distances on the globe;
- use matrices and vectors, the maths behind graphics and machine learning;
- describe data with statistics, and reason about chance with probability;
- use calculus to work with rates of change and areas, including gradients for machine learning;
- solve problems numerically on a computer when no exact answer exists.

## Where to start

The order matters more here than anywhere else in the vault: each subject depends on the ones before. **Do the problems** at the end of every lesson; reading maths gives the feeling of understanding without the substance.

### 1. Foundations (start here)

1. [[mathematics/01-core/00-foundations/01-number-systems|Number Systems]]: whole numbers, negatives, fractions and decimals, and the question each one answers.
2. [[mathematics/01-core/00-foundations/02-variables|Variables]]: using letters for unknown numbers, and why `=` means something different in code.
3. [[mathematics/01-core/00-foundations/03-algebraic-manipulation|Algebraic Manipulation]]: expanding and factorising expressions.
4. [[mathematics/01-core/00-foundations/04-approximation-and-standard-form|Approximation and Standard Form]]: rounding, significant figures, and writing very large and small numbers.

### 2. Numbers and algebra

- [[mathematics/01-core/01-numbers/01-number-bases/01-introduction|Number Bases]]: counting in bases other than ten, with a hands-on lab. Then [[mathematics/01-core/01-numbers/01-number-bases/02-binary|Binary]], [[mathematics/01-core/01-numbers/01-number-bases/03-decimal|Decimal]] and [[mathematics/01-core/01-numbers/01-number-bases/04-hexadecimal|Hexadecimal]].
- [[mathematics/01-core/01-numbers/03-indices-and-logarithms/01-indices-and-logarithms|Indices and Logarithms]]: powers and their opposite, worked out rather than memorised.
- [[mathematics/01-core/01-numbers/04-sets/01-sets|Sets]]: groups of things, and Venn diagrams.
- [[mathematics/01-core/02-algebra/02-linear-equations/01-linear-equations|Linear Equations]]: solving equations, including two at once.

### 3. Discrete mathematics

The part computing uses most.

- [[mathematics/02-discrete-math/index|Discrete Mathematics]]: logic and truth tables, proofs, sets and relations, induction, counting, graphs, and number theory (the maths behind encryption).

### 4. Geometry and trigonometry

- [[mathematics/03-geometry-trigonometry/index|Geometry and Trigonometry]]: 16 lessons on shapes and measurement, from angles and circles to trigonometry, areas and volumes, latitude and longitude, and shapes in 3D.

### 5. Linear algebra

- [[mathematics/04-linear-algebra/index|Linear Algebra]]: 6 lessons on matrices and vectors. A matrix is a function that moves and stretches space, and that idea runs through graphics, machine learning and Google's original search ranking.

### 6. Probability and statistics

- [[mathematics/05-probability-statistics/index|Probability and Statistics]]: 6 lessons, from averages and charts to probability, distributions, estimating from samples, and processes that change randomly over time.

### 7. Calculus

Read in order; each lesson names what it needs.

**Calculus 1: limits and derivatives**

1. [[mathematics/06-calculus/02-calculus-1/01-preview/01-preview|Preview]]: the two problems calculus exists to solve, and the one idea behind both.
2. [[mathematics/06-calculus/02-calculus-1/02-limit-of-function/01-definition|The Limit of a Function]]: what a function approaches near a point, even if it's undefined there.
3. [[mathematics/06-calculus/02-calculus-1/03-limit-laws/01-laws|Limit Laws]]: the rules for working limits out.
4. [[mathematics/06-calculus/02-calculus-1/04-continuity/01-definition|Continuity]]: functions with no jumps or gaps, and a theorem that `git bisect` relies on.
5. [[mathematics/06-calculus/02-calculus-1/05-precise-definition/01-epsilon-delta|The Precise Definition]]: the exact, formal meaning of a limit. Harder; optional on a first pass.
6. [[mathematics/06-calculus/02-calculus-1/06-defining-derivative/01-definition|Defining the Derivative]]: the rate of change at an instant.
7. [[mathematics/06-calculus/02-calculus-1/07-derivative-rules/01-rules|Derivative Rules]]: the shortcuts, including the chain rule that machine learning is built on.
8. [[mathematics/06-calculus/02-calculus-1/08-applications/01-related-rates|Applications]]: linked rates of change, and finding the biggest or smallest value.

**Calculus 2: integration**

9. [[mathematics/06-calculus/03-calculus-2/01-integration-by-parts|Integration and Integration by Parts]]: adding up infinitely many tiny pieces, and how it reverses differentiation.
10. [[mathematics/06-calculus/03-calculus-2/02-partial-fractions|Partial Fractions]]: breaking fractions apart so they can be integrated.
11. [[mathematics/06-calculus/03-calculus-2/03-applications|Applications of Integration]]: volumes, lengths of curves, averages and probability.

**Calculus 3: several variables**

12. [[mathematics/06-calculus/04-calculus-3/01-partial-derivatives|Partial Derivatives]]: rates of change when there are several inputs, and why gradient descent works.
13. [[mathematics/06-calculus/04-calculus-3/02-multiple-integrals|Multiple Integrals]]: adding up over an area or volume.
14. [[mathematics/06-calculus/04-calculus-3/03-optimization|Multivariable Optimisation]]: finding the best value when there are several inputs.

### 8. Numerical methods

- [[mathematics/07-applied-and-computational/01-numerical-methods/index|Numerical Methods]]: 13 notes on getting answers with a computer when no exact formula exists: rounding errors, finding roots, solving systems, and approximating areas and change. Needs linear algebra and calculus.

## Where this maths is used

| Maths | Used in |
| :--- | :--- |
| Number bases | [[how-computers-work/index\|How Computers Work]], [[computer-architecture/02-data-representation\|data representation]] |
| Logarithms | [[dsa/03-algorithms/01-complexity-analysis/01-growth-and-asymptotic-notation\|Big-O]], wherever you see $\log n$ |
| Logic and proof | [[theory-of-computation/index\|Theory of Computation]] |
| Counting | [[dsa/index\|DSA]]: backtracking and dynamic programming |
| Graphs | [[dsa/02-data-structures/09-graphs/index\|graphs]], [[networking/index\|networking]] |
| Modular arithmetic | [[cybersecurity/05-cryptography/index\|cryptography]] and hashing |
| Calculus | [[ai-ml/index\|AI & ML]]: gradients and how models learn |

## How to study it

1. **Do the problems.** Every lesson ends with problems whose answers are hidden, so you attempt them first.
2. **Work things out rather than memorising them.** For example, $a^0 = 1$ isn't a rule to remember; it's forced by the rule for dividing powers. Anything you can work out, you can't forget.
3. **Ask what question each idea answers.**
4. **Go in order.** The dependencies here are strict.

## Related

- [[how-computers-work/index|How Computers Work]]: the course this one feeds most directly.
- [[operations-research/index|Operations Research]], [[control-theory/index|Control Theory]] and [[continuum-mechanics/index|Continuum Mechanics]]: engineering subjects built on this maths, kept as their own courses.
- [[COURSE-STANDARD|Course standard]]: the lesson shape these lessons follow.

---

## About this course

- **What's written:** foundations, number bases, discrete maths, geometry and trigonometry, linear algebra, probability and statistics, Calculus 1–3 and numerical methods are written in full, with worked examples and problems.
- **Not written yet:** most of school algebra (variation, quadratics, inequalities, sequences, the binomial theorem), modular arithmetic at school level (the university version is in discrete maths), surds, complex numbers, abstract algebra, the SS3 calculus introduction, differential equations, vector calculus, real and complex analysis, Fourier series and transforms, and the WAEC/NECO and JAMB practice papers. The empty folders are kept so the full shape stays visible.
- **The two curricula:** [[mathematics/ss1-ss3-course-outline|Senior Secondary (SS1–SS3)]], the Nigerian NERDC syllabus, and [[mathematics/uni-math-course-outline|University Mathematics]], a combined pure and applied degree.

## The full topic map

Every topic in both curricula, and the folder it belongs to. ✅ means written; everything else is a reserved slot.

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
| `01-descriptive-statistics/` ✅ | frequency tables, bar charts, histograms, pie charts, mean, median, mode | SS1 T3 |
| `02-dispersion-and-cumulative-frequency/` ✅ | ogives, range, variance, standard deviation | SS2 T3 |
| `03-probability/` ✅ | basic probability; mutually exclusive and independent events, tree diagrams | SS2 T3, SS3 T2 |
| `04-random-variables-and-distributions/` ✅ | probability spaces, random variables, Normal, Binomial, Poisson, joint distributions | Uni Y3S2 |
| `05-inference-and-estimation/` ✅ | central limit theorem, parameter estimation | Uni Y3S2 |
| `06-stochastic-processes/` ✅ | Markov chains, Poisson processes | Uni Y4S2 |

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
| `01-numerical-methods/` ✅ | floating point and error, root finding, linear systems, eigenvalues, interpolation, quadrature, ODEs, PDEs, optimisation — **13 notes, moved here from the vault root** | Uni Y3S2 |
| `02-numerical-pdes/` | finite element methods, stability and convergence for engineering simulation | Uni Y4S1 |
| `06-capstone-project/` | the final-year project or thesis: applying the theory to a real problem | Uni Y4S2 |

**Control theory** and **continuum mechanics** were in this umbrella's plan and are **not** here: they are engineering disciplines that happen to use this mathematics, not branches of it. They live at the vault root as [[control-theory/index|control-theory/]] and [[continuum-mechanics/index|continuum-mechanics/]]. **Optimisation and operations research** (linear programming, simplex, duality, Kuhn-Tucker, dynamic programming — planned here for Uni Y4S1) went the same way for the same reason: it's a decision-making discipline with its own methods, and it lives at [[operations-research/index|operations-research/]].

### `08-exam-practice`

| Folder | Collects | From |
| :--- | :--- | :--- |
| `01-waec-neco/` | structural essays and multiple choice from past papers | SS3 T2-T3 |
| `02-jamb-utme/` | timed testing across SS1-SS3 | SS3 T2-T3 |
