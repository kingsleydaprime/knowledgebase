# SWE 102 — AI Engineering

**Status:** next — starts the Monday after [[learning/swe-101/index|SWE 101]]'s finish line is met · **Length:** 6 weeks
**How every week works:** the four lanes, the rotation and the rules are in [[learning/swe-101/index#How every week works|SWE 101]] and don't change. Notebook sections are numbered 102.1–102.6.
**Then:** [[learning/swe-103/index|SWE 103 — systems and interviews]].

---

## Why this course

SWE 101 left you with a deployed, tested flagship. This course gives it the thing that makes the target profile real: **an AI feature you can prove works**, with an evals harness and numbers you can quote. Almost nobody applying to junior AI roles has that. It's the single highest-leverage gap left once graphs are under control.

## Course finish line

- [ ] The flagship's AI feature returns validated, structured output
- [ ] **A golden set of at least 20 cases, a scorer, and an evals run in CI** that fails when a prompt change makes results worse
- [ ] Numbers you can quote: pass rate, cost per request, p95 latency
- [ ] One write-up of the AI feature: what it does, how it's evaluated, one failure you found through evals
- [ ] Linked lists, stacks, intervals and dynamic programming: about 30 problems logged, at least 20 cold
- [ ] Applications every Friday — 10 a week from here on — and every interview debriefed the same day

**Week 1's first job is the audit** of this course's lessons — K / H / D, as in SWE 101.

## The six weeks

### Week 1 — How models actually behave

- **DSA — arrays, hashing, prefix sums:** 004 group anagrams · 005 top K frequent elements · 007 product of array except self · 009 longest consecutive sequence. Refresh: [[dsa/04-patterns/01-prefix-sum|prefix sum]].
- **Learn (core):** [[ai-ml/03-ai-engineer/02-how-llms-work|how LLMs work]] · [[ai-ml/03-ai-engineer/04-calling-models|calling models]]
- **Learn (optional):** [[ai-ml/03-ai-engineer/01-the-ai-engineer-role|the AI engineer role]] · [[ai-ml/03-ai-engineer/03-the-model-landscape|the model landscape]]
- **Build:** the AI feature's skeleton — one model call through a port, streaming if the UI needs it, with a fake model adapter for tests.
- **Apply:** Friday hour, 10 a week.
- **By Sunday:** closed-book — *why does a model hallucinate, mechanically?*

### Week 2 — Structure and prompts

- **DSA — linked lists:** 037 reorder list · 038 remove Nth node from end · 041 linked list cycle · 042 find the duplicate number · 043 LRU cache. Refresh: [[dsa/04-patterns/04-fast-slow-pointers|fast and slow pointers]] · [[dsa/04-patterns/05-linked-list-reversal|linked list reversal]].
- **Learn (core):** [[ai-ml/03-ai-engineer/11-structured-output|structured output]] · [[ai-ml/03-ai-engineer/05-prompt-engineering|prompt engineering]]
- **Learn (optional):** [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG and embeddings]] — **core instead** if the flagship's feature retrieves documents
- **Build:** the feature returns schema-validated output, and the prompt lives in version control as a file, not a string in the code.
- **Apply:** Friday hour.
- **By Sunday:** the AI feature works end to end in production.

### Week 3 — Evals ⭐

- **DSA — stacks:** 021 valid parentheses · 024 generate parentheses · 025 daily temperatures · 026 car fleet · 027 largest rectangle in histogram. Refresh: [[dsa/04-patterns/06-monotonic-stack|monotonic stack]].
- **Learn (core):** [[ai-ml/03-ai-engineer/12-evals|evals]] · [[ai-ml/03-ai-engineer/19-practice-exercises|AI engineering practice exercises]]
- **Build:** write the golden set — at least 20 real inputs with what a good answer looks like — **before** building any harness. Include the cases you expect it to fail.
- **Apply:** Friday hour.
- **By Sunday:** the golden set exists, and a scorer runs over it locally and prints a pass rate.

### Week 4 — Evals in CI, and production behaviour

- **DSA — intervals and greedy:** 128 partition labels · 130 insert interval · 131 merge intervals · 132 non-overlapping intervals · 134 meeting rooms II. Refresh: [[dsa/04-patterns/08-overlapping-intervals|overlapping intervals]].
- **Learn (core):** [[ai-ml/03-ai-engineer/13-reliability-and-plumbing|reliability and plumbing]] · [[ai-ml/03-ai-engineer/14-cost-caching-and-latency|cost, caching and latency]]
- **Learn (optional):** [[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]]
- **Build:** the evals run in CI and fail the build below a threshold. Add timeouts, a retry with backoff, and per-request cost and latency logging.
- **Apply:** Friday hour.
- **By Sunday:** **the evals harness runs in CI, with numbers you can quote.**

### Week 5 — Tools, agents, and when not to use them

- **DSA — dynamic programming I (one dimension):** 101 house robber · 102 house robber II · 106 coin change · 108 word break · 109 longest increasing subsequence. Refresh: [[dsa/04-patterns/15-dynamic-programming|dynamic programming]].
- **Learn (core):** [[ai-ml/03-ai-engineer/07-tools-and-mcp|tools and MCP]] · [[ai-ml/03-ai-engineer/08-agents|agents]]
- **Learn (optional):** [[ai-ml/03-ai-engineer/09-multimodal|multimodal]]
- **Build:** only if the feature genuinely needs a tool call — otherwise, use the week to raise the eval pass rate and record what changed it.
- **Apply:** Friday hour.
- **By Sunday:** closed-book — *when is an agent the wrong architecture?*

### Week 6 — Safety, the write-up, and a timed mock

- **DSA — dynamic programming II (two dimensions), then a mock:** 111 unique paths · 112 longest common subsequence · 114 coin change II. Then one timed mock: two unseen mediums, 45 minutes each.
- **Learn (core):** [[ai-ml/03-ai-engineer/10-safety-and-production|safety and production]] — prompt injection and PII
- **Build:** the AI feature write-up, with the evals numbers and one failure the evals caught.
- **Apply:** Friday hour, with the write-up linked.
- **By Sunday:** every box in the finish line is ticked, or has a date. **SWE 103 starts the following Monday.**

## Related

- [[learning/swe-101/index|SWE 101]] — the series overview and the weekly rules
- [[ai-ml/03-ai-engineer/index|The AI engineer track]] — the full set of lessons this course draws from
- [[learning/swe-101/06-lesson-quality|Lesson quality]]
