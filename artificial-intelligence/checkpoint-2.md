---
id: 37883b17-25c1-4766-8caf-f401a44ce9ed
kind: checkpoint
minutes: 60
---

# AI Checkpoint 2: Uninformed Search

A 1-hour test on everything so far, sections 01 and 02, with most of the marks on section 02: what search is, how to measure a method, and the six blind search methods. Take it when you've finished lesson 11 of section 02, before you start heuristic search.

**Instructions:** answer **all 17 questions**. The paper is out of 56 marks. Time allowed: **1 hour**; you can pause it. Have paper, a pen and a calculator ready: several questions are quicker if you sketch the tree or graph first. The short questions are marked for you; for the longer ones, write your answer on paper, then mark yourself against the worked answer after you submit.

**Conventions for every trace in this paper**, the same as the lessons: neighbours and children are tried in alphabetical order (left to right in a tree); breadth-first search tests for the goal when a node is generated; uniform-cost search tests for the goal when a node is taken off the frontier, and breaks ties alphabetically; graph search never visits a node twice.

## Question 1
<!-- q: mcq id="dae636da" marks="2" -->

A chess program is judged only on whether it picks the move most likely to win, given the position in front of it. Nobody cares whether its thinking resembles a human player's. Which approach to AI is this? (2 marks)

- [ ] Acting like humans
- [ ] Thinking like humans
- [ ] Thinking rationally
- [x] Acting rationally

<details><summary>Solution</summary>

**Acting rationally**: doing whatever is expected to achieve the goal best, given the information available. It judges the program by what it does, against an ideal of the best move, not against humans.

**Revise:** [[artificial-intelligence/01-foundations/03-the-four-approaches-to-ai|The Four Approaches to AI]].

</details>

## Question 2
<!-- q: mcq id="8ff75946" marks="2" -->

In a PEAS description of a supermarket self-checkout machine, which letter does the barcode scanner belong under? (2 marks)

- [ ] Performance measure
- [ ] Environment
- [ ] Actuators
- [x] Sensors

<details><summary>Solution</summary>

**Sensors.** The scanner takes information in from the environment (the barcode). The screen, speaker and receipt printer are actuators, because they act on the environment.

**Revise:** [[artificial-intelligence/01-foundations/05-agents-and-environments|Agents and Environments]].

</details>

## Question 3
<!-- q: mcq id="0a4a2899" marks="2" -->

You plan a delivery route on a map app before you leave, trying one road, deciding it's a bad idea, and going back to try another. While you're still planning, what type of problem is this? (2 marks)

- [ ] Ignorable
- [x] Recoverable
- [ ] Irrecoverable

<details><summary>Solution</summary>

**Recoverable.** While planning, every choice can be undone: you back up and try another road. That's why planning problems are solved with backtracking. Once you're actually driving, a wrong turn costs real time, but the planning itself is recoverable.

**Revise:** [[artificial-intelligence/01-foundations/07-types-of-problems-and-techniques|Types of Problems and Techniques]].

</details>

## Question 4
<!-- q: exact id="8b56c75a" marks="2" answer="216" accept="6^3" -->

A robot arm has 3 joints, and each joint can be set to one of 6 angles. How many different poses does the arm have? (2 marks)

<details><summary>Solution</summary>

$z^n = 6^3 = 216$.

**Revise:** [[artificial-intelligence/01-foundations/08-combinatorial-explosion|Combinatorial Explosion]].

</details>

## Question 5
<!-- q: gap id="cb854135" marks="3" answers="FIFO|first in first out|first-in first-out;LIFO|last in first out|last-in first-out;priority" -->

Complete the sentence about how each method stores its frontier. (3 marks)

Breadth-first search keeps its frontier in a ___ queue, depth-first search in a ___ stack, and uniform-cost search in a ___ queue.

<details><summary>Solution</summary>

**FIFO, LIFO, priority.** That's the only real difference between the three: which node comes off the frontier next. FIFO takes the oldest, LIFO the newest, and the priority queue the cheapest, $g(n)$.

**Revise:** [[artificial-intelligence/02-uninformed-search/01-what-search-is|What Search Is]].

</details>

## Question 6
<!-- q: mcq id="3358c7f9" marks="2" -->

A mechanic suspects one fault: "is the alternator failing?" They start from that fault and work back to the tests that would confirm or rule it out. Which kind of search is this? (2 marks)

- [ ] Data-driven search (forward chaining)
- [x] Goal-driven search (backward chaining)
- [ ] Depth-limited search
- [ ] Bidirectional search

<details><summary>Solution</summary>

**Goal-driven search.** The goal is clearly specified, and the search works backwards from it to the data needed, like the course's medical-diagnosis example. Data-driven search would start from all the car's readings and see what conclusions follow.

**Revise:** [[artificial-intelligence/02-uninformed-search/01-what-search-is|What Search Is]].

</details>

## Question 7
<!-- q: mcq id="f27c8c5d" marks="2" -->

A search keeps a list of every state it has already expanded, and never expands a state on that list again. What is this called? (2 marks)

- [ ] Tree search
- [x] Graph search
- [ ] Depth-limited search
- [ ] Backward chaining

<details><summary>Solution</summary>

**Graph search.** The list is the explored (or reached) set. Tree search has no such list, so on a map with loops it can expand the same state again and again. Graph search is the safe choice when the state space has loops.

**Revise:** [[artificial-intelligence/02-uninformed-search/01-what-search-is|What Search Is]].

</details>

## Question 8
<!-- q: exact id="8194d7b1" marks="2" answer="363" -->

A search tree has branching factor $b = 3$ everywhere. How many nodes does it have below the root, down to and including depth 5? (2 marks)

<details><summary>Solution</summary>

$b + b^2 + b^3 + b^4 + b^5 = 3 + 9 + 27 + 81 + 243 = 363$. The last level, 243, is two-thirds of the total, which is why we write the whole thing as $O(b^d)$.

**Revise:** [[artificial-intelligence/02-uninformed-search/02-measuring-a-search-method|Measuring a Search Method]].

</details>

## Question 9

This table describes a tree. The root is R, and each node's children are listed left to right. Nodes not in the left column have no children.

| Node | Children (left to right) |
|---|---|
| R | P, Q |
| P | T, U, V |
| Q | W, X |
| U | Y, Z |
| W | K |
| X | L, M |

So R is at depth 0; P and Q at depth 1; T, U, V, W and X at depth 2; Y, Z, K, L and M at depth 3. Write every answer as a list of nodes separated by commas, such as A, B, C.

### (a) Breadth-first order
<!-- q: exact id="c37ea676" marks="2" answer="R, P, Q, T, U, V, W, X, Y, Z, K, L, M" accept="RPQTUVWXYZKLM" -->

In what order does breadth-first search visit all 13 nodes? (2 marks)

<details><summary>Solution</summary>

Level by level, left to right: **R, P, Q, T, U, V, W, X, Y, Z, K, L, M.** The FIFO queue takes the oldest node each time, so every node at depth 1 comes before any at depth 2.

</details>

### (b) Depth-first order
<!-- q: exact id="99d8c305" marks="2" answer="R, P, T, U, Y, Z, V, Q, W, K, X, L, M" accept="RPTUYZVQWKXLM" -->

In what order does depth-first search visit all 13 nodes? (2 marks)

<details><summary>Solution</summary>

Down the leftmost branch first, backing up only at a dead end: **R, P, T, U, Y, Z, V, Q, W, K, X, L, M.** T has no children, so DFS backs up to P and tries U, goes down to Y and Z, backs up to V, and only then crosses to Q.

</details>

### (c) Depth-limited search
<!-- q: exact id="f54cd347" marks="2" answer="R, P, T, U, V, Q, W, X" accept="RPTUVQWX" -->

Depth-limited search runs with limit $\ell = 2$ and no goal in the tree. In what order does it visit the nodes? (2 marks)

<details><summary>Solution</summary>

DFS, but a node at depth 2 is treated as having no children: **R, P, T, U, V, Q, W, X.** Y, Z, K, L and M, all at depth 3, are never generated.

</details>

### (d) The two kinds of failure
<!-- q: gap id="e2b0c873" marks="2" answers="cutoff;standard" -->

Fill in each failure value. (2 marks)

Searching for M with limit 2 ends in ___ failure. Searching for N, which isn't in the tree, with limit 5 ends in ___ failure.

<details><summary>Solution</summary>

1. **Cutoff**: M is at depth 3, below the limit. The search hit the limit, so a solution might exist deeper: try again with a bigger limit.
2. **Standard**: with limit 5 the search explores the whole tree (its deepest node is at depth 3) without hitting the limit, so there's no solution at all: stop.

</details>

### (e) Iterative deepening
<!-- q: exact id="41a64166" marks="2" answer="24" -->

Iterative deepening search looks for L, starting with limit 0. Counting every visit in every round, including repeats, how many node visits does it make in total, up to and including reaching L? (2 marks)

<details><summary>Solution</summary>

1. **Limit 0:** R. 1 visit.
2. **Limit 1:** R, P, Q. 3 visits.
3. **Limit 2:** R, P, T, U, V, Q, W, X. 8 visits.
4. **Limit 3:** R, P, T, U, Y, Z, V, Q, W, K, X, L: found. 12 visits.

Total: $1 + 3 + 8 + 12 = 24$.

**Revise:** [[artificial-intelligence/02-uninformed-search/03-breadth-first-search|Breadth-First Search]], [[artificial-intelligence/02-uninformed-search/04-depth-first-search|Depth-First Search]], [[artificial-intelligence/02-uninformed-search/05-depth-limited-search|Depth-Limited Search]], [[artificial-intelligence/02-uninformed-search/06-iterative-deepening-search|Iterative Deepening Search]].

</details>

## Question 10
<!-- q: exact id="2dc13b4c" marks="2" answer="174" -->

A tree has branching factor $b = 3$ and the goal at depth $d = 4$. Iterative deepening generates the depth-1 nodes $d$ times, the depth-2 nodes $d - 1$ times, and so on, down to the depth-4 nodes once. How many nodes does it generate in total (not counting the root)? (2 marks)

<details><summary>Solution</summary>

$4(3) + 3(9) + 2(27) + 1(81) = 12 + 27 + 54 + 81 = 174$. Breadth-first search generates $3 + 9 + 27 + 81 = 120$, so IDS does 45% more work here. With a bigger $b$ the gap shrinks, because the bottom level dominates even more.

**Revise:** [[artificial-intelligence/02-uninformed-search/06-iterative-deepening-search|Iterative Deepening Search]].

</details>

## Question 11
<!-- q: exact id="55e9a4ce" marks="2" answer="22220" accept="22,220" -->

A single breadth-first search with $b = 10$ and the goal at depth $d = 8$ generates $10 + 100 + \dots + 10^8 = 111{,}111{,}110$ nodes. Bidirectional search instead runs two breadth-first searches, each to depth 4. How many nodes do the two generate together? (2 marks)

<details><summary>Solution</summary>

Each half generates $10 + 100 + 1{,}000 + 10{,}000 = 11{,}110$, so together $2 \times 11{,}110 = 22{,}220$: about 5,000 times fewer. Halving the depth takes the square root of $b^d$, not half of it.

**Revise:** [[artificial-intelligence/02-uninformed-search/09-bidirectional-search|Bidirectional Search]].

</details>

## Question 12

The table gives the step costs in a graph. Every edge can be travelled both ways. The start is S and the goal is G.

| Edge | Cost |
|---|---|
| S – A | 3 |
| S – B | 2 |
| A – C | 6 |
| A – D | 4 |
| A – G | 10 |
| B – C | 9 |
| B – E | 1 |
| C – G | 3 |
| D – E | 1 |
| D – G | 7 |

### (a) The breadth-first route
<!-- q: mcq id="3eb05fd4" marks="2" -->

Which route does breadth-first search (graph search, goal test when generated) return? (2 marks)

- [x] S → A → G
- [ ] S → A → C → G
- [ ] S → B → E → D → G
- [ ] S → A → D → G

<details><summary>Solution</summary>

**S → A → G.** Expanding S generates A and B. Expanding A (oldest, and alphabetically first) generates C, D and G, and G passes the goal test as soon as it's generated. It's the fewest steps, 2 roads, at a cost of $3 + 10 = 13$.

</details>

### (b) The depth-first route
<!-- q: exact id="d0d0b23f" marks="2" answer="27" -->

Depth-first search (alphabetical, never revisiting a node) returns S → A → C → B → E → D → G. What is its path cost? (2 marks)

<details><summary>Solution</summary>

$3 + 6 + 9 + 1 + 1 + 7 = 27$. From A it goes to C, then from C to B (alphabetically before G), and keeps going deeper until it stumbles on G. It found *a* route, nearly the worst one.

</details>

### (c) Uniform-cost order
<!-- q: exact id="553181ae" marks="3" answer="S, B, A, E, D, C, G" accept="SBAEDCG" -->

In what order does uniform-cost search take the nodes off the frontier, up to and including G? (3 marks)

<details><summary>Solution</summary>

**S, B, A, E, D, C, G.**

1. Take S (0). Frontier: B 2, A 3.
2. Take B (2). Add C 11, E 3. Frontier: A 3, E 3, C 11.
3. Take A (3; ties with E, alphabetical). C drops to $3 + 6 = 9$; add D 7 and G 13. Frontier: E 3, D 7, C 9, G 13.
4. Take E (3). D drops to $3 + 1 = 4$. Frontier: D 4, C 9, G 13.
5. Take D (4). G drops to $4 + 7 = 11$. Frontier: C 9, G 11.
6. Take C (9). G via C would be 12, worse than 11: no change.
7. Take G (11). Goal.

</details>

### (d) Uniform-cost cost
<!-- q: exact id="ef0c6db7" marks="1" answer="11" -->

What is the path cost of the route uniform-cost search returns? (1 mark)

<details><summary>Solution</summary>

**11**, by S → B → E → D → G ($2 + 1 + 1 + 7$). It uses 4 roads, more than the BFS route's 2, but it's the cheapest route in the graph; the cheapest route with 3 roads or fewer, S → A → C → G, costs 12.

</details>

### (e) Why uniform-cost search waits
<!-- q: open id="d0b677b1" marks="3" -->

G first joins the frontier at step 3 with cost 13. Explain why uniform-cost search doesn't stop there, and what would have gone wrong if it had. (3 marks)

<details><summary>Solution</summary>

1. **The goal test is done when a node comes off the frontier, not when it's added (1 mark).**
2. **At step 3, cheaper nodes are still waiting (1 mark):** E at 3 and D at 7. Since every step cost is positive, a path through one of them might reach G for less than 13, and it does: through E and D, G drops to 11.
3. **If it had stopped (1 mark),** it would have returned S → A → G at 13, not the optimal 11. Only when G is the cheapest thing on the frontier can nothing left beat it.

**Revise:** [[artificial-intelligence/02-uninformed-search/07-uniform-cost-search-1|Uniform-Cost Search 1]], [[artificial-intelligence/02-uninformed-search/08-uniform-cost-search-2|Uniform-Cost Search 2]].

</details>

## Question 13
<!-- q: mcq id="e4a4cbee" marks="2" -->

When every step costs the same, which uninformed method is complete, finds the shallowest goal, and needs only linear memory? (2 marks)

- [ ] Breadth-first search
- [ ] Depth-first search
- [x] Iterative deepening search
- [ ] Bidirectional search

<details><summary>Solution</summary>

**Iterative deepening search**: complete, optimal for equal step costs, $O(b^d)$ time and $O(bd)$ space. BFS has the guarantees but exponential memory; DFS has linear memory but no guarantees; bidirectional search needs $O(b^{d/2})$ memory.

**Revise:** [[artificial-intelligence/02-uninformed-search/10-comparing-uninformed-search|Comparing Uninformed Search Methods]].

</details>

## Question 14
<!-- q: mcq id="041d9bd6" marks="2" -->

A courier company wants the cheapest delivery route. Its roads have different tolls, and it has no estimate of how far any town is from the destination. Which method should it use? (2 marks)

- [ ] Breadth-first search
- [x] Uniform-cost search
- [ ] Depth-limited search
- [ ] Iterative deepening search

<details><summary>Solution</summary>

**Uniform-cost search**: step costs differ and there's no heuristic, and UCS is the only uninformed method that guarantees the cheapest path when costs differ. The other three find the fewest steps, not the lowest cost.

**Revise:** [[artificial-intelligence/02-uninformed-search/10-comparing-uninformed-search|Comparing Uninformed Search Methods]].

</details>

## Question 15
<!-- q: mcq id="9cb6538b" marks="2" -->

For which problem is bidirectional search a poor fit? (2 marks)

- [ ] Finding the fewest train changes from Lagos to Kano on a network where every line runs both ways
- [ ] Solving an 8-puzzle with a known goal arrangement
- [x] Finding a sequence of moves that checkmates the opponent in chess
- [ ] Finding the fewest flights between two airports

<details><summary>Solution</summary>

**Checkmate.** There's no single goal state to start the backward search from (there are huge numbers of checkmate positions), and working out which positions lead *to* a given one is hard. Bidirectional search needs one clear goal state and actions that can be reversed; the other three have both.

**Revise:** [[artificial-intelligence/02-uninformed-search/09-bidirectional-search|Bidirectional Search]].

</details>

## Question 16
<!-- q: mcq id="28ba6f99" marks="2" -->

Why does uniform-cost search need every step cost to be positive? (2 marks)

- [ ] Because a priority queue can't store negative numbers
- [x] Because its guarantee relies on paths only getting dearer as they get longer
- [ ] Because breadth-first search would be faster otherwise
- [ ] Because $g(n)$ must always equal the number of steps

<details><summary>Solution</summary>

**Its guarantee relies on paths only getting dearer as they get longer.** When the goal comes off the frontier at cost $C$, every other frontier node costs at least $C$, and extending it adds a positive cost, so nothing can beat $C$. A negative step could make a longer path cheaper and break that argument; a zero-cost loop could keep the search going round forever.

**Revise:** [[artificial-intelligence/02-uninformed-search/07-uniform-cost-search-1|Uniform-Cost Search 1]].

</details>

## Question 17
<!-- q: open id="ba76905b" marks="6" -->

Three soldiers and two boys must cross a river. Their small boat can carry one soldier, or one boy, or two boys, but never a soldier with anyone else. Everyone starts on the near bank, and everyone must end on the far bank.

Formulate this as a state space search problem (state, initial state, actions, goal test, path cost), and find the fewest crossings that get everyone across. Show the first four crossings and say how the pattern continues. (6 marks)

<details><summary>Solution</summary>

**Formulation (3 marks).**

1. **State**: (soldiers on the near bank, boys on the near bank, which bank the boat is on). People of the same kind are interchangeable, so you don't name them.
2. **Initial state**: (3, 2, near). **Goal test**: (0, 0, far).
3. **Actions**: the boat crosses carrying one soldier, one boy, or two boys, who must be on the boat's bank.
4. **Path cost**: 1 per crossing.

There's no "can't be left together" rule here; the difficulty is entirely in the boat's limits.

**Solution (3 marks): 13 crossings**, found by breadth-first search, so it's the fewest.

| Crossing | Boat carries | Near bank (soldiers, boys) |
|---|---|---|
| 1 | 2 boys across | 3, 0 |
| 2 | 1 boy back | 3, 1 |
| 3 | 1 soldier across | 2, 1 |
| 4 | 1 boy back | 2, 2 |

After those four crossings, one soldier is across and both boys are back on the near bank with the boat: the start position with one soldier fewer. Repeat the four crossings for the second soldier (crossings 5–8) and the third (9–12), then the two boys cross together (13). So $3 \times 4 + 1 = 13$.

**Revise:** [[artificial-intelligence/02-uninformed-search/11-river-crossing-puzzles|River-Crossing Puzzles]].

</details>

## About this checkpoint

Written for the AI subject on 2026-11-26 from the section 01 and 02 lessons. The questions are new, not taken from the lessons' quizzes or the past papers; the [[artificial-intelligence/question-bank|AI question bank]] has more practice for these sections. Every number and trace (the tree orders, the graph searches, the node counts and the soldiers' crossings) is computed and asserted by `scripts/diagrams/ai_checkpoints.py`.
