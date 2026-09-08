# Languages and the Translation Problem

> **[Beginner]** · High level vs low level, compiled vs interpreted, and how to choose a first language without spending three weeks on the decision.

Every language sits between two extremes: the machine code the processor runs, and plain English, which no machine can execute. **"Level" is just where on that line a language sits.**

## Low level and high level

**Low-level** languages stay close to the machine. You manage memory yourself, and the code mirrors what the hardware does. **Assembly** is the floor — one line per machine instruction. **C** is one step up: still explicit about memory, but readable and portable.

**High-level** languages hide the machine. Memory is managed for you, and one line can do a great deal. Python, JavaScript, Java, Go, C#.

The trade is consistent, and it's not a quality ranking:

| | **Low level** | **High level** |
|---|---|---|
| Control | Total | Limited, by design |
| Speed to write | Slow | Fast |
| Runtime performance | Maximum available | Usually enough |
| Ways to hurt yourself | Many, and quiet | Fewer, and loud |
| Good for | Kernels, drivers, embedded, engines | Nearly everything else |

**"Faster" needs qualifying.** C is faster at runtime. Python is faster to write, and often faster to *get a correct answer with*. Most software is limited by network calls, disk, and developer time — none of which a language change fixes. Optimising the language before you've measured is a classic misuse of effort. See [[foundations/computer-architecture/12-performance|performance]].

## Compiled, interpreted, and the middle

**How** the translation happens, which is a separate axis from level.

**Compiled** — translated to machine code ahead of time. You ship the result; the translator isn't there at runtime.
→ Fast at runtime, errors caught before shipping, but you compile for each target platform. **C, C++, Rust, Go.**

**Interpreted** — a program reads your source and executes it as it goes.
→ Run it instantly, same code on any machine with the interpreter, but slower and many errors only appear when that line is reached. **Python, Ruby, JavaScript (originally).**

**Bytecode + VM** — the common middle. Compile to an intermediate form, then a virtual machine runs it, often compiling hot paths to machine code as it goes (**JIT**).
→ **Java, C#, and modern JavaScript engines.** You get portability and, after warm-up, much of compiled speed.

Two things worth knowing so the labels don't mislead you:

**The line is about implementations, not languages.** C can be interpreted; Python can be compiled. "Python is interpreted" describes what CPython does, not a law about the language.

**The real difference you'll feel is when you find out you're wrong.** Compiled: at build time, before anyone runs it. Interpreted: when execution reaches that line, possibly in production, possibly at 2 a.m. This is the substance behind arguments about type systems and it's a genuine trade — more upfront rigour against faster iteration. [[foundations/programming-language-theory/04-type-systems-formally|Type systems]] takes it much further.

## Static and dynamic types

The other axis you'll hit immediately.

**Statically typed** — every variable's type is known before running. Mismatches are caught at compile time. *Java, C, Go, Rust, TypeScript.*

**Dynamically typed** — types are attached to values at runtime. Anything can hold anything; mismatches surface when the operation happens. *Python, JavaScript, Ruby.*

```
# dynamic — perfectly legal, and a bug waiting for the right input
x = 5
x = "hello"
```

Static typing costs you some verbosity and buys a class of error caught for free, plus much better editor assistance. Dynamic typing is quicker to write and lets a whole category of mistake reach runtime.

**The industry has been drifting toward "dynamic language, static types bolted on"** — TypeScript over JavaScript, type hints in Python — because it turns out most people want both, and the tooling caught up.

## Categories of language, by what they're for

**General-purpose** — Python, Java, C#, Go, JavaScript, C++. Wide range; these should be your default.

**Systems** — C, C++, Rust, Zig. Where you need control over memory and timing: operating systems, databases, browsers, game engines. → [[languages/README|languages/]] has full courses on these.

**Scripting** — Python, Bash, Ruby, PowerShell. Automation, glue, one-off tasks. [[devops/01-linux/12-bash-scripting|Bash]] in particular is not optional if you'll touch servers.

**Markup and styling** — HTML, CSS. Worth being pedantic about: **these are not programming languages.** HTML describes structure, CSS describes appearance. Neither has logic in the sense of the rest of this course. They're essential and they're a different kind of thing.

**Query** — SQL. You describe *what you want*, not how to get it, and something else works out the plan. → [[databases/sql-reference|SQL reference]].

**Domain-specific** — HCL for [[devops/07-infrastructure-as-code/01-provisioning-and-terraform|Terraform]], YAML for CI config, regex for text patterns. You'll learn dozens of these incidentally and none of them deliberately.

## Choosing a first language

**Almost everything in this course transfers.** Variables, conditionals, loops, functions, collections, recursion — every mainstream language has them, with different punctuation. The second language costs a fraction of the first. **This is the single most useful fact for the decision, because it means the decision is low-stakes.**

Pick by what you want to build:

| Goal | Start with |
|---|---|
| **Not sure yet / general** | **Python** — least syntax between you and the idea |
| Websites, front end | JavaScript (then TypeScript) — the browser runs nothing else |
| Data, ML, scripting | Python |
| Mobile | Swift (iOS), Kotlin (Android), or React Native |
| Big backends, enterprise | Java, C#, Go |
| Systems, embedded, performance | C first, then Rust or C++ |
| Servers and automation | Bash, alongside whatever else |

**The genuine mistake is not picking wrong — it's not picking.** Weeks spent comparing languages produce zero programs. Any of the above teaches you the concepts, and the concepts are the actual asset.

**Then finish something small in it before you evaluate.** Judging a language from tutorials tells you about tutorials.

## Related
- [[foundations/programming-fundamentals/03-where-code-gets-written|where code gets written]] — the tools you'll need next
- [[languages/README|languages/]] — the vault's full courses: Java, Go, Rust, C, C++
- [[foundations/compilers/README|compilers]] — how translation actually works
- [[foundations/programming-language-theory/README|PL theory]] — why languages differ, much later
- [[foundations/programming-fundamentals/12-choosing-what-to-build-next|what to build next]] — where to take this

*Source: [reference] — from the freeCodeCamp Introduction to Programming course, extended with the static/dynamic and compilation-model distinctions it left implicit.*
