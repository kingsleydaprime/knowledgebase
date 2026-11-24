---
id: 8a21710f-0ded-4cd6-9d07-63fd98c81782
---

# Modelling 3: Translational Mechanical Systems

A mechanical system moving in straight lines is built from masses, springs and dampers, and writing Newton's law at each moving point gives its transfer function.

## Before you start
<!-- bite: 0c06ea5a-e55d-462b-8ba8-7ec852350ed7 -->

You should have read [[control-theory/04-modelling-2|04 — Modelling 2: Transfer Functions of Electrical Circuits]], including mesh analysis with Cramer's rule.

After this lesson you will be able to:

1. write the force law for a mass, a spring and a damper, and its $s$-domain "impedance";
2. draw a mechanical network and write the equation at each displacement;
3. find the transfer function of a two-mass system with Cramer's rule;
4. combine springs in parallel and in series, and use the force-voltage analogy.

## What this lesson covers
<!-- bite: d6c5efcd-066b-44c9-95d1-7a7ceeb1399c -->

Lesson 13 met the suspension as one mass on a spring and damper. Real machines have several masses joined by springs and dampers: a car body and its wheels, a train of carriages, a building's floors. This lesson gives the method that handles all of them: write Newton's law at every point that can move, transform, and solve, the same way mesh analysis handled loops.

## The kid version
<!-- bite: 13e06b46-2a2a-4fe4-9a0f-5d6d3baa749e -->

Picture two trolleys joined by a spring, the first also tied to a wall by another spring. Push the first: it moves, stretches the spring between them, and that spring tugs the second. Each trolley only "feels" the springs and dampers touching it. Write down what each one feels, and you've described the whole train.

**Where the analogy stops working.** Trolleys are easy to picture; a model of a building with twenty floors isn't. The method doesn't care: one equation per moving point, however many there are.

## The three elements
<!-- bite: 88a66f03-a5c2-40f0-95b2-c1146b7829ce -->

| Element | Force law | In $s$ |
| --- | --- | --- |
| Mass $M$ | $F = M\ddot{x}$ | $Ms^2$ |
| Spring $K$ | $F = K(x_1 - x_2)$ | $K$ |
| Damper $B$ | $F = B(\dot{x}_1 - \dot{x}_2)$ | $Bs$ |

A spring pulls in proportion to how much it's stretched, the **difference** of its two ends' positions; a damper (a dashpot: a piston in oil) resists the **difference** of their speeds. If one end is fixed to the ground, that end's position is zero. $K$ is in N/m and $B$ in N·s/m.

## Springs together
<!-- bite: fc168b20-216f-44f3-8be5-6ee8257a7bb2 -->

Two springs on the same mass, side by side (in **parallel**), both stretch by $x$: $F = k_1x + k_2x$, so they act like one spring of stiffness $k_1 + k_2$.

Two springs end to end (in **series**), with the join at position $y$ (the textbook's example 1): $F = k_2(x - y)$ and $0 = k_1y + k_2(y - x)$. Eliminate $y$ and $F = \dfrac{k_1k_2}{k_1 + k_2}x$: softer than either.

So springs combine like conductances, the opposite of resistors. With $k_1 = 300$ and $k_2 = 600$ N/m: parallel 900, series 200.

## The method: one equation per displacement
<!-- bite: c40bdf93-eda2-4952-b9ae-b94417204f91 -->

1. Draw the **mechanical network**: a node for each mass's displacement, with each spring and damper as a link between nodes (or to the ground).
2. At each node, write: **applied force = mass term + every spring and damper force pulling back**, each using the difference between its two ends.
3. Take the Laplace transform, starting from rest.
4. Solve the equations for the output, by substitution or Cramer's rule.

In $s$, the equation at a node always has the same shape: **(sum of everything connected to this node) × this displacement − (what's connected to each neighbour) × that displacement = applied force.** Exactly like mesh analysis.

## A two-mass system
<!-- bite: 18772c00-fd09-4c5f-ad5a-fecf1c00fe7b -->

The textbook's example 3: mass $m_1$ tied to the wall by $k_1$; mass $m_2$ tied to the other wall by $k_3$; between them a spring $k_2$ and a damper $b$. The force $f$ pushes $m_1$.

At $x_1$: $F = (m_1s^2 + bs + k_1 + k_2)X_1 - (bs + k_2)X_2$

At $x_2$: $0 = -(bs + k_2)X_1 + (m_2s^2 + bs + k_2 + k_3)X_2$

By Cramer's rule:

$$\frac{X_1}{F} = \frac{m_2s^2 + bs + k_2 + k_3}{(m_1s^2 + bs + k_1 + k_2)(m_2s^2 + bs + k_2 + k_3) - (bs + k_2)^2}$$

## The two-mass system with numbers
<!-- bite: 785cab20-9931-485b-b02c-afa15b78d1a2 -->

Set every value to 1. Then each diagonal term is $a = s^2 + s + 2$ and the shared term is $b = s + 1$, so the denominator is $a^2 - b^2 = (a - b)(a + b)$:

$$\frac{X_1}{F} = \frac{s^2 + s + 2}{(s^2 + 1)(s^2 + 2s + 3)}$$

Predict before reading on: why is there an undamped pair of poles at $\pm j$, when the system has a damper?

The poles at $\pm j$ are the mode where **both masses move together**, the same distance in the same direction. The spring and damper between them are never stretched, so the damper does nothing, and the masses bounce on the wall springs for ever. The other pair, $s^2 + 2s + 3$, is the mode where they move in opposite directions, which does work the damper, so it decays. A damper only damps the motions that move its two ends relative to each other.

## The force-voltage analogy
<!-- bite: 5fc5e3d8-89dc-4e98-98c5-dc8c6f33297d -->

Compare a node equation, $F = (Ms^2 + Bs + K)X$, with a series RLC loop, $V = (Ls + R + 1/(Cs))I$. Writing it with speed $sX$ instead of displacement, they match term by term:

1. **Force** ↔ voltage.
2. **Speed** ↔ current.
3. **Mass** ↔ inductance, **damper** ↔ resistance, **spring** ↔ 1/capacitance.

That's why the textbook can show (its example 13) a mechanical system and an electrical circuit with identical transfer functions. Engineers once built analogue computers on exactly this: model the machine as a circuit and measure the circuit.

## From the equations to state space
<!-- bite: a04ab873-ca42-4cca-8322-c4bbf799e24a -->

The same node equations give a state-space model (lesson 30) with each mass's position and speed as states. The textbook's example 5 does this for two masses, with $x_2$ as the output, giving a 4-state model. That's the bridge from this lesson to the modern methods.

## Common pitfalls
<!-- bite: 03e19614-1d8b-4e74-b1be-44bf7bc9e076 -->

1. **Writing a spring force with one end's position only.** Use the difference, unless that end is fixed.
2. **Getting the off-diagonal sign wrong.** Coupling terms are always subtracted.
3. **Adding series springs.** Series springs combine as $k_1k_2/(k_1 + k_2)$.
4. **Expecting a damper to damp every mode.** It only damps motion that stretches it.

## Check your understanding
<!-- bite: 5819140b-7d7f-4001-844b-4048fe7ea7ca -->

Try each one before you open the answer.

1. <!-- q: exact id="3c8e1d57" answer="240" -->
   Springs of 400 N/m and 600 N/m are joined end to end. What is their combined stiffness, in N/m?

   <details><summary>Answer</summary>

   $400 \times 600/(400 + 600) = 240$ N/m.

   </details>

2. <!-- q: mcq id="9a4f2b60" -->
   A mass $M$ is attached to a wall by a spring $K$ and a damper $B$ side by side, and pushed by force $f$. What is $X/F$?

   - [x] $1/(Ms^2 + Bs + K)$
   - [ ] $Ms^2 + Bs + K$
   - [ ] $1/(Ms^2 + K)$
   - [ ] $K/(Ms^2 + Bs)$

   <details><summary>Answer</summary>

   $F = (Ms^2 + Bs + K)X$, so $X/F = 1/(Ms^2 + Bs + K)$.

   </details>

3. <!-- q: mcq id="e6b30c84" -->
   In a two-mass system, the coupling spring $k_2$ and damper $b$ join $x_1$ and $x_2$. What is the coefficient of $X_2$ in the equation at $x_1$?

   - [ ] $+(bs + k_2)$
   - [x] $-(bs + k_2)$
   - [ ] $-k_2$ only
   - [ ] $m_2s^2$

   <details><summary>Answer</summary>

   The coupling elements appear with a minus sign: $-(bs + k_2)X_2$.

   </details>

4. <!-- q: gap id="1d7c5a38" answers="inductance;resistance" -->
   In the force-voltage analogy, mass corresponds to ___ and a damper corresponds to ___.

   <details><summary>Answer</summary>

   Inductance; resistance. (A spring corresponds to 1/capacitance.)

   </details>

5. <!-- q: open id="b52d9e07" -->
   Two equal masses are each tied to a wall by a spring, and joined to each other by a damper only. One mode of vibration never dies out. Which one, and why?

   <details><summary>Answer</summary>

   The mode where the masses move together, in step. The damper sits between them and only resists their relative motion; when they move together it isn't stretched, so it removes no energy, and that mode oscillates on the wall springs for ever.

   </details>

## Before moving on
<!-- bite: dcff8a5c-1e3d-46f7-8323-4b29ea3acd1c -->

You can model translational mechanical systems with any number of masses. **Next:** [[control-theory/06-modelling-4|06 — Modelling 4: Rotational Systems, Gears and the DC Motor]].

## Related
<!-- bite: be464b80-a61e-4ad4-8772-7231eceb5a29 -->

- [[control-theory/30-state-space-1|30 — State Space 1: States and the State Equation]]: the same equations as states.
- [[continuum-mechanics/index|Continuum Mechanics]]
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 225f609b-e12e-4b1d-b3aa-6df562876564 -->

**Level:** Intermediate. **Covers:** mass, spring and damper laws, springs in parallel and series, mechanical networks and node equations, a two-mass system by Cramer's rule, and the force-voltage analogy.

**Where it sits:** lesson 5 of 58, part 3 of the modelling lessons.

**Source:** the author's course notes, A. M. Hussein, *Control Engineering*, Benha University, chapter 6 (sections 2 to 4, examples 1 to 5 and 13). Numbers checked in `scripts/diagrams/control_theory.py`.
