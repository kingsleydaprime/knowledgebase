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
| **Depth** | knowing the layer *below* the one you work at | [[foundations/networking/README\|networking]], [[foundations/os/fundamentals\|OS]], [[architecture/04-distributed-systems/README\|distributed systems]], [[foundations/dsa/README\|DSA]] |
| **Debugging** | narrowing the search space instead of guessing | [[foundations/networking/16-debugging-networks\|bisecting layers]], reading errors properly, profilers |
| **Shipping** | finishing, deploying, operating, being on call for it | [[project-ideas\|projects]], [[devops/README\|devops]] |
| **Communication** | making others faster — writing, reviewing, teaching | [[research/README\|research & writing]], [[concepts/04-best-practices/02-pr-structure\|PR structure]], this vault |

**Three of those are not code.** That's the part the movie leaves out, and it's the part most engineers skip for a decade.

### The rules of the path

1. **Reading is not a rank.** Every gate below is *demonstrable* — something you can do in front of someone, or a thing that exists and runs. Notes are the map; [[project-ideas|projects]] are the territory.
2. **Depth beats breadth, until it doesn't.** Ranks I–III are deliberately narrow. Go deep enough to hit bedrock in *one* area before spreading out — the experience of having gone all the way down once is what makes you unafraid to do it again.
3. **You can't skip the boring rank.** Rank II is unglamorous and it's the one that separates people. Everyone wants to build a Raft KV store; almost nobody wants to learn what `CLOSE_WAIT` means.
4. **The gate is "could you teach it?"** not "have you read it?" The [[foundations/networking/interview/README|interview banks]] exist for exactly this — cover the answer, say it out loud, compare.

---

## 🥉 RANK I — THE BUILDER
*"It works on my machine, and I know why."*

The baseline. You can take an idea to a running thing without help.

**Gates:**
- [ ] Ship a full-stack app **to a real domain over HTTPS** — not localhost, not a screenshot. → [[devops/04-vps/vps-setup|VPS]], [[devops/02-docker/README|Docker]]
- [ ] Use git like a professional: feature branches, [[git/git-reference|conventional commits]], an interactive rebase you didn't panic during, and a merge conflict you resolved by *reading* rather than picking a side
- [ ] Write a test suite that has actually caught a regression → [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]]
- [ ] Read a stack trace top-to-bottom and fix the root cause, **not the symptom**
- [ ] Explain what happens between typing a URL and seeing a page → [[foundations/networking/01-what-a-network-is|note 01]]

**Course load:** [[backend/README|concepts/]] · [[foundations/dsa/README|dsa/]] 01–04 · [[git/git-reference|git]] · [[devops/01-linux/README|linux]] 01–12

**Capstone:** any 🟢 in [[project-ideas|project-ideas]], deployed and written up.

**You've arrived when:** you stop googling error messages verbatim and start reading them.

---

## 🥈 RANK II — THE DIAGNOSTICIAN
*"Everyone else is guessing. You are bisecting."*

**The rank that actually separates people, and the least glamorous.** Most engineers plateau here forever because the material is unsexy and the payoff is invisible until the day it isn't.

**Gates:**
- [ ] Debug a problem **you cannot reproduce locally**, using logs and metrics alone
- [ ] `tcpdump` a request and **find the three-way handshake with your own eyes** → [[foundations/networking/06-tcp-connection-lifecycle|TCP lifecycle]]
- [ ] Know, without looking it up, what a pile of `CLOSE_WAIT` sockets means about your code → [[foundations/networking/16-debugging-networks|debugging]]
- [ ] Explain the difference between "connection refused" and a hang, and why it tells you where to look
- [ ] Profile something slow and find the *actual* bottleneck — including being willing to discover it's the database, not your code
- [ ] Read a flame graph. Read a GC log. Read an `EXPLAIN` plan. → [[databases/sql-reference|SQL]]
- [ ] Write a postmortem with a real root cause and no blame (your `blog-drafts/four-bugs-that-shipped.md` is one)

**Course load:** [[foundations/networking/README|networking/]] **all of it** · [[foundations/os/fundamentals|os/]] · [[devops/10-observability/README|observability]] · [[databases/database-design-reference|databases]]

**Capstone:** instrument a real app with metrics + traces, then **deliberately break it** and diagnose it from the dashboards alone.

**You've arrived when:** someone else's bug becomes interesting rather than annoying.

---

## 🥇 RANK III — THE SYSTEMS THINKER
*"You've built the thing you used to import."*

Depth becomes bedrock. You stop treating infrastructure as magic because you've written a bad version of it yourself.

**Gates:**
- [ ] **Build one thing from scratch that you previously only used.** Non-negotiable, pick one:
  - Your own Redis (start here — most approachable) → [[project-ideas|project-ideas]]
  - Your own git
  - An HTTP/1.1 server from raw sockets → [[foundations/networking/09-sockets-and-the-network-api|sockets]]
  - A B-tree or LSM storage engine
- [ ] Write concurrent code and **prove** it correct — where "prove" means a stress test that actually fails on a bad version → [[languages/01-java/02-jvm-and-concurrency/README|concurrency]]
- [ ] Explain memory: stack vs heap, cache lines, why the memory model exists → [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM internals]]
- [ ] Design a system on a whiteboard with explicit tradeoffs and named failure modes → [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|system design]]
- [ ] Reason about consistency without saying "eventually consistent" as though it settles anything → [[architecture/04-distributed-systems/04-consistency-models|consistency models]]

**Course load:** [[architecture/README|architecture/]] 01–03 · [[languages/01-java/README|java/]] jvm-and-concurrency · [[foundations/dsa/README|dsa/]] 05–06

**Capstone:** the 🔴 ⭐ **in-memory order book + matching engine**, benchmarked with JMH, p99 measured and explained. Or your own Redis with persistence.

**You've arrived when:** you read a framework's source when the docs are ambiguous, and it's not scary.

---

## 💎 RANK IV — THE DISTRIBUTED MIND
*"You have internalised that the network will betray you."*

Where most senior engineers stop, and where the genuinely hard problems start.

**Gates:**
- [ ] **Implement Raft.** Leader election, log replication, safety. Then a KV store on it. Then kill nodes and partition the network while it runs. → [[architecture/04-distributed-systems/08-raft-in-depth|Raft in depth]]
- [ ] Explain why exactly-once delivery is impossible, and what you build instead → [[architecture/04-distributed-systems/10-distributed-transactions|idempotency]]
- [ ] Explain CAP correctly — including why most people quoting it are wrong → [[architecture/04-distributed-systems/02-theoretical-limits|PACELC]]
- [ ] Debug a p99 problem that turns out to be transport-layer → [[foundations/networking/15-network-performance|tail latency]], incast, RTO
- [ ] Run something in production that **other people depend on**, and carry the pager for it
- [ ] Design for failure explicitly: circuit breakers, backpressure, graceful degradation → [[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]]

**Course load:** [[architecture/04-distributed-systems/README|distributed systems]] **all of it** · [[devops/05-orchestration/README|k8s]] · [[devops/11-delivery-and-advanced/README|delivery]]

**Capstone:** the Raft KV store, tested against partitions and crashes. Write up what surprised you — that write-up is worth more than the code.

**You've arrived when:** "just add a retry" makes you ask what happens if the first one succeeded.

---

## 🔮 RANK V — THE SPECIALIST
*"You are the person who is called."*

Depth in **one** domain deep enough that you're the escalation point. Pick a lane — this rank is explicitly not about breadth.

**Choose your path:**

**⚡ Low-latency / systems** *(the current target)*
- [ ] Sub-microsecond p99 on a hot path, measured, with the number defended
- [ ] Zero-allocation code on the hot path, verified by profiler not by vibes
- [ ] Explain mechanical sympathy: cache lines, false sharing, branch prediction, NUMA
- [ ] Read the [[foundations/networking/08-congestion-control|congestion control]] and [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|GC]] notes and know which one your latency spike came from

**🤖 AI engineering**
- [ ] Ship an agent with a real eval suite, not vibes → [[ai-ml/03-ai-engineer/README|ai-engineer]]
- [ ] Red-team your own system for prompt injection and document the mitigations
- [ ] Defend a model/cost/latency tradeoff with numbers

**🔐 Security**
- [ ] Find a real vulnerability in a real system, with authorisation → [[cybersecurity/README|cybersecurity]]
- [ ] Build the defensive side too — detection, not just exploitation → [[cybersecurity/07-security-operations/README|secops]]

**☁️ Infrastructure**
- [ ] Run a multi-region system and survive losing a region
- [ ] Reduce a cloud bill by 50% with a written explanation of *why* it was high

**You've arrived when:** people in your specialty ask *you*, and your answer starts with a question.

---

## 👑 RANK VI — THE FORCE MULTIPLIER
*"Your impact stopped being measured in code."*

The rank almost nobody plans for. It's not management — it's the point where **the constraint on your impact stops being your own throughput.**

**Gates:**
- [ ] Write something technical that **changes how other people work** → your blog drafts, [[research/09-scientific-writing-craft|writing craft]]
- [ ] Review code so that the author is better afterwards, not just the code → [[concepts/04-best-practices/02-pr-structure|PR structure]]
- [ ] Make a decision under genuine uncertainty, write down the reasoning, and **be publicly wrong about one** → `DECISIONS.md`
- [ ] Mentor someone from Rank I to Rank II
- [ ] Say no to a technically interesting project for a correct business reason
- [ ] Teach the hard thing simply — if you can't do the "kid version first" of it, you don't understand it → the convention every [[foundations/networking/README|networking]] and [[architecture/04-distributed-systems/README|dist-sys]] note follows

**You've arrived when:** your best week involved very little code and you're at peace with that.

---

## 🕶️ RANK VII — PRIMETECHIE
*"That one guy."*

Not a checklist. An emergent property of the six ranks below it, plus years. But it looks like this:

- **You go down a layer without flinching.** Kernel source, RFC, disassembly — you don't know it, but you know how to find out, and you're not afraid.
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
| **I — Builder** | ✅ **Cleared** | 12 projects, real deployments, git fluency |
| **II — Diagnostician** | 🟡 **In progress** | Networking course now exists — *do* the tcpdump exercise. Observability is still reference-only, not run. |
| **III — Systems Thinker** | 🟡 **Partial** | Theory is deep (architecture + JVM). **No build-your-own project finished yet** — this is the single biggest gap in the vault. |
| **IV — Distributed Mind** | 🔵 **Theory only** | [[architecture/04-distributed-systems/README\|15 notes]] read, Raft unimplemented. Theory without reps. |
| **V — Specialist** | 🔵 **Aiming** | Low-latency Java is the stated target; the order-book project is the proof |
| **VI — Force Multiplier** | 🟡 **Started** | This vault *is* Rank VI work. Blog drafts written but unpublished — publish one. |
| **VII** | 🕶️ | see you there |

### The next three moves, in order

1. **Finish one build-your-own project.** Your own Redis. It closes the Rank III gap and is the prerequisite for everything above it. This is the highest-leverage single thing in this entire document.
2. **Do the tcpdump exercise** in [[foundations/networking/README|the networking README]]. Thirty minutes, and it converts a course you read into a layer you've seen.
3. **Publish one blog draft.** `blog-drafts/four-bugs-that-shipped.md` is closest to ready. Rank VI compounds earlier than people expect.

> Reading this document is Rank 0. Go build something.

## Related
- [[project-ideas|Project Ideas]] — the reps behind every gate here
- [[README|Vault README]] — the map
- [[problem-solving/thinking-patterns|Thinking Patterns]] — the meta-skill under all of it
