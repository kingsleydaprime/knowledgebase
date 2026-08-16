# Lambda Calculus

**[Intermediate → Advanced]** — Three constructs that compute everything, and the model every functional language is a sugaring of.

## The whole language

$$e ::= x \mid \lambda x.\,e \mid e_1\,e_2$$

**Variables. Abstraction (function definition). Application (function call).**

**That's it.** No numbers, no booleans, no conditionals, no loops, no data structures.

> **And it's Turing-complete** (Church, 1936). Everything computable is expressible in those three constructs. **Church arrived at this independently of Turing's machine, and they turned out to define the same class** — which is the main evidence for the Church–Turing thesis. → [[foundations/theory-of-computation/01-what-computation-is|Church–Turing]]

**Conventions:** application is left-associative ($f\,x\,y$ means $(f\,x)\,y$), and abstraction extends as far right as possible.

## Reduction

**Beta reduction — apply a function by substituting:**

$$(\lambda x.\,e)\,v \;\to_\beta\; e[x := v]$$

$$(\lambda x.\,x + 1)\,5 \to 5 + 1 \to 6$$

**Alpha conversion** — bound variable names don't matter. $\lambda x.x \equiv \lambda y.y$.

**Eta conversion** — $\lambda x.\,f\,x \equiv f$. **This is the formal justification for "point-free" style**, and for a linter telling you `x => f(x)` can just be `f`.

### Variable capture

**The subtlety that makes naive substitution wrong.**

$$(\lambda x.\,\lambda y.\,x)\;y \;\longrightarrow\; \lambda y.\,y \quad \textbf{WRONG}$$

**The free $y$ being substituted got *captured* by the inner binder.** It was a reference to an outer variable and became a reference to the parameter.

**The fix is to rename first:**

$$(\lambda x.\,\lambda y.\,x)\;y \;\to\; (\lambda x.\,\lambda y'.\,x)\;y \;\to\; \lambda y'.\,y \quad \textbf{✓}$$

> **This is not a theoretical curiosity — it's the hygiene problem in macro systems.** A macro that introduces a variable named `temp` and captures the user's `temp` has exactly this bug. **Scheme's `syntax-rules` and Rust's `macro_rules!` are hygienic by design**; C's preprocessor is not, which is why C macros are so hazardous. → [[languages/03-rust/17-macros|Macros]]
>
> **De Bruijn indices** avoid it entirely by replacing names with numbers counting binders outward — $\lambda x.\lambda y.x$ becomes $\lambda.\lambda.1$. **Ugly for humans, standard in implementations**, and it makes alpha-equivalence into literal syntactic equality.

## Church encodings

**How you get data from nothing but functions.**

**Booleans — encode the *choice* they represent:**

$$\text{true} = \lambda a.\lambda b.\,a \qquad \text{false} = \lambda a.\lambda b.\,b$$
$$\text{if} = \lambda c.\lambda t.\lambda f.\;c\,t\,f$$

**A boolean *is* a two-argument selector.** `if` just applies it — no conditional construct needed.

**Numerals — encode $n$ as "apply $f$ $n$ times":**

$$\bar{n} = \lambda f.\lambda x.\;f^n(x)$$
$$\text{succ} = \lambda n.\lambda f.\lambda x.\;f\,(n\,f\,x)$$

**Pairs — encode as "give me a function and I'll hand you both parts":**

$$\text{pair} = \lambda a.\lambda b.\lambda s.\;s\,a\,b \qquad \text{fst} = \lambda p.\,p\,(\lambda a.\lambda b.\,a)$$

> **The pattern across all three: encode data by what you can *do* with it.** A boolean is its elimination form; a number is iteration; a pair is projection.
>
> **This is exactly the Church-encoding/object-orientation correspondence** — an object is data bundled with the operations on it, which is the same idea. **And it's why "everything is a function" isn't a slogan; it's a theorem.**

## Recursion and the Y combinator

**A lambda term has no name, so how does it call itself?**

**The Y combinator:**

$$Y = \lambda f.\,(\lambda x.\,f\,(x\,x))\,(\lambda x.\,f\,(x\,x))$$

**It satisfies $Y\,f = f\,(Y\,f)$** — it produces a fixed point, so $f$ receives *itself* as an argument.

**Which lets you write recursion without names:**

$$\text{fact} = Y\,(\lambda f.\lambda n.\;\text{if}\;(n = 0)\;1\;(n \times f(n-1)))$$

> **This is genuinely one of the more beautiful results in computing** — recursion, which feels primitive, is *derivable* from anonymous functions alone.
>
> **In a strict language $Y$ diverges** (it evaluates its argument forever), so you use the **Z combinator** — the same idea with an eta-expansion to delay evaluation. **Every "recursive anonymous function" trick in JavaScript is a Z combinator.**

## Evaluation strategies

**Given $(\lambda x.\,e)\,a$, do you evaluate $a$ first?**

**Call by value (strict/eager)** — evaluate arguments before the call. **C, Java, Python, Rust, OCaml, and most languages.**

*Predictable performance and evaluation order; wasteful if the argument is unused; diverges if the argument diverges even when unneeded.*

**Call by name** — substitute the unevaluated argument, evaluate on use. **Re-evaluates on each use.**

**Call by need (lazy)** — call by name plus memoisation. **Haskell.**

> **Laziness enables infinite data structures:**
> ```haskell
> nats = [0..]              -- infinite, and fine
> take 5 (map (*2) nats)    -- [0,2,4,6,8]
> ```
> **And it makes composition efficient without fusion** — `head . sort` can be $O(n)$ rather than $O(n\log n)$ if the sort is lazy enough.
>
> **The cost is unpredictable space and time.** **Space leaks from accumulated unevaluated thunks are Haskell's characteristic performance problem**, and reasoning about *when* something evaluates is genuinely hard. `foldl` building a chain of thunks and blowing the stack is the classic example, which is why `foldl'` exists.

**Church–Rosser (confluence)** — **if a term reduces to a normal form, that normal form is unique regardless of reduction order.** So the *answer* doesn't depend on strategy — **only whether you find it, and how fast.**

**And normal-order reduction (leftmost-outermost) is normalising:** if a normal form exists, it finds it. **Call-by-value can diverge where lazy evaluation succeeds.**

## Simply typed lambda calculus

**Add types, and something surprising happens.**

$$\tau ::= \text{base} \mid \tau_1 \to \tau_2$$

$$\frac{\Gamma, x{:}\tau_1 \vdash e : \tau_2}{\Gamma \vdash \lambda x{:}\tau_1.\,e : \tau_1\to\tau_2}
\qquad
\frac{\Gamma\vdash e_1 : \tau_1\to\tau_2 \quad \Gamma\vdash e_2 : \tau_1}{\Gamma\vdash e_1\,e_2 : \tau_2}$$

> **The simply typed lambda calculus is *strongly normalising*: every well-typed term terminates.**
>
> **Which means it is no longer Turing-complete.** $Y$ cannot be typed — self-application $x\,x$ requires $x$ to have a type that contains itself.
>
> **Adding types removed computational power, and gained you a guarantee.** That trade is the entire subject of type theory, and it's why total languages like Coq and Agda restrict recursion. → [[foundations/theory-of-computation/01-what-computation-is|Turing completeness]]

**Real languages add general recursion back** via a `fix` primitive or recursive definitions — **regaining Turing completeness and losing the termination guarantee.**

## The extensions worth naming

**System F** — parametric polymorphism. $\Lambda\alpha.\,e$ abstracts over *types*. **This is generics**, and full type inference for System F is undecidable — which is why Java and C# require type annotations where ML doesn't. → [[foundations/programming-language-theory/05-type-inference|Type Inference]]

**System F$_\omega$** — type operators. Higher-kinded types, `Functor f`.

**Dependent types** — types depending on *values*. `Vec n a`, where the length is in the type. Coq, Agda, Idris. → [[foundations/programming-language-theory/06-curry-howard-and-proofs|Curry–Howard]]

**Linear types** — every value used **exactly once**. **Rust's ownership is affine types** (at most once), and it's the same idea. → [[foundations/programming-language-theory/07-effects-and-substructural-types|Substructural Types]]

**The lambda cube** organises these along three axes: terms depending on types (polymorphism), types depending on types (operators), types depending on terms (dependency). **The Calculus of Constructions has all three**, and it's what Coq is built on.

## Why it matters practically

**Beyond the elegance:**

**Every functional language is sugar over this.** Haskell, OCaml, F#, Scala, Elm — **desugar far enough and you reach lambda calculus.** So do JavaScript's arrow functions and Python's `lambda`.

**Compilers use it as an IR.** GHC's Core is System F with extensions. **Optimisations are provably-correct lambda-term transformations.** → [[foundations/compilers/06-intermediate-representations|Intermediate Representations]]

**Continuations, CPS and async.** Continuation-passing style is a lambda calculus transformation, and **async/await is essentially a CPS transform** the compiler does for you.

**Closures are the implementation of lambda abstraction with free variables** — the environment captures them. → [[build-your-own-x/04-your-own-language|Build your own language]], where closures are the milestone.

**Currying** — $\lambda x.\lambda y.\,e$ rather than a two-argument function. **Why Haskell and OCaml have partial application for free**, and why `f(x)(y)` works in JavaScript.

---

## Related
- [[foundations/programming-language-theory/03-semantics|Semantics]] — giving meaning rigorously
- [[foundations/programming-language-theory/04-type-systems-formally|Type Systems Formally]] — what types buy you
- [[build-your-own-x/04-your-own-language|Build Your Own Language]] — implementing closures, which is this
- [[foundations/programming-language-theory/README|PL theory map]]
