# Pointers

**[Beginner → Intermediate]** — A variable holding an address. Simple to state, and the thing everything else in C is built from.

## The basics

```c
int x = 42;
int *p = &x;        // p holds the ADDRESS of x
printf("%d\n", *p); // 42 — dereference: "the value at that address"
*p = 100;           // writes through the pointer; x is now 100

printf("%p\n", (void *)p);   // print an address — cast to void*, use %p
```

- `&` — address-of
- `*` — in a declaration, "is a pointer"; in an expression, "dereference"

Declaration syntax is the confusing part:

```c
int *a, b;          // a is int*, b is int  ← the * binds to the NAME
int *a, *b;         // both are pointers
```

Which is why `int *p` is the conventional spacing rather than `int* p` — it reflects what actually happens. C's declaration syntax is "declaration mirrors use", and it doesn't age well.

## Pointer arithmetic

```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr;

p + 1               // advances by sizeof(int) bytes, not 1 byte
*(p + 2)            // 30
p[2]                // identical — a[i] IS *(a + i), by definition
```

**Arithmetic scales by the pointed-to type.** `p + 1` on an `int*` moves 4 bytes; on a `char*`, 1 byte; on a `struct Foo*`, `sizeof(struct Foo)`.

Because `a[i]` is defined as `*(a + i)`, and addition commutes:

```c
arr[2] == *(arr + 2) == *(2 + arr) == 2[arr]     // all legal. 2[arr] compiles.
```

A curiosity, not advice.

```c
ptrdiff_t n = p2 - p1;      // elements between them, not bytes
```

**Arithmetic is only defined within a single array** (plus one past the end). Computing a pointer outside that is UB even if you never dereference it. The one-past-the-end pointer is legal to *form* and compare, illegal to dereference — which is what makes `for (p = arr; p < arr + n; p++)` valid.

## `void *`

```c
void *generic;                    // a pointer to unknown type
int *p = malloc(10 * sizeof *p);  // malloc returns void*, converts implicitly in C
```

`void *` converts to and from any object pointer without a cast in C. It's how `malloc`, `memcpy` and `qsort` are type-agnostic — and it's a total hole in the type system, since nothing checks you got it right.

You **cannot dereference or do arithmetic on `void *`** — its size is unknown. (GCC allows `void*` arithmetic as an extension, treating it as `char*`; don't rely on it.)

```c
// Don't cast malloc's result in C. It's unnecessary, and it hides a missing
// #include <stdlib.h>, which used to cause real bugs.
int *p = malloc(n * sizeof *p);          // good — note sizeof *p, not sizeof(int)
```

`sizeof *p` rather than `sizeof(int)` means changing `p`'s type doesn't silently break the allocation. Use it.

## `NULL`

```c
int *p = NULL;
if (p == NULL) { }
if (!p) { }                  // equivalent, and common
```

`NULL` is a null pointer constant. **Dereferencing it is undefined behaviour** — in practice a segfault on a hosted OS, because page zero is unmapped. On embedded targets with no MMU, it may silently read address 0 and continue with garbage, which is far worse.

```c
free(p);
p = NULL;        // defensive: prevents use-after-free and makes double-free a no-op
```

`free(NULL)` is explicitly a no-op, so setting to `NULL` after freeing is safe and worth doing.

**Always check the result of anything that can return `NULL`:**

```c
FILE *f = fopen(path, "r");
if (!f) { perror("fopen"); return -1; }

char *buf = malloc(n);
if (!buf) { return -1; }
```

The absence of `Option<T>` means nothing forces this. It's the discipline C asks of you and the one people skip.

## Pointers to pointers

```c
int x = 5;
int *p = &x;
int **pp = &p;
**pp = 10;                 // x is now 10
```

Two real uses:

**Output parameters** — modifying the caller's pointer:

```c
int alloc_buffer(char **out, size_t n) {
    char *p = malloc(n);
    if (!p) return -1;
    *out = p;              // write through, so the CALLER's pointer changes
    return 0;
}

char *buf;
if (alloc_buffer(&buf, 128) != 0) { /* handle */ }
```

**Arrays of pointers** — `char **argv` is the canonical example:

```c
int main(int argc, char **argv) {
    for (int i = 0; i < argc; i++) printf("%s\n", argv[i]);
}
```

C is strictly **pass-by-value**. Passing a pointer lets a function modify what it points at; passing a pointer *to* a pointer lets it modify the pointer itself.

## Function pointers

```c
int add(int a, int b) { return a + b; }

int (*op)(int, int) = add;     // declaration: name in the middle, parens mandatory
int r = op(2, 3);              // call it
int r = (*op)(2, 3);           // same thing; the older spelling
```

The parentheses around `*op` are required — without them, `int *op(int, int)` declares a *function returning* `int*`.

Almost always worth a `typedef`:

```c
typedef int (*BinaryOp)(int, int);
BinaryOp op = add;
```

Function pointers are C's mechanism for polymorphism, callbacks, and dispatch tables:

```c
// The standard library's sorting hook
int cmp(const void *a, const void *b) {
    return (*(const int *)a) - (*(const int *)b);   // note: this subtraction can overflow
}
qsort(arr, n, sizeof(int), cmp);
```

```c
// A vtable, by hand — this is what C++ virtual methods compile to
struct Shape {
    double (*area)(const struct Shape *);
    void   (*draw)(const struct Shape *);
};
```

That struct-of-function-pointers pattern is how you get interfaces in C, and it's exactly what [[languages/03-rust/09-traits|`dyn Trait`]] and a C++ vtable are underneath. Writing it by hand once makes dynamic dispatch permanently unmysterious.

## `const` with pointers

```c
const char *p;          // pointer to const char — can't write *p, CAN reassign p
char *const p;          // const pointer to char — can write *p, can't reassign p
const char *const p;    // neither
```

**Read right to left.** `const char *const p` = "p is a const pointer to a const char".

The first form is the one you write constantly — a function that reads but doesn't modify:

```c
size_t my_strlen(const char *s);
void print_all(const int *arr, size_t n);
```

Taking `const` is free documentation, lets callers pass literals, and occasionally helps the optimiser.

## Why pointers are dangerous

Everything C's reputation rests on. All of these compile without warning:

```c
int *p;                      // uninitialised — points at garbage
*p = 5;                      // UB

int *p = malloc(4);
free(p);
*p = 5;                      // use-after-free

int *dangling(void) {
    int x = 5;
    return &x;               // returns a pointer to a dead stack frame
}

int arr[5];
arr[10] = 1;                 // out of bounds; no check exists

free(p); free(p);            // double free — heap corruption
```

There is **no runtime check for any of this**. The pointer doesn't know what it points at, how big it is, whether it's still valid, or whether anyone else holds it.

This is the entire motivation for [[languages/03-rust/03-ownership|Rust's ownership system]]:

| C failure | What Rust does |
|---|---|
| use-after-free | ownership — you can't use a moved value |
| dangling pointer | lifetimes — a reference can't outlive its owner |
| double free | one owner, one drop |
| buffer overrun | bounds-checked slices |
| null dereference | no null; `Option<T>` |
| data race | the borrow rule |

The tools that catch these in C — ASan, Valgrind — are runtime and only find bugs on paths you actually execute. → [[languages/04-c/13-debugging-and-tooling|Debugging and Tooling]]

## Practical rules

1. **Initialise every pointer.** To `NULL` if nothing else.
2. **Set to `NULL` after `free`.**
3. **Check every allocation and every `fopen`.**
4. **`const` on any pointer parameter you don't modify.**
5. **Never return a pointer to a local.**
6. **Pass the length alongside the pointer.** A bare pointer carries no size, and every buffer overflow starts there.
7. **`sizeof *p` over `sizeof(Type)`** in allocations.

---

## Related
- [[languages/04-c/06-arrays-strings-and-decay|Arrays, Strings and Decay]] — where pointers and arrays blur
- [[languages/04-c/07-memory-management|Memory Management]] — the heap, and every way to lose it
- [[languages/04-c/10-undefined-behaviour|Undefined Behaviour]] — the consequences
- [[languages/03-rust/03-ownership|Rust: Ownership]] — the systematic fix
- [[languages/04-c/README|C course map]]
