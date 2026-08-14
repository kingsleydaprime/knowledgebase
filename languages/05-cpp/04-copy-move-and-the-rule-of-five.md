# Copy, Move and the Rule of Five

**[Intermediate]** — What happens when your class owns a resource, why C++11's move semantics were the biggest change in the language's history, and the rule that keeps you out of trouble.

## The problem

```cpp
class Buffer {
    char *data_;
    size_t size_;
public:
    explicit Buffer(size_t n) : data_(new char[n]), size_(n) {}
    ~Buffer() { delete[] data_; }
};

Buffer a(100);
Buffer b = a;        // the compiler-generated copy constructor copies the POINTER
```

Now `a.data_` and `b.data_` are the same address, and both destructors run `delete[]` on it. **Double free.** This is the C bug from [[languages/04-c/07-memory-management|Memory Management]], arrived at by writing nothing at all.

The compiler's generated copy is a **shallow, member-by-member copy**. That's correct for an `int` and wrong for anything that owns a resource.

## Copy semantics

```cpp
Buffer(const Buffer &other)                       // copy constructor
    : data_(new char[other.size_]), size_(other.size_) {
    std::memcpy(data_, other.data_, size_);
}

Buffer& operator=(const Buffer &other) {          // copy assignment
    if (this == &other) return *this;             // self-assignment check
    char *tmp = new char[other.size_];            // allocate BEFORE freeing
    std::memcpy(tmp, other.data_, other.size_);
    delete[] data_;
    data_ = tmp;
    size_ = other.size_;
    return *this;
}
```

Two details that matter: **check for self-assignment**, and **allocate before you free** so a throwing `new` leaves the object intact. That second point is basic exception safety. → [[languages/05-cpp/11-exceptions-and-error-handling|Exceptions]]

The **copy-and-swap idiom** gets both properties for free:

```cpp
Buffer& operator=(Buffer other) {       // note: BY VALUE — the copy happens here
    swap(*this, other);
    return *this;
}                                        // `other` (holding the old data) dies here
```

Strong exception safety, self-assignment-safe, and it handles move assignment too. It costs one extra move in some cases. Worth knowing; not always worth using.

## Move semantics — the C++11 change

Copying is often wasteful. Returning a `std::vector` from a function, or pushing a `std::string` into a container, historically copied the whole buffer, then destroyed the original.

**A move transfers ownership** instead: steal the pointer, null the source, no allocation.

```cpp
Buffer(Buffer &&other) noexcept                   // move constructor
    : data_(other.data_), size_(other.size_) {
    other.data_ = nullptr;                        // leave the source VALID but empty
    other.size_ = 0;
}

Buffer& operator=(Buffer &&other) noexcept {      // move assignment
    if (this == &other) return *this;
    delete[] data_;
    data_ = other.data_;
    size_ = other.size_;
    other.data_ = nullptr;
    other.size_ = 0;
    return *this;
}
```

`Buffer&&` is an **rvalue reference** — it binds to temporaries and to things you've explicitly said you're done with.

> **The moved-from object must be left in a valid but unspecified state.** Its destructor will still run. Nulling the pointer is what makes `delete[] nullptr` a harmless no-op.

### `noexcept` on moves is not optional

`std::vector` will only use your move constructor when reallocating if it's `noexcept`. Otherwise it copies, because it can't provide its strong exception guarantee if a move might throw halfway through.

A move constructor that isn't marked `noexcept` silently costs you every performance benefit you wrote it for. Mark them.

## lvalues, rvalues, and `std::move`

```cpp
int x = 5;
int &lref = x;          // lvalue reference — binds to named objects
int &&rref = 5;         // rvalue reference — binds to temporaries
```

Roughly: an **lvalue** has a name and an address you could take. An **rvalue** is a temporary about to expire.

```cpp
Buffer a(100);
Buffer b = a;                  // a is an lvalue → COPY
Buffer c = make_buffer();      // the return is an rvalue → MOVE
Buffer d = std::move(a);       // explicitly say "treat a as expiring" → MOVE
```

**`std::move` doesn't move anything.** It's a cast to `T&&` — it changes overload resolution so the move constructor is selected. The move happens in the constructor you wrote.

```cpp
Buffer a(100);
Buffer b = std::move(a);
a.size();                      // a is valid but EMPTY — don't rely on its contents
```

Using a moved-from object is legal but its value is unspecified. For standard types the guarantee is that it's valid to destroy and assign to; a moved-from `std::string` is usually empty but you shouldn't depend on it.

## The rule of zero / three / five

**Rule of Three (pre-C++11):** if you need any of destructor, copy constructor, copy assignment, you almost certainly need all three — because needing one means you're managing a resource.

**Rule of Five (C++11):** add move constructor and move assignment.

**Rule of Zero — the one to actually follow:**

> **Design your classes so you need none of them.** Use RAII members that manage themselves, and let the compiler generate everything.

```cpp
class Buffer {
    std::vector<char> data_;          // manages itself
public:
    explicit Buffer(size_t n) : data_(n) {}
    // no destructor, no copy, no move — all correct, all generated
};
```

That class is correct, exception-safe, movable and copyable, and you wrote none of it. **The vast majority of classes should look like this.** Write the five only when you're implementing a resource wrapper — and even then, prefer `std::unique_ptr` with a custom deleter. → [[languages/05-cpp/05-smart-pointers-and-ownership|Smart Pointers]]

### The suppression rules, which bite silently

The generation rules are genuinely tricky, and getting caught by them is common:

- **Declaring a destructor, copy constructor, or copy assignment suppresses the implicit MOVE operations.** Your class silently falls back to copying.
- **Declaring a move operation deletes the copy operations.**
- A user-declared constructor of any kind suppresses the default constructor.

```cpp
class Widget {
    std::vector<int> data_;
public:
    ~Widget() { log("destroyed"); }    // just a log line...
};
// ...and now Widget has NO move constructor. Every "move" copies the vector.
```

That's a real and invisible performance bug. If you declare any of the five, declare all of them (`= default` is fine):

```cpp
class Widget {
public:
    ~Widget() { log("destroyed"); }
    Widget(const Widget&) = default;
    Widget& operator=(const Widget&) = default;
    Widget(Widget&&) = default;
    Widget& operator=(Widget&&) = default;
};
```

## Copy elision and RVO

```cpp
std::vector<int> make() {
    std::vector<int> v{1, 2, 3};
    return v;                        // NOT a copy, and not even a move
}
auto x = make();
```

**Return Value Optimisation** constructs the object directly in the caller's storage. Since C++17 this is *mandatory* for temporaries, not just permitted.

```cpp
return std::move(v);       // WORSE — this DEFEATS RVO by making it an rvalue expression
```

**Don't `std::move` a return value.** It's a pessimisation, and `-Wpessimizing-move` warns about it. Just `return v;`.

## Perfect forwarding, briefly

```cpp
template <typename T>
void wrapper(T &&arg) {                    // a FORWARDING reference, not an rvalue ref
    target(std::forward<T>(arg));          // preserves lvalue-ness / rvalue-ness
}
```

`T&&` in a **deduced template context** is a forwarding reference: it binds to both lvalues and rvalues, and `std::forward` passes the value category through unchanged. Using `std::move` here would wrongly move an lvalue the caller still owns.

This is what `std::make_unique` and `emplace_back` are built on. You need it when writing generic wrappers, and rarely otherwise.

```cpp
v.push_back(Widget(1, 2));      // constructs a temporary, then moves it
v.emplace_back(1, 2);           // constructs IN PLACE from the arguments
```

## Practical rules

1. **Rule of Zero.** Use RAII members; write none of the five.
2. **If you write one, write all five** (or `= default` them).
3. **`noexcept` on move operations**, or containers won't use them.
4. **Leave moved-from objects valid.**
5. **Don't `std::move` a return value.**
6. **`const T&` for reading, `T&&` + `std::move` for sinking, `T` by value for small types.**
7. **`emplace_back` over `push_back(T(...))`.**

## The Rust comparison

Move semantics in C++ are **opt-in and non-destructive** — you say `std::move`, and the source remains a valid object you can still (unwisely) use.

In [[languages/03-rust/03-ownership|Rust]] moves are the **default and destructive** — the source is statically unusable, enforced by the compiler. C++ gave you the performance benefit; Rust made it impossible to use the husk afterwards.

---

## Related
- [[languages/05-cpp/03-classes-and-raii|Classes and RAII]] — the destructors involved
- [[languages/05-cpp/05-smart-pointers-and-ownership|Smart Pointers and Ownership]] — the Rule of Zero, in practice
- [[languages/05-cpp/11-exceptions-and-error-handling|Exceptions]] — why copy assignment allocates first
- [[languages/03-rust/03-ownership|Rust: Ownership]] — moves by default
- [[languages/05-cpp/README|C++ course map]]
