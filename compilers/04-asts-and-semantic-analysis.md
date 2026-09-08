# ASTs and Semantic Analysis

**[Intermediate]** — Designing the tree, walking it without drowning in boilerplate, and resolving names to the things they mean.

## Designing the AST

The AST drops everything the parser needed but the rest of the compiler doesn't — parentheses, semicolons, the precedence scaffolding.

```rust
enum Expr {
    Literal { value: Value, span: Span },
    Var     { name: Symbol, span: Span },
    Binary  { op: BinOp, left: Box<Expr>, right: Box<Expr>, span: Span },
    Unary   { op: UnOp, operand: Box<Expr>, span: Span },
    Call    { callee: Box<Expr>, args: Vec<Expr>, span: Span },
    Assign  { target: Box<Expr>, value: Box<Expr>, span: Span },
}

enum Stmt {
    Let    { name: Symbol, init: Option<Expr>, span: Span },
    Expr   (Expr),
    Block  { stmts: Vec<Stmt>, span: Span },
    If     { cond: Expr, then_branch: Box<Stmt>, else_branch: Option<Box<Stmt>>, span: Span },
    While  { cond: Expr, body: Box<Stmt>, span: Span },
    Fn     { name: Symbol, params: Vec<Param>, body: Vec<Stmt>, span: Span },
    Return { value: Option<Expr>, span: Span },
}
```

**Notice there's no `Grouping` node.** `(1 + 2) * 3` produces a tree where the addition is already the left child of the multiplication — the parentheses did their job during parsing and carry no further information.

(Exception: a formatter or linter *does* need them, which is why those tools use a **concrete syntax tree** that keeps every token, whitespace and comment. `rustfmt` and `tree-sitter` work on CSTs.)

**Every node carries a span.** Repetitive, and it's what makes every later error message possible.

## Arena allocation

`Box<Expr>` gives you a pointer chase per node and an allocation per node. The standard alternative:

```rust
struct ExprId(u32);                 // an index, not a pointer

struct Ast { exprs: Vec<Expr>, stmts: Vec<Stmt> }

enum Expr {
    Binary { op: BinOp, left: ExprId, right: ExprId, span: Span },
}

let left = &ast.exprs[id.0 as usize];
```

Everything in one `Vec`, referenced by index. The benefits are substantial:

- **One allocation**, not thousands
- **Cache locality** — nodes are contiguous
- **`Copy` IDs** — no borrow-checker fights in Rust, no ownership questions in C++
- **Cycles are trivial** — an index can point anywhere, so parent pointers and cross-references don't need `Rc<RefCell<>>`
- **Cheap serialisation** — dump the `Vec`

The cost is losing type safety at the index level (an `ExprId` could index the wrong arena) and slightly noisier code. **Every serious compiler does this** — rustc, Clang, Zig, and Roslyn all use arenas or index-based ASTs. → [[languages/04-c/07-memory-management|arenas]]

## Walking the tree

**Pattern matching**, in a language that has it:

```rust
fn eval(&mut self, e: &Expr) -> Value {
    match e {
        Expr::Literal { value, .. } => value.clone(),
        Expr::Binary { op, left, right, .. } => {
            let l = self.eval(left);
            let r = self.eval(right);
            self.binary_op(*op, l, r)
        }
        Expr::Var { name, span } => self.env.get(*name)
            .unwrap_or_else(|| self.error(*span, "undefined variable")),
    }
}
```

Exhaustive matching is the killer feature: **add a node type and every match becomes a compile error listing what needs updating.** That's the same argument as [[languages/03-rust/06-structs-enums-and-pattern-matching|Rust's enums]] and it's why compilers are pleasant to write in ML-family languages.

**The visitor pattern**, in a language without sum types:

```java
interface Visitor<R> {
    R visitBinary(Binary expr);
    R visitLiteral(Literal expr);
}

abstract class Expr { abstract <R> R accept(Visitor<R> v); }
class Binary extends Expr { <R> R accept(Visitor<R> v) { return v.visitBinary(this); } }
```

Verbose, and it recovers the "add a case, get an error everywhere" property via the interface. → [[concepts/03-design-patterns/03-behavioral-patterns|Visitor]]

**Watch the recursion depth.** A deeply nested expression — a machine-generated file with 100,000 chained `+` — will blow the stack in a recursive walker. Real compilers either bound nesting depth explicitly (and report it as an error) or use an explicit stack. It's a genuine crash-on-untrusted-input bug, and fuzzing finds it immediately.

## Multiple passes

Semantic analysis is usually several traversals, each doing one thing:

```
parse → AST
  ↓
resolve names       every identifier → its declaration
  ↓
type check          every expression → its type
  ↓
other checks        reachability, definite assignment, exhaustiveness, borrowck
  ↓
lower to IR
```

Separating them keeps each pass simple and gives better errors — a name-resolution error is reported as such, rather than surfacing as a confusing type error.

## Scopes and symbol tables

A **symbol table** maps names to what they denote — a variable, function, type, or module.

```rust
struct Scope {
    symbols: HashMap<Symbol, SymbolId>,
    parent: Option<ScopeId>,
}

fn lookup(&self, name: Symbol) -> Option<SymbolId> {
    let mut scope = Some(self.current);
    while let Some(id) = scope {
        if let Some(&sym) = self.scopes[id].symbols.get(&name) { return Some(sym); }
        scope = self.scopes[id].parent;                          // walk OUTWARD
    }
    None
}
```

Walking outward from the innermost scope is **lexical scoping**, and shadowing falls out of it for free — an inner declaration is found first.

```rust
fn resolve_block(&mut self, stmts: &[Stmt]) {
    self.push_scope();
    for s in stmts { self.resolve_stmt(s); }
    self.pop_scope();
}
```

### Declaration order

Two designs, and the choice is visible to users:

**Sequential** — a name must be declared before use. Simple, one pass, matches how you read.

**Hoisted** — collect all declarations in a first pass, then resolve bodies. Necessary for mutual recursion:

```rust
fn is_even(n: u32) -> bool { n == 0 || is_odd(n - 1) }     // is_odd not yet declared
fn is_odd(n: u32) -> bool { n != 0 && is_even(n - 1) }
```

Most languages hoist *items* (functions, types) and require sequential declaration of *locals*. C's forward declarations are the manual version of hoisting, and the reason [[languages/04-c/02-headers-and-the-translation-unit|headers exist]].

JavaScript's `var` hoisting — the declaration moves but not the initialisation — is a well-known wart that `let` and `const` fixed with the temporal dead zone.

### Resolving to slots

Rather than a hash lookup at runtime, resolve each variable to a **stack slot index** at compile time:

```rust
enum VarRef {
    Local(u16),          // slot in the current frame
    Upvalue(u16),        // captured from an enclosing function
    Global(Symbol),
}
```

Turning a name into an index is one of the biggest single wins available to an interpreter — array indexing instead of hashing on every variable access. → [[foundations/compilers/09-bytecode-and-virtual-machines|Bytecode VMs]]

## Closures and upvalues

The interesting case:

```rust
fn make_counter() -> impl FnMut() -> u32 {
    let mut count = 0;
    move || { count += 1; count }        // `count` OUTLIVES make_counter
}
```

The closure refers to a local of an already-returned function. So a closure is **code plus captured environment**, and the captured variables must live somewhere other than the stack frame that created them.

Two implementations:

**Heap-allocated environments** — every scope is a heap object, chained to its parent. Simple, and slow: every variable access is a pointer chase.

**Upvalues** (Lua's approach, and Crafting Interpreters') — locals live on the stack normally; when a closure captures one, it gets an *upvalue* pointing at the stack slot. If the function returns while a closure still holds it, the upvalue is **closed** — the value is copied into the upvalue itself.

Faster, because the common case (an uncaptured local) stays a plain stack slot.

**Capture semantics are a language design decision**, and a visible one:

```javascript
// JavaScript pre-ES6: `var` is function-scoped, all closures share ONE binding
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i));    // 3 3 3
for (let i = 0; i < 3; i++) setTimeout(() => console.log(i));    // 0 1 2 — fresh binding
```

Go had the same bug and **fixed it in 1.22** by giving each iteration a fresh variable. → [[languages/02-go/02-language-fundamentals|Go: Fundamentals]]

Rust makes it explicit: `move` captures by value, otherwise by reference, and the borrow checker enforces the lifetimes. → [[languages/03-rust/10-generics-and-trait-bounds|closure traits]]

## Other semantic checks

Things that are neither parsing nor typing:

**Definite assignment** — is this variable definitely initialised on every path? Needs dataflow analysis. Java and C# enforce it; C doesn't, which is a whole bug class.

**Reachability** — code after `return` is unreachable. A warning in most languages, an error in some.

**Exhaustiveness** — does this `match` cover every case? Genuinely valuable, and the reason [[languages/03-rust/06-structs-enums-and-pattern-matching|sum types]] are safer than an integer tag.

**Control-flow validity** — `break` outside a loop, `return` outside a function.

**Ownership and borrowing** — Rust's borrow checker is a semantic pass operating on a CFG, after type checking.

These mostly need a **control-flow graph** rather than the AST, which is one of the motivations for lowering to an IR. → [[foundations/compilers/06-intermediate-representations|IR]]

---

## Related
- [[foundations/compilers/03-parsing|Parsing]] — what produces the AST
- [[foundations/compilers/05-type-systems-and-checking|Type Systems and Checking]] — the next pass
- [[foundations/compilers/09-bytecode-and-virtual-machines|Bytecode VMs]] — where slot resolution pays off
- [[concepts/03-design-patterns/03-behavioral-patterns|Design Patterns: Visitor]]
- [[foundations/compilers/README|Compilers course map]]
