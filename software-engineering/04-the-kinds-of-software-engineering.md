---
id: 635e16b3-a543-4b5d-af6a-f8cfaf41d71d
---

# The Kinds of Software Engineering

[[software-engineering/03-the-engineering-roles|The roles note]] listed eleven roles from a **product** perspective — frontend, backend, data, ML. This note cuts the field a different way: **by the constraint the software runs under**, which is what actually makes the disciplines different.

**Most people meet only web and mobile**, because that's where the volume of jobs is. It's a small part of the software that exists.

## The tree
<!-- bite: c51197c8-ff63-4908-9610-e4e2ecaecbd8 -->

| Branch | Defining constraint | Typical languages |
|---|---|---|
| **Web / cloud** | Change is cheap; scale and latency | TS, Python, Go, Java |
| **Mobile** | Battery, offline, app-store cycles | Swift, Kotlin, Dart |
| **Embedded** | **Memory, power, no OS or a small one** | **C, C++, Rust** |
| **Real-time / safety-critical** | **Deadlines are correctness** | C, Ada, Rust |
| **Systems** | Performance, resource control | C, C++, Rust, Zig |
| **Games** | **16 ms, every frame** | C++, C# |
| **Scientific / HPC** | Numerical accuracy, throughput | Fortran, C++, Python, CUDA |
| **Data / ML** | Data volume, statistical correctness | Python, SQL, Scala |
| **Desktop** | Platform integration, distribution | C++, C#, Swift, Rust, TS |
| **Firmware / drivers** | Hardware you can't change | C, assembly |
| **Security** | An adversary | C, Python, Rust |

**The constraint column is the useful one.** Two jobs with the same title in different branches share a language and almost nothing else.

## Embedded software engineering
<!-- bite: 9a5a15c3-1771-4718-ad07-9266fdfa190d -->

**Since this is the one you named**, it gets the detail.

Embedded is software running on hardware that isn't a general-purpose computer: a washing machine, a car's ECU, a pacemaker, a drone flight controller, a smart meter, an insulin pump. **There are vastly more embedded processors in the world than there are PCs and phones combined.**

**What makes it different:**

**Resources are genuinely scarce.** Not "we should optimise" scarce — a microcontroller might have **32 KB of RAM and 256 KB of flash**. There is often **no heap at all**: dynamic allocation is banned outright in many safety-critical codebases, because `malloc` can fail and fragmentation is unbounded → [[os/05-memory-allocation|memory allocation]].

**Often no operating system.** "Bare metal" means your code *is* the whole software. You write the loop, you handle the interrupts, you initialise the hardware. Or you run an RTOS (FreeRTOS, Zephyr) — a scheduler and not much else.

**You talk to hardware directly.** Writing a value to a specific memory address flips a physical pin. Peripherals are configured by setting bits in registers described in a 900-page datasheet → [[hardware/03-embedded-systems|embedded systems]].

**Debugging is different.** There's often no console. You use a JTAG/SWD debugger, a logic analyser, an oscilloscope, or you toggle an LED. **A bug may be electrical rather than logical** — a floating pin, noise on a line, a brown-out on power draw. Software people entering embedded consistently underestimate this.

**The feedback loop is slow.** Compile, flash, test on hardware. Seconds to minutes, not milliseconds — and that changes how you work: you think more before running, because running is expensive → [[programming-fundamentals/11-planning-before-you-type|planning]].

**Concurrency is interrupts, not threads.** An interrupt can fire between any two instructions. Shared state between an ISR and main code needs `volatile`, atomics, or disabled interrupts — and getting it wrong produces bugs that appear once a week → [[os/10-signals-and-ipc|signals]].

**What you need:** C, properly — pointers, memory layout, undefined behaviour → [[languages/04-c/index|C]]. Then datasheets, the common protocols (I2C, SPI, UART, CAN) → [[hardware/05-communication-protocols|communication protocols]], interrupts and timers, and enough electronics to read a schematic and not damage the board → [[hardware/01-electricity|electricity]].

**Rust is a genuine and growing option here** — `no_std` embedded Rust gives memory safety without a runtime, which is exactly the pitch for a field where memory bugs are expensive and unreachable → [[languages/03-rust/index|Rust]].

**You already have an unusual amount of this.** [[hardware/index|hardware/]] is 10 notes plus a **fabricated PCB**, and projects/ has the IoT bridge. **That combination — real firmware plus a board you designed — is rare among software engineers** and is the single strongest thing you own for entering this field.

## Real-time and safety-critical
<!-- bite: ea25df8d-1fb3-4ad3-bcb5-49c49e4b9dbc -->

Frequently confused with embedded; **not the same thing.**

**Real-time means a late answer is a wrong answer.** Not "slow" — *incorrect*.

- **Hard real-time** — missing a deadline is a system failure. Airbag deployment, engine timing, flight control
- **Soft real-time** — missing it degrades quality. Video playback, audio

**The consequence people find counterintuitive: you optimise for predictability, not speed.** A function that always takes 1 ms is better than one averaging 0.1 ms with an occasional 5 ms spike. That's why hard real-time systems avoid garbage collection, dynamic allocation, and unbounded loops — and why **worst-case execution time** analysis is a discipline in itself.

**Safety-critical** adds regulation: DO-178C (avionics), ISO 26262 (automotive), IEC 62304 (medical). Certification means traceability from requirement to test for every line, restricted language subsets (MISRA C), mandated static analysis, and independent review. **Slow, expensive, and appropriate** → [[systems-engineering/08-risk-and-failure-analysis|risk and failure analysis]].

## The others, briefly
<!-- bite: 865aaaf3-cc48-4f41-8625-c547000e79fc -->

**Systems** — operating systems, databases, compilers, browsers, runtimes. Performance in microseconds; correctness under concurrency. → [[os/index|OS]] · [[compilers/index|compilers]] · [[databases/index|databases]]

**Games** — [[game-development/index|its own folder]].

**Scientific / HPC** — simulation, modelling, numerical methods at scale. Fortran is genuinely alive here. Correctness means *numerical* correctness → [[mathematics/07-applied-and-computational/01-numerical-methods/index|numerical methods]] · [[gpu-and-parallel-computing/index|GPU]].

**Desktop** — [[desktop/index|its own folder]].

**Firmware and drivers** — the layer between the OS and the hardware. Deep hardware knowledge, and bugs crash the machine.

## How hard is it to switch?
<!-- bite: fd6c3d64-4621-418a-9072-24088425d842 -->

**The honest version, because this determines what to do first.**

**Easy to move between:** web ↔ mobile ↔ data ↔ ML ↔ devops. Shared assumptions — plenty of memory, an OS, cheap iteration, high-level languages. **These are the interchangeable ones**, and most careers move freely among them.

**Harder, one-way-ish:** web → embedded, systems, games. The gap is real: C and memory, hardware, and a different attitude to iteration.

**Easier in reverse.** Embedded and systems engineers move into web comfortably; the reverse takes deliberate effort. **The general rule: it is easier to move up the abstraction stack than down**, because down requires knowledge that higher layers exist specifically to hide.

**The practical consequence for you:** the constrained disciplines are worth *touching* early even if you don't commit — not because you must choose now, but because the direction of travel is asymmetric. Firmware on a board you designed is exactly that touch, and you have it.

## The realistic advice
<!-- bite: ad5eb8e1-d7fd-4c22-b3d6-2364a38f06ec -->

**Don't pick a branch yet.** Depth in one thing plus literacy in the neighbours beats a shallow tour, and the fundamentals — [[dsa/index|data structures]], [[networking/index|networking]], [[os/index|OS]], [[git/index|version control]], debugging — are the same in every branch and are what actually transfers.

**Earn in the branch with the most jobs; explore the others deliberately.** Web and cloud fund the exploration. Embedded, games and systems are smaller markets with fewer, more specialised roles.

**And notice what you already have:** hardware and firmware experience *plus* modern software practice is a genuinely uncommon combination. Robotics, IoT, drones, medical devices and automotive all want exactly that pairing, and most candidates have one half → [[hardware/index|hardware]] · [[robotics/index|robotics]].

## Check your understanding
<!-- bite: 74976558-e577-4c5f-bb73-10a1595f0bf5 -->

Try each one before you open the answer.

1. <!-- q: mcq id="275ce2c9" -->
   A team writes the code for a car's airbag controller. Which branch's defining constraint matters most?

   - [ ] Web: change is cheap
   - [x] Real-time: a late answer is a wrong answer
   - [ ] Data: statistical correctness
   - [ ] Desktop: platform integration

   <details><summary>Answer</summary>

   Hard real-time. Missing the deadline is a system failure, so the code is built for predictable timing above all.

   </details>

2. <!-- q: mcq id="39f2ccb4" -->
   In a hard real-time system, which function is better?

   - [x] One that always takes 1 ms
   - [ ] One that averages 0.1 ms but occasionally takes 5 ms
   - [ ] They're equally good
   - [ ] Whichever uses less memory

   <details><summary>Answer</summary>

   The steady 1 ms one. Real-time work optimises for predictability, not speed, which is why it avoids garbage collection, dynamic allocation and unbounded loops, and analyses worst-case execution time.

   </details>

3. <!-- q: open id="492a1ff4" -->
   Many safety-critical embedded codebases ban `malloc` outright. Why?

   <details><summary>Answer</summary>

   The device has very little memory (perhaps 32 KB of RAM), `malloc` can fail at runtime, and fragmentation is unbounded, so you can't prove the program will always have memory. Allocating everything statically up front makes the memory use known and checkable.

   </details>

4. <!-- q: open id="17775214" -->
   A web developer's first embedded bug turns out to be a floating input pin, not a code mistake. What does this say about debugging in embedded work?

   <details><summary>Answer</summary>

   Bugs can be electrical as well as logical: a floating pin, noise on a line, a brown-out when power draw spikes. There's often no console, so you debug with a JTAG/SWD debugger, a logic analyser, an oscilloscope or a blinking LED, and you need enough electronics to read a schematic.

   </details>

5. <!-- q: mcq id="3e447967" -->
   Which career move is usually harder?

   - [ ] Embedded engineer moving into web development
   - [x] Web developer moving into embedded or systems work
   - [ ] Mobile developer moving into web
   - [ ] Data engineer moving into ML

   <details><summary>Answer</summary>

   Web to embedded. It's easier to move up the abstraction stack than down, because going down needs exactly the knowledge the higher layers exist to hide: C and memory, hardware, and a slower way of iterating.

   </details>

6. <!-- q: gap id="5a5cf6fe" answers="interrupts|interrupt;volatile|atomics" -->
   On a bare-metal microcontroller, concurrency usually comes from ___ rather than threads, and state shared with main code needs ___, atomics or disabled interrupts.

   <details><summary>Answer</summary>

   Interrupts, then `volatile` (or atomics). An interrupt can fire between any two instructions, and getting the sharing wrong gives bugs that show up once a week.

   </details>

## Related
<!-- bite: d63af190-7d6b-4758-a3ee-b32e2eb20cc2 -->
- [[software-engineering/03-the-engineering-roles|the engineering roles]] — the same field cut by product area
- [[hardware/index|hardware]] — embedded, hands-on, with a real board
- [[game-development/index|game development]] · [[desktop/index|desktop]]
- [[systems-engineering/index|systems engineering]] — the discipline that coordinates several of these at once
- [[PRIMETECHIE|the Primetechie path]] — an order to explore in

## About this lesson
<!-- bite: 170ef867-831b-4307-be8b-19d2f80c3b00 -->

**Level:** Beginner. **Covers:** Web is one branch of a much larger tree. What each specialisation actually does, what constraint defines it, and which are hard to switch into later.

*Source: [reference] — written Aug 2026 to answer "what other kinds of software engineering are there?", which the roles note didn't cover.*
