---
id: ed16d6bc-dbd4-4664-8802-99d5f9d2d7a7
---

# Optimal Control 1: The Performance Index and the Discrete Recipe

Optimal control chooses the inputs that make a cost smallest, using three equations built from one function, the Hamiltonian.

## Before you start
<!-- bite: 2f179a0d-1c09-42a6-8642-236cd4027be3 -->

You should have read [[control-theory/35-pole-placement|35 — Pole Placement]], and be able to minimise a function by setting its derivative to zero, including with a Lagrange multiplier ([[mathematics/06-calculus/04-calculus-3/03-optimization|optimisation in calculus 3]]).

After this lesson you will be able to:

1. write a performance index for a problem in words, and recognise the standard kinds;
2. form the Hamiltonian and write the state, costate and stationarity equations;
3. state the boundary conditions for a fixed or a free final state;
4. solve a small two-step problem by hand, and check the answer by brute force.

## What optimal control is
<!-- bite: c8f9bc3d-01f4-4898-b5a8-fff3ce01d22b -->

Pole placement asked "where should the poles go?", and had no good way to answer. Optimal control asks a better question: **what do I care about, and what am I willing to pay for it?** Write the answer as a number, the **cost**, and let maths find the inputs that make it smallest.

For a discrete-time system that steps from $k = 0$ to a final step $N$,

$$x_{k+1} = f^k(x_k, u_k), \qquad J = \phi(x_N) + \sum_{k=0}^{N-1} L^k(x_k, u_k)$$

$J$ is the **performance index**. $L^k$ is the cost charged at every step, and $\phi$ is an extra cost on where you end up. This lesson and the next three work through the problem sheets from the author's optimal-control course (Lewis's *Optimal Control*, sections 2.1, 2.2 and 3.2).

## The kid version
<!-- bite: 01abe48c-5a6c-481b-adf9-4de704f6c3df -->

You're driving home with a fixed amount of fuel money, and every litre has a price. Spend too little early and you're late; spend too much and you're broke. The trick of optimal control is to attach a **price tag** to the car's position at every moment: how much it's worth to be a bit further along *here*. Once you know the prices, every step's decision is easy: spend until the extra fuel costs more than the progress is worth.

**Where the analogy stops working.** Fuel prices are given to you. Here you must work the prices out *backwards* from the destination, while the car moves *forwards* from home, and that's what makes the problem hard.

## Terms used in optimal control
<!-- bite: 689c1e77-d7cc-4b65-8145-16b006aa6aa0 -->

1. **Performance index**: This is also known as the **cost** or **cost function**, $J$. It is the single number you want to make as small as possible.
2. **Horizon**: This is the final step $N$ (or final time $T$), where the problem ends.
3. **Running cost**: This is $L^k(x_k, u_k)$, the cost charged at each step, such as $\tfrac12 u_k^2$ for effort used.
4. **Terminal cost**: This is $\phi(x_N)$, the cost on the final state, such as $5x_N^2$ for ending up away from zero.
5. **Costate**: This is also known as the **Lagrange multiplier**, $\lambda_k$. It is the price tag on the state at step $k$: how much the best possible cost would change if $x_k$ were nudged.
6. **Hamiltonian**: This is $H^k = L^k + \lambda_{k+1}^T f^k$: this step's cost plus the priced value of where it sends the state.

## The standard performance indices
<!-- bite: dbf09af2-ded4-46dc-9ea0-832fbe6fe73d -->

Each is a sentence in words first:

1. **Minimum energy**: "get there using as little effort as possible": $J = \tfrac12\sum u_k^2$, with the final state fixed.
2. **Quadratic (LQ)**: "keep the state small without using too much effort": $J = \tfrac12 x_N^TS_Nx_N + \tfrac12\sum(x_k^TQx_k + u_k^TRu_k)$. The weights $Q$, $R$ and $S_N$ set the trade.
3. **Terminal only**: "end up as close to the target as possible": $J = \phi(x_N)$.
4. **Minimum time**: "get there as fast as possible", with limits on the input. Covered in Lewis chapter 5.

Remember this one: the cost must actually *penalise* the input in a way that has a minimum. A cost that's **linear** in $u$, like $\sum Ru_k$, has none: you could always save more by pushing harder the cheap way. Lewis problem 2.2-6 asks you to find exactly that problem.

## Why multipliers
<!-- bite: bb2fd509-6c92-403a-8875-8ada50b367d6 -->

We want the smallest $J$, but the $x_k$ aren't free: each one is tied to the last by the dynamics. That's a **constrained** minimisation, and the standard tool is a Lagrange multiplier per constraint. Attach $\lambda_{k+1}$ to the constraint $x_{k+1} = f^k(x_k, u_k)$ and add it to the cost:

$$J' = \phi(x_N) + \sum_{k=0}^{N-1}\Big[L^k + \lambda_{k+1}^T\big(f^k - x_{k+1}\big)\Big]$$

When the dynamics hold, the bracket adds nothing, so $J' = J$. But now every $x_k$ and $u_k$ can be varied freely, and at the minimum the derivative of $J'$ with respect to each must be zero. Grouping the terms with the Hamiltonian $H^k = L^k + \lambda_{k+1}^Tf^k$ gives the recipe.

## The recipe: three equations
<!-- bite: 5453111d-4363-44f3-8d75-9983b1a66150 -->

Setting the derivatives of $J'$ to zero gives:

1. **State equation** (derivative with respect to $\lambda_{k+1}$): $x_{k+1} = \dfrac{\partial H^k}{\partial \lambda_{k+1}} = f^k(x_k, u_k)$. The dynamics, as expected.
2. **Costate equation** (derivative with respect to $x_k$): $\lambda_k = \dfrac{\partial H^k}{\partial x_k}$. The prices, which run **backwards**.
3. **Stationarity** (derivative with respect to $u_k$): $0 = \dfrac{\partial H^k}{\partial u_k}$. The best input at each step.

In words: at each step, choose the input that makes "this step's cost plus the priced value of the next state" stationary, where the prices themselves come from the future.

## The recipe: boundary conditions
<!-- bite: 0a882c53-5044-4e14-8f27-9adce0ce7769 -->

Three equations need starting values at both ends:

1. **At the start**: $x_0$ is given.
2. **At the end, if the final state is fixed** ($x_N = r_N$): that is the condition, and $\lambda_N$ is whatever it needs to be.
3. **At the end, if the final state is free**: $\lambda_N = \dfrac{\partial \phi}{\partial x_N}$. The price of the final state is the slope of the terminal cost.

So the state is pinned at the start and the costate (or state) at the end. This is a **two-point boundary-value problem**: you can't just step forwards, because $\lambda$ runs backwards. That's what makes optimal control hard, and lesson 40 shows the trick that solves it for the LQ case.

## A worked problem: the setup
<!-- bite: ab87cc9b-fb8c-4b3d-8dbb-a911f47ae4fd -->

Lewis problem 2.1-1. A scalar plant that multiplies its state by the input:

$$x_{k+1} = x_ku_k + 1, \qquad J = \tfrac12\sum_{k=0}^{1}u_k^2, \qquad N = 2,\ x_2 = 0$$

Form the Hamiltonian: $H^k = \tfrac12u_k^2 + \lambda_{k+1}(x_ku_k + 1)$.

1. **Costate**: $\lambda_k = \partial H^k/\partial x_k = \lambda_{k+1}u_k$.
2. **Stationarity**: $0 = u_k + \lambda_{k+1}x_k$, so $u_k = -\lambda_{k+1}x_k$.

Eliminate $u_k$ from both (part a):

$$x_{k+1} = 1 - \lambda_{k+1}x_k^2, \qquad \lambda_k = -\lambda_{k+1}^2x_k$$

## A worked problem: solving it
<!-- bite: a70224b1-5eee-4055-8585-fb4fbb0fcb4d -->

Part b: suppose $\lambda_2$ were known. Then $\lambda_1 = -\lambda_2^2x_1$, and $x_1 = 1 - \lambda_1x_0^2 = 1 + \lambda_2^2x_1x_0^2$, so

$$x_1 = \frac{1}{1 - \lambda_2^2x_0^2}$$

The final condition $x_2 = 1 - \lambda_2x_1^2 = 0$ means $\lambda_2x_1^2 = 1$, and substituting $x_1$:

$$\lambda_2 = (1 - \lambda_2^2x_0^2)^2 \quad\Longleftrightarrow\quad x_0^4\lambda_2^4 - 2x_0^2\lambda_2^2 - \lambda_2 + 1 = 0$$

A quartic in $\lambda_2$. Part c sets $x_0 = 1$: $\lambda_2^4 - 2\lambda_2^2 - \lambda_2 + 1 = 0$. Before reading on: how many answers do you expect?

## A worked problem: two candidates
<!-- bite: b1bb323c-a68b-4b78-91d9-2ce5b56aa6d9 -->

The quartic has two real roots, and each gives a complete candidate:

| $\lambda_2$ | $x_1$ | $\lambda_1$ | $u_0$ | $u_1$ | $J$ |
| --- | --- | --- | --- | --- | --- |
| 0.5249 | 1.3803 | −0.3803 | 0.3803 | −0.7245 | **0.3347** |
| 1.4902 | −0.8192 | 1.8192 | −1.8192 | 1.2207 | 2.3998 |

Both reach $x_2 = 0$ and both satisfy the three equations: stationarity only finds *candidates*, the way $f'(x) = 0$ finds both peaks and dips. The optimum is the cheaper one: $u_0 = 0.380$, $u_1 = -0.725$, $J^* = 0.335$.

## Checking by brute force
<!-- bite: 433f6626-b4fa-4a31-96eb-dd5f1e2ff777 -->

With $x_0 = 1$: $x_1 = u_0 + 1$, and $x_2 = 0$ forces $u_1 = -1/x_1$. So $J = \tfrac12\big(u_0^2 + 1/(u_0+1)^2\big)$, one variable. Its minimum, by search, is at $u_0 = 0.380$ with $J = 0.3347$. The recipe was right.

![The cost of problem 2.1-1 as a function of the first input u0, once u1 is chosen to reach zero: a curve with its lowest point at u0 = 0.380, J = 0.335, marked as the optimum. Left of u0 = minus 1, where the cost shoots up to infinity, there is a second, higher dip at u0 = minus 1.82, J = 2.40: the other candidate.](images/ct-oc-bilinear-cost.svg)

## Common pitfalls
<!-- bite: 9b52ef1f-7e27-4801-af8e-128b2e720431 -->

1. **Running the costate forwards.** $\lambda_k$ depends on $\lambda_{k+1}$: it runs from the end backwards.
2. **Taking the first stationary point.** Check every candidate's cost, as in the table.
3. **Forgetting the final boundary condition.** Fixed $x_N$ and free $x_N$ give different conditions.
4. **Using a cost that's linear in $u$.** Stationarity then has no $u$ in it, and there's no minimum without input limits.

## Check your understanding
<!-- bite: 5081213e-d517-49a5-ac9a-aa16e4a6860c -->

Try each one before you open the answer.

1. <!-- q: mcq id="7c2a9e15" -->
   For $x_{k+1} = ax_k + bu_k$ and $L^k = \tfrac12(qx_k^2 + ru_k^2)$, what is the Hamiltonian?

   - [x] $\tfrac12(qx_k^2 + ru_k^2) + \lambda_{k+1}(ax_k + bu_k)$
   - [ ] $\tfrac12(qx_k^2 + ru_k^2) - \lambda_k(ax_k + bu_k)$
   - [ ] $\lambda_{k+1}(ax_k + bu_k)$
   - [ ] $\tfrac12(qx_k^2 + ru_k^2) + \lambda_{k+1}x_{k+1}$

   <details><summary>Answer</summary>

   $H^k = L^k + \lambda_{k+1}f^k$, with the dynamics written out.

   </details>

2. <!-- q: mcq id="1e5b8d40" -->
   Same problem. What does stationarity give?

   - [ ] $u_k = -\lambda_kb/r$
   - [x] $u_k = -b\lambda_{k+1}/r$
   - [ ] $u_k = -a\lambda_{k+1}/r$
   - [ ] $u_k = \lambda_{k+1}/(rb)$

   <details><summary>Answer</summary>

   $\partial H/\partial u_k = ru_k + b\lambda_{k+1} = 0$, so $u_k = -b\lambda_{k+1}/r$.

   </details>

3. <!-- q: mcq id="c08f3d62" -->
   Same problem. What is the costate equation?

   - [x] $\lambda_k = qx_k + a\lambda_{k+1}$
   - [ ] $\lambda_{k+1} = qx_k + a\lambda_k$
   - [ ] $\lambda_k = ru_k + b\lambda_{k+1}$
   - [ ] $\lambda_k = a\lambda_{k+1}$

   <details><summary>Answer</summary>

   $\lambda_k = \partial H/\partial x_k = qx_k + a\lambda_{k+1}$. It runs backwards from $\lambda_N$.

   </details>

4. <!-- q: exact id="9d4e2b76" answer="6" -->
   A problem has terminal cost $\phi = 3x_N^2$ and a free final state. If $x_N = 1$, what is $\lambda_N$?

   <details><summary>Answer</summary>

   $\lambda_N = \partial\phi/\partial x_N = 6x_N = 6$.

   </details>

5. <!-- q: open id="5f1c7a03" -->
   Lewis problem 2.2-6 uses the linear cost $J = S_Nx_N + \sum(Qx_k + Ru_k)$ with $x_{k+1} = Ax_k + Bu_k$. Write the stationarity condition and explain what goes wrong.

   <details><summary>Answer</summary>

   $H^k = Qx_k + Ru_k + \lambda_{k+1}^T(Ax_k + Bu_k)$, so $\partial H/\partial u_k = R + B^T\lambda_{k+1} = 0$. The input doesn't appear, so stationarity can't be solved for $u_k$: with no limit on $u$, the cost can be driven down without end. A linear cost needs bounds on the input, and then the answer is "bang-bang" (always at a limit), handled by Pontryagin's principle in Lewis section 5.2.

   </details>

## Practice: the vector version
<!-- bite: ee9b491a-00c0-4b28-a1c2-922943edbc8e -->

Lewis problem 2.1-2: the bilinear system $x_{k+1} = Ax_k + Dx_ku_k + bu_k$ with $x_k \in \mathbb{R}^n$, a scalar input, and $J = \tfrac12x_N^TS_Nx_N + \tfrac12\sum(x_k^TQx_k + ru_k^2)$. Form the Hamiltonian and show that the optimal control is $u_k = -(b + Dx_k)^T\lambda_{k+1}/r$, then write the state and costate equations with $u_k$ eliminated.

**Done when:** your costate equation matches $\lambda_k = Qx_k + A^T\lambda_{k+1} - (b + Dx_k)^T\lambda_{k+1}\,D^T\lambda_{k+1}/r$. The [[control-theory/optimal-control-problem-bank|problem bank]] has the check.

## Before moving on
<!-- bite: 19339ea4-a49d-48c2-8b0e-6a1b04029fc7 -->

You can write the Hamiltonian, the three equations and the boundary conditions, and solve a two-step problem. **Next:** [[control-theory/39-optimal-control-2|39 — Optimal Control 2: Minimum-Energy Control and Deadbeat]], which solves the fixed-final-state problem in closed form for a linear plant.

## Related
<!-- bite: fae54a23-7db4-4bc0-8c03-bde4e851a704 -->

- [[operations-research/08-dynamic-programming|Dynamic Programming]]: the other road to the same answers.
- [[control-theory/optimal-control-problem-bank|Optimal control problem bank]]: every problem from the sheets.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 0a487107-3668-4de0-b550-a344e62c818c -->

**Level:** Advanced. **Covers:** performance indices, the Hamiltonian, the state, costate and stationarity equations, boundary conditions, and Lewis problem 2.1-1 solved and checked.

**Where it sits:** lesson 38 of 58, part 1 of 4 on optimal control.

**Source:** the author's optimal-control problem sheets, from F. L. Lewis, *Optimal Control*, chapter 2 (problems 2.1-1, 2.1-2, 2.2-6). Numbers and the cost curve are checked in `scripts/diagrams/control_theory.py`.
