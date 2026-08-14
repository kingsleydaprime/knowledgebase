# References and `const`

**[Beginner]** — References are the first thing C++ added that changes how you write every function signature. `const` is the first thing that changes how you think about them.

## References

```cpp
int x = 5;
int &ref = x;        // ref IS x — an alias, not a copy, not a pointer
ref = 10;            // x is now 10
```

A reference is another name for an existing object. Compared to a pointer:

| | Pointer | Reference |
|---|---|---|
| Can be null | yes | **no** |
| Can be reseated | yes | **no** — bound at initialisation, forever |
| Must be initialised | no | **yes** |
| Syntax to use | `*p`, `p->x` | `r`, `r.x` |
| Arithmetic | yes | no |

```cpp
int &ref;            // ERROR — must be initialised
int &ref = x;
ref = y;             // does NOT rebind — this ASSIGNS y's value into x
```

That last line is the one to internalise: after binding, a reference *is* the object, so every operation on it operates on the referent.

**Use a reference when the thing must exist. Use a pointer when it might not.** That's the whole rule, and it's why C++ signatures are mostly references while C's are all pointers.

```cpp
void modify(int &x)  { x = 42; }        // must have a value
void maybe(int *x)   { if (x) *x = 42; } // may be null
```

Under the hood a reference is usually a pointer the compiler dereferences for you. The difference is entirely in what the type system permits.

## Passing arguments

The three ways, and when each is right:

```cpp
void by_value(std::string s);          // COPIES — expensive for big objects
void by_ref(std::string &s);           // no copy, and CAN modify
void by_const_ref(const std::string &s); // no copy, CANNOT modify — the default
```

> **`const T&` is the default for anything larger than a pointer.** No copy, no null, and the signature documents that you won't modify it.

```cpp
void by_value(int n);                   // for small types, by value is FASTER
```

Small trivially-copyable types — `int`, `double`, a pointer, a two-field struct — should go by value. A reference is an indirection; copying 4 bytes is cheaper than dereferencing. The usual threshold is "bigger than 2 pointers, or non-trivial to copy".

There's a fourth case once you know move semantics — taking by value to sink a parameter. → [[languages/05-cpp/04-copy-move-and-the-rule-of-five|Copy, Move and the Rule of Five]]

## The dangling reference

References don't protect you from lifetime bugs:

```cpp
const std::string &bad() {
    std::string local = "hello";
    return local;                     // DANGLING — local dies here
}                                      // UB when the caller reads it
```

```cpp
const int &r = vec[0];
vec.push_back(x);                     // may reallocate
std::cout << r;                       // DANGLING — the buffer moved
```

This is exactly the case [[languages/03-rust/05-lifetimes|Rust's lifetimes]] exist to prevent, and it's why "C++ is safer than C" is only partly true. The compiler will warn about the first (`-Wreturn-local-addr`) and cannot see the second.

**Const references extend the lifetime of a temporary**, which is a genuine and useful exception:

```cpp
const std::string &r = make_string();   // the temporary lives as long as r
```

That's how `const T&` parameters can bind to temporaries — which is why `f("literal")` works for `void f(const std::string&)`.

## `const`

```cpp
const int x = 5;                  // can't modify x
const int *p;                     // pointer to const int  — can't write *p
int *const p = &x;                // const pointer         — can't reassign p
const int *const p = &x;          // neither
```

**Read right to left**, same as C. `const int *const p` is "p is a const pointer to a const int".

C++ adds `const` **member functions**, which is where it becomes structural:

```cpp
class Counter {
    int n = 0;
public:
    int  get() const { return n; }     // promises not to modify the object
    void inc()       { ++n; }
};

const Counter c;
c.get();            // fine
c.inc();            // ERROR — can't call a non-const method on a const object
```

The `const` after the parameter list means "this method doesn't modify `*this`". It's the mechanism that makes `const T&` parameters actually useful — through a `const` reference you can only call `const` methods.

### `const` correctness

The discipline: **mark everything `const` that can be.** Parameters, member functions, local variables, member data where possible.

```cpp
class Rect {
    double w_, h_;
public:
    double area() const { return w_ * h_; }        // const
    double width() const { return w_; }            // const
    void scale(double f) { w_ *= f; h_ *= f; }     // not const, obviously
};

void print(const Rect &r) {
    std::cout << r.area();     // only works because area() is const
}
```

Forget one `const` on a getter and every `const&` parameter downstream breaks. This propagates, which is why `const` correctness is something you do from the start rather than retrofit.

`mutable` is the escape hatch for members that don't affect logical state — a cache, a mutex:

```cpp
class Widget {
    mutable std::mutex mu_;
    mutable std::optional<int> cached_;
public:
    int value() const {                     // logically const...
        std::lock_guard lock(mu_);          // ...but must lock
        if (!cached_) cached_ = compute();
        return *cached_;
    }
};
```

Use it for exactly that. `mutable` on ordinary state is a lie in the signature.

### `constexpr` vs `const`

```cpp
const int a = f();          // runtime constant — can't change after init
constexpr int b = 42;       // COMPILE-TIME constant
```

`constexpr` is a much stronger claim and can be used where a compile-time value is required (array sizes, template arguments). → [[languages/05-cpp/12-constexpr-and-compile-time|constexpr]]

## `auto`

```cpp
auto x = 5;                        // int
auto s = std::string("hi");        // std::string
auto it = v.begin();               // std::vector<int>::iterator — saves real typing
const auto &r = get_thing();       // deduced, no copy
```

`auto` deduces the type from the initialiser. It's essential once templates and iterators arrive, where the real type is unwriteable.

**The trap:** `auto` strips references and `const` by default.

```cpp
auto x = obj.get_ref();            // COPIES, even if get_ref returns T&
auto &x = obj.get_ref();           // binds by reference
const auto &x = obj.get_ref();     // the safe default for reading
```

Writing `auto x = ...` in a range-for over big objects is a common accidental-copy bug:

```cpp
for (auto item : big_vector) { }        // copies every element
for (const auto &item : big_vector) { } // correct
for (auto &item : big_vector) { }       // to modify
```

> **`const auto&` in range-for unless you're modifying.** This single habit removes a whole class of silent performance loss.

`auto` in function return position (C++14) is fine for short functions; it hurts readability on public APIs where the caller has to read the body to know the type.

## `nullptr`

```cpp
void f(int);
void f(char *);

f(NULL);        // AMBIGUOUS — NULL is 0, which is an int
f(nullptr);     // unambiguous — nullptr has type std::nullptr_t
```

**Use `nullptr`, never `NULL` or `0`** for pointers. `NULL` in C++ is just `0`, which is an integer, which breaks overload resolution and template deduction.

---

## Related
- [[languages/05-cpp/03-classes-and-raii|Classes and RAII]] — where `const` methods matter
- [[languages/05-cpp/04-copy-move-and-the-rule-of-five|Copy, Move and the Rule of Five]] — the fourth way to pass an argument
- [[languages/04-c/05-pointers|C: Pointers]] — what references replace
- [[languages/03-rust/04-borrowing-and-references|Rust: Borrowing]] — references with lifetimes attached
- [[languages/05-cpp/README|C++ course map]]
