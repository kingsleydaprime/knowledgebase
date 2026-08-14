# 🕶️ THE PRIMETECHIE PATH

> *"There's always that one guy."*
>
> A hypothetical, mildly ridiculous, but structurally serious progression from "competent developer" to the engineer everyone else escalates to. Named because I'm kingsleydaprime and nobody was going to stop me.

---

## First, the honest part

Movies get the "one guy" wrong. He's never the one who memorised the most APIs. He's the one who, when everyone else is guessing, **asks the question that eliminates half the possibilities** — and he can do that because he knows what's happening one layer below where everybody else stopped looking.

That's the actual trait, and it decomposes into four things you can deliberately build:

| The trait | What it actually is | Where it's built |
|---|---|---|
| **Depth** | knowing the layer *below* the one you work at | [[foundations/networking/README\|networking]], [[foundations/os/fundamentals\|OS]], [[architecture/04-distributed-systems/README\|distributed systems]], [[foundations/dsa/README\|DSA]], [[hardware/README\|hardware]] |
| **Debugging** | narrowing the search space instead of guessing | [[foundations/networking/16-debugging-networks\|bisecting layers]], reading errors properly, profilers, a multimeter |
| **Shipping** | finishing, deploying, operating, being on call for it | [[project-ideas\|projects]], [[devops/README\|devops]] |
| **Communication** | making others faster — writing, reviewing, teaching | [[research/README\|research & writing]], [[concepts/04-best-practices/02-pr-structure\|PR structure]], this vault |

**Three of those are not code.** That's the part the movie leaves out, and it's the part most engineers skip for a decade.

### It isn't only software

The trait is domain-independent, so the path is too. Every rank below has gates in five disciplines:

| | |
|---|---|
| 💻 **Software** | Backends, systems, algorithms — [[backend/README\|backend]], [[foundations/dsa/README\|dsa]], [[architecture/README\|architecture]], [[languages/01-java/README\|java]], and [[ai-ml/03-ai-engineer/README\|AI engineering]] |
| ☁️ **Infra** | Linux, cloud, containers, CI/CD, observability — [[devops/README\|devops]] |
| 🔐 **Security** | Offence and defence, because you can't do one well without the other — [[cybersecurity/README\|cybersecurity]] |
| 🔌 **Hardware** | Electronics, embedded, boards that physically exist — [[hardware/README\|hardware]] |
| 🧠 **ML & Data** | Training models and reasoning from data — [[ai-ml/02-ml-engineer/README\|ml-engineer]], [[ai-ml/01-data-scientist/README\|data-scientist]], [[ai-ml/00-foundations/03-mathematics/README\|the maths]] |

### Why AI is split across two columns

Because it's two different jobs, and [[ai-ml/README|the ai-ml course]] already says so: *"the sharpest line is between **ML Engineer** (trains models, needs the math and the algorithm zoo) and **AI Engineer** (uses someone else's trained models)."*

- **AI engineering is software engineering.** You call an API, handle retries and timeouts, validate a schema, write an eval suite, argue about cost. It's backend work with a probabilistic dependency, and it belongs in the Software column.
- **ML engineering isn't.** Its bedrock is [[ai-ml/00-foundations/03-mathematics/README|linear algebra, calculus, probability and optimization]] — an entire foundation no other column needs. "Knowing the layer below" means the maths, not the kernel. Its failure modes are leakage, overfitting and drift, none of which are software bugs.
- **Data science isn't even engineering.** It optimises for a defensible *answer*, not shipped software — statistics, experiment design, causal inference.

**You are not expected to clear all five columns at a rank.** Clear your primary discipline and get to Rank I–II literacy in the others — that's what makes you the person who can follow a problem from a web request down to a voltage rail, or from a dashboard back to a leaked feature, instead of handing it off at the boundary. The columns exist so the boundaries are visible, not so you tick every box.

### The rules of the path

1. **Reading is not a rank.** Every gate below is *demonstrable* — something you can do in front of someone, or a thing that exists and runs. Notes are the map; [[project-ideas|projects]] are the territory.
2. **Depth beats breadth, until it doesn't.** Go deep enough to hit bedrock in *one* discipline before spreading out — the experience of having gone all the way down once is what makes you unafraid to do it again. Breadth without one deep column is just being shallow in four places.
3. **You can't skip the boring rank.** Rank II is unglamorous and it's the one that separates people. Everyone wants to build a Raft KV store; almost nobody wants to learn what `CLOSE_WAIT` means.
4. **The gate is "could you teach it?"** not "have you read it?" The [[INTERVIEW|interview banks]] exist for exactly this — cover the answer, say it out loud, compare.

---

## 🥉 RANK I — THE BUILDER
*"It works on my machine, and I know why."*

The baseline. You can take an idea to a running thing without help.

**💻 Software**
- [ ] Ship a full-stack app **to a real domain over HTTPS** — not localhost, not a screenshot
- [ ] Use git like a professional: feature branches, [[git/12-conventions-and-hygiene|conventional commits]], an interactive rebase you didn't panic during, and a merge conflict you resolved by *reading* rather than picking a side
- [ ] Write a test suite that has actually caught a regression → [[backend/07-practices/02-testing-a-backend|testing a backend]]
- [ ] Read a stack trace top-to-bottom and fix the root cause, **not the symptom**

**☁️ Infra**
- [ ] Deploy that app yourself → [[devops/04-vps/vps-setup|VPS]], [[devops/02-docker/README|Docker]]
- [ ] Explain what happens between typing a URL and seeing a page → [[foundations/networking/01-what-a-network-is|note 01]]
- [ ] Find out why a service won't start **from its logs**, not from guessing → [[devops/01-linux/17-logs-and-journald|logs & journald]]

**🔐 Security**
- [ ] Lock down a box you own: keys-only SSH, root login off, default-deny inbound → [[devops/01-linux/20-firewalls-and-hardening|firewalls & hardening]]
- [ ] Run `ss -tulpn` on your own server and be able to justify **every single listening port**

**🔌 Hardware**
- [ ] Build a circuit on a breadboard that does something, having **calculated** the resistor rather than copying it → [[hardware/01-electricity|electricity]]
- [ ] Read a datasheet well enough to wire a part you've never used → the [[hardware/README|golden rule]], and `blog-drafts/reading-a-datasheet.md`

**🧠 ML & Data**
- [ ] Train a model on a real dataset and **beat a trivial baseline** — and be able to say what the baseline was and why beating it is the only claim that means anything
- [ ] Split your data properly and explain what a test set is *for* → [[ai-ml/02-ml-engineer/02-working-with-data/03-train-val-test-splits|train/val/test]]
- [ ] Pick an evaluation metric on purpose, and say why accuracy was the wrong one → [[ai-ml/02-ml-engineer/04-model-evaluation/01-evaluation-metrics|metrics]]

**Capstone:** any 🟢 in [[project-ideas|project-ideas]], deployed and written up.

**You've arrived when:** you stop googling error messages verbatim and start reading them.

---

## 🥈 RANK II — THE DIAGNOSTICIAN
*"Everyone else is guessing. You are bisecting."*

**The rank that actually separates people, and the least glamorous.** Most engineers plateau here forever because the material is unsexy and the payoff is invisible until the day it isn't.

This is also the rank where the four columns stop being separate skills. The method — hypothesis, cheapest discriminating test, eliminate, repeat — is identical whether the tool is a debugger, `tcpdump`, a SIEM query, or an oscilloscope.

**💻 Software**
- [ ] Debug a problem **you cannot reproduce locally**, using logs and metrics alone
- [ ] Profile something slow and find the *actual* bottleneck — including being willing to discover it's the database, not your code
- [ ] Read a flame graph. Read a GC log. Read an `EXPLAIN` plan. → [[databases/sql-reference|SQL]]

**☁️ Infra**
- [ ] `tcpdump` a request and **find the three-way handshake with your own eyes** → [[foundations/networking/06-tcp-connection-lifecycle|TCP lifecycle]]
- [ ] Know, without looking it up, what a pile of `CLOSE_WAIT` sockets means about your code → [[foundations/networking/16-debugging-networks|debugging]]
- [ ] Explain the difference between "connection refused" and a hang, and why it tells you where to look
- [ ] Diagnose a crash from the **previous** boot's logs → [[devops/01-linux/19-the-boot-process|boot process]], `journalctl -b -1`
- [ ] Fix a full disk that `df -h` says has space → [[devops/01-linux/18-disks-and-filesystems|disks & filesystems]]

**🔐 Security**
- [ ] Triage an alert to true or false positive, and **defend the call**
- [ ] Write a detection rule, then **test it by performing the attack** against your own lab → [[cybersecurity/07-security-operations/02-logging-siem-and-detection|SIEM & detection]], [[cybersecurity/02-ethical-hacking/05-home-lab-setup|home lab]]
- [ ] Read an auth log and reconstruct what someone tried to do

**🔌 Hardware**
- [ ] Find where a voltage is being lost with a multimeter, by bisecting the rail rather than poking hopefully
- [ ] Look at a signal on a scope and explain why it isn't the clean square wave the datasheet drew

**🧠 ML & Data**
- [ ] Diagnose a model that scored well in your notebook and badly in reality — and identify **which** it was: leakage, distribution shift, or a broken split → [[ai-ml/02-ml-engineer/02-working-with-data/03-train-val-test-splits|splits & leakage]]
- [ ] Read a learning curve and say whether you're looking at bias or variance → [[ai-ml/02-ml-engineer/04-model-evaluation/02-overfitting-and-regularization|overfitting]]
- [ ] Find the bug that was in the **data**, not the model. It usually is

**Universal:** write a postmortem with a real root cause and no blame (`blog-drafts/four-bugs-that-shipped.md` is one).

**Capstone:** instrument a real app with metrics + traces, then **deliberately break it** and diagnose it from the dashboards alone.

**You've arrived when:** someone else's bug becomes interesting rather than annoying.

---

## 🥇 RANK III — THE SYSTEMS THINKER
*"You've built the thing you used to import."*

Depth becomes bedrock. You stop treating infrastructure as magic because you've written a bad version of it yourself.

**The non-negotiable gate, in whichever column is yours:**

- [ ] 💻 **Build one thing from scratch that you previously only used** — your own Redis (most approachable), your own git, an HTTP/1.1 server from raw sockets → [[foundations/networking/09-sockets-and-the-network-api|sockets]], or a B-tree/LSM storage engine
- [ ] 🔌 **Design, order, and bring up your own PCB** — schematic → layout → fab → first power-on without releasing the smoke → [[hardware/10-kicad-basics|KiCad]], [[projects/iot-bridge-pcb/task|IoT Bridge PCB]]
- [ ] 🔐 **Exploit something end to end in your own lab** — recon → foothold → privilege escalation → written up as a report someone could act on → [[cybersecurity/02-ethical-hacking/12-practice-exercises|practice exercises]]
- [ ] ☁️ **Run the thing you usually rent** — self-host the database, the queue, the object store, and survive the operational reality of it
- [ ] 🧠 **Implement the algorithm you usually import** — gradient descent and backprop by hand on a small network, or a decision tree from scratch, then check it against the library version → [[ai-ml/00-foundations/03-mathematics/04-optimization|optimization]], [[ai-ml/02-ml-engineer/05-deep-learning/02-training-loop-in-pytorch|the training loop]]

**Also at this rank, whatever your column:**
- [ ] Write concurrent code and **prove** it correct — where "prove" means a stress test that actually fails on a bad version → [[languages/01-java/02-jvm-and-concurrency/README|concurrency]]
- [ ] Explain memory: stack vs heap, cache lines, why the memory model exists → [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM internals]]
- [ ] Design a system on a whiteboard with explicit tradeoffs and named failure modes → [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|system design]]
- [ ] Reason about consistency without saying "eventually consistent" as though it settles anything → [[architecture/04-distributed-systems/04-consistency-models|consistency models]]

**Capstone:** the 🔴 ⭐ **in-memory order book + matching engine**, benchmarked with JMH, p99 measured and explained. Or your own Redis with persistence. Or a working board you designed.

**You've arrived when:** you read a framework's source when the docs are ambiguous, and it's not scary.

---

## 💎 RANK IV — THE DISTRIBUTED MIND
*"You have internalised that the network will betray you."*

Where most senior engineers stop, and where the genuinely hard problems start.

**This rank is narrower than the others on purpose.** Its shape is distributed-systems-shaped, and forcing four columns onto it would be dishonest. What it has instead is one insight that shows up everywhere: *independent things that must agree, over a channel that loses messages.* That's a cluster, and it's also a fleet of devices, and it's also an incident with three teams in the call.

- [ ] **Implement Raft.** Leader election, log replication, safety. Then a KV store on it. Then kill nodes and partition the network while it runs. → [[architecture/04-distributed-systems/08-raft-in-depth|Raft in depth]]
- [ ] Explain why exactly-once delivery is impossible, and what you build instead → [[architecture/04-distributed-systems/10-distributed-transactions|idempotency]]
- [ ] Explain CAP correctly — including why most people quoting it are wrong → [[architecture/04-distributed-systems/02-theoretical-limits|PACELC]]
- [ ] Debug a p99 problem that turns out to be transport-layer → [[foundations/networking/15-network-performance|tail latency]], incast, RTO
- [ ] Run something in production that **other people depend on**, and carry the pager for it
- [ ] Design for failure explicitly: circuit breakers, backpressure, graceful degradation → [[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]]

**The same shape in the other columns, if that's where you live:**
- 🔐 Run an incident end to end — detect, contain, eradicate, recover, postmortem → [[cybersecurity/07-security-operations/04-incident-response|incident response]]
- 🔌 Build a fleet of devices that stay coherent with a server they **can't always reach** — buffering, reconnection, conflict on resync → [[hardware/08-iot-architecture|IoT architecture]]
- 🧠 Operate a model **other people depend on** — monitor it for drift, detect that it has silently degraded, and retrain it without breaking the consumers. A model in production is a dependency that rots on its own, which nothing else in this document does → [[ai-ml/02-ml-engineer/10-mlops/03-monitoring-and-edge|monitoring & drift]]

**Capstone:** the Raft KV store, tested against partitions and crashes. Write up what surprised you — that write-up is worth more than the code.

**You've arrived when:** "just add a retry" makes you ask what happens if the first one succeeded.

---

## 🔮 RANK V — THE SPECIALIST
*"You are the person who is called."*

Depth in **one** domain deep enough that you're the escalation point. Pick a lane — this rank is explicitly not about breadth.

**⚡ Low-latency / systems** *(the current target)*
- [ ] Sub-microsecond p99 on a hot path, measured, with the number defended
- [ ] Zero-allocation code on the hot path, verified by profiler not by vibes
- [ ] Explain mechanical sympathy: cache lines, false sharing, branch prediction, NUMA
- [ ] Know whether your latency spike came from [[foundations/networking/08-congestion-control|congestion control]] or [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|GC]]

**🤖 AI engineering** *(a Software lane — you build on models you didn't train)*
- [ ] Ship an agent with a real eval suite, not vibes → [[ai-ml/03-ai-engineer/19-practice-exercises|the exercises]]
- [ ] Red-team your own system for prompt injection and document the mitigations
- [ ] Defend a model/cost/latency tradeoff with numbers

**🧠 ML engineering** *(the other half — you train the model)*
- [ ] Take a model from a notebook to a served endpoint with a **reproducible** training pipeline — same data and seed, same model → [[ai-ml/02-ml-engineer/10-mlops/README|MLOps]]
- [ ] Detect drift in production and retrain on a schedule you can justify → [[ai-ml/02-ml-engineer/10-mlops/03-monitoring-and-edge|monitoring]]
- [ ] Defend a metric choice to someone who wanted accuracy, using the confusion matrix and the actual cost of each error type
- [ ] Know when **not** to train — when a heuristic, a bought API, or [[ai-ml/03-ai-engineer/06-rag-and-embeddings|retrieval]] beats a model you'd have to maintain forever

**📊 Data science**
- [ ] Design and run an experiment that changes a decision — with the power calculation done *before* the data, not after → [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|experimentation]]
- [ ] Tell someone senior their favourite metric is measuring the wrong thing, and be right

**🔐 Security**
- [ ] Find a real vulnerability in a real system, with authorisation → [[cybersecurity/README|cybersecurity]]
- [ ] Build the defensive side too — detection rules that fire, tuned against your own false-positive rate → [[cybersecurity/07-security-operations/README|secops]]
- [ ] Do the boring half: write the finding up so a developer can fix it without asking you a question

**☁️ Infrastructure**
- [ ] Run a multi-region system and survive losing a region
- [ ] Reduce a cloud bill by 50% with a written explanation of *why* it was high
- [ ] Rebuild your entire environment from code, from nothing, and have it work → [[devops/07-infrastructure-as-code/README|IaC]]

**🔌 Hardware & embedded**
- [ ] Take a board from schematic to a **manufactured, working revision two** — where rev 2 exists because you found rev 1's mistakes
- [ ] Debug a problem that turns out to be electrical, not firmware, and prove it with an instrument
- [ ] Design for the physical constraints that don't exist in software: power budget, thermals, EMC, the cost of a part at quantity

**You've arrived when:** people in your specialty ask *you*, and your answer starts with a question.

---

## 👑 RANK VI — THE FORCE MULTIPLIER
*"Your impact stopped being measured in code."*

The rank almost nobody plans for. It's not management — it's the point where **the constraint on your impact stops being your own throughput.** Domain-independent by nature; this is the rank where the columns rejoin.

- [ ] Write something technical that **changes how other people work** → your blog drafts, [[research/09-scientific-writing-craft|writing craft]]
- [ ] Review code so that the author is better afterwards, not just the code → [[concepts/04-best-practices/02-pr-structure|PR structure]]
- [ ] Make a decision under genuine uncertainty, write down the reasoning, and **be publicly wrong about one** → `DECISIONS.md`
- [ ] Mentor someone from Rank I to Rank II
- [ ] Say no to a technically interesting project for a correct business reason
- [ ] Teach the hard thing simply — if you can't do the "kid version first" of it, you don't understand it → the convention every [[foundations/networking/README|networking]] and [[architecture/04-distributed-systems/README|dist-sys]] note follows
- [ ] **Explain your discipline to someone in another one** — the software gate is explaining a race condition to a hardware engineer; the hardware gate is explaining why the board needs another revision to a product manager

**You've arrived when:** your best week involved very little code and you're at peace with that.

---

## 🕶️ RANK VII — PRIMETECHIE
*"That one guy."*

Not a checklist. An emergent property of the six ranks below it, plus years. But it looks like this:

- **You go down a layer without flinching.** Kernel source, RFC, disassembly, a datasheet erratum — you don't know it, but you know how to find out, and you're not afraid.
- **You cross the boundaries other people stop at.** The bug is in the web app, or the network, or the firewall rule, or the firmware, or the power supply — and you don't hand it off at the edge of your job title.
- **Your debugging looks like magic and is actually just method** — hypothesis, cheapest discriminating test, eliminate, repeat. Every time.
- **You've been badly wrong in public** and it made you more trusted, not less.
- **You can explain anything you know to anyone**, at whatever depth they need.
- **You build things people rely on** and you're still there when they break.
- **You know what you don't know**, precisely, and say so without embarrassment.

**The honest closing note:** nobody arrives here and stays. The people who look like this are just further along a road they're still on, and most of them think they're at Rank III. The rank is a direction, not a destination — which is the least cinematic and most true thing on this page.

---

## 📍 Where you actually are right now

Assessed against this vault as of **August 2026** — an honest read, not a flattering one:

| Rank | Status | The gap |
|---|---|---|
| **I — Builder** | ✅ **Cleared** | 12 projects, real deployments, git fluency, a fabricated PCB |
| **II — Diagnostician** | 🟡 **In progress** | Networking course exists — *do* the tcpdump exercise. Observability still reference-only, not run. Security column is the newest and least practised. |
| **III — Systems Thinker** | 🟡 **Partial** | Hardware column is **cleared** — [[projects/iot-bridge-pcb/task\|the IoT Bridge PCB]] is a real board, designed and documented. Software column is not: **no build-your-own project finished yet**, still the single biggest gap in the vault. |
| **IV — Distributed Mind** | 🔵 **Theory only** | [[architecture/04-distributed-systems/README\|15 notes]] read, Raft unimplemented. Theory without reps. |
| **V — Specialist** | 🔵 **Aiming** | Low-latency Java is the stated target; the order-book project is the proof |
| **VI — Force Multiplier** | 🟡 **Started** | This vault *is* Rank VI work. Blog drafts written but unpublished — publish one. |
| **VII** | 🕶️ | see you there |

### Coverage by column, honestly

| Column | Vault state | Reps |
|---|---|---|
| 💻 **Software** | Deep — backend (40), architecture (39), DSA, java (37), AI engineering (21) | Many projects; no build-your-own yet |
| ☁️ **Infra** | Deepest — devops is 83 notes / 123k words | Real deployments; 05–11 still mostly unrun |
| 🔐 **Security** | Deep on paper — 54 notes, the vault's best exercise set | Lab exists; exercises not worked through |
| 🔌 **Hardware** | Real but thin — 15 notes + a 19k-word project | **Strongest reps-to-notes ratio in the vault** |
| 🧠 **ML & Data** | Deep on paper — ml-engineer 42 notes, data-scientist 8 (thinnest track) | **Zero. No project has trained a model** |
| 🤖 **Robotics** | [[robotics/README\|Scaffold only]] | None. Stated direction, not knowledge |

Two asymmetries worth naming:

**Hardware is the one column with more built than written** — every other column is the reverse. The reps are the hard part everywhere else.

**ML & Data is the exact opposite, and it's the starkest gap in the vault.** `ai-ml/` is **98 notes and 60,685 words — the largest domain here by note count**, larger than cybersecurity — and *not one project has trained a model*. Every applied AI thing you've built ([[projects/my-applicant/learning/02-ai-sdk-and-byok|my-applicant]], [[projects/socioboom/learning/backend/06-ai-and-agents|socioboom agents]], [[projects/nextvibe/learning/backend/04-games-ai|nextvibe games]]) is **AI engineering — calling someone else's model.** That's real work, and it's the Software column. The ML column has the vault's biggest theory-to-practice gap by a wide margin.

### The next three moves, in order

1. **Finish one build-your-own project.** Your own Redis. It closes the Rank III software gate and is the prerequisite for everything above it. Highest-leverage single thing in this document.
2. **Do the tcpdump exercise** in [[foundations/networking/README|the networking README]]. Thirty minutes, and it converts a course you read into a layer you've seen.
3. **Publish one blog draft.** `blog-drafts/four-bugs-that-shipped.md` is closest to ready. Rank VI compounds earlier than people expect.

> Reading this document is Rank 0. Go build something.

## Related
- [[project-ideas|Project Ideas]] — the reps behind every gate here
- [[README|Vault README]] — the map
- [[INTERVIEW|Interview Prep Index]] — the "could you teach it?" test, per domain
- [[problem-solving/thinking-patterns|Thinking Patterns]] — the meta-skill under all of it
