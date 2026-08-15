# Compilers

How source text becomes something that runs. Lexing, parsing, type checking, IRs, optimisation, code generation, VMs, garbage collection, and JITs.

**~16,500 words across 11 notes**, built August 2026 to unblock [[BUILD-PLAN|build-your-own-language]]. `[reference]` — no compiler project in this vault yet.

> **The pipeline is the whole idea:** characters → tokens → tree → typed tree → IR → optimised IR → machine code. Each phase is simple in isolation, and the split is what lets one front end serve many CPUs. It's why Rust, Swift, Julia and Clang all share LLVM's back end — 5 languages + 5 targets instead of 5 × 5.

## Reading order

**The front end**

1. [[foundations/compilers/01-what-a-compiler-is|What a Compiler Is]] — **[Beginner → Intermediate]** — the phases, the front/back-end split, and the spectrum from interpreter to JIT that most real languages sit on
2. [[foundations/compilers/02-lexical-analysis|Lexical Analysis]] — **[Beginner → Intermediate]** — characters to tokens, maximal munch, and why everyone hand-writes lexers now
3. [[foundations/compilers/03-parsing|Parsing]] — **[Intermediate]** — recursive descent for statements, **Pratt parsing for expressions**, error recovery, and why parser generators lost
4. [[foundations/compilers/04-asts-and-semantic-analysis|ASTs and Semantic Analysis]] — **[Intermediate]** — arena-allocated trees, scopes and symbol tables, resolving names to slots, and closures
5. [[foundations/compilers/05-type-systems-and-checking|Type Systems and Checking]] — **[Intermediate → Advanced]** — the design axes, Hindley–Milner and unification, variance, and why full inference isn't universal

**The middle and back end**

6. [[foundations/compilers/06-intermediate-representations|Intermediate Representations]] — **[Advanced]** — the CFG, **SSA and φ-functions**, LLVM IR, and whether to target it
7. [[foundations/compilers/07-optimisation|Optimisation]] — **[Advanced]** — the passes, **why inlining is the one that matters**, and the honest limits
8. [[foundations/compilers/08-code-generation|Code Generation]] — **[Advanced]** — instruction selection, register allocation, calling conventions, linking

**Runtimes**

9. [[foundations/compilers/09-bytecode-and-virtual-machines|Bytecode and Virtual Machines]] — **[Intermediate → Advanced]** — **the realistic target for a language you build.** Stack vs register, dispatch, NaN boxing, closures
10. [[foundations/compilers/10-garbage-collection|Garbage Collection]] — **[Advanced]** — reachability, mark-sweep, generational collection, and the three-way tradeoff
11. [[foundations/compilers/11-jit-compilation|JIT Compilation]] — **[Advanced]** — tiered execution, speculation and deoptimisation, inline caching, warm-up

## If you're building a language

The realistic path, and the milestone that matters:

1. **Lexer** — a few hundred lines → note 02
2. **Recursive descent + Pratt parser** producing an AST → notes 03, 04
3. **Tree-walking interpreter** with environments and closures → note 04
4. → **You now have a working language.** A weekend or two. Everything after this is optimisation or rigour
5. Then either a **bytecode VM** (note 09) or a **type checker** (note 05), depending on what interests you
6. **Mark-and-sweep GC** once you have closures and objects → note 10
7. A **JIT** only if you have a specific reason → note 11

**Don't write a native code generator first.** Register allocation, calling conventions and linking are a project in themselves — target a bytecode VM, or LLVM/Cranelift if you want native.

## The advice that recurs

- **Spans on every token and AST node, from line one.** Retrofitting them is painful, and without them you can never produce good error messages. This is the highest-value single decision
- **Error messages are the product.** You interact with them more than with successful output
- **Recover and keep going.** One error per compile is a miserable experience
- **Hand-write the lexer and parser.** Every major compiler does — the reason is error messages and context sensitivity
- **Arena-allocate the AST.** One `Vec`, index-based references. Cache-friendly, no ownership fights
- **Resolve variables to slot indices at compile time.** Array indexing instead of hashing is the biggest easy interpreter win
- **A GC stress mode that collects on every allocation**, run against your test suite. It turns missed-root heisenbugs into deterministic failures

## The references

- **[Crafting Interpreters](https://craftinginterpreters.com)** (Nystrom, free) — build a tree-walker and a bytecode VM, completely. **The best starting point by a wide margin**, and the source of most of the practical advice above
- **Engineering a Compiler** (Cooper & Torczon) — more modern and practical than the Dragon Book
- **The Dragon Book** — the classic. Thorough on theory, dated on back ends
- **[Compiler Explorer](https://godbolt.org)** — an hour here teaches more about optimisation than any chapter

## Known gaps

- **No project.** The largest gap, and the whole reason this domain exists → [[BUILD-PLAN|build-your-own-language]]
- **Formal language theory** — regular vs context-free, pumping lemmas, decidability. That's a [[BUILD-PLAN|theory-of-computation]] domain, listed as optional
- **Linkers and loaders** in depth — partly covered in [[languages/04-c/12-build-systems|C: Build Systems]]
- **Incremental compilation** — how rustc and IDEs avoid recompiling everything
- **Language design itself** — this is about implementation, not about what makes a good language

## Related
- [[languages/04-c/01-why-c-and-the-compilation-model|C: The Compilation Model]] — the four stages, concretely
- [[foundations/os/README|Operating Systems]] — what the output runs on
- [[foundations/dsa/README|DSA]] — trees, graphs, and union-find, all used here
- [[languages/03-rust/17-macros|Rust: Macros]] — compile-time code generation from the user's side
- [[BUILD-PLAN|Build Plan]] — `build-your-own-x/` is next
