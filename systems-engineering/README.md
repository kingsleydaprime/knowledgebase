# Systems Engineering

The discipline of making a whole work when no one person understands all of it.

**~8,200 words across 8 notes.** Built August 2026. `[reference]`.

> **The one idea:** **the failures live between the parts.** Every component can meet its specification and the system can still fail — because emergent behaviour, unowned interfaces and unstated assumptions belong to nobody. Systems engineering is the practice of claiming that space.

## Why this exists

**This vault is written by and for a systems engineering student, and had nothing on systems engineering.** Zero hits vault-wide for INCOSE, MBSE, SysML, requirements engineering, or trade studies. `engineering/` meant continuum mechanics and control theory; `architecture/` meant distributed software.

The gap mattered in both directions:

**Toward the degree** — the vault's software material is full of systems-engineering reasoning under other names (coupling, interfaces, non-functional requirements, blast radius, postmortems) and none of it was connected to the vocabulary you're being examined on.

**Toward the software** — the reverse is more interesting. **Requirements traceability, FMEA, fault trees, interface control and margin are genuinely underused in software**, and several are better answers than what software has independently invented. A dependency FMEA takes an afternoon and finds more than most design reviews.

## Reading order

**01–03 are the frame. 04–05 are design. 06–08 are proving it works and what to do about what you missed.**

1. [[foundations/systems-engineering/01-what-systems-engineering-is|What Systems Engineering Is]] — **[Beginner]** — emergence, the three canonical failures, **where lifecycle cost is committed**, and why this isn't senior software engineering
2. [[foundations/systems-engineering/02-requirements|Requirements]] — **[Beginner → Intermediate]** — the hierarchy, what makes one good, **why "verifiable" kills most bad requirements**, traceability, and the SLO correspondence
3. [[foundations/systems-engineering/03-the-lifecycle-and-the-v-model|The Lifecycle and the V-Model]] — **[Beginner → Intermediate]** — the V, verification vs validation, **why the V isn't opposed to agile**, gates, and TRLs
4. [[foundations/systems-engineering/04-architecture-and-interfaces|Architecture and Interfaces]] — **[Intermediate]** — functional vs physical decomposition, the coupling types software doesn't have, **the ICD**, N² diagrams, margin, Conway's Law
5. [[foundations/systems-engineering/05-trade-studies|Trade Studies]] — **[Intermediate]** — the method, **the four ways a scoring matrix lies**, sensitivity analysis, TCO, and ADRs
6. [[foundations/systems-engineering/06-verification-and-validation|Verification and Validation]] — **[Intermediate]** — the four methods, testing like reality, **why coverage isn't confidence**, independence, human factors
7. [[foundations/systems-engineering/07-mbse-and-modelling|MBSE and Modelling]] — **[Intermediate]** — SysML, **why v2's textual notation matters**, digital twins, and the software parallels
8. [[foundations/systems-engineering/08-risk-and-failure-analysis|Risk and Failure Analysis]] — **[Intermediate]** — FMEA, fault trees, common-cause failure, **and normalisation of deviance**

## The things worth carrying

1. **A system has properties none of its parts have.** That's the entire justification for the discipline → [[foundations/systems-engineering/01-what-systems-engineering-is|01]]
2. **~80% of lifecycle cost is committed before ~15% is spent.** The highest-leverage engineering happens before anyone is confident → [[foundations/systems-engineering/01-what-systems-engineering-is|01]]
3. **If you can't write the test, the requirement isn't finished** → [[foundations/systems-engineering/02-requirements|02]] · [[foundations/systems-engineering/03-the-lifecycle-and-the-v-model|03]]
4. **An SLO is a verifiable non-functional requirement.** SRE reinvented the discipline's oldest idea → [[foundations/systems-engineering/02-requirements|02]]
5. **Batch size should follow the cost of being wrong.** Nobody iterates a bridge; nobody writes a requirements baseline for a landing page → [[foundations/systems-engineering/03-the-lifecycle-and-the-v-model|03]]
6. **A gate that has never returned "no" is a status meeting** → [[foundations/systems-engineering/03-the-lifecycle-and-the-v-model|03]]
7. **Do the functional decomposition before the physical one**, or you've chosen a solution before considering alternatives → [[foundations/systems-engineering/04-architecture-and-interfaces|04]]
8. **The interface is owned by neither side, and is harder to change than either implementation** → [[foundations/systems-engineering/04-architecture-and-interfaces|04]]
9. **Margin is the physical form of "don't run at 100% utilisation"** — and it's the first thing cut under schedule pressure → [[foundations/systems-engineering/04-architecture-and-interfaces|04]]
10. **Weight the criteria before you score.** Whoever sets the weights has made the decision → [[foundations/systems-engineering/05-trade-studies|05]]
11. **Report the break-even, not the winner** → [[foundations/systems-engineering/05-trade-studies|05]]
12. **Decide in proportion to reversibility.** Two-way doors deserve an afternoon → [[foundations/systems-engineering/05-trade-studies|05]]
13. **The people who built it share the assumptions that would cause the failure.** That's what independence buys → [[foundations/systems-engineering/06-verification-and-validation|06]]
14. **"The user made a mistake" is almost always a system finding** → [[foundations/systems-engineering/06-verification-and-validation|06]]
15. **Whatever is executable becomes the truth; everything else becomes decoration** → [[foundations/systems-engineering/07-mbse-and-modelling|07]]
16. **The cheapest fix is often "make it fail loudly", not "make it fail less"** → [[foundations/systems-engineering/08-risk-and-failure-analysis|08]]
17. **Redundancy only helps against failures that are genuinely independent** → [[foundations/systems-engineering/08-risk-and-failure-analysis|08]]
18. **Each survival of a known anomaly is treated as evidence of safety.** It isn't → [[foundations/systems-engineering/08-risk-and-failure-analysis|08]]

## The bridge to the rest of the vault

**The systems-engineering habit is everywhere here under other names.** This table is the point of the folder:

| Systems engineering | Already in this vault as |
|---|---|
| Requirements & non-functional properties | [[architecture/01-system-design-fundamentals/README\|system design]] · [[devops/10-observability/01-observability-fundamentals\|SLOs]] |
| The V-model | [[foundations/software-engineering/02-the-software-development-lifecycle\|the SDLC]] |
| Batch size vs cost of error | [[devops/12-sre-and-platform-engineering/01-how-delivery-practice-evolved\|how delivery practice evolved]] |
| Interface control documents | [[backend/02-api-design/README\|API contracts]] |
| Coupling & cohesion | [[concepts/04-best-practices/05-solid-principles\|SOLID]] |
| Margin | [[architecture/01-system-design-fundamentals/03-availability-and-reliability\|headroom, error budgets]] |
| Trade studies | ADRs → [[concepts/04-best-practices/03-documentation-practices\|documentation practices]] |
| FMEA / fault trees | [[cybersecurity/06-attacks-and-threats/README\|threat modelling]] · [[architecture/04-distributed-systems/README\|failure modes]] |
| IV&V, blameless review | [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering\|postmortems]] |
| MBSE | [[devops/07-infrastructure-as-code/01-provisioning-and-terraform\|infrastructure as code]] |
| Multi-disciplinary systems | [[robotics/README\|robotics]] · [[hardware/08-iot-architecture\|IoT]] · [[engineering/README\|engineering]] |

## Note on roadmap.sh

Most domains in this vault are cross-referenced against [roadmap.sh](https://roadmap.sh). **This one can't be — there is no systems-engineering roadmap**, because roadmap.sh covers software and adjacent tech roles only. The nearest neighbours are [software-architect](https://roadmap.sh/software-architect) and [system-design](https://roadmap.sh/system-design), and both are software architecture rather than the INCOSE discipline.

The standards are the substitute, and they're the real syllabus: **INCOSE Systems Engineering Handbook** (the reference), **NASA/SP-2016-6105** (free, excellent, and more readable than INCOSE's), **ISO/IEC/IEEE 15288** (lifecycle processes), and **INCOSE's Guide to Writing Requirements**.

## The honest note

**`[reference]`, and the gap is unusually large here** — this is a discipline whose entire value shows up on projects with many people, many disciplines, long lifecycles and expensive mistakes. **None of those conditions exist in a solo project**, so nothing in this folder has been tested by me against the thing it's for.

**What would close the gap, in rising order of realism:**

1. **Write a requirements spec for something you've already built** — the [[projects/README|IoT bridge PCB]] is the natural candidate, since it's genuinely multi-disciplinary. Then check the built thing against it. **The gap between what you built and what you'd have specified is the lesson**
2. **Run a dependency FMEA on one real service.** Every external dependency × {slow, down, wrong data, stale data, silently no-op}. An afternoon, and it will find something
3. **Draw the N² diagram for a project you know.** Any filled cell you didn't expect is an interface nobody owns
4. **Write three ADRs retrospectively** for decisions already made. Notice which ones you can no longer justify
5. **Coursework is the real gap-closer here**, and it's the one thing you have that this vault doesn't: an actual multi-disciplinary project with a grade attached

**What's missing:** cost estimation and earned value management, configuration management as its own discipline, logistics and supportability, human systems integration at depth, systems-of-systems, agile-systems-engineering hybrids in practice, and the entire contractual/programme-management side, which is a large part of the real job.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Related
- [[foundations/software-engineering/README|software engineering]] — the sibling discipline
- [[architecture/README|architecture]] — this, for software
- [[engineering/README|engineering]] — the physical domains this coordinates
- [[BUILD-PLAN|Build Plan]]
