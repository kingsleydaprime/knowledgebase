---
id: 0f642ee7-2cb1-4465-992e-b8ff77839e57
---

# Pole Placement

Pole placement feeds every state back through a gain matrix, and if the system is controllable it can put the closed-loop poles anywhere you choose.

## Before you start
<!-- bite: 4e5e9c59-091d-4ec1-bf71-03a676ef4005 -->

You should have read [[control-theory/34-controllability-and-observability|34 — Controllability and Observability]], and be able to turn an overshoot and settling-time specification into a target pole ([[control-theory/13-time-response-1|13 — Time Response 1: First- and Second-Order Systems]]).

After this lesson you will be able to:

1. write the closed-loop matrix $A - BK$ under state feedback;
2. compute $K$ by hand by matching coefficients;
3. choose pole locations from a specification, and name three standard patterns;
4. add integral action, and explain why pole placement needs the full state.

## What pole placement is
<!-- bite: 85223954-ca7a-4aae-9627-9fbba08ebab7 -->

With a PID, you turn three knobs and the poles go wherever they go. Pole placement flips that around: **decide where the poles should be, then compute the gains that put them there.**

The controller multiplies every state by a gain and adds them up:

$$\mathbf{u} = -K\mathbf{x}$$

Substitute into $\dot{\mathbf{x}} = A\mathbf{x} + B\mathbf{u}$:

$$\dot{\mathbf{x}} = (A - BK)\mathbf{x}$$

So the closed-loop poles are the eigenvalues of $A - BK$. And the remarkable result: **if $(A, B)$ is controllable, you can put the eigenvalues of $A - BK$ anywhere you want.** Not "improve the response": place every pole exactly. Controllability is precisely the condition for it.

## The kid version
<!-- bite: 2a2755d1-59ad-40af-ad8d-83343af8b9e3 -->

A sound engineer has a mixing desk with one slider per instrument. With enough sliders, they can make the band sound exactly how they want. State feedback gives you one slider per state, and with them you can set the system's natural behaviour to anything.

**Where the analogy stops working.** A mixing desk doesn't cost more when you push the sliders up. Here, every pole you move far costs actuator effort and amplifies sensor noise, so "anything" is limited by what the hardware can take.

## Placing the suspension's poles
<!-- bite: 5658ded1-a644-4392-8083-db445328eef5 -->

The passive suspension has poles at $-4 \pm 6.93j$: $\zeta = 0.5$, 16% overshoot. Suppose we build an **active suspension**, with a motor that pushes on the body, and we want $\zeta = 0.707$ (under 5% overshoot) and to settle in half a second. Settling in 0.5 s needs $\zeta\omega_n = 4/0.5 = 8$, and $\zeta = 0.707$ puts the poles at 45°: **$-8 \pm 8j$**. The target polynomial is

$$(s + 8)^2 + 64 = s^2 + 16s + 128$$

Now the closed loop. With $K = \begin{bmatrix}k_1 & k_2\end{bmatrix}$:

$$A - BK = \begin{bmatrix}0 & 1 \\ -64 - 0.004k_1 & -8 - 0.004k_2\end{bmatrix}$$

Its characteristic polynomial is $s^2 + (8 + 0.004k_2)s + (64 + 0.004k_1)$. Before reading on, match the coefficients and predict $K$.

## The gains, and what they mean
<!-- bite: 32cff28e-ee29-4d0d-97e9-5c162d885069 -->

Matching: $8 + 0.004k_2 = 16$ gives $k_2 = 2000$; $64 + 0.004k_1 = 128$ gives $k_1 = 16000$. So

$$K = \begin{bmatrix}16000 & 2000\end{bmatrix}$$

Read it physically: the motor pushes back with 16000 N per metre of displacement and 2000 N per m/s of speed. That's an *extra* spring and damper, exactly doubling the passive ones. State feedback can always be read like that.

## Passive against placed poles
<!-- bite: 272a2f80-f041-4c0f-bffc-e00534196326 -->

Released from 5 cm down, here is the difference the extra spring and damper make.

![The suspension released from 5 centimetres down, passive against pole placement: the passive suspension overshoots rest by 8 millimetres and settles in about a second; with poles placed at minus 8 plus or minus 8j it overshoots by 2 millimetres and settles in about half a second.](images/ct-pole-placement.svg)

The cost is effort: released from 5 cm down, the motor's first push is $16000 \times 0.05 = 800$ N.

## Computing K in general
<!-- bite: 164014fb-b861-41c2-946d-b5b941c4797f -->

Three ways:

1. **By hand**: match the coefficients of $\det(sI - A + BK)$ to the target polynomial, as above. Fine for two or three states.
2. **Ackermann's formula**: a closed form. Fine for teaching, but numerically poor above about five states.
3. **`place()`** in a control library: what you should use. With several inputs $K$ isn't unique, and this uses the spare freedom to make the poles as insensitive as possible to model error.

## Choosing where to put them
<!-- bite: 1b44da91-e1f8-4d28-bbff-ae65fa6c8c83 -->

Placing is mechanical; choosing *where* is the design.

1. **Start from the specification**: $\zeta$ from the overshoot, $\zeta\omega_n$ from the settling time, as we just did. Put the dominant pair there and the rest 5 to 10 times further left (lesson 14).
2. **Butterworth**: poles evenly spaced on a semicircle. A good all-round response with no single dominant mode.
3. **Bessel**: chosen for the least overshoot. Good when overshoot is the binding limit.
4. **ITAE**: tabulated poles that minimise the time-weighted error, a good compromise.

## Three warnings
<!-- bite: 86990bd5-e661-4000-a155-c84e3769942c -->

Where beginners come unstuck:

1. **Fast poles cost effort.** Effort grows with how far you move a pole. Ask for ten times the natural speed and you'll demand force the motor doesn't have, and once it saturates, all your careful placement is gone.
2. **Fast poles amplify noise.** High gain on a noisy measurement gives a jittery actuator that wears out and can excite modes you didn't model.
3. **Pole placement says nothing about robustness.** You can place poles beautifully and still have terrible margins, because margins aren't part of the calculation. This is the main criticism of the method, and why LQR (lesson 42) is usually preferred: same structure, but the gains come from an optimisation with guaranteed margins.

## Integral action
<!-- bite: b752d5a6-6de8-4b0e-aef6-65c6de117131 -->

State feedback alone has the same flaw as proportional control: a **steady-state error**. $\mathbf{u} = -K\mathbf{x}$ drives the state to zero, which isn't the same as following a reference, and a constant load (passengers in the car) leaves an offset.

The fix is the same as PID's: **add an integrator as an extra state**, the running total of the error:

$$\dot{x}_I = r - y$$

Stack it onto the system:

$$\begin{bmatrix}\dot{\mathbf{x}} \\ \dot{x}_I\end{bmatrix} = \begin{bmatrix}A & 0 \\ -C & 0\end{bmatrix}\begin{bmatrix}\mathbf{x} \\ x_I\end{bmatrix} + \begin{bmatrix}B \\ 0\end{bmatrix}\mathbf{u} + \begin{bmatrix}0 \\ 1\end{bmatrix}r$$

then place all $n + 1$ poles of this bigger system. The result has zero steady-state error and shrugs off constant disturbances and gain errors. And it needs anti-windup, for exactly the reason PID does (lesson 17).

## The catch: you need every state
<!-- bite: 247c390d-1b3b-44b5-a1d9-ba89c34e7ef9 -->

$\mathbf{u} = -K\mathbf{x}$ needs **the full state**, and you rarely have it. You have $\mathbf{y} = C\mathbf{x}$: a few sensors, not every state. The suspension might measure position but not speed; a furnace one temperature out of five.

Two options:

1. **Add sensors.** Sometimes right, often expensive, and some states can't be measured directly at all.
2. **Estimate the state from what you can measure.** That needs observability, and it's the next lesson.

## Common pitfalls
<!-- bite: 5b8b3483-78a6-4b38-95db-4978ebc318f0 -->

1. **Placing poles without checking controllability.** If it fails on an unstable mode, no $K$ exists.
2. **Placing poles very far left.** The gains, the effort and the noise all grow; check the actuator command.
3. **Forgetting the offset.** Plain state feedback doesn't track; add an integrator.
4. **Assuming good poles mean good margins.** Check the margins separately.

## Check your understanding
<!-- bite: 6fffb165-3d43-434a-a3dd-3768b8657861 -->

Try each one before you open the answer.

1. <!-- q: exact id="0b3d7e92" answer="-5" accept="−5" -->
   A plant $\dot{x} = 2x + u$ (unstable) gets state feedback $u = -kx$ with $k = 7$. Where is the closed-loop pole?

   <details><summary>Answer</summary>

   $\dot{x} = (2 - 7)x = -5x$, so the pole is at $-5$. Stable.

   </details>

2. <!-- q: exact id="8c5f1a06" answer="6" -->
   Same plant, $\dot{x} = 2x + u$. What gain $k$ puts the closed-loop pole at $-4$?

   <details><summary>Answer</summary>

   $2 - k = -4$, so $k = 6$.

   </details>

3. <!-- q: gap id="d7a2e4c9" answers="10;7" -->
   $A = \begin{bmatrix}0 & 1 \\ -2 & -3\end{bmatrix}$, $B = \begin{bmatrix}0 \\ 1\end{bmatrix}$. To get the closed-loop polynomial $s^2 + 10s + 12$, you need $k_1 = $ ___ and $k_2 = $ ___.

   <details><summary>Answer</summary>

   $A - BK$ has polynomial $s^2 + (3 + k_2)s + (2 + k_1)$. Matching: $k_2 = 7$, $k_1 = 10$.

   </details>

4. <!-- q: mcq id="1e6b9f43" -->
   Why is LQR usually preferred to pole placement for the same structure $u = -Kx$?

   - [ ] It needs fewer sensors
   - [ ] It doesn't need a model
   - [x] Its gains come from an optimisation that guarantees good margins and weighs effort
   - [ ] It always gives faster poles

   <details><summary>Answer</summary>

   LQR chooses $K$ by trading state error against effort, and the result has guaranteed margins. Pole placement ignores both.

   </details>

5. <!-- q: open id="5a8c3d71" -->
   An engineer places a motor's poles ten times further left than its natural poles. In simulation it's perfect; on the real motor it buzzes and barely follows. Give two likely reasons.

   <details><summary>Answer</summary>

   The large gains demand more torque than the motor can give, so it saturates and the placed poles no longer apply. And the high gains amplify sensor noise, making the actuator buzz and possibly exciting unmodelled modes.

   </details>

## Before moving on
<!-- bite: 82cbac99-2eeb-43db-9f90-aae0f9c986f3 -->

You can place poles by hand, choose where to put them, and add integral action. **Next:** [[control-theory/36-observers|36 — Observers]], which estimates the states you can't measure so that state feedback works with real sensors.

## Related
<!-- bite: cdff4695-edd7-48f4-9836-81f64d12800c -->

- [[control-theory/42-lqr|42 — LQR]]: choosing $K$ by optimisation instead.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: a48e2e7a-a2d8-4d59-9d30-cdef7fb81db6 -->

**Level:** Advanced. **Covers:** state feedback, placing poles by coefficient matching, the active suspension example, choosing pole locations, the costs of fast poles, integral action, and the need for the full state.

**Where it sits:** lesson 35 of 58, the second of two on what state feedback can do.

**Source:** `[reference]`, assembled from standard control texts. The simulation and gains are checked in `scripts/diagrams/control_theory.py`.
