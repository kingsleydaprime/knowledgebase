# Modern C++ and Modules

**[Intermediate]** — What actually changed between 1998 and 2023, which subset to write, and why headers are still everywhere despite modules existing since 2020.

## The dividing line

**C++11 is where the language changed.** Code before and after it look different enough to be separate languages, and "modern C++" means C++11 or later.

```cpp
// C++98
std::vector<Widget *> widgets;
for (std::vector<Widget *>::iterator it = widgets.begin(); it != widgets.end(); ++it) {
    (*it)->process();
}
for (std::vector<Widget *>::iterator it = widgets.begin(); it != widgets.end(); ++it) {
    delete *it;
}
```

```cpp
// C++11+
std::vector<std::unique_ptr<Widget>> widgets;
for (const auto &w : widgets) { w->process(); }
// no delete loop — unique_ptr handles it
```

Shorter, and it's also exception-safe, leak-free, and const-correct — which the first version isn't.

## What each standard added

### C++11 — the big one

| Feature | Why it mattered |
|---|---|
| **`auto`** | iterator types stopped being unwriteable |
| **Range-based `for`** | `for (const auto &x : v)` |
| **Lambdas** | algorithms became usable without writing functor classes |
| **Move semantics** | returning containers stopped being expensive → [[languages/05-cpp/04-copy-move-and-the-rule-of-five\|Rule of Five]] |
| **`unique_ptr` / `shared_ptr`** | `new`/`delete` became unnecessary → [[languages/05-cpp/05-smart-pointers-and-ownership\|Smart Pointers]] |
| **`nullptr`** | replaced `NULL`, which was `0` |
| **`override` / `final`** | silent override bugs became compile errors |
| **Threads, mutexes, atomics, memory model** | concurrency became defined → [[languages/05-cpp/13-concurrency\|Concurrency]] |
| **`constexpr`** | compile-time computation without templates |
| **`enum class`** | scoped, strongly typed enums |
| **Uniform initialisation `{}`** | one syntax, and it prevents narrowing |
| **Variadic templates** | `make_unique`, `emplace_back` |
| **`= default` / `= delete`** | explicit control over the special members |

`enum class` is worth calling out — plain C enums are integers that convert implicitly and leak their names into the enclosing scope:

```cpp
enum Color { Red, Green };          // Red is now a global name
enum class Color { Red, Green };    // Color::Red; no implicit conversion to int
```

**Always `enum class`.**

### C++14 — polish

`make_unique` (a C++11 oversight), generic lambdas (`[](auto x){}`), relaxed `constexpr` with loops, binary literals, digit separators (`1'000'000`).

### C++17 — quality of life

```cpp
auto [key, value] = *map.begin();                 // structured bindings
if (auto it = m.find(k); it != m.end()) { }       // if with initialiser
std::optional<Widget> maybe;                       // → 05-smart-pointers
std::variant<int, std::string> either;              // type-safe union
std::string_view sv = "no allocation";
if constexpr (std::is_pointer_v<T>) { }            // → 08-templates
std::filesystem::path p{"/tmp/x"};
std::scoped_lock lock(mu1, mu2);
std::vector v{1, 2, 3};                            // class template argument deduction
[[nodiscard]] int compute();                        // warn if the result is ignored
```

**Structured bindings** and **`if` with initialiser** are the two you'll use hourly. `[[nodiscard]]` is worth putting on anything returning an error or an allocated resource.

### C++20 — the second big one

```cpp
template <std::integral T> void f(T);              // concepts → 08-templates
auto evens = v | std::views::filter(is_even);      // ranges → 10-iterators
auto operator<=>(const T&) const = default;         // spaceship → 07-operators
import std;                                         // modules — see below
Task<int> f() { co_await something(); }             // coroutines → 13-concurrency
std::jthread t(work);                               // auto-joining thread
std::span<int> s = vec;                             // non-owning array view
std::format("{} = {}", name, value);                // type-safe formatting, at last
constinit int x = f();                              // guaranteed compile-time init
```

`std::format` deserves a mention: it replaces both `printf`'s type-unsafety and `iostream`'s verbosity with Python-style formatting that's checked at compile time.

### C++23

`std::expected<T, E>` ([[languages/05-cpp/11-exceptions-and-error-handling|Result-style errors]]), `std::print` (finally, no `<<`), `std::generator`, deducing `this`, `std::mdspan`, ranges `to<>`.

## The subset to write

Given a language this large, the useful question isn't "what exists" but "what should I write". The consensus:

**Do:**
- **RAII for every resource.** No exceptions to this
- **`std::unique_ptr` for owning pointers**, `shared_ptr` only for genuine sharing
- **Containers, never raw arrays.** `std::vector`, `std::array`
- **`const` and references by default**; `const auto&` in range-for
- **Algorithms and ranges** over hand-written loops
- **`enum class`, `nullptr`, `override`, `[[nodiscard]]`**
- **Structured bindings, `if` with initialiser**
- **Rule of Zero** — let the compiler generate the special members
- **`std::optional` / `std::expected`** for absence and failure

**Don't:**
- **`new` / `delete`** — if you type `delete`, something is wrong
- **Raw owning pointers**
- **C arrays and `char*` strings** — → [[languages/04-c/06-arrays-strings-and-decay|the C reasons]]
- **`using namespace std;`** at file scope
- **`#define` for constants** — use `constexpr`
- **Deep inheritance hierarchies** — → [[languages/05-cpp/06-inheritance-and-virtual-dispatch|prefer composition]]
- **`malloc`/`free`** in C++ code
- **C-style casts** — `static_cast`, `dynamic_cast`, `const_cast`, `reinterpret_cast` say what you mean and are greppable

That list is essentially what the [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/) say, and `clang-tidy`'s `cppcoreguidelines-*` and `modernize-*` checks enforce a good chunk of it automatically. → [[languages/05-cpp/15-build-tooling-and-ecosystem|Build Tooling]]

## Modules

Standardised in C++20, and the intended replacement for [[languages/04-c/02-headers-and-the-translation-unit|headers]].

```cpp
// math.cppm — a module interface unit
export module math;

export int square(int x) { return x * x; }     // exported
int helper(int x) { return x + 1; }             // NOT exported — internal
```

```cpp
// main.cpp
import math;

int main() { return square(5); }
```

What this fixes:

| Header problem | Modules |
|---|---|
| Parsed once per including file | **compiled once**, imported as a binary artefact |
| Macros leak into and out of headers | **macros don't cross module boundaries** |
| Include order affects meaning | **order-independent** |
| Everything is visible unless hidden | **nothing is visible unless exported** |
| `#pragma once` / include guards | not needed |

Reported build-time improvements are substantial — often 2–5× on template-heavy code, because you stop re-parsing the same tens of thousands of lines.

```cpp
import std;                     // C++23 — the whole standard library, one import
```

## So why is everyone still using headers?

Honestly:

**Tooling.** Modules require the build system to determine module dependencies *before* compiling, since a module must be compiled before anything importing it. That's a fundamental change to how builds work, and CMake support only became genuinely usable in 3.28 (late 2023).

**Compiler support is uneven.** MSVC is furthest along; GCC and Clang have been catching up for years and there are still rough edges, especially around `import std`.

**Interop.** A module can `#include` a header, but a header cannot `import` a module usefully. Migration must start at the leaves, and most large codebases are all header.

**Nobody has migrated.** Boost, Qt, and essentially every major library still ship headers, so you're including them anyway.

> **Realistically: know modules exist and how they work. Write headers for now, unless you control the whole toolchain and are on a recent CMake.** The transition is happening at roughly the speed of Python 2→3, for similar reasons.

Header units are the migration path:

```cpp
import <vector>;             // a header unit — compiled once, still a header underneath
```

## Deprecated and removed

Worth knowing when reading old code:

- **`auto_ptr`** — removed in C++17. Broken copy semantics; `unique_ptr` replaced it
- **`register`, `throw(...)` exception specifications** — removed
- **`std::bind`** — superseded by lambdas, which are clearer and optimise better
- **Trigraphs** — removed in C++17
- **`std::rand`** — still there; use `<random>` for anything real, and a CSPRNG for anything security-relevant

## Practical rules

1. **Target C++17 as a floor**, C++20 where the toolchain allows.
2. **Write the modern subset.** The language won't stop you writing 1998 C++.
3. **Turn on `clang-tidy` with `modernize-*`** and let it flag the old idioms.
4. **`enum class`, `nullptr`, `override`, `[[nodiscard]]`** — free correctness.
5. **Know modules; don't bet a project on them yet.**

---

## Related
- [[languages/05-cpp/01-why-cpp-and-what-it-added|Why C++]] — the "several languages in one" problem
- [[languages/05-cpp/15-build-tooling-and-ecosystem|Build Tooling and Ecosystem]] — enforcing the subset
- [[languages/04-c/02-headers-and-the-translation-unit|C: Headers]] — what modules replace
- [[languages/05-cpp/README|C++ course map]]
