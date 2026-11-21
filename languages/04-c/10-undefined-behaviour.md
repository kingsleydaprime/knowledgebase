---
id: d5344742-6fb7-458b-b3f1-8c12c142ed66
---

# Undefined Behaviour

Undefined behaviour is what happens when a C program does something the language rules do not allow, such as reading past the end of an array. The C standard makes no promise about what happens next: the program might work, crash or do something strange. Many famous security bugs started this way, so this lesson shows the common cases and how to find them.

## The three kinds
<!-- bite: 2cddd1c1-6594-4401-8fb3-2deb2a3dcb88 -->

**Implementation-defined** — the implementation picks, and must document it. Legal, just not portable.

```c
sizeof(int)                 // 4 on most platforms, not guaranteed
char                        // signed on x86, unsigned on ARM
>> on a negative number     // arithmetic shift in practice
```

**Unspecified** — the implementation picks, needn't document it, may vary.

```c
f(g(), h());                // which of g and h runs first
a[i++] + a[i]               // ordering within the expression
```

**Undefined** — the standard imposes **no requirements whatsoever**. The program is meaningless.

```c
int x = INT_MAX; x + 1;     // signed overflow
*(int *)NULL;               // null dereference
arr[10] on int arr[5];      // out of bounds
```

## What "undefined" actually licenses
<!-- bite: c9879219-1719-4b8b-acf1-d8db57f2952d -->

The crucial misconception: people read UB as "you'll get a weird value" or "it'll crash". Neither is the rule.

> The compiler is entitled to **assume undefined behaviour never happens**, and optimise on that assumption.

That assumption propagates backwards through your code and deletes things.

```c
int f(int *p) {
    int x = *p;              // dereference — so p CANNOT be null, or this is UB
    if (p == NULL) return 0; // therefore this branch is dead
    return x;
}
```

The compiler removes the null check entirely. It reasoned: "the dereference happened, so `p` isn't null, so the comparison is always false." Your safety check is gone, and the compiler was correct to remove it.

```c
int add_overflows(int a, int b) {
    return a + b < a;        // "overflow check"
}
```

Signed overflow is UB, so `a + b` cannot overflow, so `a + b < a` is false whenever `b >= 0`. GCC compiles this to `return b < 0;`. The check does not work.

```c
for (int i = 0; i <= n; i++) { }    // if n == INT_MAX, i++ overflows → UB
                                     // compiler may assume the loop terminates,
                                     // and generate code that doesn't
```

This is why "it worked at `-O0` and broke at `-O2`" is a classic C bug report. The behaviour didn't change; the optimiser started relying on an assumption you'd violated all along.

**UB is not a runtime event. It's a property of the program.** Code containing UB has no defined meaning *anywhere*, including the parts before it runs.

## The catalogue
<!-- bite: 5ba231b2-1930-45d4-a4dd-37c7e24bf6f7 -->

The ones you'll actually hit:

**Memory**
```c
*p                    // p uninitialised, NULL, freed, or out of bounds
arr[i]                // i outside [0, n)
free(p); *p;          // use-after-free
free(p); free(p);     // double free
return &local;        // dangling stack pointer
memcpy(dst, src, n)   // overlapping regions — use memmove
```

**Integers**
```c
INT_MAX + 1           // signed overflow (unsigned wraps — that's defined)
x / 0                 // division by zero
x % 0
1 << 32               // shift >= the width of the type
1 << -1               // negative shift
-1 << 1               // shifting a negative value left (pre-C++20; UB in C)
INT_MIN / -1          // overflows
```

**Sequencing**
```c
i = i++ + 1;          // multiple unsequenced modifications
a[i] = i++;
printf("%d %d", i++, i++);
```

**Types and lifetime**
```c
*(float *)&int_var;              // strict aliasing violation
p[0] = 'X' on a char *p = "lit"; // modifying a string literal
printf("%d", 3.14);              // format/argument mismatch
```

**Library misuse**
```c
strcpy(small_buf, long_string);   // overflow
strlen(unterminated);             // reads until it finds a zero, somewhere
printf(user_input);               // format string vulnerability
```

## Strict aliasing
<!-- bite: e9f8f76f-07ac-43d7-a18f-59248feea553 -->

The one that surprises experienced programmers:

> An object may only be accessed through a pointer to its own type, a compatible type, or `char`/`unsigned char`.

```c
float f = 1.0f;
uint32_t bits = *(uint32_t *)&f;      // UB — strict aliasing violation
```

It usually "works" — until the optimiser assumes the `float*` and `uint32_t*` can't refer to the same memory, reorders the accesses, and produces nonsense.

```c
uint32_t bits;
memcpy(&bits, &f, sizeof bits);        // correct, portable, and compiles to zero instructions
```

`memcpy` is the right answer for type punning. Every compiler recognises the pattern and emits nothing. A `union` is also explicitly allowed in C (though not C++).

`-fno-strict-aliasing` disables the optimisation. The Linux kernel builds with it, because too much existing code violates the rule.

## Why C has UB at all
<!-- bite: c0ea0302-4192-4ce6-afcf-8b26415eb9c7 -->

It isn't an oversight. UB exists to allow:

- **Performance.** No bounds checks, no null checks, no overflow checks. Adding them costs, and C's premise is that you don't pay for what you don't use.
- **Portability across strange hardware.** C targets machines with 9-bit bytes, no unaligned access, and unusual pointer representations. Nailing down behaviour would exclude them.
- **Optimisation.** Signed overflow being UB lets the compiler assume `i + 1 > i`, enabling loop transformations that are otherwise unsound.

The bargain: **the programmer guarantees they never invoke UB, and in exchange gets a compiler that assumes it.**

That bargain was reasonable in 1972 and has aged badly, because humans don't keep the guarantee across millions of lines. The measured result is the 70% memory-safety figure. This is the entire reason [[languages/03-rust/index|Rust]] exists: same performance, but the guarantee is checked rather than assumed.

## Finding it
<!-- bite: 3b0aecbe-e6ec-440a-b823-17c4191e0fa4 -->

UB isn't a compiler error, because it's usually undecidable at compile time. So you need runtime tools:

```bash
# UndefinedBehaviorSanitizer — catches overflow, bad shifts, misalignment, and more
gcc -fsanitize=undefined -fno-omit-frame-pointer -g prog.c && ./a.out

# AddressSanitizer — out of bounds, use-after-free, double free, leaks
gcc -fsanitize=address -g prog.c && ./a.out

# Both at once
gcc -fsanitize=address,undefined -g prog.c

# Valgrind — no recompile needed; slower and finds slightly different things
valgrind --leak-check=full --track-origins=yes ./prog
```

```text
prog.c:7:12: runtime error: signed integer overflow: 2147483647 + 1 cannot be
             represented in type 'int'
```

**These are dynamic** — they only find bugs on paths that actually execute. That's why sanitizers plus a decent test suite plus fuzzing is the standard combination, and why it's still weaker than a compile-time guarantee.

Static analysis catches a different slice:

```bash
gcc -Wall -Wextra -Wpedantic -Wconversion -Wshadow -Wstrict-prototypes
clang --analyze prog.c
cppcheck --enable=all prog.c
scan-build make
```

## The rules
<!-- bite: 5e253d26-0dd3-4b27-b59a-15fb990c316a -->

1. **Turn on `-Wall -Wextra`, and `-Werror` in CI.** Many UB patterns produce warnings nobody enabled.
2. **Run ASan and UBSan on your test suite.** In CI, not occasionally.
3. **Check *before* you act.** `if (a > INT_MAX - b)`, not `if (a + b < a)`.
4. **`memcpy` for type punning.** Never a pointer cast.
5. **Don't modify a variable twice in one expression.**
6. **Never index without knowing the bound.**
7. **Don't reason from "it works."** UB that appears to work is the dangerous kind — it means the optimiser hasn't exploited it *yet*, and a compiler upgrade can turn a working program into a broken one.

> The mental model worth keeping: **the compiler is not trying to run your program. It's trying to run a program that behaves like yours on all inputs where your program is defined.** Where you invoked UB, it owes you nothing at all.

---

## Related
<!-- bite: b0e6a379-5da0-4796-aa28-2e7dce2aa62d -->
- [[languages/04-c/13-debugging-and-tooling|Debugging and Tooling]] — the sanitizers in depth
- [[languages/04-c/04-types-and-integers|Types and Integers]] — signed overflow, promotion
- [[languages/04-c/07-memory-management|Memory Management]] — the memory-related half
- [[languages/03-rust/15-unsafe-and-ffi|Rust: Unsafe]] — the same UB, confined to blocks you opt into
- [[languages/04-c/index|C course map]]

## About this lesson
<!-- bite: 4b90112e-bb60-4165-9da2-9d62ad73e20c -->

**Level:** Intermediate → Advanced. **Covers:** The most misunderstood thing about C. Not "unpredictable output" — a licence for the compiler to assume your code cannot do what it does.
