# C++

A language that added abstraction to C without giving up a single cycle, then kept every feature it ever shipped for forty-five years. The result is the most powerful and the most difficult mainstream language in use.

**~24,000 words across 15 notes.** Built August 2026, cross-referenced against [roadmap.sh C++](https://roadmap.sh/cpp).

**Source: `[reference]`.** No C++ project in this vault. See [[project-ideas|Project Ideas]] — and [[PRIMETECHIE|reading is not a rank]].

> **Read [[languages/04-c/README|the C course]] first.** C++ only makes sense as a reaction to C: RAII is the answer to `goto cleanup`, `std::vector` is the answer to array decay, references are the answer to pointers that can't be null, and smart pointers are the answer to `malloc`/`free`. Every one of these notes assumes you know what it's fixing.

## The one idea worth taking away

**RAII.** Acquire a resource in a constructor, release it in the destructor, and the object's lifetime *is* the resource's lifetime.

It's stronger than every alternative — `goto cleanup`, `try/finally`, `defer`, `with` — for one reason: those put the cleanup at the **call site**, where any caller can forget it. RAII puts it in the **type**, so nobody can. Written once, correct for every user, and it composes automatically.

If you take one idea from C++ into other languages, take that one. [[languages/03-rust/03-ownership|Rust took it and made it a rule]] rather than a convention.

## Reading order

**Getting oriented**

1. [[languages/05-cpp/01-why-cpp-and-what-it-added|Why C++, and What It Added]] — **[Beginner → Intermediate]** — the zero-overhead principle, what it added to C, what it kept, and the "several languages in one" problem
2. [[languages/05-cpp/02-references-and-const|References and `const`]] — **[Beginner]** — references vs pointers, `const` correctness, `auto`, and the argument-passing rules

**The core**

3. [[languages/05-cpp/03-classes-and-raii|Classes and RAII]] — **[Beginner → Intermediate]** — **the central note.** Constructors, destructors, and why RAII beats every other cleanup mechanism
4. [[languages/05-cpp/04-copy-move-and-the-rule-of-five|Copy, Move and the Rule of Five]] — **[Intermediate]** — what happens when your class owns something; move semantics; the Rule of Zero you should actually follow
5. [[languages/05-cpp/05-smart-pointers-and-ownership|Smart Pointers and Ownership]] — **[Intermediate]** — `unique_ptr`, `shared_ptr`, `weak_ptr`, and expressing ownership in a signature

**Polymorphism**

6. [[languages/05-cpp/06-inheritance-and-virtual-dispatch|Inheritance and Virtual Dispatch]] — **[Intermediate]** — vtables, slicing, the diamond, and why modern C++ uses far less inheritance
7. [[languages/05-cpp/07-operator-overloading|Operator Overloading]] — **[Intermediate]** — making your types behave like built-ins, and the rules that stop it becoming a problem
8. [[languages/05-cpp/08-templates-and-concepts|Templates and Concepts]] — **[Intermediate → Advanced]** — monomorphisation, the notorious error messages, and the C++20 feature that fixed them

**The standard library**

9. [[languages/05-cpp/09-the-stl-containers|The STL Containers]] — **[Intermediate]** — what to reach for, what each costs, and the invalidation rules
10. [[languages/05-cpp/10-iterators-and-algorithms|Iterators and Algorithms]] — **[Intermediate]** — the design that made the STL famous, plus C++20 ranges

**The hard parts**

11. [[languages/05-cpp/11-exceptions-and-error-handling|Exceptions and Error Handling]] — **[Intermediate → Advanced]** — safety guarantees, `noexcept`, and why a large slice of the industry disables exceptions
12. [[languages/05-cpp/12-constexpr-and-compile-time|`constexpr` and Compile-Time Computation]] — **[Advanced]** — running your code during compilation
13. [[languages/05-cpp/13-concurrency|Concurrency]] — **[Advanced]** — threads, the memory model, and the fact that none of it is checked

**Practice**

14. [[languages/05-cpp/14-modern-cpp-and-modules|Modern C++ and Modules]] — **[Intermediate]** — what each standard changed, **the subset to write**, and why headers persist despite modules
15. [[languages/05-cpp/15-build-tooling-and-ecosystem|Build Tooling and Ecosystem]] — **[Intermediate]** — CMake, the package-manager situation, and the tools that catch what the compiler won't

## The subset to write

C++ will happily let you write 1998 C++, and a real codebase usually contains three decades at once. Learning C++ is mostly learning **which subset to write**:

**Do:** RAII for every resource · `unique_ptr` for owning pointers · containers, never raw arrays · `const` and references by default · algorithms over hand-written loops · `enum class`, `nullptr`, `override`, `[[nodiscard]]` · Rule of Zero · `std::optional` / `std::expected`

**Don't:** `new`/`delete` · raw owning pointers · C arrays and `char*` · `using namespace std;` · `#define` constants · deep inheritance hierarchies · C-style casts

`clang-tidy` with `modernize-*` and `cppcoreguidelines-*` enforces most of that automatically — which is the practical answer to a language too large to hold in your head. → note 15.

## The honest safety position

C++ is **safer than C if you use it well, and it is not safe.** Use-after-free, dangling references, iterator invalidation, object slicing and data races are all reachable in ordinary-looking modern code, and nothing checks you.

The ~70% memory-safety-bug figure from Microsoft and Google covers C **and** C++. Smart pointers and containers remove most of the easy mistakes; they don't remove the category. That's the entire argument for [[languages/03-rust/README|Rust]] in new systems work, and it's why the four-language comparison is worth keeping in view:

| | [[languages/04-c/README\|C]] | C++ | [[languages/03-rust/README\|Rust]] | [[languages/02-go/README\|Go]] |
|---|---|---|---|---|
| Resources | manual | **RAII** | RAII + ownership | GC |
| Memory safety | none | by discipline | **guaranteed** | guaranteed |
| Data races | possible | possible | **impossible** | possible |
| Abstraction cost | n/a | zero | zero | small |
| Language size | tiny | **enormous** | large | small |
| Compile speed | fast | **slow** | slow | fast |
| Dependencies | none | vcpkg/Conan | cargo | modules |

C++'s remaining unassailable ground: existing codebases (which are vast), game engines and their tooling, and domains where the library ecosystem simply isn't in Rust yet.

## Where the frameworks are

Per [[languages/README|the vault rule]]:

### → **[[backend/frameworks/cpp/README|backend/frameworks/cpp/]]** — Drogon, Crow, Pistache, oat++, Boost.Beast

## Known gaps

- **No project.** The largest gap
- **Coroutines** get a section, not the note they deserve — they're a major C++20 feature and genuinely hard
- **Boost** is listed, not explored
- **Embedded C++** — `-fno-exceptions`, `-fno-rtti`, freestanding. Adjacent to [[hardware/README|hardware/]]
- **The ABI and linkage details** — `inline`, ODR violations, vague linkage
- **Performance work specifically** — the C notes' `perf` material applies, but C++-specific costs (virtual calls, allocation, template bloat) deserve their own note

---

## Related
- [[languages/04-c/README|C]] — read this first
- [[languages/03-rust/README|Rust]] — the same niche, with the guarantees checked
- [[languages/README|Languages]] — the language/framework split rule
- [[BUILD-PLAN|Build Plan]] — `backend/frameworks/` is next
