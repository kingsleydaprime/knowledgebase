---
id: 8d6b0c20-8eff-4357-bf61-d789b798851a
kind: exam
minutes: 120
choose: 4
---

# SSG 518 Mock Exam 3

A full practice paper in the format of the real SSG 518 (Artificial Intelligence II) exam, with new questions on the same topics. This one leans on diagrams, as the real paper does: three questions ask you to draw, and their worked answers give the picture and a list of what your drawing must show. Sit it like the real thing: closed book, on paper, with a calculator, in one go.

**Instructions:** answer any **four** questions. Each question carries 15 marks, so the paper is out of 60. Time allowed: **2 hours**, about 30 minutes a question. Draw neat, labelled diagrams where a question asks for one. Where a question asks for a number, give it to at least 3 significant figures. The worked answers and marking scheme open after you submit; mark your own long answers and drawings against them honestly.

## Question 1

### (a) Three kinds of model
<!-- q: open id="a675139a" marks="6" -->

Compare the statistical, structural and neural-network approaches to building a pattern-recognition model. For each, say how it represents a pattern, and give one advantage and one disadvantage. (6 marks)

<details><summary>Solution</summary>

Two marks each.

1. **Statistical models** describe each class by numbers learned from data (such as a mean and variance per feature) and classify by probability or distance, as naive Bayes and the nearest-mean classifier do. **Advantage:** well founded, quick to train, and they work with modest data. **Disadvantage:** they assume a shape for each class's distribution, and perform badly when the assumption is wrong.
2. **Structural (syntactic) models** describe a pattern as simple parts and the relationships between them, like a grammar: a character as strokes joined in a certain way. **Advantage:** they capture structure and relationships, and the description can be read and explained. **Disadvantage:** the rules are hard to write and they cope badly with noisy data.
3. **Neural-network models** learn their own features from raw data by adjusting many weights. **Advantage:** high accuracy on complex, noisy data such as images and speech. **Disadvantage:** they need a lot of labelled data and computing power, and it's hard to explain why they made a decision.

**Revise:** [[machine-learning/03-classical-ml/22-pattern-recognition-2|Pattern Recognition 2]].

</details>

### (b) A fingerprint attendance system
<!-- q: open id="a71bc215" marks="9" -->

With the aid of a block diagram, design a pattern-recognition system that takes lecture attendance by fingerprint. Explain each stage, and say how the system is trained (enrolled) before it can be used. (9 marks)

<details><summary>Solution</summary>

**The block diagram (3 marks):**

![A fingerprint attendance system as a block diagram: a scanner captures the print; preprocessing enhances, binarises and thins the ridges; feature extraction finds the minutiae; the minutiae are matched against each student's enrolled template; a match marks the student present, no match asks for another scan; the attendance record is saved and reported to the lecturer.](images/mock3-fingerprint-system.svg)

**What to check in your diagram:**

- It starts with the scanner (input) and ends with the attendance record (output).
- Preprocessing, feature extraction, matching and the decision are separate boxes, in that order, joined by arrows.
- The boxes name what happens in *this* system: ridges, minutiae, templates, present or absent.

**Each stage (4 marks):**

1. **Data acquisition:** an optical or capacitive scanner captures an image of the fingertip.
2. **Preprocessing:** improve contrast, remove noise and smudges, turn the image into black ridges on white (binarise), and thin each ridge to one pixel wide.
3. **Feature extraction:** find the **minutiae**, the points where ridges end or split (bifurcate), with their positions and directions. These are the features; the rest of the image is thrown away.
4. **Matching and decision:** compare the minutiae with the stored template of each enrolled student, scoring how many line up. Above a threshold, mark the best-matching student present; below it, ask for another scan.

**Training, or enrolment (2 marks):** at the start of the semester each student scans the same finger several times; the system extracts the minutiae and stores a template, labelled with the matric number. Testing then checks the false-accept and false-reject rates on scans not used for enrolment, and the threshold is tuned to balance them.

**Revise:** [[machine-learning/03-classical-ml/21-pattern-recognition-1|Pattern Recognition 1]], [[machine-learning/03-classical-ml/22-pattern-recognition-2|Pattern Recognition 2]].

</details>

## Question 2

A one-feature problem has two classes. Class P has the values 2, 3, 3, 11 and 12. Class Q has the values 6, 7, 7, 8 and 8. A new example has the value $x = 9$. You may use the Gaussian density $p(x) = \frac{1}{\sqrt{2\pi\sigma^2}}\, e^{-(x - \mu)^2 / 2\sigma^2}$, with the variance taken as the average squared distance from the mean.

### (a) Two ways to model a class
<!-- q: open id="68262e52" marks="3" -->

State the difference between a parametric and a non-parametric classifier, and name one of each. (3 marks)

<details><summary>Solution</summary>

A **parametric** classifier assumes a fixed form for each class's distribution, usually a Gaussian, and learns a fixed number of parameters (here a mean and a variance per class); the model doesn't grow with the data. Example: naive Bayes, or a Gaussian (maximum likelihood) classifier. A **non-parametric** classifier assumes no form and estimates the density from the training points themselves, so it grows with the data. Example: K-nearest neighbour, or a Parzen window.

</details>

### (b) The variance of class P
<!-- q: exact id="38a52d69" marks="2" answer="18.96" sigfigs="3" -->

Class P's mean is 6.2. What is its variance? (2 marks)

<details><summary>Solution</summary>

The squared distances from 6.2 are $4.2^2, 3.2^2, 3.2^2, 4.8^2, 5.8^2 = 17.64, 10.24, 10.24, 23.04, 33.64$. Their average is $94.8 / 5 = 18.96$. Class P is very spread out.

</details>

### (c) Class P's Gaussian density at 9
<!-- q: exact id="4fd27451" marks="2" answer="0.0745075" sigfigs="3" -->

What is the Gaussian density of class P at $x = 9$? (2 marks)

<details><summary>Solution</summary>

$\mu = 6.2$, $\sigma^2 = 18.96$: $p(9) = \frac{1}{\sqrt{2\pi \times 18.96}} e^{-(2.8)^2 / 37.92} = 0.09162 \times e^{-0.2068} = 0.0745$.

</details>

### (d) Class Q's Gaussian density at 9
<!-- q: exact id="6e9f7deb" marks="2" answer="0.0295437" sigfigs="3" -->

Class Q has mean 7.2 and variance 0.56. What is its Gaussian density at $x = 9$? (2 marks)

<details><summary>Solution</summary>

$p(9) = \frac{1}{\sqrt{2\pi \times 0.56}} e^{-(1.8)^2 / 1.12} = 0.5331 \times e^{-2.893} = 0.0295$. So the Gaussian classifier says **class P** (0.0745 > 0.0295).

</details>

### (e) A Parzen window
<!-- q: exact id="831cdfa1" marks="2" answer="0.2" accept="1/5" -->

A Parzen window of width 2, from 8 to 10, is placed around $x = 9$. The density estimate for a class is the number of its points inside the window divided by (the number of its points × the window width). What is class Q's estimate? (2 marks)

<details><summary>Solution</summary>

Q's two 8s are inside the window: $2 / (5 \times 2) = 0.2$. Class P has no points between 8 and 10, so its estimate is 0. The Parzen window says **class Q**.

</details>

### (f) Which is right?
<!-- q: open id="021187ba" marks="4" -->

The two classifiers disagree. Explain why, and say which answer you trust. (4 marks)

<details><summary>Solution</summary>

1. **Why they disagree (2 marks):** class P isn't one bell: it's two clumps, 2–3 and 11–12, with nothing in between. A single Gaussian can't represent that, so it draws one wide hump (variance 18.96) right across the empty middle, and gives P a fair density at 9, where P has no data at all. Q is one tight clump around 7.2, so its narrow Gaussian falls off fast by 9.
2. **Which to trust (2 marks):** the Parzen window's **Q**. It looks only at the points actually near 9, and the two nearest points (the 8s, 1 away) are both Q, while P's nearest is 11, 2 away. The parametric classifier failed because its assumption about the shape of class P was wrong, which is exactly the disadvantage of parametric methods.

**Revise:** [[machine-learning/03-classical-ml/23-parametric-and-non-parametric-classifiers-1|Parametric and Non-Parametric Classifiers 1]].

</details>

## Question 3

Parts (b) and (c) use this graph. Every edge can be travelled both ways.

| Edge | S–A | S–B | A–B | A–C | B–C | B–D | C–G | A–G | D–G |
|---|---|---|---|---|---|---|---|---|---|
| Cost | 4 | 1 | 2 | 5 | 8 | 4 | 3 | 12 | 9 |

### (a) Formulating the 4-queens problem
<!-- q: open id="eb7c0079" marks="5" -->

Four queens must be placed on a 4 × 4 chessboard so that no two attack each other (no two share a row, column or diagonal). Formulate this as a state-space search problem, placing one queen per column from left to right: give the states, initial state, actions, transition model, goal test and path cost, and say why a solution must exist deep in the tree rather than near the top. (5 marks)

<details><summary>Solution</summary>

1. **States (1 mark):** an arrangement of 0 to 4 queens in the leftmost columns, one per column, with no two attacking.
2. **Initial state and actions (1 mark):** the empty board. An action adds a queen to the leftmost empty column, in any row where it isn't attacked by a queen already placed.
3. **Transition model (1 mark):** the board with that queen added.
4. **Goal test and path cost (1 mark):** 4 queens on the board, none attacking. Path cost doesn't matter (every solution has exactly 4 actions); only the final board counts.
5. **Depth (1 mark):** every solution is at depth 4, the number of queens, and no shallower state can be a goal. So a depth-first search with backtracking is natural: it goes straight to depth 4 and backs up when a column has no safe row. (One solution: rows 2, 4, 1, 3 for columns 1 to 4.)

**Revise:** [[artificial-intelligence/01-foundations/06-problem-solving-in-ai|Problem Solving in AI]], [[artificial-intelligence/05-constraint-satisfaction/01-constraint-satisfaction-problems|Constraint Satisfaction Problems]].

</details>

### (b) Uniform-cost order
<!-- q: exact id="94ff843f" marks="4" answer="S, B, A, D, C, G" accept="SBADCG" -->

Uniform-cost search runs on the graph above from S to the goal G, taking the cheapest node off the frontier, breaking ties alphabetically, and testing for the goal when a node comes off. In what order are the nodes taken off the frontier? (4 marks)

<details><summary>Solution</summary>

**S, B, A, D, C, G.**

1. Take S (0). Frontier: B 1, A 4.
2. Take B (1). A drops to $1 + 2 = 3$; add C 9 and D 5.
3. Take A (3). C drops to $3 + 5 = 8$; add G $3 + 12 = 15$.
4. Take D (5). G drops to $5 + 9 = 14$.
5. Take C (8). G drops to $8 + 3 = 11$.
6. Take G (11). Goal.

</details>

### (c) Uniform-cost cost
<!-- q: exact id="07285a6d" marks="2" answer="11" -->

What is the path cost of the route uniform-cost search returns, from S to G? (2 marks)

<details><summary>Solution</summary>

**11**, by S → B → A → C → G ($1 + 2 + 5 + 3$). G was on the frontier at 15 and then 14 before 11 turned up, which is why uniform-cost search only stops when the goal comes *off* the frontier.

</details>

### (d) Iterative deepening
<!-- q: exact id="d03067bf" marks="4" answer="190" -->

A tree has branching factor $b = 5$ and the goal at depth $d = 3$. Iterative deepening generates the depth-1 nodes 3 times, the depth-2 nodes twice and the depth-3 nodes once. How many nodes does it generate in total, not counting the root? (4 marks)

<details><summary>Solution</summary>

$3(5) + 2(25) + 1(125) = 15 + 50 + 125 = 190$, against $5 + 25 + 125 = 155$ for breadth-first search: 23% more work, for linear memory instead of exponential.

**Revise:** [[artificial-intelligence/02-uninformed-search/07-uniform-cost-search-1|Uniform-Cost Search 1]], [[artificial-intelligence/02-uninformed-search/06-iterative-deepening-search|Iterative Deepening Search]].

</details>

## Question 4

Parts (b) and (c) use this graph and heuristic. Every edge can be travelled both ways; the start is S and the goal is G. Best-first methods break ties alphabetically and test for the goal when a node comes off the frontier.

| Edge | S–A | S–B | A–B | A–C | B–C | B–D | C–G | D–G |
|---|---|---|---|---|---|---|---|---|
| Cost | 1 | 4 | 2 | 5 | 1 | 5 | 3 | 1 |

| Node | S | A | B | C | D | G |
|---|---|---|---|---|---|---|
| $h$ | 5 | 4 | 3 | 2 | 1 | 0 |

### (a) The hill-climbing landscape
<!-- q: open id="8dc7a86b" marks="6" -->

With the aid of a diagram of a state-space landscape, explain the following: global maximum, local maximum, flat local maximum and shoulder. Say why hill climbing can get stuck in three of them, and how sideways moves and simulated annealing each help. (6 marks)

<details><summary>Solution</summary>

**The diagram (2 marks).** Any landscape that shows all four regions, labelled. For example:

![A landscape over states 0 to 14 with values 2, 5, 3, 4, 4, 4, 7, 9, 12, 5, 6, 6, 6, 4, 2: a local maximum of 5 at state 1, a shoulder (a flat stretch of 4 at states 3 to 5 that rises again), the global maximum 12 at state 8, and a flat local maximum of 6 at states 10 to 12.](images/mock3-landscape.svg)

**What to check in your diagram:**

- The horizontal axis is the states and the vertical axis is the value (objective function).
- All four regions are drawn and labelled: a single global maximum, a lower peak (local maximum), a flat stretch that rises again on one side (shoulder), and a flat stretch with lower ground on both sides (flat local maximum).

**The regions (2 marks).** The **global maximum** is the best state of all. A **local maximum** is higher than its neighbours but lower than the global maximum. A **flat local maximum** is a flat top: equal neighbours, lower ground all round. A **shoulder** is a flat stretch partway up a slope, with higher ground further on.

**Why hill climbing gets stuck, and the fixes (2 marks).** Plain hill climbing only moves to a strictly better neighbour and never backtracks, so it stops at a local maximum (every step is down), on a flat local maximum, and on a shoulder (no neighbour is better). **Sideways moves**, a limited number of steps to equal neighbours, carry it across a shoulder, but not off a flat local maximum. **Simulated annealing** sometimes accepts a worse move, with probability $e^{\Delta E / T}$, so while the temperature is high it can step down out of a local maximum and reach the global one.

**Revise:** [[artificial-intelligence/03-heuristic-search/07-hill-climbing-1|Hill Climbing 1]], [[artificial-intelligence/03-heuristic-search/08-hill-climbing-2|Hill Climbing 2]].

</details>

### (b) The greedy cost
<!-- q: exact id="125b40da" marks="2" answer="10" -->

What is the path cost of the route greedy best-first search returns? (2 marks)

<details><summary>Solution</summary>

**10.** Greedy takes S, then B (h 3 beats A's 4), then D (h 1), then G: S → B → D → G, $4 + 5 + 1 = 10$.

</details>

### (c) The A\* order
<!-- q: exact id="f3392eb3" marks="3" answer="S, A, B, C, G" accept="SABCG" -->

In what order does A\* take nodes off the frontier, up to and including G? (3 marks)

<details><summary>Solution</summary>

**S, A, B, C, G.**

1. Take S ($f$ 5). Add A ($1 + 4 = 5$) and B ($4 + 3 = 7$).
2. Take A (5). B drops to $g = 3$, $f = 6$; add C ($6 + 2 = 8$).
3. Take B (6). C drops to $g = 4$, $f = 6$; add D ($8 + 1 = 9$).
4. Take C (6). Add G ($7 + 0 = 7$).
5. Take G (7). Goal.

A\* returns S → A → B → C → G at cost **7**, against greedy's 10. The heuristic is admissible: the true costs to G are S 7, A 6, B 4, C 3, D 1.

</details>

### (d) Annealing when warm
<!-- q: exact id="ee55f7b5" marks="2" answer="0.548812" sigfigs="3" -->

Simulated annealing considers a move with $\Delta E = -3$. With what probability does it accept it at temperature $T = 5$? (2 marks)

<details><summary>Solution</summary>

$e^{-3/5} = e^{-0.6} = 0.549$.

</details>

### (e) Annealing when cool
<!-- q: exact id="68d845e2" marks="2" answer="0.0497871" sigfigs="3" -->

With what probability does it accept the same move at $T = 1$? (2 marks)

<details><summary>Solution</summary>

$e^{-3} = 0.0498$: about 5%, against 55% at $T = 5$. As it cools, it stops taking downhill steps and settles on whatever hill it's on.

**Revise:** [[artificial-intelligence/03-heuristic-search/05-a-star-search-2|A\* Search 2]], [[artificial-intelligence/03-heuristic-search/10-simulated-annealing|Simulated Annealing]].

</details>

## Question 5

Parts (c) to (e) use this table. X is the weather in the morning, {rain, dry}, and Y is the traffic on the way to campus, {jam, clear}.

| Y \ X | Rain | Dry |
|---|---|---|
| Jam | 3/8 | 1/8 |
| Clear | 1/8 | 3/8 |

### (a) A loaded die
<!-- q: open id="152c0b49" marks="3" -->

Explain, in terms of uncertainty and surprise, why a loaded die has lower entropy than a fair one. (3 marks)

<details><summary>Solution</summary>

Entropy is the average surprise, $H = -\sum p \log_2 p$: the average number of bits needed to report the outcome. A fair die is as uncertain as a six-way choice can be: every face has probability 1/6, so $H = \log_2 6 = 2.585$ bits, the maximum. A loaded die makes one face (say the six) very likely, so most rolls are unsurprising and carry little information; the rare faces are surprising but rare, so they add little on average. The outcome is more predictable, so the entropy is lower; a die that always showed six would have entropy 0.

</details>

### (b) Entropy of a source
<!-- q: exact id="d4714922" marks="3" answer="1.75" -->

A source sends four symbols with probabilities 1/2, 1/4, 1/8 and 1/8. What is its entropy, in bits? (3 marks)

<details><summary>Solution</summary>

$H = \frac{1}{2}(1) + \frac{1}{4}(2) + \frac{1}{8}(3) + \frac{1}{8}(3) = 0.5 + 0.5 + 0.375 + 0.375 = 1.75$ bits, less than the 2 bits four equally likely symbols would need.

</details>

### (c) H(X, Y)
<!-- q: exact id="259ea42f" marks="3" answer="1.811278" sigfigs="3" -->

What is the joint entropy $H(X, Y)$, in bits? (3 marks)

<details><summary>Solution</summary>

Two cells are 3/8 and two are 1/8: $H(X, Y) = 2 \times \frac{3}{8}\log_2\frac{8}{3} + 2 \times \frac{1}{8}\log_2 8 = 2(0.5306) + 2(0.375) = 1.81$ bits.

</details>

### (d) H(Y | X)
<!-- q: exact id="81a423e9" marks="3" answer="0.811278" sigfigs="3" -->

What is the conditional entropy $H(Y \mid X)$, in bits? (3 marks)

<details><summary>Solution</summary>

Each column adds up to 1/2, so $H(X) = 1$ bit. Then $H(Y \mid X) = H(X, Y) - H(X) = 1.811 - 1 = 0.811$ bits. Once you know the weather, about 0.81 bits of uncertainty about the traffic remain.

</details>

### (e) I(X; Y)
<!-- q: exact id="1bebf408" marks="3" answer="0.188722" sigfigs="3" -->

What is the mutual information $I(X; Y)$, in bits? (3 marks)

<details><summary>Solution</summary>

Each row also adds up to 1/2, so $H(Y) = 1$ bit. $I(X; Y) = H(Y) - H(Y \mid X) = 1 - 0.811 = 0.189$ bits. Knowing the weather removes about 0.19 of the 1 bit of uncertainty about the traffic: rain makes a jam more likely.

**Revise:** [[information-theory/01-what-information-is|What Information Is]], [[information-theory/02-entropy-joint-conditional-and-mutual|Entropy, Joint, Conditional and Mutual Information]].

</details>

## Question 6

This game tree has a MAX root with three MIN children. The first MIN node's leaves are 5, 9 and 7; the second's are 2, 11 and 8; the third's are 10, 4 and 12 (left to right).

### (a) The minimax value
<!-- q: exact id="34e891aa" marks="2" answer="5" -->

What is the minimax value of the root? (2 marks)

<details><summary>Solution</summary>

**5.** The MIN nodes back up 5, 2 and 4, and MAX takes the largest, 5: the left move.

</details>

### (b) Alpha-beta on the tree
<!-- q: sketch id="b678cb0e" marks="7" -->

Draw the tree and solve it with alpha-beta pruning, searching left to right. Show the backed-up values and the bounds, mark every pruned leaf, and justify each prune. (7 marks)

<details><summary>Solution</summary>

1. **First MIN node:** 5, 9, 7, so it backs up 5. The root now has $\alpha = 5$.
2. **Second MIN node, with $\alpha = 5$:** the first leaf, 2, gives $\beta = 2 \le \alpha = 5$. MIN can already hold MAX to 2 here, worse for MAX than the 5 it has, so **prune 11 and 8**. Value 2.
3. **Third MIN node, with $\alpha = 5$:** 10 gives $\beta = 10$; then 4 gives $\beta = 4 \le 5$: **prune 12**. Value 4.
4. **Root:** max(5, 2, 4) = **5**.

![The Mock 3 tree solved with alpha-beta: a MAX root over three MIN nodes with leaves 5, 9, 7; 2, 11, 8; and 10, 4, 12; the MIN nodes are 5, 2 and 4, so the root is 5; the leaves 11 and 8 under the second MIN node and the leaf 12 under the third are pruned and greyed out.](images/mock3-alphabeta.svg)

**What to check in your drawing:**

- A MAX root, three MIN nodes and nine leaves, with the MIN nodes backed up as 5, 2 and 4, and the root 5.
- Three pruned leaves marked: 11 and 8 under the second MIN node, and 12 under the third. Only 6 of the 9 leaves are examined.
- Each prune has its comparison written beside it ($2 \le 5$, $4 \le 5$).

</details>

### (c) Cut-offs and the horizon effect
<!-- q: open id="387b890f" marks="6" -->

Real games are far too big to search to the end. Explain how a game program uses a depth cut-off and an evaluation function, give an example of an evaluation function for draughts or ayo, and explain the horizon effect. (6 marks)

<details><summary>Solution</summary>

1. **The cut-off (2 marks).** A full game tree has about $b^m$ nodes, impossible for chess ($b \approx 35$) or even ayo. So the program searches only to a fixed depth (say 6 moves ahead), or until time runs out, and treats the positions at that depth as leaves.
2. **The evaluation function (2 marks).** Instead of the true game result, each cut-off position gets an estimated score of how good it is for MAX, and minimax backs these up as usual. It must be fast and correlate with winning. For draughts: (my pieces − your pieces) + 2 × (my kings − your kings), plus a little for controlling the centre. For ayo: (seeds in my store − seeds in yours), plus a penalty for runs of empty pits the opponent can capture from.
3. **The horizon effect (2 marks).** Something bad that will happen just beyond the cut-off depth is invisible to the search. A program about to lose a piece may make delaying moves that push the loss past its horizon, so the position *looks* fine at the cut-off, even though the loss is still coming. A common fix is to search further in "unquiet" positions, such as when captures are pending, before evaluating.

**Revise:** [[artificial-intelligence/04-adversarial-search/02-minimax-1|Minimax 1]], [[artificial-intelligence/04-adversarial-search/03-minimax-2|Minimax 2]], [[artificial-intelligence/04-adversarial-search/04-alpha-beta-pruning-1|Alpha-Beta Pruning 1]].

</details>

## About this paper

Written for the AI subject on 2026-11-26 in the format of the 2025/26 SSG 518 paper ([[artificial-intelligence/mock-exam-1|Mock Exam 1]]): six questions on the same topics, answer any four in 2 hours. The questions are new, not taken from the lessons, the checkpoints or the past papers; the [[artificial-intelligence/question-bank|AI question bank]] has more practice. Every number, trace and diagram is computed and asserted by `scripts/diagrams/ai_mocks.py`, which also draws the three answer pictures. The mark split inside each worked answer is a guide for marking yourself, not an official scheme.
