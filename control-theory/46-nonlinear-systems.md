---
id: dfe59854-4dfd-43ec-a2de-beeed1978784
---

# Nonlinear Systems

A nonlinear system is one where doubling the input doesn't simply double the output, and it can do things no linear system can.

## Before you start
<!-- bite: 37d9f3f6-26a4-4400-96ef-e0f59cfe330e -->

You should have read [[control-theory/08-block-diagrams-1|08 — Block Diagrams 1: Connections and the Feedback Rule]] (linearisation) and [[control-theory/30-state-space-1|30 — State Space 1: States and the State Equation]] (writing a system as first-order equations).

After this lesson you will be able to:

1. say what makes a system nonlinear, and name five hard nonlinearities found in real hardware;
2. find the equilibrium points of a nonlinear system;
3. describe five behaviours that have no linear equivalent;
4. explain why stability becomes a local property with a region of attraction.

## What a nonlinear system is
<!-- bite: b8974bce-52f1-4fa1-8f56-400b9763dc70 -->

Everything from lesson 03 to 45 assumed linearity: double the input, double the output; add two inputs, add their outputs. That's called **superposition**, and every tool so far (transfer functions, Bode plots, eigenvalues) depends on it.

Real systems aren't linear. Lesson 07 already met the fix for *smooth* curves: linearise around an operating point, $\sin\theta \approx \theta$ for small angles. This part of the subject is about what that fix misses: nonlinearities you can't linearise away, and behaviours that only nonlinear systems have.

The running example from here on is the **pendulum**, the one the source lectures use: with angle $x_1$ and angular speed $x_2$,

$$\dot{x}_1 = x_2, \qquad \dot{x}_2 = -10\sin x_1$$

where 10 is $g/L$ for a pendulum about a metre long.

## The kid version
<!-- bite: bd787aa8-b1ad-4644-a8fc-8024888019df -->

Push a child on a swing gently and they swing back and forth, a little further for a little more push. Push really hard and they go over the top, all the way round: a completely different kind of motion, not just "more swinging". That's nonlinearity: big pushes don't just give bigger answers, they give different ones.

**Where the analogy stops working.** A swing's nonlinearity is smooth and easy to see. Many machine nonlinearities are sudden, a valve that does nothing until pushed past 5%, a gear with play in it, and they hide inside the hardware until they cause an oscillation.

## Hard nonlinearities
<!-- bite: 7b358961-1811-4eaa-a387-a89ce5ae98d6 -->

Some nonlinearities are sharp corners that no Taylor series can smooth away:

1. **Saturation**: every actuator has a limit. Lesson 17's windup came from this.
2. **Dead zone**: a valve that doesn't move for the first 5% of its command.
3. **Backlash**: play in a gearbox; the output doesn't move until the slack is taken up, and it depends on which way you were going.
4. **Coulomb friction**: a constant force opposing motion that flips sign at zero speed. It's why a position loop can hunt around its setpoint for ever.
5. **Hysteresis**: the output depends on history, as in magnets and piezo actuators.

![Input-output curves of three hard nonlinearities: saturation, a straight line that flattens at plus and minus a limit; a dead zone, flat around zero and then straight; and backlash, a parallelogram where the output only moves once the input has crossed the gap, with a different path going up and going down.](images/ct-hard-nonlinearities.svg)

## Equilibrium points
<!-- bite: 15b3eefe-d943-4edd-b7a1-84baffb2f266 -->

An **equilibrium point** is a state where, once there, the system stays for ever: all the derivatives are zero. For $\dot{\mathbf{x}} = f(\mathbf{x})$, solve $f(\mathbf{x}) = 0$.

For the pendulum: $x_2 = 0$ and $-10\sin x_1 = 0$, so $x_1 = 0, \pm\pi, \pm2\pi, \ldots$ Physically there are just two: **hanging straight down** ($x_1 = 0$) and **balanced straight up** ($x_1 = \pi$). Before reading on: which is stable?

Hanging down: nudge it and it swings back. Balanced up: nudge it and it falls. A linear system has exactly one equilibrium (or a whole line of them); **a nonlinear system can have several isolated ones, with different stability.** Lesson 49 shows how to classify each from its linearisation.

## Behaviours with no linear equivalent
<!-- bite: d7d5f0ec-869e-4f67-bea1-d80cf86e2c79 -->

1. **Multiple equilibria**: the pendulum's two, a switch with two stable states (lesson 49's tunnel-diode circuit).
2. **Limit cycles**: a self-sustaining oscillation at a fixed size, whatever the starting point. A linear oscillator's size depends on how you started it; a limit cycle's doesn't (lessons 50 and 51).
3. **Finite escape time**: blowing up to infinity in a *finite* time, not just growing exponentially. $\dot{x} = x^2$ from $x(0) = 1$ has solution $x = 1/(1 - t)$, which reaches infinity at $t = 1$.
4. **Chaos**: bounded, perfectly deterministic, yet unpredictable in practice, as in the Lorenz weather model (lesson 54).
5. **Amplitude-dependent behaviour**: small and large inputs give different *kinds* of response, like the swing going over the top.

## Stability becomes local
<!-- bite: b745f743-ae7f-438b-99e0-fca7cdf4cc34 -->

That last behaviour breaks the mental model most. For a linear system, stability is a yes-or-no fact about the whole system. For a nonlinear one, **a system can be stable for small disturbances and unstable for large ones.**

The pendulum shows it: from hanging down, a small nudge just swings and settles (with friction), but a big enough shove sends it over the top. So stability becomes a property of an equilibrium **plus a region around it**: the **region of attraction**, the set of starting states that end up there.

Remember this one: for nonlinear systems, "is it stable?" becomes "**stable for which starting states?**" The next nine lessons give the tools: the phase plane, which draws the answer for two-state systems (30 to 34), and Lyapunov's method, which proves it for any number of states (35 to 38).

## Common pitfalls
<!-- bite: 63579fec-4d8b-44d5-ac58-2e8fc47aff2e -->

1. **Linearising a hard nonlinearity.** Saturation and backlash have corners; a tangent line says nothing useful about them.
2. **Assuming one equilibrium.** Solve $f(\mathbf{x}) = 0$ fully; there may be several.
3. **Calling a nonlinear system "stable" without saying where.** State the equilibrium and the region.
4. **Expecting bigger inputs to give proportionally bigger outputs.** Check large signals separately.

## Check your understanding
<!-- bite: 9662d4d2-c129-41c4-b0ff-456a189183e8 -->

Try each one before you open the answer.

1. <!-- q: mcq id="4f1d8b26" -->
   A motor's driver ignores commands smaller than 0.3 V and responds normally above. Which nonlinearity is this?

   - [ ] Saturation
   - [x] Dead zone
   - [ ] Backlash
   - [ ] Hysteresis

   <details><summary>Answer</summary>

   A dead zone: no output for small inputs, then normal behaviour.

   </details>

2. <!-- q: mcq id="9b3c0e71" -->
   What are the equilibrium points of $\dot{x}_1 = x_2$, $\dot{x}_2 = x_1 - x_1^3$?

   - [ ] Only $(0, 0)$
   - [x] $(0, 0)$, $(1, 0)$ and $(-1, 0)$
   - [ ] $(1, 1)$ and $(-1, -1)$
   - [ ] None

   <details><summary>Answer</summary>

   $x_2 = 0$ and $x_1(1 - x_1^2) = 0$, so $x_1 = 0, 1, -1$.

   </details>

3. <!-- q: exact id="c6e2a058" answer="0.5" accept="1/2" -->
   $\dot{x} = x^2$ starts at $x(0) = 2$. Its solution is $x = 1/(1/x_0 - t)$. At what time does it escape to infinity?

   <details><summary>Answer</summary>

   When $1/2 - t = 0$, at $t = 0.5$: a finite escape time.

   </details>

4. <!-- q: mcq id="1a7f5d93" -->
   Which behaviour can a linear system show?

   - [ ] A limit cycle whose size doesn't depend on the starting point
   - [ ] Two separate stable equilibrium points
   - [x] A sustained oscillation whose size depends on the starting point
   - [ ] Escaping to infinity in finite time

   <details><summary>Answer</summary>

   A linear system with poles on the imaginary axis oscillates for ever, at a size set by its starting state. The other three need nonlinearity.

   </details>

5. <!-- q: open id="e3d70b4c" -->
   Explain, using the pendulum, why "is it stable?" isn't enough of a question for a nonlinear system.

   <details><summary>Answer</summary>

   Hanging down, a damped pendulum returns after a small nudge, but a big enough shove sends it over the top to another equilibrium. So its stability depends on how big the disturbance is. The useful question is which starting states return, its region of attraction.

   </details>

## Before moving on
<!-- bite: a4f1a7df-a5ca-4ea1-860f-6e89b92feaa0 -->

You can find equilibria, name hard nonlinearities and say why stability is local. **Next:** [[control-theory/47-phase-plane-1|47 — Phase Plane 1: Trajectories, Vector Fields and Isoclines]], a way of *seeing* every possible motion of a two-state system in one picture.

## Related
<!-- bite: 2432212e-4328-45a2-bb27-b61ff0bcfe9f -->

- [[control-theory/08-block-diagrams-1|08 — Block Diagrams 1: Connections and the Feedback Rule]]: linearisation and its limits.
- [[robotics/index|Robotics]]: where most nonlinear control gets applied.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: daab857a-eb87-47e0-956a-639e7dd09e61 -->

**Level:** Advanced. **Covers:** superposition and why it fails, hard nonlinearities, equilibrium points, behaviours with no linear equivalent, and local stability with a region of attraction.

**Where it sits:** lesson 46 of 58, the opening of the nonlinear part (lessons 46 to 58).

**Source:** `[reference]`, assembled from standard control texts, with the pendulum example from the author's nonlinear-control lecture notes (F. Abdollahi, *Nonlinear Control*, lecture 2, Amirkabir University of Technology). Diagram from `scripts/diagrams/control_theory.py`.
