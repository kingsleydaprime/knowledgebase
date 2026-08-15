# Regular Languages

**[Intermediate]** — What finite memory can and cannot recognise, and how to prove a language is out of reach.

## Three equivalent definitions

A language is **regular** if it's described by any of:

1. A **regular expression**
2. A **finite automaton** (DFA or NFA — equivalent)
3. A **regular grammar** (all productions $A \to aB$ or $A \to a$)

**Kleene's theorem says these coincide exactly.** Which definition you use is a matter of convenience.

**The regular operations** — and regular languages are precisely what you get by closing $\{$single symbols, $\epsilon$, $\emptyset\}$ under them:

$$\text{union } L_1\cup L_2 \qquad \text{concatenation } L_1L_2 \qquad \text{Kleene star } L^*$$

## Closure properties

**Regular languages are closed under almost everything**, which is unusually convenient and is why regular tools compose so well.

| Operation | Closed? | How |
|---|---|---|
| Union, concatenation, star | ✓ | by definition |
| **Complement** | ✓ | **swap accepting and non-accepting states of a DFA** |
| **Intersection** | ✓ | product construction, or De Morgan on complement+union |
| Difference | ✓ | $L_1 \cap \overline{L_2}$ |
| Reversal, homomorphism | ✓ | |

**Complement is the striking one, and it's why the DFA/NFA distinction matters.** Flipping the accepting states of a *DFA* gives exactly the complement. **Doing that to an NFA does not work** — an NFA accepts if *some* path accepts, so flipping gives "some path rejects", which isn't the complement. **You must determinise first.**

**The product construction** for intersection: run both DFAs simultaneously, with states $Q_1\times Q_2$, accepting when both accept. **Simple, and it's how tools combine multiple patterns.**

**Why closure properties are useful:** they let you *prove non-regularity indirectly*. If $L$ were regular, then $L \cap (\text{something regular})$ would be regular — and if you can show that intersection is a known-irregular language, you're done. **Often much easier than a direct pumping argument.**

## The pumping lemma

**The standard tool for proving a language is *not* regular.**

> **If $L$ is regular, there's a pumping length $p$ such that every string $s\in L$ with $|s|\geq p$ can be split $s = xyz$ where:**
> 1. $|y| > 0$
> 2. $|xy| \leq p$
> 3. **$xy^iz \in L$ for every $i \geq 0$**

**Where it comes from, which is more useful than memorising it:** a DFA with $p$ states reading a string of length $\geq p$ must **revisit a state** — pigeonhole. The substring consumed between the two visits is a **loop**, and a loop can be traversed any number of times. **So the pumped strings must also be accepted.** → [[foundations/discrete-math/06-combinatorics-and-counting|Pigeonhole]]

### Using it

**It's an adversary game, and the quantifier order is what people get wrong:**

- **The adversary picks $p$** (you don't know it)
- **You pick $s \in L$** with $|s| \geq p$ — choose wisely
- **The adversary picks the split** $xyz$ (you must handle all valid splits)
- **You pick $i$** to force a contradiction

> **Claim:** $L = \{a^nb^n\}$ is not regular.
>
> **Proof.** Suppose it is, with pumping length $p$. Take $s = a^pb^p$.
>
> Since $|xy|\leq p$, **$y$ consists only of $a$s** — that's what condition 2 buys you, and it's why the condition exists.
>
> Pump with $i=2$: $xy^2z$ has more `a`s than `b`s, so it's not in $L$. Contradiction. $\blacksquare$

**Choosing $s$ well is the skill.** A bad choice lets the adversary pick a $y$ that pumps harmlessly. $a^pb^p$ works because condition 2 traps $y$ inside the `a`s.

**Two warnings:**

**It's necessary, not sufficient.** Passing the pumping lemma does *not* prove regularity — there are non-regular languages that pump. **For a proof of regularity, build an automaton or use Myhill–Nerode.**

**Get the quantifiers right.** You don't get to choose the split; the adversary does. Handling only one convenient split is the commonest error in a pumping proof. → [[foundations/discrete-math/02-logic|Quantifier order]]

## Myhill–Nerode

**The complete characterisation**, and unlike the pumping lemma it works in both directions.

Define $x \equiv_L y$ if **no suffix distinguishes them**: for every $z$, $xz\in L \iff yz\in L$.

> **$L$ is regular if and only if $\equiv_L$ has finitely many equivalence classes.**
>
> **And the number of classes is exactly the number of states in the minimal DFA.**

**The intuition:** a state is precisely "everything the machine needs to remember", and two strings need the same state exactly when no future input can tell them apart. **Finitely many things to remember ⟺ finite automaton.** → [[foundations/discrete-math/04-sets-relations-and-functions|Equivalence relations]]

**Applied to $\{a^nb^n\}$:** $a^1, a^2, a^3, \ldots$ are pairwise distinguishable — $a^ib^i \in L$ but $a^jb^i \notin L$ for $j\neq i$. **Infinitely many classes, so not regular.** Cleaner than the pumping argument, and it also tells you the minimal machine.

## Non-regular languages worth recognising

| Language | Why not regular |
|---|---|
| $\{a^nb^n\}$ | must count unboundedly |
| Balanced parentheses | unbounded nesting depth |
| $\{ww\}$ | must remember an arbitrary string |
| $\{a^{n^2}\}$, $\{a^p : p \text{ prime}\}$ | gaps grow without bound |
| Palindromes | must compare front to back |

**The common thread: they all require unbounded memory.** Finite state gives you a bounded amount of "what have I seen", and any language needing more is out.

**Contrast with what *is* regular** and looks harder than it is:

- **Strings with an even number of `a`s** — one bit of state
- **Strings whose value mod 7 is 0** — seven states, and this is genuinely surprising the first time
- **Any finite language** — trivially, just enumerate it
- **Nesting bounded to depth 3** — regular, with many states

> **"Bounded" is the word that decides it.** Nesting to depth 3 is regular; arbitrary nesting is not.

## The practical payoff

**This note's whole value is knowing when a regex is the wrong tool** — and being able to say *why* rather than just *that*.

**A regex cannot parse:**

- **HTML/XML** — arbitrary nesting. **The famous Stack Overflow answer is correct**, and this is the theorem behind it
- **JSON** — nested objects and arrays
- **Source code** — nested blocks, balanced brackets
- **Any recursive structure**

**A regex is exactly right for:**

- **Tokenising** — identifiers, numbers, string literals. **This is what lexers are** → [[foundations/compilers/02-lexical-analysis|Lexical Analysis]]
- **Validating flat formats** — dates, postcodes, simple patterns
- **Search and replace** on unstructured text
- **Log filtering**

> **The rule: if the structure can nest arbitrarily, you need at least a stack, which means a parser.** → [[foundations/theory-of-computation/04-context-free-languages|Context-Free Languages]]
>
> **And the corollary people miss:** reaching for a regex on nested input doesn't produce a slightly-wrong solution that you can patch. It produces one that is wrong on inputs you haven't imagined, permanently. **The right move is to switch tools, not to add another special case to the pattern.**

**Email validation** is the recurring cautionary tale. RFC 5322 permits nested comments, so **a fully-correct email regex does not exist**. The practical answer — used by every serious system — is a loose sanity check plus sending a confirmation link. **The theory tells you to stop trying.**

## Practical notes

**Regular languages are cheap.** DFA matching is $O(n)$ in input length with $O(1)$ memory — one pass, one integer of state. **Nothing beats that**, which is why lexers are fast and why finite automata are used in hardware and hot paths.

**Know your engine.** POSIX/RE2/Rust are true regular engines with linear guarantees. PCRE/Perl/Python/Java add backreferences, exceeding regular and risking exponential time. → [[foundations/theory-of-computation/02-finite-automata|Catastrophic backtracking]]

**Compile once, match many.** Building the automaton is the expensive part.

**Ask "does this nest?" first.** It's the one question that decides regex versus parser, and it takes five seconds.

---

## Related
- [[foundations/theory-of-computation/02-finite-automata|Finite Automata]] — the machines
- [[foundations/theory-of-computation/04-context-free-languages|Context-Free Languages]] — what you need when this isn't enough
- [[foundations/compilers/02-lexical-analysis|Lexical Analysis]] — regular languages, industrially
- [[foundations/theory-of-computation/README|Theory of computation map]]
