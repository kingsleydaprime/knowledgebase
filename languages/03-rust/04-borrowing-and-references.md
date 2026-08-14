# Borrowing and References

**[Beginner → Intermediate]** — Using a value without taking it, the one rule that governs everything, and how to actually get past the borrow checker.

## References

```rust
fn calculate_length(s: &String) -> usize {
    s.len()
}                        // s goes out of scope, but it doesn't own the data — nothing is dropped

let s1 = String::from("hello");
let len = calculate_length(&s1);
println!("{} is {} long", s1, len);   // s1 still usable
```

`&s1` creates a **reference** — a pointer that borrows the value without owning it. This is the fix for the take-and-give-back ugliness from [[languages/03-rust/03-ownership|Ownership]].

References are immutable by default:

```rust
fn change(s: &String) { s.push_str(" world"); }   // ERROR: cannot borrow as mutable

fn change(s: &mut String) { s.push_str(" world"); }
let mut s = String::from("hello");
change(&mut s);
```

Note `s` itself must be `mut` for you to take a `&mut` to it.

## The borrowing rule

> **At any given time you can have either one mutable reference, or any number of immutable references — never both.**

```rust
let mut s = String::from("hello");

let r1 = &s;        // fine
let r2 = &s;        // fine — many readers
let r3 = &mut s;    // ERROR: cannot borrow as mutable, already borrowed as immutable
```

```rust
let r1 = &mut s;
let r2 = &mut s;    // ERROR: cannot borrow as mutable more than once
```

This is **readers-writer locking, enforced at compile time with zero runtime cost.** It's exactly the discipline you'd apply manually with a `RwLock` — except the compiler proves you followed it and there's no lock to acquire.

The rule prevents **data races** by construction. A data race needs two accesses, one of them a write, unsynchronised. Rust makes that unrepresentable: if there's a writer, there are no other references at all.

It also prevents **iterator invalidation**, which is the same bug in single-threaded clothing:

```rust
let mut v = vec![1, 2, 3];
let first = &v[0];
v.push(4);                  // ERROR: v is borrowed
println!("{}", first);      // ← in C++ this is a dangling pointer, because push may reallocate
```

## Non-lexical lifetimes

A borrow ends at its **last use**, not at the end of the block. This is what makes the rule liveable:

```rust
let mut s = String::from("hello");

let r1 = &s;
let r2 = &s;
println!("{} {}", r1, r2);   // last use of r1 and r2 — their borrows END HERE

let r3 = &mut s;             // fine now
println!("{}", r3);
```

If you read Rust material from before 2018 (pre-NLL), it will describe this as an error. It isn't any more.

## No dangling references

```rust
fn dangle() -> &String {
    let s = String::from("hello");
    &s              // ERROR: missing lifetime specifier / s is dropped here
}
```

The compiler refuses to return a reference to something that's about to be freed. In C this compiles and gives you a use-after-free. The fix is to return the owned value: `fn no_dangle() -> String { s }`.

## Slices

A slice is a borrowed view into a contiguous sequence — a pointer plus a length, owning nothing:

```rust
let s = String::from("hello world");
let hello: &str = &s[0..5];
let world: &str = &s[6..11];

let v = vec![1, 2, 3, 4, 5];
let part: &[i32] = &v[1..3];
```

`&str` **is** a string slice — which is why string literals have that type. They're slices into the binary's static data.

Slices are why this is the right signature:

```rust
fn first_word(s: &str) -> &str { }     // accepts &String, &str, and literals
fn sum(nums: &[i32]) -> i32 { }        // accepts &Vec<i32> and &[i32; 5]
```

Taking `&str` and `&[T]` rather than `&String` and `&Vec<T>` makes a function strictly more general, at no cost. This is standard advice and you should follow it.

Because a slice borrows, it keeps the borrow rule alive across the collection:

```rust
let mut s = String::from("hello world");
let word = first_word(&s);
s.clear();                  // ERROR: cannot borrow as mutable, `word` still borrows it
println!("{}", word);
```

Which is precisely the bug this prevents — `word` would otherwise point into a cleared buffer.

## Fighting the borrow checker — the four patterns that unstick you

Everyone gets stuck. Almost always it's one of these.

**1. Shorten the borrow.** The commonest fix. Extract the value you need so the borrow ends:

```rust
// stuck
if let Some(v) = map.get("k") { map.insert("k2", v + 1); }   // map borrowed, then mutated

// fixed — the borrow ends at the semicolon
let v = map.get("k").copied();
if let Some(v) = v { map.insert("k2", v + 1); }
```

**2. Restructure to avoid simultaneous borrows.** Compute first, mutate second:

```rust
let to_remove: Vec<_> = items.iter().filter(|i| i.stale).map(|i| i.id).collect();
for id in to_remove { items.retain(|i| i.id != id); }
```

**3. Split the borrow.** The compiler tracks fields separately, so borrowing two different fields is allowed — but it can't see through a method call:

```rust
let a = &mut s.field_one;
let b = &s.field_two;         // fine — different fields

// but s.get_one() and s.get_two() both borrow ALL of s
let (a, b) = s.split_at_mut(i);   // slices provide explicit splitting methods
```

**4. Use interior mutability — last, not first.** `RefCell` moves the check to runtime; `Rc`/`Arc` allow multiple owners. These are real tools, but reaching for them early usually means you skipped a simpler restructuring. → [[languages/03-rust/12-smart-pointers-and-interior-mutability|Smart Pointers]]

> The honest framing: **the borrow checker is usually right.** When it rejects your code, the design generally has aliasing that would be a latent bug elsewhere. When it's genuinely wrong, it's because the analysis is conservative — and those cases are rarer than your frustration suggests. Clone your way past it while learning; come back and remove the clones later.

---

## Related
- [[languages/03-rust/05-lifetimes|Lifetimes]] — the annotations that appear when borrows cross function boundaries
- [[languages/03-rust/03-ownership|Ownership]] — the rules being relaxed here
- [[languages/03-rust/12-smart-pointers-and-interior-mutability|Smart Pointers]] — escape hatches, used deliberately
- [[languages/03-rust/13-concurrency|Concurrency]] — the same rule preventing data races
- [[languages/03-rust/README|Rust course map]]
