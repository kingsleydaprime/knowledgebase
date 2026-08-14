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
*The deepest reps in the vault. Each one turns a whole [[architecture/README|architecture / distributed-systems]] topic from words into bone-deep understanding. These are the projects you asked for — pick one and go far.*

- 🔴 ⭐ **Your own Redis** — an in-memory key-value store: implement the core data structures (strings, lists, hashes, sorted sets), a TCP server speaking a simple protocol (RESP), and persistence (snapshotting + an append-only log). Teaches data structures + networking + [[languages/01-java/02-jvm-and-concurrency/02-concurrency|event-loop concurrency]] + durability. The most approachable of these — start here. (See *Build Your Own Redis* / the "codecrafters" style.)
- 🔴 **Your own database** — a storage engine from scratch: a **B-tree** or **LSM-tree** on-disk structure, an [[architecture/02-building-blocks/03-databases-at-scale|index]], a simple query layer, and [[databases/database-design-reference|ACID transactions]] (a write-ahead log for durability, isolation via locking/MVCC). The project that demystifies what a database *is*. (See *Designing Data-Intensive Applications* + *Build Your Own Database*.)
- 🔴 **Your own git** — a content-addressable store: [[git/git-reference|hash objects]] (blobs/trees/commits), build the commit DAG, and implement `add`/`commit`/`log`/`branch`/`checkout`. Small, elegant, and it permanently demystifies git. (See *Build Your Own Git* / "git from the inside out.")
- 🔴 ⭐ **A Raft key-value store** — [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] made real: implement Raft (leader election, log replication, safety), then a replicated KV store on top, and test it against node crashes and partitions. **The single best distributed-systems learning project** — it forces you to confront every edge case the [[architecture/04-distributed-systems/README|theory]] describes. (See MIT 6.824 labs — the gold standard.)
- 🔴 **Your own language / interpreter** — lexer → parser → tree-walking interpreter (then maybe a bytecode VM or compiler). *Note:* this is **compiler/interpreter theory**, a different domain from system design — there's no vault course for it yet (a good future one). Superb for understanding how code runs. (See *Crafting Interpreters* — the definitive resource.)

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
*⚠️ **No vault course backs these yet** — [[robotics/README|robotics/]] is scaffold. Listed deliberately: the vault's own rule is that the build comes before the notes, so the first project here is the prerequisite for writing that folder at all.*

- 🟢 **Make one motor go exactly where you tell it** — a servo or a stepper with an encoder, commanded to a position and holding it. Then disturb it by hand and watch it correct. That's a closed loop, and it's the entire subject in miniature.
- 🟡 ⭐ **Tune a PID by hand, and write down what each term did** — a line follower or a self-balancing two-wheeler. Start with P only and watch it oscillate; add D and watch it stop; add I and watch the steady-state error close. **Tuning one loop badly on real hardware teaches more than any amount of control theory reading** — and it's the honest prerequisite for the `control-theory-basics` note.
- 🟡 **Sensor fusion on something that moves** — combine an accelerometer and a gyro into one angle estimate with a complementary filter, and demonstrate why neither alone is usable (one drifts, one is noisy). The intuition Kalman filters formalise.
- 🔴 **Teleoperation with a latency budget** — drive something remotely and measure the end-to-end delay, then make it degrade safely when the link drops rather than continuing at the last command. Joins [[foundations/networking/15-network-performance|latency]] to a machine that can hurt someone.
- 🔴 **A robot that maps a room** — odometry plus a range sensor into a 2D occupancy map, and an honest account of how far it drifts. The entry point to SLAM, and the project that would justify writing that note.

**If you do one:** the PID tuning project. It's cheap, it fits on a desk, and it converts an entire planned folder from aspiration into something you've earned the right to write.

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
- [[hardware/README|Hardware]] · [[robotics/README|Robotics]] — the two newest columns; robotics is scaffold, so its projects come *before* its notes
- [[problem-solving/thinking-patterns|problem-solving]] — the thinking-process companion
