---
id: f99e4727-dcd0-4766-8429-72e431bba1c3
---

# Controllability and Observability

Controllability asks whether your inputs can steer every part of a system, and observability asks whether your sensors can see every part of it.

## Before you start
<!-- bite: d1080cff-18c2-49e4-8533-e88f92b97082 -->

You should have read [[control-theory/31-state-space-2|31 — State Space 2: Solution, Eigenvalues and Conversions]], and know what the rank of a matrix is ([[mathematics/04-linear-algebra/index|linear algebra]]).

After this lesson you will be able to:

1. build the controllability and observability matrices and test their rank;
2. give a physical example of an uncontrollable mode and an unobservable one;
3. say why stabilisable and detectable are the conditions that really matter;
4. explain duality, and why only the controllable and observable part shows in a transfer function.

## What controllability and observability are
<!-- bite: e800a7e9-6efe-4190-a1d6-df0e110b04d7 -->

Lesson 21 warned that cancelling an unstable pole hides it without removing it. State space lets us say exactly what "hidden" means, with two questions:

1. **Controllability**: can the inputs drive the state from *any* starting value to *any* other value, in finite time?
2. **Observability**: can you work out the starting state from watching the outputs for a finite time?

Before designing any controller in lesson 35, you check both. If either fails on an unstable part of the system, no controller in the world will save it.

## The kid version
<!-- bite: 8a145203-226a-4f68-97d9-2935a4fb0c16 -->

You're steering a shopping trolley with one stuck wheel. You can push it forward and back fine, but however you push, you can't make it go sideways. That direction is **uncontrollable**. Now you're in a car with only a speedometer, no map, no windows. You know exactly how fast you're going, but not *where* you are. Your position is **unobservable**.

**Where the analogy stops working.** In real life you'd notice the stuck wheel. In a big model, an uncontrollable or unobservable direction can be a hidden mix of many states, and only the maths finds it.

## The controllability test
<!-- bite: 63cb22f0-e99c-4505-a654-dcac604309b7 -->

Build the **controllability matrix** from $A$ and $B$:

$$\mathcal{C} = \begin{bmatrix} B & AB & A^2B & \cdots & A^{n-1}B \end{bmatrix}$$

The system is **controllable exactly when $\mathcal{C}$ has rank $n$** (as many independent columns as there are states).

Why that matrix: $B$ is where the input pushes directly. $AB$ is where that push has spread to an instant later, $A^2B$ the instant after that. Together the columns cover everything the input can ever reach. Full rank means it reaches every direction. (The list stops at $A^{n-1}$ because higher powers add nothing new.)

## Controllability on the suspension
<!-- bite: 6f7db6ce-06ed-4fb3-9e55-f850e631817b -->

With $A = \begin{bmatrix}0 & 1 \\ -64 & -8\end{bmatrix}$ and $B = \begin{bmatrix}0 \\ 0.004\end{bmatrix}$:

$$AB = \begin{bmatrix}0.004 \\ -0.032\end{bmatrix}, \qquad \mathcal{C} = \begin{bmatrix}0 & 0.004 \\ 0.004 & -0.032\end{bmatrix}$$

Its determinant is $-0.000016 \ne 0$, so rank 2: controllable. The force pushes the speed directly, and the speed then moves the position, so between them every direction is reached.

## When controllability fails
<!-- bite: 5bd28e1b-b1bc-4d48-9ad6-a6effc462f4a -->

An uncontrollable system has a direction you can't influence whatever the actuators do:

1. A satellite whose thruster points straight through its centre of mass can't produce any spin.
2. A symmetric two-mass system pushed exactly at its centre can't excite the mode where the masses move in opposite directions.
3. A drone with three rotors has more ways to move than inputs to move them.

Remember this one: **if an uncontrollable mode is unstable, the system cannot be stabilised, by any controller.** That's the strongest negative result in the subject, so check it first.

The weaker condition that's actually needed is **stabilisable**: every *unstable* mode is controllable. Uncontrollable stable modes are usually fine: they die away by themselves.

## A test that tells you how controllable
<!-- bite: e25adbfb-38aa-4255-92ea-3d2660ec0aea -->

The rank test is fragile in numbers: "rank 3 with one tiny number" versus "rank 4" is a judgement call. Two better habits:

1. **Look at the smallest singular value of $\mathcal{C}$**, not just the rank. It says *how* controllable a direction is. A direction that's only barely controllable needs enormous effort to move.
2. **Use the PBH test**: the system is controllable exactly when $\text{rank}\begin{bmatrix} sI - A & B\end{bmatrix} = n$ at every eigenvalue $s$ of $A$. It's more reliable, and it tells you *which* mode is the problem.

## Observability
<!-- bite: 1bc0f68b-c25d-42f1-85d8-89637fa6946b -->

The mirror question. Build the **observability matrix** from $A$ and $C$:

$$\mathcal{O} = \begin{bmatrix} C \\ CA \\ CA^2 \\ \vdots \\ CA^{n-1} \end{bmatrix}$$

The system is **observable exactly when $\mathcal{O}$ has rank $n$**. $C$ is what you see directly, $CA$ what you see of the state's motion, and so on. Full rank means nothing is hidden.

**Detectable** is the weaker condition that matters: every *unstable* mode is observable. An unobservable stable mode decays harmlessly. **An unobservable unstable mode grows with no sign at the output** until something breaks. That's the formal version of lesson 21's warning: cancelling an unstable pole with a controller zero makes it unobservable.

## Observability on the car
<!-- bite: 121a9193-fac1-4e4b-81c6-58384b34562a -->

Give the car two states, position $p$ and speed $v$: $\dot{p} = v$ and $\dot{v} = -0.05v + 0.001u$. Its only sensor is the speedometer, so $C = \begin{bmatrix}0 & 1\end{bmatrix}$.

$$A = \begin{bmatrix}0 & 1 \\ 0 & -0.05\end{bmatrix}, \quad CA = \begin{bmatrix}0 & -0.05\end{bmatrix}, \quad \mathcal{O} = \begin{bmatrix}0 & 1 \\ 0 & -0.05\end{bmatrix}$$

The first column is all zeros: rank 1, not observable. Predict before reading: which state is hidden? Position. Start the car 10 km further down the road and every speedometer reading is identical, so no amount of watching tells you where you are. Swap the sensor for a GPS, $C = \begin{bmatrix}1 & 0\end{bmatrix}$, and $\mathcal{O}$ becomes the identity: observable.

## Duality
<!-- bite: 13463ba3-1605-44aa-8468-eff25baed4e8 -->

The two tests are mirror images:

$$(A, B) \text{ controllable} \iff (A^T, B^T) \text{ observable}$$

Every controllability result has an observability twin. It's no coincidence: lesson 36 designs an observer by running the controller design on the transposed system, so learning one gives you the other free.

| Control | Estimation |
| --- | --- |
| Controllability | Observability |
| $\mathcal{C} = [B, AB, \ldots]$ | $\mathcal{O} = [C; CA; \ldots]$ |
| State-feedback gain $K$ | Observer gain $L$ |
| LQR | Kalman filter |
| Stabilisable | Detectable |

## Minimal realisation
<!-- bite: 6926326c-8e44-462d-b035-5dd8ab2fea40 -->

A state-space model is **minimal** when it's both controllable and observable. Every model's states split into four groups, an idea called Kalman's decomposition:

| | Observable | Unobservable |
| --- | --- | --- |
| **Controllable** | the transfer function sees this | can drive it, can't see it |
| **Uncontrollable** | can see it, can't drive it | completely invisible |

**Only the top-left group appears in the transfer function.** The other three are real dynamics a classical model is blind to. Convert a non-minimal model to a transfer function and they vanish silently, while still existing in the hardware. That's the clearest single argument for state space.

## Common pitfalls
<!-- bite: fb234bb5-9a1f-4ac4-ae4e-03118e9c2740 -->

1. **Trusting the rank alone.** Check how small the smallest singular value is.
2. **Demanding full controllability.** Stabilisable (all unstable modes controllable) is what you need.
3. **Assuming a sensor reveals everything it's connected to.** The car's speed doesn't depend on where the car is, so a speedometer never reveals position.
4. **Forgetting that cancellation makes a mode unobservable.** The output looks perfect; the state doesn't.

## Check your understanding
<!-- bite: ad6dceba-5bf1-4544-9c53-3f5a922b8626 -->

Try each one before you open the answer.

1. <!-- q: mcq id="9b4e0d27" -->
   $A = \begin{bmatrix}-1 & 0 \\ 0 & 2\end{bmatrix}$ and $B = \begin{bmatrix}1 \\ 0\end{bmatrix}$. What can you conclude?

   - [ ] Controllable, so it can be stabilised
   - [x] Not stabilisable: the unstable mode at 2 can't be reached by the input
   - [ ] Not controllable, but stabilisable
   - [ ] Unobservable

   <details><summary>Answer</summary>

   $\mathcal{C} = [B, AB] = \begin{bmatrix}1 & -1 \\ 0 & 0\end{bmatrix}$, rank 1. The second state (eigenvalue 2, unstable) gets no input at all, so no controller can stabilise it.

   </details>

2. <!-- q: exact id="4e1a8c53" answer="2" -->
   $A = \begin{bmatrix}0 & 1 \\ -2 & -3\end{bmatrix}$ and $C = \begin{bmatrix}1 & 0\end{bmatrix}$. What is the rank of the observability matrix?

   <details><summary>Answer</summary>

   $\mathcal{O} = \begin{bmatrix}1 & 0 \\ 0 & 1\end{bmatrix}$, rank 2: observable.

   </details>

3. <!-- q: mcq id="c3f7a291" -->
   Which pair of conditions is enough for a stabilising controller and observer to exist?

   - [ ] Controllable and observable, nothing weaker
   - [x] Stabilisable and detectable
   - [ ] Detectable only
   - [ ] Stable open loop

   <details><summary>Answer</summary>

   Stabilisable and detectable: every unstable mode can be both moved and seen. Stable modes that can't be moved or seen die away by themselves.

   </details>

4. <!-- q: gap id="e0d65b8f" answers="observable;transposed|transpose" -->
   $(A, B)$ is controllable exactly when $(A^T, B^T)$ is ___. This is duality, and it lets you design an observer by running a controller design on the ___ system.

   <details><summary>Answer</summary>

   Observable; transposed.

   </details>

5. <!-- q: open id="76d2c0a4" -->
   A model's transfer function looks stable, but the real machine drifts away and eventually hits a limit. Using Kalman's decomposition, explain how that can happen.

   <details><summary>Answer</summary>

   The transfer function only shows the part that is both controllable and observable. An unstable mode that is uncontrollable or unobservable (for example after a pole–zero cancellation) is missing from it, but still exists in the machine, so it grows while the transfer function says nothing.

   </details>

## Before moving on
<!-- bite: 9c35d29c-adc5-4845-b005-95c8e33adf4b -->

You can test controllability and observability and say why the stabilisable and detectable versions matter. **Next:** [[control-theory/35-pole-placement|35 — Pole Placement]], which uses controllability to put every closed-loop pole exactly where you choose.

## Related
<!-- bite: ffc9df88-69ab-4665-8b2e-e10fd035c06e -->

- [[control-theory/21-root-locus-1|21 — Root Locus 1: Sketching the Locus]]: the cancellation warning.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 67ab0b24-313a-4c24-876a-8515294a1d85 -->

**Level:** Advanced. **Covers:** the controllability and observability tests, stabilisable and detectable, the PBH test, duality, and minimal realisations, worked on the suspension and the car.

**Where it sits:** lesson 34 of 58, the first of two on what state feedback can do.

**Source:** `[reference]`, assembled from standard control texts. Matrices checked in `scripts/diagrams/control_theory.py`.
