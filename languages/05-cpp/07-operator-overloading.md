---
id: a2205077-5e88-49b9-bb92-94c894b0c394
---

# Operator Overloading

Operator overloading is giving symbols like `+`, `==` or `<<` a meaning for your own types. It is why you can add two strings with `+` in C++, or print a value with `<<`. Used with care, it makes code read naturally, and this lesson shows how to do it well.

## Why it exists
<!-- bite: 247e754e-2fbe-409d-bee9-6e9be0da3f90 -->

The original motivation was numeric types. Without overloading:

```cpp
Matrix c = add(multiply(a, b), scale(d, 2.0));
Complex z = complex_add(complex_mul(x, y), w);
```

With it:

```cpp
Matrix c = a * b + d * 2.0;
Complex z = x * y + w;
```

For mathematical types the second is unarguably better. That's the case operator overloading is *for*: **types with an established, universally-understood notation.**

It's also what makes `std::string` concatenate with `+`, `std::vector` index with `[]`, iterators advance with `++`, and `std::cout` work with `<<`. The standard library is built on it.

## Member vs non-member
<!-- bite: e6d77377-82e5-433a-ae4d-6cdefac47136 -->

```cpp
class Vec2 {
    double x_, y_;
public:
    Vec2(double x, double y) : x_(x), y_(y) {}

    Vec2 &operator+=(const Vec2 &rhs) {        // MEMBER — modifies *this
        x_ += rhs.x_; y_ += rhs.y_;
        return *this;
    }

    double x() const { return x_; }
    double y() const { return y_; }
};

Vec2 operator+(Vec2 lhs, const Vec2 &rhs) {    // NON-MEMBER, lhs BY VALUE
    lhs += rhs;                                 // reuse the member
    return lhs;
}
```

Two conventions worth following:

**Implement `op=` as a member, then define `op` as a non-member in terms of it.** No duplicated logic, and the by-value `lhs` gives you a copy to modify and return — which the compiler often elides entirely.

**Binary arithmetic and comparison operators should be non-members.** A member operator requires the *left* operand to be your type, which breaks symmetry:

```cpp
class Money { Money operator*(double f) const; };   // member
m * 2.0;      // works
2.0 * m;      // DOESN'T — left operand is a double
```

As a free function taking both operands, both directions work.

Which must be members: `=`, `[]`, `()`, `->`, and conversion operators. Everything else can be free, and mostly should be.

## Comparison — and the spaceship
<!-- bite: 36c4e106-3a13-4017-8fae-94e9a02c5d50 -->

Before C++20 you wrote six operators. Since C++20:

```cpp
class Version {
    int major_, minor_, patch_;
public:
    auto operator<=>(const Version &) const = default;   // generates < <= > >=
    bool operator==(const Version &) const = default;     // generates == and !=
};
```

`<=>` (three-way comparison, "spaceship") returns an ordering. Defaulted, it compares members lexicographically in declaration order — which is usually exactly right.

You still declare `==` separately, because equality is often cheaper than ordering (compare sizes first, then contents).

Custom:

```cpp
std::strong_ordering operator<=>(const Version &o) const {
    if (auto c = major_ <=> o.major_; c != 0) return c;
    if (auto c = minor_ <=> o.minor_; c != 0) return c;
    return patch_ <=> o.patch_;
}
```

The ordering types encode how strong the relation is:

- **`strong_ordering`** — equal values are interchangeable
- **`weak_ordering`** — equivalent but distinguishable (case-insensitive strings)
- **`partial_ordering`** — some pairs are unordered. **Floats are this**, because `NaN` compares unordered with everything

That last distinction is the same one [[languages/03-rust/09-traits|Rust encodes]] as `PartialOrd` vs `Ord`.

## Stream insertion
<!-- bite: d259cea1-ef14-4c07-bffd-26e0d9e17098 -->

```cpp
std::ostream &operator<<(std::ostream &os, const Vec2 &v) {
    return os << '(' << v.x() << ", " << v.y() << ')';
}
```

Must be a non-member — the left operand is `std::ostream`, not your type. Return the stream so calls chain.

If it needs private access, declare it a `friend`:

```cpp
class Vec2 {
    friend std::ostream &operator<<(std::ostream &, const Vec2 &);
};
```

This is the main legitimate use of `friend`.

## Subscript, call, and dereference
<!-- bite: 4fd0914f-3c16-4150-8310-5ac82ee034e5 -->

```cpp
class Grid {
    std::vector<double> data_;
    size_t cols_;
public:
    double &operator[](size_t i)             { return data_[i]; }
    const double &operator[](size_t i) const { return data_[i]; }   // const overload

    double &operator()(size_t r, size_t c)   { return data_[r * cols_ + c]; }
};
```

**Always provide both const and non-const `[]`.** Without the const version, you can't index a `const Grid&`, which breaks every `const T&` parameter downstream.

C++23 allows `operator[]` with multiple arguments; before that, `operator()` was the standard workaround for 2D indexing — which is why matrix libraries use `m(i, j)`.

```cpp
class Callable {
public:
    int operator()(int x) const { return x * 2; }     // function call operator
};
Callable c;
c(5);                            // a "functor"
```

Lambdas are compiler-generated classes with an `operator()` — that's all they are:

```cpp
auto add = [](int a, int b) { return a + b; };     // a class with operator()(int,int)
int n = 10;
auto f = [n](int x) { return x + n; };              // capture by value
auto g = [&n](int x) { return x + n; };             // capture by reference
auto h = [=](int x) { return x + n; };              // capture all by value
auto i = [&](int x) { return x + n; };              // capture all by reference — beware lifetimes
auto j = [n = std::move(big)](int x) { };           // init capture / capture by move
auto k = [](auto x) { return x * 2; };              // generic lambda (C++14)
```

**Capturing by reference (`[&]`) in anything stored or deferred is a dangling-reference bug waiting to happen.** For a lambda that outlives the enclosing scope — a callback, a thread body — capture by value or by move.

```cpp
class SmartPtr {
public:
    T &operator*() const  { return *ptr_; }
    T *operator->() const { return ptr_; }        // "drill-down" — chains automatically
};
```

`operator->` is special: it repeatedly applies until it gets a raw pointer, which is what makes `smart->member` work.

## Conversion operators
<!-- bite: 5c6a529c-3b1f-4697-a0f6-a9971cebfd80 -->

```cpp
class Celsius {
    double t_;
public:
    explicit operator double() const { return t_; }
    explicit operator bool() const { return t_ > -273.15; }
};

double d = static_cast<double>(c);      // explicit required
if (c) { }                               // exception: explicit operator bool works
                                         // directly in conditions
```

**Mark conversion operators `explicit`.** Implicit conversions produce surprising overload resolution and accidental conversions — the same problem as non-`explicit` single-argument constructors from [[languages/05-cpp/03-classes-and-raii|Classes and RAII]].

The `explicit operator bool` idiom is how `std::optional`, `std::unique_ptr` and `std::ifstream` work in `if` conditions without being convertible to `int`.

## What you can't overload
<!-- bite: a3f83ae7-ef08-4ed3-93d7-dca7ed7826e2 -->

```text
.        ::        ?:        sizeof        typeid        .*
```

And you can't invent new operators or change precedence and associativity. `a + b * c` always groups as `a + (b * c)` regardless of what those types are — which is a design constraint worth remembering.

## The rules that stop it becoming a problem
<!-- bite: a5432810-6572-4a56-9b5e-c9b463842c07 -->

**1. Preserve the conventional meaning.** `+` adds, `<<` shifts or streams, `==` compares. Overloading `+` to mean "launch" is legal and indefensible.

The classic cautionary example is `operator+` on strings being O(n) — reasonable, and it makes accidental quadratic loops easy to write.

**2. Preserve expected relationships.**
- `a + b` shouldn't modify `a`
- `a += b` should be equivalent to `a = a + b`
- if `a == b` then `!(a != b)`
- `++x` returns a reference; `x++` returns a copy of the old value (and is therefore more expensive)

```cpp
Iterator &operator++()    { ++pos_; return *this; }              // pre: return ref
Iterator  operator++(int) { Iterator t = *this; ++pos_; return t; }  // post: dummy int param
```

**Prefer `++it` over `it++`** in loops — the postfix version constructs a copy you throw away.

**3. Don't overload `&&`, `||`, or `,`.** Overloading them **removes short-circuit evaluation** and the sequencing guarantee. `a && b` with overloaded `&&` evaluates both operands, always. This silently breaks the `if (p && p->x)` idiom.

**4. If it isn't obvious, use a named function.** `matrix.inverse()` beats `~matrix` every time.

## The other languages
<!-- bite: 9ede770a-df89-4031-b3f6-e10f8c9dd281 -->

| | |
|---|---|
| **C** | none — hence `complex_add(a, b)` |
| **Java** | none, except built-in `+` for `String` |
| **[[languages/02-go/index\|Go]]** | none, deliberately — part of "one obvious way" |
| **[[languages/03-rust/09-traits\|Rust]]** | via traits (`Add`, `Index`, `Deref`) — same power, must implement a named trait |
| **Python** | dunder methods — same idea, dynamically |

Go's omission is a considered position: operator overloading makes code shorter to write and harder to read, because `a + b` might do anything. Rust's compromise is instructive — you get it, but only by implementing a trait whose name says what you're doing.

---

## Related
<!-- bite: afa592e2-6fc3-4e4d-9b7a-604c6bf69997 -->
- [[languages/05-cpp/09-the-stl-containers|The STL Containers]] — built on these operators
- [[languages/05-cpp/10-iterators-and-algorithms|Iterators and Algorithms]] — where `++` and `*` earn their keep
- [[languages/05-cpp/04-copy-move-and-the-rule-of-five|Copy, Move and the Rule of Five]] — `operator=`
- [[languages/03-rust/09-traits|Rust: Traits]] — operators as named traits
- [[languages/05-cpp/index|C++ course map]]

## About this lesson
<!-- bite: 92efebad-b53f-4977-b1be-b6bb9c2bccfc -->

**Level:** Intermediate. **Covers:** Making your types behave like built-in ones, which is the feature C++ was arguably built around — and the one most easily abused.
