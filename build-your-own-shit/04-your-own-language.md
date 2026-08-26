# Build Your Own Language

**[Intermediate → Advanced]** — The deepest single lesson on this list. A weekend gets you a working interpreter; everything after that is optimisation or rigour.

## What you're building

A small dynamically-typed language with variables, arithmetic, control flow, functions, and closures — first as a tree-walking interpreter, then optionally recompiled to a bytecode VM.

By the end **you will run a non-trivial program written in your own language.** That's the hook.

**What you're deliberately not building:** a type checker (a large separate project — [[foundations/compilers/05-type-systems-and-checking|note 05]] if you want one), native code generation, a module system, or a standard library beyond a handful of builtins.

**Why this one:** every other program you write runs on top of something like this. Building one converts "I use a language" into "I know what a language *is*" — and the tree-walker milestone arrives fast enough to stay motivating.

## What you need first

| You should know | Where |
|---|---|
| **The compiler pipeline** | [[foundations/compilers/01-what-a-compiler-is\|compilers/01]] |
| **Lexing** | [[foundations/compilers/02-lexical-analysis\|compilers/02]] |
| **Recursive descent and Pratt parsing** | [[foundations/compilers/03-parsing\|compilers/03]] — **the core prerequisite** |
| **ASTs, scopes, closures** | [[foundations/compilers/04-asts-and-semantic-analysis\|compilers/04]] |
| **Bytecode VMs** (for the second half) | [[foundations/compilers/09-bytecode-and-virtual-machines\|compilers/09]] |
| **Garbage collection** (once you have closures) | [[foundations/compilers/10-garbage-collection\|compilers/10]] |

**[Crafting Interpreters](https://craftinginterpreters.com) is the companion to this guide.** It builds exactly this — a tree-walker in Java, then a bytecode VM in C — and it's free. This guide is the language-agnostic map; that book is the detailed walkthrough.

## The build order

### 1. Lexer

Characters to tokens. Numbers, strings, identifiers, keywords, operators, punctuation.

```
"let x = 1 + 2;"  →  LET IDENT(x) EQ INT(1) PLUS INT(2) SEMICOLON EOF
```

**Test:** a table-driven test asserting the token stream for various inputs.

**Watch for:** **put a source span on every token from the first line of code.** Retrofitting spans is painful and gates every error message you'll ever produce. Lex identifiers first, then check whether they're keywords — or `letter` lexes as `let` + `ter`.

### 2. Parser and AST

Recursive descent for statements, Pratt for expressions.

```
1 + 2 * 3   →   Binary(+, Literal(1), Binary(*, Literal(2), Literal(3)))
```

**Test:** print the AST as an s-expression and check precedence — `(+ 1 (* 2 3))`, not `(* (+ 1 2) 3)`.

**Watch for:** the `(left_bp, right_bp)` asymmetry in the Pratt table *is* your associativity. Left-associative means `left < right`. Get this wrong and `1-2-3` evaluates as `1-(2-3)`.

**Don't bail on the first syntax error** — synchronise at statement boundaries and keep going.

### 3. Tree-walking interpreter — expressions

Recursively evaluate. `Binary(+, l, r)` → evaluate both sides, add.

**Test:** a REPL that evaluates `1 + 2 * 3` and prints `7`.

**Watch for:** you now need a **value type** — a tagged union of number, string, bool, nil. Decide your semantics deliberately: is `1 + "a"` an error or concatenation? Is `0` falsey? These are language design decisions, and writing them down is part of the exercise.

### 4. Statements, variables, scope

`let`, assignment, `print`, blocks.

An **environment** is a map from name to value, with a parent pointer. Entering a block pushes one; leaving pops it. Lookup walks outward.

**Test:**

```
let a = 1;
{ let a = 2; print a; }    // 2 — shadowing
print a;                    // 1
```

**Watch for:** shadowing falls out of the parent-chain design for free. Decide whether using an undeclared variable is an error (it should be) and whether redeclaring in the same scope is (usually yes).

### 5. Control flow

`if`/`else`, `while`, and `&&`/`||` with short-circuit evaluation.

**Test:** FizzBuzz. It exercises conditionals, loops, arithmetic, and printing in one small program — and it's the first time your language does something recognisable.

**Watch for:** `&&` must not evaluate its right side when the left is false. That's not an optimisation, it's a semantic guarantee people rely on (`p != nil && p.field`).

### 6. Functions

Declaration, calls, parameters, `return`.

A call: create a new environment whose parent is the function's *defining* scope, bind parameters, execute the body.

**Test:** recursive fibonacci. Then mutual recursion, which forces you to decide whether functions are hoisted.

**Watch for:**

**`return` needs a non-local exit** from arbitrarily deep recursion in your evaluator. The clean implementations are an exception/error propagated up, or a signal value checked after every statement. Pick one early — retrofitting is unpleasant.

**Guard the recursion depth**, or a runaway recursive program in *your* language blows *your* interpreter's stack and segfaults the host process instead of raising a language-level error.

### 7. Closures — the milestone that matters

```
fn make_counter() {
    let count = 0;
    fn increment() { count = count + 1; return count; }
    return increment;
}
let c = make_counter();
print c();  // 1
print c();  // 2
```

**Test:** exactly the above. If it prints 1 then 2, you have real closures.

**Watch for:** this is where naive scoping breaks. `count` outlives `make_counter`, so the environment can't live on the stack. In a tree-walker, heap-allocating environments handles it — which is also why tree-walkers are slow, since every variable access is a pointer chase.

> **You now have a working programming language.** Turing-complete, with first-class functions. Everything below is making it faster or more rigorous.

**Write something real in it.** A few hundred lines — a JSON parser, a small game, a text adventure. Using your own language is where you discover which decisions were wrong.

### 8. Where to go next — pick one

**A. Bytecode VM** (the performance path)

Compile the AST to a flat instruction array, then interpret that. Typically **10× faster** than a tree-walker.

```
1 + 2 * 3  →  CONST 1 / CONST 2 / CONST 3 / MUL / ADD
```

Start with a stack machine — code generation is a post-order walk with no register-allocation decisions. → [[foundations/compilers/09-bytecode-and-virtual-machines|compilers/09]]

The single biggest win: **resolve variables to stack slot indices at compile time** so runtime access is an array index rather than a hash lookup.

**B. A type checker** (the rigour path)

A pass between parsing and execution that assigns and verifies types. Start with local inference and required function signatures — the best cost/benefit by a distance. → [[foundations/compilers/05-type-systems-and-checking|compilers/05]]

**C. Garbage collection** (necessary once you have closures and objects)

Mark-and-sweep is a few hundred lines: track allocations, mark from roots, sweep. → [[foundations/compilers/10-garbage-collection|compilers/10]]

**The essential technique: a stress mode that collects on every allocation**, run against your whole test suite. A missed root is otherwise an intermittent heisenbug that appears months later.

### 9. Extras worth having

Arrays and maps · string methods · a small builtin library (`len`, `print`, `clock`) · classes or structs · error handling · a module system · a REPL with history.

**Classes are the natural extension** if you took the VM path — *Crafting Interpreters* covers them, and method dispatch plus inheritance is where inline caching starts to matter.

## Per-language toolkit

| Milestone | C | C++ | Rust | Go | Python | JS/Node |
|---|---|---|---|---|---|---|
| **Lexer** | by hand | by hand | by hand; `logos` | by hand | by hand | by hand |
| **AST** | tagged unions | `std::variant` | **enums** | interfaces + type switch | classes | classes/objects |
| **Tree walk** | function pointers | visitor | `match` | type switch | visitor / `match` | switch |
| **Values** | tagged union, NaN boxing | `std::variant` | enum | `interface{}` | native | native |
| **Env/scope** | hash map by hand | `unordered_map` | `HashMap` | `map` | `dict` | `Map` |
| **GC** | write one | write one | `Rc` first, then write one | **host GC — free** | **host GC — free** | **host GC — free** |
| **VM dispatch** | **computed goto** | computed goto | `match` | `switch` | `match` | `switch` |

**This is the guide where language choice matters most:**

**Rust** — the best fit for the AST and value types. Enums with exhaustive matching mean adding a node type produces a compile error at every site needing an update. The borrow checker fights you on environments; `Rc<RefCell<Environment>>` is the standard answer and it's a legitimate use. → [[languages/03-rust/06-structs-enums-and-pattern-matching|enums]]

**Python / JS / Go** — the host GC handles memory for you, so closures and cycles just work. **You skip the GC lesson entirely**, which is fine for a first language and a real gap if that's what you came for.

**C** — the full experience, and the only way to genuinely learn GC and NaN boxing. This is what `clox` in *Crafting Interpreters* does. Slowest to a working language, most learned.

**Java/C#** — what the book's first half uses; the visitor pattern is idiomatic and verbose.

> **Recommendation: build the tree-walker in whatever you're fastest in, then rebuild the VM in C or Rust.** That's the book's structure and it works — you learn the semantics first without fighting a language, then the implementation properly.

## The parts that will bite you

**No spans.** Add them from token one, or every error says "error somewhere".

**`return` from deep recursion.** Decide the mechanism early.

**Closures capturing by reference vs value.** Both are defensible; be deliberate. The classic bug is a loop variable shared by every closure created in the loop — JavaScript's `var` and Go before 1.22 both had it.

**Your interpreter's stack overflowing.** Bound the call depth.

**Environments as a linked list are O(depth) per lookup.** Fine for a tree-walker, and the first thing to fix in a VM.

**GC and a missed root.** An object reachable only from a local in your *interpreter's* host-language code is invisible to your collector. Stress mode catches it.

**Left vs right associativity** in the Pratt table.

**`nil` semantics.** Is `nil == false`? Is accessing a field on `nil` an error? Decide, write it down, and be consistent.

## How to know it works

**A test suite of programs with expected output** is the right structure — a directory of `.lang` files each with the output as a comment, and a runner that diffs.

```
// test: closures.lang
// expect: 1
// expect: 2
```

*Crafting Interpreters* ships exactly this for Lox, and **you can point it at your language if you follow its semantics** — a ready-made conformance suite of a few hundred tests.

Milestone programs, in order:

```
1 + 2 * 3          — precedence
FizzBuzz           — control flow
fib(25)            — recursion, and your first performance datapoint
make_counter()     — closures
a JSON parser      — written IN your language: the real test
```

**Benchmark the tree-walker against the VM** on `fib(30)`. Seeing 10× from the same semantics is the most satisfying number in this project.

**Fuzz the parser.** It should never panic, only produce errors.

## Where to stop

**Stop after closures if you want the concept. Stop after the bytecode VM if you want the craft.**

You'll have learned:

- That a language is a lexer, a parser, and a loop — the mystique doesn't survive
- Why every language has the precedence rules it has
- What a closure actually captures, and why the loop-variable bug exists everywhere
- Why interpreted languages are slow, and precisely which 10× the VM recovers
- What your daily language is doing on every variable access

**Real languages additionally have:** a type system, a module system, a standard library, a package manager, a debugger, an LSP server, JIT compilation, and years of semantics arguments. **The implementation is the easy part** — designing something people want to write in is the hard one.

**If you want to go further:** add **classes with inline caching** (the foundation of every fast dynamic-language runtime), or write a **compiler to a real target** — WebAssembly is the friendliest, since it's a stack machine and your bytecode is already close. → [[foundations/compilers/08-code-generation|code generation]]

---

## Related
- [[foundations/compilers/README|Compilers]] — the whole domain, written to unblock this
- [[foundations/compilers/03-parsing|Parsing]] · [[foundations/compilers/09-bytecode-and-virtual-machines|Bytecode VMs]] · [[foundations/compilers/10-garbage-collection|GC]]
- [[build-your-own-shit/06-your-own-database|Your Own Database]] — reuses the parser for SQL
- [[build-your-own-shit/README|build-your-own-shit]]
