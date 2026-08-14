# Structs, Unions and Layout

**[Intermediate]** — Aggregating data, and the padding rules that decide how much memory it actually takes.

## Structs

```c
struct Point { int x, y; };

struct Point p = {1, 2};
struct Point p = {.x = 1, .y = 2};       // designated initialisers (C99) — prefer these
struct Point p = {0};                     // zero every field

p.x = 5;
struct Point *ptr = &p;
ptr->x = 5;                               // (*ptr).x
```

`typedef` to drop the `struct` keyword:

```c
typedef struct Point { int x, y; } Point;   // named AND typedef'd — best form
Point p;
```

Naming the struct as well as the typedef lets it refer to itself:

```c
typedef struct Node {
    int value;
    struct Node *next;         // needs the struct tag — the typedef isn't defined yet
} Node;
```

Structs **are** copied on assignment and when passed by value, unlike arrays:

```c
struct Point a = {1, 2};
struct Point b = a;            // full copy
void f(struct Point p);        // copies the whole struct
void f(const struct Point *p); // pass a pointer for anything non-trivial
```

For anything beyond a couple of words, pass `const T *`.

## Padding and alignment

The part that surprises people:

```c
struct Bad {
    char  a;      // 1 byte
    int   b;      // 4 bytes
    char  c;      // 1 byte
};
printf("%zu\n", sizeof(struct Bad));    // 12, not 6
```

```
offset: 0    1  2  3    4  5  6  7    8    9 10 11
        [a] [pad pad pad] [   b     ] [c] [pad pad]
```

Each member must sit at an offset that's a multiple of its **alignment** — an `int` at a multiple of 4. The compiler inserts padding to make that true, and pads the whole struct up to a multiple of its largest member's alignment, so arrays of it stay aligned.

**Reorder largest-first and the padding mostly disappears:**

```c
struct Good {
    int   b;      // 4
    char  a;      // 1
    char  c;      // 1
                  // 2 bytes tail padding
};
printf("%zu\n", sizeof(struct Good));   // 8
```

12 → 8 bytes for free. On a million-element array that's 4MB and a meaningfully better cache profile. **Declaring members in descending size order is a free optimisation** worth doing by habit.

```c
#include <stddef.h>
offsetof(struct Bad, b);          // 4 — where a member actually sits
_Alignof(int);                    // 4 (C11)
```

### Packing

```c
#pragma pack(push, 1)
struct Packed { char a; int b; char c; };    // sizeof == 6, no padding
#pragma pack(pop)

struct __attribute__((packed)) Packed2 { ... };   // GCC/Clang
```

Packing removes padding — necessary for a struct that must match a wire format or hardware register layout exactly.

**But:** unaligned access is slower on x86 and a **fault** on some ARM configurations, and taking a pointer to a packed member is undefined behaviour. Use packing only where the layout is dictated externally, and prefer explicit serialisation for wire formats:

```c
// safer than casting a buffer to a packed struct
uint32_t v;
memcpy(&v, buf + 4, sizeof v);
v = ntohl(v);
```

Casting a `char *` buffer to a `struct *` also risks a strict-aliasing violation. → [[languages/04-c/10-undefined-behaviour|Undefined Behaviour]]

## Flexible array members

```c
struct Buffer {
    size_t len;
    char   data[];        // C99 flexible array member — must be LAST
};

struct Buffer *b = malloc(sizeof *b + n);
b->len = n;
```

Header and payload in **one allocation** — one `malloc`, one `free`, and the data is contiguous with its header. This is the idiomatic way to do variable-length records in C, and you'll see it throughout the kernel and in network code.

## Unions

All members share the same memory; the size is the largest member.

```c
union Value {
    int    i;
    float  f;
    char   bytes[4];
};

union Value v;
v.i = 65;
printf("%f\n", v.f);       // reading a member you didn't write is... complicated
```

Writing one member and reading another is **type punning**. In C it's explicitly allowed through a union (unlike C++, where it's UB); the value you get is the reinterpreted bit pattern.

The safest form is `memcpy`, which every compiler optimises to nothing:

```c
float f = 1.0f;
uint32_t bits;
memcpy(&bits, &f, sizeof bits);      // portable, no aliasing issue
```

### Tagged unions

A union alone doesn't record which member is valid, so you pair it with a tag:

```c
typedef enum { VAL_INT, VAL_FLOAT, VAL_STR } ValueKind;

typedef struct {
    ValueKind kind;
    union {
        int    i;
        double d;
        char  *s;
    } as;
} Value;

void print(const Value *v) {
    switch (v->kind) {
        case VAL_INT:   printf("%d\n", v->as.i); break;
        case VAL_FLOAT: printf("%f\n", v->as.d); break;
        case VAL_STR:   printf("%s\n", v->as.s); break;
    }
}
```

**This is a sum type, built by hand.** It's exactly what [[languages/03-rust/06-structs-enums-and-pattern-matching|a Rust enum]] is, with two differences: nothing forces you to check the tag before reading, and nothing checks your `switch` is exhaustive. Read the wrong member and you get garbage or a crash.

It's the core data structure of every interpreter and JSON parser written in C, so it's worth building once — it's also the clearest possible demonstration of what a language feature buys you.

(`-Wswitch` warns on unhandled enum cases if you `switch` on the enum type without a `default`. Turn it on; it recovers part of the safety.)

## Bitfields

```c
struct Flags {
    unsigned int is_active : 1;
    unsigned int priority  : 3;      // 0-7
    unsigned int type      : 4;
};
```

Sub-byte fields, for protocol headers and hardware registers. Convenient and **badly under-specified**: bit order within a unit, whether fields straddle boundaries, and the exact layout are all implementation-defined. You cannot portably map a bitfield struct onto a wire format.

For anything portable, use explicit masks and shifts:

```c
#define FLAG_ACTIVE   (1u << 0)
#define PRIORITY_MASK (0x7u << 1)

flags |=  FLAG_ACTIVE;                                  // set
flags &= ~FLAG_ACTIVE;                                  // clear
if (flags & FLAG_ACTIVE) { }                            // test
uint32_t prio = (flags & PRIORITY_MASK) >> 1;           // extract
```

More verbose, completely defined. → [[foundations/dsa/05-algorithms/13-bit-manipulation|Bit Manipulation]]

## Enums

```c
enum Color { RED, GREEN, BLUE };            // 0, 1, 2
enum Status { OK = 0, ERR = -1, BUSY = 10 };
```

C enums are **weakly typed** — they're integers, and any integer assigns to them without complaint:

```c
enum Color c = 47;         // legal C
```

No exhaustiveness, no namespacing (the constants leak into the enclosing scope, hence `COLOR_RED` prefixes by convention), and the underlying type is implementation-defined before C23.

Their genuine advantage over `#define` is that the debugger knows the names and `-Wswitch` can warn on unhandled cases.

## Practical rules

1. **Order members largest-first** to minimise padding.
2. **Designated initialisers** (`.x = 1`) — order-independent and readable.
3. **`= {0}`** to zero a struct.
4. **Pass `const T *`** for anything larger than a couple of words.
5. **Don't pack** unless an external format demands it; use `memcpy` for serialisation.
6. **Flexible array members** for header-plus-payload.
7. **Tag your unions**, and turn on `-Wswitch`.
8. **Masks and shifts over bitfields** for anything portable.

---

## Related
- [[languages/04-c/07-memory-management|Memory Management]] — allocating these
- [[languages/04-c/11-modular-c-and-project-structure|Modular C]] — opaque structs as an interface
- [[languages/03-rust/06-structs-enums-and-pattern-matching|Rust: Enums]] — tagged unions with the checking built in
- [[hardware/03-embedded-systems|Embedded Systems]] — where layout control genuinely matters
- [[languages/04-c/README|C course map]]
