# Project Ideas — turning notes into ability

The notes in this vault are a **map**. This file is the **territory** — the projects that turn "I read about it" into "I built it and can prove it." Reading is not reps; building is.

## How to use this

- **Pick one and finish it.** One shipped project beats five half-started ones. Finishing — deployed, tested, written up — is the skill.
- **Extend your real projects where you can.** Adding CI/CD or JMH benchmarks to an app you already built ([[projects/record-id-generator-java/learning/01-java-fundamentals|record-id-generator]], [[projects/direct-debit-sandbox-java/learning/01-java-fundamentals|direct-debit-sandbox]], arete, gees-arise, nextvibe) is higher-signal than a toy, and faster to start.
- **Write it up.** A short README with the *why* and what you learned turns a project into portfolio signal. A repo no one can understand isn't signal.

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade.

**If you only do five** (highest signal for where you're aiming): the ⭐ projects below — the order-book matching engine (Java/systems), a RAG app over *this vault* (AI eng), an end-to-end MLOps project (ML eng), a full A/B-test analysis (data sci), and putting one app through a real CI/CD + container deploy (DevOps).

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

## Foundations (Python / data tools)
*Do these alongside the ML/DS tracks — they're the muscle memory those depend on.*

- 🟢 **pandas cleaning gauntlet** — take a deliberately messy CSV and clean it end-to-end ([[ai-ml/00-foundations/04-python-and-data-tools/03-pandas|pandas]]): missing data, dtypes, duplicates, inconsistent categories — no loops, all vectorized.
- 🟢 **NumPy, no loops** — reimplement a handful of numeric routines (normalization, moving average, a distance matrix, one-hot encoding) as pure vectorized [[ai-ml/00-foundations/04-python-and-data-tools/02-numpy|NumPy]] — the "if you're looping you're doing it wrong" drill.
- 🟢 **10 questions, one dataset** — answer ten analytical questions about a dataset using only `groupby`/`value_counts`/boolean selection ([[ai-ml/00-foundations/04-python-and-data-tools/03-pandas|pandas]]) and [[ai-ml/00-foundations/04-python-and-data-tools/04-visualization-basics|seaborn]].

---

## Related
- [[README|Knowledgebase home]] — the notes these projects exercise
- [[languages/01-java/02-jvm-and-concurrency/exercises/README|Java concurrency exercises]] — the one place ready-made reps already exist
- [[problem-solving/thinking-patterns|problem-solving]] — the thinking-process companion
