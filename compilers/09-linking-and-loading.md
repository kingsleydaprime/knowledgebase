# Linking and Loading

**[Intermediate → Advanced]** — What happens between "the compiler produced machine code" and "the program is running". The step every course skips, including this one until now.

## Before you start

- You know what a compiler emits — [[08-code-generation|code generation]].
- You can read basic assembly and know what an address is — [[foundations/computer-architecture/04-assembly|computer-architecture/assembly]].
- Access to `gcc`, `nm` and `readelf`. Any Linux machine has them.

**What you will be able to do after this lesson:**

1. Explain why compilation is separate from linking, and what each step can and cannot know.
2. Read an object file's symbol table and say which symbols are promises and which are definitions.
3. Explain what a relocation is and why position-dependent code needs one.
4. Explain the difference between static and dynamic linking, and what the dynamic loader does.

---

## 1. The gap this fills

[[08-code-generation|Code generation]] ends with assembly, and the assembler turns that into machine code. **But that machine code is not a program yet.**

```
   hello.c  --compile-->  hello.s  --assemble-->  hello.o  --link-->  hello
                                                      ^                  ^
                                              not runnable          runnable
```

**`hello.o` cannot run.** It contains your function, correctly compiled — and it also contains *references to things that are not in it*, with blanks where their addresses belong. Something must fill those blanks and decide where everything lives in memory.

**That something is the linker**, and the gap between object file and executable is where a surprising amount of real-world confusion lives: `undefined reference to`, `symbol not found`, version mismatches, "works on my machine".

## 2. Why compilation and linking are separate

**A compiler sees one file at a time.** That is a deliberate choice, and it buys two things:

**Incremental builds.** Change one file in a thousand-file project and only that file recompiles. If compilation required seeing everything, every edit would rebuild everything.

**Libraries.** You link against `libc` without having its source. Someone compiled it years ago; you supply only the names you want.

**The cost is that the compiler cannot know addresses.** When `main.c` calls `add()`, the compiler has no idea where `add` will end up in memory — that depends on what else gets linked and in what order. **So it leaves a hole and writes down what should fill it.**

## 3. Symbols: promises and definitions

**A symbol is a name with a kind.** Running `nm` on an object file shows them:

```
   main.o:
     U  add              UNDEFINED  - promised, not provided
     T  main             TEXT       - a function, defined here
     U  shared_counter   UNDEFINED  - promised, not provided

   lib.o:
     T  add              TEXT       - defined here
     t  helper           text       - defined here but STATIC
     B  shared_counter   BSS        - a zero-initialised variable
```

**`U` is a promise; `T`, `B` and `D` are definitions.** The linker's core job is matching every `U` to exactly one definition.

| Letter | Meaning |
| :--- | :--- |
| `U` | Undefined — referenced but not defined here |
| `T` | Text — a function, exported |
| `t` | text — a function, **`static`**, invisible to other files |
| `D` | Data — an initialised global |
| `B` | BSS — a zero-initialised global |

> [!NOTE]
> **Lowercase means local, and that is what `static` does in C.**
>
> `static int helper()` is not about storage duration — at file scope it means **do not export this symbol**. The function still exists in the object file, but the linker will not match another file's `U helper` to it.
>
> This is why `static` prevents name collisions between translation units, and why two files can each define `static void log()` without conflict. **The `t` versus `T` distinction *is* the mechanism.**

## 4. The sections of an object file

An object file is not a flat blob. It is divided by what the contents *are*:

| Section | Holds | Note |
| :--- | :--- | :--- |
| `.text` | machine code | read-only and executable at runtime |
| `.data` | initialised globals | the values are stored in the file |
| `.bss` | zero-initialised globals | **only a size** — no bytes in the file |
| `.rodata` | constants, string literals | read-only |
| `.symtab` | the symbol table | names, kinds, which section |
| `.rela.text` | relocations | the list of holes to patch |

**`.bss` is the clever one.** A million-element zero array needs no bytes on disk — just "reserve 8 MB of zeros". That is why a program with huge zeroed buffers has a small executable, and why `.bss` stands for "block started by symbol" and confuses everyone who looks it up.

## 5. Relocations: the holes and their instructions

When the compiler emits a call to a function it cannot locate, it writes a placeholder and records a **relocation entry**:

```
   R_X86_64_PLT32   patch a reference to 'add'
   R_X86_64_PC32    patch a reference to 'shared_counter'
```

**Each entry says: at this offset, once you know where this symbol lives, write its address in this format.**

**The format matters.** `PC32` means "a 32-bit offset relative to the program counter" — so the value written is not the address but the *distance* to it. That is what makes code relocatable: move the whole block and the relative distances still hold.

**This is the same idea as [[foundations/how-computers-work/08-capstone/02-the-isa|PRIME-1's PC-relative branches]]**, and it is why the disassembler in that module needed to know an instruction's address. Position-dependent encodings must be adjusted when code moves — and relocation is that adjustment, done once at link time.

## 6. What the linker actually does

**Four steps:**

1. **Collect** all input object files and libraries.
2. **Merge sections** — every `.text` concatenated into one, every `.data` into one, and so on.
3. **Resolve symbols** — match each `U` to exactly one definition. **Zero matches is `undefined reference`; two is `multiple definition`.**
4. **Apply relocations** — now that every symbol has a final address, patch every recorded hole.

**Then it writes an executable**, which differs from an object file mainly by having no unresolved symbols and by carrying an entry point — the address where execution starts.

> [!NOTE]
> **The entry point is not `main`.** It is `_start`, supplied by the C runtime (`crt0`).
>
> `_start` sets up the stack, arranges `argc` and `argv`, initialises the runtime, calls `main`, and then calls `exit` with whatever `main` returned. **`main` returning is not how a process ends** — the runtime calling `exit` is.
>
> That is why a C program without `main` links fine if you supply your own `_start`, and why "undefined reference to `main`" comes from the *runtime*, not the compiler.

## 7. Static versus dynamic linking

**Static** — copy the library's code into the executable.

**Dynamic** — record only the library's *name*, and resolve at load time.

| | Static | Dynamic |
| :--- | :--- | :--- |
| Executable size | Large — contains every routine used | Small — contains names |
| Startup | Immediate | Loader must map libraries first |
| Library security fix | **Relink every program** | Replace one file |
| Memory with many processes | Each has its own copy | **One copy shared** |
| Deployment | One self-contained file | Must ship or match the libraries |

**The dependency problem is the real trade.** A dynamically linked binary requires compatible libraries on the target machine — and "compatible" is where version conflicts, `GLIBC_2.34 not found`, and container images come from. **Static linking trades disk space for the guarantee that it will run.**

That is why Go defaults to static binaries, why Docker images exist largely to pin the dynamic dependencies, and why `musl` is popular for small static builds.

## 8. The dynamic loader

A dynamically linked executable contains this:

```
   [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
```

**The kernel does not start your program. It starts that.**

The dynamic loader maps the required shared libraries into the address space, resolves the remaining symbols, applies further relocations, and only then jumps to your entry point.

**Symbol resolution is usually lazy.** The first call to a library function goes through a stub in the **PLT** (Procedure Linkage Table), which asks the loader for the real address, records it in the **GOT** (Global Offset Table), and jumps there. Every later call reads the GOT directly.

**Why bother:** a program that links a large library but calls three functions from it resolves three symbols, not thousands. The cost is one extra indirection per call and a slightly slower first call.

**And this is why `LD_PRELOAD` works** — you can insert a library ahead of the normal search order and have your `malloc` found first, which is exactly what [[build-your-own-shit/11-your-own-memory-allocator|your own memory allocator]] relies on.

## 9. Worked example — runnable

**Runnable example:** save as `linker_lab.py` and run `python3 linker_lab.py`. Needs `gcc`, `nm` and `readelf`; it compiles into a temporary directory and cleans up after itself. Everything printed is a symbol name or a relocation type — no addresses — so your output should match.

```python
"""Watch a symbol go from UNDEFINED to resolved.

Compiles two C files, inspects the object files, links them, and inspects
the result. Everything printed is a symbol name or a binding type -- no
addresses or sizes, so the output is identical on any x86-64 Linux."""
import subprocess, tempfile, os, shutil, sys

MAIN_C = r'''
extern int add(int a, int b);
extern int shared_counter;
int main(void) {
    shared_counter = add(2, 3);
    return 0;
}
'''

LIB_C = r'''
int shared_counter;               /* definition lives HERE */
int add(int a, int b) { return a + b; }
static int helper(int x) { return x; }   /* static = not exported */
'''

def run(*cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if r.returncode != 0:
        raise SystemExit(f"{cmd[0]} failed:\n{r.stderr}")
    return r.stdout

def symbols(path, cwd):
    """nm output, reduced to (name, type-letter) for symbols we care about."""
    out = run("nm", path, cwd=cwd)
    interesting = {"add", "main", "shared_counter", "helper", "printf"}
    rows = []
    for line in out.splitlines():
        parts = line.split()
        name, kind = parts[-1], parts[-2] if len(parts) >= 2 else "?"
        if name in interesting:
            rows.append((name, kind))
    return sorted(rows)

MEANING = {
    "U": "UNDEFINED  - promised, not provided. The linker must find it.",
    "T": "TEXT       - a function, defined here, visible to other files",
    "t": "text       - defined here but STATIC: invisible outside this file",
    "B": "BSS        - a zero-initialised variable, defined here",
    "D": "DATA       - an initialised variable, defined here",
}

def show(title, rows):
    print(f"  {title}")
    for name, kind in rows:
        print(f"    {kind}  {name:16s} {MEANING.get(kind, '')}")

if __name__ == "__main__":
    for tool in ("gcc", "nm", "readelf"):
        if not shutil.which(tool):
            raise SystemExit(f"needs {tool} on PATH")
    d = tempfile.mkdtemp()
    open(os.path.join(d, "main.c"), "w").write(MAIN_C)
    open(os.path.join(d, "lib.c"), "w").write(LIB_C)

    print("TWO SOURCE FILES. main.c USES add() and shared_counter;")
    print("lib.c DEFINES them. Neither knows where the other will land.")
    print()

    run("gcc", "-c", "main.c", "-o", "main.o", cwd=d)
    run("gcc", "-c", "lib.c", "-o", "lib.o", cwd=d)
    print("STEP 1 -- COMPILE each file separately to an object file")
    show("main.o:", symbols("main.o", d))
    print()
    show("lib.o:", symbols("lib.o", d))
    print()
    print("  -> main.o has PROMISES (U). lib.o has the DEFINITIONS (T, B).")
    print("     Note 'helper' is lowercase t -- static, so the linker")
    print("     cannot see it from another file even though it exists.")
    print()

    print("STEP 2 -- RELOCATIONS: the holes the linker must fill")
    rel = run("readelf", "-r", "main.o", cwd=d)
    entries = []
    for line in rel.splitlines():
        parts = line.split()
        # rows look like: offset info TYPE symvalue NAME +/- addend
        if len(parts) >= 5 and parts[2].startswith("R_"):
            entries.append((parts[2], parts[4]))
    for reloc_type, name in entries:
        if name in ("add", "shared_counter"):
            print(f"    {reloc_type:16s} patch a reference to {name!r}")
    print("  -> the compiler left a blank where each address belongs and")
    print("     recorded 'patch this once you know where the symbol lives'.")
    print()

    print("STEP 3 -- LINK. Try main.o alone first:")
    r = subprocess.run(["gcc", "main.o", "-o", "broken"],
                       capture_output=True, text=True, cwd=d)
    fails = [l for l in r.stderr.splitlines() if "undefined" in l.lower()]
    print(f"    exit code {r.returncode} -- {len(fails)} undefined reference(s)")
    print("    this is the 'undefined reference to ...' error, and it means")
    print("    exactly what step 1 showed: a promise nobody kept.")
    print()

    run("gcc", "main.o", "lib.o", "-o", "program", cwd=d)
    print("STEP 4 -- LINK BOTH. Now the promises are matched to definitions:")
    show("program:", symbols("program", d))
    print()
    print("  -> 'add' and 'shared_counter' are no longer U. The linker")
    print("     found them in lib.o, chose final addresses, and patched")
    print("     every relocation.")
    print()

    rc = subprocess.run(["./program"], cwd=d, capture_output=True).returncode
    print(f"STEP 5 -- IT RUNS. exit code {rc}")
    print()

    print("STATIC vs DYNAMIC linking:")
    run("gcc", "main.o", "lib.o", "-o", "dyn", cwd=d)
    dyn = os.path.getsize(os.path.join(d, "dyn"))
    static_ok = subprocess.run(["gcc", "-static", "main.o", "lib.o", "-o", "sta"],
                               capture_output=True, text=True, cwd=d).returncode == 0
    print(f"    dynamically linked : {dyn:>9,} bytes")
    if static_ok:
        sta = os.path.getsize(os.path.join(d, "sta"))
        print(f"    statically linked  : {sta:>9,} bytes  (~{sta // dyn}x larger)")
    else:
        print("    statically linked  :  unavailable -- no static libc installed")
        print("      (install glibc-static / libc6-dev to try it; the point")
        print("       stands: a static build embeds a COPY of every library")
        print("       routine, a dynamic one stores only NAMES)")
    print()
    interp = run("readelf", "-l", "dyn", cwd=d)
    line = [l.strip() for l in interp.splitlines() if "interpreter" in l]
    if line:
        print(f"    {line[0]}")
        print("    ^ that is the DYNAMIC LOADER. The kernel starts IT, not")
        print("      your program -- it maps the libraries, then jumps to main.")

    assert any(k == "U" for _, k in symbols("main.o", d))
    assert any(n == "add" and k == "T" for n, k in symbols("lib.o", d))
    assert any(n == "helper" and k == "t" for n, k in symbols("lib.o", d))
    assert not any(n == "add" and k == "U" for n, k in symbols("program", d))
    shutil.rmtree(d)
    print()
    print("linker_lab: passed")
```

Expected output:

```
TWO SOURCE FILES. main.c USES add() and shared_counter;
lib.c DEFINES them. Neither knows where the other will land.

STEP 1 -- COMPILE each file separately to an object file
  main.o:
    U  add              UNDEFINED  - promised, not provided. The linker must find it.
    T  main             TEXT       - a function, defined here, visible to other files
    U  shared_counter   UNDEFINED  - promised, not provided. The linker must find it.

  lib.o:
    T  add              TEXT       - a function, defined here, visible to other files
    t  helper           text       - defined here but STATIC: invisible outside this file
    B  shared_counter   BSS        - a zero-initialised variable, defined here

  -> main.o has PROMISES (U). lib.o has the DEFINITIONS (T, B).
     Note 'helper' is lowercase t -- static, so the linker
     cannot see it from another file even though it exists.

STEP 2 -- RELOCATIONS: the holes the linker must fill
    R_X86_64_PLT32   patch a reference to 'add'
    R_X86_64_PC32    patch a reference to 'shared_counter'
  -> the compiler left a blank where each address belongs and
     recorded 'patch this once you know where the symbol lives'.

STEP 3 -- LINK. Try main.o alone first:
    exit code 1 -- 2 undefined reference(s)
    this is the 'undefined reference to ...' error, and it means
    exactly what step 1 showed: a promise nobody kept.

STEP 4 -- LINK BOTH. Now the promises are matched to definitions:
  program:
    T  add              TEXT       - a function, defined here, visible to other files
    t  helper           text       - defined here but STATIC: invisible outside this file
    T  main             TEXT       - a function, defined here, visible to other files
    B  shared_counter   BSS        - a zero-initialised variable, defined here

  -> 'add' and 'shared_counter' are no longer U. The linker
     found them in lib.o, chose final addresses, and patched
     every relocation.

STEP 5 -- IT RUNS. exit code 0

STATIC vs DYNAMIC linking:
    dynamically linked :    12,512 bytes
    statically linked  :  unavailable -- no static libc installed
      (install glibc-static / libc6-dev to try it; the point
       stands: a static build embeds a COPY of every library
       routine, a dynamic one stores only NAMES)

    [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
    ^ that is the DYNAMIC LOADER. The kernel starts IT, not
      your program -- it maps the libraries, then jumps to main.

linker_lab: passed
```

**Note step 3.** Linking `main.o` alone fails with exactly the `undefined reference` you have seen a hundred times — and step 1 already told you why: `add` and `shared_counter` were marked `U`. **The error message and the symbol table are the same fact, stated twice.**

---

## 10. Common pitfalls and traps

1. **Reading `undefined reference` as a compiler error.** It is a *linker* error — the code compiled fine. The distinction tells you where to look: a missing declaration is a compile error, a missing definition is a link error.
2. **Getting library order wrong.** With static libraries, `gcc main.o -lfoo` works and `gcc -lfoo main.o` may not — the linker processes left to right and only pulls in objects satisfying symbols it has *already* seen undefined.
3. **Assuming `static` means "one copy".** At file scope it means "not exported". Inside a function it means "persists between calls". Same keyword, unrelated meanings.
4. **Expecting `.bss` to occupy file space.** It records a size only. A file that seems too small for its globals is not corrupt.
5. **Shipping a dynamically linked binary and assuming it runs.** It needs compatible libraries. This is most of what container images exist to guarantee.
6. **Thinking `main` is the entry point.** `_start` is. `main` is called by the runtime.

## 11. Check your understanding

1. **Why can the compiler not resolve a call to a function in another file?**
   <details><summary>Answer</summary>
   Because the address depends on the final memory layout, which depends on <em>which other objects are linked and in what order</em> — information the compiler does not have when processing one file. It records a relocation instead, deferring the decision to the point where the layout is known.
   </details>

2. **You get `multiple definition of 'counter'`. What did you do, and what are two fixes?**
   <details><summary>Answer</summary>
   You defined the variable in a header that is included by more than one source file, so each translation unit has its own definition and the linker finds several.<br>
   <strong>Fix 1:</strong> declare it <code>extern</code> in the header and define it in exactly one <code>.c</code> file. <strong>Fix 2:</strong> mark it <code>static</code> if each file genuinely wants its own private copy — though then they are different variables, which may not be what you meant.
   </details>

3. **Why is a statically linked binary larger but more portable?**
   <details><summary>Answer</summary>
   It contains a <em>copy</em> of every library routine it uses rather than a name to resolve later, so nothing needs to be present on the target machine. The size is the cost of that self-containment.<br>
   The deeper trade is <strong>update policy</strong>: a security fix in a dynamically linked library takes effect for every program at once, while statically linked programs must each be relinked and redeployed.
   </details>

4. **What is the PLT/GOT indirection for, and what does it cost?**
   <details><summary>Answer</summary>
   It enables <strong>lazy symbol resolution</strong>: the first call to a library function goes through a PLT stub that asks the loader for the real address and caches it in the GOT; subsequent calls read the GOT directly.<br>
   The benefit is that a program linking a large library resolves only the handful of symbols it actually calls, rather than everything at startup. The cost is one extra indirection per call and a slower first call. It is also the mechanism <code>LD_PRELOAD</code> exploits, and — for the same reason — a target for attackers, which is why hardened builds use <code>RELRO</code> to make the GOT read-only after startup.
   </details>

## 12. Practice — independent task

**Task:** Build and inspect a shared library end to end.

- **(a)** Compile `lib.c` as position-independent code (`gcc -fPIC -c`) and link it into `libmine.so` (`gcc -shared`).
- **(b)** Link `main.o` against it. Run the program — it will probably fail to start. **Why?** Fix it with `LD_LIBRARY_PATH` or `-rpath`.
- **(c)** Compare `readelf -d` output for the dynamic and static builds. Which entries name the library?
- **(d)** Use `ldd` on your binary. What else got linked in that you never asked for?
- **(e)** Use `nm -D libmine.so` to list its *dynamic* symbols. How does that differ from plain `nm`?
- **(f)** Add `static` to `add()` in `lib.c`, rebuild, and observe the link failure. Connect it to the `t` versus `T` distinction from section 3.
- **(g)** Write a tiny `LD_PRELOAD` library that intercepts `add()` and returns a wrong answer. Run the original binary against it, unmodified.

**Done when:** your program runs against a shared library you built, and you have made `LD_PRELOAD` change its behaviour without recompiling it.

<details><summary>Hint for (b) and (g) — open only after an attempt</summary>
<strong>(b)</strong> The loader searches a fixed set of paths and the current directory is not one of them. <code>LD_LIBRARY_PATH=.</code> works for a test; <code>-Wl,-rpath,'$ORIGIN'</code> bakes the search path into the binary, which is what real applications do.<br><br>
<strong>(g)</strong> Compile a <code>.so</code> defining your own <code>add()</code>, then run <code>LD_PRELOAD=./evil.so ./program</code>. The loader resolves <code>add</code> to the first definition it finds, and your library is searched first. <strong>This is why <code>LD_PRELOAD</code> is ignored for setuid binaries</strong> — otherwise it would be a trivial privilege escalation.
</details>

## 13. Tradeoffs and limits

- **This covers ELF only.** macOS uses Mach-O and Windows uses PE/COFF. The concepts — symbols, sections, relocations, dynamic loading — are the same; the formats and tools differ (`otool`, `dumpbin`).
- **Link-time optimisation blurs the boundary.** With LTO the compiler defers code generation so the linker can optimise across translation units, which makes "compilation" and "linking" less cleanly separated than described here.
- **Symbol versioning is omitted.** glibc attaches versions to symbols so old binaries keep working, which is why you see `GLIBC_2.34` in error messages.
- **Nothing here covers relocatable kernels or position-independent executables in depth.** PIE is now the default on most distributions, which adds another layer of runtime relocation.

## Before moving on

- [ ] Explain why compilation and linking are separate, and what each step cannot know.
- [ ] Read `nm` output and distinguish promises from definitions.
- [ ] Explain what a relocation records and why PC-relative encodings need one.
- [ ] Explain static versus dynamic linking, and what the dynamic loader does at startup.

**Recap:** A compiler sees one file at a time, so it cannot know where anything will finally live — it emits definitions, records unresolved references as symbols, and leaves relocation entries describing the holes to patch. The linker merges sections, matches every undefined symbol to exactly one definition, assigns final addresses and applies the relocations. Static linking copies library code in; dynamic linking stores names and defers resolution to a loader that maps libraries at startup and resolves symbols lazily through the PLT and GOT.

**Next:** [[10-bytecode-and-virtual-machines|Bytecode and Virtual Machines]] — what happens when the target is not a real machine.

## Related

- [[08-code-generation|Code generation]] — where the object files come from
- [[foundations/os/09-syscalls-interrupts-and-the-abi|os/syscalls and the ABI]] — the calling convention the linker assumes
- [[foundations/how-computers-work/07-the-bridge|How Computers Work — the bridge]] — which flagged this as the missing link
- [[build-your-own-shit/11-your-own-memory-allocator|Your own memory allocator]] — uses `LD_PRELOAD`
- [[build-your-own-shit/18-your-own-compiler|Your own compiler]] — emits the assembly this links
