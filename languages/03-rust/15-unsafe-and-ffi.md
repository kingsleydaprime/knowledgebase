# Unsafe and FFI

**[Advanced]** — What `unsafe` actually permits, why it isn't a way out of the borrow checker, and calling C from Rust.

## What `unsafe` means

The most common misconception: `unsafe` does **not** turn off the borrow checker, disable ownership, or make Rust into C. Ownership, borrowing, lifetimes and type checking all still apply.

It unlocks exactly **five** additional abilities:

1. Dereference a raw pointer
2. Call an `unsafe` function or method (including any FFI function)
3. Access or modify a mutable `static`
4. Implement an `unsafe` trait (`Send`, `Sync`)
5. Access fields of a `union`

That's the complete list. Everything else about the language is unchanged.

What `unsafe` really means is: **"I have personally verified the invariants the compiler can't."** It's a promise to the compiler, and the compiler takes you at your word.

```rust
let mut n = 5;
let r1 = &n as *const i32;
let r2 = &mut n as *mut i32;

unsafe {
    println!("{}", *r1);      // dereferencing needs unsafe
    *r2 = 10;
}
```

Creating a raw pointer is safe. Only *dereferencing* one requires `unsafe`, because that's where it can go wrong.

## Undefined behaviour

Breaking the promise gives you **undefined behaviour** — and Rust's UB is as unforgiving as C's. Not "a crash", but "the optimiser assumed this couldn't happen and generated code accordingly."

The rules you must uphold in `unsafe`:

- No dangling or unaligned pointer dereferences
- No aliasing violations — you cannot have a `&mut T` alongside any other live reference to the same data, even created through raw pointers
- No data races
- No invalid values — a `bool` that isn't 0 or 1, an out-of-range enum discriminant, an uninitialised reference
- No breaking the invariants of safe abstractions you're building on

The aliasing rule is the one that catches experienced C programmers. Rust's optimiser relies on `&mut T` being genuinely unique far more aggressively than a C compiler relies on `restrict`.

## The safe-abstraction pattern

Idiomatic Rust doesn't spread `unsafe` around. It confines it inside a small, audited module and exposes a **safe API** whose invariants are checked at the boundary:

```rust
pub fn split_at_mut(slice: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = slice.len();
    let ptr = slice.as_mut_ptr();
    assert!(mid <= len);                      // the invariant, checked in SAFE code

    unsafe {
        (
            slice::from_raw_parts_mut(ptr, mid),
            slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}
```

Two `&mut` into one slice is something the borrow checker cannot prove is disjoint. The `assert!` establishes it, the `unsafe` block acts on it, and callers never see any of it. This exact function is in the standard library.

That's the whole model: `Vec`, `String`, `Rc`, `Mutex` and the rest are all safe abstractions over `unsafe` internals. **The point of `unsafe` isn't to write unsafe code — it's to build safe things the compiler couldn't have verified.**

By convention, every `unsafe` block carries a `// SAFETY:` comment explaining why it's sound. Clippy can enforce this (`clippy::undocumented_unsafe_blocks`).

```rust
// SAFETY: mid <= len is asserted above, so both ranges are in bounds and disjoint.
unsafe { ... }
```

## `unsafe fn`

```rust
/// # Safety
/// `ptr` must be valid, aligned, and point to `len` initialised elements.
pub unsafe fn from_parts(ptr: *const u8, len: usize) -> &'static [u8] { }
```

Marking a function `unsafe` means **the caller** must uphold preconditions the function can't check. Document them under a `# Safety` heading — that's the universal convention and rustdoc renders it.

## FFI — calling C

```rust
#[link(name = "m")]
extern "C" {
    fn sqrt(x: f64) -> f64;
    fn abs(input: i32) -> i32;
}

fn main() {
    let r = unsafe { sqrt(4.0) };
}
```

Every FFI call is `unsafe` — the compiler has no idea what C will do with the pointers you hand it.

Exposing Rust to C is the reverse:

```rust
#[no_mangle]                                   // keep the symbol name
pub extern "C" fn add(a: i32, b: i32) -> i32 { a + b }
```

### The types

```rust
use std::os::raw::{c_char, c_int, c_void};
use std::ffi::{CStr, CString};

// Rust String → C string
let c = CString::new("hello").unwrap();       // adds the NUL; errors on interior NULs
unsafe { c_function(c.as_ptr()); }

// C string → Rust
let s = unsafe { CStr::from_ptr(ptr) }.to_str().unwrap();
```

The mismatch to keep in mind: **Rust strings are UTF-8 with a length; C strings are NUL-terminated bytes.** `CString` owns and adds the NUL, `CStr` borrows. Converting back can fail on invalid UTF-8, which is why `to_str()` returns a `Result`.

`#[repr(C)]` guarantees C-compatible struct layout — Rust reorders fields for packing by default:

```rust
#[repr(C)]
struct Point { x: f64, y: f64 }
```

### Tooling

```bash
cargo add bindgen --build      # generate Rust bindings FROM C headers
cargo add cbindgen --build     # generate C headers FROM Rust
```

Nobody transcribes headers by hand. `bindgen` in a `build.rs` is the standard approach, and it's how `-sys` crates work — the convention being a `foo-sys` crate with raw bindings plus a `foo` crate with a safe wrapper over it.

**Ownership across the boundary is the hard part.** Who frees what? A pointer Rust hands to C must not be dropped while C holds it (`std::mem::forget` or `Box::into_raw`), and memory C allocated must be freed by C's `free`, not Rust's allocator.

```rust
let boxed = Box::new(data);
let ptr = Box::into_raw(boxed);        // Rust forgets it; C now owns it
// later, to reclaim:
let boxed = unsafe { Box::from_raw(ptr) };   // Rust owns it again; drops normally
```

## When `unsafe` is justified

- **FFI** — unavoidable
- **Building a data structure the borrow checker can't express** — intrusive lists, arenas, lock-free structures
- **A measured performance win** — skipping a bounds check in a proven-hot loop, after profiling
- **Hardware and embedded** — memory-mapped registers
- **Implementing `Send`/`Sync`** for a type whose safety you're guaranteeing manually

## When it isn't

- **Getting past the borrow checker.** If you're using `unsafe` because the compiler said no, you almost certainly have the bug it was describing.
- **Assumed performance.** Bounds checks are usually elided by the optimiser already. Measure first — the win is often zero.
- **Convenience.** `Rc<RefCell<T>>`, an arena, or a redesign is nearly always the better answer.

## Tools

```bash
cargo +nightly miri test        # interpreter that DETECTS undefined behaviour
cargo +nightly careful test
RUSTFLAGS="-Z sanitizer=address" cargo +nightly test
cargo geiger                    # count unsafe in your dependency tree
```

**Miri is the important one.** It interprets your program and catches UB — out-of-bounds access, use-after-free, alignment violations, data races — that normal testing sails past. If you write `unsafe`, run Miri over its tests. It's slow and it will find things.

---

## Related
- [[languages/03-rust/12-smart-pointers-and-interior-mutability|Smart Pointers]] — safe abstractions built on this
- [[languages/03-rust/13-concurrency|Concurrency]] — `Send`/`Sync` as unsafe traits
- [[languages/03-rust/18-performance-and-zero-cost|Performance]] — measure before reaching for `unsafe`
- [[languages/03-rust/README|Rust course map]]
