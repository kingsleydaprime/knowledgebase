# Systems Engineering

## What systems engineering is

**Systems engineering is making a big, complicated thing work as a whole, when it's built by many teams and no single person understands every part.**

Think of an aircraft, a power grid or a hospital's computer system. Each part can be built perfectly to its own specification, and the whole can still fail. The engine team assumed the fuel team would handle something; the fuel team assumed the opposite; nobody owned the gap between them. **Failures live between the parts.** Systems engineers own those gaps: they turn vague goals into clear, testable requirements, define exactly how parts connect, weigh up design choices fairly, check the finished system really does what was needed, and hunt for ways it could fail before it does.

It began in aerospace and defence, but software needs it too. Many of its tools, like listing every way a part can fail and what happens next, are better than what software teams invented on their own.

## What you'll be able to do

By the end you will be able to:
- explain why a system can fail even when every part works;
- write clear requirements that can actually be tested, and trace each one to what satisfies it;
- explain the standard lifecycle of a system, and how it fits with agile work;
- break a system into parts and define exactly how they connect;
- compare design options fairly, and spot a comparison that's been rigged;
- check that a system is built right *and* that it's the right system;
- find likely failures early, using failure-mode tables and fault trees.

## Where to start

No special background is needed, though some experience building software or hardware helps everything click.

Read in order. Notes 01–03 set the frame, 04–05 are about design, and 06–08 are about proving it works and handling what you missed.

1. [[systems-engineering/01-what-systems-engineering-is|What Systems Engineering Is]]: behaviour no single part has, the three classic failures, and why most of a project's cost is decided before anyone feels sure.
2. [[systems-engineering/02-requirements|Requirements]]: what makes a requirement good, why "can it be tested?" catches most bad ones, and tracing each requirement through the design.
3. [[systems-engineering/03-the-lifecycle-and-the-v-model|The Lifecycle and the V-Model]]: the standard stages, checking you built it right versus built the right thing, and why this isn't the opposite of agile.
4. [[systems-engineering/04-architecture-and-interfaces|Architecture and Interfaces]]: splitting a system by what it does before deciding what it's made of, writing down exactly how parts connect, and leaving spare capacity.
5. [[systems-engineering/05-trade-studies|Trade Studies]]: comparing design options properly, the four ways a scoring table misleads, and testing how sensitive the answer is.
6. [[systems-engineering/06-verification-and-validation|Verification and Validation]]: the four ways of checking a system, testing in realistic conditions, and why "every line was tested" isn't the same as confidence.
7. [[systems-engineering/07-mbse-and-modelling|MBSE and Modelling]]: describing a system as a model instead of documents, the SysML language, and "digital twins".
8. [[systems-engineering/08-risk-and-failure-analysis|Risk and Failure Analysis]]: tables of how each part can fail, fault trees, failures that hit several parts at once, and how warning signs become normal until disaster.

## Key ideas to remember

1. **A system can do things none of its parts do, good and bad.** That's why the discipline exists. → [[systems-engineering/01-what-systems-engineering-is|01]]
2. **About 80% of a project's lifetime cost is locked in before 15% is spent.** The early decisions matter most. → [[systems-engineering/01-what-systems-engineering-is|01]]
3. **If you can't write the test, the requirement isn't finished.** → [[systems-engineering/02-requirements|02]]
4. **The connection between two parts belongs to neither team,** and it's harder to change than either part. → [[systems-engineering/04-architecture-and-interfaces|04]]
5. **Agree how much each factor matters before scoring the options.** Whoever sets the weights has already made the decision. → [[systems-engineering/05-trade-studies|05]]
6. **The people who built it share the blind spots that would cause it to fail.** That's why independent testing matters. → [[systems-engineering/06-verification-and-validation|06]]
7. **A backup only helps if it can't fail for the same reason as the main part.** → [[systems-engineering/08-risk-and-failure-analysis|08]]
8. **Getting away with a known problem isn't proof it's safe.** → [[systems-engineering/08-risk-and-failure-analysis|08]]

## Related

- [[architecture/index|Architecture]]: the same thinking for large software systems.
- [[software-engineering/index|Introduction to Software Engineering]]: the lifecycle from the software side.
- [[devops/12-sre-and-platform-engineering/index|SRE]]: reliability work that rediscovered many of these ideas.
- [[concepts/01-best-practices/06-coupling-and-cohesion/index|Coupling and Cohesion]]: how tightly parts depend on each other, in code.

---

## About this course

- **Size:** 8 notes, about 8,200 words, written in August 2026. The vault is written by a systems engineering student and had nothing on the subject until then.
- **Why it matters for software:** much of the vault's software material (interfaces, requirements for speed and uptime, limiting how far a failure spreads, reviewing incidents afterwards) is systems engineering under other names. Tools like requirement tracing and failure-mode tables are underused in software.
