# Types and Integers

**[Beginner → Intermediate]** — Types whose sizes aren't fixed, promotion rules that fire silently, and the signed/unsigned comparison that has caused real CVEs.

## The basic types

```c
char        // 1 byte. SIGNEDNESS IS IMPLEMENTATION-DEFINED
short       // at least 16 bits
int         // at least 16 bits; 32 on essentially every modern platform
long        // at least 32 bits. 64 on Linux/macOS 64-bit, 32 on Windows 64-bit
long long   // at least 64 bits
float       // ~7 significant digits
double      // ~15 significant digits
_Bool/bool  // C99, via <stdbool.h>; a keyword in C23
void        // no value
```

**The standard specifies minimums, not sizes.** `int` is not guaranteed to be 32 bits. `long` is 64-bit on Linux and 32-bit on Windows — the LP64 vs LLP64 split, and a classic source of portability bugs.

```c
printf("%zu\n", sizeof(int));     // %zu is the format for size_t
```

Never assume. When the size matters, say the size:

```c
#include <stdint.h>

int8_t  int16_t  int32_t  int64_t        // exact width — use these
uint8_t uint16_t uint32_t uint64_t
intptr_t uintptr_t                        // big enough to hold a pointer
int_least32_t  int_fast32_t               // at-least / fastest-at-least
```

```c
#include <inttypes.h>
printf("%" PRId64 "\n", value);           // the portable way to print an int64_t
```

**Use `stdint.h` types whenever the width matters** — file formats, network protocols, hardware registers, anything crossing an ABI. Use plain `int` for loop counters and small local arithmetic where it genuinely doesn't.

## `size_t`

```c
size_t len = strlen(s);
for (size_t i = 0; i < n; i++) { }
```

`size_t` is the **unsigned** type returned by `sizeof`, `strlen`, and every standard function describing a size or count. It's big enough to index any object.

Use it for sizes and indices. But be aware of what unsigned means:

```c
for (size_t i = n - 1; i >= 0; i--) { }    // INFINITE LOOP — size_t is never < 0
```

At `i == 0`, `i--` wraps to `SIZE_MAX`. Downward loops over unsigned types are a classic hang:

```c
for (size_t i = n; i-- > 0; ) { }          // the correct idiom
```

## Integer promotion

Any type smaller than `int` is **promoted to `int`** before arithmetic. This is automatic, invisible, and surprises people constantly.

```c
char a = 100, b = 100;
char c = a + b;              // a and b promote to int → 200 → truncated back to char
                             // char is often signed, so this is -56
```

```c
uint8_t x = 200, y = 100;
if (x + y > 255) { }         // TRUE — promoted to int, so 300 > 255. No wraparound.
```

The second one catches people who expect 8-bit wraparound. It doesn't happen in the expression; it happens on assignment back to `uint8_t`.

## The usual arithmetic conversions

When operands differ, the compiler converts them to a common type. The rule that bites:

> **If one operand is unsigned and the other is signed of the same rank, the signed operand converts to unsigned.**

```c
int i = -1;
unsigned u = 1;
if (i < u) printf("less\n");
else       printf("NOT less\n");     // ← this prints
```

`-1` becomes `UINT_MAX`. This is not a compiler bug; it's the standard.

The realistic version:

```c
int len = get_length();              // returns -1 on error
if (len < sizeof(buffer)) {          // sizeof is size_t — UNSIGNED
    memcpy(buffer, src, len);        // -1 becomes SIZE_MAX → catastrophic overflow
}
```

**This exact shape has produced real CVEs.** The defence: compile with `-Wsign-compare` (included in `-Wextra`), keep sizes in `size_t` throughout, and check `< 0` *before* comparing against anything unsigned.

## Overflow

**Signed overflow is undefined behaviour.** Unsigned overflow wraps, and is well-defined.

```c
int x = INT_MAX;
x + 1;                    // UNDEFINED — anything may happen

unsigned y = UINT_MAX;
y + 1;                    // 0 — defined, modular arithmetic
```

"Undefined" isn't academic. The optimiser is allowed to *assume it cannot happen*:

```c
if (x + 1 < x) { /* overflow check */ }    // compiler deletes this — it "can't" be true
```

The correct check tests before the operation:

```c
if (a > INT_MAX - b) { /* would overflow */ }

// or use the builtins (GCC/Clang)
if (__builtin_add_overflow(a, b, &result)) { /* overflowed */ }
```

`-fsanitize=undefined` catches signed overflow at runtime. `-ftrapv` traps on it. Neither is on by default.

Compare with [[languages/03-rust/02-language-fundamentals|Rust]], which panics on overflow in debug builds and wraps in release, and gives you `checked_add`/`saturating_add`/`wrapping_add` to say what you meant. C makes you write the check yourself and punishes you with UB if you get it wrong.

## `char` signedness

```c
char c = 200;             // implementation-defined: -56 on x86, 200 on ARM
```

Plain `char` is signed on x86 and unsigned on ARM. It's a distinct type from both `signed char` and `unsigned char`.

This matters for `<ctype.h>`:

```c
char c = get_byte();
if (isalpha(c)) { }       // UB if c is negative — isalpha takes an int that must be
                          // representable as unsigned char, or EOF
if (isalpha((unsigned char)c)) { }   // correct
```

**Use `unsigned char` for raw bytes**, `char` only for text, and cast when passing to `<ctype.h>`.

## Casts and conversions

```c
int i = (int)3.99;             // 3 — truncation TOWARD ZERO, not rounding
double d = (double)a / b;      // force floating-point division
```

```c
int a = 7, b = 2;
double r = a / b;              // 3.0 — integer division happens FIRST
double r = (double)a / b;      // 3.5
```

**Beware casting away `const`:**

```c
const char *s = "literal";
char *m = (char *)s;
m[0] = 'X';                    // UB — string literals are usually read-only. Segfault.
```

Casting is telling the compiler you know better. It's right sometimes, and it silences the diagnostic either way.

## Floating point

```c
0.1 + 0.2 == 0.3          // FALSE — binary floating point can't represent 0.1 exactly
```

Not a C problem; IEEE 754 everywhere. Compare with a tolerance:

```c
#include <math.h>
if (fabs(a - b) < 1e-9) { }
```

Special values: `INFINITY`, `NAN`, and `-0.0`. **`NAN != NAN` is true**, which is why `isnan(x)` exists and why floats only implement partial ordering (a fact [[languages/03-rust/09-traits|Rust encodes]] as `PartialOrd` without `Ord`).

**Never use floating point for money.** Use integer cents, or a decimal library.

## `const`, `volatile`, `restrict`

```c
const int x = 5;                  // x can't be modified
const char *p;                    // pointer to const char — can't modify *p
char *const p;                    // const pointer — can't reassign p
const char *const p;              // both
```

Read declarations **right to left**: `const char *const p` is "p is a const pointer to a const char".

`const` on a parameter documents that the function won't modify what's pointed at, and lets callers pass string literals safely:

```c
size_t my_strlen(const char *s);      // correct: takes const
```

```c
volatile int *reg = (volatile int *)0x40021000;
```

`volatile` tells the compiler the value may change outside the program's control — so don't cache it in a register or optimise reads away. Correct for memory-mapped hardware registers and signal handlers. **It is not a threading primitive** — it provides no atomicity and no memory ordering, and using it for that is a well-known mistake. → [[hardware/03-embedded-systems|Embedded Systems]]

```c
void copy(int *restrict dst, const int *restrict src, size_t n);
```

`restrict` promises the pointers don't alias, letting the compiler optimise aggressively. Lie and you get UB. This is what Rust's `&mut` uniqueness gives the optimiser for free and permanently.

---

## Related
- [[languages/04-c/05-pointers|Pointers]] — where these types get interesting
- [[languages/04-c/10-undefined-behaviour|Undefined Behaviour]] — signed overflow and friends, in full
- [[languages/03-rust/02-language-fundamentals|Rust: Fundamentals]] — fixed-width types and explicit overflow handling
- [[languages/04-c/README|C course map]]
