# Building UniFootball — from source file to running game

See also: the general Linux notes in `devops/01-linux/`.

## 1. Installing the tools (Fedora)

```sh
sudo dnf install raylib-devel gcc make
pkg-config --modversion raylib     # → 5.5.0
```

- `gcc` is the C compiler. `make` runs the build steps written in the `Makefile`.
- `raylib-devel` installs two things: the **header** (`raylib.h`, which lists the functions so the compiler can check your calls) and the **library** (`libraylib.so`, the compiled code those functions actually run). A `-devel` package on Fedora (`-dev` on Ubuntu) is the version that includes the headers you compile against.
- `pkg-config` answers "what flags do I need to use library X?". `pkg-config --cflags raylib` gives compiler flags (where the headers are); `--libs raylib` gives linker flags (`-lraylib`). On Fedora the headers are in a standard place, so `--cflags` prints nothing, but the Makefile asks anyway so it still works on a machine where they live somewhere else.

## 2. Compiling vs linking

Building a C program happens in two steps:

1. **Compile**: each `.c` file becomes an **object file** (`.o`) of machine code. A call to `DrawRectangle` is left as a "fill this in later" note, because that function's code isn't in your file.
2. **Link**: all the `.o` files, plus libraries such as raylib and the maths library (`-lm`), get joined into one executable. The linker fills in those notes.

So two kinds of error look different:
- `error: implicit declaration of function 'DrawRectangle'` → **compile** error. You forgot `#include "raylib.h"`, or misspelled the name.
- `undefined reference to 'InitWindow'` → **link** error. The header was found but the library wasn't linked (`-lraylib` missing).

## 3. The Makefile, line by line

```make
CFLAGS  := -std=c11 -Wall -Wextra -Wpedantic -g -MMD -MP $(shell pkg-config --cflags raylib)
LDLIBS  := $(shell pkg-config --libs raylib) -lm
```
- `-std=c11`: use the 2011 C standard.
- `-Wall -Wextra -Wpedantic`: turn on almost every warning. In C, a warning is often a real bug, like an unused variable that should have been used, or a comparison between signed and unsigned numbers. Treat warnings as errors you fix.
- `-g`: include debug info, so `gdb` and the sanitizers can show file names and line numbers.
- `-MMD -MP`: write a `.d` file next to each `.o` that lists the headers it includes. The `-include $(DEP)` line at the bottom reads those files, so editing a header rebuilds every `.c` file that uses it.
- `$(shell ...)`: run a shell command and paste its output in.

```make
SRC := $(wildcard src/*.c)
OBJ := $(patsubst src/%.c,build/%.o,$(SRC))
```
Every `.c` file in `src/` gets built automatically, so adding `src/ball.c` later needs no Makefile change. `patsubst` turns `src/main.c` into `build/main.o`.

```make
build/%.o: src/%.c | build
	$(CC) $(CFLAGS) -c $< -o $@
```
A **pattern rule**: to make `build/X.o`, compile `src/X.c`. `$<` means "the first input", `$@` means "the target being made", and `$^` (in the link rule) means "all inputs". The `| build` part is an **order-only prerequisite**: the `build/` folder must exist first, but its timestamp changing shouldn't force a rebuild.

Make compares timestamps. If `main.o` is newer than `main.c`, it's skipped. That's why rebuilding a big project after one small edit is fast.

`.PHONY` marks targets that are names for actions (`run`, `clean`), not files, so a file that happened to be called `clean` wouldn't confuse make.

## 4. `make asan`: the memory-bug catcher

`-fsanitize=address,undefined` adds checks to the compiled program. Reading past the end of an array, using memory after `free`, or overflowing a signed integer then stops the program with a report naming the exact line, instead of crashing randomly later (or quietly giving wrong results). It's slower, so use it to hunt bugs, not for normal play.

## 5. Commands run while setting up

```sh
mkdir -p src                 # -p: also create parent folders, and don't fail if it already exists
make -n                      # dry run: print the commands make *would* run, without running them
```
