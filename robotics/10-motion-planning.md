# Motion Planning

**[Advanced]** — Finding a path that reaches the goal without hitting anything, in a space with more dimensions than you can picture.

## Configuration space

**The idea that makes planning tractable**, and it's worth the effort to internalise.

A robot's **configuration** $q$ is the vector of everything that determines its shape and pose — joint angles for an arm, $(x,y,\theta)$ for a mobile robot. **C-space** is the space of all configurations.

**The trick:**

> **In C-space, the robot is a *point*.** Its whole geometry has been folded into the definition of the space, and obstacles become forbidden regions.

```
  workspace                    C-space
  ┌──────────┐                ┌──────────┐
  │   ▓▓▓    │                │  ▓▓▓▓▓▓  │   obstacle "grown"
  │   ▓▓▓    │      ──→       │ ▓▓▓▓▓▓▓▓ │   by the robot's shape
  │  ┌─┐     │                │    ●     │   robot = a point
  │  └─┘robot│                │          │
  └──────────┘                └──────────┘
```

So planning becomes: **find a curve from $q_{start}$ to $q_{goal}$ that stays in $C_{free}$.** One clean problem statement covering arms, mobile robots and everything else.

**The cost is dimension.** A 6-DOF arm has a 6-dimensional C-space; a 7-DOF arm, 7. **You cannot compute $C_{free}$ explicitly** — for a 6-DOF arm with 100 samples per joint that's $10^{12}$ cells. This is the reason the field moved to sampling.

**And C-space has structure you must respect.** A revolute joint's space is a circle, not a line — 359° and 1° are adjacent. Ignore that and your planner refuses to see the short way round.

## Collision checking

**Where the time goes.** A planner spends 80–90% of its runtime here, so it dominates everything.

**Broad phase** — cheap rejection with bounding volumes (spheres, AABBs) and a spatial structure. Discards most pairs immediately.

**Narrow phase** — exact geometry on the survivors: GJK for convex shapes, mesh-mesh tests otherwise. FCL is the standard library, and it's what MoveIt uses.

**Practical points, all of which matter more than the planner choice:**

- **Self-collision matters.** An arm can hit itself, and it's the constraint people forget. Pre-compute which link pairs *can never* touch and skip them permanently — this is a large saving
- **Simplify geometry.** Convex hulls or capsules instead of full meshes. **An order of magnitude faster** and rarely less safe if you add margin
- **Add a safety margin.** Plan with the robot inflated slightly; execution isn't perfect
- **Discrete checking misses things.** Checking waypoints can step *through* a thin obstacle between samples. Use continuous collision detection, or a step size smaller than the thinnest obstacle

## Grid and graph search

For low-dimensional problems (mobile robots in 2D/3D), discretise and search. → [[foundations/dsa/05-algorithms/06-dijkstra|Dijkstra and graph search]]

**A\*** — the standard. Optimal given an admissible heuristic, and Euclidean distance is admissible for a mobile robot.

**Dijkstra** — A* with no heuristic. Use when you want distances to everything.

**D\* Lite** — **incremental replanning.** When the map changes, repair the existing solution instead of starting over. **This is what you want on a real robot**, because the map always changes: a person walks past, a sensor updates.

**Hybrid A\*** — A* over a continuous state space using motion primitives that obey the vehicle's kinematics. **The standard for car-like robots**, because a plain grid A* path is not drivable by something that can't turn on the spot.

**Grid search breaks down above ~3 dimensions.** Cells grow exponentially. Fine for a mobile robot's $(x,y,\theta)$; hopeless for a 7-DOF arm.

## Sampling-based planning

**The answer for high-dimensional problems**, and the reason arm planning is practical at all.

> **Don't represent the free space. Sample it.** Check random configurations for collision and connect the valid ones. You never build $C_{free}$; you build a graph that approximates its connectivity.

### PRM

**Probabilistic Roadmap** — a two-phase, multi-query method:

1. **Build:** sample many random configurations, keep the collision-free ones, connect nearby pairs with collision-free straight-line segments in C-space
2. **Query:** connect start and goal to the roadmap, run a graph search

**Good when the environment is static and you'll plan many times** — build the roadmap once, query it cheaply forever. A factory cell with a fixed layout is the ideal case.

### RRT

**Rapidly-exploring Random Tree** — single-query, incremental, and the workhorse:

```
tree ← {q_start}
repeat:
    q_rand ← random configuration      (bias ~5-10% toward the goal)
    q_near ← nearest node in tree
    q_new  ← step from q_near toward q_rand by ε
    if the motion q_near→q_new is collision-free:
        add q_new to tree
until q_new is near q_goal
```

**Why it works:** the nearest-neighbour step biases growth toward unexplored regions — large Voronoi regions get sampled more often. **It explores outward aggressively** rather than filling in locally, which is exactly right for finding a way through a maze-like space.

**RRT-Connect** grows trees from *both* ends and tries to join them. **Dramatically faster in practice**, and it's the default in MoveIt.

**The caveat: RRT paths are ugly.** Jagged, wandering, and far from optimal. **Always post-process** — shortcut smoothing (repeatedly try to replace two waypoints with a direct connection) removes most of the ugliness in a few milliseconds and is essentially mandatory.

### RRT*

**Asymptotically optimal.** Same growth, plus a rewiring step: when a new node is added, check whether it offers a cheaper route to its neighbours and re-parent them.

**Converges to the optimal path given enough time.** The path improves continuously, so you can run it under a time budget and take the best so far — an **anytime** algorithm, which is a genuinely useful property when you have 50 ms.

**BIT\*** and **Informed RRT\*** are the modern refinements: once a solution exists, restrict sampling to the ellipsoid that could possibly contain a better one. Much faster convergence.

### What to know about all of them

**Probabilistically complete** — if a solution exists, the probability of finding it goes to 1 with more samples. **They never prove that no solution exists**, and a planner that returns "failed" is telling you it ran out of time, not that the problem is impossible.

**They struggle with narrow passages.** A thin corridor in C-space has low probability of being sampled, and this is the known weakness. Bridge sampling and other heuristics help.

**They're randomised**, so two runs give different paths. **Seed the RNG if you need reproducibility for debugging** — an intermittent planner failure is otherwise very hard to chase.

## Optimisation-based planning

Start with a (possibly bad) path and optimise it against a cost function.

**CHOMP**, **STOMP**, **TrajOpt** — gradient descent or stochastic optimisation on a trajectory, with costs for obstacle proximity, smoothness, and joint limits.

**The trade against sampling:** these produce **smooth, high-quality trajectories directly**, no post-processing. But they're **local** — they find a nearby minimum, not the global answer, and they can fail where a sampling planner would succeed. If the straight-line initialisation goes through a wall, gradient descent may not find its way around.

**A good combination in practice:** sampling planner for a feasible path, optimiser to smooth and improve it. Global search then local refinement.

## Nonholonomic constraints

A car cannot move sideways, so **not every path in C-space is drivable**.

$$\dot{x}\sin\theta - \dot{y}\cos\theta = 0$$

**The constraint is on velocities, not positions.** The car can *reach* any pose (parallel parking works), it just can't get there directly. → [[robotics/01-what-robotics-actually-is|Degrees of freedom]]

**Consequences for planning:**

- **Straight lines in C-space aren't valid connections**, so a plain RRT edge is meaningless
- **Use motion primitives** — short feasible arcs — as the edges instead
- **Dubins paths** (forward only) and **Reeds–Shepp paths** (forward and reverse) give optimal connections for a car with a minimum turning radius. These are the standard local planners
- **Hybrid A\*** and **kinodynamic RRT** are the usual global methods

## From path to trajectory

**A path is geometry. A trajectory is geometry plus time.** The planner gives you the first, and the robot needs the second.

**Time parameterisation** assigns timing that respects velocity, acceleration and torque limits. **TOPP-RA** is the current standard — time-optimal parameterisation along a fixed path.

**Then smooth it.** Corners in a path mean infinite acceleration. Blend them, or fit splines. → [[robotics/09-robot-control|Robot Control]]

**And check the result.** Time-parameterising can produce a trajectory that violates a limit you didn't include. Verify against every actual constraint before executing.

## Task and behaviour layers

Above motion planning sits *what to do*.

**Task planning** — symbolic. "To make tea: fill kettle, boil, pour." PDDL and classical planners. **Task and Motion Planning (TAMP)** interleaves the two, because whether a symbolic action is possible depends on geometry — you can't grasp the mug if the arm can't reach it.

**Behaviour trees** — the practical mechanism for sequencing and reacting, and they've largely displaced finite state machines in robotics. **Modular, composable, and reactive by construction:** a subtree can be reused, and failure propagates upward in a defined way. Games got there first; ROS 2's Nav2 is built on them.

**Finite state machines** are still fine for simple sequences and easier to reason about exhaustively. Use them when the behaviour genuinely is a handful of states.

## Practical notes

**Plan in joint space for arms.** Cartesian paths can be unreachable, pass through singularities, or require a configuration flip mid-path. → [[robotics/07-jacobians-and-singularities|Singularities]]

**Always smooth after sampling-based planning.** Non-negotiable — raw RRT output is not something you should execute.

**Set a time budget and handle failure.** Planners fail. Have a fallback: retry with a different seed, relax a constraint, or stop and ask.

**Replan continuously in dynamic environments.** A path computed once is stale the moment a person moves. Plan at 10 Hz and execute the first part.

**The map is not the world.** Plan with margin. Execution error, localisation error, and unmapped obstacles are all real.

**Use MoveIt (arms) or Nav2 (mobile) before writing your own.** Both wrap OMPL/planners plus collision checking, kinematics, execution and monitoring. **Writing an RRT is a great exercise; shipping your own planning stack usually isn't.** → [[robotics/13-ros-and-robot-software|ROS and Robot Software]]

---

## Related
- [[robotics/06-inverse-kinematics|Inverse Kinematics]] — called constantly inside planning
- [[robotics/09-robot-control|Robot Control]] — executing what this produces
- [[foundations/dsa/05-algorithms/06-dijkstra|Dijkstra and graph search]] — A*, Dijkstra, graph search
- [[robotics/README|Robotics map]]
