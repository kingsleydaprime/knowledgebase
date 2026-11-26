---
id: 8eeea8e8-3c99-4940-aaad-059993f063d7
kind: checkpoint
minutes: 60
---

# AI Checkpoint 1: Foundations

A 1-hour test on everything in section 01, Foundations: what AI is, the ways of knowing, the four approaches, the history, agents, problem solving, the types of problem, and combinatorial explosion. Take it when you've finished lesson 08, before you start search.

**Instructions:** answer **all 20 questions**. The paper is out of 65 marks. Time allowed: **1 hour**; you can pause it. Have paper, a pen and a calculator ready. The short questions are marked for you; for the longer ones, write your answer on paper, then mark yourself against the worked answer after you submit. All the questions use fresh examples, so you apply what you learned rather than remember the lessons' own examples.

## Question 1
<!-- q: mcq id="d5f74fd5" marks="2" -->

A program is told "Ada has 2 goats and 3 cows" and answers "Ada has 5 animals". Simple adding can't do this, because goats and cows aren't the same thing. Which way of knowing did the program use? (2 marks)

- [ ] Recall
- [ ] Calculation
- [x] Reasoning
- [ ] Perception

<details><summary>Solution</summary>

**Reasoning.** It used the concept "animal" to treat goats and cows as the same kind of thing, then counted. Working with concepts (symbols) to reach a conclusion nobody wrote down is reasoning, the way of knowing that demands intelligence. Recall only fetches stored facts, and calculation only manipulates numbers.

**Revise:** [[artificial-intelligence/01-foundations/02-ways-of-knowing|Ways of Knowing]].

</details>

## Question 2
<!-- q: gap id="fc2106de" marks="3" answers="data;information;knowledge" -->

A farm sensor sends three messages. Name the step of the data–knowledge continuum each one is. (3 marks)

"Soil moisture: 12%" is ___. "The maize field is dry" is ___. "A dry maize field in March means irrigate tonight" is ___.

<details><summary>Solution</summary>

1. **Data**: a raw figure, with no meaning attached.
2. **Information**: processed data, the figure turned into a statement about the field.
3. **Knowledge**: applied information, the information plus a rule for what to do about it.

**Revise:** [[artificial-intelligence/01-foundations/02-ways-of-knowing|Ways of Knowing]].

</details>

## Question 3
<!-- q: mcq id="6c83878e" marks="2" -->

A draughts program looks ahead at every possible move and picks the best one. It never learns from games it has played. Which statement is true? (2 marks)

- [ ] It isn't AI, because it doesn't learn.
- [x] It is AI, but not machine learning.
- [ ] It is machine learning, but not AI.
- [ ] It is deep learning, because it searches deeply.

<details><summary>Solution</summary>

**It is AI, but not machine learning.** AI is the big box; machine learning is one way of filling it. A program that searches ahead to choose a move is symbolic, classical AI: it works out what to do without learning anything from data.

**Revise:** [[artificial-intelligence/01-foundations/01-what-ai-is|What Artificial Intelligence Is]].

</details>

## Question 4
<!-- q: mcq id="6e974978" marks="2" -->

Researchers build a program that solves logic puzzles. They count it a success when it takes the same steps and makes the same mistakes as human volunteers on the same puzzles, even when that means it gets some puzzles wrong. Which approach to AI is this? (2 marks)

- [ ] Acting like humans
- [x] Thinking like humans
- [ ] Thinking rationally
- [ ] Acting rationally

<details><summary>Solution</summary>

**Thinking like humans**, also called cognitive modelling. It judges the program by its *process* (the steps inside), compared with humans, not by whether its answers are correct. Acting like humans would only care whether the answers pass for human; the two rational approaches would want the correct answer.

**Revise:** [[artificial-intelligence/01-foundations/03-the-four-approaches-to-ai|The Four Approaches to AI]].

</details>

## Question 5
<!-- q: mcq id="62f47301" marks="2" -->

The *total* Turing test lets the examiner test seeing and handling objects as well as conversation. Which abilities does a machine need for the total test that it does **not** need for the ordinary Turing test? Choose all that apply. (2 marks)

- [ ] Natural language processing
- [ ] Knowledge representation
- [x] Computer vision
- [x] Robotics
- [ ] Machine learning

<details><summary>Solution</summary>

**Computer vision and robotics.** The ordinary test needs four: natural language processing, knowledge representation, automated reasoning and machine learning. The total test adds a camera and a hand, so it also needs vision to perceive objects and robotics to move them.

**Revise:** [[artificial-intelligence/01-foundations/03-the-four-approaches-to-ai|The Four Approaches to AI]].

</details>

## Question 6
<!-- q: gap id="d688ef7d" marks="3" answers="Dartmouth;1956;McCarthy" -->

Complete the sentence. (3 marks)

Most histories date the birth of AI to the summer workshop at ___ in the year ___, organised by John ___, who coined the name "artificial intelligence".

<details><summary>Solution</summary>

**Dartmouth, 1956, McCarthy.** Marvin Minsky, Herbert Simon, Allen Newell and Arthur Samuel were also there. The other key date is 1950, Turing's paper proposing the Turing test.

**Revise:** [[artificial-intelligence/01-foundations/04-foundations-and-history-of-ai|Foundations and History of AI]].

</details>

## Question 7
<!-- q: mcq id="983d2cf0" marks="2" -->

In 1973 a report told the UK government that AI had not delivered what it promised, and AI funding in the UK was cut hard. What was that report? (2 marks)

- [ ] The ALPAC report
- [x] The Lighthill report
- [ ] *Perceptrons*
- [ ] The Dartmouth proposal

<details><summary>Solution</summary>

**The Lighthill report.** The ALPAC report (1966) ended US funding for machine translation, and *Perceptrons* (Minsky and Papert, 1969) is a book that slowed neural-network research. All three are AI winters, and the course's lesson from them is the same: don't claim too much for your discipline.

**Revise:** [[artificial-intelligence/01-foundations/04-foundations-and-history-of-ai|Foundations and History of AI]].

</details>

## Question 8
<!-- q: mcq id="5221bd6c" marks="2" -->

A security light switches on whenever its sensor detects movement, and switches off 30 seconds after the movement stops. It has no goal and never looks ahead. What kind of agent is it? (2 marks)

- [x] A simple reflex agent
- [ ] A goal-based agent
- [ ] A utility-based agent
- [ ] A learning agent

<details><summary>Solution</summary>

**A simple reflex agent.** It acts on the current percept with a condition–action rule: "if movement, then light on". A goal-based agent would look ahead through sequences of actions to reach a goal, which the light never does.

**Revise:** [[artificial-intelligence/01-foundations/05-agents-and-environments|Agents and Environments]].

</details>

## Question 9
<!-- q: mcq id="c255bd28" marks="2" -->

A route-planning agent is described two ways. (A) "Given everything the user has typed and every location the phone has reported, return the cheapest route." (B) The 40,000 lines of code on the phone that work that route out. Which statement is right? (2 marks)

- [ ] (A) is the agent program and (B) is the agent function.
- [x] (A) is the agent function and (B) is the agent program.
- [ ] Both are the agent function.
- [ ] Both are the agent program.

<details><summary>Solution</summary>

**(A) is the agent function and (B) is the agent program.** The agent function is the mathematical mapping from percept sequences to actions, $f: P^* \rightarrow A$. The agent program is the code, running on a real machine, that computes it. The function can be easy to state and still expensive to compute.

**Revise:** [[artificial-intelligence/01-foundations/05-agents-and-environments|Agents and Environments]].

</details>

## Question 10
<!-- q: gap id="7e4a1be3" marks="4" answers="fully|fully observable;deterministic;sequential;multi-agent|multi|multiagent|multi agent|two-agent|two agent" -->

A program plays ayo against a person. Both players can see every seed on the board, a move always sows the seeds the same way, and each move changes the moves available later. Classify its environment. (4 marks)

Observable: ___. Deterministic or stochastic: ___. Episodic or sequential: ___. Single-agent or multi-agent: ___.

<details><summary>Solution</summary>

1. **Fully observable**: the whole board is visible.
2. **Deterministic**: the same move from the same position always gives the same result. There are no dice.
3. **Sequential**: each move changes what's possible later.
4. **Multi-agent**: two players, working against each other.

It's also static (the board waits while you think, unless there's a clock) and discrete (a countable number of positions and moves).

**Revise:** [[artificial-intelligence/01-foundations/05-agents-and-environments|Agents and Environments]].

</details>

## Question 11
<!-- q: open id="11d6154b" marks="5" -->

A drone delivers blood and medicine from a hospital in Ibadan to village clinics up to 60 km away. Describe its task with PEAS, giving at least two items for each letter. Then name one pair of goals in your performance measure that pull against each other. (5 marks)

<details><summary>Solution</summary>

One mark for each letter, one for the conflict. A good answer:

1. **Performance measure**: delivery arrives on time; package arrives intact and at the right temperature; no crashes or injuries; low battery use; stays out of restricted airspace.
2. **Environment**: the sky and weather (wind, rain), trees, power lines, buildings, birds, other aircraft, the hospital and clinic landing pads.
3. **Actuators**: rotors and motors, the package-release mechanism, lights, a speaker or radio to warn people.
4. **Sensors**: GPS, cameras, altimeter, airspeed and wind sensors, battery gauge, obstacle-distance sensors, a temperature sensor in the box.

**Conflict (1 mark):** speed against safety (flying fast in strong wind risks a crash), or speed against battery (flying faster drains the battery, so it may not make the return trip).

**Revise:** [[artificial-intelligence/01-foundations/05-agents-and-environments|Agents and Environments]].

</details>

## Question 12
<!-- q: open id="03fce8ae" marks="6" -->

You have a 4-litre jug and a 3-litre jug, a tap, and no markings on either jug. You can fill a jug from the tap, empty a jug onto the ground, or pour one jug into the other until the first is empty or the second is full. You need exactly 2 litres in the 4-litre jug.

Formulate this as a problem: give the initial state, actions, transition model, goal test and path cost. Then give a sequence of actions that solves it. (6 marks)

<details><summary>Solution</summary>

**Formulation (1 mark each).**

1. **State**: a pair $(a, b)$, the litres in the 4-litre jug and the 3-litre jug. **Initial state**: $(0, 0)$, both empty.
2. **Actions**: fill the 4-litre jug; fill the 3-litre jug; empty either jug; pour the 4-litre into the 3-litre; pour the 3-litre into the 4-litre.
3. **Transition model**: filling sets that jug to its capacity; emptying sets it to 0; pouring from $a$ into $b$ moves $\min(a, 3 - b)$ litres, and pouring from $b$ into $a$ moves $\min(b, 4 - a)$.
4. **Goal test**: $a = 2$ (the 3-litre jug can hold anything).
5. **Path cost**: 1 per action, so the cost is the number of actions.

**A solution (1 mark): 6 actions, the fewest possible.**

| Action | State $(a, b)$ |
|---|---|
| Start | (0, 0) |
| Fill the 3-litre jug | (0, 3) |
| Pour the 3-litre into the 4-litre | (3, 0) |
| Fill the 3-litre jug | (3, 3) |
| Pour the 3-litre into the 4-litre | (4, 2) |
| Empty the 4-litre jug | (0, 2) |
| Pour the 3-litre into the 4-litre | (2, 0) |

Another 6-action solution also works: fill the 4-litre, pour into the 3-litre (1, 3), empty the 3-litre (1, 0), pour (0, 1), fill the 4-litre (4, 1), pour into the 3-litre (2, 3). Any correct sequence earns the mark; a longer one is still a solution, just not the cheapest.

**Revise:** [[artificial-intelligence/02-uninformed-search/12-water-jugs-and-tower-of-hanoi|Water Jugs and the Tower of Hanoi]], [[artificial-intelligence/01-foundations/06-problem-solving-in-ai|Problem Solving in AI]].

</details>

## Question 13

The table gives road distances in km between towns in the south-east. The distances are made up for this question. Every road can be driven both ways, and the initial state is Enugu; the goal is Port Harcourt.

| Road | km |
|---|---|
| Enugu – Awka | 60 |
| Enugu – Okigwe | 80 |
| Awka – Onitsha | 45 |
| Awka – Owerri | 110 |
| Okigwe – Owerri | 55 |
| Okigwe – Aba | 120 |
| Onitsha – Owerri | 100 |
| Owerri – Port Harcourt | 95 |
| Owerri – Aba | 30 |
| Aba – Port Harcourt | 60 |

### (a) Cost of a path
<!-- q: exact id="f0531cbb" marks="2" answer="265" accept="265 km|265km" -->

What is the path cost of Enugu → Awka → Owerri → Port Harcourt, in km? (2 marks)

<details><summary>Solution</summary>

$60 + 110 + 95 = 265$ km.

</details>

### (b) The optimal solution
<!-- q: mcq id="08f2fe2f" marks="2" -->

Which of these routes is the optimal solution? (2 marks)

- [ ] Enugu → Okigwe → Owerri → Port Harcourt
- [ ] Enugu → Okigwe → Aba → Port Harcourt
- [x] Enugu → Okigwe → Owerri → Aba → Port Harcourt
- [ ] Enugu → Awka → Onitsha → Owerri → Port Harcourt

<details><summary>Solution</summary>

Cost each one: $80 + 55 + 95 = 230$; $80 + 120 + 60 = 260$; $80 + 55 + 30 + 60 = 225$; $60 + 45 + 100 + 95 = 300$. **Enugu → Okigwe → Owerri → Aba → Port Harcourt, 225 km**, is the cheapest of every route on the map, so it's optimal.

</details>

### (c) Fewest roads versus cheapest
<!-- q: open id="4ea70cd5" marks="2" -->

The optimal route uses 4 roads, but some routes reach Port Harcourt in 3. A friend says "fewer roads means a shorter trip". Use this map to explain why they're wrong. (2 marks)

<details><summary>Solution</summary>

The cheapest 3-road route, Enugu → Okigwe → Owerri → Port Harcourt, is 230 km. The 4-road route through Aba is 225 km, 5 km shorter, because the Owerri–Aba and Aba–Port Harcourt roads (30 + 60 = 90 km) together are shorter than the single Owerri–Port Harcourt road (95 km). Path cost adds up distances, not roads, so the fewest steps and the lowest cost are different questions, and a search method built for one can give the wrong answer to the other.

**Revise:** [[artificial-intelligence/01-foundations/06-problem-solving-in-ai|Problem Solving in AI]].

</details>

## Question 14
<!-- q: gap id="e12e5bd0" marks="3" answers="ignorable;recoverable;irrecoverable" -->

Classify each problem as ignorable, recoverable or irrecoverable. (3 marks)

Proving a theorem, where a lemma that turns out to be useless can just be left in the proof, is ___. Solving a Sudoku in pencil with an eraser is ___. Making the first cut in a surgical operation is ___.

<details><summary>Solution</summary>

1. **Ignorable**: a useless step can be skipped or left alone without affecting the outcome. It needs only a simple control structure.
2. **Recoverable**: a wrong number can be rubbed out, so it needs backtracking.
3. **Irrecoverable**: a cut can't be undone, so it needs careful planning before acting.

**Revise:** [[artificial-intelligence/01-foundations/07-types-of-problems-and-techniques|Types of Problems and Techniques]].

</details>

## Question 15
<!-- q: mcq id="75f53e29" marks="2" -->

A league must schedule 40 football matches across 4 pitches and 3 weekends, so that no team plays twice on the same day and no pitch has two matches at once. Which family of techniques fits this problem best? (2 marks)

- [ ] Adversarial search
- [x] Constraint satisfaction
- [ ] Supervised learning
- [ ] Natural language processing

<details><summary>Solution</summary>

**Constraint satisfaction.** The solution is an assignment of a pitch and a time to each match that satisfies a set of constraints, exactly like an exam timetable. It's solved by backtracking, and by constraint propagation to cut the options before trying them.

**Revise:** [[artificial-intelligence/01-foundations/07-types-of-problems-and-techniques|Types of Problems and Techniques]].

</details>

## Question 16
<!-- q: exact id="4eccbd66" marks="2" answer="1024" accept="1,024|4^5" -->

A control panel has 5 switches, and each switch can be set to one of 4 positions. How many different settings does the panel have? (2 marks)

<details><summary>Solution</summary>

Each switch multiplies the count by 4: $z^n = 4^5 = 1{,}024$. The number of switches sits in the exponent, so each extra switch multiplies the work by 4 instead of adding to it. That's combinatorial explosion.

**Revise:** [[artificial-intelligence/01-foundations/08-combinatorial-explosion|Combinatorial Explosion]].

</details>

## Question 17

A board game gives the player at most 4 possible moves on every turn. A program for it looks 8 moves ahead and checks 1,000 positions a second.

### (a) Positions at the bottom of the tree
<!-- q: exact id="0c45cd2b" marks="2" answer="65536" accept="65,536|4^8" -->

In the worst case, how many positions are at the bottom of the game tree? (2 marks)

<details><summary>Solution</summary>

$b^m = 4^8 = 65{,}536$ positions.

</details>

### (b) Time to check them
<!-- q: exact id="6ee04638" marks="1" answer="65.536" sigfigs="3" -->

How many seconds does the program take to check all of them? (1 mark)

<details><summary>Solution</summary>

$65{,}536 \div 1{,}000 = 65.5$ seconds, just over a minute.

</details>

### (c) The saving from a heuristic
<!-- q: exact id="a2279b63" marks="2" answer="9.98872" sigfigs="3" -->

A rule of thumb rules out 1 of the 4 moves on every turn, so the program only explores 3. How many times fewer positions does it check, looking 8 moves ahead? (2 marks)

<details><summary>Solution</summary>

$3^8 = 6{,}561$ positions instead of 65,536, so $65{,}536 \div 6{,}561 = 9.99$, about **10 times fewer**. Cutting one move per turn compounds over all 8 levels, because every pruned move removes a whole subtree.

**Revise:** [[artificial-intelligence/01-foundations/08-combinatorial-explosion|Combinatorial Explosion]].

</details>

## Question 18

Two programs each solve the largest problem they can in one hour. Program X does $n^2$ steps and manages $n = 1{,}000$. Program Y does $2^n$ steps and manages $n = 30$. Both are moved to a computer **1,024 times faster** and given an hour again.

### (a) The exponential program
<!-- q: exact id="b752555f" marks="2" answer="40" -->

What is the largest $n$ program Y can now handle? (2 marks)

<details><summary>Solution</summary>

It can now do $1{,}024 \times 2^{30} = 2^{10} \times 2^{30} = 2^{40}$ steps, so $n = 40$. A thousand times more computing power bought only 10 more.

</details>

### (b) The quadratic program
<!-- q: exact id="95beeda2" marks="2" answer="32000" accept="32,000" -->

What is the largest $n$ program X can now handle? (2 marks)

<details><summary>Solution</summary>

It can now do $1{,}024 \times 1{,}000^2$ steps, so $n^2 = 1{,}024 \times 1{,}000^2$ and $n = 32 \times 1{,}000 = 32{,}000$: 32 times bigger. Compare with (a): that's the tyranny of combinatorial explosion. Faster hardware helps a polynomial method a lot and an exponential method hardly at all.

**Revise:** [[artificial-intelligence/01-foundations/08-combinatorial-explosion|Combinatorial Explosion]].

</details>

## Question 19
<!-- q: open id="900c67d7" marks="4" -->

A draughts program has 10 seconds per move. In a typical position only 3 or 4 moves are sensible, but in some positions as many as 12 are legal. Explain why its designer must plan for the worst case, not the typical one. (4 marks)

<details><summary>Solution</summary>

1. **The clock applies on every move (1 mark).** The program must answer within 10 seconds in *every* position, not on average.
2. **The tree grows as $b^m$ (1 mark).** With 12 moves instead of 4, looking $m$ moves ahead costs $12^m$ instead of $4^m$ positions, $3^m$ times more, so a search depth that fits easily in a typical position can blow far past 10 seconds in a wide one.
3. **The hard positions are the important ones (1 mark).** Positions with many options are usually the sharp, critical ones, so running out of time there costs the game.
4. **So (1 mark):** the worst case is the guarantee and the average is only a hope. The designer sets the search depth, or a time cut-off, so that even the widest position finishes in time.

**Revise:** [[artificial-intelligence/01-foundations/08-combinatorial-explosion|Combinatorial Explosion]].

</details>

## Question 20
<!-- q: open id="0c45cd2c" marks="4" -->

Problems that demand intelligence usually have to be solved by search, but combinatorial explosion means a full search is often impossible. Give four things that are done to make search workable, with one line on each. (4 marks)

<details><summary>Solution</summary>

One mark each:

1. **Use heuristics**: rules of thumb that explore the most promising states first, so most of the space is never visited.
2. **Prune**: cut off branches that can't lead to a better answer, as alpha-beta does in games.
3. **Formulate the problem well**: abstraction throws away details that don't matter, so the state space is as small as possible.
4. **Accept a good answer instead of the best one**: local search methods, such as hill climbing, find a good solution fast when the perfect one would take too long.

**Revise:** [[artificial-intelligence/01-foundations/08-combinatorial-explosion|Combinatorial Explosion]].

</details>

## About this checkpoint

Written for the AI subject on 2026-11-26 from the section 01 lessons. The questions are new, not taken from the lessons' quizzes or the past papers; the [[artificial-intelligence/question-bank|AI question bank]] has more practice for this section. Every number in the questions and answers (the jug puzzle, the map, the counts and timings) is computed and asserted by `scripts/diagrams/ai_checkpoints.py`. The south-east road distances are made up for the question, not real figures.
