# Bytecode and Virtual Machines

**[Intermediate → Advanced]** — The realistic target for a language you build yourself: 10× faster than a tree-walker, a fraction of the work of native code generation.

## Why bytecode

A tree-walking interpreter is **10–100× slower than native**, and the reasons are structural:

- **Pointer chasing.** Every node visit is a cache miss waiting to happen
- **A virtual call per node** — dynamic dispatch on every operation
- **Nothing is precomputed.** Variable lookup, operator resolution, and scope walking happen every time

Bytecode fixes all three: a **flat array of instructions** (cache-friendly, sequential), a **switch or computed goto** instead of virtual dispatch, and **everything resolvable at compile time already resolved** — variables become slot indices, not hash lookups.

Typical result: **3–10× slower than native** instead of 10–100×. That's the difference between "a toy" and "usable".

## Stack vs register

The first design decision.

**Stack machine** — operands are implicit, on a stack:

```
// a + b * c
GET_LOCAL 0      // push a
GET_LOCAL 1      // push b
GET_LOCAL 2      // push c
MULTIPLY         // pop 2, push 1
ADD              // pop 2, push 1
```

**Register machine** — operands are explicit indices into a frame:

```
MUL  r3, r1, r2      // r3 = b * c
ADD  r4, r0, r3      // r4 = a + r3
```

| | Stack | Register |
|---|---|---|
| Instruction size | tiny (often 1 byte) | larger (opcode + operands) |
| Instruction count | **more** | **fewer** (~half) |
| Compiler complexity | trivial — a post-order walk | needs register allocation |
| Dispatch overhead | more instructions = more dispatches | fewer |
| Used by | **JVM, CPython, .NET, WASM** | **Lua, Dalvik, LuaJIT, BEAM** |

**Register VMs are meaningfully faster** — roughly 20–40% in published comparisons — because dispatch dominates and they execute fewer instructions. The Lua 5.0 paper is the canonical write-up.

**Stack VMs are much easier to generate code for.** Compiling an expression tree is a post-order traversal with no allocation decisions:

```rust
fn compile_expr(&mut self, e: &Expr) {
    match e {
        Expr::Binary { op, left, right, .. } => {
            self.compile_expr(left);           // leaves its result on the stack
            self.compile_expr(right);
            self.emit(op_to_instruction(op));  // consumes both, pushes one
        }
        Expr::Literal { value, .. } => {
            let idx = self.add_constant(value.clone());
            self.emit(OpCode::Constant(idx));
        }
    }
}
```

That's the whole compiler for expressions. **Start with a stack machine.**

## The instruction set

```rust
enum OpCode {
    // constants and literals
    Constant(u16), Nil, True, False,

    // stack
    Pop, Dup,

    // variables — INDICES, resolved at compile time
    GetLocal(u8), SetLocal(u8),
    GetGlobal(u16), SetGlobal(u16),
    GetUpvalue(u8), SetUpvalue(u8),

    // arithmetic and comparison
    Add, Sub, Mul, Div, Negate,
    Equal, Greater, Less, Not,

    // control flow — RELATIVE offsets
    Jump(i16), JumpIfFalse(i16), Loop(u16),

    // functions
    Call(u8), Return, Closure(u16), CloseUpvalue,
}
```

**`GetLocal(u8)` is where the speed comes from.** The variable name was resolved to a stack slot at compile time, so runtime access is `stack[frame_base + slot]` — an array index, not a hash lookup. → [[foundations/compilers/04-asts-and-semantic-analysis|Semantic Analysis]]

**Jumps are relative**, so code is position-independent and can be moved or spliced.

Real designs to look at: **JVM** (~200 opcodes, typed — `iadd`, `fadd`, `aload`), **CPython** (~120, and it changes every version), **WebAssembly** (stack-based, statically validated, structured control flow — no arbitrary jumps).

## Patching jumps

You emit a jump before knowing its target. The standard fix:

```rust
fn emit_jump(&mut self, op: fn(i16) -> OpCode) -> usize {
    self.emit(op(0xFFFF));           // placeholder
    self.code.len() - 1              // remember where to patch
}

fn patch_jump(&mut self, offset: usize) {
    let jump = self.code.len() - offset - 1;
    self.code[offset] = OpCode::JumpIfFalse(jump as i16);
}

// compiling `if`
self.compile_expr(cond);
let then_jump = self.emit_jump(OpCode::JumpIfFalse);
self.emit(OpCode::Pop);
self.compile_stmt(then_branch);
let else_jump = self.emit_jump(OpCode::Jump);
self.patch_jump(then_jump);          // now we know where `else` starts
self.emit(OpCode::Pop);
if let Some(e) = else_branch { self.compile_stmt(e); }
self.patch_jump(else_jump);
```

Backpatching is the same technique assemblers use for forward references.

## The interpreter loop

```rust
fn run(&mut self) -> Result<Value, RuntimeError> {
    loop {
        let instruction = self.chunk.code[self.ip];
        self.ip += 1;

        match instruction {
            OpCode::Constant(idx) => self.push(self.chunk.constants[idx as usize].clone()),
            OpCode::Add => {
                let b = self.pop();
                let a = self.pop();
                self.push(self.add_values(a, b)?);
            }
            OpCode::GetLocal(slot) => {
                let v = self.stack[self.frame_base + slot as usize].clone();
                self.push(v);
            }
            OpCode::JumpIfFalse(offset) => {
                if self.peek(0).is_falsey() { self.ip += offset as usize; }
            }
            OpCode::Return => return Ok(self.pop()),
        }
    }
}
```

**This loop is 80% of your runtime**, so its details matter more than anything else.

### Dispatch

The `match` compiles to a jump table — one indirect branch per instruction, and modern CPUs mispredict it constantly because the target varies.

**Computed goto** (a GCC/Clang extension) gives each opcode its own dispatch:

```c
static void *dispatch[] = { &&op_constant, &&op_add, &&op_return };
#define NEXT() goto *dispatch[code[ip++]]

op_add:
    b = pop(); a = pop(); push(a + b);
    NEXT();                              // its OWN indirect branch
```

Because each opcode ends with a distinct branch site, the CPU can learn the common *sequences* — `GET_LOCAL` is often followed by `GET_LOCAL`, then `ADD`. Reported speedups are **15–30%**, and it's why CPython uses this on GCC.

Beyond that: **direct threading** (store label addresses instead of opcodes, skipping the table lookup) and **superinstructions** (fuse common pairs — `GET_LOCAL`+`GET_LOCAL`+`ADD` becomes one opcode), which cut dispatch count directly.

## Value representation

How do you store an integer, a float, a string and an object in one slot?

**Tagged union** — the obvious approach:

```rust
enum Value { Nil, Bool(bool), Number(f64), Obj(*mut Obj) }
```

16 bytes in Rust or C (8 for the payload, plus a tag padded to alignment). Simple and correct.

**NaN boxing** — the trick real VMs use. IEEE 754 doubles have ~2^51 unused NaN bit patterns, so you store *everything* in 8 bytes:

```
double:     any bit pattern that isn't a quiet NaN
nil/true/false: specific NaN patterns
pointer:    a NaN pattern with the 48-bit address in the mantissa
```

Halves memory use and doubles cache density. Used by LuaJIT, JavaScriptCore, SpiderMonkey, and Crafting Interpreters' `clox`. Fiddly, and a large win for a numeric workload.

**Pointer tagging** — use the low bits of an aligned pointer (always zero) as a tag. V8 uses this for small integers ("Smis"), which is why integer arithmetic in JavaScript is fast despite the language having only doubles.

## Call frames

```rust
struct CallFrame {
    function: Rc<Function>,
    ip: usize,              // saved instruction pointer
    slot_base: usize,       // where this frame's locals start in the shared stack
}

struct Vm {
    stack: Vec<Value>,          // ONE stack, shared by all frames
    frames: Vec<CallFrame>,
}
```

**One value stack, with frames indexing into it.** A call pushes a frame recording where its slots begin; a return pops the frame and truncates the stack. Arguments are already in place — the caller pushed them, and they become the callee's first locals.

**Guard the frame depth**, or deep recursion overflows your host stack (or your `Vec`) and crashes the process rather than raising a language-level error:

```rust
if self.frames.len() >= MAX_FRAMES { return Err(RuntimeError::StackOverflow); }
```

## Closures

The interesting case, and where a naive design breaks:

```rust
struct Closure { function: Rc<Function>, upvalues: Vec<Rc<RefCell<Upvalue>>> }

enum Upvalue {
    Open(usize),          // still on the stack — an index
    Closed(Value),        // the stack frame is gone — the value moved in here
}
```

While the enclosing function is alive, an upvalue **points at the stack slot**, so reads and writes are shared correctly. When that function returns, the upvalue is **closed** — the value is copied into the upvalue object, which the closure now owns.

That two-state design is Lua's, and it's why the common case (an uncaptured local) stays a plain stack slot with no indirection. → [[foundations/compilers/04-asts-and-semantic-analysis|closures and upvalues]]

## Making it faster

In rough order of payoff:

1. **Computed goto** — 15–30%, one afternoon
2. **Superinstructions** for common sequences
3. **Inline caching** — cache the result of a property or method lookup at each call site. This is the single biggest win for dynamic languages, and the foundation of every fast JavaScript engine
4. **NaN boxing** — halves memory traffic
5. **Constant folding at compile time** — free, do it in the compiler
6. **Avoid allocating per operation.** Interning strings and reusing buffers matters enormously
7. **Then, a JIT** → [[foundations/compilers/11-jit-compilation|JIT compilation]]

**Inline caching deserves emphasis.** In a dynamic language `obj.field` requires a hash lookup every time. Caching "last time at this site, the object had shape X and the field was at offset 3" turns it into a shape check plus an indexed load. V8's hidden classes are exactly this.

## What to build

For [[BUILD-PLAN|build-your-own-language]]:

1. **A stack VM.** Simpler code generation, and fast enough
2. **A tagged union for values.** NaN-box later if you care
3. **Slot-resolved locals.** The biggest easy win
4. **Computed goto** once it works
5. **Mark-and-sweep GC** when you add closures and objects → [[foundations/compilers/10-garbage-collection|GC]]

*Crafting Interpreters* builds exactly this — `clox`, in C, with NaN boxing and a mark-sweep collector. It is the best available guide to this specific task.

---

## Related
- [[foundations/compilers/10-garbage-collection|Garbage Collection]] — what a VM with objects needs next
- [[foundations/compilers/11-jit-compilation|JIT Compilation]] — where VMs go for speed
- [[foundations/compilers/04-asts-and-semantic-analysis|ASTs and Semantic Analysis]] — slot resolution and upvalues
- [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM Internals]] — a production example
- [[foundations/compilers/README|Compilers course map]]
