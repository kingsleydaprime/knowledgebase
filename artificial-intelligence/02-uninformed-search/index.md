# 02 — Uninformed Search

What search is, how to judge a search method, and the six blind search methods, each traced by hand on the Lagos-to-Abuja map. Part of the [[artificial-intelligence/index|Artificial Intelligence]] subject.

1. [[artificial-intelligence/02-uninformed-search/01-what-search-is|01 — What Search Is]]: search trees, the frontier, and searching forward from the data or backward from the goal.
2. [[artificial-intelligence/02-uninformed-search/02-measuring-a-search-method|02 — Measuring a Search Method]]: the four questions for judging any search, and why the tree grows so fast.
3. [[artificial-intelligence/02-uninformed-search/03-breadth-first-search|03 — Breadth-First Search]]: level by level with a queue; finds the fewest steps but uses a lot of memory.
4. [[artificial-intelligence/02-uninformed-search/04-depth-first-search|04 — Depth-First Search]]: one path as deep as it goes, then back up; tiny memory, no guarantees.
5. [[artificial-intelligence/02-uninformed-search/05-depth-limited-search|05 — Depth-Limited Search]]: depth-first with a maximum depth, and its two ways of failing.
6. [[artificial-intelligence/02-uninformed-search/06-iterative-deepening-search|06 — Iterative Deepening Search]]: deeper and deeper limits; the best of breadth-first and depth-first.
7. [[artificial-intelligence/02-uninformed-search/07-uniform-cost-search-1|07 — Uniform-Cost Search 1: The Cheapest Path First]]: always extend the cheapest path, traced on the graph from the class notes.
8. [[artificial-intelligence/02-uninformed-search/08-uniform-cost-search-2|08 — Uniform-Cost Search 2: The Road Trip and When to Stop]]: the 790 km route, and why the goal test waits.
9. [[artificial-intelligence/02-uninformed-search/09-bidirectional-search|09 — Bidirectional Search]]: search from both ends and meet in the middle.
10. [[artificial-intelligence/02-uninformed-search/10-comparing-uninformed-search|10 — Comparing Uninformed Search Methods]]: all six side by side, and how to choose.
11. [[artificial-intelligence/02-uninformed-search/11-river-crossing-puzzles|11 — River-Crossing Puzzles: Formulating and Solving with Search]]: the goat, yam and lion, and the missionaries and cannibals, solved with breadth-first search.

## About this section

Built from the SSG 518 class notes, *Introduction to Search Method in AI Problem* (23/11/25 and 24/11/25), and the SSG 518 *Introduction to Search* slides. Every trace, route and node count is computed and asserted by `scripts/diagrams/ai_search.py`. Added 2026-11-25.
