# Parsing

**[Intermediate]** — Tokens to a tree. Recursive descent for statements, Pratt for expressions, and why nobody uses parser generators any more.

## Grammars

A **context-free grammar** describes legal arrangements of tokens:

```
expr    → term (("+" | "-") term)*
term    → factor (("*" | "/") factor)*
factor  → NUMBER | IDENT | "(" expr ")"
```

Read `→` as "can be", `*` as "zero or more", `|` as "or". This is EBNF, and it's how nearly every language spec states its syntax.

**Precedence and associativity are encoded in the shape of the grammar.** `expr` calls `term`, so `*` binds tighter than `+` — because by the time you're inside `term`, the `+` level has already committed. That's the entire trick, and it's why the grammar has one rule per precedence level.

The classic grammar problem:

```
expr → expr "+" expr | NUMBER
```

**Ambiguous** — `1 + 2 + 3` has two parse trees. And **left-recursive**: `expr` starts by calling `expr`, which infinitely recurses in a top-down parser. The layered form above fixes both.

## Recursive descent

One function per grammar rule. That's it.

```rust
fn parse_expr(&mut self) -> Expr {
    let mut left = self.parse_term();
    while self.matches(&[Plus, Minus]) {
        let op = self.previous();
        let right = self.parse_term();
        left = Expr::Binary { left: Box::new(left), op, right: Box::new(right) };
    }
    left
}

fn parse_term(&mut self) -> Expr {
    let mut left = self.parse_factor();
    while self.matches(&[Star, Slash]) { ... }
    left
}

fn parse_factor(&mut self) -> Expr {
    if self.matches(&[Number]) { return Expr::Literal(...); }
    if self.matches(&[LParen]) {
        let e = self.parse_expr();
        self.expect(RParen, "expected ')' after expression");
        return Expr::Grouping(Box::new(e));
    }
    self.error("expected expression")
}
```

**The `while` loop is what gives left associativity** — `1-2-3` becomes `(1-2)-3`. For right associativity (assignment, exponentiation), recurse instead:

```rust
fn parse_assign(&mut self) -> Expr {
    let left = self.parse_or();
    if self.matches(&[Eq]) {
        let value = self.parse_assign();          // RIGHT-recursive
        return Expr::Assign { target: ..., value: Box::new(value) };
    }
    left
}
```

**This is what to write.** GCC, Clang, rustc, Go, V8, and TypeScript all use hand-written recursive descent. It's readable, debuggable with an ordinary debugger, gives complete control over error messages, and handles context-sensitive cases a generator can't.

The limitation: **the grammar must not be left-recursive**, and one function per precedence level gets tedious when you have fifteen of them. Which is what Pratt parsing fixes.

## Pratt parsing

For expressions, a precedence table beats a stack of nearly-identical functions.

```rust
fn parse_expr(&mut self, min_bp: u8) -> Expr {
    // NUD — "null denotation": what starts an expression
    let mut left = match self.advance() {
        Number(n) => Expr::Literal(n),
        Ident(s)  => Expr::Var(s),
        Minus     => Expr::Unary(Minus, Box::new(self.parse_expr(PREFIX_BP))),
        LParen    => { let e = self.parse_expr(0); self.expect(RParen); e }
        t => return self.error(&format!("unexpected {t:?}")),
    };

    // LED — "left denotation": what CONTINUES an expression
    loop {
        let op = match self.peek() {
            Plus | Minus | Star | Slash | EqEq => self.peek(),
            _ => break,
        };

        let (l_bp, r_bp) = infix_binding_power(op);
        if l_bp < min_bp { break; }              // ← the whole precedence mechanism

        self.advance();
        let right = self.parse_expr(r_bp);
        left = Expr::Binary { left: Box::new(left), op, right: Box::new(right) };
    }
    left
}

fn infix_binding_power(op: TokenKind) -> (u8, u8) {
    match op {
        EqEq          => (1, 2),
        Plus | Minus  => (3, 4),      // left-assoc: left < right
        Star | Slash  => (5, 6),
        Caret         => (10, 9),     // RIGHT-assoc: left > right
        _ => unreachable!(),
    }
}
```

**Associativity is `(left_bp, right_bp)`.** Left-associative means `left < right`; right-associative means `left > right`. That asymmetry is the entire mechanism, and it's much neater than a function per level.

Adding an operator is one table entry rather than a new function and a rewiring of two others. **Use recursive descent for statements and declarations, Pratt for expressions** — that combination is what most modern hand-written parsers do.

## LL, LR, and the generator era

The theory, which you should recognise without necessarily using:

**LL(k)** — Left-to-right, Leftmost derivation, k tokens of lookahead. Top-down. Recursive descent is hand-written LL(k). Can't handle left recursion.

**LR(k)** — Left-to-right, Rightmost derivation. Bottom-up: shift tokens onto a stack, reduce when the top matches a rule. **Strictly more powerful than LL** — handles left recursion and more grammars.

- **LALR(1)** — the `yacc`/`bison` variety. Smaller tables, occasional mysterious conflicts
- **GLR** — forks on ambiguity and explores all parses. Handles genuinely ambiguous grammars like C++

**PEG** — Parsing Expression Grammars. Ordered choice, so ambiguity is impossible by construction; **packrat parsing** memoises for linear time at the cost of memory.

The generators: `yacc`/`bison`, ANTLR (LL(*), good tooling and error messages), `tree-sitter` (GLR, incremental — designed for editors), `lalrpop` and `pest` in Rust.

### Why hand-written won

Generators dominated for decades and lost. The reasons are worth knowing because they're the same reasons that recur across tooling decisions:

**Error messages.** A generated parser says "syntax error at token 47". A hand-written one says "expected `)` to close the `(` on line 3". That difference is most of a compiler's usability.

**Error recovery.** Generators recover badly; you want to report ten errors, not one.

**Context sensitivity.** C's typedef ambiguity, Rust's turbofish (`::<>` exists precisely to disambiguate `a < b > c`), template `>>`, contextual keywords, and significant whitespace all need the parser to be a little bit stateful.

**Debuggability.** Stepping through `parse_expression` in a debugger works. Stepping through a generated LALR table-walker does not.

**The shift/reduce conflict experience.** Anyone who has debugged one in `bison` understands why people stopped.

**Use a generator when** the grammar is large, stable, and you don't own it — parsing SQL, or an existing language's syntax for tooling. `tree-sitter` in particular is excellent for editor integration because it's incremental and error-tolerant by design.

## Error recovery

Reporting one error per compile is a bad experience. Two techniques:

**Panic-mode recovery** — on error, discard tokens until you reach a plausible synchronisation point:

```rust
fn synchronize(&mut self) {
    self.advance();
    while !self.is_at_end() {
        if self.previous().kind == Semicolon { return; }        // statement boundary
        match self.peek().kind {
            Fn | Let | If | While | Return => return,           // start of a new construct
            _ => { self.advance(); }
        }
    }
}
```

Simple and effective. Statement boundaries and block delimiters are the natural sync points.

**Error productions** — grammar rules that match *common mistakes* specifically, so you can give a targeted message:

```rust
// a rule matching `if x == 1 {` without parens, in a language that requires them
if self.check(If) && !self.check_next(LParen) {
    self.error_with_help("expected '(' after 'if'", "add parentheses around the condition");
}
```

That's how the best error messages happen — someone anticipated the mistake.

**Produce a partial AST with error nodes** rather than bailing out. Later phases can then run and report *their* errors too, and it's essential for IDE features, where the code is almost always incomplete mid-keystroke.

## Ambiguity

**The dangling else:**

```
if (a) if (b) x(); else y();      // which `if` owns the `else`?
```

Nearly every language resolves it as "bind to the nearest `if`" — a special case in the parser, or mandatory braces (Rust, Go) so it can't arise.

**Expression vs statement:** in C-family languages, `{` starts either a block or an object literal in JavaScript. JS resolves it by position, which is why `{}+[]` is a famous puzzle.

**The most vexing parse:**

```cpp
Widget w();          // a FUNCTION declaration, not a variable
```

C++ resolves ambiguity toward declarations. → [[languages/05-cpp/03-classes-and-raii|C++: Classes]]

The lesson for a language designer: **ambiguity you resolve by rule is ambiguity your users will get wrong.** Prefer a syntax where it can't arise.

## Practical advice

1. **Hand-written recursive descent + Pratt for expressions.** This is the answer for a new language
2. **Spans on every node**, propagated from tokens
3. **Never panic on bad input** — produce error nodes and continue
4. **Synchronise at statement boundaries**
5. **Write the grammar down** in EBNF, even informally. It's the spec, and it catches ambiguity before you implement it
6. **Test with a corpus** of valid programs and a corpus of broken ones with expected messages
7. **Fuzz it** — a parser is untrusted-input handling

---

## Related
- [[foundations/compilers/02-lexical-analysis|Lexical Analysis]] — where the tokens come from
- [[foundations/compilers/04-asts-and-semantic-analysis|ASTs and Semantic Analysis]] — the tree being built
- [[foundations/dsa/04-data-structures/05-trees/01-trees|Trees]] · [[foundations/dsa/04-data-structures/07-stacks-and-queues|Stacks]] — the structures underneath
- [[foundations/compilers/README|Compilers course map]]
