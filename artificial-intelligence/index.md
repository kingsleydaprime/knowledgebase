# Artificial Intelligence

## What artificial intelligence is

**Artificial intelligence is building computer systems that do things we'd call intelligent if a person did them: finding a route, playing a game, solving a puzzle, making a sensible decision.**

You use it every day without calling it AI. The map app that finds you the fastest way from Lagos to Abuja, the computer opponent in a game of draughts or chess, the program that builds an exam timetable with no clashes: none of these learn from data, and all of them are AI. They work by describing the problem exactly and then searching through the possibilities, smartly enough to find a good answer fast.

That's the side of AI this subject teaches. It's often called **classical AI**: describing problems, searching for solutions, and playing games against an opponent. The other side, where the system learns its rules from examples, is the [[machine-learning/index|Machine Learning]] subject.

## What you'll be able to do

By the end you will be able to:

- say what AI is, how it differs from machine learning, and where it came from;
- describe any agent and the world it works in, and turn a real task into a problem a computer can solve;
- run the main search methods by hand on a map, and say which one to use when;
- use a rule of thumb to make search much faster, and know when it still gives the best answer;
- choose the best move in a two-player game by looking ahead, and skip the parts of the game that can't change the answer.

## Where to start

**Before you start:** nothing beyond school maths. A few lessons use simple sums and the idea of a tree (a diagram that branches). If you've met graphs, queues and stacks in [[dsa/index|Data Structures and Algorithms]], the search lessons will feel familiar, but they explain everything they use.

Read the sections in order. Section 01 sets up the words every later lesson uses. One example runs through the whole subject: a trip from Lagos to Abuja on a small map of seven cities.

### 01. Foundations

1. [[artificial-intelligence/01-foundations/01-what-ai-is|01 — What Artificial Intelligence Is]]: the definition, the two words in the name, symbolic versus learned AI, and the areas of the field.
2. [[artificial-intelligence/01-foundations/02-the-four-approaches-to-ai|02 — The Four Approaches to AI]]: thinking or acting, like a human or rationally; the Turing test; and why we build rational agents.
3. [[artificial-intelligence/01-foundations/03-foundations-and-history-of-ai|03 — Foundations and History of AI]]: the six fields AI borrows from, its history from 1956, its booms and crashes, and its pros and cons.
4. [[artificial-intelligence/01-foundations/04-agents-and-environments|04 — Agents and Environments]]: sensors, actuators and the agent loop; describing a task; the kinds of world an agent can live in.
5. [[artificial-intelligence/01-foundations/05-problem-solving-in-ai|05 — Problem Solving in AI]]: the five steps, and the five parts every problem needs, on the Lagos-to-Abuja map.
6. [[artificial-intelligence/01-foundations/06-types-of-problems-and-techniques|06 — Types of Problems and Techniques]]: problems you can ignore, undo or never undo, and the families of technique that solve them.

### 02. Uninformed search

7. [[artificial-intelligence/02-uninformed-search/01-what-search-is|01 — What Search Is]]: search trees, the frontier, and searching forward from the data or backward from the goal.
8. [[artificial-intelligence/02-uninformed-search/02-measuring-a-search-method|02 — Measuring a Search Method]]: the four questions for judging any search, and why the tree grows so fast.
9. [[artificial-intelligence/02-uninformed-search/03-breadth-first-search|03 — Breadth-First Search]]: level by level with a queue; finds the fewest steps but uses a lot of memory.
10. [[artificial-intelligence/02-uninformed-search/04-depth-first-search|04 — Depth-First Search]]: one path as deep as it goes, then back up; tiny memory, no guarantees.
11. [[artificial-intelligence/02-uninformed-search/05-depth-limited-search|05 — Depth-Limited Search]]: depth-first with a maximum depth, and its two ways of failing.
12. [[artificial-intelligence/02-uninformed-search/06-iterative-deepening-search|06 — Iterative Deepening Search]]: deeper and deeper limits; the best of breadth-first and depth-first.
13. [[artificial-intelligence/02-uninformed-search/07-uniform-cost-search-1|07 — Uniform-Cost Search 1: The Cheapest Path First]]: always extend the cheapest path, traced on the graph from the class notes.
14. [[artificial-intelligence/02-uninformed-search/08-uniform-cost-search-2|08 — Uniform-Cost Search 2: The Road Trip and When to Stop]]: the 790 km route, and why the goal test waits.
15. [[artificial-intelligence/02-uninformed-search/09-bidirectional-search|09 — Bidirectional Search]]: search from both ends and meet in the middle.
16. [[artificial-intelligence/02-uninformed-search/10-comparing-uninformed-search|10 — Comparing Uninformed Search Methods]]: all six side by side, and how to choose.

### 03. Heuristic search

17. [[artificial-intelligence/03-heuristic-search/01-heuristics-and-heuristic-search|01 — Heuristics and Heuristic Search]]: what a heuristic is, straight-line distance, and trading guarantees for speed.
18. [[artificial-intelligence/03-heuristic-search/02-generate-and-test|02 — Generate and Test]]: guess, check, guess again, and why a smart generator matters.
19. [[artificial-intelligence/03-heuristic-search/03-greedy-best-first-search|03 — Greedy Best-First Search]]: always head for whatever looks closest; fast but not optimal.
20. [[artificial-intelligence/03-heuristic-search/04-a-star-search-1|04 — A\* Search 1: Cost So Far Plus Estimate to Go]]: the method that adds both, traced on the course slides' graph.
21. [[artificial-intelligence/03-heuristic-search/05-a-star-search-2|05 — A\* Search 2: The Road Trip and When A\* Is Optimal]]: the 790 km route, and the rule that makes A\* trustworthy.
22. [[artificial-intelligence/03-heuristic-search/06-heuristics-for-the-8-puzzle|06 — Heuristics for the 8-Puzzle]]: inventing good estimates for a puzzle, and how much a better one saves.
23. [[artificial-intelligence/03-heuristic-search/07-hill-climbing|07 — Hill Climbing]]: always step uphill, and the three places it gets stuck.
24. [[artificial-intelligence/03-heuristic-search/08-beam-search|08 — Beam Search]]: keep only the few most promising states at each level.
25. [[artificial-intelligence/03-heuristic-search/09-simulated-annealing|09 — Simulated Annealing]]: sometimes step downhill on purpose, less and less as things cool.
26. [[artificial-intelligence/03-heuristic-search/10-genetic-algorithms|10 — Genetic Algorithms]]: evolve a population of solutions, and how to choose among this section's methods.

### 04. Adversarial search

27. [[artificial-intelligence/04-adversarial-search/01-games-as-search|01 — Games as Search]]: what changes when someone is playing against you, and how big game trees get.
28. [[artificial-intelligence/04-adversarial-search/02-minimax-1|02 — Minimax 1: Choosing the Best Move]]: pick the move whose worst case is best, worked on the class-notes tree.
29. [[artificial-intelligence/04-adversarial-search/03-minimax-2|03 — Minimax 2: Cost, Cut-offs and Evaluation Functions]]: solving tic-tac-toe, and estimating positions when the tree is too big.
30. [[artificial-intelligence/04-adversarial-search/04-alpha-beta-pruning-1|04 — Alpha-Beta Pruning 1: Skipping What Can't Matter]]: alpha, beta and the pruning rule, traced step by step.
31. [[artificial-intelligence/04-adversarial-search/05-alpha-beta-pruning-2|05 — Alpha-Beta Pruning 2: Move Ordering and How Much It Saves]]: why the order of moves decides the saving, and searching twice as deep.

### Coming later

Everything SSG 518 covers in this subject is now written. The subject will grow into the rest of classical AI: constraint satisfaction, logic and knowledge representation, inference, planning, reasoning under uncertainty and expert systems.

## Practise with past papers

When you've finished a section, try its questions in the [[artificial-intelligence/ssg-518-question-bank|SSG 518 question bank]]: the full 2025/2026 SSG 518 exam and the questions that keep coming back in the older SSG 503 papers, every one solved step by step.

## SSG 518 week by week

The University of Lagos SSG 518 course (Artificial Intelligence II) is spread across three subjects. Here's where each week lives:

1. **Week 1, introduction to search methods**: [[artificial-intelligence/02-uninformed-search/index|Uninformed Search]] and [[artificial-intelligence/03-heuristic-search/index|Heuristic Search]].
2. **Week 2, self-organising systems**: [[machine-learning/08-other-architectures/04-self-organising-systems-1|Self-Organising Systems 1]] and [[machine-learning/08-other-architectures/05-self-organising-systems-2|Self-Organising Systems 2]].
3. **Week 3, information theory**: the [[information-theory/index|Information Theory]] subject, especially [[information-theory/02-entropy-joint-conditional-and-mutual|Entropy, Joint, Conditional and Mutual Information]].
4. **Week 4, rational decision making**: [[machine-learning/08-other-architectures/06-rational-decision-making-1|Rational Decision Making 1]] and [[machine-learning/08-other-architectures/07-rational-decision-making-2|Rational Decision Making 2]].
5. **Weeks 5–6, pattern recognition**: [[machine-learning/03-classical-ml/21-pattern-recognition-1|Pattern Recognition 1]] and [[machine-learning/03-classical-ml/22-pattern-recognition-2|Pattern Recognition 2]]. **Weeks 8–9, parametric and non-parametric classifiers**: [[machine-learning/03-classical-ml/23-parametric-and-non-parametric-classifiers-1|Parametric and Non-Parametric Classifiers 1]] and [[machine-learning/03-classical-ml/24-parametric-and-non-parametric-classifiers-2|Parametric and Non-Parametric Classifiers 2]]. All four are in the Machine Learning subject, after its other classifier lessons.
6. **Week 10, problem solving**: [[artificial-intelligence/01-foundations/05-problem-solving-in-ai|Problem Solving in AI]] and [[artificial-intelligence/01-foundations/06-types-of-problems-and-techniques|Types of Problems and Techniques]]. They come first here, because search depends on them.
7. **Weeks 11–13, minimax, alpha-beta and heuristic approaches to state space search**: [[artificial-intelligence/03-heuristic-search/index|Heuristic Search]] for the heuristic approaches, and [[artificial-intelligence/04-adversarial-search/index|Adversarial Search]] for minimax and alpha-beta.

## Related

- [[machine-learning/index|Machine Learning]]: the learning side of AI.
- [[ai-engineering/index|AI Engineering]]: building products on top of today's large language models.
- [[dsa/index|Data Structures and Algorithms]]: graphs, queues, stacks and priority queues, the data structures search is built from.
- [[information-theory/index|Information Theory]]: measuring information and uncertainty, week 3 of SSG 518.

## About this course

**Level:** third/fourth-year undergraduate. Built from the author's University of Lagos materials for **SSG 518 (Artificial Intelligence II)**: the Module 1 slides (*Introduction/History*, following Ben Coppin's *Artificial Intelligence Illuminated*), the *Introduction to Search Methods in AI* slides, and the author's handwritten class notes for 2025/26. The SSG 503 (Artificial Intelligence) notes will feed the later classical-AI sections.

**Order:** the lessons follow a learning order, not the lecture order. Problem solving (week 10) comes before search (week 1), because search uses its terms.

**How it is checked:** every path cost and search result in the lessons is computed and asserted before any picture is drawn: `scripts/diagrams/artificial_intelligence.py` (the map and section 01) `scripts/diagrams/ai_search.py` (section 02, which implements all six uninformed methods) `scripts/diagrams/ai_heuristic.py` (section 03: greedy search, A\*, beam search, hill climbing, annealing, a genetic algorithm and an 8-puzzle solver) and `scripts/diagrams/ai_games.py` (section 04: minimax, alpha-beta and a tic-tac-toe solver). Every quiz answer with a number is asserted too. The Python examples in the lessons were run and their printed output is copied exactly. Run it from the vault root. The Nigeria map's distances are rounded road distances chosen for hand tracing, not survey figures.

**Trace conventions:** neighbours are tried in alphabetical order; breadth-first search tests for the goal when a node is generated, uniform-cost search when it is taken off the frontier; depth-limited search skips states already on the current path.

**Judgement calls worth knowing:**

1. The class notes' "translation model" is taught as the standard **transition model**.
2. The class notes list game playing as a recoverable problem; lesson 06 classifies chess as irrecoverable, the standard view, and explains why.
3. The A\* example graph is read from the edge labels on the *Introduction to Search* slide; taking B–C as the cost-1 edge reproduces every number in the slide's comparison table.
4. The class notes' minimax step 4 names the minimising player at the root; lesson 04-02 corrects this to the maximising player, as in the notes' own example.
5. The straight-line distances to Abuja are rounded and chosen to be admissible and consistent on the lesson map; the script checks both.
6. Two dates from the Module 1 slides are corrected in lesson 03: *Perceptrons* is from 1969, and the 1966 US funding cut followed the ALPAC report.

**Status:** sections 01–04 (31 lessons) written 2026-11-25, covering all of SSG 518's AI topics; the question bank, from the 2025/26 SSG 518 paper and six SSG 503 papers, added 2026-11-26 and checked by `scripts/diagrams/ai_question_bank.py`. The wider classical-AI sections, using the SSG 503 notes, come later.
