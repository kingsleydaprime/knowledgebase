---
id: 59d64b38-338f-4668-8eb0-29d3424102f8
---

# Integer Programming

**[Intermediate → Advanced]** — Models where some decisions must be whole numbers or yes/no. They let you express fixed costs, logic and choices that LPs can't — at the price of being, in general, very hard to solve. This note covers modelling with binary variables, branch and bound, and why a good formulation matters more than a fast computer.

**Source:** `[reference]` — see [[operations-research/index|the domain note]]. The numbers in the worked example were checked by hand; the SciPy script itself has not been run yet — see "Still to run" in [[operations-research/index|the index]].

## Before you start
<!-- bite: bcb0e78d-9c04-43f5-a9fd-5d04c36ccd89 -->

You need to be able to formulate and solve an LP → [[operations-research/02-formulating-linear-programs|note 02]], read its geometry → [[operations-research/03-the-geometry-of-linear-programs|note 03]], and know that any feasible dual gives a bound → [[operations-research/05-duality-and-sensitivity|note 05, weak duality]].

After this lesson you will be able to:

1. Model fixed costs, either-or constraints, and logical rules ("if we open A, we must also open B") with binary variables.
2. Run branch and bound by hand on a two-variable integer program, pruning with bounds.
3. Explain why rounding an LP answer can be infeasible or far from optimal.
4. Read a solver's progress log: incumbent, bound and gap.

**Study route:** sections 1–3 (modelling) are the most useful part; stop and do check question 1. Then branch and bound (section 4) with a pencil, and the rest.

## The kid version
<!-- bite: 00457176-82d2-4e02-b6cb-9c49919f032d -->

You're packing a school bag. Each book is either in or out — you can't take half a maths book. Some rules link choices: "if you take the football boots, you need the boot bag too." **Integer programming is optimisation where some answers have to be whole numbers or yes/no, and that lets you write rules like these.** The catch is that "in or out" for 50 books means more combinations than there are grains of sand on Earth, so the clever part is ruling out huge groups of them without checking each one.

**Where the analogy stops working.** You'd pack a bag by feel and do fine. Solvers can't feel; what they do instead is solve an easier version where half-books *are* allowed, use that to know how good things could possibly get, and throw away any branch of choices that can't beat the best bag found so far.

## 1. Why this exists
<!-- bite: 1e6f2cd1-0407-46e1-86f9-6ad03d8bfaab -->

Note 02's divisibility assumption says 30.6 tables is fine. Plenty of decisions don't work that way:

1. **Counts of big things.** Buy 2 or 3 aircraft — not 2.4.
2. **Yes/no choices.** Open this warehouse? Run the night shift? Accept this order?
3. **Fixed costs.** A machine costs ₦500,000 to set up whether it makes one item or a thousand. That breaks proportionality.
4. **Logic.** "At most two of these three projects." "If route A is used, route B can't be."

Integer programming handles all four. It's the language most real scheduling, routing, rostering and network-design models are written in.

## Terms used in integer programming
<!-- bite: d099525e-e93b-4479-8fa9-d8b399b48234 -->

1. **Integer program**: This is also known as an **IP**. This is an LP with the extra rule that some or all variables must take whole-number values.
2. **Mixed-integer linear program**: This is also known as a **MILP** or **MIP**. This is an integer program where only some variables must be integers and the rest may be fractional. Most real models are MILPs.
3. **Binary variable**: This is an integer variable restricted to 0 or 1. It represents a yes/no decision.
4. **LP relaxation**: This is the LP you get by dropping the integer requirements. Its optimal value is a bound on the integer program's: at least as good, never worse.
5. **Incumbent**: This is the best integer-feasible solution found so far during the search.
6. **Bound**: This is also known as the **best bound** or **dual bound**. This is a value the optimum is proven not to exceed (for a maximisation). It comes from LP relaxations.
7. **Optimality gap**: This is the relative difference between the incumbent and the bound. A gap of 0% means the incumbent is proven optimal; a gap of 2% means it's within 2% of optimal.
8. **Big-M constraint**: This is a constraint containing a large constant $M$ that switches the constraint on or off depending on a binary variable.
9. **Formulation strength**: One formulation is stronger than another when its LP relaxation is closer to the true integer feasible set. Stronger formulations give tighter bounds and solve faster.

## 2. Why not just round?
<!-- bite: 301e5c1f-d464-482f-9f3e-77260c72e8d8 -->

Take this integer program:

$$\max\; 5x + 4y \quad\text{s.t.}\quad 6x + 4y \le 24,\quad x + 2y \le 6,\quad x, y \ge 0 \text{ and integer}$$

The LP relaxation's optimum is $(3, 1.5)$ with value 21.

1. **Round to nearest:** $(3, 2)$. Check: $6(3) + 4(2) = 26 > 24$. **Infeasible.**
2. **Round down:** $(3, 1)$. Feasible, value 19.
3. **The true integer optimum:** $(4, 0)$, value **20**.

Rounding down lost 1 out of 20, and the true optimum, $(4, 0)$, isn't next to the LP answer at all. In bigger models it's worse: with yes/no variables, an LP answer of "open 0.5 of each warehouse" tells you almost nothing about which warehouses to open.

**The integer points form a scatter inside the LP region, and the best one can be anywhere.**

```
 y        ● feasible integer point    ○ (3, 2) breaks 6x + 4y ≤ 24
 3 ┤ ●
 2 ┤ ●   ●   ●   ○
 1 ┤ ●   ●   ●   ●          the LP optimum (3, 1.5) sits between rows 1 and 2,
 0 ┼─●───●───●───●───★──    above (3, 1); ★ (4, 0) is the integer optimum
   0   1   2   3   4   x
```

## 3. Modelling with binary variables
<!-- bite: 92676473-decf-4e8c-a7b5-1718926c7d48 -->

This is the real skill. Each pattern below is a standard building block.

### Fixed charge

Making product $x$ costs ₦3,000 per unit plus a one-off ₦50,000 to set up the line, and capacity is 200 units. Introduce binary $z$ = "is the line set up?":

$$\text{cost} = 3000x + 50000z, \qquad x \le 200z, \qquad z \in \{0, 1\}$$

**Why it works:** if $z = 0$, the constraint forces $x \le 0$, so nothing is made and no setup is paid. If $z = 1$, $x$ can go up to 200 and the setup is paid. The solver would never choose $z = 1$ with $x = 0$, because that costs money for nothing.

### Either-or (disjunctive) constraints

A job on a machine must be scheduled either entirely before another job or entirely after it. Or: "either $x \le 10$ or $y \le 10$." Use a binary $w$ and a large $M$:

$$x \le 10 + Mw, \qquad y \le 10 + M(1 - w)$$

If $w = 0$, the first constraint is active and the second is switched off (since $10 + M$ is huge). If $w = 1$, the reverse.

**$M$ must be as small as you can justify.** It needs to be large enough not to cut off real solutions — the largest value $x$ could ever sensibly take — but every extra digit weakens the LP relaxation (section 6) and invites numerical trouble. $M = 10^9$ "to be safe" is a classic way to make a model slow and flaky.

### Logical rules

With binaries $a$, $b$, $c$ for three yes/no choices:

1. **At most two of them:** $a + b + c \le 2$.
2. **Exactly one:** $a + b + c = 1$.
3. **If $a$ then $b$:** $a \le b$. (If $a = 1$, $b$ must be 1. If $a = 0$, $b$ is free.)
4. **$a$ and $b$ can't both be chosen:** $a + b \le 1$.
5. **$c$ is 1 exactly when both $a$ and $b$ are:** $c \le a$, $c \le b$, $c \ge a + b - 1$. This linearises the product $c = ab$.

### The classic models built from these

1. **Knapsack:** choose items with values and weights to maximise value within a weight limit. One constraint, binary variables. The simplest integer program → [[dsa/04-patterns/15-dynamic-programming|DSA: dynamic programming]] solves small ones.
2. **Facility location:** which warehouses to open (binary, with a fixed cost each) and how to serve customers from the open ones (continuous flows, allowed only from open sites).
3. **Set covering:** choose the cheapest set of fire stations so every district is within 10 minutes of at least one.
4. **Bin packing:** pack items into the fewest bins. This is what Kubernetes does with pods on nodes, approximately.
5. **Travelling salesman:** visit every city once with the shortest tour. Integer programs solve instances with tens of thousands of cities to proven optimality, but it takes serious machinery → [[operations-research/10-heuristics-and-metaheuristics|note 10]] for the heuristic approach.

## 4. Branch and bound
<!-- bite: da3a9a86-c7b9-4a19-9ab4-196e52da7bcd -->

The standard algorithm, and the core of every MILP solver. It's a search tree that uses LP relaxations to avoid exploring most of the tree.

**The idea in words.** Solve the LP relaxation. If the answer is integer, done. If a variable is fractional, say $y = 1.5$, then every integer solution has either $y \le 1$ or $y \ge 2$. Split into those two subproblems (**branch**), and solve each one's LP. A subproblem's LP value is a **bound** on every integer solution inside it. If that bound is no better than the best integer solution already found, the whole branch can be thrown away (**pruned**).

### Trace on the example

Maximise $5x + 4y$ s.t. $6x + 4y \le 24$, $x + 2y \le 6$, integers.

```
                    Node 0: LP (3, 1.5)  z = 21
                   /                          \
             y ≤ 1                             y ≥ 2
                 /                               \
   Node 1: LP (3.33, 1)  z = 20.67        Node 2: LP (2, 2)  z = 18
         /              \                  integer, but 18 < 20 → prune
     x ≤ 3              x ≥ 4
       /                    \
 Node 3: (3, 1)          Node 4: (4, 0)
  integer, z = 19          integer, z = 20
  new incumbent 19         new incumbent 20 ★
```

Step by step:

1. **Node 0.** LP: $(3, 1.5)$, $z = 21$. So no integer solution can beat 21. $y$ is fractional — branch on it.
2. **Node 1 ($y \le 1$).** With $y = 1$, the first constraint $6x + 4 \le 24$ gives $x \le 3.33$. LP: $(3.33, 1)$, $z = 20.67$. $x$ is fractional — branch.
3. **Node 3 ($y \le 1$, $x \le 3$).** LP: $(3, 1)$, $z = 19$. Integer! **Incumbent = 19.**
4. **Node 4 ($y \le 1$, $x \ge 4$).** $6(4) + 4y \le 24$ forces $y = 0$. LP: $(4, 0)$, $z = 20$. Integer and better. **Incumbent = 20.**
5. **Node 2 ($y \ge 2$).** LP: $(2, 2)$, $z = 18$. Its bound, 18, is below the incumbent 20 — **prune**. Nothing in this branch can beat 20, so it's never explored further.

Every node is now closed. **Optimum: $(4, 0)$ with $z = 20$**, proven.

**Pause and think:** if the solver had explored node 2 *first*, it would have found incumbent 18 there. Would it then have been able to prune node 1? (No: node 1's bound, 20.67, is above 18. Search order changes the work done, not the answer.)

### What makes it fast or slow

1. **Tight bounds prune more.** If the LP relaxation's value is close to the integer optimum, most branches get pruned early. That's what formulation strength buys (section 6).
2. **Good incumbents prune more.** Finding a good integer solution early — often by a heuristic — lets the solver throw away more of the tree. Real solvers run heuristics constantly.
3. **Branching choices.** Which fractional variable to branch on, and which node to explore next, can change the work by orders of magnitude.

## 5. Cutting planes, and what solvers actually do
<!-- bite: 4224932b-9645-4afb-b524-d565160554c3 -->

A **cutting plane** is an extra linear constraint that every integer solution satisfies but the current fractional LP solution doesn't. Adding it "cuts off" the fractional corner without losing any integer points, tightening the relaxation.

In the example, every integer solution satisfies $x + y \le 4$: check $(4, 0)$, $(3, 1)$, $(2, 2)$ — all fine — but the LP point $(3, 1.5)$ has $x + y = 4.5$. Adding $x + y \le 4$ cuts it off. Ralph Gomory showed in 1958 how to generate such cuts automatically from the simplex tableau.

**Modern solvers combine everything: branch-and-cut.** Presolve shrinks the model, cuts tighten the relaxation at the root and in the tree, heuristics find incumbents, branch and bound closes the gap. A typical progress log:

```
  Nodes      Incumbent     Best bound     Gap
      0             —          21.00        —
     12         19.00          20.67     8.1%
     15         20.00          20.00     0.0%   optimal
```

**The gap is the honest number.** Stopping at "gap 1%" means "this plan is within 1% of the best possible," which is often exactly what a business needs — and can be thousands of times faster than proving 0%.

## 6. Formulation strength
<!-- bite: bc4b376b-b0a6-4a7d-9387-c4135ac9fa99 -->

Two formulations can have exactly the same integer solutions but very different LP relaxations — and the one with the tighter relaxation can solve dramatically faster.

**Example: facility location.** Warehouse $i$ is open ($y_i = 1$) or not; $x_{ij}$ is the fraction of customer $j$'s demand served from $i$. There are $n$ customers. Two ways to say "only serve from open warehouses":

1. **Aggregated (weak):** $\sum_j x_{ij} \le n\,y_i$ — one constraint per warehouse.
2. **Disaggregated (strong):** $x_{ij} \le y_i$ for every customer $j$ — $n$ constraints per warehouse.

Both allow exactly the same integer solutions. But in the LP relaxation, the weak version lets a warehouse serve one customer fully with $y_i = 1/n$ — "open a tiny fraction of a warehouse" — which makes the fixed costs look nearly free and the bound terrible. The strong version forces $y_i \ge x_{ij}$, so serving a customer fully means $y_i = 1$. **More constraints, faster solve.** This is counter-intuitive and very common.

The same lesson: **the smallest valid big-M is a stronger formulation than a large one.**

## 7. Why it's hard
<!-- bite: 76468452-c1f6-4ad8-ab84-e2ffbc8e8b1c -->

Integer programming is NP-hard in general → [[theory-of-computation/07-complexity-classes|complexity classes]]. No known algorithm solves every instance in polynomial time, and the knapsack, set-cover and travelling-salesman problems are all special cases.

In practice that's less bleak than it sounds:

1. Real instances often have structure solvers exploit, and many solve in seconds.
2. A proven gap of a few percent is usually enough.
3. Network problems (note 06) are integer programs that happen to be easy.

But some models of a few hundred binary variables will not solve in a lifetime. When that happens, reformulate (stronger), decompose (solve pieces separately), or switch to heuristics (note 10).

## Worked example — LP relaxation vs MILP in SciPy
<!-- bite: fc630ce4-bcfd-4239-b3eb-a6b9334a1266 -->

**Runnable.** SciPy 1.9+ (`milp` uses HiGHS's branch-and-cut).

```python
# branch_and_bound.py — note 07's integer program, LP relaxation vs MILP
import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds

c = np.array([5, 4])
A = np.array([[6, 4], [1, 2]])
b = np.array([24, 6])

lp = linprog(-c, A_ub=A, b_ub=b, method="highs")
print("LP relaxation:", lp.x, "value", -lp.fun)

ip = milp(-c, constraints=LinearConstraint(A, ub=b), integrality=[1, 1], bounds=Bounds(0, np.inf))
print("integer optimum:", ip.x, "value", -ip.fun)
print("rounded-down LP:", np.floor(lp.x), "value", c @ np.floor(lp.x))
```

```bash
uv run --with scipy python branch_and_bound.py
```

Expected output:

```
LP relaxation: [3.  1.5] value 21.0
integer optimum: [4. 0.] value 20.0
rounded-down LP: [3. 1.] value 19.0
```

`integrality=[1, 1]` marks both variables as integer; `0` would leave a variable continuous. That's all it takes to turn an LP into a MILP — the hard part is the modelling.

## Common pitfalls and traps
<!-- bite: 3814bd50-1804-47f3-abc3-503304a3358d -->

1. **Rounding LP answers.** Can be infeasible, can be far from optimal. Only safe when values are large and rounding barely changes them.
2. **Huge big-M values.** Weak relaxation, slow solve, and numerical errors where $10^{-9} \times 10^9$ isn't quite zero.
3. **Symmetry.** Ten identical lorries give $10!$ equivalent solutions, and branch and bound explores them all. Break it: "lorry 1 is used at least as much as lorry 2."
4. **Asking for 0% gap when 1% would do.** The last fraction of a percent can take most of the run time.
5. **Integer variables that don't need to be.** Declaring a quantity of 3,000 litres as integer adds work and changes nothing. Use integers only where fractional answers would be meaningless.

## Check your understanding
<!-- bite: f9aee600-d401-4c92-a548-b0a1f495998e -->

1. Write constraints for: a binary $o$ ("open the factory") and production $p$ between 100 and 500 if open, and exactly 0 if closed.
2. In the branch-and-bound trace, why can node 2 be pruned without branching further, even though it has an integer solution?
3. Why does a stronger formulation make branch and bound faster, if it has the same integer solutions?
4. After an hour on a cost-minimisation model, a solver reports incumbent ₦1.25 million and best bound ₦1.20 million. What can you tell your manager?

<details>
<summary>After your attempt — answers</summary>

1. $100\,o \le p \le 500\,o$. If $o = 0$, both sides are 0 so $p = 0$. If $o = 1$, $100 \le p \le 500$. (A minimum-production rule like this is called a *semi-continuous* variable.)
2. Its LP value, 18, bounds every integer solution in that branch, and 18 is already worse than the incumbent 20. (It also happens to be integer itself, which would close it on its own — but the bound alone is enough.)
3. Each node's LP value is closer to the best integer value in that branch, so more nodes have bounds that are worse than the incumbent and can be pruned early. Fewer nodes means less time.
4. "We have a plan costing ₦1.25 million, and we've proven no plan can cost less than ₦1.20 million — so this plan is within about 4% of the best possible." For minimisation the bound is a *lower* bound on cost. Whether to keep running depends on whether that last 4% is worth more than the waiting.

</details>

## Practice — independent task
<!-- bite: 3c723081-8591-4ad3-afc3-1089d22914d8 -->

**A small facility-location model.** Three possible depots with fixed opening costs ₦100k, ₦80k and ₦120k, each with capacity 50 units. Four customers each need 20 units. Delivery cost per unit (₦k) from depot $i$ to customer $j$:

```
          C1   C2   C3   C4
   D1      2    4    5    3
   D2      3    1    3    4
   D3      4    3    1    2
```

1. Formulate it with binary $y_i$ (open depot $i$) and continuous $x_{ij}$ (units from $i$ to $j$), using the **disaggregated** linking constraints $x_{ij} \le 20\,y_i$ plus capacity $\sum_j x_{ij} \le 50\,y_i$.
2. Solve it with `scipy.optimize.milp`.
3. Solve the LP relaxation (integrality off) with the **aggregated** form (capacity only) and with the **disaggregated** form. Compare the two LP bounds with the integer optimum.

**Done when:** you have the optimal depots, and you can show numerically that the disaggregated relaxation's bound is closer to the integer optimum.

## Before moving on
<!-- bite: f9a5b5ee-d774-4e18-945b-6a7db9942e7c -->

You're ready when you can model a fixed charge and an either-or rule from words, trace branch and bound on a two-variable problem with pruning, and explain what an optimality gap means.

**Recap:**

1. Integers express counts, yes/no choices, fixed costs and logic.
2. Rounding LP answers is unreliable — infeasible or suboptimal.
3. Branch and bound splits on fractional variables and prunes with LP bounds against an incumbent.
4. Solvers use branch-and-cut; the gap is the honest measure of progress.
5. Formulation strength — tight relaxations, small big-M — often matters more than solver speed.

**Next:** [[operations-research/08-dynamic-programming|Dynamic Programming]] — another way to beat combinatorial explosion, by splitting decisions into stages.

## Related
<!-- bite: 28e9caff-1eb9-4a89-ada4-edd079d1afa3 -->

- [[operations-research/05-duality-and-sensitivity|Duality and Sensitivity]] — where the bounds come from
- [[operations-research/06-network-models|Network Models]] — integer programs that are secretly easy
- [[operations-research/10-heuristics-and-metaheuristics|Heuristics and Metaheuristics]] — when proving optimality is out of reach
- [[theory-of-computation/07-complexity-classes|Complexity classes]] — why it's NP-hard
- [[operations-research/index|Operations research map]]
