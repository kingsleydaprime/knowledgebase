# 04 — Adversarial Search

Search when there's an opponent: game trees, choosing the best move against perfect play, and skipping the parts of the tree that can't change the answer. Part of the [[artificial-intelligence/index|Artificial Intelligence]] subject.

1. [[artificial-intelligence/04-adversarial-search/01-games-as-search|01 — Games as Search]]: what changes when someone is playing against you, and how big game trees get.
2. [[artificial-intelligence/04-adversarial-search/02-minimax-1|02 — Minimax 1: Choosing the Best Move]]: pick the move whose worst case is best, worked on the class-notes tree.
3. [[artificial-intelligence/04-adversarial-search/03-minimax-2|03 — Minimax 2: Cost, Cut-offs and Evaluation Functions]]: solving tic-tac-toe, and estimating positions when the tree is too big.
4. [[artificial-intelligence/04-adversarial-search/04-alpha-beta-pruning-1|04 — Alpha-Beta Pruning 1: Skipping What Can't Matter]]: alpha, beta and the pruning rule, traced step by step.
5. [[artificial-intelligence/04-adversarial-search/05-alpha-beta-pruning-2|05 — Alpha-Beta Pruning 2: Move Ordering and How Much It Saves]]: why the order of moves decides the saving, and searching twice as deep.

## About this section

Built from the SSG 518 class notes, *The Minimax and Alpha-Beta Algorithms and Heuristic Approaches to State Space Search Problem* (10/03/26), and the SSG 518 *Introduction to Search* slides. Every backed-up value, pruned branch, leaf count and tic-tac-toe number is computed and asserted by `scripts/diagrams/ai_games.py`. Added 2026-11-25.
