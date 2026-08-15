# Assembly

**[Intermediate]** — Reading it, which is the skill that matters. The stack, function calls, and what your code actually compiles to.

## Why read assembly

**You will almost certainly never write assembly professionally. You will read it.**

**When it's the only way to know:**

- **Performance.** Did the compiler vectorise that loop? Inline that call? Hoist that bounds check? **The source doesn't tell you; the disassembly does**
- **Debugging optimised builds.** When the debugger says "value optimised out", assembly is what's left
- **Crash analysis.** A stack trace with no symbols, a core dump, a `SIGILL`
- **Security.** Reverse engineering, exploit development, understanding a CVE → [[cybersecurity/02-ethical-hacking/README|Ethical Hacking]]
- **Understanding costs.** Seeing that a virtual call is a load plus an indirect branch makes the cost concrete

**Godbolt (compiler explorer) is the tool.** Paste code, see assembly, change flags, watch it change. **An hour there teaches more about optimisation than any amount of reading.**

## Two syntaxes

**The first confusion, and it's purely cosmetic:**

```asm
; Intel syntax (Windows, Godbolt default, NASM)
mov rax, rbx        ; destination first

# AT&T syntax (GNU/Linux default, objdump)
movq %rbx, %rax     # source first — REVERSED
```

**AT&T** prefixes registers with `%`, immediates with `$`, suffixes for size (`movq`), and **puts the destination last.** **Intel** puts the destination first and uses `[...]` for memory.

**`objdump -d -M intel`** gives you Intel syntax on Linux, which is worth setting up if you learned it that way.

## Reading x86-64

**Enough to follow a disassembly**, which is the goal:

```asm
mov  rax, rbx          ; rax = rbx
mov  rax, [rbx]        ; rax = *rbx          — brackets mean dereference
lea  rax, [rbx+rcx*8]  ; rax = rbx + rcx*8   — computes ADDRESS, no memory access
add  rax, 5            ; rax += 5
cmp  rax, rbx          ; set flags from rax - rbx (result discarded)
test rax, rax          ; set flags from rax & rax — the idiomatic zero check
je   label             ; jump if equal (ZF set)
jne / jl / jg / jle    ; not equal / less / greater / less-or-equal
call func              ; push return address, jump
ret                    ; pop return address, jump to it
push rax / pop rax     ; stack operations
xor  rax, rax          ; rax = 0 — shorter and faster than mov rax, 0
```

**Three idioms to recognise immediately:**

**`xor rax, rax`** is `rax = 0`. Two bytes instead of five, and the CPU special-cases it as a zeroing idiom with no dependency on the old value.

**`test rax, rax` + `je`** is `if (x == 0)`. `test` ANDs without storing, purely to set flags.

**`lea`** — "load effective address" — **does arithmetic, not memory access.** Compilers use it as a fast three-operand add-and-multiply: `lea rax, [rbx + rcx*4 + 8]` computes a value in one instruction without touching the ALU flags. **Seeing `lea` in arithmetic code is normal, not a memory operation.**

## The stack

**Grows downward** — toward lower addresses — on x86 and ARM.

```
 high addresses
   ┌──────────────────┐
   │  caller's frame  │
   ├──────────────────┤
   │  return address  │  ← pushed by call
   ├──────────────────┤
   │  saved RBP       │  ← frame pointer chain
   ├──────────────────┤ ← RBP
   │  local variables │
   │  saved registers │
   │  spilled temps   │
   ├──────────────────┤ ← RSP (stack pointer)
   │   (unused)       │
 low addresses
```

**A standard prologue and epilogue:**

```asm
push rbp            ; save caller's frame pointer
mov  rbp, rsp       ; establish ours
sub  rsp, 32        ; allocate 32 bytes of locals
...
mov  rsp, rbp       ; deallocate
pop  rbp            ; restore
ret
```

**`-fomit-frame-pointer` removes this** and frees a register — the default at `-O2` for years. **The cost is that stack unwinding needs DWARF data instead of walking the RBP chain**, which is why profilers sometimes give broken stacks. `perf` wants `--call-graph dwarf` or a build with frame pointers. **Several distributions re-enabled frame pointers by default in 2023–24 specifically for profiling.**

**Red zone** — 128 bytes below RSP that leaf functions may use without adjusting the pointer. A small System V optimisation, and it must be disabled in kernel code (signals would clobber it).

## Function calls

```c
int add(int a, int b) { return a + b; }
int main() { return add(3, 4); }
```

```asm
add:
    lea  eax, [rdi + rsi]   ; args in RDI, RSI — one instruction, no frame
    ret

main:
    mov  eax, 7             ; constant-folded at compile time
    ret
```

> **Look at `main`.** The call is gone entirely — inlined, then constant-folded. **This is why microbenchmarks lie:** if the result isn't used, the compiler deletes the work. Use `volatile`, a `black_box`, or a benchmarking framework that defeats it. → [[foundations/computer-architecture/12-performance|Performance]]

**Recognising call patterns:**

- **Direct call** — `call func`. Predictable, cheap
- **Indirect call** — `call [rax]` or `call rax`. Function pointer, virtual method, or dynamic dispatch. **Costs a load plus a branch prediction** → [[foundations/computer-architecture/07-branch-prediction-and-speculation|Branch Prediction]]
- **PLT call** — `call func@plt`. A dynamically-linked library call through the procedure linkage table
- **Tail call** — `jmp func` instead of `call`. The frame is reused, so no stack growth

## Common patterns

**A loop:**

```asm
    mov  ecx, 0
.loop:
    cmp  ecx, 10
    jge  .done
    ...
    inc  ecx
    jmp  .loop
.done:
```

**Optimised loops usually look different** — the compiler rotates them so the branch is at the bottom (one branch per iteration instead of two), unrolls them, and often vectorises.

**A switch statement** becomes either a chain of compares (few cases), a **jump table** (dense cases — an indirect jump through an array of addresses), or a binary search tree of compares (sparse). **Seeing a jump table tells you the compiler found your cases dense.**

**A virtual call:**

```asm
mov  rax, [rdi]        ; load vtable pointer from object
call [rax + 16]        ; call the third entry
```

**Two dependent loads and an indirect branch.** That's the cost of dynamic dispatch, and it's why devirtualisation is a valuable optimisation.

**Bounds checking** in Rust or Java:

```asm
cmp  rsi, [rdi + 8]    ; index vs length
jae  .panic            ; unsigned compare catches negative too
```

**Two instructions, well-predicted.** **This is why "bounds checking is slow" is largely false** — the branch predicts perfectly and the compiler often eliminates the check entirely when it can prove the index is in range. → [[languages/03-rust/18-performance-and-zero-cost|Zero-Cost Abstractions]]

## AArch64, briefly

Worth recognising since it's on every phone and increasingly on servers:

```asm
ldr  x0, [x1]          ; load
str  x0, [x1]          ; store
add  x0, x1, x2        ; three-operand — destination is separate
cbz  x0, label         ; compare and branch if zero, one instruction
bl   func              ; branch with link (call) — return address in X30
ret                    ; branches to X30
```

**Differences that stand out:**

- **Three-operand form** — `add x0, x1, x2` doesn't destroy an input, unlike x86's two-operand `add`
- **Return address in a register (X30)**, not pushed to the stack. **Cheaper calls**, and leaf functions need no stack traffic at all
- **Fixed 32-bit instructions**, so every instruction boundary is obvious
- **31 general registers**, plus a zero register that reads as 0 and discards writes
- **Conditional execution and combined compare-and-branch** reduce instruction count

## Inline assembly

**Rarely correct, occasionally necessary.**

```c
uint64_t rdtsc(void) {
    uint32_t lo, hi;
    __asm__ volatile ("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}
```

**Legitimate uses:** instructions with no intrinsic (`rdtsc`, `cpuid`), privileged instructions in kernel code, constant-time cryptographic primitives, and atomics not exposed by the language.

**The rules if you must:**

- **Declare clobbers correctly.** An undeclared clobbered register produces corruption that appears far from the cause
- **Use `volatile`** if the code has effects the compiler can't see, or it may be deleted or hoisted
- **Add a `"memory"` clobber** if it touches memory the compiler tracks
- **Prefer intrinsics** — you keep register allocation and scheduling
- **It blocks optimisation** across the boundary, so a small `asm` block in a hot loop can cost more than it saves

## Practical notes

**Godbolt, constantly.** Change one line, see what moves.

**Compare `-O0` and `-O2`.** The difference is startling and instructive — `-O0` output maps almost line-for-line to source, which makes it the right place to *learn* to read assembly.

**`perf annotate`** shows assembly with per-instruction sample counts. **This is how you find the actual hot instruction**, which is frequently not where you expected.

**Symbols matter.** Build with `-g` and keep symbols, or your stack traces are hex addresses. `addr2line` and `c++filt` recover what you can.

**Don't over-interpret instruction counts.** A longer instruction sequence can be faster if it has more instruction-level parallelism or fewer cache misses. **Measure.** → [[foundations/computer-architecture/12-performance|Performance]]

---

## Related
- [[foundations/computer-architecture/03-instruction-sets|Instruction Sets]] — the vocabulary
- [[foundations/compilers/08-code-generation|Code Generation]] — what produces this
- [[foundations/computer-architecture/12-performance|Performance]] — using it to make things fast
- [[foundations/computer-architecture/README|Architecture map]]
