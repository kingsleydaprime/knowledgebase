# Why C++, and What It Added

**[Beginner → Intermediate]** — C++ only makes sense as a reaction to C. What it added, the principle it never compromised, and the reason it's the hardest mainstream language to learn.

**Source:** `[reference]` — cross-referenced against [roadmap.sh C++](https://roadmap.sh/cpp). No C++ project in this vault. See [[project-ideas|Project Ideas]].

## The premise

Bjarne Stroustrup started with "C with Classes" in 1979. The goal was **abstraction without giving up control** — you should be able to build a `string`, a `vector`, a `Matrix` that behave like built-in types, and pay nothing for the ones you don't use.

That's the **zero-overhead principle**, and it's the one thing C++ has never compromised:

> *What you don't use, you don't pay for. What you do use, you couldn't hand-code any better.*

So: no garbage collector, no runtime, no mandatory bounds checks, no reflection, no interpreter. A `std::vector<int>` is a pointer and two sizes; iterating one compiles to the same loop you'd write in C.

The result is a language that is genuinely faster to *write* than C and just as fast to *run* — while being enormously harder to learn than either.

## What it added to C

| Addition | Fixes what in C |
|---|---|
| **Classes and destructors → RAII** | manual `free`/`fclose`/`unlock`, and forgetting them |
| **References** | pointer syntax where you never wanted null |
| **`std::string`, `std::vector`** | `char*` and manual arrays → [[languages/04-c/06-arrays-strings-and-decay\|decay and overflow]] |
| **Templates** | `void*` and macros for generic code |
| **Function/operator overloading** | `abs`/`labs`/`fabs`, and `add_int`/`add_float` |
| **Namespaces** | `module_prefix_on_every_symbol` |
| **Exceptions** | `if (rc != 0) goto cleanup` everywhere |
| **`const` that means something** | `const` that everyone casts away |
| **Smart pointers** | ownership as a comment |

**RAII is the big one**, and if you take one idea from C++ into other languages, take that one. Everything else is convenience; RAII is a genuinely different way to manage resources. → [[languages/05-cpp/03-classes-and-raii|Classes and RAII]]

## What it kept — including the bad parts

C++ is **almost** a superset of C, and that compatibility is both its distribution strategy and its greatest weakness:

- **Raw pointers, manual `new`/`delete`, pointer arithmetic** — all still there
- **[[languages/04-c/10-undefined-behaviour|Undefined behaviour]]** — all of C's, plus more of its own
- **The preprocessor** — still required, because [[languages/04-c/02-headers-and-the-translation-unit|headers]] are still the compilation model
- **No memory safety.** C++ is *safer* than C if you use it well, and it is not *safe*. Use-after-free, dangling references, iterator invalidation and data races are all reachable in ordinary-looking modern code.

That last point matters, because the industry conversation is about it. Microsoft's and Google's ~70% memory-safety-bug figures cover C **and** C++. Modern C++ with smart pointers and containers eliminates most of the easy mistakes; it does not eliminate the category, because nothing checks you.

## The real problem: it's several languages

C++ has accumulated 45 years of features without removing any. You can write:

```cpp
// 1990s C++: raw pointers, manual new/delete, inheritance hierarchies
Shape *s = new Circle(5);
s->draw();
delete s;

// 2010s C++: RAII, smart pointers, algorithms, lambdas
auto s = std::make_unique<Circle>(5);
s->draw();

// 2020s C++: ranges, concepts, structured bindings
auto evens = data | std::views::filter([](int n){ return n % 2 == 0; });
for (auto [key, value] : map) { }
```

All three compile. All three are "C++". A codebase usually contains all three, written by different people in different decades.

**This is why C++ is hard.** Not any individual feature — the fact that there are five ways to do everything, three of them obsolete, and the language won't tell you which is which. Learning C++ is mostly learning **which subset to write**.

> **The subset to write:** RAII everywhere, `std::unique_ptr` for owning pointers, containers instead of raw arrays, algorithms instead of hand-written loops, `const` and references by default, and `new`/`delete` essentially never. That's "modern C++", and it's what these notes teach.

## Compilation — same model as C

Preprocess → compile → assemble → link, one [[languages/04-c/02-headers-and-the-translation-unit|translation unit]] at a time. Everything in the C note applies.

Two C++-specific differences:

**Name mangling.** Because C++ has overloading, namespaces and templates, the linker needs distinct symbol names:

```cpp
int add(int, int);        // _Z3addii
double add(double, double); // _Z3adddd
```

```bash
nm -C app | grep add       # -C demangles
```

This is why calling C from C++ needs `extern "C"` to suppress mangling:

```cpp
extern "C" {
    #include <some_c_header.h>
}
```

And why a C library's headers usually contain:

```c
#ifdef __cplusplus
extern "C" {
#endif
/* declarations */
#ifdef __cplusplus
}
#endif
```

**Templates are compiled per-instantiation**, which is why template code lives in headers and why C++ builds are slow. → [[languages/05-cpp/08-templates-and-concepts|Templates]]

```bash
g++ -std=c++20 -Wall -Wextra -Wpedantic -g -O2 main.cpp -o main
clang++ -std=c++23 ...
```

Use `g++`/`clang++`, not `gcc`, or you won't link the C++ standard library.

## Hello, world

```cpp
#include <iostream>
#include <string>

int main() {
    std::string name = "world";
    std::cout << "Hello, " << name << "!\n";
    return 0;                    // optional in main
}
```

- **`std::`** — everything in the standard library is in namespace `std`
- **`<<`** — an overloaded operator, not a shift. `std::cout` is an object
- **`std::string`** manages its own memory; it frees itself
- **`"\n"` over `std::endl`** — `endl` also flushes, which is usually an unwanted cost

**Never write `using namespace std;`** at file scope in a header, and preferably not at all. It pulls ~2,000 names into your scope and produces baffling ambiguity errors (`std::count` vs your `count`).

## Where C++ fits

**Good at:** game engines, trading systems, browsers, databases, CAD, embedded with a real toolchain, scientific computing, and any large existing C++ codebase. It's the default where you need C-level performance *and* substantial abstraction.

**Bad at:** anything where compile times or onboarding matter, small tools, and new systems work where [[languages/03-rust/README|Rust]] is viable. It's also poorly suited to teams without a strong shared convention, because the language won't enforce one.

The comparison that matters now that all four are here:

| | [[languages/04-c/README\|C]] | C++ | [[languages/03-rust/README\|Rust]] | [[languages/02-go/README\|Go]] |
|---|---|---|---|---|
| Resource management | manual | **RAII** | RAII + ownership | GC |
| Memory safety | none | partial, by discipline | guaranteed | guaranteed |
| Abstraction cost | n/a | zero | zero | small |
| Language size | tiny | enormous | large | small |
| Compile speed | fast | slow | slow | fast |
| Learning curve | shallow, deep pitfalls | very steep | steep | shallow |

C++ and Rust occupy nearly the same performance niche. The difference is that C++ gives you RAII and asks you to be careful, while Rust gives you RAII and checks.

## The standards

| | Notable |
|---|---|
| **C++98/03** | the original standard; templates, STL |
| **C++11** | the language changed. `auto`, lambdas, move semantics, smart pointers, range-for, `nullptr`, threads |
| **C++14** | generic lambdas, `make_unique` |
| **C++17** | structured bindings, `std::optional`, `std::variant`, `if constexpr`, filesystem |
| **C++20** | concepts, ranges, modules, coroutines, `<=>` |
| **C++23** | `std::expected`, `std::print`, deducing `this` |

**C++11 is the dividing line.** Code before it and after it look like different languages, and "modern C++" means C++11 or later. Target **C++17 as a safe floor** and **C++20** where the toolchain allows.

---

## Related
- [[languages/05-cpp/03-classes-and-raii|Classes and RAII]] — the central idea
- [[languages/04-c/01-why-c-and-the-compilation-model|C: The Compilation Model]] — the model C++ inherited
- [[languages/05-cpp/14-modern-cpp-and-modules|Modern C++ and Modules]] — what changed and what to write
- [[languages/03-rust/01-why-rust-and-the-toolchain|Rust: Why Rust]] — the same niche, checked
- [[languages/05-cpp/README|C++ course map]]
