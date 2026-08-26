# Practice Exercises

> **[Advanced]** · Twelve exercises. **PL theory is the one domain here where the exercises are mostly *implementations* — because an interpreter you wrote cannot lie to you about the semantics.**

**Paper for Part A. A language with algebraic data types for B–D** — Haskell, OCaml, Rust or Scala are natural; Python works with more typing.

Solutions in [[foundations/programming-language-theory/09-practice-exercises-solutions|note 09]].

---

## Part A — Lambda calculus (note 02)

**1. Reduce by hand.**
Beta-reduce to normal form: (a) $(\lambda x.\,x\,x)(\lambda y.\,y)$, (b) $(\lambda x.\lambda y.\,x)\,a\,b$, (c) $(\lambda x.\lambda y.\,x\,y)(\lambda z.\,z)\,w$.
**Done when:** each is fully reduced with **every substitution written out** → [[foundations/programming-language-theory/02-lambda-calculus|note 02]].

**2. Get capture wrong on purpose.**
Reduce $(\lambda x.\lambda y.\,x)\,y$ **naively**, without renaming. Then do it correctly with alpha-conversion.
**Done when:** you can show the naive result means something different, and state the rule that prevents it. **This is the bug every first substitution implementation has.**

**3. Church numerals.**
Define $0,1,2$ as Church numerals. Implement `succ` and `plus`, and verify $1+1=2$ by reduction.

**4. Y combinator.**
Verify $Y\,g \to g\,(Y\,g)$ by reduction, where $Y = \lambda f.(\lambda x.f(x\,x))(\lambda x.f(x\,x))$. Then explain why $Y$ does not terminate under **call-by-value**, and what $Z$ changes.
**Done when:** you can state why a language with strict evaluation needs a different fixpoint combinator → [[foundations/programming-language-theory/03-semantics|note 03]].

---

## Part B — Semantics (note 03)

**5. Write the rules, then the interpreter.**
For a language of integers, booleans, `+`, `if`, and variables: write **small-step** operational semantics as inference rules, then implement an evaluator that follows them exactly.
**Done when:** the code's structure mirrors the rules one-to-one. **If it doesn't, one of them is wrong.**

**6. Make evaluation order observable.**
Add a `print` side effect. Write a program whose output differs under call-by-value and call-by-name. Implement both.
**Done when:** you have two different outputs from one program, and can say which strategy Haskell, Python and Rust use → [[foundations/programming-language-theory/03-semantics|note 03]].

---

## Part C — Types (notes 04–05)

**7. Implement a type checker.**
Simply-typed lambda calculus: a bidirectional checker with a context $\Gamma$. Reject $(\lambda x{:}\text{Int}.\,x)\,\text{true}$.
**Done when:** it accepts well-typed terms and rejects ill-typed ones **with a useful message** → [[foundations/programming-language-theory/04-type-systems-formally|note 04]].

**8. Prove progress and preservation.**
For your language from exercise 5, state and prove both. **Preservation:** if $e : \tau$ and $e \to e'$ then $e' : \tau$. **Progress:** if $e : \tau$ then $e$ is a value or $e \to e'$.
**Done when:** you can explain, in one sentence, why the two together give *"well-typed programs don't get stuck"*.

**9. Implement Algorithm W.**
Hindley–Milner inference with unification. Infer the type of `λf.λx. f (f x)` with no annotations.
**Done when:** you get $(\alpha \to \alpha) \to \alpha \to \alpha$ **without being told**, and your unifier performs the **occurs check** → [[foundations/programming-language-theory/05-type-inference|note 05]].

**10. Break inference.**
Write a term that needs the occurs check to reject ($\lambda x.\,x\,x$), and one where let-polymorphism matters (a `let id = λx.x` used at two different types).
**Done when:** you can state why HM generalises at `let` but not at `λ`, and what that buys.

---

## Part D — Curry–Howard and effects (notes 06–07)

**11. Programs as proofs.**
Give the type corresponding to each and write an inhabiting term: $A \to (B \to A)$; $(A \to B) \to (B \to C) \to (A \to C)$; $A \land B \to A$. Then try $A \lor \lnot A$ and fail.
**Done when:** you can explain **why excluded middle has no inhabitant** in a constructive setting → [[foundations/programming-language-theory/06-curry-howard-and-proofs|note 06]].

**12. Linearity by hand.**
Write typing rules for a linear lambda calculus where every variable is used **exactly once**. Show $\lambda x.\,x\,x$ and $\lambda x.\lambda y.\,x$ are both rejected.
**Done when:** you can connect the rules to Rust's move semantics and say which Rust feature corresponds to weakening → [[foundations/programming-language-theory/07-effects-and-substructural-types|note 07]] · [[languages/03-rust/README|Rust]].

## Related
- [[foundations/programming-language-theory/09-practice-exercises-solutions|Solutions]]
- [[foundations/programming-language-theory/README|the course]]
- [[foundations/compilers/README|compilers]] · [[build-your-own-shit/04-your-own-language|build your own language]]

*Source: [reference] — built from this course's own gap-closing list.*
