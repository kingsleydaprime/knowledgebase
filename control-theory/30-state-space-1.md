---
id: 2e4bc6b0-6c02-48a3-b93e-2a498a56a7dd
---

# State Space 1: States and the State Equation

State space describes a system by a short list of numbers, its state, that captures everything about it right now, plus matrix rules for how that list changes.

## Before you start
<!-- bite: 6e4bf2b0-52c4-4bc3-a25f-fe9fb8c7e4e4 -->

You should have read [[control-theory/29-nyquist-3|29 — Nyquist 3: Uncertainty and Fundamental Limits]] (or at least [[control-theory/13-time-response-1|13 — Time Response 1: First- and Second-Order Systems]]), and be able to multiply a matrix by a vector ([[mathematics/04-linear-algebra/index|linear algebra]]).

After this lesson you will be able to:

1. say what a state is, and choose states for a mechanical or electrical system;
2. write a system in the form $\dot{\mathbf{x}} = A\mathbf{x} + B\mathbf{u}$, $\mathbf{y} = C\mathbf{x} + D\mathbf{u}$, and say what each matrix means;
3. turn a second-order differential equation into two first-order ones;
4. give the reasons state space handles many inputs and outputs better than transfer functions.

## What state space is
<!-- bite: 1179eeed-7506-4d49-8428-76f99b970cab -->

Up to now we've described each plant by one transfer function: one input in, one output out. That works beautifully for a car's speed. But a drone has four motors and six ways to move, and they all affect each other. Writing that as transfer functions becomes a matrix of fractions, and the algebra turns ugly fast.

**State space** takes a different route. Instead of one high-order equation, write several first-order ones, one for each quantity that stores energy, and stack them into a vector:

$$\dot{\mathbf{x}} = A\mathbf{x} + B\mathbf{u}, \qquad \mathbf{y} = C\mathbf{x} + D\mathbf{u}$$

Bold letters are vectors, capital letters are matrices. The next sections say what each one is.

## The kid version
<!-- bite: 4bd55800-1ef1-4e47-a49f-65c55b1ee759 -->

A doctor checking a patient doesn't need their whole life story. A handful of numbers, temperature, pulse, blood pressure, breathing rate, tell the doctor where the patient is *right now* and roughly where they're heading. That handful is the patient's state. State space describes a machine the same way: a short list of numbers, and rules for how each number changes.

**Where the analogy stops working.** A patient's vital signs are a rough summary. A system's state is exact: with it and the future inputs, you can predict *everything* that will happen, with no need for any of the past.

## Terms used in state space
<!-- bite: 7c46e3ff-a3b6-4837-9037-c1516f5a1a37 -->

1. **State**: This is the vector $\mathbf{x}$ of $n$ numbers, the smallest set that, together with the future inputs, decides all future behaviour.
2. **Input**: This is the vector $\mathbf{u}$ of the $m$ things you command.
3. **Output**: This is the vector $\mathbf{y}$ of the $p$ things you measure.
4. **System matrix $A$**: This is the $n \times n$ matrix saying how the state changes on its own.
5. **Input matrix $B$**: This is the $n \times m$ matrix saying how each input pushes each state.
6. **Output matrix $C$**: This is the $p \times n$ matrix saying what the sensors see.
7. **Feedthrough $D$**: This is the $p \times m$ matrix linking inputs straight to outputs. It is zero for almost every physical plant, because a real plant can't respond instantly.

## What "state" really means
<!-- bite: 7457d720-bf82-43b6-abba-34266e9945e5 -->

The definition to hold onto: **the state is the smallest set of variables such that, knowing $\mathbf{x}$ now and the inputs from now on, you can work out all future behaviour.**

So the state is a complete summary of the past. Nothing that happened before matters beyond what's in $\mathbf{x}$ now. That's the same "memoryless" idea (the Markov property) that appears in [[ai-engineering/index|reinforcement learning]] and queueing theory, for the same reason.

How to choose states: pick the things that **store energy**, because energy can't change instantly.

1. **Mechanical**: positions (spring energy) and speeds (kinetic energy).
2. **Electrical**: capacitor voltages and inductor currents.
3. **Thermal**: temperatures. **Chemical**: concentrations.

The number of states is the system's order: the number of independent energy stores. The car has one (its speed), so it is first order.

## The suspension in state space
<!-- bite: 7c97c8d0-3f11-4571-a10e-ce7de0072b20 -->

Take the suspension, $m\ddot{x} + c\dot{x} + kx = F$, with $m = 250$, $c = 2000$, $k = 16000$. It stores energy in two places, the spring and the moving mass, so pick two states: position $x_1 = x$ and speed $x_2 = \dot{x}$.

Now write one first-order equation for each:

1. Position changes at the speed: $\dot{x}_1 = x_2$.
2. Speed changes by Newton's law, $\dot{x}_2 = (F - kx_1 - cx_2)/m = -64x_1 - 8x_2 + 0.004F$.

Stack them:

$$\begin{bmatrix}\dot{x}_1 \\ \dot{x}_2\end{bmatrix} = \begin{bmatrix}0 & 1 \\ -64 & -8\end{bmatrix}\begin{bmatrix}x_1 \\ x_2\end{bmatrix} + \begin{bmatrix}0 \\ 0.004\end{bmatrix}F, \qquad y = \begin{bmatrix}1 & 0\end{bmatrix}\mathbf{x}$$

The first row is bookkeeping (the derivative of position *is* speed); **the second row is the physics**. That pattern, plain rows plus one real row, is what every mechanical state-space model looks like.

## Watching the state move
<!-- bite: 037bb0aa-60b8-4fea-b77c-6a25a5842e1f -->

Because the state is a point $(x_1, x_2)$, you can draw it moving. Push the suspension down 5 cm and let go: the point starts at $(-0.05, 0)$ and spirals into the origin as the bounce dies away.

![The suspension's state plotted as position against speed after being released from 5 centimetres below rest: the point spirals clockwise into the origin; on the first swing the speed peaks at 0.22 metres per second and the body overshoots rest by 8 millimetres, and each turn is smaller.](images/ct-suspension-state.svg)

That picture is a **trajectory** in the **state plane**. Lesson 47 turns this one picture into a whole method for nonlinear systems.

## Many coordinate choices, one system
<!-- bite: 7cf0f4bf-e8a4-4e7d-925d-af72fe5ac259 -->

State representations aren't unique. We could have used position and *momentum*, or any mix of the two. Any invertible matrix $T$ gives new states $\mathbf{z} = T\mathbf{x}$ and new matrices

$$\bar{A} = TAT^{-1}, \quad \bar{B} = TB, \quad \bar{C} = CT^{-1}$$

Different coordinates, same system. The **eigenvalues of $A$ don't change** under this swap, which is the first hint that they, not the matrix entries, carry the physical meaning. Lesson 31 shows they are exactly the poles.

## Why bother
<!-- bite: 9bd60953-9255-4697-aeb9-fc344914f1a1 -->

Transfer functions work fine for one input and one output. The case for state space:

1. **Many inputs and outputs are natural.** $B$ just gets wider and $C$ taller.
2. **Hidden behaviour is visible.** A transfer function only sees input to output. State space shows states that run away inside while the output looks fine: lesson 21's cancellation trap, now something you can write down.
3. **Time-varying and nonlinear systems fit.** $A(t)$ is no harder to write, and $\dot{\mathbf{x}} = f(\mathbf{x}, \mathbf{u})$ covers nonlinear plants.
4. **Starting conditions are built in.** Transfer functions assume everything starts at rest.
5. **Better numbers.** Matrix calculations are far more reliable than finding roots of high-order polynomials. Beyond about ten states, transfer-function methods become numerically untrustworthy.
6. **It's what the algorithms use.** LQR, the Kalman filter and MPC are all written in state space.

## Many inputs and outputs
<!-- bite: 22b11dd6-f64a-4fc9-ba2b-133b3200a2f5 -->

Here's where state space pays for itself. Nothing in the notation changes: $B$ has one column per actuator, $C$ one row per sensor, and all the analysis applies as it is.

**Coupling** is what makes many-input systems hard classically: input 1 moves outputs 1 *and* 2, so two separate PID loops fight. Classical fixes exist (decoupling networks, closing loops one at a time) but they're painful. **State-space methods don't have the problem**: a state-feedback gain is a matrix, and it handles all the coupling at once.

A drone is the standard example: 12 states (three positions, three speeds, three angles, three spin rates), 4 inputs, and the couplings, tilt moves you sideways and thrust affects everything, are the whole difficulty.

## Common pitfalls
<!-- bite: 30b79eca-f94c-4cac-ab5d-9ae724ea2a5d -->

1. **Choosing states that aren't independent.** Position and twice position are one state, not two.
2. **Too few states.** Every independent energy store needs one.
3. **Putting the physics in the wrong row.** In the mechanical pattern, the bookkeeping row is $\dot{x}_1 = x_2$.
4. **Thinking the matrices are unique.** Many correct models exist; their eigenvalues agree.

## Check your understanding
<!-- bite: 4e676a53-e28a-42e3-a5f8-24b87c56cb35 -->

Try each one before you open the answer.

1. <!-- q: exact id="6c2f0e91" answer="3" -->
   A circuit has two capacitors and one inductor, all independent. How many states does it need?

   <details><summary>Answer</summary>

   Three: one per independent energy store (two capacitor voltages and one inductor current).

   </details>

2. <!-- q: mcq id="e1b8d3a4" -->
   A car body is modelled as $m\ddot{y} + ky = u$ with state $\mathbf{x} = [y,\ \dot{y}]^T$. What is the matrix $A$?

   - [ ] $\begin{bmatrix}0 & 1 \\ k/m & 0\end{bmatrix}$
   - [x] $\begin{bmatrix}0 & 1 \\ -k/m & 0\end{bmatrix}$
   - [ ] $\begin{bmatrix}1 & 0 \\ 0 & -k/m\end{bmatrix}$
   - [ ] $\begin{bmatrix}0 & -k/m \\ 1 & 0\end{bmatrix}$

   <details><summary>Answer</summary>

   $\dot{x}_1 = x_2$ and $\dot{x}_2 = (u - ky)/m = -(k/m)x_1 + u/m$. So $A = \begin{bmatrix}0 & 1 \\ -k/m & 0\end{bmatrix}$ and $B = \begin{bmatrix}0 \\ 1/m\end{bmatrix}$.

   </details>

3. <!-- q: exact id="8a4d2f60" answer="-1" accept="−1" -->
   A source drives a 1 Ω resistor and a 1 H inductor in series. With the inductor current $x$ as the state, the voltage balance is $u = 1 \cdot x + 1 \cdot \dot{x}$. In $\dot{x} = ax + bu$, what is $a$?

   <details><summary>Answer</summary>

   $\dot{x} = -x + u$, so $a = -1$ (and $b = 1$).

   </details>

4. <!-- q: gap id="b7e0c5d2" answers="0|zero;instantly|instantaneously|immediately" -->
   For almost every physical plant $D$ is ___, because a real plant can't respond to its input ___.

   <details><summary>Answer</summary>

   Zero; instantly. Every output takes some time to react.

   </details>

5. <!-- q: open id="f04c9a18" -->
   Why do engineers choose energy-storing quantities as states?

   <details><summary>Answer</summary>

   Stored energy can't change instantly, so those quantities are continuous and summarise the system's past. Knowing them now, plus the future inputs, is enough to predict everything, which is the definition of a state.

   </details>

## Before moving on
<!-- bite: e75f4452-cff0-4aad-baff-f334ed30c662 -->

You can choose states and write a system as $A$, $B$, $C$, $D$. **Next:** [[control-theory/31-state-space-2|31 — State Space 2: Solution, Eigenvalues and Conversions]], which solves the state equation and shows that the eigenvalues of $A$ are the poles you already know.

## Related
<!-- bite: 6856d7f1-e67a-4912-803a-d58b53bbbfa5 -->

- [[control-theory/47-phase-plane-1|47 — Phase Plane 1: Trajectories, Vector Fields and Isoclines]]: the state plane, used for nonlinear systems.
- [[mathematics/04-linear-algebra/index|Linear algebra]]: matrices and vectors.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: d141f04d-0c6d-48d9-9ded-69a53912a067 -->

**Level:** Advanced. **Covers:** the state-space form, what a state is and how to choose one, the suspension as a state-space model, changes of coordinates, why state space, and many-input systems.

**Where it sits:** lesson 30 of 58, part 1 of 4 on state space, and the first lesson of modern control.

**Source:** `[reference]`, assembled from standard control texts. Questions 2 and 3 are based on problems 3.2-3 and 3.2-4 of the author's optimal-control problem sheets (see the [[control-theory/optimal-control-problem-bank|problem bank]]). The trajectory comes from `scripts/diagrams/control_theory.py`.
