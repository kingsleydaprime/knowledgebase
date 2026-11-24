# Systems Simulation

## What systems simulation is

Systems simulation is building a model of a real or planned system on a computer and running it over time, so you can see how the system behaves and compare ways of running it without touching the real thing.

You've seen the questions it answers. Would a third teller cut the bank queue? How many beds does the hospital need on a busy night? Will the new traffic lights clear the junction faster? Trying each idea on the real bank, hospital or road would be slow, costly or dangerous. A simulation tries them on a model instead, in seconds.

## What you'll be able to do

By the end you will be able to:
- say what a system, a model and a simulation are, and when simulation is the right tool;
- plan a simulation study from the problem to the recommendation;
- simulate a queue by hand, and use the formulas for one and several servers;
- make random numbers, test them, and turn them into the times a model needs;
- build discrete-event models in GPSS/H and in Arena;
- choose input distributions from real data, including messy data;
- check that a model is built right and is the right model, and read its random output properly.

## Where to start

No background is needed beyond school maths and basic probability. **Start with 01** and read in order. Parts 1 and 2 (lessons 01 to 08) give the vocabulary for everything else. Part 3 (queues) and part 4 (random numbers) are the core of the calculation questions. Parts 7 and 8 (input analysis and verification and validation) are the core of the case questions.

If you're revising for the SSG 418 or SSG 517 exam, the [[systems-simulation/ssg-517-question-bank|question bank]] points each past question to its lesson.

### Part 1: Systems and models

1. [[systems-simulation/01-what-simulation-is|01 — What Simulation Is]]: what a system, a model and a simulation are, and the ways to study a system.
2. [[systems-simulation/02-when-to-simulate|02 — When to Simulate]]: why experimenting on the real thing often fails, and what simulation gives and costs.
3. [[systems-simulation/03-systems-and-their-components|03 — Systems and Their Components]]: the types of system, and the five parts used to describe any system.
4. [[systems-simulation/04-modelling-1|04 — Modelling 1: Why We Model and How Purpose Shapes the Model]]: why we build models, and why the question decides what the model keeps.
5. [[systems-simulation/05-modelling-2|05 — Modelling 2: Mathematical Models From First Principles]]: writing a model as equations from physical laws.
6. [[systems-simulation/06-types-and-components-of-simulation-models|06 — Types and Components of Simulation Models]]: the five kinds of simulation model and what they are built from.

### Part 2: The simulation study

7. [[systems-simulation/07-the-simulation-study-1|07 — The Simulation Study 1: The Twelve Steps]]: the twelve steps of a study, from the problem to putting the answer into practice.
8. [[systems-simulation/08-the-simulation-study-2|08 — The Simulation Study 2: The Ten Steps, the Challenges and the Tools]]: the ten-step class version, the challenges every study meets, and choosing software.

### Part 3: Discrete-event simulation and queues

9. [[systems-simulation/09-discrete-event-simulation|09 — Discrete-Event Simulation]]: how a simulation jumps from one event to the next.
10. [[systems-simulation/10-queueing-systems-1|10 — Queueing Systems 1: Configurations and Characteristics]]: what a queue is, its layouts and its characteristics.
11. [[systems-simulation/11-queueing-systems-2|11 — Queueing Systems 2: Behaviour, Discipline and Kendall's Notation]]: customers who leave or switch lines, who goes next, and a short code for any queue.
12. [[systems-simulation/12-measuring-a-queue-1|12 — Measuring a Queue 1: The Performance Measures]]: the numbers a queue is judged by, and how to work them out.
13. [[systems-simulation/13-measuring-a-queue-2|13 — Measuring a Queue 2: A Hand Simulation]]: a full queue simulated by hand on paper.
14. [[systems-simulation/14-littles-law-and-the-mm1-queue|14 — Little's Law and the M/M/1 Queue]]: the law linking crowd size to waiting time, and the formulas for one server.
15. [[systems-simulation/15-the-mmc-queue|15 — The M/M/c Queue]]: the formulas when several servers share one line.

### Part 4: Random numbers and Monte Carlo

16. [[systems-simulation/16-random-numbers-1|16 — Random Numbers 1: What Makes a Number Random]]: what makes a number random, and what a good generator needs.
17. [[systems-simulation/17-random-numbers-2|17 — Random Numbers 2: The Linear Congruential Method]]: making random numbers with one multiply, one add and a remainder.
18. [[systems-simulation/18-random-numbers-3|18 — Random Numbers 3: Period, Combined Generators and Streams]]: how long a generator runs before repeating, and separate streams for fair comparisons.
19. [[systems-simulation/19-testing-random-numbers-1|19 — Testing Random Numbers 1: Hypothesis Tests and the Kolmogorov-Smirnov Test]]: checking random numbers with a hypothesis test, starting with Kolmogorov-Smirnov.
20. [[systems-simulation/20-testing-random-numbers-2|20 — Testing Random Numbers 2: Chi-Square and Autocorrelation]]: two more checks: chi-square for spread and autocorrelation for patterns.
21. [[systems-simulation/21-generating-random-variates|21 — Generating Random Variates]]: turning random numbers into exponential times or values from a table.
22. [[systems-simulation/22-monte-carlo-simulation|22 — Monte Carlo Simulation]]: estimating hard quantities by sampling many times and averaging.

### Part 5: GPSS/H

23. [[systems-simulation/23-gpss-1|23 — GPSS/H 1: Transactions, Resources and Blocks]]: the SSG 418 simulation language: moving transactions, resources and blocks.
24. [[systems-simulation/24-gpss-2|24 — GPSS/H 2: Two Complete Models]]: two complete GPSS/H models, a drill and a telephone exchange.

### Part 6: Building a model

25. [[systems-simulation/25-model-building-1|25 — Model Building 1: The Eight Steps and the Questions to Ask]]: the eight model-building steps, and the questions to ask first.
26. [[systems-simulation/26-model-building-2|26 — Model Building 2: The Production Control Case]]: the lecturer's packaging-and-warehouse case worked through.

### Part 7: Input analysis and data

27. [[systems-simulation/27-input-analysis-1|27 — Input Analysis 1: Garbage In, Garbage Out, and the Four Steps]]: why wrong inputs ruin a model, and the four steps for getting them right.
28. [[systems-simulation/28-input-analysis-2|28 — Input Analysis 2: Choosing a Distribution]]: choosing the right distribution for each random input.
29. [[systems-simulation/29-input-analysis-3|29 — Input Analysis 3: Four Common Data Challenges]]: handling data that is thin, lumpy, changing over time or correlated.
30. [[systems-simulation/30-collecting-and-preparing-data|30 — Collecting and Preparing Data]]: where the data comes from, and cleaning it before you use it.

### Part 8: Verification, validation and output

31. [[systems-simulation/31-verification-and-validation-1|31 — Verification and Validation 1: Built Right, and the Right Model]]: checking the model was built as designed.
32. [[systems-simulation/32-verification-and-validation-2|32 — Verification and Validation 2: Validation Methods and Calibration]]: checking the model matches reality, and adjusting it until it does.
33. [[systems-simulation/33-verification-and-validation-3|33 — Verification and Validation 3: Errors, Bounds of Validity and Credibility]]: the ways a decision about a model can go wrong, and why a model is valid only over a range.
34. [[systems-simulation/34-output-analysis|34 — Output Analysis]]: reading random results with replications and confidence intervals.

### Part 9: Arena

35. [[systems-simulation/35-arena-1|35 — Arena 1: The Environment, Modules and Functions]]: the Arena screen, its modules and its functions.
36. [[systems-simulation/36-arena-2|36 — Arena 2: How Time Works and the Activity Diagram]]: how Arena moves time, and sketching a model before building it.
37. [[systems-simulation/37-arena-3|37 — Arena 3: Building and Running a Single-Server Queue]]: building and running a one-teller bank, and checking it against theory.
38. [[systems-simulation/38-arena-4|38 — Arena 4: Branching, Balking and Arena's Other Tools]]: branching paths, customers who give up, and Arena's analysis tools.

### Exam support (SSG 418 and SSG 517)

- [[systems-simulation/ssg-517-question-bank|SSG 418 and SSG 517 question bank]]: the 2025/26 SSG 517 paper, the 2024/25 data-collection questions, the SSG 418 practice questions and likely questions, unsolved, each pointing to the lesson that teaches it.

## Key ideas to remember

Once you've read the lessons, these are the points worth keeping. Each links to where it's explained.

1. **Simulate only when simpler routes fail.** If a formula or common sense answers it, use that. → [[systems-simulation/02-when-to-simulate|02]]
2. **An attribute belongs to one entity; a state variable describes the whole system.** → [[systems-simulation/03-systems-and-their-components|03]]
3. **The clock jumps from event to event.** Nothing happens in between. → [[systems-simulation/09-discrete-event-simulation|09]]
4. **A customer starts service at the later of their arrival and the previous departure.** → [[systems-simulation/12-measuring-a-queue-1|12]]
5. **L = λW holds for almost any queue,** and queues explode as utilisation nears 1. → [[systems-simulation/14-littles-law-and-the-mm1-queue|14]]
6. **Random numbers must be uniform and independent,** and passing a test is not proof. → [[systems-simulation/19-testing-random-numbers-1|19]]
7. **Garbage in, garbage out.** Collect input data, not performance data, and model changing rates and correlation. → [[systems-simulation/27-input-analysis-1|27]]
8. **Verification: built right. Validation: the right model.** And a model is valid only over a range. → [[systems-simulation/31-verification-and-validation-1|31]]
9. **One run proves nothing.** Use replications and confidence intervals. → [[systems-simulation/34-output-analysis|34]]

## Related

- [[operations-research/index|Operations Research]]: queueing theory, inventory and simulation for decisions.
- [[systems-engineering/index|Systems Engineering]]: managing big systems through their whole life.
- [[engineering-design-and-prototyping/index|Engineering Design and Prototyping]]: designing the systems a simulation tests.

---

## About this course

- **Size:** 38 lessons and a question bank.
- **History:** written in November 2026 from the author's own study notes for SSG 418 (Systems Simulation 1) and SSG 517 (Systems Simulation 2), which merge his class notes, lecture slides, the Banks, Carson, Nelson and Nicol textbook, the Kelton Arena textbook and past questions.
- **Corrections:** the GPSS/H handout's drill model printed `GENERATE 10.0,2.5`, which matches neither the question nor the report; lesson 24 uses 15,4.5. The notes' M/M/c worked example left out a 2! and gave P0 = 0.130; lesson 15 shows the corrected P0 = 0.2.
- **Not in the class notes:** the M/M/c formulas (standard theory, added because the notebook photos were unreadable), the Pollaczek-Khinchine check in lesson 37, the autocorrelation formulas in lesson 20 and the t-based confidence interval in lesson 34 are standard textbook material. Worked examples marked "added for this lesson" are new too. Check them against your lecturer's notes.
- **Diagrams** come from `scripts/diagrams/systems_simulation.py`, which also checks the worked numbers in the lessons.
