# Modules, Cargo and Testing

**[Intermediate]** — Code organisation, the package manager, and a testing story that's mostly built in.

## Modules

A module is a namespace. Unlike [[languages/02-go/12-modules-and-project-layout|Go]], where a package *is* a directory, Rust decouples them — modules can be inline, in a file, or in a directory.

```rust
// src/lib.rs
mod network;                    // loads src/network.rs OR src/network/mod.rs

pub mod http {                  // inline module
    pub fn get() { }
    fn internal() { }           // private to this module

    pub mod headers {
        pub fn parse() { }
    }
}

use http::headers::parse;       // bring into scope
use http::{get, headers};
use std::collections::{HashMap, HashSet};
use std::io::Result as IoResult;
pub use http::get;              // RE-EXPORT — part of your public API
```

Modern layout uses `network.rs` plus a `network/` directory for submodules. The old `mod.rs` convention still works and you'll see both.

### Visibility

**Everything is private by default**, including to parent modules — stricter than most languages.

```rust
pub fn f() { }              // public
pub(crate) fn g() { }       // visible within this crate only
pub(super) fn h() { }       // visible to the parent module
pub(in crate::a::b) fn i()  // visible within a specific path
fn j() { }                  // this module and its children
```

**`pub(crate)` is the workhorse.** It's how you share across your crate without committing to a public API — the equivalent of Go's `internal/`, but per-item and finer-grained.

Note that a child module can always see its parent's private items; the reverse isn't true.

```rust
use crate::network::http;       // absolute, from the crate root
use self::helpers::x;           // relative to here
use super::sibling;             // parent module
```

## Crates and packages

- **Crate** — a compilation unit. One binary or one library.
- **Package** — one `Cargo.toml`. Contains at most one library crate and any number of binaries.

```
myproject/
├── Cargo.toml
├── src/
│   ├── lib.rs          ← the library crate root
│   ├── main.rs         ← a binary crate root
│   └── bin/
│       └── tool.rs     ← another binary: cargo run --bin tool
├── tests/              ← integration tests, each file its own crate
├── benches/            ← benchmarks
└── examples/           ← compiled and checked by `cargo test`
```

A very common shape is `lib.rs` holding all the logic with a thin `main.rs` that calls it — because integration tests and benchmarks can only use the *library*, not the binary.

## Cargo

```toml
[package]
name = "myservice"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
anyhow = "1.0"
local = { path = "../local" }
gh = { git = "https://github.com/x/y", tag = "v1.0" }

[dev-dependencies]
criterion = "0.5"            # tests and benches only

[profile.release]
opt-level = 3
lto = true                   # link-time optimisation — meaningfully faster, slower to build
codegen-units = 1            # better optimisation, slower build
strip = true                 # strip symbols; much smaller binary
```

```bash
cargo add serde --features derive
cargo update
cargo tree -d                    # find DUPLICATE versions of a dependency
cargo build --release
cargo install cargo-edit cargo-watch cargo-nextest
```

**`"1.0"` means `>=1.0.0, <2.0.0`** — caret semantics by default, like npm. `Cargo.lock` pins exact versions; **commit it for binaries, and for libraries too these days** (the old advice against it has been reversed).

**Feature flags** are Rust's conditional compilation and a genuine strength:

```toml
[features]
default = ["json"]
json = ["dep:serde_json"]
full = ["json", "tls"]
```

```rust
#[cfg(feature = "json")]
pub mod json;
```

They're also the main cause of long compile times — `tokio = { features = ["full"] }` pulls in far more than most projects use. Narrowing features is the cheapest build-time win available.

### Workspaces

```toml
# top-level Cargo.toml
[workspace]
members = ["api", "core", "cli"]
resolver = "2"

[workspace.dependencies]
serde = "1.0"                 # members write: serde = { workspace = true }
```

One `Cargo.lock`, one `target/` directory, shared dependency versions. This is how any non-trivial Rust project is laid out, and splitting into crates is also the main lever for **parallel compilation** — crates build concurrently, modules within a crate do not.

## Testing

```rust
#[cfg(test)]                    // only compiled during `cargo test`
mod tests {
    use super::*;

    #[test]
    fn adds() {
        assert_eq!(add(2, 2), 4);
    }

    #[test]
    #[should_panic(expected = "divide by zero")]
    fn panics() { divide(1, 0); }

    #[test]
    fn with_result() -> Result<(), String> {
        if add(2, 2) == 4 { Ok(()) } else { Err("nope".into()) }
    }

    #[test]
    #[ignore]                   // run only with --ignored
    fn slow() { }
}
```

**Unit tests live in the same file as the code**, in a `#[cfg(test)] mod tests`. That's idiomatic, not a compromise — it lets them test private functions, which most languages can't.

```rust
assert!(cond);
assert_eq!(a, b);
assert_ne!(a, b);
assert!(cond, "custom message with {value}");
```

The assertion macros print both values on failure, so there's no assertion-library debate like [[languages/02-go/11-testing-and-benchmarking|Go's]].

**Integration tests** go in `tests/`, one crate per file, and can only use your public API — which is a useful forcing function for API design:

```rust
// tests/api.rs
use myservice::process;

#[test]
fn end_to_end() { assert!(process("input").is_ok()); }
```

```bash
cargo test
cargo test -- --nocapture       # show println! output
cargo test adds                 # filter by name
cargo test -- --test-threads=1  # tests run in PARALLEL by default
cargo test --doc                # just the doc tests
```

Tests run in parallel by default — the opposite of most frameworks — which is only safe because of `Send`/`Sync`. Shared mutable state between tests won't compile.

### The ecosystem crates

```rust
proptest / quickcheck    // property-based testing
insta                    // snapshot testing — excellent for parsers and serialisers
mockall                  // mocking, when you can't hand-roll a fake
rstest                   // parameterised tests and fixtures
criterion                // statistical benchmarking → 18-performance
cargo-nextest            // a much faster test runner
```

Hand-rolled fakes work as well as they do in Go — implement the trait with a test struct. Reach for `mockall` only for large traits.

## Documentation

```rust
//! Crate-level docs, at the top of lib.rs

/// Adds two numbers.
///
/// # Examples
/// ```
/// assert_eq!(mylib::add(2, 2), 4);
/// ```
///
/// # Panics
/// Panics if the result overflows.
///
/// # Errors
/// Returns `Err` if the input is negative.
pub fn add(a: i32, b: i32) -> i32 { a + b }
```

```bash
cargo doc --open        # your crate AND all dependencies, offline
cargo test --doc        # run the examples
```

**Doc examples are compiled and run as tests.** Documentation that can't rot, because CI fails when it does. The `# Panics`, `# Errors` and `# Safety` headings are universal conventions worth following.

`#![warn(missing_docs)]` at the crate root enforces documentation on public items.

---

## Related
- [[languages/03-rust/18-performance-and-zero-cost|Performance]] — release profiles and benchmarking
- [[languages/02-go/12-modules-and-project-layout|Go: Modules and Layout]] — a different packaging model
- [[devops/06-ci-cd/08-ci-pipelines|CI Pipelines]] — wiring `cargo test`, `clippy` and `fmt` into gates
- [[languages/03-rust/README|Rust course map]]
