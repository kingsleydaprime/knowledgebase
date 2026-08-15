# Lexical Analysis

**[Beginner → Intermediate]** — Characters to tokens. The simplest phase, and the one where you decide how good your error messages can ever be.

## The job

```
"let x = 1 + 2;"
        ↓
[LET] [IDENT "x"] [EQUALS] [INT 1] [PLUS] [INT 2] [SEMICOLON] [EOF]
```

The lexer (or scanner, or tokeniser) groups characters into **tokens** — the smallest meaningful units. It also discards whitespace and comments, and it's where you attach source positions.

Why separate it from parsing at all? The parser gets much simpler when it can think about `IDENT` rather than "a letter followed by zero or more alphanumerics". And lexing is a *regular* language problem while parsing needs *context-free* machinery — different tools, cleanly split. → [[foundations/compilers/03-parsing|Parsing]]

## The token

```rust
struct Token {
    kind: TokenKind,
    lexeme: String,        // the exact source text
    span: Span,            // byte offsets — for ERROR MESSAGES
}

struct Span { start: u32, end: u32 }

enum TokenKind {
    // literals
    Int(i64), Float(f64), Str(String), Ident(String),
    // keywords
    Let, Fn, If, Else, While, Return, True, False,
    // operators
    Plus, Minus, Star, Slash, Eq, EqEq, Bang, BangEq, Lt, LtEq,
    // punctuation
    LParen, RParen, LBrace, RBrace, Semicolon, Comma,
    Eof,
}
```

> **Put spans in from the first line of code.** Every token, and later every AST node, carries where it came from. Retrofitting this is genuinely painful, and without it you cannot produce the kind of error message that makes a compiler pleasant to use. → [[foundations/compilers/01-what-a-compiler-is|What a Compiler Is]]

Byte offsets are better than `(line, column)` — smaller, and you convert to line/column only when printing an error, using a precomputed table of line starts.

## A hand-written lexer

The core is a loop with one character of lookahead:

```rust
fn next_token(&mut self) -> Token {
    self.skip_whitespace_and_comments();
    let start = self.pos;

    let c = match self.advance() {
        Some(c) => c,
        None => return self.make(TokenKind::Eof, start),
    };

    let kind = match c {
        '+' => TokenKind::Plus,
        '(' => TokenKind::LParen,

        // MAXIMAL MUNCH: prefer the longest match
        '=' if self.peek() == Some('=') => { self.advance(); TokenKind::EqEq }
        '=' => TokenKind::Eq,
        '!' if self.peek() == Some('=') => { self.advance(); TokenKind::BangEq }
        '!' => TokenKind::Bang,

        '0'..='9' => self.number(start),
        'a'..='z' | 'A'..='Z' | '_' => self.identifier_or_keyword(start),
        '"' => self.string(start),

        _ => { self.error(start, "unexpected character"); TokenKind::Error }
    };

    self.make(kind, start)
}
```

**Maximal munch** is the rule that matters: always take the longest token that matches. `==` is one token, not two `=`. `>=` is one, not `>` then `=`.

It's also the source of a classic C++ wart: `vector<vector<int>>` failed to parse before C++11 because `>>` lexed as a right-shift operator. The fix was a special case in the parser.

### Keywords

```rust
fn identifier_or_keyword(&mut self, start: usize) -> TokenKind {
    while self.peek().is_some_and(|c| c.is_alphanumeric() || c == '_') {
        self.advance();
    }
    match &self.src[start..self.pos] {
        "let" => TokenKind::Let,
        "fn" => TokenKind::Fn,
        "if" => TokenKind::If,
        s => TokenKind::Ident(s.to_string()),
    }
}
```

**Lex an identifier first, then check whether it's a keyword.** Trying to match keywords directly breaks on `letter` — you'd lex `let` and then `ter`. Maximal munch again.

This is also where **contextual keywords** live: `async` in Rust and `await` in JavaScript are identifiers in some positions and keywords in others, which means either lexer state or a parser that accepts `Ident("async")`.

### Numbers and strings

```rust
fn number(&mut self, start: usize) -> TokenKind {
    while self.peek().is_some_and(|c| c.is_ascii_digit() || c == '_') { self.advance(); }

    if self.peek() == Some('.') && self.peek_next().is_some_and(|c| c.is_ascii_digit()) {
        self.advance();                        // consume '.'
        while self.peek().is_some_and(|c| c.is_ascii_digit()) { self.advance(); }
        return TokenKind::Float(...);
    }
    TokenKind::Int(...)
}
```

The two-character lookahead on `.` matters: without it, `1.method()` lexes `1.` as a float and breaks method calls on integers. Rust and Swift both deal with this.

Decisions to make deliberately: numeric separators (`1_000_000`), other bases (`0x1F`, `0b1010`, `0o17`), and **what to do on overflow** — a literal too large for the type is a lexer or a parser error, and silently wrapping is the wrong answer.

Strings need escape handling (`\n`, `\t`, `\"`, `\\`, `\u{1F600}`), and unterminated strings are one of the most common real errors — report them at the *opening* quote, not at EOF.

## Regular expressions, DFAs, and generators

Tokens are **regular languages** — describable by regular expressions, recognisable by a finite automaton. That's the formal basis for `lex`/`flex`.

```
IDENT   [a-zA-Z_][a-zA-Z0-9_]*
INT     [0-9]+
FLOAT   [0-9]+\.[0-9]+
```

A generator converts these to an NFA (Thompson's construction), then to a DFA (subset construction), then minimises it, then emits a table-driven scanner. The result is O(n) with a small constant.

Generators available: `flex` (C), `logos` (Rust, derive-based and very fast), `re2c`.

**Most production compilers hand-write their lexer anyway** — GCC, Clang, rustc, Go, V8 all do. The reasons:

- **Better error messages.** A generated scanner says "no rule matches"; a hand-written one says "unterminated string literal starting here"
- **Context sensitivity.** String interpolation, nested comments, and significant indentation don't fit a pure DFA
- **Performance.** A tight hand-written loop beats a table-driven scanner
- **No build dependency**

**Write it by hand.** It's a few hundred lines and you'll want the control. Generators are worth it for a quick prototype or a language with a genuinely large token set.

## The cases that break the model

**Nested comments** — `/* /* */ */` is not regular; it needs a counter. Just track depth in the lexer.

**String interpolation** — `"hello ${name}"` contains an expression, which needs the parser. Solutions: lex it as one token and re-lex the inside later, or keep a mode stack in the lexer.

**Significant indentation** (Python) — the lexer keeps an indentation stack and emits synthetic `INDENT`/`DEDENT` tokens. That's genuinely stateful and one of the reasons Python's grammar isn't as simple as it looks.

**Automatic semicolon insertion** (JavaScript, Go) — the lexer inserts a semicolon when a line ends with something that could end a statement. It's why this JavaScript returns `undefined`:

```javascript
return
    { value: 1 };        // ASI inserts a semicolon after `return`
```

Go's version is more principled — the rule is stated precisely in the spec, and it's why Go requires `{` on the same line.

**The C typedef problem** — `A * B;` is either a multiplication or a pointer declaration, depending on whether `A` is a type. That requires symbol-table information *during parsing* — the "lexer hack", where the parser feeds type names back to the lexer. A genuine design wart, and a reason later languages made declarations unambiguous.

## Performance

Lexing touches every byte, so it's often 5–15% of front-end time.

**Operate on bytes, not chars.** For UTF-8, only string and identifier contents need decoding; structural characters are ASCII.

**Intern identifiers.** Map each unique string to an integer once; comparisons become integer equality, and it saves substantial allocation. Every serious compiler does this.

**Avoid allocating per token.** Store `Span` and slice the source when needed, rather than copying a `String` into every token.

```rust
enum TokenKind { Ident(Symbol), ... }    // Symbol = u32 index into an interner
```

## Testing it

The lexer is the easiest phase to test thoroughly, and worth doing:

```rust
#[test]
fn operators() {
    assert_tokens("= == ! !=", &[Eq, EqEq, Bang, BangEq]);
}

#[test]
fn unterminated_string_reports_at_open_quote() {
    let errs = lex_errors("let s = \"abc");
    assert_eq!(errs[0].span.start, 8);
}
```

**And fuzz it.** A lexer is a parser of untrusted input; feeding it random bytes finds panics on malformed UTF-8, integer overflow in literals, and unbounded lookahead. → [[languages/04-c/13-debugging-and-tooling|fuzzing]]

---

## Related
- [[foundations/compilers/03-parsing|Parsing]] — what consumes these tokens
- [[foundations/compilers/01-what-a-compiler-is|What a Compiler Is]] — where this sits
- [[languages/04-c/03-the-preprocessor|C: The Preprocessor]] — a separate token-level pass before the real lexer
- [[foundations/compilers/README|Compilers course map]]
