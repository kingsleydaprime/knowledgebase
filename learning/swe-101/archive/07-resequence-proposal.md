# Proposal — Re-sequencing the Scheme of Work

> **Archived 2026-10-01.** Superseded by the three-course series — [[learning/swe-101/index|SWE 101]] → [[learning/swe-102/index|SWE 102]] → [[learning/swe-103/index|SWE 103]]. Kept for the reasoning it records; it is no longer the plan.

> **Status: adopted in modified form, 2026-10-01.** Rather than one re-ordered 26-week scheme, the two tracks were merged into weekly lanes and split into three short courses. The reasoning below still holds.

## Why change it

The scheme was re-ordered once already, around "interview relevance". Reading it against [[learning/swe-101/archive/01-hire-track|Track A]] week by week shows it still works against the flagship, and it no longer fits its own time budget.

1. **The flagship needs things months before the scheme teaches them.**

| The flagship needs | By (Track A) | The scheme teaches it in |
|---|---|---|
| Tests running in CI | week 3–4 | week 24 |
| An AI feature working | week 7–8 | weeks 20–22 |
| **Evals harness** | **week 9–10** | **week 23** |
| Hardening: errors, rate limits, cost and latency numbers | week 11 | weeks 19, 23 |
| Observability | week 12 | week 24 |
| System design reps, one per fortnight | from week 12 | weeks 5–8 (then nothing for 4 months) |

2. **The time budget doesn't fit.** Track B has 2–4 hours a week. Weeks 2–4 now link about 33,000 words of lessons, each with a practice task of 1–3 hours, and the notebook method asks for a full page per topic, across about 148 topics.

3. **Depth goes where the target role doesn't ask.** Four weeks of networking (link layer, subnetting, congestion control, QUIC), four of distributed systems (Paxos, Raft), and database internals down to LSM trees. The target is *a TypeScript full-stack engineer who ships AI product features*.

4. **Weeks 2 and 4 overlap.** Both send you to the same five structuring-a-backend lessons.

5. **The two tracks disagree on the DSA order.** The scheme follows the vault's 15 pattern lessons. The hire track lists a different order, including greedy, tries and bit manipulation, none of which has a pattern lesson here.

## The principles

- **Learn it the week before you build it.** For weeks 1–12, Track B follows the flagship's milestones.
- **Two core lessons a week, plus one practice task.** Everything else in a week is optional, and the [[learning/swe-101/archive/05-week-1-audit|audit]] decides: **K** → skip, **H** → core only, **D** → core plus optional.
- **Practice targets the flagship** wherever a lesson allows it, so studying and building are the same hours.
- **Notebook pages for core topics only.** Optional topics get a line in the index, not a page.
- **Depth the role rarely asks for moves to the CS spine** (week 27+), not out of the vault.
- **Finish in 26 weeks, not 30**, leaving two buffer weeks before Track A ends at week 28. School will eat some weeks; the plan should expect that.

## The proposed order

**Core** is what the week requires. **Optional** is read only if the audit says D, or if there's time.

### Weeks 1–12 · Build the flagship, learning each piece the week before

| Wk | Block | Core | Optional | Flagship (Track A) | By Sunday |
|---|---|---|---|---|---|
| 1 | Introduction & the audit | [[software-engineering/01-what-software-engineering-is\|what SWE is]] · [[software-engineering/02-the-software-development-lifecycle\|SDLC]] | [[software-engineering/03-the-engineering-roles\|roles]] | Pick the flagship | The audit, done honestly |
| 2 | Design principles | [[concepts/04-best-practices/08-coupling-and-cohesion/index\|coupling & cohesion]] · [[concepts/04-best-practices/05-solid-principles/index\|SOLID]] | [[concepts/04-best-practices/01-clean-code/index\|clean code]] | — | Run the coupling tool on the flagship; fix one finding |
| 3 | Structuring a codebase | [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/index\|layers]] · [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index\|layer vs feature]] | [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture/index\|hexagonal]] · [[backend/03-structuring-a-backend/05-modular-monolith-to-services/index\|modular monolith]] | w3–4: skeleton deployed, CI green | Flagship's folder structure decided, with a boundary lint rule |
| 4 | Wiring & testing | [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index\|DI & wiring]] · [[concepts/04-best-practices/04-testing-fundamentals/index\|testing fundamentals]] | [[backend/07-practices/02-testing-a-backend\|testing a backend]] | w3–4: CI green | Flagship has a composition root and its first real tests in CI |
| 5 | Patterns | [[concepts/03-design-patterns/03-behavioral-patterns/index\|behavioural]] · [[concepts/03-design-patterns/02-structural-patterns/index\|structural]] | [[concepts/03-design-patterns/01-creational-patterns/index\|creational]] | w5–6: core feature | One pattern applied in the flagship's core feature, with a sentence on why |
| 6 | LLMs: the ground floor | [[ai-ml/03-ai-engineer/02-how-llms-work/index\|how LLMs work]] · [[ai-ml/03-ai-engineer/04-calling-models/index\|calling models]] | [[ai-ml/03-ai-engineer/01-the-ai-engineer-role\|the role]] · [[ai-ml/03-ai-engineer/03-the-model-landscape\|model landscape]] | w5–6: core feature | Closed-book: *why does a model hallucinate, mechanically?* |
| 7 | Prompting, structure, retrieval | [[ai-ml/03-ai-engineer/11-structured-output/index\|structured output]] · [[ai-ml/03-ai-engineer/05-prompt-engineering/index\|prompt engineering]] | [[ai-ml/03-ai-engineer/06-rag-and-embeddings/index\|RAG]] (core if the flagship retrieves) | w7–8: AI feature · **applications start** | The flagship's AI feature returns validated, structured output |
| 8 | **Evals** ⭐ | [[ai-ml/03-ai-engineer/12-evals/index\|evals]] · [[ai-ml/03-ai-engineer/19-practice-exercises\|AI practice exercises]] | — | w9–10: evals next week | A golden set of 20+ cases for the flagship, written *before* building the harness |
| 9 | LLMs in production | [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index\|reliability]] · [[ai-ml/03-ai-engineer/14-cost-caching-and-latency/index\|cost & latency]] | [[ai-ml/03-ai-engineer/10-safety-and-production/index\|safety]] · [[architecture/03-architectural-patterns/02-resilience-patterns/index\|resilience patterns]] | w9–10: evals in CI | **Evals harness running in CI, with numbers you can quote** |
| 10 | Tools and agents | [[ai-ml/03-ai-engineer/07-tools-and-mcp/index\|tools & MCP]] · [[ai-ml/03-ai-engineer/08-agents/index\|agents]] | [[ai-ml/03-ai-engineer/09-multimodal/index\|multimodal]] | w9–10 | Closed-book: *when is an agent the wrong architecture?* |
| 11 | Hardening | [[backend/07-practices/01-backend-best-practices/index\|backend practices]] (validation, errors, rate limits, idempotency) · [[devops/10-observability/01-observability-fundamentals/index\|observability]] | [[devops/10-observability/02-the-observability-stack\|the stack]] | w11: hardening | Flagship answers "is it up, is it fast, what does it cost per request" |
| 12 | Securing what you shipped | [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index\|input & output]] · [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/index\|headers & SOP]] (XSS, CSRF) | [[ai-ml/03-ai-engineer/10-safety-and-production/index\|prompt injection]] · [[devops/09-secret-management/01-secret-management\|secrets]] | w12: ship + write-up | Threat model: the flagship's top five risks, and what you did about each |

### Weeks 13–16 · System design, as the interview reps begin

Track A starts one system-design rep per fortnight from week 12. This block feeds them.

| Wk | Block | Core | Optional | By Sunday |
|---|---|---|---|---|
| 13 | Approach & scale | [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index\|the approach]] · [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index\|scalability]] | [[architecture/interview/01-system-design-round\|the round]] | **URL shortener**, 45 minutes, out loud |
| 14 | Availability & caching | [[architecture/02-building-blocks/02-caching\|caching]] · [[architecture/02-building-blocks/01-load-balancing-and-proxies\|load balancing]] | [[architecture/01-system-design-fundamentals/03-availability-and-reliability\|availability]] · [[architecture/01-system-design-fundamentals/04-cap-and-consistency\|CAP]] | — (rep on alternate weeks) |
| 15 | Data, messaging, communication | [[architecture/02-building-blocks/04-messaging-and-async\|messaging]] · [[architecture/02-building-blocks/05-communication\|communication]] | [[architecture/02-building-blocks/03-databases-at-scale\|databases at scale]] | **Notification system** |
| 16 | Architectural patterns | [[architecture/03-architectural-patterns/01-monolith-microservices-serverless\|monolith vs microservices]] · [[architecture/03-architectural-patterns/05-transactional-outbox/index\|transactional outbox]] | [[architecture/03-architectural-patterns/03-data-and-integration-patterns\|data & integration]] · [[architecture/03-architectural-patterns/04-microservices-patterns\|microservices patterns]] | **Payment system** — from your nextvibe ledger experience |

### Weeks 17–25 · Depth the interviews probe

| Wk | Block | Core | Moves to optional or the spine |
|---|---|---|---|
| 17 | Databases I — querying well | [[databases/04-b-trees-and-indexes\|B-trees & indexes]] · [[databases/07-join-algorithms-and-the-optimiser\|EXPLAIN ANALYZE & the optimiser]] | [[databases/01-what-a-database-is\|what a DB is]] · [[databases/02-the-relational-model\|relational model]] (audit-dependent) · [[databases/06-the-query-pipeline\|query pipeline]] |
| 18 | Databases II — changing data safely | [[databases/08-transactions-and-acid\|transactions]] · [[databases/09-mvcc-and-concurrency-control\|isolation & MVCC]] | [[databases/12-operating-a-database\|operating]] · [[databases/11-replication-and-scaling\|replication]] · spine: [[databases/03-storage-and-page-layout\|page layout]], [[databases/05-lsm-trees\|LSM trees]], [[databases/10-durability-and-recovery\|durability]] |
| 19 | The web, end to end | [[networking/10-dns-in-depth\|DNS]] · [[networking/11-http-evolution\|HTTP]] · [[networking/12-tls-and-transport-security\|TLS]] | **By Sunday:** "what happens when I type google.com", one page from memory |
| 20 | Transport & debugging | [[networking/06-tcp-connection-lifecycle\|TCP lifecycle]] · [[networking/16-debugging-networks\|debugging networks]] | [[networking/15-network-performance\|performance]] · spine: [[networking/02-the-link-layer\|link layer]], [[networking/03-ip-addressing-and-subnetting\|subnetting]], [[networking/04-routing\|routing]], [[networking/08-congestion-control\|congestion control]], [[networking/13-quic-and-modern-transport\|QUIC]], [[networking/14-nat-firewalls-and-middleboxes\|NAT]] |
| 21 | The request path & the event loop | [[backend/01-foundations/03-the-request-lifecycle\|request lifecycle]] · [[backend/01-foundations/04-runtime-and-concurrency-models\|runtime & the event loop]] | [[os/06-concurrency-primitives\|locks & races]] · [[os/02-processes-and-threads\|processes & threads]] |
| 22 | Identity & cryptography | [[backend/05-auth/01-authentication-flows\|sessions vs JWT]] · [[backend/05-auth/03-oauth-provider-integrations\|OAuth & OIDC]] | [[cybersecurity/05-cryptography/03-hashing-and-integrity\|hashing]] · [[cybersecurity/05-cryptography/05-digital-signatures-and-pki\|signatures & PKI]] · [[backend/05-auth/02-authorization\|authorisation]] |
| 23 | Distributed systems I | [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard\|why it's hard]] · [[architecture/04-distributed-systems/04-consistency-models\|consistency models]] | [[architecture/04-distributed-systems/03-time-and-ordering\|time & ordering]] |
| 24 | Distributed systems II | [[architecture/04-distributed-systems/05-replication\|replication]] · [[architecture/04-distributed-systems/13-partitioning\|partitioning]] | [[architecture/04-distributed-systems/10-distributed-transactions\|distributed transactions]] · spine: [[architecture/04-distributed-systems/07-consensus-and-paxos\|consensus]], [[architecture/04-distributed-systems/08-raft-in-depth\|Raft]] |
| 25 | Delivery gap-fill | [[devops/06-ci-cd/09-cd-and-deployment\|CD & deployment]] · [[devops/02-docker/04-multi-stage-builds\|multi-stage Docker]] | everything else in DevOps — you run it already |

### Week 26 · Review and mock loops

Unchanged from the current week 30: two system-design mocks, two timed coding mocks, the project story at three lengths, six STAR stories, and the re-audit.

### Weeks 27–28 · Buffer

Nothing scheduled. This is where the weeks school took get made up. If none were lost, start the spine early.

### Week 29+ · The CS spine

The current week 31+ list, **plus** everything marked "spine" above.

## What this costs

Honestly stated, so you can disagree with it:

- **Less networking and distributed-systems depth before the job hunt.** Link layer, subnetting, congestion control, QUIC, Paxos and Raft come after. A role that asks about them in depth is probably not a junior TypeScript or AI role.
- **System design reps start in week 13, not week 5.** But under the current scheme, the design exercises finish in week 8, while Track A's design reps start in week 12, so they're four months stale by then.
- **Fewer notebook pages.** Optional topics stop getting a page.

## What it means for lesson conversion

The converted Software design block (13 lessons) is still used, in weeks 2–5. The next block to convert becomes **weeks 4–12**: testing fundamentals, testing a backend, the AI-engineering lessons 01–14, backend practices, observability, and the two web-security lessons — about 22 lessons, not the architecture block that was next.

## Open questions — your call

1. **Which project is the flagship, and does it already have an LLM feature?** Weeks 6–10 assume the AI feature is built in weeks 7–8. If it's my-applicant or nextvibe with AI already working, weeks 6–7 shrink and evals can come a week earlier.
2. **Is moving the networking and distributed-systems depth to the spine acceptable?** It's the biggest cut. If you want one of them kept, say which, and something else moves.
3. **Which DSA order do you want to follow?** The vault's 15 pattern lessons (the scheme's order), or the hire track's list? The hire track's list includes greedy, tries and bit manipulation, which have no lessons here — choosing it means writing three.
4. **Is "two core lessons plus one practice task" the right weekly size?** It's sized for 2–4 hours. If you have more in practice, it can be three.

## Related

- [[learning/swe-101/archive/04-scheme-of-work|The current scheme of work]]
- [[learning/swe-101/archive/01-hire-track|Track A — Hire]] · [[learning/swe-101/archive/02-foundation-track|Track B — Foundation]]
- [[learning/swe-101/06-lesson-quality|Lesson quality]] — conversion progress
