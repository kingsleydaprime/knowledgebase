---
id: 1cf27b1c-faee-4bc1-8894-a95b9611263a
---

# Programming Paradigms

A **paradigm** is a style of organising a program — a set of ideas about what the building blocks are and how they fit together. The words get used loosely and territorially. They're less mystical than they sound, and there are really only two roots.

## The root distinction: how vs what
<!-- bite: 7a3238e8-cab5-457b-8f31-0efa913bdb7a -->

**Imperative** — you write *how*. Explicit steps, in order, changing state as they go.

```python
total = 0
for item in cart:
    if item.in_stock:
        total = total + item.price
```

**Declarative** — you write *what you want*, and something else decides how.

```python
total = sum(item.price for item in cart if item.in_stock)
```

```sql
SELECT SUM(price) FROM cart WHERE in_stock = true;
```

Same result. The first specifies the loop, the counter and the mutation. The second specifies the outcome.

**The trade:** declarative is shorter, harder to get subtly wrong, and easier to optimise automatically — an SQL engine rewrites your query into a plan you never see, and a good one beats what you'd have written. What you give up is control: when it's slow, the *how* is somebody else's, and you need to understand the machinery anyway to fix it → [[databases/07-join-algorithms-and-the-optimiser/index|the query optimiser]].

You already write declarative code constantly. HTML, CSS, SQL, [[devops/09-infrastructure-as-code/01-provisioning-and-terraform|Terraform]], and every CI YAML file are declarative. So is React's render model.

## Expressions and statements
<!-- bite: a26fa584-32d6-493e-856c-ec723222789a -->

Worth naming here because it's the mechanical version of the same split, and it explains a lot of syntax you'll otherwise find arbitrary.

**An expression produces a value.** `2 + 3`, `max(a, b)`, `user.name`.
**A statement does something.** An `if` block, a `for` loop, an assignment.

Imperative languages are built from statements; declarative and functional ones push everything toward expressions. That's why in Rust an `if` **returns a value**:

```rust
let grade = if score >= 90 { "A" } else { "B" };     // if is an expression
```

and why Python needs a separate conditional-expression form (`"A" if score >= 90 else "B"`) — its `if` is a statement and produces nothing.

**"Everything is an expression" is a design goal**, not a quirk: expressions compose, statements don't. You can nest an expression inside another anywhere; a statement has to go on its own line and communicate by side effect. → [[compilers/03-parsing|parsing]].

## The four styles you'll actually meet
<!-- bite: 388dfe20-bbcf-4ba2-a80f-44f2e4156b59 -->

### Procedural
Imperative code organised into procedures (functions) that operate on data passed to them. Data and behaviour are **separate**. C is the canonical example, and most scripts you write are this whether or not you call it that.

**Good for:** scripts, systems code, anything that's fundamentally a sequence of transformations.
**Breaks down when:** state and the rules governing it drift apart — the problem [[programming-fundamentals/13-objects-and-classes|note 13]] opens with.

### Object-oriented
Data and behaviour **bundled** into objects. Organised around encapsulation, inheritance and polymorphism. Java, C#, Python, Ruby, C++.

**Good for:** domains with clear entities that carry invariants; large codebases where a boundary per concept keeps people out of each other's way; anything that benefits from swapping implementations behind a shared interface.
**Breaks down when:** it's forced onto work that's really a pipeline, or hierarchies get deep. → [[programming-fundamentals/13-objects-and-classes|note 13]]

### Functional
Programs built from **pure functions** — same input, same output, no side effects — composed together, with data treated as **immutable**. Haskell is the strict case; Lisp, Elixir, F#, Scala are practical ones.

The core ideas, and all of them have leaked into mainstream languages:

- **Immutability** — you don't change data, you produce new data. No "who modified this?" bugs
- **Pure functions** — trivially testable, safe to parallelise, safe to cache
- **Functions as values** — pass them, return them, store them (`map`, `filter`, `reduce`)
- **Composition** — build big transformations from small ones

```python
# functional in style, in a language that isn't
in_stock = [i for i in cart if i.in_stock]
total = sum(i.price for i in in_stock)
```

**Why it's ascendant:** immutability and purity are the most effective defence against concurrency bugs there is, because a value nobody can change needs no lock. As machines went multi-core, that stopped being an aesthetic preference. → [[os/06-concurrency-primitives|concurrency]].

**Breaks down when:** the problem is genuinely stateful (a game loop, a device driver) and the contortions to avoid state cost more than the state would have.

### Event-driven
Not usually listed beside the others, and you'll spend more time in it than in most of them: code registers **handlers** and a loop dispatches to them when things happen. Every UI, every server, every browser page.

The inversion is the point — **you don't call the framework, it calls you** — and it's why callback-heavy code is hard to follow: control flow lives in a dispatcher you didn't write. → [[backend/01-foundations/04-runtime-and-concurrency-models/index|runtime and concurrency models]].

## Almost everything is multi-paradigm now
<!-- bite: 8b68b4c9-9e4f-4e95-b918-1b70847a8d68 -->

The tribal era is over. Python has classes, first-class functions, comprehensions and decorators. JavaScript is all four at once. Java added lambdas and records; C# added pattern matching and immutability; Rust has traits, closures, iterators and no inheritance at all.

**So the useful question isn't "which paradigm is best" — it's "which fits this piece of code".** In one program:

- The **domain model** with its invariants → objects
- The **data transformations** → functional: map, filter, reduce, immutable values
- The **glue and the scripts** → procedural
- The **I/O boundary** → event-driven, because the runtime decided

**And one heuristic that's worth more than the taxonomy:** *push the pure logic apart from the effects.* Keep the calculating, deciding and transforming in pure functions, and confine the mutation, I/O and state changes to a thin shell around them. The pure part is testable, movable and reusable; the shell is small enough to reason about. Every paradigm above agrees with this, which is a decent sign it's the real lesson.

## Check your understanding
<!-- bite: f4631587-ed70-4644-ba5c-14a5ed4280d2 -->

Try each one before you open the answer.

1. <!-- q: mcq id="ae1e7205" -->
   Which of these is declarative?

   - [ ] A `for` loop that adds each price to a running total
   - [x] `SELECT SUM(price) FROM cart WHERE in_stock = true;`
   - [ ] A `while` loop that reads a file line by line
   - [ ] Incrementing a counter inside an `if`

   <details><summary>Answer</summary>

   The SQL query. It says what you want and leaves how to the database engine. The others spell out the steps, which is imperative.

   </details>

2. <!-- q: mcq id="ed91198e" -->
   Which of these are expressions, meaning they produce a value? Choose all that apply.

   - [x] `2 + 3`
   - [x] `max(a, b)`
   - [ ] A Python `for` loop
   - [x] `"A" if score >= 90 else "B"` in Python

   <details><summary>Answer</summary>

   `2 + 3`, `max(a, b)` and the conditional expression all produce a value. A `for` loop is a statement: it does something and gives nothing back.

   </details>

3. <!-- q: gap id="008e3f30" answers="immutable|immutability;pure" -->
   Functional programming builds programs from data that is ___, meaning it is never changed in place, and from ___ functions, which give the same output for the same input and have no side effects.

   <details><summary>Answer</summary>

   Immutable, then pure. Together they are the strongest defence against concurrency bugs, because a value nobody can change needs no lock.

   </details>

4. <!-- q: mcq id="2ba7b6bb" -->
   A browser button runs your `onClick` handler when someone clicks it. You never call `onClick` yourself. Which paradigm is this?

   - [ ] Procedural
   - [ ] Functional
   - [x] Event-driven
   - [ ] Declarative

   <details><summary>Answer</summary>

   Event-driven. You register handlers and a loop calls them when things happen: you don't call the framework, it calls you.

   </details>

5. <!-- q: open id="3ae92c6d" -->
   What does "push the pure logic apart from the effects" mean, and why does it help?

   <details><summary>Answer</summary>

   Keep the calculating, deciding and transforming in pure functions, and confine the mutation, input/output and state changes to a thin outer layer. The pure part is easy to test, move and reuse, and the outer layer is small enough to reason about. Every paradigm agrees with this.

   </details>

## Related
<!-- bite: cf686d47-771e-4d78-a8d4-5a6bd6ccdb69 -->
- [[programming-fundamentals/13-objects-and-classes|objects and classes]] — the OO paradigm in depth
- [[programming-fundamentals/08-functions|functions]] — purity, introduced
- [[programming-language-theory/index|PL theory]] — the formal treatment, much later
- [[languages/03-rust/index|Rust]] · [[languages/02-go/index|Go]] — two modern languages that deliberately dropped inheritance
- [[concepts/01-best-practices/index|best practices]] — the habits these produce

## About this lesson
<!-- bite: 1b3f71ab-3637-4757-82b8-339b37eb6e54 -->

**Level:** Beginner → Intermediate. **Covers:** Imperative, declarative, procedural, object-oriented, functional — what the words mean, and why almost every language you'll use is several of them at once.

*Source: [reference] — written Aug 2026 alongside note 13, prompted by `sources/100 CS concepts explained.md`.*
