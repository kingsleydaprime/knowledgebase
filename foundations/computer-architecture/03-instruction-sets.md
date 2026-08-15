# Instruction Sets

**[Intermediate]** — What a CPU can be asked to do, how instructions are encoded, and the design choices that separate x86 from ARM.

## What an instruction does

**Four things a CPU instruction can be:**

**Data movement** — load, store, move between registers. **The majority of real code**, which surprises people expecting arithmetic to dominate.

**Arithmetic and logic** — add, subtract, multiply, and, or, shift.

**Control flow** — jump, branch, call, return.

**System** — syscall, interrupt handling, privileged operations. → [[foundations/os/09-syscalls-interrupts-and-the-abi|Syscalls and the ABI]]

## Registers

**The fastest storage on the machine** — a handful of named locations inside the CPU, accessible in a single cycle.

| ISA | General-purpose registers |
|---|---|
| x86 (32-bit) | **8** — famously cramped |
| x86-64 | 16 |
| AArch64 | **31** |
| RISC-V | 32 |

> **Register count matters more than it sounds.** With few registers the compiler must **spill** values to the stack and reload them, which costs memory traffic. **x86-64 doubling the register count was a bigger performance win than the 64-bit addressing** for most code.
>
> But note the twist: modern x86 chips have **hundreds of physical registers** and rename the architectural ones onto them. The ISA exposes 16; the hardware has far more. → [[foundations/computer-architecture/10-out-of-order-and-superscalar|Register Renaming]]

**Special registers:** the **program counter** (RIP/PC), the **stack pointer** (RSP/SP), and **flags** (zero, carry, sign, overflow) set by arithmetic and tested by branches.

## Addressing modes

**How an instruction names its operands.**

| Mode | Example | Meaning |
|---|---|---|
| Immediate | `mov rax, 5` | constant in the instruction |
| Register | `mov rax, rbx` | register contents |
| Direct | `mov rax, [0x1000]` | fixed address |
| Register indirect | `mov rax, [rbx]` | address in a register |
| **Base + index × scale + disp** | `mov rax, [rbx + rcx*8 + 16]` | **array indexing in one instruction** |
| PC-relative | `lea rax, [rip + off]` | position-independent code |

**That fifth row is why x86 array access is compact:** `arr[i]` for 8-byte elements is a single addressing mode, computing `base + i*8` in the address generation unit for free.

**RISC ISAs deliberately offer fewer.** ARM has base+offset and some scaling; RISC-V has only base+immediate. **Anything more complex takes extra instructions** — the trade being simpler, faster decode and a more regular pipeline.

## Load/store vs register-memory

**The defining architectural split.**

**Load/store (RISC)** — only `load` and `store` touch memory; everything else is register-to-register:

```asm
ldr  x0, [x1]        // load
add  x0, x0, #1      // compute
str  x0, [x1]        // store
```

**Register-memory (CISC)** — arithmetic can operate directly on memory:

```asm
add  qword [rbx], 1  // read-modify-write in one instruction
```

**RISC's argument:** memory access has variable latency (cache hit or miss), so **separating it from computation makes pipelining far easier.** Every instruction has predictable timing.

**CISC's argument:** fewer instructions, smaller code, better instruction-cache utilisation.

**How it resolved:** x86 chips **crack** complex instructions into micro-ops internally, so `add [rbx], 1` becomes load, add, store. **The CPU is RISC inside and CISC outside** — you get code density from the ISA and pipelining from the micro-ops. Both sides were right about different things.

## Instruction encoding

**Fixed-length (ARM, RISC-V)** — every instruction is 32 bits.

*Decode is trivial and parallel.* Wastes space on simple instructions, and constants must be built from pieces (a 64-bit constant takes several instructions).

**Variable-length (x86)** — 1 to 15 bytes.

*Compact, and immediate values fit inline.* **Decode is genuinely hard**: you cannot find where instruction $n+1$ starts without decoding instruction $n$.

> **This is x86's real, permanent disadvantage.** To decode 8 instructions in parallel you must speculate about boundaries, which costs power and silicon. **Intel and AMD spend enormous effort on decode — including a micro-op cache to skip it entirely for hot loops.** ARM and RISC-V get parallel decode for free.
>
> It's a substantial part of why Apple Silicon achieves high performance at low power: an 8-wide decoder is straightforward with fixed-length instructions and very difficult without.

**Compressed encodings** split the difference: ARM's Thumb-2 and RISC-V's **C extension** add 16-bit forms for common instructions, recovering ~25–30% code density while keeping decode simple.

## Calling conventions

**Not part of the ISA, but part of the ABI** — the agreement that lets separately-compiled code interoperate.

**Specifies:** which registers pass arguments, where the return value goes, which registers the callee must preserve, stack alignment, and how the stack frame is laid out.

| | First integer args | Return |
|---|---|---|
| **System V** (Linux/macOS x86-64) | RDI, RSI, RDX, RCX, R8, R9 | RAX |
| **Microsoft x64** | RCX, RDX, R8, R9 | RAX |
| **AArch64** | X0–X7 | X0 |

**Caller-saved (volatile)** — the caller must save these if it needs them after the call. **Callee-saved** — the callee must restore them.

**Why it matters to you:**

- **FFI.** Calling C from Rust, Python or Go requires matching the convention exactly. Mismatch means corruption, not an error → [[languages/03-rust/15-unsafe-and-ffi|FFI]]
- **Debugging.** Reading a stack trace or a core dump means knowing where arguments live
- **Inline assembly** must declare which registers it clobbers
- **Stack alignment** — System V requires 16-byte alignment at a call, and violating it crashes on SSE instructions in ways that look unrelated

## SIMD

**Single Instruction, Multiple Data** — one instruction operating on a vector of values.

```
 scalar:  a₀+b₀
 SIMD:   [a₀ a₁ a₂ a₃] + [b₀ b₁ b₂ b₃] = [c₀ c₁ c₂ c₃]
```

| Extension | Width |
|---|---|
| SSE | 128-bit |
| AVX2 | 256-bit |
| AVX-512 | 512-bit |
| ARM NEON | 128-bit |
| **ARM SVE / RISC-V V** | **vector-length agnostic** |

**4–16× throughput on the right workload:** image processing, audio, matrix multiply, checksums, string search, and the inner loops of ML frameworks.

**How to actually use it:**

**Auto-vectorisation** — the compiler does it. **Fragile**: it needs no loop-carried dependencies, known alignment, no aliasing between pointers, and a trip count it can reason about. Use `-fopt-info-vec-missed` to find out why it didn't fire. → [[foundations/compilers/07-optimisation|Optimisation]]

**Intrinsics** — write the vector operations explicitly. Full control, unreadable, and tied to one ISA.

**Libraries** — BLAS, Eigen, `std::simd`, `ndarray`. **Usually the right answer.**

> **Two practical warnings.** **AVX-512 causes frequency throttling** on many Intel chips — heavy use downclocks the core, and it can be a net loss for mixed workloads. And **vectorisation only helps if you're compute-bound**; if you're waiting on memory, wider registers change nothing. **Check with a profiler before reaching for intrinsics.** → [[foundations/computer-architecture/12-performance|Performance]]

**ARM SVE and RISC-V's vector extension are the modern design**: the code doesn't specify the vector width, so the same binary uses 128-bit or 2048-bit hardware. **No recompiling for each generation** — a genuinely better approach than AVX's fixed widths.

## Specialised instructions

**Where hardware specialisation shows up in the ISA:**

- **AES-NI** — AES rounds in hardware, ~10× faster and **constant-time**, which removes a whole class of timing side channels → [[cybersecurity/05-cryptography/02-symmetric-encryption|Symmetric Encryption]]
- **CRC32, SHA extensions** — checksums and hashing
- **`popcnt`, `lzcnt`, `tzcnt`** — bit counting, used in bitboards, compression, and set operations
- **Atomics and `cmpxchg`** — the foundation of every lock-free data structure → [[foundations/os/06-concurrency-primitives|Concurrency Primitives]]
- **`rdtsc`** — cycle counter, useful for microbenchmarks and dangerous for timing attacks
- **Matrix extensions** — Intel AMX, ARM SME. Systolic arrays for ML, in the CPU

**The pattern: when a workload matters enough, it gets an instruction.** Cryptography and ML are the recent examples.

## Practical notes

**Read the disassembly when performance matters.** `objdump -d`, `perf annotate`, or Godbolt. **It's the ground truth**, and it frequently contradicts what you assumed the compiler did.

**Compile for your target.** `-march=native` unlocks AVX and other extensions. **The default targets a very old baseline** — often just SSE2 on x86-64 — so you may be leaving several-fold performance unclaimed.

**But check portability.** A binary built with `-march=native` crashes with `SIGILL` on older hardware. Use runtime dispatch (`__builtin_cpu_supports`) for distributed binaries.

**Don't write assembly.** Modern compilers beat hand-written assembly except in narrow cases (crypto needing constant time, specific SIMD kernels). **Write clear C and check the output.**

**Intrinsics before assembly** if you must go low-level — you keep register allocation and scheduling.

---

## Related
- [[foundations/computer-architecture/04-assembly|Assembly]] — reading and writing this
- [[foundations/computer-architecture/05-the-datapath|The Datapath]] — how instructions execute
- [[foundations/compilers/08-code-generation|Code Generation]] — what emits these
- [[foundations/computer-architecture/README|Architecture map]]
