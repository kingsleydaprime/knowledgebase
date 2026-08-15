# What a Compiler Is

**[Beginner → Intermediate]** — The phases, and the spectrum from interpreter to JIT that most real languages sit somewhere on.

**Source:** `[reference]` — built August 2026 to unblock [[BUILD-PLAN|build-your-own-language]]. No compiler project in this vault yet.

## The pipeline

```
source text
   │
   ├─ 1. LEXING          characters → tokens
   │                     "let x = 1 + 2"  →  LET IDENT(x) EQ INT(1) PLUS INT(2)
   │
   ├─ 2. PARSING         tokens → a tree
   │                     checks GRAMMAR: is this arrangement legal?
   │
   ├─ 3. SEMANTIC        name resolution, type checking
   │     ANALYSIS        checks MEANING: does `x` exist? is `1 + "a"` allowed?
   │
   ├─ 4. IR GENERATION   tree → a simpler linear form
   │
   ├─ 5. OPTIMISATION    IR → better IR
   │
   └─ 6. CODE GENERATION IR → machine code / bytecode
              │
         executable
```

The first three are the **front end** (language-specific), the last two the **back end** (target-specific), with the IR as the boundary. That split is why GCC and LLVM support many languages *and* many CPUs without an N×M explosion — you write one front end per language and one back end per target.

**Rust, Swift, Julia, Clang and Zig all share LLVM's back end.** That's the whole payoff of having an IR.

## Front end vs back end

```
  C ─┐                              ┌─→ x86-64
 C++ ─┤                             ├─→ ARM64
Rust ─┼─→ front ends → LLVM IR → ───┼─→ RISC-V
Swift ─┤                            ├─→ WASM
Julia ─┘                            └─→ PowerPC
```

Without the IR: 5 languages × 5 targets = 25 code generators. With it: 5 + 5 = 10.

This is just the adapter pattern applied at enormous scale, and it's the single most consequential architectural decision in compiler construction.

## Compiler, interpreter, JIT

The distinction is less binary than it's usually taught.

**Ahead-of-time compiler** — translate the whole program to machine code before running. C, C++, Rust, Go.

- Fast execution, no startup cost, no runtime needed
- Slow edit-run cycle, target-specific binaries, no runtime information to optimise with

**Tree-walking interpreter** — build an AST, then recursively execute it.

- Trivial to write, instant startup, easy debugging
- **10–100× slower** than compiled — every node visit is a virtual call and a pointer chase

**Bytecode VM** — compile to a compact instruction set, interpret that.

- 3–10× slower than native, portable, fast startup
- CPython, early JVM, Lua, Ruby → [[foundations/compilers/09-bytecode-and-virtual-machines|Bytecode VMs]]

**JIT** — compile to machine code *at runtime*, guided by observed behaviour.

- Approaches or beats AOT on long-running programs, because it knows things AOT can't
- Warm-up time, memory overhead, and enormous implementation complexity
- HotSpot, V8, LuaJIT, PyPy, .NET → [[foundations/compilers/11-jit-compilation|JIT]]

**Where real languages actually sit:**

| | Model |
|---|---|
| **C, C++, Rust, Go** | AOT to native |
| **Java, C#** | AOT to bytecode → JIT to native at runtime |
| **JavaScript** | parse → interpret → JIT hot functions (V8 does all three) |
| **Python** | AOT to bytecode → interpret. (PyPy JITs; CPython 3.13 has a copy-and-patch JIT) |
| **Ruby** | bytecode → YJIT |
| **Lua** | bytecode; LuaJIT is one of the fastest JITs ever written |

**Nearly every "interpreted" language compiles.** Python compiles to bytecode — that's what `.pyc` files are. The distinction that survives is *when* compilation happens and *what it targets*, not whether it occurs.

## Why the phases exist

You could write a one-pass compiler that emits code while parsing — early Pascal and C compilers did, because memory was scarce. Turbo Pascal was famously fast for exactly this reason.

The phases exist because separating them buys:

**Each phase is simple.** A lexer that only does characters→tokens is a few hundred lines. A parser that can assume well-formed tokens is far simpler than one handling raw characters.

**Optimisation needs the whole picture.** You can't inline a function you haven't parsed yet, or eliminate dead code before knowing what's reachable.

**Reuse.** One front end, many back ends.

**Better errors.** A parser that has seen the whole statement can say "expected `;` after this expression" rather than failing at the next character.

The cost is memory and multiple passes — irrelevant now, decisive in 1975.

## Errors are the product

An underrated point: **a compiler's error messages are most of its user interface.** You interact with them far more than with successfully compiled output.

The standard for good diagnostics is [[languages/03-rust/01-why-rust-and-the-toolchain|rustc]] and Elm:

```
error[E0308]: mismatched types
  --> src/main.rs:4:18
   |
 4 |     let x: i32 = "hello";
   |            ---   ^^^^^^^ expected `i32`, found `&str`
   |            |
   |            expected due to this
```

What makes it good: the exact span, both the expectation and what was found, *why* the expectation exists, and often a suggested fix.

That requires **every token and AST node to carry its source location** — a span, not just a line number. Retrofitting spans is painful, so put them in from the first line of code. This is the single most valuable piece of advice for anyone writing a compiler.

Also: **recover from errors and keep going.** Reporting one error per compile is a miserable experience. → [[foundations/compilers/03-parsing|Parsing]]

## Static and dynamic

**Static** = known at compile time. **Dynamic** = known only at runtime.

The whole discipline is about moving work from dynamic to static: type checking, dispatch resolution, bounds checks, memory layout. Every check you can do at compile time is one you don't pay for on every execution.

That's the same argument [[languages/03-rust/README|Rust]] makes about ownership, and it's why [[languages/05-cpp/12-constexpr-and-compile-time|`constexpr`]] exists.

## What you'll actually build

For [[BUILD-PLAN|build-your-own-language]], the realistic path:

1. **Lexer** — a few hundred lines. → [[foundations/compilers/02-lexical-analysis|02]]
2. **Parser** producing an AST — recursive descent + Pratt. → [[foundations/compilers/03-parsing|03]] · [[foundations/compilers/04-asts-and-semantic-analysis|04]]
3. **Tree-walking interpreter** with environments and closures. **You now have a working language.**
4. Then either **a bytecode VM** (→ [[foundations/compilers/09-bytecode-and-virtual-machines|09]]) or **a type checker** (→ [[foundations/compilers/05-type-systems-and-checking|05]]), depending on what interests you
5. Eventually **GC**, once you have closures and objects. → [[foundations/compilers/10-garbage-collection|10]]

Step 3 is the milestone. A tree-walking interpreter for a small language is a weekend, and everything afterwards is optimisation or rigour.

## The canonical references

- **Crafting Interpreters** (Nystrom, free online) — build two complete implementations, a tree-walker and a bytecode VM. **The best starting point by a wide margin**
- **The Dragon Book** — the classic. Thorough, theory-heavy, dated on back ends
- **Engineering a Compiler** (Cooper & Torczon) — more modern and more practical than the Dragon Book
- **SSA-based Compiler Design** — for the IR and optimisation material

---

## Related
- [[foundations/compilers/02-lexical-analysis|Lexical Analysis]] — the first phase
- [[foundations/compilers/06-intermediate-representations|Intermediate Representations]] — the front/back-end boundary
- [[languages/04-c/01-why-c-and-the-compilation-model|C: The Compilation Model]] — preprocess/compile/assemble/link, concretely
- [[foundations/compilers/README|Compilers course map]]
