# Smart Pointers and Ownership

**[Intermediate]** — RAII for memory, off the shelf. The reason modern C++ contains almost no `new` and no `delete` at all.

## Why

```cpp
Widget *w = new Widget();
do_something();               // if this throws, w LEAKS
delete w;
```

Manual `new`/`delete` has every failure mode from [[languages/04-c/07-memory-management|C's memory management]], plus exceptions creating new paths out of a function that skip your `delete`.

Smart pointers apply [[languages/05-cpp/03-classes-and-raii|RAII]]: the pointer is an object, and its destructor frees.

> **Modern C++ rule: no raw `new`, no raw `delete`, ever.** If you type `delete`, you're writing 2005 C++ or implementing a container.

## `std::unique_ptr` — the default

```cpp
#include <memory>

auto w = std::make_unique<Widget>(arg1, arg2);   // ALWAYS prefer make_unique
std::unique_ptr<Widget> w(new Widget());          // works; don't

w->method();
(*w).method();
Widget *raw = w.get();          // borrow, without transferring ownership
w.reset();                       // delete now
w.reset(new Widget());           // delete and take a new one
Widget *r = w.release();         // give up ownership — YOU must delete it now
if (w) { }                       // null check
```

**Exactly one owner.** `unique_ptr` is move-only — it cannot be copied:

```cpp
auto a = std::make_unique<Widget>();
auto b = a;                       // ERROR — copy is deleted
auto b = std::move(a);            // ownership transfers; a is now null
```

This is [[languages/03-rust/03-ownership|Rust's ownership]] as a library type. The difference is that Rust makes using the moved-from `a` a compile error; C++ leaves you a null pointer to dereference.

**Zero overhead.** A `unique_ptr` is the size of a raw pointer, and its operations inline away. There is no reason to use a raw owning pointer instead.

```cpp
auto arr = std::make_unique<int[]>(100);    // array form — calls delete[]
arr[0] = 1;
```

### Custom deleters

```cpp
auto closer = [](FILE *f) { if (f) std::fclose(f); };
std::unique_ptr<FILE, decltype(closer)> file(std::fopen("x.txt", "r"), closer);
```

This is how you wrap any C API's create/destroy pair without writing a class — and it's the answer to "should I write my own RAII wrapper?" most of the time. → [[languages/04-c/09-the-standard-library|C's stdlib]] is full of these pairs.

## `std::shared_ptr` — when ownership is genuinely shared

```cpp
auto a = std::make_shared<Widget>();
auto b = a;                        // both own it; refcount == 2
std::cout << a.use_count();        // 2
```

Reference counted. The object is destroyed when the last `shared_ptr` goes away.

**It is not free:**

- **Two allocations** with `new` (control block + object); **one** with `make_shared`, which is why you use it
- **Twice the size** of a raw pointer (object pointer + control block pointer)
- **Atomic refcount updates** on every copy and destruction — a real cost in hot paths and across threads
- **Thread-safe count, NOT thread-safe object.** Two threads sharing a `shared_ptr<Widget>` still need a mutex around the `Widget` itself.

> **Use `unique_ptr` by default. Reach for `shared_ptr` only when ownership is genuinely shared and no single owner outlives the others.** `shared_ptr` everywhere is a common code smell — usually it means nobody worked out who owns what.

## `std::weak_ptr` — breaking cycles

```cpp
struct Node {
    std::shared_ptr<Node> next;
    std::weak_ptr<Node> parent;      // does NOT keep the parent alive
};

if (auto p = node->parent.lock()) {   // returns shared_ptr, or null if it's gone
    p->do_something();
}
```

Two `shared_ptr`s pointing at each other never reach zero and **never free**. Reference counting cannot collect cycles — this is a real leak, not a theoretical one, and it's the classic parent/child tree bug.

The convention, identical to [[languages/03-rust/12-smart-pointers-and-interior-mutability|Rust's `Rc`/`Weak`]]: **owners hold `shared_ptr` downward, back-references are `weak_ptr`.**

`weak_ptr` can't be dereferenced directly — you must `lock()` it, which is what makes checking for expiry unavoidable.

## Expressing ownership in signatures

This is where smart pointers pay off most: **the parameter type documents the ownership contract**, and the compiler enforces it.

```cpp
void observe(const Widget &w);            // I look at it. I don't own it. It must exist.
void observe(const Widget *w);            // same, but may be null.

void consume(std::unique_ptr<Widget> w);  // I TAKE ownership. Caller must std::move.

void share(std::shared_ptr<Widget> w);    // I take part-ownership and may outlive you.

std::unique_ptr<Widget> create();         // I give you ownership.
Widget &get_ref();                        // I keep ownership; here's a view.
```

> **Take `const T&` or `T*` unless you're taking ownership.** Passing `const std::shared_ptr<T>&` to a function that just reads the object is a common mistake — it couples the callee to the ownership model for no reason. Take `const T&`.

That guidance turns a whole category of "who frees this?" questions into something readable from the signature — which is the same thing a doc comment does in [[languages/04-c/11-modular-c-and-project-structure|C]], except the compiler checks it.

## When a raw pointer is still correct

Raw pointers are fine, and idiomatic, for **non-owning observation**:

```cpp
class Widget {
    Parent *parent_;          // non-owning back-reference; parent outlives us
public:
    void set_parent(Parent *p) { parent_ = p; }
};
```

The rule: **a raw pointer never owns.** It's a nullable view. If it might be null, use `T*`; if it can't, use `T&`.

## `new` and `delete`, for completeness

```cpp
Widget *w = new Widget();      // allocate + construct
delete w;                       // destruct + deallocate

int *arr = new int[100];
delete[] arr;                   // MUST match — delete on new[] is UB
```

You need to recognise these in older code. Two classic bugs:

**Mismatched forms** — `delete` on a `new[]` allocation is UB.

**Deleting a derived object through a base pointer without a virtual destructor:**

```cpp
Base *p = new Derived();
delete p;                        // UB unless ~Base() is virtual → leaks the Derived part
```

→ [[languages/05-cpp/06-inheritance-and-virtual-dispatch|Inheritance and Virtual Dispatch]]

## `std::optional` — absence without a pointer

```cpp
#include <optional>

std::optional<Widget> find(int id) {
    if (!exists(id)) return std::nullopt;
    return Widget(id);
}

if (auto w = find(42)) {
    w->use();
}
int v = opt.value_or(0);
```

Since C++17, this is the right way to express "might not be there" for a **value** — no pointer, no allocation, no null. It's `Option<T>` from [[languages/03-rust/07-option-and-result|Rust]], with one important difference: **`*opt` on an empty optional is undefined behaviour**, not a compile error. `.value()` throws instead; `operator*` doesn't check.

Related C++17 vocabulary types:

```cpp
std::variant<int, std::string>    // a type-safe union → tagged union, checked
std::any                          // holds anything; requires any_cast
std::span<T>                      // C++20: a non-owning pointer + length view
std::string_view                  // a non-owning view into a string
```

`std::span` and `std::string_view` are the fix for [[languages/04-c/06-arrays-strings-and-decay|C's array decay]] — a pointer that carries its length:

```cpp
void process(std::span<const int> data) {    // accepts vector, array, C array
    for (int x : data) { }                    // knows its size
}
```

**Views don't own.** A `string_view` into a temporary dangles exactly like a reference does:

```cpp
std::string_view sv = std::string("temp");   // DANGLING immediately
```

## Practical rules

1. **`make_unique` by default.** No raw `new`.
2. **`shared_ptr` only for genuinely shared ownership**, and prefer `make_shared`.
3. **`weak_ptr` for back-references**, to break cycles.
4. **Raw pointers and references never own** — they observe.
5. **Take `const T&` unless you're taking ownership.**
6. **`std::optional` for maybe-a-value**, not a pointer.
7. **`std::span` / `std::string_view` for non-owning views**, and watch their lifetimes.

---

## Related
- [[languages/05-cpp/03-classes-and-raii|Classes and RAII]] — the mechanism these are built on
- [[languages/05-cpp/04-copy-move-and-the-rule-of-five|Copy, Move and the Rule of Five]] — why `unique_ptr` is move-only
- [[languages/03-rust/12-smart-pointers-and-interior-mutability|Rust: Smart Pointers]] — `Box`/`Rc`/`Weak`, the same set
- [[languages/04-c/07-memory-management|C: Memory Management]] — what this replaces
- [[languages/05-cpp/README|C++ course map]]
