# Collections and Iterators

**[Intermediate]** — The standard collections, and the `Iterator` trait — the best-designed thing in the standard library and the reason Rust reads like a high-level language.

## The collections

```rust
Vec<T>            // growable array — your default
VecDeque<T>       // double-ended queue (ring buffer)
HashMap<K, V>     // hash map; K: Eq + Hash
BTreeMap<K, V>    // sorted map; K: Ord — use when you need ordered iteration or range queries
HashSet<T> / BTreeSet<T>
BinaryHeap<T>     // max-heap; wrap in Reverse for a min-heap
LinkedList<T>     // exists; you almost never want it
String            // owned UTF-8
```

```rust
let mut v = Vec::new();
let mut v = Vec::with_capacity(100);   // preallocate — same win as in Go
let v = vec![1, 2, 3];

v.push(4);
v.pop();                    // Option<T>
v.get(0);                   // Option<&T> — safe
v[0];                       // panics if out of range
v.first() / v.last();
v.iter() / v.iter_mut() / v.into_iter();
v.sort() / v.sort_by(|a,b| ...) / v.sort_by_key(|x| x.field);
v.dedup();
v.retain(|x| *x > 2);
v.extend(other);
v.contains(&x);
v.binary_search(&x);
```

```rust
let mut m = HashMap::new();
m.insert("k", 1);
m.get("k");                 // Option<&V>
m.remove("k");
m.contains_key("k");

*m.entry("k").or_insert(0) += 1;                    // the entry API — the important idiom
m.entry("k").or_insert_with(Vec::new).push(item);
m.entry("k").and_modify(|v| *v += 1).or_insert(1);
```

The **entry API** is how you do get-or-insert with a single lookup. The naive version borrows the map twice and won't compile — which is the borrow checker steering you toward the more efficient code, a recurring theme.

`HashMap` uses SipHash by default, which is DoS-resistant but not the fastest. For internal maps with trusted keys, `rustc-hash`'s `FxHashMap` is a meaningful speedup.

## The `Iterator` trait

```rust
trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
    // ...and ~70 provided methods, all built on next()
}
```

**One required method.** Implement `next`, get everything else free. This is the argument for default methods on traits, made concrete.

```rust
struct Counter { count: u32 }

impl Iterator for Counter {
    type Item = u32;
    fn next(&mut self) -> Option<u32> {
        if self.count < 5 { self.count += 1; Some(self.count) } else { None }
    }
}

Counter { count: 0 }.zip(Counter { count: 0 }.skip(1))
    .map(|(a, b)| a * b)
    .filter(|x| x % 3 == 0)
    .sum::<u32>();          // all of this, from writing next()
```

### The three ways to iterate

```rust
for x in &v      // v.iter()       → Item = &T          (borrow)
for x in &mut v  // v.iter_mut()   → Item = &mut T      (mutable borrow)
for x in v       // v.into_iter()  → Item = T           (MOVES v)
```

This distinction is [[languages/03-rust/03-ownership|ownership]] showing up in a loop, and it's the thing to be deliberate about. `into_iter()` is what you want when you're transforming a collection you no longer need — it avoids cloning every element.

## Adapters and consumers

**Adapters** are lazy and return another iterator. **Consumers** actually run it.

```rust
// Adapters — nothing happens until consumed
.map(|x| ...)          .filter(|x| ...)       .filter_map(|x| Option)
.enumerate()           .zip(other)            .chain(other)
.take(n)               .skip(n)               .take_while(|x| ...)
.skip_while(|x| ...)   .step_by(n)            .rev()
.flat_map(|x| iter)    .flatten()             .peekable()
.windows(n) .chunks(n) // slice methods
.scan(state, f)        .inspect(|x| ...)      // inspect = debug print mid-chain

// Consumers — these drive it
.collect::<Vec<_>>()   .sum()      .product()  .count()
.fold(init, f)         .reduce(f)
.for_each(|x| ...)     .find(|x| ...)          .position(|x| ...)
.any(|x| ...)          .all(|x| ...)
.min() .max() .min_by_key(f) .max_by_key(f)
.last() .nth(n)        .partition(|x| ...)
```

**Laziness matters.** This does no work:

```rust
v.iter().map(|x| expensive(x));     // warning: unused `Map` that must be used
```

And this only calls `expensive` three times, not on the whole vector:

```rust
v.iter().map(|x| expensive(x)).take(3).collect::<Vec<_>>();
```

### `collect` is unusually powerful

```rust
let v: Vec<i32>              = iter.collect();
let s: HashSet<i32>          = iter.collect();
let m: HashMap<String, i32>  = pairs.collect();     // from an iterator of tuples
let s: String                = chars.collect();

// The one worth remembering:
let r: Result<Vec<i32>, E> = strings.iter().map(|s| s.parse()).collect();
```

That last line collects `Iterator<Item = Result<T, E>>` into `Result<Vec<T>, E>` — short-circuiting on the first error. It replaces a loop with a mutable accumulator and an early return, and it's the single most useful `collect` trick. The same works for `Option`.

`collect()` needs a target type, hence the turbofish (`collect::<Vec<_>>()`) or an annotation.

## Why chains are as fast as loops

Iterator chains compile to the same machine code as a hand-written loop. Genuinely — this is the flagship example of a **zero-cost abstraction**.

The reason: every adapter is a struct with an inlinable `next()`. `v.iter().map(f).filter(g).sum()` becomes a `Sum<Filter<Map<Iter>>>`, and after inlining LLVM sees one loop body with no allocation and no indirection. It'll often vectorise it too.

So there's no readability-vs-performance trade here. Write the chain.

The exception is `collect()` into a new collection, which allocates. If you're chaining several `collect()`s, you're allocating several times — keep it lazy until the end.

## Common patterns

```rust
// index with the value
for (i, item) in v.iter().enumerate() { }

// filter and transform in one pass
let nums: Vec<i32> = strs.iter().filter_map(|s| s.parse().ok()).collect();

// group into a map
let mut groups: HashMap<char, Vec<&str>> = HashMap::new();
for w in words { groups.entry(w.chars().next().unwrap()).or_default().push(w); }

// sum a field
let total: f64 = orders.iter().map(|o| o.amount).sum();

// max by a computed key
let longest = words.iter().max_by_key(|w| w.len());

// flatten nested
let all: Vec<i32> = nested.into_iter().flatten().collect();

// dedup an unsorted collection, preserving nothing
let unique: HashSet<_> = v.into_iter().collect();

// windows over pairs
for pair in v.windows(2) { println!("{} {}", pair[0], pair[1]); }
```

`itertools` is the near-standard crate that fills the gaps — `group_by`, `sorted`, `unique`, `chunks`, `cartesian_product`, `join`.

## `Iterator` vs `IntoIterator`

```rust
trait IntoIterator { type Item; type IntoIter: Iterator; fn into_iter(self) -> Self::IntoIter; }
```

`for x in collection` desugars to `IntoIterator::into_iter(collection)`. `Vec<T>` implements it three times — for `Vec<T>`, `&Vec<T>` and `&mut Vec<T>` — which is exactly what gives you the three iteration modes above.

Take `impl IntoIterator<Item = T>` in a function parameter and callers can pass a `Vec`, an array, or any iterator:

```rust
fn process(items: impl IntoIterator<Item = String>) { }
```

---

## Related
- [[languages/03-rust/09-traits|Traits]] — default methods, which `Iterator` exploits fully
- [[languages/03-rust/18-performance-and-zero-cost|Performance and Zero-Cost Abstractions]] — why the chains are free
- [[languages/03-rust/03-ownership|Ownership]] — `iter` vs `into_iter`
- [[foundations/dsa/04-data-structures/03-hash-maps|Hash Maps]] and [[foundations/dsa/04-data-structures/08-heaps|Heaps]] — what is underneath these
- [[languages/03-rust/README|Rust course map]]
