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
| **Calculus** | ⚠️ **14 stub files.** Titles and one-line summaries only |

**If a link below leads to a one-line file, it is a stub and is marked as such.** Nothing else in the vault depends on the calculus stubs — [[foundations/how-computers-work/index|How Computers Work]] uses calculus only qualitatively.

## The foundations sequence

Read in order. Each lesson names its prerequisites and ends with problems whose answers are hidden until you attempt them.

1. [[01-numbers|Number Systems]] — **[Beginner]** — naturals → integers → rationals → reals, and the question each one answers
2. [[02-sets|Sets]] — **[Beginner]** — notation, operations, Venn diagrams, inclusion–exclusion
3. [[03-variables|Variables]] — **[Beginner]** — naming the unknown, and why `=` means something different in code
4. [[04-equations|Equations]] — **[Beginner]** — solving, simultaneous equations, changing the subject
5. [[05-algebraic-manipulation|Algebraic Manipulation]] — **[Beginner]** — expanding, factorising, and why an identical expression can compute better
6. [[06-exponents|Exponents]] — **[Beginner]** — the laws *derived* rather than memorised, and why exponential growth defeats intuition
7. [[07-scientific-notation|Scientific Notation]] — **[Beginner]** — very large and very small numbers, significant figures, order-of-magnitude estimation

## Number bases

The first topic in the [[ss1-ss3-course-outline|SS1 curriculum]], and the one [[foundations/how-computers-work/index|How Computers Work]] depends on directly.

- [[core/01-numbers/01-number-bases/01-introduction|Number Bases]] — **[Beginner]** — place value in any base, conversion both ways, arithmetic, **with a runnable lab**
- [[core/01-numbers/01-number-bases/02-binary|Binary]] — bits, bytes, the powers of two, and the kilobyte problem
- [[core/01-numbers/01-number-bases/03-decimal|Decimal]] — why ten, which fractions terminate, and why $0.999\ldots = 1$
- [[core/01-numbers/01-number-bases/04-hexadecimal|Hexadecimal]] — why $16 = 2^4$ is the entire reason it exists

## Discrete mathematics

**The most complete part of this course**, and the one computing draws on most.

→ [[discrete-math/index|discrete-math/]] — logic and truth tables, proof techniques, sets and relations, induction and recursion, combinatorics, graph theory, number theory and modular arithmetic, plus exercises and solutions.

## Calculus — not yet written

[[calculus/02-calculus-1/01-preview/01-preview|calculus/]] currently contains **14 stub files**: correct titles, one-line summaries, no lessons. They cover limits, continuity, derivatives, integration techniques and multivariable calculus.

**Treat them as a table of contents, not as material.** Until they are written, use a standard text — the vault has `calculus-volume-1_-_WEB.pdf` at the repository root.

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
| Calculus *(when written)* | [[foundations/ai-ml/index\|ai-ml]] — gradients and backpropagation |

## How to study this

1. **Do the problems.** Reading mathematics produces the feeling of understanding without the substance. Every lesson here ends with problems whose answers are hidden for that reason.
2. **Derive rather than memorise.** [[06-exponents|Exponents]] shows the pattern: $a^0 = 1$ is not a convention to remember, it is forced by requiring the division law to keep working. Anything you can derive, you cannot forget.
3. **Follow the "why does this exist" thread.** Each topic answers a question the previous one could not.
4. **Go in order.** Unlike most of this vault, the dependencies here are strict — you cannot manipulate equations before you can substitute into expressions.

## Related

- [[foundations/discrete-math/index|discrete-math/]] — the written continuation
- [[foundations/numerical-methods/index|numerical-methods/]] — what happens when exact answers are unavailable
- [[foundations/how-computers-work/index|How Computers Work]] — the course this one feeds most directly
- [[COURSE-STANDARD|Course standard]] — the teaching shape these lessons follow
