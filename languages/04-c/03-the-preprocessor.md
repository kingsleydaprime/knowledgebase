# The Preprocessor

**[Beginner → Intermediate]** — A text substitution engine that runs before the compiler, knows nothing about C, and will happily generate nonsense.

## What it is

The preprocessor is a **separate program** that transforms text. It doesn't parse C, doesn't know about types or scope, and has no idea what a function is. It handles lines starting with `#`, does substitution, and hands the result to the compiler.

```bash
gcc -E main.c | less        # see exactly what the compiler will actually receive
```

Run that once on a real file. It's the fastest way to stop being confused by macros.

## `#include`

```c
#include <stdio.h>     // search system include paths (/usr/include, then -I paths)
#include "myheader.h"  // search the current directory first, then system paths
```

Literally pastes the file's contents at that point. Covered in [[languages/04-c/02-headers-and-the-translation-unit|Headers and the Translation Unit]].

## `#define`

### Object-like macros

```c
#define MAX_BUFFER 1024
#define PI 3.14159265358979
#define DEBUG_MODE
```

Every occurrence of the token is replaced. `MAX_BUFFER` has no type, occupies no memory, and doesn't exist by the time the compiler runs.

**Prefer `const` or `enum` for constants:**

```c
#define MAX 1024              // no type, invisible to the debugger
const int max = 1024;         // typed, scoped, debuggable
enum { MAX = 1024 };          // typed, and usable as an array size / case label
```

`const int` can't be used as an array size in C89 or as a `case` label ever, which is why the `enum` trick exists. In C23, `constexpr` finally fixes this properly.

### Function-like macros

```c
#define SQUARE(x) ((x) * (x))
#define MAX(a, b) ((a) > (b) ? (a) : (b))
```

Note the parentheses. They are not decorative.

## The four macro traps

**1. Missing parentheses around the whole body**

```c
#define SQUARE(x) x * x
SQUARE(2 + 3)       // expands to: 2 + 3 * 2 + 3  →  11, not 25
```

**2. Missing parentheses around each parameter**

```c
#define DOUBLE(x) (x * 2)
DOUBLE(3 + 1)       // (3 + 1 * 2) → 5, not 8
```

Rule: **wrap the whole body in parentheses, and wrap every parameter.**

```c
#define SQUARE(x) ((x) * (x))
```

**3. Double evaluation** — the trap parentheses don't fix

```c
#define MAX(a, b) ((a) > (b) ? (a) : (b))

MAX(i++, j++)          // one of them increments TWICE
MAX(expensive(), 5)    // expensive() may run twice
```

The argument text is substituted, so it appears — and executes — wherever the parameter appears. There's no way to fix this within the macro. It's the single strongest argument for using functions instead.

**4. Multi-statement macros and dangling `if`**

```c
#define SWAP(a, b) int t = a; a = b; b = t;

if (x) SWAP(p, q);     // only the FIRST statement is inside the if
```

The idiom that fixes it:

```c
#define SWAP(a, b) do { int t = (a); (a) = (b); (b) = t; } while (0)
```

`do { ... } while(0)` makes the macro a single statement that still requires a semicolon after it. If you see this in real code, that's why.

> **Use a function unless you genuinely can't.** `static inline` gives you the performance with none of these problems, and it type-checks. Reach for a macro when you need type-genericity, token pasting, stringification, or conditional compilation — not to avoid a function call.

## Conditional compilation

```c
#ifdef DEBUG
    printf("x = %d\n", x);
#endif

#ifndef NDEBUG
    /* assert-style checks */
#endif

#if defined(__linux__)
    #include <sys/epoll.h>
#elif defined(__APPLE__)
    #include <sys/event.h>
#elif defined(_WIN32)
    #include <windows.h>
#else
    #error "unsupported platform"
#endif

#if VERSION >= 2
#endif
```

```bash
gcc -DDEBUG main.c            # define DEBUG from the command line
gcc -DVERSION=3 main.c
gcc -DNDEBUG main.c           # disables assert()
```

This is C's portability mechanism, and it's how one codebase targets Linux, macOS, Windows and an embedded board. It's also how codebases become unreadable — deeply nested `#ifdef`s produce code where no single configuration is visible on the page.

**The discipline that keeps it sane:** push platform differences behind a common interface in a few files rather than scattering `#ifdef` through business logic.

```c
// platform.h  — one clean interface
int platform_poll(int fd, int timeout_ms);

// platform_linux.c, platform_macos.c — the #ifdefs live here, or in the build
```

Common predefined macros:

```c
__FILE__      // current filename       __LINE__      // current line number
__DATE__      // compile date            __TIME__      // compile time
__func__      // enclosing function name (C99; technically not a macro)
__STDC_VERSION__   // 201112L for C11, 201710L for C17
```

These make a logging macro genuinely useful:

```c
#define LOG(fmt, ...) \
    fprintf(stderr, "[%s:%d %s] " fmt "\n", __FILE__, __LINE__, __func__, ##__VA_ARGS__)

LOG("connection failed: %s", strerror(errno));
```

`__VA_ARGS__` is variadic macro arguments; `##__VA_ARGS__` is a GCC/Clang extension that eats the trailing comma when there are no variadic arguments. C23 standardises this as `__VA_OPT__`.

## Stringify and paste

```c
#define STR(x) #x                 // # turns the argument into a string literal
#define XSTR(x) STR(x)            // the two-level trick, so macros get expanded first
#define CONCAT(a, b) a ## b       // ## pastes tokens together

STR(hello)          // "hello"
STR(MAX_BUFFER)     // "MAX_BUFFER"   ← not expanded!
XSTR(MAX_BUFFER)    // "1024"         ← expanded, then stringified
CONCAT(my_, var)    // my_var
```

The two-level `XSTR` idiom exists because `#` and `##` suppress expansion of their operands. It's obscure and you'll need it exactly when you're stringifying a macro value.

Token pasting powers the X-macro pattern, which is C's answer to code generation:

```c
#define COLORS  X(RED) X(GREEN) X(BLUE)

#define X(name) name,
enum Color { COLORS };                       // RED, GREEN, BLUE,
#undef X

#define X(name) #name,
const char *color_names[] = { COLORS };      // "RED", "GREEN", "BLUE",
#undef X
```

One list, and the enum and its names can't drift apart. Ugly, effective, and still the standard trick — it's what you use where Rust would use a `derive` macro.

## `#pragma`

```c
#pragma once                    // include guard
#pragma pack(1)                 // no struct padding → 08-structs-unions-and-layout
#pragma GCC diagnostic ignored "-Wunused-variable"
```

Compiler-specific directives. `#pragma once` is the only one you'll use routinely.

## Why this is C's weakest feature

The preprocessor operates on **tokens, not syntax**. It has no notion of scope, type, or the surrounding code. Consequences:

- **Macros ignore scope.** `#define max 10` breaks every variable named `max` in every file that includes you. This is why macro names are `SCREAMING_CASE` — a naming convention doing a language's job.
- **Debuggers see the expansion, not your macro.** Stepping through macro-heavy code is unpleasant.
- **Errors point at the expansion**, often somewhere baffling.
- **No type checking.** A macro will happily produce garbage for the wrong type.

Every later language replaced it: [[languages/03-rust/17-macros|Rust's macros]] operate on the AST, are hygienic (they can't capture your variables), and are type-checked after expansion. C++ added templates, `constexpr`, and eventually modules to displace three of the preprocessor's four jobs.

Knowing the preprocessor is still necessary, because you'll read a lot of code that leans on it.

## Practical rules

1. **`static inline` function over a function-like macro**, always, unless you need type-genericity or token tricks.
2. **Parenthesise the body and every parameter** when you must write one.
3. **`do { } while (0)`** for multi-statement macros.
4. **`const` or `enum` over `#define`** for constants.
5. **Confine `#ifdef` to a platform layer.** Don't scatter it.
6. **`gcc -E` when confused.** The expansion is the truth.

---

## Related
- [[languages/04-c/02-headers-and-the-translation-unit|Headers and the Translation Unit]] — `#include`, in depth
- [[languages/04-c/10-undefined-behaviour|Undefined Behaviour]] — what a careless macro can produce
- [[languages/03-rust/17-macros|Rust: Macros]] — hygienic, AST-based, type-checked
- [[languages/04-c/README|C course map]]
