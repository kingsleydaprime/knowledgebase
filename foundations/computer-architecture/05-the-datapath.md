# The Datapath

**[Intermediate]** — How a CPU actually executes one instruction, from fetch to writeback.

## The five stages

**The classic RISC pipeline**, and it's the mental model everything else builds on:

```
 ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
 │  IF  │→│  ID  │→│  EX  │→│  MEM │→│  WB  │
 └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
  fetch    decode  execute  memory  writeback
```

**IF — Instruction Fetch.** Read the instruction at the PC from the instruction cache. Increment the PC.

**ID — Instruction Decode.** Work out what it is, and read the source registers.

**EX — Execute.** The ALU does the arithmetic — or computes a memory address, or evaluates a branch condition.

**MEM — Memory.** Load or store, for instructions that touch memory. **Most instructions do nothing here.**

**WB — Writeback.** Write the result into the destination register.

## The components

**Program counter** — the address of the next instruction.

**Instruction memory / I-cache** — where instructions come from.

**Register file** — the architectural registers. **Multi-ported**: typically two read ports and one write port, so it can supply both operands and accept a result in one cycle.

**ALU** — arithmetic and logic. Add, subtract, and, or, xor, shift, compare.

**Data memory / D-cache** — loads and stores.

**Control unit** — decodes the instruction into the control signals that steer everything else: which ALU operation, whether to write a register, whether to access memory, whether to branch.

**Muxes everywhere** — selecting between the register value and an immediate, between the ALU result and a loaded value, between PC+4 and a branch target.

```
        ┌────────────┐
  PC ──→│  I-CACHE   │──→ instruction
   ▲    └────────────┘         │
   │                           ▼
   │                    ┌────────────┐
   │                    │  DECODE +  │
   │                    │  REGISTERS │
   │                    └────────────┘
   │                       │      │
   │                       ▼      ▼
   │                    ┌────────────┐
   │                    │    ALU     │
   │                    └────────────┘
   │                           │
   │                           ▼
   │                    ┌────────────┐
   │                    │  D-CACHE   │
   │                    └────────────┘
   │                           │
   └───── branch target ◄──────┴──→ writeback to registers
```

## Single-cycle vs multi-cycle

**Single-cycle** — every instruction completes in one clock.

**Simple to understand, and a bad design.** The clock period must accommodate the **slowest** instruction — a load, which fetches, decodes, computes an address, reads memory, and writes back. **Every fast instruction is padded out to that duration**, so an `add` takes as long as a load.

**Multi-cycle** — break instructions into steps, each one clock. Different instructions take different numbers of cycles.

**Better utilisation** (a fast instruction finishes in fewer cycles) and **hardware reuse** — one ALU can serve address computation and arithmetic in different cycles. **But only one instruction is in flight at a time**, so most of the hardware sits idle each cycle.

**Pipelining** is the fix: keep every stage busy with a *different* instruction. That's the next note, and it's where real performance comes from. → [[foundations/computer-architecture/06-pipelining|Pipelining]]

## Instruction execution, traced

**`add x1, x2, x3`** (AArch64, `x1 = x2 + x3`):

| Stage | What happens |
|---|---|
| IF | fetch from I-cache at PC; PC += 4 |
| ID | decode as ADD; read x2 and x3 from the register file |
| EX | ALU computes x2 + x3 |
| MEM | **nothing** |
| WB | write the result to x1 |

**`ldr x1, [x2, #8]`** (load):

| Stage | What happens |
|---|---|
| IF | fetch |
| ID | decode; read x2 |
| EX | **ALU computes the address** x2 + 8 |
| MEM | **read the D-cache at that address** |
| WB | write the loaded value to x1 |

**Note the ALU is used for address arithmetic**, not just user-visible arithmetic. That's why the same hardware serves both, and why address computation is essentially free.

**`b.eq label`** (conditional branch):

| Stage | What happens |
|---|---|
| IF | fetch |
| ID | decode; read flags |
| EX | evaluate the condition; compute the target |
| MEM | nothing |
| WB | nothing — but **the PC is updated** |

> **The branch problem is visible right here.** The outcome isn't known until EX, but the *next* instruction had to be fetched in the meantime. **Something must be fetched, and it might be wrong.** That's what branch prediction exists to solve. → [[foundations/computer-architecture/07-branch-prediction-and-speculation|Branch Prediction]]

## Control signals

**The control unit turns an opcode into a set of switches.** For a simplified RISC:

| Signal | Effect |
|---|---|
| `RegWrite` | write the result to a register? |
| `ALUSrc` | second ALU operand: register or immediate? |
| `ALUOp` | which operation? |
| `MemRead` / `MemWrite` | access memory? |
| `MemToReg` | writeback source: ALU result or loaded value? |
| `Branch` | is this a branch? |

**Two ways to generate them:**

**Hardwired** — combinational logic straight from the opcode. **Fast, inflexible.** Standard for RISC, where instructions are regular.

**Microcoded** — each instruction indexes a small ROM of micro-instructions. **Slower, and enormously more flexible** — complex instructions become sequences of simple steps.

> **Microcode is why x86 survives.** Complex instructions are implemented as micro-op sequences rather than dedicated hardware, and **microcode is updatable** — which is how Spectre and Meltdown mitigations were shipped to existing CPUs as firmware updates rather than requiring new silicon. **A design decision from the 1960s that saved the industry in 2018.**

## Clocking

**A clock signal synchronises everything.** State elements (registers, latches) update on the clock edge; combinational logic settles in between.

$$\text{clock period} \geq \text{longest combinational path} + \text{setup time} + \text{clock skew}$$

**The longest path is the critical path**, and it determines your maximum frequency.

**So there's a fundamental trade in pipeline design:**

**More stages → shorter critical path → higher clock.** But also **more overhead per stage** (each pipeline register costs setup time), **worse branch misprediction penalty** (more work to discard), and **more power**.

> **The Pentium 4 is the cautionary tale.** Intel pushed to 31 pipeline stages chasing clock speed, reaching 3.8 GHz. **The misprediction penalty was catastrophic** and per-clock performance was poor, so it lost to chips running at 2 GHz. **The industry settled around 14–20 stages**, which is where the trade balances.

**Power** is the other constraint, and it's why clocks stopped rising:

$$P \approx C V^2 f + \text{leakage}$$

**Power scales with frequency and with the *square* of voltage.** Higher clocks need higher voltage to switch reliably, so **power grows super-linearly.** Around 2005 that hit the limit of what a chip could dissipate — the end of frequency scaling and the start of multicore. → [[foundations/computer-architecture/01-what-architecture-is|Where performance comes from]]

## What real CPUs do instead

**The five-stage pipeline is a teaching model.** A modern high-performance core:

- **Decodes 4–8 instructions per cycle**, into micro-ops
- **Caches the micro-ops** so hot loops skip decode entirely
- **Renames registers** onto hundreds of physical registers
- **Executes out of order** from a scheduler holding 200+ instructions
- **Runs 8–12 execution units** in parallel — several ALUs, multiple load/store units, vector units
- **Retires in order**, to preserve the illusion of sequential execution
- **Has 14–20 pipeline stages**, sometimes more

**But the five stages are still the right mental model** — fetch, decode, execute, memory, writeback happen to every instruction. **Everything else is about doing many of them at once.** → [[foundations/computer-architecture/10-out-of-order-and-superscalar|Out-of-Order Execution]]

**In-order cores are far from obsolete.** Efficiency cores (Intel E-cores, ARM's little cores), microcontrollers, and most embedded processors are in-order — **much smaller, much lower power, and adequate when the workload isn't latency-critical.** → [[hardware/04-microcontrollers|Microcontrollers]]

---

## Related
- [[foundations/computer-architecture/06-pipelining|Pipelining]] — overlapping these stages
- [[hardware/02-digital-and-analog|Digital and Analog]] — the gates underneath
- [[foundations/computer-architecture/03-instruction-sets|Instruction Sets]] — what's being executed
- [[foundations/computer-architecture/README|Architecture map]]
