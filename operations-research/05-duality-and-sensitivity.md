---
id: 1ab4dd10-d5af-4b35-9040-9456902d4eff
---

# Duality and Sensitivity

**Source:** `[reference]` — see [[operations-research/index|the domain note]].

## Before you start
<!-- bite: 8430f22d-a53f-4a23-80af-6c27a90fc2d8 -->

You need to be able to run the simplex method and read the shadow prices off the final tableau → [[operations-research/04-the-simplex-method|note 04]], and solve an LP with `linprog` → [[operations-research/02-formulating-linear-programs|note 02]].

After this lesson you will be able to:

1. Write the dual of any LP, and explain what its variables mean in the original problem's terms.
2. State weak duality, strong duality and complementary slackness, and use them to check whether a solution is optimal.
3. Compute the range over which a shadow price stays valid, and the range over which an objective coefficient can move without changing the plan.
4. Explain a sensitivity report to someone who has never heard of linear programming.

**Study route:** sections 1–3 (the dual), then stop and write the dual of the paint problem from note 02. Then sections 4–6 (sensitivity).

## The kid version
<!-- bite: f879e865-ea24-4137-948a-1ac3fc3885b8 -->

You own a lemonade stand with 10 lemons and 5 cups of sugar, and you've worked out the best way to use them. A neighbour knocks: "I'll buy all your lemons and sugar. What price would make you happy to sell instead of making lemonade?" You'd want at least as much as the lemonade would earn you. The neighbour wants to pay as little as possible. **The lowest fair price for your ingredients turns out to be exactly what your best lemonade plan earns.** Working out that price is a second problem — the "twin" — and it tells you what each lemon is really worth to you.

**Where the analogy stops working.** There is no real neighbour. The dual is a mathematical fact about every LP, not a market. Its prices are what a resource is worth to *this* plan, at the margin, and only over a limited range — a hundred more lemons wouldn't each be worth the same as one more.

## 1. Why this exists
<!-- bite: 96c54d2d-86f7-4deb-9541-117867657c9a -->

The workshop's optimal plan is 30 tables and 40 chairs. The owner's next questions aren't about tables:

1. "Should I pay a carpenter ₦2,000 an hour for overtime?"
2. "Finishing hours could rise by 30 if I buy a spray booth. Worth it?"
3. "Table profit is really between ₦6,000 and ₦8,000 — does that change the plan?"

Re-solving for every question works for a two-variable toy. For a real model with ten thousand constraints, you want the answers *read off* the solution you already have. Duality is what makes that possible, and it's why LP is so widely used in planning: **the solver returns not just a decision but a price for every constraint.**

## Terms used in duality
<!-- bite: 81bfdaa4-4475-4150-b83d-5f027e487af1 -->

1. **Primal**: This is the original LP — the one you wrote to make a decision.
2. **Dual**: This is the twin LP built from the primal's numbers. It has one variable per primal constraint and one constraint per primal variable.
3. **Shadow price**: This is also known as the **dual value** or **marginal value** of a constraint. This is how much the optimal objective would improve if the constraint's right-hand side increased by one unit, with everything else unchanged.
4. **Reduced cost**: This is how much a variable's objective coefficient would have to improve before it's worth using that variable in the optimal plan. Variables already in the plan have reduced cost zero.
5. **Complementary slackness**: This is the rule that, at an optimum, a constraint with slack has a shadow price of zero, and a constraint with a positive shadow price has no slack.
6. **Ranging**: This is also known as **sensitivity analysis** or **post-optimality analysis**. This is finding the interval over which a number in the model can change without changing the structure of the optimal solution.
7. **Duality gap**: This is the difference between the primal and dual objective values for a given pair of feasible solutions. At the optimum it's zero.

## 2. The dual from a story
<!-- bite: 47ecebe6-300b-46ac-b084-8dbc408c94c8 -->

Back to the workshop:

$$\max\; 7x_1 + 5x_2 \quad\text{s.t.}\quad 4x_1 + 3x_2 \le 240,\quad 2x_1 + x_2 \le 100,\quad x \ge 0$$

A rival wants to rent all of the workshop's hours. They'll pay $y_1$ per carpentry hour and $y_2$ per finishing hour. What prices would the owner accept?

1. **A table's worth of hours must fetch at least a table's profit.** A table uses 4 carpentry and 2 finishing hours, so renting them out earns $4y_1 + 2y_2$. If that's less than ₦7,000, the owner would rather make a table. So: $4y_1 + 2y_2 \ge 7$.
2. **The same for chairs:** $3y_1 + y_2 \ge 5$.
3. **Prices can't be negative:** $y_1, y_2 \ge 0$.
4. **The rival wants to pay as little as possible** for all the hours: minimise $240y_1 + 100y_2$.

That's the dual:

$$\min\; 240y_1 + 100y_2 \quad\text{s.t.}\quad 4y_1 + 2y_2 \ge 7,\quad 3y_1 + y_2 \ge 5,\quad y \ge 0$$

**Solve it.** Guess that both constraints bind: $4y_1 + 2y_2 = 7$ and $3y_1 + y_2 = 5$. From the second, $y_2 = 5 - 3y_1$; substitute: $4y_1 + 10 - 6y_1 = 7$, so $y_1 = 1.5$ and $y_2 = 0.5$. Dual objective: $240(1.5) + 100(0.5) = 410$.

**Pause and look.** $y_1 = 1.5$ and $y_2 = 0.5$ are the shadow prices from the simplex tableau in note 04. And the dual's minimum, 410, equals the primal's maximum.

### The recipe

The story generalises into a mechanical recipe. For a primal in this "canonical" form:

| Primal (max) | Dual (min) |
|---|---|
| $\max\; c^\top x$ | $\min\; b^\top y$ |
| $Ax \le b$ | $A^\top y \ge c$ |
| $x \ge 0$ | $y \ge 0$ |
| one constraint per row of $A$ | one variable $y_i$ per primal constraint |
| one variable per column of $A$ | one constraint per primal variable |

In words: **the primal's right-hand sides become the dual's objective, the primal's objective becomes the dual's right-hand sides, and the matrix is transposed.** The dual of the dual is the primal again.

Two further rules handle the other cases: a primal **equality** constraint gives a dual variable that is **free** (any sign), and a primal $\ge$ constraint in a max problem gives a dual variable $\le 0$. When in doubt, convert to canonical form first.

## 3. The duality theorems
<!-- bite: d6677d55-8b58-4acb-81a7-a6e65bb95b3f -->

**Weak duality states that for a maximisation primal, the objective of any feasible primal solution is at most the objective of any feasible dual solution.**

$$c^\top x \;\le\; b^\top y \quad\text{for every feasible } x \text{ and feasible } y$$

Why: $c^\top x \le (A^\top y)^\top x = y^\top (Ax) \le y^\top b$. The first step uses $A^\top y \ge c$ and $x \ge 0$; the second uses $Ax \le b$ and $y \ge 0$. In story terms: the rent the rival pays for everything can never be less than what any production plan earns, because every unit of production is "covered" by its rent.

**Consequences, all useful:**

1. Any feasible dual solution gives an **upper bound** on the primal optimum, for free. Integer programming solvers use exactly this to prune their search (note 07).
2. If the primal is unbounded, the dual is infeasible (nothing can bound infinity), and vice versa.

**Strong duality states that if the primal has an optimal solution, so does the dual, and their objective values are equal.**

$$\max c^\top x = \min b^\top y$$

So a primal–dual pair with equal objectives is a **certificate of optimality**: anyone can check it with arithmetic, without trusting the solver. In the workshop: plan (30, 40) earns 410, prices (1.5, 0.5) charge 410, both are feasible, so both are optimal.

**Complementary slackness states that at an optimum, for every constraint, either the slack is zero or the shadow price is zero (or both).**

$$y_i \cdot (b_i - a_i^\top x) = 0 \quad\text{for every constraint } i$$

In words: **a resource you don't use up is worth nothing at the margin.** If the workshop had 20 idle finishing hours, one more wouldn't help, so its price would be 0. The same rule applies the other way: a product with a strictly positive reduced cost (its resources are worth more than its profit) isn't made.

This gives a way to *verify* a claimed optimum without re-solving: check primal feasibility, compute the duals that complementary slackness forces, check those duals are feasible.

## 4. Shadow prices and how far they hold
<!-- bite: 02326d44-f89b-4d45-bbee-fce8ea673af7 -->

The shadow price of carpentry is ₦1,500 per hour. So the overtime question has an answer: **paying ₦2,000 per hour for carpentry overtime loses money** (₦500 per hour), and paying ₦1,200 would gain ₦300 per hour.

But "per hour" for how many hours? A shadow price is a *rate*, and it holds only while the same constraints stay binding — the same basis, in note 04's terms. To find the range, read the final tableau's slack columns. With $\Delta_1$ extra carpentry hours:

$$x_1 = 30 - 0.5\,\Delta_1, \qquad x_2 = 40 + \Delta_1$$

(The coefficients are the $s_1$ column of the final tableau, from note 04.) The plan stays feasible while both are non-negative: $\Delta_1 \le 60$ and $\Delta_1 \ge -40$. So:

**Carpentry's shadow price of 1.5 holds for 200 to 300 carpentry hours.** Beyond 300, so many chairs are made that tables hit zero, the corner changes, and the price drops.

Doing the same with finishing ($s_2$ column: $x_1 = 30 + 1.5\Delta_2$, $x_2 = 40 - 2\Delta_2$):

**Finishing's shadow price of 0.5 holds for 80 to 120 finishing hours.**

Now the spray booth question. Adding 30 finishing hours takes you to 130, outside the range. The first 20 hours are worth ₦500 each (₦10,000 total). What the last 10 are worth needs a re-solve. **A shadow price applied outside its range gives a confident wrong answer.**

## 5. Objective coefficient ranging
<!-- bite: f04aa43d-f027-4a03-8228-7c323ed10fa4 -->

"Table profit is really ₦6,000–₦8,000. Does the plan change?"

From note 03's geometry, corner C stays optimal while the profit line's slope stays between the two binding constraints' slopes: between $-4/3$ (carpentry) and $-2$ (finishing). With chair profit fixed at 5, the profit line's slope is $-c_1/5$:

$$\frac{4}{3} \le \frac{c_1}{5} \le 2 \quad\Longrightarrow\quad 6.67 \le c_1 \le 10$$

**The plan stays at 30 tables and 40 chairs for any table profit from about ₦6,670 to ₦10,000.** The profit *amount* changes ($30 \times c_1 + 200$), but the decision doesn't. So the owner's uncertainty range of ₦6,000–₦8,000 *does* matter at the bottom end: below ₦6,670, the optimum jumps to all chairs.

That's the kind of sentence a sensitivity report exists to produce: "the plan is robust to the profit estimate unless it falls below ₦6,670."

**Changing several numbers at once.** The ranges above assume one change at a time. The **100% rule** extends it: if you change several right-hand sides, add up each change as a fraction of its allowed range in that direction. If the total is at most 100%, the shadow prices still hold. Above 100%, they might not — re-solve.

## Worked example — checking duality with a solver
<!-- bite: 524cc05f-f122-4957-b7ef-2acd4d28f80c -->

**Runnable.** SciPy 1.9+ with the HiGHS solver.

```python
# duality.py — solve the workshop primal and dual, and test a shadow price by re-solving
from scipy.optimize import linprog

def primal(carpentry=240, finishing=100, table_profit=7):
    r = linprog([-table_profit, -5], A_ub=[[4, 3], [2, 1]], b_ub=[carpentry, finishing],
                method="highs")
    return r.x, -r.fun

# dual: min 240y1 + 100y2  s.t.  4y1 + 2y2 >= 7,  3y1 + y2 >= 5  (written as <= by negating)
d = linprog([240, 100], A_ub=[[-4, -2], [-3, -1]], b_ub=[-7, -5], method="highs")
x, z = primal()
print("primal plan", x, "profit", z)
print("dual prices", d.x, "rent", d.fun)

for hours in (241, 300, 301, 320):
    print(f"carpentry {hours}: profit {primal(carpentry=hours)[1]:.2f}")
for p in (6.5, 6.7, 9.9, 10.5):
    print(f"table profit {p}: plan {primal(table_profit=p)[0]}")
```

```bash
uv run --with scipy python duality.py
```

Expected output:

```
primal plan [30. 40.] profit 410.0
dual prices [1.5 0.5] rent 410.0
carpentry 241: profit 411.50
carpentry 300: profit 500.00
carpentry 301: profit 500.00
carpentry 320: profit 500.00
table profit 6.5: plan [ 0. 80.]
table profit 6.7: plan [30. 40.]
table profit 9.9: plan [30. 40.]
table profit 10.5: plan [50.  0.]
```

Read it against the theory:

1. Primal 410 = dual 410: strong duality.
2. One extra carpentry hour adds exactly 1.5. From 240 to 300 hours, profit rises by $60 \times 1.5 = 90$. **Past 300 it stops rising at all**: at 300 hours the plan is 0 tables and 100 chairs, finishing is the only limit, and more carpentry is useless. The shadow price fell from 1.5 to 0 at the edge of its range.
3. The plan flips below about 6.67 and above 10, as computed.

## Common pitfalls and traps
<!-- bite: fb8c5604-c8fb-4310-b0ff-2baec9f604b5 -->

1. **Using a shadow price outside its range.** The commonest misuse. Always quote the range with the price.
2. **Sign conventions.** Solvers differ on the sign they report for duals, especially when they minimise internally. SciPy's `marginals` are for its minimisation form, which is why note 02 negates them. Check a shadow price against a one-unit re-solve the first time you use a new solver.
3. **Shadow prices at degenerate optima.** When the optimum is degenerate (note 04), the shadow price can differ for an increase and a decrease. A solver reports one of them.
4. **Confusing reduced cost and shadow price.** Shadow prices belong to *constraints* (what a resource is worth). Reduced costs belong to *variables* (how far a product is from being worth making).
5. **Reading the dual as a real market price.** It's the value *to this plan*, not what the hour costs or what anyone would pay.

## Check your understanding
<!-- bite: b297fc4e-3e73-4fe7-85dc-09c6e12807bc -->

1. Write the dual of the paint problem from note 02: $\max\; 5x_E + 4x_I$ s.t. $6x_E + 4x_I \le 24$, $x_E + 2x_I \le 6$, $-x_E + x_I \le 1$, $x_I \le 2$.
2. In that problem the demand constraints have slack at the optimum. Without solving the dual, what are their shadow prices?
3. A manager says: "The shadow price of warehouse space is ₦300 per square metre, so 1,000 more square metres is worth ₦300,000." What should you ask before agreeing?
4. Someone hands you a production plan and a set of prices, both feasible, with profit 970 and rent 1,000. What can you conclude?

<details>
<summary>After your attempt — answers</summary>

1. $\min\; 24y_1 + 6y_2 + y_3 + 2y_4$ s.t. $6y_1 + y_2 - y_3 \ge 5$ (for $x_E$), $4y_1 + 2y_2 + y_3 + y_4 \ge 4$ (for $x_I$), $y \ge 0$.
2. Zero, by complementary slackness: a constraint with slack has a zero shadow price. (Solving the remaining two equations gives $y_1 = 0.75$, $y_2 = 0.5$; the dual objective is $18 + 3 = 21$, matching the primal.)
3. "Over what range does that price hold?" One thousand square metres is very likely outside it — once space stops being the bottleneck, its value drops to zero.
4. By weak duality, the true optimum lies between 970 and 1,000. The plan is within 3% of optimal, and you know that without solving anything. That's the duality gap, and it's exactly how integer programming solvers report progress.

</details>

## Practice — independent task
<!-- bite: bf00d7ee-62e8-49de-aa77-9f11de3eb821 -->

Using `duality.py` as a starting point:

1. **Predict, then check:** compute by hand the range of chair profit $c_2$ over which (30, 40) stays optimal (table profit fixed at 7). Then confirm by re-solving at values just inside and just outside your range.
2. **Apply:** extend the script so it prints, for each constraint, its shadow price, its slack, and its valid range found by re-solving (step the right-hand side up and down until the profit-per-hour rate changes). Run it on the workshop and on the paint problem.
3. **Explain:** write a three-sentence sensitivity report for the workshop owner in plain English, with no symbols.

**Done when:** your computed ranges match the hand calculations in sections 4 and 5, and your plain-English report would make sense to someone who's never seen an LP.

<details>
<summary>Hint — after your attempt</summary>

For part 1: slope condition $4/3 \le 7/c_2 \le 2$, so $3.5 \le c_2 \le 5.25$.

</details>

## Before moving on
<!-- bite: 0842c685-957b-48d9-8817-f932dae1e5bc -->

You're ready when you can write the dual of a three-constraint LP from memory, explain in one sentence why the primal and dual optima are equal, and say what a shadow price means *and* why its range matters.

**Recap:**

1. Every LP has a dual: one price per constraint, one constraint per variable, the matrix transposed.
2. Weak duality: any dual solution bounds the primal. Strong duality: at the optimum they're equal — a checkable certificate.
3. Complementary slackness: unused resources are worth zero; profitable-to-produce means priced exactly at profit.
4. Shadow prices answer "is more of this worth it?" — but only within their range.
5. Objective ranging answers "would the plan change if this estimate is wrong?"

**Next:** [[operations-research/06-network-models|Network Models]] — LPs with a special structure that solve fast and return whole numbers for free.

## Related
<!-- bite: 985b376a-062d-4b4d-a651-250713c15564 -->

- [[operations-research/04-the-simplex-method|The Simplex Method]] — where the shadow prices first appeared
- [[operations-research/07-integer-programming|Integer Programming]] — where weak duality's bounds do the pruning
- [[operations-research/09-nonlinear-optimisation|Nonlinear Optimisation]] — Lagrange multipliers are shadow prices for nonlinear models
- [[operations-research/11-decision-analysis-and-game-theory|Decision Analysis and Game Theory]] — zero-sum games are solved by an LP and its dual
- [[operations-research/index|Operations research map]]

## About this lesson
<!-- bite: a2883e9f-f366-4e8e-9316-944decb96a33 -->

**Level:** Intermediate → Advanced. **Covers:** Every LP has a twin that prices its resources. This note builds the twin from a story, proves that the two always agree, and uses it to answer the question managers actually ask: *how much would the answer change if the numbers were wrong?*
