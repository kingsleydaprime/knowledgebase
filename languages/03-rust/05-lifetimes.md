---
id: 8196a30d-b104-428c-bdd2-27ff8e44e324
---

# Lifetimes

A lifetime is the stretch of time during which a reference is safe to use. A bus ticket is a good picture: it is only valid until the end of the trip, and using it after that is a mistake. Rust tracks lifetimes so that a reference can never outlive the value it points to.

## What they actually are
<!-- bite: 68c62797-8d54-4dfa-bd5e-a9bf69fb51c6 -->

A lifetime is **the scope for which a reference is valid**. Every reference has one; the compiler infers it almost always. Annotations appear only when it can't.

The crucial thing to get straight, because it's the usual misconception:

> **Lifetime annotations do not change how long anything lives.** They *describe* a relationship between the lifetimes of existing values, so the compiler can check it.

You're not allocating or extending anything. You're telling the compiler "the reference coming out is valid as long as the one going in", and it verifies you.

## Why they're needed
<!-- bite: 3ff7d04c-1fb2-466b-8d96-412fc064b469 -->

```rust
fn longest(x: &str, y: &str) -> &str {      // ERROR: missing lifetime specifier
    if x.len() > y.len() { x } else { y }
}
```

The compiler cannot tell whether the return value borrows from `x` or from `y` — it depends on runtime data. Without knowing, it can't check that the result doesn't outlive whichever it came from.

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

Read `'a` as a label: "these two inputs and the output all share a lifetime." Concretely, `'a` resolves to the **shorter** of the two inputs' lifetimes, and the compiler checks the caller against that:

```rust
let s1 = String::from("long string");
let result;
{
    let s2 = String::from("short");
    result = longest(&s1, &s2);      // 'a is the shorter one — s2's scope
}
println!("{}", result);              // ERROR: s2 doesn't live long enough
```

That error is the whole feature working. In C++ this compiles and reads freed memory.

Note that a lifetime only needs to appear where it constrains something:

```rust
fn first<'a>(x: &'a str, _y: &str) -> &'a str { x }   // _y is unrelated; give it its own
```

## Elision — why you rarely write them
<!-- bite: 59b80112-8077-4349-91a0-de057de39002 -->

Three rules let the compiler infer lifetimes in the common cases. If they fully determine the answer, you write nothing:

1. **Each elided input lifetime gets its own parameter.**
2. **If there is exactly one input lifetime, it's assigned to all output lifetimes.**
3. **If one of the inputs is `&self` or `&mut self`, its lifetime is assigned to all output lifetimes.**

```rust
fn first_word(s: &str) -> &str { }        // rule 2 — unambiguous, no annotation needed

impl Parser {
    fn name(&self) -> &str { &self.name }  // rule 3 — output borrows from self
}
```

Rule 3 is why methods almost never need annotations, and it's why `longest` above *does* — two inputs, no `self`, so rules 1 and 2 leave the output ambiguous.

## Lifetimes in structs
<!-- bite: d3eb4351-1736-4ce9-b6f1-21a25c13bdc9 -->

A struct holding a reference must declare that it can't outlive what it borrows:

```rust
struct Parser<'a> {
    input: &'a str,
    pos: usize,
}

impl<'a> Parser<'a> {
    fn new(input: &'a str) -> Self { Parser { input, pos: 0 } }

    fn rest(&self) -> &str { &self.input[self.pos..] }   // rule 3 applies
}
```

`Parser<'a>` means "a Parser that borrows something living at least `'a`". This is the zero-copy parsing pattern — the parser holds slices into the original buffer rather than allocating `String`s, which is a real performance win and a place Rust shines.

**When a struct starts collecting lifetime parameters, consider owning the data instead.** `String` rather than `&'a str` costs an allocation and removes the constraint. Fighting three lifetime parameters to avoid one `clone()` in a config struct is a bad trade — measure before assuming it matters.

## `'static`
<!-- bite: 57afb1ec-c528-4e21-9d3a-129d091552ce -->

```rust
let s: &'static str = "I live for the whole program";
```

`'static` means the reference is valid for the program's entire duration. String literals are `'static` because they're baked into the binary.

Two distinct meanings that get conflated:

- **`&'static T`** — a reference valid forever
- **`T: 'static`** — a *type* that contains no non-`'static` references, i.e. it either owns all its data or only holds `'static` references. `String` is `T: 'static`. `&'a str` is not.

The second is what you see in thread-spawn and async bounds — `thread::spawn` requires `F: 'static` because the closure might outlive the caller. It does **not** mean "lives forever"; it means "doesn't borrow anything short-lived".

When the compiler suggests adding a `'static` bound, that's usually the wrong fix. It's telling you something borrowed is escaping a scope, and the right answer is normally to own it — `to_owned()`, `Arc`, or restructuring — not to promise it lives forever.

## Bounds and subtyping
<!-- bite: 8486d15c-5580-4ed2-8183-4106ce437b67 -->

```rust
struct Wrapper<'a, 'b: 'a> {    // 'b outlives 'a
    long: &'b str,
    short: &'a str,
}
```

`'b: 'a` reads "'b outlives 'a". You'll meet this rarely, mostly in library code.

Lifetimes are **covariant** in most positions, meaning a longer lifetime can be used where a shorter one is expected — which is why passing a `'static` reference to a function wanting `&'a str` just works.

## Higher-ranked bounds
<!-- bite: 3c2952c7-72bd-439d-9cb8-4d4408e1ccb4 -->

```rust
fn apply<F>(f: F) where F: for<'a> Fn(&'a str) -> &'a str { }
```

`for<'a>` means "for *any* lifetime `'a`", not one specific one — the function must work for all of them. It's usually inferred; you'll only write it explicitly for closures stored in structs. Filed here so it isn't alarming when you see it.

## Practical advice
<!-- bite: 157b8c0d-2892-4d0b-9a8c-ea2984300f34 -->

1. **Don't add lifetimes until the compiler asks.** Elision covers most code.
2. **When you're stuck, try owning the data.** `String` over `&'a str`, `Vec<T>` over `&'a [T]`. Correct first, optimise later.
3. **Read the error message.** "borrowed value does not live long enough" names the exact scope that ends too early.
4. **`'static` in an error is a hint, not usually the fix.** It means something is escaping.
5. **Multiple lifetime parameters are a smell** in application code. Common and correct in libraries; usually over-engineering elsewhere.

Lifetimes are the last big concept and they're less used day to day than ownership and borrowing. Most application Rust has almost no explicit lifetime annotations at all.

---

## Related
<!-- bite: 10525222-e170-4794-b443-7f06a43668ae -->
- [[languages/03-rust/04-borrowing-and-references|Borrowing and References]] — what lifetimes describe
- [[languages/03-rust/10-generics-and-trait-bounds|Generics and Trait Bounds]] — lifetimes are a kind of generic parameter
- [[languages/03-rust/14-async-and-tokio|Async and Tokio]] — where `'static` bounds bite hardest
- [[languages/03-rust/index|Rust course map]]

## About this lesson
<!-- bite: 8b7a0043-7c29-45a8-8cfc-9b918c57f394 -->

**Level:** Intermediate. **Covers:** The scariest-looking syntax in Rust, which turns out to be describing something you already understand.
