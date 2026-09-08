# Logic

**[Beginner]** — Propositions, predicates, quantifiers, and the difference between an argument that's valid and one that's merely persuasive.

## Propositional logic

A **proposition** is a statement that is either true or false. "It is raining." "$x > 5$" is not a proposition until you know $x$.

**The connectives**, and note that three of them behave exactly like operators you already use:

| Symbol | Name | Code | True when |
|---|---|---|---|
| $\neg p$ | negation | `!p` | $p$ is false |
| $p \wedge q$ | conjunction | `p && q` | both |
| $p \vee q$ | disjunction | `p \|\| q` | at least one (**inclusive**) |
| $p \to q$ | implication | — | **$p$ false, or $q$ true** |
| $p \leftrightarrow q$ | biconditional | `p == q` | same truth value |

**$\vee$ is inclusive or.** English "or" is often exclusive ("tea or coffee"); mathematical or is not. XOR is written $\oplus$.

## Implication is the strange one

$p \to q$ — "if $p$ then $q$" — is where everyone stumbles, and it's worth stopping on.

| $p$ | $q$ | $p \to q$ |
|---|---|---|
| T | T | **T** |
| T | F | **F** |
| F | T | **T** ← surprising |
| F | F | **T** ← surprising |

**When $p$ is false, $p \to q$ is true regardless of $q$.** This is *vacuous truth*.

> "If the moon is made of cheese, then I am the king of France" is **true**.

**Why it's defined this way:** an implication claims *only* that you can't have $p$ true and $q$ false. It makes no claim about what happens when $p$ is false, and a claim that says nothing is not violated.

**It's less strange in code than it looks.** Consider:

```
for (x in emptyList) { assert(f(x)) }
```

This passes. **"All elements satisfy $f$" is true of an empty list** — vacuously, because there's no counterexample. Every `all()` on an empty collection returns `true`, in every language, for exactly this reason.

**And the key identity:**

$$p \to q \equiv \neg p \vee q$$

Which is how you'd implement it: `!p || q`. **Implication isn't a mysterious new operation — it's shorthand for a disjunction.**

### Converse, inverse, contrapositive

Given $p \to q$:

| | Form | Equivalent to original? |
|---|---|---|
| **Converse** | $q \to p$ | **No** |
| **Inverse** | $\neg p \to \neg q$ | **No** |
| **Contrapositive** | $\neg q \to \neg p$ | **Yes** |

$$\boxed{p \to q \equiv \neg q \to \neg p}$$

**"If it's raining, the ground is wet"** does *not* mean "if the ground is wet, it's raining" (the sprinkler). **It does mean "if the ground isn't wet, it isn't raining."**

**Two practical consequences:**

**Confusing a statement with its converse is the most common reasoning error there is** — in code review, in debugging, in medical statistics, everywhere. "All bugs of this type show symptom X" does not mean "symptom X means this bug type".

**The contrapositive is a proof technique.** If proving $p \to q$ directly is awkward, prove $\neg q \to \neg p$ instead — it's the same statement and is often much easier. → [[foundations/discrete-math/03-proof-techniques|Proof Techniques]]

## Equivalences worth knowing

**De Morgan's laws** — the ones you'll use constantly:

$$\neg(p \wedge q) \equiv \neg p \vee \neg q$$
$$\neg(p \vee q) \equiv \neg p \wedge \neg q$$

**Negating an AND gives an OR, and vice versa.** This is why

```
if (!(a && b))     is      if (!a || !b)
```

and getting it wrong is a classic bug. **When you invert a compound condition, the connective flips too.**

The rest, briefly:

$$\text{Distribution: } p \wedge (q \vee r) \equiv (p\wedge q)\vee(p \wedge r)$$
$$\text{Double negation: } \neg\neg p \equiv p$$
$$\text{Contradiction: } p \wedge \neg p \equiv \text{F} \qquad \text{Tautology: } p \vee \neg p \equiv \text{T}$$

**Tautology** — true under every assignment. **Contradiction** — false under every assignment. **Satisfiable** — true under at least one.

> **That last word is doing a lot of work in practice.** Determining whether a propositional formula is satisfiable is **SAT**, the original NP-complete problem — and modern SAT solvers, despite the worst case being exponential, routinely handle formulas with millions of variables. They're what verify hardware designs, solve package-dependency resolution, and drive symbolic execution engines. → [[foundations/theory-of-computation/07-complexity-classes|NP-completeness]]

## Predicate logic

Propositional logic can't express "every integer has a successor" — you'd need infinitely many propositions. **Predicate logic adds variables and quantifiers.**

A **predicate** is a proposition with a variable: $P(x) = $ "$x$ is prime". Not true or false until $x$ is fixed or quantified.

**Universal:** $\forall x\, P(x)$ — "for all $x$, $P(x)$"

**Existential:** $\exists x\, P(x)$ — "there exists an $x$ such that $P(x)$"

$$\forall x \in \mathbb{Z},\ \exists y \in \mathbb{Z},\ y > x$$

"For every integer there's a larger one." **True.**

### Order matters, enormously

$$\forall x\, \exists y\, \text{Loves}(x,y) \quad\text{— everyone loves someone (possibly different people)}$$
$$\exists y\, \forall x\, \text{Loves}(x,y) \quad\text{— someone is loved by everyone (one specific person)}$$

**Completely different claims.** The second implies the first; the first does not imply the second.

> **This distinction shows up constantly in computing.** "For every input there's an algorithm that solves it quickly" (trivially true — hardcode the answer) versus "there's an algorithm that solves every input quickly" (the actual question). **Getting the quantifier order wrong turns a hard claim into a vacuous one.**
>
> It's also exactly the difference between $\epsilon$-$\delta$ definitions in analysis, and between "eventually consistent" and "always consistent" in [[architecture/04-distributed-systems/04-consistency-models|distributed systems]].

### Negating quantifiers

**The rule you'll use most**, and it's De Morgan generalised:

$$\neg\forall x\, P(x) \equiv \exists x\, \neg P(x)$$
$$\neg\exists x\, P(x) \equiv \forall x\, \neg P(x)$$

**"Not everything is $P$" means "something is not $P$".** To disprove a universal claim, produce **one counterexample**. To disprove an existential claim, you must show *nothing* works — much harder.

**This asymmetry is why bugs are easy to demonstrate and correctness is hard to establish.** A test is a search for a counterexample to "the code is always right".

**Mechanically:** to negate, walk inward flipping every quantifier and negating the body.

$$\neg\left[\forall x\,\exists y\, (x < y)\right] \equiv \exists x\,\forall y\, (x \geq y)$$

## Arguments and validity

An **argument** is premises plus a conclusion. It's **valid** if the conclusion follows necessarily — whenever the premises are all true, the conclusion must be.

> **Validity is about form, not truth.** A valid argument from false premises can reach a false conclusion. A **sound** argument is valid *and* has true premises — that's what you actually want.

**The rules of inference**, which are just named valid patterns:

| Name | From | Conclude |
|---|---|---|
| **Modus ponens** | $p \to q$, $p$ | $q$ |
| **Modus tollens** | $p \to q$, $\neg q$ | $\neg p$ |
| **Hypothetical syllogism** | $p\to q$, $q\to r$ | $p \to r$ |
| **Disjunctive syllogism** | $p \vee q$, $\neg p$ | $q$ |

**And the two invalid patterns that look valid** — worth being able to name, because they're the errors people actually make:

**Affirming the consequent:** from $p \to q$ and $q$, concluding $p$. *Invalid.* "The tests pass, therefore the code is correct" — tests passing is a consequence of correctness, not evidence sufficient for it.

**Denying the antecedent:** from $p \to q$ and $\neg p$, concluding $\neg q$. *Invalid.* "We didn't deploy, so it can't be our fault."

**Both are the converse/inverse confusion from earlier, in argument form.** Recognising them is one of the more directly useful things in this note.

## Where logic shows up in computing

**Boolean expressions** — directly, and De Morgan is how you simplify them.

**Digital circuits** — AND/OR/NOT gates *are* the connectives in silicon. Circuit minimisation is logical simplification. → [[hardware/02-digital-and-analog|Digital and Analog]]

**Type systems** — the **Curry–Howard correspondence** says *propositions are types and proofs are programs*. A function of type `A → B` is a proof that $A$ implies $B$. This isn't an analogy; it's an isomorphism, and it's the foundation of proof assistants like Coq, Lean and Agda. → [[foundations/compilers/05-type-systems-and-checking|Type Systems]]

**SQL `WHERE` clauses** — predicate logic, and `NULL` introduces a genuine third truth value, which is why `NULL = NULL` is neither true nor false and catches people out. → [[databases/database-design-reference|Databases]]

**Formal verification** — TLA+, model checkers, SMT solvers. Specifying "this can never happen" precisely enough to check exhaustively. → [[architecture/04-distributed-systems/15-testing-distributed-systems|Testing Distributed Systems]]

**Preconditions, postconditions, invariants** — design by contract is applied predicate logic.

---

## Related
- [[foundations/discrete-math/03-proof-techniques|Proof Techniques]] — using this to establish things
- [[foundations/discrete-math/04-sets-relations-and-functions|Sets, Relations and Functions]] — the objects logic talks about
- [[foundations/theory-of-computation/07-complexity-classes|Complexity Classes]] — where SAT becomes central
- [[foundations/discrete-math/README|Discrete maths map]]
