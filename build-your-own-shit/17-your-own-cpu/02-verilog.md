# Track 2 — Verilog (Describe the Hardware)

**[Advanced]** — Two or three evenings. Produces **synthesisable HDL** that simulates on your laptop and runs on an FPGA if you have one. The track that teaches how hardware is actually built professionally.

> [!WARNING]
> **The Verilog on this page has not been simulated.** Unlike tracks 1 and 3, whose Python was executed and whose output is the real output, this environment had no `iverilog` or `verilator` available.
>
> The design **structurally mirrors `datapath.py` from [[build-your-own-shit/17-your-own-cpu/01-digital-simulator|track 1]]**, which *is* verified against the track-3 emulator — same control table, same signal names, same datapath order. But mirroring a verified model is not the same as running.
>
> **Treat it as a careful draft to verify, not a known-good answer.** Section 6 gives you the exact commands. If it fails, that is a genuine bug in this page and worth telling me about.

## Why this track

Tracks 1 and 3 build a CPU you can see and a CPU you can run. **Neither is how chips are actually made.**

Real hardware is *described* in a hardware description language and then synthesised — turned into gates automatically by a tool. Verilog is text, so it diffs, reviews and version-controls like code, and it scales to designs no human could draw.

**The mental shift is the lesson.** Verilog looks like a programming language and is not one. `always @(posedge clk)` does not "run"; it *describes a flip-flop*. Every line becomes hardware that exists permanently and operates in parallel. Getting that distinction into your hands is worth the two evenings.

## The one idea you must internalise first

```verilog
assign y = a + b;                  // a WIRE, driven continuously by an ADDER
                                   // this adder exists forever and always computes

always @(posedge clk)              // a FLIP-FLOP
    q <= d;                        // captures d at the clock edge
```

**`assign` and `always @(*)` create combinational logic** — gates, computing continuously. **`always @(posedge clk)` creates sequential logic** — flip-flops, from [[how-computers-work/06-memory/01-latches-and-flip-flops|module 23]].

**Two rules that prevent most beginner bugs:**

1. Use `<=` (non-blocking) inside `always @(posedge clk)`. Use `=` (blocking) inside `always @(*)`. Mixing them creates simulation/synthesis mismatches — code that works in the simulator and fails in silicon.
2. **Never assign the same signal from two `always` blocks.** In software that is a race; in hardware it is two drivers fighting over one wire, which is [[how-computers-work/01-electricity/03-circuit-laws|module 3]]'s short circuit.

## Milestones

Build in the master guide's order, but with a **testbench at every step** — that is the real Verilog workflow.

### 1 — ALU alone

Write `alu.v` and a testbench that drives all eight operations and checks results. **Do not proceed until it passes.**

Verilog's `$signed()` matters for `SLT`: `$signed(a) < $signed(b)` is signed comparison, `a < b` is unsigned. Both are correct; they answer different questions ([[how-computers-work/05-combinational/03-multipliers-and-comparators|module 21]]).

### 2 — Register file

Two async read ports, one sync write, R0 hardwired.

**The idiom for hardwiring R0** is to simply not store it:

```verilog
reg [15:0] r [1:7];                       // R0 has no storage at all
assign qa = (ra == 3'd0) ? 16'd0 : r[ra];
```

**Test:** write to R0, read it back, assert zero.

### 3 — Control unit

The table from track 1 as a `case` statement, with **defaults assigned first** so every signal has a known value on every path:

```verilog
always @(*) begin
    {reg_write, reg_b_src, alu_src} = 3'b000;   // defaults FIRST
    ...
    case (op)
        4'h1: begin reg_write=1; alu_op=3'd0; end
```

**Omitting the defaults infers a latch** — the synthesiser sees a signal that keeps its old value on some path and builds storage you did not ask for. This is the single most common Verilog mistake, and it produces designs that fail timing mysteriously.

### 4–7 — Datapath, memory, branches, jumps

Wire it exactly as track 1's block diagram. Because Verilog is text, this is mostly naming wires and connecting module ports.

### 8 — Full testbench

Load the reference program into `imem`, clock until `halted`, check `R1 == 55`.

## The implementation

Save as `prime1.v`:

```verilog
// PRIME-1 -- single-cycle 16-bit processor
// Structure mirrors datapath.py: control unit + datapath, no opcode
// decisions anywhere except the control ROM.

`default_nettype none

// ---------------------------------------------------------------- ALU
module alu (
    input  wire [15:0] a,
    input  wire [15:0] b,
    input  wire [2:0]  op,
    output reg  [15:0] y
);
    localparam ADD=3'd0, SUB=3'd1, AND=3'd2, OR=3'd3,
               XOR=3'd4, SHL=3'd5, SHR=3'd6, SLT=3'd7;
    always @(*) begin
        case (op)
            ADD: y = a + b;
            SUB: y = a - b;
            AND: y = a & b;
            OR : y = a | b;
            XOR: y = a ^ b;
            SHL: y = a << b[3:0];
            SHR: y = a >> b[3:0];
            SLT: y = ($signed(a) < $signed(b)) ? 16'd1 : 16'd0;
            default: y = 16'd0;
        endcase
    end
endmodule

// ------------------------------------------------------- REGISTER FILE
// Two asynchronous read ports, one synchronous write port.
// R0 is hardwired to zero: writes to it are discarded.
module regfile (
    input  wire        clk,
    input  wire [2:0]  ra, rb, rw,
    input  wire [15:0] wdata,
    input  wire        we,
    output wire [15:0] qa, qb
);
    reg [15:0] r [1:7];          // note: R0 is NOT stored
    integer i;
    initial for (i = 1; i < 8; i = i + 1) r[i] = 16'd0;

    assign qa = (ra == 3'd0) ? 16'd0 : r[ra];
    assign qb = (rb == 3'd0) ? 16'd0 : r[rb];

    always @(posedge clk)
        if (we && rw != 3'd0)
            r[rw] <= wdata;
endmodule

// -------------------------------------------------------- CONTROL UNIT
// The table from track 1, as combinational logic.
module control (
    input  wire [3:0] op,
    output reg        reg_write, reg_b_src, alu_src,
    output reg [2:0]  alu_op,
    output reg        mem_read, mem_write, mem_to_reg,
    output reg        branch, branch_not, jump, link
);
    always @(*) begin
        // defaults -- every signal off, ALU adding
        {reg_write, reg_b_src, alu_src} = 3'b000;
        alu_op = 3'd0;
        {mem_read, mem_write, mem_to_reg} = 3'b000;
        {branch, branch_not, jump, link}  = 4'b0000;
        case (op)
            4'h0: ;                                              // NOP
            4'h1: begin reg_write=1; alu_op=3'd0; end             // ADD
            4'h2: begin reg_write=1; alu_op=3'd1; end             // SUB
            4'h3: begin reg_write=1; alu_op=3'd2; end             // AND
            4'h4: begin reg_write=1; alu_op=3'd3; end             // OR
            4'h5: begin reg_write=1; alu_op=3'd4; end             // XOR
            4'h6: begin reg_write=1; alu_op=3'd5; end             // SHL
            4'h7: begin reg_write=1; alu_op=3'd6; end             // SHR
            4'h8: begin reg_write=1; alu_op=3'd7; end             // SLT
            4'h9: begin reg_write=1; alu_src=1; end               // LDI
            4'hA: begin reg_write=1; alu_src=1;
                        mem_read=1; mem_to_reg=1; end             // LD
            4'hB: begin reg_b_src=1; alu_src=1; mem_write=1; end  // ST
            4'hC: begin branch=1; end                             // BEZ
            4'hD: begin branch=1; branch_not=1; end               // BNZ
            4'hE: begin jump=1; end                               // JMP
            4'hF: begin reg_write=1; jump=1; link=1; end          // JAL
        endcase
    end
endmodule

// ------------------------------------------------------------- TOP
module prime1 (
    input  wire        clk,
    input  wire        rst,
    output wire [15:0] pc_out,
    output wire        halted
);
    reg  [15:0] pc;
    reg  [15:0] imem [0:4095];
    reg  [15:0] dmem [0:4095];

    wire [15:0] ir      = imem[pc[11:0]];
    wire [15:0] pc_next_seq = pc + 16'd1;

    // ---- decode
    wire [3:0] op   = ir[15:12];
    wire [2:0] rd   = ir[11:9];
    wire [2:0] ra   = ir[8:6];
    wire [2:0] rb   = ir[5:3];
    wire [15:0] imm = {{10{ir[5]}}, ir[5:0]};   // sign-extend from bit 5
    wire [11:0] addr = ir[11:0];

    wire reg_write, reg_b_src, alu_src, mem_read, mem_write,
         mem_to_reg, branch, branch_not, jump, link;
    wire [2:0] alu_op;
    control ctrl (.op(op), .reg_write(reg_write), .reg_b_src(reg_b_src),
                  .alu_src(alu_src), .alu_op(alu_op), .mem_read(mem_read),
                  .mem_write(mem_write), .mem_to_reg(mem_to_reg),
                  .branch(branch), .branch_not(branch_not),
                  .jump(jump), .link(link));

    // ---- register read (port B address is muxed: stores read rd)
    wire [2:0]  rb_addr = reg_b_src ? rd : rb;
    wire [15:0] qa, qb;
    wire [15:0] wb_data;
    wire [2:0]  wb_addr = link ? 3'd7 : rd;
    regfile rf (.clk(clk), .ra(ra), .rb(rb_addr), .rw(wb_addr),
                .wdata(wb_data), .we(reg_write), .qa(qa), .qb(qb));

    // ---- execute
    wire [15:0] operand_b = alu_src ? imm : qb;
    wire [15:0] alu_y;
    alu u_alu (.a(qa), .b(operand_b), .op(alu_op), .y(alu_y));

    // ---- memory
    wire [15:0] mem_q = dmem[alu_y[11:0]];
    always @(posedge clk)
        if (mem_write) dmem[alu_y[11:0]] <= qb;

    // ---- writeback
    assign wb_data = link ? pc_next_seq : (mem_to_reg ? mem_q : alu_y);

    // ---- next PC
    wire a_is_zero  = (qa == 16'd0);
    wire take_branch = branch & (a_is_zero ^ branch_not);
    assign halted   = jump & (addr == pc[11:0]);      // jump-to-self idiom

    always @(posedge clk) begin
        if (rst)             pc <= 16'd0;
        else if (jump)       pc <= {4'd0, addr};
        else if (take_branch) pc <= pc_next_seq + imm;
        else                 pc <= pc_next_seq;
    end

    assign pc_out = pc;
endmodule
```

And the testbench, `tb_prime1.v`:

```verilog
`timescale 1ns/1ps
`default_nettype none

module tb_prime1;
    reg clk = 0, rst = 1;
    wire [15:0] pc;
    wire halted;
    integer cycles = 0;

    prime1 dut (.clk(clk), .rst(rst), .pc_out(pc), .halted(halted));

    always #5 clk = ~clk;            // 100 MHz

    initial begin
        $dumpfile("prime1.vcd");
        $dumpvars(0, tb_prime1);

        // the reference program: sum 1..10, expect R1 = 55
        dut.imem[0] = 16'h9200;      // LDI R1, 0
        dut.imem[1] = 16'h940A;      // LDI R2, 10
        dut.imem[2] = 16'h1250;      // loop: ADD R1, R1, R2
        dut.imem[3] = 16'h9601;      // LDI R3, 1
        dut.imem[4] = 16'h2498;      // SUB R2, R2, R3
        dut.imem[5] = 16'hD0BC;      // BNZ R2, loop   (offset -4)
        dut.imem[6] = 16'hE006;      // halt: JMP halt

        @(negedge clk); rst = 0;

        while (!halted && cycles < 1000) begin
            @(negedge clk);
            cycles = cycles + 1;
        end

        $display("halted after %0d cycles", cycles);
        $display("R1 = %0d  (expected 55)", dut.rf.r[1]);
        if (dut.rf.r[1] === 16'd55)
            $display("PASS");
        else
            $display("FAIL: R1 = %0d", dut.rf.r[1]);
        $finish;
    end
endmodule
```

## 6. Running it — the commands to verify this page

**Install the toolchain** (all free and open source):

```bash
# Fedora
sudo dnf install iverilog gtkwave

# Debian / Ubuntu
sudo apt install iverilog gtkwave

# macOS
brew install icarus-verilog gtkwave
```

**Compile and run:**

```bash
iverilog -g2005 -o prime1_sim prime1.v tb_prime1.v
vvp prime1_sim
```

**Expected output:**

```
halted after 43 cycles
R1 = 55  (expected 55)
PASS
```

**43 cycles is the number to check.** It is what both `prime1.py` and `datapath.py` produce, so a match means all three implementations agree — the differential test the master guide asks for.

**Then look at the waveforms**, which is the thing this track offers that no other does:

```bash
gtkwave prime1.vcd
```

Add `pc`, `ir`, `qa`, `qb`, `alu_y` and the control signals to the view. **You can now watch the branch fire**: see `qa` go to zero, `take_branch` drop, and the PC stop looping. That picture is worth the setup.

### If it fails

The most likely culprits, in order:

1. **Inferred latch in `control`** — check every signal has a default before the `case`.
2. **`imem` initialisation in the testbench** — hierarchical access (`dut.imem[0]`) works in Icarus but some tools require `$readmemh` from a file instead.
3. **Reset timing** — the testbench releases `rst` on a `negedge`; if your PC starts at 1 instead of 0, that is why.
4. **Blocking vs non-blocking** — `<=` in clocked blocks, `=` in combinational ones.

**Tell me if it fails.** This page's code is unverified, and a failure is a bug in the page rather than in your setup.

## The parts that will bite you

- **Inferred latches.** Assign defaults first, always.
- **`reg` does not mean register.** It means "assigned inside a procedural block". A `reg` assigned in `always @(*)` is combinational logic. This naming is a historical wart; SystemVerilog's `logic` fixes it.
- **Array indexing width.** `imem[pc]` with a 16-bit `pc` and a 4096-entry array needs `imem[pc[11:0]]`, or the tool warns and truncates unpredictably.
- **Simulation/synthesis mismatch.** Code that simulates but does not synthesise (or worse, synthesises differently) usually traces to blocking assignments in clocked blocks or incomplete sensitivity lists.
- **`$signed` is not sticky.** It applies to the expression it wraps, not the whole statement.

## Where to stop

**Stop when the testbench prints PASS at 43 cycles**, and you have looked at the waveform once.

**Worth continuing to** if you have an FPGA (an iCE40 or ECP5 board is cheap, and works with the fully open-source yosys/nextpnr flow): synthesise it, add a memory-mapped output port, and drive some LEDs from a program you wrote. **Your own processor, running your own program, on real silicon.**

**Not worth it here:** pipelining, caches, or a bus interface. Those turn a weekend project into a term project.

## Related

- [[build-your-own-shit/17-your-own-cpu/index|PRIME-1 index and ISA spec]]
- [[build-your-own-shit/17-your-own-cpu/01-digital-simulator|Track 1]] — the verified `datapath.py` this mirrors
- [[build-your-own-shit/17-your-own-cpu/03-python-emulator|Track 3]] — the oracle to diff against
- [[build-your-own-shit/17-your-own-cpu/04-breadboard|Track 4 — Breadboard]]
- [[how-computers-work/06-memory/01-latches-and-flip-flops|module 23]] — what `always @(posedge clk)` actually builds
