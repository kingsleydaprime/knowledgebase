# 🎯 Interview Prep — Index

**Thirteen domains have an `interview/` folder** — the ones below. The theory and engineering tracks added since (`engineering/`, `robotics/`, and the CS-theory spine from `discrete-math` through `programming-language-theory`) deliberately don't: those are `[reference]` material with no reps behind them, and **an interview bank for a subject you haven't practised would be memorisation, not preparation.** The place to start with those is [[project-ideas|project-ideas]], not a question list. Same format throughout, generalised from [[projects/arete/interview/01-backend-and-data|the arete interview notes]]: the **question**, what a **strong answer covers**, and the **detail worth adding** that separates memorised from understood. 🔥 marks questions that come up constantly.

## The banks

| Domain | Focus | Files |
|---|---|---|
| [[backend/interview/README\|Backend / Node]] | **built from a real interview** — p99 spikes, AZ vs deploy, retry storms, `Promise.all`, `Buffer` | 2 |
| [[foundations/networking/interview/README\|Networking]] | layering → TCP → TLS → debugging scenarios | 4 |
| [[languages/01-java/interview/README\|Java]] | **JVM, GC, memory model, concurrency** — the low-latency round | 3 |
| [[architecture/interview/README\|Architecture]] | the system design round + distributed systems depth | 2 |
| [[foundations/dsa/interview/README\|DSA]] | how to *run* a coding round + the pattern lookup | 1 |
| [[databases/interview/README\|Databases]] | indexes, isolation levels, query plans, migrations | 1 |
| [[foundations/os/interview/README\|OS]] | processes, virtual memory, syscalls, scheduling | 1 |
| [[devops/interview/README\|DevOps]] | Linux, containers, CI/CD, observability, incidents | 1 |
| [[concepts/interview/README\|Concepts]] | APIs, auth, OAuth, patterns, testing philosophy | 1 |
| [[cybersecurity/interview/README\|Security]] | injection classes, crypto, SSRF, defence, IR | 1 |
| [[ai-ml/interview/README\|AI/ML]] | RAG, agents, evals, prompt injection + ML fundamentals | 2 |
| [[frontend/interview/README\|Frontend]] | React model, rendering strategies, Web Vitals, compositor | 1 |
| [[hardware/interview/README\|Hardware]] | decoupling, I2C/SPI, interrupts, board bring-up + RF, MQTT, battery life | 2 |

Plus the project-specific bank: [[projects/arete/interview/01-backend-and-data|arete/interview/]] — the original, and still the best template because every answer is anchored in code you actually wrote.

## How to use these

**Cover the answer. Say it out loud. Then compare.** Recognition feels like knowledge and isn't — the gap between "I could follow that" and "I could say that" is exactly what an interview measures.

Two failure modes these banks are written against:
1. **Reciting definitions.** Every answer here has a "detail worth adding" precisely because the definition alone is table stakes.
2. **Not committing.** "It depends" is only good when followed by "so I'd choose X because Y." An interviewer can't distinguish thoughtful hedging from not knowing.

## If you're preparing for a specific role

**Low-latency / systems (the current target in [[PRIMETECHIE|the Primetechie path]]):**
[[languages/01-java/interview/02-jvm-and-concurrency|Java: JVM & concurrency]] → [[foundations/os/interview/01-processes-memory-and-io|OS]] → [[foundations/networking/interview/02-tcp-and-transport|TCP]] → [[foundations/dsa/interview/01-the-coding-round|coding round]] → [[architecture/interview/02-distributed-systems-depth|dist-sys depth]]

**Backend / platform (Node):**
[[backend/interview/01-production-debugging|production debugging]] ⭐ → [[backend/interview/02-node-runtime-and-api|Node runtime]] → [[concepts/interview/01-apis-auth-and-practices|APIs & auth]] → [[databases/interview/01-sql-modelling-and-internals|databases]] → [[architecture/interview/01-system-design-round|system design]] → [[devops/interview/01-linux-containers-and-operations|Linux & containers]]

⭐ Start there — it's reconstructed from a real interview, so it's the only file here that isn't a guess at what gets asked.

**AI engineering:**
[[ai-ml/interview/01-ai-engineering|AI engineering]] → [[ai-ml/interview/02-ml-and-stats-fundamentals|ML fundamentals]] → [[databases/interview/01-sql-modelling-and-internals|databases]] (vector search) → [[concepts/interview/01-apis-auth-and-practices|APIs]]

**Embedded / hardware:**
[[hardware/interview/01-electronics-and-embedded|Electronics & embedded]] → [[hardware/interview/02-rf-and-iot|RF & IoT]] → [[foundations/os/interview/01-processes-memory-and-io|OS]] (memory, interrupts) → [[foundations/networking/interview/02-tcp-and-transport|TCP]]
⭐ Lead with [[projects/iot-bridge-pcb/task|the IoT Bridge PCB]] — a board you designed beats any prepared answer.

## The five questions worth over-preparing

Across every bank, these carry the most weight per minute spent:

1. **"Walk me through a p99 latency investigation."** ([[languages/01-java/interview/02-jvm-and-concurrency|Java Q11]]) — the answer is a method, and it spans GC, locks, and the transport layer.
2. **"The service is down — what do you check?"** ([[foundations/networking/interview/04-debugging-and-scenarios|Networking Q1]]) — bisecting layers, the single most transferable skill in this vault.
3. **"Design X."** ([[architecture/interview/01-system-design-round|Architecture]]) — requirements *before* boxes, every time.
4. **"How would you evaluate this?"** ([[ai-ml/interview/01-ai-engineering|AI Q4]]) — separates engineers from demo-builders.
5. **"How do you safely migrate a huge table?"** ([[databases/interview/01-sql-modelling-and-internals|Databases Q10]]) — expand/migrate/contract; the fastest way to spot someone who's shipped.

## Related
- [[README|Vault README]] · [[PRIMETECHIE|The Primetechie Path]] · [[project-ideas|Project Ideas]]
- **The strongest answers cite your own code.** [[projects/README|projects/]] is the raw material — have one crisp story per project.
