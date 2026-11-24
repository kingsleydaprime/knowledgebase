---
id: 2f273fe6-41b3-47d4-b9d8-06c25f81d10a
---

# Verification, Validation and Testing

Verification proves the design meets its requirements, validation proves it meets the users' real needs, and testing produces the evidence for both.

## Before you start
<!-- bite: 3a071715-e788-40a3-9341-84f064141709 -->

You should know the four verification methods and the traceability matrix ([[engineering-design-and-prototyping/07-requirements-engineering|Requirements Engineering]]) and testing protocols ([[engineering-design-and-prototyping/25-prototyping-and-testing-protocols|25 — Prototyping and Testing Protocols]]).

After this lesson you will be able to:

1. tell verification from validation, with examples;
2. explain the V-model and the four levels of testing;
3. choose the right kind of test, plan it, and work out how long a life test takes.

## What verification, validation and testing are
<!-- bite: 10823dc6-3944-4be6-a657-c65f885463db -->

1. **Verification** asks: *did we build the design right?* Does it meet every written requirement?
2. **Validation** asks: *did we build the right design?* Does it meet the stakeholders' real needs, in real use?

A bicycle frame can pass every requirement and still fail validation: it holds 100 kg, weighs under 2 kg and costs under ₦150,000, but riders find it uncomfortable because nobody wrote down a requirement about the riding position. Verification checks against the specification; validation checks against the world.

**Testing** is one way of producing evidence for both. Lesson 25 wrote testing protocols for a single prototype. This lesson places testing in the whole project.

## The four ways to verify
<!-- bite: 50f0d04a-f7e3-45d7-b986-639f0b4adff6 -->

Lesson 07 gave every requirement one of four verification methods:

1. **Inspection:** look and measure.
2. **Analysis:** calculate or simulate (lesson 20).
3. **Demonstration:** operate it and observe.
4. **Test:** measure performance under controlled conditions.

The **verification matrix** is the traceability matrix with results added: each requirement, its method, the test or analysis that covers it, and **pass or fail**. A design is verified when every row passes.

## The V-model
<!-- bite: 29d9a9f9-1d22-43f9-b2b7-4c571228ed21 -->

The **V-model** shows how design and testing mirror each other.

![The V-model: down the left side, stakeholder needs, system requirements, subsystem design and component design; at the bottom, build the parts; up the right side, component testing, integration testing, system testing and acceptance testing, each level of testing checking the matching level of design on the left](images/ed-v-model.svg)

## The four levels of testing
<!-- bite: c6fa2b5d-f551-4bf7-8cca-b84baf4e5d9b -->

Down the left, the design is broken into finer detail. Up the right, parts are tested and joined back together, and **each level of testing checks the level of design opposite it**:

1. **Component (unit) testing:** each part against its own specification. Does the motor give its rated torque?
2. **Integration testing:** subsystems joined, especially their interfaces. Do the battery, controller and motor work together?
3. **System testing:** the whole product against the system requirements. That is **verification**.
4. **Acceptance testing:** users or the client try it in real conditions against their needs. That is **validation**.

Problems found low on the right are cheap to fix; problems found at acceptance can mean going all the way back up the left side.

## Kinds of test
<!-- bite: d010c415-61b3-4b0d-b983-3e7dbfd43669 -->

1. **Functional:** does it do each job?
2. **Performance:** how well: speed, range, efficiency.
3. **Environmental:** heat, cold, humidity, rain, dust, vibration, drops.
4. **Durability and life:** repeated use until failure, or for a set number of cycles. **Accelerated life testing** speeds this up by running it faster or harder than normal.
5. **Safety:** guards, interlocks, electrical safety, as required by standards (lesson 29).
6. **Usability:** real users doing real tasks (lesson 25).

Tests are **destructive** (break the sample to find its limit) or **non-destructive** (check without damage). Non-destructive testing (NDT) includes visual inspection, dye penetrant for surface cracks, ultrasound and X-ray for hidden flaws.

## Plan, procedure, report
<!-- bite: ebb9b2b2-0c17-4799-9cf1-48a33067f8a2 -->

Every formal test has three documents:

1. **Test plan:** what will be tested, why (which requirements), with what equipment, how many samples, and the **pass/fail criteria**, written before testing so they can't be bent to fit the results.
2. **Test procedure:** the exact steps, so anyone can repeat it.
3. **Test report:** what was done, the results, pass or fail, and anything unexpected.

When a design is changed to fix a failure, earlier tests that the change could affect are run again: **regression testing**.

## Common pitfalls
<!-- bite: 4c09554d-4c71-4d13-8267-7a80b2ee8c90 -->

1. **Treating verification as enough.** A product can meet every requirement and still not suit its users.
2. **Writing the pass mark after the test.** Set the criteria in the test plan first.
3. **Only testing the whole product.** Test components and interfaces first, where faults are cheap to find.
4. **Forgetting regression tests** after a fix.

The design has now been proven to work and to suit its users. Next lesson looks at making it in quantity: manufacturing processes and their costs.

## Check your understanding
<!-- bite: d0b8bc6d-ffcf-4658-b19e-dca378134e26 -->

Try each one before you open the answer.

1. <!-- q: mcq id="499c5313" -->
   A new phone meets every requirement in its specification, but users find the buttons too small to press with a thumb. Which check failed?

   - [ ] Verification
   - [x] Validation
   - [ ] Both
   - [ ] Neither

   <details><summary>Answer</summary>

   Validation: the design meets its requirements but not its users' real needs. A usability need was missing from the requirements.

   </details>

2. <!-- q: mcq id="3f50b30d" -->
   On the V-model, which level of testing checks the system requirements?

   - [ ] Component testing
   - [ ] Integration testing
   - [x] System testing
   - [ ] Acceptance testing

   <details><summary>Answer</summary>

   System testing, opposite the system requirements on the left. Acceptance testing checks the stakeholder needs.

   </details>

3. <!-- q: exact id="2cf2f395" answer="30.416667" sigfigs="3" -->
   A cupboard hinge must survive 10 openings a day for 10 years (365 days a year). A test rig opens it 20 times a minute. How many hours does the life test take?

   <details><summary>Answer</summary>

   About 30.4 hours: 10 × 365 × 10 = 36,500 cycles, and 36,500 ÷ 20 = 1,825 minutes, which is 1,825 ÷ 60 hours.

   </details>

4. <!-- q: mcq id="5001e327" -->
   Which of these is a non-destructive test?

   - [ ] Loading a bracket until it breaks
   - [x] Ultrasound to find a hidden crack in a weld
   - [ ] Dropping a phone until its screen cracks
   - [ ] Bending a sample to measure its strength

   <details><summary>Answer</summary>

   Ultrasound, which finds the flaw without damaging the part. The others break the sample.

   </details>

5. <!-- q: open id="033e5ae5" -->
   Why must pass/fail criteria be written in the test plan before the test is run?

   <details><summary>Answer</summary>

   So they can't be adjusted to fit the results. If the criteria are set afterwards, a weak result can be talked into a pass. Fixing them first, from the requirements, makes the test an honest check.

   </details>

6. <!-- q: open id="20aff65e" -->
   After the e-bike's motor mount was strengthened to fix a cracking problem, why should the team rerun some earlier tests?

   <details><summary>Answer</summary>

   Regression testing: the change could affect things that already passed, such as the bike's weight, vibration, how the battery fits or the motor's cooling. Rerunning the tests the change could touch checks that the fix didn't break something else.

   </details>

## Before moving on
<!-- bite: be7d6b86-d8b0-4c35-b5c7-c90f94529c8c -->

You can separate verification from validation, read the V-model, choose tests, plan them and size a life test. **Next:** [[engineering-design-and-prototyping/31-manufacturing-processes|31 — Manufacturing Processes]]: moulding, casting, forging, extrusion and sheet metal, and when a mould pays for itself.

## Related
<!-- bite: 87ca7421-693a-4b58-92fc-ed050ab38fe0 -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[systems-engineering/06-verification-and-validation|Verification and Validation]] in systems engineering.
- [[systems-simulation/31-verification-and-validation-1|Verification and Validation 1]]: the same idea applied to simulation models.

## About this lesson
<!-- bite: 69e20761-dcbe-47da-98d4-22afa26a2f73 -->

**Level:** Intermediate. **Covers:** verification and validation, the four verification methods and the verification matrix, the V-model and four levels of testing, kinds of test, destructive and non-destructive testing, test documents and regression testing.

**Where it sits:** lesson 30 of 36, in part 8 (making it safe and proving it works).

**Source:** written from general engineering knowledge, because the SSG 532 lecture notes cover testing protocols but not verification and validation; they are on the official course outline. The worked numbers and the diagram come from `scripts/diagrams/engineering_design.py`.
