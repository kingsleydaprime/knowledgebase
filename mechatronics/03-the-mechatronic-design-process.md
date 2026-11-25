---
id: ff475afa-ef4e-4c51-aa45-e3aeb8a4b494
---

# The Mechatronic Design Process

**The mechatronic design process is the ordered set of stages that takes a mechatronic product from recognising a need, through modelling and control design, to a tested prototype and a deployed product.**

It answers "I've been asked to design an automated assembly line — where do I start, and what comes next?" We use that **automated assembly line** as the running example throughout, because it is what the exam asks you to design.

## Before you start
<!-- bite: 359f1d71-7a84-4df1-beac-f1535b78f997 -->

You should know the five elements of mechatronics ([[mechatronics/02-the-five-elements-of-mechatronics|The Five Elements of Mechatronics]]), because the design process is where those elements get used in order. No maths.

After this lesson you will be able to:

1. draw and label the stages of the mechatronic design process;
2. explain what happens at each stage, and why that order;
3. say what the feedback loops are for, and what hardware-in-the-loop testing adds.

## What the design process is
<!-- bite: b3f38554-b6b3-4c1b-b7b3-51546edede9b -->

Designing a mechatronic product is not "think of it, then build it". It is a sequence: understand the need, sketch a concept, build a rough mathematical model, choose sensors and actuators, build a detailed model, design the control, optimise, then prototype and deploy — with **feedback loops** that send you back to re-model whenever the optimisation shows the concept will not meet the need.

The whole process splits into three phases: **modelling and simulation**, **prototyping**, and **deployment and life cycle**. We will walk it stage by stage.

## Seeing the whole flow
<!-- bite: cfaccab4-a4fa-44c4-ad6f-42efddb92a9c -->

Here is the full process in one picture — the three phases top to bottom, with the feedback arrows that make it a loop. Keep it in view as we walk the stages.

![The mechatronic design process as a vertical flow: recognition of the need, conceptual design and functional specification, first-principle modular mathematical modelling, sensor and actuator selection, detailed modular mathematical modelling, control system design, design optimisation, then prototyping by hardware-in-the-loop simulation and finally deployment and life cycle, with dashed feedback arrows from design optimisation back to the modelling and conceptual-design stages](images/mecha-design-process.svg)

## 1. The modelling and simulation phase
<!-- bite: 40d9c1f9-0aee-4fec-8dc7-8ffdf780077c -->

This is the phase you do **before cutting any metal** — everything here is on paper and in simulation, which is cheap to change.

1. **Recognition of the need.** State the problem the product must solve. *Assembly line:* "parts arrive on a belt and must be picked, placed and fastened, 600 per hour, with no human in the danger zone."
2. **Conceptual design and functional specification.** Sketch the concept and write down, in measurable terms, what it must do. *Assembly line:* a gantry with two robot arms and a vision camera; spec of reach, speed, payload, cycle time.
3. **First-principle modular mathematical modelling.** Build a rough model of each module from physics — forces, masses, speeds — just good enough to size things. "Modular" means you model each part (arm, belt, gripper) on its own so you can swap one without redoing the rest.
4. **Sensor and actuator selection.** Now that the rough model tells you the forces and speeds, choose the sensors and actuators that can meet them. *Assembly line:* motors with enough torque for the arm's model, encoders with enough resolution for the placement accuracy. (This is where the sensor datasheet, a lesson of its own, earns its keep.)
## 1. The modelling phase: from parts to control
<!-- bite: f36b67dd-6d37-4243-944d-23e936dd4061 -->

With the sensors and actuators chosen, the modelling phase finishes with three more stages:

5. **Detailed modular mathematical modelling.** With real parts chosen, refine the model with their actual numbers — the motor's true torque curve, the sensor's true noise.
6. **Control system design.** Design the control laws that will make it behave — the arm moving smoothly to each point, the line staying in time. This uses the signals-and-systems element.
7. **Design optimisation.** Tune the whole design against the spec: faster, cheaper, lighter, more reliable. If it cannot meet the spec, you **feed back** to re-model, or even back to the concept.

Those dashed arrows are the point: the process is a **loop, not a straight line**. Optimisation that fails sends you back to modelling, and sometimes all the way back to the concept. That is cheaper than finding out after you have built it.

## 2. Prototyping: hardware-in-the-loop
<!-- bite: 7740e69a-a8c3-4b4e-be6a-d9efe50da9da -->

Once the design survives optimisation on paper, you build a prototype — but you do not test it against the whole real line straight away. You use **hardware-in-the-loop (HIL) simulation**: the real control hardware runs, but the rest of the plant it controls is a *simulated model* instead of real machinery.

Why: it lets you test the real controller against dangerous or expensive situations — a jam, a motor fault, a part arriving wrong — safely, before the real line exists. Problems found here feed back into design optimisation again.

## 3. Deployment and life cycle
<!-- bite: 662c1c60-00d9-4c27-b25c-fbb05003c7a7 -->

The last phase is putting it into service and keeping it there. It has two parts:

1. **Deployment of the embedded software** — the tested control software is loaded onto the real product and it goes into service.
2. **Life-cycle optimisation** — the product is designed not just to work on day one but across its whole life: **delivery, reliability, maintainability, serviceability, upgradeability and disposability**. A mechatronic product that cannot be maintained or upgraded is a poor design even if it works.

So the full arc is: understand → model → choose parts → model in detail → control → optimise (looping back as needed) → prototype with HIL → deploy → support across the life cycle.

## Terms used in this lesson
<!-- bite: 87590b91-929b-4bd4-825a-b8d65219f252 -->

1. **Functional specification**: this is the written, measurable statement of what the product must do — speeds, loads, accuracies, cycle times — agreed before detailed design. It is what "done" is measured against.
2. **First-principle model**: this is a model built from the underlying physics (Newton's laws, circuit laws) rather than from measured data. It is used early, when you have no real parts to measure yet.
3. **Modular modelling**: this is modelling each part of the system separately, so one part can be changed, improved or re-sized without redoing the model of the whole.
4. **Hardware-in-the-loop (HIL) simulation**: this is testing where the real control hardware runs against a *simulated* version of the machinery it controls, so you can test faults and limits safely before the real plant exists.
5. **Life-cycle optimisation**: this is designing for the product's whole life — how it is delivered, kept reliable, maintained, serviced, upgraded and finally disposed of — not just for its first day of working.

## Common pitfalls and traps
<!-- bite: 3db55283-c51f-4099-8627-2de3d30397d7 -->

- **Drawing it as a straight line.** The feedback loops from optimisation back to modelling (and sometimes to the concept) are part of the process, and the exam diagram should show them.
- **Selecting sensors and actuators too early.** You select them *after* the first-principle model, because the model is what tells you the forces, speeds and accuracies they must meet. Choosing parts before modelling is guessing.
- **Forgetting the life-cycle phase.** Many answers stop at "build the prototype". Deployment and life-cycle optimisation (reliability, maintainability, upgradeability, disposability) are explicitly part of the process.
- **Confusing HIL with full field testing.** In HIL the *plant* is simulated and only the *controller* is real hardware. That is what makes it safe for testing faults.

## Check your understanding
<!-- bite: 0bb52a01-9bac-4c5e-befb-ac9298c61d76 -->

Try each one before you open the answer.

1. <!-- q: mcq id="da9f24ad" -->
   In the mechatronic design process, when are the sensors and actuators selected?

   - [ ] Before any modelling, so the model can use their exact numbers.
   - [x] After the first-principle model, which tells you the forces, speeds and accuracies they must meet.
   - [ ] After the prototype is built.
   - [ ] During deployment.

   <details><summary>Answer</summary>

   After the first-principle modular model. That rough model gives you the required forces and speeds, which are what you select the parts against. A detailed model with their real numbers then follows.

   </details>

2. <!-- q: gap id="36970323" answers="modelling|modeling|the concept|conceptual design" -->
   The dashed feedback arrows in the design-process diagram run from the design-optimisation stage back to the ___ stages, so a design that fails to meet the specification is reworked rather than built as-is.

   <details><summary>Answer</summary>

   Back to the modelling (and conceptual-design) stages. The process is a loop: failed optimisation sends you back to re-model, which is far cheaper than discovering the problem after building.

   </details>

3. <!-- q: mcq id="3cbc0ab2" -->
   What is distinctive about hardware-in-the-loop (HIL) simulation?

   - [ ] Both the controller and the plant are simulated in software.
   - [ ] Both the controller and the plant are the real hardware.
   - [x] The controller is the real hardware, but the plant it controls is simulated.
   - [ ] Neither the controller nor the plant exists yet.

   <details><summary>Answer</summary>

   In HIL the real control hardware runs against a simulated plant. That is what lets you test faults, jams and limits safely before the real machinery is built.

   </details>

4. <!-- q: mcq id="d9c9a492" -->
   Which of these belong to the deployment and life-cycle phase? (choose all that apply)

   - [x] Reliability
   - [x] Maintainability
   - [x] Upgradeability
   - [x] Disposability
   - [ ] Control-law design

   <details><summary>Answer</summary>

   Reliability, maintainability, upgradeability and disposability are all life-cycle concerns. Control-law design happens earlier, in the modelling-and-simulation phase.

   </details>

5. <!-- q: open id="e5806ccf" -->
   You are designing an automated assembly line. Walk from "recognition of the need" to "control system design", naming each stage and giving one concrete thing you would decide at it. Then explain why the order matters — why modelling comes before part selection.

   <details><summary>Answer</summary>

   Recognition of need: state the throughput and safety requirement (600 parts/hour, no human in the danger zone). Conceptual design and functional specification: choose a two-arm gantry concept and write measurable reach, speed and cycle-time targets. First-principle modular modelling: model each arm's forces and speeds from physics. Sensor and actuator selection: pick motors and encoders that meet those modelled forces and accuracies. Detailed modular modelling: refine the model with the chosen parts' real numbers. Control system design: design the laws that move each arm smoothly and keep the line in time. The order matters because the model is what tells you the forces, speeds and accuracies the parts must meet — selecting parts first would be guessing, and would force you to re-model anyway.

   </details>

## Before moving on
<!-- bite: 60c115bc-8244-4415-9e96-7e64711c4bb9 -->

You are done when you can draw the design process with its feedback loops, name every stage and its job, and explain why selection follows modelling and what HIL adds.

Recap: modelling-and-simulation phase (need → concept/spec → first-principle model → select sensors/actuators → detailed model → control design → optimise, looping back), then prototyping with hardware-in-the-loop, then deployment and life-cycle optimisation.

Next, [[mechatronics/04-examples-of-mechatronic-systems|Examples of Mechatronic Systems]] grounds all of this in real products — including the four systems that make a modern car mechatronic.

## Related
<!-- bite: cabaa4ba-cdee-4cef-8958-77a983a43386 -->

- [[mechatronics/02-the-five-elements-of-mechatronics|The Five Elements of Mechatronics]]: the elements this process puts to work.
- [[mechatronics/07-choosing-and-classifying-sensors|Choosing and Classifying Sensors]]: the sensor-selection stage in depth.
- [[engineering-design-and-prototyping/16-system-architecture-and-mbse|System Architecture and MBSE]]: a wider engineering-design view of the same arc.

## About this lesson
<!-- bite: 23e01854-5a33-4776-bda2-a0dc9301799f -->

**Level:** introductory, no maths. It covers the stages of the mechatronic design process, the feedback loops, and hardware-in-the-loop testing, with an automated assembly line as the running example. It is lesson 3 of section A; read [[mechatronics/02-the-five-elements-of-mechatronics|the five elements]] first and [[mechatronics/04-examples-of-mechatronic-systems|examples]] next.

**Source:** University of Lagos SSG 415 lecture notes (mechatronic design-process stages, prototyping and deployment/life-cycle) and the SSG 415 exam question banks (Question 1c, "with the aid of a diagram describe the Mechatronic Design Process"; 2024/25 and 2025/26 on designing an automated assembly line).
