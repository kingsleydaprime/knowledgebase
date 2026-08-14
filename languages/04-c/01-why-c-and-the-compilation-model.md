# Why C, and the Compilation Model

**[Beginner]** — Why a language from 1972 is still under everything, and the four-stage pipeline that turns your text into a binary.

**Source:** `[reference]` — no C project in this vault yet. See [[project-ideas|Project Ideas]].

## Why C still matters

C is small — the entire language fits in a short book — and it maps almost directly onto how a machine works. That combination made it the substrate everything else got built on.

Concretely, C is still what you're standing on:

- **Every operating system kernel** — Linux, Windows, macOS/XNU, and every RTOS
- **Every language runtime** — CPython, the JVM's HotSpot, V8, the Go runtime, Ruby, PHP
- **The databases** — SQLite, PostgreSQL, MySQL, Redis
- **The infrastructure** — nginx, OpenSSL, curl, git, ffmpeg, SQLite again
- **Embedded and firmware**, near-universally → [[hardware/README|hardware/]]
- **The ABI everything speaks.** When Rust, Python, or Java calls into another language, it speaks C's calling convention. C is the lingua franca of FFI — which is why [[languages/03-rust/15-unsafe-and-ffi|Rust's FFI note]] is entirely about C compatibility.

So even if you never ship C, you read it: to understand a kernel bug, to debug a library, to know what your runtime is doing.

## What you're signing up for

The honest framing, especially having just done [[languages/03-rust/README|Rust]]:

C gives you **no safety at all**. No bounds checking, no ownership, no lifetimes, no type safety across a `void*`, no null protection, no automatic memory management, no exceptions, no destructors, no strings, no collections, no modules, no namespaces.

There is **you**, and there is what the machine does.

That's why **~70% of serious security vulnerabilities in large C/C++ codebases are memory-safety bugs** — the figure Microsoft and Google both publish. Not because C programmers are careless, but because the language provides no mechanism to be careful *with*, and humans do not maintain perfect vigilance across a million lines. → [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|Exploits]]

The correct attitude: **learn C to understand the machine and read the world's infrastructure. Reach for it for new projects only when you genuinely need it** — embedded targets with no Rust toolchain, existing C codebases, or a stable ABI boundary.

## The compilation pipeline

C compilation is four distinct stages. Knowing them is what makes linker errors readable instead of terrifying.

```
hello.c
   │
   │  1. PREPROCESS   cpp        — text substitution: #include, #define, #if
   ▼
hello.i   (still C, but expanded — often 20,000+ lines from one #include <stdio.h>)
   │
   │  2. COMPILE      cc1        — parse, type-check, optimise, emit assembly
   ▼
hello.s   (assembly for your target architecture)
   │
   │  3. ASSEMBLE     as         — assembly → machine code
   ▼
hello.o   (OBJECT FILE — machine code with unresolved symbols)
   │
   │  4. LINK         ld         — resolve symbols across object files and libraries
   ▼
hello     (executable)
```

You can stop at any stage and look:

```bash
gcc -E hello.c -o hello.i     # preprocess only — see what #include actually pasted in
gcc -S hello.c -o hello.s     # stop after compiling — read the assembly
gcc -c hello.c -o hello.o     # stop after assembling — one object file
gcc hello.o -o hello          # link
gcc hello.c -o hello          # all four
```

`gcc -E` on a file that includes `<stdio.h>` is worth running once, just to see that `#include` is *literally pasting a file in*. It explains a lot of C's design.

### Why stages 3 and 4 are separate

Each `.c` file compiles **independently** into a `.o`. The compiler sees one file and nothing else — this is the **translation unit**, and it's the single most important concept in the next note.

Separate compilation is why:

- Changing one `.c` file only recompiles that file
- The compiler can't check calls across files (it hasn't seen the other file) — **headers exist to fix this**
- Linker errors are a different species from compiler errors

```
undefined reference to `foo'          ← LINKER: nobody defined foo. Missing .c file or -l flag
multiple definition of `foo'          ← LINKER: two translation units both defined it
implicit declaration of function      ← COMPILER: you called foo without declaring it. Missing #include
```

Reading which stage failed tells you where to look. A compiler error is in your code; a linker error is in your build.

## Compiling properly

```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -g -O2 main.c -o main
```

| Flag | Does |
|---|---|
| `-std=c17` | pin the language standard (`c99`, `c11`, `c17`, `c23`) |
| `-Wall -Wextra` | **turn on warnings — C's defaults are far too quiet** |
| `-Wpedantic` | warn on non-standard extensions |
| `-Werror` | warnings become errors; correct for CI |
| `-g` | debug symbols, for `gdb` |
| `-O0 / -O2 / -O3` | optimisation level; `-O0` for debugging |
| `-fsanitize=address,undefined` | runtime bug detection → [[languages/04-c/13-debugging-and-tooling\|Debugging and Tooling]] |
| `-I dir` | where to look for headers |
| `-L dir -lfoo` | link `libfoo` from `dir` |

> **`-Wall -Wextra` is not optional.** C compiles a shocking amount of broken code silently by default. Most of the classic beginner disasters produce a warning that nobody enabled.

## Hello, world

```c
#include <stdio.h>

int main(void) {
    printf("Hello, world!\n");
    return 0;
}
```

- **`#include <stdio.h>`** — a preprocessor directive that pastes the file in. `<>` searches system paths, `""` searches your project first.
- **`int main(void)`** — `void` explicitly means "no parameters". Bare `main()` means "unspecified parameters", which is different and worse. Use `int main(void)` or `int main(int argc, char **argv)`.
- **`return 0`** — 0 is success. Non-zero is failure, and that's what a shell's `$?` and `&&` read → [[devops/01-linux/12-bash-scripting|Bash Scripting]].
- **`\n` matters.** `stdout` is line-buffered to a terminal; without a newline your output may not appear when you expect.

## Static vs dynamic linking

```bash
gcc main.c -o main                    # dynamic by default — links libc at RUN time
gcc -static main.c -o main            # static — everything baked in, big binary
ldd main                              # what shared libraries does this need?
```

Dynamic linking means the binary depends on `libc.so` existing on the target machine, at a compatible version. That's the "works on my machine, glibc version mismatch in the container" problem, and it's the reason [[languages/02-go/01-why-go-and-the-toolchain|Go's static binaries]] are considered such a deployment advantage.

## The standards

| Standard | Notable |
|---|---|
| **C89/C90** | the old baseline; declarations must precede statements |
| **C99** | `//` comments, declare-anywhere, `stdint.h`, `bool`, VLAs, designated initialisers |
| **C11** | `_Static_assert`, atomics, threads, anonymous structs |
| **C17** | bug fixes only |
| **C23** | `nullptr`, `constexpr`, `typeof`, `#embed`, `bool` as a keyword |

**Default to C11 or C17.** C99 is the floor for anything modern; C89 only for genuinely ancient targets.

---

## Related
- [[languages/04-c/02-headers-and-the-translation-unit|Headers and the Translation Unit]] — the model this pipeline implies
- [[languages/04-c/10-undefined-behaviour|Undefined Behaviour]] — the price of no safety net
- [[languages/03-rust/01-why-rust-and-the-toolchain|Rust: Why Rust]] — the language built to replace this one
- [[foundations/os/README|Operating Systems]] — written in C, all of them
- [[languages/04-c/README|C course map]]
