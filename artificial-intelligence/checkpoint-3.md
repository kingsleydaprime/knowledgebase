---
id: 93c6543c-6071-412a-bfe6-94e1967860aa
kind: checkpoint
minutes: 60
---

# AI Checkpoint 3: Heuristic Search

A 1-hour test on everything so far, sections 01 to 03, with most of the marks on section 03: heuristics, greedy best-first search, A\*, heuristics for the 8-puzzle, and the local search methods. Take it when you've finished lesson 11 of section 03, before you start adversarial search.

**Instructions:** answer **all 13 questions**. The paper is out of 54 marks. Time allowed: **1 hour**; you can pause it. Have paper, a pen and a calculator ready, and sketch the graph in Question 5 before you trace it. The short questions are marked for you; for the longer ones, write your answer on paper, then mark yourself against the worked answer after you submit.

**Conventions for every trace in this paper**, the same as the lessons: best-first methods (uniform-cost, greedy and A\*) take the node with the smallest value off the frontier, break ties alphabetically, test for the goal when a node comes off the frontier, and keep only the cheapest known path to each node.

## Question 1
<!-- q: mcq id="d1d687d0" marks="2" -->

What does the Turing test judge a machine by? (2 marks)

- [ ] Whether its internal steps match a human's
- [x] Whether its answers can be told apart from a person's
- [ ] Whether it reasons by the laws of logic
- [ ] Whether it chooses the best action given what it knows

<details><summary>Solution</summary>

**Whether its answers can be told apart from a person's.** It's the "acting like humans" approach: it looks only at behaviour, not at what goes on inside.

**Revise:** [[artificial-intelligence/01-foundations/03-the-four-approaches-to-ai|The Four Approaches to AI]].

</details>

## Question 2
<!-- q: mcq id="840ea764" marks="2" -->

All step costs are equal, the search space is very large, and you have no idea how deep the solution is. Which uninformed method is the usual choice? (2 marks)

- [ ] Breadth-first search
- [ ] Depth-first search
- [ ] Depth-limited search
- [x] Iterative deepening search

<details><summary>Solution</summary>

**Iterative deepening search.** It finds the shallowest goal like BFS, with linear memory like DFS, and it doesn't need the depth in advance, as depth-limited search does.

**Revise:** [[artificial-intelligence/02-uninformed-search/06-iterative-deepening-search|Iterative Deepening Search]].

</details>

## Question 3
<!-- q: exact id="10212cc5" marks="2" answer="18" -->

You want a two-digit number whose digits add up to 9 and multiply to 14. An exhaustive generator tries 10, 11, 12, … in order and tests each one. How many numbers does it test, up to and including the first that works? (2 marks)

<details><summary>Solution</summary>

The first that works is **27** ($2 + 7 = 9$, $2 \times 7 = 14$). From 10 to 27 is $27 - 10 + 1 = 18$ tests. A smarter generator that only makes numbers whose digits sum to 9 (18, 27, 36, …) finds it on the second test. The test didn't change; the generator got smarter.

**Revise:** [[artificial-intelligence/03-heuristic-search/02-generate-and-test|Generate and Test]].

</details>

## Question 4
<!-- q: gap id="ddfe55ce" marks="3" answers="g(n)|g;h(n)|h;g(n)+h(n)|g+h|g(n) + h(n)|g + h" -->

Each best-first method ranks the frontier by an evaluation function $f(n)$. Fill in each one, using $g(n)$ for the cost so far and $h(n)$ for the heuristic estimate. (3 marks)

Uniform-cost search: $f(n)$ = ___. Greedy best-first search: $f(n)$ = ___. A\* search: $f(n)$ = ___.

<details><summary>Solution</summary>

1. **Uniform-cost: $g(n)$**, the cost already paid. It looks only backwards.
2. **Greedy: $h(n)$**, the estimate still to go. It looks only forwards.
3. **A\*: $g(n) + h(n)$**, the estimated cost of the cheapest solution through $n$.

**Revise:** [[artificial-intelligence/03-heuristic-search/01-heuristics-and-heuristic-search|Heuristics and Heuristic Search]].

</details>

## Question 5

The tables give a graph and a heuristic. Every edge can be travelled both ways. The start is S and the goal is G.

| Edge | Cost |
|---|---|
| S – A | 2 |
| S – B | 5 |
| A – C | 3 |
| A – D | 6 |
| B – D | 3 |
| C – D | 2 |
| C – G | 7 |
| D – G | 2 |

| Node | S | A | B | C | D | G |
|---|---|---|---|---|---|---|
| $h$ | 8 | 6 | 5 | 3 | 2 | 0 |

### (a) The greedy route
<!-- q: mcq id="a72048d9" marks="2" -->

Which route does greedy best-first search return? (2 marks)

- [ ] S → A → C → D → G
- [x] S → B → D → G
- [ ] S → A → D → G
- [ ] S → A → C → G

<details><summary>Solution</summary>

**S → B → D → G.** Take S off; add A ($h$ 6) and B ($h$ 5). Take B (smaller $h$); add D ($h$ 2). Take D; add G ($h$ 0). Take G. Goal. It only ever looked at $h$, so it went to B, which looks closer, without noticing that the road to B costs 5.

</details>

### (b) The greedy cost
<!-- q: exact id="225f7777" marks="1" answer="10" -->

What is the path cost of the greedy route? (1 mark)

<details><summary>Solution</summary>

$5 + 3 + 2 = 10$.

</details>

### (c) The A\* order
<!-- q: exact id="61bf18eb" marks="3" answer="S, A, C, D, G" accept="SACDG" -->

In what order does A\* take nodes off the frontier, up to and including G? (3 marks)

<details><summary>Solution</summary>

**S, A, C, D, G.** Write each frontier node as $f = g + h$.

1. Take S ($f = 8$). Add A ($2 + 6 = 8$) and B ($5 + 5 = 10$).
2. Take A (8). Add C ($5 + 3 = 8$) and D ($8 + 2 = 10$).
3. Take C (8). D drops to $g = 7$, $f = 9$; add G ($12 + 0 = 12$).
4. Take D (9). G drops to $g = 9$, $f = 9$. B via D would be $g = 10$, worse than 5.
5. Take G (9). Goal.

B is never expanded: its $f$ of 10 is above the optimal cost 9, so nothing through B can win.

</details>

### (d) The A\* cost
<!-- q: exact id="3e999dab" marks="1" answer="9" -->

What is the path cost of the route A\* returns? (1 mark)

<details><summary>Solution</summary>

**9**, by S → A → C → D → G ($2 + 3 + 2 + 2$). It's the cheapest route in the graph, 1 cheaper than greedy's.

</details>

### (e) Uniform-cost search for comparison
<!-- q: exact id="485e2cb1" marks="2" answer="6" -->

Uniform-cost search also returns the cost-9 route. How many nodes does it take off the frontier, counting S and G? (2 marks)

<details><summary>Solution</summary>

**6**: S (0), A (2), B (5; ties with C at 5, alphabetical), C (5), D (7), G (9). A\* took off 5, because the heuristic told it B couldn't lead anywhere under 9; uniform-cost search expanded B just because B was cheap to reach.

</details>

### (f) Is the heuristic admissible?
<!-- q: open id="ae354700" marks="3" -->

Show that this heuristic is admissible. (3 marks)

<details><summary>Solution</summary>

**Admissible means $h(n) \le h^*(n)$ for every node (1 mark)**, where $h^*(n)$ is the true cheapest cost from $n$ to G.

**The true costs (1 mark):** D 2 (D → G); C 4 (C → D → G); B 5 (B → D → G); A 7 (A → C → D → G); S 9; G 0.

**Compare (1 mark):** S $8 \le 9$, A $6 \le 7$, B $5 \le 5$, C $3 \le 4$, D $2 \le 2$, G $0 \le 0$. It never overestimates, so it's admissible. (It's also consistent: on every edge, $h(n) \le c(n, n') + h(n')$; for example $h(B) = 5 \le 3 + h(D) = 5$.)

</details>

### (g) An overestimate
<!-- q: exact id="ea61678f" marks="2" answer="10" -->

Someone changes $h(C)$ to 8, though C is really only 4 from the goal. Every other value stays the same. What path cost does A\* now return? (2 marks)

<details><summary>Solution</summary>

**10.** C now gets $f = 5 + 8 = 13$, so A\* never expands it. It takes S, A, then B and D (both $f = 10$), and G comes off at $f = 10$ by S → A → D → G. The optimal route ran through C, and the overestimate hid it. One bad value, and A\* is no longer optimal.

**Revise:** [[artificial-intelligence/03-heuristic-search/03-greedy-best-first-search|Greedy Best-First Search]], [[artificial-intelligence/03-heuristic-search/04-a-star-search-1|A\* Search 1]], [[artificial-intelligence/03-heuristic-search/05-a-star-search-2|A\* Search 2]].

</details>

## Question 6

An 8-puzzle state, row by row, is 1 8 2 / 4 3 5 / 7 6 _ (where _ is the blank). The goal is 1 2 3 / 4 5 6 / 7 8 _.

### (a) Misplaced tiles
<!-- q: exact id="5e180fa6" marks="1" answer="5" -->

What is $h_1$, the number of misplaced tiles (not counting the blank)? (1 mark)

<details><summary>Solution</summary>

**5**: tiles 8, 2, 3, 5 and 6 are out of place. Tiles 1, 4 and 7 are home.

</details>

### (b) Manhattan distance
<!-- q: exact id="554311a7" marks="2" answer="8" -->

What is $h_2$, the sum of the Manhattan distances of the tiles from their goal squares? (2 marks)

<details><summary>Solution</summary>

**8.** Tile 8 is two rows from home (2); tile 2 is one column (1); tile 3 is one row and one column (2); tile 5 is one column (1); tile 6 is one row and one column (2). $2 + 1 + 2 + 1 + 2 = 8$. The true solution takes 10 moves, so both heuristics underestimate, as admissible ones must.

</details>

### (c) Which heuristic is better
<!-- q: mcq id="4c2752e4" marks="2" -->

Which statement about $h_1$ and $h_2$ is true? (2 marks)

- [ ] $h_1$ is better, because it's smaller and so safer
- [x] $h_2$ dominates $h_1$, so A\* with $h_2$ expands no more nodes than with $h_1$
- [ ] $h_2$ is not admissible, because it's larger
- [ ] They always give the same value

<details><summary>Solution</summary>

**$h_2$ dominates $h_1$.** For every state $h_2 \ge h_1$, because each misplaced tile adds 1 to $h_1$ but at least 1 to $h_2$, and both are admissible. A larger admissible heuristic pushes more nodes' $f$ above the optimal cost, so A\* never expands them.

**Revise:** [[artificial-intelligence/03-heuristic-search/06-heuristics-for-the-8-puzzle|Heuristics for the 8-Puzzle]].

</details>

## Question 7
<!-- q: open id="70532e6f" marks="3" -->

A warehouse robot moves on a grid of squares, one square north, south, east or west per move, and some squares are blocked by shelves. Invent an admissible heuristic for the number of moves from any square to the loading bay, and use the idea of a relaxed problem to explain why it's admissible. (3 marks)

<details><summary>Solution</summary>

1. **The heuristic (1 mark):** the Manhattan distance to the loading bay: rows apart plus columns apart, ignoring the shelves.
2. **The relaxed problem (1 mark):** it's the exact cost of the problem with the rule "you can't enter a blocked square" removed. With no shelves, the robot can walk straight along a row and then a column, which takes exactly the Manhattan distance.
3. **Why that's admissible (1 mark):** the relaxed problem allows every move the real one does, and more, so its shortest solution can't be longer than the real one. So the heuristic never overestimates.

(Straight-line distance is also admissible, by relaxing "move only along the grid", but it's smaller than Manhattan distance, so it's a weaker heuristic.)

**Revise:** [[artificial-intelligence/03-heuristic-search/06-heuristics-for-the-8-puzzle|Heuristics for the 8-Puzzle]].

</details>

## Question 8

A landscape has states 0 to 10. Each state's neighbours are the states either side of it, and the table gives each state's value. Hill climbing wants the highest value.

| State | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Value | 3 | 5 | 4 | 4 | 4 | 6 | 8 | 7 | 9 | 12 | 10 |

### (a) Where plain hill climbing stops
<!-- q: gap id="4ae1f933" marks="3" answers="1;3;9" -->

Plain steepest-ascent hill climbing moves to its best neighbour only when that neighbour is strictly better. Fill in the state where it stops from each start. (3 marks)

Starting at state 0, it stops at state ___. Starting at state 3, it stops at state ___. Starting at state 8, it stops at state ___.

<details><summary>Solution</summary>

1. **From 0, stops at 1** (value 5): its neighbours have 3 and 4. A local maximum.
2. **From 3, stops at 3** (value 4): both neighbours also have 4, so nothing is strictly better. It's on a plateau and doesn't move at all.
3. **From 8, stops at 9** (value 12): it climbs to 9, whose neighbours have 9 and 10. The global maximum.

</details>

### (b) With sideways moves
<!-- q: exact id="49a6a4c2" marks="2" answer="6" -->

Now allow up to 3 sideways moves to an equally good neighbour (never stepping straight back). Starting at state 3 and stepping sideways to the right, where does it stop? (2 marks)

<details><summary>Solution</summary>

**State 6** (value 8). One sideways move to 4, then uphill to 5 (6) and 6 (8). At 6 the neighbours have 6 and 7, both lower, so it stops. Sideways moves got it off the plateau, but it's now stuck on a local maximum; the global maximum, 12 at state 9, is past the dip at state 7.

</details>

### (c) Local maxima
<!-- q: mcq id="2fb105f0" marks="2" -->

Which states are local maxima that are **not** the global maximum? Choose all that apply. (2 marks)

- [x] State 1
- [ ] State 5
- [x] State 6
- [ ] State 9
- [ ] State 10

<details><summary>Solution</summary>

**States 1 and 6.** Each is higher than both its neighbours (5 against 3 and 4; 8 against 6 and 7), but lower than state 9's 12. State 9 is the global maximum; 5 and 10 each have a higher neighbour.

**Revise:** [[artificial-intelligence/03-heuristic-search/07-hill-climbing-1|Hill Climbing 1]], [[artificial-intelligence/03-heuristic-search/08-hill-climbing-2|Hill Climbing 2]].

</details>

## Question 9
<!-- q: gap id="91d4893f" marks="2" answers="8;11" -->

The current state has value 7. Its neighbours are generated in this order, with values 8, 11 and 9. Fill in the value each type of hill climbing moves to. (2 marks)

Simple hill climbing moves to the neighbour with value ___. Steepest-ascent hill climbing moves to the neighbour with value ___.

<details><summary>Solution</summary>

1. **Simple: 8.** It takes the first neighbour that's better than the current state, and 8 is checked first.
2. **Steepest-ascent: 11.** It checks all the neighbours and takes the best.

Stochastic hill climbing would pick one of the three at random, since all are uphill.

**Revise:** [[artificial-intelligence/03-heuristic-search/08-hill-climbing-2|Hill Climbing 2]].

</details>

## Question 10

Simulated annealing is on a state with value 10 and picks a random neighbour with value 8, so $\Delta E = -2$. It accepts a worse move with probability $e^{\Delta E / T}$.

### (a) When it's warm
<!-- q: exact id="91f304be" marks="2" answer="0.606531" sigfigs="3" -->

What is the probability it accepts the move when $T = 4$? (2 marks)

<details><summary>Solution</summary>

$e^{-2/4} = e^{-0.5} = 0.607$: about a 61% chance of stepping down.

</details>

### (b) When it's cold
<!-- q: exact id="fcea5cf6" marks="2" answer="0.0183156" sigfigs="3" -->

What is the probability it accepts the same move when $T = 0.5$? (2 marks)

<details><summary>Solution</summary>

$e^{-2/0.5} = e^{-4} = 0.0183$: under 2%. The same downhill step that was likely while hot is now almost never taken, so as the temperature falls, simulated annealing turns into hill climbing.

**Revise:** [[artificial-intelligence/03-heuristic-search/10-simulated-annealing|Simulated Annealing]].

</details>

## Question 11

A genetic algorithm has four individuals, each a 4-bit number $x$, and the fitness is $x$ itself: 1010, 0111, 1100 and 0011.

### (a) Roulette-wheel selection
<!-- q: exact id="c51c04fa" marks="2" answer="0.375" accept="3/8|37.5%" -->

With fitness-proportional (roulette-wheel) selection, what is the probability that 1100 is picked on one spin? (2 marks)

<details><summary>Solution</summary>

The fitnesses are 10, 7, 12 and 3, total 32. So $P(1100) = 12 / 32 = 0.375$.

</details>

### (b) Crossover
<!-- q: gap id="c108107d" marks="2" answers="1011;0110" -->

1010 and 0111 are crossed over with the cut after bit 2. Fill in the two children. (2 marks)

The child that starts like 1010 is ___, and the child that starts like 0111 is ___.

<details><summary>Solution</summary>

Cut as 10 | 10 and 01 | 11, and swap the tails: **1011** (11) and **0110** (6). One child is fitter than both parents' average; selection will favour it in the next generation.

**Revise:** [[artificial-intelligence/03-heuristic-search/11-genetic-algorithms|Genetic Algorithms]].

</details>

## Question 12
<!-- q: mcq id="f64adb2d" marks="2" -->

Beam search keeps the best $k$ states at each level. What does it become when the beam width $k$ is unlimited? (2 marks)

- [ ] Greedy best-first search
- [ ] Hill climbing
- [x] Breadth-first search
- [ ] A\* search

<details><summary>Solution</summary>

**Breadth-first search**: it keeps every state on every level. With $k = 1$ it keeps only the single best state each level, which is greedy search with no backing up, like hill climbing on $h$.

**Revise:** [[artificial-intelligence/03-heuristic-search/09-beam-search|Beam Search]].

</details>

## Question 13
<!-- q: open id="55167430" marks="4" -->

Choose the best method from section 03 for each problem, with one reason each. (4 marks)

1. A game character must find the shortest path across a grid map, and you have an admissible heuristic.
2. A university must produce a clash-free timetable for 300 exams; only the final timetable matters, and hill climbing keeps getting stuck.
3. A rescue drone must head toward a signal as fast as possible; a reasonable route now is worth more than the best route later.
4. A translation system builds sentences word by word from millions of possibilities, with fixed memory, and a good sentence is enough.

<details><summary>Solution</summary>

One mark each:

1. **A\***: with an admissible heuristic it's optimal, and usually expands far fewer nodes than uniform-cost search.
2. **Simulated annealing** (or a genetic algorithm): it's a local search, since only the final state matters, and it accepts some worse moves, so it escapes the local maxima that trap hill climbing.
3. **Greedy best-first search**: it heads straight for whatever looks closest, so it's fast, though not optimal.
4. **Beam search**: it keeps only the best $k$ partial sentences at each word, so memory stays fixed, and a good answer is enough.

**Revise:** [[artificial-intelligence/03-heuristic-search/11-genetic-algorithms|Genetic Algorithms]] (the "choosing a method" list at the end).

</details>

## About this checkpoint

Written for the AI subject on 2026-11-26 from the section 01 to 03 lessons. The questions are new, not taken from the lessons' quizzes or the past papers; the [[artificial-intelligence/question-bank|AI question bank]] has more practice for these sections. Every number and trace (the three best-first searches, the true costs, the overestimate, the 8-puzzle heuristics and its 10-move solution, the hill climbs, the annealing probabilities and the genetic algorithm) is computed and asserted by `scripts/diagrams/ai_checkpoints.py`.
