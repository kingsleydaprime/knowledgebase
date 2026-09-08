# JIT Compilation

**[Advanced]** — Compiling at runtime, and the speculative optimisations that let a JIT beat an ahead-of-time compiler.

## The claim

A JIT can be **faster than AOT**, which sounds impossible until you see what it knows that a static compiler doesn't:

**The actual types.** In a dynamic language, `a + b` could be integers, floats, strings, or user objects. AOT must emit code handling all of them. A JIT observes that this site has only ever seen integers and emits an integer add plus a guard.

**Which branches are taken.** Profile data lets it lay out hot paths contiguously and hoist cold paths out of the instruction cache.

**The concrete call targets.** A virtual call with one observed receiver type becomes a direct call, then gets inlined — **speculative devirtualisation**, the biggest win in Java and JavaScript.

**The actual CPU.** AOT targets a baseline ISA for portability; a JIT emits AVX-512 if the machine has it.

The cost is warm-up, memory, and enormous complexity.

## Tiered execution

Nobody JITs everything — compilation isn't free, and most code runs once.

```
        ┌──────────────┐   hot?   ┌───────────────┐  very hot?  ┌──────────────┐
source →│ INTERPRETER  │─────────→│ BASELINE JIT  │────────────→│ OPTIMISING   │
        │ instant start│          │ fast compile  │             │ JIT          │
        │ slow         │          │ ~5× faster    │             │ ~50× faster  │
        └──────────────┘          └───────────────┘             └──────────────┘
                                                                        │
                                                        ┌───────────────┘
                                                        ▼
                                                  DEOPTIMISE
                                             (assumption violated)
```

| Runtime | Tiers |
|---|---|
| **HotSpot** | interpreter → C1 (fast) → C2 or Graal (optimising) |
| **V8** | Ignition (interpreter) → Sparkplug (baseline) → Maglev → TurboFan |
| **SpiderMonkey** | interpreter → Baseline → IonMonkey |
| **PyPy** | interpreter → tracing JIT |
| **LuaJIT** | interpreter → tracing JIT |

Promotion is driven by **counters** — invocations and loop back-edges. Cross a threshold and the method is queued for compilation, usually on a background thread so the program keeps running.

**On-stack replacement (OSR)** handles the case where a long-running loop is hot but its enclosing method was only entered once: the runtime swaps the executing frame from interpreted to compiled *mid-loop*. Fiddly, and necessary — otherwise a `main` with a hot loop never gets optimised.

## Method JIT vs tracing JIT

**Method-based** — compile a whole function. HotSpot, V8, .NET.

**Tracing** — record a linear trace of the actual instructions executed through a hot loop, including across function boundaries, then compile that straight-line trace with guards.

```
for (...) { foo(); bar(); }

trace:  [loop header] → foo's body inlined → bar's body inlined → [jump to header]
        with a GUARD at every point the trace assumed something
```

Tracing gets **aggressive inlining for free** — the trace already crosses call boundaries — and produces excellent code for numeric loops. LuaJIT and PyPy are tracing JITs, and LuaJIT is one of the fastest dynamic-language implementations ever built.

It's weaker on branchy code, where traces multiply and the guards dominate.

## Speculation and deoptimisation

The mechanism that makes JITs fast, and the thing to understand:

```javascript
function add(a, b) { return a + b; }
// called 10,000 times with integers
```

The JIT emits, roughly:

```asm
    ; GUARD: both are small integers?
    test rdi, 1
    jnz  deopt
    test rsi, 1
    jnz  deopt
    ; the fast path — a single instruction
    add  rax, rdi, rsi
    jo   deopt              ; overflow → deopt
    ret
deopt:
    ; reconstruct the interpreter frame and fall back
```

If someone later calls `add("a", "b")`, the guard fails and the runtime **deoptimises**: discards the compiled code, rebuilds an interpreter frame from the compiled one, and resumes in the interpreter.

**Deoptimisation is the hard part.** The compiled frame has values in registers, in different layouts, possibly with allocations elided by escape analysis. Reconstructing a valid interpreter state requires the compiler to have recorded, at every deopt point, exactly where every value lives. That bookkeeping is a large fraction of a JIT's complexity.

**Inline caching** is the same idea for property access:

```javascript
obj.field
```

- **Monomorphic** — one shape seen. A shape check plus a fixed-offset load. Fast
- **Polymorphic** — 2–4 shapes. A small inline check chain
- **Megamorphic** — many shapes. Fall back to a hash lookup. Slow

**This is why "monomorphic code is fast" is real advice in JavaScript.** Passing consistently-shaped objects keeps sites monomorphic; a function called with ten different object shapes goes megamorphic and loses the optimisation entirely. V8's hidden classes exist to make shape comparison a pointer compare. → [[foundations/compilers/09-bytecode-and-virtual-machines|inline caching]]

## Warm-up

The JIT's structural weakness. A process starts interpreting, gathers profiles, compiles, maybe deoptimises and recompiles. Peak performance arrives **seconds to minutes** in.

That's fine for a long-running server and terrible for:

- **CLI tools** — the process exits before anything is compiled
- **Serverless** — cold starts are the dominant cost
- **Short-lived batch jobs**

The responses:

**AOT compilation of the managed language** — GraalVM Native Image, .NET Native AOT, CRaC. Instant startup, lower memory, no JIT benefits, and closed-world assumptions that break reflection.

**Tiered compilation** — get *some* speedup quickly rather than the best speedup eventually.

**Profile caching** — .NET's ReadyToRun and Android's baseline profiles ship pre-compiled or pre-profiled code so the first run isn't cold.

This is the concrete reason [[languages/02-go/README|Go]] and [[languages/03-rust/README|Rust]] win for CLI tools and short-lived processes, regardless of peak throughput.

## How you actually emit code

A JIT needs writable-then-executable memory:

```c
void *mem = mmap(NULL, size, PROT_READ | PROT_WRITE,
                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
memcpy(mem, machine_code, size);
mprotect(mem, size, PROT_READ | PROT_EXEC);        // W^X: never both at once
__builtin___clear_cache(mem, mem + size);          // required on ARM
((void (*)())mem)();
```

Three things that bite:

**W^X.** Modern systems refuse pages that are simultaneously writable and executable — a fundamental exploit mitigation. You map writable, write, then flip to executable. macOS on Apple Silicon requires `pthread_jit_write_protect_np()` and a specific entitlement.

**Instruction cache flushing.** x86 keeps I-cache coherent with D-cache; **ARM does not**. Skip the flush and you execute stale bytes — a spectacular, architecture-specific bug.

**Some environments forbid it entirely.** iOS bans JIT for third-party apps (which is why JavaScriptCore has a special entitlement and why other browsers on iOS are slower). Some hardened container runtimes block it too.

Rather than emitting bytes by hand, use a backend: **Cranelift** (designed for fast compilation), **LLVM's ORC JIT** (excellent code, slow compilation — usually the wrong trade for a JIT), **AsmJit**, or **DynASM** (what LuaJIT uses).

## Should you write one?

**For build-your-own-language: no.** A JIT is comparable in effort to everything else in the language combined. Get a good bytecode VM first — [[foundations/compilers/09-bytecode-and-virtual-machines|computed goto, inline caching, NaN boxing]] deliver a large fraction of the benefit for a fraction of the work.

**Consider it when** you have a well-defined hot inner loop and a genuine need — a regex engine compiling patterns, a query engine compiling plans, a template engine, a numeric DSL. Those are tractable because the domain is narrow.

**A realistic path:** compile only hot functions, only with monomorphic types, with a guard that bails to the interpreter on anything unexpected. No deoptimisation machinery needed if "bail out" means "abandon this compiled version and interpret from the top of the next call".

## The wider picture

The interpreter/JIT/AOT distinction is blurring:

- **CPython 3.13** added a copy-and-patch JIT — a lightweight technique that stencils precompiled machine-code templates together, far simpler than a traditional JIT
- **GraalVM** AOT-compiles Java *and* provides Truffle, a framework for building self-optimising interpreters that become JITs almost for free
- **WebAssembly** is a compilation target that browsers JIT, and `wasmtime` AOT-compiles
- **eBPF** JITs verified bytecode inside the kernel → [[foundations/os/09-syscalls-interrupts-and-the-abi|eBPF]]

**Copy-and-patch is worth knowing about** if you want JIT-like speed without writing a compiler: you precompile small machine-code templates for each bytecode operation at build time, then at runtime concatenate and patch them. It's ~2× faster than an interpreter for a small fraction of a real JIT's complexity, and it's a genuinely practical option for a hobby language.

---

## Related
- [[foundations/compilers/09-bytecode-and-virtual-machines|Bytecode and Virtual Machines]] — what a JIT sits on top of
- [[foundations/compilers/07-optimisation|Optimisation]] — the same passes, with runtime information
- [[foundations/compilers/10-garbage-collection|Garbage Collection]] — the other half of a managed runtime
- [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM Internals]] — HotSpot's tiers in practice
- [[foundations/compilers/README|Compilers course map]]
