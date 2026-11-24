---
id: 82a20b1c-c466-4c63-89fe-e2cb96841ca2
---

# Requirements Engineering

Requirements engineering is the whole process of finding, agreeing, writing, checking and managing a design's requirements, from the first interview to the final test.

## Before you start
<!-- bite: ae37d7e5-afef-4f9b-ad6d-eafce5f8aced -->

You should know the types of requirement and what makes a good one ([[engineering-design-and-prototyping/06-requirements-and-requirement-writing|06 — Requirements and Requirement Writing]]), and how stakeholders' needs are found ([[engineering-design-and-prototyping/05-stakeholder-analysis|Stakeholder Analysis]]).

After this lesson you will be able to:

1. name the five activities of requirements engineering;
2. prioritise requirements with MoSCoW and give each one a verification method;
3. build a traceability matrix, and explain why changes to requirements must be controlled.

## What requirements engineering is
<!-- bite: ecdf4219-12b7-4209-96cc-bfe090d4967e -->

Lesson 06 showed how to write one good requirement. A real product has hundreds, written by different people, changing as the project goes on. **Requirements engineering** is the disciplined process that keeps them all correct, agreed and checkable from start to finish.

It matters because most project failures trace back to requirements: something was missed, misunderstood, or changed without anyone noticing. This lesson follows the bicycle from lesson 06 through the five activities.

## The five activities
<!-- bite: 15a2691c-c8cd-4cc4-bfc3-2e1b06986270 -->

1. **Elicitation:** draw out the needs from stakeholders (lesson 05's interviews, surveys, observation and workshops), plus standards, laws and competing products (**benchmarking**).
2. **Analysis:** sort the needs, find gaps and conflicts, and decide priorities.
3. **Specification:** write them as clear requirements, each with an identifier, in one document: the **product design specification (PDS)**.
4. **Verification and validation of the requirements:** check the requirements themselves are right before designing to them. Are they clear, testable and complete? Do stakeholders agree they describe what they need?
5. **Management:** track every requirement through design and testing, and control changes.

The activities loop: analysis often sends you back to elicit more, and a change late on sends you back to analysis.

## Prioritising with MoSCoW
<!-- bite: e2099376-7b16-41cc-9fe2-f48098d7f705 -->

Not every requirement is equally important, and when money or time runs short you need to know what to drop. **MoSCoW** sorts them into four groups:

1. **Must have:** without it the product fails. The frame carries a 100 kg rider.
2. **Should have:** important, but the product still works without it. Frame mass under 2 kg.
3. **Could have:** nice if time and money allow. A built-in bell.
4. **Won't have (this time):** agreed to leave out of this version. Electric assist.

Writing down the "won't haves" is as useful as the "musts": it stops them creeping back in.

## Giving every requirement a verification method
<!-- bite: 0f49c417-02a3-42ae-9933-a1da208ac6e1 -->

A requirement isn't finished until you know how you will prove it is met. There are four methods:

1. **Inspection:** look or measure. "The frame is painted blue."
2. **Analysis:** calculate or simulate. "The frame's stress at 100 kg stays below the allowable stress," checked by calculation or FEA (lesson 20).
3. **Demonstration:** operate it and watch. "The seat height can be adjusted without tools."
4. **Test:** measure performance under set conditions. "The frame survives 100,000 load cycles."

Choosing the method early exposes untestable requirements: if you can't name a method, the requirement is too vague. Lesson 30 uses these four methods when the design is tested.

## The traceability matrix
<!-- bite: 124a1bf8-8aa9-447e-890b-02f85641b0b8 -->

**Traceability** means you can follow each requirement backwards to the need it came from, and forwards to the design that meets it and the test that proves it. A **requirements traceability matrix** records this as a table:

| ID | Need | Requirement | Priority | Design element | Verification |
| --- | --- | --- | --- | --- | --- |
| R1 | Safe for adults | Frame carries a 100 kg rider | Must | Steel tube, 1.5 mm wall | Test: static and fatigue load |
| R2 | Easy to carry upstairs | Frame mass under 2 kg | Should | Aluminium frame | Inspection: weigh |
| R3 | Comfortable | Seat height 75 to 90 cm | Must | Quick-release seat post | Demonstration |
| R4 | Affordable | Price under ₦150,000 | Must | Local welding, standard parts | Analysis: cost estimate |

Read across a row and you see why each design choice exists. Notice R1 and R2 already pull against each other: steel is strong but heavy. Traceability makes conflicts like that visible.

## Managing change
<!-- bite: 57e32f41-9359-4b1e-ba24-89cb635b2abe -->

Requirements change: a stakeholder changes their mind, a test fails, a regulation changes. Uncontrolled change is called **scope creep**, and it wrecks budgets.

So once the PDS is agreed, it becomes a **baseline**, and changes go through **change control**:

1. Someone proposes a change, with a reason.
2. The team assesses its impact, using the traceability matrix to see which designs and tests it touches.
3. A named person approves or rejects it.
4. If approved, the PDS and matrix are updated and everyone affected is told.

## Common pitfalls
<!-- bite: 6009f308-7d4c-437e-8796-dc89657a1b66 -->

1. **Writing requirements nobody can verify.** If you can't name the verification method, rewrite the requirement.
2. **Everything is a "must".** Then nothing can be dropped when money runs out.
3. **No traceability.** Later, nobody knows why a design choice was made or whether a requirement was ever tested.
4. **Accepting changes in the corridor.** Every change goes through change control.

With the requirements agreed, prioritised and traceable, the team can start generating ideas to meet them. That is concept generation, next.

## Check your understanding
<!-- bite: 51882fd9-fc68-4a91-b649-1c75e3e9fa30 -->

Try each one before you open the answer.

1. <!-- q: mcq id="c41cdcbd" -->
   Which verification method fits "the kettle switches itself off within 5 seconds of the water boiling"?

   - [ ] Inspection
   - [ ] Analysis
   - [ ] Demonstration
   - [x] Test

   <details><summary>Answer</summary>

   Test: it is measured under set conditions with a pass or fail figure (5 seconds). A demonstration would only show that it switches off, without timing it.

   </details>

2. <!-- q: mcq id="1e23c738" -->
   A phone's development is behind schedule. Using MoSCoW, which kind of requirement is dropped first?

   - [ ] Must have
   - [ ] Should have
   - [x] Could have
   - [ ] None; all requirements must be met

   <details><summary>Answer</summary>

   Could haves go first. Should haves come next if needed, and must haves are never dropped.

   </details>

3. <!-- q: gap id="6923ce33" answers="traceability|traceability matrix|requirements traceability matrix" -->
   A table that links each requirement back to the stakeholder need it came from and forward to the design element and test that cover it is called a requirements ___ matrix.

   <details><summary>Answer</summary>

   A requirements traceability matrix.

   </details>

4. <!-- q: open id="1ffc6a3b" -->
   A client tells a designer in a meeting, "oh, and add a USB port", three weeks before production. What should happen, and why?

   <details><summary>Answer</summary>

   It should go through change control: record the request and its reason, assess its impact on cost, schedule, design and tests using the traceability matrix, have a named person approve or reject it, then update the specification and tell everyone affected. Accepting it informally is scope creep, which breaks budgets and can leave untested changes in the product.

   </details>

5. <!-- q: mcq id="9fc292cf" -->
   Which activity of requirements engineering checks that the requirements themselves are clear, testable and agreed, before any design starts?

   - [ ] Elicitation
   - [ ] Specification
   - [x] Verification and validation of the requirements
   - [ ] Management

   <details><summary>Answer</summary>

   Verification and validation of the requirements. Fixing a bad requirement on paper is far cheaper than after it has been built.

   </details>

6. <!-- q: open id="6ccca359" -->
   Write one traceability matrix row for a school backpack, with an ID, the need, the requirement, its MoSCoW priority, a design element and a verification method.

   <details><summary>Answer</summary>

   For example: R1; need "protects my laptop"; requirement "holds a 15-inch laptop in a padded sleeve that survives a 1 m drop"; priority Must; design element "10 mm foam sleeve against the back panel"; verification "Test: drop the loaded bag from 1 m and check the laptop". Any row whose parts link up sensibly is fine.

   </details>

## Before moving on
<!-- bite: 90049f35-bb75-42d3-a386-bd066592157d -->

You can run the five activities, prioritise with MoSCoW, give each requirement a verification method, build a traceability matrix and control changes. **Next:** [[engineering-design-and-prototyping/08-concept-generation-1|08 — Concept Generation 1: Brainstorming, Morphological Analysis and TRIZ]]: getting many ideas, from free brainstorming to 40 inventive principles.

## Related
<!-- bite: 872983e2-6336-4722-874a-261ee1f83ae8 -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[systems-engineering/02-requirements|Requirements]] in systems engineering.

## About this lesson
<!-- bite: 1fa5b300-0aac-4dc8-a578-dfa121c79e0a -->

**Level:** Beginner to intermediate. **Covers:** the five activities of requirements engineering, the product design specification, MoSCoW, the four verification methods, the traceability matrix and change control.

**Where it sits:** lesson 07 of 36, in part 2 (defining the problem).

**Source:** written from general engineering design knowledge, because the SSG 532 lecture notes only cover requirement writing; requirements engineering is on the official course outline.
