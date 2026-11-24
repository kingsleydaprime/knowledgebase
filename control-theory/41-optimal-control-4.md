---
id: e7024ec0-e2e3-4e67-b864-f98b7e41e4ec
---

# Optimal Control 4: Continuous Time and the Euler–Lagrange Equations

In continuous time the same recipe holds, with the sums becoming integrals and the costate becoming a differential equation that runs backwards from the final time.

## Before you start
<!-- bite: 6db92618-1fcd-4c52-88f6-a19264640b79 -->

You should have read [[control-theory/40-optimal-control-3|40 — Optimal Control 3: The Discrete Riccati Equation]], and be able to solve first-order linear differential equations such as $\dot{x} = -x + e^{t}$ ([[mathematics/06-calculus/05-ode|ODEs]]).

After this lesson you will be able to:

1. write the continuous Hamiltonian and the state, costate and stationarity equations;
2. state the boundary conditions for a fixed or free final state;
3. solve a minimum-energy problem on a first-order circuit by hand;
4. set up the same problem for a second-order plant, and say when the equations need a computer.

## What changes in continuous time
<!-- bite: 398c4cea-302a-47cf-a2d2-25faf1c09a4f -->

Lessons 38 to 40 stepped from $k$ to $k+1$. Most physical plants are continuous: the suspension, the circuit, the car. The problem becomes

$$\dot{x} = f(x, u, t), \qquad J = \phi(x(T), T) + \int_0^T L(x, u, t)\,dt$$

The idea is identical: attach a multiplier $\lambda(t)$ to the dynamics at every instant, and set every variation of the cost to zero. What changes is only the form: sums become integrals, and the backward costate *step* becomes a backward costate *differential equation*.

## The kid version
<!-- bite: f95aa0b5-8fd4-4b85-a005-0d874d42d7dc -->

Lesson 38's driver checked prices at every junction. Now the road has no junctions: you can adjust the pedal at every instant. The price tags still exist, but they slide smoothly along the road, and they still have to be worked out backwards from where you're going.

**Where the analogy stops working.** With smooth time you can't list the prices in a table any more; you have to solve an equation for them. That's why most continuous problems beyond the simplest end up on a computer.

## The Euler–Lagrange equations
<!-- bite: 232587f9-714b-4568-b305-82bca087a6bd -->

With the Hamiltonian $H = L + \lambda^Tf$:

1. **State equation**: $\dot{x} = \dfrac{\partial H}{\partial \lambda} = f$.
2. **Costate equation**: $-\dot{\lambda} = \dfrac{\partial H}{\partial x}$. Note the minus sign: the costate runs backwards.
3. **Stationarity**: $0 = \dfrac{\partial H}{\partial u}$.

Together these are called the **Euler–Lagrange equations**, after the calculus of variations they come from.

Boundary conditions, as in discrete time:

1. **At the start**: $x(0)$ given.
2. **Final state fixed**, $x(T) = r$: that is the condition, and $\lambda(T)$ is free.
3. **Final state free**: $\lambda(T) = \dfrac{\partial\phi}{\partial x}\Big|_T$.

## The worked problem: charging an inductor
<!-- bite: ddacc95f-c131-420c-a004-8703aa98b0e8 -->

Lewis problem 3.2-4. A voltage source $u$ drives a 1 Ω resistor and a 1 H inductor in series. The current $x$ obeys (part a)

$$\dot{x} = -x + u$$

Part b: charge the inductor from $x(0) = 0$ to $x(1) = 2$ A while minimising $J = \int_0^1 u^2\,dt$, the energy the source puts in.

Form the Hamiltonian, $H = u^2 + \lambda(-x + u)$:

1. **Costate**: $-\dot{\lambda} = \partial H/\partial x = -\lambda$, so $\dot\lambda = \lambda$ and $\lambda(t) = \lambda(0)e^{t}$.
2. **Stationarity**: $0 = 2u + \lambda$, so $u = -\lambda/2$.

So the optimal voltage has the shape $u(t) = ce^{t}$, rising exponentially, with one number $c = -\lambda(0)/2$ still unknown.

## The worked problem: finding c
<!-- bite: ae00b767-a683-4476-8353-160d08abb674 -->

Put $u = ce^{t}$ into the state equation, $\dot{x} = -x + ce^{t}$, starting from $x(0) = 0$. Its solution is

$$x(t) = \frac{c}{2}\big(e^{t} - e^{-t}\big) = c\sinh t$$

The final condition $x(1) = 2$ gives $c = 2/\sinh 1 = 2/1.1752 = 1.702$. So (parts b and c):

$$u^*(t) = 1.702\,e^{t}, \qquad x^*(t) = 1.702\sinh t$$

The energy used is $J = c^2\int_0^1e^{2t}dt = c^2(e^2 - 1)/2 = 9.25$.

## Why the voltage rises
<!-- bite: fc52ca1b-f6ca-43ee-bd24-63253f22bf57 -->

Why rising? Current leaks away through the resistor, so charge pushed in early has time to leak; voltage applied late does more good. Predict: what would a constant voltage cost? Holding $u$ constant needs $u(1 - e^{-1}) = 2$, so $u = 3.16$ and $J = 10.01$. The optimal shape saves about 8%.

![Charging the inductor from 0 to 2 amps in 1 second: the optimal source voltage rises from 1.70 to 4.63 volts, and the current follows 1.702 sinh t up to 2. A constant 3.16 volt input, shown dashed for comparison, also reaches 2 amps but uses 10.01 units of energy against 9.25.](images/ct-oc-rl.svg)

## A second-order plant: the suspension test
<!-- bite: 3e7608b1-6490-403e-a18c-1605b78c3fe0 -->

Lewis problem 3.2-3 uses a car body on its spring, $m\ddot{y} + ky = u$, with state $x = [y,\ \dot{y}]^T$:

$$\dot{x}_1 = x_2, \qquad \dot{x}_2 = -\frac{k}{m}x_1 + \frac{u}{m}$$

A durability test lifts it from rest to $y(T) = h$, $\dot{y}(T) = 0$, minimising $J = \tfrac12\int_0^Tu^2\,dt$. With $m = k = 1$:

1. $H = \tfrac12u^2 + \lambda_1x_2 + \lambda_2(-x_1 + u)$.
2. Costate: $\dot\lambda_1 = \lambda_2$ and $\dot\lambda_2 = -\lambda_1$, so the costate oscillates: $\lambda_2 = a\cos t + b\sin t$.
3. Stationarity: $u = -\lambda_2$.

So the best force is a sine wave at the body's own natural frequency, pumping it like a child on a swing. The two numbers $a$ and $b$ come from the two final conditions. With $T = 2$ and $h = -3$, they give $u^*(t) = -3.439\cos t + 0.146\sin t$, with cost 4.60. The full working is the practice task below.

## When you need a computer
<!-- bite: d331cb59-9766-4a84-b6da-4118db22eddc -->

Both examples were linear, so the state and costate equations could be solved by hand. In general they can't, for two reasons:

1. **Nonlinear plants** give nonlinear state and costate equations. Lewis problem 3.2-5 (a bilinear plant) shows the optimal control is $u = -(Dx + b)^T\lambda/r$, a product of state and costate, and the resulting cubic equations are "very hard to solve".
2. **Even when solvable, it's a two-point problem**: $x$ known at the start, $\lambda$ (or $x$) at the end.

Numerical **boundary-value solvers** handle it. Lewis's book used a Fortran routine; today `scipy.integrate.solve_bvp` takes the Euler–Lagrange equations and the boundary conditions directly (problem 3.2-6). And for linear plants with quadratic costs, the continuous Riccati equation does the job, which is lesson 42.

Sometimes an approximation works instead. Lewis problem 3.2-2 has $\dot{x} = -x^3 + u$, where for small $x$ the costate is approximately $\lambda = x - x^3$, giving the simple closed loop $\dot{x} = -x$. The [[control-theory/optimal-control-problem-bank|problem bank]] walks through it.

## Common pitfalls
<!-- bite: 3692eafe-6a57-4742-8a99-c165b23d6f27 -->

1. **Dropping the minus sign in the costate equation.** It's $-\dot\lambda = \partial H/\partial x$.
2. **Applying the wrong end condition.** A fixed final state gives a condition on $x(T)$; a free one gives $\lambda(T) = \partial\phi/\partial x$.
3. **Forgetting a factor in stationarity.** With $L = u^2$ (no $\tfrac12$), $u = -\lambda/2$.
4. **Expecting a closed form for every problem.** Nonlinear ones usually need a numerical solver.

## Check your understanding
<!-- bite: 193b8f0c-c827-44a2-96ac-b1407c97985b -->

Try each one before you open the answer.

1. <!-- q: mcq id="a7e3c901" -->
   For $\dot{x} = ax + bu$ and $L = \tfrac12(qx^2 + ru^2)$, what is the costate equation?

   - [x] $-\dot\lambda = qx + a\lambda$
   - [ ] $\dot\lambda = qx + a\lambda$
   - [ ] $-\dot\lambda = ru + b\lambda$
   - [ ] $\dot\lambda = -a\lambda$

   <details><summary>Answer</summary>

   $H = \tfrac12(qx^2 + ru^2) + \lambda(ax + bu)$, and $-\dot\lambda = \partial H/\partial x = qx + a\lambda$.

   </details>

2. <!-- q: mcq id="3c6f0b28" -->
   Same problem. What does stationarity give?

   - [ ] $u = -a\lambda/r$
   - [x] $u = -b\lambda/r$
   - [ ] $u = -\lambda/(2r)$
   - [ ] $u = b\lambda r$

   <details><summary>Answer</summary>

   $\partial H/\partial u = ru + b\lambda = 0$.

   </details>

3. <!-- q: exact id="e9b5d147" answer="6" -->
   A free-final-state problem has terminal cost $\phi = \tfrac32x(T)^2$, and $x(T) = 2$. What is $\lambda(T)$?

   <details><summary>Answer</summary>

   $\lambda(T) = \partial\phi/\partial x = 3x(T) = 6$.

   </details>

4. <!-- q: exact id="58d2a6f3" answer="0.8509" sigfigs="3" -->
   Charge the same inductor ($\dot{x} = -x + u$) from $x(0) = 0$ to $x(1) = 1$ A, minimising $\int_0^1u^2dt$. The optimal input is $u = ce^{t}$ with $c = x(1)/\sinh 1$. What is $c$?

   <details><summary>Answer</summary>

   $c = 1/1.1752 = 0.851$. Half the 2 A answer, because the problem is linear.

   </details>

5. <!-- q: open id="16c4e8d2" -->
   In the inductor problem, why does the optimal voltage rise over time instead of staying constant?

   <details><summary>Answer</summary>

   Current leaks away through the resistor at a rate proportional to itself. Charge pushed in early has longer to leak before the deadline, so it's worth less; voltage applied near the end counts almost fully. Since energy is charged by the square of the voltage, the cheapest plan puts more voltage where it does more good: late.

   </details>

## Practice: the suspension test
<!-- bite: 30f6e31f-d85a-41b8-977c-c4db2b936f42 -->

Do Lewis problem 3.2-3 in full with $m = k = 1$, $T = 2$, $h = -3$:

1. Write the costate solution in terms of the unknown $\lambda(0)$, and the state in terms of $\lambda(0)$ and $x(0) = 0$ (part c).
2. Use $x(2) = [-3,\ 0]^T$ to find $\lambda(0)$ (part d).
3. Write the optimal force and check that $x^*(2) = [-3,\ 0]^T$ (parts e and f), by hand or with a short simulation.

**Done when:** you get $\lambda(0) = [0.146,\ 3.439]^T$ and $u^*(t) = -3.439\cos t + 0.146\sin t$, with $J^* = 4.60$. If yours differ, check the sign in $-\dot\lambda = \partial H/\partial x$ first.

## Before moving on
<!-- bite: c5b78b70-c95c-4397-b033-5411da93dc78 -->

You can write and solve the continuous Euler–Lagrange equations for linear plants. **Next:** [[control-theory/42-lqr|42 — LQR]], where the continuous Riccati equation turns all this into the standard infinite-horizon controller.

## Related
<!-- bite: f25928ad-ea42-415f-b59c-e2cdaa79547a -->

- [[control-theory/optimal-control-problem-bank|Optimal control problem bank]]: problems 3.2-2 to 3.2-6.
- [[control-theory/30-state-space-1|30 — State Space 1: States and the State Equation]]: the suspension and circuit state equations.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 55766f81-0915-4662-ab91-b5c7a70dfb5b -->

**Level:** Advanced. **Covers:** the continuous Hamiltonian, the Euler–Lagrange equations and boundary conditions, Lewis problem 3.2-4 solved, problem 3.2-3 set up, and when to reach for a numerical solver.

**Where it sits:** lesson 41 of 58, part 4 of 4 on optimal control.

**Source:** the author's optimal-control problem sheets, from F. L. Lewis, *Optimal Control*, section 3.2 (problems 3.2-2 to 3.2-6). Numbers and the figure are checked in `scripts/diagrams/control_theory.py`.
