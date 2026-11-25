---
id: 7096328f-ece6-467c-b213-50b8b8ba1f41
---

# The Five Elements of Mechatronics

**Every mechatronic system is built from five fundamental elements: physical-system modelling, sensors and actuators, signals and systems, computers and logic, and software and data acquisition.**

In the last lesson "integration" was still a slogan. This lesson turns it into a parts list: ask "what is inside a mechatronic product, in engineering terms?", and these five headings are the answer every time.

## Before you start
<!-- bite: 05dd257f-3a9c-4c83-89aa-1b250cc37f71 -->

You should have met the definition of mechatronics and the idea of synergy ([[mechatronics/01-what-mechatronics-is|What Mechatronics Is]]). No maths here.

After this lesson you will be able to:

1. list the five fundamental elements of mechatronics in order;
2. say in one plain sentence what each element contributes;
3. point to each element in a real system, such as a robotic arm.

## What the five elements are
<!-- bite: 15855ece-de88-4798-9677-03b9d1d1b73c -->

A mechatronic system always needs five things: a way to **model the physical parts**, **sensors and actuators** to feel and act on the world, the **signals-and-systems** theory to understand and control the behaviour, **computers and logic** to do the deciding, and **software and data acquisition** to run it all and move numbers between the real world and the computer.

We will use one running example the whole way through: **a robotic arm on an assembly line**, because the 2024/25 exam asks you to place the five elements in exactly that design. Keep the arm in mind for each element.

## 1. Physical systems modelling
<!-- bite: 863ffb91-43f0-4381-aa28-6e1e87245a6e -->

This is the element that describes the **mechanical and physical parts in mathematics**, so you can predict how they will move before you build them.

It covers the mechanics of solids, translational and rotational motion, fluid systems, thermal systems, electromagnetics, micro and nano systems including MEMS, and the physical-system analogies that let you treat one kind of system like another. (Those analogies are a whole section of this course later.)

*On the arm:* modelling the links, joints and loads — how heavy each link is, how its inertia resists a motor, how the arm sags under a payload. You cannot size the motors until you have this model.

## 2. Sensors and actuators
<!-- bite: 34796401-4371-4391-b044-2256449e3d3d -->

This is the element that **connects the system to the physical world**: sensors read the world in, actuators push action back out. It is the pair of doorways between the metal and the maths.

**Sensors** measure things: linear and rotational position, acceleration, force, torque and pressure, flow, temperature, ranging and proximity, light, image and vision, fibre-optic, and micro/nano sensors. **Actuators** make things happen: electro-mechanical (motors, solenoids), piezoelectric, pneumatic and hydraulic, and micro/nano actuators.

*On the arm:* encoders on each joint sensing angle, a force sensor in the wrist sensing contact; electric motors at the joints and a gripper actuator at the hand. Sensors and actuators get three lessons of their own next.

## 3. Signals and systems
<!-- bite: 3da45906-f37f-4602-8a18-91b43c11735d -->

This is the element that holds the **theory for understanding and controlling behaviour over time** — how a system responds, and how to make it respond the way you want.

It covers modelling of signals and systems, the response of dynamic systems, root locus and frequency response, state-variable methods, stability, controllability and observability, observers and Kalman filters, digital filters, optimal, adaptive and nonlinear control, and the intelligent-control family (neural networks, fuzzy systems, identification, design optimisation).

*On the arm:* the control law that takes "I want the hand *there*" and commands joint torques that get it there smoothly, without overshoot or oscillation. This is where transfer functions and control theory live.

## 4. Computers and logic systems
<!-- bite: cb97d16f-766f-4c90-a706-e50cc22b64d2 -->

This is the element that does the **deciding and the digital housekeeping** — the actual computing hardware and its logic.

It covers digital logic, logic-systems design, synchronous and asynchronous sequential logic, communication systems, fault detection, computer architectures and microprocessors, system interfaces, PLCs, and embedded control computers.

*On the arm:* the embedded controller or PLC that runs the program, the digital logic that interlocks the gripper so it cannot close on a person, the bus that carries messages between joints. The Boolean-logic and Karnaugh-map lesson later lives under this element.

## 5. Software and data acquisition
<!-- bite: 7197e548-f1b6-403e-b1a2-2da2798cc60c -->

This is the element that **moves information between the real world and the computer, and runs the programs** that tie everything together.

It covers data-acquisition systems, transducers and measurement systems, analogue-to-digital and digital-to-analogue conversion, amplifiers and signal conditioning, computer-based instrumentation, software engineering, and data recording.

*On the arm:* the A/D converters that turn each sensor's voltage into a number the computer can use, the D/A side that turns commands back into drive signals, and the software that schedules it all and logs what happened. Note how this element overlaps element 2 — the sensor is the doorway, data acquisition is the machinery that carries the signal through it. That overlap is the synergy from lesson 1, showing up as a parts list.

## Terms used in this lesson
<!-- bite: 7ec0f379-90cb-4ed4-83a7-9bb0d50e5fb1 -->

1. **Element (of mechatronics)**: here it means one of the five fundamental building blocks a mechatronic system is made of. It is a category of engineering work, not a physical component.
2. **Data acquisition**: this is the business of getting real-world measurements into a computer — reading a sensor, conditioning its signal, and converting it to a number. Often shortened to "DAQ".
3. **Signal conditioning**: this is adjusting a raw sensor signal — amplifying it, filtering out noise, shifting its range — so it is clean and in the right form before it reaches the converter.
4. **A/D and D/A conversion**: A/D turns a continuous voltage into a digital number a computer can read; D/A turns a digital number back into a voltage that can drive hardware. They are the translators between the analogue world and the digital computer.

## Common pitfalls and traps
<!-- bite: bcc23555-412d-479d-9a7c-10cfe17ae14e -->

- **Missing element 3 (signals and systems).** Students often jump from sensors straight to computers and forget the control theory in between. Without it you can read and switch, but you cannot make the system *behave*.
- **Confusing element 2 with element 5.** Sensors and actuators (2) are the devices; data acquisition and conversion (5) are how their signals get into and out of the computer. The exam lists them separately, so keep them separate.
- **Listing components instead of elements.** "Motor, wire, chip" is a component list. The five elements are categories of engineering: modelling, sensing/actuating, signals-and-systems, computing/logic, software/DAQ.

## Check your understanding
<!-- bite: 0a8f19a6-1201-4bb5-935c-4571449583b1 -->

Try each one before you open the answer.

1. <!-- q: mcq id="0bfde15a" -->
   Which of the following is **not** one of the five fundamental elements of mechatronics?

   - [ ] Physical systems modelling
   - [ ] Sensors and actuators
   - [x] Marketing and sales
   - [ ] Software and data acquisition

   <details><summary>Answer</summary>

   Marketing and sales. The five are physical-systems modelling; sensors and actuators; signals and systems; computers and logic systems; and software and data acquisition.

   </details>

2. <!-- q: gap id="aaf94623" answers="sensors;actuators" -->
   The element that connects a mechatronic system to the physical world does so with two kinds of device: ___ read the world in, and ___ push action back out.

   <details><summary>Answer</summary>

   Sensors read in; actuators act out. Together they are element 2, the doorways between the metal and the maths.

   </details>

3. <!-- q: mcq id="dc2ac2f1" -->
   On a robotic arm, the control law that turns "move the hand to this point" into smooth joint torques belongs to which element?

   - [ ] Physical systems modelling
   - [x] Signals and systems
   - [ ] Computers and logic systems
   - [ ] Software and data acquisition

   <details><summary>Answer</summary>

   Signals and systems — this is where dynamic response, stability and control laws live. The physical model (element 1) tells you how the arm moves; signals and systems (element 3) decides how to drive it.

   </details>

4. <!-- q: mcq id="6535d8fc" -->
   An encoder produces a voltage, which is amplified, filtered and turned into a number the controller reads. Which element covers the amplifying, filtering and number-conversion?

   - [ ] Sensors and actuators
   - [x] Software and data acquisition
   - [ ] Signals and systems
   - [ ] Physical systems modelling

   <details><summary>Answer</summary>

   Software and data acquisition — signal conditioning and A/D conversion are its job. The encoder itself is element 2; getting its signal into the computer is element 5.

   </details>

5. <!-- q: open id="aed77ba5" -->
   Pick any mechatronic system you know (a drone, a washing machine, a 3D printer) and name one concrete part or task for each of the five elements. Then say which two elements overlap most, and why.

   <details><summary>Answer</summary>

   Example (3D printer): (1) physical modelling — the mass and friction of the moving print head; (2) sensors and actuators — endstop switches and the stepper motors; (3) signals and systems — the motion controller that keeps the head on the path; (4) computers and logic — the embedded board running the firmware; (5) software and data acquisition — reading the thermistor's voltage and converting it to a temperature. Elements 2 and 5 overlap most: the sensor is the device, and data acquisition is the chain that carries its signal into the computer — they are two views of the same doorway.

   </details>

## Before moving on
<!-- bite: b4908b04-f7f2-4785-88d4-15f09004ea42 -->

You are done when you can list the five elements from memory, give each a one-line job, and point to all five in a system you choose.

Recap: (1) physical-systems modelling, (2) sensors and actuators, (3) signals and systems, (4) computers and logic systems, (5) software and data acquisition. They are categories of engineering, not components, and they overlap — which is the synergy of lesson 1 made concrete.

Next, [[mechatronics/03-the-mechatronic-design-process|The Mechatronic Design Process]] shows how these five elements are actually brought together to design a product, step by step from a need to a tested prototype.

## Related
<!-- bite: b9f7b9f4-bb06-42ef-a914-c1d8da5f9a85 -->

- [[mechatronics/01-what-mechatronics-is|What Mechatronics Is]]: the definition and synergy these elements make concrete.
- [[mechatronics/05-sensors-and-transducers|Sensors and Transducers]]: element 2 in depth.
- [[mechatronics/10-transfer-functions|Transfer Functions]]: a core tool of element 3.

## About this lesson
<!-- bite: 12e05e8a-6376-4498-b48b-1e9b3dc53353 -->

**Level:** introductory, no maths. It covers the five fundamental elements of mechatronics, what each contributes, and how to spot them in a real system, using a robotic arm as the running example. It is lesson 2 of section A; read [[mechatronics/01-what-mechatronics-is|What Mechatronics Is]] first and [[mechatronics/03-the-mechatronic-design-process|the design process]] next.

**Source:** University of Lagos SSG 415 lecture notes (the five fundamental elements and their contents) and the SSG 415 exam question banks (Question 1b: "describe the five fundamental elements"; 2024/25 Question 1b on the robotic-arm design).
