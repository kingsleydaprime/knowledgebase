---
id: 9de349ed-e3ba-4157-81e5-e66208c6ca7a
---

# Types of Problems and Techniques

AI problems are classified by whether a wrong step can be ignored, undone, or never undone.

## Before you start
<!-- bite: c4d4e9a8-63b5-403b-90af-580ff798e4e2 -->

Read [[artificial-intelligence/01-foundations/05-problem-solving-in-ai|Problem Solving in AI]] first. You need the five parts of a problem and the idea of a state space.

After this lesson you will be able to:

1. name the three types of problem (ignorable, recoverable, irrecoverable), with an example and the characteristics of each;
2. say what kind of control each type needs: none, backtracking, or careful planning;
3. list the five families of problem-solving technique and match a problem to one.

## What the types of problem are
<!-- bite: c1125337-049d-4a23-82f3-2d83d123e29b -->

In the last lesson, every problem looked the same: five parts, then search. But problems behave very differently when you make a mistake.

Take three cases. A maths proof: if you write down a fact you didn't need, no harm done, you just ignore it. The 8-puzzle: if you slide a tile the wrong way, you slide it back. Chess: once you've moved your queen and your opponent has taken it, you can't take that move back.

In AI, problems are classified by exactly this: what their characteristics are and how they affect the problem-solving process. There are three main types.

## The kid version
<!-- bite: ac26da63-22b8-4cf8-a6c3-a80ac1fce226 -->

Think of three ways to write. With a pencil and a huge sheet of paper, a bad sentence doesn't matter, you just write the right one after it. With a pencil and an eraser, you can rub out a mistake and try again. With a pen on your exam script, what you write stays. You'd write carelessly in the first case, try things in the second, and think hard before every word in the third. Problems in AI are the same three kinds.

**Where the analogy stops working.** With a pen you at least know when you've made a mistake. In an irrecoverable AI problem, like a game against an opponent, you often only find out many moves later that an earlier move was the bad one.

## Type 1: ignorable problems
<!-- bite: 58958ea9-8ab7-42c2-b826-c137e9d080a7 -->

**Ignorable problems** are problems where some solution steps can be skipped, ignored or disregarded without affecting the outcome.

The classic example is **proving a theorem**. Suppose you're proving something and you prove a side fact that turns out not to help. You don't have to undo it. You just carry on, and the useless step sits there harmlessly. Your class notes give another: optimisation tasks where some variables have negligible impact, such as tuning a hyperparameter in a machine-learning model that barely changes the result.

**Characteristics:**

1. A simpler problem structure.
2. Fewer computational resources needed.

**Control it needs:** a simple control structure that never has to go back. If a step doesn't help, ignore it and keep going.

## Type 2: recoverable problems
<!-- bite: da68d591-866b-401f-af20-43fd68a358ed -->

**Recoverable problems** are problems where the agent can undo or correct its actions, which gives flexibility in the problem-solving process.

The classic example is the **8-puzzle** from the last lesson. Slide a tile the wrong way, and you can slide it straight back. Every action can be reversed. A route on a map is the same while you're planning it: you can try Benin, decide it's a bad idea, and go back to try Ibadan instead.

**Characteristics:**

1. Actions are reversible.
2. Lower risk than irrecoverable problems.

**Control it needs:** **backtracking**. Try a step; if it leads to a dead end, go back to the last choice and try a different option. Many of the search methods in section 02 work this way.

## Type 3: irrecoverable problems
<!-- bite: 79121700-ce0c-4011-a9e1-3a0f0d8f8758 -->

**Irrecoverable problems** are problems where actions can't be reversed, so the agent has to plan carefully before it acts.

The classic example is **chess**. Once a move is made and your opponent replies, you can't take it back. Your class notes give **autonomous vehicle navigation**: a wrong action at speed can have permanent consequences.

**Characteristics:**

1. High-risk problem solving.
2. Precise execution is needed.

**Control it needs:** careful planning. Look ahead and think through the consequences *before* each action, because you'll have to live with it. Section 04's minimax algorithm does exactly that for games.

## Are games recoverable?
<!-- bite: c8b21381-87cc-4ea8-99ab-96de66cb3e4c -->

One thing to watch. Your class notes give "decision making in game playing, where moves can be adjusted based on the opponent's actions" as a *recoverable* example. You can adjust your *next* move, but you can't undo the *last* one, so the standard classification puts games like chess under irrecoverable. Use chess as the irrecoverable example in the exam.

## Techniques of problem solving, part 1
<!-- bite: b177eb07-6d0f-4064-8b5f-ea01add0f54b -->

Once you know what kind of problem you have, you pick a technique. Your class notes list five families. Here are the first two:

1. **Search algorithms.** Look through the state space for a path to the goal.
   - **Uninformed search** explores without any knowledge of where the goal is. (Section 02.)
   - **Informed search** uses a **heuristic**, a rule of thumb, to guide the search toward the goal and make it faster. (Section 03.)
2. **Constraint satisfaction problems (CSP).** The solution must satisfy a set of constraints, such as a timetable where no lecturer teaches two classes at once.
   - **Backtracking** systematically tries possible solutions and goes back when a constraint is broken.
   - **Constraint propagation** narrows down the possibilities by applying the constraints before trying anything.

## Techniques of problem solving, part 2
<!-- bite: fac9483d-fea2-4d89-9fcb-a08aca435d3d -->

The third family is about finding the best value of something:

3. **Optimisation techniques.** Find the best value of something.
   - **Linear programming** optimises a linear objective subject to linear constraints, such as allocating a factory's resources to maximise profit.
   - **Metaheuristics** are approximate methods for very complex problems, such as genetic algorithms.

## Techniques of problem solving, part 3
<!-- bite: bd286b80-0d38-47c8-a1f2-53dd6d4755ff -->

4. **Machine learning.** Learn how to solve the problem from data or experience.
   - **Supervised learning** learns from labelled data to make predictions.
   - **Reinforcement learning** learns the best behaviour through rewards and penalties.
5. **Natural language processing (NLP).** Process and interpret human language.
   - It's used for **language understanding** in chatbots for customer support and translation tools like Google Translate.

These five aren't separate worlds. A chess program searches (1), a timetable is a constraint problem but is solved by search with backtracking (2), and a genetic algorithm (3) is itself a kind of search. That's why search is the fundamental technique, and why the rest of this subject is built on it.

## Matching problems to techniques
<!-- bite: 57b3f5ea-a206-498c-a2ce-5de077ce3e67 -->

Here's how the pieces fit together, for some problems you've already met:

1. **Route from Lagos to Abuja.** Recoverable while planning. Search, ideally informed search with a heuristic like straight-line distance.
2. **8-puzzle.** Recoverable. Search with backtracking, or informed search.
3. **Exam timetable.** Recoverable. Constraint satisfaction.
4. **Chess.** Irrecoverable, with an opponent. Adversarial search (minimax).
5. **Spam filtering.** Episodic, learned from examples. Machine learning.

## Terms used in this lesson
<!-- bite: 9e4ad28b-937c-40c9-9bff-c79fa318a65b -->

1. **Ignorable problem**: This is a problem where unhelpful solution steps can simply be ignored, such as proving a theorem.
2. **Recoverable problem**: This is a problem where actions can be undone, such as the 8-puzzle.
3. **Irrecoverable problem**: This is a problem where actions can't be undone, such as chess or driving.
4. **Backtracking**: This is going back to the last choice point when a path fails, and trying a different option there.
5. **Heuristic**: This is a rule of thumb that estimates how close a state is to the goal, used to guide search.
6. **CSP (constraint satisfaction problem)**: The letters stand for those three words. It's a problem where the solution must satisfy a set of constraints, such as a timetable.
7. **Metaheuristic**: This is a general, approximate strategy for searching very large spaces, such as a genetic algorithm. It finds good solutions without guaranteeing the best.

## Common pitfalls and traps
<!-- bite: adf84012-7cc4-4d09-b108-96e4bb87b173 -->

- **Calling chess recoverable because you can plan your next move.** Recoverable means you can *undo* an action. In chess you can't, so it's irrecoverable.
- **Forgetting that the type decides the control.** Exam questions often ask not just "what type is it?" but "how should it be solved?". Ignorable needs no backtracking, recoverable uses backtracking, irrecoverable needs planning ahead.
- **Treating the five techniques as unrelated.** CSPs and metaheuristics are both kinds of search. Knowing that helps when a problem seems to fit two families.

## Check your understanding
<!-- bite: 45d04fdc-a2b9-4774-80bd-f7e817cd5726 -->

Try each one before you open the answer.

1. <!-- q: mcq id="015e49b5" -->
   A robot arranges blocks into a tower. If it puts a block in the wrong place, it can lift it off and try again. What type of problem is this?

   - [ ] Ignorable
   - [x] Recoverable
   - [ ] Irrecoverable

   <details><summary>Answer</summary>

   Recoverable: every action can be undone by lifting the block off again. Backtracking is the natural control for it.

   </details>

2. <!-- q: gap id="ef83de6b" answers="ignorable;recoverable;irrecoverable" -->
   Proving a theorem is a classic ___ problem. The 8-puzzle is a classic ___ problem. Chess is a classic ___ problem.

   <details><summary>Answer</summary>

   Ignorable, recoverable, irrecoverable. Useless proof steps can be ignored, puzzle moves can be undone, and chess moves can't.

   </details>

3. <!-- q: mcq id="9a9dd157" -->
   Which control strategy suits an irrecoverable problem best?

   - [ ] No control: just ignore unhelpful steps
   - [ ] Try a step and undo it if it fails
   - [x] Plan ahead and think through consequences before each action
   - [ ] Pick actions at random

   <details><summary>Answer</summary>

   Plan ahead. Actions can't be undone, so you must think through their consequences first. Undoing (backtracking) only works when actions are reversible.

   </details>

4. <!-- q: mcq id="a24986f2" -->
   A university must schedule 40 exams into 10 days so that no student sits two exams at the same time. Which family of technique fits best?

   - [ ] Natural language processing
   - [x] Constraint satisfaction
   - [ ] Supervised learning
   - [ ] Linear programming only

   <details><summary>Answer</summary>

   Constraint satisfaction. The solution must satisfy a set of constraints (no clashes), and it's solved with backtracking and constraint propagation.

   </details>

5. <!-- q: open id="28b75aff" -->
   Your class notes list "games where moves can be adjusted based on the opponent's actions" as a recoverable problem. Explain why chess is normally classified as irrecoverable instead.

   <details><summary>Answer</summary>

   Recoverable means an action can be undone. In chess you can adjust your *next* move in response to the opponent, but you can't take back a move you've already made, and its effects (such as a lost piece) stay. So the actions are irreversible, which makes it irrecoverable, and it needs careful look-ahead before each move.

   </details>

## Before moving on
<!-- bite: f0bee251-1172-4b76-a419-9068fb857ca7 -->

You're done when you can name the three types of problem with an example, characteristics and control strategy for each, and match a new problem to one of the five technique families.

Recap: ignorable problems let you skip unhelpful steps (theorem proving); recoverable problems let you undo steps, so backtracking works (8-puzzle); irrecoverable problems can't be undone, so you plan ahead (chess, driving). The techniques are search (uninformed and informed), constraint satisfaction, optimisation, machine learning and NLP, and search underlies most of them.

That's the end of section 01. Section 02 of the [[artificial-intelligence/index|Artificial Intelligence]] subject is uninformed search: what search is, how to measure a search method, and the six blind search methods, run on our Lagos-to-Abuja map.

## Related
<!-- bite: 30b9caad-19cb-4815-8067-5aa4c0c6fc70 -->

- [[operations-research/index|Operations Research]]: linear programming and optimisation in depth.
- [[machine-learning/index|Machine Learning]]: the learning family of techniques.
- [[dsa/04-patterns/index|DSA Patterns]]: backtracking as a coding pattern.

## About this lesson
<!-- bite: 63a212d5-4af6-4dd4-b89b-cc3840150db1 -->

**Level:** introductory. Lesson 6 of section 01 (foundations). It covers ignorable, recoverable and irrecoverable problems, their characteristics and control strategies, and the five families of problem-solving technique.

**Source:** University of Lagos SSG 518 class notes, *Problem Solving in AI* (09/03/26: types of problem-solving in AI and techniques of problem solving). The theorem-proving, 8-puzzle and chess examples are the standard ones from Rich and Knight's *Artificial Intelligence*, where this classification comes from. One judgement call: the notes' "game playing" example of a recoverable problem is reclassified as irrecoverable, with the reason given in the lesson.
