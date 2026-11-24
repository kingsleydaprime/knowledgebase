---
id: 337ed242-6f2b-4ae2-b355-481ba4e11818
---

# Lyapunov Stability 4: The Lyapunov Equation and the Indirect Method

For a linear system a Lyapunov function comes from one matrix equation, and it proves why linearisation works.

## Before you start
<!-- bite: 6f4b8320-42ee-4148-98ac-135fcf65a6c7 -->

You should have read [[control-theory/54-lyapunov-stability-3|54 — Lyapunov Stability 3: Global Stability, LaSalle and Discrete Time]], and know what a symmetric positive definite matrix is ([[mathematics/04-linear-algebra/index|linear algebra]]).

After this lesson you will be able to:

1. write and solve the Lyapunov equation $PA + A^TP = -Q$ for a 2×2 system;
2. use it to test a linear system's stability without finding its eigenvalues;
3. state Lyapunov's indirect method and explain why it works;
4. apply the direct method to gradient systems and to gradient descent.

## What the Lyapunov equation is
<!-- bite: 8f9498d1-4654-4e5f-a253-a8cbaee477cf -->

Finding $V$ was the hard part of lessons 53 and 54. For a **linear** system $\dot{x} = Ax$ it isn't hard at all. Try a quadratic, $V(x) = x^TPx$ with $P$ symmetric. Then

$$\dot{V} = \dot{x}^TPx + x^TP\dot{x} = x^T(A^TP + PA)x$$

So if we can find a positive definite $P$ with

$$PA + A^TP = -Q$$

for some positive definite $Q$ (often $Q = I$), then $V$ is positive definite, radially unbounded, and $\dot{V} = -x^TQx$ is negative definite. The system is globally asymptotically stable. This is the **continuous Lyapunov equation**, and it's linear in the entries of $P$.

## The kid version
<!-- bite: 66d7527c-b01e-4341-86af-aa10ee585001 -->

Lessons 53 and 54 were like searching for a bowl that fits a ball's motion by trial and error. For linear systems there's a machine that *makes* the bowl for you: you feed in the system and the rate you want the energy to drain, and it returns the bowl's exact shape, or tells you no bowl exists.

**Where the analogy stops working.** The machine only works for linear systems. For nonlinear ones you can still use the bowl it makes, but only close to the equilibrium, which is the indirect method.

## The theorem, both ways
<!-- bite: 86f3b9c4-01c7-402e-82a3-4fa645f18b1b -->

The MIT notes (exercise 13.6) prove both directions:

1. **If** $PA + A^TP = -Q$ has a symmetric positive definite solution $P$ (with $Q$ positive definite), then $\dot{x} = Ax$ is asymptotically stable: every eigenvalue of $A$ is in the open left half plane.
2. **Conversely**, if the system is asymptotically stable, then

$$P = \int_0^\infty e^{A^Tt}Qe^{At}\,dt$$

exists (the integrand decays exponentially), is symmetric and positive definite, and is the **unique** solution.

So a linear system is asymptotically stable **exactly when** the Lyapunov equation has a positive definite solution. That decides stability by solving a linear system of equations, with no eigenvalues needed.

## Solving one by hand
<!-- bite: 83ce07dd-4c69-4d95-9f04-6be6d3596e52 -->

Take $A = \begin{bmatrix}0 & 1 \\ -2 & -3\end{bmatrix}$ (eigenvalues $-1$ and $-2$) and $Q = I$. Write $P = \begin{bmatrix}p_1 & p_2 \\ p_2 & p_3\end{bmatrix}$ and multiply out $A^TP + PA$:

$$A^TP + PA = \begin{bmatrix}-4p_2 & p_1 - 3p_2 - 2p_3 \\ p_1 - 3p_2 - 2p_3 & 2p_2 - 6p_3\end{bmatrix} = \begin{bmatrix}-1 & 0 \\ 0 & -1\end{bmatrix}$$

Three equations, three unknowns. Predict, then solve:

1. $-4p_2 = -1$, so $p_2 = 0.25$.
2. $2(0.25) - 6p_3 = -1$, so $p_3 = 0.25$.
3. $p_1 = 3(0.25) + 2(0.25) = 1.25$.

$$P = \begin{bmatrix}1.25 & 0.25 \\ 0.25 & 0.25\end{bmatrix}$$

Positive definite? $p_1 = 1.25 > 0$ and $\det P = 0.3125 - 0.0625 = 0.25 > 0$. Yes: the system is asymptotically stable, as its eigenvalues said.

## The discrete version
<!-- bite: fafb202e-c914-408c-8d3c-f709aa545c59 -->

For $x(k+1) = Ax(k)$ and $V = x^TPx$, the one-step change is $\Delta V = x^T(A^TPA - P)x$. So the **discrete Lyapunov equation** is

$$A^TPA - P = -Q$$

and a positive definite solution exists exactly when every eigenvalue of $A$ has size less than 1 (MIT exercise 13.8). It's the same equation lesson 40 used to price a fixed feedback gain, and the one in Lewis problem 2.2-2.

For a scalar $x(k+1) = 0.5x(k)$ with $Q = 1$: $0.25P - P = -1$, so $P = 4/3 > 0$: stable.

## The indirect method
<!-- bite: a3bfad30-c2f1-4621-b856-9351b8769453 -->

Now the big payoff. **Lyapunov's indirect method**: if the linearisation of a nonlinear system at an equilibrium is asymptotically stable, then the equilibrium of the **nonlinear** system is asymptotically stable too.

Here's why (MIT exercise 13.7). Write the system as

$$\dot{x} = Ax + h(x), \qquad \frac{\|h(x)\|}{\|x\|} \to 0 \text{ as } \|x\| \to 0$$

where $A$ is the Jacobian and $h$ holds the higher-order terms. Since $A$ is stable, solve $PA + A^TP = -I$ and use $V = x^TPx$:

$$\dot{V} = -x^Tx + 2x^TPh(x) \le -\|x\|^2 + 2\|P\|\,\|h(x)\|\,\|x\|$$

That's negative whenever $\|h(x)\|/\|x\| < 1/(2\|P\|)$, and near enough to the origin the higher-order terms are that small. So $\dot{V} < 0$ in a small neighbourhood: asymptotically stable.

For the matrix above, $\|P\| = 1.309$ (its largest eigenvalue), so any nonlinear terms smaller than $0.38\|x\|$ can't spoil stability.

## What the indirect method says, in full
<!-- bite: 5fbdb5e6-2b9d-470d-93d8-82134d6f52b5 -->

1. **All eigenvalues of the Jacobian in the open left half plane**: locally asymptotically stable.
2. **Any eigenvalue in the open right half plane**: unstable.
3. **Eigenvalues on the imaginary axis, none on the right**: **no conclusion**. This is lesson 49's centre: $\dot{r} = -\mu r^3$ could go either way. Use the direct method instead.

So the indirect method justifies everything we did with linearisation in lessons 07 and 32, and also marks its limit.

## Gradient systems and gradient descent
<!-- bite: 4b5afdf5-d4ee-4c9b-8d4f-b75963f6a1a3 -->

One last family, which links control to machine learning. A **gradient system** moves straight downhill on a potential $P(x)$:

$$\dot{x} = -\nabla P(x)$$

If $x^*$ is an isolated local minimum of $P$, take $V(x) = P(x) - P(x^*)$, which is lpd around $x^*$. Then $\dot{V} = \nabla P \cdot \dot{x} = -\|\nabla P(x)\|^2 \le 0$, and it's zero only where the gradient vanishes, which near an isolated minimum is only at $x^*$. So $x^*$ is **asymptotically stable** (MIT exercise 13.3).

That's why continuous **gradient descent** converges to a local minimum from nearby. The discrete version, $x(k+1) = x(k) - \alpha\nabla f(x(k))$, needs a step size $\alpha$ that's not too big. For $f = \tfrac12x^TQx$, the step is $x(k+1) = (I - \alpha Q)x(k)$, which converges exactly when $0 < \alpha < 2/\lambda_{max}(Q)$ (MIT exercise 13.4). → [[machine-learning/index|Machine learning]]

## Common pitfalls
<!-- bite: 1a4575de-58d3-44ea-ae6e-c0b546400176 -->

1. **Solving for a non-symmetric $P$.** Take $P$ symmetric; for a stable $A$ the solution is unique and symmetric.
2. **Checking only that $P$ exists.** It must be positive definite.
3. **Using the indirect method at a centre.** Eigenvalues on the axis give no conclusion.
4. **Mixing up the two equations.** Continuous: $PA + A^TP = -Q$. Discrete: $A^TPA - P = -Q$.

## Check your understanding
<!-- bite: c1d61ed9-2f52-48e4-b802-e68acd79b296 -->

Try each one before you open the answer.

1. <!-- q: exact id="9c4f1a62" answer="0.16667" accept="1/6" sigfigs="3" -->
   For the scalar system $\dot{x} = -3x$, solve the Lyapunov equation $2aP = -1$ (with $a = -3$, $Q = 1$). What is $P$?

   <details><summary>Answer</summary>

   $-6P = -1$, so $P = 1/6 \approx 0.167$. Positive, so stable.

   </details>

2. <!-- q: exact id="e2a85b03" answer="1.3333" accept="4/3" sigfigs="3" -->
   For the discrete scalar system $x(k+1) = 0.5x(k)$, solve $a^2P - P = -1$. What is $P$?

   <details><summary>Answer</summary>

   $0.25P - P = -1$, so $P = 4/3 \approx 1.33$.

   </details>

3. <!-- q: mcq id="6b0d3e98" -->
   A nonlinear system's Jacobian at an equilibrium has eigenvalues $-2$ and $0$. What does the indirect method conclude?

   - [ ] Asymptotically stable
   - [ ] Unstable
   - [x] Nothing: an eigenvalue is on the imaginary axis
   - [ ] Marginally stable

   <details><summary>Answer</summary>

   An eigenvalue at 0 is on the imaginary axis, so the linearisation can't decide. The higher-order terms do; use the direct method.

   </details>

4. <!-- q: exact id="3f7c9a20" answer="0.5" accept="1/2" -->
   Gradient descent on $f = \tfrac12x^TQx$ with $Q$ having eigenvalues 1 and 4. What is the largest step size $\alpha$ for which it converges (the bound $2/\lambda_{max}$)?

   <details><summary>Answer</summary>

   $2/4 = 0.5$. Any $0 < \alpha < 0.5$ converges.

   </details>

5. <!-- q: open id="a81e6c47" -->
   Explain in your own words why a stable linearisation guarantees local stability of the nonlinear system.

   <details><summary>Answer</summary>

   Because the linearisation is stable, the Lyapunov equation gives a quadratic $V$ whose derivative along the linear system is $-\|x\|^2$. The nonlinear terms add something to $\dot{V}$ that shrinks faster than $\|x\|^2$ near the origin, so close enough in, the $-\|x\|^2$ term wins and $\dot{V}$ stays negative. That makes $V$ a Lyapunov function for the nonlinear system near the equilibrium.

   </details>

## Before moving on
<!-- bite: d2c3d305-42c2-439b-ba82-3964b5ed8e9b -->

You can solve the Lyapunov equation, use it as a stability test, and explain the indirect method. That completes stability analysis. **Next:** [[control-theory/56-nonlinear-design-1|56 — Nonlinear Design 1: Describing Functions and Gain Scheduling]], which turns from analysing nonlinear systems to controlling them.

## Related
<!-- bite: ae0f13ed-b879-4753-a39f-1e53e9dc7362 -->

- [[control-theory/40-optimal-control-3|40 — Optimal Control 3: The Discrete Riccati Equation]]: the discrete Lyapunov equation pricing a gain.
- [[control-theory/49-phase-plane-3|49 — Phase Plane 3: Linearising Around an Equilibrium]]: classifying equilibria by linearisation.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: f50c6f3c-aa9a-4b22-9407-a030cb77f3bf -->

**Level:** Advanced. **Covers:** the continuous and discrete Lyapunov equations, solving one by hand, the stability test both ways, the indirect method and its proof, and gradient systems and gradient descent.

**Where it sits:** lesson 55 of 58, part 4 of 4 on Lyapunov stability.

**Source:** the author's notes from Dahleh, Dahleh and Verghese, *Lectures on Dynamic Systems and Control*, chapter 13 (exercises 13.3, 13.4, 13.6, 13.7 and 13.8), MIT OpenCourseWare 6.241J. Numbers checked in `scripts/diagrams/control_theory.py`.
