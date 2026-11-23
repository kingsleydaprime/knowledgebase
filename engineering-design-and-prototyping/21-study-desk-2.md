---
id: df530a96-1aff-4f7f-b4f7-01b4530434d9
---

# Study Desk 2: Refining, Detailing, Building and Testing

This is the second half of the study desk worked example, taking the chosen stand through phases 4 to 7: refinement, detailed design, prototyping, and testing and evaluation.

## Before you start
<!-- bite: ca9af3b7-a514-4459-8957-44b49bddc7b9 -->

You should have read [[engineering-design-and-prototyping/20-study-desk-1|Study Desk 1]], where Concept B was chosen with a decision matrix. You should also know concept refinement ([[engineering-design-and-prototyping/12-concept-refinement|lesson 12]]) and testing protocols ([[engineering-design-and-prototyping/18-prototyping-and-testing-protocols|lesson 18]]).

After this lesson you will be able to:

1. refine a chosen concept with functional decomposition and QFD, and say when a DSM isn't needed;
2. write a detailed design: dimensions, materials, components, interfaces and functions;
3. plan the prototypes and the tests that check the criteria for success.

## What this part does
<!-- bite: 692f0de7-785b-41ea-b980-de5a517c8230 -->

In part 1, Concept B won the decision matrix with 44. But a concept is still just an idea. This part turns it into a real object you could build and test.

Remember the problem definition, because everything here traces back to it:

- **Requirements:** laptop and notes at eye level; holds at least 4 textbooks; dedicated space for stationery.
- **Constraints:** under ₦20,000; lightweight; eco-friendly.
- **Criteria for success:** 20% less neck strain; "high" satisfaction rating.

## Phase 4: Concept refinement, functional decomposition
<!-- bite: b0f416ad-3269-49e9-a197-ccc56becb7d0 -->

Optimise the selected stand using functional decomposition: break its job into sub-functions and improve each one.

- **Sub-function 1, support laptop:** refine it to include adjustable height notches to cater to different user heights. A tall student and a short student need the screen at different heights to keep their necks straight.
- **Sub-function 2, organise stationery:** add magnetic strips to the side unit to keep paperclips and metal rulers in place.

## Phase 4: DSM and QFD
<!-- bite: e19bb299-a24e-4566-9a9f-fabe72181b6d -->

**Design structure matrix:** we don't need this here, because there are no bottlenecks. The stand has few parts and they don't depend on each other in complicated ways. Saying *why* you skip a method is part of the answer.

**Quality function deployment:** ensure the foldable feature is prioritised, because user research showed that students value portability. A student moving between hostel and library wants to carry it.

## Phase 5: Detailed design
<!-- bite: 6253f393-3030-41d6-9d9d-8d10196f708b -->

Now every detail is pinned down:

- **Dimensions:** length 50 cm, width 10 cm, thickness 5 cm; adjustable heights of 10 cm, 15 cm and 25 cm.
- **Materials:** 3-ply bamboo, 12 mm thick carbonised bamboo, and a surface finish of water-resistant matte varnish.
- **Components:**
  1. Hinges: 2 heavy-duty stainless steel friction hinges.
  2. Fasteners: M4 steel screws.
- **Interfaces:** safe edges.
- **Functions:**
  1. Laptop stand.
  2. Stationery organiser.

## Why these choices fit
<!-- bite: ea4f0421-b30d-4d02-ab45-d4f7b1a2cc1a -->

Check the detailed design against the problem definition:

- **Bamboo** is light (constraint: lightweight) and grows back fast (constraint: eco-friendly). The varnish protects it from spilled water, a real service condition on a student's desk.
- **Friction hinges** hold any angle, and they're what makes the foldable feature from QFD work.
- **Standard M4 screws** are a DFMA choice: one standard fastener, easy to buy and replace.
- **Safe edges** are human factors: no sharp corners near hands and wrists.

## Phase 6: Prototyping
<!-- bite: 1ba8159c-d00c-4d18-9f9e-f48d46bff206 -->

Build a low-fidelity model using cardboard first, then move to a high-fidelity 3D printed or CNC cut version to test stability.

The cardboard model checks the cheap things cheaply: is 50 cm long enough for a laptop and books? Are the three heights right? The high-fidelity version then checks what cardboard can't: does it stay stable with 4 textbooks on it?

## Phase 7: Testing and evaluation
<!-- bite: 93a65d51-3ab5-45b6-a916-23cc9e9b81af -->

The tests come from the criteria for success and the requirements. Using the protocol from lesson 18:

1. **Load test:** 4 textbooks and a laptop for 24 hours. Pass: no permanent deformation or cracks. (Checks the "4 textbooks" requirement.)
2. **Stability test:** tilt and push gently at each height. Pass: doesn't tip in normal use.
3. **Durability test:** fold and unfold the hinges about 1,000 times. Pass: the hinges still hold position.
4. **Ergonomic test:** users work with and without the stand. Pass: at least 20% less user-reported neck strain. (Criterion for success 1.)
5. **Satisfaction survey:** ratings from 1 to 5 after use. Pass: an average of 4 or more, a "high" rating. (Criterion for success 2.)

If every test passes, the stand is released. If one fails, say it tips at 25 cm, the design goes back to phase 5 for a wider base, and round the loop again.

## Common pitfalls
<!-- bite: aa3faa32-8a89-4b45-9c4c-bf7204b233f5 -->

1. **Detailed design that ignores the constraints.** Every material and part should trace back to a requirement or constraint, the way bamboo traces to "lightweight" and "eco-friendly".
2. **Skipping a method without saying why.** "No DSM needed, because there are no bottlenecks" is a correct answer. Leaving it out silently is not.
3. **Tests that don't check the criteria for success.** If the criterion was 20% less neck strain, one test must measure neck strain.

## Check your understanding
<!-- bite: 2984ca8d-d034-4e73-a91d-651ff82795c3 -->

Try each one before you open the answer.

1. <!-- q: mcq id="9a1e7c40" -->
   A designer refining a water dispenser breaks its job into "store water", "cool water" and "dispense water", and improves each one. Which method is this?

   - [x] Functional decomposition
   - [ ] Quality function deployment
   - [ ] Design structure matrix

   <details><summary>Answer</summary>

   Functional decomposition: breaking the overall function into sub-functions.

   </details>

2. <!-- q: mcq id="1d6b5f28" -->
   A team designing a simple wooden coat hook decides not to build a design structure matrix. Which reason is valid?

   - [x] The product has few parts and no bottlenecks between them
   - [ ] DSMs are only for software
   - [ ] The customer didn't ask for one

   <details><summary>Answer</summary>

   With few parts and no complicated dependencies, a DSM shows nothing new, so it can be skipped, as long as you say why.

   </details>

3. <!-- q: mcq id="e4c09a75" -->
   Which of these belong in a detailed design? Choose all that apply.

   - [x] Dimensions
   - [x] Materials
   - [x] Components and interfaces
   - [ ] A list of brainstormed ideas

   <details><summary>Answer</summary>

   Dimensions, materials, components, interfaces and functions. Brainstormed ideas belong to concept generation.

   </details>

4. <!-- q: open id="5b2f8d91" -->
   A rice cooker's criteria for success are "cooks 1 kg of rice in under 25 minutes" and "average user rating of 4 out of 5". Name the test for each criterion and its pass condition.

   <details><summary>Answer</summary>

   (1) Cooking test: cook 1 kg of rice and time it; pass if it is done in under 25 minutes. (2) Satisfaction survey: users rate it from 1 to 5 after use; pass if the average is 4 or more. Each test checks one criterion directly.

   </details>

5. <!-- q: open id="c07e3a46" -->
   Why build a low-fidelity prototype before a high-fidelity one? Use a product of your choice as an example.

   <details><summary>Answer</summary>

   A low-fidelity model is quick and cheap, so it catches size and shape mistakes before money is spent on real materials. For example, a foam model of a new television remote shows whether it fits the hand and the buttons are reachable; only then is it worth 3D printing a proper one to test the buttons and strength.

   </details>

## Before moving on
<!-- bite: a6ce94d7-71c6-494c-9ec6-490aa516f588 -->

You can take a chosen concept through refinement, detailed design, prototyping and testing, and trace every decision back to the problem definition. That's the whole design process. **Next:** the [[engineering-design-and-prototyping/ssg-532-question-bank|SSG 532 Question Bank]], to practise on the real exam.

## Related
<!-- bite: 7a56cc06-5278-484e-9bcb-6ec42bcfbb61 -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]

## About this lesson
<!-- bite: 6a16376e-5dbc-4ba0-8d61-321aae8d9a6b -->

**Level:** Intermediate. **Covers:** phases 4 to 7 of the design process on the student study desk: functional decomposition, QFD, detailed design, prototyping, and testing against the criteria for success.

**Where it sits:** lesson 21 of 21, part 2 of 2 of the worked example, and the end of the course.

**Source:** the author's own SSG 532 term paper (handwritten notes) for phases 4 to 6. Some values in the handwritten notes were hard to read (the notch heights, and one item in the materials list), so check them against the original page. The handwritten notes stop at phase 6; phase 7 here uses the testing protocol from lesson 18.
