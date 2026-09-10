# Module 27: The Bridge (Parts VIII to XVIII)

**[Intermediate → Advanced]** — You have built every physical component of a computer. This module is the route through the parts of the stack this vault already teaches well — with the dependency from Parts II–VII named at each step, so you know *why* you can now read them.

## Before you start

You should have completed **modules 1–26**. Specifically, you should be able to:

- Explain the digital abstraction and what it costs — [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]]
- Derive a logic gate from transistors — [[how-computers-work/04-logic/01-gates-from-transistors|module 15]]
- Build an ALU and explain why the carry chain sets clock speed — [[how-computers-work/05-combinational/04-the-alu|module 23]]
- Explain how feedback creates memory — [[how-computers-work/06-memory/01-latches-and-flip-flops|module 24]]
- Build a register file and a program counter — [[how-computers-work/06-memory/02-registers-and-counters|module 25]]

**If any of those are shaky, go back.** The whole point of a bottom-up course is that you never have to take the layer below on faith — and everything from here assumes you don't.

---

## 1. What this module is, and what it is not

**This is not a summary of Parts VIII–XVIII.** It is a *reading route*.

The upper half of the computing stack — datapaths, ISAs, caches, pipelining, operating systems, compilers — is already taught properly elsewhere in this vault, in four full courses totalling many weeks of work. Rewriting them here would duplicate thousands of lines and create two versions to keep in sync.

**What was missing was never the material. It was the thread** — the reason each of those courses is the next thing to read, and what from the physics half makes it comprehensible.

So each section below gives you:

1. **The dependency** — what you built in Parts II–VII that this layer stands on
2. **The destination** — exactly which notes to read
3. **What to watch for** — the moment where your bottom-up knowledge changes how you read it

**Be realistic about scale.** Parts II–VII were 26 modules and perhaps six weeks. Parts VIII–XVIII are four courses and considerably more. This module is a map, not a shortcut.

---

## 2. Where you are

```
   ✅ PART II    electricity, signals, the digital abstraction
   ✅ PART III   atoms, silicon, bands, doping, PN junctions
   ✅ PART IV    transistors, MOSFET physics, CMOS, fabrication
   ✅ PART V     gates, Boolean algebra, K-maps, NAND universality, buffers
   ✅ PART VI    MUX/decoders, adders, multipliers, the ALU
   ✅ PART VII   latches, registers, the program counter, memory technology
   ───────────────────────────────────────────────────────────────
   ▶  PART VIII  assembling it into a CPU          <- you are here
      PART IX    instruction set architecture
      PART X     memory hierarchy
      PART XI    making the CPU fast
      PART XII   the software-hardware interface
      PART XIII  operating systems
      PART XIV   programming languages
      PART XV    compilers
      PART XVI   interpreters and runtimes
      PART XVII  language runtime systems
      PART XVIII the complete trace
```

**You have every component. What remains is organisation** — and then the software that exploits it.

---

## 3. Part VIII — Building a computer

**The dependency:** you have an ALU ([[how-computers-work/05-combinational/04-the-alu|module 23]]), a register file and a program counter ([[how-computers-work/06-memory/02-registers-and-counters|module 25]]), and memory ([[how-computers-work/06-memory/03-memory-technology|module 26]]). A CPU is those four blocks plus multiplexers deciding what connects to what, plus a control unit deciding the multiplexers.

**Read:**

- [[computer-architecture/01-what-architecture-is|computer-architecture/what architecture is]]
- [[computer-architecture/05-the-datapath|computer-architecture/the datapath]] — **the central note for this part**

**What to watch for:** the datapath diagram will look familiar, because you built every box in it. **The new idea is the control unit** — the block turning an opcode into the signals steering everything else.

You have already met it concretely: the control table in [[build-your-own-shit/17-your-own-cpu/01-digital-simulator|the PRIME-1 build guide]] is exactly this, for a real ISA. **Read the datapath note with that table beside you** and the abstraction will not be abstract.

---

## 4. Part IX — Instruction set architecture

**The dependency:** [[how-computers-work/05-combinational/04-the-alu|Module 23]] ended by noting that the ALU's function-select bits come from the instruction. **The ISA is the specification of what those bits mean** — the contract between hardware and software.

**Read:**

- [[computer-architecture/03-instruction-sets|computer-architecture/instruction sets]] — RISC vs CISC, encoding, addressing modes
- [[computer-architecture/04-assembly|computer-architecture/assembly]] — actually writing it

**What to watch for:** the ISA is where the two directions of this course meet. **Everything below it is physics; everything above it is software** — and the ISA is deliberately positioned as the one interface both sides agree on, which is why the same binary runs on chips with wildly different microarchitectures.

**Do the capstone alongside this.** [[how-computers-work/08-capstone/02-the-isa|Module 29]] has you design your own ISA, and designing one teaches more than reading about six.

---

## 5. Part X — Memory hierarchy

**The dependency:** [[how-computers-work/06-memory/03-memory-technology|Module 26]] derived the hierarchy from cell costs — SRAM is fast and 23× larger per bit than DRAM, so you get kilobytes of one and gigabytes of the other. **You already know why the hierarchy must exist.** These notes are about exploiting it.

**Read:**

- [[computer-architecture/08-the-memory-hierarchy|computer-architecture/the memory hierarchy]]
- [[computer-architecture/09-caches-in-depth|computer-architecture/caches in depth]]
- [[os/04-virtual-memory|os/virtual memory]] — address translation, page tables, the TLB

**What to watch for:** caching only works because programs exhibit **locality**. Nothing in the hardware guarantees that — it is an empirical property of real code, and a program that violates it (random access over a huge array) gets no benefit at all.

Also connect it back: [[how-computers-work/06-memory/03-memory-technology|module 26]] explained why DRAM has row buffers and why sequential access is faster. **Cache lines exist to exploit exactly that.**

---

## 6. Part XI — Making the CPU fast

**The dependency:** [[how-computers-work/01-electricity/04-signals-and-time|Module 4]] showed the critical path sets $f_{max}$, and that halving it gives less than double the clock because register overheads do not shrink. [[how-computers-work/05-combinational/02-adders|Module 21]] showed the carry chain is usually that critical path.

**Pipelining is the response**: if you cannot make the path shorter, cut it into stages so a new instruction can start each cycle.

**Read, in order:**

- [[computer-architecture/06-pipelining|computer-architecture/pipelining]] — stages, hazards, forwarding, stalls
- [[computer-architecture/07-branch-prediction-and-speculation|computer-architecture/branch prediction]]
- [[computer-architecture/10-out-of-order-and-superscalar|computer-architecture/out-of-order and superscalar]]
- [[computer-architecture/12-performance|computer-architecture/performance]] — CPI, Amdahl's law, and the power wall

**What to watch for:** the **read-after-write hazard** in pipelining is the exact timing question from [[how-computers-work/06-memory/02-registers-and-counters|module 25]] — an instruction reading a register before an earlier instruction's write has landed. You met it as "reads see the old value"; here it becomes a problem needing forwarding logic.

And [[computer-architecture/12-performance|performance]] will discuss the power wall. **You derived it** in [[how-computers-work/01-electricity/02-resistance-and-ohms-law|module 2]] and again in [[how-computers-work/03-transistors/02-mosfet-physics|module 12]]: $P = \alpha CV^2f$, with $V$ floored by the 60 mV/decade subthreshold limit. Read it as confirmation rather than new information.

---

## 7. Part XII — The software-hardware interface

**The dependency:** you can read machine code as bit fields. This part is about how those bits get into a file and then into memory.

**Read:**

- [[compilers/08-code-generation|compilers/code generation]] — covers assembly output, object files, symbols and relocation
- [[languages/04-c/01-why-c-and-the-compilation-model|languages/c/the compilation model]] — the four stages, and why headers exist
- [[os/09-syscalls-interrupts-and-the-abi|os/syscalls, interrupts and the ABI]] — the calling convention and how a program talks to the kernel

> [!NOTE]
> **Honest gap.** This vault has no dedicated note on **linkers and executable formats**. Static versus dynamic linking, relocation entries, the ELF layout and the dynamic loader are covered *in passing* across the three notes above rather than taught as a unit.
>
> If you want that properly, the standard reference is Levine's *Linkers and Loaders*, and `man elf` plus `readelf -a` on a real binary teaches a surprising amount in an hour.
>
> **This is the weakest link in the chain from your source code to the CPU**, and it is worth knowing that it is a gap rather than assuming you missed something.

---

## 8. Part XIII — Operating systems

**The dependency:** [[how-computers-work/06-memory/03-memory-technology|Module 26]] gave you physical memory. An OS is what shares one machine between many programs that each think they own it.

**Read** [[os/index|os/]] in order. The essential path:

- [[os/01-what-an-os-is|what an OS is]] — kernel vs user space, privilege levels
- [[os/02-processes-and-threads|processes and threads]]
- [[os/03-scheduling|scheduling]]
- [[os/04-virtual-memory|virtual memory]] — if you skipped it in Part X, read it now
- [[os/09-syscalls-interrupts-and-the-abi|syscalls and interrupts]]

**What to watch for:** **interrupts are a hardware mechanism.** A device asserts a line, the CPU finishes its current instruction, saves the PC, and jumps to a handler. That is your program counter ([[how-computers-work/06-memory/02-registers-and-counters|module 25]]) being loaded by something other than the program — the same mechanism as a branch, triggered externally.

And the interrupt controller deciding *which* device wins is a **priority encoder** from [[how-computers-work/05-combinational/01-multiplexers-and-decoders|module 20]].

---

## 9. Parts XIV–XVII — Languages, compilers and runtimes

**The dependency:** you can now read the machine code a compiler emits, and know what each instruction physically does. **This is the top-down half of the course**, descending to meet the bottom-up half at the ISA.

**Read:**

| Part | Course |
| :--- | :--- |
| XIV — Programming languages | [[programming-language-theory/index\|programming-language-theory/]] — syntax, semantics, type systems |
| XV — Compilers | [[compilers/index\|compilers/]] modules 1–8 — lexing, parsing, ASTs, IR, optimisation, codegen |
| XVI — Interpreters and VMs | [[compilers/10-bytecode-and-virtual-machines\|bytecode and VMs]], [[compilers/12-jit-compilation\|JIT]] |
| XVII — Runtime systems | [[compilers/11-garbage-collection\|garbage collection]], [[os/05-memory-allocation\|os/memory allocation]] |

**What to watch for:** [[compilers/07-optimisation|optimisation]] will describe **strength reduction** — replacing `x * 8` with `x << 3`. You know exactly why that is worth doing: a constant shift is free wiring, while a multiply is $O(n^2)$ gates ([[how-computers-work/05-combinational/03-multipliers-and-comparators|module 22]]).

**Most compiler optimisations become obvious once you know the hardware costs.** That is the payoff for having gone bottom-up.

---

## 10. Part XVIII — The complete trace

The original curriculum's final exercise, and the point of everything:

> Take `int x = 5 + 3;` and trace it from source code to transistor activity.

**Do not attempt this as reading.** Do it as a written exercise, closed-book, after Parts XIV–XVII. Write out every layer, and for each one state *what represents the data* and *what performs the operation*.

You should be able to get from C to electrons without a gap. **If you find one, that gap is your next study topic** — which is the most useful thing this course can give you.

The capstone builds the machine end of this. [[how-computers-work/08-capstone/07-final-integration|Module 34]] is the trace itself.

---

## 11. Suggested route

**If you want the shortest path to the capstone** (you can start building after this):

1. [[computer-architecture/05-the-datapath|the datapath]]
2. [[computer-architecture/03-instruction-sets|instruction sets]]
3. [[computer-architecture/04-assembly|assembly]]
4. → start [[how-computers-work/08-capstone/01-design-the-cpu|the capstone]]

That is four notes. **Everything else can follow while you build**, and building will make it stick better anyway.

**If you want the full stack in order:** Parts VIII → IX → X → XI → XII → XIII → XIV → XV → XVI → XVII, then the capstone, then the trace. Expect months, not weeks.

**A middle route, and the one I would suggest:** do the four notes above, build the capstone, then read Parts X–XVII with a working CPU of your own to compare against. **Having built one makes reading about better ones far more productive** — you have somewhere to put the information.

---

## Before moving on

- [ ] Name what each of Parts VIII–XVIII covers and which course teaches it.
- [ ] Explain what a control unit does and why it is the new idea in Part VIII.
- [ ] Explain why the ISA is the meeting point of the course's two directions.
- [ ] Name three places your Parts II–VII knowledge changes how you read the upper stack.
- [ ] State the one genuine gap in this vault's coverage (linkers and executable formats).

**Recap:** Parts II–VII built every physical component of a computer from electric charge upward. Parts VIII–XVIII are taught by four existing courses in this vault — `computer-architecture/`, `os/`, `compilers/` and `programming-language-theory/` — and this module is the route through them, naming at each step which piece of the physics half makes the next layer comprehensible. The one real gap is linkers and executable formats, covered only in passing.

**Next:** [[how-computers-work/08-capstone/01-design-the-cpu|Module 28 — Design the PRIME-1 CPU]] begins the capstone. You have the components and the map; now build the machine.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[computer-architecture/index|computer-architecture/]]
- [[os/index|os/]]
- [[compilers/index|compilers/]]
- [[programming-language-theory/index|programming-language-theory/]]
- [[build-your-own-shit/17-your-own-cpu/index|Build Your Own CPU — the four build tracks]]
