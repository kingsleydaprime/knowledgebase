---
id: 91ab761e-9929-49f7-85f6-fb46ac2359cc
---

# Modular C and Project Structure

## What you get, and what you don't
<!-- bite: 5b5b1729-f1a3-4a7a-875e-351d0d4ec656 -->

**You get:** translation units, `static` for internal linkage, headers for interfaces, and incomplete types for encapsulation.

**You don't get:** namespaces, modules, classes, generics, method syntax, package-level visibility, or any enforcement beyond `static`.

So a well-structured C project is a set of disciplines. The good news is that the disciplines are few, and they're visible in every well-regarded C codebase — SQLite, Redis, curl, git.

## Layout
<!-- bite: de1e398e-9fe3-4ba7-a3a8-797b5fae62c8 -->

```
myproject/
├── Makefile
├── include/
│   └── myproject/          ← namespaced directory, so users write
│       ├── stack.h            #include <myproject/stack.h>
│       └── parser.h
├── src/
│   ├── stack.c
│   ├── parser.c
│   ├── internal.h          ← headers NOT part of the public API
│   └── main.c
├── tests/
│   └── test_stack.c
└── third_party/
```

`include/` for the public interface, `src/` for implementation and private headers. If you're building a library, that split is what users see; for an application it still helps by making the internal boundaries visible.

## The module pattern
<!-- bite: 52be11d2-fd63-45ff-a4d9-ee07d51ee254 -->

One module = one `.h` (interface) + one `.c` (implementation). The single most important rule:

> **Everything in the `.c` that isn't declared in the `.h` should be `static`.**

```c
/* ---- stack.h ---- */
#pragma once
#include <stddef.h>

typedef struct Stack Stack;                  // OPAQUE — callers can't see inside

Stack *stack_create(size_t capacity);
void   stack_destroy(Stack *s);
int    stack_push(Stack *s, int value);      // 0 on success, -1 on failure
int    stack_pop(Stack *s, int *out);
size_t stack_len(const Stack *s);
```

```c
/* ---- stack.c ---- */
#include "myproject/stack.h"     // include your own header FIRST — proves it's self-contained
#include <stdlib.h>

struct Stack {                    // the definition lives here, and nowhere else
    int   *data;
    size_t len, cap;
};

static int grow(Stack *s) {       // static — invisible outside this file
    size_t ncap = s->cap ? s->cap * 2 : 8;
    int *tmp = realloc(s->data, ncap * sizeof *tmp);
    if (!tmp) return -1;
    s->data = tmp;
    s->cap  = ncap;
    return 0;
}

Stack *stack_create(size_t capacity) {
    Stack *s = calloc(1, sizeof *s);
    if (!s) return NULL;
    if (capacity) {
        s->data = malloc(capacity * sizeof *s->data);
        if (!s->data) { free(s); return NULL; }
        s->cap = capacity;
    }
    return s;
}

void stack_destroy(Stack *s) {
    if (!s) return;               // accept NULL, like free()
    free(s->data);
    free(s);
}
```

What that buys you:

- **Callers cannot touch `s->len`.** The invariant is yours to maintain.
- **You can change the layout** without recompiling callers.
- **`grow` doesn't exist** outside this file — no name collisions at link time, and the compiler can inline it freely.
- **`stack_destroy(NULL)` is safe**, matching `free`'s contract, so cleanup paths stay simple.

`FILE *` is exactly this pattern, which is a good argument that it's idiomatic rather than clever.

The cost: callers must heap-allocate (they can't put a `Stack` on the stack, since the size is unknown), and every access goes through a function call. Where that matters — a small vector type in a hot loop — expose the struct and document the invariants instead. It's a trade, not a law.

## Naming
<!-- bite: 3311e6a1-920a-48f1-9b8e-d83863894549 -->

Without namespaces, **prefix everything public** with the module name:

```c
stack_create   stack_push   stack_destroy      // module_verb
STACK_MAX_SIZE                                  // MODULE_CONSTANT
typedef struct Stack Stack;                     // ModuleType or module_t
```

This is why C library APIs read like `pthread_mutex_lock`, `sqlite3_open`, `curl_easy_setopt`. It's verbose and it's the only collision avoidance available — every non-`static` symbol shares one global namespace at link time.

## Error handling conventions
<!-- bite: 8e44039a-d456-4c09-8a33-c707fa88e08d -->

C has no exceptions and no `Result`. Pick **one** convention and hold it across the project:

**Return an int status, output via pointer** — the most common, and what POSIX does:

```c
int stack_pop(Stack *s, int *out);          // 0 = success, negative = error
```

**Return the value, sentinel on error:**

```c
FILE *fopen(...);                            // NULL on failure
ssize_t read(...);                           // -1 on failure, errno set
```

**Return an error enum:**

```c
typedef enum { ERR_OK = 0, ERR_NOMEM, ERR_INVALID, ERR_IO } Error;
Error stack_push(Stack *s, int v);
```

The enum version is the most readable at call sites and the easiest to extend. Whichever you choose, **document it in the header** and don't mix conventions within a project.

And the cleanup discipline from [[languages/04-c/07-memory-management|Memory Management]]:

```c
int process(const char *path) {
    int rc = -1;
    FILE *f = NULL; char *buf = NULL;

    if (!(f = fopen(path, "r")))  goto cleanup;
    if (!(buf = malloc(SIZE)))    goto cleanup;
    if (do_work(f, buf) != 0)     goto cleanup;
    rc = 0;
cleanup:
    free(buf);
    if (f) fclose(f);
    return rc;
}
```

## Interfaces via function pointers
<!-- bite: f00fc8ed-bdba-45bd-aae8-8cde1305394e -->

C's polymorphism, from [[languages/04-c/05-pointers|Pointers]] — a struct of function pointers is a vtable:

```c
typedef struct Logger {
    void *ctx;
    void (*write)(void *ctx, const char *msg);
    void (*close)(void *ctx);
} Logger;

void log_info(const Logger *l, const char *msg) {
    l->write(l->ctx, msg);
}
```

The `void *ctx` carries the implementation's own state. This is how you'd inject a dependency in C, and it's the same shape as a [[languages/03-rust/09-traits|`dyn Trait`]] or a Go interface — you're just writing the vtable by hand.

## Configuration and compile-time options
<!-- bite: 950078d2-40b5-475d-9269-0c14476c7e85 -->

```c
// config.h
#pragma once
#ifndef MAX_CONNECTIONS
#define MAX_CONNECTIONS 1024
#endif
```

The `#ifndef` guard lets the build override it: `gcc -DMAX_CONNECTIONS=4096`. Platform variation belongs in a thin platform layer, not scattered through the code:

```c
// platform.h — one interface
int platform_mkdir(const char *path);

// platform_posix.c / platform_win32.c — the #ifdefs live here, or the build picks a file
```

## Testing
<!-- bite: 2c903b3f-f66b-4ea5-8390-74ab6dfb1656 -->

There's no built-in test framework. Options, in increasing weight:

**A plain `main` per test file** — no dependency at all:

```c
// tests/test_stack.c
#include "myproject/stack.h"
#include <assert.h>

static void test_push_pop(void) {
    Stack *s = stack_create(4);
    assert(s);
    assert(stack_push(s, 42) == 0);
    int v;
    assert(stack_pop(s, &v) == 0 && v == 42);
    stack_destroy(s);
}

int main(void) { test_push_pop(); puts("ok"); return 0; }
```

Note `assert` disappears under `-DNDEBUG` — build tests without it, or use your own always-on check macro.

**A small framework** — Unity, greatest, µnit, criterion. Header-only ones cost nothing to adopt.

**Always run the test suite under sanitizers**, since that's where the real bugs are:

```make
test: CFLAGS += -fsanitize=address,undefined -g
test: $(TESTS)
	./run_tests
```

## Practical rules
<!-- bite: 26fe4bae-7777-466e-99bc-d76dec6797b9 -->

1. **One module = one `.h` + one `.c`.**
2. **`static` everything not in the header.**
3. **Opaque structs for anything with invariants.**
4. **Prefix all public symbols** with the module name.
5. **Include your own header first** in the `.c`.
6. **One error convention per project**, documented.
7. **Pair every `create` with a `destroy`**, and make `destroy(NULL)` safe.
8. **Forward-declare instead of including** where a pointer will do.
9. **Tests under ASan/UBSan**, in CI.

---

## Related
<!-- bite: 84f64070-7dab-40d2-a010-18bf042816c5 -->
- [[languages/04-c/02-headers-and-the-translation-unit|Headers and the Translation Unit]] — the mechanism behind all of this
- [[languages/04-c/12-build-systems|Build Systems]] — compiling the layout above
- [[languages/04-c/07-memory-management|Memory Management]] — ownership discipline
- [[backend/03-structuring-a-backend/index|Structuring a Backend]] — the same ideas, with language support
- [[languages/04-c/index|C course map]]

## About this lesson
<!-- bite: 74079812-13e9-478a-900e-6eb732f46bc4 -->

**Level:** Intermediate. **Covers:** C gives you almost no structuring tools, so the structure is convention. Here's the convention that works.
