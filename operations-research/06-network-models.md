---
id: 7b262398-8c35-4299-9247-597041a78cc7
---

# Network Models

**Source:** `[reference]` — see [[operations-research/index|the domain note]]. The numbers in the worked example were checked by hand; the SciPy script itself has not been run yet — see "Still to run" in [[operations-research/index|the index]].

## Before you start
<!-- bite: 7031eaea-c366-453f-a2a7-76cab3065449 -->

You should know what a directed graph is, with nodes, edges and edge weights → [[dsa/02-data-structures/09-graphs/01-what-a-graph-is|DSA: what a graph is]]. You should be able to formulate a transportation LP → [[operations-research/02-formulating-linear-programs|note 02, pattern 3]] and know what a dual is → [[operations-research/05-duality-and-sensitivity|note 05]].

After this lesson you will be able to:

1. Recognise the five classic network problems in a word description and say which algorithm solves each.
2. Find a maximum flow by hand, and prove it's maximum with a cut.
3. Solve a small assignment problem with the Hungarian method.
4. Find a project's critical path and its slack activities.

**Study route:** sections 1–2, then max flow (section 4) with a pencil. Stop and do check question 2. Then assignment, project scheduling and the code.

## The kid version
<!-- bite: 91059357-f3bd-4f8b-a390-5a7513bc1a97 -->

Picture the water pipes under a town. Water goes in at the reservoir and comes out at the taps; every pipe has a maximum it can carry, and what flows into a junction must flow out of it. Lots of questions are really pipe questions: the shortest way for one drop to get through, the most water the whole system can push per second, the cheapest way to deliver what each tap needs. **Network models are those pipe questions, and they turn out to be the easiest optimisation problems there are.**

**Where the analogy stops working.** Real water doesn't take "the cheapest route" — it follows pressure. In a network model you are *choosing* the flows, and the "pipes" can be roads, cables, job assignments or the order of tasks in a project. Some of the most useful networks have nothing physical flowing at all.

## 1. Why this exists
<!-- bite: 75ca8296-e988-4d18-8035-c3e2b9863253 -->

Many of the largest LPs ever solved are network problems: airline crew scheduling, internet routing, electricity grids, supply chains. They get their own note for three reasons:

1. **Special algorithms beat the simplex method by orders of magnitude.** Dijkstra's algorithm solves a shortest-path problem on a million-node road map in milliseconds.
2. **Integer answers come for free.** If the supplies, demands and capacities are whole numbers, the optimal flows are too. In note 07 you'll see how valuable — and rare — that is.
3. **They show up disguised.** Assigning workers to jobs, matching students to schools and scheduling a project are all network flows once you draw them.

## Terms used in network models
<!-- bite: d600f76a-bf3f-4a36-b8b9-eb62faef0da1 -->

1. **Node**: This is also known as a **vertex**. This is a point in the network — a city, a junction, a worker, a project milestone.
2. **Arc**: This is also known as a **directed edge**. This is a one-way connection from one node to another, usually with a cost or a capacity.
3. **Capacity**: This is the maximum amount that can flow along an arc.
4. **Source and sink**: The source is the node flow starts from and the sink is where it ends. A network can have several of each, as supply and demand nodes.
5. **Flow conservation**: This is the rule that, at every node except sources and sinks, flow in equals flow out. It's the balance constraint from note 02, pattern 5.
6. **Cut**: This is a split of the nodes into two groups, one containing the source and the other the sink. The capacity of a cut is the total capacity of arcs that go from the source side to the sink side.
7. **Augmenting path**: This is a path from source to sink along which more flow can still be pushed — every forward arc has spare capacity, and every backward arc has flow that could be cancelled.
8. **Totally unimodular**: A matrix is totally unimodular when every square sub-matrix has determinant 0, 1 or −1. Network constraint matrices are; this is why their LP solutions come out as whole numbers.

## 2. One problem underneath them all: minimum-cost flow
<!-- bite: 4ce6d2b7-c577-4f5c-b7ec-1b174b1fb6ff -->

Every problem in this note is a special case of one model. Each node $i$ has a net supply $b_i$ (positive for supply, negative for demand, zero for a junction). Each arc $(i, j)$ has a cost $c_{ij}$ per unit and a capacity $u_{ij}$. Choose flows $x_{ij}$:

$$\min \sum_{(i,j)} c_{ij} x_{ij} \quad\text{s.t.}\quad \underbrace{\sum_j x_{ij} - \sum_j x_{ji}}_{\text{out minus in}} = b_i \;\;\forall i, \qquad 0 \le x_{ij} \le u_{ij}$$

The special cases, and what each fixes:

| Problem | What it asks | Special structure | Algorithm |
|---|---|---|---|
| Shortest path | cheapest route from $s$ to $t$ | send 1 unit, no capacities | Dijkstra (non-negative costs), Bellman–Ford (negative costs) |
| Maximum flow | most that can get from $s$ to $t$ | no costs, just capacities | Ford–Fulkerson / Edmonds–Karp, push–relabel |
| Transportation | cheapest way to meet demand from supply | two layers: sources then sinks | network simplex |
| Assignment | match $n$ people to $n$ jobs | transportation with all supplies and demands 1 | Hungarian method |
| Project scheduling | how long a project takes | a DAG; find the *longest* path | critical path method |

## 3. Shortest path
<!-- bite: 159fdb36-d2e2-42c2-99cc-eb5b20008203 -->

You've met this in DSA: Dijkstra's algorithm repeatedly settles the closest unsettled node → [[dsa/02-data-structures/09-graphs/06-algorithms/index|DSA: graph algorithms]]. The operations research view adds one thing: **shortest path is an LP**, the min-cost flow with one unit of supply at $s$ and one unit of demand at $t$. Its dual assigns each node a "potential" $\pi_i$ — the shortest distance from $s$ — and the dual constraints $\pi_j - \pi_i \le c_{ij}$ are exactly the triangle inequality that Dijkstra and Bellman–Ford maintain. The algorithm *is* a dual method.

The practical consequence: **when costs can be negative** (a route that earns money, like a backhaul load), Dijkstra breaks and you need Bellman–Ford. A negative-cost *cycle* makes the problem unbounded — note 03's fourth outcome, in network form.

## 4. Maximum flow and the minimum cut
<!-- bite: bb6ffb66-25ba-4eb3-9418-f0ddb66997e9 -->

**The network.** Source $s$, sink $t$, two junctions $a$ and $b$. Capacities in units per hour:

```text
            10            4
      s ─────────▶ a ─────────▶ t
      │            │            ▲
    5 │         15 │            │ 10
      ▼            ▼            │
      b ◀──────────┘            │
      └─────────────────────────┘
```

Arcs: $s \to a$ (10), $s \to b$ (5), $a \to b$ (15), $a \to t$ (4), $b \to t$ (10).

**Pause and predict:** what's the most that can reach $t$ per hour?

### Ford–Fulkerson, step by step

Repeat: find any augmenting path, push as much as its tightest arc allows, update.

1. **Path $s \to a \to t$.** Tightest arc: $a \to t$ with 4. Push 4. Flow so far: 4. $a \to t$ is now full.
2. **Path $s \to b \to t$.** Tightest: $s \to b$ with 5. Push 5. Flow: 9. $s \to b$ is full; $b \to t$ has 5 spare.
3. **Path $s \to a \to b \to t$.** Spare: $s \to a$ has 6, $a \to b$ has 15, $b \to t$ has 5. Push 5. Flow: 14. $b \to t$ is full.
4. **No augmenting path remains.** Both arcs into $t$ are full.

**Maximum flow: 14 units per hour.** Final flows: $s \to a$ 9, $s \to b$ 5, $a \to b$ 5, $a \to t$ 4, $b \to t$ 10. Check conservation at $a$: 9 in, 5 + 4 out. ✓

### Proving it's the maximum

**The max-flow min-cut theorem states that the maximum flow from source to sink equals the minimum capacity of any cut separating them.**

Take the cut with $\{s, a, b\}$ on one side and $\{t\}$ on the other. The arcs crossing it are $a \to t$ (4) and $b \to t$ (10): capacity 14. No flow can exceed any cut's capacity, because all flow must cross every cut. A flow of 14 meets a cut of 14, so both are optimal. The cut is the dual certificate — the network version of note 05's strong duality.

**Why the cut is useful in practice.** It names the bottleneck. To raise throughput, you must widen one of the arcs in the minimum cut; widening anything else ($s \to a$, say) adds nothing. In this network, upgrading $s \to a$ from 10 to 100 changes the maximum flow by exactly zero.

**Why "backward arcs" matter.** Augmenting paths may also *cancel* existing flow, by going backwards along an arc that carries flow. Without that, a bad choice of early paths can get stuck below the maximum. Edmonds–Karp chooses the shortest augmenting path each time (by breadth-first search), which guarantees polynomial time.

## 5. Assignment and the Hungarian method
<!-- bite: e4c98a3d-0074-4329-9d7d-ab74a7b89636 -->

Three workers, three jobs, and the hours each worker would take:

```text
          J1   J2   J3
     A     9    2    7
     B     6    4    3
     C     5    8    1
```

Assign each worker one job to minimise total hours. There are $3! = 6$ ways. With 20 workers there are $20! \approx 2.4 \times 10^{18}$, so enumeration is out.

**The key fact:** subtracting a constant from a whole row (or column) doesn't change which assignment is best, because every assignment uses exactly one entry from each row. So reduce until zeros appear, then look for an assignment that uses only zeros.

1. **Subtract each row's minimum** (2, 3 and 1):

```text
          J1   J2   J3
     A     7    0    5
     B     3    1    0
     C     4    7    0
```

2. **Subtract each column's minimum** (3, 0 and 0):

```text
          J1   J2   J3
     A     4    0    5
     B     0    1    0
     C     1    7    0
```

3. **Find an independent set of zeros** — one per row and column. A must take J2 (its only zero). C must take J3. That leaves B on J1, which is a zero. ✓

**Assignment: A → J2, B → J1, C → J3. Total: 2 + 6 + 1 = 9 hours.**

When no complete set of zeros exists after step 2, the full method adds a step: cover all zeros with the fewest lines, subtract the smallest uncovered number from every uncovered entry, add it where lines cross, and try again. It runs in $O(n^3)$.

## 6. Project scheduling: the critical path
<!-- bite: a081b57b-e16e-4977-a6d3-82e67f2c001c -->

A project is a set of activities, some of which must finish before others start. The question: **how soon can the whole project finish, and which activities can't slip without delaying it?**

| Activity | Takes (days) | Must follow |
|---|---|---|
| A — design | 3 | — |
| B — order parts | 5 | A |
| C — write software | 6 | A |
| D — assemble | 2 | B |
| E — integrate and test | 3 | C, D |

Draw it as a graph of dependencies; it's a **directed acyclic graph**, because dependencies can't loop. The project's duration is the **longest** path through it — every chain of dependent work has to fit.

**Forward pass — earliest finish of each activity:**

1. A: 3.
2. B: after A, $3 + 5 = 8$. C: after A, $3 + 6 = 9$.
3. D: after B, $8 + 2 = 10$.
4. E: after both C (9) and D (10), so starts at 10 and finishes at $10 + 3 = 13$.

**The project takes 13 days.** The longest path is A → B → D → E: $3 + 5 + 2 + 3 = 13$. That's the **critical path**.

**Slack.** C could finish as late as day 10 without delaying E, so it has **1 day of slack**. A, B, D and E have zero slack: any delay to them delays the project.

This is the critical path method (CPM). Its statistical cousin, PERT, gives each activity a range of durations. The insight managers use: **speeding up a non-critical activity is wasted money.** Paying to finish C a day early changes nothing.

Note that the longest path is easy here *only* because the graph is acyclic. Longest path in a general graph is NP-hard.

## Worked example — assignment and max flow with SciPy
<!-- bite: 5f140737-eb21-4487-ae62-bb7d143ab1f9 -->

**Runnable.** SciPy 1.4+ (`maximum_flow` needs integer capacities).

```python
# networks.py — assignment and max flow from note 06
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow

cost = np.array([[9, 2, 7],
                 [6, 4, 3],
                 [5, 8, 1]])
rows, cols = linear_sum_assignment(cost)
for r, k in zip(rows, cols):
    print(f"worker {'ABC'[r]} -> job J{k + 1} (cost {cost[r, k]})")
print("total cost:", cost[rows, cols].sum())

# nodes: 0=s, 1=a, 2=b, 3=t
cap = np.zeros((4, 4), dtype=np.int32)
cap[0, 1], cap[0, 2], cap[1, 2], cap[1, 3], cap[2, 3] = 10, 5, 15, 4, 10
flow = maximum_flow(csr_matrix(cap), 0, 3)
print("max flow:", flow.flow_value)
print(flow.flow.toarray())
```

```bash
uv run --with scipy python networks.py
```

Expected output (the flow matrix shows positive flow on each arc used, and its negative in the reverse position):

```text
worker A -> job J2 (cost 2)
worker B -> job J1 (cost 6)
worker C -> job J3 (cost 1)
total cost: 9
max flow: 14
```

followed by a $4 \times 4$ flow matrix. Its row for $s$ should sum to 14. The split between $s \to a$ and $s \to b$ may differ from the hand trace — max flows are often not unique — but $a \to t = 4$ and $b \to t = 10$ in every maximum flow, because those arcs form the minimum cut.

## Common pitfalls and traps
<!-- bite: 34cbcd1e-f2b0-44b3-b011-d7c141e90cc5 -->

1. **Dijkstra with negative costs.** It silently returns wrong answers. Use Bellman–Ford, or check that all costs are non-negative.
2. **Unbalanced transportation problems.** If total supply exceeds demand, add a dummy customer with zero-cost arcs to absorb the surplus. Forgetting this makes "meet demand exactly" infeasible.
3. **Expecting a unique max flow.** The maximum *value* is unique; the flows that achieve it usually aren't. The minimum cut is the stable thing to report.
4. **Losing integrality by adding constraints.** "No more than two jobs from the same department" added to an assignment problem breaks total unimodularity. The LP may return fractions; it's now an integer program (note 07).
5. **Treating CPM durations as certain.** The critical path can change when a non-critical activity overruns by more than its slack. Recompute; don't assume.

## Check your understanding
<!-- bite: d6634395-43b0-4616-b244-c2f6f321a3f3 -->

1. Which network problem is each? (a) Assigning 40 delivery drivers to 40 routes. (b) How many fans per minute can leave a stadium through its corridors and gates? (c) A satnav's fastest route.
2. In the max-flow example, what happens to the maximum flow if $b \to t$ is widened to 20? Find the new minimum cut.
3. Why does subtracting a constant from a row of the assignment matrix not change the best assignment?
4. In the project example, activity B overruns by 2 days. What's the new project length, and is the critical path the same?

<details>
<summary>After your attempt — answers</summary>

1. (a) Assignment. (b) Maximum flow — the gates and corridors are capacities. (c) Shortest path, with travel time as cost.
2. Now the arcs into $t$ total 24, so that cut is no longer the bottleneck. The cut $\{s\}$ vs the rest has capacity $10 + 5 = 15$; the cut $\{s, b\}$ vs $\{a, t\}$ has $10 + 20 = 30$; the cut $\{s, a\}$ vs $\{b, t\}$ has $5 + 15 + 4 = 24$. The minimum is 15, the arcs out of $s$. Max flow 15: push 4 on $s \to a \to t$, 6 on $s \to a \to b \to t$, 5 on $s \to b \to t$.
3. Every complete assignment uses exactly one entry from that row, so every assignment's total drops by the same constant. The ranking of assignments is unchanged.
4. B finishes at 10, D at 12, E at 15. The project takes 15 days, and the critical path is still A → B → D → E (C's slack has grown to 3 days).

</details>

## Practice — independent task
<!-- bite: 4b78e764-e650-489a-ba30-8b3ac16dd5bf -->

1. **Reconstruct:** with the note closed, run Ford–Fulkerson on the example network, choosing paths in a *different* order from the trace. Confirm you still reach 14.
2. **Apply — a transportation problem.** Two bakeries supply three shops. Bakery 1 makes 60 loaves, bakery 2 makes 40. Shops need 30, 45 and 25. Costs per loaf (₦): from bakery 1: 4, 6, 9; from bakery 2: 5, 3, 7. Formulate it as an LP and solve with `linprog`. Confirm the answer comes out in whole loaves without any integer constraints.
3. **Extend:** add a shortest-path call with `scipy.sparse.csgraph.dijkstra` on a small road network of your own (6+ nodes), and check one distance by hand.

**Done when:** the transportation answer is integer, meets every demand, and you can explain *why* it's integer using the phrase "network structure".

<details>
<summary>Answer to part 2 — after your attempt</summary>

Minimum cost ₦495: bakery 1 sends 30 to shop 1, 5 to shop 2 and 25 to shop 3; bakery 2 sends 40 to shop 2. Supply and demand both total 100, so it's balanced.

</details>

## Before moving on
<!-- bite: cd9017f8-6268-4646-be93-6dc3f280f04f -->

You're ready when you can recognise each of the five network problems in a word description, find a max flow by hand with a cut to prove it, and find a critical path with slacks.

**Recap:**

1. Shortest path, max flow, transportation, assignment and scheduling are all special cases of minimum-cost flow.
2. Network LPs solve fast with special algorithms, and give integer answers when the data are integers.
3. Max flow equals min cut, and the cut names the bottleneck.
4. The Hungarian method reduces rows and columns until an all-zero assignment appears.
5. A project's length is its longest path; activities on it have zero slack.

**Next:** [[operations-research/07-integer-programming|Integer Programming]] — what happens when you need whole numbers and *don't* get them for free.

## Related
<!-- bite: aa9ee10c-1c91-4a3e-9c2f-c660ad025e36 -->

- [[dsa/02-data-structures/09-graphs/index|DSA: graphs]] — the data structure underneath
- [[dsa/02-data-structures/09-graphs/06-algorithms/index|DSA: graph algorithms]] — Dijkstra, BFS and friends in code
- [[operations-research/05-duality-and-sensitivity|Duality and Sensitivity]] — min cut is a dual
- [[operations-research/07-integer-programming|Integer Programming]] — the next note
- [[networking/index|Networking]] — routing protocols are shortest-path algorithms running on real routers
- [[operations-research/index|Operations research map]]

## About this lesson
<!-- bite: 711252b7-59a6-4407-8e96-ce277a3ab94e -->

**Level:** Intermediate. **Covers:** Shortest paths, maximum flows, assignment, transportation and project scheduling: LPs whose structure is a graph. They solve far faster than general LPs and, remarkably, give whole-number answers without being asked.
