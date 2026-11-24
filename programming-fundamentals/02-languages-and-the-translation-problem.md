---
id: 597e4b56-b27a-455c-b02b-024fdef3c682
---

# Languages and the Translation Problem

Every language sits between two extremes: the machine code the processor runs, and plain English, which no machine can execute. **"Level" is just where on that line a language sits.**

## Low level and high level
<!-- bite: 036d6922-d151-4e90-a9b5-70a1e6d3d918 -->

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

**"Faster" needs qualifying.** C is faster at runtime. Python is faster to write, and often faster to *get a correct answer with*. Most software is limited by network calls, disk, and developer time — none of which a language change fixes. Optimising the language before you've measured is a classic misuse of effort. See [[computer-architecture/12-performance|performance]].

## Compiled, interpreted, and the middle
<!-- bite: 073fee6e-03d6-4cbf-ae0e-79823cfc8b1e -->

**How** the translation happens, which is a separate axis from level.

**Compiled** — translated to machine code ahead of time. You ship the result; the translator isn't there at runtime.
→ Fast at runtime, errors caught before shipping, but you compile for each target platform. **C, C++, Rust, Go.**

**Interpreted** — a program reads your source and executes it as it goes.
→ Run it instantly, same code on any machine with the interpreter, but slower and many errors only appear when that line is reached. **Python, Ruby, JavaScript (originally).**

**Bytecode + VM** — the common middle. Compile to an intermediate form, then a virtual machine runs it, often compiling hot paths to machine code as it goes (**JIT**).
→ **Java, C#, and modern JavaScript engines.** You get portability and, after warm-up, much of compiled speed.

Two things worth knowing so the labels don't mislead you:

**The line is about implementations, not languages.** C can be interpreted; Python can be compiled. "Python is interpreted" describes what CPython does, not a law about the language.

**The real difference you'll feel is when you find out you're wrong.** Compiled: at build time, before anyone runs it. Interpreted: when execution reaches that line, possibly in production, possibly at 2 a.m. This is the substance behind arguments about type systems and it's a genuine trade — more upfront rigour against faster iteration. [[programming-language-theory/04-type-systems-formally|Type systems]] takes it much further.

## Static and dynamic types
<!-- bite: 00931562-d695-4386-b0fb-9d48d9dd1ead -->

The other axis you'll hit immediately.

**Statically typed** — every variable's type is known before running. Mismatches are caught at compile time. *Java, C, Go, Rust, TypeScript.*

**Dynamically typed** — types are attached to values at runtime. Anything can hold anything; mismatches surface when the operation happens. *Python, JavaScript, Ruby.*

```text
# dynamic — perfectly legal, and a bug waiting for the right input
x = 5
x = "hello"
```

Static typing costs you some verbosity and buys a class of error caught for free, plus much better editor assistance. Dynamic typing is quicker to write and lets a whole category of mistake reach runtime.

**The industry has been drifting toward "dynamic language, static types bolted on"** — TypeScript over JavaScript, type hints in Python — because it turns out most people want both, and the tooling caught up.

## Categories of language, by what they're for
<!-- bite: 0d8cb165-c771-452b-919b-d4fea55ebd4f -->

**General-purpose** — Python, Java, C#, Go, JavaScript, C++. Wide range; these should be your default.

**Systems** — C, C++, Rust, Zig. Where you need control over memory and timing: operating systems, databases, browsers, game engines. → [[languages/index|languages/]] has full courses on these.

**Scripting** — Python, Bash, Ruby, PowerShell. Automation, glue, one-off tasks. [[devops/01-linux/12-bash-scripting|Bash]] in particular is not optional if you'll touch servers.

**Markup and styling** — HTML, CSS. Worth being pedantic about: **these are not programming languages.** HTML describes structure, CSS describes appearance. Neither has logic in the sense of the rest of this course. They're essential and they're a different kind of thing.

**Query** — SQL. You describe *what you want*, not how to get it, and something else works out the plan. → [[databases/sql-reference|SQL reference]].

**Domain-specific** — HCL for [[devops/09-infrastructure-as-code/01-provisioning-and-terraform|Terraform]], YAML for CI config, regex for text patterns. You'll learn dozens of these incidentally and none of them deliberately.

## Choosing a first language
<!-- bite: 5a741245-f9a0-47a8-8e38-bba899a7d62f -->

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

## Check your understanding
<!-- bite: 4d13c313-1018-4cea-989b-b17855c378d2 -->

Try each one before you open the answer.

1. <!-- q: mcq id="6408c3a5" -->
   Which of these is a low-level language?

   - [ ] Python
   - [ ] JavaScript
   - [x] C
   - [ ] C#

   <details><summary>Answer</summary>

   C. You manage memory yourself and the code stays close to what the hardware does. Python, JavaScript and C# manage memory for you, which makes them high-level.

   </details>

2. <!-- q: mcq id="222a8c1d" -->
   A language compiles your code to an intermediate form, and a virtual machine runs it, compiling the busy parts to machine code as it goes. Which languages work this way?

   - [ ] C and Rust
   - [x] Java and C#
   - [ ] Bash and HTML
   - [ ] Assembly

   <details><summary>Answer</summary>

   Java and C# (and modern JavaScript engines). This is the bytecode-plus-VM middle, with a JIT compiling hot paths. C and Rust compile straight to machine code ahead of time.

   </details>

3. <!-- q: gap id="4e6a9992" answers="static|statically;dynamic|dynamically" -->
   In a ___ typed language, every variable's type is known before the program runs. In a ___ typed language, types belong to values and mistakes show up only when the operation happens.

   <details><summary>Answer</summary>

   Static, then dynamic. Java, Go and TypeScript are static; Python, JavaScript and Ruby are dynamic.

   </details>

4. <!-- q: mcq id="8c4596d7" -->
   Which of these is not a programming language, in the sense of having logic like conditions and loops?

   - [ ] SQL
   - [ ] Bash
   - [x] CSS
   - [ ] Go

   <details><summary>Answer</summary>

   CSS. It describes how a page looks, and HTML describes its structure. Neither has the logic the rest of the course is about. They are essential, but they are a different kind of thing.

   </details>

5. <!-- q: open id="3052d41c" -->
   Someone says "Python is interpreted, so it's slow; C is compiled, so it's fast." Give two ways this statement is misleading.

   <details><summary>Answer</summary>

   First, compiled versus interpreted describes an implementation, not the language. CPython interprets Python, but Python can be compiled and C can be interpreted.

   Second, "fast" needs qualifying. C runs faster, but Python is often faster to write and to get a correct answer with. Most software is held up by network calls, disk and developer time, and changing language fixes none of those. Measure before you blame the language.

   </details>

6. <!-- q: open id="16035fb2" -->
   A friend has spent three weeks comparing languages and still hasn't written a program. Why is the choice of first language lower-stakes than they think?

   <details><summary>Answer</summary>

   Almost everything you learn first carries over: variables, conditionals, loops, functions, collections and recursion exist in every mainstream language with different punctuation. The second language costs a fraction of the first. The real mistake is not picking, because comparing produces no programs. Pick one by what you want to build and finish something small in it.

   </details>

## Related
<!-- bite: 167b9a39-637b-4ba4-8802-bb5dfa311f22 -->
- [[programming-fundamentals/03-where-code-gets-written|where code gets written]] — the tools you'll need next
- [[languages/index|languages/]] — the vault's full courses: Java, Go, Rust, C, C++
- [[compilers/index|compilers]] — how translation actually works
- [[programming-language-theory/index|PL theory]] — why languages differ, much later
- [[programming-fundamentals/12-choosing-what-to-build-next|what to build next]] — where to take this

## About this lesson
<!-- bite: 11e1481b-06ee-41cd-88e0-90c2c610c426 -->

**Level:** Beginner. **Covers:** High level vs low level, compiled vs interpreted, and how to choose a first language without spending three weeks on the decision.

*Source: [reference] — from the freeCodeCamp Introduction to Programming course, extended with the static/dynamic and compilation-model distinctions it left implicit.*
