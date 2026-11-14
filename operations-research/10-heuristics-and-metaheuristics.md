# Heuristics and Metaheuristics

**[Intermediate]** — When exact methods would take too long, you settle for good answers found fast. This note covers building a solution (constructive heuristics), improving it (local search), escaping local optima (simulated annealing, tabu search, genetic algorithms), and — the part most people skip — measuring how good "good" is.

**Source:** `[reference]` — see [[operations-research/index|the domain note]]. The code below was run and its output checked.

## Before you start

You should know why integer programs can be too hard to solve exactly → [[operations-research/07-integer-programming|note 07, section 7]], and what a local optimum is → [[operations-research/09-nonlinear-optimisation|note 09]]. Basic Python: lists, loops, functions.

After this lesson you will be able to:

1. Build a travelling-salesman tour with nearest neighbour and improve it with 2-opt, by hand and in code.
2. Explain why local search gets stuck, and how simulated annealing and tabu search get unstuck.
3. Evaluate a heuristic honestly: against a bound, across several random seeds, and on more than one instance.

**Study route:** sections 1–4 (build, improve), then do the 2-opt check question by hand. Then metaheuristics and evaluation.

## The kid version

You need to visit eight friends' houses and get home, walking as little as possible. A quick plan: always walk to the nearest house you haven't visited yet. That's fast and pretty good, but sometimes it leaves you a long walk at the end. So you look at your map for two paths that cross each other, and swap them so they don't — that always makes the route shorter. Keep un-crossing until nothing crosses. **Heuristics are quick, sensible rules for getting a good answer, plus ways of polishing it.** They don't promise the best answer, but they finish before tea.

**Where the analogy stops working.** With eight houses you could check every route. Heuristics matter when you have thousands of stops, many vans, time windows and driver rules — where checking everything is impossible, and even the clever exact methods of note 07 can't finish.

## 1. Why this exists

A courier has 40 vans and 900 parcels, and the routes must be ready by 6 a.m. An integer program might prove the optimum — next week. The business needs a plan in five minutes, and a plan within 2–3% of optimal is worth far more than a perfect plan that arrives late.

Heuristics run most real-world routing, scheduling and timetabling. Google's OR-Tools, which plans vehicle routes for a lot of logistics software, is mostly heuristic search. The craft is choosing a method that suits the problem and **measuring how far from optimal it is**, because a heuristic with no measure of quality is just a guess.

## Terms used in heuristics

1. **Heuristic**: This is a method that finds a good solution quickly without guaranteeing it's optimal.
2. **Constructive heuristic**: This is a heuristic that builds a solution from nothing, one piece at a time — adding the next city, the next job.
3. **Neighbourhood**: This is the set of solutions you can reach from the current one by one small change, called a **move**. Swapping two cities in a tour is a move; all the tours you can get that way form the neighbourhood.
4. **Local search**: This is the method of repeatedly moving to a better solution in the neighbourhood until none is better.
5. **Local optimum**: This is a solution with no better neighbour. It depends on the neighbourhood: a tour can be a local optimum for swaps but not for 2-opt.
6. **Metaheuristic**: This is a general strategy for guiding local search out of local optima. Simulated annealing, tabu search and genetic algorithms are metaheuristics.
7. **Travelling salesman problem**: This is also known as the **TSP**. This is the problem of finding the shortest tour that visits every city exactly once and returns to the start.
8. **Vehicle routing problem**: This is also known as the **VRP**. This is the multi-vehicle version of the TSP, usually with vehicle capacities and often with delivery time windows.
9. **Lower bound**: This is a value that no solution can beat (for a minimisation). It's how you measure a heuristic's quality without knowing the optimum.

## 2. The running problem

Eight cities on a grid, starting and ending at city 0:

```
  y
  6 ┤      1           3
  5 ┤
  4 ┤         7
  3 ┤   5                    4
  2 ┤               2
  1 ┤
  0 ┼0────────────────────6─────── x
     0  1  2  3  4  5  6  7  8
```

Coordinates: 0 (0,0), 1 (2,6), 2 (5,2), 3 (6,6), 4 (8,3), 5 (1,3), 6 (7,0), 7 (3,4). Distance is straight-line. There are $7!/2 = 2{,}520$ distinct tours — small enough to brute-force, which is exactly why it's a good test: you can check the heuristics against the truth.

## 3. Constructive: nearest neighbour

**Rule:** from the current city, go to the nearest unvisited one. Return home at the end.

From 0, the nearest is 5 (distance 3.16). From 5: 7 (2.24). From 7: 1 (2.24). From 1: 3 (4.00). From 3: 4 (3.61). From 4: 2 (3.16). From 2: 6 (2.83). Then home from 6: 7.00.

**Tour: 0 → 5 → 7 → 1 → 3 → 4 → 2 → 6 → 0. Length ≈ 28.23.**

Notice the last two legs: 4 → 2 goes back *west*, then 2 → 6 goes *east* again. Greedy choices early on leave awkward ones later. Nearest neighbour is typically about 25% above optimal on random instances.

**Other constructive heuristics:**

1. **Cheapest insertion:** start with a small loop and repeatedly insert the city that increases the tour length least.
2. **Clarke–Wright savings** (for vehicle routing): start with one van per customer, then merge routes in order of how much distance the merge saves. Simple, from 1964, and still a standard starting point.

## 4. Local search: 2-opt

**The move:** remove two edges of the tour and reconnect the two pieces the other way. This reverses the segment between them.

```
 before:  ... a ─── b ... c ─── d ...      edges (a,b) and (c,d) cross
 after:   ... a ─── c ... b ─── d ...      segment b...c reversed
```

**A crossing in a tour can always be removed by a 2-opt move, and doing so always makes the tour shorter.** That's the triangle inequality: in any four-sided shape, the two diagonals together are longer than either pair of opposite sides. So a 2-opt local optimum has no crossings.

**Apply it to the nearest-neighbour tour.** The legs 4 → 2 → 6 → 0 zig-zag. Try reversing the segment "2, 6", i.e. replace edges (4, 2) and (6, 0) with (4, 6) and (2, 0):

1. Removed: $d(4, 2) + d(6, 0) = 3.16 + 7.00 = 10.16$.
2. Added: $d(4, 6) + d(2, 0) = 3.16 + 5.39 = 8.55$.
3. Saving: 1.61.

**New tour: 0 → 5 → 7 → 1 → 3 → 4 → 6 → 2 → 0. Length ≈ 26.62.** No improving 2-opt move remains, so it's a 2-opt local optimum.

**Brute force over all 2,520 tours confirms 26.62 is the true optimum.** Here, nearest neighbour plus 2-opt found it. On large instances, 2-opt typically ends about 5% above optimal; richer moves (3-opt, Lin–Kernighan) get within 1–2%.

## 5. Metaheuristics: escaping local optima

Local search stops at the first local optimum, which may be poor. Each metaheuristic is a different answer to "how do I keep going?"

### Simulated annealing

Accept **worse** moves sometimes, with a probability that shrinks over time. A move that makes the tour longer by $\Delta$ is accepted with probability

$$P(\text{accept}) = e^{-\Delta / T}$$

where $T$, the **temperature**, starts high and is lowered slowly. Read it in words: **at high temperature almost anything is accepted, so the search wanders widely; as it cools, it gets choosier, and at the end it's plain local search.** The name comes from annealing metal, where slow cooling lets atoms settle into a low-energy structure.

The tuning that matters: starting temperature (high enough that most moves are accepted at first), cooling rate (slower is better but costs time), and when to stop.

### Tabu search

Always take the **best** neighbouring move, even if it's worse than the current solution, but keep a short **tabu list** of recent moves that may not be reversed. Without the list, the search would step out of a local optimum and immediately step back in. An **aspiration rule** lets a tabu move through anyway if it would give the best solution found so far.

### Genetic algorithms

Keep a **population** of solutions. Repeatedly pick good ones as parents, combine them (**crossover**) to make children, randomly alter some (**mutation**), and keep the fittest. Appealing, widely used, and often outperformed by a well-tuned local search on the same budget — the crossover has to make sense for the problem (combining two tours naively usually doesn't give a valid tour).

### Large neighbourhood search

Destroy part of the solution — remove 10% of the stops — and **repair** it, often with a greedy rule or even a small integer program. It's very effective for vehicle routing and scheduling, and is what many modern solvers do under the hood.

**There's no universally best metaheuristic.** The "no free lunch" theorems show that, averaged over all possible problems, every search method performs the same. What works is a method that exploits the structure of *your* problem — usually through a good neighbourhood.

## 6. Measuring a heuristic honestly

This is where heuristic work is usually weakest. Four habits:

1. **Compare against a lower bound.** For a minimisation, any lower bound gives a worst-case gap: if the heuristic finds 1,050 and the LP relaxation (note 07) proves nothing beats 1,000, you're within 5%. For the TSP, the minimum spanning tree's length is a quick lower bound.
2. **Run several seeds.** Randomised methods give different answers each run. Report the median and the spread over 10+ seeds, not the best run.
3. **Test on several instances**, including ones built to be awkward (clustered cities, tight time windows). A method tuned on one instance has learned that instance.
4. **Fix the time budget.** "Simulated annealing beat tabu search" means nothing unless both had the same time.

## Worked example — nearest neighbour, 2-opt and brute force

**Runnable**, standard library only. Brute force over 5,040 permutations takes a second or two.

```python
# tsp.py — note 10: nearest neighbour, then 2-opt, on 8 fixed cities
import math, itertools

cities = [(0, 0), (2, 6), (5, 2), (6, 6), (8, 3), (1, 3), (7, 0), (3, 4)]
d = lambda a, b: math.dist(cities[a], cities[b])
length = lambda t: sum(d(t[i], t[(i + 1) % len(t)]) for i in range(len(t)))

def nearest_neighbour(start=0):
    tour, left = [start], set(range(len(cities))) - {start}
    while left:
        nxt = min(left, key=lambda j: d(tour[-1], j))
        tour.append(nxt); left.remove(nxt)
    return tour

def two_opt(tour):
    improved = True
    while improved:
        improved = False
        for i in range(1, len(tour) - 1):
            for k in range(i + 1, len(tour)):
                new = tour[:i] + tour[i:k + 1][::-1] + tour[k + 1:]
                if length(new) < length(tour) - 1e-9:
                    tour, improved = new, True
    return tour

nn = nearest_neighbour()
print("nearest neighbour:", nn, round(length(nn), 3))
opt = two_opt(nn)
print("after 2-opt:      ", opt, round(length(opt), 3))
best = min(([0] + list(p) for p in itertools.permutations(range(1, len(cities)))), key=length)
print("true optimum:     ", best, round(length(best), 3))
```

```bash
python3 tsp.py
```

Expected output:

```
nearest neighbour: [0, 5, 7, 1, 3, 4, 2, 6] 28.231
after 2-opt:       [0, 5, 7, 1, 3, 4, 6, 2] 26.616
true optimum:      [0, 2, 6, 4, 3, 1, 7, 5] 26.616
```

The "true optimum" is the 2-opt tour traversed in the opposite direction — the same tour. `two_opt` here recomputes the full length for every candidate, which is $O(n)$ per move; a real implementation computes only the change from the four edges involved, in $O(1)$.

## Common pitfalls and traps

1. **No benchmark.** "Our heuristic saves 12%" — compared to what? The previous manual plan, a simple heuristic, or a bound? Each means something different.
2. **Reporting the best seed.** It's the most flattering number and the least likely to repeat.
3. **Over-tuning.** Parameters tuned on one instance often fail on the next. Tune on some instances, test on others.
4. **Slow move evaluation.** The difference between $O(n)$ and $O(1)$ per move is the difference between a usable heuristic and one that never finishes on real data.
5. **Reaching for a metaheuristic first.** A good constructive heuristic plus a good local search often beats a fancy metaheuristic with a poor neighbourhood. Try the simple thing first and measure.
6. **Ignoring exact methods.** Modern MILP solvers handle surprisingly large problems. Check before assuming a heuristic is needed.

## Check your understanding

1. In the nearest-neighbour tour, verify the 2-opt saving for replacing edges (4, 2) and (6, 0) with (4, 6) and (2, 0), using the distances given.
2. Why does removing a crossing always shorten a tour?
3. In simulated annealing at $T = 10$, what's the probability of accepting a move that's 5 units worse? At $T = 1$?
4. A heuristic finds a route of 1,240 km. The LP relaxation bound is 1,180 km. What can you say about how good the route is?

<details>
<summary>After your attempt — answers</summary>

1. $d(4,2) = \sqrt{9 + 1} \approx 3.16$, $d(6,0) = 7$, $d(4,6) = \sqrt{1 + 9} \approx 3.16$, $d(2,0) = \sqrt{25 + 4} \approx 5.39$. Saving $= 10.16 - 8.55 = 1.61$, which matches $28.23 - 26.62$.
2. Two crossing edges are the diagonals of a four-sided shape formed by their endpoints. By the triangle inequality, the two diagonals together are longer than a pair of opposite sides, so swapping to the sides shortens the tour.
3. $e^{-5/10} = e^{-0.5} \approx 0.61$. At $T = 1$: $e^{-5} \approx 0.0067$. So at high temperature the move is likely; at low temperature it's rare.
4. The route is at most $(1240 - 1180) / 1180 \approx 5.1\%$ above optimal. The true gap could be smaller, since the bound may be loose.

</details>

## Practice — independent task

1. **Modify:** add a function `random_tour(seed)` and run 2-opt from 20 random starting tours. Report the best, median and worst result. Does 2-opt always reach 26.616 on this instance?
2. **Apply:** implement simulated annealing on the same instance with a random 2-opt move, $T$ starting at 10, multiplied by 0.995 each step, for 5,000 steps. Report the median result over 10 seeds.
3. **Scale up:** generate 50 random cities (fixed seed), and compare nearest neighbour, nearest neighbour + 2-opt, and your simulated annealing. Brute force is now impossible, so compute a lower bound: the minimum spanning tree length (use `scipy.sparse.csgraph.minimum_spanning_tree`). Report each method's gap against it.

**Done when:** you have a small table of methods against gap, over several seeds, with a one-paragraph honest conclusion — including what the bound *can't* tell you.

## Before moving on

You're ready when you can build a nearest-neighbour tour and improve it with 2-opt by hand on a small map, explain simulated annealing's acceptance rule in words, and say how you'd measure a heuristic's quality without knowing the optimum.

**Recap:**

1. Construct a solution, then improve it with local search; metaheuristics escape local optima.
2. The neighbourhood is the most important design choice.
3. 2-opt removes crossings; simulated annealing accepts worse moves with a probability that falls as $T$ cools; tabu search forbids undoing recent moves.
4. Always measure: against a bound, over seeds, over instances, at a fixed time.

**Next:** [[operations-research/11-decision-analysis-and-game-theory|Decision Analysis and Game Theory]] — the first of the uncertainty notes: choosing well when the outcome is a gamble, or depends on an opponent.

## Related

- [[operations-research/07-integer-programming|Integer Programming]] — the exact alternative, and the source of lower bounds
- [[dsa/03-algorithms/10-greedy-algorithms/index|DSA: greedy algorithms]] — constructive heuristics are greedy algorithms without the proof
- [[dsa/04-patterns/14-backtracking|DSA: backtracking]] — exhaustive search, the thing heuristics avoid
- [[operations-research/index|Operations research map]]
