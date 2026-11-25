# Mechatronics

## What mechatronics is

**Mechatronics is the field of building products that join moving mechanical parts, electronics, control and software into one working system.**

A washing machine, a car's anti-lock brakes, a drone, a 3D printer, an automatic gate, a robot arm on an assembly line — all of these are mechatronic. None of them is "just" a machine, "just" a circuit, or "just" a program. The mechanical parts carry the load and do the physical work, the electronics sense the world and switch power, and the software decides what to do. The whole point is that these pieces are designed *together*, so the result does something none of them could do alone.

This course is the mechatronics and robotic-systems course taught at the University of Lagos (SSG 415, and the robotics follow-on SSG 515/519). It starts from what mechatronics is and the design process, moves through sensors, the mathematics of modelling a physical system and turning it into a transfer function, the electrical analogies that let you reason about a mechanical system as a circuit, a little digital logic, and measurement uncertainty. The last section is robotic systems: kinematics, the real numerical methods used to solve inverse kinematics, redundancy and singularities, parallel manipulators, grasping, and moving safely around obstacles.

## What you'll be able to do

By the end you will be able to:

- say what mechatronics is, name its five fundamental elements, and walk a design from a need to a working product;
- read a sensor datasheet and choose a sensor from its accuracy, resolution, range and the rest;
- take a mechanical system (masses, springs, dampers), draw its free-body diagram and mechanical network, and write its differential equations;
- turn those equations into a transfer function, and reduce a block diagram to one;
- model a mechanical system as an equivalent electrical circuit using the force–voltage and force–current analogies;
- minimise a control function with a Karnaugh map, including don't-care conditions;
- work out the uncertainty in a measured quantity from the uncertainties of its parts;
- solve forward and inverse kinematics for a robot arm, by hand and with the four numerical methods (Newton–Raphson, Jacobian transpose, pseudoinverse, damped least squares);
- recognise redundancy and singularities, analyse a parallel manipulator, and reason about grasping and obstacle avoidance.

## Where to start

**Before you start:** some calculus (differentiation and integration), basic trigonometry, and a little linear algebra (vectors and matrices). The modelling sections use the Laplace transform; it is introduced where it is first needed, so you do not need it in advance. The robotics section leans on matrices and trig more heavily.

Read in order within a section. The first two sections (fundamentals and sensors) need almost no maths. The modelling and analogy sections are the mathematical core of SSG 415 and build strictly on each other. The robotics section is a separate course and can be read on its own once you are comfortable with matrices.

### A. Mechatronics fundamentals

1. [[mechatronics/01-what-mechatronics-is|01 — What Mechatronics Is]]: where the word comes from, the synergy of mechanical, electronic, control and computing, and how the field grew from pure machines to today's integrated systems.
2. [[mechatronics/02-the-five-elements-of-mechatronics|02 — The Five Elements of Mechatronics]]: the five building blocks every mechatronic system is made of — physical modelling, sensors and actuators, signals and systems, computers and logic, and software and data acquisition.
3. [[mechatronics/03-the-mechatronic-design-process|03 — The Mechatronic Design Process]]: how a mechatronic product is actually designed, from recognising the need to hardware-in-the-loop testing and optimisation.
4. [[mechatronics/04-examples-of-mechatronic-systems|04 — Examples of Mechatronic Systems]]: real mechatronic systems, including the four systems that make a modern car mechatronic, and what the integration buys you in each.

### B. Sensors and measurement

5. [[mechatronics/05-sensors-and-transducers|05 — Sensors and Transducers]]: what a sensor and a transducer are, the measurement loop they sit in, and the chain from a measurand to an application.
6. [[mechatronics/06-sensor-performance-characteristics|06 — Sensor Performance Characteristics]]: sensitivity, resolution, accuracy, precision, repeatability, linearity and the rest — the numbers that tell you whether a sensor is good enough.
7. [[mechatronics/07-choosing-and-classifying-sensors|07 — Choosing and Classifying Sensors]]: the four ways sensors are classified, the criteria you select on, and why the datasheet is the document that decides it.
8. [[mechatronics/15-measurement-uncertainty|15 — Measurement Uncertainty and Error Propagation]]: working out the uncertainty in a result from the uncertainties of the things you measured to get it.

### C. Modelling mechanical systems

9. [[mechatronics/08-mechanical-system-elements|08 — Mechanical System Elements]]: the mass, spring and damper (and their rotational cousins), the three ideal elements every mechanical model is built from.
10. [[mechatronics/09-translational-systems|09 — Translational Systems: Free-Body Diagrams and Networks]]: drawing the free-body diagram and mechanical network of a mass–spring–damper system and writing its differential equation.
11. [[mechatronics/10-transfer-functions|10 — Transfer Functions]]: the Laplace transform, the impulse response, the transfer function, and the step-by-step procedure for deriving one from a system's equations.
12. [[mechatronics/11-rotational-systems|11 — Rotational Systems]]: the same ideas for discs, shafts and torques, through to the transfer function of the three-inertia class example.
13. [[mechatronics/16-block-diagram-reduction|16 — Block Diagram Reduction]]: reducing a block diagram of summing junctions and feedback loops to a single transfer function.

### D. Electrical analogies

14. [[mechatronics/12-electrical-systems-and-analogies|12 — Electrical Systems and the Two Analogies]]: modelling RLC circuits, and the force–voltage and force–current analogies that map a mechanical system onto a circuit.
15. [[mechatronics/13-two-mass-coupled-systems|13 — Two-Mass Coupled Systems and Analogies]]: the two-train-car system worked end to end — equations, both analogies, networks and transfer function.

### E. Digital logic

16. [[mechatronics/14-karnaugh-maps|14 — Karnaugh Maps and Boolean Minimisation]]: writing a controller's logic as a Boolean function and minimising it with a Karnaugh map, don't-cares and all.

### F. Robotic systems

17. [[mechatronics/17-serial-and-parallel-manipulators|17 — Serial and Parallel Manipulators]]: the two ways to build a robot arm, and what each is good and bad at.
18. [[mechatronics/18-forward-and-inverse-kinematics|18 — Forward and Inverse Kinematics]]: working out where the hand is from the joint angles, and the much harder reverse.
19. [[mechatronics/19-numerical-inverse-kinematics|19 — Numerical Methods for Inverse Kinematics]]: the four methods that solve inverse kinematics when there is no formula — Newton–Raphson, Jacobian transpose, pseudoinverse, and damped least squares.
20. [[mechatronics/20-redundancy-and-singularities|20 — Redundancy and Singularities]]: having more joints than you need, and the configurations where an arm loses the ability to move.
21. [[mechatronics/25-manipulator-performance-evaluation|25 — Manipulator Performance Evaluation]]: scoring an arm with numbers — how much space it reaches, how well its joints are used, and how its joint errors show up at the hand.
22. [[mechatronics/21-parallel-manipulators|21 — Parallel Manipulators]]: analysing a platform held by several legs, and its two kinds of singularity.
23. [[mechatronics/22-robot-dynamics|22 — Robot Dynamics: Newton–Euler and Lagrangian]]: the forces and torques behind the motion, by two methods.
24. [[mechatronics/23-multi-fingered-grasping|23 — Multi-Fingered Grasping]]: holding an object with several fingers, and checking the grasp will not slip.
25. [[mechatronics/24-compliant-motion-and-obstacle-avoidance|24 — Compliant Motion and Obstacle Avoidance]]: moving while touching the world, and planning a path around an obstacle with a potential field.

## Related

- [[robotics/index|Robotics]]: the general robotics course. It covers kinematics, Jacobians, dynamics and SLAM for their own sake; this course covers the robotics that sits inside the University of Lagos mechatronics syllabus, with its own worked examples and exam questions.
- [[control-theory/index|Control Theory]]: the theory of transfer functions, block diagrams and feedback in depth. This course uses those tools; that one explains them.
- [[engineering-design-and-prototyping/24-embedded-electronics-and-mechatronics|Embedded Electronics and Mechatronic Integration]]: mechatronics from the product-design side — ADCs, PWM, motor drivers and battery life.

## About this course

**Level:** second/third-year undergraduate engineering. Built from the author's University of Lagos course materials for **SSG 415 (Mechatronics & Robotic Systems)** and **SSG 515 / SSG 519 (Mechanics and Robotic Systems II)**: lecture notes and slides by Dr John Ogbemhe, whiteboard worked examples, Mechatronics Class Example 1, the Sensors and Transducers notes, the Topic 1–3 deep dives, and the past-exam, tutorial (T_3 to T_6) and quiz question banks from 2020/21 through 2025/26.

**What is here:** 25 lessons, about 62,000 words, with 60 diagrams. Sections A–E are SSG 415; section F is the SSG 515/519 robotics follow-on. Every end-of-lesson quiz is built from the real question banks or from fresh numbers in the same style, so the practice here is the practice the course sets.

**How it is checked:** every calculated number, transfer function, minimal Boolean expression and robotics result is computed and asserted by the diagram scripts before any picture is drawn — `scripts/diagrams/mechatronics.py` (sections A–B), `mechatronics_models.py` (sections C–D: transfer functions, block diagrams and analogous circuits, solved numerically), `mechatronics_logic.py` (section E: a Quine–McCluskey solver) and `mechatronics_robotics.py` (section F: all four inverse-kinematics methods, parallel-manipulator velocities, Lagrangian dynamics, grasp indices, potential fields and the workspace). Run them from the vault root.

**Judgement calls worth knowing:**

1. The RLC-impedance uncertainty question gives no frequency; lesson 15 assumes 50 Hz mains and says so.
2. The robotic-arm Karnaugh-map function (2024/25, 2025/26) minimises to F = 1 once the don't-cares are used; lesson 14 explains what that means and when it is unsafe.
3. Quiz 1's block diagrams were drawn from written descriptions of the figures; figure 5's description was too unclear to draw reliably, so lesson 16 teaches the method that solves it rather than a possibly wrong answer.
4. A few worked values differ from the notes in the last digit (for example Newton–Raphson's first steps in tutorials Q1 and Q7, and the parallel-manipulator joint speeds); the lessons give the exactly computed values and say where the notes rounded.
5. The parallel-manipulator model (one rigid link per leg, platform at the centroid of the tips) and the T_4 and T_5 indices are the course's simplified teaching measures; lessons 21, 23 and 25 label them as such and say what a full treatment adds.
6. The T_4 tutorial (manipulator performance) became lesson 25, added after the others; read it after lesson 20.
