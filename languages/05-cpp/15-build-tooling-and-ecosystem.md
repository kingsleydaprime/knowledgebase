# Build Tooling and Ecosystem

**[Intermediate]** — CMake, the package-manager situation, and the tools that catch what the compiler won't.

## CMake

The de facto standard, and it generates rather than executes — producing Makefiles, Ninja files, or IDE projects from one description. Everything in [[languages/04-c/12-build-systems|the C build note]] applies; here's the C++-shaped version.

```cmake
cmake_minimum_required(VERSION 3.20)
project(myproject VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)                 # -std=c++20, not -std=gnu++20
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)         # for clangd

add_library(core
    src/parser.cpp
    src/engine.cpp)

target_include_directories(core
    PUBLIC  ${CMAKE_CURRENT_SOURCE_DIR}/include
    PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

target_compile_features(core PUBLIC cxx_std_20)
target_compile_options(core PRIVATE -Wall -Wextra -Wpedantic)

add_executable(app src/main.cpp)
target_link_libraries(app PRIVATE core)

enable_testing()
add_subdirectory(tests)
```

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release -G Ninja
cmake --build build -j
ctest --test-dir build --output-on-failure
```

**"Modern CMake" means target-based.** Use `target_*` commands exclusively; never the old global `include_directories()` / `add_definitions()`. The visibility keywords are the whole point:

- **`PRIVATE`** — needed to build this target only
- **`PUBLIC`** — needed by this target *and* anything linking it
- **`INTERFACE`** — needed only by consumers (header-only libraries)

Get these right and consumers inherit include paths and flags automatically, which is what makes a library usable without documentation.

**Presets** (CMake 3.19+) replace the pile of shell scripts everyone used to have:

```json
// CMakePresets.json
{
  "version": 3,
  "configurePresets": [
    { "name": "debug",  "binaryDir": "build/debug",
      "cacheVariables": { "CMAKE_BUILD_TYPE": "Debug",
                          "CMAKE_CXX_FLAGS": "-fsanitize=address,undefined" } },
    { "name": "release", "binaryDir": "build/release",
      "cacheVariables": { "CMAKE_BUILD_TYPE": "Release" } }
  ]
}
```

```bash
cmake --preset debug && cmake --build build/debug
```

**Use Ninja** (`-G Ninja`). It's substantially faster than Make for large builds and parallelises better.

## Package management

C++ has no equivalent of Cargo or Go modules. What exists:

**vcpkg** (Microsoft) — the closest to a normal experience:

```bash
vcpkg install fmt spdlog catch2
cmake -B build -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
```

```json
// vcpkg.json — manifest mode, versions pinned per project
{ "dependencies": ["fmt", "spdlog", "catch2"] }
```

**Conan** — Python-based, binary caching, strong in industry:

```ini
# conanfile.txt
[requires]
fmt/10.2.1
[generators]
CMakeDeps
CMakeToolchain
```

**CPM.cmake** — a thin wrapper over `FetchContent`; no external tool needed:

```cmake
CPMAddPackage("gh:fmtlib/fmt#10.2.1")
target_link_libraries(app PRIVATE fmt::fmt)
```

**FetchContent** — built into CMake, no dependencies at all:

```cmake
include(FetchContent)
FetchContent_Declare(fmt GIT_REPOSITORY https://github.com/fmtlib/fmt GIT_TAG 10.2.1)
FetchContent_MakeAvailable(fmt)
```

**System packages / vendoring / submodules** — as in C.

> **For a new project: vcpkg manifest mode, or CPM if you want zero extra tooling.** Neither is Cargo. Expect to spend real time on this, and expect C++ projects to have far fewer dependencies as a result — which is partly discipline and partly the friction.

## Libraries worth knowing

```
fmt          formatting (std::format's origin; use it pre-C++20)
spdlog       logging, built on fmt
Catch2       testing — header-only, expressive
GoogleTest   testing — the industry default, with GoogleMock
Boost        the enormous incubator; much of it became the standard library
Abseil       Google's extensions — StatusOr, flat_hash_map, string utilities
nlohmann/json  JSON, with a very pleasant API
Eigen        linear algebra, expression templates
asio         networking and async (standalone or Boost); the basis of the proposed std::net
```

`nlohmann/json` and `fmt` are the two that most improve day-to-day C++ immediately.

## Testing

```cpp
// Catch2
#define CATCH_CONFIG_MAIN
#include <catch2/catch_test_macros.hpp>

TEST_CASE("stack push and pop", "[stack]") {
    Stack<int> s;
    REQUIRE(s.size() == 0);

    SECTION("after push") {          // each SECTION reruns the whole TEST_CASE
        s.push(42);
        REQUIRE(s.size() == 1);
        REQUIRE(*s.pop() == 42);
    }
}
```

```cpp
// GoogleTest
#include <gtest/gtest.h>

TEST(StackTest, PushIncreasesSize) {
    Stack<int> s;
    s.push(42);
    EXPECT_EQ(s.size(), 1);          // EXPECT_ continues; ASSERT_ aborts the test
}

TEST_P(...)                           // parameterised
MOCK_METHOD(...)                      // GoogleMock
```

**Catch2** for a new project (header-only, `SECTION` is a genuinely good idea); **GoogleTest** if you want mocking or match what most of the industry uses.

Wire into CTest so `ctest` runs everything:

```cmake
include(Catch)
catch_discover_tests(tests)
```

## The tools that catch what the compiler won't

### Warnings

```bash
-Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wsign-conversion
-Wnon-virtual-dtor          # a base class without a virtual destructor
-Wold-style-cast            # C casts in C++ code
-Wsuggest-override
-Woverloaded-virtual        # hiding a base virtual by overloading
-Wnull-dereference -Wdouble-promotion -Wformat=2
-Werror                     # in CI
```

`-Wnon-virtual-dtor` and `-Wsuggest-override` catch two of the [[languages/05-cpp/06-inheritance-and-virtual-dispatch|silent inheritance bugs]] directly.

### Sanitizers

```bash
-fsanitize=address,undefined -fno-omit-frame-pointer -g -O1
-fsanitize=thread                          # separate build — incompatible with ASan
-D_GLIBCXX_DEBUG                           # libstdc++ debug mode: checks iterator
                                           # invalidation, bad comparators, bounds
```

`_GLIBCXX_DEBUG` is the C++-specific one and it's under-used. It catches the [[languages/05-cpp/09-the-stl-containers|iterator invalidation]] bugs that ASan often misses, and turns "strict weak ordering violated" from a crash into a message.

### `clang-tidy`

```yaml
# .clang-tidy
Checks: >
  bugprone-*,
  cppcoreguidelines-*,
  modernize-*,
  performance-*,
  readability-*,
  -modernize-use-trailing-return-type
WarningsAsErrors: 'bugprone-*'
```

```bash
clang-tidy src/*.cpp -- -std=c++20 -Iinclude
run-clang-tidy -p build                     # parallel, over compile_commands.json
```

**This is the tool that enforces the modern subset** from [[languages/05-cpp/14-modern-cpp-and-modules|Modern C++]]. `modernize-*` will rewrite loops to range-for, `NULL` to `nullptr`, and `new` to `make_unique` — with `-fix`, automatically. On an older codebase that's a genuinely useful afternoon.

### Formatting and static analysis

```bash
clang-format -i src/*.cpp                   # .clang-format at the project root
cppcheck --enable=all --std=c++20 src/
g++ -fanalyzer                              # GCC's static analyzer
include-what-you-use                        # find unnecessary #includes
```

`clang-format` with a committed `.clang-format` ends style arguments the way `gofmt` does — just decided later and less completely.

### Compile-time and binary size

```bash
cmake --build build -- -j                   # parallelism first
ccache g++ ...                              # cache compilations; large win on rebuilds
clang -ftime-trace                          # per-file compile timeline (view in chrome://tracing)
ClangBuildAnalyzer                          # what's actually slow to compile
bloaty app                                  # what's in the binary
```

C++ build times are a real productivity cost, and the usual causes are template instantiation and heavy headers. **`ccache` and `-ftime-trace`** are the first two things to reach for. Longer-term: forward declarations, the pimpl idiom, extracting non-template code from templates, and eventually modules.

## A CI setup worth copying

```yaml
- Build: Debug + Release, GCC + Clang
- Warnings: -Wall -Wextra -Werror
- Tests under: -fsanitize=address,undefined AND -D_GLIBCXX_DEBUG
- Separate job: -fsanitize=thread
- clang-tidy on changed files
- clang-format --dry-run --Werror
- Coverage: gcov/lcov or llvm-cov
```

Building with **both GCC and Clang** catches more than either alone — they disagree about enough that it's a cheap correctness check.

---

## Related
- [[languages/05-cpp/14-modern-cpp-and-modules|Modern C++ and Modules]] — the subset `clang-tidy` enforces
- [[languages/04-c/12-build-systems|C: Build Systems]] — Make and the fundamentals
- [[languages/04-c/13-debugging-and-tooling|C: Debugging and Tooling]] — gdb, Valgrind, perf, all applicable
- [[devops/06-ci-cd/08-ci-pipelines|CI Pipelines]] — where this belongs
- [[languages/05-cpp/README|C++ course map]]
