---
id: d6a8a1da-ea85-4cfd-8232-a553be10fd51
---

# Phase Plane 2: The Equilibria of Linear Systems

A linear two-state system's phase portrait around its equilibrium takes one of a few shapes, decided entirely by the eigenvalues of its matrix: node, saddle, focus or centre.

## Before you start
<!-- bite: ce10980b-3c56-4381-bcb2-2a31128177fe -->

You should have read [[control-theory/47-phase-plane-1|47 — Phase Plane 1: Trajectories, Vector Fields and Isoclines]], and be able to find the eigenvalues and eigenvectors of a 2×2 matrix ([[control-theory/31-state-space-2|31 — State Space 2: Solution, Eigenvalues and Conversions]]).

After this lesson you will be able to:

1. classify the equilibrium of $\dot{x} = Ax$ from the eigenvalues of $A$;
2. sketch each portrait, including which eigenvector trajectories hug near the origin;
3. handle the special cases: repeated eigenvalues and zero eigenvalues;
4. explain why these linear results hold everywhere, but only locally for nonlinear systems.

## Why study linear systems first
<!-- bite: 9dfaa8c1-1a21-46a0-8bd3-64defe0ffe80 -->

Lesson 47 drew portraits by brute force. Before going back to nonlinear systems, it pays to know every shape a *linear* system can make, because near an equilibrium, a nonlinear system usually looks just like its linearisation (lesson 49). So this catalogue is the vocabulary for describing any equilibrium.

For $\dot{x} = Ax$ with $A$ a 2×2 matrix, the solution from $x_0$ is $x(t) = Me^{J_rt}M^{-1}x_0$, where $M$ holds the eigenvectors and $J_r$ is the **real Jordan form** of $A$. Depending on the eigenvalues, $J_r$ is one of three shapes:

$$\begin{bmatrix}\lambda_1 & 0 \\ 0 & \lambda_2\end{bmatrix} \text{ (real, distinct)}, \quad \begin{bmatrix}\lambda & k \\ 0 & \lambda\end{bmatrix} \text{ (real, repeated)}, \quad \begin{bmatrix}\alpha & -\beta \\ \beta & \alpha\end{bmatrix} \text{ (complex } \alpha \pm j\beta)$$

## The kid version
<!-- bite: ec418f24-3c87-409c-bee6-62c1ccbf1ef1 -->

Think of the origin as a plughole and the trajectories as water. Water can drain straight in (a **node**), swirl round as it drains (a **focus**), circle for ever without draining (a **centre**), or come in from two sides and shoot off along the other two, like water hitting a ridge (a **saddle**). Turn every arrow round and draining becomes gushing: an unstable node or focus.

**Where the analogy stops working.** Real water always drains in the end. Here a saddle's water, apart from one exact line, always leaves, and a centre's never drains at all.

## Case 1: two different real eigenvalues
<!-- bite: 4a6f6957-f6f2-45eb-b557-6d9b6167bad4 -->

Change coordinates to $z = M^{-1}x$, along the eigenvectors. The system splits in two independent equations:

$$\dot{z}_1 = \lambda_1z_1, \quad \dot{z}_2 = \lambda_2z_2 \quad\Longrightarrow\quad z_1 = z_{10}e^{\lambda_1t},\ z_2 = z_{20}e^{\lambda_2t}$$

Eliminate $t$ and every trajectory is a curve $z_2 = Cz_1^{\lambda_2/\lambda_1}$. The portrait depends on the signs of the eigenvalues.

**Stable node** ($\lambda_2 < \lambda_1 < 0$): both terms die, so every trajectory heads into the origin. $e^{\lambda_2t}$ dies faster, so $\lambda_2$ is the **fast** eigenvalue and $v_2$ the fast eigenvector. Near the origin, trajectories are **tangent to the slow eigenvector** $v_1$ (the fast part has already gone); far away, they run **parallel to the fast eigenvector** $v_2$.

**Unstable node** ($\lambda_2 > \lambda_1 > 0$): the same shapes with the arrows reversed.

## Case 1: the saddle
<!-- bite: cba9f3e7-759a-4061-806b-50db5332e779 -->

**Saddle point** ($\lambda_2 < 0 < \lambda_1$): one term dies and the other grows. Trajectories are hyperbola-like curves that come in along the **stable eigenvector** $v_2$ and leave along the **unstable eigenvector** $v_1$.

There are exactly four special trajectories: two along $v_2$ heading *into* the origin (the **stable trajectories**) and two along $v_1$ heading *out* (the **unstable** ones). Start anywhere else and you eventually leave. A saddle is always unstable.

## Case 2: complex eigenvalues
<!-- bite: eafc2f20-e778-4610-a7aa-7dd14dfcf2e5 -->

With $\lambda = \alpha \pm j\beta$, switch to polar coordinates in the $z$ plane, $r = \sqrt{z_1^2 + z_2^2}$, $\theta = \tan^{-1}(z_2/z_1)$:

$$\dot{r} = \alpha r,\ \ \dot\theta = \beta \quad\Longrightarrow\quad r(t) = r_0e^{\alpha t},\ \ \theta(t) = \theta_0 + \beta t$$

The angle turns steadily, and the radius grows or shrinks: a logarithmic spiral. The real part $\alpha$ decides which:

1. **$\alpha < 0$, stable focus**: the spiral winds into the origin. The suspension (lesson 30) is one.
2. **$\alpha > 0$, unstable focus**: the spiral winds out.
3. **$\alpha = 0$, centre**: $r$ stays at $r_0$, so trajectories are closed circles (ellipses in the original coordinates). The frictionless pendulum, linearised, is one.

## The six portraits
<!-- bite: d8109e08-b830-4873-849f-c0df21450fd1 -->

![Six phase portraits of linear systems: a stable node with trajectories entering tangent to the slow eigenvector; an unstable node with the same shapes leaving; a saddle with trajectories arriving along one eigenvector and leaving along the other; a stable focus spiralling in; an unstable focus spiralling out; and a centre of closed ellipses.](images/ct-pp-six-types.svg)

## Case 3: repeated eigenvalues
<!-- bite: 759ce50e-fd14-46c8-abcf-0b464e479935 -->

With $\lambda_1 = \lambda_2 = \lambda \ne 0$, the Jordan form has a $k$ that is 0 or 1:

1. **$k = 0$** (two independent eigenvectors): both modes decay at the same rate, so there's no fast or slow direction and every trajectory is a **straight line** into (or out of) the origin. Sometimes called a **star node**.
2. **$k = 1$** (only one eigenvector): $z_1 = e^{\lambda t}(z_{10} + kz_{20}t)$, $z_2 = z_{20}e^{\lambda t}$. Trajectories curve and all become tangent to the single eigenvector: a **degenerate node**.

Either way it's a stable node if $\lambda < 0$ and unstable if $\lambda > 0$.

## Case 4: zero eigenvalues
<!-- bite: 53e53728-3728-4f44-b059-8e7afbe81c51 -->

A zero eigenvalue means $A$ is singular, so **every vector in its null space is an equilibrium**: there's a whole line of them.

1. **One zero eigenvalue** ($\lambda_1 = 0$, $\lambda_2 \ne 0$): $z_1$ stays constant and $z_2 = z_{20}e^{\lambda_2t}$. Trajectories are straight lines that **converge onto** the line of equilibria if $\lambda_2 < 0$, or **leave it** if $\lambda_2 > 0$.
2. **Both zero** ($\dot{z}_1 = z_2$, $\dot{z}_2 = 0$): $z_1 = z_{10} + z_{20}t$, $z_2 = z_{20}$. Every trajectory off the equilibrium line **moves parallel to it**, drifting away linearly.

## The summary
<!-- bite: a3e00277-6535-44bb-a289-1ac5c3abd666 -->

Six types of isolated equilibrium:

1. Stable node.
2. Unstable node.
3. Saddle.
4. Stable focus.
5. Unstable focus.
6. Centre.

The type depends on the eigenvalues: **any eigenvalue with a positive real part means unstable; all real parts negative means stable.**

Remember this one: **for a linear system these results hold globally**, across the whole plane. **For a nonlinear system they only hold locally**, near the equilibrium, and lesson 49 shows exactly when even that fails.

## Common pitfalls
<!-- bite: 62a0cdf4-ffa2-44b9-996a-1e76b70fd77a -->

1. **Mixing up slow and fast eigenvectors.** Near a stable node, trajectories hug the *slow* one.
2. **Calling a saddle "partly stable".** Unless you start exactly on the stable line, you leave. It's unstable.
3. **Reading a centre as stable.** It's only marginally stable: closed orbits, no convergence.
4. **Missing the line of equilibria.** A zero eigenvalue means infinitely many equilibria, not one.

## Check your understanding
<!-- bite: 19c03f6c-ba4b-4746-b5f4-dd3623226b49 -->

Try each one before you open the answer.

1. <!-- q: mcq id="1c8a4e59" -->
   $A = \begin{bmatrix}1 & 2 \\ 3 & 0\end{bmatrix}$ has eigenvalues 3 and −2. What is the equilibrium?

   - [ ] Stable node
   - [ ] Unstable node
   - [x] Saddle point
   - [ ] Centre

   <details><summary>Answer</summary>

   One positive and one negative real eigenvalue: a saddle. (Quick check: $\det A = -6 < 0$ always means a saddle.)

   </details>

2. <!-- q: mcq id="7e2f0b36" -->
   $A = \begin{bmatrix}-1 & 2 \\ -2 & -1\end{bmatrix}$. What is the equilibrium?

   - [x] Stable focus
   - [ ] Unstable focus
   - [ ] Centre
   - [ ] Stable node

   <details><summary>Answer</summary>

   Eigenvalues $-1 \pm 2j$: complex with negative real part, so a stable focus.

   </details>

3. <!-- q: mcq id="d40b9c72" -->
   $A = \begin{bmatrix}-1 & 0 \\ 0 & -3\end{bmatrix}$. Near the origin, trajectories are tangent to which axis?

   - [x] The $x_1$ axis, the slow eigenvector (eigenvalue −1)
   - [ ] The $x_2$ axis, the fast eigenvector (eigenvalue −3)
   - [ ] Neither; they spiral
   - [ ] The line $x_1 = x_2$

   <details><summary>Answer</summary>

   The $x_2$ part dies three times faster, so near the origin only the $x_1$ part is left: trajectories become tangent to the slow eigenvector, the $x_1$ axis.

   </details>

4. <!-- q: gap id="a3e57c18" answers="centre|center;0" -->
   $A = \begin{bmatrix}0 & 1 \\ -4 & 0\end{bmatrix}$ has eigenvalues $\pm 2j$, so the origin is a ___, and the real part of the eigenvalues is ___.

   <details><summary>Answer</summary>

   A centre; real part 0. Trajectories are closed ellipses.

   </details>

5. <!-- q: open id="6f9d2e04" -->
   $A = \begin{bmatrix}0 & 0 \\ 0 & -2\end{bmatrix}$. Describe its equilibria and its trajectories.

   <details><summary>Answer</summary>

   Eigenvalues 0 and −2. The whole $x_1$ axis is a line of equilibria (the null space of $A$). Every trajectory keeps its $x_1$ value and moves straight down or up onto that axis, since $x_2 = x_{20}e^{-2t}$ decays.

   </details>

## Before moving on
<!-- bite: 5069af22-4ebe-415f-bf1c-5cdfd7cd6db1 -->

You can classify any linear equilibrium and sketch its portrait. **Next:** [[control-theory/49-phase-plane-3|49 — Phase Plane 3: Linearising Around an Equilibrium]], which uses this catalogue to classify the equilibria of nonlinear systems, and finds where it breaks.

## Related
<!-- bite: b6ee4c71-f860-44e5-8c46-13b5260df02b -->

- [[control-theory/31-state-space-2|31 — State Space 2: Solution, Eigenvalues and Conversions]]: eigenvalues as poles.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 405cc412-04fb-4976-9d64-df04a9bf4a02 -->

**Level:** Advanced. **Covers:** the real Jordan form, nodes, saddles, foci and centres, repeated and zero eigenvalues, and the six types of equilibrium.

**Where it sits:** lesson 48 of 58, part 2 of 3 on the phase plane.

**Source:** the author's nonlinear-control lecture notes, F. Abdollahi, *Nonlinear Control*, lecture 2, slides 12 to 25. Portraits computed in `scripts/diagrams/control_theory.py`.
