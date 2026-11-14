# Operations Research

## What operations research is

**Operations research is using maths to make the best decision when you have limited money, time, people or materials.**

A bakery has so much flour, sugar and oven time. Which cakes should it make to earn the most? A delivery company has 20 vans and 400 parcels. Which van takes which parcels, in what order, so the total driving is shortest? A call centre needs enough staff to answer within a minute, without paying for people sitting idle. These are operations research problems.

The method is always the same: write the decision down as unknowns (how many of each cake), a goal (most profit), and limits (only so much flour). The shape of what you've written tells you which method can solve it, and a solver program finds the best answer, or one that's provably close. Airlines, delivery firms, factories, hospitals and cloud services all run on it. Most of the skill is in writing the problem down correctly.

## What you'll be able to do

By the end you will be able to:
- turn a real decision into a model a computer can solve;
- solve linear programs, and explain what the answer means and how far to trust it;
- find shortest routes, maximum flows and best assignments;
- handle yes/no decisions, like "open this warehouse or not";
- break a decision over time into stages and solve it step by step;
- get good answers quickly when the best answer would take too long;
- work out waiting times in queues, the right stock levels, and use simulation when the maths gets too hard.

## Where to start

**Before you start:** school algebra (straight lines, simultaneous equations), basic probability (averages and chances), and enough Python to run a script. Notes 09 and 13 also need [[mathematics/06-calculus/04-calculus-3/01-partial-derivatives|derivatives]], and [[mathematics/04-linear-algebra/index|linear algebra]] helps from note 03.

**Tools:** Python with SciPy (`uv` or `pip install scipy`). It includes a free, professional-grade solver, so nothing here needs a paid licence.

Notes 02–05 build strictly in order. After that, each note lists what it needs, so you can choose. Read 12 before 14.

**You don't have to read all 14.** After note 02 you can already solve real problems. After 05 you know linear programming properly. After 07 you can model most scheduling, routing and planning problems. And note 12 on its own is the most useful one for a software engineer.

### Getting oriented

1. [[operations-research/01-what-operations-research-is|What Operations Research Is]]: unknowns, goals and limits, the steps of a project, and a map of the field.

### Linear programming

2. [[operations-research/02-formulating-linear-programs|Formulating Linear Programs]]: the note that matters most. Writing a decision as a linear program, five common patterns, and your first solver run.
3. [[operations-research/03-the-geometry-of-linear-programs|The Geometry of Linear Programs]]: why the best answer is always at a corner of the allowed region, drawn as a picture.
4. [[operations-research/04-the-simplex-method|The Simplex Method]]: the classic method that walks from corner to corner, worked by hand and then in sixty lines of Python.
5. [[operations-research/05-duality-and-sensitivity|Duality and Sensitivity]]: what one more unit of each resource is worth, and how far that answer can be trusted if the numbers change.

### Other kinds of decision

6. [[operations-research/06-network-models|Network Models]]: shortest routes, maximum flow, matching people to jobs, shipping goods, and project scheduling.
7. [[operations-research/07-integer-programming|Integer Programming]]: decisions that must be whole numbers or yes/no, why rounding doesn't work, and how solvers search.
8. [[operations-research/08-dynamic-programming|Dynamic Programming]]: decisions made in stages over time, solved by working backwards.
9. [[operations-research/09-nonlinear-optimisation|Nonlinear Optimisation]]: when the goal or limits curve, with an example of choosing a low-risk investment mix.
10. [[operations-research/10-heuristics-and-metaheuristics|Heuristics and Metaheuristics]]: quick methods that find good answers to problems too big to solve exactly, and how to judge them honestly.

### Uncertainty

11. [[operations-research/11-decision-analysis-and-game-theory|Decision Analysis and Game Theory]]: decision trees, what extra information is worth, attitudes to risk, and games against an opponent.
12. [[operations-research/12-queueing-theory|Queueing Theory]]: waiting in line, maths version. Why waiting times explode as a system gets close to full, and why one shared queue beats several.
13. [[operations-research/13-inventory-models|Inventory Models]]: how much stock to order and when, and how much spare to keep.
14. [[operations-research/14-simulation|Simulation]]: running thousands of random trials on a computer when the maths is too hard, and checking the results against theory.

## Practice

- [[operations-research/projects|Projects]]: hands-on tasks with a clear "done when".

## Key ideas to remember

1. **Write each unknown in words, with units, before any maths.** Most mistakes are caught here. → [[operations-research/02-formulating-linear-programs|02]]
2. **For a linear program, the best answer is always at a corner.** → [[operations-research/03-the-geometry-of-linear-programs|03]]
3. **Rounding a fractional answer to whole numbers can be badly wrong,** or not even allowed. → [[operations-research/07-integer-programming|07]]
4. **A better-written model beats a faster computer.** → [[operations-research/07-integer-programming|07]]
5. **Waiting times shoot up as a system nears full capacity.** A server at 90% busy has far longer queues than one at 80%. → [[operations-research/12-queueing-theory|12]]
6. **One shared queue beats separate queues** for each server. → [[operations-research/12-queueing-theory|12]]

## Related

- [[mathematics/index|Mathematics]]: the algebra, probability and calculus underneath.
- [[dsa/index|Data Structures and Algorithms]]: shortest paths, dynamic programming and greedy methods from the programming side.
- [[architecture/index|Architecture]]: where queueing explains why servers slow down under load.
- [[data-analysis/index|Data Analysis]]: deciding with data.

---

## About this course

- **Size:** 14 notes, about 40,000 words, written in November 2026.
- **Where it came from:** standard textbooks and solver documentation, not real operations research work. The examples using only Python's standard library (notes 04, 08, 10, 12, 13 and 14) were run and their output checked.
- **Still to run:** SciPy couldn't be installed when this was written, so these scripts were checked by hand but never executed. Run each with `uv run --with scipy python <file>.py`, compare with the expected output in its note, and tick it off here:
  - [ ] `product_mix.py`: [[operations-research/02-formulating-linear-programs|note 02]]
  - [ ] `duality.py`: [[operations-research/05-duality-and-sensitivity|note 05]]
  - [ ] `networks.py`: [[operations-research/06-network-models|note 06]]
  - [ ] `branch_and_bound.py`: [[operations-research/07-integer-programming|note 07]]
  - [ ] `kkt.py`: [[operations-research/09-nonlinear-optimisation|note 09]]
  - [ ] `game.py`: [[operations-research/11-decision-analysis-and-game-theory|note 11]]
