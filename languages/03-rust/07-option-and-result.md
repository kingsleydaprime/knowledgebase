# Option and Result

**[Beginner → Intermediate]** — No null, no exceptions. Two enums and one operator that replace both.

## `Option<T>` — absence in the type system

```rust
enum Option<T> { Some(T), None }
```

`Option<T>` and `T` are **different types**. You cannot use an `Option<i32>` as an `i32` — you have to handle the `None` case first, and the compiler won't let you skip it.

That's the whole story on null-pointer errors. There is no null, so there's nothing to dereference.

```rust
let maybe: Option<i32> = Some(5);

match maybe {
    Some(n) => println!("{n}"),
    None => println!("nothing"),
}

if let Some(n) = maybe { println!("{n}"); }

let n = maybe.unwrap_or(0);
```

### The methods worth knowing

Writing `match` for every `Option` gets tedious, so the combinators matter:

```rust
opt.is_some() / opt.is_none()

opt.unwrap()                  // panics on None — see below
opt.expect("config missing")  // panics with YOUR message — always prefer this to unwrap
opt.unwrap_or(default)
opt.unwrap_or_else(|| expensive())   // lazy — the closure only runs on None
opt.unwrap_or_default()

opt.map(|v| v * 2)            // Option<T> -> Option<U>
opt.and_then(|v| lookup(v))   // flatMap — for a function that itself returns Option
opt.filter(|v| *v > 5)
opt.or(other) / opt.or_else(|| other())

opt.ok_or(MyError::Missing)          // Option<T> -> Result<T, E>
opt.ok_or_else(|| MyError::Missing)  // lazy version

opt.as_ref()      // Option<T> -> Option<&T>, so you don't move out of it
opt.as_mut()
opt.take()        // moves the value out, leaving None behind
opt.replace(v)
opt.cloned() / opt.copied()   // Option<&T> -> Option<T>
```

`as_ref()` is the one that gets people. `match opt { Some(s) => ... }` on an `Option<String>` **moves** the String out. `match opt.as_ref()` borrows instead.

Chaining reads well once it's familiar:

```rust
let name = config
    .get("user")
    .and_then(|u| u.get("name"))
    .map(|n| n.to_uppercase())
    .unwrap_or_else(|| "anonymous".to_string());
```

## `Result<T, E>` — failure in the type system

```rust
enum Result<T, E> { Ok(T), Err(E) }
```

Rust has no exceptions. A function that can fail returns `Result`, and `Result` is `#[must_use]` — ignoring one is a compiler warning.

```rust
fn read_config(path: &str) -> Result<Config, io::Error> {
    let contents = fs::read_to_string(path)?;
    Ok(parse(&contents))
}
```

The same combinators exist, plus:

```rust
res.is_ok() / res.is_err()
res.unwrap() / res.expect("msg")
res.unwrap_or(default) / res.unwrap_or_else(|e| fallback(e))
res.map(|v| ...)            // transforms Ok
res.map_err(|e| ...)        // transforms Err — you'll use this constantly
res.and_then(|v| next(v))
res.ok()                    // Result<T, E> -> Option<T>, discarding the error
res.err()
res?                        // the important one
```

## The `?` operator

```rust
fn read_username() -> Result<String, io::Error> {
    let mut s = String::new();
    File::open("user.txt")?.read_to_string(&mut s)?;
    Ok(s)
}
```

`?` means: **if `Ok`, unwrap it and continue; if `Err`, return it from this function immediately.**

Without it:

```rust
let mut f = match File::open("user.txt") {
    Ok(f) => f,
    Err(e) => return Err(e),
};
```

`?` is the reason Rust's error handling doesn't feel like Go's. The happy path stays on one line and reads linearly, while errors still propagate explicitly — you get the readability of exceptions with the visibility of return values. Compare with [[languages/02-go/05-errors|Go's `if err != nil`]], which is the same semantics without the sugar.

`?` also works on `Option`, returning `None` early:

```rust
fn first_char(s: &str) -> Option<char> {
    s.chars().next()?.to_lowercase().next()
}
```

### `?` and error conversion

The part that makes `?` powerful: it calls `From::from` on the error, so it converts automatically if a conversion exists.

```rust
enum AppError { Io(io::Error), Parse(ParseIntError) }

impl From<io::Error> for AppError {
    fn from(e: io::Error) -> Self { AppError::Io(e) }
}

fn run() -> Result<i32, AppError> {
    let s = fs::read_to_string("n.txt")?;   // io::Error -> AppError, automatically
    let n: i32 = s.trim().parse()?;         // ParseIntError -> AppError, automatically
    Ok(n)
}
```

Writing those `From` impls by hand is boilerplate, which is why `thiserror` exists. → [[languages/03-rust/08-error-handling-in-practice|Error Handling in Practice]]

`?` needs the enclosing function to return a compatible `Result` (or `Option`). It doesn't work in a `main` that returns `()` — but `fn main() -> Result<(), Box<dyn Error>>` is allowed and is the usual fix.

## When to panic

`unwrap`, `expect`, `panic!`, and slice indexing all abort on failure. The line:

**Panic when it's a bug** — an invariant you're certain of, an impossible state, a programming error. The program is in a state you didn't design for and continuing is worse than stopping.

**Return `Result` when it's an expected condition** — a missing file, bad user input, a failed network call. Not bugs; the world being the world.

```rust
let port: u16 = env::var("PORT")
    .expect("PORT must be set")     // OK at startup — can't run without it
    .parse()
    .expect("PORT must be a number");
```

Startup-time `expect` with a clear message is fine and idiomatic — failing loudly and immediately beats a confusing failure later.

**`unwrap()` in a request handler or a library is not fine.** It panics with no context, and in a server that's an unhandled 500 at best.

> Rules of thumb: `expect` over `unwrap` always, because the message is what future-you reads in the log. Never `unwrap` in library code. Prototype with `unwrap`, then grep for it before shipping — `#![deny(clippy::unwrap_used)]` makes that automatic.

## Why this is better than exceptions

The comparison with [[languages/01-java/01-language/06-exceptions|Java's exceptions]] is worth making explicitly:

- **A function's signature tells you it can fail.** No hidden control flow, no reading the body to find out.
- **You cannot silently ignore it.** `#[must_use]` warns; there's no empty catch block.
- **No unwinding surprises.** No `finally` semantics to reason about, no exception thrown from a destructor.
- **Errors are values.** Store them, collect them, return them in a `Vec` — no special mechanism needed.

The cost is that error types have to be composed by hand, which is what the next note is about.

---

## Related
- [[languages/03-rust/08-error-handling-in-practice|Error Handling in Practice]] — `thiserror`, `anyhow`, and real error types
- [[languages/03-rust/06-structs-enums-and-pattern-matching|Structs, Enums and Pattern Matching]] — the enums these are built from
- [[languages/02-go/05-errors|Go: Errors]] — the same philosophy without `?`
- [[languages/03-rust/README|Rust course map]]
