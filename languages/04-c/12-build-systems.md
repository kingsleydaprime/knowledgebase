# Build Systems

**[Intermediate]** — `make` from first principles, then CMake, then the honest state of C dependency management.

## Why a build system

Compiling by hand doesn't scale past a couple of files:

```bash
gcc -c src/stack.c -o build/stack.o
gcc -c src/parser.c -o build/parser.o
gcc -c src/main.c -o build/main.o
gcc build/*.o -o app -lm
```

You need something that recompiles **only what changed** — and to know that, it has to understand which files depend on which. Because [[languages/04-c/02-headers-and-the-translation-unit|`#include` is textual]], changing one header can require recompiling fifty `.c` files, and nothing in the language records that.

That dependency problem is what build systems exist for.

## `make`

Make's model is small: **targets, prerequisites, and recipes.** If any prerequisite is newer than the target, run the recipe.

```make
app: main.o stack.o
	gcc main.o stack.o -o app

main.o: main.c stack.h
	gcc -c main.c -o main.o

stack.o: stack.c stack.h
	gcc -c stack.c -o stack.o
```

> **Recipes must be indented with a TAB, not spaces.** This is Make's most notorious wart and it produces `Makefile:4: *** missing separator. Stop.`

### A real Makefile

```make
CC      := gcc
CFLAGS  := -std=c17 -Wall -Wextra -Wpedantic -g -O2 -Iinclude
LDFLAGS :=
LDLIBS  := -lm

SRC_DIR := src
OBJ_DIR := build
TARGET  := app

SRCS := $(wildcard $(SRC_DIR)/*.c)
OBJS := $(patsubst $(SRC_DIR)/%.c,$(OBJ_DIR)/%.o,$(SRCS))
DEPS := $(OBJS:.o=.d)

.PHONY: all clean test

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) $^ -o $@ $(LDLIBS)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c | $(OBJ_DIR)
	$(CC) $(CFLAGS) -MMD -MP -c $< -o $@

$(OBJ_DIR):
	mkdir -p $@

clean:
	rm -rf $(OBJ_DIR) $(TARGET)

-include $(DEPS)
```

Reading the unfamiliar parts:

| | |
|---|---|
| `:=` vs `=` | `:=` expands once (use this); `=` re-expands on every use |
| `$@` | the target |
| `$<` | the first prerequisite |
| `$^` | all prerequisites |
| `%` | pattern rule wildcard |
| `\|` | *order-only* prerequisite — must exist, but its timestamp is ignored |
| `.PHONY` | this target isn't a file (or a file named `clean` would break it) |

### `-MMD -MP` — the important two flags

This is how Make learns about headers. `-MMD` makes the compiler emit a `.d` file alongside each `.o`:

```make
build/stack.o: src/stack.c include/stack.h include/common.h
```

`-include $(DEPS)` pulls those in, so Make now knows `stack.o` depends on those headers and rebuilds it when they change. `-MP` adds dummy targets for the headers so deleting one doesn't break the build.

**Without this, editing a header doesn't trigger a rebuild**, and you get baffling behaviour where your change appears to do nothing. Hand-maintained header dependencies are the classic Makefile bug — this pair of flags fixes it permanently.

```bash
make -j$(nproc)          # parallel build — the easiest speedup available
make -n                  # dry run: print commands without running them
make -B                  # force rebuild everything
make --debug=b           # why did it decide to rebuild that?
```

## CMake

Make is a build *executor*. CMake is a build *generator* — it produces Makefiles, Ninja files, Visual Studio projects, or Xcode projects from one description. That cross-platform generation is why it won.

```cmake
cmake_minimum_required(VERSION 3.16)
project(myproject VERSION 1.0 LANGUAGES C)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)      # generates compile_commands.json

add_library(stack src/stack.c)
target_include_directories(stack PUBLIC include)
target_compile_options(stack PRIVATE -Wall -Wextra -Wpedantic)

add_executable(app src/main.c)
target_link_libraries(app PRIVATE stack m)

enable_testing()
add_executable(test_stack tests/test_stack.c)
target_link_libraries(test_stack PRIVATE stack)
add_test(NAME stack COMMAND test_stack)
```

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j
ctest --test-dir build
```

**"Modern CMake" means target-based.** Use `target_*` commands, never the old global `include_directories()` / `add_definitions()`. The visibility keywords are the point:

- **`PRIVATE`** — needed to build this target only
- **`PUBLIC`** — needed to build this target *and* anything linking it
- **`INTERFACE`** — needed only by consumers

Getting these right means dependencies propagate automatically and consumers don't have to know your include paths.

`CMAKE_EXPORT_COMPILE_COMMANDS` produces `compile_commands.json`, which is what `clangd` (and therefore your editor's autocomplete, go-to-definition and diagnostics) reads. **Turn it on.** For Make, `bear -- make` generates the same file.

## The alternatives

| Tool | Character |
|---|---|
| **Ninja** | very fast executor; you generate it from CMake or Meson, not by hand |
| **Meson** | cleaner syntax than CMake, generates Ninja. Genuinely nicer; smaller ecosystem |
| **Autotools** | `./configure && make && make install`. Ancient, arcane, still everywhere in GNU projects |
| **Bazel** | hermetic and reproducible; heavy, aimed at monorepos |
| **`zig cc`** | Zig's compiler as a drop-in C cross-compiler — genuinely useful for cross builds |

If you're starting fresh: **Make for something small, CMake for anything with dependencies or that others will build.**

## Dependencies — the honest state

C has **no standard package manager.** This is its biggest practical weakness compared to [[languages/02-go/12-modules-and-project-layout|Go modules]] or [[languages/03-rust/16-modules-cargo-and-testing|Cargo]].

What people actually do:

**1. System packages** — `apt install libcurl4-openssl-dev`, then `pkg-config`:

```make
CFLAGS  += $(shell pkg-config --cflags libcurl)
LDLIBS  += $(shell pkg-config --libs libcurl)
```

Easy, and it makes your build depend on the distro. Version pinning is whatever the distro shipped.

**2. Vendoring** — copy the source into `third_party/` and build it yourself. Ugly, and completely reproducible. Very common in serious C projects for exactly that reason.

**3. Header-only libraries** — drop in one `.h`. The [stb](https://github.com/nothings/stb) libraries popularised this and it's genuinely pleasant:

```c
#define STB_IMAGE_IMPLEMENTATION      // exactly ONE .c file does this
#include "stb_image.h"
```

**4. Git submodules** — `git submodule add`, then `add_subdirectory()`. Works; submodules are their own source of friction. → [[languages/03-rust/README|`git/16-power-tools`]] covers submodules.

**5. CMake FetchContent** — the closest thing to a package manager built in:

```cmake
include(FetchContent)
FetchContent_Declare(cjson
    GIT_REPOSITORY https://github.com/DaveGamble/cJSON.git
    GIT_TAG v1.7.18)
FetchContent_MakeAvailable(cjson)
target_link_libraries(app PRIVATE cjson)
```

**6. Conan / vcpkg** — real package managers, if the team adopts one.

The consequence of all this: **C projects minimise dependencies.** Where a Node project has 400 and a Rust project 50, a serious C project has five, and often writes its own hash table rather than take a sixth. That's partly discipline and partly the packaging story being bad enough to make dependencies genuinely expensive.

## Libraries

```bash
# Static — .a, an archive of .o files, copied into the binary
gcc -c stack.c -o stack.o
ar rcs libstack.a stack.o
gcc main.c -L. -lstack -o app        # -lstack finds libstack.a or libstack.so

# Shared — .so, loaded at run time
gcc -fPIC -c stack.c -o stack.o      # -fPIC: position-independent code, REQUIRED
gcc -shared stack.o -o libstack.so
gcc main.c -L. -lstack -o app
LD_LIBRARY_PATH=. ./app              # the loader must find it at RUN time
```

```bash
ldd app          # what shared libs does this need?
nm -D libstack.so   # what symbols does it export?
```

**Link order matters** with static libraries: `-l` flags must come *after* the objects that need them. `gcc -lm main.c` fails where `gcc main.c -lm` works, because the linker processes left to right and discards a library whose symbols nothing has requested yet. This trips up everyone once.

## A CI target worth having

```make
.PHONY: check
check: CFLAGS += -fsanitize=address,undefined -fno-omit-frame-pointer -g -O1
check: clean all
	./run_tests
```

Build and test under sanitizers as a separate target, since they're too slow for normal development but are where the real bugs surface. → [[devops/06-ci-cd/08-ci-pipelines|CI Pipelines]]

---

## Related
- [[languages/04-c/02-headers-and-the-translation-unit|Headers and the Translation Unit]] — the dependency problem `-MMD` solves
- [[languages/04-c/11-modular-c-and-project-structure|Modular C]] — the layout being built
- [[languages/04-c/13-debugging-and-tooling|Debugging and Tooling]] — the sanitizer flags
- [[languages/03-rust/16-modules-cargo-and-testing|Rust: Cargo]] — what a solved dependency story looks like
- [[languages/04-c/README|C course map]]
