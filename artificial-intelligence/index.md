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

### Coming next

These sections are planned and being written in this order:

1. **02. Uninformed search**: what search is, how to judge a search method, and the six blind searches: breadth-first, depth-first, depth-limited, iterative deepening, uniform-cost and bidirectional.
2. **03. Heuristic search**: rules of thumb, generate-and-test, greedy best-first search, A\*, and local search (hill climbing, beam search, simulated annealing, genetic algorithms).
3. **04. Adversarial search**: game trees, minimax, and alpha-beta pruning.

After that, the subject grows into the rest of classical AI: constraint satisfaction, logic and knowledge representation, inference, planning, reasoning under uncertainty and expert systems.

## SSG 518 week by week

The University of Lagos SSG 518 course (Artificial Intelligence II) is spread across three subjects. Here's where each week lives:

1. **Week 1, introduction to search methods**: section 02 (and section 03 for heuristic search).
2. **Week 2, self-organising systems**: [[machine-learning/08-other-architectures/04-self-organising-systems-1|Self-Organising Systems 1]] and [[machine-learning/08-other-architectures/05-self-organising-systems-2|Self-Organising Systems 2]].
3. **Week 3, information theory**: the [[information-theory/index|Information Theory]] subject, especially [[information-theory/02-entropy-joint-conditional-and-mutual|Entropy, Joint, Conditional and Mutual Information]].
4. **Week 4, rational decision making**: [[machine-learning/08-other-architectures/06-rational-decision-making-1|Rational Decision Making 1]] and [[machine-learning/08-other-architectures/07-rational-decision-making-2|Rational Decision Making 2]].
5. **Weeks 5–6, pattern recognition**, and **weeks 8–9, parametric and non-parametric classifiers**: planned for the Machine Learning subject's classical ML section, after its classifier lessons.
6. **Week 10, problem solving**: [[artificial-intelligence/01-foundations/05-problem-solving-in-ai|Problem Solving in AI]] and [[artificial-intelligence/01-foundations/06-types-of-problems-and-techniques|Types of Problems and Techniques]]. They come first here, because search depends on them.
7. **Weeks 11–13, minimax, alpha-beta and heuristic approaches to state space search**: sections 03 and 04.

## Related

- [[machine-learning/index|Machine Learning]]: the learning side of AI.
- [[ai-engineering/index|AI Engineering]]: building products on top of today's large language models.
- [[dsa/index|Data Structures and Algorithms]]: graphs, queues, stacks and priority queues, the data structures search is built from.
- [[information-theory/index|Information Theory]]: measuring information and uncertainty, week 3 of SSG 518.

## About this course

**Level:** third/fourth-year undergraduate. Built from the author's University of Lagos materials for **SSG 518 (Artificial Intelligence II)**: the Module 1 slides (*Introduction/History*, following Ben Coppin's *Artificial Intelligence Illuminated*), the *Introduction to Search Methods in AI* slides, and the author's handwritten class notes for 2025/26. The SSG 503 (Artificial Intelligence) notes will feed the later classical-AI sections.

**Order:** the lessons follow a learning order, not the lecture order. Problem solving (week 10) comes before search (week 1), because search uses its terms.

**How it is checked:** every path cost and search result in the lessons is computed and asserted by `scripts/diagrams/artificial_intelligence.py` before any picture is drawn. Run it from the vault root. The Nigeria map's distances are rounded road distances chosen for hand tracing, not survey figures.

**Judgement calls worth knowing:**

1. The class notes' "translation model" is taught as the standard **transition model**.
2. The class notes list game playing as a recoverable problem; lesson 06 classifies chess as irrecoverable, the standard view, and explains why.
3. Two dates from the Module 1 slides are corrected in lesson 03: *Perceptrons* is from 1969, and the 1966 US funding cut followed the ALPAC report.

**Status:** section 01 (6 lessons) written 2026-11-25. Sections 02–04 to follow.
