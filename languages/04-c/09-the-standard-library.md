# The Standard Library

**[Intermediate]** — What C actually ships, which is far less than you're used to, and the parts of it that are traps.

## How small it is

There are no collections, no strings, no hash maps, no JSON, no networking, no threads before C11, no sorting beyond `qsort`, and no error type. The C standard library is roughly: I/O, string-and-memory functions, allocation, math, time, and a handful of utilities.

Everything else you either write or take as a dependency — which is why every large C project has its own vector, its own hash table, and its own string builder. That duplication is a real cost of the language.

## `<stdio.h>`

```c
printf("%s is %d\n", name, age);
fprintf(stderr, "error: %s\n", msg);
snprintf(buf, sizeof buf, "%d", n);        // the safe formatter
sprintf(buf, "%d", n);                      // ☠ no bound — avoid

int n = scanf("%d", &x);                    // returns items matched — CHECK IT
fgets(line, sizeof line, stdin);            // safe line input
```

**Format specifiers:**

```
%d %i   int              %u    unsigned
%ld     long             %lld  long long
%zu     size_t           %f %g  double
%c      char             %s    char* (NUL-terminated)
%p      void*            %x %o  hex / octal
%%      a literal %
%-10s   left-align in 10  %.2f  two decimals   %*d  width from an argument
%" PRId64 "  int64_t (from <inttypes.h>)
```

Two things that go wrong:

**Mismatched specifiers are undefined behaviour**, not a conversion:

```c
printf("%d\n", 3.14);          // UB — reads the wrong bytes
printf("%s\n", 42);            // UB — treats 42 as an address. Segfault.
```

`-Wformat` (in `-Wall`) catches these for literal format strings.

**Never pass user input as the format string:**

```c
printf(user_input);            // ☠ FORMAT STRING VULNERABILITY
printf("%s", user_input);      // correct
```

`%n` in a format string *writes* to memory. A user-controlled format string is an arbitrary-write primitive, and this was a major exploit class through the 2000s. → [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|Exploits]]

### Files

```c
FILE *f = fopen("data.txt", "r");        // "r" "w" "a" "r+" "w+" "rb" ...
if (!f) { perror("fopen"); return -1; }

fgets(buf, sizeof buf, f);
fread(buf, 1, n, f);
fwrite(buf, 1, n, f);
fprintf(f, "...");
fseek(f, 0, SEEK_END); long size = ftell(f); rewind(f);
fclose(f);                                // check the return value if you wrote data
```

`FILE *` is an opaque handle — the standard library's own example of the pattern from [[languages/04-c/11-modular-c-and-project-structure|Modular C]].

**Buffering matters.** `stdout` is line-buffered to a terminal and **fully buffered to a pipe or file** — which is why your output vanishes when you redirect and the program crashes:

```c
fflush(stdout);
setvbuf(stdout, NULL, _IONBF, 0);      // unbuffered
```

`stderr` is unbuffered, which is why debug output belongs there.

**Check `fclose`.** Data can still be in a buffer; a failed flush surfaces there and nowhere else.

## `<stdlib.h>`

```c
malloc calloc realloc free                 // → 07-memory-management

int   atoi(const char *s);                 // ☠ no error detection at all
long  strtol(const char *s, char **end, int base);   // use this

exit(EXIT_SUCCESS); exit(EXIT_FAILURE);
atexit(cleanup_fn);
abort();                                    // no cleanup, raises SIGABRT

qsort(base, n, size, cmp);
bsearch(key, base, n, size, cmp);

int r = rand();                             // ☠ NOT for anything security-related
srand(time(NULL));

char *v = getenv("HOME");                   // may be NULL
system("ls");                               // ☠ shell injection if any input is user-controlled
```

**`atoi` cannot report failure** — it returns 0 for both `"0"` and `"banana"`. Use `strtol`:

```c
errno = 0;
char *end;
long v = strtol(s, &end, 10);
if (end == s)                { /* no digits */ }
else if (*end != '\0')       { /* trailing garbage */ }
else if (errno == ERANGE)    { /* out of range */ }
```

Verbose, and it's the only way to parse an integer correctly in C.

**`rand()` is not a CSPRNG.** For anything security-relevant use `getrandom()` (Linux), `arc4random_buf()` (BSD/macOS), or read `/dev/urandom`. → [[cybersecurity/05-cryptography/README|Cryptography]]

## `<string.h>`

Covered in [[languages/04-c/06-arrays-strings-and-decay|Arrays, Strings and Decay]]. The summary:

- **Use:** `snprintf`, `memcpy`, `memmove`, `memset`, `strlen`, `strcmp`, `strchr`, `strstr`
- **Avoid:** `strcpy`, `strcat`, `sprintf` (no bounds), `strncpy` (may not terminate), `gets` (removed from the language)

`memset` for zeroing secrets is a trap — the optimiser deletes a write to memory that's about to be freed. Use `memset_s` (C11 Annex K), `explicit_bzero`, or a `volatile` function pointer.

## `<errno.h>`

```c
#include <errno.h>

errno = 0;                     // reset BEFORE the call
FILE *f = fopen(path, "r");
if (!f) {
    fprintf(stderr, "fopen: %s\n", strerror(errno));
    perror("fopen");           // prints "fopen: No such file or directory"
}
```

C's error mechanism: a thread-local global integer, set by library functions on failure.

Two rules: **only check `errno` after a function has indicated failure** (a successful call may set it anyway), and **reset it to 0 first** if the function you're calling doesn't have an unambiguous failure return.

Compared to [[languages/03-rust/07-option-and-result|`Result<T, E>`]] or even [[languages/02-go/05-errors|Go's error returns]], this is genuinely bad: it's easy to ignore, easy to clobber with an intervening call, and carries no context.

## `<math.h>`

```c
sqrt pow fabs floor ceil round trunc fmod
sin cos tan asin acos atan atan2
exp log log2 log10
isnan(x) isinf(x) fmin fmax
M_PI                            // POSIX, not ISO C — define your own for portability
```

**Link with `-lm`** on Linux, or you get `undefined reference to 'sqrt'` — a classic first linker error.

## `<time.h>`

```c
time_t now = time(NULL);
struct tm *lt = localtime(&now);          // returns a STATIC buffer — not thread-safe
localtime_r(&now, &tm_buf);               // POSIX reentrant version — prefer it

char buf[64];
strftime(buf, sizeof buf, "%Y-%m-%d %H:%M:%S", &tm);

clock_t start = clock();                  // CPU time, not wall time
clock_gettime(CLOCK_MONOTONIC, &ts);      // POSIX — use MONOTONIC for measuring elapsed time
```

`CLOCK_MONOTONIC` doesn't jump when NTP adjusts the clock. Measuring elapsed time with `CLOCK_REALTIME` produces negative durations occasionally, which is a genuinely confusing bug.

## Other headers

```c
<stdbool.h>   bool, true, false                    (C99)
<stdint.h>    int32_t, uint64_t, ...               → 04-types-and-integers
<inttypes.h>  PRId64 and friends, for printing them
<stddef.h>    size_t, ptrdiff_t, NULL, offsetof
<limits.h>    INT_MAX, CHAR_BIT, ...
<float.h>     DBL_EPSILON, ...
<assert.h>    assert(cond) — compiled out by -DNDEBUG
<ctype.h>     isalpha, isdigit, toupper — CAST THE ARGUMENT to unsigned char
<signal.h>    signal handling
<stdarg.h>    variadic functions
<threads.h>   C11 threads — poorly supported; everyone uses pthreads
```

```c
assert(ptr != NULL);           // a DEVELOPMENT check — disappears in release builds
```

**Assertions are for bugs, not for validation.** They vanish under `-DNDEBUG`, so anything that must hold in production needs a real check. Never put a side effect inside one.

### Variadic functions

```c
#include <stdarg.h>

int sum(int count, ...) {
    va_list args;
    va_start(args, count);
    int total = 0;
    for (int i = 0; i < count; i++) total += va_arg(args, int);
    va_end(args);
    return total;
}
```

**Completely type-unsafe** — `va_arg` trusts the type you name, and there's no way to know how many arguments were passed. That's why `printf` needs a format string and why a wrong specifier is UB. Use them for logging wrappers and little else.

## POSIX, which is where the real work is

The C standard has no files-as-descriptors, no networking, no processes, no threads. On Unix that's POSIX:

```c
<unistd.h>     read write close fork exec pipe dup2 sleep getpid
<fcntl.h>      open, O_RDONLY, O_CREAT
<sys/socket.h> socket bind listen accept connect send recv
<sys/stat.h>   stat, mkdir, permissions
<pthread.h>    pthread_create, mutexes, condition variables
<dirent.h>     opendir, readdir
<sys/mman.h>   mmap
```

This is what [[foundations/os/fundamentals|OS Fundamentals]] and [[foundations/networking/09-sockets-and-the-network-api|the sockets note]] cover, and it's what you'll actually use to build anything real. Portability to Windows means a compatibility layer or a library.

## Rules

1. **`snprintf` over `sprintf`. Never `gets`.**
2. **Never pass user input as a format string.**
3. **`strtol` over `atoi`.**
4. **Check `errno` only after a failure indication, and reset it first.**
5. **`-lm` for math.**
6. **`localtime_r`, `CLOCK_MONOTONIC`.**
7. **Cast to `unsigned char` for `<ctype.h>`.**
8. **`assert` for bugs, real checks for input.**

---

## Related
- [[languages/04-c/06-arrays-strings-and-decay|Arrays, Strings and Decay]] — the string functions in detail
- [[languages/04-c/07-memory-management|Memory Management]] — `malloc` and friends
- [[foundations/os/fundamentals|OS Fundamentals]] — where POSIX takes over
- [[foundations/networking/09-sockets-and-the-network-api|Sockets]] — the networking C doesn't have
- [[languages/04-c/README|C course map]]
