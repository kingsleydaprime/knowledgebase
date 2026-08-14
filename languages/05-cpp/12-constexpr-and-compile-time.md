# `constexpr` and Compile-Time Computation

**[Advanced]** — Running your code during compilation. The feature that turned C++'s accidental compile-time language into a deliberate one.

## The accident

C++ templates turned out to be Turing-complete — discovered, not designed, in 1994. That gave rise to **template metaprogramming**: computation expressed as recursive template instantiation.

```cpp
template <int N>
struct Factorial { static constexpr int value = N * Factorial<N-1>::value; };

template <>
struct Factorial<0> { static constexpr int value = 1; };

int x = Factorial<5>::value;      // 120, computed by the COMPILER
```

It works, and it's a functional language with terrible syntax, no debugger, and error messages measured in screenfuls. For twenty years this was the only way to compute at compile time.

## `constexpr`

C++11 introduced a far better answer: **write ordinary functions and mark them `constexpr`.**

```cpp
constexpr int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);      // C++11: single return only
}

constexpr int x = factorial(5);        // computed at COMPILE time
int y = factorial(runtime_value);       // same function, computed at RUNTIME
```

`constexpr` means **"can be evaluated at compile time"**, not "must be". The same function serves both, which is the whole point — one implementation, no duplication.

C++14 lifted the single-expression restriction, and now it's just normal code:

```cpp
constexpr int factorial(int n) {
    int result = 1;
    for (int i = 2; i <= n; ++i) result *= i;      // loops, locals, branches — all fine
    return result;
}
```

Compare that with the template version. Same computation, readable, debuggable, and it works at runtime too.

## Forcing compile-time evaluation

```cpp
constexpr int a = factorial(5);        // ERROR if it can't be done at compile time
int b = factorial(5);                   // MAY be computed at compile time, or not
```

`constexpr` on the *variable* is what requires it. C++20 added `consteval` to force it at the function level:

```cpp
consteval int must_be_compile_time(int n) { return n * 2; }

int a = must_be_compile_time(5);        // fine
int b = must_be_compile_time(runtime);  // COMPILE ERROR
```

Use `consteval` for things that are meaningless at runtime — compile-time validation, code generation.

```cpp
constexpr int f(int n) {
    if consteval { return compile_time_impl(n); }   // C++23: different implementations
    else         { return runtime_impl(n); }
}
```

## What's allowed

The restrictions have shrunk dramatically:

| Version | Allows |
|---|---|
| C++11 | a single return statement, basically |
| C++14 | loops, locals, multiple statements, mutation |
| C++17 | `if constexpr`, lambdas |
| C++20 | **allocation** (if freed within the same evaluation), `try/catch`, virtual calls, `std::vector` and `std::string` |
| C++23 | `static_assert` in more places, relaxed further |

Still not allowed: I/O, `reinterpret_cast`, `goto`, uninitialised variables, and any allocation that escapes the constant evaluation.

That C++20 allocation rule is the subtle one — you *can* use a `std::vector` inside a `constexpr` function, but it must be destroyed before the evaluation ends. You can compute with it; you can't return one as a compile-time constant.

## `if constexpr`

```cpp
template <typename T>
auto get_value(T t) {
    if constexpr (std::is_pointer_v<T>) {
        return *t;               // this branch is only COMPILED when T is a pointer
    } else {
        return t;
    }
}
```

The discarded branch isn't compiled, so it can contain code that would be invalid for the other type. Before C++17 this required tag dispatch or template specialisation — several times the code for the same effect.

Not to be confused with a plain runtime `if` on a `constexpr` condition, which compiles both branches.

## `static_assert`

```cpp
static_assert(sizeof(void *) == 8, "64-bit only");
static_assert(factorial(5) == 120);
static_assert(std::is_trivially_copyable_v<Widget>,
              "Widget must be trivially copyable for memcpy serialisation");
```

Compile-time assertions, with your message in the error. Excellent for enforcing invariants a comment would otherwise carry — struct sizes for a wire format, type properties an algorithm depends on.

## Type traits

The compile-time reflection library:

```cpp
#include <type_traits>

std::is_integral_v<T>              std::is_pointer_v<T>
std::is_same_v<T, U>               std::is_base_of_v<Base, Derived>
std::is_trivially_copyable_v<T>    std::is_move_constructible_v<T>
std::remove_const_t<T>             std::remove_reference_t<T>
std::decay_t<T>                    std::conditional_t<B, T, F>
std::underlying_type_t<Enum>
```

```cpp
template <typename T>
void serialise(const T &v, std::byte *out) {
    static_assert(std::is_trivially_copyable_v<T>, "cannot memcpy this type");
    std::memcpy(out, &v, sizeof v);
}
```

That `static_assert` turns a silent, catastrophic bug — `memcpy`ing a type with a pointer or a vtable — into a clear compile error. This is the most practically valuable thing in `<type_traits>`.

Since C++20, [[languages/05-cpp/08-templates-and-concepts|concepts]] are the better interface for constraining templates, but traits remain the underlying vocabulary.

## `constexpr` containers and `std::array`

```cpp
constexpr std::array<int, 5> squares = [] {
    std::array<int, 5> a{};
    for (int i = 0; i < 5; ++i) a[i] = i * i;
    return a;
}();                                    // immediately-invoked constexpr lambda
```

That IIFE pattern is how you build a compile-time lookup table with ordinary imperative code. Before C++14 you'd have needed template recursion or a macro.

```cpp
constexpr auto build_crc_table() {
    std::array<uint32_t, 256> t{};
    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t c = i;
        for (int k = 0; k < 8; ++k) c = (c & 1) ? (0xEDB88320u ^ (c >> 1)) : (c >> 1);
        t[i] = c;
    }
    return t;
}
constexpr auto crc_table = build_crc_table();     // zero runtime cost
```

A CRC table computed by the compiler, from readable code. That's what this feature is for.

## What it's actually good for

**Lookup tables** — computed at build time instead of shipped as a literal or built at startup.

**Compile-time validation:**

```cpp
consteval bool valid_ip(std::string_view s) { /* parse */ }
static_assert(valid_ip("192.168.1.1"));
```

**Removing startup work** — configuration parsing, table generation, string hashing:

```cpp
constexpr uint64_t hash(std::string_view s) {
    uint64_t h = 14695981039346656037ULL;
    for (char c : s) { h ^= static_cast<uint64_t>(c); h *= 1099511628211ULL; }
    return h;
}

switch (hash(input)) {                    // switch on strings, via compile-time hashing
    case hash("start"): ...; break;
    case hash("stop"):  ...; break;
}
```

**Units and dimensional analysis** — encoding physical units in types so a compile error catches adding metres to seconds. (`std::chrono` is the standard library's own example: adding a `seconds` to a `milliseconds` converts correctly, and adding a `seconds` to an `int` doesn't compile.)

## Costs

**Compile time.** You've moved work from run time to build time, and build time is a cost you pay on every build. Heavy `constexpr` computation makes builds slow.

**Debuggability.** You cannot step through compile-time evaluation. `static_assert` and printing from a `constexpr` function forced to run at runtime are the debugging tools, and they're thin.

**Error messages.** Better than template metaprogramming, still not good — "expression did not evaluate to a constant" with a long note trail.

**Don't `constexpr` everything.** It's for values genuinely needed at compile time or that measurably help startup. Marking every small function `constexpr` inflates build times for nothing.

## The comparison

| | |
|---|---|
| **C** | `#define`, and the preprocessor. No computation worth the name |
| **[[languages/03-rust/README\|Rust]]** | `const fn` — the same idea, more restricted; and proc macros for real codegen |
| **[[languages/02-go/README\|Go]]** | none. `go generate` shells out to a program |
| **Zig** | `comptime` — the cleanest design of the lot; the compile-time language *is* the language |

C++'s version is the most capable in mainstream use, and it got there by accident and then by twenty years of retrofitting. Zig's `comptime` is what it would look like designed from the start.

---

## Related
- [[languages/05-cpp/08-templates-and-concepts|Templates and Concepts]] — the older compile-time mechanism
- [[languages/05-cpp/14-modern-cpp-and-modules|Modern C++ and Modules]] — where `constexpr` fits in the timeline
- [[languages/04-c/03-the-preprocessor|C: The Preprocessor]] — what this replaces
- [[languages/05-cpp/README|C++ course map]]
