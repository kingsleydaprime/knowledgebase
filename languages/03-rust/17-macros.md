---
id: 757bc104-bd06-4912-8ed1-5292b5626ad1
---

# Macros

**[Advanced]** — Code that writes code, checked by the compiler. Why `println!` has an exclamation mark, and where `#[derive]` comes from.

## Two kinds
<!-- bite: 79e71961-9c4b-4360-b036-950aa83888e8 -->

**Declarative** (`macro_rules!`) — pattern matching on syntax. Good for repetition.

**Procedural** — a Rust function that takes a token stream and returns one. Three flavours: custom `#[derive]`, attribute macros, and function-like macros.

Both operate on the **abstract syntax tree**, not on text. This is the crucial difference from C's preprocessor: a Rust macro can't produce syntactically invalid code, can't capture variables by accident, and gets type-checked after expansion.

## Why macros exist here
<!-- bite: fd16b964-ed5e-42f9-9ef0-2d4517afa7a1 -->

Rust's type system can't express "a function with any number of arguments of any types". `println!("{} {}", a, b)` needs exactly that, plus compile-time validation of the format string. A macro does both:

```rust
println!("{}", x);          // checked at compile time — wrong arity won't build
vec![1, 2, 3];              // can't be a function: variadic
#[derive(Debug)]            // generates an impl from the struct definition
```

## `macro_rules!`
<!-- bite: 27b8e604-b853-45ec-8041-c97cb889d753 -->

```rust
macro_rules! my_vec {
    () => { Vec::new() };

    ($($x:expr),+ $(,)?) => {{           // one or more exprs, optional trailing comma
        let mut v = Vec::new();
        $( v.push($x); )+                 // repeat the body per match
        v
    }};
}

let v = my_vec![1, 2, 3];
```

The syntax is dense. Reading it:

- `$x:expr` — capture something, call it `$x`, and require it to be an *expression*
- `$( ... ),+` — one or more of the pattern, separated by commas (`*` for zero or more, `?` for optional)
- `$( ... )+` in the body — emit once per captured repetition
- The doubled braces `{{ }}` make the expansion a block expression that produces a value

**Fragment specifiers** — what kind of syntax to capture:

```
expr    an expression          ident   an identifier
ty      a type                 pat     a pattern
stmt    a statement            block   a block
item    an item (fn, struct)   path    a path like a::b::C
literal a literal              tt      a single token tree (most flexible)
```

A practical example — reducing real boilerplate:

```rust
macro_rules! impl_from {
    ($from:ty, $variant:ident) => {
        impl From<$from> for AppError {
            fn from(e: $from) -> Self { AppError::$variant(e) }
        }
    };
}

impl_from!(std::io::Error, Io);
impl_from!(serde_json::Error, Json);
```

### Hygiene

```rust
macro_rules! bad {
    () => { let x = 5; };
}

let x = 10;
bad!();
println!("{x}");     // 10 — the macro's `x` is a DIFFERENT variable
```

Identifiers introduced by a macro live in their own syntactic context and cannot collide with the caller's. This is what makes macros safe compared to C's `#define`, where the equivalent silently shadows.

The consequence: a macro can't create a variable for the caller to use unless the name is passed in as an `ident`.

### Scope and export

```rust
#[macro_export]              // makes it available at the crate root
macro_rules! my_macro { ... }
```

`macro_rules!` macros are textually scoped — usable only *after* their definition in the file, which is unlike everything else in Rust. `#[macro_export]` lifts them to the crate root and makes them importable.

## Procedural macros
<!-- bite: 5cc00fe7-4291-4ab9-b8bf-2848b0e3d64d -->

These live in a **separate crate** with `proc-macro = true`, because they run at compile time and must be compiled first.

```toml
[lib]
proc-macro = true

[dependencies]
syn = { version = "2", features = ["full"] }   # parse Rust syntax
quote = "1"                                     # generate Rust syntax
proc-macro2 = "1"
```

### Derive macros

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
struct User { name: String }
```

Each derive reads the type definition and generates an `impl`. This is the most-used proc macro by far — `serde`'s `Serialize`/`Deserialize` alone probably accounts for most of it.

A minimal one:

```rust
#[proc_macro_derive(Hello)]
pub fn hello_derive(input: TokenStream) -> TokenStream {
    let ast: DeriveInput = syn::parse(input).unwrap();
    let name = &ast.ident;
    quote! {
        impl Hello for #name {
            fn hello(&self) { println!("Hello, {}!", stringify!(#name)); }
        }
    }.into()
}
```

`syn` parses the input into a syntax tree; `quote!` builds the output with `#name` interpolation. That pair is the whole workflow.

### Attribute macros

```rust
#[tokio::main]
async fn main() { }

#[get("/users/{id}")]
async fn handler() { }
```

These *replace* the item they're attached to. `#[tokio::main]` rewrites your async `main` into a sync one that builds a runtime and calls `block_on` — which is worth knowing, because it explains why `#[tokio::main]` isn't magic and can be written out by hand.

### Function-like proc macros

```rust
let q = sql!(SELECT * FROM users WHERE id = ?);
let re = regex!(r"^\d{4}-\d{2}-\d{2}$");        // compiled AT COMPILE TIME
```

These can validate their input at compile time — a malformed SQL query or regex becomes a build error. `sqlx::query!` goes further and checks the query against a live database schema during compilation, which is a genuinely remarkable thing to be able to do.

## Costs
<!-- bite: 00c853ed-3ebb-472d-994a-d8909e2421f3 -->

**Compile time.** Proc macros are programs that run during your build. `serde`'s derive is a significant chunk of many projects' build times.

**Debuggability.** Errors inside generated code point at confusing places. The tools:

```bash
cargo install cargo-expand
cargo expand                 # see the code AFTER macro expansion
cargo expand --test mytest
```

`cargo expand` is essential the moment you write or debug a macro. It's also the best way to understand what `#[derive(Debug)]` or `#[tokio::main]` actually produce.

**Readability.** A codebase heavy in custom macros is harder for newcomers — the syntax isn't in the book.

## When to write one
<!-- bite: d12f382f-f499-4d04-bfeb-6eb517d1e386 -->

**Yes:**
- Repetitive trait impls across many types (`impl_from!` above)
- Deriving behaviour from a struct's shape — serialisation, ORM mapping, CLI parsing
- Compile-time validation of a DSL — SQL, regex, format strings
- Genuinely variadic APIs

**No:**
- **A function will do.** This is the main one. Generics and traits cover most of what people reach for macros to do.
- To work around a design problem
- To save a few lines once

> The order to try things: **function → generic function → trait → `macro_rules!` → proc macro.** Stop at the first that works. Most code should never leave the first three.

---

## Related
<!-- bite: 99946caa-0085-4446-a2da-208cfed63abf -->
- [[languages/03-rust/09-traits|Traits]] — usually the better tool
- [[languages/03-rust/16-modules-cargo-and-testing|Modules, Cargo and Testing]] — where proc-macro crates fit
- [[languages/03-rust/08-error-handling-in-practice|Error Handling]] — `thiserror` is a derive macro
- [[languages/03-rust/index|Rust course map]]
