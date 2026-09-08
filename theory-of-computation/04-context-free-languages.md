# Context-Free Languages

**[Intermediate]** — Add a stack and you can handle nesting. The level where programming languages live.

## Context-free grammars

A **CFG** is a set of production rules $(V, \Sigma, R, S)$ — variables, terminals, rules, start symbol. **Every rule has a single variable on the left:**

$$A \to \alpha$$

**"Context-free" means exactly that:** a variable can be replaced regardless of what surrounds it. In a context-sensitive grammar, the left side can carry context.

Balanced parentheses:

$$S \to (S) \mid SS \mid \epsilon$$

**Three rules, and it handles arbitrary nesting** — which no regular expression can. **The recursion in the rule is where the power comes from.**

Simple arithmetic:

$$E \to E + T \mid T \qquad T \to T \times F \mid F \qquad F \to (E) \mid \text{num}$$

**The layering is deliberate**: it encodes precedence (× binds tighter than +) and associativity (left-recursive rules give left associativity). **That's how a grammar expresses precedence** — not as a separate table, but in its shape. → [[foundations/compilers/03-parsing|Parsing]]

## Derivations and parse trees

A **derivation** applies rules from $S$ until only terminals remain. **The parse tree** records the structure, and the tree is what you actually want — it *is* the meaning.

```
      E                 for  2 + 3 × 4
     /|\
    E + T
    |  /|\
    T T × F
    | |   |
    F 3   4
    |
    2
```

**The tree says $3\times4$ groups first.** Flat text doesn't; the tree does.

**Ambiguity** — a grammar is ambiguous if some string has **two distinct parse trees.**

$$E \to E + E \mid E \times E \mid \text{num}$$

This parses `2 + 3 × 4` two ways: $(2+3)\times4$ and $2+(3\times4)$. **Different meanings, same input.** The layered grammar above avoids it by construction.

> **The dangling else** is the ambiguity every language has to resolve:
>
> `if a then if b then x else y` — which `if` owns the `else`?
>
> **Every mainstream language picks "nearest `if`"**, either by rewriting the grammar or by a parser-generator precedence declaration. It's the reason some style guides mandate braces always.

**And a hard fact:** **ambiguity of a CFG is undecidable.** No algorithm can tell you in general whether a grammar is ambiguous — you find out when your parser reports a conflict. **Some languages are *inherently* ambiguous**: no unambiguous grammar exists for them at all. → [[foundations/theory-of-computation/06-decidability|Decidability]]

## Pushdown automata

**An NFA plus a stack.**

$$\delta: Q \times (\Sigma\cup\{\epsilon\}) \times \Gamma \to \mathcal{P}(Q\times\Gamma^*)$$

Each move reads an input symbol (or none), pops a stack symbol, and pushes a string.

**The stack is exactly what regular languages lacked.** For $\{a^nb^n\}$: push on every `a`, pop on every `b`, accept if the stack empties exactly when input does. **Unbounded counting, with one stack.**

> **PDAs and CFGs are equivalent** — every CFG has a PDA and vice versa. Same relationship as regex to finite automaton, one level up.

**The crucial asymmetry with finite automata:**

| | Nondeterminism adds power? |
|---|---|
| Finite automata | **No** — NFA ≡ DFA |
| **Pushdown automata** | **Yes** — NPDA ⊋ DPDA |

**Deterministic PDAs are strictly weaker.** Even-length palindromes need a nondeterministic PDA — you must *guess* the midpoint, and a deterministic machine can't.

**Why this matters practically:** real parsers are deterministic, so **they handle DCFLs, not all CFLs.** LL and LR grammars are restrictions chosen precisely to be deterministically parsable. **When a parser generator reports a shift/reduce conflict, it's telling you your grammar left the deterministic fragment.** → [[foundations/compilers/03-parsing|Parsing]]

**And DCFLs are closed under complement while general CFLs are not** — one more reason determinism is a meaningful dividing line.

## Closure properties

**Notably worse than regular languages:**

| Operation | CFL closed? |
|---|---|
| Union, concatenation, star | ✓ |
| **Intersection** | ✗ |
| **Complement** | ✗ |
| Intersection with a **regular** language | ✓ |

**The counterexample for intersection:**

$$\{a^nb^nc^m\} \cap \{a^mb^nc^n\} = \{a^nb^nc^n\}$$

**Both are context-free; the intersection is not.** You can match one pair with a stack, not two independent pairs.

**That last row is genuinely useful** — CFL ∩ regular is still a CFL, which is why you can layer a regular filter on a parser without leaving the class.

## The pumping lemma for CFLs

Same idea as [[foundations/theory-of-computation/03-regular-languages|the regular version]], but you pump **two** substrings, because a parse tree deep enough must repeat a variable — and that gives a loop in the *tree*, which grows on both sides.

> If $L$ is context-free, there's $p$ such that any $s\in L$ with $|s|\geq p$ splits as $s = uvxyz$ with $|vy|>0$, $|vxy|\leq p$, and $uv^ixy^iz \in L$ for all $i\geq0$.

**Proving $\{a^nb^nc^n\}$ isn't context-free:** take $s = a^pb^pc^p$. Since $|vxy|\leq p$, the pumped parts $v$ and $y$ span at most two of the three letter blocks. **Pumping raises the count of at most two letters, so the three counts can't stay equal.** Contradiction.

## What's context-free and what isn't

**Context-free:**
- Balanced brackets, nested structures
- **Most of a programming language's syntax**
- JSON, XML structure
- Arithmetic expressions

**Not context-free:**
- $\{a^nb^nc^n\}$ — three-way agreement
- $\{ww\}$ — copying an arbitrary string
- **Declare-before-use**, and type correctness

> **That last one is the practically important one.** **No programming language is truly context-free.** "Every variable must be declared before use" requires remembering an unbounded set of names and checking membership — a stack can't do it.
>
> **So real compilers use a CFG for syntax and a separate semantic pass for the rest.** Parsing gives you the tree; **name resolution and type checking are deliberately not the parser's job**, because they can't be. That split isn't an engineering convenience — it's forced by the hierarchy. → [[foundations/compilers/04-asts-and-semantic-analysis|Semantic Analysis]]

**C's famous case:** `A * B;` is a declaration if `A` is a type and a multiplication otherwise. **The grammar cannot decide** — hence the "lexer hack", where the symbol table feeds back into the lexer. An ugly, well-known consequence of trying to parse a non-context-free language with a CFG.

## Parsing algorithms

**How you actually recognise these**, and the trade is generality against speed:

| Algorithm | Handles | Time |
|---|---|---|
| **Recursive descent** | LL(k), hand-written | $O(n)$ |
| **LL(k)** | top-down, predictive | $O(n)$ |
| **LR(1) / LALR** | bottom-up, **most languages** | $O(n)$ |
| **Pratt** | expressions with precedence | $O(n)$ |
| **Earley** | **any CFG, including ambiguous** | $O(n^3)$, $O(n^2)$ unambiguous |
| **CYK** | any CFG in CNF | $O(n^3)$ |
| **GLR** | any CFG, forks on conflict | $O(n^3)$ worst, near-linear typical |

**The practical answer:** hand-written recursive descent plus Pratt for expressions. **Every major compiler does this** — GCC, Clang, Rust, Go — because error messages and context-sensitivity matter more than generator convenience. → [[foundations/compilers/03-parsing|Parsing]]

**$O(n^3)$ general parsing exists** and is used where grammars are genuinely ambiguous — natural language, and reverse-engineering legacy syntax.

**Chomsky Normal Form** ($A\to BC$ or $A\to a$) is what CYK requires; every CFG can be converted. **Useful for proofs, not for practice.**

## Beyond context-free

**Context-sensitive** ($\alpha A\beta \to \alpha\gamma\beta$) recognised by linear bounded automata. Handles $\{a^nb^nc^n\}$ and $\{ww\}$.

**Rarely used directly** — the parsing complexity is PSPACE-complete, so it's a theoretical waypoint rather than a tool. **Real systems use a CFG plus arbitrary code**, which is simpler and strictly more powerful.

**Parsing expression grammars (PEGs)** are the modern alternative worth knowing: **ordered choice** makes them unambiguous by construction, and with memoisation (packrat parsing) they run in linear time. **They can express some non-context-free languages** via syntactic predicates. The catch is that ordered choice can silently hide alternatives — the second option is never tried if the first succeeds, so a mis-ordered grammar fails quietly rather than reporting a conflict.

---

## Related
- [[foundations/compilers/03-parsing|Parsing]] — the industrial application
- [[foundations/theory-of-computation/03-regular-languages|Regular Languages]] — the level below
- [[foundations/theory-of-computation/05-turing-machines|Turing Machines]] — the level above
- [[foundations/theory-of-computation/README|Theory of computation map]]
