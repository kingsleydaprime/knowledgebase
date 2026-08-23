# Requirements

> **[Beginner → Intermediate]** · Turning "we want it safer" into something buildable and testable — and why this is where most projects are actually lost.

**Requirements defects are the most expensive class of defect there is**, because everything downstream is competent work aimed at the wrong target. Every survey of failed projects puts requirements at or near the top of the causes.

## The hierarchy

Requirements flow down, each level traceable to the one above:

```
Stakeholder needs        "I want to arrive on time"
        ↓
System requirements      "The vehicle shall reach 100 km/h in ≤ 8.0 s"
        ↓
Subsystem requirements   "The motor shall deliver ≥ 250 Nm from 0–3000 rpm"
        ↓
Component requirements   "The controller shall switch at ≥ 20 kHz"
```

**Every requirement must trace upward to a need.** One with no parent is somebody's preference that got written down, and it will cost real money to satisfy. Tracing down matters too: a need with no requirement beneath it is a need nobody is building.

## Functional and non-functional

**Functional** — what it does. *"The system shall log every transaction."*

**Non-functional** — how well. Performance, reliability, availability, safety, security, usability, maintainability, cost, weight, power.

**The non-functional ones determine the architecture.** "Handles 100 users" and "handles 100 million" are the same functional requirement and completely different systems. Software people learn this as *"you can't add scalability later"* → [[architecture/01-system-design-fundamentals/README|system design]].

They are also the ones most often left vague, which is how you get an argument at acceptance about whether "fast" was met.

## What makes a requirement good

The INCOSE criteria, with the two that do the most work first:

**Verifiable.** There must exist a test whose result is unambiguous. **This one criterion kills most bad requirements**, because applying it forces every other quality:

> ✗ "The system shall be user-friendly."
> ✓ "A first-time user shall complete checkout in ≤ 3 minutes without assistance, in ≥ 90% of trials (n ≥ 20)."

> ✗ "The system shall be fast."
> ✓ "The system shall return search results within 200 ms at the 95th percentile under a load of 500 concurrent users."

**Unambiguous.** One reading only. *"The system shall process requests quickly and store them"* — quickly by whose measure, and does "them" mean requests or results?

Then: **necessary** (traces to a need), **singular** (one requirement per statement — "and" is usually two requirements, and you'll pass one and fail the other), **feasible**, **complete** (no TBDs at baseline), **consistent** (doesn't contradict another).

**The language convention is load-bearing:**

- **shall** — a binding requirement, verifiable, contractual
- **should** — a goal
- **will** — a statement of fact or intent
- **may** — an option

Mixing these in a contract is how you end up arguing about whether something was mandatory.

## Why they fail

**Stakeholders don't know what they want**, and cannot until they see something. This is genuinely true, not laziness — and it is the entire argument for prototypes, mockups and iteration, even in a heavyweight process.

**The stated need isn't the real need.** *"We need a faster horse."* The technique is to keep asking *why* until you reach the underlying goal, because that's the level where alternatives exist.

**Implementation smuggled in as requirement.** *"The system shall use a PostgreSQL database"* is a design decision wearing a requirement's clothes. It removes an option you may need later. The requirement is about durability and query characteristics; the database is a solution → [[foundations/systems-engineering/05-trade-studies|trade studies]].

**Requirements churn.** Change is inevitable; *uncontrolled* change is what kills projects. Hence a baseline, and a change process that makes the cost of each change visible before it's accepted.

**The unstated assumption.** Ariane 5 → [[foundations/systems-engineering/01-what-systems-engineering-is|note 01]]. The requirement was met; the assumption about the flight profile was never written down, so nobody rechecked it.

## Eliciting them

Requirements are *elicited*, not collected — they mostly don't exist in usable form until you extract them:

- **Interviews and workshops** — and ask *why*, repeatedly
- **Observation** — watch people do the work. **What people say they do and what they do differ**, reliably
- **Prototypes** — the fastest way to discover what someone actually wants is to show them something wrong
- **Use cases and scenarios** — walk through the system's life, including the bad days
- **Analysis of the existing system** — what it does, what people work around
- **Regulation and standards** — non-negotiable, and expensive to discover late

**Include the abnormal cases.** Most requirements sets describe the happy path in detail and failure in a sentence. Then the system meets every requirement and is unusable when something breaks. Ask: what should happen when the input is malformed, the network is down, power is lost mid-operation, or the operator does the wrong thing?

## Traceability

A matrix linking need → requirement → design element → test:

| Need | Requirement | Design | Verification |
|---|---|---|---|
| N-03 arrive on time | SYS-014 0–100 in ≤8.0 s | Motor spec MT-2 | TC-114 track test |

Bureaucratic-looking, and it answers three questions nothing else can:

1. **Is every need being built?** (gaps)
2. **Why does this component exist?** (orphans — genuinely, this finds work nobody needs)
3. **If this requirement changes, what breaks?** (impact)

**In software this is what a well-kept issue tracker linking ticket → commit → test approximates**, and it's why "which requirement does this PR satisfy" is a reasonable question rather than bureaucracy.

## The software translation

| Systems engineering | Software |
|---|---|
| Stakeholder need | Problem statement / job to be done |
| System requirement | Acceptance criteria |
| Non-functional requirement | **SLO** → [[devops/10-observability/01-observability-fundamentals\|observability]] |
| Requirements baseline | The agreed scope of a milestone |
| Traceability matrix | Issue → commit → test |
| Change control board | Triage |

**The SLO row is the most useful correspondence in this note.** An SLO *is* a verifiable non-functional requirement with an agreed measurement and an agreed consequence for missing it — the same thing the discipline has always asked for, arrived at independently by [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|SRE]].

## Related
- [[foundations/systems-engineering/03-the-lifecycle-and-the-v-model|the V-model]] — requirements' matching verification
- [[foundations/systems-engineering/05-trade-studies|trade studies]] — choosing between solutions
- [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|how to approach system design]] — the software version
- [[foundations/software-engineering/02-the-software-development-lifecycle|the SDLC]]

*Source: [reference] — from the INCOSE Guide to Writing Requirements and the NASA SE Handbook.*
