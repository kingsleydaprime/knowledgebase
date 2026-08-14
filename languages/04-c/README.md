# C

A language from 1972 that is still underneath everything you use. Small enough to hold entirely in your head, close enough to the machine that reading it teaches you what the machine does, and unsafe enough that it has generated most of the security industry.

**~19,000 words across 13 notes.** Built August 2026, cross-referenced against [roadmap.sh C++](https://roadmap.sh/cpp) and the C standard.

**Source: `[reference]`.** No C project in this vault yet. The first one belongs in [[project-ideas|Project Ideas]] — and C is the language where the gap between reading and building is widest, because the failure modes are silent. [[PRIMETECHIE|Reading is not a rank.]]

> **The honest framing, having just done [[languages/03-rust/README|Rust]]:** C gives you no safety at all. No bounds checks, no ownership, no lifetimes, no null protection, no destructors, no strings, no collections. There is you, and there is what the machine does. That's why **~70% of serious vulnerabilities in large C/C++ codebases are memory-safety bugs** — not because C programmers are careless, but because the language provides no mechanism to be careful *with*.
>
> Learn C to understand the machine and to read the world's infrastructure. Reach for it on new projects only when you genuinely need it.

## Reading order

**The model**

1. [[languages/04-c/01-why-c-and-the-compilation-model|Why C, and the Compilation Model]] — **[Beginner]** — why it's still everywhere, the four-stage pipeline, and reading compiler vs linker errors
2. [[languages/04-c/02-headers-and-the-translation-unit|Headers and the Translation Unit]] — **[Beginner → Intermediate]** — **the note that makes C make sense.** Why `.h`/`.c` exists at all, declaration vs definition, include guards, `static`, and opaque types
3. [[languages/04-c/03-the-preprocessor|The Preprocessor]] — **[Beginner → Intermediate]** — text substitution that knows no C, the four macro traps, and conditional compilation

**The type system, such as it is**

4. [[languages/04-c/04-types-and-integers|Types and Integers]] — **[Beginner → Intermediate]** — sizes that aren't fixed, integer promotion, and the signed/unsigned comparison that has caused real CVEs
5. [[languages/04-c/05-pointers|Pointers]] — **[Beginner → Intermediate]** — addresses, arithmetic, `void *`, function pointers, and every way they go wrong
6. [[languages/04-c/06-arrays-strings-and-decay|Arrays, Strings and Decay]] — **[Beginner → Intermediate]** — the decay rule, why a function can't know an array's size, and strings as a convention rather than a type

**Managing memory yourself**

7. [[languages/04-c/07-memory-management|Memory Management]] — **[Intermediate]** — stack/heap/static, `malloc`/`free`, the full catalogue of failures, ownership discipline, and `goto cleanup`
8. [[languages/04-c/08-structs-unions-and-layout|Structs, Unions and Layout]] — **[Intermediate]** — padding and alignment, flexible array members, tagged unions built by hand, bitfields

**Using it**

9. [[languages/04-c/09-the-standard-library|The Standard Library]] — **[Intermediate]** — how little there is, and which parts are traps
10. [[languages/04-c/10-undefined-behaviour|Undefined Behaviour]] — **[Intermediate → Advanced]** — not "unpredictable output" but a licence for the compiler to assume your code can't do what it does. **Read this one properly**
11. [[languages/04-c/11-modular-c-and-project-structure|Modular C and Project Structure]] — **[Intermediate]** — the conventions that substitute for language features

**Tooling**

12. [[languages/04-c/12-build-systems|Build Systems]] — **[Intermediate]** — `make` from first principles, CMake, and the honest state of C dependency management
13. [[languages/04-c/13-debugging-and-tooling|Debugging and Tooling]] — **[Intermediate → Advanced]** — sanitizers, Valgrind, `gdb`, perf, fuzzing. **In a language with no safety net, the tooling is the safety net**

## The two notes that matter most

If you read nothing else:

- **[[languages/04-c/02-headers-and-the-translation-unit|02 — Headers and the Translation Unit]]**, because the compiler sees one `.c` file and nothing else, and every convention in C follows from that. It also makes C++, FFI boundaries, and half of every build error comprehensible.
- **[[languages/04-c/10-undefined-behaviour|10 — Undefined Behaviour]]**, because the common mental model is wrong. UB isn't a runtime accident; it's a property of the program that lets the optimiser delete your null checks. It explains "worked at `-O0`, broke at `-O2`" permanently.

## Where the frameworks are

Per [[languages/README|the vault rule]]:

### → **[[backend/frameworks/c/README|backend/frameworks/c/]]** — libmicrohttpd, Kore, Ulfius, civetweb

Including the honest question of when a C web server is a real answer and when it's a bad idea.

## C, Rust and Go side by side

All three are now in the vault, and the comparison is the fastest way to see what each is for:

| | C | [[languages/02-go/README\|Go]] | [[languages/03-rust/README\|Rust]] |
|---|---|---|---|
| Memory | manual `malloc`/`free` | GC | compile-time ownership |
| Safety | none | memory-safe, races possible | memory-safe, races impossible |
| Learning curve | small language, endless pitfalls | days | weeks to months |
| Compile speed | very fast | very fast | slow |
| Runtime | none | GC + scheduler | none |
| Dependencies | no package manager | modules | cargo |
| Best for | kernels, embedded, ABI boundaries | services, infra tooling | systems where safety must be proven |

C's remaining unassailable niches: **the ABI everything speaks**, targets with no other toolchain, and the tens of millions of existing lines.

## Known gaps

- **No project.** The largest gap
- **Concurrency** — pthreads, C11 `<threads.h>`, atomics and the memory model get a mention and no note. It's a real omission; the material lives partly in [[foundations/os/fundamentals|OS Fundamentals]]
- **Signals** — `signal`/`sigaction` and async-signal-safety
- **Embedded C specifically** — freestanding implementations, linker scripts, `volatile` for registers. Adjacent to [[hardware/README|hardware/]]
- **C23** — mentioned, not covered in depth

---

## Related
- [[languages/03-rust/README|Rust]] — the language built to replace this one
- [[languages/README|Languages]] — the language/framework split rule
- [[foundations/os/README|Operating Systems]] — written in C, all of them
- [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|Exploits]] — where C's failure modes lead
- [[BUILD-PLAN|Build Plan]] — C++ is next
