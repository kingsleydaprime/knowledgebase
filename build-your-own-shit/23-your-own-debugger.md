# Build Your Own Debugger

> **[Advanced]** · `ptrace`, `INT3`, ELF and DWARF. **Set a breakpoint by source line, inspect a variable by name, and print a backtrace — from a program you wrote.**

## What you're building

**A source-level debugger for Linux x86-64.** Launch or attach to a process, set breakpoints by function or by `file:line`, step through source, read and write registers and memory, print a backtrace, and inspect local variables by name.

**And what you're deliberately not:** a user interface, a Windows port, reverse debugging, or support for optimised code. **You will debug programs compiled with `-g -O0`**, which is what you would do anyway.

**This guide sits on top of more of the vault than any other.** Processes and signals from `os/`, the ELF format from `compilers/09`, assembly from `computer-architecture/`, and process memory layout from `cybersecurity/11` — this is the project where all four stop being separate subjects.

## What you need first

- **Processes, `fork` and `exec`** → [[os/02-processes-and-threads|processes and threads]]
- **Signals**, because the entire mechanism is a `SIGTRAP` conversation → [[os/10-signals-and-ipc|signals and IPC]]
- **System calls and the ABI** → [[os/09-syscalls-interrupts-and-the-abi|syscalls and the ABI]]
- **The ELF format and how a binary is laid out** → [[compilers/09-linking-and-loading|linking and loading]]
- **x86-64 assembly**, enough to read a disassembly and know what `RIP` and `RSP` do → [[computer-architecture/04-assembly|assembly]]
- **Process memory layout** — the stack, the heap, and where a frame lives → [[cybersecurity/11-binary-exploitation/01-process-memory-and-why-it-breaks|process memory]]
- Helpful: having built [[build-your-own-shit/07-your-own-shell|your own shell]], since launching the target is the same `fork`/`exec` dance

**C or C++ is the natural choice**, with `libelfin` or `libdwarf` for the format parsing. **Rust** has `nix` for ptrace and `gimli` for DWARF, which is an excellent combination. **Python** with `python-ptrace` and `pyelftools` is the fastest way to get to the interesting parts, and this is one of the projects where that is the right call.

## The build order

**1. Launch a process under your control.**
`fork`, then in the child call `ptrace(PTRACE_TRACEME, 0, 0, 0)` followed by `execv`. The `exec` raises a `SIGTRAP` that stops the child before its first instruction, and your `waitpid` in the parent catches it.
*Works when:* your program prints "stopped at entry" and `PTRACE_CONT` lets the target run to completion.

**2. A command loop.**
`continue`, `quit`, and a prompt. Unglamorous, but everything else hangs off it. Add readline for history.
*Works when:* you can start a program, continue it, and see its exit status.

**3. Breakpoints — the trick at the centre of everything.**
Read the byte at the target address with `PTRACE_PEEKDATA`, **save it**, and write back `0xCC` — the one-byte `INT3` instruction. When execution reaches it the CPU traps and the kernel stops your child with `SIGTRAP`.

Two details that are not optional. First, `PTRACE_PEEKDATA` and `POKEDATA` work in **words**, so you must read the surrounding word, patch one byte, and write it back. Second, after the trap **`RIP` points one byte past the breakpoint** — rewind it before doing anything else.
*Works when:* the target stops at an address you chose, and reports it.

**4. Resuming from a breakpoint.**
You cannot simply continue — the `0xCC` is still there and you would trap forever. The dance is: restore the original byte, `PTRACE_SINGLESTEP` one instruction, re-insert `0xCC`, then continue.
*Works when:* a breakpoint inside a loop hits on every iteration. **Getting this right is the moment you have a debugger rather than a demo.**

**5. Registers and memory.**
`PTRACE_GETREGS` fills a `user_regs_struct` with every general-purpose register. Print them, write them, and read arbitrary memory — `process_vm_readv` or `/proc/<pid>/mem` are far more pleasant than word-at-a-time peeks.
*Works when:* you can dump registers at a breakpoint and the values match what `gdb` reports at the same point.

**6. ELF symbols, so you can name things.**
Parse the section headers, find `.symtab`, and you can turn `break main` into an address. Now breakpoints stop being hex.
*Works when:* `break main` works on a program compiled with `-g`.

**7. Deal with PIE, before it wastes your evening.**
Modern binaries are position-independent and the loader places them at a random base. **A symbol at `0x1139` in the file is at `base + 0x1139` in memory**, and the base is the first line of `/proc/<pid>/maps`. Every static address needs this offset added.
*Works when:* breakpoints work across repeated runs with address space layout randomisation left on. **If your breakpoints work under `setarch -R` and nowhere else, this is why.**

**8. DWARF line tables — from addresses to source.**
`.debug_line` holds a compressed state machine that maps addresses to `(file, line, column)`. Decode it and you get both directions: `break main.c:42`, and "stopped at main.c:42" when a breakpoint hits.
*Works when:* you can set a breakpoint on a line number and print the source line, with a few lines of context, when it is hit.

**9. Source-level stepping.**
Three commands, each built from breakpoints and single-stepping:

1. **Step in:** single-step until the line number changes.
2. **Step over:** if the next line involves a call, set a temporary breakpoint at the return address and continue.
3. **Step out:** set a temporary breakpoint at the current frame's return address and continue.

*Works when:* stepping through a recursive function behaves the way you expect it to, including at the return.

**10. A backtrace.**
Compile the target with `-fno-omit-frame-pointer` first and you can simply walk the saved `RBP` chain, mapping each return address to a function. **Then learn why that is a shortcut** — real unwinding uses the `.eh_frame` tables precisely because production code does not keep a frame pointer.
*Works when:* a backtrace from five frames deep names all five functions correctly.

**11. Variables by name.**
`.debug_info` is a tree of DIEs — debugging information entries — describing every function, variable and type. A local variable carries a **location expression**, usually `DW_OP_fbreg` with an offset from the frame base. Evaluate it, read that memory, and format the bytes according to the variable's DWARF type.
*Works when:* `print counter` at a breakpoint prints the same value `gdb` does.

**12. Optional: watchpoints.**
x86 has four hardware debug registers, `DR0`–`DR3`, that trap on *access* to an address rather than on execution. Four is the hardware limit, which is why every debugger's fifth watchpoint is suddenly catastrophically slow.

## The parts that will bite you

**Optimisation destroys the mapping.** At `-O2` your variable is in a register, or in three registers, or gone. DWARF describes this faithfully and the answer is genuinely "optimised out". **Debug at `-O0` and understand that the gap between source and execution is real**, not a tooling failure.

**The `waitpid` status word.** `WIFSTOPPED`, `WSTOPSIG`, `WIFEXITED` — and `PTRACE_GETSIGINFO` to distinguish a breakpoint trap from a single-step trap from a genuine `SIGTRAP` in the program. They arrive identically and mean different things.

**`PTRACE_PEEKDATA` returns `-1` both for errors and for the legitimate value `-1`.** Set `errno = 0` before the call and check it after. This is a documented wart and it will catch you once.

**Yama.** `/proc/sys/kernel/yama/ptrace_scope` set to `1` blocks attaching to a process that is not your child. Launching works; `attach` fails with `EPERM` and no explanation.

**One tracer per process.** If `gdb` has it, you cannot — which matters, because your instinct will be to run both at once.

**The stale-breakpoint bug.** Forget to re-insert `0xCC` after stepping over it and the breakpoint silently fires exactly once. The symptom appears several commands later.

## How to know it works

1. **`gdb` is the reference implementation and it is already installed.** Run both on the same binary at the same breakpoint and compare registers, source line and backtrace. **Nothing else in this folder gives you an oracle this good**
2. **`objdump -d` and `readelf --debug-dump=decodedline`** verify your parsing against the canonical tools, section by section
3. **A recursive test program** — breakpoints in recursion catch frame-handling bugs immediately
4. **A multi-file program**, so line lookup has to pick the right compilation unit
5. **A loop with a breakpoint inside it**, run a thousand iterations — this is the re-insertion test
6. **Attach to an already-running process**, not just one you launched

## Where to stop

**Stop once you can print a local variable by name and a correct backtrace.**

**Not worth it here:** multi-threaded targets (every thread is separately traced and the bookkeeping dominates), reverse debugging, JIT-compiled code, or a UI.

**You will have learned** what a debugger actually is — a process using one system call and a one-byte instruction — and along the way you will have *used* ELF and DWARF rather than read about them. **`-g` stops being a flag you copy and becomes a thing you can open.** It also makes [[cybersecurity/11-binary-exploitation/index|binary exploitation]] read very differently: the tooling those techniques defeat is tooling you have now written.

## Related

- [[compilers/09-linking-and-loading|Linking and loading]] — the ELF reference for this guide
- [[os/10-signals-and-ipc|Signals and IPC]] — the mechanism the whole thing rides on
- [[cybersecurity/11-binary-exploitation/01-process-memory-and-why-it-breaks|Process memory]] — the layout you will be reading
- [[build-your-own-shit/18-your-own-compiler|Your Own Compiler]] — the other end: emit the DWARF this consumes
- [[build-your-own-shit/index|Build Your Own Shit index]]

*Source: [reference] — build guide, Sep 2026.*
