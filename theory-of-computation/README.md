# Theory of Computation

What can be computed at all, and what can be computed quickly. Automata, Turing machines, undecidability and complexity — the part of computer science that tells you when to **stop looking for a solution.**

**~13,300 words across 10 notes** (including practice + solutions). Built August 2026 to close a gap found by auditing a standard CS syllabus against this vault. `[reference]`.

> **The one idea worth the whole track:** the hierarchy of machines is a hierarchy of **memory**. No memory, a stack, a bounded tape, an unbounded tape. **Which level a problem sits at tells you which tool it needs** — and the two hardest boundaries (undecidable, NP-complete) tell you when no tool will do.

## Reading order

**02–04 climb the hierarchy. 05–06 are Turing machines and their limits. 07–08 are complexity.** Strictly in order.

1. [[foundations/theory-of-computation/01-what-computation-is|What Computation Is]] — **[Intermediate]** — languages as problems, the Chomsky hierarchy, the Church–Turing thesis, and **why a Turing-complete config language is a bug**
2. [[foundations/theory-of-computation/02-finite-automata|Finite Automata]] — **[Intermediate]** — DFAs, NFAs, the subset construction, and **catastrophic backtracking as a real availability bug**
3. [[foundations/theory-of-computation/03-regular-languages|Regular Languages]] — **[Intermediate]** — closure, the pumping lemma, Myhill–Nerode, and **why parsing HTML with a regex is provably impossible**
4. [[foundations/theory-of-computation/04-context-free-languages|Context-Free Languages]] — **[Intermediate]** — grammars, ambiguity, pushdown automata, and **why no programming language is truly context-free**
5. [[foundations/theory-of-computation/05-turing-machines|Turing Machines]] — **[Intermediate → Advanced]** — the model, its robustness, **the universal machine as the stored-program computer**, and decidable vs recognisable
6. [[foundations/theory-of-computation/06-decidability|Decidability]] — **[Advanced]** — the halting problem, reductions, **Rice's theorem**, and why every static analyser must be incomplete or unsound
7. [[foundations/theory-of-computation/07-complexity-classes|Complexity Classes]] — **[Advanced]** — P, NP, NP-completeness, and **what to actually do when your problem is NP-hard.** The most useful note here
8. [[foundations/theory-of-computation/08-beyond-p-vs-np|Beyond P vs NP]] — **[Advanced]** — randomised algorithms, quantum and post-quantum crypto, zero-knowledge proofs, and an honest account of which parts pay rent

## The things worth carrying

1. **The hierarchy is about memory.** If the structure nests arbitrarily, you need at least a stack — that's a parser, not a regex → [[foundations/theory-of-computation/03-regular-languages|03]]
2. **Language choice never changes what's computable**, only what's convenient. Every general-purpose language is Turing-complete → [[foundations/theory-of-computation/01-what-computation-is|01]]
3. **A Turing-complete config format is a liability.** eBPF, Bitcoin Script and Dhall are deliberately limited so their behaviour can be analysed → [[foundations/theory-of-computation/01-what-computation-is|01]]
4. **Rice's theorem: every non-trivial semantic property of programs is undecidable.** That's *one* theorem covering "does it terminate", "is this equivalent", "is this reachable", "is this malicious" → [[foundations/theory-of-computation/06-decidability|06]]
5. **So every static analyser is unsound, incomplete, or both.** Type checkers choose sound-and-conservative, which is why they reject correct programs → [[foundations/theory-of-computation/06-decidability|06]]
6. **"Undecidable" and "intractable" are different failures.** One says change the problem; the other says approximate → [[foundations/theory-of-computation/05-turing-machines|05]]
7. **NP-complete means: give up exact, efficient, or general — pick one.** Recognising this in the first five minutes rather than the sixth month is the practical payoff of the whole domain → [[foundations/theory-of-computation/07-complexity-classes|07]]
8. **Reductions go known-hard → your problem.** Reducing yours to a hard one proves nothing, and it's the classic error → [[foundations/theory-of-computation/06-decidability|06]]
9. **Quantum computers are not parallel search.** They exploit interference, which needs structure — hence Shor's exponential speedup on factoring and only Grover's quadratic one on general search → [[foundations/theory-of-computation/08-beyond-p-vs-np|08]]
10. **Symmetric crypto survives quantum by doubling key sizes. Public-key does not survive** → [[foundations/theory-of-computation/08-beyond-p-vs-np|08]]

## Where this connects

| | |
|---|---|
| [[foundations/discrete-math/README\|discrete maths]] | **The prerequisite.** Proof, countability, induction |
| [[foundations/compilers/README\|compilers]] | **The direct application.** Lexers are DFAs, parsers are PDAs, and the syntax/semantics split is forced by the hierarchy |
| [[foundations/dsa/05-algorithms/01-algorithms\|algorithms]] | Complexity analysis, and why some problems have no good algorithm |
| [[cybersecurity/05-cryptography/README\|cryptography]] | Rests entirely on believed-hard problems |
| [[foundations/computer-architecture/01-what-architecture-is\|computer architecture]] | The universal machine, realised in silicon |

**The compilers connection is the strongest.** That course was built first, for practical reasons; **this one explains why it's structured the way it is** — why lexing and parsing are separate phases, why type checking can't be part of parsing, and why parser generators report conflicts instead of verdicts.

## The honest note

**`[reference]`, and this track has a specific version of the problem: the proofs *are* the content.**

The facts are memorable and cheap — "HTML isn't regular", "SAT is NP-complete". **The value is in being able to construct a reduction or a pumping argument yourself**, and reading one is not the same as producing one. Every proof here is presented; none of them makes you do one.

**What would close the gap, cheaply:**

- **Prove three things from scratch:** $\{a^nb^n\}$ isn't regular, the halting problem is undecidable, and one NP-completeness reduction (VERTEX COVER from 3-SAT is the standard first). An afternoon with paper
- **Build a regex engine** — Thompson's construction, then subset construction. **A few hundred lines, and it makes the equivalences concrete.** It's the natural companion to [[build-your-own-shit/README|build-your-own-shit]], and arguably belongs there
- **Write a SAT solver.** DPLL is surprisingly short; adding clause learning turns it into something that actually works
- **Sipser's *Introduction to the Theory of Computation*** — the standard text, and unusually well written. Papadimitriou for complexity, Arora–Barak for the modern treatment

**What's missing here:** ~~exercises~~ — **closed by notes 9–10 (Aug 2026)**; formal proofs of the equivalences (they're described rather than derived), the arithmetical hierarchy in depth, circuit complexity, communication complexity, descriptive complexity, and anything on computability over the reals.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Practice

- [[foundations/theory-of-computation/09-practice-exercises|Practice Exercises]] — fourteen problems — three proofs from scratch, plus a regex engine and a SAT solver to build
- [[foundations/theory-of-computation/10-practice-exercises-solutions|Solutions]] — worked answers, **after you've tried**

## Related
- [[foundations/discrete-math/README|Discrete Mathematics]] — the prerequisite
- [[foundations/compilers/README|Compilers]] — the applied version of notes 02–04
- [[foundations/computer-architecture/README|Computer Architecture]] — the third domain in this batch
- [[BUILD-PLAN|Build Plan]]
