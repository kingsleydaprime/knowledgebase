# Module 33: Build the Language (The Two Directions Meet)

**[Advanced]** — A compiler for a language you designed, emitting instructions for a CPU you designed. **This is the module the whole course exists for.**

## Before you start

- You have a working CPU, assembler and emulator — modules [[how-computers-work/08-capstone/03-build-the-hardware|30]]–[[how-computers-work/08-capstone/05-build-the-emulator|32]].
- You have read [[foundations/compilers/02-lexical-analysis|compilers/lexical analysis]] through [[foundations/compilers/08-code-generation|code generation]], or are prepared to learn them here.
- Ideally you have built [[build-your-own-shit/04-your-own-language|Your Own Language]], though this module is self-contained.

**After this lesson you will be able to:**

1. Build a lexer, a recursive-descent parser and a code generator.
2. Explain why an AST is the right intermediate structure.
3. Generate correct code for expressions, assignment, conditionals and loops.
4. Explain what your compiler does *not* do, and what a real one would.

**Study route:** section 4 (code generation) is where the ISA decisions from module 28 come back to help or hurt you.

---

## 1. Why this exists (real-world motivation)

[[how-computers-work/index|The course index]] promised two directions: bottom-up from physics, and top-down from source code, meeting at the processor.

**You have climbed all the way up.** Electrons → doped silicon → transistors → gates → adders → ALU → registers → datapath → ISA → machine code.

**This module is the descent.** A language, a compiler, and the moment where compiler output becomes the opcodes your control unit decodes — which become control signals, which steer multiplexers built from transistors, which are doped silicon responding to fields.

**After this, `let z = x + y;` has no magic left in it anywhere.**

---

## 2. The language: Pebble

Deliberately tiny — one page of grammar, enough to write real programs:

```
let sum = 0;
let i = 10;
while (i) {
    sum = sum + i;
    i = i - 1;
}
print(sum);
```

**It has:** integer variables, arithmetic (`+`, `-`), comparison (`<`, `>`, `==`), `if`, `while`, and `print`.

**It does not have:** functions, arrays, strings, types, or scope. Each of those is a genuine extension and the practice task takes some on.

**The grammar, lowest precedence first:**

```
program    := statement*
statement  := 'let' ID '=' expr ';'
            | ID '=' expr ';'
            | 'print' '(' expr ')' ';'
            | 'while' '(' expr ')' block
            | 'if' '(' expr ')' block
expr       := comparison
comparison := sum (('<' | '>' | '==') sum)?
sum        := term (('+' | '-') term)*
term       := NUMBER | ID | '(' expr ')'
```

> [!NOTE]
> **Precedence is encoded in the grammar's shape, not in a table.** `sum` calls `term`, and `comparison` calls `sum` — so `term` binds tightest and `comparison` loosest.
>
> That is why `a + b < c` parses as `(a + b) < c`: by the time `comparison` looks for its operator, `sum` has already consumed the `+`. **A recursive-descent parser gets precedence for free from how the functions call each other**, which is the main reason it is the parser to write by hand.

---

## 3. The three stages

### Lexer — characters to tokens

`let sum = 0;` becomes `[LET, ID(sum), OP(=), NUMBER(0), PUNCT(;)]`.

**A regular expression per token type, matched in priority order.** The only subtlety is keywords: `let` matches the identifier pattern, so the lexer scans identifiers first and *then* reclassifies any that are keywords. Otherwise you need a separate pattern per keyword and they must precede the identifier rule.

### Parser — tokens to an AST

Recursive descent: one function per grammar rule, calling each other as the grammar nests.

```
    while (i) { sum = sum + i; }

    ("while", ("var", "i"),
              [("assign", "sum", ("binop", "+", ("var","sum"), ("var","i")))])
```

**Why a tree and not direct code emission?** Because a tree can be *traversed in any order*, examined, and rewritten. Emitting code straight from the parser works for the simplest languages and blocks every optimisation — you cannot constant-fold `2 + 3` if you have already emitted two `LDI`s and an `ADD`. **The AST is what makes a compiler more than a translator.**

### Code generator — AST to PRIME-1 assembly

Walk the tree, emitting instructions. **Two conventions carry the whole design:**

1. **Variables live in memory**, one word each, at slots 0, 1, 2… Access is `LD Rn, R0, slot` — base + displacement, with R0 as the zero base ([[how-computers-work/08-capstone/02-the-isa|module 29]]'s addressing mode earning its keep).
2. **Expressions evaluate into a register stack.** `gen(node, depth)` leaves its result in `R{depth}`. A binary operation evaluates its left operand into `R{depth}`, its right into `R{depth+1}`, then combines them.

**That second rule is a real register allocator**, just a crude one. It is why deeply nested expressions eventually run out of registers — and why real compilers spend so much effort on allocation.

---

## 4. Code generation, in detail

### Expressions

```
    sum + i
        ->  LD R1, R0, 0        ; sum, into R1
            LD R2, R0, 1        ; i, into R2
            ADD R1, R1, R2      ; combine into R1
```

### Loops — and why the branch pattern is inverted

The obvious translation of `while (cond) body` is:

```
    top:  <eval cond>
          BEZ R1, end        ; if false, exit
          <body>
          JMP top
    end:
```

**This breaks for long loop bodies.** `BEZ`'s offset is 6-bit signed — only −32 to +31 ([[how-computers-work/08-capstone/01-design-the-cpu|module 28]]'s budget) — so a body over about 30 instructions puts `end` out of reach and the assembler rejects it.

**The fix is to branch over an unconditional jump:**

```
    top:   <eval cond>
           BNZ R1, body      ; offset +1, ALWAYS in range
           JMP end           ; 12-bit absolute address, no range limit
    body:  <body>
           JMP top
    end:
```

**The conditional branch now always jumps exactly one instruction**, so its range never matters; the unconditional `JMP` carries the distance. Pebble's code generator emits this pattern for both `if` and `while`.

> [!NOTE]
> **This is a compiler working around an ISA limitation, and it is worth recognising as such.**
>
> Real compilers do exactly this. ARM and RISC-V both have short conditional branches and longer unconditional jumps, and compilers emit **branch islands** or invert conditions when a target is out of range.
>
> **It is also feedback on your ISA design.** If your compiler needs a workaround for every loop, the immediate field is too small — which is precisely the kind of evidence module 28 said should drive the decision. A wider branch offset, or a "compare and branch" instruction, would remove it.

### Output

PRIME-1 has no I/O instruction. **`print` writes to memory address 31, and the emulator watches that address** — memory-mapped I/O, exactly as described in [[foundations/os/09-syscalls-interrupts-and-the-abi|os/syscalls and interrupts]], and how real hardware exposes peripherals.

Address 31 is used because `ST` takes a 6-bit signed displacement, so 31 is the highest directly reachable slot. **The ISA's encoding budget decided where the output port lives.**

---

## 5. The complete pipeline

```
   Pebble source
        ↓  lexer
   tokens
        ↓  parser
   AST
        ↓  code generator
   PRIME-1 assembly
        ↓  assembler (module 31)
   machine code
        ↓  PRIME-1 (module 30 / the build tracks)
   55
```

**Every arrow is code you wrote.** The lab runs the whole chain and prints each intermediate form.

---

## 6. Predict before reading on

Pebble compiles `sum = sum + i;` into a load, a load, an add, and a store — **four instructions to add two numbers.**

**A real compiler would emit one. What is Pebble missing?**

<details><summary>Check your answer</summary>

**Register allocation across statements.** Pebble treats memory as the home of every variable and registers as scratch, so it reloads `sum` and `i` from memory every time they are used, and stores the result back immediately.

**A real compiler keeps hot variables in registers** for as long as it can, spilling to memory only when it runs out. In this loop, `sum` and `i` would live in R1 and R2 for the entire loop, and the body would be one `ADD` and one `SUB` — **four instructions per iteration instead of ten**.

**Doing this well requires:**

1. **Liveness analysis** — for each point, which variables will be read later?
2. **An interference graph** — which variables are live simultaneously and so cannot share a register?
3. **Graph colouring** — assign registers so no two interfering variables collide, spilling when there are not enough colours.

**This is the single biggest performance gap** between a teaching compiler and a real one, and it is why [[foundations/compilers/07-optimisation|compilers/optimisation]] spends so long on it. It is also the concrete reason module 28's register-count decision mattered: more registers means less spilling.
</details>

---

## 7. Worked example — runnable

Save as `pebble.py` next to `prime1.py`, and run `python3 pebble.py`.

```python
"""Pebble -- a tiny language that compiles to PRIME-1 assembly.

    let sum = 0;
    let i = 10;
    while (i) { sum = sum + i; i = i - 1; }
    print(sum);

Lexer -> parser -> AST -> code generator -> PRIME-1 assembly.
No optimisation, no type checking: the point is the full path from text
you wrote to instructions your own CPU executes."""
import re
from prime1 import assemble, Prime1

OUT_PORT = 31          # writing memory[31] prints. Variables use slots 0..30.

# --------------------------------------------------------------- 1. LEXER
TOKEN_SPEC = [
    ("NUMBER",   r"\d+"),
    ("ID",       r"[A-Za-z_]\w*"),
    ("OP",       r"==|<=|>=|[+\-*<>=]"),
    ("PUNCT",    r"[(){};]"),
    ("SKIP",     r"[ \t\n]+"),
]
KEYWORDS = {"let", "print", "while", "if"}

def lex(source):
    """Characters -> tokens. Each token is (kind, text, position)."""
    regex = "|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC)
    tokens, pos = [], 0
    for m in re.finditer(regex, source):
        if m.lastgroup == "SKIP":
            continue
        kind, text = m.lastgroup, m.group()
        if kind == "ID" and text in KEYWORDS:
            kind = text.upper()
        tokens.append((kind, text, m.start()))
    tokens.append(("EOF", "", len(source)))
    return tokens

# -------------------------------------------------------------- 2. PARSER
# Grammar, lowest precedence first:
#   program    := statement*
#   statement  := 'let' ID '=' expr ';' | ID '=' expr ';'
#               | 'print' '(' expr ')' ';'
#               | 'while' '(' expr ')' block | 'if' '(' expr ')' block
#   expr       := comparison
#   comparison := sum (('<' | '>' | '==') sum)?
#   sum        := term (('+' | '-') term)*
#   term       := NUMBER | ID | '(' expr ')'

class Parser:
    def __init__(self, tokens):
        self.tokens, self.i = tokens, 0

    def peek(self):  return self.tokens[self.i]
    def kind(self):  return self.tokens[self.i][0]
    def text(self):  return self.tokens[self.i][1]

    def eat(self, kind=None, text=None):
        k, t, pos = self.tokens[self.i]
        if kind and k != kind:
            raise SyntaxError(f"expected {kind}, got {k} '{t}' at {pos}")
        if text and t != text:
            raise SyntaxError(f"expected '{text}', got '{t}' at {pos}")
        self.i += 1
        return t

    def parse(self):
        body = []
        while self.kind() != "EOF":
            body.append(self.statement())
        return ("program", body)

    def block(self):
        self.eat("PUNCT", "{")
        body = []
        while self.text() != "}":
            body.append(self.statement())
        self.eat("PUNCT", "}")
        return body

    def statement(self):
        if self.kind() == "LET":
            self.eat("LET"); name = self.eat("ID"); self.eat("OP", "=")
            value = self.expr(); self.eat("PUNCT", ";")
            return ("let", name, value)
        if self.kind() == "PRINT":
            self.eat("PRINT"); self.eat("PUNCT", "(")
            value = self.expr()
            self.eat("PUNCT", ")"); self.eat("PUNCT", ";")
            return ("print", value)
        if self.kind() == "WHILE":
            self.eat("WHILE"); self.eat("PUNCT", "(")
            cond = self.expr(); self.eat("PUNCT", ")")
            return ("while", cond, self.block())
        if self.kind() == "IF":
            self.eat("IF"); self.eat("PUNCT", "(")
            cond = self.expr(); self.eat("PUNCT", ")")
            return ("if", cond, self.block())
        name = self.eat("ID"); self.eat("OP", "=")
        value = self.expr(); self.eat("PUNCT", ";")
        return ("assign", name, value)

    def expr(self):
        left = self.sum()
        if self.kind() == "OP" and self.text() in ("<", ">", "=="):
            op = self.eat("OP")
            return ("binop", op, left, self.sum())
        return left

    def sum(self):
        node = self.term()
        while self.kind() == "OP" and self.text() in ("+", "-"):
            op = self.eat("OP")
            node = ("binop", op, node, self.term())
        return node

    def term(self):
        if self.kind() == "NUMBER":
            return ("number", int(self.eat("NUMBER")))
        if self.kind() == "ID":
            return ("var", self.eat("ID"))
        self.eat("PUNCT", "(")
        node = self.expr()
        self.eat("PUNCT", ")")
        return node

# ------------------------------------------------------- 3. CODE GENERATOR
class CodeGen:
    """Emits PRIME-1 assembly. Variables live in memory slots 0..30.

    Expressions are evaluated into a small register stack R1..R5 --
    a crude register allocator, but a real one."""
    def __init__(self):
        self.asm, self.vars, self.label_n = [], {}, 0

    def emit(self, line):     self.asm.append("        " + line)
    def label(self, name):    self.asm.append(name + ":")
    def new_label(self, hint):
        self.label_n += 1
        return f"L{self.label_n}_{hint}"

    def slot(self, name):
        if name not in self.vars:
            if len(self.vars) >= OUT_PORT:
                raise MemoryError("too many variables for 6-bit displacement")
            self.vars[name] = len(self.vars)
        return self.vars[name]

    def gen(self, node, depth=1):
        """Evaluate `node`, leaving the result in register R{depth}."""
        kind = node[0]
        if kind == "number":
            self.emit(f"LDI R{depth}, {node[1]}")
        elif kind == "var":
            self.emit(f"LD R{depth}, R0, {self.slot(node[1])}")
        elif kind == "binop":
            _, op, left, right = node
            self.gen(left, depth)
            self.gen(right, depth + 1)          # right operand one register up
            if op == "+":   self.emit(f"ADD R{depth}, R{depth}, R{depth+1}")
            elif op == "-": self.emit(f"SUB R{depth}, R{depth}, R{depth+1}")
            elif op == "<": self.emit(f"SLT R{depth}, R{depth}, R{depth+1}")
            elif op == ">": self.emit(f"SLT R{depth}, R{depth+1}, R{depth}")
            elif op == "==":
                self.emit(f"SUB R{depth}, R{depth}, R{depth+1}")
                skip = self.new_label("eq")
                self.emit(f"BNZ R{depth}, {skip}_zero")
                self.emit(f"LDI R{depth}, 1")
                self.emit(f"JMP {skip}_done")
                self.label(f"{skip}_zero")
                self.emit(f"LDI R{depth}, 0")
                self.label(f"{skip}_done")
            else:
                raise SyntaxError(f"unknown operator {op}")
        else:
            raise SyntaxError(f"cannot evaluate {kind}")

    def statement(self, node):
        kind = node[0]
        if kind in ("let", "assign"):
            self.gen(node[2])
            self.emit(f"ST R1, R0, {self.slot(node[1])}")
        elif kind == "print":
            self.gen(node[1])
            self.emit(f"ST R1, R0, {OUT_PORT}       ; memory-mapped output")
        elif kind == "while":
            top, body, end = (self.new_label("while"),
                              self.new_label("body"), self.new_label("end"))
            self.label(top)
            self.gen(node[1])
            self.emit(f"BNZ R1, {body}")     # +1: always in branch range
            self.emit(f"JMP {end}")
            self.label(body)
            for s in node[2]:
                self.statement(s)
            self.emit(f"JMP {top}")
            self.label(end)
        elif kind == "if":
            body, end = self.new_label("body"), self.new_label("end")
            self.gen(node[1])
            self.emit(f"BNZ R1, {body}")
            self.emit(f"JMP {end}")
            self.label(body)
            for s in node[2]:
                self.statement(s)
            self.label(end)
        else:
            raise SyntaxError(f"unknown statement {kind}")

    def compile(self, ast):
        for s in ast[1]:
            self.statement(s)
        halt = self.new_label("halt")
        self.label(halt)
        self.emit(f"JMP {halt}")
        return "\n".join(self.asm)

def compile_pebble(source):
    return CodeGen().compile(Parser(lex(source)).parse())

def run(source, trace=False):
    """Full pipeline: source -> assembly -> machine code -> execution."""
    asm = compile_pebble(source)
    program, _ = assemble(asm)
    cpu = Prime1()
    cpu.load(program)
    printed, last = [], cpu.mem[OUT_PORT]
    while not cpu.halted and cpu.cycles < 100000:
        cpu.step()
        if cpu.mem[OUT_PORT] != last:            # memory-mapped output
            last = cpu.mem[OUT_PORT]
            printed.append(last)
    return asm, program, printed, cpu

PROGRAM = """
let sum = 0;
let i = 10;
while (i) {
    sum = sum + i;
    i = i - 1;
}
print(sum);
"""

if __name__ == "__main__":
    print("SOURCE (Pebble):")
    for line in PROGRAM.strip().splitlines():
        print("    " + line)
    print()

    tokens = lex(PROGRAM)
    print(f"1. LEXER -> {len(tokens)} tokens")
    print("   " + " ".join(f"{t[1]}" for t in tokens[:14]) + " ...")
    print()

    ast = Parser(tokens).parse()
    print(f"2. PARSER -> AST with {len(ast[1])} top-level statements")
    for s in ast[1]:
        print(f"   {s[0]:6s} {str(s[1])[:52]}")
    print()

    asm = compile_pebble(PROGRAM)
    print("3. CODE GENERATOR -> PRIME-1 assembly")
    for line in asm.splitlines():
        print("   " + line)
    print()

    asm, program, printed, cpu = run(PROGRAM)
    print(f"4. ASSEMBLER -> {len(program)} machine words")
    print("   " + " ".join(f"{w:04x}" for w in program[:12]) + " ...")
    print()

    print(f"5. EXECUTION on PRIME-1")
    print(f"   halted after {cpu.cycles} cycles")
    print(f"   printed: {printed}")
    print()
    print(f"   sum of 1..10 = {printed[-1]}   (expected 55)")

    assert printed[-1] == 55, f"expected 55, got {printed}"

    # a second program exercising if, comparison and nesting
    prog2 = """
    let a = 7;
    let b = 12;
    let big = 0;
    if (a < b) { big = b; }
    if (b < a) { big = a; }
    print(big);
    """
    _, _, out2, _ = run(prog2)
    print(f"   max(7, 12) = {out2[-1]}   (expected 12)")
    assert out2[-1] == 12

    prog3 = """
    let n = 6;
    let acc = 0;
    let k = 0;
    while (k < n) { k = k + 1; acc = acc + k; }
    print(acc);
    """
    _, _, out3, _ = run(prog3)
    print(f"   sum of 1..6 = {out3[-1]}   (expected 21)")
    assert out3[-1] == 21

    print()
    print("pebble: passed")
```

Expected output:

```
SOURCE (Pebble):
    let sum = 0;
    let i = 10;
    while (i) {
        sum = sum + i;
        i = i - 1;
    }
    print(sum);

1. LEXER -> 34 tokens
   let sum = 0 ; let i = 10 ; while ( i ) ...

2. PARSER -> AST with 4 top-level statements
   let    sum
   let    i
   while  ('var', 'i')
   print  ('var', 'sum')

3. CODE GENERATOR -> PRIME-1 assembly
           LDI R1, 0
           ST R1, R0, 0
           LDI R1, 10
           ST R1, R0, 1
   L1_while:
           LD R1, R0, 1
           BNZ R1, L2_body
           JMP L3_end
   L2_body:
           LD R1, R0, 0
           LD R2, R0, 1
           ADD R1, R1, R2
           ST R1, R0, 0
           LD R1, R0, 1
           LDI R2, 1
           SUB R1, R1, R2
           ST R1, R0, 1
           JMP L1_while
   L3_end:
           LD R1, R0, 0
           ST R1, R0, 31       ; memory-mapped output
   L4_halt:
           JMP L4_halt

4. ASSEMBLER -> 19 machine words
   9200 b200 920a b201 a201 d041 e010 a200 a401 1250 b200 a201 ...

5. EXECUTION on PRIME-1
   halted after 120 cycles
   printed: [55]

   sum of 1..10 = 55   (expected 55)
   max(7, 12) = 12   (expected 12)
   sum of 1..6 = 21   (expected 21)

pebble: passed
```

---

## 8. Common pitfalls and traps

1. **Emitting code directly from the parser.** It works and forecloses every optimisation. Build the AST.
2. **Getting precedence wrong.** It comes from the grammar's nesting, not a table. If `a + b * c` is wrong, your rule-call order is wrong.
3. **Forgetting keywords match the identifier pattern.** Lex identifiers, then reclassify keywords.
4. **Naive branch generation.** A conditional branch to a distant label overflows a 6-bit offset. Branch over a jump.
5. **Reusing a register across a subexpression.** `gen(left, depth)` then `gen(right, depth)` clobbers the left result. The depth must increase.
6. **Assuming unlimited variables.** A 6-bit displacement reaches 31 slots. Beyond that you need a base register.

---

## 9. Check your understanding

1. **Why does `gen()` take a `depth` parameter?**
   <details><summary>Answer</summary>
   Because a binary operation needs both operands live at once. If both were generated into the same register, the second would overwrite the first.<br>
   Passing <code>depth</code> and using <code>R{depth}</code> for the left operand and <code>R{depth+1}</code> for the right guarantees they occupy different registers, and the recursion naturally nests deeper for nested expressions. <strong>This is a register allocator</strong> — a stack discipline rather than a graph colouring, which is why it is simple and why it runs out of registers on deeply nested expressions.
   </details>

2. **What limits how deeply an expression can nest?**
   <details><summary>Answer</summary>
   The register count. Pebble uses R1 upward, so an expression nesting more than about six levels deep on its right spine exhausts the registers and generates references to R8, which does not exist.<br>
   <strong>A real compiler spills to memory</strong> when it runs out — pushing an intermediate result onto a stack and reloading it later. Adding spilling to Pebble is the natural next step, and it is what makes arbitrarily complex expressions work.
   </details>

3. **Why does `print` write to memory rather than using an instruction?**
   <details><summary>Answer</summary>
   Because PRIME-1 has no I/O instruction — all 16 opcodes are spent ([[how-computers-work/08-capstone/02-the-isa|module 29]]).<br>
   <strong>Memory-mapped I/O</strong> solves this without an instruction: designate an address that is not real memory, and have hardware watch for writes to it. Real systems do exactly this for most peripherals — a UART's transmit register, a framebuffer, GPIO pins are all just addresses. It is why <code>mmap</code>ing <code>/dev/mem</code> lets you drive hardware from userspace, and why device drivers are largely structured reads and writes to specific addresses.
   </details>

4. **The compiler emits a branch-over-jump for every loop. Is that the compiler's fault or the ISA's?**
   <details><summary>Answer</summary>
   <strong>The ISA's</strong>, and the compiler is doing the right thing given it.<br>
   A 6-bit branch offset was chosen in module 28 because 8 registers left only 6 bits for immediates. That decision, made to keep the register file usable, now costs one extra instruction per loop and per conditional.<br>
   <strong>This is what "the decisions are coupled" meant in practice.</strong> The right response is not to blame either component but to notice you now have evidence: if loops dominate your workload, a wider branch offset or a dedicated compare-and-branch instruction would pay for itself. That is how real ISAs evolve — compiler writers report what they keep working around.
   </details>

---

## 10. Practice — independent task

**Task:** Extend Pebble toward a language you would actually use.

- **(a)** Add `*` (multiplication). PRIME-1 has no `MUL`, so emit a shift-and-add loop ([[how-computers-work/05-combinational/03-multipliers-and-comparators|module 22]]). Verify `let x = 6 * 7; print(x);` prints 42.
- **(b)** Add `else`. Which labels do you need, and where does control converge?
- **(c)** Add `!=`, `<=` and `>=`. Each is a small rearrangement of `SLT` and the equality pattern — do not add ISA instructions.
- **(d)** Add constant folding: when both operands of a `binop` are `number` nodes, evaluate at compile time and emit one `LDI`. Confirm `let x = 2 + 3;` emits a single instruction.
- **(e)** Add spilling: when `depth` exceeds 5, store the intermediate to a scratch memory slot and reload it. Test with a deeply nested expression.
- **(f)** Add functions with no arguments — `fn name() { ... }` and `name();` — using `JAL` and the `JR` you added in module 29. Handle nesting with a stack.
- **(g)** Report errors with line numbers. Currently a syntax error gives a character offset; make it say `line 4: expected ';'`.

**Done when:** multiplication, `else` and constant folding all work, and you can compile and run a program using functions.

<details><summary>Hint for (a), only if stuck</summary>
Shift-and-add, exactly as in module 22: initialise a result to 0, then for each bit of the multiplier, if that bit is set add the (shifted) multiplicand.<br>
In Pebble's code generator, emit a small loop rather than trying to unroll it — you do not know the operand values at compile time. <strong>This is precisely why early CPUs without a multiplier were slow at it</strong>: a single-cycle `MUL` becomes a loop of ten-plus instructions, which is the concrete cost of the ISA decision not to include one.
</details>

---

## 11. Tradeoffs and limits

- **No type checking.** Everything is a 16-bit integer. A real compiler has a semantic analysis phase between parsing and codegen that catches type errors, undefined variables and scope violations ([[foundations/compilers/04-asts-and-semantic-analysis|compilers/ASTs and semantic analysis]]).
- **No intermediate representation.** Pebble goes straight from AST to assembly. Real compilers lower to an IR first, because optimisation is far easier on a flat, uniform representation than on a tree ([[foundations/compilers/06-intermediate-representations|compilers/IR]]).
- **No optimisation at all.** No constant folding, no dead code elimination, no common subexpression elimination. Every one is a genuine improvement and (d) is the easiest place to start.
- **No scope or functions.** Every variable is global. Adding scope means a symbol table with nesting; adding functions means a calling convention and a stack.

---

## Before moving on

- [ ] Build a lexer, and explain the keyword-versus-identifier ordering problem.
- [ ] Write a recursive-descent parser and explain where precedence comes from.
- [ ] Explain why an AST is worth building rather than emitting code directly.
- [ ] Generate correct code for expressions using a register stack.
- [ ] Explain the branch-over-jump pattern and which ISA decision forces it.

**Recap:** A compiler is three stages — a lexer turning characters into tokens, a recursive-descent parser building an AST whose shape encodes precedence, and a code generator walking that tree to emit instructions. Pebble stores variables in memory and evaluates expressions into a register stack, which is a real if crude register allocator. Loops branch over an unconditional jump because a 6-bit conditional offset cannot reach a distant label — a compiler working around an ISA decision made in module 28. `print` uses memory-mapped I/O because every opcode was spent.

**Next:** [[how-computers-work/08-capstone/07-final-integration|Module 34 — Final Integration]]. One line of Pebble, traced all the way down to transistors.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[build-your-own-shit/04-your-own-language|Your Own Language]] — the fuller treatment, with a bytecode VM and closures
- [[foundations/compilers/index|compilers/]] — lexing through code generation, properly
- [[how-computers-work/08-capstone/01-design-the-cpu|Module 28]] — the ISA decisions this compiler works around
