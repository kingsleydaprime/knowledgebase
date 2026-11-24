# Control Theory

## What control theory is

Control theory is the maths of making a system do what you want, automatically, by measuring it and correcting it over and over.

Think of a room thermostat. It measures the temperature, compares it with what you set, and switches the heating on or off to close the gap. That's a **feedback loop**: measure, compare, correct, again and again. The same idea keeps a car's cruise control at a steady speed, a drone level in the wind, a robot arm on its path and a rocket upright.

The surprise is how easily it goes wrong. Correct too hard and the system overshoots and swings back and forth; correct too slowly and it never quite gets there; and a delay in measuring can make a well-meant loop shake itself apart. Control theory gives you the tools to predict that, and to design loops that are both fast and steady.

Software engineers meet it more than they realise: the internet slowing senders down when it's busy, cloud services adding servers under load, and rate limiting are all feedback loops with the same problems.

## What you'll be able to do

By the end you will be able to:
- write the equations of a circuit, a machine or a motor, and turn them into a transfer function;
- simplify a diagram of a whole control system into one formula;
- predict how a system responds: how fast, how much it overshoots, and how close it gets to its target;
- tune a PID controller, the most common controller in the world, and write it as code that works on real hardware;
- tell whether a loop is stable, how much safety margin it has, and design a compensator to fix it;
- describe systems with many inputs and outputs using matrices, and estimate what you can't measure;
- design the best controller for a stated goal, including when the actuators have limits;
- analyse systems that aren't linear, and prove they're stable.

## Where to start

**Before you start:** [[mathematics/06-calculus/02-calculus-1/01-preview/01-preview|calculus]], including derivatives, and complex numbers. From lesson 30 on you also need [[mathematics/04-linear-algebra/index|linear algebra]] (matrices and eigenvalues).

**Start with 01** and read in order. One example runs through most of the subject: a car's cruise control, then its suspension, then a pendulum for the nonlinear part. Parts 2 to 7 (lessons 03 to 29) are classical control and build on each other; parts 8 to 10 are modern control; part 11 is nonlinear systems.

If you're studying for a university control course, parts 2 to 7 follow the usual first-course syllabus: modelling, block diagrams, signal flow graphs, time response, steady-state error, Routh, root locus, Bode and Nyquist. The [[control-theory/optimal-control-problem-bank|optimal control problem bank]] has every problem from the author's optimal-control sheets, each pointing to its lesson.

### Part 1: Getting oriented

1. [[control-theory/01-what-control-theory-is-1|01 — What Control Theory Is 1: The Feedback Loop]]: the feedback loop: open versus closed loops, the names of each part, and what feedback does to a disturbance.
2. [[control-theory/02-what-control-theory-is-2|02 — What Control Theory Is 2: Costs, Feedforward and Requirements]]: what feedback costs, acting ahead with feedforward, and the six numbers a good loop must meet.

### Part 2: Modelling physical systems

3. [[control-theory/03-modelling-1|03 — Modelling 1: From Physics to Transfer Functions]]: turning physics into a differential equation, then into a transfer function, and what poles and zeros mean.
4. [[control-theory/04-modelling-2|04 — Modelling 2: Transfer Functions of Electrical Circuits]]: transfer functions of circuits from impedances, mesh analysis and op-amps.
5. [[control-theory/05-modelling-3|05 — Modelling 3: Translational Mechanical Systems]]: masses, springs and dampers: writing the equation at each moving point.
6. [[control-theory/06-modelling-4|06 — Modelling 4: Rotational Systems, Gears and the DC Motor]]: rotating systems, gear trains and the DC motor.
7. [[control-theory/07-modelling-5|07 — Modelling 5: Linearisation and System Identification]]: making a curved plant straight near one operating point, and measuring a model you can't derive.

### Part 3: Block diagrams and signal flow graphs

8. [[control-theory/08-block-diagrams-1|08 — Block Diagrams 1: Connections and the Feedback Rule]]: drawing a system as connected blocks, and the series, parallel and feedback rules.
9. [[control-theory/09-block-diagrams-2|09 — Block Diagrams 2: Reduction Rules]]: reducing a complicated diagram to one block by moving summing and take-off points.
10. [[control-theory/10-block-diagrams-3|10 — Block Diagrams 3: Multiple Inputs and Disturbances]]: systems with a reference and a disturbance, handled one input at a time.
11. [[control-theory/11-signal-flow-graphs-1|11 — Signal Flow Graphs 1: Nodes, Branches and Loops]]: drawing a system as nodes and arrows, and listing its paths and loops.
12. [[control-theory/12-signal-flow-graphs-2|12 — Signal Flow Graphs 2: Mason's Gain Formula]]: Mason's formula: the transfer function in one step from a signal flow graph.

### Part 4: Time response and steady-state error

13. [[control-theory/13-time-response-1|13 — Time Response 1: First- and Second-Order Systems]]: how first- and second-order systems respond to a step, and the numbers you design against.
14. [[control-theory/14-time-response-2|14 — Time Response 2: Dominant Poles, Delay and Step Tests]]: when high-order plants act like second-order ones, why delay is so harmful, and models from step tests.
15. [[control-theory/15-steady-state-error-1|15 — Steady-State Error 1: Test Inputs and Error Constants]]: the error left once a response settles, and how the number of integrators decides it.
16. [[control-theory/16-steady-state-error-2|16 — Steady-State Error 2: Non-Unity Feedback and Disturbances]]: error with a sensor in the feedback path, and error caused by disturbances.

### Part 5: PID control

17. [[control-theory/17-pid-control-1|17 — PID Control 1: The Three Terms]]: what P, I and D each do, the windup bug, and why D is filtered.
18. [[control-theory/18-pid-control-2|18 — PID Control 2: Tuning and Implementation]]: choosing the three gains, and a working PID program with every practical fix.

### Part 6: Stability and the root locus

19. [[control-theory/19-stability-1|19 — Stability 1: What Stability Means and Routh–Hurwitz]]: what makes a loop stable, and testing it without solving for the poles.
20. [[control-theory/20-stability-2|20 — Stability 2: Routh's Special Cases and Stability Design]]: the two ways the Routh table breaks, and finding the range of a gain that keeps a loop stable.
21. [[control-theory/21-root-locus-1|21 — Root Locus 1: Sketching the Locus]]: drawing where the closed-loop poles go as the gain rises.
22. [[control-theory/22-root-locus-2|22 — Root Locus 2: Test Points, Departure Angles and Positive Feedback]]: testing points, departure angles, finding the gain, and the positive-feedback locus.
23. [[control-theory/23-root-locus-design|23 — Design by Root Locus: Lead and Lag Compensators]]: reshaping the locus with lead and lag compensators to meet a specification.

### Part 7: Frequency response and Nyquist

24. [[control-theory/24-frequency-response-1|24 — Frequency Response 1: Bode Plots]]: how a system treats slow and fast wiggles, drawn as Bode plots.
25. [[control-theory/25-frequency-response-2|25 — Frequency Response 2: Loop Shaping, Bandwidth and Margins]]: shaping a loop by its Bode plot, and the gain and phase margins that say how safe it is.
26. [[control-theory/26-frequency-response-3|26 — Frequency Response 3: Reading Bode Plots and Design by Gain Adjustment]]: reading a Bode plot backwards, setting margins by choosing the gain, and closed-loop bandwidth.
27. [[control-theory/27-nyquist-1|27 — Nyquist 1: The Nyquist Criterion]]: deciding stability by counting how often one curve goes around −1.
28. [[control-theory/28-nyquist-2|28 — Nyquist 2: Sketching Polar and Nyquist Plots]]: sketching polar and Nyquist plots by hand.
29. [[control-theory/29-nyquist-3|29 — Nyquist 3: Uncertainty and Fundamental Limits]]: how wrong a model can be, and the limits no controller can beat.

### Part 8: State space and estimation

30. [[control-theory/30-state-space-1|30 — State Space 1: States and the State Equation]]: describing a system by a list of numbers, its state, and matrix equations.
31. [[control-theory/31-state-space-2|31 — State Space 2: Solution, Eigenvalues and Conversions]]: solving the state equation, and why the eigenvalues are the poles.
32. [[control-theory/32-state-space-3|32 — State Space 3: From Transfer Function to State Space]]: turning a transfer function into a state-space model.
33. [[control-theory/33-state-space-4|33 — State Space 4: Solving the State Equation with Laplace]]: solving the state equation with Laplace, and diagonalising.
34. [[control-theory/34-controllability-and-observability|34 — Controllability and Observability]]: whether the inputs can steer, and the sensors see, every part of a system.
35. [[control-theory/35-pole-placement|35 — Pole Placement]]: feeding back every state to put the poles exactly where you choose.
36. [[control-theory/36-observers|36 — Observers]]: estimating the states you can't measure with a model that corrects itself.
37. [[control-theory/37-kalman-filter|37 — The Kalman Filter]]: the best estimator when sensors and model are both noisy.

### Part 9: Optimal control

38. [[control-theory/38-optimal-control-1|38 — Optimal Control 1: The Performance Index and the Discrete Recipe]]: choosing the inputs that make a cost smallest, and the Hamiltonian recipe.
39. [[control-theory/39-optimal-control-2|39 — Optimal Control 2: Minimum-Energy Control and Deadbeat]]: reaching a target with the least effort, and the fastest possible discrete controller.
40. [[control-theory/40-optimal-control-3|40 — Optimal Control 3: The Discrete Riccati Equation]]: turning an optimal plan into feedback with the Riccati equation.
41. [[control-theory/41-optimal-control-4|41 — Optimal Control 4: Continuous Time and the Euler–Lagrange Equations]]: the same recipe for continuous-time plants.
42. [[control-theory/42-lqr|42 — LQR]]: the standard optimal controller, tuned by saying what you care about.
43. [[control-theory/43-lqg-and-mpc|43 — LQG and MPC]]: adding a Kalman filter to LQR, and model predictive control for systems with limits.

### Part 10: Digital control

44. [[control-theory/44-digital-control-1|44 — Digital Control 1: Sampling and the z-Transform]]: what running a controller on a computer does to a loop, and the z-transform.
45. [[control-theory/45-digital-control-2|45 — Digital Control 2: Discretising and Implementing a Controller]]: turning a controller into safe code, and what goes wrong on real hardware.

### Part 11: Nonlinear systems

46. [[control-theory/46-nonlinear-systems|46 — Nonlinear Systems]]: what nonlinearity is, equilibrium points, and why stability becomes local.
47. [[control-theory/47-phase-plane-1|47 — Phase Plane 1: Trajectories, Vector Fields and Isoclines]]: drawing every motion of a two-state system as curves in one picture.
48. [[control-theory/48-phase-plane-2|48 — Phase Plane 2: The Equilibria of Linear Systems]]: the six shapes a linear system's portrait can take.
49. [[control-theory/49-phase-plane-3|49 — Phase Plane 3: Linearising Around an Equilibrium]]: classifying a nonlinear system's equilibria from its linearisation, and when that fails.
50. [[control-theory/50-limit-cycles-1|50 — Limit Cycles 1: Stable, Unstable and Semi-Stable]]: self-sustaining oscillations, and their three kinds.
51. [[control-theory/51-limit-cycles-2|51 — Limit Cycles 2: Proving They Exist or Don't]]: proving an oscillation exists or can't exist, without solving anything.
52. [[control-theory/52-lyapunov-stability-1|52 — Lyapunov Stability 1: What Stable Means]]: exactly what "stable" means, and why converging isn't enough.
53. [[control-theory/53-lyapunov-stability-2|53 — Lyapunov Stability 2: The Direct Method]]: proving stability with an energy-like function that never increases.
54. [[control-theory/54-lyapunov-stability-3|54 — Lyapunov Stability 3: Global Stability, LaSalle and Discrete Time]]: stability for every starting state, LaSalle's idea, and discrete time.
55. [[control-theory/55-lyapunov-stability-4|55 — Lyapunov Stability 4: The Lyapunov Equation and the Indirect Method]]: computing that function for linear systems, and why linearisation works.
56. [[control-theory/56-nonlinear-design-1|56 — Nonlinear Design 1: Describing Functions and Gain Scheduling]]: predicting oscillations caused by hard nonlinearities, and gain scheduling.
57. [[control-theory/57-nonlinear-design-2|57 — Nonlinear Design 2: Feedback Linearisation, Sliding Mode and Adaptive Control]]: cancelling, overpowering or learning a nonlinearity.
58. [[control-theory/58-where-control-is-going|58 — Where Control Is Going]]: where control is heading, and what to take away from the subject.

## Practice

- [[control-theory/projects|Projects]]: hands-on tasks with a clear "done when".
- **The best first experiment:** a motor that follows a knob. Close the loop yourself, turn up the gain, and watch it start to swing. Lessons 17 and 18 become concrete in an afternoon.
- [[control-theory/optimal-control-problem-bank|Optimal control problem bank]]: worked problems with answers to check against.

## Key ideas to remember

1. **Feedback is measure, compare, correct.** It handles disturbances and imperfect models, and it can also cause swinging. → [[control-theory/01-what-control-theory-is-1|01]]
2. **Each integrator in the loop removes the steady-state error for one more kind of input.** That's why the I in PID matters. → [[control-theory/15-steady-state-error-1|15]]
3. **Every real PID needs anti-windup, a filtered D, and D taken from the measurement.** → [[control-theory/17-pid-control-1|17]]
4. **Delay is the enemy.** It costs phase margin and gives nothing back. → [[control-theory/14-time-response-2|14]]
5. **Cancelling an unstable part of a system hides it rather than fixing it.** → [[control-theory/34-controllability-and-observability|34]]
6. **For nonlinear systems, stability belongs to a region, not the whole system.** → [[control-theory/46-nonlinear-systems|46]]
7. **A good model beats a clever controller.** Most control failures are really modelling failures. → [[control-theory/58-where-control-is-going|58]]

## Related

- [[robotics/index|Robotics]]: the biggest user of this subject.
- [[hardware/index|Hardware & Embedded]]: where controllers run.
- [[networking/08-congestion-control|Congestion Control]]: a feedback loop running across the internet.
- [[digital-signal-processing/index|Digital Signal Processing]]: the closely related maths of signals and filters.

---

## About this course

- **Size:** 58 lessons, plus an optimal-control problem bank and projects.
- **Where it came from:** first written in August 2026 from reference sources (13 lessons). Rebuilt in November 2026 to the course standard and extended from the author's course materials: A. M. Hussein's *Control Engineering* chapters (Benha University) for modelling, block diagrams, signal flow graphs, state variables, time response, steady-state error, stability, the root locus, Bode and Nyquist; F. Abdollahi's *Nonlinear Control* lecture on phase-plane analysis; the MIT OpenCourseWare 6.241J chapter on Lyapunov stability; and problem sheets from F. L. Lewis's *Optimal Control*.
- **Checked:** every worked number, quiz answer and diagram is computed in `scripts/diagrams/control_theory.py`, which asserts the lessons' values before drawing.
- **What's still `[reference]`:** nothing here has been validated on real hardware by the author; the hardware warnings come from other people's experience.
