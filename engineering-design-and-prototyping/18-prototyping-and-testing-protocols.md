---
id: 1dfbb5bb-45a6-40a4-bdcb-e0b205532c59
---

# Prototyping and Testing Protocols

Prototyping builds a model of the design, and testing checks it against the criteria for success.

## Before you start
<!-- bite: 69318057-6823-4b19-8023-c18808fe80b9 -->

You should know the criteria for success ([[engineering-design-and-prototyping/04-problem-definition|lesson 04]]) and what detailed design produces ([[engineering-design-and-prototyping/16-engineering-drawings-and-dfma|lesson 16]]).

After this lesson you will be able to:

1. tell a low-fidelity prototype from a high-fidelity one, and say when to use each;
2. say what a testing protocol contains;
3. design a testing protocol for performance and usability.

## What prototyping and testing are
<!-- bite: 43a8bc25-e7fe-4478-88dc-185ad060514f -->

Back in lesson 1: prototyping is creating physical or virtual models of the design solution to test its feasibility, functionality and usability. Testing and evaluation then checks whether it actually meets the criteria for success.

This is where the design meets reality. Everything before was on paper. Now we find out if we were right.

The methods from lesson 2:

- **Prototyping:** 3D printing, CAD, simulation.
- **Testing and evaluation:** experiments, surveys, interviews.

## Low-fidelity and high-fidelity prototypes
<!-- bite: 1bfeed0e-475b-4e38-9d19-a29fdf4594e6 -->

Prototypes don't have to be perfect. There are two levels:

1. **Low-fidelity prototype**: a quick, cheap, rough model, often cardboard, foam or paper. It checks size, shape and basic idea. If it's wrong, you've lost an afternoon.
2. **High-fidelity prototype**: close to the real product in material and finish, for example 3D printed or CNC cut. It checks strength, stability and how it really feels to use.

You start low and move up. For a desk stand that holds a laptop and 4 textbooks at eye level: build a low-fidelity model using cardboard first, then move to a high-fidelity 3D printed or CNC cut version to test stability.

## What a testing protocol is
<!-- bite: 15aa9c02-3ea3-4fc0-8e1c-896b62047266 -->

You can't just "try it and see". A **test protocol** says:

1. **What** is tested.
2. **How** it is tested (the procedure).
3. **What data** is recorded.
4. **What counts as a pass** (the success criterion).

Every success criterion should trace back to the problem definition's criteria for success. If the problem definition said "20% less neck strain", one test had better measure neck strain.

## Example protocol: performance tests
<!-- bite: 50cd64af-989b-400c-80b9-7be70d5d31e1 -->

Here's a protocol for the desk stand. First, the tests of how the product itself performs:

| Test | Procedure | Data collected | Success criterion |
| --- | --- | --- | --- |
| Load test | Place 4 textbooks and a laptop on the stand for 24 hours | Deflection, any cracks | No permanent deformation or cracks |
| Stability test | Tilt and push gently at each height setting | Tilt angle at which it tips | Does not tip in normal use |
| Durability (cycle) test | Fold and unfold the hinges many times (for example 1,000 cycles) | Number of cycles before loosening or failure | Hinges still hold position after the test |
| Safety test | Inspect edges and pinch points | Sharp edges and pinch points found | None found |

## Example protocol: usability tests
<!-- bite: 4624e31a-a799-402c-8869-d14c6dc8f041 -->

Then the tests with real users:

| Test | Procedure | Data collected | Success criterion |
| --- | --- | --- | --- |
| Ergonomic test | Users work for a set time with and without the stand | User-reported neck strain scores | At least 20% reduction in neck strain |
| Usability test | Users set it up and organise stationery without instructions | Time taken, errors, observations | Most users finish without help |
| Satisfaction survey | Questionnaire after use | Ratings from 1 to 5 | Average rating "high" (for example 4 or more) |

Record the conditions, the sample of users, the results and any redesign actions.

## After the tests
<!-- bite: 97a206ed-68bc-4f68-ae29-dd6c84df98fb -->

The output of testing is a decision: **release or redesign**. If the stand tips at the highest setting, that's the dashed arrow from lesson 2: back to detailed design for a wider base, then build and test again.

Testing checks whether the product passes. But a smart team also asks a different question *before* testing: how could this fail? That's FMEA, the next lesson.

## Common pitfalls
<!-- bite: 2e41ab49-6cab-4432-a27e-0c959225512f -->

1. **A test without a success criterion.** "Load it with books" isn't a test until you say what counts as a pass.
2. **Only testing performance.** A strong stand that nobody can set up without the manual fails usability.
3. **Jumping straight to a high-fidelity prototype.** Cardboard first finds the cheap mistakes cheaply.

## Check your understanding
<!-- bite: 77476834-7050-4a5d-a974-12eca81e7c3c -->

Try each one before you open the answer.

1. <!-- q: mcq id="7c3e9a15" -->
   A team tapes cardboard boxes together to check whether a new kiosk is the right height for customers. What kind of prototype is this?

   - [x] Low-fidelity
   - [ ] High-fidelity

   <details><summary>Answer</summary>

   Low-fidelity: quick, cheap and rough, checking size and basic idea.

   </details>

2. <!-- q: gap id="0e4b8d72" answers="what|tested;how|procedure;data;pass|success criterion|criterion" -->
   Fill in the gaps. A test protocol says ___ is tested, ___ it is tested, what ___ is recorded, and what counts as a ___.

   <details><summary>Answer</summary>

   What, how, data, pass (the success criterion).

   </details>

3. <!-- q: mcq id="f1a6c084" -->
   A new folding chair is opened and closed 5,000 times, and the team counts how many cycles it takes for the joints to loosen. What kind of test is this?

   - [ ] Load test
   - [x] Durability (cycle) test
   - [ ] Usability test

   <details><summary>Answer</summary>

   A durability (cycle) test.

   </details>

4. <!-- q: open id="92d5b7e3" -->
   Design a short testing protocol (at least three tests) for a new rechargeable torch. For each test, give the procedure, the data collected and the success criterion.

   <details><summary>Answer</summary>

   For example. (1) Battery test: charge fully, leave on until it goes out; data: hours of light; pass: at least 8 hours. (2) Drop test: drop from 1.5 m onto concrete 10 times; data: damage, whether it still works; pass: still works, no cracks. (3) Water test: spray with water for 5 minutes; data: whether it still works, water inside; pass: still works. (4) Usability test: users switch it on and change modes without instructions; data: time and errors; pass: most users succeed within 30 seconds. Any protocol works if each test has a procedure, data and a measurable pass.

   </details>

5. <!-- q: open id="4a0f6e28" -->
   Where should a testing protocol's success criteria come from? Why?

   <details><summary>Answer</summary>

   From the criteria for success in the problem definition. Those are the metrics the team agreed would show the design worked, so the tests must check exactly them. Otherwise a product could pass every test and still miss its objective.

   </details>

## Before moving on
<!-- bite: f43bdda2-a3f8-471d-a2c7-4d57faca4aa6 -->

You can tell low- from high-fidelity prototypes, say what a test protocol contains, and design one for performance and usability. **Next:** [[engineering-design-and-prototyping/19-failure-mode-and-effects-analysis|Failure Mode and Effects Analysis]]: finding how a design could fail before it does.

## Related
<!-- bite: 07967f0e-4141-4bc1-a936-6b7340a8abfe -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[engineering-design-and-prototyping/23-rapid-prototyping|Rapid Prototyping]]: which machine to make a prototype with.
- [[systems-engineering/06-verification-and-validation|Verification and Validation]]: checking you built it right, and built the right thing.

## About this lesson
<!-- bite: 1d827da3-f82d-4eca-9f16-38284b0b1785 -->

**Level:** Intermediate. **Covers:** low- and high-fidelity prototypes, what a testing protocol contains, and a full performance and usability protocol for a desk stand.

**Where it sits:** lesson 18 of 21, phases 6 and 7 of the design process. Exam question 5(a) comes from here.

**Source:** the prototyping steps come from the author's own SSG 532 notes. The testing protocol was written for the exam from general engineering knowledge; it is not in the lecture notes.
