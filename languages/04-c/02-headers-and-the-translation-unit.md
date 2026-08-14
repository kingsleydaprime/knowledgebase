# Headers and the Translation Unit

**[Beginner → Intermediate]** — The thing nobody explains properly. Why `.h`/`.c` exists at all, what a header is *for*, and the rules that make multi-file C work.

## The translation unit

> A **translation unit** is one `.c` file *after preprocessing* — meaning after every `#include` has been pasted in.

That's the compiler's entire world. It compiles one translation unit at a time and **sees nothing else**. Not your other `.c` files, not the library you're linking against, nothing.

Everything about headers follows from that one fact.

```c
// math_utils.c
int square(int x) { return x * x; }
```

```c
// main.c
int main(void) {
    int r = square(5);      // warning: implicit declaration of function 'square'
    return 0;
}
```

When compiling `main.c`, the compiler has never heard of `square`. It doesn't know its return type, how many arguments it takes, or their types. Pre-C99 it would *guess* (assume `int`, assume you got the arguments right) and generate code accordingly. If you guessed wrong, you got a corrupted stack and no warning.

You need to **tell each translation unit what exists elsewhere**. That's a header.

## Declaration vs definition

The distinction the whole system rests on:

**A declaration** says *this exists somewhere, here's its type.* Allocates nothing.

```c
int square(int x);          // function declaration (a "prototype") — note the semicolon
extern int counter;         // variable declaration
struct Point;               // incomplete type declaration
```

**A definition** actually creates the thing.

```c
int square(int x) { return x * x; }   // function definition — has a body
int counter = 0;                       // variable definition — allocates storage
struct Point { int x, y; };            // struct definition — describes a layout
```

The rules:

- **A declaration may appear many times**, in many translation units. It's just information.
- **A definition may appear exactly once** across the whole program. Two definitions of the same function is a linker error: `multiple definition of 'square'`.

So the split is:

| | contains | goes in |
|---|---|---|
| **Header (`.h`)** | declarations — the *interface* | included by many files |
| **Source (`.c`)** | definitions — the *implementation* | compiled once |

**That's the entire reason `.h`/`.c` exists.** It isn't convention or taste. It's a direct consequence of separate compilation: declarations must be visible everywhere, definitions must exist exactly once.

## The pattern

```c
// math_utils.h
#ifndef MATH_UTILS_H
#define MATH_UTILS_H

int square(int x);          // declaration only
int cube(int x);

#endif
```

```c
// math_utils.c
#include "math_utils.h"     // include your OWN header — see below

int square(int x) { return x * x; }
int cube(int x)   { return x * x * x; }
```

```c
// main.c
#include <stdio.h>
#include "math_utils.h"     // now main.c knows what square() looks like

int main(void) {
    printf("%d\n", square(5));
    return 0;
}
```

```bash
gcc -c math_utils.c -o math_utils.o    # translation unit 1
gcc -c main.c       -o main.o          # translation unit 2
gcc math_utils.o main.o -o app         # the linker connects them
```

The compiler compiled `main.c` trusting the declaration. The **linker** is what finally connects the call in `main.o` to the definition in `math_utils.o`.

If the header lies — declares `int square(int)` while the `.c` defines `double square(double)` — the compiler catches nothing, and you get a corrupted call. **Always `#include` your own header in its `.c` file.** Then the compiler compares the declaration against the definition and tells you when they drift apart. This one line prevents a genuinely nasty class of bug.

## Include guards

`#include` pastes text. Include the same header twice and you get its contents twice — and duplicate struct definitions are an error.

This happens constantly through indirect inclusion: `a.h` includes `common.h`, `b.h` includes `common.h`, and `main.c` includes both.

```c
#ifndef MATH_UTILS_H     // if this macro is not defined...
#define MATH_UTILS_H     // define it

/* header contents */

#endif                   // second time through, the body is skipped entirely
```

The macro name must be unique per header — `PROJECT_MODULE_H` is the safe convention.

```c
#pragma once             // non-standard, universally supported, does the same thing
```

`#pragma once` is one line, can't have a name collision, and is marginally faster. It isn't in the standard but every real compiler supports it. **Use `#pragma once` for new code**; understand `#ifndef` because you'll read it everywhere.

## What goes in a header

**Yes:**
- Function declarations (prototypes)
- Type definitions — `struct`, `union`, `enum`, `typedef`
- `extern` declarations of global variables
- Macros meant for callers
- `static inline` functions
- Other `#include`s your header genuinely needs

**No:**
- **Function definitions with a body** (except `static inline`) — included twice, defined twice, linker error
- **Variable definitions** — same problem. Declare `extern` in the header, define once in a `.c`
- `using`-style shortcuts, or anything that pollutes every file that includes you
- `#include`s only your `.c` needs — that's a dependency you've forced on everyone

### Globals across files

```c
// config.h
extern int g_verbose;        // DECLARATION — "this exists somewhere"

// config.c
int g_verbose = 0;           // DEFINITION — exactly once, in one .c file
```

Forget the `extern` and every `.c` including the header defines its own — `multiple definition` at link time.

## `static` — the other meaning

`static` at file scope means **internal linkage**: visible only within this translation unit.

```c
// parser.c
static int depth = 0;                 // not visible to other files
static void advance(void) { ... }     // a private helper

void parse(const char *s) { ... }     // public — declared in parser.h
```

This is C's only encapsulation mechanism, and it's the equivalent of Rust's private-by-default or Go's lowercase identifiers — except C is public-by-default, so you have to opt *in* to privacy.

**Mark every function and global not in your header as `static`.** It prevents name collisions at link time, tells readers it's internal, and lets the compiler optimise more aggressively because it knows all the callers.

(Confusingly, `static` inside a *function* means something else entirely — a variable that persists across calls. Same keyword, unrelated meaning.)

## Opaque types — real encapsulation

The strongest information-hiding C offers:

```c
// stack.h
typedef struct Stack Stack;        // INCOMPLETE type — callers can't see inside

Stack *stack_create(size_t cap);
void   stack_destroy(Stack *s);
int    stack_push(Stack *s, int v);
```

```c
// stack.c
#include "stack.h"
#include <stdlib.h>

struct Stack {                      // the definition lives HERE only
    int   *data;
    size_t len, cap;
};

Stack *stack_create(size_t cap) { ... }
```

Callers can hold a `Stack *` but cannot touch `s->len` or allocate a `Stack` on the stack — the type is incomplete to them, so its size is unknown. You can change the struct's layout without recompiling a single caller.

This is the C equivalent of a private field, and it's how good C libraries are built (`FILE *` is exactly this pattern). Use it.

## Header hygiene

**Self-contained.** A header must compile on its own — include what it needs. If `widget.h` uses `size_t`, it includes `<stddef.h>` itself rather than hoping the caller did.

```bash
echo '#include "widget.h"' > /tmp/t.c && gcc -fsyntax-only -I. /tmp/t.c
```

**Forward-declare to break cycles.** If a header only needs a *pointer* to a type, declare the type instead of including its header:

```c
struct Widget;                       // enough for Widget * — no #include needed
void render(struct Widget *w);
```

This cuts compile times and breaks circular includes, which are otherwise a real problem.

**Include order**, by convention: your own header first (so it's proven self-contained), then other project headers, then system headers.

```c
#include "parser.h"      // this file's own header

#include "lexer.h"       // project
#include "util.h"

#include <stdio.h>       // system
#include <stdlib.h>
```

## Why later languages abandoned this

Every modern language replaced headers with **modules**, because the textual-inclusion model has real costs:

- **Compile time.** A header included by 200 files is parsed 200 times. `#include <stdio.h>` alone expands to tens of thousands of lines.
- **The declaration must be maintained twice** — in the header and the `.c` — and nothing forces them to agree unless you include your own header.
- **Order-dependence.** `#include` is text substitution, so macros defined earlier affect files included later.
- **No real encapsulation** without the opaque-pointer trick.

[[languages/03-rust/16-modules-cargo-and-testing|Rust's modules]], [[languages/02-go/12-modules-and-project-layout|Go's packages]] and Java's imports all solve this by making the compiler read the *definition* rather than pasting text. C++20 finally added modules; adoption is slow, and headers remain everywhere.

Understanding headers isn't legacy trivia — it's what makes C, C++, and every FFI boundary comprehensible.

---

## Related
- [[languages/04-c/01-why-c-and-the-compilation-model|The Compilation Model]] — where translation units come from
- [[languages/04-c/03-the-preprocessor|The Preprocessor]] — the text substitution doing all this
- [[languages/04-c/11-modular-c-and-project-structure|Modular C]] — using these tools to structure a real project
- [[languages/03-rust/16-modules-cargo-and-testing|Rust: Modules]] — what replaced headers
- [[languages/04-c/README|C course map]]
