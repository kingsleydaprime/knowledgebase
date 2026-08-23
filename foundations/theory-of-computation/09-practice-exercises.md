# Practice Exercises

> **[Intermediate → Advanced]** · Fourteen problems. **Three proofs from scratch, and two things to build.**

This course's own honest note names the gap precisely: the equivalences are *"described rather than derived"*. These derive them.

**Paper for A–C. A compiler for D.** Solutions in [[foundations/theory-of-computation/10-practice-exercises-solutions|note 10]].

---

## Part A — Automata and regular languages (notes 02–03)

**1. Build three DFAs.** Over $\Sigma = \{0,1\}$, construct a DFA accepting:
(a) strings with an even number of 0s
(b) strings whose binary value is divisible by 3
(c) strings containing `101` as a substring
**Done when:** each is drawn with every state's meaning **named in words**. (b) is the one worth the effort — the states are the remainders → [[foundations/theory-of-computation/02-finite-automata|note 02]].

**2. Subset construction.** Take an NFA for "strings ending in `01`" and convert it to a DFA by hand.
**Done when:** you can state the worst-case blow-up and give a language family that achieves it.

**3. Prove $\{a^n b^n\}$ is not regular.**
**Done when:** you've written a complete pumping-lemma proof **without looking**, including the quantifier structure — who chooses $p$, who chooses $w$, who chooses the decomposition, and who chooses $i$. **Getting that order wrong is the commonest way these proofs fail** → [[foundations/theory-of-computation/03-regular-languages|note 03]].

**4. Pump the wrong thing.**
Attempt a pumping-lemma "proof" that $\{a^nb^m : n,m \ge 0\}$ is non-regular. It *is* regular, so your proof must fail.
**Done when:** you can point at the exact step where it breaks. **This teaches more than exercise 3** — it shows the lemma is a one-way tool.

**5. Closure as a construction.** Given DFAs for $L_1$ and $L_2$, construct one for $L_1 \cap L_2$. Then for $L_1 \setminus L_2$.
**Done when:** you can say how many states the product has, and why complement is trivial for a DFA and awkward for an NFA.

---

## Part B — Context-free (note 04)

**6. Write two grammars.** For balanced parentheses, and for palindromes over $\{a,b\}$.

**7. Show ambiguity, then remove it.**
The grammar $E \to E + E \mid E \times E \mid \text{num}$ is ambiguous. Give a string with two distinct parse trees, then rewrite the grammar to enforce precedence and left-associativity.
**Done when:** your fixed grammar gives exactly one tree for `1 + 2 * 3`, and the tree matches arithmetic. **This is precisely what a parser generator makes you do** → [[foundations/compilers/03-parsing|parsing]].

**8. Prove $\{a^nb^nc^n\}$ is not context-free**, with the pumping lemma for CFLs.
**Done when:** you've handled every case for where the pumped substrings can sit — **the case analysis is the proof**.

---

## Part C — Computability and complexity (notes 05–08)

**9. Program a Turing machine.** Write the transition table for a TM that decides $\{a^nb^n\}$. Trace it on `aabb` and on `aab`.

**10. Prove the halting problem undecidable.** Full diagonalisation, from scratch.
**Done when:** you can explain **what goes wrong when the contradictory machine is run on itself** — in one sentence, to someone who hasn't seen it → [[foundations/theory-of-computation/06-decidability|note 06]].

**11. Reduce.** Prove that "does this TM ever print the letter `z`?" is undecidable by reducing the halting problem to it.
**Done when:** your reduction is in the **right direction** — this is where most attempts fail, and stating which problem you're assuming solvable is the check.

**12. One NP-completeness reduction.** Reduce 3-SAT to VERTEX COVER. Construct the graph, state $k$, and prove both directions.
**Done when:** you've proved *both* "satisfiable ⇒ cover exists" and "cover exists ⇒ satisfiable". **One direction is not a reduction** → [[foundations/theory-of-computation/07-complexity-classes|note 07]].

---

## Part D — Build it (the equivalences, made concrete)

**13. A regex engine.**
Implement Thompson's construction (regex → NFA), then subset construction (NFA → DFA), then simulate. Support `. * + ? | ()` and literals.
**Done when:** it matches correctly **and** you can demonstrate it running in linear time on the input that makes [[languages/06-python/16-regular-expressions|Python's `re`]] take 23 seconds — `(a+)+$` against `aaaa…b`. **That contrast is the entire payoff of this course.** → [[build-your-own-x/09-your-own-regex-engine|build your own regex engine]]

**14. A DPLL SAT solver.**
Unit propagation, pure literal elimination, and branching. Test it on a small graph-colouring instance encoded as CNF.
**Done when:** it solves instances a brute-force $2^n$ search can't, and you can state which heuristic bought the most.

---

## Related
- [[foundations/theory-of-computation/10-practice-exercises-solutions|Solutions]]
- [[foundations/theory-of-computation/README|the course]]
- [[foundations/compilers/README|compilers]] — where the CFG material gets used
- [[foundations/discrete-math/09-practice-exercises|discrete maths exercises]] — the proof technique underneath

*Source: [reference] — built from this course's own "what would close the gap" list.*
