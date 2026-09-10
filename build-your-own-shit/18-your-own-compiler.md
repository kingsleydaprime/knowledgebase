# Your Own Compiler

**[Advanced]** — Source code → AST → **IR** → optimisation → **register allocation** → real x86-64 that runs on your machine. The three middle stages are the ones nothing else in this vault teaches.

## What you're building

A compiler for a small statically-scoped language with functions, producing a native executable.

**The reference implementation here is called Cairn** — around 600 lines of Python across four files. Yours will differ; the guide is about the stages, not the language.

By the end:

```
$ cat demo.cairn
fn add(a, b) { return a + b; }
fn main() {
    let x = 5;
    print(add(x, 3));
    let i = 0;
    while (i < 4) { print(i * 10); i = i + 1; }
    return 0;
}

$ python3 cairnc.py demo.cairn
IR 41 -> 34 instructions (folded 3, removed 7)
program output:
8
0
10
20
30
```

**A real binary.** `file out` says ELF executable, `objdump -d out` disassembles it, `gdb` debugs it.

**What you're deliberately not building:** a type system, garbage collection, closures, or your own binary encoder. Each is a project in its own right and is pointed at below.

### Why this one, when two related guides already exist

| Guide | Front end | Middle | Back end |
| :--- | :--- | :--- | :--- |
| [[build-your-own-shit/04-your-own-language\|04 — Your Own Language]] | ✅ lexer, parser, AST | ✅ optional bytecode | ❌ **interprets** — it says so |
| [[how-computers-work/08-capstone/06-build-the-language\|HCW module 33 — Pebble]] | ✅ | ❌ no IR, no optimisation | ✅ but a toy 16-bit CPU |
| **This guide** | ✅ + semantic analysis | ✅ **IR, optimisation, register allocation** | ✅ **real x86-64** |

**Guide 04 stops before code generation. Pebble skips the middle entirely.** The interesting problems — liveness, spilling, instruction selection, calling conventions — only appear when you have both a real IR and a real target. That is the gap this fills.

## What you need first

**Required:**

- **A parser you have written before.** Recursive descent, from [[build-your-own-shit/04-your-own-language|guide 04]] or [[how-computers-work/08-capstone/06-build-the-language|Pebble]]. This guide assumes lexing and parsing are familiar and spends its time after the AST.
- **Comfort reading assembly.** [[computer-architecture/04-assembly|computer-architecture/assembly]] is enough. You need to recognise `movq`, `addq`, `cmpq`, `jne`, `call`, `ret`.
- **A toolchain:** `gcc` (or `clang`) and `objdump`. Any Linux or macOS machine has them.

**Helpful:**

- [[compilers/06-intermediate-representations|compilers/IR]] and [[compilers/07-optimisation|compilers/optimisation]] for the theory this makes concrete.
- [[how-computers-work/index|How Computers Work]] if you want to know what the instructions you emit physically do.

**Honest note:** this guide targets **x86-64 on Linux** because that is what most readers can run natively. ARM64 has a far cleaner encoding and everything here transfers; the differences are register names, the argument registers, and the calling convention's details.

## The key decision: emit assembly text, not bytes

**Your compiler emits `.s` files and lets `as` assemble them.** That is not a shortcut — it is what `gcc` and `clang` actually do.

**What you keep:** IR design, optimisation, liveness analysis, register allocation, instruction selection, calling conventions, stack frame layout.

**What you skip:** ModRM bytes, REX prefixes, and x86's genuinely baroque variable-length encoding — which teaches almost nothing you cannot learn faster from [[how-computers-work/08-capstone/02-the-isa|PRIME-1's fixed-width encoder]], where the same idea fits on one page.

**If you want binary emission anyway,** do it after everything works, and expect it to take as long as the rest combined.

## The build order

**Each milestone runs.** That is the folder's rule and it matters more here than anywhere else, because a compiler has a lot of stages that are individually untestable.

### 1. Lexer and parser → AST

You have done this before. Get to an AST for functions, `let`, assignment, `if`/`else`, `while`, `return`, calls and arithmetic.

**Test:** parse and pretty-print the AST. *One evening.*

### 2. Semantic analysis — the pass guide 04 and Pebble both skip

A walk over the AST **before** any code generation, catching what the parser structurally cannot:

- undefined variables
- undefined functions
- **wrong argument count** at a call site
- duplicate function definitions
- assignment to an undeclared name

```
  undefined variable 'nope'
  add() takes 2 args, got 1
  function 'f' defined twice
```

**This is the difference between "it crashed" and "line 7: you called add with one argument".** Do it now — every later stage assumes names resolve.

**Test:** a file of deliberately broken programs, each producing the right message.

### 3. IR generation — three-address code

**Lower the tree to a flat list of instructions over unlimited virtual registers.**

```
fn main(){ let i=0; while(i<3){ print(i); i=i+1; } return 0; }
```

becomes

```
  %1 = const 0
.main_top1:
  %2 = const 3
  %3 = cmp_lt %1, %2
  br %3 -> .main_body2, .main_endw3
.main_body2:
  print %1
  %4 = const 1
  %5 = add %1, %4
  %1 = copy %5
  jmp .main_top1
.main_endw3:
  %6 = const 0
  ret %6
```

**Why bother, when Pebble went straight from AST to assembly?** Three reasons, and they are the whole argument for an IR:

1. **Optimisation is far easier on a flat list.** "Is this value ever used?" is a scan; on a tree it is a recursive search.
2. **Unlimited virtual registers** let you generate code without worrying about running out — allocation becomes a separate, solvable problem.
3. **It decouples front end from back end.** One IR, many targets.

**Test:** print the IR. Read it. It should obviously correspond to the source.

### 4. Optimisation — and the bug you will write

Two passes get you most of the visible win:

**Constant folding** — if both operands are known constants, compute at compile time.
**Dead code elimination** — remove instructions whose result nobody reads.

Run them alternately until nothing changes; folding exposes dead code, which exposes more folding.

```
  no opt: IR 11 -> 11
  with -O: IR 11 -> 4   (folded 3, removed 7)
```

> [!WARNING]
> **You will almost certainly write this bug, so here it is in advance.**
>
> The naive constant folder tracks known values in a dictionary as it scans the instruction list. Applied to the loop above, it sees `%1 = const 0`, then `cmp_lt %1, %2` with both known — and **folds the loop condition to a constant `1`**. It then removes the increment as dead. The program loops forever.
>
> **Constant propagation is only valid within a basic block.** A label begins a block that can be reached from elsewhere, so nothing known before it still holds. **Clear the known-values map at every label.**
>
> The same trap catches dead code elimination. A backward scan makes a loop counter look dead, because it is *updated at the bottom* of the loop and *read at the top*. Either do proper dataflow analysis, or use the conservative version: "is this register read anywhere in the function?"
>
> **Both bugs produce a program that compiles cleanly and runs wrong**, which is the worst kind. This is why real compilers are built around a control-flow graph rather than a flat list.

### 5. Liveness and register allocation — the heart of the guide

You have unlimited virtual registers. The machine has about fifteen, and fewer once you reserve some.

**Live interval:** the span from a virtual register's first definition to its last use.

**Linear scan allocation:**

1. Sort virtual registers by where their interval starts.
2. Walk them in order, freeing any machine register whose interval has ended.
3. Assign a free machine register if one exists.
4. Otherwise **spill** — pick the value whose interval ends latest and put it on the stack.

```
  virtual registers: 24   in machine regs: 19   SPILLED: 5
```

**Read that carefully.** Nineteen virtual registers share five machine registers, because their live intervals do not overlap. **That reuse is the entire point of allocation**, and it is why a small register file is workable at all.

**Spilled values become stack slots**, loaded into a scratch register around each use:

```
  movq %rax, -48(%rbp)      # spill
  movq -48(%rbp), %r11      # reload before use
```

> [!NOTE]
> **Simplification worth knowing you are making:** allocating only into **callee-saved** registers (`rbx`, `r12`–`r15`) means a `call` cannot clobber your values, so you never have to save anything around calls.
>
> A real allocator uses caller-saved registers too and saves the live ones across each call — more registers, more bookkeeping. Start with callee-saved only.
>
> **Linear scan is also the simple option.** The classical algorithm builds an *interference graph* and colours it, which produces better allocation and is much more work. Linear scan is what JITs use, precisely because it is fast and good enough.

### 6. Code generation — instruction selection

Walk the IR, emit assembly. Mostly mechanical; three parts are not:

**Comparisons** do not produce a value on x86 — they set flags. You need `cmp` then a `setcc` then a zero-extend:

```
  cmpq %r12, %rbx
  setl %al
  movzbq %al, %rax
```

**Calls** follow the **System V AMD64 ABI**: integer arguments in `rdi, rsi, rdx, rcx, r8, r9`, return value in `rax`.

**Stack frames** need care:

```
  pushq %rbp
  movq %rsp, %rbp
  pushq %rbx ... pushq %r15     # save callee-saved
  subq $N, %rsp                 # spill slots + alignment
```

**Alignment is the one that will bite you** — see below.

### 7. The driver

Write the `.s` file, invoke `gcc` to assemble and link, run it. Now you have a compiler you can use.

**Test:** the demo program at the top of this guide.

### 8. Where to go next — pick one

**A. A control-flow graph.** Replace the flat instruction list with basic blocks and edges. This makes the module-4 bugs *impossible* rather than merely avoided, and unlocks real dataflow analysis. **The highest-value next step.**

**B. SSA form.** Each virtual register assigned exactly once, with φ-nodes where control flow merges. It is what LLVM and every serious compiler uses, and it makes most optimisations dramatically simpler. → [[compilers/06-intermediate-representations|compilers/06]]

**C. More optimisations.** Common subexpression elimination, strength reduction (`x * 8` → `x << 3`), inlining, loop-invariant code motion. → [[compilers/07-optimisation|compilers/07]]

**D. A type checker.** → [[compilers/05-type-systems-and-checking|compilers/05]], and [[build-your-own-shit/04-your-own-language|guide 04]] option B.

**E. Retarget it.** Emit ARM64, or PRIME-1 assembly from [[build-your-own-shit/17-your-own-cpu/index|guide 17]]. **A second target is the real test of whether your IR was well designed** — if the back end was properly separated, the front end and optimiser should need no changes at all.

## Per-language toolkit

| | What the stdlib gives you | What you'd reach for |
| :--- | :--- | :--- |
| **Python** | `re` for lexing, dicts for symbol tables, `subprocess` for the driver | nothing — this is the fastest language to write a compiler in |
| **C** | almost nothing; hand-rolled lexer, manual memory for the AST | `flex`/`bison` if you want generated parsers |
| **Rust** | strong enums make ASTs and IR genuinely pleasant | `logos` for lexing, `cranelift` if you want a real back end |
| **Go** | `text/scanner`, `go/ast` as a reference design | — |
| **OCaml / Haskell** | pattern matching over algebraic data types is the natural fit — this is why compilers are written in ML-family languages | — |

**Whatever you use, the AST and IR want sum types.** Python tuples work; tagged unions work better.

## The parts that will bite you

- **Constant propagation across basic blocks.** The bug above. Clear known values at every label.
- **Backward dead-code elimination in loops.** The other half of the same bug.
- **Stack alignment.** The System V ABI requires `rsp` to be **16-byte aligned at the point of a `call`**. After `call` pushes the return address, `rsp ≡ 8 (mod 16)` on entry. `push rbp` makes it 0, five more pushes make it 8 again, so your `sub` must restore alignment. **Get this wrong and `printf` segfaults** — with SSE instructions in libc as the visible culprit, which sends you looking in entirely the wrong place.
- **Spill slot offsets colliding with saved registers.** If you push five registers after `rbp`, your first spill slot is at `-48(%rbp)`, not `-8`.
- **`imul` operand order and `sub` direction.** `subq %b, %a` computes `a - b` in AT&T syntax. GNU assembler is AT&T by default; Intel syntax reverses it. Pick one and stay there.
- **Forgetting to zero `eax` before a variadic call.** `printf` is variadic; the ABI uses `al` to say how many vector registers hold arguments. Not zeroing it usually works and occasionally does not.
- **Emitting a function with no `ret`.** If control falls off the end, execution continues into the next function. Always emit an epilogue.

## How to know it works

1. **Per stage.** Print the AST. Print the IR. Print the allocation. Print the assembly. Each is inspectable, and a bug is almost always visible at exactly one stage.
2. **A test corpus.** Twenty small programs with known outputs — arithmetic, loops, nested calls, recursion, deep expressions. Run them on every change.
3. **Differential testing against the source language's semantics.** Write a simple tree-walking interpreter for your language (you may already have one from guide 04) and check the compiled program agrees with it on every test. **This is the same oracle technique as [[how-computers-work/08-capstone/05-build-the-emulator|the PRIME-1 emulator]]**, and it catches optimiser bugs immediately.
4. **`-O` versus no `-O` must agree.** If optimisation changes a program's output, the optimiser is wrong. This one check would have caught the loop bug above instantly.
5. **`objdump -d out`.** Read the real disassembly. It should look like what you emitted.
6. **Force spilling.** Write a function with more live values than you have registers, using values derived from a *parameter* so they cannot be folded away. If nothing spills, your test is not testing what you think.

## Where to stop

**Stop when your demo program compiles, links and prints the right numbers**, and your test corpus passes with and without optimisation. That is a real compiler.

**Worth continuing to:** the control-flow graph (option A). It is the difference between a compiler that works and a compiler you can keep extending, and it retroactively makes your optimiser correct by construction rather than by care.

**Not worth it here:** your own binary encoder, your own linker, or a self-hosting compiler. All three are legitimate projects and all three are much larger than everything above.

## Related

- [[build-your-own-shit/04-your-own-language|Your Own Language]] — the interpreter this is the sequel to
- [[build-your-own-shit/17-your-own-cpu/index|Your Own CPU]] — retarget this compiler at PRIME-1 and close the loop
- [[how-computers-work/08-capstone/06-build-the-language|How Computers Work, module 33]] — the minimal version, compiling to a 16-bit CPU
- [[compilers/index|compilers/]] — the reference course for every stage here
- [[computer-architecture/04-assembly|computer-architecture/assembly]] — the target language
- [[build-your-own-shit/index|Build Your Own Shit index]]
