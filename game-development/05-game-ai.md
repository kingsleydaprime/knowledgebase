# Game AI

> **[Intermediate]** · State machines, behaviour trees, pathfinding and utility systems — and why the goal is *fun*, not intelligence.

**Game AI is a different discipline from [[ai-ml/README|machine learning]]**, and conflating them is the most common misconception in the field. It's almost entirely hand-authored logic, and it optimises for **being interesting to play against**, not for playing well.

**A perfect opponent is not fun.** An aimbot wins every time. Chess engines stopped being interesting opponents decades ago. So game AI deliberately includes reaction delays, imperfect aim, forgetting the player's position, and losing convincingly.

**And AI that isn't *legible* reads as broken.** If an enemy flanks brilliantly but the player can't tell why they died, the AI has failed. This is why games have enemies shout "flanking left!" — the announcement isn't for realism, it's so the player can perceive the intelligence. **Perceived intelligence is the product.**

## Finite state machines

The starting point, and still correct for a great deal:

```
        ┌────────┐  sees player   ┌────────┐
        │ PATROL │───────────────►│ CHASE  │
        └────────┘                └────────┘
             ▲                      │    │
    lost him └──────────────────────┘    │ in range
                                          ▼
                                     ┌────────┐
                                     │ ATTACK │
                                     └────────┘
```

States, transitions, conditions. Easy to write, easy to debug, easy for a designer to reason about.

**Where it breaks: transitions grow as O(n²).** Ten states means up to ninety transitions, and adding an eleventh means revisiting all of them. That's the point at which the diagram stops fitting on a whiteboard and behaviour becomes emergent in the bad sense.

**Hierarchical state machines** buy you headroom by nesting (Combat contains Attack/Reload/TakeCover), which is also how UI and animation systems manage the same explosion.

## Behaviour trees

**The industry standard for complex agents**, and the fix for the transition explosion: instead of states pointing at each other, a tree is re-evaluated each tick.

```
Selector (first child that succeeds)
├── Sequence: Flee
│   ├── Condition: health < 25%
│   ├── Action: find cover
│   └── Action: move to cover
├── Sequence: Attack
│   ├── Condition: enemy visible
│   ├── Condition: in range
│   └── Action: fire
└── Action: patrol            ← fallback
```

Node types: **Selector** (try children until one succeeds — an OR), **Sequence** (all must succeed in order — an AND), **Decorator** (modify a child: invert, repeat, cooldown), **Leaf** (a condition or an action).

**Why it beat FSMs:** behaviour is **compositional** rather than connective. Adding "flee when hurt" is one subtree at the top — no existing node changes, because priority is expressed by *position in the tree* rather than by editing transitions. And they're readable enough that designers can author them in a visual editor, which matters more than elegance → [[game-development/07-tools-and-production|tools]].

**Watch for:** trees that grow to hundreds of nodes, per-tick cost when conditions are expensive (cache them), and the fact that a tree has no memory unless you give it a blackboard.

## Utility AI

Instead of rules, **score every possible action each tick and take the best**:

```
score(attack)  = f(health) × f(ammo) × f(distance) × f(threat)
score(heal)    = f(1 - health) × f(has_medkit) × f(safety)
score(flee)    = f(1 - health) × f(enemy_count)
```

Each factor is a curve a designer tunes.

**Strengths:** graceful degradation, nuanced trade-offs, no combinatorial explosion, and behaviour that varies naturally with context. *The Sims* is the canonical example — every object advertises how well it satisfies each need, and Sims simply pick the highest-scoring option.

**Weakness:** hard to debug. When an agent does something odd, the answer is "the numbers said so", and finding *which* factor is a tuning exercise rather than a logic trace. Behaviour trees fail more predictably, which is why many games use both — a tree for structure, utility scoring inside a node.

**GOAP** (Goal-Oriented Action Planning) goes further: define actions with preconditions and effects, and let an A* search over world states build a plan. *F.E.A.R.* (2005) is the famous case, and its enemies still read as unusually smart. Powerful, expensive, and hard to control — planners surprise designers.

## Pathfinding

The most-used algorithm in games, and one this vault already covers → [[foundations/dsa/05-algorithms/06-dijkstra|Dijkstra]] and [[foundations/dsa/05-algorithms/03-bfs|BFS]].

**A\*** is Dijkstra plus a heuristic — an estimate of remaining distance that steers the search toward the goal:

```
f(n) = g(n) + h(n)
       ↑      ↑
    cost so far    estimated cost to goal
```

**The heuristic must never overestimate** (must be *admissible*), or A* can return a non-optimal path. Euclidean or Manhattan distance is the usual choice and is safe.

**The representation matters more than the algorithm:**

- **Grid** — simple, memory-heavy, produces visibly blocky paths
- **Navmesh** — walkable surfaces as convex polygons. **The standard for 3D**: far fewer nodes, and paths that look natural
- **Waypoint graph** — hand-placed nodes; cheap, and constrains movement visibly

**Then smooth the result.** Raw A* output has unnecessary turns; string-pulling or funnel algorithms straighten it. **The path A* returns is optimal in graph terms and looks robotic** — a distinction that catches people who think pathfinding is finished once A* works.

**And for crowds, don't run A* per agent per frame.** Flow fields (one Dijkstra pass, every agent reads a direction) or hierarchical pathfinding are the standard answers, plus local avoidance (steering, RVO) layered on top for agent-to-agent collisions.

## Where machine learning actually fits

**Rarely in shipped gameplay AI**, and it's worth being clear why: designers need *control*. A trained policy can't be told "be 15% more aggressive on Tuesday", can't be guaranteed not to do something absurd, and can't be debugged by reading it.

Where it does appear:

- **Testing** — agents that play thousands of hours to find exploits and unbeatable levels. Genuinely valuable and increasingly used
- **Animation** — motion matching and learned transitions, which is now mainstream
- **Content generation** — textures, dialogue, level suggestions, with a human in the loop
- **Research showcases** — OpenAI Five, AlphaStar. Superhuman, and **not what you want as an opponent**

**Reinforcement learning is a genuinely good fit for balancing**, not for the agents themselves → [[ai-ml/README|AI & ML]].

## Related
- [[foundations/dsa/05-algorithms/06-dijkstra|Dijkstra]] · [[foundations/dsa/05-algorithms/03-bfs|BFS]] — pathfinding's foundation
- [[foundations/discrete-math/07-graph-theory|graph theory]] — what a navmesh is
- [[ai-ml/README|AI & ML]] — the other kind of AI
- [[game-development/02-engines-and-the-game-loop|the game loop]] — where AI ticks

*Source: [reference] — cross-referenced against [roadmap.sh game-developer](https://roadmap.sh/game-developer).*
