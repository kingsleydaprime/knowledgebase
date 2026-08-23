# MBSE and Modelling

> **[Intermediate]** · Model-Based Systems Engineering, SysML, digital twins — moving the source of truth out of documents.

## The problem with documents

Traditional systems engineering produces documents: requirements specs, ICDs, trade studies, test plans. Hundreds of them, in Word and Excel.

**They drift.** A requirement changes; the spec is updated, the ICD isn't, the test plan isn't, and the block diagram in the presentation is eighteen months old. **Nobody can tell you which documents are consistent**, and there's no mechanical way to check.

**MBSE's move: make a single formal model the source of truth, and generate views from it.** Requirements, structure, behaviour and parametrics are all elements *in one model*, with real relationships between them. Documents become exports.

**The immediate payoff is the query.** *"What breaks if this requirement changes?"* becomes something the tool answers, instead of a week of reading. Same for "which components have no requirement", "which requirements have no test", and "what does this interface touch".

## SysML in five diagrams

SysML is a UML profile adapted for systems rather than software. Nine diagram types; **five carry nearly all the value**:

**Requirement diagram** — requirements as model elements, with `«derive»`, `«satisfy»`, `«verify»` relationships. Traceability becomes structural rather than a spreadsheet.

**Block Definition Diagram (BDD)** — what the system is made of. Blocks, their properties, and composition. The structural taxonomy.

**Internal Block Diagram (IBD)** — how blocks connect *inside* a parent: ports, connectors, what flows across them. **This is the ICD, formalised** → [[foundations/systems-engineering/04-architecture-and-interfaces|interfaces]].

**Activity / State Machine diagrams** — behaviour. What happens in what order; what states the system occupies and what triggers transitions. State machines are the most immediately useful diagram in the set for anyone who has debugged a mode-confusion bug.

**Parametric diagram** — the one with no software equivalent. It binds *equations* to properties, so `mass_total = Σ mass_i` or a power budget is enforced by the model. **Change a component's mass and the system mass updates, and a violated constraint is flagged.** This is where a model stops being a drawing.

## SysML v2

v1 is widely criticised — verbose, tool-dependent, awkward to diff, and with a reputation for producing beautiful diagrams nobody reads.

**SysML v2 (released 2023–24) is a substantial redesign**, and the parts that matter to anyone from software:

- **A textual notation** alongside the graphical one. Which means **the model is text, so it diffs, merges and lives in git** → [[git/README|git]]
- **A standard API**, so tooling isn't locked to one vendor
- **A cleaner metamodel**

**The textual notation is the change that could actually shift adoption**, because it makes a model reviewable in a pull request. v1's binary vendor formats made version control effectively impossible, which quietly undermined every other benefit.

Adoption as of 2026 is still early. Treat v2 as the direction, not the current state.

## Digital twins and simulation

A **digital twin** is a model of a specific physical instance, kept in sync with live data from it — as opposed to a model of the design in general.

The progression, and each step costs more:

1. **Model** — a representation of the design
2. **Simulation** — the model, executed
3. **Digital shadow** — real data flows in, one-way
4. **Digital twin** — bidirectional; the model informs decisions about the real thing

Used for predictive maintenance, operator training, testing changes before making them, and diagnosing a system you can't physically reach — a wind turbine offshore, a rover on Mars.

**The honest limit: a model is only as good as its assumptions**, and a twin that has drifted from its physical counterpart is worse than no twin, because it's confidently wrong. Validating the model is a real, ongoing, funded activity → [[foundations/systems-engineering/06-verification-and-validation|V&V]].

## The software parallels

Software has arrived at MBSE's central idea repeatedly without calling it that. **The pattern each time: make the artefact executable, and generate the documents.**

| MBSE idea | Software equivalent |
|---|---|
| Model as source of truth | **Infrastructure as code** → [[devops/07-infrastructure-as-code/01-provisioning-and-terraform\|Terraform]] |
| Generated documentation | OpenAPI → generated client + docs → [[backend/02-api-design/README\|API design]] |
| Consistency checked mechanically | **Type checking** → [[languages/06-python/08-typing-and-type-hints\|typing]] |
| Parametric constraints | Property-based testing; SLO burn calculations |
| Simulation before commitment | `terraform plan`, staging, canaries |
| Traceability | Ticket → commit → test |

**`terraform plan` is a parametric diagram's argument, exactly:** the model knows the intended state, so it can tell you what changing one thing does before you do it.

**And the counter-lesson software learned the hard way is worth carrying back:** heavyweight UML modelling in the 2000s largely failed because the model and the code diverged, and the code was what ran. **Whatever is executable becomes the truth, and everything else becomes decoration.** MBSE only holds if the model is genuinely the source — the moment a spreadsheet becomes authoritative "just for this", the benefit evaporates.

## Is it worth it?

**The costs are real:** expensive tools, a steep learning curve, and organisational commitment. Half-adoption is the worst outcome — model *and* documents, both maintained, both drifting.

**Worth it when:** the system is large and long-lived, many organisations must interface, regulation demands traceability, or the cost of an interface error is enormous. Aerospace, defence, automotive, medical devices.

**Not worth it when:** the system is small, the team is one, or the design will change faster than the model can be maintained.

**The useful middle ground, and the one most people should actually occupy:** take the ideas without the tooling. **Traceability from need to test. A written, owned interface contract. Diagrams generated from something real rather than drawn by hand. Decisions recorded.** All of that is available in markdown and git, at close to zero cost, and it captures most of the value → [[foundations/systems-engineering/05-trade-studies|ADRs]].

## Related
- [[foundations/systems-engineering/04-architecture-and-interfaces|architecture and interfaces]] — what gets modelled
- [[foundations/systems-engineering/02-requirements|requirements]] — traceability, mechanised
- [[devops/07-infrastructure-as-code/01-provisioning-and-terraform|infrastructure as code]] — the same idea, in software
- [[engineering/02-control-theory/README|control theory]] — models with dynamics

*Source: [reference] — from OMG SysML specifications, INCOSE's MBSE initiative, and the digital-twin literature.*
