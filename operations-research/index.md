# Operations Research

Making decisions with mathematics: building a model of a choice — what to make, where to send it, who works when, how much to stock, how many servers to run — and using it to find the best option, or a provably good one. The discipline behind airline schedules, delivery routes, refinery blending, call-centre staffing and, if you look at it right, your server's latency graph.

**~40,000 words across 14 notes.** Built November 2026. `[reference]` — read and assembled from the standard textbooks and solver documentation, not from doing operations research on a real organisation. The standard-library examples (notes 04, 08, 10, 12, 13, 14) were run and their output checked. The SciPy examples were checked by hand but not yet run — see *Still to run* below. Either way, that establishes the code behaves as described, not that the reader has learned the subject.

> **The one idea:** write the decision down as variables, an objective and constraints, and the structure of that model — linear or not, integer or not, certain or random — tells you which method can solve it and how far you can trust the answer. Most of the skill is in the writing down.

## Before you start

**You need:** school algebra (straight lines, simultaneous equations), basic probability (expected value, conditional probability), and enough Python to run a script. Calculus — derivatives and partial derivatives — for notes 09 and 13. Linear algebra helps from note 03 on → [[mathematics/04-linear-algebra/index|linear algebra]].

**Tooling:** Python 3.10+ and `uv` (or `pip install scipy`). SciPy ships HiGHS, a production-grade open-source LP and MILP solver, so nothing in this track needs a licence. Several notes run on the standard library alone.

## Reading order

**Notes 02–05 are linear programming** and build strictly in order. **06–10 are the other optimisation models.** **11–14 are uncertainty.** Each note opens with its prerequisites, so after 05 you can take 06–14 in any order that suits — but 12 before 14 is strongly recommended.

**Orientation**

1. [[operations-research/01-what-operations-research-is|What Operations Research Is]] — **[Beginner]** — variables, objective, constraints; the six-step process; a map of the field by "known or random?" and "optimise or evaluate?"

**Linear programming**

2. [[operations-research/02-formulating-linear-programs|Formulating Linear Programs]] — **[Beginner → Intermediate]** — the four assumptions hiding in "linear", five standard patterns, two tricks for awkward objectives, and a first solver run. **The note that matters most**: formulation is the job
3. [[operations-research/03-the-geometry-of-linear-programs|The Geometry of Linear Programs]] — **[Intermediate]** — why the optimum is at a corner, the four possible outcomes, and corners as basic solutions
4. [[operations-research/04-the-simplex-method|The Simplex Method]] — **[Intermediate]** — Dantzig's corner walk traced by hand, degeneracy, phase one, why it's fast in practice and exponential in theory, and a sixty-line implementation
5. [[operations-research/05-duality-and-sensitivity|Duality and Sensitivity]] — **[Intermediate → Advanced]** — the twin LP that prices every resource, strong duality as a certificate, and **how far a shadow price can be trusted**

**Beyond linear programming**

6. [[operations-research/06-network-models|Network Models]] — **[Intermediate]** — shortest path, max flow and min cut, assignment, transportation and the critical path, and why they give integer answers for free
7. [[operations-research/07-integer-programming|Integer Programming]] — **[Intermediate → Advanced]** — modelling with binary variables, why rounding fails, branch and bound traced, and **why a stronger formulation beats a faster computer**
8. [[operations-research/08-dynamic-programming|Dynamic Programming]] — **[Intermediate]** — Bellman's principle, backward recursion with tables, policies under uncertainty, and the curse of dimensionality
9. [[operations-research/09-nonlinear-optimisation|Nonlinear Optimisation]] — **[Intermediate → Advanced]** — convexity as the real dividing line, Lagrange multipliers as shadow prices, the KKT conditions, and the minimum-variance portfolio
10. [[operations-research/10-heuristics-and-metaheuristics|Heuristics and Metaheuristics]] — **[Intermediate]** — nearest neighbour and 2-opt, simulated annealing and tabu search, and **how to measure a heuristic honestly**

**Uncertainty**

11. [[operations-research/11-decision-analysis-and-game-theory|Decision Analysis and Game Theory]] — **[Intermediate]** — decision trees, what information is worth, risk attitude, and zero-sum games as an LP and its dual
12. [[operations-research/12-queueing-theory|Queueing Theory]] — **[Intermediate]** — Little's law, M/M/1 and M/M/c, **the utilisation cliff**, pooling, and why variability hurts
13. [[operations-research/13-inventory-models|Inventory Models]] — **[Intermediate]** — the economic order quantity and why it's forgiving, safety stock, and the newsvendor
14. [[operations-research/14-simulation|Simulation]] — **[Intermediate]** — Monte Carlo and discrete-event simulation, verified against theory, and the habits that make the answer trustworthy

**Then:** [[operations-research/projects|Projects]] — where it stops being reading.

## Still to run

SciPy couldn't be installed in the session that wrote this track, so these scripts have hand-checked numbers but have not been executed. Run each with `uv run --with scipy python <file>.py`, compare with the expected output in the note, and delete its line here:

- [ ] `product_mix.py` — [[operations-research/02-formulating-linear-programs|note 02]]
- [ ] `duality.py` — [[operations-research/05-duality-and-sensitivity|note 05]]
- [ ] `networks.py` — [[operations-research/06-network-models|note 06]]
- [ ] `branch_and_bound.py` — [[operations-research/07-integer-programming|note 07]]
- [ ] `kkt.py` — [[operations-research/09-nonlinear-optimisation|note 09]]
- [ ] `game.py` — [[operations-research/11-decision-analysis-and-game-theory|note 11]]

## Practical stopping points

You don't have to read all fourteen to get value:

1. **After 02** you can write and solve real LPs. That alone covers a large share of practical work.
2. **After 05** you know linear programming properly: model, solve, and say how much to trust the answer.
3. **After 07** you can model most scheduling, routing and planning problems a business will bring you.
4. **12 on its own** is the single most useful note for a software engineer.

## The things worth carrying

If the algebra fades, these keep paying:

1. **Write the variables in words, with units, before any maths.** Most formulation errors are found here → [[operations-research/02-formulating-linear-programs|02]]
2. **The optimum of an LP is at a corner, and the corner names the binding constraints.** Those are the bottlenecks → [[operations-research/03-the-geometry-of-linear-programs|03]]
3. **A shadow price is a rate over a range.** Quote the range, or the price is a confident wrong answer → [[operations-research/05-duality-and-sensitivity|05]]
4. **A feasible solution and a bound together tell you how good a plan is without knowing the optimum.** That's what the optimality gap is → [[operations-research/05-duality-and-sensitivity|05]], [[operations-research/07-integer-programming|07]]
5. **Max flow equals min cut, and widening anything outside the cut adds nothing** → [[operations-research/06-network-models|06]]
6. **Rounding an LP answer is not integer programming.** It can be infeasible or far from optimal → [[operations-research/07-integer-programming|07]]
7. **Convexity, not linearity, decides whether a local optimum can be trusted** → [[operations-research/09-nonlinear-optimisation|09]]
8. **No information is worth more than perfect information** — a fast way to kill proposals → [[operations-research/11-decision-analysis-and-game-theory|11]]
9. **Time in system is $1/(1-\rho)$ service times.** At 90% utilisation, ten times; at 95%, twenty → [[operations-research/12-queueing-theory|12]]
10. **One shared queue beats several separate ones** with the same servers → [[operations-research/12-queueing-theory|12]]
11. **EOQ is flat at the bottom**: 20% off the optimum costs about 2% → [[operations-research/13-inventory-models|13]]
12. **A million runs of a wrong simulation give a precise wrong answer.** Validate, don't just replicate → [[operations-research/14-simulation|14]]

## Where this connects

**Software engineers meet operations research more than they realise:**

- **Latency and capacity** — every thread pool, connection pool and request queue is a queueing system; note 12 explains why p99 latency explodes before CPU hits 100% → [[backend/index|backend]], [[devops/index|devops]]
- **Scheduling** — Kubernetes placing pods is bin packing; CI runners, cron jobs and batch systems are scheduling problems → [[operations-research/07-integer-programming|07]]
- **Routing** — maps, delivery apps and network routing protocols run shortest-path and vehicle-routing algorithms → [[operations-research/06-network-models|06]], [[networking/index|networking]]
- **Product features** — "best timetable", "cheapest basket", "fair shift rota" features are small optimisation models behind an API. A study-plan or meal-plan generator is an integer program

**Within the vault:**

- [[dsa/index|DSA]] — graphs, greedy and dynamic programming are the algorithmic half of notes 06, 08 and 10
- [[mathematics/07-applied-and-computational/01-numerical-methods/10-numerical-optimisation|Numerical optimisation]] — the algorithms under note 09
- [[control-theory/index|Control theory]] — optimal control and LQR are dynamic programming in continuous time, and MPC solves an optimisation problem every sample
- [[systems-engineering/index|Systems engineering]] — trade studies are decision analysis with less arithmetic
- [[theory-of-computation/07-complexity-classes|Complexity classes]] — why integer programming is NP-hard and LP isn't

## Prerequisites and gaps

**What this track doesn't cover:** stochastic programming and robust optimisation (optimising directly under uncertainty, not just testing afterwards), column generation and decomposition for very large models, constraint programming, multi-objective optimisation beyond a mention, forecasting, and detailed vehicle-routing and scheduling formulations with time windows. Each is a real topic with its own literature.

**Tooling gap:** the examples use SciPy's low-level matrix interface, which is good for learning and awkward for big models. Real models are written in a modelling layer — **PuLP** or **Pyomo** in Python, **JuMP** in Julia, or **OR-Tools**'s own APIs — which let you write `sum(x[p] for p in products) <= capacity` instead of building matrices by hand. Learning one of these is the first step after this track.

## The honest note

**This is a map, not a practice.** Operations research is learned by modelling a real, messy decision, getting it wrong, talking to the person who actually does the work, and modelling it again. The reading tells you what a model is; only building one for a real problem tells you what's hard about it — usually the data and the missing constraint nobody mentioned, not the solver.

**The cheapest way to close that gap: model a decision you actually make.** Your own study timetable, a weekly meal plan on a budget, a rota for something you organise. Small, real, and you're the domain expert who can say "that answer is wrong because…". → [[operations-research/projects|projects]]

## Related

- [[operations-research/projects|Operations research projects]]
- [[control-theory/index|Control Theory]] — the other "decisions by mathematics" track
- [[mathematics/index|Mathematics]] — the probability, calculus and linear algebra underneath
- [[dsa/index|DSA]] — the algorithms side
