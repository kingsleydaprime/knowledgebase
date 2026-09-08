# Decidability

**[Advanced]** — The halting problem, why it generalises to almost everything, and what it means for the tools you use every day.

## The halting problem

> **Given a program $P$ and input $w$, does $P$ halt on $w$?**
>
> **No algorithm can answer this for all inputs.**

**The proof is short**, and it's worth following because the shape recurs.

Suppose `HALTS(P, w)` exists and always correctly returns true or false. Build:

```
function DIAGONAL(P):
    if HALTS(P, P):
        loop forever
    else:
        halt
```

**Now ask: does `DIAGONAL(DIAGONAL)` halt?**

- **If it halts**, then `HALTS(DIAGONAL, DIAGONAL)` was true, so it loops forever. **Contradiction.**
- **If it loops forever**, then `HALTS` returned false, so it halts. **Contradiction.**

**Either way, contradiction. So `HALTS` cannot exist.** $\blacksquare$

**The engine is self-reference plus negation** — build something that does the opposite of what's predicted about it. **Cantor's diagonal argument, Russell's paradox, and Gödel's incompleteness theorems all run on the same mechanism.** Gödel's is the closest relative: a statement asserting its own unprovability.

**And the counting argument from [[foundations/discrete-math/04-sets-relations-and-functions|note 04]] says the same thing less sharply:** programs are countable, problems are uncountable, so **most problems have no program.** The halting problem is a specific, natural one.

> **What it does *not* say.** It doesn't say you can never tell whether a program halts. **Often you can** — a `for` loop with a constant bound obviously terminates. It says **no single algorithm works for every program.** Termination checkers exist, work well, and answer "yes", "no", or "don't know". **That third answer is where the theorem lives.**

## Reductions

**The tool that spreads undecidability**, and the most transferable technique here.

> **To prove $B$ undecidable: show that if you could decide $B$, you could decide a known-undecidable $A$.**

**Direction is everything, and it's the classic error.** You reduce **known-hard → new problem** ($A \leq B$). Reducing your problem to a hard one proves nothing.

$$A \leq_m B \quad\text{means}\quad \exists \text{ computable } f: \ w\in A \iff f(w)\in B$$

**A worked example — the emptiness problem.** Is $L(M) = \emptyset$?

Given $(P, w)$, construct machine $M$ that ignores its input, runs $P$ on $w$, and accepts if $P$ halts.

**Then $L(M) = \emptyset$ exactly when $P$ doesn't halt on $w$.** A decider for emptiness would decide halting. **So emptiness is undecidable.** $\blacksquare$

**The pattern:** build a machine whose *language* encodes the answer to halting.

## Rice's theorem

**The sledgehammer**, and the result that makes the scope clear.

> **Every non-trivial semantic property of programs is undecidable.**
>
> *Semantic* = about the function computed, not the source text. *Non-trivial* = true of some programs and false of others.

**So all of these are undecidable:**

- Does this program ever output 42?
- Are these two programs equivalent?
- Is this program free of infinite loops?
- Does this function always return a value?
- Is this code unreachable?
- Does this program access a null pointer?
- Does this terminate for all inputs?

**One theorem, all of them at once.** Anything you'd want a perfect static analyser to tell you is on this list.

**What's *decidable*, and the distinction is precise:**

- **Syntactic properties.** "Does the source contain a `while` loop?" — read the text
- **Bounded questions.** "Does it halt within 1000 steps?" — just run it
- **Restricted models.** Finite state, terminating languages, decidable fragments
- **Trivial properties.** True of all programs or none

> **The dividing line is *semantic vs syntactic*.** Static analysis works by finding syntactic proxies for semantic properties, and **every such proxy is necessarily imperfect** — that's Rice's theorem, not a weakness of any particular tool.

## What this means for your tools

**The practical payoff of the whole note.**

**Every static analyser must be incomplete, unsound, or both.**

- **Sound** — no false negatives. Catches every real bug, reports some non-bugs
- **Complete** — no false positives. Every report is real, misses some bugs

**Rice's theorem says you cannot have both.** So every tool picks:

| Tool | Choice |
|---|---|
| **Type checkers** | **Sound**, conservative. Reject some correct programs |
| **Linters** | Neither, tuned for usefulness |
| **Borrow checker** | **Sound.** Rejects some safe programs — hence `unsafe` |
| **Optimising compilers** | Sound. Miss optimisations they can't prove |
| Bug finders (Coverity, Infer) | Unsound, tuned for a low false-positive rate |

> **This is the answer to "why does the type checker reject my obviously-correct code?"** It's not that the designers weren't clever enough. **A sound checker must reject some correct programs, because accepting exactly the correct ones is undecidable.** The design question is only *which* correct programs to sacrifice. → [[foundations/compilers/05-type-systems-and-checking|Type Systems]]

**Concrete consequences you've met:**

**Compilers can't optimise perfectly.** "Is this branch ever taken?" is undecidable, so they use conservative analysis and profile data. → [[foundations/compilers/07-optimisation|Optimisation]]

**Dead code elimination is approximate.** "Unreachable" is undecidable in general.

**Garbage collectors over-approximate.** "Will this object be used again?" is undecidable, so GCs use *reachability* — a decidable, conservative proxy. **Reachable-but-never-used objects are retained**, and that's a memory leak the collector cannot fix by being smarter. → [[foundations/compilers/10-garbage-collection|Garbage Collection]]

**Antivirus cannot be perfect.** "Is this program malicious?" is semantic. **Signature matching is the syntactic proxy**, which is why novel malware gets through and why heuristics produce false positives. **Provably no perfect virus scanner exists** (Cohen, 1987).

**eBPF requires provable termination.** The kernel verifier rejects anything it can't prove halts — bounded loops only. **Rather than solve an undecidable problem, they restricted the language.** → [[foundations/os/09-syscalls-interrupts-and-the-abi|Syscalls and the ABI]]

**Total languages (Coq, Agda, Idris) reject general recursion** for the same reason: to keep type checking decidable, they give up Turing completeness. **A deliberate, principled trade.**

## Other undecidable problems

Worth recognising, because they show the reach:

**Post Correspondence Problem** — given dominoes with top and bottom strings, is there an ordering where top matches bottom? **Deceptively simple, undecidable**, and the standard tool for proving grammar problems undecidable.

**Grammar problems** — is a CFG ambiguous? Are two CFGs equivalent? Is a CFG's language equal to $\Sigma^*$? **All undecidable**, which is why parser generators report conflicts rather than a verdict. → [[foundations/theory-of-computation/04-context-free-languages|Context-Free Languages]]

**Hilbert's tenth problem** — does a polynomial with integer coefficients have integer roots? **Undecidable** (Matiyasevich, 1970), settling one of Hilbert's 1900 problems negatively.

**Wang tiles** — can a set of tiles tile the plane? Undecidable.

**Program equivalence** — the one that would make refactoring verifiable and doesn't exist.

## Degrees of unsolvability

**Not all undecidable problems are equally undecidable**, which is a satisfying refinement.

**Turing reduction** ($A \leq_T B$) allows an *oracle* for $B$. Problems that reduce to each other form a **Turing degree.**

**The arithmetical hierarchy** stratifies them by quantifier alternation:

- $\Sigma_1$ — "does there exist a computation that halts?" **The halting problem lives here**
- $\Pi_2$ — "for every input, does there exist a halting computation?" **Totality is here, strictly harder**

**The halting problem *with a halting oracle*** is still undecidable — it's a strictly harder problem. **There's an infinite tower of unsolvability**, which is a genuinely surprising structural result.

## Living with it

**The productive responses**, because "undecidable" is not "give up":

**Restrict the problem.** Finite state, bounded loops, a decidable fragment. **eBPF and total languages do this**, and it's usually the best move.

**Accept approximation.** Sound-but-incomplete or complete-but-unsound, chosen deliberately and documented.

**Add annotations.** Let the programmer supply what the analyser can't infer — loop variants, invariants, type annotations. **This is why dependent types need proofs from you.**

**Bound the resources.** "Halts within $n$ steps" is decidable. Every timeout is this.

**Use it as a shortcut.** Recognising a problem as undecidable **immediately stops a doomed search.** If someone proposes a tool that finds all bugs with no false positives, you can say why it can't exist without examining the design.

> **That last one is the practical value.** The theory's payoff isn't building anything — it's knowing which things cannot be built, and recognising it in the first five minutes rather than the sixth month.

---

## Related
- [[foundations/theory-of-computation/05-turing-machines|Turing Machines]] — the machines this is about
- [[foundations/theory-of-computation/07-complexity-classes|Complexity Classes]] — hard rather than impossible
- [[foundations/compilers/05-type-systems-and-checking|Type Systems]] — soundness/completeness in practice
- [[foundations/theory-of-computation/README|Theory of computation map]]
