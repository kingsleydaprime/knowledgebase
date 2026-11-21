---
id: c7dd0ab3-1886-46c0-9497-dbeaeef5c2e1
---

# Arrays, Strings and Decay

An array is a row of values of the same type sitting next to each other in memory, and a string in C is just an array of characters with a zero at the end. Every name, message and file path a C program handles is stored this way. "Decay" is the rule that turns an array into a pointer in most places, and it explains much of how C arrays behave.

## Arrays
<!-- bite: f4089a54-90cf-40c4-8f47-2d75e5201567 -->

```c
int a[5];                          // uninitialised — contains garbage
int a[5] = {1, 2, 3, 4, 5};
int a[5] = {0};                    // ALL elements zero — the idiom
int a[]  = {1, 2, 3};              // size inferred: 3
int a[5] = {[2] = 30, [4] = 50};   // designated initialisers (C99)

size_t n = sizeof a / sizeof a[0]; // element count — only works where a is a real array
```

Arrays are contiguous, fixed at compile time (unless VLA), and **there is no bounds checking**:

```c
int a[5];
a[10] = 1;        // compiles, no warning, corrupts whatever is at that address
a[-1] = 1;        // also fine, as far as the language is concerned
```

An array carries **no length information at runtime**. `sizeof` works at compile time only, and only while the compiler can see the array's declaration.

## Decay — the rule that explains everything
<!-- bite: 97a2158f-99c0-4cc4-95c2-716224347d78 -->

> **In almost every expression, an array's name converts to a pointer to its first element.**

```c
int a[5];
int *p = a;          // implicit — a decays to &a[0]
a[2] == *(a + 2)     // indexing IS pointer arithmetic
```

The three exceptions where an array stays an array: `sizeof a`, `&a`, and a string literal initialising a `char` array.

Decay is why this is a trap:

```c
void f(int arr[5]) {                      // looks like it takes an array of 5
    printf("%zu\n", sizeof arr);          // 8 — it's an int*, not an array
}

int main(void) {
    int a[5];
    printf("%zu\n", sizeof a);            // 20 — here it IS an array
    f(a);
}
```

**Arrays are never passed by value in C.** `void f(int arr[5])`, `void f(int arr[])` and `void f(int *arr)` are the *same declaration*. The `5` is documentation the compiler discards.

The consequence, which is the root of a whole bug class:

> **A function receiving an array cannot know its size. You must pass the length.**

```c
void process(const int *arr, size_t n);       // the only correct shape
```

Every buffer overflow starts with someone not doing this, or passing the wrong `n`.

To keep a real array, pass a pointer to it:

```c
void f(int (*arr)[5]) { printf("%zu\n", sizeof *arr); }   // 20
f(&a);
```

Rarely used, but it's what makes `int (*)[5]` comprehensible when you meet it.

## Multidimensional arrays
<!-- bite: 49ebea7f-9c45-46db-ae68-b0913b09a0d8 -->

```c
int grid[3][4];              // 3 rows of 4 — CONTIGUOUS, row-major
grid[1][2] = 5;
```

The memory is one flat block of 12 ints. `grid[1][2]` is `*(*(grid + 1) + 2)`, which is offset `1*4 + 2`.

Decay applies to the *first* dimension only, so a parameter must specify the rest:

```c
void f(int g[][4], size_t rows);      // the 4 is REQUIRED — it's the row stride
void f(int (*g)[4], size_t rows);     // identical
```

Because it's contiguous and row-major, iterating rows-then-columns is cache-friendly and the reverse is not. On a large matrix that's an easy 5–10× difference — the clearest everyday example of why memory layout matters. → [[languages/03-rust/18-performance-and-zero-cost|cache locality]]

An "array of pointers" is a genuinely different thing:

```c
int *rows[3];               // 3 pointers, each to a separately allocated row — NOT contiguous
```

## Strings are a convention
<!-- bite: 6bca8d30-e28e-41aa-9d15-a67c0a72114e -->

**C has no string type.** A "string" is a `char` array whose end is marked by a `'\0'` byte.

```c
char s[] = "hello";        // 6 bytes: 'h','e','l','l','o','\0' — MUTABLE copy
char *p  = "hello";        // pointer to a string LITERAL — read-only, do not modify
const char *p = "hello";   // correct: say so
```

```c
p[0] = 'H';                // UB — literals usually live in a read-only page. Segfault.
```

**Always declare string-literal pointers `const char *`.** C++ requires it; C allows the unsafe form for historical reasons.

The NUL terminator means:

- **Length is O(n)** — `strlen` walks until it finds the zero
- **A string cannot contain a zero byte**, which is why binary data needs a pointer + length
- **Lose the terminator and every string function runs off the end**

## `<string.h>`, and which functions to avoid
<!-- bite: 10179a0c-7f7e-47b1-9458-9727bc953c3b -->

```c
size_t strlen(const char *s);
char  *strcpy(char *dst, const char *src);          // ☠ no bounds check
char  *strncpy(char *dst, const char *src, size_t n); // ⚠ may not NUL-terminate
char  *strcat(char *dst, const char *src);          // ☠ no bounds check
int    strcmp(const char *a, const char *b);        // 0 if equal
char  *strchr(const char *s, int c);
char  *strstr(const char *h, const char *n);
void  *memcpy(void *dst, const void *src, size_t n);   // regions must NOT overlap
void  *memmove(void *dst, const void *src, size_t n);  // overlap is fine
void  *memset(void *s, int c, size_t n);
int    memcmp(const void *a, const void *b, size_t n);
```

```c
char buf[10];
strcpy(buf, "this is much longer than ten bytes");   // overflows. No error. No warning.
```

**This is the buffer overflow**, and it is the single most exploited bug class in the history of computing. Overflow a stack buffer and you can overwrite the saved return address, redirecting execution to code of the attacker's choosing. → [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|Exploits]]

`strncpy` is the classic wrong fix:

```c
char buf[10];
strncpy(buf, "0123456789abc", sizeof buf);   // copies 10 bytes, NO terminator
printf("%s", buf);                            // reads past the end
```

`strncpy` was designed for fixed-width records, not for safe copying. If the source is longer than `n`, it truncates *without* a NUL.

**What to use:**

```c
snprintf(buf, sizeof buf, "%s", src);    // always NUL-terminates; portable; use this

strlcpy(dst, src, sizeof dst);           // BSD/glibc 2.38+; truncates AND terminates
strlcat(dst, src, sizeof dst);
```

`snprintf` is the portable answer for both copy and concatenate. It returns the length it *wanted* to write, so you can detect truncation:

```c
int n = snprintf(buf, sizeof buf, "%s/%s", dir, file);
if (n < 0 || (size_t)n >= sizeof buf) { /* truncated */ }
```

**Never use `gets`.** It was removed from the language in C11 because there is no safe way to call it. Use `fgets`:

```c
char line[256];
if (fgets(line, sizeof line, stdin)) {
    line[strcspn(line, "\n")] = '\0';   // fgets KEEPS the newline; strip it
}
```

## The `sizeof` trap
<!-- bite: f760dc8d-f430-49c8-b42e-411f725b4db8 -->

```c
void f(char *buf) {
    snprintf(buf, sizeof buf, "...");   // WRONG — sizeof a pointer is 8
}
```

`sizeof buf` inside the function is the pointer's size, not the buffer's. Decay again. This is why buffer size must be a parameter:

```c
void f(char *buf, size_t bufsz) {
    snprintf(buf, bufsz, "...");
}
```

`sizeof buf` is only correct where `buf` is a declared array in scope.

## Off-by-one, and the `+ 1`
<!-- bite: 0244af6d-60d6-4f9a-ba87-86730eef6f25 -->

```c
char *dup = malloc(strlen(s));          // WRONG — no room for '\0'
char *dup = malloc(strlen(s) + 1);      // correct
strcpy(dup, s);
```

Forgetting `+ 1` for the terminator is probably the most common single C bug. `strdup` does it for you and is in POSIX (and C23).

## Unicode
<!-- bite: a5567480-8309-492c-8af3-6a9c9f73a8e5 -->

`char` is a byte. A UTF-8 code point is 1–4 bytes, so:

```c
strlen("héllo")     // 6 — bytes, not characters
```

C's standard library has essentially no UTF-8 support. `wchar_t` is 2 bytes on Windows and 4 on Linux and is best avoided. In practice: treat strings as UTF-8 bytes, use a library (ICU, utf8proc) if you need real text processing, and never index into a string by "character".

Both [[languages/02-go/02-language-fundamentals|Go]] and [[languages/03-rust/02-language-fundamentals|Rust]] make strings UTF-8 by definition and refuse or discourage byte indexing. C gives you bytes and no opinion.

## Practical rules
<!-- bite: 95d4d644-6837-47da-b1f2-563832074602 -->

1. **Always pass the buffer size** alongside a pointer.
2. **`snprintf` over `strcpy`/`strcat`/`sprintf`.** Never `gets`.
3. **`const char *` for string literals.**
4. **Remember the `+ 1`.**
5. **`sizeof arr` only where `arr` is a real array in scope.**
6. **Check `snprintf`'s return value** if truncation matters.
7. **`memmove` when regions might overlap.**

---

## Related
<!-- bite: b76acc80-4df2-44b3-aabf-0047a9fe36f7 -->
- [[languages/04-c/05-pointers|Pointers]] — what arrays decay into
- [[languages/04-c/07-memory-management|Memory Management]] — allocating for strings
- [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|Exploits]] — where buffer overflows lead
- [[languages/03-rust/04-borrowing-and-references|Rust: Slices]] — a pointer that carries its length
- [[languages/04-c/index|C course map]]

## About this lesson
<!-- bite: fdc78b76-4792-4f4c-a88b-38ba87e97b5f -->

**Level:** Beginner → Intermediate. **Covers:** Arrays that turn into pointers when you're not looking, and strings that are just bytes with a convention — which is where most of the security industry comes from.
