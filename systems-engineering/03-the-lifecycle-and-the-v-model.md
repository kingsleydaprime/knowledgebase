# The Lifecycle and the V-Model

> **[Beginner → Intermediate]** · The shape of a systems project, why the V is a V, and how it relates to agile without either being wrong.

## The V

The field's most recognisable diagram. Decomposition down the left, integration up the right, and **each level of specification paired with the verification that proves it**:

```
 Stakeholder needs ──────────────────────────► Operation & validation
   ↓                                                        ↑
   System requirements ──────────────────► System verification
     ↓                                                    ↑
     Architecture ──────────────────► Integration & testing
       ↓                                                ↑
       Subsystem design ────────► Subsystem testing
         ↓                                            ↑
         Component design ──► Unit testing
           ↓                                       ↑
           └────────── IMPLEMENTATION ─────────────┘
```

**The horizontal arrows are the point.** They aren't decoration — each says *this is the artefact that proves that specification was met.* You write the system-level test plan when you write the system requirements, not two years later.

**And that's the discipline the V actually enforces: if you cannot write the test now, the requirement isn't finished.** Everything else about the V is scheduling. This is the part worth keeping even if you never draw one.

**The asymmetry to notice:** defects are *injected* on the left and *found* on the right. The further apart injection and detection are, the more expensive the fix — which is the cost curve from [[foundations/systems-engineering/01-what-systems-engineering-is|note 01]] restated as a process.

## Verification and validation are different questions

The distinction the V makes visible, and the most-confused pair of words in the field:

- **Verification** — *did we build the thing right?* Against the specification.
- **Validation** — *did we build the right thing?* Against the actual need.

**A system can pass every verification and fail validation.** That's the Mars Climate Orbiter: correct against its spec, wrong against reality. It's also every product that meets its requirements and nobody wants → [[foundations/systems-engineering/06-verification-and-validation|note 06]].

## The lifecycle

The V covers development. The **lifecycle** is the whole life, and ISO/IEC 15288 names the stages:

**Concept → Development → Production → Utilisation → Support → Retirement**

**The last three are where most of the money goes and most engineers never think.**

- A commercial aircraft flies for 30+ years; **support cost dwarfs purchase cost**
- Software: the maintenance phase is most of the total spend, and it's decided by choices made in a fortnight of design
- **Retirement is a real engineering problem** — decommissioning a nuclear plant, recycling a battery pack, migrating off a system 200 other systems depend on

**Design for the whole life, not the handover.** Concretely: maintainability, upgradability, diagnosability, and data migration are requirements, not afterthoughts. The software-shaped version of this argument is in [[foundations/software-engineering/01-what-software-engineering-is|what software engineering is]] — code is read and changed far longer than it is written.

## The V is not opposed to agile

The common framing — *V-model is waterfall, agile is modern, pick one* — is wrong in both directions, and worth getting right because you'll meet both.

**The V describes relationships, not a schedule.** "This test verifies that requirement" is true whether you traverse it once over three years or forty times over three years.

The real variable is **how big a batch you push through**, exactly as in [[devops/12-sre-and-platform-engineering/01-how-delivery-practice-evolved|how delivery practice evolved]]. And batch size should follow the **cost of being wrong**:

| Cost of a wrong decision | Batch size | Example |
|---|---|---|
| A deploy | **Tiny** — iterate | Web app |
| A firmware update | Small | Connected device |
| A recall | Large | Car ECU |
| A launch | **Enormous** — one shot | Spacecraft |

**Nobody iterates a bridge, and nobody writes a 300-page requirements baseline for a landing page.** Both are the same principle applied to different economics.

**The hybrids that actually get used:**

- **Incremental V** — several passes, each a complete V over a subset of capability
- **Spiral (Boehm)** — repeated risk-driven cycles; *"identify the biggest risk, and do the work that retires it"*. Genuinely underrated as a general planning heuristic
- **Agile hardware** — software iterates weekly *within* a hardware V that iterates yearly. Very common in robotics and automotive, and the interface between the two cadences is the hard part
- **Digital twin / model-based** — iterate on a simulation cheaply, commit to physical build rarely → [[foundations/systems-engineering/07-mbse-and-modelling|MBSE]]

## Gates and reviews

Formal checkpoints where a project must demonstrate readiness to continue. The standard sequence:

| Review | Asks |
|---|---|
| **SRR** System Requirements | Are the requirements complete, verifiable, agreed? |
| **PDR** Preliminary Design | Does the architecture plausibly meet them? |
| **CDR** Critical Design | Is the detailed design ready to build? |
| **TRR** Test Readiness | Are we ready to test, with criteria agreed in advance? |
| **ORR** Operational Readiness | Ready for real use, with people trained and procedures written? |

**A gate's value is entirely in whether it can actually stop the project.** A review that has never returned "no" is a status meeting, and everyone in the room knows it — which is precisely why the pressure to pass a gate on schedule is the mechanism behind several famous disasters. *Challenger*'s O-ring discussion is the canonical study: the concern was raised, the decision was made anyway.

**The software analogue is a release gate or a change-approval board**, with the identical failure mode: it becomes a rubber stamp, and then people route around it → [[devops/12-sre-and-platform-engineering/03-platform-engineering|platform engineering]].

## Technology Readiness Levels

NASA's 1–9 scale for how proven a technology is:

**1** basic principles → **3** proof of concept → **5** validated in relevant environment → **7** demonstrated in operational environment → **9** flight-proven.

**Its use is risk management, not vanity.** A programme depending on a TRL-3 technology with a fixed delivery date is a programme with an unfunded schedule risk, and saying so early is a systems engineer's job.

**Directly transferable to software:** "we'll use this new database" is a TRL question. Has *your team* run it in production under *your* load? If not, that's a risk with a mitigation (spike it, prototype it, keep a fallback), not a decision that's already been made.

## Related
- [[foundations/systems-engineering/06-verification-and-validation|verification and validation]] — the right-hand side, properly
- [[foundations/systems-engineering/08-risk-and-failure-analysis|risk and failure analysis]] — what gates are looking for
- [[devops/12-sre-and-platform-engineering/01-how-delivery-practice-evolved|how delivery practice evolved]] — the same batch-size argument in software
- [[foundations/software-engineering/02-the-software-development-lifecycle|the SDLC]]

*Source: [reference] — from ISO/IEC/IEEE 15288, the NASA SE Handbook, and INCOSE.*
