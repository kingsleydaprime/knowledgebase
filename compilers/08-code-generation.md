# Code Generation

**[Advanced]** — IR to machine code: picking instructions, allocating registers, and obeying the calling convention.

## The three problems

**Instruction selection** — which machine instructions implement this IR?

**Register allocation** — the IR has infinite virtual registers; the machine has 16.

**Instruction scheduling** — what order minimises stalls?

All three are NP-hard in general, and all three have good heuristics.

## Instruction selection

One IR operation may map to many instruction sequences, and one instruction may cover several IR operations:

```
IR:      t1 = a * 4
         t2 = b + t1
         t3 = load t2

x86:     mov rax, [rbx + rcx*4]        ← ONE instruction covers all three
```

x86's addressing modes fold multiplication by 1/2/4/8, addition, and a load into a single instruction. Finding these is **tree tiling** — cover the IR tree with instruction patterns, minimising total cost.

Approaches: **maximal munch** (greedy, take the largest matching pattern), **dynamic programming** (optimal for trees), or **BURS** (table-driven, from a grammar of patterns).

Real compilers use pattern-matching tables — LLVM's SelectionDAG matches subgraphs against TableGen-defined patterns, and GlobalISel is the newer, faster replacement.

```
x * 8            →  shl rax, 3           (not imul)
x / 8   (uint)   →  shr rax, 3
x / 7            →  a multiply by a magic constant, then a shift
x == 0           →  test rax, rax        (shorter than cmp rax, 0)
x = 0            →  xor eax, eax         (shorter, and breaks the dependency chain)
```

That division-by-constant trick is worth knowing: division is ~20–40 cycles, so compilers replace it with a multiply by a precomputed reciprocal plus shifts. It's why dividing by a constant is fast and dividing by a variable isn't.

## Register allocation

The one that matters most for output quality.

**The machine has 16 general-purpose registers on x86-64** (fewer usable — some are reserved), 31 on ARM64. The IR has thousands of virtual registers. Values that don't fit get **spilled** to the stack, and a spill costs a store and later a load.

### Graph colouring

The classic formulation:

1. Compute **live ranges** — where each value is live (from definition to last use) → [[foundations/compilers/06-intermediate-representations|dataflow analysis]]
2. Build an **interference graph** — an edge between values live at the same time
3. **Colour** the graph with K colours (K = number of registers), where adjacent nodes differ
4. Uncolourable nodes get **spilled**

```
a: ├────────┤
b:      ├────────┤        a and b interfere → different registers
c:                ├────┤  c can reuse a's register
```

Graph colouring is NP-complete, so Chaitin's algorithm uses a heuristic: repeatedly remove nodes with fewer than K neighbours (trivially colourable), then colour them back in reverse order. If you get stuck, pick a spill candidate — usually by a cost heuristic weighting loop depth heavily, because a spill inside a loop is far worse.

### Linear scan

Much faster, slightly worse output: sort live intervals by start position, sweep, assign registers, spill the interval ending latest when you run out.

**Used by JITs**, where compile time is runtime — V8, HotSpot's C1, and older LuaJIT. The quality gap versus graph colouring is maybe 5–10%, and the compile-time difference is an order of magnitude.

**SSA-based allocation** exploits a lovely property: **the interference graph of a program in SSA form is chordal**, and chordal graphs are optimally colourable in polynomial time. That's a major practical result and it's why modern allocators work on SSA before destructing φ-nodes.

### What you can influence

Not much directly, but the shape of your code matters: fewer simultaneously-live values means fewer spills. A function with thirty locals live across a call will spill; splitting it often helps more than any flag.

Callee-saved vs caller-saved registers interact with this — a value live across a call must either be in a callee-saved register or be spilled, which is one reason inlining helps so much.

## Calling conventions

The ABI contract, and it's not negotiable. → [[foundations/os/09-syscalls-interrupts-and-the-abi|Syscalls and the ABI]]

**System V AMD64** (Linux, macOS, BSD):

```
integer args:   rdi, rsi, rdx, rcx, r8, r9    then the stack
float args:     xmm0–xmm7
return:         rax (and rdx for 128-bit)
callee-saved:   rbx, rbp, r12–r15             ← the callee must preserve these
caller-saved:   everything else               ← the caller must save if it cares
stack:          16-byte aligned at the call
red zone:       128 bytes below rsp, usable by leaf functions without adjusting rsp
```

Windows x64 uses `rcx, rdx, r8, r9` and a 32-byte shadow space — which is why cross-platform binaries aren't a thing and why FFI must agree on the convention.

A typical prologue and epilogue:

```asm
push rbp                ; save the caller's frame pointer
mov  rbp, rsp           ; establish ours
sub  rsp, 32            ; allocate locals
...
leave                   ; mov rsp, rbp ; pop rbp
ret
```

Frame pointers are omissible (`-fomit-frame-pointer`, default at `-O2`) which frees a register — **and breaks stack unwinding for profilers**. This is why `perf` output is often useless on optimised builds, and why `-fno-omit-frame-pointer` is standard when profiling. Several distributions have re-enabled frame pointers by default for exactly this reason.

## Instruction scheduling

Modern CPUs are pipelined and superscalar. An instruction depending on the immediately preceding one stalls:

```asm
mov rax, [rbx]      ; load — ~4 cycles from L1, ~200 from RAM
add rax, 1          ; STALLS waiting for the load
```

```asm
mov rax, [rbx]      ; start the load
mov rcx, 5          ; independent work fills the gap
add rax, 1          ; the load has landed
```

**List scheduling** over the dependency DAG, prioritising by critical-path length, is the standard approach.

Out-of-order CPUs do this themselves in hardware, so scheduling matters less on modern x86 than it did — but it still matters for in-order cores (many embedded and some ARM), and the compiler's ordering affects register pressure regardless.

## Peephole optimisation

A sliding window over the final instruction stream, rewriting local patterns:

```asm
mov rax, rbx
mov rbx, rax        →   (delete the second — redundant)

add rax, 0          →   (delete)
mov rax, 0          →   xor eax, eax
jmp L1; L1:         →   (delete the jump)
```

Small, cheap, and it cleans up the debris that instruction selection and register allocation leave behind.

## Assembling and linking

Code generation emits assembly or object code; two more stages follow. → [[languages/04-c/01-why-c-and-the-compilation-model|C: The Compilation Model]]

**The assembler** turns mnemonics into bytes and produces an object file with a symbol table and **relocations** — placeholders for addresses not yet known.

**The linker** resolves symbols across object files, assigns final addresses, and patches the relocations.

**Position-independent code** (`-fPIC`) is required for shared libraries — the code must work at any load address, so it goes through the **GOT** (Global Offset Table) for data and the **PLT** (Procedure Linkage Table) for calls.

That indirection is what makes `LD_PRELOAD` work: the dynamic linker resolves a symbol to whichever library comes first, so you can interpose your own `malloc`. It's also a small performance cost, and why `-static` binaries are marginally faster.

**Lazy binding** resolves a function's address on first call, via a PLT stub. `LD_BIND_NOW` disables it, which is what `-Wl,-z,now` sets — required for full RELRO hardening. → [[languages/04-c/12-build-systems|Build Systems]]

## Debug information

DWARF records the mapping from machine code back to source: line numbers, variable locations, types, and unwinding tables.

**Optimisation makes this genuinely hard.** Variables live in different registers at different points or are eliminated entirely; inlined code has no single source location; instructions are reordered. Hence `<optimized out>` in gdb and the general misery of debugging `-O2` builds.

`-Og` exists as a compromise — optimise, but not in ways that destroy debuggability.

## What to do for your own language

If you're building a language, **don't write a native code generator first.**

**A bytecode VM is the right target.** No register allocation, no calling convention, no ABI, no linker, portable by construction. → [[foundations/compilers/09-bytecode-and-virtual-machines|Bytecode VMs]]

If you do want native code:

1. **Target LLVM or Cranelift.** You get all of this for free
2. **Or emit C** and let a C compiler do it. Genuinely legitimate — Nim, Vala, and early C++ all did
3. **Write your own only to learn.** It's the most educational part and by far the largest

For a JIT specifically, Cranelift or a hand-rolled assembler over a small instruction subset is the realistic path. → [[foundations/compilers/11-jit-compilation|JIT]]

---

## Related
- [[foundations/compilers/06-intermediate-representations|Intermediate Representations]] — the input
- [[foundations/compilers/07-optimisation|Optimisation]] — what runs before this
- [[foundations/os/09-syscalls-interrupts-and-the-abi|Syscalls and the ABI]] — the calling convention as a contract
- [[languages/04-c/12-build-systems|C: Build Systems]] — assembling and linking, practically
- [[foundations/compilers/README|Compilers course map]]
