# Project Ideas — turning notes into ability

The notes in this vault are a **map**. This file is the **territory** — the projects that turn "I read about it" into "I built it and can prove it." Reading is not reps; building is.

## How to use this

- **Pick one and finish it.** One shipped project beats five half-started ones. Finishing — deployed, tested, written up — is the skill.
- **Extend your real projects where you can.** Adding CI/CD or JMH benchmarks to an app you already built ([[projects/record-id-generator-java/learning/01-java-fundamentals|record-id-generator]], [[projects/direct-debit-sandbox-java/learning/01-java-fundamentals|direct-debit-sandbox]], arete, gees-arise, nextvibe) is higher-signal than a toy, and faster to start.
- **Write it up.** A short README with the *why* and what you learned turns a project into portfolio signal. A repo no one can understand isn't signal.

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade.

**If you only do five** (highest signal for where you're aiming): the ⭐ projects below — the order-book matching engine (Java/systems), a RAG app over *this vault* (AI eng), an end-to-end MLOps project (ML eng), a full A/B-test analysis (data sci), and putting one app through a real CI/CD + container deploy (DevOps).

**The other columns.** Those five are aimed at the low-latency/software target. [[PRIMETECHIE|The path]] is four columns wide, and the reps below cover all of them — 🔐 security (secure your own app, then a SIEM detection you tested by attacking your own lab) and 🔌 hardware (rev 2 of the IoT Bridge). Hardware is the one column where you already have more built than written, so it needs the *fewest* new projects and gives the fastest returns.

---

## Java / JVM & Systems
*The low-latency / systems signal — what a firm doing market-data / FPGA work actually screens for. This is where you have the most to prove and the most upside.*

- 🟢 **Solve the concurrency exercises** — the [[languages/01-java/02-jvm-and-concurrency/exercises/README|bounded blocking queue and token-bucket rate limiter]] already have a red→green test harness. Do both — once with `synchronized`, once lock-free with `ReentrantLock`/atomics. Exercises: [[languages/01-java/02-jvm-and-concurrency/02-concurrency|concurrency]].
- 🟡 **Lock-free ring buffer (SPSC/MPSC queue)** — a bounded ring buffer using `AtomicLong` cursors and CAS, no locks. Benchmark it against `ArrayBlockingQueue`. The canonical low-latency data structure (the LMAX Disruptor's core). Exercises: [[languages/01-java/02-jvm-and-concurrency/02-concurrency|atomics/CAS]], [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|memory model]].
- 🔴 ⭐ **In-memory order book + matching engine** — a limit-order book (price levels, bid/ask, add/cancel/match) with a matching engine, single-threaded on the hot path for determinism. Feed it a synthetic order stream, measure throughput and p99 latency. *This is the single most on-target project for a trading firm* — it's literally the domain.
- 🟡 **Market-data feed parser** — parse a binary/CSV market-data feed (or a simplified FIX/ITCH-style format) at high throughput, zero-allocation on the hot path. Ties [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|batch/streaming]] to [[languages/01-java/01-language/01-fundamentals|the language]].
- 🟡 **JMH benchmark + GC tuning study** on your record-generator pipeline — add [[languages/01-java/03-tooling/04-testing|JMH]] microbenchmarks, then run it under different collectors (Parallel vs G1 vs ZGC), capture GC logs / a JFR recording, and write up the latency-vs-throughput tradeoff. Exercises: [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM internals]] — GC/JIT in practice, the exact thing the notes say only *doing* teaches.
- 🟢 **Add a real test suite** to one of your Java projects — JUnit + Mockito + a Testcontainers integration test against real MySQL/RabbitMQ. The projects shipped without tests; fixing that is direct engineering-maturity signal. Exercises: [[languages/01-java/03-tooling/04-testing|testing]].

---

## ⭐ Build-Your-Own — systems mastery
*The deepest reps in the vault. Each one turns a whole topic from words into bone-deep understanding.*

> **These now have full build guides in [[build-your-own-shit/README|build-your-own-shit/]]** — numbered milestones, each independently testable, with per-language toolkits and a "where to stop". Read the guide rather than this list; the entries below are the one-line pitch and the difficulty rating.

| | Guide | Why |
|---|---|---|
| 🟠 | [[build-your-own-shit/01-http-server\|HTTP server]] | **Start here.** A weekend; a real browser is the test |
| 🟠 | [[build-your-own-shit/07-your-own-shell\|Shell]] | The smallest one that teaches the most — `fork`/`exec`, fds, pipes |
| 🟠 | [[build-your-own-shit/08-your-own-container\|Container]] | ~200 lines, one evening, and Docker stops being magical |
| 🔴 | [[build-your-own-shit/02-your-own-git\|Git]] | Real Git reads your repository. Permanently demystifies it |
| 🔴 ⭐ | [[build-your-own-shit/03-your-own-redis\|Redis]] | Data structures + networking + durability. The real `redis-cli` connects |
| 🔴 | [[build-your-own-shit/04-your-own-language\|Language / interpreter]] | The deepest single lesson. → [[foundations/compilers/README\|compilers]] is the course behind it |
| 🔴 | [[build-your-own-shit/06-your-own-database\|Database]] | B-tree, SQL subset, WAL. `kill -9` mid-write and the data survives |
| 🔴 | [[build-your-own-shit/05-your-own-os\|Operating system]] | Weeks, not a weekend. Boots from a USB stick → [[foundations/os/README\|os]] |

**Not yet a guide, and the best distributed-systems project there is:**

- 🔴 ⭐ **A Raft key-value store** — [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] made real: leader election, log replication, safety, then a replicated KV store on top, tested against crashes and partitions. It forces you to confront every edge case the [[architecture/04-distributed-systems/README|theory]] describes. (MIT 6.824 labs are the gold standard.)

Pair each with a short write-up of what you learned; these are portfolio-grade signal on their own.

## DevOps
*Mostly reference in the notes — this is the section where doing matters most, because you haven't run k8s/Terraform/Prometheus yet.*

- 🟢 ⭐ **Containerize + deploy one of your apps end to end** — multi-stage [[devops/02-docker/README|Dockerfile]], docker-compose for local, then deploy to a [[devops/04-vps/vps-setup|VPS]] behind [[devops/08-networking-and-web/02-web-servers-and-proxies|Nginx]] with Let's Encrypt TLS. The practical capstone.
- 🟡 **A real CI/CD pipeline** — extend beyond this vault's deploy workflow: a [[devops/06-ci-cd/README|GitHub Actions]] pipeline for one of your apps that runs typecheck/lint/tests on PRs and deploys on merge, with a build-once-promote-artifact flow.
- 🟡 **Local Kubernetes deploy** — stand up a `kind`/`minikube` cluster, write the [[devops/05-orchestration/01-kubernetes|Deployment/Service/Ingress]] manifests, deploy a containerized app with health probes, and do a rolling update + rollback. Makes the biggest reference gap concrete.
- 🟡 **Terraform a small cloud setup** — provision a VM + network + managed DB on a throwaway cloud account with [[devops/07-infrastructure-as-code/01-provisioning-and-terraform|Terraform]], read the `plan`, `apply`, then `destroy`. Learn state the safe way.
- 🔴 **Observability stack** — instrument an app with metrics, run [[devops/10-observability/README|Prometheus + Grafana]] (+ Loki for logs), build a dashboard and an alert on an SLO. The "you can't operate what you can't see" lesson, hands-on.
- 🟢 **Secrets, done right** — take an app with a committed `.env` and move it to [[devops/09-secret-management/01-secret-management|SOPS or Vault]]; wire it into the deploy.

---

## AI Engineer
*Your strongest applied area (AI SDK / MCP). These produce shippable, demoable products — high portfolio value.*

- 🟢 ⭐ **RAG over this vault** — a chatbot that answers questions about *this knowledgebase*: chunk the markdown, embed it, store in [[ai-ml/03-ai-engineer/06-rag-and-embeddings|pgvector/Chroma]], retrieve + answer with citations. Dogfoods your own notes and is a perfect [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]] project.
- 🟡 **Build an MCP server** — wrap a real system (your notes, a database, an API) as an [[ai-ml/03-ai-engineer/07-tools-and-mcp|MCP server]] with tools + resources, and use it from an MCP host. You already *use* MCP — building one closes the loop.
- 🟡 **An agent with real tools + an eval set** — an [[ai-ml/03-ai-engineer/08-agents|agent]] (via the AI SDK's agent loop) that does a multi-step task with 2–3 tools, plus an [[ai-ml/03-ai-engineer/10-safety-and-production|eval set]] measuring success rate as you change the prompt/model. The evals are what make it engineering, not a demo.
- 🟡 **Structured extraction pipeline** — feed scanned docs/receipts to a [[ai-ml/03-ai-engineer/09-multimodal|vision model]], extract typed JSON with [[ai-ml/03-ai-engineer/04-calling-models|structured output]], validate against a schema. A genuinely useful, sellable tool.
- 🟢 **Model bake-off via OpenRouter** — same prompt/eval set across 5 models through [[ai-ml/03-ai-engineer/03-the-model-landscape|OpenRouter]], compare quality/latency/cost. Cheap, fast, and teaches model selection.
- 🔴 **Prompt-injection red-team** — build a small agent, then try to break it (direct + indirect [[ai-ml/03-ai-engineer/10-safety-and-production|injection]]); document what worked and the mitigations. Rare, valuable security-adjacent signal.

---

## ML Engineer
*The modeling half — needs a dataset and patience. Kaggle is the fastest source of real data.*

- 🟢 **Tabular ML done right** — take a Kaggle tabular dataset, do [[ai-ml/01-data-scientist/04-exploratory-data-analysis|EDA]], train [[ai-ml/02-ml-engineer/03-classical-ml/02-trees-and-ensembles|gradient boosting]] vs [[ai-ml/02-ml-engineer/03-classical-ml/01-regression|logistic regression]], with proper [[ai-ml/02-ml-engineer/04-model-evaluation/03-validation-and-tuning|cross-validation + tuning]]. Prove the boosting-beats-deep-learning-on-tabular point yourself.
- 🟢 **Implement it from scratch in NumPy** — write linear regression (gradient descent) and k-means using *only* [[ai-ml/00-foundations/04-python-and-data-tools/02-numpy|NumPy]], no scikit-learn. The fastest way to make [[ai-ml/00-foundations/03-mathematics/README|the math]] and vectorization click.
- 🟡 **Image classifier with transfer learning** — fine-tune a pretrained CNN ([[ai-ml/02-ml-engineer/06-computer-vision/03-transfer-learning|transfer learning]]) on a custom image set. Small, satisfying, and teaches the [[ai-ml/02-ml-engineer/05-deep-learning/02-training-loop-in-pytorch|PyTorch loop]].
- 🟡 **Fine-tune a small open model** — LoRA-fine-tune a small model from [[ai-ml/03-ai-engineer/03-the-model-landscape|Hugging Face]] on a narrow task, and honestly compare it to just prompting a bigger model (the [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG vs fine-tuning]] decision, tested).
- 🔴 ⭐ **End-to-end MLOps project** — train a model, track experiments with [[ai-ml/02-ml-engineer/10-mlops/02-experiment-tracking-and-pipelines|MLflow]], [[ai-ml/02-ml-engineer/10-mlops/04-serving-and-monitoring|serve it]] behind a FastAPI endpoint in a container, and add [[ai-ml/02-ml-engineer/10-mlops/03-monitoring-and-edge|drift monitoring]]. This is the whole *engineer* half of ML engineering, and it reuses your DevOps skills.

---

## Data Scientist
*The analysis/inference half — the deliverable is a trustworthy answer, well communicated.*

- 🟢 **A real EDA + statistical report** — take a dataset you care about, do a full [[ai-ml/01-data-scientist/04-exploratory-data-analysis|EDA]], compute [[ai-ml/01-data-scientist/02-descriptive-statistics|descriptive stats]], and write up findings with honest [[ai-ml/01-data-scientist/05-data-visualization|visualizations]]. Practice the "numbers + a picture + a takeaway" discipline.
- 🟡 ⭐ **A/B test analysis, done rigorously** — take (or simulate) experiment data and analyze it properly: [[ai-ml/01-data-scientist/03-inferential-statistics|hypothesis test]], effect size *and* confidence interval, check for the [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|pitfalls]] (SRM, peeking, Simpson's paradox). The core data-scientist skill.
- 🟡 **Causal case study** — pick a question where correlation ≠ causation and attempt a [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|difference-in-differences or regression-discontinuity]] analysis, stating your assumptions honestly. Rare, high-value reasoning.
- 🟢 **Power analysis calculator** — a small tool that computes required sample size for an A/B test given a minimum detectable effect. Cements [[ai-ml/01-data-scientist/03-inferential-statistics|power/significance]].
- 🟡 **A stakeholder dashboard** — turn an analysis into a clean, honest dashboard (a BI tool or a notebook), tuned for a decision-maker, not a data person. Communication reps.

---

## Cybersecurity
*Notes went deep on offense + the defensive/SOC half — but security is learned by doing, safely and legally, on systems you own or are authorized to test.*

- 🟢 ⭐ **Secure one of *your own* apps** — threat-model it, fix its [[cybersecurity/06-attacks-and-threats/03-web-application-attacks|OWASP Top 10]] issues, add [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|security headers]], scan its dependencies, get secrets out of the repo. Highest relevance — it hardens real work and teaches app-sec, the natural security path for a developer.
- 🟢 **Build a home lab** — a VM lab ([[cybersecurity/02-ethical-hacking/05-home-lab-setup|home lab setup]]) with Kali + a deliberately-vulnerable target (Juice Shop, DVWA, Metasploitable), isolated from your real network. The sandbox for everything below.
- 🟢 **Capture the Flag** — work a beginner path on TryHackMe / HackTheBox / picoCTF. The fastest, most fun way to build hands-on offensive intuition ([[cybersecurity/02-ethical-hacking/12-practice-exercises|practice]]).
- 🟡 **Stand up a SIEM and catch an attack** — deploy Wazuh or Elastic Security, ship logs to it, run a benign attack against your lab target, and *write the detection rule* that catches it ([[cybersecurity/07-security-operations/02-logging-siem-and-detection|logging & SIEM]]). Real blue-team reps.
- 🟡 **Authorized web-app pentest + report** — pentest a vulnerable app you host, then write a professional [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|findings report]]. The report is the actual deliverable of the job.
- 🟡 **Harden a server to CIS + an IR runbook** — take a fresh VM, harden it to a [[cybersecurity/08-governance-risk-and-compliance/01-risk-and-frameworks|CIS benchmark]], verify it; and write an [[cybersecurity/07-security-operations/04-incident-response|incident-response runbook]] for a scenario, then tabletop it.
- 🔴 **Detection engineering from ATT&CK** — pick a [[cybersecurity/07-security-operations/03-threat-intelligence-and-hunting|MITRE ATT&CK]] technique, emulate it in your lab, and build the detection that fires on it. The core skill of a modern blue team.

---

## Hardware & Embedded
*The column where you already have **more built than written** — [[projects/iot-bridge-pcb/task|the IoT Bridge PCB]] is a real fabricated board. These extend that rather than starting from zero. Note the difficulty scale shifts here: everything has a lead time, because parts ship and boards get fabbed.*

- 🟢 **Blink, but properly** — get an LED blinking on a bare microcontroller with **no Arduino framework**: registers directly, your own delay, read the datasheet for the GPIO section. The "hello world" that actually teaches something, because the abstraction you skipped is the whole lesson ([[hardware/03-embedded-systems|GPIO & the firmware loop]]).
- 🟢 **Talk to a sensor over I2C** — wire a temperature/IMU sensor, write the driver yourself from the datasheet rather than importing a library: address it, read its registers, convert the raw value. Then put a scope or logic analyser on the bus and *watch the transaction you wrote* ([[hardware/05-communication-protocols|UART/I2C/SPI]]).
- 🟢 **Instrument your own power** — measure the actual current draw of a board in idle, active, and sleep, and make a number-backed claim about how long it would run on a given battery. Turns "power budget" from a phrase into arithmetic.
- 🟡 **Design a small board and have it fabbed** — something genuinely simple (a breakout, a sensor node, a USB-powered widget): schematic → footprints → layout → gerbers → order it → bring it up. The [[hardware/10-kicad-basics|KiCad]] workflow end to end, at a scale where a mistake costs £15 and a fortnight rather than a project.
- 🟡 ⭐ **Rev 2 of the IoT Bridge** — you have a board and you have notes on what you'd change. Do the revision: fix what rev 1 got wrong, and write up the diff and *why*. **Designing a rev 2 is a different and more valuable skill than designing a rev 1**, and it's the [[PRIMETECHIE|Rank V hardware gate]] almost nobody has.
- 🟡 **Bring-up procedure, written down** — take a new board and document the order you power and verify it: continuity before power, current-limited first power-on, rails measured against the schematic, then clocks, then comms. Then use it on the next board. The checklist that stops you releasing the smoke.
- 🟡 **Firmware you can update over the air** — an ESP32 that fetches and applies its own firmware update, with a rollback path when the new image doesn't boot. Ties [[hardware/03-embedded-systems|embedded]] to [[foundations/networking/README|networking]] and to the "design for failure" instinct from [[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]].
- 🔴 **A device fleet that survives a bad network** — several nodes reporting to a server they can't always reach: local buffering, reconnect with backoff, and a defensible answer for what happens when two nodes resync with conflicting data. This is [[architecture/04-distributed-systems/README|distributed systems]] with a physical body, and it's the [[PRIMETECHIE|Rank IV hardware analogue]].
- 🔴 **Debug something electrical and prove it** — take a fault you'd normally guess at and instrument it instead: scope the rail, find the noise, identify the cause (insufficient decoupling, ground bounce, a trace carrying more current than it should), fix it, and show the before/after trace. The hardware equivalent of a flame graph.

---

## Robotics
*⚠️ **The notes exist; the reps don't.** [[robotics/README|robotics/]] is now 14 notes, and every one is `[reference]` — assembled from the standard sources, not from a robot that moved. **These projects are what would make that folder trustworthy**, and its own README says as much. The vault's rule normally puts the build before the notes; this domain went the other way, so the debt is explicit.*

- 🟢 **Make one motor go exactly where you tell it** — a servo or a stepper with an encoder, commanded to a position and holding it. Then disturb it by hand and watch it correct. That's a closed loop, and it's the entire subject in miniature.
- 🟡 ⭐ **Tune a PID by hand, and write down what each term did** — a line follower or a self-balancing two-wheeler. Start with P only and watch it oscillate; add D and watch it stop; add I and watch the steady-state error close. **Tuning one loop badly on real hardware teaches more than any amount of control theory reading** — and it's the honest prerequisite for trusting a word of [[engineering/02-control-theory/04-pid-control|the PID note]].
- 🟡 **Sensor fusion on something that moves** — combine an accelerometer and a gyro into one angle estimate with a complementary filter, and demonstrate why neither alone is usable (one drifts, one is noisy). The intuition Kalman filters formalise.
- 🔴 **Teleoperation with a latency budget** — drive something remotely and measure the end-to-end delay, then make it degrade safely when the link drops rather than continuing at the last command. Joins [[foundations/networking/15-network-performance|latency]] to a machine that can hurt someone.
- 🔴 **A robot that maps a room** — odometry plus a range sensor into a 2D occupancy map, and an honest account of how far it drifts. The entry point to [[robotics/12-localisation-and-slam|SLAM]], and the project that turns "odometry drifts without bound" from a sentence you read into a number you measured.

**If you do one:** the PID tuning project. It's cheap, it fits on a desk, and it's the difference between having read [[engineering/02-control-theory/04-pid-control|the PID note]] and having earned it.

---

## Graphics & GPU — the most visible reps
*⚠️ **Notes exist, reps don't** — [[foundations/computer-graphics/README|graphics]] and [[foundations/gpu-and-parallel-computing/README|GPU & parallel]]. **Best reps-to-effort ratio in the vault**, because a broken renderer* looks *broken. Free GPUs on Colab and Kaggle if you don't have one.*

- 🟢 ⭐ **[Ray Tracing in One Weekend](https://raytracing.github.io)** — genuinely a weekend, no API, no build system, and you finish with a real rendered image. **The single best entry point in graphics.**
- 🟢 **Break coalescing deliberately** — write a CUDA kernel, transpose the index calculation, measure. **A 10–30× slowdown from one swapped index** makes [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|note 05]] permanent.
- 🟡 **Write a software rasteriser** — edge functions, z-buffer, perspective-correct interpolation. No GPU. **Then deliberately skip the perspective correction and watch textures warp like a PlayStation 1** → [[foundations/computer-graphics/03-rasterisation|03]].
- 🟡 **Reduce your render resolution.** If the frame rate doesn't change, you're CPU-bound. **A ten-second test that saves days** → [[foundations/computer-graphics/06-the-gpu-graphics-pipeline|06]].
- 🟡 ⭐ **Matrix multiply on a GPU three ways** — naive, tiled with shared memory, then cuBLAS. Measure each. **Seeing how far short hand-written code falls is the lesson** → [[foundations/gpu-and-parallel-computing/04-parallel-patterns|04]].
- 🔴 **Profile a real training loop** with `torch.profiler` and find the data-loading gaps. **They're almost always there**, and the GPU is idle while you optimise kernels → [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|06]].

**If you do one:** Ray Tracing in One Weekend. It's the rare project that's short, self-contained, and produces something you want to show people.

---

## Game Development — the reps that are their own portfolio
*⚠️ **Notes exist, reps don't** — [[game-development/README|game-development/]]. **The one domain where finishing is the whole skill**, and where a shipped 48-hour jam entry outperforms a polished unfinished thing. Free: Godot (MIT), itch.io hosting, Ludum Dare/GMTK jams.*

- 🟢 ⭐ **Do a game jam.** Ludum Dare, GMTK, or any of the hundreds on itch.io. A theme, 48 hours, ship something. **The single highest-value item in this section** — it forces scope discipline and an actual finish line, and produces a public artefact with feedback from strangers → [[game-development/08-getting-started|08]].
- 🟢 **Ship Pong, then Breakout.** Two weekends, publicly on itch.io. Menus, sound, a build someone else can run. **The last 20% is where the learning is** → [[game-development/08-getting-started|the ladder]].
- 🟢 **Write a shader that colours a surface by its normal**, then by a light direction. Ten lines on Shadertoy. **It demystifies the whole of graphics** → [[foundations/computer-graphics/10-practice-exercises|graphics exercise 1]].
- 🟢 **Implement Euler integration and watch a pendulum gain energy**, then change two lines to semi-implicit and watch it stop. **Ten minutes, and note 04's central claim becomes a memory** → [[game-development/04-game-physics|04]].
- 🟡 **A platformer with good feel** — coyote time, jump buffering, variable jump height, all hand-authored rather than physics-driven. **Feel is a real, teachable skill and it's what interviews ask about** → [[game-development/04-game-physics|04]].
- 🟡 **Profile a frame with RenderDoc.** Capture, find where 16 ms goes, fix one thing, re-measure. **Seeing the budget is worth more than reading about it** → [[game-development/03-graphics-for-games|03]].
- 🟡 **A top-down roguelike** — enemy state machines, A\* pathfinding on a navmesh or grid, procedural levels → [[game-development/05-game-ai|05]].
- 🔴 ⭐ **Build a 2D engine from scratch and ship one small game with it.** Window, fixed-timestep loop, sprite renderer, collision, audio. **The game is what forces you to build the parts engine projects skip** → [[game-development/engines/from-scratch|from-scratch]].
- 🔴 **Networked multiplayer for a simple game** — client prediction, server reconciliation, entity interpolation. **The hardest common problem in the field**; do it after something simpler ships → [[game-development/06-multiplayer-and-networking|06]].

**If you do one:** the game jam. It tests scope, finishing, and whether you actually enjoy this — for the price of a weekend, before you commit years.

---

## Numerical methods & information theory — short scripts, real insight
*⚠️ **Notes exist, reps don't** — [[foundations/numerical-methods/README|numerical methods]] and [[foundations/information-theory/README|information theory]]. Every one of these is under 50 lines.*

- 🟢 ⭐ **Plot the finite-difference error U-curve** — compute $f'(x)$ at $h$ from $10^{-1}$ to $10^{-16}$, plot the error. **The V shape is the whole of [[foundations/numerical-methods/01-why-numerical-methods|note 01]] in one picture**, and it takes five minutes.
- 🟢 **Break the quadratic formula** — solve $x^2 + 10^8x + 1 = 0$ naively and with the stable form. **Watch half your digits vanish** → [[foundations/numerical-methods/02-floating-point-and-error|02]].
- 🟢 **Measure the entropy of a real file**, then compare against what `gzip` and `zstd` achieve. **The gap is the redundancy your model isn't capturing** → [[foundations/information-theory/01-what-information-is|01]].
- 🟡 **Reproduce Runge's phenomenon** — interpolate $1/(1+25x^2)$ at 5, 10, 20 equally-spaced points. **More points makes it worse.** Then use Chebyshev nodes and watch it converge → [[foundations/numerical-methods/06-interpolation-and-approximation|06]].
- 🟡 **Hit a stiffness wall** — integrate a stiff ODE with `RK45` and with `BDF`. **Compare step counts; it's usually orders of magnitude** → [[foundations/numerical-methods/08-ordinary-differential-equations|08]].
- 🟡 **Fit forward vs reverse KL to a bimodal distribution.** One covers both modes, one picks a single mode. **Twenty lines, and [[foundations/information-theory/04-cross-entropy-and-kl-divergence|note 04]]'s central point becomes visual.**
- 🔴 **Do a convergence study on anything** — halve the step, confirm the error falls at the promised rate. **The single most useful habit in numerical work.**

**If you do one:** the finite-difference U-curve. Five minutes, and it permanently changes how you think about "just use a smaller step."

---

## CS Theory — the cheapest reps in this vault
*⚠️ **Notes exist, reps don't** — [[foundations/discrete-math/README|discrete maths]], [[foundations/theory-of-computation/README|theory of computation]] and [[foundations/computer-architecture/README|computer architecture]] are all `[reference]`. **Unlike engineering or robotics, closing this gap needs no hardware and no money** — `perf`, a compiler, and an afternoon. That makes it the least excusable gap on this page.*

- 🟢 **Run `perf stat` on something you wrote** — look at the IPC, then work out *why* it's that number. Twenty minutes, and it turns [[foundations/computer-architecture/12-performance|the whole performance note]] from reading into a method you've used.
- 🟢 **Reproduce the sorted-array branch experiment** — the same loop over sorted vs shuffled data, several-fold difference, identical instruction count. **Seeing it yourself is different from reading it** → [[foundations/computer-architecture/06-pipelining|pipelining]].
- 🟢 **Demonstrate false sharing** — two threads incrementing adjacent array elements, then padded to 64 bytes. **Watch a parallel program get faster by adding memory** → [[foundations/computer-architecture/09-caches-in-depth|caches]].
- 🟡 ⭐ **Matrix multiply, three ways** — naive, loop-interchanged, blocked. Measure each. **A 10× spread from reordering identical arithmetic** is the single best demonstration of [[foundations/computer-architecture/08-the-memory-hierarchy|the memory hierarchy]].
- 🟡 **Prove three things on paper** — $\{a^nb^n\}$ isn't regular, the halting problem is undecidable, one NP-completeness reduction. **Reading a proof and producing one are different skills** → [[foundations/discrete-math/03-proof-techniques|proof techniques]].
- 🟡 ⭐ **Build a regex engine** — Thompson's construction → subset construction → simulate the DFA. A few hundred lines, and it makes [[foundations/theory-of-computation/02-finite-automata|the regex/NFA/DFA equivalence]] concrete. **This is the missing ninth guide in [[build-your-own-shit/README|build-your-own-shit]].**
- 🔴 **Write a SAT solver** — DPLL is short; adding clause learning makes it genuinely useful. The best way to understand why [[foundations/theory-of-computation/07-complexity-classes|NP-completeness]] is survivable in practice.
- 🔴 **Lean's Natural Number Game, then a real proof in Lean** — a proof assistant will not let you skip a step, which is exactly the discipline reading proofs doesn't build.

**If you do one:** the matrix-multiply trio. It takes an hour, produces a number you can't argue with, and permanently changes how you think about data layout.

---

## Foundations (Python / data tools)
*Do these alongside the ML/DS tracks — they're the muscle memory those depend on.*

- 🟢 **pandas cleaning gauntlet** — take a deliberately messy CSV and clean it end-to-end ([[ai-ml/00-foundations/04-python-and-data-tools/03-pandas|pandas]]): missing data, dtypes, duplicates, inconsistent categories — no loops, all vectorized.
- 🟢 **NumPy, no loops** — reimplement a handful of numeric routines (normalization, moving average, a distance matrix, one-hot encoding) as pure vectorized [[ai-ml/00-foundations/04-python-and-data-tools/02-numpy|NumPy]] — the "if you're looping you're doing it wrong" drill.
- 🟢 **10 questions, one dataset** — answer ten analytical questions about a dataset using only `groupby`/`value_counts`/boolean selection ([[ai-ml/00-foundations/04-python-and-data-tools/03-pandas|pandas]]) and [[ai-ml/00-foundations/04-python-and-data-tools/04-visualization-basics|seaborn]].

---

## Related
- [[README|Knowledgebase home]] — the notes these projects exercise
- [[PRIMETECHIE|The Primetechie Path]] — which rank and column each project is a gate for
- [[languages/01-java/02-jvm-and-concurrency/exercises/README|Java concurrency exercises]] · [[ai-ml/03-ai-engineer/19-practice-exercises|AI engineering exercises]] · [[cybersecurity/02-ethical-hacking/12-practice-exercises|ethical hacking exercises]] · [[devops/01-linux/15-rhcsa/15-practice-exercises|RHCSA exercises]] — where ready-made reps already exist
- [[hardware/README|Hardware]] · [[robotics/README|Robotics]] · [[engineering/README|Engineering]] · [[foundations/computer-architecture/README|CS theory]] · [[foundations/computer-graphics/README|graphics & GPU]] — the newest columns. Hardware has a fabricated board behind it; the rest have notes and no reps, which is what these projects are for — and **everything below hardware on that list is free to try**
- [[problem-solving/thinking-patterns|problem-solving]] — the thinking-process companion
