---
id: f3f94552-542c-463c-9980-d19d2809a34d
---

# LQR

The linear quadratic regulator is the feedback controller that minimises a quadratic cost on state error and effort forever, found by solving one algebraic Riccati equation.

## Before you start
<!-- bite: e43bf3dd-8fb9-4b3e-ab25-092a272e871f -->

You should have read [[control-theory/40-optimal-control-3|40 — Optimal Control 3: The Discrete Riccati Equation]] and [[control-theory/41-optimal-control-4|41 — Optimal Control 4: Continuous Time and the Euler–Lagrange Equations]], and know what pole placement does ([[control-theory/35-pole-placement|35 — Pole Placement]]).

After this lesson you will be able to:

1. write the infinite-horizon LQR cost and its solution, $K = R^{-1}B^TP$ with the algebraic Riccati equation;
2. solve a scalar LQR by hand;
3. choose $Q$ and $R$ with Bryson's rule and tune their ratio;
4. say why LQR beats pole placement, including its guaranteed margins.

## What LQR is
<!-- bite: 2c590a14-b012-4626-ba2f-a57392e90cd4 -->

Lessons 38 to 41 built optimal control from the ground up, over a fixed horizon. Now let the horizon go to infinity, keep the plant linear and the cost quadratic, and the answer becomes the most-used modern controller:

$$J = \int_0^\infty \left(\mathbf{x}^TQ\mathbf{x} + \mathbf{u}^TR\mathbf{u}\right)dt$$

1. $\mathbf{x}^TQ\mathbf{x}$ is a **penalty on state error**: "being off target is bad".
2. $\mathbf{u}^TR\mathbf{u}$ is a **penalty on effort**: "actuation costs fuel, wear and heat".

Pole placement asked "where do I want the poles?", which on a 12-state drone is twelve numbers to guess. LQR asks "what do I care about, and what will I pay?", and **$Q$ and $R$ mean something physical** in a way pole locations don't. "Position error matters ten times more than speed error, and I have limited torque" is a sentence an engineer can say with confidence.

## The kid version
<!-- bite: 7f9fe591-334f-4a16-a045-848284ddcb71 -->

You're teaching someone to park a car. You could tell them exactly how far to turn the wheel at every moment (pole placement). Or you could just say "end up close to the kerb, but don't yank the wheel", and let them work out the moves. LQR is the second way: you state the priorities, and the maths finds the best steering rule.

**Where the analogy stops working.** A learner driver adapts as they go. LQR computes its rule once, from the model, so if the model is wrong the rule is wrong, faithfully.

## The LQR solution
<!-- bite: 783a0038-5286-4f8f-8b44-9aee7fe31f01 -->

The answer is linear state feedback, the same structure as pole placement, with $K$ computed rather than chosen:

$$\mathbf{u} = -K\mathbf{x}, \qquad K = R^{-1}B^TP$$

where $P$ solves the **algebraic Riccati equation**:

$$A^TP + PA - PBR^{-1}B^TP + Q = 0$$

This is the continuous, steady-state version of lesson 40's backward sweep: with an infinite horizon, the sweep has settled, so $\dot{P} = 0$. And the minimum cost from state $\mathbf{x}_0$ is $\tfrac12\mathbf{x}_0^TP\mathbf{x}_0$ (or $\mathbf{x}_0^TP\mathbf{x}_0$ without the $\tfrac12$ in $J$).

In code it's one line, `K = lqr(A, B, Q, R)`, and the solver is reliable. **You don't solve it by hand** beyond one or two states; the effort goes into choosing the weights.

## A scalar LQR on the car
<!-- bite: 7ada4924-1b35-4e4d-a896-781cb5dd7e35 -->

One state, so the algebraic Riccati equation is a quadratic you can solve. The car is $\dot{v} = -0.05v + 0.001u$, so $A = -0.05$ and $B = 0.001$. Choose the weights with Bryson's rule (next section): 1 m/s of error is acceptable and so is 1000 N of force, giving $Q = 1/1^2 = 1$ and $R = 1/1000^2 = 10^{-6}$.

The Riccati equation becomes $2AP - P^2B^2/R + Q = 0$:

$$-0.1P - P^2 + 1 = 0 \quad\Rightarrow\quad P = \frac{-0.1 + \sqrt{0.01 + 4}}{2} = 0.951$$

(taking the positive root, since $P$ must be positive). Then $K = R^{-1}BP = 10^6 \times 0.001 \times 0.951 = 951$ N per m/s. The closed-loop pole is $A - BK = -0.05 - 0.951 = -1.00$ rad/s: the car now settles in about 4 s instead of 80, and a 1 m/s error asks for 951 N, right at the "acceptable" level we chose.

## Choosing Q and R
<!-- bite: 51d877bb-ebc6-4e87-b5d4-ff4990781d65 -->

The actual design work. **Start diagonal**: $Q = \text{diag}(q_1, \ldots, q_n)$, $R = \text{diag}(r_1, \ldots, r_m)$. Cross terms are rarely needed.

**Bryson's rule** is the standard starting point, and it fixes the units problem:

$$q_i = \frac{1}{(\text{largest acceptable } x_i)^2}, \qquad r_j = \frac{1}{(\text{largest acceptable } u_j)^2}$$

Each term then contributes about 1 when its variable is at its acceptable limit, so states in radians and states in metres become comparable. Without it, a badly scaled $Q$ silently ignores whichever state has small numbers.

**Then tune the ratio.** Only $Q$ relative to $R$ matters; scaling both by the same number changes nothing.

1. **$Q$ up relative to $R$**: tighter, faster, more effort, more noise passed to the actuator.
2. **$R$ up relative to $Q$**: gentler, slower, less effort, more robust.

## The tuning loop
<!-- bite: f8179454-3f5c-4d56-bd2e-2832928f95b2 -->

The workflow that works: Bryson's rule, simulate, then ask. Is the actuator saturating? Raise $R$. Too slow? Raise $Q$. Repeat.

Remember this one: **always check the control signal**, not just the state. An LQR design that looks perfect while demanding three times the available torque is not a design.

Two facts people miss:

1. **LQR is stable by construction** whenever $(A, B)$ is stabilisable and $(A, Q^{1/2})$ is detectable (lesson 34). For any positive weights, you can't accidentally design an unstable LQR.
2. **"Optimal" means optimal for that cost.** If the response is bad, the cost is wrong, not the solver. LQR faithfully turns a statement of priorities into a controller; bad priorities give a bad controller.

## Why it beats pole placement
<!-- bite: e464db93-af83-4e1e-af15-786116d5f43b -->

| | Pole placement | LQR |
| --- | --- | --- |
| Tuning knobs | $n$ pole locations | $Q$, $R$, physically meaningful |
| Many inputs | $K$ not unique, awkward | natural, one answer |
| Control effort | ignored | explicitly penalised |
| Stability | yours to ensure | guaranteed |
| Margins | none promised | GM ∞ upward, 0.5 downward, PM ≥ 60° |

That last row is the striking result. **Every LQR state-feedback design has an infinite upward gain margin, can lose half its gain, and has at least 60° of phase margin**, automatically (lesson 25). That's exactly what pole placement fails to provide. It's why LQR is usually the better way to *do* pole placement: tune $Q$ and $R$, and the poles land somewhere sensible on their own.

## Common pitfalls
<!-- bite: f779bcfc-2119-47f4-9174-e229e4b3919f -->

1. **Taking the negative root of the Riccati equation.** $P$ must be positive (definite).
2. **Unscaled weights.** Use Bryson's rule, or small-valued states get ignored.
3. **Tuning $Q$ and $R$ both upward.** Only their ratio matters.
4. **Ignoring the control signal.** Check it every time.

## Check your understanding
<!-- bite: 77bcef9c-64d5-47c4-9bae-2763ce06d127 -->

Try each one before you open the answer.

1. <!-- q: exact id="9a2c7e14" answer="0.0004" accept="4e-4|4×10^-4" -->
   By Bryson's rule, a state that may be off by at most 50 should get what weight $q$?

   <details><summary>Answer</summary>

   $q = 1/50^2 = 1/2500 = 0.0004$.

   </details>

2. <!-- q: exact id="d3f6b081" answer="1.4142" sigfigs="3" -->
   A scalar plant $\dot{x} = u$ ($A = 0$, $B = 1$) has $Q = 2$, $R = 1$. The algebraic Riccati equation is $-P^2 + 2 = 0$. What is the LQR gain $K = BP/R$?

   <details><summary>Answer</summary>

   $P = \sqrt2 = 1.414$ (positive root), so $K = 1.414$.

   </details>

3. <!-- q: exact id="4e81c5a9" answer="-2.236" accept="−2.236" sigfigs="3" -->
   A scalar plant $\dot{x} = x + u$ ($A = 1$, $B = 1$) has $Q = 4$, $R = 1$. The algebraic Riccati equation $2P - P^2 + 4 = 0$ gives $P = 1 + \sqrt5$. Where is the closed-loop pole $A - BK$?

   <details><summary>Answer</summary>

   $K = P = 3.236$, so $A - K = 1 - 3.236 = -2.236$. The unstable plant is now stable, as LQR guarantees.

   </details>

4. <!-- q: mcq id="7b0e3d62" -->
   An LQR design keeps saturating the motor. What should you change first?

   - [x] Increase $R$ relative to $Q$
   - [ ] Increase $Q$ relative to $R$
   - [ ] Multiply both $Q$ and $R$ by 10
   - [ ] Switch to pole placement

   <details><summary>Answer</summary>

   Raising $R$ makes effort more expensive, so the controller asks for less. Scaling both changes nothing.

   </details>

5. <!-- q: open id="c61f8a27" -->
   Give two advantages of LQR over pole placement for a drone with four motors and twelve states.

   <details><summary>Answer</summary>

   You tune a few physically meaningful weights instead of guessing twelve pole locations, and with four inputs the gain matrix comes out unique instead of needing extra choices. It also penalises motor effort, is stable by construction, and comes with guaranteed margins (infinite upward gain margin, at least 60° phase margin).

   </details>

## Before moving on
<!-- bite: d4d8ff2e-c97d-4ea3-aebf-b3b692bf34d6 -->

You can solve a scalar LQR, choose weights with Bryson's rule, and explain the guaranteed margins. **Next:** [[control-theory/43-lqg-and-mpc|43 — LQG and MPC]], where adding a Kalman filter quietly destroys those margins, and model predictive control adds the one thing LQR can't handle: limits.

## Related
<!-- bite: c3f6ffad-fcb4-4623-9760-dafa25052c91 -->

- [[control-theory/35-pole-placement|35 — Pole Placement]]: the alternative way to choose $K$.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 5e1c3d3c-af5e-4e9a-b4d3-a7a52dd1cbec -->

**Level:** Advanced. **Covers:** the infinite-horizon LQR, the algebraic Riccati equation, a scalar LQR on the car, Bryson's rule and tuning, stability by construction, and the guaranteed margins.

**Where it sits:** lesson 42 of 58, the first of two on modern optimal controllers, after the four optimal-control lessons.

**Source:** `[reference]`, assembled from standard control texts. Numbers checked in `scripts/diagrams/control_theory.py`.
