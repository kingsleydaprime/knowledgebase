---
id: 39b50011-85ee-4238-a628-566f3e19f6a1
---

# Nonlinear Optimisation

**Source:** `[reference]` — see [[operations-research/index|the domain note]]. The numbers in the worked example were checked by hand; the SciPy script itself has not been run yet — see "Still to run" in [[operations-research/index|the index]].

## Before you start
<!-- bite: 70c015b2-eb3d-4b1a-ad31-dd9595316c22 -->

You need partial derivatives and the gradient (the vector of partial derivatives) → [[mathematics/06-calculus/04-calculus-3/01-partial-derivatives|partial derivatives]], and the idea of a shadow price → [[operations-research/05-duality-and-sensitivity|note 05]]. The vault's numerical-methods note covers the algorithms in more depth than this one → [[mathematics/07-applied-and-computational/01-numerical-methods/10-numerical-optimisation|numerical optimisation]].

After this lesson you will be able to:

1. Say whether a problem is convex, and why that decides whether a "best" answer can be trusted.
2. Solve an equality-constrained problem with Lagrange multipliers, and read the multiplier as a shadow price.
3. Check whether a point satisfies the KKT conditions for an inequality-constrained problem.
4. Set up a minimum-variance portfolio as a quadratic program.

**Study route:** sections 1–3. Stop after the fence example and redo it on paper. Then KKT (section 4), the portfolio and the code.

## The kid version
<!-- bite: d6fbad38-2575-425b-ae82-e0574ac00618 -->

Back in note 03, the field was a flat tilted plane, so the top was always at a corner. Now imagine a field with a real hill in it — a smooth round mound. The highest point might be in the middle of the field, nowhere near a fence. And if the field had *several* hills, standing on top of one wouldn't tell you whether a taller one is somewhere else. **Nonlinear optimisation is finding the top when the ground curves — and the most important question is whether there's only one hill.**

**Where the analogy stops working.** You can see a whole field. An algorithm can only feel the slope where it's standing, like walking in fog. On a single smooth hill, always walking uphill works. On ground with many hills, it gets you to *a* top, with no way of knowing it's *the* top.

## 1. Why this exists
<!-- bite: dd5c5098-f047-483b-8d9d-22d395880db0 -->

Linearity fails in ways that matter:

1. **Diminishing returns.** Advertising spend: the first ₦1 million reaches new people; the tenth mostly reaches the same people again.
2. **Risk.** An investment portfolio's risk is the *variance* of its return, which involves products of holdings — quadratic, not linear.
3. **Physics and engineering.** Drag rises with the square of speed; a beam's strength depends on the cube of its depth.
4. **Prices that respond.** If you set the price and demand falls as price rises, revenue = price × quantity is a product of two things you influence.

## Terms used in nonlinear optimisation
<!-- bite: cd511df6-842b-414c-a574-b2fdfdde7ffa -->

1. **Gradient**: This is the vector of partial derivatives of a function, written $\nabla f$. It points in the direction the function increases fastest, and its length is how fast.
2. **Stationary point**: This is a point where the gradient is zero — the ground is flat. It can be a minimum, a maximum, or a saddle.
3. **Local optimum**: This is a point that's better than every point *near* it, but not necessarily better than every point everywhere.
4. **Global optimum**: This is a point that's better than every feasible point anywhere.
5. **Convex function**: A function is convex when the straight line between any two points on its graph lies on or above the graph — it curves upwards, like a bowl. $x^2$ is convex; $\sin x$ isn't.
6. **Convex problem**: A minimisation problem is convex when its objective is convex and its feasible region is a convex set. (For maximisation, the objective must be *concave*: bowl upside-down.)
7. **Lagrange multiplier**: This is a number attached to each constraint, written $\lambda$, which measures how much the optimal objective changes per unit change in the constraint. It's the nonlinear shadow price.
8. **Lagrangian**: This is the objective with each constraint added in, multiplied by its multiplier: $L = f + \sum \lambda_i g_i$.
9. **KKT conditions**: KKT stands for **Karush–Kuhn–Tucker**, after the three people who found them. These are the conditions any optimum of an inequality-constrained problem must satisfy (under mild assumptions), generalising "gradient equals zero".
10. **Quadratic program**: This is also known as a **QP**. This is a problem with a quadratic objective and linear constraints. Portfolio optimisation is the classic example.

## 2. Convexity is the dividing line
<!-- bite: fa430dfa-e142-47a2-8d8d-a0a5548cf88c -->

**For a convex problem, every local optimum is a global optimum.**

That one sentence is why convexity matters more than linearity. Why it's true, in words: suppose a point $x$ is a local minimum but some other point $y$ is better. Walk along the straight line from $x$ to $y$. Because the region is convex, the line stays feasible. Because the function is convex, it lies below the line joining $f(x)$ and $f(y)$, so it's below $f(x)$ even right next to $x$. That contradicts $x$ being a local minimum.

So:

1. **Convex problems** (LPs, least squares, minimum-variance portfolios, many engineering designs) can be solved reliably, at scale, with a guarantee.
2. **Non-convex problems** (most neural network training, many design problems, anything with integer variables) can only be solved locally, unless you're willing to pay for a global search.

**How to check convexity in practice:**

1. A sum of convex functions is convex. A positive multiple of a convex function is convex.
2. Linear functions are both convex and concave.
3. $x^2$, $e^x$, $|x|$ and $\max(x, y)$ are convex.
4. A twice-differentiable function of one variable is convex when its second derivative is never negative. For several variables, the matrix of second derivatives (the Hessian) must be positive semi-definite.
5. Constraints $g(x) \le 0$ with convex $g$, and linear equality constraints, give a convex region. A nonlinear *equality* constraint generally doesn't.

## 3. Equality constraints: Lagrange multipliers
<!-- bite: f75f8aaf-e21d-4fb7-94aa-ed45528cb5b9 -->

**The problem:** a farmer has 40 metres of fence and wants the largest rectangular pen. Width $x$, length $y$:

$$\max\; xy \quad\text{s.t.}\quad 2x + 2y = 40$$

**The idea in words.** At the optimum, you can't move along the constraint and improve the objective. That means the objective's gradient must point straight *across* the constraint, not along it. So the objective's gradient and the constraint's gradient must be parallel: one is a multiple of the other.

**The method states that at an optimum of $f$ subject to $g = c$, there is a number $\lambda$ with $\nabla f = \lambda \nabla g$.**

Apply it. $\nabla(xy) = (y, x)$ and $\nabla(2x + 2y) = (2, 2)$, so:

1. $y = 2\lambda$.
2. $x = 2\lambda$.
3. $2x + 2y = 40$.

From 1 and 2, $x = y$. From 3, $4x = 40$, so $x = y = 10$, and $\lambda = 5$. **The best pen is a 10 × 10 square with area 100 m².**

**Now read $\lambda$.** One more metre of fence should add about $\lambda = 5$ square metres. Check: with fence $P$, the best pen is a square of side $P/4$, area $P^2/16$. Its derivative is $P/8$, which at $P = 40$ is 5. ✓

**The Lagrange multiplier is the shadow price of the constraint**, exactly as in note 05. LP duality is the linear special case of this.

## 4. Inequality constraints: the KKT conditions
<!-- bite: c819529a-03c6-44bd-8a36-2f0e0cf7288b -->

Real constraints are usually inequalities: budgets, capacities, limits. Then a constraint might be binding at the optimum, or might not matter at all.

**The example:**

$$\min\; (x - 3)^2 + (y - 2)^2 \quad\text{s.t.}\quad x + y \le 4$$

The objective is the squared distance from the point $(3, 2)$. Without the constraint, the answer is $(3, 2)$ itself. But $3 + 2 = 5 > 4$, so that's infeasible. The best you can do is the closest point on the line $x + y = 4$.

**The KKT conditions, for minimising $f$ subject to $g(x) \le 0$, state that at an optimum there is a multiplier $\mu \ge 0$ such that:**

1. **Stationarity:** $\nabla f + \mu \nabla g = 0$. The objective's downhill direction is blocked exactly by the constraint.
2. **Primal feasibility:** $g(x) \le 0$.
3. **Dual feasibility:** $\mu \ge 0$. The constraint can only push, not pull.
4. **Complementary slackness:** $\mu \, g(x) = 0$. Either the constraint is binding, or its multiplier is zero — note 05's rule again.

**Apply them.** Write the constraint as $g = x + y - 4 \le 0$. Guess it's binding.

1. Stationarity: $2(x - 3) + \mu = 0$ and $2(y - 2) + \mu = 0$. So $x - 3 = y - 2$, i.e. $y = x - 1$.
2. Binding: $x + (x - 1) = 4$, so $x = 2.5$, $y = 1.5$.
3. Then $\mu = -2(2.5 - 3) = 1$. That's $\ge 0$. ✓

**Optimum: $(2.5, 1.5)$, objective $0.25 + 0.25 = 0.5$, multiplier $\mu = 1$.**

If the guess had produced $\mu < 0$, it would mean the constraint was "pulling" the solution, which inequality constraints can't do — so the guess was wrong, and you'd try the constraint as non-binding instead.

**For convex problems, the KKT conditions are sufficient as well as necessary**: a point that satisfies them is the global optimum. For non-convex problems, they only identify candidates.

## 5. A quadratic program: the minimum-variance portfolio
<!-- bite: 1c5fe1e6-a85a-4ac8-a026-93b150f0cc41 -->

Harry Markowitz's 1952 insight, which won a Nobel prize: an investor should care about risk as well as return, and **combining risky assets can produce something less risky than any of them**.

Two assets. Asset 1 has standard deviation (risk) 20% a year; asset 2 has 30%. Their returns are uncorrelated. Put a fraction $w$ in asset 1 and $1 - w$ in asset 2. The portfolio's variance is:

$$\sigma_p^2 = w^2 (0.2)^2 + (1 - w)^2 (0.3)^2 = 0.04\,w^2 + 0.09\,(1 - w)^2$$

This is a convex quadratic in $w$. Set its derivative to zero: $0.08w - 0.18(1 - w) = 0$, so $w = 0.18 / 0.26 \approx 0.692$.

**Put 69% in asset 1 and 31% in asset 2.** Variance: $0.04(0.479) + 0.09(0.095) \approx 0.0277$, so risk $\approx 16.6\%$ — **lower than either asset alone.** That's diversification, made exact.

With $n$ assets, a target return and a no-short-selling rule, it becomes:

$$\min\; w^\top \Sigma\, w \quad\text{s.t.}\quad \mu^\top w \ge r_{\text{target}},\quad \textstyle\sum_i w_i = 1,\quad w \ge 0$$

where $\Sigma$ is the covariance matrix and $\mu$ the expected returns. It's a convex QP, and solvers handle thousands of assets. The weakness is the input: expected returns are notoriously hard to estimate, and the optimiser magnifies the errors.

## 6. How solvers work, briefly
<!-- bite: e6a55daa-4216-4f29-a1d4-b5e83f415b76 -->

1. **Unconstrained:** **gradient descent** steps downhill, $x \leftarrow x - \alpha \nabla f$. **Newton's method** uses second derivatives to jump towards the bottom of a local quadratic approximation, converging much faster near the optimum. Quasi-Newton methods (BFGS) approximate the second derivatives cheaply. → [[mathematics/07-applied-and-computational/01-numerical-methods/10-numerical-optimisation|numerical optimisation]]
2. **Constrained:** **sequential quadratic programming** (SQP) repeatedly solves a QP approximation of the problem. **Interior-point methods** (the same family as note 04's) handle large convex problems.
3. **Non-convex, global:** multistart (run a local method from many starting points), or spatial branch and bound, which works like note 07 but branches on continuous variables.

## Worked example — KKT with SciPy
<!-- bite: f1770f2b-50dc-490d-9ebd-b646b14a05c1 -->

**Runnable.** SciPy 1.0+.

```python
# kkt.py — note 09: minimise (x-3)^2 + (y-2)^2 subject to x + y <= 4
from scipy.optimize import minimize

f = lambda v: (v[0] - 3) ** 2 + (v[1] - 2) ** 2
cons = [{"type": "ineq", "fun": lambda v: 4 - v[0] - v[1]}]   # scipy wants g(v) >= 0
res = minimize(f, x0=[0, 0], constraints=cons, method="SLSQP")
print("x, y =", res.x.round(4), " objective =", round(res.fun, 4))
```

```bash
uv run --with scipy python kkt.py
```

Expected output:

```text
x, y = [2.5 1.5]  objective = 0.5
```

**Notice the sign convention**: SciPy's `"ineq"` means `fun(v) >= 0`, the opposite of this note's $g \le 0$. Getting it backwards silently solves a different problem — always check the answer is feasible.

## Common pitfalls and traps
<!-- bite: 025bb0c3-7669-43bc-87a6-0396459f30a6 -->

1. **Trusting a local optimum on a non-convex problem.** Run from several starting points. If they disagree, you've learned something important.
2. **Nonlinear equality constraints.** They make the region non-convex in general, even if everything else is convex.
3. **Bad scaling.** Variables in millions alongside variables in thousandths make gradient methods crawl. Rescale so all variables are roughly of order 1.
4. **Treating a Lagrange multiplier as valid far from the optimum.** Like a shadow price, it's a local rate.
5. **Non-smooth objectives.** $|x|$ and $\max$ have kinks where the gradient doesn't exist, which confuses gradient-based solvers. Use note 02's tricks to make them linear constraints instead.

## Check your understanding
<!-- bite: 454bcadb-d894-4d2e-985c-0866ca218619 -->

Attempt these without the note, then compare your reasoning with the answers.

1. <!-- q: open id="ae02552b" -->
   Is $f(x, y) = x^2 + y^2 - xy$ convex? (Hint: try $x = y$ and $x = -y$.)

   <details><summary>Answer</summary>

   Yes. Along $x = y = t$ it is $t^2$; along $x = -y = t$ it is $3t^2$. Both bowl upward. In general its Hessian $\begin{pmatrix} 2 & -1 \\ -1 & 2 \end{pmatrix}$ has eigenvalues 1 and 3, both positive, so it's convex.

   </details>

2. <!-- q: exact id="6cf9cf0d" answer="120" -->
   A farmer with 40 m of fence encloses the largest rectangle: a 10 × 10 square of 100 m², with Lagrange multiplier $\lambda = 5$ m² per metre of fence. Using $\lambda$, estimate the best area if the farmer gets 44 m of fence.

   <details><summary>Answer</summary>

   120 m²: 100 + 5 × 4. The exact answer is an 11 × 11 square, 121 m². The multiplier is a local rate, so it slightly underestimates a 4-metre change.

   </details>

3. <!-- q: mcq id="b87a406b" -->
   A problem minimises a convex function whose unconstrained minimum is at $(3, 2)$. A constraint $x + y \le 6$ is added. What is the KKT multiplier $\mu$ for that constraint at the optimum?

   - [x] 0, because $(3, 2)$ already satisfies the constraint, so it is slack
   - [ ] Positive, because every constraint has a positive multiplier
   - [ ] Negative
   - [ ] It can't be found without solving numerically

   <details><summary>Answer</summary>

   0. $3 + 2 = 5 \le 6$, so the unconstrained optimum is feasible, the constraint is slack, and complementary slackness makes $\mu = 0$.

   </details>

4. <!-- q: open id="15121a11" -->
   Why can a portfolio of two risky assets have less risk than either asset alone? Would that still be true if the two were perfectly correlated?

   <details><summary>Answer</summary>

   When one asset has a bad year, the other often doesn't, so losses partly cancel. With perfect positive correlation they rise and fall together, and the portfolio's risk is just the weighted average of the two (for risks of 20% and 30%, $0.2w + 0.3(1-w)$), never below the smaller one. The benefit of diversifying comes entirely from imperfect correlation.

   </details>

## Practice — independent task
<!-- bite: 8add43b7-2ef3-4ffd-93ab-d0b2a95dfd39 -->

1. **Predict, then solve:** the farmer's pen is against a wall, so only three sides need fencing: $\max\; xy$ s.t. $x + 2y = 40$. Solve it with a Lagrange multiplier by hand, then check with `minimize` (maximise by minimising $-xy$).
2. **Apply — a three-asset portfolio.** Expected returns 8%, 12%, 15%; risks 15%, 20%, 30%; correlations $\rho_{12} = 0.3$, $\rho_{13} = 0.1$, $\rho_{23} = 0.4$. Build the covariance matrix ($\Sigma_{ij} = \rho_{ij}\sigma_i\sigma_j$), and use `minimize` to find the minimum-variance portfolio with no short selling, then the minimum-variance portfolio with expected return at least 12%.
3. **Explain:** for part 2, which constraints are binding at each answer, and what does that say about the trade-off between risk and return?

**Done when:** part 1 matches by hand and by code; part 2 gives weights summing to 1, all non-negative, meeting the return target, and you can name the binding constraints.

<details>
<summary>Answer to part 1 — after your attempt</summary>

$\nabla(xy) = (y, x) = \lambda(1, 2)$, so $y = \lambda$, $x = 2\lambda$. Then $2\lambda + 2\lambda = 40$, $\lambda = 10$: $x = 20$, $y = 10$, area 200 m². The wall doubles the area — and each extra metre of fence is now worth 10 m².

</details>

## Before moving on
<!-- bite: e688bdd3-090f-4464-9664-b4ca533ba923 -->

You're ready when you can say whether a problem is convex and why it matters, solve a two-variable Lagrange problem and interpret $\lambda$, and check the four KKT conditions at a given point.

**Recap:**

1. Convexity, not linearity, is what makes optimisation reliable: in a convex problem every local optimum is global.
2. Lagrange: at an equality-constrained optimum, the gradients are parallel, and the multiplier is the shadow price.
3. KKT: stationarity, feasibility, $\mu \ge 0$, complementary slackness. Sufficient for convex problems.
4. Portfolios are convex QPs; diversification falls out of the maths.

**Next:** [[operations-research/10-heuristics-and-metaheuristics|Heuristics and Metaheuristics]] — what to do when no method can promise the optimum in reasonable time.

## Related
<!-- bite: e27ad8b1-7b5b-4b9a-b54b-a382bc7dc0af -->

- [[mathematics/07-applied-and-computational/01-numerical-methods/10-numerical-optimisation|Numerical optimisation]] — the algorithms in depth
- [[operations-research/05-duality-and-sensitivity|Duality and Sensitivity]] — the linear version of multipliers
- [[control-theory/11-optimal-control-and-lqr|Optimal control and LQR]] — quadratic optimisation over time
- [[machine-learning/index|AI and machine learning]] — training a model is (usually non-convex) nonlinear optimisation
- [[operations-research/index|Operations research map]]

## About this lesson
<!-- bite: e44ce28a-e3d3-4e5f-9e19-97c6adf309ff -->

**Level:** Intermediate → Advanced. **Covers:** When the objective or constraints curve: diminishing returns, risk, physics. Corners stop being special, convexity becomes the thing that matters, and Lagrange multipliers and the KKT conditions take over from shadow prices and the simplex method.
