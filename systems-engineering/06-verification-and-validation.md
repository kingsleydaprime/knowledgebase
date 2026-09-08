# Verification and Validation

> **[Intermediate]** · Proving it works — the four methods, and why "all tests passed" is not the same as "it works".

**Verification:** did we build the thing right? *(against the specification)*
**Validation:** did we build the right thing? *(against the actual need)*

A system can pass every verification activity and fail validation completely. That's Mars Climate Orbiter, and it's every product that meets its requirements and nobody wants.

## The four methods

Every requirement is verified by one of these, and **choosing the method is part of writing the requirement** — you specify it at baseline, not at test time.

| Method | What it is | Use when | Confidence |
|---|---|---|---|
| **Inspection** | Look at it | Physical properties, documentation, workmanship | Low |
| **Analysis** | Calculate or simulate | Testing is impossible or ruinous | Medium |
| **Demonstration** | Operate it, observe qualitatively | Functional behaviour, procedures | Medium |
| **Test** | Instrumented, quantitative, controlled | **Anything measurable** | **High** |

**Prefer test.** Use analysis where a test is impossible — you cannot test a bridge to destruction, or a satellite in orbit before launch, or a 40-year fatigue life.

**And when you rely on analysis, the model becomes the thing that must be trusted.** That's where a whole discipline lives → [[foundations/numerical-methods/README|numerical methods]] on conditioning and error, and [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]] on whether your simulation resembles reality.

## The levels

Verification happens at every level of the V, bottom-up:

1. **Component** — does this part meet its spec? *(unit tests)*
2. **Subsystem** — does this assembly meet its spec? *(integration tests)*
3. **System** — does the whole meet system requirements? *(system tests)*
4. **Acceptance** — does the customer agree it's delivered? *(UAT)*

**Then validation, which is a different question at every level:** does it satisfy the need, in the real environment, with real users, under real conditions?

## Test like reality, not like the lab

**The most reliable source of field failures is a test environment that differs from the operating environment.**

Physical systems test against the environment explicitly — thermal cycling, vibration, humidity, salt spray, EMC, drop, and combinations, because a system can pass each individually and fail under vibration *at* temperature.

**Software's equivalents are exactly the ones commonly skipped:**

- **Load** — at realistic and at 2× realistic concurrency
- **Soak** — run for days. Memory leaks and file-descriptor leaks are invisible in a five-minute test → [[languages/06-python/15-files-and-io|files and I/O]]
- **Chaos** — kill dependencies and see what happens → [[architecture/04-distributed-systems/15-testing-distributed-systems|testing distributed systems]]
- **Data realism** — production-shaped volumes and production-shaped ugliness. **An index missing on a 1,000-row test database is invisible and fatal at 10 million** → [[databases/04-b-trees-and-indexes|indexes]]
- **Degraded conditions** — slow network, packet loss, partial outage

**"It works on my machine" and "it passed in staging" are the same statement**: verified in an environment that isn't the one that matters.

## Coverage is not confidence

Every requirement traced to a verification activity gives you a **verification cross-reference matrix**, and it answers "have we checked everything we said?"

**It cannot answer "have we thought of everything?"** — which is the question that actually matters, and the reason [[foundations/systems-engineering/08-risk-and-failure-analysis|FMEA and hazard analysis]] exist as separate activities. They look for failures nobody wrote a requirement about.

The software version is the same trap: **line coverage measures what ran, not what was checked** → [[languages/06-python/13-testing-and-tooling|testing and tooling]]. 100% coverage of the behaviour you thought of says nothing about the behaviour you didn't.

## Independence

Serious programmes use **Independent Verification and Validation** — a team not reporting to the development organisation.

The reason isn't distrust; it's that **the people who built it share the assumptions that would cause the failure.** If your mental model is wrong, your tests are wrong in exactly the same way, and no amount of diligence fixes it from the inside.

**Software's weaker versions:** code review by someone who didn't write it, a separate QA function, external penetration testing, and a red team. All are the same move — buy a different set of assumptions → [[cybersecurity/02-ethical-hacking/README|ethical hacking]].

**A blameless postmortem is retrospective IV&V**: an examination of the assumptions that failed, deliberately structured so people will tell the truth → [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|SRE]].

## Operational validation

The last stage, and the one most often treated as ceremony: **does it work in the hands of real users, doing real work, at real pace?**

Physical programmes call it operational test and evaluation, sea trials, or flight test. Software calls it a canary, a beta, a pilot deployment, or a staged rollout → [[devops/11-delivery-and-advanced/README|delivery]].

**The recurring finding across both is the same: systems that pass every technical verification fail on human factors.** Operators misread the display, procedures don't fit the shift pattern, the alarm is ignored because it fires constantly. Three Mile Island was substantially an interface problem — the instrumentation showed valve *commanded* position rather than actual position, and the operators reasoned correctly from wrong information.

**"The user made a mistake" is almost always a system finding, not a user finding.** That's the same reasoning as blameless postmortems, and it's why human factors is part of the discipline rather than a nicety.

## Related
- [[foundations/systems-engineering/03-the-lifecycle-and-the-v-model|the V-model]] — where V&V sits
- [[foundations/systems-engineering/08-risk-and-failure-analysis|risk and failure analysis]] — finding what you didn't specify
- [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]] — the software version
- [[architecture/04-distributed-systems/15-testing-distributed-systems|testing distributed systems]]

*Source: [reference] — from the NASA SE Handbook, INCOSE, and the standard human-factors case studies.*
