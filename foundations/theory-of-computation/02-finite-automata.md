# Finite Automata

**[Intermediate]** — Machines with no memory beyond their current state, and why that's enough for lexers, protocols and UI logic.

## The machine

**A finite automaton is a fixed set of states, transitions on input symbols, and nothing else.** No memory, no counter, no stack — **the current state is all it knows.**

Formally, a **DFA** is $(Q, \Sigma, \delta, q_0, F)$:

| | |
|---|---|
| $Q$ | finite set of states |
| $\Sigma$ | input alphabet |
| $\delta: Q\times\Sigma \to Q$ | transition function |
| $q_0$ | start state |
| $F \subseteq Q$ | accepting states |

**Read the input one symbol at a time, following transitions. Accept if you end in $F$.**

A DFA accepting binary strings with an even number of 1s:

```
        1
   ┌─────────┐
   ▼         │
 ((even))   (odd)
   │         ▲
   └─────────┘
        1
   (0 loops on both)
```

**Two states. That's the entire machine**, and it correctly handles inputs of any length — because "even so far" is all you need to remember.

> **The defining constraint: a machine with $n$ states can distinguish at most $n$ situations.** It cannot count beyond $n$, because counting to $n+1$ requires $n+1$ distinguishable states. **That single observation is what limits regular languages**, and it's the whole content of the pumping lemma. → [[foundations/theory-of-computation/03-regular-languages|Regular Languages]]

## Nondeterministic automata

An **NFA** relaxes two things: a state may have **several transitions** on the same symbol, and may have **$\epsilon$-transitions** taken without consuming input.

$$\delta: Q\times(\Sigma\cup\{\epsilon\}) \to \mathcal{P}(Q)$$

**It accepts if *any* path through the choices ends in an accepting state.**

**NFAs are much easier to construct.** "Strings ending in `ab`" as an NFA: loop on everything at the start, then guess when the `ab` begins. As a DFA you must track how much of `ab` you've seen and handle every failure case explicitly.

### They're equally powerful

**The result that makes NFAs safe to use:**

> **Every NFA has an equivalent DFA.** Nondeterminism adds convenience, not power, at this level.

**The subset construction** proves it: **each DFA state is a *set* of NFA states** — "all the states the NFA could be in right now". Determinism is recovered by tracking the whole possibility set at once.

**The cost:** $n$ NFA states can become up to $2^n$ DFA states. **Usually far fewer in practice**, but the exponential blowup is real and achievable — and it's why some regex engines are slow. → [[foundations/compilers/02-lexical-analysis|Lexical Analysis]]

**DFA minimisation** then finds the unique smallest equivalent DFA, by merging states that can't be distinguished by any suffix (Hopcroft's algorithm, $O(n\log n)$).

> **The minimal DFA is unique up to renaming** — a genuinely elegant result, and it comes from **Myhill–Nerode**: the states of the minimal DFA *are* the equivalence classes of "strings that behave identically from here on". [[foundations/discrete-math/04-sets-relations-and-functions|Equivalence relations]] doing real work.

## Regular expressions are the same thing

**Kleene's theorem:**

$$\text{regular expression} \equiv \text{NFA} \equiv \text{DFA}$$

**All three describe exactly the regular languages.** The conversions are constructive:

**Regex → NFA** is **Thompson's construction** — build a small NFA per operator and glue them:

```
concatenation ab :   →(a)→(b)→
alternation a|b :    →ε→(a)→ε→
                      └ε→(b)→ε┘
Kleene star a*  :    →ε→((a))→ε→   with a loop back
```

**NFA → DFA** is the subset construction. **DFA → regex** is state elimination.

> **So a regex engine is compiling a pattern into an automaton and running it.** That's not a metaphor — it's literally the implementation, and knowing it explains the performance characteristics below.

**Important caveat:** modern "regex" libraries include **backreferences** (`\1`) and lookahead, and **backreferences are not regular** — they can match $\{ww\}$, which no finite automaton can. **PCRE-style regex is strictly more powerful than regular expressions, and pays for it in worst-case exponential time.**

**RE2, Go's `regexp`, and Rust's `regex` deliberately omit backreferences** to guarantee linear time. That's the trade, made explicitly.

## Catastrophic backtracking

**The practical consequence worth knowing**, because it's a real availability bug.

A backtracking engine matching `(a+)+b` against `aaaaaaaaaaaaaaaaaaaaaaaaX` tries **exponentially many** ways to split the `a`s before failing.

**20 characters can take seconds. 30 can take hours.**

> **ReDoS** — regular expression denial of service — is this, weaponised. A user-supplied string against a vulnerable pattern hangs a request thread. **It has taken down Stack Overflow (2016) and Cloudflare (2019).**
>
> **The fix:** use a non-backtracking engine (RE2, Rust's `regex`, Go's `regexp`), which is guaranteed $O(nm)$ because it simulates the NFA directly rather than backtracking. **Or avoid nested quantifiers** — `(a+)+`, `(a*)*`, `(a|a)*` — and set a timeout. **Never run a user-supplied regex in a backtracking engine.**

## Variants

**Moore machine** — output attached to states. **Mealy machine** — output attached to transitions. **Same power**, different convenience; both are standard in hardware design. → [[hardware/02-digital-and-analog|Digital and Analog]]

**Transducers** map input strings to output strings rather than accepting/rejecting — the basis of `sed`-style tools and of morphological analysis in NLP.

**Two-way automata** can move the head both directions. **Surprisingly, no extra power** — still exactly regular.

## Where finite automata actually appear

**More places than people expect**, and the pattern is: whenever the state you need is bounded, this is the right tool.

**Lexical analysis.** A lexer is a DFA. `flex` and friends take token patterns as regexes, build an NFA, determinise, minimise, and emit a table-driven DFA. **This is the single biggest industrial application.** → [[foundations/compilers/02-lexical-analysis|Lexical Analysis]]

**Protocol state machines.** [[foundations/networking/07-tcp-reliability-and-flow-control|TCP's connection state machine]] — LISTEN, SYN_SENT, ESTABLISHED, FIN_WAIT — is a finite automaton, and it's specified as one in the RFC. So is TLS handshake state.

**UI and workflow state.** Order states, form wizards, game AI. **Making the state machine explicit** (XState, or a hand-rolled enum + transition table) turns "which booleans are set" into "which state are we in", and eliminates the impossible-combination bugs that boolean soup creates.

**Text search.** Aho–Corasick builds an automaton matching many patterns in one pass — what `grep -F` and intrusion-detection signature matching use.

**Hardware.** Control units, bus arbiters, traffic lights. **FSM is the fundamental design pattern in digital logic**, and Verilog/VHDL have idioms specifically for it.

**Model checking.** System states as automaton states; verify properties by exhaustive exploration.

**Embedded systems.** No dynamic allocation, bounded memory, predictable timing — **a table-driven FSM is ideal**. → [[hardware/03-embedded-systems|Embedded Systems]]

## What they cannot do

**The limits, stated plainly:**

**Cannot count without bound.** $\{a^nb^n\}$ — matching numbers of `a`s and `b`s — needs unbounded memory.

**Cannot match nested structure.** Balanced parentheses, nested HTML tags, JSON. **This is why parsing HTML with a regex is provably impossible**, not merely inadvisable — nesting is unbounded and finite state isn't.

**Cannot compare arbitrary substrings.** $\{ww\}$ — a string repeated.

**But:** if the nesting depth is *bounded* — say at most 3 levels — it becomes regular again, with a lot of states. **The limit is unbounded structure, not structure**, which is a distinction worth keeping straight when someone says "you can't parse that with a regex".

**Proving a language isn't regular** is the pumping lemma, in the next note.

## Practical notes

**Make the state explicit.** Replacing five booleans with one enum eliminates $2^5 - k$ impossible states by construction. **This is one of the highest-value refactorings available**, and it's applied automata theory.

**Draw the diagram.** A state machine you can see is one you can check for missing transitions.

**Handle every (state, input) pair**, including the invalid ones. An unhandled transition is a bug waiting for unusual input.

**Table-driven beats nested switches** past a handful of states — easier to verify, easier to generate, and often faster.

**Prefer a linear-time regex engine** for anything touching user input.

---

## Related
- [[foundations/theory-of-computation/03-regular-languages|Regular Languages]] — what these recognise, and the limits
- [[foundations/compilers/02-lexical-analysis|Lexical Analysis]] — the industrial application
- [[foundations/theory-of-computation/04-context-free-languages|Context-Free Languages]] — the next level up
- [[foundations/theory-of-computation/README|Theory of computation map]]
