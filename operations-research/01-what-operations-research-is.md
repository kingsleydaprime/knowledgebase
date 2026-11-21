---
id: 2fb46eb7-b68f-4dc5-8b50-1d959296f048
---

# What Operations Research Is

**Source:** `[reference]` — read and assembled from textbooks (Hillier & Lieberman, Winston, Taha) and solver documentation, not from running operations research on a real organisation. See [[operations-research/index|the domain note]].

## Before you start
<!-- bite: dabbe693-b5da-48c1-9fbe-a2f7803828b0 -->

You need school algebra: you can solve two simultaneous equations and draw a straight line from its equation. Nothing else yet.

After this lesson you will be able to:

1. Say what makes a problem an operations research problem, and what doesn't.
2. Take a decision described in words and name its decision variables, objective and constraints.
3. Place a problem on the map (deterministic or uncertain, optimise or evaluate) and so know which later note handles it.

## The kid version
<!-- bite: f70cf4ac-2d10-40f6-a978-590840d230b4 -->

You have ₦2,000 to spend at a school fair. Sweets cost ₦200 and make you a bit happy; a ride costs ₦500 and makes you very happy; you can only stay two hours, and each ride takes half an hour of queueing. You could just guess, but you could also write the rules down — money left, time left, how happy each thing makes you — and work out the best mix. **Operations research is writing those rules down properly and letting maths find the best choice.**

**Where the analogy stops working.** At a fair you can try every combination in your head. Real problems have thousands of choices that interact, so the point of the field is methods that find the best answer *without* trying every combination — and models whose answers you can trust enough to act on.

## 1. Why this exists
<!-- bite: a0070ee9-474a-491c-a6cd-7432e74f04ee -->

A delivery company has 40 vans, 900 parcels and drivers who can only work nine hours. Which van takes which parcels, in what order?

The simple approach is a sensible rule: "each van takes the nearest undelivered parcel next." It works, roughly. But the number of possible routes is astronomically large — for a single van with 20 stops there are about $10^{18}$ orders — and simple rules regularly leave 10–20% on the table. At the scale of a national courier that is fuel, overtime and vans worth billions.

**Operations research (OR) is the discipline of building a mathematical model of a decision and using it to find the best — or a provably good — choice.** It sits between mathematics, computer science and management: the maths supplies the methods, the computer runs them, and the organisation supplies the problem and has to live with the answer.

## Terms used in operations research
<!-- bite: 18a60072-864d-475b-ac99-a83eec642ee4 -->

1. **Decision variable**: This is a quantity you control and are trying to choose. "How many tables to make this week" is a decision variable, usually written $x$.
2. **Objective function**: This is also known as the **objective**. This is the single number the decision is judged by, written as a formula in the decision variables — profit to maximise, or cost, time or distance to minimise.
3. **Constraint**: This is a rule the decision must obey, written as an equation or inequality. "Carpentry can't exceed 240 hours" is a constraint.
4. **Feasible solution**: This is any choice of the decision variables that obeys every constraint. It may be a bad choice, but it is allowed.
5. **Feasible region**: This is also known as the **feasible set**. This is the set of all feasible solutions.
6. **Optimal solution**: This is a feasible solution with the best possible objective value. There may be more than one.
7. **Model**: This is the whole package — the variables, objective and constraints — written down precisely enough that a computer could solve it. A model is a deliberate simplification of reality.
8. **Parameter**: This is a number in the model that you don't control but have to know — a price, a machine's capacity, an average demand. Parameters are usually estimated, which is why every model is only as good as its data.
9. **Solver**: This is software that takes a model and returns an optimal (or good) solution. HiGHS, Gurobi, CPLEX and Google's OR-Tools are solvers.
10. **Heuristic**: This is a method that finds a good solution quickly but gives no guarantee it is the best. "Always go to the nearest stop next" is a heuristic.

## 2. The shape every model shares
<!-- bite: 109010a2-2903-4243-b141-f48fda1ccdda -->

Every optimisation model in this track has the same three parts, and learning to see them in a paragraph of English is the most important skill in the field.

**A model is a choice of what to decide, how to score it, and what you're not allowed to do.**

$$\begin{aligned}
\text{maximise or minimise} \quad & f(x) && \text{the objective}\\
\text{subject to} \quad & g_i(x) \le b_i && \text{the constraints}\\
& x \in X && \text{what kind of values } x \text{ may take}
\end{aligned}$$

### A worked translation

A small workshop makes tables and chairs. A table needs 4 hours of carpentry and 2 hours of finishing, and earns ₦7,000 profit. A chair needs 3 hours of carpentry and 1 hour of finishing, and earns ₦5,000. This week there are 240 carpentry hours and 100 finishing hours. What should they make?

Read it in three passes:

1. **What is being decided?** How many tables, $x_1$, and how many chairs, $x_2$.
2. **How is a decision scored?** Profit, in thousands of naira: $7x_1 + 5x_2$. Maximise it.
3. **What is forbidden?** Using more carpentry than exists: $4x_1 + 3x_2 \le 240$. Using more finishing than exists: $2x_1 + x_2 \le 100$. Making a negative number of anything: $x_1, x_2 \ge 0$.

$$\begin{aligned}
\max \quad & 7x_1 + 5x_2\\
\text{s.t.} \quad & 4x_1 + 3x_2 \le 240\\
& 2x_1 + x_2 \le 100\\
& x_1, x_2 \ge 0
\end{aligned}$$

**Pause and predict:** before reading on, guess the best plan. Is it all tables (they earn more each), all chairs, or a mix?

This workshop is the running example for notes 02–05. The answer — 30 tables and 40 chairs, ₦410,000 — comes in [[operations-research/03-the-geometry-of-linear-programs|note 03]], and *why* "all tables" loses is the first real insight of the track.

## 3. The process, not just the maths
<!-- bite: 896975ee-e62c-45ce-914c-ae7a613826fc -->

Textbooks spend 90% of their pages on solving. Practitioners spend most of their time elsewhere. The classic operations research process has six steps:

```
 1. Define the problem      ← most failures start here
        ↓
 2. Gather data             ← usually the longest step
        ↓
 3. Build the model
        ↓
 4. Solve it                ← the part the textbooks teach
        ↓
 5. Validate it             ← does the answer make sense to the people who do the work?
        ↓
 6. Implement and monitor   ← a model nobody uses is worth nothing
        ↑______________________________↓   (repeat: reality changes)
```

Two warnings come from this:

1. **The right answer to the wrong problem is worthless.** If the workshop's real bottleneck is wood supply, not labour hours, the model above is precisely wrong. Step 1 is talking to the people who run the thing.
2. **Validation means showing the answer to someone who knows the work.** If the foreman says "we can't make 30 tables, the clamps only hold 20," you have found a missing constraint — that's the model improving, not failing.

## 4. A map of the field
<!-- bite: 85ec531d-935c-461f-b198-fd7b95bdda2e -->

Operations research problems split along two questions:

1. **Is everything known (deterministic), or is something random (stochastic)?**
2. **Do you want the best choice (optimise), or to understand how a system behaves (evaluate)?**

| | **Optimise: find the best decision** | **Evaluate: predict how it behaves** |
|---|---|---|
| **Deterministic** | Linear programming (02–05), networks (06), integer programming (07), dynamic programming (08), nonlinear optimisation (09), heuristics (10) | Project scheduling (06) |
| **Stochastic** | Decision analysis (11), stochastic inventory (13), stochastic dynamic programming (08) | Queueing theory (12), simulation (14) |

The table is a map, not a wall. Inventory theory uses optimisation on a stochastic model; simulation is often wrapped inside an optimiser. But when a new problem lands, these two questions tell you where to start looking.

## 5. Where it came from
<!-- bite: 5af55061-ea72-484e-80c1-9fe89d64e64b -->

The name comes from the Second World War. British scientists were asked to study military *operations* — how to place radar stations, how big convoys should be, how to set depth charges — and called the work operational research. (British English still says "operational research"; American English says "operations research".)

Two moments matter for this track:

1. **1947 — George Dantzig invents the simplex method** for planning US Air Force logistics. Linear programming becomes solvable at scale, and the field takes off with the computer → [[operations-research/04-the-simplex-method|note 04]].
2. **1990s onward — solvers get vastly faster.** Algorithm improvements and hardware together made integer programs that were hopeless in 1990 solvable in seconds. That is why the modern job is mostly *modelling*: the solving is bought off the shelf.

## 6. Where you have already met it
<!-- bite: 722d4de2-97e1-40cc-ae6f-e6abd2738223 -->

1. **Shortest paths.** Dijkstra's algorithm is an operations research method; Google Maps runs a descendant of it → [[operations-research/06-network-models|note 06]].
2. **Dynamic programming.** Richard Bellman invented it in the 1950s for multi-stage decision problems, and the DSA pattern is the same idea → [[dsa/04-patterns/15-dynamic-programming|DSA: dynamic programming]].
3. **Server capacity.** "Why does latency explode when the CPU hits 90%?" is a queueing theory question with an exact answer → [[operations-research/12-queueing-theory|note 12]].
4. **Scheduling.** Kubernetes placing pods on nodes is bin packing, a classic integer programming problem → [[operations-research/07-integer-programming|note 07]].

## Common pitfalls and traps
<!-- bite: 92da13c7-40c0-489e-8577-e098ff5e2048 -->

1. **Optimising a proxy.** Minimising delivery *distance* when the real cost is driver *hours* (which includes waiting and loading) gives routes that look short and run late. Check that the objective is what the organisation actually pays for.
2. **Forgetting the obvious constraint.** Non-negativity, integer quantities, "a driver can't be in two places at once." Solvers exploit every missing rule ruthlessly — they will happily make −20 chairs if you let them.
3. **Treating estimates as facts.** Demand of "100 a week" is a guess with a spread. If the decision changes a lot when the guess moves a little, you need the sensitivity analysis in [[operations-research/05-duality-and-sensitivity|note 05]] before acting.
4. **Mistaking "optimal" for "good."** The answer is optimal *for the model*. A beautifully solved model of the wrong problem is the field's most common failure.

## Check your understanding
<!-- bite: 7463784a-fcc9-46da-9e7c-316f4fa225d0 -->

1. A hospital wants to roster nurses so every shift is covered and nobody works more than five shifts a week, at least cost. Name the decision variables, objective and constraints.
2. Why is "how many customers will be waiting at 5pm?" not an optimisation problem? Where on the map does it go?
3. In the workshop model, what would happen if you deleted the line $x_1, x_2 \ge 0$?

<details>
<summary>After your attempt — answers</summary>

1. Decision variables: for each nurse and each shift, whether that nurse works it (a yes/no, so a 0/1 variable). Objective: minimise total wage cost. Constraints: each shift has at least the required number of nurses; each nurse works at most five shifts. Note the 0/1 variables — this is an integer program (note 07).
2. Nothing is being chosen; you are predicting how a random system behaves. It's stochastic and evaluative: queueing theory (12) or simulation (14). It *becomes* an optimisation problem when you ask "how many cashiers should we schedule?"
3. In this particular model the answer doesn't change, because the optimum already has both quantities positive. But that's luck. If chairs were barely profitable, a model without $x_2 \ge 0$ would choose *negative* chairs, because "−10 chairs" frees 30 carpentry hours for tables. Leave out non-negativity and the solver will use that loophole. Always say what values the variables are allowed to take.

</details>

## Practice — independent task
<!-- bite: 568a2208-d0ae-45f3-b9f9-9f1dec8e092e -->

Pick a decision from your own week — revision time across courses, a food budget, how to spend a Saturday — and write it as a model on paper.

**Done when:** you have (a) at least two decision variables with units, (b) one objective with units, (c) at least three constraints including the "obvious" ones, and (d) one sentence naming something real you deliberately left out of the model and why.

## Before moving on
<!-- bite: c108dcdd-08d9-4cc7-839c-d995b4eb74d9 -->

You can move on when you can take a paragraph of English and write its variables, objective and constraints without looking at the workshop example.

**Recap:**

1. A model is variables, objective and constraints. Finding those three in words is the core skill.
2. The process is define → data → model → solve → validate → implement. Solving is the part you can buy.
3. Two questions place a problem: known or random? optimise or evaluate?

**Next:** [[operations-research/02-formulating-linear-programs|Formulating Linear Programs]] — the most common kind of model, and the habits that make formulations correct.

## Related
<!-- bite: 654b7500-2291-4d11-ba21-b2769c29e7dd -->

- [[operations-research/index|Operations research map]]
- [[operations-research/02-formulating-linear-programs|Formulating Linear Programs]] — the next note
- [[control-theory/index|Control Theory]] — another discipline of decisions made by mathematics, where the decision is continuous and repeated in time
- [[systems-engineering/index|Systems Engineering]] — trade studies are operations research's informal cousin

## About this lesson
<!-- bite: 622c3a60-c891-4689-88ae-9d4978bfa1e1 -->

**Level:** Beginner. **Covers:** The discipline of making decisions with mathematics: what it is, where it came from, the shape every model shares, and the map of the rest of this track.
