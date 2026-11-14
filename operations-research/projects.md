# Operations Research — Projects

_The track is `[reference]`: read, not yet practised. **Operations research validates against a decision someone actually has to live with, not against a textbook answer.** These projects are ordered from cheapest to most real. Each one says what "done" means._

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

**Python + SciPy (HiGHS) is the whole toolchain.** For anything beyond a toy, move to a modelling layer — PuLP or Pyomo — which wraps the same open-source solvers. Nothing here needs licensed software.

## Projects

- 🟢 **Reproduce every worked example from memory** — the workshop LP, the simplex trace, the branch-and-bound tree, the allocation DP, the M/M/2 comparison. **Done when:** you can rebuild each with the note closed and your numbers match. Exercises: notes [[operations-research/04-the-simplex-method|04]], [[operations-research/07-integer-programming|07]], [[operations-research/08-dynamic-programming|08]], [[operations-research/12-queueing-theory|12]].

- 🟢 ⭐ **Model a decision you actually make** — your weekly study timetable (subjects, hours, one subject per day, deadlines), or a week of meals on a budget meeting nutrition targets. Write it as an LP or MILP, solve it, and **use the answer for a week**. **Done when:** you've followed the plan, written down what the model got wrong, added the missing constraints, and re-solved. That loop — model, act, find the missing rule — *is* the discipline. Exercises: [[operations-research/02-formulating-linear-programs|formulation]], [[operations-research/07-integer-programming|integer programming]].

- 🟢 **A capacity calculator for a real service** — take a service you've built (or a realistic invented one), measure or estimate arrival rate and service time, and use Little's law and M/M/c to predict queueing at 1×, 1.5× and 2× load. Then load-test it and compare. **Done when:** you have a table of predicted vs measured latency and can explain the gaps (variability, warm-up, non-Poisson arrivals). Exercises: [[operations-research/12-queueing-theory|queueing]]. Ties to [[backend/index|backend]].

- 🟡 ⭐ **A rota generator** — staff, shifts, availability, minimum cover per shift, maximum shifts per person, no back-to-back late-then-early, a fairness objective. Build it in PuLP or OR-Tools with a small web or CLI front end. **Done when:** it produces a valid rota for a realistic month in seconds, explains infeasibility in plain words ("Tuesday night can't be covered because…"), and someone who does rotas by hand agrees the result is usable. Exercises: [[operations-research/07-integer-programming|integer programming]].

- 🟡 **A delivery route planner** — a vehicle-routing problem with capacities on real addresses (geocoded, with road distances from an open routing engine). Compare nearest neighbour, 2-opt, and OR-Tools' routing solver, against a lower bound. **Done when:** you have a table of method vs distance vs run time over several instances and seeds, with an honest gap estimate. Exercises: [[operations-research/10-heuristics-and-metaheuristics|heuristics]].

- 🟡 **Simulate a real queue** — a clinic, a restaurant, a bus stop, a support inbox. Collect real arrival and service times (even 50 observations), fit distributions, simulate, and test one change ("add a second server at lunch"). **Done when:** your simulation reproduces the observed average wait within its confidence interval *before* you test the change. Exercises: [[operations-research/14-simulation|simulation]].

- 🔴 **Optimise, then simulate** — a small supply chain: two warehouses, ten shops, random daily demand. Use a MILP to decide which warehouse serves which shop and the reorder points; then simulate a year of random demand against the plan and measure stockouts and cost. Iterate. **Done when:** you can show the plan's simulated service level and cost, and one change the simulation caught that the optimiser couldn't. Exercises: notes [[operations-research/07-integer-programming|07]], [[operations-research/13-inventory-models|13]], [[operations-research/14-simulation|14]].

## If you only do one

**Model a decision you actually make, and live with the answer for a week.** It's the only project here where you're also the client — and the client is where operations research is really tested.

## Related

- [[operations-research/index|Operations research]] — the course these exercise
- [[control-theory/projects|Control theory projects]] — the other "decisions by mathematics" track
- [[project-ideas|Project Ideas]] — the vault-wide index
