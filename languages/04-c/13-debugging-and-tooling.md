# Debugging and Tooling

**[Intermediate → Advanced]** — In a language with no safety net, the tooling *is* the safety net. This is the note that most changes whether your C works.

## Compile with warnings on

The cheapest bug-finding available, and it's off by default:

```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -Wshadow -Wconversion \
    -Wstrict-prototypes -Wwrite-strings -Wcast-qual -Wformat=2 \
    -g -O2 main.c -o main
```

| Flag | Catches |
|---|---|
| `-Wall -Wextra` | the essential set — always on |
| `-Wshadow` | an inner variable hiding an outer one |
| `-Wconversion` | implicit narrowing conversions |
| `-Wstrict-prototypes` | `f()` where you meant `f(void)` |
| `-Wwrite-strings` | assigning a literal to `char *` |
| `-Wcast-qual` | casting away `const` |
| `-Wformat=2` | `printf` format mismatches, non-literal format strings |
| `-Werror` | make them all fatal — correct for CI |

## Sanitizers

The single highest-value tool in modern C. They instrument the binary at compile time.

```bash
# AddressSanitizer — memory errors
gcc -fsanitize=address -fno-omit-frame-pointer -g -O1 prog.c && ./a.out

# UndefinedBehaviorSanitizer
gcc -fsanitize=undefined -fno-omit-frame-pointer -g prog.c && ./a.out

# Both — the normal combination
gcc -fsanitize=address,undefined -fno-omit-frame-pointer -g -O1 prog.c

# ThreadSanitizer — data races. Incompatible with ASan; run separately
gcc -fsanitize=thread -g prog.c

# MemorySanitizer — reads of uninitialised memory. Clang only
clang -fsanitize=memory -fno-omit-frame-pointer -g prog.c
```

**ASan finds:** heap and stack buffer overflow, use-after-free, use-after-return, use-after-scope, double free, invalid free, and memory leaks at exit.

**UBSan finds:** signed overflow, bad shifts, misaligned access, null dereference, out-of-bounds indexing where the bound is known, invalid enum and bool values.

The output is genuinely good:

```
==12345==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x60200000eff4
WRITE of size 4 at 0x60200000eff4 thread T0
    #0 0x4f8b2a in main /home/k/prog.c:12:5

0x60200000eff4 is located 0 bytes to the right of 4-byte region [0x60200000eff0,0x60200000eff4)
allocated by thread T0 here:
    #0 0x4f5c1d in malloc
    #1 0x4f8ae2 in main /home/k/prog.c:10:15
```

It gives you the faulting line, the allocation site, and the exact overrun. Compare with the alternative — a segfault somewhere unrelated, ten minutes later.

**Costs:** ASan is ~2× slower and ~3× memory; UBSan is cheap; TSan is ~10× and heavy. All are dev/CI tools, not production. `-O1` is the recommended level (`-O0` is very slow, `-O2` can inline away frames).

Useful runtime options:

```bash
ASAN_OPTIONS=detect_leaks=1:abort_on_error=1 ./prog
UBSAN_OPTIONS=print_stacktrace=1 ./prog
```

> **Run your test suite under `-fsanitize=address,undefined` in CI.** If you take one thing from this note, take this. It converts a class of silent corruption into a loud, located failure.

## Valgrind

Runs an unmodified binary under an emulated CPU — no recompilation needed, catches slightly different things, ~20× slower.

```bash
valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes ./prog
```

```
==1234== Invalid write of size 4
==1234==    at 0x1091AE: main (prog.c:12)
==1234==  Address 0x4a4a044 is 0 bytes after a block of size 4 alloc'd

==1234== LEAK SUMMARY:
==1234==    definitely lost: 100 bytes in 1 blocks
==1234==    indirectly lost: 0 bytes in 0 blocks
==1234==      possibly lost: 0 bytes in 0 blocks
```

`--track-origins=yes` tells you where an uninitialised value came from, which is its best feature.

Other tools in the suite:

```bash
valgrind --tool=callgrind ./prog     # call graph profiling; view with kcachegrind
valgrind --tool=helgrind ./prog      # race detection
valgrind --tool=massif ./prog        # heap profiling over time
```

**ASan vs Valgrind:** ASan is faster and catches stack overflows and use-after-return, which Valgrind misses. Valgrind needs no recompile and catches uninitialised reads that ASan doesn't. Use ASan routinely; reach for Valgrind when ASan comes up empty.

## `gdb`

```bash
gcc -g -O0 prog.c -o prog        # -g for symbols, -O0 so the code matches the source
gdb ./prog
gdb --args ./prog arg1 arg2
gdb -p 1234                       # attach to a running process
```

```
(gdb) run                     r
(gdb) break main              b main
(gdb) break prog.c:42         b prog.c:42
(gdb) break f if x > 100      conditional breakpoint
(gdb) next                    n     step OVER
(gdb) step                    s     step INTO
(gdb) finish                        run until this function returns
(gdb) continue                c

(gdb) print x                 p x
(gdb) print *ptr
(gdb) print arr[0]@10               print 10 elements from arr[0]
(gdb) x/16xb ptr                    examine 16 bytes in hex
(gdb) ptype var                     what type is this
(gdb) info locals
(gdb) backtrace               bt    THE MOST USEFUL COMMAND
(gdb) frame 2                       switch stack frame
(gdb) watch x                       break when x CHANGES
(gdb) layout src                    TUI mode — source alongside the prompt
```

`print arr[0]@10` and `watch` are the two most under-used commands. A watchpoint on a variable being mysteriously corrupted takes you straight to the writer.

### Core dumps

```bash
ulimit -c unlimited                       # enable them for this shell
cat /proc/sys/kernel/core_pattern         # where they go (often piped to systemd-coredump)
coredumpctl list && coredumpctl gdb       # systemd systems
gdb ./prog core                            # or load one directly
(gdb) bt full
```

A crash in production with a core dump is a solved problem. Without one you're reading logs.

## Profiling

```bash
perf stat ./prog                             # cycles, instructions, cache misses, IPC
perf record -g ./prog && perf report         # sampling profiler with call graphs
perf top                                      # live

gprof                                         # older, needs -pg; largely superseded
valgrind --tool=callgrind ./prog              # exact counts, very slow
```

Flame graphs, which are the most readable form:

```bash
perf record -F 99 -g ./prog
perf script | stackcollapse-perf.pl | flamegraph.pl > out.svg
```

`perf stat` first — if IPC is low and cache misses are high, the problem is memory layout, not algorithm. → [[languages/04-c/08-structs-unions-and-layout|Structs and Layout]]

## Static analysis

Finds bugs without running the program, so it isn't limited to executed paths:

```bash
clang --analyze prog.c
scan-build make                    # clang analyzer over a whole build
cppcheck --enable=all --inconclusive src/
gcc -fanalyzer prog.c              # GCC 10+; genuinely good now
clang-tidy prog.c -- -Iinclude
```

`gcc -fanalyzer` catches double-free, use-after-free, leaks and null dereferences at compile time, with a path explanation. It's worth turning on.

## Fuzzing

For anything that parses untrusted input, this finds bugs nothing else will:

```bash
# libFuzzer (clang)
clang -fsanitize=fuzzer,address,undefined fuzz_target.c -o fuzzer
./fuzzer corpus/ -max_total_time=60
```

```c
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    parse(data, size);        // ASan+UBSan catch anything it triggers
    return 0;
}
```

AFL++ is the other standard option. Fuzzing plus sanitizers is how the serious C projects — OpenSSL, curl, SQLite — actually stay alive; OSS-Fuzz runs this continuously against hundreds of them.

## Editor tooling

```bash
# generate compile_commands.json, which clangd reads
cmake -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
bear -- make            # for Make-based builds
```

`clangd` gives you go-to-definition, find-references, inline diagnostics and refactoring in any LSP editor. **This is a large quality-of-life difference** and it needs `compile_commands.json` — without it, clangd doesn't know your include paths or defines and half its features degrade.

```bash
clang-format -i src/*.c        # formatting; .clang-format at the project root
```

## The workflow that actually works

1. **Warnings maximal**, `-Werror` in CI
2. **`gcc -fanalyzer` / `clang-tidy`** in CI
3. **Every test under ASan + UBSan**, always
4. **Valgrind** when ASan finds nothing and something's still wrong
5. **`gdb`** for a specific crash — start with `bt`
6. **Fuzz anything that parses untrusted input**
7. **`perf stat` before optimising anything**

None of this is optional in the way it might be in a memory-safe language. C gives you no guarantees, so the tooling is where the guarantees come from — and a C project without sanitizers in CI is shipping bugs it could have found for free.

---

## Related
- [[languages/04-c/10-undefined-behaviour|Undefined Behaviour]] — what these tools detect
- [[languages/04-c/07-memory-management|Memory Management]] — the bug classes
- [[languages/04-c/12-build-systems|Build Systems]] — wiring the flags in
- [[devops/06-ci-cd/08-ci-pipelines|CI Pipelines]] — where sanitizers belong
- [[languages/04-c/README|C course map]]
