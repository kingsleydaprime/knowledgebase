---
id: 9320f58f-0968-488b-9b10-a17385d4db22
---

# Inheritance and Virtual Dispatch

Inheritance is building a new class on top of an existing one, and virtual dispatch is how C++ picks the right version of a function at run time. In a game, a dog and a cat might both be animals, and calling "make sound" on any animal should give the right noise. This lesson shows how that works and the mistakes to avoid.

## Inheritance
<!-- bite: ea2637ee-0d9b-4826-98c8-45641d8645a9 -->

```cpp
class Animal {
protected:
    std::string name_;
public:
    explicit Animal(std::string n) : name_(std::move(n)) {}
    virtual ~Animal() = default;                 // ESSENTIAL — see below

    virtual void speak() const = 0;              // pure virtual → abstract class
    virtual std::string describe() const {       // virtual with a default
        return name_ + " is an animal";
    }
    const std::string &name() const { return name_; }   // non-virtual
};

class Dog : public Animal {
public:
    explicit Dog(std::string n) : Animal(std::move(n)) {}

    void speak() const override { std::cout << name_ << " says woof\n"; }
    std::string describe() const override { return name_ + " is a dog"; }
};
```

- **`virtual`** — this function can be overridden, and calls dispatch on the *runtime* type
- **`= 0`** — pure virtual. The class is abstract and can't be instantiated
- **`override`** — always write it; see below
- **`public` inheritance** means "is-a". `private` inheritance means "implemented-in-terms-of" and is rare — prefer composition

## Virtual dispatch and the vtable
<!-- bite: 5f25ddd7-1ceb-4942-ad77-c76d8a2aaaeb -->

```cpp
std::unique_ptr<Animal> a = std::make_unique<Dog>("Rex");
a->speak();          // calls Dog::speak — resolved at RUNTIME
```

How: each polymorphic class gets a **vtable** — a static array of function pointers — and each object gets a hidden **vptr** pointing at its class's vtable.

```text
Dog object            Dog vtable
┌──────────────┐     ┌──────────────────────┐
│ vptr    ─────┼────→│ ~Dog                 │
│ name_        │     │ Dog::speak           │
└──────────────┘     │ Dog::describe        │
                     └──────────────────────┘
```

A virtual call is: load the vptr, index the vtable, call through the pointer. **Two indirections and no inlining** — the last part usually costs more than the loads.

This is **exactly** the struct-of-function-pointers you'd write by hand in [[languages/04-c/05-pointers|C]], and exactly what [[languages/03-rust/09-traits|Rust's `dyn Trait`]] does. C++ just generates it. Having written one manually in C, the cost model is obvious rather than mysterious.

The costs, concretely:
- **+8 bytes per object** for the vptr — significant for small, numerous objects
- **No inlining** through a virtual call unless the compiler can devirtualise
- **A cache miss** for the vtable lookup, in cold code

`final` lets the compiler devirtualise when it can prove the type:

```cpp
class Dog final : public Animal { };        // nobody can derive from Dog
void speak() const final;                    // nobody can override this
```

## The virtual destructor rule
<!-- bite: d36254cf-a1e8-4fd2-8954-1ecbc53569e6 -->

```cpp
class Base { public: ~Base() {} };           // NOT virtual
class Derived : public Base { std::vector<int> data_; };

Base *p = new Derived();
delete p;                                     // UB — only ~Base runs. data_ leaks.
```

> **If a class has any virtual function, it needs a virtual destructor.** If it's meant to be a base class, it needs a virtual destructor.

```cpp
virtual ~Base() = default;
```

The alternative, for a base class not meant to be deleted polymorphically, is a `protected` non-virtual destructor — which makes `delete p` through a `Base*` a compile error instead of UB.

## `override` and `final`
<!-- bite: 487ba2ee-fe05-4d7a-b5d9-b7b18019326b -->

```cpp
class Dog : public Animal {
    void speak() override;              // compiler CHECKS this overrides something
};
```

Without `override`, a signature mismatch silently creates a *new* function instead of overriding:

```cpp
class Animal { virtual void speak() const; };
class Dog : public Animal {
    void speak();                       // missing const → NEW function, not an override
                                        // Animal::speak still called through a base ptr
};
```

That bug is silent, common, and produces "my override isn't being called". **Always write `override`.** Turn on `-Wsuggest-override`.

## Object slicing
<!-- bite: ad3ad6b5-a6b9-4969-9666-c47a6c8cf931 -->

The trap that has no equivalent in reference-based languages:

```cpp
void process(Animal a);            // BY VALUE — takes an Animal
Dog d("Rex");
process(d);                        // SLICED — only the Animal part is copied
                                   // virtual dispatch is lost; a.speak() calls Animal::speak
```

Copying a `Dog` into an `Animal`-sized slot literally discards everything the derived class added. It compiles without a warning.

> **Polymorphism requires a pointer or a reference.** `Animal&`, `Animal*`, `unique_ptr<Animal>` — never `Animal` by value.

Making the base class abstract (any pure virtual) prevents slicing, because you then can't have an `Animal` by value at all. That's a good reason to have at least one pure virtual in an interface.

## Multiple inheritance and the diamond
<!-- bite: f395c8a9-f10e-4a41-8817-250403b64783 -->

C++ allows multiple inheritance, which produces the diamond problem:

```cpp
class A { public: int x; };
class B : public A {};
class C : public A {};
class D : public B, public C {};      // D has TWO copies of A::x

D d;
d.x;                                   // ambiguous — B::x or C::x?
d.B::x;                                // must qualify
```

```cpp
class B : virtual public A {};        // virtual inheritance — ONE shared A
class C : virtual public A {};
class D : public B, public C {};      // d.x is now unambiguous
```

Virtual inheritance adds runtime cost and complicates construction (the most-derived class initialises the virtual base). Later languages banned this entirely — Java allows multiple *interface* inheritance only, Rust has traits with no data.

**The practical rule: inherit from at most one class with data, and any number of pure-interface classes.**

```cpp
class Drawable { public: virtual ~Drawable() = default; virtual void draw() const = 0; };
class Serialisable { public: virtual ~Serialisable() = default; virtual std::string to_json() const = 0; };

class Widget : public Drawable, public Serialisable { };    // fine — no data, no diamond
```

## Why modern C++ uses less inheritance
<!-- bite: e5fce2c7-7993-43bd-834e-53fa9ad589b1 -->

1990s C++ taught deep hierarchies. Current practice doesn't, for reasons that hold across languages:

- **Fragile base class** — changing a base breaks derived classes in ways you can't see from the base
- **Tight coupling** — inheritance is the strongest coupling available
- **It forces runtime dispatch** where compile-time would do
- **Slicing** — a whole bug class that composition doesn't have

The alternatives, in rough order of preference:

**Composition** — hold the thing rather than being it:

```cpp
class Car {
    Engine engine_;              // has-a, not is-a
    std::vector<Wheel> wheels_;
};
```

**Templates for static polymorphism** — no vtable, fully inlinable:

```cpp
template <typename Shape>
double total_area(const std::vector<Shape> &shapes) {
    double t = 0;
    for (const auto &s : shapes) t += s.area();     // resolved at COMPILE time
    return t;
}
```

**Type erasure** — `std::function` is the everyday example, letting you store any callable without a hierarchy:

```cpp
std::vector<std::function<void()>> callbacks;
```

**`std::variant` + `std::visit`** — a closed set of types, checked exhaustively:

```cpp
using Shape = std::variant<Circle, Square, Triangle>;

double area(const Shape &s) {
    return std::visit([](const auto &x) { return x.area(); }, s);
}
```

This is the [[languages/03-rust/06-structs-enums-and-pattern-matching|sum type]] approach, and it's better than inheritance when the set of types is **closed and known**. Inheritance is better when it's **open** — plugins, user-extensible types.

> **The rule of thumb: use inheritance for open sets of types that share behaviour and need runtime dispatch. Use `variant` for closed sets. Use templates when the type is known at compile time. Use composition for everything else.**

## RTTI
<!-- bite: 08a71515-af65-45fc-9b57-aa5eb4d2daa0 -->

```cpp
Animal *a = get_animal();
if (Dog *d = dynamic_cast<Dog *>(a)) { }        // null if it isn't a Dog
Dog &d = dynamic_cast<Dog &>(*a);                // THROWS std::bad_cast if not

std::cout << typeid(*a).name();                  // implementation-defined string
```

`dynamic_cast` is checked at runtime and requires RTTI to be enabled. It's relatively slow, and **frequent `dynamic_cast` is a design smell** — it usually means a virtual function is missing, or `variant` was the right model.

Many projects (games, embedded) compile with `-fno-rtti` to save binary size, which disables `dynamic_cast` and `typeid` entirely.

## Practical rules
<!-- bite: 7e22ef95-5d61-4537-b9a0-b964a7a0e95e -->

1. **`virtual ~Base() = default`** on any polymorphic base.
2. **`override` on every override.** `final` where it helps.
3. **Never pass polymorphic types by value** — slicing.
4. **At most one data-carrying base**, any number of pure interfaces.
5. **Prefer composition.** Inheritance is the strongest coupling you can create.
6. **`variant` for closed sets**, inheritance for open ones.
7. **Frequent `dynamic_cast` means the design is wrong.**

---

## Related
<!-- bite: 13f661f5-f4ca-4aea-96ce-0fd97cd5b72c -->
- [[languages/05-cpp/08-templates-and-concepts|Templates and Concepts]] — static polymorphism
- [[languages/05-cpp/09-the-stl-containers|The STL Containers]] — `std::variant` and friends
- [[languages/03-rust/09-traits|Rust: Traits]] — no inheritance at all
- [[languages/04-c/05-pointers|C: Function Pointers]] — the vtable, by hand
- [[concepts/02-design-patterns/index|Design Patterns]] — most of which are about avoiding this
- [[languages/05-cpp/index|C++ course map]]

## About this lesson
<!-- bite: 5817c3e3-083c-470f-9226-61a6c6a9cd4d -->

**Level:** Intermediate. **Covers:** How polymorphism actually works, what a vtable costs, and why modern C++ uses far less inheritance than 1990s C++ did.
