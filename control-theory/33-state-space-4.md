---
id: 9926ea2b-d439-4a76-ac6e-130162ef0113
---

# State Space 4: Solving the State Equation with Laplace

The Laplace transform solves the state equation in one line, $X(s) = (sI - A)^{-1}\big[x(0) + BU(s)\big]$, and $(sI - A)^{-1}$ is the transform of the state transition matrix.

## Before you start
<!-- bite: 5d4c936f-716f-4b44-b05d-f4f6cfd32406 -->

You should have read [[control-theory/32-state-space-3|32 — State Space 3: From Transfer Function to State Space]], and be able to invert a 2×2 matrix and take inverse Laplace transforms with partial fractions.

After this lesson you will be able to:

1. solve $\dot{x} = Ax + Bu$ in the $s$ domain;
2. find the state transition matrix $\Phi(t)$ from $(sI - A)^{-1}$;
3. split a solution into its zero-input and zero-state parts;
4. diagonalise $A$ with its eigenvectors.

## What this lesson covers
<!-- bite: 54f4d19b-04bf-417f-9341-a25c407a75e9 -->

Lesson State Space 2 wrote the solution with the matrix exponential, $x(t) = e^{At}x(0) + \int_0^te^{A(t-\tau)}Bu(\tau)\,d\tau$, and warned against computing $e^{At}$ from its series. For hand calculation on small systems there's a cleaner route, the one the course notes use: Laplace.

## The kid version
<!-- bite: 82b1dc98-5aaf-439e-b2dc-c3eb0d64a9e5 -->

Solving a set of linked equations in time is like untangling several knotted ropes while they're moving. The Laplace transform freezes them: in the $s$ world the knots become ordinary algebra you can untie with a matrix inverse. Then you transform back to watch the ropes move again.

**Where the analogy stops working.** Freezing ropes is free. Transforming back takes partial fractions for every entry of the matrix, which gets heavy fast beyond two or three states. That's when software takes over.

## The solution in the s domain
<!-- bite: fe5d17b8-eceb-4e98-b1c4-8dd9fda86023 -->

Transform $\dot{x} = Ax + Bu$, keeping the initial state this time: $sX(s) - x(0) = AX(s) + BU(s)$. Collect $X$:

$$X(s) = (sI - A)^{-1}x(0) + (sI - A)^{-1}BU(s)$$

The matrix $\Phi(s) = (sI - A)^{-1}$ is the **resolvent**, and its inverse transform is the **state transition matrix** $\Phi(t) = e^{At}$. So the two terms are:

1. **Zero-input response**, $\Phi(t)x(0)$: what the initial state does by itself.
2. **Zero-state response**, the inverse transform of $\Phi(s)BU(s)$: what the input does from rest.

The output is $y = Cx + Du$, as always.

## Worked: the transition matrix
<!-- bite: f4897f82-6e66-4e59-a3d0-96b2c98cf5c7 -->

$A = \begin{bmatrix}0 & 1 \\ -2 & -3\end{bmatrix}$ (eigenvalues $-1$ and $-2$).

$$sI - A = \begin{bmatrix}s & -1 \\ 2 & s + 3\end{bmatrix}, \qquad (sI - A)^{-1} = \frac{1}{(s+1)(s+2)}\begin{bmatrix}s + 3 & 1 \\ -2 & s\end{bmatrix}$$

Partial fractions on each entry, then transform back:

$$\Phi(t) = \begin{bmatrix}2e^{-t} - e^{-2t} & e^{-t} - e^{-2t} \\ -2e^{-t} + 2e^{-2t} & -e^{-t} + 2e^{-2t}\end{bmatrix}$$

A quick check: at $t = 0$, $\Phi(0) = I$, as it must be (no time, no change). And every entry is built from $e^{-t}$ and $e^{-2t}$: the eigenvalues, again.

## Worked: a full response
<!-- bite: 60cebc6a-1b51-429e-8ab5-580e86fe8a37 -->

Same $A$, with $B = \begin{bmatrix}0 \\ 1\end{bmatrix}$, $x(0) = \begin{bmatrix}1 \\ 0\end{bmatrix}$ and a unit-step input. Predict before reading on: where does $x_1$ settle?

1. **Zero-input**: $\Phi(t)x(0)$ is $\Phi$'s first column: $x_1 = 2e^{-t} - e^{-2t}$.
2. **Zero-state**: $\Phi(s)BU(s) = \dfrac{1}{s(s+1)(s+2)}\begin{bmatrix}1 \\ s\end{bmatrix}$, giving $x_1 = \tfrac12 - e^{-t} + \tfrac12e^{-2t}$.
3. **Total**:

$$x_1(t) = \tfrac12 + e^{-t} - \tfrac12e^{-2t}, \qquad x_2(t) = -e^{-t} + e^{-2t}$$

It starts at 1, as given, and settles at $\tfrac12$: the step's steady state, $-A^{-1}B$'s first entry. A simulation agrees to many decimal places.

## Diagonalisation
<!-- bite: 3fb7127f-508a-4c21-ae1a-87acdc11cb59 -->

If $A$ has $n$ independent eigenvectors, put them as the columns of a matrix $P$. Then

$$P^{-1}AP = \Lambda = \text{diag}(\lambda_1, \ldots, \lambda_n)$$

and with new states $z = P^{-1}x$ the system splits into $n$ separate first-order equations, $\dot{z}_i = \lambda_iz_i + \ldots$: the modal form of lesson State Space 2.

For our $A$: $\lambda = -1$ has eigenvector $[1,\ -1]^T$ and $\lambda = -2$ has $[1,\ -2]^T$. So $P = \begin{bmatrix}1 & 1 \\ -1 & -2\end{bmatrix}$ and $P^{-1}AP = \begin{bmatrix}-1 & 0 \\ 0 & -2\end{bmatrix}$. In those coordinates, $\Phi$ is simply $\text{diag}(e^{-t}, e^{-2t})$.

The course notes also go the other way: transforming a given $A$ into phase-variable form, with a transformation built from the controllability matrix of lesson 34. Both are the same idea: change coordinates, keep the eigenvalues.

## Common pitfalls
<!-- bite: 4cfb92ee-6153-4da3-9701-b86f285ecc82 -->

1. **Dropping $x(0)$.** The state solution keeps the initial condition, unlike a transfer function.
2. **Inverting $sI - A$ wrongly.** For 2×2, swap the diagonal, negate the off-diagonal, divide by the determinant.
3. **Forgetting to check $\Phi(0) = I$.** It catches most algebra slips.
4. **Diagonalising a matrix without enough eigenvectors.** Repeated eigenvalues may need a Jordan form instead.

## Check your understanding
<!-- bite: bc3c8fd0-41d6-450d-ac7f-fa633e9988d8 -->

Try each one before you open the answer.

1. <!-- q: mcq id="2f4d8e61" -->
   What must the state transition matrix equal at $t = 0$?

   - [x] The identity matrix
   - [ ] The zero matrix
   - [ ] $A$
   - [ ] $(sI - A)^{-1}$

   <details><summary>Answer</summary>

   $\Phi(0) = e^{A \cdot 0} = I$: no time has passed, so the state hasn't changed.

   </details>

2. <!-- q: mcq id="a7b60c35" -->
   For $A = \begin{bmatrix}-1 & 0 \\ 0 & -4\end{bmatrix}$, what is $\Phi(t)$?

   - [x] $\begin{bmatrix}e^{-t} & 0 \\ 0 & e^{-4t}\end{bmatrix}$
   - [ ] $\begin{bmatrix}e^{t} & 0 \\ 0 & e^{4t}\end{bmatrix}$
   - [ ] $\begin{bmatrix}1 & -t \\ 0 & 1 - 4t\end{bmatrix}$
   - [ ] $\begin{bmatrix}e^{-t} & e^{-4t} \\ e^{-4t} & e^{-t}\end{bmatrix}$

   <details><summary>Answer</summary>

   A diagonal $A$ gives a diagonal $\Phi$ with $e^{\lambda_it}$ on the diagonal.

   </details>

3. <!-- q: exact id="d1e8a476" answer="0.5" accept="1/2" -->
   With $A = \begin{bmatrix}0 & 1 \\ -2 & -3\end{bmatrix}$ and $B = [0,\ 1]^T$, a unit step is applied. Where does $x_1$ settle, from any start? (Use $x_\infty = -A^{-1}B$.)

   <details><summary>Answer</summary>

   $A^{-1} = \dfrac{1}{2}\begin{bmatrix}-3 & -1 \\ 2 & 0\end{bmatrix}$, so $-A^{-1}B = \tfrac12[1,\ 0]^T$: $x_1 \to 0.5$.

   </details>

4. <!-- q: mcq id="6c3f9b02" -->
   Which part of the solution depends on the input but not on $x(0)$?

   - [ ] The zero-input response
   - [x] The zero-state response
   - [ ] Both
   - [ ] Neither

   <details><summary>Answer</summary>

   The zero-state response is the input's effect starting from rest.

   </details>

5. <!-- q: open id="e9a14d57" -->
   What does diagonalising $A$ achieve, and when can't it be done?

   <details><summary>Answer</summary>

   With the eigenvectors as new coordinates, the states decouple into separate first-order modes, each $\dot{z}_i = \lambda_iz_i$ plus its input, so the system is easy to read and solve. It needs $n$ independent eigenvectors; a repeated eigenvalue with too few eigenvectors needs a Jordan form instead.

   </details>

## Before moving on
<!-- bite: 89426e29-1790-4a6f-8cfa-fd30ead77bff -->

You can solve the state equation by Laplace and diagonalise a system. **Next:** [[control-theory/34-controllability-and-observability|34 — Controllability and Observability]].

## Related
<!-- bite: ea6d32fc-8362-4acb-af58-a0c8f8843ed7 -->

- [[control-theory/52-lyapunov-stability-1|52 — Lyapunov Stability 1: What Stable Means]]: Jordan blocks and stability.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: d44d096a-83d4-4504-bd28-1aa58015abf4 -->

**Level:** Intermediate. **Covers:** the state equation in the $s$ domain, the resolvent and state transition matrix, zero-input and zero-state responses, a full worked solution, and diagonalisation.

**Where it sits:** lesson 33 of 58, part 4 of the state-space lessons.

**Source:** the author's course notes, A. M. Hussein, *Control Engineering*, Benha University, chapter 5 (sections 7 to 10, examples 21 to 25). The solution is checked against a simulation in `scripts/diagrams/control_theory.py`.
