---
id: 625c7fd3-907e-4e9d-9368-67407533fdef
---

# Genetic Algorithms

A genetic algorithm evolves a population of candidate solutions using selection, crossover and mutation, guided by a fitness score, so that good solutions breed better ones.

## Before you start
<!-- bite: ecc93e2a-89bb-418d-9769-7dfa4c4a9522 -->

Read [[artificial-intelligence/03-heuristic-search/09-simulated-annealing|Simulated Annealing]] first, for the idea of a local search that uses randomness. You should know how to read a binary number (for example, 01101 is 13).

After this lesson you will be able to:

1. name the parts of a genetic algorithm: population, fitness, selection, crossover and mutation;
2. run one generation by hand on a small problem, including fitness-proportional selection;
3. explain what crossover and mutation each contribute;
4. choose between the informed and local search methods of this section for a given problem.

## What a genetic algorithm is
<!-- bite: e96f5b66-c88b-46eb-bc89-efa42aae9fb1 -->

Hill climbing and simulated annealing improve one state. Local beam search kept $k$ states. A **genetic algorithm** keeps a whole **population** of states, and makes new ones by *combining* good old ones, the way living things pass on their genes.

Your slides put it in one line: genetic algorithms evolve a population of candidate solutions using selection, crossover and mutation, guided by a fitness score. Your class notes list them under **metaheuristics**: approximate methods for solving complex problems. And lesson 03 of section 01 mentioned their history: evolutionary computing goes back to Friedberg's work in 1958.

## The kid version
<!-- bite: 75b96195-df1a-4a95-97a7-76fd15a5864d -->

A farmer wants maize that grows tall. She plants many seeds, sees which plants grow tallest, and saves seeds only from those. She cross-pollinates two tall plants, hoping the children get the best of both. Now and then a seed comes out slightly different by chance, and once in a while that difference is an improvement. Year after year, the field gets taller. A genetic algorithm does the same with solutions instead of maize.

**Where the analogy stops working.** Real evolution has no goal. A genetic algorithm has an explicit fitness function chosen by the programmer, and it stops when a solution is good enough or a set number of generations has run.

## The parts
<!-- bite: 76a47f66-1254-4f30-9ffd-4ccf117eceec -->

1. **Individual**: one candidate solution, written as a string, usually of bits. It's sometimes called a **chromosome**.
2. **Population**: the set of individuals in one generation.
3. **Fitness function**: a score for how good an individual is. Higher is better.
4. **Selection**: choosing parents, with fitter individuals more likely to be chosen.
5. **Crossover**: making children by cutting two parents' strings at a point and swapping the tails.
6. **Mutation**: flipping a bit at random now and then, with a small probability.

One round of select, cross over and mutate makes the next **generation**. Repeat for many generations.

## The example problem
<!-- bite: 80fd53eb-bf9a-4ecc-aeff-5d480bf9ed18 -->

Here's the classic first example. Find the whole number $x$ from 0 to 31 that makes $x^2$ as big as possible. Of course the answer is 31, but watch how the algorithm gets there without being told.

Each individual is $x$ written as 5 bits. Fitness is $x^2$. Start with a random population of four:

| Individual | $x$ | Fitness $x^2$ | Share of total |
|---|---|---|---|
| 01101 | 13 | 169 | 0.144 |
| 11000 | 24 | 576 | 0.492 |
| 01000 | 8 | 64 | 0.055 |
| 10011 | 19 | 361 | 0.309 |
| **Total** | | **1,170** | 1.000 |

## Selection
<!-- bite: 92868a77-7b84-4685-9c2d-b495d5f19c99 -->

The usual method is **fitness-proportional selection**, also called **roulette-wheel selection**. Each individual's chance of being picked as a parent is its fitness divided by the total fitness:

$$P(\text{pick } i) = \frac{\text{fitness}_i}{\text{total fitness}}$$

Picture a roulette wheel where each individual gets a slice in proportion to its fitness. 11000 gets almost half the wheel (0.492); 01000 gets a thin sliver (0.055). Spin four times to pick four parents.

Say the spins pick 01101 and 11000 as one pair, and 11000 and 10011 as the other. 11000, the fittest, was picked twice; 01000, the weakest, wasn't picked at all. That's selection doing its job: good genes spread, poor ones fade.

## Crossover
<!-- bite: 3a37bc84-3b86-4e7a-9171-fb3af0aa92f0 -->

For each pair, choose a crossover point and swap everything after it.

**Pair 1**, cut after bit 4:

1. 0110 | 1 and 1100 | 0
2. Children: 0110**0** and 1100**1**, that is 01100 (12) and 11001 (25).

**Pair 2**, cut after bit 2:

1. 11 | 000 and 10 | 011
2. Children: 11**011** and 10**000**, that is 11011 (27) and 10000 (16).

Crossover combines what's good in each parent. 11011 got the "11" start from one parent, which makes a number big, and the "011" ending from the other.

## The new generation
<!-- bite: c5e86a1e-7f82-4e5a-98f8-bbea4b7a961e -->

Here's the new population with its fitness:

| Individual | $x$ | Fitness $x^2$ |
|---|---|---|
| 01100 | 12 | 144 |
| 11001 | 25 | 625 |
| 11011 | 27 | 729 |
| 10000 | 16 | 256 |
| **Total** | | **1,754** |

In one generation, total fitness rose from 1,170 to 1,754, and the best individual from 576 to 729. Keep going, and the population closes in on 11111, $x = 31$.

## Mutation
<!-- bite: 04101167-cc68-49b8-9474-acef4b90fb2e -->

Crossover can only shuffle bits that are already in the population. Suppose no individual had a 1 in the last position. Then no amount of crossover could ever make 11111.

**Mutation** fixes that. With a small probability, say 1 in 1,000 per bit, a bit is flipped. 11011 might mutate to 11111. Mutation keeps variety in the population and lets the search reach states crossover alone can't. Too much mutation, though, and the algorithm becomes a random search, throwing away what selection has built.

## How good are genetic algorithms?
<!-- bite: 8d86524c-1f03-4c52-b777-2c3ebdd7eb57 -->

Like the other local methods, a genetic algorithm gives no guarantee of the best answer. Your slides say these methods give good solutions quickly but don't guarantee the best one. Their strength is in huge, bumpy search spaces where hill climbing would get stuck: the population explores many regions at once, and crossover can jump between them.

Typical uses from your slides: the n-queens puzzle, timetabling and scheduling, circuit layout, and the travelling salesman problem.

## Choosing a heuristic or local method
<!-- bite: 5b5dd588-3e56-467c-bee7-707ed4ff500a -->

Here's the whole section in one list, following your slides' *Choosing a Search Method* table:

1. **A good admissible heuristic is available, and you need the best path:** A\*. It's optimal and usually efficient.
2. **Speed matters more than the best answer:** greedy best-first search. It moves quickly toward the goal.
3. **A huge space, and a good-enough path will do, with fixed memory:** beam search.
4. **Only the final state matters, and the space is huge:** local search. Hill climbing is fastest; simulated annealing escapes local maxima; genetic algorithms explore many regions at once.

## Terms used in this lesson
<!-- bite: a65d0cd3-a87f-4240-a635-87197d84479f -->

1. **Genetic algorithm**: This is a search method that evolves a population of candidate solutions through selection, crossover and mutation, guided by a fitness function.
2. **Individual**: This is also known as a **chromosome**. It's one candidate solution, usually written as a string of bits.
3. **Population**: This is the set of individuals in one generation.
4. **Fitness function**: This is the score that says how good an individual is.
5. **Roulette-wheel selection**: This is also known as **fitness-proportional selection**. Each individual is chosen as a parent with probability equal to its fitness divided by the total fitness.
6. **Crossover**: This is combining two parents by cutting their strings at a point and swapping the parts after it.
7. **Mutation**: This is randomly flipping a bit with a small probability, to keep variety in the population.
8. **Metaheuristic**: This is a general, approximate strategy for searching very large spaces, such as a genetic algorithm.

## Common pitfalls and traps
<!-- bite: 87c6e9a5-669a-4197-8796-e9848c748764 -->

- **Thinking the fittest individual always survives.** Selection is probabilistic: fitter individuals are more *likely* to be picked, not certain.
- **Forgetting mutation.** Without it, the population can lose a bit value entirely and never get it back.
- **Mixing up the crossover point.** "Cut after bit 2" means the first two bits stay and the last three are swapped.

## Check your understanding
<!-- bite: 71ef9d3d-9364-40e3-9e3d-f1bb5edc3c00 -->

Try each one before you open the answer.

1. <!-- q: exact id="8ce2d830" answer="0.2" accept="1/5|20%" -->
   A population has four individuals with fitness 10, 20, 30 and 40. Using roulette-wheel selection, what is the probability of picking the individual with fitness 20 for one spin?

   <details><summary>Answer</summary>

   The total is 10 + 20 + 30 + 40 = 100, so the probability is 20 / 100 = 0.2.

   </details>

2. <!-- q: gap id="758a5b61" answers="10001;01110" -->
   Parents 10110 and 01001 cross over after bit 2. The first child is ___ and the second child is ___.

   <details><summary>Answer</summary>

   10|110 and 01|001 swap tails: 10**001** = 10001, and 01**110** = 01110.

   </details>

3. <!-- q: mcq id="3e3ad9cd" -->
   What does mutation contribute that crossover can't?

   - [ ] It makes the fittest individual certain to survive.
   - [x] It can create bit values that no individual in the population currently has.
   - [ ] It doubles the population each generation.
   - [ ] It guarantees the optimal solution.

   <details><summary>Answer</summary>

   Crossover only rearranges bits already present. Mutation flips bits at random, so it can bring back a value the whole population has lost.

   </details>

4. <!-- q: exact id="d8ebb5fc" answer="625" -->
   In the "maximise $x^2$" example, what is the fitness of the individual 11001?

   <details><summary>Answer</summary>

   11001 is 16 + 8 + 1 = 25, and $25^2 = 625$.

   </details>

5. <!-- q: open id="43624848" -->
   Your slides say genetic algorithms, simulated annealing and hill climbing "give good solutions quickly but do not guarantee the best one". For each of the three, say briefly how it tries to avoid getting stuck at a poor solution.

   <details><summary>Answer</summary>

   Hill climbing on its own doesn't; it's usually run with random restarts so different starts reach different peaks. Simulated annealing accepts some worse moves while the temperature is high, so it can walk off a local maximum. A genetic algorithm keeps a whole population spread across the space, crossover combines good parts from different regions, and mutation keeps adding variety.

   </details>

## Before moving on
<!-- bite: b48c1d91-5c4c-4109-9950-c209966c7a0c -->

You're done when you can name the parts of a genetic algorithm, run one generation by hand with roulette-wheel selection, crossover and mutation, and choose the right method from this section for a described problem.

Recap: a genetic algorithm keeps a population, scores it with a fitness function, picks parents in proportion to fitness, makes children by crossover, and flips the occasional bit by mutation. In the $x^2$ example, one generation raised total fitness from 1,170 to 1,754 and the best from 576 to 729. Like the other local methods, it finds good solutions without guaranteeing the best.

That's the end of section 03. Section 04 of the [[artificial-intelligence/index|Artificial Intelligence]] subject is adversarial search: what changes when there's an opponent trying to make you lose, and the minimax and alpha-beta algorithms.

## Related
<!-- bite: 5d9224de-5548-4965-8e21-c6e2081af444 -->

- [[artificial-intelligence/03-heuristic-search/08-beam-search|Beam Search]]: stochastic beam search is close to selection without crossover.
- [[operations-research/index|Operations Research]]: other ways to attack scheduling and routing problems.

## About this lesson
<!-- bite: d64150cd-f28d-41c8-bfae-61bb5e43cc00 -->

**Level:** introductory to intermediate. Lesson 10 of section 03 (heuristic search). It covers the parts of a genetic algorithm, one full generation of the "maximise $x^2$" example, mutation, and a summary of how to choose among this section's methods.

**Source:** University of Lagos SSG 518 class notes (*Metaheuristics: approximation methods for solving complex problems, e.g. genetic algorithms*, 09/03/26) and the SSG 518 *Introduction to Search* slides (*Local Search and Optimisation* and *Choosing a Search Method*). The "maximise $x^2$" example is the classic one from Goldberg's *Genetic Algorithms in Search, Optimization and Machine Learning*. Every fitness value, share and child is computed and asserted by `scripts/diagrams/ai_heuristic.py`.
