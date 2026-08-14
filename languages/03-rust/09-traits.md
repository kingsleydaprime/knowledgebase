# Traits

**[Intermediate]** — Shared behaviour without inheritance. Rust's answer to interfaces, and it does more than they do.

## Defining and implementing

```rust
trait Summary {
    fn summarize(&self) -> String;                    // required

    fn preview(&self) -> String {                     // default implementation
        format!("{}...", &self.summarize()[..20])
    }
}

struct Article { title: String, body: String }

impl Summary for Article {
    fn summarize(&self) -> String { format!("{}: {}", self.title, self.body) }
    // preview() comes free
}
```

Unlike [[languages/02-go/04-methods-and-interfaces|Go's implicit satisfaction]], implementation is **explicit** — you write `impl Trait for Type`. That's a deliberate difference: Go optimises for retrofitting interfaces onto existing types, Rust optimises for knowing exactly which traits a type promises.

Default methods are why traits do more than Java interfaces did pre-8: `Iterator` requires one method (`next`) and gives you seventy for free.

## The orphan rule

> You can implement a trait for a type only if **you own the trait or you own the type.**

You can't `impl Display for Vec<T>` — both belong to the standard library. Without this rule two crates could provide conflicting impls and the compiler couldn't choose.

The workaround is the **newtype** pattern:

```rust
struct Wrapper(Vec<String>);

impl fmt::Display for Wrapper {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "[{}]", self.0.join(", "))
    }
}
```

Zero runtime cost — it compiles to the inner type — and it's used constantly in real code.

## The derivable traits

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Default)]
struct Point { x: i32, y: i32 }
```

| Trait | Gives you |
|---|---|
| `Debug` | `{:?}` formatting — derive it on everything |
| `Clone` | explicit `.clone()` |
| `Copy` | implicit copy instead of move; requires `Clone` |
| `PartialEq` / `Eq` | `==`. `Eq` also asserts reflexivity — floats are `PartialEq` only, because `NaN != NaN` |
| `PartialOrd` / `Ord` | `<`, sorting |
| `Hash` | usable as a `HashMap` key |
| `Default` | `Type::default()` |

**Derive `Debug` on every type you write.** It costs nothing and its absence is infuriating when you need it at 2am.

## Traits worth knowing

```rust
Display          // user-facing {} — implement by hand, never derived
Debug            // developer-facing {:?}
From<T> / Into<T>  // conversion; implement From, get Into free
TryFrom / TryInto  // fallible conversion
Iterator         // → 11-collections-and-iterators
IntoIterator     // what `for` loops desugar to
Deref            // smart-pointer transparency; String derefs to &str
Drop             // destructor
Default
AsRef<T>         // cheap reference conversion — the flexible-parameter trick
Send / Sync      // thread safety marker traits → 13-concurrency
Error            // → 08-error-handling-in-practice
Add, Sub, Mul... // operator overloading
```

**Implement `From`, never `Into`.** The blanket impl `impl<T, U: From<T>> Into<U> for T` gives you `Into` automatically, and `From` is the more useful direction.

`AsRef` enables the flexible-argument pattern the standard library uses everywhere:

```rust
fn open<P: AsRef<Path>>(path: P)    // accepts &str, String, PathBuf, &Path
```

## Static vs dynamic dispatch

The distinction that matters for performance and for what compiles.

**Static dispatch** — `impl Trait` or a generic. Monomorphised: the compiler stamps out a separate copy per concrete type, then inlines. Zero cost, bigger binary, slower compile.

```rust
fn notify(item: &impl Summary) { }              // sugar for the generic form
fn notify<T: Summary>(item: &T) { }             // identical
```

**Dynamic dispatch** — `dyn Trait`. One copy, vtable lookup at runtime, exactly like a Java interface call.

```rust
fn notify(item: &dyn Summary) { }
let items: Vec<Box<dyn Summary>> = vec![Box::new(article), Box::new(tweet)];
```

**Use `dyn` when you need a heterogeneous collection** — that `Vec` above can't be generic, because a `Vec<T>` holds one type. That's the main reason to reach for it. Otherwise prefer static dispatch.

The cost of `dyn` is a pointer indirection and no inlining. It's small; measure before contorting your design to avoid it.

### Object safety

Not every trait can be a `dyn Trait`. Roughly, a trait is object-safe if no method returns `Self` and no method has generic type parameters — because the vtable would need to know the concrete type.

```rust
trait Bad { fn clone_me(&self) -> Self; }       // NOT object-safe
trait Bad2 { fn generic<T>(&self, t: T); }      // NOT object-safe
```

"The trait cannot be made into an object" is that error, and the usual fix is returning `Box<dyn Trait>` instead of `Self`.

## Associated types

```rust
trait Container {
    type Item;                                  // associated TYPE
    fn get(&self, i: usize) -> Option<&Self::Item>;
}

impl Container for MyVec {
    type Item = String;
    fn get(&self, i: usize) -> Option<&String> { }
}
```

Versus a generic parameter:

```rust
trait Container<T> { fn get(&self, i: usize) -> Option<&T>; }
```

**Associated type = one impl per type.** `MyVec` is a container of exactly one thing. **Generic parameter = many impls per type.** `MyVec` could implement `Container<String>` and `Container<i32>`.

`Iterator` uses an associated type because a given iterator yields one type. `From<T>` uses a generic parameter because a type can convert from many things. Choosing correctly is most of designing a trait.

## Supertraits and blanket impls

```rust
trait Loud: Summary {                    // requires Summary
    fn shout(&self) -> String { self.summarize().to_uppercase() }
}
```

```rust
impl<T: Display> MyTrait for T {         // blanket impl — every Display type gets MyTrait
    fn describe(&self) -> String { format!("{self}") }
}
```

Blanket impls are how `ToString` exists for every `Display` type, and how `Into` exists for every `From`. They're powerful and they interact with the orphan rule, so use them sparingly outside libraries.

## Traits vs inheritance

There is **no inheritance** in Rust. No base classes, no `extends`, no overriding a parent's method.

What you get instead:

- **Shared behaviour** → traits with default methods
- **Shared data** → composition; put the common struct in a field
- **Polymorphism** → generics (static) or `dyn Trait` (dynamic)

This means no fragile base class problem, no diamond problem, and no "where is this method actually defined" archaeology. It also means genuinely deep hierarchies are awkward — which is mostly a feature, since [[concepts/03-design-patterns/README|composition over inheritance]] is the advice everywhere anyway. Rust just removed the option.

---

## Related
- [[languages/03-rust/10-generics-and-trait-bounds|Generics and Trait Bounds]] — constraining generics with traits
- [[languages/03-rust/11-collections-and-iterators|Collections and Iterators]] — `Iterator`, the best trait in the library
- [[languages/02-go/04-methods-and-interfaces|Go: Interfaces]] — implicit satisfaction, for contrast
- [[languages/01-java/01-language/02-oop|Java: OOP]] — the inheritance model Rust rejected
- [[languages/03-rust/README|Rust course map]]
