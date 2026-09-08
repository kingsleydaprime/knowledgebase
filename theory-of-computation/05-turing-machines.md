# Turing Machines

**[Intermediate → Advanced]** — Unbounded memory, and therefore everything computable. The model that defines the word.

## The machine

**A finite control plus an infinite tape.** The head reads a symbol, writes a symbol, and moves one cell left or right.

$$\delta: Q\times\Gamma \to Q\times\Gamma\times\{L,R\}$$

```
  ... │ a │ b │ b │ a │ ␣ │ ␣ │ ...
              ▲
           [ q3 ]     finite control
```

**That's the whole model.** It is almost insultingly simple, and it is exactly as powerful as any computer ever built.

**The difference from a PDA is the memory discipline**, and that's the entire story of the hierarchy:

| Machine | Memory | Access |
|---|---|---|
| Finite automaton | none | — |
| Pushdown automaton | stack | **LIFO only** |
| **Turing machine** | tape | **read/write anywhere** |

**A stack forces you to destroy data to reach what's underneath. A tape lets you revisit.** That's what unlocks everything else.

## Why it's the right model

**Turing's argument was about people.** In 1936 a "computer" was a person doing arithmetic with pencil and paper. Turing asked what such a person actually does:

- Reads symbols from a finite alphabet
- Has finitely many mental states
- Writes symbols
- Moves attention locally
- Acts on what they see and remember

**The machine is a formalisation of a human clerk**, argued from first principles about what mechanical procedure *means*. That's why the Church–Turing thesis is persuasive rather than arbitrary — it wasn't reverse-engineered from hardware, and hardware later matched it. → [[foundations/theory-of-computation/01-what-computation-is|Church–Turing thesis]]

## Robustness

**The remarkable fact: nothing you add makes it more powerful.**

| Variant | Power |
|---|---|
| Multiple tapes | **same** (quadratic slowdown to simulate) |
| Two-dimensional tape | **same** |
| Nondeterministic | **same** (exponential slowdown) |
| Multiple heads | **same** |
| Infinite in both directions | **same** |
| Random access (RAM model) | **same** (polynomial) |

> **Every reasonable extension is simulable.** Two tapes can be interleaved on one. A nondeterministic machine can be simulated by breadth-first search over its choice tree.
>
> **This robustness is the evidence for the Church–Turing thesis.** A definition that survives every modification is capturing something real, rather than an artefact of the formalism.

**Note the slowdowns matter for [[foundations/theory-of-computation/07-complexity-classes|complexity]] even though they don't matter for computability.** *Whether* you can compute it is model-independent; *how fast* is not — which is why complexity theory has to fix a model and why "polynomial time" is the robust notion (all reasonable models are polynomially related).

**Turing-complete systems** are everything that can simulate this: every general-purpose language, λ-calculus, cellular automata, and a long list of accidental cases. → [[foundations/theory-of-computation/01-what-computation-is|Turing completeness in the wild]]

## The Universal Turing Machine

**Turing's other great idea, and arguably the more consequential one.**

> **There is a single Turing machine $U$ that takes as input a description of any machine $M$ and an input $w$, and simulates $M$ on $w$.**

**A machine that runs other machines.**

**This is the stored-program computer.** Before it, a "computing machine" meant hardware built for one task. **The UTM says: build one machine, feed it a description of the task.** Von Neumann's architecture is this idea in silicon — **programs and data in the same memory, because to the UTM they're the same thing.** → [[foundations/computer-architecture/01-what-architecture-is|Computer Architecture]]

**It's also every interpreter you've used.** CPython running Python is a UTM. A JVM is. A CPU decoding instructions is. **`eval` is a universal machine, and virtualisation is one machine simulating another.**

**And it's the source of the impossibility results.** Because machines can be encoded as strings and fed to other machines, you can ask "what does this machine do on itself?" — and that self-reference is what produces the halting problem. → [[foundations/theory-of-computation/06-decidability|Decidability]]

## Decidable vs recognisable

**The distinction the whole subject turns on**, and it's the one thing to take from this note.

**Decidable (recursive)** — a TM that **always halts** and answers correctly. Yes *and* no.

**Recognisable (recursively enumerable)** — a TM that halts and accepts on yes instances, but **may loop forever on no instances.**

$$\text{decidable} \subsetneq \text{recognisable} \subsetneq \text{all languages}$$

> **A decider always terminates. A recogniser may not.** If it hasn't answered yet, you cannot tell whether the answer is "no" or "not yet".

**Why "enumerable":** you can write a program that lists every string in the language, eventually. It just never says "that's all of them".

**The complementation theorem:**

$$L \text{ decidable} \iff L \text{ and } \bar{L} \text{ are both recognisable}$$

**Run both recognisers in parallel** (dovetailing — alternate steps). One must eventually accept, and whichever does gives you the answer, always terminating.

**The practical shape of this**, which appears everywhere:

- **A type checker** must be a decider — it has to terminate on every program
- **A theorem prover** is typically a recogniser: it finds proofs that exist, and may search forever when none does
- **A test suite** recognises bugs — it finds them if they manifest, and never proves absence
- **A model checker** decides for finite state and only recognises for infinite

## Simulating a real computer

**Bridging the gap between the model and the machine on your desk:**

**Registers** — a fixed portion of the tape. **Memory** — the tape, addressed by scanning. **Instructions** — states and transitions. **The program counter** — the current state.

**A real CPU is a finite automaton**, strictly speaking — finite RAM means finitely many states. **In practice we model it as a Turing machine** because $2^{10^{12}}$ states is not a useful thing to reason about, and because "add more memory" is always available. **The unbounded tape models extensibility, not physics.**

**The cost of the model:** a TM scanning to a memory location takes $O(n)$ where a real machine takes $O(1)$. **This is why the RAM model is used for algorithm analysis** and the TM for computability. Both are "correct"; they answer different questions.

## What Turing machines can't do

**Two separate limits, and conflating them is a common error:**

**Undecidable** — no algorithm exists, at any speed. The halting problem. **A permanent limit.** → [[foundations/theory-of-computation/06-decidability|Decidability]]

**Intractable** — an algorithm exists but takes infeasibly long. NP-hard problems, if P≠NP. **A limit on resources, not on possibility.** → [[foundations/theory-of-computation/07-complexity-classes|Complexity Classes]]

> **"Impossible" and "too slow" are different failures and call for different responses.** Undecidable means change the problem. Intractable means approximate, restrict the input, or accept exponential time on small instances.

## The Busy Beaver

A concrete demonstration of how bad undecidability gets.

**$BB(n)$ = the most steps an $n$-state TM can run and still halt.**

$$BB(1)=1 \quad BB(2)=6 \quad BB(3)=21 \quad BB(4)=107 \quad BB(5)=47{,}176{,}870$$

**$BB(6) > 10^{10^{10^{10^{18{,}705{,}353}}}}$.**

> **$BB$ grows faster than any computable function** — provably. And it's uncomputable: knowing $BB(n)$ would solve the halting problem for $n$-state machines (run for $BB(n)$ steps; if it hasn't halted, it never will).
>
> **$BB(5) = 47{,}176{,}870$ was only proved in 2024**, by a collaborative effort verified in Coq — for a machine with **five states**. **$BB(6)$ is known to be beyond reach**, and $BB(748)$ is independent of ZFC set theory: a specific 748-state machine halts if and only if ZFC is inconsistent.

**The practical moral:** "just run it and see" fails catastrophically. **A five-state program can run 47 million steps before halting, and there is no bound you can compute in general.** Every timeout you set is a guess.

---

## Related
- [[foundations/theory-of-computation/06-decidability|Decidability]] — what these machines cannot decide
- [[foundations/theory-of-computation/01-what-computation-is|What Computation Is]] — the Church–Turing thesis
- [[foundations/computer-architecture/01-what-architecture-is|Computer Architecture]] — the UTM, built
- [[foundations/theory-of-computation/README|Theory of computation map]]
