---
id: e7410d4a-4abf-4df9-a4ae-28db59f070b0
---

# Phase Plane 3: Linearising Around an Equilibrium

Near each equilibrium a nonlinear system behaves like its linearisation, unless the Jacobian's eigenvalues sit on the imaginary axis.

## Before you start
<!-- bite: 7ea01b82-7634-470d-976a-e6d70c0648b9 -->

You should have read [[control-theory/48-phase-plane-2|48 — Phase Plane 2: The Equilibria of Linear Systems]], and be able to take partial derivatives.

After this lesson you will be able to:

1. find a nonlinear system's equilibria and compute its Jacobian at each one;
2. classify each equilibrium as a node, focus or saddle from the Jacobian's eigenvalues;
3. explain why that works for nodes, foci and saddles but not for centres;
4. describe a bistable system and its separatrix.

## What linearising around an equilibrium means
<!-- bite: b92d9eab-97ff-4955-8bb3-b66c643a93dd -->

Lesson 48 catalogued every linear equilibrium. A nonlinear system can have several equilibria (lesson 46), and we'd like to classify each without drawing the whole portrait. The idea: **zoom in close enough to an equilibrium and the nonlinear system looks linear.** So linearise there, read off the type from lesson 48, and you know the local behaviour.

There are two ways to get the qualitative picture of a second-order nonlinear system:

1. generate the global phase portrait by computer;
2. linearise about each equilibrium and study the behaviour near each one, without drawing anything.

This lesson is the second way, and it explains what the first way shows.

## The kid version
<!-- bite: 3ce460d5-b522-4d16-95d9-c2203bde77dc -->

The Earth is round, but your street looks flat. Zoomed in close enough, a curved surface looks like a flat one, and a map of your street drawn as if the Earth were flat works fine. Linearising is drawing that flat street map around each equilibrium.

**Where the analogy stops working.** On a street the flat map is always good enough. Around an equilibrium where the linear picture is "on the fence" (a centre, circling for ever), the tiny curvature you ignored decides whether the real system spirals in or out, and the flat map can't tell you.

## The Jacobian
<!-- bite: 503967ef-4734-44e1-ba1c-f13f2abb6617 -->

Let $(x_{10}, x_{20})$ be an equilibrium of $\dot{x}_1 = f_1(x_1, x_2)$, $\dot{x}_2 = f_2(x_1, x_2)$, with $f_1$ and $f_2$ smooth there. Write the state as the equilibrium plus a small perturbation, $x_1 = x_{10} + y_1$, $x_2 = x_{20} + y_2$, and expand in a Taylor series. The constant terms are zero (it's an equilibrium), and dropping the higher-order terms leaves

$$\dot{y} = Ay, \qquad A = \frac{\partial f}{\partial x}\bigg|_{x_0} = \begin{bmatrix}\partial f_1/\partial x_1 & \partial f_1/\partial x_2 \\ \partial f_2/\partial x_1 & \partial f_2/\partial x_2\end{bmatrix}_{x_0}$$

That matrix of partial derivatives is the **Jacobian**. The rule, in words: **if the origin of the linearised system is a stable or unstable node, a stable or unstable focus, or a saddle, then near the equilibrium the nonlinear system behaves the same way.**

## The pendulum's two equilibria
<!-- bite: a16039e5-bc6f-4dcf-ba14-5e764eb9c52f -->

For the pendulum with friction, $\dot{x}_1 = x_2$, $\dot{x}_2 = -10\sin x_1 - 0.5x_2$, the Jacobian is

$$A = \begin{bmatrix}0 & 1 \\ -10\cos x_1 & -0.5\end{bmatrix}$$

Predict the types before reading on.

1. **Hanging down**, $(0, 0)$: $A = \begin{bmatrix}0 & 1 \\ -10 & -0.5\end{bmatrix}$, eigenvalues $-0.25 \pm 3.15j$. A **stable focus**: it swings and settles.
2. **Upright**, $(\pi, 0)$: $A = \begin{bmatrix}0 & 1 \\ 10 & -0.5\end{bmatrix}$, eigenvalues $2.92$ and $-3.42$. A **saddle**: unstable.

## The tunnel-diode circuit: the model
<!-- bite: 0140814d-df52-409d-947c-83ef125368fd -->

The lecture's main example is a circuit with a **tunnel diode**, a component whose current $h(v)$ rises, falls and rises again as the voltage grows. With the capacitor voltage $x_1$ and inductor current $x_2$ as states, and the given component values ($u = 1.2$ V, $R = 1.5$ kΩ, $C = 2$ pF, $L = 5$ μH, time in nanoseconds, current in mA):

$$\dot{x}_1 = 0.5\big[-h(x_1) + x_2\big], \qquad \dot{x}_2 = 0.2\big[-x_1 - 1.5x_2 + 1.2\big]$$

$$h(x_1) = 17.76x_1 - 103.79x_1^2 + 229.62x_1^3 - 226.31x_1^4 + 83.72x_1^5$$

Setting both derivatives to zero gives three equilibria: $Q_1 = (0.063, 0.758)$, $Q_2 = (0.285, 0.610)$ and $Q_3 = (0.884, 0.210)$.

## The tunnel-diode circuit: classifying
<!-- bite: 8dc3ac4e-e63d-4476-b515-016bba1d18dc -->

The Jacobian is

$$A = \begin{bmatrix}-0.5h'(x_1) & 0.5 \\ -0.2 & -0.3\end{bmatrix}$$

(The lecture slide prints the top-left entry as $0.5h'$; the minus sign comes from $-h(x_1)$, and the slide's own numbers only work with it.) Evaluate at each equilibrium (the slide's values differ in the second decimal place because it rounded the equilibria):

| Equilibrium | Top-left entry | Eigenvalues | Type |
| --- | --- | --- | --- |
| $Q_1 = (0.063, 0.758)$ | −3.62 | −3.59, −0.33 | stable node |
| $Q_2 = (0.285, 0.610)$ | 1.82 | 1.77, −0.25 | saddle |
| $Q_3 = (0.884, 0.210)$ | −1.44 | −1.34, −0.40 | stable node |

## The global picture: a bistable circuit
<!-- bite: bafbe312-bb14-43c9-a9bb-639315361a06 -->

The computer-drawn portrait agrees. Every trajectory heads to $Q_1$ or $Q_3$, except two special ones that run into the saddle $Q_2$.

![The phase portrait of the tunnel-diode circuit, x1 from minus 0.4 to 1.6 and x2 from minus 0.4 to 1.6. Trajectories flow to the stable nodes Q1 at (0.063, 0.758) and Q3 at (0.884, 0.210). The saddle Q2 at (0.285, 0.610) sits between them, and the two trajectories that run into it form the separatrix, a curve dividing the plane into the part that ends at Q1 and the part that ends at Q3.](images/ct-pp-tunnel-diode.svg)

Those two special trajectories form a **separatrix**: a curve that splits the plane in two. Start on one side and you end at $Q_1$; start on the other and you end at $Q_3$.

In practice only $Q_1$ and $Q_3$ are ever seen. Even if you set the exact starting conditions of $Q_2$, ever-present electrical noise pushes the state off it. A circuit with two steady operating points is called **bistable**, and you switch it between $Q_1$ and $Q_3$ by briefly changing the supply. That's a memory cell.

## When linearisation fails: the centre
<!-- bite: aa826944-3644-451a-a466-55680eabe772 -->

Why does the rule exclude centres? Think of a small change in the matrix, $A \to A + \Delta A$. Eigenvalues move continuously, so one with a clearly positive or negative real part keeps its sign under a small nudge: nodes, foci and saddles survive. But an eigenvalue **on the imaginary axis** can be pushed either way by the tiniest nudge, and the higher-order terms we dropped are exactly such a nudge.

The lecture's example:

$$\dot{x}_1 = -x_2 - \mu x_1(x_1^2 + x_2^2), \qquad \dot{x}_2 = x_1 - \mu x_2(x_1^2 + x_2^2)$$

At the origin, $A = \begin{bmatrix}0 & -1 \\ 1 & 0\end{bmatrix}$, eigenvalues $\pm j$: a centre. But in polar coordinates the system is exactly

$$\dot{r} = -\mu r^3, \qquad \dot\theta = 1$$

So for $\mu > 0$ it's **stable** (spirals in), and for $\mu < 0$ it's **unstable** (spirals out). The linearisation is the same for both and can't tell them apart. Remember this one: **when the Jacobian has eigenvalues on the imaginary axis, linearisation tells you nothing about stability.** Lesson 55 meets the same rule as Lyapunov's indirect method.

## Common pitfalls
<!-- bite: 83f0b49c-361e-4097-8f53-22f8df0eece8 -->

1. **Evaluating the Jacobian at the wrong point.** Use the equilibrium's coordinates, one equilibrium at a time.
2. **Trusting a linearised centre.** Higher-order terms decide; use energy or a Lyapunov function.
3. **Expecting to see a saddle in practice.** Noise always pushes the state off it.
4. **Applying local results far away.** The classification only holds near the equilibrium.

## Check your understanding
<!-- bite: f596b26f-b758-4d0d-b3e8-7be687801e41 -->

Try each one before you open the answer.

1. <!-- q: mcq id="8b0c2f47" -->
   For $\dot{x}_1 = x_2$, $\dot{x}_2 = x_1 - x_1^3$, what type is the equilibrium at $(1, 0)$? (The Jacobian there is $\begin{bmatrix}0 & 1 \\ -2 & 0\end{bmatrix}$.)

   - [ ] Stable node
   - [ ] Saddle
   - [x] A centre for the linearisation, so the linearisation can't decide
   - [ ] Unstable focus

   <details><summary>Answer</summary>

   $1 - 3x_1^2 = -2$ at $x_1 = 1$, giving eigenvalues $\pm j\sqrt2$: a linear centre. Linearisation is inconclusive. (This system conserves an energy, so in fact the orbits close.)

   </details>

2. <!-- q: mcq id="2e7a9d15" -->
   Same system, $\dot{x}_1 = x_2$, $\dot{x}_2 = x_1 - x_1^3$. What type is the equilibrium at $(0, 0)$?

   - [ ] Stable node
   - [x] Saddle
   - [ ] Centre
   - [ ] Stable focus

   <details><summary>Answer</summary>

   The Jacobian is $\begin{bmatrix}0 & 1 \\ 1 & 0\end{bmatrix}$, eigenvalues $\pm1$: a saddle, and since it's not on the imaginary axis, the nonlinear system is a saddle there too.

   </details>

3. <!-- q: exact id="f1c48a03" answer="-0.25" accept="−0.25" -->
   The damped pendulum $\dot{x}_1 = x_2$, $\dot{x}_2 = -10\sin x_1 - 0.5x_2$ is linearised at $(0, 0)$. What is the real part of its eigenvalues?

   <details><summary>Answer</summary>

   $s^2 + 0.5s + 10 = 0$, so the real part is $-0.25$: a stable focus.

   </details>

4. <!-- q: gap id="0d9e5b26" answers="separatrix;bistable" -->
   The curve that divides a portrait into regions flowing to different equilibria is a ___, and a circuit with two stable operating points is called ___.

   <details><summary>Answer</summary>

   Separatrix; bistable.

   </details>

5. <!-- q: open id="7c3f1a88" -->
   The system $\dot{x}_1 = -x_2 - \mu x_1(x_1^2 + x_2^2)$, $\dot{x}_2 = x_1 - \mu x_2(x_1^2 + x_2^2)$ has the same linearisation for every $\mu$. Why can't linearisation decide its stability, and what decides it?

   <details><summary>Answer</summary>

   The linearisation has eigenvalues $\pm j$, on the imaginary axis, where any small extra term can tip the behaviour either way. The cubic terms dropped by linearising decide it: in polar form $\dot{r} = -\mu r^3$, so it's stable for $\mu > 0$ and unstable for $\mu < 0$.

   </details>

## Before moving on
<!-- bite: d53bbd18-911b-437b-82fd-93cff5d3ed2c -->

You can classify a nonlinear system's equilibria and know when the method fails. **Next:** [[control-theory/50-limit-cycles-1|50 — Limit Cycles 1: Stable, Unstable and Semi-Stable]], about the closed orbits only nonlinear systems can have.

## Related
<!-- bite: 229ebaf9-10fa-4c8a-bc95-fadefe9b6e35 -->

- [[control-theory/08-block-diagrams-1|08 — Block Diagrams 1: Connections and the Feedback Rule]]: linearisation for control design.
- [[control-theory/55-lyapunov-stability-4|55 — Lyapunov Stability 4: The Lyapunov Equation and the Indirect Method]]: the indirect method, the same idea made rigorous.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: d213d2e1-ed23-4b2a-b7fb-d05a3e9a73b6 -->

**Level:** Advanced. **Covers:** the Jacobian, classifying equilibria by linearisation, the pendulum's two equilibria, the tunnel-diode circuit and its separatrix, and why linearisation fails at a centre.

**Where it sits:** lesson 49 of 58, part 3 of 3 on the phase plane.

**Source:** the author's nonlinear-control lecture notes, F. Abdollahi, *Nonlinear Control*, lecture 2, slides 26 to 34. The sign of the Jacobian's first entry is corrected here. The portrait and eigenvalues are computed in `scripts/diagrams/control_theory.py`.
