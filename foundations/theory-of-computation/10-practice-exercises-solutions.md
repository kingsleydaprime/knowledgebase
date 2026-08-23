# Practice Exercises — Solutions

> **[Intermediate → Advanced]** · Worked answers to [[foundations/theory-of-computation/09-practice-exercises|note 09]].

---

## Part A — Automata and regular languages

### 1. Three DFAs

**(a) Even number of 0s.** Two states: $q_{even}$ (accepting), $q_{odd}$. `0` flips; `1` self-loops. **The state *is* the parity** — that's the design principle: a DFA's state set is exactly the information you must remember.

**(b) Divisible by 3.** Three states $q_0,q_1,q_2$ = the remainder mod 3 so far. Reading a bit $b$ doubles the value and adds $b$, so $q_r \xrightarrow{b} q_{(2r+b) \bmod 3}$. Start and accept at $q_0$.

**This is the one worth doing.** It shows a finite machine handling arbitrarily large numbers — because it never stores the number, only the residue. **Bounded memory, unbounded input** is the whole idea of the model.

**(c) Contains `101`.** Four states tracking the longest prefix of `101` matched so far: none / `1` / `10` / `101` (accepting, absorbing). **This is exactly what Knuth–Morris–Pratt builds** → [[foundations/dsa/README|DSA]].

### 2. Subset construction

Each DFA state is a *set* of NFA states. Start with $\{q_0\}$ (plus $\varepsilon$-closure), and for each symbol take the union of the NFA transitions.

**Worst case is $2^n$ DFA states from $n$ NFA states**, and it's achieved: $L_k = $ "strings whose $k$-th symbol from the end is `1`" needs an NFA of $k{+}1$ states and a DFA of $2^k$ — because a DFA must remember the last $k$ symbols, and there are $2^k$ possibilities.

**Why it matters practically:** it's the trade behind regex engines. A DFA matches in $O(n)$ but may take exponential space to build; simulating the NFA directly costs $O(nm)$ time and linear space. **`grep` and RE2 choose the NFA simulation; backtracking engines choose neither and get exponential *time*** → exercise 13.

### 3. $\{a^nb^n\}$ is not regular

**The quantifier order is the proof**, so state it explicitly:

Assume $L$ regular. The pumping lemma gives a $p$ (**adversary chooses**). Choose $w = a^pb^p$ (**you choose**, and $|w| \ge p$). The adversary decomposes $w = xyz$ with $|xy| \le p$ and $|y| \ge 1$ (**adversary chooses**). Since $|xy| \le p$, both $x$ and $y$ lie entirely within the leading $a$s, so $y = a^k$ for some $k \ge 1$. Choose $i = 2$ (**you choose**). Then $xy^2z = a^{p+k}b^p$, which has more $a$s than $b$s, so $\notin L$. Contradiction. ∎

**You choose $w$ and $i$; the adversary chooses $p$ and the decomposition.** Your $w$ must work against *every* legal decomposition — that's why $a^pb^p$ is chosen so that $|xy| \le p$ traps $y$ inside the $a$s.

### 4. Pump the wrong thing

Try it on $\{a^nb^m\}$ (all $a$s before all $b$s, counts unrelated — this **is** regular, matched by `a*b*`).

Take $w = a^pb^p$, and again $y = a^k$. Pump: $a^{p+k}b^p$. **Still in the language** — $n$ and $m$ need not be equal. No contradiction. The proof simply fails to close.

**The lesson: the pumping lemma is a one-way tool.** It gives a *necessary* condition for regularity, not a sufficient one. Failing to derive a contradiction proves nothing — and there are non-regular languages that satisfy the pumping condition anyway. **To prove regularity you must exhibit a DFA, regex or right-linear grammar; the Myhill–Nerode theorem is the tool that characterises it exactly.**

### 5. Closure as construction

**Intersection — the product construction.** States are pairs $(q_1,q_2)$; run both machines in lockstep; accept when **both** accept. **$|Q_1| \times |Q_2|$ states.** Union is identical but accepts when *either* does.

**Complement of a DFA: swap accepting and non-accepting states.** Trivial — but only because a DFA is *total and deterministic*, so every string has exactly one run.

**For an NFA this fails.** A string may have both accepting and rejecting runs, so swapping accept states gives the wrong language. You must determinise first — and pay the $2^n$ from exercise 2. **That asymmetry is why regex engines supporting negation can blow up.**

$L_1 \setminus L_2 = L_1 \cap \overline{L_2}$.

---

## Part B — Context-free

### 6. Two grammars

**Balanced parentheses:** $S \to (S) \mid SS \mid \varepsilon$
**Palindromes:** $P \to aPa \mid bPb \mid a \mid b \mid \varepsilon$

**Both need the stack that a DFA lacks** — matching nested structure requires unbounded counting, which is exactly what the pumping lemma rules out for regular languages.

### 7. Ambiguity

`1 + 2 * 3` has two parse trees under $E \to E+E \mid E\times E \mid \text{num}$: one grouping $(1+2)\times3 = 9$, one grouping $1+(2\times3) = 7$. **The grammar doesn't say which**, so the language is ambiguous and the "meaning" is undefined.

Stratify by precedence:
$$E \to E + T \mid T \qquad T \to T \times F \mid F \qquad F \to (\,E\,) \mid \text{num}$$

Now `1 + 2 * 3` has exactly one tree, yielding 7. **Left recursion ($E \to E+T$) gives left-associativity**; the layering gives precedence.

**This is what you do every time you write a grammar for a parser generator**, and the shift/reduce conflicts such tools report are ambiguity being detected mechanically → [[foundations/compilers/03-parsing|parsing]].

### 8. $\{a^nb^nc^n\}$ is not context-free

The CFL pumping lemma gives $p$; take $w = a^pb^pc^p$; the adversary picks $w = uvxyz$ with $|vxy| \le p$ and $|vy| \ge 1$.

**Because $|vxy| \le p$, the window cannot span both $a$s and $c$s** (they're $p$ symbols apart). So:

- $vxy$ within one letter block ⇒ pumping changes one count, breaking equality
- $vxy$ straddles $a$/$b$ ⇒ pumping changes $a$s and/or $b$s but **never $c$s**
- $vxy$ straddles $b$/$c$ ⇒ never touches $a$s

In every case $uv^2xy^2z \notin L$. ∎

**The case analysis *is* the proof**, and the $|vxy| \le p$ constraint is what makes it finite. A pushdown automaton has one stack: it can match $a$s against $b$s, but by then it's popped the information it would need for the $c$s.

---

## Part C — Computability and complexity

### 9. Turing machine for $\{a^nb^n\}$

The standard algorithm: mark the leftmost unmarked `a` (write `X`), scan right to the leftmost unmarked `b` (write `Y`), return left, repeat. Accept when no unmarked `a` and no unmarked `b` remain.

On `aabb`: `XabY` → `XXYY` → accept.
On `aab`: `XaYb`... second pass marks the remaining `a`, finds no unmarked `b`, **rejects**.

**The tape is the unbounded memory a PDA's stack couldn't provide in the right shape** — and note it does this in $O(n^2)$ steps, which is a first taste of complexity distinct from computability.

### 10. Halting problem

Assume a total decider $H(M, x)$ returning *halts* / *loops*. Build:

```
D(M):  if H(M, M) says "halts":  loop forever
       else:                     halt
```

Now run $D(D)$:

- If $H$ says $D(D)$ halts, then $D$ loops ⇒ it doesn't halt. Contradiction.
- If $H$ says $D(D)$ loops, then $D$ halts. Contradiction.

So $H$ cannot exist. ∎

**The one-sentence version:** *$D$ is built to do the opposite of whatever it's predicted to do, so asking it about itself makes the prediction self-refuting.*

**Same shape as Russell's paradox and Cantor's diagonal** — self-reference plus negation. And it's not an artefact: Rice's theorem generalises it to **every** non-trivial semantic property of programs, which is why perfect static analysis of program behaviour is impossible in principle, not merely hard → [[foundations/compilers/README|compilers]].

### 11. Reduce: "does this TM print `z`?"

**Direction matters.** To prove PRINTS-Z undecidable, assume it *is* decidable and use it to decide HALTING.

Given $\langle M, x\rangle$, build $M'$: run $M$ on $x$ with `z` erased from the alphabet (or renamed), and if $M$ ever halts, **then** print `z`.

$M'$ prints `z` $\iff$ $M$ halts on $x$. So a decider for PRINTS-Z gives a decider for HALTING, which doesn't exist. ∎

**The common error is reducing the wrong way** — showing PRINTS-Z reduces *to* HALTING proves nothing about PRINTS-Z's difficulty. **You must reduce the known-hard problem *to* the new one**: "if I could solve yours, I could solve this known-impossible one."

### 12. 3-SAT ⇒ VERTEX COVER

Given a 3-CNF formula with $n$ variables and $m$ clauses:

- **Variable gadget:** for each variable, two vertices $x_i$, $\lnot x_i$ joined by an edge. Covering it requires ≥1 vertex — that's the truth assignment
- **Clause gadget:** for each clause, a triangle of three vertices labelled with its literals. A triangle requires ≥2 vertices
- **Connection:** edge from each clause-triangle vertex to the matching literal vertex
- **Set $k = n + 2m$**

**(⇒)** Given a satisfying assignment: take the true literal from each variable pair ($n$), and from each triangle take the two vertices whose literals are *false* ($2m$). Each connecting edge is covered — either by its triangle endpoint, or, for the one literal left out, by the variable vertex, which is true because the clause is satisfied. Total $n+2m$. ✓

**(⇐)** Given a cover of size $n+2m$: the gadgets force exactly 1 per variable pair and exactly 2 per triangle, with nothing spare. Read the assignment off the variable vertices. The uncovered triangle vertex's connecting edge must be covered by its variable vertex, so that literal is true, so the clause is satisfied. ✓ ∎

**Both directions are required.** One direction shows only that a solution maps across; the other shows no *spurious* solutions appear. A "reduction" with one direction is a common and fatal error.

---

## Part D — Build it

### 13. The regex engine

Thompson's construction builds an NFA compositionally: literals are two states and an edge; concatenation joins them; alternation adds a branching start; `*` adds $\varepsilon$-loops. Subset construction determinises. Simulation walks the DFA in **$O(n)$ in the input**, independent of the pattern's shape.

**The payoff is the comparison.** On `(a+)+$` against `"a"*28 + "b"`:

| | time |
|---|---|
| Python `re` (backtracking) | **23 seconds** |
| Your Thompson NFA/DFA | **microseconds** |

**Same regex. Same input. Different algorithm.** A backtracking engine explores exponentially many decompositions; an automaton tracks the *set* of reachable states, and there are only finitely many. That's why RE2 and Go's `regexp` are linear-time by construction — and why they refuse backreferences, which take the language beyond regular → [[languages/06-python/16-regular-expressions|regular expressions]] · [[build-your-own-x/09-your-own-regex-engine|build your own]].

**Finishing this exercise makes the whole course concrete**: you will have built the regex ≡ NFA ≡ DFA equivalence rather than read it.

### 14. DPLL

Unit propagation (a clause with one unassigned literal forces it), pure literal elimination (a variable appearing in one polarity can be set freely), then branch and recurse.

**Unit propagation is by far the biggest win** — typically the difference between minutes and milliseconds. Modern CDCL solvers add clause learning (on conflict, derive a new clause that prevents repeating the mistake) and non-chronological backtracking.

**The practical upshot, which is the reason this exercise is here:** SAT is NP-complete, and industrial solvers routinely handle instances with **millions** of variables. **NP-complete means no known polynomial *worst-case* algorithm — not that instances you meet are hard.** Confusing those two is the most common misuse of complexity theory in engineering arguments → [[foundations/theory-of-computation/07-complexity-classes|note 07]].

## Related
- [[foundations/theory-of-computation/09-practice-exercises|the exercises]]
- [[foundations/theory-of-computation/README|the course]]

*Source: [reference] — the 23-second figure measured on Python 3.14, August 2026.*
