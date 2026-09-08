# What Computation Is

**[Intermediate]** — Why you'd formalise something as obvious as "computing", and what the hierarchy of machines is for.

**Source:** `[reference]` — see [[foundations/theory-of-computation/README|the domain note]].

## The question

**What can be computed?**

Not "what can this language do" or "what's fast enough" — **what is computable at all, by any machine, given unlimited time and memory?**

That sounds like philosophy. It produced the most practically consequential results in computer science: **the halting problem, NP-completeness, and the fact that your compiler cannot catch every bug — not because it isn't clever enough, but because no compiler can.**

> **The field's defining move was formalising "algorithm" before computers existed.** Turing, Church, Post and Kleene were working in the 1930s on a question from mathematical logic — Hilbert's *Entscheidungsproblem*, "is there a mechanical procedure to decide any mathematical statement?" **The answer was no, and defining "mechanical procedure" precisely enough to prove it invented the computer.**

## Languages and problems

The formal setup. It looks like bureaucracy and it buys you precision.

**Alphabet $\Sigma$** — a finite set of symbols. $\{0,1\}$, or ASCII.

**String** — a finite sequence over $\Sigma$. $\epsilon$ is the empty string.

**Language $L \subseteq \Sigma^*$** — a set of strings. **Any** set of strings.

**The reframing that makes everything work:**

> **Every decision problem is a language, and every language is a decision problem.**

"Is $n$ prime?" is the language $\{$binary strings encoding primes$\}$. "Is this program syntactically valid Python?" is a language. "Does this Turing machine halt?" is a language.

**So "can a machine solve this problem?" becomes "can a machine recognise this language?"** — and now you can compare machines by which languages they handle. **That's the entire architecture of the subject.**

**Why restrict to decision problems?** Yes/no is simpler to reason about, and it loses nothing important: any function can be probed with yes/no questions ("is the $i$th bit of the output 1?"). Hardness results transfer.

## The Chomsky hierarchy

**Four classes of language, four classes of machine, nested strictly.**

```
┌───────────────────────────────────────────────────┐
│  Recursively enumerable  —  Turing machine        │
│  ┌─────────────────────────────────────────────┐  │
│  │  Context-sensitive  —  linear bounded aut.  │  │
│  │  ┌───────────────────────────────────────┐  │  │
│  │  │  Context-free  —  pushdown automaton   │  │  │
│  │  │  ┌─────────────────────────────────┐  │  │  │
│  │  │  │  Regular  —  finite automaton    │  │  │  │
│  │  │  └─────────────────────────────────┘  │  │  │
│  │  └───────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────┘
              (and outside all of it: undecidable)
```

| Level | Machine | Memory | Recognises | You know it as |
|---|---|---|---|---|
| **Regular** | finite automaton | **none** (finite state) | `(ab)*`, keywords | regex, lexers |
| **Context-free** | pushdown automaton | **a stack** | balanced brackets | grammars, parsers |
| **Context-sensitive** | linear bounded | bounded tape | agreement, `aⁿbⁿcⁿ` | rare in practice |
| **Recursively enumerable** | Turing machine | **unbounded tape** | everything computable | programs |

> **The hierarchy is exactly about memory.** No memory, a stack, a bounded tape, an unbounded tape. **Each step up buys strictly more power**, and every containment is proper — there are provably languages at each level that the level below cannot recognise.

**And the practical reading:** the hierarchy tells you **which tool to reach for**. Matching keywords needs no memory, so a regex is right. Matching nested brackets needs a stack, so a regex is *provably* the wrong tool. → [[foundations/theory-of-computation/03-regular-languages|Regular Languages]]

## The Church–Turing thesis

Multiple people, from different directions, formalised "computable" in the 1930s:

- **Turing machines** (Turing) — a tape, a head, states
- **λ-calculus** (Church) — function abstraction and application
- **Recursive functions** (Gödel, Kleene) — built from primitives by composition and recursion
- **Post systems** (Post) — string rewriting

**All four define exactly the same class of functions.** So do register machines, cellular automata, Conway's Game of Life, and every programming language you've used.

> **The Church–Turing thesis:** anything effectively computable by any mechanical procedure is computable by a Turing machine.

**It's a thesis, not a theorem** — "effectively computable" is an informal notion, so it can't be proved. **It could be refuted** by exhibiting a physically realisable device computing something a Turing machine can't. Nobody has, in ninety years.

**What follows, and it's the reason the subject is worth learning:**

**Language choice doesn't affect *what* is computable.** Python, Haskell, x86 assembly and Brainfuck are all Turing-complete. **They differ in convenience, speed and safety — never in power.** So "which language can solve this?" is never the right question.

**A limit proved for Turing machines is a limit for everything.** The halting problem isn't a limitation of a particular formalism; it's a limitation of computation. That's what makes the impossibility results in [[foundations/theory-of-computation/06-decidability|note 06]] worth knowing.

**Quantum computers don't change this.** They compute the same *class* of functions, potentially much faster for some. **Shor's algorithm doesn't make anything newly computable** — it makes factoring fast. → [[foundations/theory-of-computation/08-beyond-p-vs-np|Beyond P vs NP]]

## Turing completeness in the wild

A system is **Turing complete** if it can simulate a Turing machine — which needs surprisingly little: conditional branching and unbounded memory.

**Things that are accidentally Turing complete:**

- **C++ templates** — discovered, not designed. Which is why template metaprogramming can loop forever at compile time
- **TypeScript's type system**
- **Excel** (with `LAMBDA`, deliberately; before that, accidentally)
- **Magic: The Gathering**, x86's `MOV` instruction alone, Minecraft redstone, PowerPoint animations
- **`sed`**, and Conway's Game of Life

**Why this matters practically:**

> **A Turing-complete configuration language is a bug, not a feature.** If your config format can express arbitrary computation, you cannot statically determine what it does, whether it terminates, or whether it's safe. **This is why YAML-with-templating gets unpredictable, and why some systems deliberately choose non-Turing-complete languages.**

**Deliberately limited by design:** SQL (the core relational algebra), Bitcoin Script, eBPF (the verifier requires provable termination), Dhall, Coq's total fragment, and regular expressions proper. **In each case the limitation is the point** — you trade expressiveness for decidable analysis.

## Nondeterminism

A concept that recurs in every note here, so worth introducing now.

**A deterministic machine has one next move. A nondeterministic machine may have several, and accepts if *any* choice sequence leads to acceptance.**

**Think of it as perfect guessing** — the machine always guesses the right branch — or as exploring all branches in parallel.

**It's not physically realisable**, and that's fine. **It's a tool for defining problem classes**, and the interesting question is always: *does nondeterminism add power?*

| Machine | Does nondeterminism add power? |
|---|---|
| Finite automata | **No** — NFA and DFA recognise the same languages |
| Pushdown automata | **Yes** — NPDA is strictly stronger than DPDA |
| Turing machines | **No** for computability — same class |
| Turing machines | **Unknown** for efficiency — **that's P vs NP** |

> **P vs NP is exactly the question of whether nondeterminism helps *efficiency* for Turing machines.** Every other row in that table is settled. That one is the biggest open problem in the field. → [[foundations/theory-of-computation/07-complexity-classes|Complexity Classes]]

## What this track is for

**Three concrete payoffs**, and they're the reason to spend the time:

**1. Knowing which tool a problem needs.** HTML is not regular, so parsing it with a regex is provably wrong — not stylistically, mathematically. **The hierarchy tells you what memory a problem requires.**

**2. Recognising impossibility.** Undecidable means *stop looking*. NP-complete means *stop looking for an exact efficient algorithm and start approximating*. **Recognising these early saves months**, and it's the single most valuable thing here.

**3. Reading the literature.** Complexity classes, reductions and hardness proofs are the shared vocabulary of algorithms, cryptography, databases and PL.

**Reading order:** 02–04 climb the hierarchy (finite automata → regular → context-free). 05–06 are Turing machines and what they can't do. 07–08 are complexity — what they can't do *quickly*.

**Prerequisites:** [[foundations/discrete-math/README|discrete maths]], particularly proof technique, countability, and induction. **The proofs here are the point**, so the ability to follow one matters more than any specific fact.

---

## Related
- [[foundations/theory-of-computation/02-finite-automata|Finite Automata]] — the bottom of the hierarchy
- [[foundations/discrete-math/04-sets-relations-and-functions|Sets, Relations and Functions]] — countability, the prerequisite for undecidability
- [[foundations/compilers/README|Compilers]] — where the hierarchy is applied daily
- [[foundations/theory-of-computation/README|Theory of computation map]]
