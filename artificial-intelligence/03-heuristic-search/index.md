# 03 — Heuristic Search

Giving search a sense of direction with an estimate of the distance to the goal, then searching without a path at all when only the final state matters. Part of the [[artificial-intelligence/index|Artificial Intelligence]] subject.

1. [[artificial-intelligence/03-heuristic-search/01-heuristics-and-heuristic-search|01 — Heuristics and Heuristic Search]]: what a heuristic is, straight-line distance, and trading guarantees for speed.
2. [[artificial-intelligence/03-heuristic-search/02-generate-and-test|02 — Generate and Test]]: guess, check, guess again, and why a smart generator matters.
3. [[artificial-intelligence/03-heuristic-search/03-greedy-best-first-search|03 — Greedy Best-First Search]]: always head for whatever looks closest; fast but not optimal.
4. [[artificial-intelligence/03-heuristic-search/04-a-star-search-1|04 — A\* Search 1: Cost So Far Plus Estimate to Go]]: the method that adds both, traced on the course slides' graph.
5. [[artificial-intelligence/03-heuristic-search/05-a-star-search-2|05 — A\* Search 2: The Road Trip and When A\* Is Optimal]]: the 790 km route, and the rule that makes A\* trustworthy.
6. [[artificial-intelligence/03-heuristic-search/06-heuristics-for-the-8-puzzle|06 — Heuristics for the 8-Puzzle]]: inventing good estimates for a puzzle, and how much a better one saves.
7. [[artificial-intelligence/03-heuristic-search/07-hill-climbing|07 — Hill Climbing]]: always step uphill, and the three places it gets stuck.
8. [[artificial-intelligence/03-heuristic-search/08-beam-search|08 — Beam Search]]: keep only the few most promising states at each level.
9. [[artificial-intelligence/03-heuristic-search/09-simulated-annealing|09 — Simulated Annealing]]: sometimes step downhill on purpose, less and less as things cool.
10. [[artificial-intelligence/03-heuristic-search/10-genetic-algorithms|10 — Genetic Algorithms]]: evolve a population of solutions, and how to choose among this section's methods.

## About this section

Built from the SSG 518 class notes on informed search (23/11/25, 02/02/26) and on heuristic search in state space and generate-and-test (10/02/26), and the SSG 518 *Introduction to Search* slides (informed search, the A\* worked example, local search, choosing a method). Every heuristic value, trace, 8-puzzle count and genetic-algorithm number is computed and asserted by `scripts/diagrams/ai_heuristic.py`. Added 2026-11-25.
