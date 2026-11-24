---
id: 5898cbf7-cf77-4aff-b6c9-1b0ed8304001
---

# Steady-State Error 2: Non-Unity Feedback and Disturbances

Non-unity feedback and disturbances change the steady-state error, and both are handled by tracing them through the loop.

## Before you start
<!-- bite: b5d70650-79bf-4dbd-a15a-2c8f810c3684 -->

You should have read [[control-theory/15-steady-state-error-1|15 — Steady-State Error 1: Test Inputs and Error Constants]] and [[control-theory/10-block-diagrams-3|10 — Block Diagrams 3: Multiple Inputs and Disturbances]] (disturbance inputs).

After this lesson you will be able to:

1. define the error of a non-unity feedback system and convert it to an equivalent unity-feedback system;
2. compute its steady-state error, including a negative one;
3. find the steady-state error caused by a step disturbance;
4. say which part of the loop must hold the gain or integrator to reject a disturbance.

## What this lesson covers
<!-- bite: 2ba4b75d-e759-4de7-b66e-139f7f560465 -->

Lesson Steady-State Error 1 assumed unity feedback ($H = 1$) and a reference as the only input. Real loops break both: sensors have their own dynamics and gains, so $H \ne 1$, and disturbances act on the plant. This lesson extends the error calculation to both.

## The kid version
<!-- bite: b27e2bc8-1884-4d88-a8f6-d071f46bed6a -->

You're steering a boat towards a buoy using a compass that reads a few degrees off. You'll faithfully steer to where the compass says the buoy is, and miss the real one. A non-unity feedback path is like that compass. And a side current pushing the boat is a disturbance: how much it pushes you off depends on how hard you steer back, and on where your steering acts.

**Where the analogy stops working.** A compass error is a fixed offset. A feedback path $H(s)$ can also change with frequency, so it shapes the transient as well as the final value.

## The error with non-unity feedback
<!-- bite: ba7aa4e8-740b-41fb-a075-20095578dd56 -->

With forward path $G$ and feedback $H$, the actuating signal is $R - HC$, but the **error** we care about is still $E = R - C$: how far the output is from what we asked for. To use the error constants, rewrite the loop as unity feedback with an equivalent forward path $G_e$ chosen so that the closed loop is unchanged:

$$\frac{G_e}{1 + G_e} = \frac{G}{1 + GH} \quad\Longrightarrow\quad G_e(s) = \frac{G(s)}{1 + G(s)H(s) - G(s)}$$

Then find $K_p$, $K_v$ or $K_a$ from $G_e$ as before.

## Worked: a negative error
<!-- bite: e69b3e2f-193f-4bc1-b8c9-0e3d7acdbff4 -->

$G(s) = \dfrac{100}{s(s + 10)}$ with $H(s) = \dfrac{1}{s + 5}$, and a unit step. First check stability: $1 + GH = 0$ gives $s^3 + 15s^2 + 50s + 100 = 0$, and Routh's cubic test $15 \times 50 > 100$ passes.

$$G_e = \frac{100(s + 5)}{s^3 + 15s^2 - 50s - 400}$$

This is type 0, with $K_p = G_e(0) = 500/(-400) = -1.25$, so

$$e_{ss} = \frac{1}{1 + K_p} = \frac{1}{-0.25} = -4$$

A negative error means the output settles **above** the reference: at 5 for a reference of 1. Predict why: the feedback path has DC gain $H(0) = 0.2$, so the loop "sees" only a fifth of the output, and keeps pushing until that fifth matches the reference.

## Errors caused by disturbances
<!-- bite: 28dc6bf4-014b-4399-ac48-44c83b8f132f -->

With a controller $G_1$ and plant $G_2$, and a disturbance $D$ added between them, Block Diagrams 3 gave $C = \dfrac{G_1G_2R + G_2D}{1 + G_1G_2}$. The error $E = R - C$ is then

$$E(s) = \frac{1}{1 + G_1G_2}R(s) - \frac{G_2}{1 + G_1G_2}D(s)$$

For a unit-step disturbance alone, the final value theorem gives

$$e_D = -\frac{1}{\displaystyle\lim_{s\to0}\frac{1}{G_2(s)} + \lim_{s\to0}G_1(s)}$$

In words: **to make the disturbance's error small, make the controller's DC gain large, or the plant's DC gain small.** An integrator in the *controller* makes $\lim G_1 = \infty$ and removes the disturbance error entirely; an integrator in the plant doesn't help in the same way.

## Worked: a disturbance on a position loop
<!-- bite: f430c2d2-c5f7-44b8-8300-4ccee12f9980 -->

$G_1 = 1000$ (a proportional controller) and $G_2 = \dfrac{1}{s(s + 25)}$. The plant has an integrator, so $\lim 1/G_2 = 0$, and

$$e_D = -\frac{1}{0 + 1000} = -0.001$$

A unit-step load pushes the output 0.001 off its target for good. Raise the gain to 10000 and it's 0.0001; give the controller an integrator and it's zero.

## Common pitfalls
<!-- bite: 17ae1b96-0cff-4da7-8b44-b0d45ffe6b59 -->

1. **Using $G$ instead of $G_e$** for a non-unity loop.
2. **Reading a negative error as a mistake.** It means the output overshoots the reference for good.
3. **Putting the integrator in the wrong place.** It must sit before the disturbance enters to reject it.
4. **Skipping the stability check.** The final value theorem needs a stable loop.

## Check your understanding
<!-- bite: 3b4f60dd-6ec2-46fa-9aa5-9e45949f525e -->

Try each one before you open the answer.

1. <!-- q: exact id="2e9b7f40" answer="0.52381" accept="11/21" sigfigs="3" -->
   A loop has $G(s) = 10/(s + 1)$ and a constant feedback gain $H = 2$. What is the steady-state error $R - C$ to a unit step?

   <details><summary>Answer</summary>

   $C/R = 10/(s + 21)$, so $C$ settles at $10/21$ and $e_{ss} = 1 - 10/21 = 11/21 = 0.524$. With $G_e = 10/(s + 11)$: $1/(1 + 10/11) = 11/21$ too.

   </details>

2. <!-- q: exact id="a6c34d18" answer="-0.019231" accept="−0.019231|-1/52|−1/52" sigfigs="3" -->
   A controller $G_1 = 50$ drives a plant $G_2 = 2/(s + 4)$. What steady-state error does a unit-step disturbance (entering between them) cause?

   <details><summary>Answer</summary>

   $e_D = -1/(1/G_2(0) + G_1(0)) = -1/(2 + 50) = -0.0192$.

   </details>

3. <!-- q: mcq id="7d0f5b29" -->
   Where must an integrator be placed to remove the steady-state error caused by a step disturbance entering just before the plant?

   - [x] In the controller, before the disturbance enters
   - [ ] In the plant, after the disturbance enters
   - [ ] In the feedback path
   - [ ] Anywhere in the loop

   <details><summary>Answer</summary>

   In the controller: it makes $\lim G_1 = \infty$, so $e_D = 0$.

   </details>

4. <!-- q: gap id="f3b8e061" answers="above|higher|over" -->
   A negative steady-state error means the output settles ___ the reference.

   <details><summary>Answer</summary>

   Above. $e = r - c < 0$ means $c > r$.

   </details>

5. <!-- q: open id="49e1c7a6" -->
   Why is the equivalent forward path $G_e = G/(1 + GH - G)$ needed for a non-unity feedback loop?

   <details><summary>Answer</summary>

   The error constants are defined for unity feedback, where the actuating signal equals the true error $R - C$. With $H \ne 1$ they differ. $G_e$ is the forward path of a unity-feedback loop with the same closed-loop transfer function, so its error constants give the true error.

   </details>

## Before moving on
<!-- bite: b134ebd3-9a14-4641-8096-b615b3527f0f -->

You can find the steady-state error of any linear loop, from any input. **Next:** [[control-theory/17-pid-control-1|17 — PID Control 1: The Three Terms]], which finally gives the car its integrator.

## Related
<!-- bite: b298409c-cf5c-4700-9e24-ace5c70112ac -->

- [[control-theory/10-block-diagrams-3|10 — Block Diagrams 3: Multiple Inputs and Disturbances]]: disturbance transfer functions.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: c983581d-abfd-46ce-af0b-98732aa8ff4b -->

**Level:** Intermediate. **Covers:** error in non-unity feedback, the equivalent unity-feedback system, a negative error, disturbance-induced error, and where integrators must sit.

**Where it sits:** lesson 16 of 58, part 2 of 2 on steady-state error.

**Source:** the author's course notes, A. M. Hussein, *Control Engineering*, Benha University, chapter 8 (section 4 and the disturbance objective); worked examples after N. S. Nise. Numbers checked in `scripts/diagrams/control_theory.py`.
