# Intermediate Representations

**[Advanced]** — Why the tree isn't good enough for optimisation, and why SSA became the universal answer.

## Why lower the AST at all

The AST mirrors the source, which is exactly wrong for analysis:

- **Control flow is implicit.** `while`, `break`, `if/else` and early `return` are nested structures; to ask "which statements can reach this one?" you'd have to interpret the tree's semantics
- **It's too rich.** `for`, `while`, and `do-while` are three node types with one underlying meaning. Every optimisation would need three cases
- **It's too far from the machine.** No notion of registers, addresses, or evaluation order

So compilers **lower** the AST into something simpler, more explicit, and closer to a machine — usually through several IRs at decreasing levels of abstraction.

```
AST  →  HIR  →  MIR  →  LLVM IR  →  machine code
        │       │        │
   desugared,  CFG,   optimised,
   typed    borrowck  target-independent
```

That's roughly rustc's pipeline. Each level throws away structure the next doesn't need.

## Three-address code

The classic linear IR: at most one operation per instruction, with explicit temporaries.

```
// source
x = a + b * c - d;

// three-address code
t1 = b * c
t2 = a + t1
t3 = t2 - d
x  = t3
```

Every instruction is `result = op arg1 arg2`. Expression nesting is gone, evaluation order is explicit, and every intermediate value has a name — which is what makes analysis tractable.

## The control-flow graph

Straight-line code is grouped into **basic blocks** — sequences with one entry and one exit, no branches in or out of the middle. Blocks are nodes; branches are edges.

```
if (x > 0) { y = 1; } else { y = 2; }
print(y);
```

```
    ┌─────────────┐
    │ B0:         │
    │ t0 = x > 0  │
    │ br t0,B1,B2 │
    └──┬───────┬──┘
       │       │
  ┌────▼───┐ ┌─▼──────┐
  │ B1:    │ │ B2:    │
  │ y = 1  │ │ y = 2  │
  │ jmp B3 │ │ jmp B3 │
  └────┬───┘ └───┬────┘
       └────┬────┘
      ┌─────▼──────┐
      │ B3:        │
      │ print(y)   │
      └────────────┘
```

**Now `while`, `for`, `goto` and early `return` all look the same** — they're just edges. One implementation of an optimisation handles every source construct.

The CFG is what dataflow analysis runs on, and it's why several semantic checks (definite assignment, reachability, Rust's borrow checker) happen *after* lowering rather than on the AST. → [[foundations/compilers/04-asts-and-semantic-analysis|Semantic Analysis]]

**Dominance** is the key relation: block A **dominates** B if every path from entry to B goes through A. It's how you find loop headers, where it's safe to hoist code to, and where to place φ-functions.

## SSA

**Static Single Assignment**: every variable is assigned **exactly once**.

```
// not SSA
x = 1
x = x + 1
y = x * 2

// SSA
x₁ = 1
x₂ = x₁ + 1
y₁ = x₂ * 2
```

Why this is transformative: **a variable's name uniquely identifies its definition.** "Where did this value come from?" is answered by the name itself, with no dataflow analysis at all.

That makes constant propagation, dead code elimination, and common subexpression elimination nearly trivial — they become graph walks rather than fixpoint computations.

### φ-functions

The obvious problem: what about a variable assigned differently on two branches?

```
      ┌──────────┐
      │ br cond  │
      └─┬──────┬─┘
   ┌────▼──┐ ┌─▼─────┐
   │ y₁ = 1│ │ y₂ = 2│
   └────┬──┘ └───┬───┘
        └───┬────┘
     ┌──────▼──────────┐
     │ y₃ = φ(y₁, y₂)  │  ← "y₁ if we came from the left, y₂ if from the right"
     │ print(y₃)       │
     └─────────────────┘
```

A **φ-function** selects a value based on which predecessor block you arrived from. It isn't a real instruction — it's a notation for "the value depends on the path", and it's resolved during register allocation by inserting copies in the predecessors.

φ-nodes go at **dominance frontiers** — the blocks where control flow merges — which is computed with the Lengauer–Tarjan or Cytron algorithm. That placement is the one genuinely non-obvious part of constructing SSA.

**Almost every serious compiler uses SSA**: LLVM, GCC (GIMPLE), V8's TurboFan, HotSpot C2, Go's compiler, and Cranelift. It's the closest thing to a settled answer in compiler design.

Variants worth recognising: **sea of nodes** (V8, HotSpot C2 — control and data flow in one graph, more optimisation freedom, much harder to debug) and **CPS** (continuation-passing style, equivalent in power, used in functional-language compilers).

## LLVM IR

The IR you'll actually encounter, because so many languages target it:

```llvm
define i32 @add(i32 %a, i32 %b) {
entry:
  %sum = add nsw i32 %a, %b
  ret i32 %sum
}

define i32 @max(i32 %a, i32 %b) {
entry:
  %cmp = icmp sgt i32 %a, %b
  br i1 %cmp, label %then, label %else
then:
  br label %merge
else:
  br label %merge
merge:
  %result = phi i32 [ %a, %then ], [ %b, %else ]      ; ← a real φ-node
  ret i32 %result
}
```

Properties worth noting: **SSA**, **typed** (every value has a type, which catches bugs in your own code generator), **infinite virtual registers** (`%0`, `%1`, … — real allocation happens later), and **three forms** — human-readable `.ll`, compact bitcode `.bc`, and an in-memory API.

`nsw` = "no signed wrap", i.e. signed overflow is [[languages/04-c/10-undefined-behaviour|undefined]] and the optimiser may assume it can't happen. That's how a C-level UB rule becomes an optimisation licence, made explicit in the IR.

```bash
clang -S -emit-llvm foo.c -o foo.ll      # see the IR for any C program
opt -O2 -S foo.ll -o foo-opt.ll          # run the optimiser and diff
```

**Reading the before-and-after of `opt -O2` is the single best way to build intuition** about what optimisers actually do.

## Should you target LLVM?

**Yes:** enormous optimisation quality for free, every target architecture, mature tooling and debug-info support. It's why Rust, Swift, Julia and Clang all use it.

**No:** it's a huge dependency (hundreds of MB), **compile times are dominated by it**, the API is C++ and changes between versions, and for a simple language the optimisations may not pay for the integration cost.

The alternatives:

| | Character |
|---|---|
| **Cranelift** | Rust, designed for **fast compilation** over peak output. Used by Wasmtime, and as rustc's debug back end |
| **QBE** | tiny (~10k lines), 70% of LLVM's performance, genuinely readable |
| **Your own** | for a bytecode VM you don't need any of this → [[foundations/compilers/09-bytecode-and-virtual-machines\|Bytecode VMs]] |
| **C as a target** | emit C and let a C compiler do the work. Ugly, portable, and completely legitimate — Nim and early C++ did this |

**For build-your-own-language, target a bytecode VM.** LLVM is a project in itself.

## Lowering, step by step

Desugaring is most of the work, and it's satisfying — many features vanish:

```rust
// for loops → while
for x in iter { body }
→ let mut it = iter.into_iter();
  while let Some(x) = it.next() { body }

// while → conditional branches
while cond { body }
→ loop_header: if !cond goto exit; body; goto loop_header; exit:

// && short-circuits → branches
a && b
→ if a { b } else { false }

// method calls → function calls with an explicit receiver
x.foo(y)  →  Type::foo(&x, y)

// operator overloads → trait method calls
a + b  →  Add::add(a, b)

// pattern matching → decision trees of tests and branches
```

By the time you reach the low-level IR, the language's surface features are gone and what remains is loads, stores, arithmetic, calls and branches.

## Dataflow analysis

The framework nearly every optimisation is expressed in: propagate facts around the CFG until they stop changing.

```
Liveness (backwards):
  live_out[B] = ∪ live_in[S] for each successor S
  live_in[B]  = use[B] ∪ (live_out[B] − def[B])

  iterate until nothing changes
```

**Forward** analyses (reaching definitions, constant propagation, available expressions) flow entry→exit; **backward** ones (liveness, very-busy expressions) flow exit→entry.

**Liveness is the important one** — it drives register allocation (a variable that's dead needs no register) and dead-store elimination. → [[foundations/compilers/08-code-generation|Code Generation]]

The theory is **lattices and monotone functions**, which guarantees the iteration terminates. In practice you use a worklist rather than iterating over everything.

**SSA makes many of these unnecessary** — reaching definitions is free when a name *is* its definition, which is exactly why SSA won.

---

## Related
- [[foundations/compilers/07-optimisation|Optimisation]] — what runs on this
- [[foundations/compilers/08-code-generation|Code Generation]] — turning IR into instructions
- [[foundations/compilers/04-asts-and-semantic-analysis|ASTs and Semantic Analysis]] — what gets lowered
- [[foundations/dsa/04-data-structures/06-graphs|Graphs]] — the CFG is one, and dominance is a graph property
- [[foundations/compilers/README|Compilers course map]]
