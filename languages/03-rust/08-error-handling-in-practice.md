# Error Handling in Practice

**[Intermediate]** — Building real error types, the `thiserror`/`anyhow` split, and how errors become HTTP responses.

## The `Error` trait

```rust
pub trait Error: Debug + Display {
    fn source(&self) -> Option<&(dyn Error + 'static)> { None }
}
```

That's the whole contract: printable for humans (`Display`), printable for developers (`Debug`), and optionally pointing at the error that caused it (`source`). The `source` chain is Rust's equivalent of a Java stack trace's "Caused by" — except you build it deliberately.

## Hand-rolled, so you know what the macros generate

```rust
#[derive(Debug)]
enum ConfigError {
    NotFound(String),
    Io(std::io::Error),
    Parse { line: usize, msg: String },
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Self::NotFound(p) => write!(f, "config not found at {p}"),
            Self::Io(e) => write!(f, "reading config: {e}"),
            Self::Parse { line, msg } => write!(f, "parse error on line {line}: {msg}"),
        }
    }
}

impl std::error::Error for ConfigError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::Io(e) => Some(e),
            _ => None,
        }
    }
}

impl From<std::io::Error> for ConfigError {
    fn from(e: std::io::Error) -> Self { Self::Io(e) }
}
```

That's ~25 lines of boilerplate for one error type, and the `From` impl is what makes `?` convert automatically. Nobody writes this by hand any more.

## `thiserror` — for libraries

```rust
use thiserror::Error;

#[derive(Debug, Error)]
enum ConfigError {
    #[error("config not found at {0}")]
    NotFound(String),

    #[error("reading config")]
    Io(#[from] std::io::Error),        // #[from] generates the From impl AND sets source()

    #[error("parse error on line {line}: {msg}")]
    Parse { line: usize, msg: String },
}
```

Everything above, generated. `#[from]` gives you the `From` conversion so `?` works, and wires `source()` at the same time.

**Use `thiserror` when callers need to distinguish failures** — which is the definition of a library. Your error type is part of your public API: a caller should be able to `match` on it and react differently to "not found" versus "permission denied".

## `anyhow` — for applications

```rust
use anyhow::{Context, Result, bail};

fn run() -> Result<()> {                      // Result<(), anyhow::Error>
    let cfg = load_config()
        .context("loading configuration")?;   // adds context to whatever error came up

    let port = cfg.port
        .ok_or_else(|| anyhow!("no port configured"))?;

    if port < 1024 {
        bail!("port {port} is privileged");    // early return with an error
    }
    Ok(())
}
```

`anyhow::Error` is a type-erased wrapper around any `Error`. You lose the ability to match on specific variants; you gain not having to define types at all, and `?` accepts everything.

`.context()` is the important part — it's `%w` wrapping from [[languages/02-go/05-errors|Go]], with the chain printed for you:

```
Error: loading configuration

Caused by:
    0: reading config file
    1: No such file or directory (os error 2)
```

**Use `anyhow` in binaries** — CLIs, services, anything at the top of the stack where the response to a failure is "log it and return 500". Nobody is matching on your error type because nobody is calling you.

### The split, stated plainly

| | `thiserror` | `anyhow` |
|---|---|---|
| Where | libraries | applications |
| Error type | your enum | erased |
| Can callers match? | yes | no |
| Boilerplate | some | none |

They compose: a binary using `anyhow` happily consumes libraries using `thiserror`. Using both in one workspace is normal — `thiserror` in your `lib` crates, `anyhow` in `main.rs`.

If you want to downcast out of `anyhow` occasionally:

```rust
if let Some(e) = err.downcast_ref::<ConfigError>() { ... }
```

## `Box<dyn Error>` — the no-dependency option

```rust
fn run() -> Result<(), Box<dyn std::error::Error>> {
    let s = fs::read_to_string("f.txt")?;   // any error converts
    Ok(())
}
```

Works with `?` for anything implementing `Error`, needs no crates. It's what `fn main() -> Result<(), Box<dyn Error>>` uses, and it's fine for small programs. `anyhow` is strictly better — it adds context, backtraces, and a nicer `Display` — but this is the zero-dependency version.

## Errors to HTTP responses

The pattern that connects this to [[backend/frameworks/rust/README|Axum]] — implement `IntoResponse` on your error type and every handler can just use `?`:

```rust
#[derive(Debug, Error)]
enum ApiError {
    #[error("not found")]
    NotFound,
    #[error("invalid input: {0}")]
    Validation(String),
    #[error(transparent)]
    Internal(#[from] anyhow::Error),
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, msg) = match self {
            Self::NotFound => (StatusCode::NOT_FOUND, self.to_string()),
            Self::Validation(_) => (StatusCode::BAD_REQUEST, self.to_string()),
            Self::Internal(ref e) => {
                tracing::error!("internal error: {e:?}");    // log the detail
                (StatusCode::INTERNAL_SERVER_ERROR, "internal error".into())  // don't leak it
            }
        };
        (status, Json(json!({ "error": msg }))).into_response()
    }
}

async fn get_user(Path(id): Path<u64>) -> Result<Json<User>, ApiError> {
    let user = db::find(id).await?.ok_or(ApiError::NotFound)?;
    Ok(Json(user))
}
```

Note the two things that separates this from a naive version: internal errors are **logged in full and reported as generic**, and `#[error(transparent)]` forwards `Display` to the wrapped error rather than adding a layer.

This is the type-system version of Spring's `@ControllerAdvice` and Nest's exception filters — one place, checked by the compiler, no runtime reflection. → [[backend/01-foundations/03-the-request-lifecycle|The Request Lifecycle]]

## Backtraces

```bash
RUST_BACKTRACE=1 cargo run
RUST_BACKTRACE=full cargo run
```

`anyhow::Error` captures a backtrace automatically when the feature is enabled. Note it's captured at error *creation*, not at the `?` that propagates it — so create errors where they happen, not where you notice them.

## Practical rules

1. **Libraries: `thiserror`. Binaries: `anyhow`.**
2. **Add context at every layer** with `.context()` — an error that says "No such file or directory" and nothing else is nearly useless.
3. **Never `unwrap` in library code.** `#![deny(clippy::unwrap_used)]` enforces it.
4. **`expect` over `unwrap`**, always — the message is what you read in the log.
5. **Don't leak internal errors to clients.** Log the detail, return the generic.
6. **Panics are for bugs.** If it's a condition the world can produce, it's a `Result`.

---

## Related
- [[languages/03-rust/07-option-and-result|Option and Result]] — the types being composed here
- [[languages/03-rust/09-traits|Traits]] — `Error`, `Display`, `From` are all traits
- [[backend/frameworks/rust/README|Rust Backends]] — `IntoResponse` in context
- [[languages/02-go/05-errors|Go: Errors]] — the same philosophy, more manual
- [[languages/03-rust/README|Rust course map]]
