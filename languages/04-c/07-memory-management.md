# Memory Management

**[Intermediate]** — The three storage regions, `malloc`/`free`, and a catalogue of every way this goes wrong — because it's the same list that fills the CVE database.

## Where memory lives

```
high addresses
┌────────────────────┐
│ command line, env  │
├────────────────────┤
│ STACK              │  local variables, parameters, return addresses
│    ↓ grows down    │  automatic — freed on function return
├────────────────────┤
│                    │
│ (unmapped)         │
│                    │
├────────────────────┤
│    ↑ grows up      │
│ HEAP               │  malloc/free — YOU manage lifetime
├────────────────────┤
│ BSS                │  uninitialised globals/statics — zeroed at start
├────────────────────┤
│ DATA               │  initialised globals/statics
├────────────────────┤
│ TEXT               │  the machine code; read-only. String literals often live here
└────────────────────┘
low addresses
```

```c
int global = 5;              // DATA
int uninit;                  // BSS — zero-initialised, guaranteed
static int counter;          // BSS

void f(void) {
    int local = 1;           // STACK — dies at return
    static int calls = 0;    // BSS — persists across calls, but scoped to f
    int *heap = malloc(4);   // the POINTER is on the stack; the 4 bytes are on the heap
}
```

**Stack allocation is nearly free** — one register adjustment. Heap allocation involves an allocator, possibly a syscall, and bookkeeping. Prefer the stack when the size is known and modest.

**The stack is small** — typically 8MB on Linux, 1MB on Windows, and *far* less on embedded. Overflow it and you get a segfault:

```c
int big[10000000];      // ~40MB on the stack — segfault at first touch
int *big = malloc(10000000 * sizeof *big);   // heap: fine (if it succeeds)
```

Deep or unbounded recursion overflows the stack for the same reason.

## `malloc` and friends

```c
#include <stdlib.h>

void *malloc(size_t size);              // uninitialised memory
void *calloc(size_t n, size_t size);    // n*size bytes, ZEROED, overflow-checked
void *realloc(void *p, size_t newsize); // resize; may move the block
void  free(void *p);
```

```c
int *arr = malloc(n * sizeof *arr);
if (!arr) { return -1; }                // ALWAYS check

/* use it */

free(arr);
arr = NULL;
```

**`calloc` is the safer allocator for arrays.** It checks `n * size` for overflow; `malloc(n * size)` does not:

```c
size_t n = 0x100000001;                     // attacker-controlled
int *p = malloc(n * sizeof(int));           // multiplication WRAPS → tiny allocation
                                            // then you write n elements into it
int *p = calloc(n, sizeof(int));            // returns NULL on overflow
```

That integer-overflow-into-heap-overflow shape is a real and recurring CVE pattern. → [[languages/04-c/04-types-and-integers|Types and Integers]]

### `realloc` correctly

```c
char *tmp = realloc(buf, newsize);
if (!tmp) {
    free(buf);           // buf is STILL VALID — realloc didn't free it
    return -1;
}
buf = tmp;
```

```c
buf = realloc(buf, newsize);      // WRONG — on failure you've leaked the original
```

Assigning `realloc`'s result directly to the same pointer leaks the old block when it returns `NULL`. Always use a temporary.

`realloc` may move the block, so **every other pointer into it is now dangling.** This is C's version of iterator invalidation, and it's why growing a buffer while holding pointers into it is a bug.

## Every way this goes wrong

**1. Memory leak** — allocated, never freed.

```c
void f(void) {
    char *p = malloc(100);
    if (error) return;      // leaked
    free(p);
}
```

Not immediately fatal, and fatal eventually for a long-running process. Valgrind finds these.

**2. Use-after-free** — using memory you've returned.

```c
free(p);
printf("%d\n", *p);        // UB. Often "works" — which is worse
```

Dangerous because the allocator may have handed that block to something else. An attacker who can control what gets allocated there can control what your program reads or calls. This is the basis of a large fraction of modern browser and kernel exploits.

**3. Double free** — freeing twice.

```c
free(p);
free(p);                   // corrupts allocator metadata → often exploitable
```

`p = NULL` after `free` makes the second one a harmless no-op.

**4. Buffer overflow** — writing past the end.

```c
char *buf = malloc(10);
strcpy(buf, "much longer than ten bytes");
```

→ [[languages/04-c/06-arrays-strings-and-decay|Arrays, Strings and Decay]]

**5. Freeing a non-heap pointer.**

```c
int x;
free(&x);                  // UB — not from malloc

char *p = malloc(10);
p += 5;
free(p);                   // UB — must be the ORIGINAL pointer
```

**6. Dangling stack pointer.**

```c
int *f(void) {
    int x = 5;
    return &x;             // x is gone the moment f returns
}
```

**7. Uninitialised read.**

```c
int *p = malloc(sizeof *p);
printf("%d\n", *p);        // garbage — malloc doesn't zero. Use calloc if you need that.
```

**8. Mismatched allocator.** Memory from a library's allocator must be freed by that library's `free`. Crossing an FFI boundary, this is a real hazard. → [[languages/03-rust/15-unsafe-and-ffi|Rust FFI]]

## Ownership discipline

C has no ownership system, so you impose one by convention. The rules that make a codebase survivable:

**1. Every allocation has exactly one owner** — one place responsible for freeing it.

**2. Document ownership transfer in the API.** Whether a function takes ownership, returns ownership, or borrows should be stated:

```c
/* Returns a newly allocated string; caller must free(). */
char *build_path(const char *dir, const char *file);

/* Borrows `s`; does not retain it. */
void log_line(const char *s);

/* Takes ownership of `node`; frees it on failure. */
int list_append(List *l, Node *node);
```

**3. Allocate and free at the same level.** If a function allocates, its caller frees — or it provides an explicit destructor.

**4. Pair constructor and destructor:**

```c
Stack *stack_create(size_t cap);
void   stack_destroy(Stack *s);       // frees everything stack_create allocated
```

**5. `goto cleanup` for error paths.** This is the one place `goto` is idiomatic C and genuinely better than the alternatives:

```c
int process(const char *path) {
    int rc = -1;
    FILE *f = NULL;
    char *buf = NULL;

    f = fopen(path, "r");
    if (!f) goto cleanup;

    buf = malloc(SIZE);
    if (!buf) goto cleanup;

    if (do_work(f, buf) != 0) goto cleanup;

    rc = 0;
cleanup:
    free(buf);          // free(NULL) is safe, so this is fine even on early failure
    if (f) fclose(f);
    return rc;
}
```

Without it you get either nested `if`s five deep or the same cleanup duplicated at every return. The kernel uses this pattern throughout.

Note this is C reinventing, by hand and by discipline, what [[languages/03-rust/03-ownership|Rust's `Drop`]] and C++'s RAII do automatically. The comparison is the whole argument for those languages:

| | C | Rust |
|---|---|---|
| Free | manual `free()` | automatic at scope exit |
| Double free | UB, exploitable | impossible — one owner |
| Use-after-free | UB, exploitable | impossible — compile error |
| Leak | easy | possible but hard |
| Ownership | a comment | the type system |

## Custom allocation strategies

Worth knowing, because they sidestep whole categories of the above:

**Arena / bump allocator** — allocate from a big block by moving a pointer, free everything at once:

```c
typedef struct { char *base; size_t used, cap; } Arena;

void *arena_alloc(Arena *a, size_t n) {
    n = (n + 15) & ~(size_t)15;          // align to 16
    if (a->used + n > a->cap) return NULL;
    void *p = a->base + a->used;
    a->used += n;
    return p;
}
```

Allocation is a pointer bump; there is no individual `free`, so **no use-after-free, no double free, no leaks** — you reset the whole arena. Perfect for per-request or per-frame lifetimes, which is why compilers, game engines and web servers use them.

**Pool allocator** — fixed-size blocks from a free list. O(1), no fragmentation, ideal for many same-sized objects.

**Stack allocation with VLAs or `alloca`** — avoid both. VLAs can't fail gracefully and blow the stack on attacker-controlled sizes; `alloca` is worse. C11 made VLAs optional for good reason.

## Rules

1. **Check every allocation.**
2. **`p = NULL` after `free`.**
3. **`calloc` for arrays** — it checks the multiplication.
4. **Temporary for `realloc`.**
5. **One owner per allocation, documented.**
6. **`goto cleanup` for multi-resource error paths.**
7. **Run Valgrind and ASan.** Always. → [[languages/04-c/13-debugging-and-tooling|Debugging and Tooling]]
8. **Consider an arena** when lifetimes are naturally grouped.

---

## Related
- [[languages/04-c/05-pointers|Pointers]] — what you're managing
- [[languages/04-c/10-undefined-behaviour|Undefined Behaviour]] — what these bugs formally are
- [[languages/04-c/13-debugging-and-tooling|Debugging and Tooling]] — ASan and Valgrind
- [[languages/03-rust/03-ownership|Rust: Ownership]] — this discipline, enforced
- [[foundations/os/fundamentals|OS Fundamentals]] — virtual memory underneath
- [[languages/04-c/README|C course map]]
