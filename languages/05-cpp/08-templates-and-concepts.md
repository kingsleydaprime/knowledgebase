# Templates and Concepts

**[Intermediate → Advanced]** — Generic code with zero runtime cost, the error messages that made C++ notorious, and the C++20 feature that finally fixed them.

## Function templates

```cpp
template <typename T>
T max_of(T a, T b) { return a > b ? a : b; }

max_of(3, 7);              // T deduced as int
max_of(3.5, 2.1);          // T = double
max_of<double>(3, 2.1);    // explicit
```

The compiler generates a separate function for each `T` you use. That's **monomorphisation** — the same model as [[languages/03-rust/10-generics-and-trait-bounds|Rust's generics]] — and it means no boxing, no vtable, full inlining.

## Class templates

```cpp
template <typename T>
class Stack {
    std::vector<T> data_;
public:
    void push(T value) { data_.push_back(std::move(value)); }

    std::optional<T> pop() {
        if (data_.empty()) return std::nullopt;
        T v = std::move(data_.back());
        data_.pop_back();
        return v;
    }
    size_t size() const { return data_.size(); }
};

Stack<int> s;
Stack<std::string> t;
```

```cpp
template <typename T, size_t N>            // non-type template parameter
class FixedArray { T data_[N]; };

FixedArray<int, 10> a;
```

Non-type parameters take values, not types — that's how `std::array<int, 5>` knows its size at compile time, and it's [[languages/03-rust/10-generics-and-trait-bounds|Rust's const generics]] arriving thirty years earlier.

**Class template argument deduction** (C++17) removes most explicit arguments:

```cpp
std::vector v{1, 2, 3};              // deduces std::vector<int>
std::pair p{1, "hello"};             // std::pair<int, const char*>
std::lock_guard lock(mu);            // std::lock_guard<std::mutex>
```

## Templates live in headers

This is the practical consequence you'll hit first.

The compiler can only generate `Stack<int>` if it can see the **full definition** at the point of use. Split a template across `.h`/`.cpp` like a normal class and you get `undefined reference` at link time.

So: **template definitions go in the header.** That's why the STL is header-only, why C++ compiles slowly, and why heavy template code inflates build times so badly — every translation unit that includes your header re-instantiates everything it uses.

The workaround where the set of types is known:

```cpp
// stack.cpp — explicit instantiation
template class Stack<int>;
template class Stack<std::string>;
```

Now `stack.cpp` contains those instantiations and the header can hold declarations only. Useful for a small closed set of types; useless for a general-purpose container.

## Specialisation

```cpp
template <typename T>
struct Printer {
    static void print(const T &v) { std::cout << v; }
};

template <>                                    // FULL specialisation for bool
struct Printer<bool> {
    static void print(bool v) { std::cout << (v ? "true" : "false"); }
};

template <typename T>                          // PARTIAL specialisation for pointers
struct Printer<T *> {
    static void print(T *p) { p ? Printer<T>::print(*p) : std::cout << "null"; }
};
```

Function templates support full specialisation only — for functions, **overloading is the better tool**, since it interacts more predictably with overload resolution.

The most notorious specialisation in the standard library is `std::vector<bool>`, which is bit-packed and therefore **doesn't behave like a `vector`**: `operator[]` returns a proxy object, not a `bool&`, so `auto& b = v[0]` doesn't compile and `&v[0]` doesn't give you a pointer. Use `std::vector<char>` or `std::bitset` instead. It's a standing lesson in why specialising to change behaviour is dangerous.

## Variadic templates

```cpp
template <typename... Args>
void log(Args... args) {
    (std::cout << ... << args) << '\n';        // C++17 fold expression
}
log("x = ", 42, ", y = ", 3.14);
```

```cpp
template <typename T, typename... Args>
std::unique_ptr<T> make_unique_impl(Args &&...args) {
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
}
```

That's roughly `std::make_unique` — variadic templates plus [[languages/05-cpp/04-copy-move-and-the-rule-of-five|perfect forwarding]] are what let you pass arbitrary constructor arguments through a wrapper. Same mechanism behind `emplace_back`.

Fold expressions (C++17) replaced the old recursive-template-with-base-case pattern, which was genuinely unpleasant to read.

## The error-message problem

Templates are checked at **instantiation**, not at definition. So an error surfaces deep inside the library:

```cpp
std::vector<NonComparable> v;
std::sort(v.begin(), v.end());
```

Pre-C++20 this produced several hundred lines of errors from inside `<algorithm>`, with the actual problem — "your type has no `operator<`" — buried somewhere in the middle. This is the single biggest reason C++ has the reputation it does.

[[languages/03-rust/10-generics-and-trait-bounds|Rust avoided this]] by checking generics against their bounds *at definition*. C++ took until 2020 to get the same thing.

## Concepts (C++20)

```cpp
#include <concepts>

template <typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template <Numeric T>                            // constrained
T sum(const std::vector<T> &v) {
    T total{};
    for (const auto &x : v) total += x;
    return total;
}
```

```cpp
auto sum(const std::vector<Numeric auto> &v);   // abbreviated form
template <typename T> requires Numeric<T>       // requires clause
void f(T x);
```

Custom concepts state requirements structurally:

```cpp
template <typename T>
concept Drawable = requires(const T &t, Canvas &c) {
    { t.area() } -> std::convertible_to<double>;    // must have area() returning double-ish
    t.draw(c);                                       // must have draw(Canvas&)
};

template <Drawable T>
void render(const T &shape) { shape.draw(canvas); }
```

Now the error is at the call site and says what's missing:

```
error: no matching function for call to 'render(Widget&)'
note: constraints not satisfied
note: the required expression 't.area()' is invalid
```

This is a genuine transformation of the experience. **Use concepts on any template you expect others to call.**

Standard concepts worth knowing: `std::integral`, `std::floating_point`, `std::same_as`, `std::convertible_to`, `std::derived_from`, `std::invocable`, `std::ranges::range`, `std::sortable`.

### Before concepts: SFINAE

You'll meet this in any pre-C++20 codebase:

```cpp
template <typename T,
          typename = std::enable_if_t<std::is_integral_v<T>>>
void f(T x);
```

**SFINAE** — "substitution failure is not an error". If substituting a type produces an invalid signature, that overload is quietly dropped rather than causing a compile error, which lets you select overloads by type properties.

It works, it's unreadable, and concepts replace it entirely. Recognise it; don't write new code with it.

## `if constexpr`

```cpp
template <typename T>
void process(T value) {
    if constexpr (std::is_pointer_v<T>) {
        std::cout << *value;         // only COMPILED when T is a pointer
    } else {
        std::cout << value;
    }
}
```

The discarded branch isn't compiled, so it can contain code that would be invalid for the other type. Before C++17 this needed tag dispatch or specialisation — several times more code for the same effect. → [[languages/05-cpp/12-constexpr-and-compile-time|constexpr]]

## Costs

**Compile time.** The biggest practical cost in C++. Every instantiation is a separate compilation, repeated per translation unit.

**Binary size.** `Stack<int>`, `Stack<double>` and `Stack<std::string>` are three complete classes in the output.

**Error messages** — improved enormously by concepts, still worse than most languages.

**Debuggability.** Stepping through instantiated template code is unpleasant.

Mitigations:
- **Concepts**, for the errors
- **Extract type-independent logic into a non-template base**, so only the thin wrapper is duplicated
- **Explicit instantiation** for closed type sets
- **Forward declarations** and `extern template` to cut redundant instantiation
- **Precompiled headers**, or [[languages/05-cpp/14-modern-cpp-and-modules|modules]]

## Templates vs inheritance

The two polymorphisms, and the real trade:

| | Templates (static) | Virtual (dynamic) |
|---|---|---|
| Resolved | compile time | runtime |
| Cost | zero; inlinable | vtable indirection |
| Types | must be known at compile time | open set, plugins |
| Binary size | one copy per type | one copy total |
| Compile time | slow | fast |
| Heterogeneous containers | no | yes |

**Templates when the types are known at compile time and performance matters. Virtual when the set of types is open or must be heterogeneous.** A `std::vector<std::unique_ptr<Shape>>` needs virtual; a `sort` over any comparable type wants a template.

---

## Related
- [[languages/05-cpp/06-inheritance-and-virtual-dispatch|Inheritance and Virtual Dispatch]] — the other polymorphism
- [[languages/05-cpp/10-iterators-and-algorithms|Iterators and Algorithms]] — the STL, which is all templates
- [[languages/05-cpp/12-constexpr-and-compile-time|constexpr]] — computation at compile time
- [[languages/03-rust/10-generics-and-trait-bounds|Rust: Generics]] — bounds checked at definition, from the start
- [[languages/05-cpp/README|C++ course map]]
