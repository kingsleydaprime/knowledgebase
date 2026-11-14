# Formulating Linear Programs

**[Beginner → Intermediate]** — How to turn a messy description into a linear program a solver can use, the four assumptions that make it "linear", and the standard patterns most real models are built from.

**Source:** `[reference]` — see [[operations-research/index|the domain note]].

## Before you start

You should be able to pick out the variables, objective and constraints of a decision in words → [[operations-research/01-what-operations-research-is|note 01]].

After this lesson you will be able to:

1. Say what makes a model *linear*, and spot a formulation that quietly isn't.
2. Write product-mix, blending, transportation and staff-covering models from a paragraph of English.
3. Use the two standard tricks for objectives that don't look linear (absolute values and "minimise the worst case").
4. Solve a small linear program with a real solver and read its output.

**Study route:** sections 1–3, then stop and try the first two check questions. Then patterns (section 4), the worked example, and the practice task.

## The kid version

A recipe says "two eggs for every cake." Making three cakes means six eggs, and making cakes and biscuits means adding up the eggs each one needs. Nothing gets cheaper in bulk, nothing gets weird when you mix. **A linear program is a decision where every cost and every limit works like that recipe: double the amount, double the effect, and totals are just sums.**

**Where the analogy stops working.** Real kitchens aren't linear — the oven is preheated once whether you bake one cake or three, and you can't bake half a cake. Linear programs pretend you can, and knowing when that pretence is safe is most of this lesson.

## 1. Why this exists

Linear programs (LPs) are the workhorse of operations research. Refinery blending, airline fuel planning, diet design, supply-chain flows and portfolio rebalancing all run on them. The reason isn't that the world is linear. It's that **LPs with millions of variables solve reliably in seconds**, and the theory tells you exactly how the answer would change if your data were wrong (note 05). Nonlinear and integer models lose some or all of those guarantees.

So the practical skill is: model as linearly as the problem allows, and know precisely where you have bent the truth to do it.

## Terms used in linear programming

1. **Linear expression**: This is a sum of variables, each multiplied by a constant, such as $7x_1 + 5x_2$. No variable is multiplied by another, squared, divided into, or placed inside a function.
2. **Linear program**: This is also known as an **LP** or a **linear optimisation problem**. This is a model whose objective is a linear expression and whose constraints each say a linear expression is $\le$, $\ge$ or $=$ a constant.
3. **Coefficient**: This is the constant multiplying a variable — the 4 in "4 hours of carpentry per table".
4. **Right-hand side**: This is the constant on the right of a constraint, usually a capacity or a requirement — the 240 in $4x_1 + 3x_2 \le 240$.
5. **Index set**: This is a named list the model ranges over, like the set of products $P$ or factories $F$. It lets one line of maths stand for many constraints.
6. **Infeasible**: A model is infeasible when no choice of variables satisfies every constraint at once. Usually it means the data or a constraint is wrong.
7. **Unbounded**: A model is unbounded when the objective can be made as good as you like — infinite profit. It almost always means a constraint is missing.

## 2. The four assumptions hiding in "linear"

A linear program commits you to four things. **Every time a formulation goes wrong, one of these is the reason.**

1. **Proportionality.** Each variable's contribution scales exactly with its value. Ten tables earn ten times one table, and use ten times the hours. *Breaks when:* there are bulk discounts, setup costs, or diminishing returns.
2. **Additivity.** The total is the sum of the parts. A table plus a chair uses exactly the table's hours plus the chair's hours. *Breaks when:* products interact — making both on the same day saves a machine changeover, or two advertising channels reinforce each other.
3. **Divisibility.** Variables can take fractional values. 30.6 tables is a legal answer. *Breaks when:* you're deciding counts of indivisible things (aircraft, staff) or yes/no choices (open this warehouse?). That is integer programming → [[operations-research/07-integer-programming|note 07]].
4. **Certainty.** Every parameter is known exactly. *Breaks:* always, a little. Sensitivity analysis measures how much it matters → [[operations-research/05-duality-and-sensitivity|note 05]].

**Divisibility is often safe to bend.** If the LP says make 3,041.6 litres of paint, rounding to 3,041 costs almost nothing. If it says buy 1.6 aircraft, rounding is a strategic decision and the LP was the wrong tool.

## 3. A method for formulating

Do these in order, in writing, every time. Skipping step 1 is the most common source of nonsense.

1. **Write the decision variables in words, with units.** "$x_p$ = number of units of product $p$ made this week." If you cannot write the sentence, you don't yet know what's being decided.
2. **Write the objective in words, then in symbols.** "Total profit, in ₦ thousands, = sum over products of (profit per unit × units made)."
3. **List every limit in words first.** One bullet per resource, requirement or rule — including the boring ones.
4. **Translate each bullet into an inequality, and check its units.** Both sides of $4x_1 + 3x_2 \le 240$ are in *hours*. If the two sides have different units, the constraint is wrong.
5. **State the domain.** Non-negative? Integer? Free to go negative?
6. **Sanity-check with a made-up solution.** Plug in an obvious plan ("make nothing", "make 10 of each") and see whether the model agrees about what's allowed.

## 4. The standard patterns

Most real models are combinations of five shapes. Learn the shapes and you can read most formulations at a glance.

### Pattern 1 — Product mix (allocating scarce resources)

*"Choose how much of each product to make, given limited resources, to maximise profit."* The workshop from note 01 is this pattern. With products $p \in P$, resources $r \in R$, profit $c_p$, usage $a_{rp}$ and availability $b_r$:

$$\max \sum_{p} c_p x_p \quad\text{s.t.}\quad \sum_{p} a_{rp} x_p \le b_r \;\;\forall r, \qquad x_p \ge 0$$

Read the constraint as: "for every resource, the total used across all products is at most what you have."

### Pattern 2 — Blending (the diet problem)

*"Mix ingredients to meet requirements at least cost."* The direction flips: the objective is cost to minimise, and the constraints are mostly $\ge$ (requirements to meet) rather than $\le$ (capacities not to exceed).

Example: animal feed from maize (₦300/kg, 10% protein, 4% fibre) and soybean meal (₦800/kg, 45% protein, 6% fibre). Each tonne of feed needs at least 20% protein and at most 5% fibre. Let $m$ and $s$ be kilograms per tonne:

$$\begin{aligned}
\min\quad & 300m + 800s\\
\text{s.t.}\quad & m + s = 1000 && \text{it's a tonne}\\
& 0.10m + 0.45s \ge 0.20 \times 1000 && \text{protein}\\
& 0.04m + 0.06s \le 0.05 \times 1000 && \text{fibre}\\
& m, s \ge 0
\end{aligned}$$

**Notice the percentages.** "At least 20% protein" must be written as protein *kilograms* ≥ 20% of total *kilograms*. Writing $0.10m + 0.45s \ge 0.20$ is a units mistake that makes the constraint almost free.

### Pattern 3 — Transportation (flows from supply to demand)

*"Ship from factories to customers at least cost."* Factories $i$ have supply $s_i$, customers $j$ have demand $d_j$, and shipping one unit from $i$ to $j$ costs $c_{ij}$. Let $x_{ij}$ be the units shipped:

$$\min \sum_{i}\sum_{j} c_{ij} x_{ij} \quad\text{s.t.}\quad \sum_j x_{ij} \le s_i \;\;\forall i, \qquad \sum_i x_{ij} \ge d_j \;\;\forall j, \qquad x_{ij} \ge 0$$

**A double-indexed variable is the tell for a network problem.** These have special structure, and that structure makes integer answers come out for free → [[operations-research/06-network-models|note 06]].

### Pattern 4 — Covering (staff scheduling)

*"Hire enough people to cover every period."* A shop needs at least $r_t$ staff in each four-hour block $t$. Each person works two consecutive blocks. Let $x_t$ be the number starting at block $t$. Block $t$ is covered by those who started at $t$ and those who started at $t-1$:

$$\min \sum_t x_t \quad\text{s.t.}\quad x_{t-1} + x_t \ge r_t \;\;\forall t, \qquad x_t \ge 0$$

The insight: **the variable is "who starts when", not "who is on duty"**. Choosing the right variable makes the constraints simple. Choosing "how many on duty in block $t$" makes it hard to say that shifts are consecutive.

### Pattern 5 — Multi-period (inventory balance)

*"Plan production over several weeks, holding stock between them."* The new idea is a **balance constraint** linking periods:

$$\text{stock}_{t} = \text{stock}_{t-1} + \text{made}_t - \text{sold}_t$$

Read it as conservation: what you end with is what you started with, plus what came in, minus what went out. Every multi-period model has one of these per item per period, and an off-by-one in its index is a classic bug.

## 5. Two tricks for objectives that don't look linear

Some objectives aren't linear, but can be made linear with an extra variable. Both tricks work because the solver is trying to push a variable in one direction, and the constraints stop it going too far.

### Minimising an absolute value

You want production $x$ close to a target of 100, so you minimise $|x - 100|$. That isn't linear. Introduce a new variable $t$ and say $t$ must be at least the distance in both directions:

$$\min\; t \quad\text{s.t.}\quad t \ge x - 100,\quad t \ge 100 - x$$

**Why it works:** minimising pushes $t$ down, but both constraints hold it at or above $|x - 100|$. At the optimum it sits exactly on the larger one, which is the absolute value.

### Minimising the worst case (minimax)

Three warehouses have workloads $w_1, w_2, w_3$, and you want to minimise the *busiest*. Introduce $z$ for "the maximum":

$$\min\; z \quad\text{s.t.}\quad z \ge w_1,\; z \ge w_2,\; z \ge w_3$$

Same logic: $z$ is pushed down onto the largest $w$. **The trick only works in one direction.** You can *minimise* a maximum or *maximise* a minimum this way. Maximising a maximum is not convex and needs integer variables (note 07).

## Worked example — solving the workshop with a real solver

**Runnable.** You need Python 3.10+ and `uv` (or `pip install scipy`). SciPy ships the open-source HiGHS solver, which is a serious, production-grade LP and MILP solver.

```python
# product_mix.py — the workshop LP from notes 02-05
from scipy.optimize import linprog

# linprog minimises, so negate the profits to maximise 7x + 5y
c = [-7, -5]
A_ub = [[4, 3],   # carpentry hours: 4 per table, 3 per chair
        [2, 1]]   # finishing hours: 2 per table, 1 per chair
b_ub = [240, 100]

res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None), (0, None)], method="highs")
print("status:", res.message)
print("tables, chairs:", res.x)
print("profit:", -res.fun)
# HiGHS reports the duals of the <= rows; negate them back because we negated c
print("shadow prices (carpentry, finishing):", -res.ineqlin.marginals)
print("slack hours:", res.slack)
```

From any folder, save the file and run:

```bash
uv run --with scipy python product_mix.py
```

Expected output:

```
status: Optimization terminated successfully. (HiGHS Status 7: Optimal)
tables, chairs: [30. 40.]
profit: 410.0
shadow prices (carpentry, finishing): [1.5 0.5]
slack hours: [0. 0.]
```

What the output tells you:

1. **30 tables and 40 chairs, ₦410,000 profit.** Not all tables, even though tables earn more each. [[operations-research/03-the-geometry-of-linear-programs|Note 03]] shows why in a picture.
2. **Both slacks are zero.** Every carpentry and finishing hour is used. Both resources are *binding*.
3. **Shadow prices 1.5 and 0.5.** One more carpentry hour would add ₦1,500 profit; one more finishing hour, ₦500. That's what an hour is *worth* to this workshop — the subject of [[operations-research/05-duality-and-sensitivity|note 05]].

**Boundary cases to try:** change the finishing hours to 0 and the answer is "make nothing", with profit 0. Delete the `bounds` argument and the default bounds are already $\ge 0$, so nothing changes — but set `bounds=[(None, None)] * 2` and see what happens.

## Common pitfalls and traps

1. **Units that don't match.** Percentages against kilograms, hours against minutes, per-week against per-day. Check every constraint's units on both sides.
2. **Multiplying two variables.** "Revenue = price × quantity" when you're choosing both price and quantity is not linear. Fix one, or move to note 09.
3. **Equality where you meant inequality.** "Meet demand" written as $=$ forbids overproduction that might have been cheaper. Write $\ge$ unless the rule really is exact.
4. **Hiding a fixed cost.** "Running the night shift costs ₦50,000 if we use it at all" breaks proportionality. That's an integer model (note 07).
5. **Unbounded means a missing constraint.** An LP that reports infinite profit has found a loophole in your rules, not in reality.
6. **Infeasible means contradictory rules — or bad data.** A demand of 1,000 with a capacity of 900 and "meet all demand" as a hard constraint is infeasible. Often the fix is to allow unmet demand at a penalty cost instead.

## Check your understanding

1. Which of the four assumptions does each of these break? (a) The first 100 kg of steel cost ₦900/kg, the rest ₦800/kg. (b) You're deciding how many lorries to buy. (c) Running two products on one machine saves a cleaning step.
2. In the feed example, why is the constraint "protein ≥ 0.20" wrong but "protein ≥ 0.20 × 1000" right?
3. In the staff-covering model, why is "number starting at $t$" a better variable than "number on duty at $t$"?
4. What does it mean if a solver says your model is unbounded?

<details>
<summary>After your attempt — answers</summary>

1. (a) Proportionality — the cost per kilogram changes with the amount (it's piecewise linear; because cost *falls*, it needs integer variables to model properly). (b) Divisibility — lorries come in whole numbers. (c) Additivity — the cost of the two products together is less than the sum of each.
2. The left side is in kilograms of protein per tonne of feed. The bare 0.20 is a fraction with no units. The requirement is 20% *of the 1000 kg*, which is 200 kg of protein.
3. With "on duty" variables you would need extra constraints to say that the people on duty in block 3 include those from block 2 who are still mid-shift. "Starting at" variables make each block's cover a simple sum of two variables, with consecutiveness built in.
4. The objective can be improved forever without breaking any constraint. In practice a constraint is missing — usually a capacity, a demand ceiling, or non-negativity.

</details>

## Practice — independent task

**The paint problem.** A factory makes interior and exterior paint. Exterior uses 6 tonnes of material A and 1 tonne of material B per tonne of paint; interior uses 4 of A and 2 of B. There are 24 tonnes of A and 6 of B available each day. Exterior earns ₦5,000 per tonne and interior ₦4,000. Market research says interior demand can't exceed exterior demand by more than 1 tonne, and interior demand is at most 2 tonnes a day.

1. Formulate it on paper, following the six-step method, with units on every line.
2. Solve it with `linprog`.
3. Say which constraints are binding.

**Done when:** your solver's answer satisfies every constraint when you substitute it in by hand, and you can name which constraints have zero slack. The answer is in the hint below — check only *after* you've solved it.

<details>
<summary>Hint and answer — after your attempt</summary>

Variables: $x_E$, $x_I$ in tonnes per day. Constraints: $6x_E + 4x_I \le 24$; $x_E + 2x_I \le 6$; $x_I - x_E \le 1$; $x_I \le 2$; both $\ge 0$. Optimum: $x_E = 3$, $x_I = 1.5$, profit ₦21,000 per day. The two material constraints are binding; the two demand constraints have slack.

</details>

## Before moving on

You're ready for note 03 when you can write a blending or transportation model from a paragraph of English, with units on every line, without looking at this note.

**Recap:**

1. Linear means proportional, additive, divisible and certain. Every formulation bug is one of these bent too far.
2. Write variables in words with units before writing any maths.
3. Five patterns cover most models: product mix, blending, transportation, covering, multi-period balance.
4. Absolute values and minimax objectives become linear with one extra variable.

**Next:** [[operations-research/03-the-geometry-of-linear-programs|The Geometry of Linear Programs]] — why the answer is always at a corner, which is the idea the simplex method is built on.

## Related

- [[operations-research/01-what-operations-research-is|What Operations Research Is]] — the shape of a model
- [[operations-research/03-the-geometry-of-linear-programs|The Geometry of Linear Programs]] — the next note
- [[operations-research/07-integer-programming|Integer Programming]] — when divisibility breaks
- [[operations-research/index|Operations research map]]
