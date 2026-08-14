# Exceptions and Error Handling

**[Intermediate → Advanced]** — Exceptions, the safety guarantees that make them workable, and why a large slice of the C++ industry disables them entirely.

## Exceptions

```cpp
#include <stdexcept>

double divide(double a, double b) {
    if (b == 0) throw std::invalid_argument("division by zero");
    return a / b;
}

try {
    double r = divide(1, 0);
} catch (const std::invalid_argument &e) {      // catch by CONST REFERENCE
    std::cerr << e.what() << '\n';
} catch (const std::exception &e) {              // base class — catches most things
    std::cerr << "error: " << e.what() << '\n';
} catch (...) {                                   // everything, including non-std types
    std::cerr << "unknown\n";
}
```

**Catch by `const&`.** Catching by value slices ([[languages/05-cpp/06-inheritance-and-virtual-dispatch|object slicing]]) — you lose the derived type and the polymorphic `what()`.

Order matters: catch handlers are tried **top to bottom, first match wins**, so derived types must precede base types.

The standard hierarchy:

```
std::exception
├── std::logic_error         — a bug: preconditions violated
│   ├── invalid_argument
│   ├── domain_error
│   ├── length_error
│   └── out_of_range         — thrown by .at()
└── std::runtime_error       — an environmental failure
    ├── range_error
    ├── overflow_error
    └── system_error         — wraps errno / OS errors
std::bad_alloc               — allocation failed
std::bad_cast                — a failed dynamic_cast to a reference
```

**Throw by value, catch by reference.** `throw new MyError()` is a Java habit and leaks in C++.

## RAII is what makes exceptions viable

```cpp
void process() {
    auto conn = std::make_unique<Connection>();
    std::lock_guard lock(mu);
    auto data = load();               // if this throws...

    // ...the stack unwinds, and BOTH destructors run. Lock released, connection closed.
}
```

**Stack unwinding** destroys every fully-constructed local object between the throw and the catch, in reverse order.

This is the crucial coupling: [[languages/05-cpp/03-classes-and-raii|RAII]] and exceptions are the same design. Exceptions create invisible exit paths from every function; RAII makes those paths safe automatically. Without RAII, exception-safe C++ would require `try/catch` around every acquisition — which is exactly the position Java is in with `try/finally`, and why it needed `try-with-resources`.

Conversely: **any code holding a raw resource across a call that can throw is a leak.**

```cpp
void bad() {
    Widget *w = new Widget();
    do_something();                    // throws → w leaked
    delete w;
}
```

## The three exception safety guarantees

The vocabulary for documenting what a function promises if it throws:

**No-throw** — it never throws. Destructors, `swap`, and move operations should be here.

```cpp
void swap(Widget &a, Widget &b) noexcept;
```

**Strong** — if it throws, the program state is **unchanged**. Commit-or-rollback. This is what `vector::push_back` provides: if reallocation throws, the vector is exactly as before.

The usual technique is to do all the failable work into a temporary, then swap:

```cpp
void Widget::update(const Data &d) {
    auto tmp = expensive_parse(d);     // may throw — nothing changed yet
    data_ = std::move(tmp);            // noexcept move → cannot fail
}
```

**Basic** — if it throws, no leaks and all invariants hold, but the state may have changed. The minimum any function must offer.

> **Every function should provide at least the basic guarantee. Aim for strong where it's cheap. Destructors and moves must be no-throw.**

## `noexcept`

```cpp
void f() noexcept;                     // promises not to throw
```

If a `noexcept` function throws, `std::terminate` is called immediately — no unwinding, no catching.

It's a real optimisation hint: the compiler can omit unwinding tables. But its most important effect is on containers:

**`std::vector` only uses your move constructor during reallocation if it's `noexcept`** — otherwise it copies, to preserve its strong guarantee. A move constructor without `noexcept` silently costs you everything you wrote it for. → [[languages/05-cpp/04-copy-move-and-the-rule-of-five|Copy, Move and the Rule of Five]]

```cpp
Widget(Widget&&) noexcept;
Widget& operator=(Widget&&) noexcept;
void swap(Widget&, Widget&) noexcept;
~Widget();                             // implicitly noexcept
```

**Destructors are implicitly `noexcept`.** Throwing from one during unwinding calls `std::terminate` — because two exceptions in flight is unresolvable. If cleanup can fail, offer an explicit `close()` that reports, and swallow in the destructor.

## Why exceptions are controversial

A large fraction of the C++ world compiles with `-fno-exceptions`: most game engines, much embedded and safety-critical code, LLVM, and parts of Google's codebase.

**The arguments against:**

- **Invisible control flow.** Any function without `noexcept` might throw, and nothing in the signature says so. You cannot see the exit paths by reading.
- **Binary size.** Unwinding tables cost — a real problem on embedded targets.
- **Unpredictable latency.** Throwing is slow and its cost isn't bounded, which is disqualifying for hard real-time.
- **They're hard to use correctly.** Writing genuinely strongly-exception-safe code is difficult, and most code silently provides only the basic guarantee.
- **`new` can throw `bad_alloc`**, so essentially everything can throw.

**The arguments for:**

- **Zero cost on the happy path.** The "table-based" implementation adds no instructions when nothing throws — unlike checking a return code at every call.
- **Errors can't be ignored.** An unhandled exception terminates; an ignored return code does nothing.
- **They work in constructors**, which have no return value. This is the strongest argument — without exceptions, a constructor cannot report failure, so you need two-phase init (`Widget w; if (!w.init()) ...`), which breaks RAII.
- **They don't clutter the happy path** with error propagation.

## The alternatives

**Error codes** — C style, still common:

```cpp
enum class Error { Ok, NotFound, Invalid };
Error find(int id, Widget &out);
```

**`std::optional`** for "might not be there" without a reason:

```cpp
std::optional<Widget> find(int id);
```

**`std::expected<T, E>`** (C++23) — a `Result` type, and the direction the language is moving:

```cpp
#include <expected>

std::expected<Config, ParseError> parse(std::string_view s) {
    if (bad) return std::unexpected(ParseError::Syntax);
    return Config{...};
}

auto cfg = parse(input);
if (!cfg) { log(cfg.error()); return; }
cfg->apply();

auto v = parse(input)
    .transform([](Config c) { return c.port; })     // map
    .value_or(8080);
```

This is [[languages/03-rust/07-option-and-result|Rust's `Result<T, E>`]], arriving in C++ in 2023. It gives you visible-in-the-signature errors with no exception machinery — and no `?` operator, so propagation is manual.

`tl::expected` and `absl::StatusOr` are the pre-C++23 versions, and widely used.

## Picking one

The pragmatic position most codebases land on:

| Use | For |
|---|---|
| **Exceptions** | genuinely exceptional failures; constructor failure; deep call stacks where every frame would otherwise propagate manually |
| **`std::optional`** | "not found", where there's nothing to explain |
| **`std::expected`** | expected failures the caller must handle — parsing, I/O, validation |
| **Error codes** | ABI boundaries, C interop, `-fno-exceptions` codebases |
| **`assert` / terminate** | programmer errors, not runtime conditions |

**The one rule everyone agrees on: pick one and be consistent.** Mixing exceptions and error codes in one codebase is worse than either alone, because callers can't tell which to check.

If you're on `-fno-exceptions`, know what you lose: `new` becomes a null return (`new (std::nothrow)`), `std::vector::at` can't work, `std::stoi` can't report failure, and constructors can't fail — so you need two-phase init and factory functions returning `optional`.

## Practical rules

1. **Throw by value, catch by `const&`.**
2. **RAII everywhere**, or exception safety is impossible.
3. **`noexcept` on moves, swaps, and destructors.**
4. **Never throw from a destructor.**
5. **Derive from `std::exception`** so generic handlers work.
6. **Don't use exceptions for control flow** — they're slow and they hide intent.
7. **`std::expected` for expected failures**, exceptions for exceptional ones.
8. **Be consistent.**

---

## Related
- [[languages/05-cpp/03-classes-and-raii|Classes and RAII]] — what makes unwinding safe
- [[languages/05-cpp/04-copy-move-and-the-rule-of-five|Copy, Move and the Rule of Five]] — `noexcept` moves
- [[languages/03-rust/07-option-and-result|Rust: Result]] — the model `std::expected` adopts
- [[languages/04-c/09-the-standard-library|C: errno]] — the alternative C++ inherited
- [[languages/05-cpp/README|C++ course map]]
