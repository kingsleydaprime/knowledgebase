---
id: 4ca2ea53-ff87-4f08-94ee-7bf12097890c
---

# State Space 3: From Transfer Function to State Space

Decomposition turns any transfer function into a state-space model, almost mechanically in phase-variable form.

## Before you start
<!-- bite: 4760d6a9-9a02-467f-b64f-24b8727e9515 -->

You should have read [[control-theory/31-state-space-2|31 — State Space 2: Solution, Eigenvalues and Conversions]], and know what a companion (controllable canonical) form looks like.

After this lesson you will be able to:

1. write a state-space model for an electrical network from its loop or node equations;
2. decompose a transfer function with a constant numerator into phase-variable form;
3. handle a numerator polynomial, putting its coefficients into $C$;
4. find the characteristic equation from a differential equation, a transfer function or a state equation, and check they agree.

## What decomposition is
<!-- bite: afbb4570-14f0-4b3b-b80c-c00be1319c03 -->

Lesson State Space 2 went from state space to a transfer function with $G(s) = C(sI - A)^{-1}B + D$. The course notes' chapter 5 spends much of its time on the reverse: **decomposition**, turning a transfer function (or a differential equation) into state equations. You'll need it whenever a design method, like pole placement or a Kalman filter, wants state space but the plant came to you as a transfer function.

## The kid version
<!-- bite: 7f7ec643-8344-44fa-a12a-220448f78f51 -->

A recipe written as one long sentence is hard to follow. Breaking it into numbered steps, each using the result of the step before, makes it easy to run one step at a time. Decomposition breaks one high-order equation into a chain of first-order steps, each state being the derivative of the one before.

**Where the analogy stops working.** A recipe's steps are unique. A system can be broken into steps in infinitely many ways; phase-variable form is just the most mechanical one.

## Phase variables
<!-- bite: 4ea1c0ff-307f-44c6-aa81-769847d8a961 -->

For a differential equation $\dddot{y} + a_2\ddot{y} + a_1\dot{y} + a_0y = b_0u$, choose the output and its derivatives as states, the **phase variables**:

$$x_1 = y, \quad x_2 = \dot{y}, \quad x_3 = \ddot{y}$$

Then each state's derivative is the next state, and the last comes from the equation itself:

$$\dot{x}_1 = x_2, \qquad \dot{x}_2 = x_3, \qquad \dot{x}_3 = -a_0x_1 - a_1x_2 - a_2x_3 + b_0u$$

$$A = \begin{bmatrix}0 & 1 & 0 \\ 0 & 0 & 1 \\ -a_0 & -a_1 & -a_2\end{bmatrix}, \quad B = \begin{bmatrix}0 \\ 0 \\ b_0\end{bmatrix}, \quad C = \begin{bmatrix}1 & 0 & 0\end{bmatrix}$$

Ones above the diagonal, the negated denominator coefficients along the bottom row (in reverse order), the input into the last state.

## Worked: a constant numerator
<!-- bite: 416b2ce0-b88c-47ea-b008-7fba82e69316 -->

$\dfrac{C(s)}{R(s)} = \dfrac{24}{s^3 + 9s^2 + 26s + 24}$. Predict the bottom row of $A$ before reading on.

The differential equation is $\dddot{c} + 9\ddot{c} + 26\dot{c} + 24c = 24r$, so

$$A = \begin{bmatrix}0 & 1 & 0 \\ 0 & 0 & 1 \\ -24 & -26 & -9\end{bmatrix}, \qquad B = \begin{bmatrix}0 \\ 0 \\ 24\end{bmatrix}, \qquad C = \begin{bmatrix}1 & 0 & 0\end{bmatrix}$$

The bottom row is $-24, -26, -9$: the denominator, constant term first, with signs flipped.

## A numerator polynomial
<!-- bite: 1763a0b0-055a-491b-8fd8-1640b13d34c1 -->

When the numerator has $s$ terms, $\dfrac{b_2s^2 + b_1s + b_0}{s^3 + a_2s^2 + a_1s + a_0}$, split the transfer function into two blocks in series:

1. $\dfrac{1}{s^3 + a_2s^2 + a_1s + a_0}$, from $R$ to an internal signal $X_1$: this is phase-variable form with $B = [0, 0, 1]^T$.
2. $b_2s^2 + b_1s + b_0$, from $X_1$ to $C$: the output is $b_0x_1 + b_1\dot{x}_1 + b_2\ddot{x}_1 = b_0x_1 + b_1x_2 + b_2x_3$.

So $A$ is unchanged, $B = [0, 0, 1]^T$, and **the numerator's coefficients go into $C$**: $C = [b_0, b_1, b_2]$.

Worked: $\dfrac{s^2 + 7s + 2}{s^3 + 9s^2 + 26s + 24}$ has the same $A$ as before, $B = [0, 0, 1]^T$, and $C = [2,\ 7,\ 1]$. Checking with $C(sI - A)^{-1}B$ at a couple of test values of $s$ gives back exactly this transfer function.

## An electrical network
<!-- bite: f8ad0e7c-c9ce-438b-b927-3d742438d86b -->

For a circuit, use the energy-storage variables (capacitor voltages, inductor currents) as states, as lesson 30 said. Write each component law so that the derivative of a state is alone on the left:

1. Inductor: $L\,\dfrac{di_L}{dt} = v_L$, so $\dfrac{di_L}{dt} = \dfrac{v_L}{L}$.
2. Capacitor: $C\,\dfrac{dv_C}{dt} = i_C$, so $\dfrac{dv_C}{dt} = \dfrac{i_C}{C}$.

Then use Kirchhoff's laws to write $v_L$ and $i_C$ in terms of the states and the input. For the series RLC circuit with states $x_1 = v_C$ and $x_2 = i$:

$$\dot{x}_1 = \frac{1}{C}x_2, \qquad \dot{x}_2 = \frac{1}{L}\big(v - x_1 - Rx_2\big)$$

## Characteristic equations agree
<!-- bite: bc0a8796-96e8-406d-9bd3-46eb91fc0a18 -->

The characteristic equation can be read three ways, and they must agree:

1. **From the differential equation**: replace each derivative by a power of $s$ on the left side. For $\dddot{y} + 9\ddot{y} + 26\dot{y} + 24y$: $s^3 + 9s^2 + 26s + 24 = 0$.
2. **From the transfer function**: its denominator set to zero.
3. **From the state equation**: $\det(sI - A) = 0$.

For the phase-variable $A$ above, expanding $\det(sI - A)$ along its last row gives $s^3 + 9s^2 + 26s + 24$ directly: the companion form is built so that this works.

## Common pitfalls
<!-- bite: ee5869d8-3c36-4595-b525-949a6f10a0f1 -->

1. **Reversing the bottom row.** It runs $-a_0, -a_1, -a_2$, constant term first.
2. **Putting the numerator into $B$.** With a polynomial numerator, $B = [0, 0, 1]^T$ and the numerator goes into $C$.
3. **Choosing non-energy states for a circuit.** Use capacitor voltages and inductor currents.
4. **Expecting decomposition to be unique.** Phase-variable form is one of infinitely many correct models.

## Check your understanding
<!-- bite: 4e0e00cb-5dab-4fd6-bb6a-9776d9b6a839 -->

Try each one before you open the answer.

1. <!-- q: mcq id="6e0b3c98" -->
   What is the bottom row of the phase-variable $A$ for $\dfrac{10}{s^3 + 4s^2 + 7s + 5}$?

   - [x] $[-5,\ -7,\ -4]$
   - [ ] $[-4,\ -7,\ -5]$
   - [ ] $[5,\ 7,\ 4]$
   - [ ] $[0,\ 0,\ 10]$

   <details><summary>Answer</summary>

   The negated denominator coefficients, constant term first: $-5, -7, -4$.

   </details>

2. <!-- q: mcq id="1d8c4a70" -->
   In phase-variable form for $\dfrac{3s^2 + 5s + 2}{s^3 + 6s^2 + 11s + 6}$, what is $C$?

   - [ ] $[1,\ 0,\ 0]$
   - [x] $[2,\ 5,\ 3]$
   - [ ] $[3,\ 5,\ 2]$
   - [ ] $[6,\ 11,\ 6]$

   <details><summary>Answer</summary>

   The numerator's coefficients, constant first: $C = [2, 5, 3]$, with $B = [0, 0, 1]^T$.

   </details>

3. <!-- q: exact id="f7a29e3b" answer="3" -->
   A transfer function's denominator is $s^3 + 2s^2 + 3s + 4$. How many states does its phase-variable model have?

   <details><summary>Answer</summary>

   Three: one per order of the denominator.

   </details>

4. <!-- q: mcq id="8b5e1f26" -->
   $\ddot{y} + 5\dot{y} + 6y = u$. What is $\det(sI - A)$ for its phase-variable model?

   - [x] $s^2 + 5s + 6$
   - [ ] $s^2 - 5s - 6$
   - [ ] $s^2 + 6s + 5$
   - [ ] $5s + 6$

   <details><summary>Answer</summary>

   $A = \begin{bmatrix}0 & 1 \\ -6 & -5\end{bmatrix}$, so $\det(sI - A) = s(s + 5) + 6 = s^2 + 5s + 6$: the same as the differential equation's characteristic equation.

   </details>

5. <!-- q: open id="c3f0e5a1" -->
   Why does a numerator polynomial end up in $C$, not $B$, in phase-variable form?

   <details><summary>Answer</summary>

   The transfer function is split into the denominator part, which drives the phase variables from the input with $B = [0, 0, 1]^T$, followed by the numerator part, which forms the output as a weighted sum of $x_1$ and its derivatives. Those derivatives are the other states, so the weights, the numerator's coefficients, become the output matrix $C$.

   </details>

## Before moving on
<!-- bite: ff9028a0-2eab-43c4-8730-7bd4ad16667f -->

You can turn a transfer function or differential equation into state space. **Next:** [[control-theory/33-state-space-4|33 — State Space 4: Solving the State Equation with Laplace]].

## Related
<!-- bite: 15403219-7475-4cc4-97a4-2b13603eccf0 -->

- [[control-theory/04-modelling-2|04 — Modelling 2: Transfer Functions of Electrical Circuits]]: the circuit equations.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 352ba89e-a3b3-4c75-8a47-0999aa1dc488 -->

**Level:** Intermediate. **Covers:** phase variables, decomposition with a constant numerator and with a numerator polynomial, state equations of a circuit, and characteristic equations three ways.

**Where it sits:** lesson 32 of 58, part 3 of the state-space lessons.

**Source:** the author's course notes, A. M. Hussein, *Control Engineering*, Benha University, chapter 5 (sections 2 to 6); examples after N. S. Nise. Checked numerically in `scripts/diagrams/control_theory.py`.
