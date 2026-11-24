---
id: 310ac35b-8037-4f8f-adc0-dfe202a2985f
---

# Nonlinear Design 2: Feedback Linearisation, Sliding Mode and Adaptive Control

When gain scheduling isn't enough, four methods design directly for the nonlinearity, each with a stability proof and a price.

## Before you start
<!-- bite: ec11a90c-741b-481d-84b3-b6b3ba3be3c0 -->

You should have read [[control-theory/56-nonlinear-design-1|56 — Nonlinear Design 1: Describing Functions and Gain Scheduling]] and [[control-theory/53-lyapunov-stability-2|53 — Lyapunov Stability 2: The Direct Method]].

After this lesson you will be able to:

1. design a feedback-linearising controller for a simple plant, and name its risks;
2. design a sliding surface and explain chattering and its fix;
3. describe backstepping and adaptive control, and when each is used;
4. choose among the nonlinear methods for a given problem.

## What this lesson covers
<!-- bite: d10664a4-6e4d-45b2-b8f5-4ba6a32af4c7 -->

Lesson 56's tools work around the nonlinearity: approximate it, or switch between linear designs. This lesson's tools face it head-on. Each comes with a proof of stability built on lessons 52 to 55, and each has a practical price. Keep the pendulum in mind, now with a motor torque $u$ at the pivot:

$$\dot{x}_1 = x_2, \qquad \dot{x}_2 = -10\sin x_1 + u$$

## The kid version
<!-- bite: f7801805-a21b-47ce-a15d-553da40f78be -->

You're carrying a tray on a ship that rolls. You could **cancel** the roll exactly by tilting your hands opposite to it (feedback linearisation): perfect if you know the roll exactly. You could just **grip hard and force** the tray level whatever happens (sliding mode): crude, robust, and tiring. Or you could **learn** the ship's rhythm as you walk and adjust (adaptive control).

**Where the analogy stops working.** You'd blend all three without thinking. A controller must commit to one structure, and each one's weakness (wrong model, chattering, slow learning) shows up in a different way.

## Feedback linearisation
<!-- bite: b965bcd9-9181-45c1-90c5-25fdcec339b3 -->

Cancel the nonlinearity with the input itself. For the pendulum, choose

$$u = 10\sin x_1 + v$$

The $\sin$ terms cancel exactly, leaving $\dot{x}_1 = x_2$, $\dot{x}_2 = v$: a linear double integrator. Now control it linearly with $v = -k_1x_1 - k_2x_2$, giving the characteristic polynomial $s^2 + k_2s + k_1$. For both poles at $-4$, $s^2 + 8s + 16$: $k_1 = 16$, $k_2 = 8$. The pendulum now behaves like a linear system at **every** angle, not just near the bottom.

In general, for $\dot{x} = f(x) + g(x)u$, choose $u = (-f(x) + v)/g(x)$, leaving $\dot{x} = v$. For robot arms this is **computed-torque control**, and it works well because rigid-body dynamics are known precisely. → [[robotics/09-robot-control|Robot control]]

## Feedback linearisation: the risks
<!-- bite: def81d08-b33f-4425-be22-cc42d7647671 -->

1. **It needs an exact model.** You're cancelling terms; any cancellation error goes straight into the response. If the real pendulum's $g/L$ is 11, not 10, a $\sin x_1$ term survives.
2. **It can demand large effort**, and it may cancel *helpful* natural behaviour (like damping), wasting effort fighting it.
3. **Watch the hidden dynamics.** When only some states are linearised, the remaining **zero dynamics** must be stable by themselves: the nonlinear cousin of lesson 03's right-half-plane zero.

## Sliding mode control
<!-- bite: 82236548-ffb4-46f0-b7c4-633e1e0c1bfc -->

Choose a **sliding surface** $s(x) = 0$ on which the motion is what you want, then switch the input hard to drive the state onto it and hold it there. For a double integrator $\ddot{x} = u + d$, with $d$ an unknown but bounded disturbance:

$$s = x_2 + \lambda x_1, \qquad u = -\lambda x_2 - k\,\text{sign}(s)$$

On the surface, $s = 0$ means $\dot{x}_1 = -\lambda x_1$: the position decays like $e^{-\lambda t}$ whatever the disturbance. To reach the surface, check with $V = \tfrac12s^2$: $\dot{V} = s\dot{s} = s(d - k\,\text{sign}(s)) \le |s|(|d| - k)$, which is negative whenever $k > |d|$. So with enough switching gain, the state reaches the surface in finite time and stays.

That's the attraction: **provable robustness** to model error and disturbances that enter with the input, which is rare in nonlinear control. With $\lambda = 2$, the position then decays with time constant 0.5 s.

## Sliding mode: chattering
<!-- bite: b590aa2b-37ea-4f00-9010-36f693c9ff9a -->

The catch is **chattering**. The ideal switch flips infinitely fast; a real one flips as fast as the hardware allows, buzzing back and forth across the surface. That wears actuators and excites modes nobody modelled.

The standard fix is a **boundary layer**: replace $\text{sign}(s)$ by a saturation that is linear in a thin band $|s| < \phi$. Inside the band the control is smooth; you trade exact convergence for a small band of error. Sliding mode is common in power electronics, where switching is what the hardware does anyway.

## Backstepping
<!-- bite: d4fe9cb4-83e7-48d2-bf2e-b02273fb082e -->

A recursive design for plants in a chain, where each state drives the next (**strict-feedback form**), like $\dot{x}_1 = f_1(x_1) + x_2$, $\dot{x}_2 = f_2(x_1, x_2) + u$:

1. Treat $x_2$ as if it were a control for the first equation, and choose the value it *should* have to stabilise $x_1$, with a Lyapunov function $V_1$.
2. Define the error between $x_2$ and that desired value, add its square to get $V_2$, and choose $u$ to make $\dot{V}_2$ negative.
3. Repeat for longer chains.

It's systematic and comes with a Lyapunov proof (lessons 53 and 54), but the control laws grow complicated fast, and it depends on the model's structure.

## Adaptive control
<!-- bite: 48f5d2cd-df57-4aba-9b88-13b1f9409c11 -->

When the plant's numbers are unknown or drift, **estimate them online and update the controller as you go**:

1. **Model reference adaptive control (MRAC)**: adjust the gains so the plant behaves like a chosen reference model.
2. **Self-tuning regulators**: identify the plant model continuously (lesson 07), and redesign the controller from it.

## Adaptive control: the caveats
<!-- bite: 97077a35-ec6d-45bb-8468-e0a1321ae58e -->

Caveats worth taking seriously:

1. **Persistent excitation.** The estimates stay honest only if the signals are rich enough. In a quiet steady state they can drift.
2. **Delicate proofs.** Stability guarantees need care, and unmodelled dynamics can break them.
3. **Real accidents.** The X-15 rocket plane crash in 1967 involved an adaptive flight controller, and the field's reputation for fragility is earned.

Use it where parameters genuinely change a lot and you can't schedule on a measured variable.

## Choosing a method
<!-- bite: 7e7134c3-3b4f-46e1-8117-1c95f2139de9 -->

1. **Smooth nonlinearity, measurable operating point**: gain scheduling first (lesson 56).
2. **Accurate model, like a rigid robot**: feedback linearisation (computed torque).
3. **Uncertain model or strong disturbances, actuator that tolerates switching**: sliding mode with a boundary layer.
4. **A chain structure and a need for a proof**: backstepping.
5. **Parameters that change a lot and can't be scheduled**: adaptive, carefully.
6. **Constraints that bind**: MPC (lesson 43), not nonlinear theory.

## Common pitfalls
<!-- bite: 0e3e2404-13ae-4ef8-9938-c57cb08fb438 -->

1. **Feedback linearising with a rough model.** The cancellation leaves the errors in.
2. **Using a pure sign function in sliding mode.** Use a boundary layer.
3. **Adaptive control without excitation.** Estimates drift when nothing is happening.
4. **Reaching for these first.** Try gain scheduling first.

## Check your understanding
<!-- bite: bfc6a169-5175-4d86-a108-592c116a1883 -->

Try each one before you open the answer.

1. <!-- q: gap id="7f3b2e60" answers="9;6" -->
   After feedback linearisation the pendulum is $\ddot{x}_1 = v$. With $v = -k_1x_1 - k_2x_2$, both poles at $-3$ need $k_1 = $ ___ and $k_2 = $ ___.

   <details><summary>Answer</summary>

   $(s + 3)^2 = s^2 + 6s + 9$, so $k_1 = 9$ and $k_2 = 6$.

   </details>

2. <!-- q: mcq id="c41d8a57" -->
   For $\dot{x} = x^2 + u$, which control makes the closed loop $\dot{x} = -2x$?

   - [x] $u = -x^2 - 2x$
   - [ ] $u = x^2 - 2x$
   - [ ] $u = -2x$
   - [ ] $u = -x^2$

   <details><summary>Answer</summary>

   $\dot{x} = x^2 - x^2 - 2x = -2x$. The first term cancels the nonlinearity.

   </details>

3. <!-- q: exact id="0e8a6f24" answer="0.25" accept="1/4" -->
   A sliding surface is $s = x_2 + 4x_1$. On the surface, the position decays like $e^{-4t}$. What is its time constant, in seconds?

   <details><summary>Answer</summary>

   $1/4 = 0.25$ s.

   </details>

4. <!-- q: mcq id="9b6e1d03" -->
   A sliding-mode motor drive buzzes loudly. What is the standard fix?

   - [ ] Raise the switching gain $k$
   - [x] Replace the sign function with a saturation over a thin boundary layer
   - [ ] Remove the sliding surface
   - [ ] Switch to feedback linearisation

   <details><summary>Answer</summary>

   A boundary layer smooths the control near the surface, trading a small error band for no chattering.

   </details>

5. <!-- q: open id="38c7e5a1" -->
   Why does feedback linearisation work well for industrial robot arms but poorly for, say, a chemical reactor?

   <details><summary>Answer</summary>

   It cancels the nonlinear terms exactly, so it needs an accurate model. A rigid robot's dynamics follow from known masses and lengths and are modelled precisely; a reactor's kinetics are uncertain and drift, so the cancellation would leave large errors.

   </details>

## Before moving on
<!-- bite: eb2afd3a-9726-4491-a5f6-66a0a3cb89f3 -->

You can design feedback-linearising and sliding-mode controllers, and describe backstepping and adaptive control. **Next:** [[control-theory/58-where-control-is-going|58 — Where Control Is Going]], the last lesson.

## Related
<!-- bite: 5fd84a3f-34bb-488b-80e8-b60fc597386f -->

- [[robotics/09-robot-control|Robot control]]: computed torque in practice.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 7ab7b268-75bc-4aa3-8867-fd42e0242e1b -->

**Level:** Advanced. **Covers:** feedback linearisation and its risks, sliding mode control with a reaching proof, chattering and the boundary layer, backstepping, adaptive control, and choosing a method.

**Where it sits:** lesson 57 of 58, part 2 of 2 on nonlinear design.

**Source:** `[reference]`, assembled from standard control texts.
