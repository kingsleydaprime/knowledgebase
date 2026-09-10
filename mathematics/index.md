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
| **Calculus** | ✅ **written** — limits, continuity, derivatives, integration, multivariable |

**Every lesson linked below is written**, with prerequisites, worked examples, problems and hidden answers. The gaps that remain are *topics not yet started* — listed at the bottom — rather than empty files.

## Structure

The folders follow your two curricula: **`01-core`** mirrors the [[ss1-ss3-course-outline|SS1-SS3 NERDC outline]] term by term, and the later folders follow the [[uni-math-course-outline|university track]]. **Empty folders are reserved slots** for topics not yet written, kept so the shape of the curriculum stays visible.

```
mathematics/
|- 01-core/                     foundations + secondary curriculum
|  |- 00-foundations/           written - precedes the curriculum proper
|  |- 01-numbers/               bases / modular* / indices+logs / sets
|  \- 02-algebra/               linear equations / the rest*
|- 02-discrete-math/            written in full
|- 03-calculus/                 Calculus 1-3 written / intro*, ODE*, PDE*
|- 04-geometry-trigonometry/    reserved*
|- 05-linear-algebra/           reserved*
\- 06-probability-statistics/   reserved*
                                              (* = not yet written)
```

## 00 - Foundations

What the curriculum assumes. Read first if any of it is shaky.

1. [[01-core/00-foundations/01-number-systems|Number Systems]] - **[Beginner]** - naturals to integers to rationals to reals, and the question each one answers
2. [[01-core/00-foundations/02-variables|Variables]] - **[Beginner]** - naming the unknown, and why `=` means something different in code
3. [[01-core/00-foundations/03-algebraic-manipulation|Algebraic Manipulation]] - **[Beginner]** - expanding, factorising, and why an identical expression can compute better
4. [[01-core/00-foundations/04-approximation-and-standard-form|Approximation and Standard Form]] - **[Beginner]** - scientific notation, significant figures, order-of-magnitude estimation

## 01 - Numbers *(SS1 Term 1)*

- [[01-core/01-numbers/01-number-bases/01-introduction|Number Bases]] - **[Beginner]** - place value in any base, conversion both ways, arithmetic, **with a runnable lab**
  - [[01-core/01-numbers/01-number-bases/02-binary|Binary]] - bits, bytes, powers of two, and the kilobyte problem
  - [[01-core/01-numbers/01-number-bases/03-decimal|Decimal]] - why ten, which fractions terminate, and why $0.999\ldots = 1$
  - [[01-core/01-numbers/01-number-bases/04-hexadecimal|Hexadecimal]] - why $16 = 2^4$ is the entire reason it exists
- **Modular arithmetic** - *reserved*; covered for now by [[02-discrete-math/08-number-theory-and-modular-arithmetic|discrete-math]]
- [[01-core/01-numbers/03-indices-and-logarithms/01-indices-and-logarithms|Indices and Logarithms]] - **[Beginner]** - the laws *derived* rather than memorised, and why complexity analysis omits the base
- [[01-core/01-numbers/04-sets/01-sets|Sets]] - **[Beginner]** - notation, operations, Venn diagrams, inclusion-exclusion

## 02 - Algebra *(SS1 Term 2 onward)*

- **Logical reasoning** - *reserved*; covered for now by [[02-discrete-math/02-logic|discrete-math/logic]]
- [[01-core/02-algebra/02-linear-equations/01-linear-equations|Linear Equations]] - **[Beginner]** - solving, simultaneous equations, changing the subject
- **Variations, quadratics, simultaneous linear-and-quadratic, inequalities, algebraic fractions** - *reserved*

## Discrete mathematics

**The most complete part of this course**, and the one computing draws on most.

→ [[02-discrete-math/index|discrete-math/]] — logic and truth tables, proof techniques, sets and relations, induction and recursion, combinatorics, graph theory, number theory and modular arithmetic, plus exercises and solutions.

## Calculus

Written in full. Read in order; each lesson names its prerequisites.

**Calculus 1 — limits and derivatives**

1. [[03-calculus/02-calculus-1/01-preview/01-preview|Preview]] — the two problems calculus exists to solve, and the one idea underneath both
2. [[03-calculus/02-calculus-1/02-limit-of-function/01-definition|The Limit of a Function]] — why the value *at* a point is irrelevant to the limit *near* it
3. [[03-calculus/02-calculus-1/03-limit-laws/01-laws|Limit Laws]] — the rules, the indeterminate forms, and the Squeeze Theorem
4. [[03-calculus/02-calculus-1/04-continuity/01-definition|Continuity]] — what makes substitution legal, and the theorem behind `git bisect`
5. [[03-calculus/02-calculus-1/05-precise-definition/01-epsilon-delta|The Precise Definition]] — **[Advanced]** — $\varepsilon$–$\delta$, and why rigour arrived 150 years late
6. [[03-calculus/02-calculus-1/06-defining-derivative/01-definition|Defining the Derivative]] — one limit, from which all of differential calculus follows
7. [[03-calculus/02-calculus-1/07-derivative-rules/01-rules|Derivative Rules]] — each derived, and the chain rule that backpropagation is built on
8. [[03-calculus/02-calculus-1/08-applications/01-related-rates|Applications]] — related rates and optimisation

**Calculus 2 — integration**

9. [[03-calculus/03-calculus-2/01-integration-by-parts|Integration and Integration by Parts]] — antidifferentiation, the Fundamental Theorem, and why integration is harder
10. [[03-calculus/03-calculus-2/02-partial-fractions|Partial Fractions]] — algebra in service of calculus
11. [[03-calculus/03-calculus-2/03-applications|Applications of Integration]] — volumes, arc length, averages, probability

**Calculus 3 — multivariable**

12. [[03-calculus/04-calculus-3/01-partial-derivatives|Partial Derivatives]] — the gradient, and why gradient descent works
13. [[03-calculus/04-calculus-3/02-multiple-integrals|Multiple Integrals]] — accumulation over a region, and the Jacobian factor
14. [[03-calculus/04-calculus-3/03-optimization|Multivariable Optimisation]] — saddle points, and why they dominate in high dimensions

## The two curricula this follows

- [[ss1-ss3-course-outline|Senior Secondary (SS1–SS3)]] — the Nigerian NERDC curriculum. The foundations sequence and number bases cover its early terms.
- [[uni-math-course-outline|University Mathematics & Engineering Mathematics]] — a combined pure and applied degree track. Almost entirely unwritten; discrete mathematics is the exception.

**These outlines are the plan, not the progress.** Read them for where this is going.

## Where this is used

| This course | Feeds |
| :--- | :--- |
| Number bases | [[foundations/how-computers-work/index\|How Computers Work]], [[foundations/computer-architecture/02-data-representation\|data representation]] |
| Exponents, logarithms | [[foundations/dsa/05-algorithms/01-algorithms\|complexity analysis]] — every $\log n$ |
| Sets, logic, proof | [[foundations/discrete-math/index\|discrete-math]], [[foundations/theory-of-computation/index\|theory of computation]] |
| Combinatorics | [[foundations/dsa/index\|DSA]] — counting arrangements in backtracking and DP |
| Graph theory | [[foundations/dsa/04-data-structures/06-graphs\|graphs]], [[foundations/networking/index\|networking]] |
| Modular arithmetic | [[foundations/cybersecurity/05-cryptography/index\|cryptography]], hashing |
| Calculus | [[foundations/ai-ml/index\|ai-ml]] — gradients and backpropagation |

## How to study this

1. **Do the problems.** Reading mathematics produces the feeling of understanding without the substance. Every lesson here ends with problems whose answers are hidden for that reason.
2. **Derive rather than memorise.** [[01-core/01-numbers/03-indices-and-logarithms/01-indices-and-logarithms|Indices and Logarithms]] shows the pattern: $a^0 = 1$ is not a convention to remember, it is forced by requiring the division law to keep working. Anything you can derive, you cannot forget.
3. **Follow the "why does this exist" thread.** Each topic answers a question the previous one could not.
4. **Go in order.** Unlike most of this vault, the dependencies here are strict — you cannot manipulate equations before you can substitute into expressions.

## Still to write

Every lesson linked above is complete. The **reserved folders** below exist and are empty - they mark planned topics so the curriculum's shape is visible even where the content is not:

| Reserved folder | From |
| :--- | :--- |
| `01-core/01-numbers/02-modular-arithmetic/` | SS1 Term 1 |
| `01-core/02-algebra/` - variations, quadratics, simultaneous, inequalities, algebraic fractions | SS1 T2 - SS2 |
| `03-calculus/01-intro-calculus/`, `05-ode/`, `06-pde/` | SS3 intro, university |
| `04-geometry-trigonometry/` - deductive, circle, coordinate, trigonometry | SS1 T3 - SS2 T3 |
| `05-linear-algebra/` - vector spaces, eigenvalues | university Year 1-2 |
| `06-probability-statistics/` | SS1 T3, SS2 T3 |

## Related

- [[foundations/discrete-math/index|discrete-math/]] — the written continuation
- [[foundations/numerical-methods/index|numerical-methods/]] — what happens when exact answers are unavailable
- [[foundations/how-computers-work/index|How Computers Work]] — the course this one feeds most directly
- [[COURSE-STANDARD|Course standard]] — the teaching shape these lessons follow
