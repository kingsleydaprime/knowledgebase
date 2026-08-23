# Practice Exercises — Solutions

> **[Advanced]** · Worked answers to [[foundations/programming-language-theory/08-practice-exercises|note 08]].

---

## Part A — Lambda calculus

### 1. Reduce by hand

**(a)** $(\lambda x.\,x\,x)(\lambda y.\,y) \to (\lambda y.\,y)(\lambda y.\,y) \to \lambda y.\,y$ — the identity.

**(b)** $(\lambda x.\lambda y.\,x)\,a\,b \to (\lambda y.\,a)\,b \to a$ — this is `const` / **K**, and Church-encoded `true`.

**(c)** $(\lambda x.\lambda y.\,x\,y)(\lambda z.\,z)\,w \to (\lambda y.(\lambda z.\,z)\,y)\,w \to (\lambda z.\,z)\,w \to w$.

**Write every substitution out.** The discipline is the exercise — reduction errors come from skipping steps, not from misunderstanding.

### 2. Capture

$(\lambda x.\lambda y.\,x)\,y$. Naively substituting $y$ for $x$ gives $\lambda y.\,y$ — **the identity function.**

That's wrong. The $y$ being passed in is a *free* variable that has been **captured** by the binder $\lambda y$, changing its meaning entirely.

Correctly: alpha-convert first, $\lambda y.\,x \equiv \lambda y'.\,x$, then substitute → $\lambda y'.\,y$ — a constant function returning the outer $y$.

**The rule: when substituting into a term with a binder, rename the bound variable if it would capture a free variable of what you're substituting.**

**Every first implementation of substitution has this bug**, and it's why real implementations use De Bruijn indices (bound variables as numbers, so there are no names to collide) or a locally-nameless representation. It's also the same phenomenon as **unhygienic macros** capturing user variables → [[foundations/compilers/README|compilers]].

### 3. Church numerals

$n$ is "apply $f$ to $x$, $n$ times":

$$0 = \lambda f.\lambda x.\,x \qquad 1 = \lambda f.\lambda x.\,f\,x \qquad 2 = \lambda f.\lambda x.\,f\,(f\,x)$$

$$\text{succ} = \lambda n.\lambda f.\lambda x.\,f\,(n\,f\,x) \qquad \text{plus} = \lambda m.\lambda n.\lambda f.\lambda x.\,m\,f\,(n\,f\,x)$$

$1+1$: apply $f$ once, then once more — $\lambda f.\lambda x.\,f(f\,x) = 2$. ✓

**The point of the exercise is that data is unnecessary.** Numbers, booleans, pairs and lists are all encodable as functions. The lambda calculus has *only* abstraction and application and is still Turing-complete → [[foundations/theory-of-computation/05-turing-machines|Turing machines]].

### 4. Y combinator

$Y\,g = (\lambda x.g(x\,x))(\lambda x.g(x\,x)) \to g\big((\lambda x.g(x\,x))(\lambda x.g(x\,x))\big) = g\,(Y\,g)$. ✓

**$Y\,g$ reproduces itself with a $g$ in front** — which is recursion without any named self-reference. That's the trick: a language with no `def` and no recursion still gets recursion.

**Under call-by-value it diverges.** CBV evaluates arguments before applying, so $Y\,g$ must fully evaluate $(\lambda x.g(x\,x))(\lambda x.g(x\,x))$ — which reduces to itself, forever. No $g$ is ever reached.

**$Z$ fixes it by eta-expansion:** $Z = \lambda f.(\lambda x.f(\lambda v.\,x\,x\,v))(\lambda x.f(\lambda v.\,x\,x\,v))$. Wrapping the self-application in $\lambda v$ makes it a *value*, so CBV stops early and unfolds only on demand.

**This is why strict languages need $Z$ and lazy ones can use $Y$**, and it's the cleanest demonstration that evaluation strategy is not a mere implementation detail — it changes which programs terminate → [[foundations/programming-language-theory/03-semantics|note 03]].

---

## Part B — Semantics

### 5. Rules, then interpreter

$$\frac{e_1 \to e_1'}{e_1 + e_2 \to e_1' + e_2} \qquad \frac{e_2 \to e_2'}{v_1 + e_2 \to v_1 + e_2'} \qquad \frac{}{n_1 + n_2 \to n_1 \boxplus n_2}$$

The first two are **congruence** rules (evaluate inside), the third is the **computation** rule. Note they encode left-to-right order: the second requires $v_1$ to already be a value.

**The interpreter should mirror them one-to-one** — one case per rule. When it doesn't, you've either implemented a rule you didn't write down, or written a rule you don't implement, and **both are bugs you can only see by keeping the two side by side.** That is the entire pedagogical point of operational semantics.

### 6. Evaluation order

```
let f = λx. 42 in f (print "hi")
```

- **Call-by-value:** prints `hi`, returns 42
- **Call-by-name / lazy:** returns 42, **prints nothing** — the argument is never used, so never evaluated

**Haskell** is lazy (call-by-need — call-by-name plus memoisation). **Python, Rust, Java, Go, OCaml** are call-by-value.

**The consequences are real:** laziness lets you define infinite structures (`take 5 [1..]`) and gives short-circuiting for free, at the cost of unpredictable space behaviour and **space leaks from unevaluated thunks**. Strict evaluation is predictable and needs explicit laziness (generators, `Iterator`, thunks) for the same tricks → [[languages/06-python/06-iterators-generators-and-comprehensions|generators]].

---

## Part C — Types

### 7. Type checker

Bidirectional checking splits into two mutually recursive functions: `infer(Γ, e) → τ` (synthesise) and `check(Γ, e, τ)` (verify against an expectation). Lambdas are *checked* against an expected function type; applications *infer* the function then check the argument.

$(\lambda x{:}\text{Int}.\,x)\,\text{true}$ fails: the function infers $\text{Int}\to\text{Int}$, so `true` is checked against `Int` and fails.

**Bidirectional is the practical approach because it produces good error messages** — you know what was *expected* at the failure point, so you can say "expected Int, found Bool" rather than "unification failed". It also needs far fewer annotations than naive checking → [[foundations/compilers/05-type-systems-and-checking|compilers]].

### 8. Progress and preservation

**Preservation:** if $\Gamma \vdash e : \tau$ and $e \to e'$ then $\Gamma \vdash e' : \tau$. By induction on the typing derivation; the substitution lemma does the work in the beta case.

**Progress:** if $\vdash e : \tau$ then $e$ is a value or $\exists e'.\ e \to e'$. By induction on typing, using a canonical forms lemma (a value of type $\tau_1\to\tau_2$ *is* a lambda).

**The one-sentence version:** *progress says a well-typed term is never stuck right now; preservation says evaluating it keeps it well-typed — so by induction it is never stuck, ever.*

**"Stuck" means a non-value that cannot step** — `true + 1`, or calling a non-function. **That is what type safety actually guarantees**, and it is narrower than people assume: it says nothing about termination, correctness, or the absence of exceptions and infinite loops.

### 9. Algorithm W

`λf.λx. f (f x)`:

Assign $f:\alpha$, $x:\beta$. From `f x`: $\alpha \sim \beta \to \gamma$. From `f (f x)`: $\alpha \sim \gamma \to \delta$. Unifying gives $\beta \sim \gamma \sim \delta$. Result: $(\beta\to\beta)\to\beta\to\beta$, generalised to $\forall\alpha.\,(\alpha\to\alpha)\to\alpha\to\alpha$. ✓

**The occurs check** rejects unifying $\alpha$ with a type *containing* $\alpha$, which would build an infinite type. Omit it and your unifier loops forever on exercise 10's first term.

**This is why ML-family languages need almost no annotations** while remaining fully statically typed, and it is the machinery behind type inference in Haskell, OCaml, Rust and (partially) TypeScript.

### 10. Break inference

**$\lambda x.\,x\,x$** requires $\alpha \sim \alpha\to\beta$ — $\alpha$ occurs in its own definition. Rejected by the occurs check. **Untyped it is perfectly fine** (it is half the Y combinator), which shows the type system rejects some terminating, meaningful programs. **Every type system is conservative — that is the trade.**

**Let-polymorphism:**

```
let id = λx.x in (id 1, id true)      -- ✓  id : ∀α. α → α
(λid. (id 1, id true)) (λx.x)         -- ✗  ill-typed
```

**HM generalises at `let` but not at `λ`.** At `let`, the definition is complete, so free type variables can be quantified. A lambda-bound variable must have **one** monomorphic type across the body, because the function might be applied to anything.

**Generalising at λ is System F, and its inference is undecidable.** HM's restriction is exactly the compromise that keeps inference decidable and complete — which is why it is the design nearly every practical inferring language adopted.

---

## Part D — Curry–Howard and effects

### 11. Programs as proofs

| Type | Proposition | Inhabitant |
|---|---|---|
| $A \to (B \to A)$ | $A \Rightarrow (B \Rightarrow A)$ | $\lambda a.\lambda b.\,a$ (**K**) |
| $(A\to B)\to(B\to C)\to(A\to C)$ | transitivity | $\lambda f.\lambda g.\lambda a.\,g\,(f\,a)$ (composition) |
| $A \land B \to A$ | conjunction elimination | $\lambda p.\ \text{fst}\ p$ |

**Types are propositions; programs are proofs; evaluation is proof simplification.** Product = ∧, sum = ∨, function = ⇒, `Void` = ⊥.

**$A \lor \lnot A$ has no inhabitant.** To construct a value of `Either A (A → Void)` you must supply *either* an $A$ *or* a refutation of $A$ — and for an arbitrary, unknown $A$ you can do neither. **A constructive proof must produce a witness**, and excluded middle asserts a disjunction without saying which side holds.

**That is why Coq, Agda and Lean are constructive by default**, and why classical reasoning must be added as an axiom — which then blocks extracting a running program from the proof → [[foundations/programming-language-theory/06-curry-howard-and-proofs|note 06]].

### 12. Linearity

Linear rules use **context splitting**:

$$\frac{\Gamma_1 \vdash e_1 : \tau\to\sigma \qquad \Gamma_2 \vdash e_2 : \tau}{\Gamma_1, \Gamma_2 \vdash e_1\,e_2 : \sigma}$$

Each variable goes to exactly one subterm, and there is no rule permitting duplication or discarding.

- **$\lambda x.\,x\,x$** rejected — $x$ used **twice** (no *contraction*)
- **$\lambda x.\lambda y.\,x$** rejected — $y$ used **zero** times (no *weakening*)

**The Rust mapping is direct:**

| Structural rule | Rust |
|---|---|
| **Contraction** (use twice) | Forbidden for non-`Copy` — that is **move semantics** |
| **Weakening** (never use) | **Allowed** — Rust is *affine*, not linear. `Drop` runs |
| Both allowed | `Copy` types |

**Rust is affine (at most once), not linear (exactly once)** — which is why an unused `String` is fine but using it after a move is not, and why the compiler inserts `drop`.

**This is the vault's clearest case of theory arriving in industry**: substructural type systems from the 1980s became the borrow checker, and "the type system tracks how many times you use a value" is the whole idea → [[languages/03-rust/README|Rust]].

## Related
- [[foundations/programming-language-theory/08-practice-exercises|the exercises]]
- [[foundations/programming-language-theory/README|the course]]

*Source: [reference] — from Pierce's *Types and Programming Languages* and the course's primary sources.*
