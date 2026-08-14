# Classes and RAII

**[Beginner → Intermediate]** — The single most important idea in C++, and the one worth stealing into every other language you write.

## Classes

```cpp
class Rectangle {
private:                          // default for `class`
    double width_, height_;

public:
    Rectangle(double w, double h) : width_(w), height_(h) {}   // constructor

    double area() const { return width_ * height_; }
    void scale(double f) { width_ *= f; height_ *= f; }
};
```

```cpp
struct Point { double x, y; };    // `struct` = class with default PUBLIC access
```

`class` and `struct` differ **only** in default access. Convention: `struct` for passive data with public members, `class` when there are invariants to protect.

Access levels: `private` (this class only), `protected` (this class and derived), `public` (everyone). C++ has no package/module-level access, so `friend` exists as the escape hatch — use it sparingly, usually for operator overloads.

### Member initialiser lists

```cpp
Rectangle(double w, double h) : width_(w), height_(h) {}      // initialise
Rectangle(double w, double h) { width_ = w; height_ = h; }    // default-construct, then ASSIGN
```

The first **initialises**; the second default-constructs the members and then assigns over them. For an `int` that's identical; for a `std::string` it's a wasted construction, and for a `const` member or a reference member the second form **doesn't compile at all**.

**Always use the initialiser list.** Members are initialised in **declaration order**, not the order you write in the list — `-Wreorder` warns when they differ, and you should listen.

```cpp
class Widget {
    int a_, b_;
public:
    Widget(int x) : b_(x), a_(b_) {}   // BUG: a_ is initialised FIRST, from garbage b_
};
```

## RAII

**Resource Acquisition Is Initialisation.** The name is bad and the idea is the best one in the language:

> **Acquire a resource in a constructor. Release it in the destructor. The object's lifetime *is* the resource's lifetime.**

```cpp
class FileHandle {
    FILE *f_;
public:
    explicit FileHandle(const char *path) : f_(std::fopen(path, "r")) {
        if (!f_) throw std::runtime_error("cannot open file");
    }
    ~FileHandle() { if (f_) std::fclose(f_); }      // ALWAYS runs on scope exit

    FILE *get() const { return f_; }
};

void process() {
    FileHandle f("data.txt");
    do_work(f.get());
    // fclose happens here. On a normal return, an early return, OR an exception.
}
```

Compare the [[languages/04-c/07-memory-management|C version]]:

```c
int process(void) {
    FILE *f = fopen("data.txt", "r");
    if (!f) return -1;
    if (do_work(f) != 0) { fclose(f); return -1; }   // remember to close
    fclose(f);                                        // remember again
    return 0;
}
```

Every exit path has to remember. RAII makes forgetting **impossible**, because the destructor is called by the language.

### Why it's stronger than the alternatives

| Mechanism | Problem |
|---|---|
| `goto cleanup` (C) | you must write it, every time, in every function |
| `try/finally` (Java) | you must write it, at every call site |
| `defer` (Go) | you must write it, at every acquisition |
| `with` (Python) | you must write it, and only in that block |
| **destructor (C++)** | **written once, in the class. Every user gets it automatically** |

That's the distinction: RAII puts the cleanup in the **type**, so no caller can forget. Every other mechanism puts it at the *call site*, where it's one omission away from a leak.

The other mechanisms also don't compose. An object holding three RAII members releases all three, in reverse order, automatically — no nesting required.

### It's not just memory

The pattern applies to every resource with an acquire/release pair:

```cpp
std::lock_guard<std::mutex> lock(mu);   // unlocks on scope exit, even on exception
std::unique_ptr<Widget> w = ...;         // deletes
std::fstream file("x.txt");              // closes
```

Locks are the strongest case. A `mutex.lock()` / `mutex.unlock()` pair with an exception or an early return between them is a deadlock; `lock_guard` makes that unrepresentable.

## Destructors

```cpp
~Rectangle() { }                    // called automatically at end of scope
```

Destruction is **deterministic** — at end of scope, in **reverse construction order**. Not "eventually", not "when the GC runs". That determinism is what makes RAII work for scarce resources like file descriptors and locks, where a finaliser in a GC'd language is useless.

Two rules:

**Never let a destructor throw.** Destructors are implicitly `noexcept`; throwing from one during stack unwinding calls `std::terminate`. If cleanup can fail, provide an explicit `close()` that reports it, and have the destructor swallow.

**Any class meant for inheritance needs a `virtual` destructor:**

```cpp
class Base {
public:
    virtual ~Base() = default;      // WITHOUT virtual, deleting via Base* is UB
};

Base *p = new Derived();
delete p;                            // only calls ~Base() unless it's virtual → leak
```

→ [[languages/05-cpp/06-inheritance-and-virtual-dispatch|Inheritance and Virtual Dispatch]]

## Constructors in detail

```cpp
class Widget {
public:
    Widget() = default;                          // default constructor
    explicit Widget(int n);                      // one argument — mark it explicit
    Widget(int n, std::string s);
    Widget(std::initializer_list<int> vals);     // for Widget{1, 2, 3}
};
```

**`explicit` on any single-argument constructor.** Without it, C++ will implicitly convert:

```cpp
class Buffer { public: Buffer(int size); };      // not explicit

void f(Buffer b);
f(42);                                            // compiles — creates a 42-byte Buffer
```

That implicit conversion is almost never what you want and produces genuinely confusing bugs. Mark it `explicit` and `f(42)` becomes a compile error.

### Delegating and defaulted

```cpp
class Widget {
    int a_, b_;
public:
    Widget(int a, int b) : a_(a), b_(b) {}
    Widget(int a) : Widget(a, 0) {}      // delegates to the other constructor

    Widget() = default;                   // ask for the compiler's version
    Widget(const Widget&) = delete;       // explicitly FORBID copying
};
```

`= delete` is how you make a type non-copyable, and it produces a clear error rather than a link failure.

### The brace-initialisation trap

```cpp
std::vector<int> a(5, 0);     // 5 elements, all 0
std::vector<int> b{5, 0};     // TWO elements: 5 and 0
```

Braces prefer `std::initializer_list` constructors when one exists. This is C++'s "most vexing" modern gotcha. Braces are otherwise better — they prevent narrowing conversions — but for containers with size arguments, use parentheses.

The *actual* most vexing parse:

```cpp
Widget w();        // declares a FUNCTION named w returning Widget — not a variable
Widget w;          // what you meant
Widget w{};        // also what you meant, unambiguously
```

## Static members

```cpp
class Counter {
    static inline int count_ = 0;        // C++17: define inline, in the header
public:
    Counter() { ++count_; }
    static int count() { return count_; }   // no `this`
};

Counter::count();
```

Before C++17, a static data member needed a separate definition in exactly one `.cpp` — a classic source of linker errors. `static inline` fixes that.

## Special member functions

The compiler will generate six functions if you don't:

```cpp
Widget();                            // default constructor
~Widget();                           // destructor
Widget(const Widget&);               // copy constructor
Widget& operator=(const Widget&);    // copy assignment
Widget(Widget&&);                    // move constructor
Widget& operator=(Widget&&);         // move assignment
```

Which ones it generates, and when writing one suppresses another, is the **rule of zero/three/five** — the next note, and the thing that most often silently breaks a class that manages a resource.

## Practical rules

1. **RAII for every resource.** Memory, files, locks, sockets, connections.
2. **Member initialiser lists**, in declaration order.
3. **`explicit` on single-argument constructors.**
4. **`virtual ~Base()`** on anything with virtual functions.
5. **Destructors never throw.**
6. **`const` on every method that doesn't modify.**
7. **Prefer the standard library's RAII types** — `std::unique_ptr`, `std::lock_guard`, `std::fstream` — over writing your own. → [[languages/05-cpp/05-smart-pointers-and-ownership|Smart Pointers]]

---

## Related
- [[languages/05-cpp/04-copy-move-and-the-rule-of-five|Copy, Move and the Rule of Five]] — what happens when your class owns something
- [[languages/05-cpp/05-smart-pointers-and-ownership|Smart Pointers and Ownership]] — RAII for memory, off the shelf
- [[languages/03-rust/03-ownership|Rust: Ownership]] — RAII promoted from convention to rule
- [[languages/04-c/07-memory-management|C: Memory Management]] — what you'd write without it
- [[languages/05-cpp/README|C++ course map]]
