# LeetCode Patterns — University-Style Teaching Notes

15 recurring problem-solving patterns, revised to university / high-school course quality per [[COURSE-STANDARD|the course standard]]. Each pattern has prerequisites, observable outcomes, motivation, definitions, a step-by-step mechanism, a complete runnable example, independent practice with checks, and a demonstrable finish line. The teaching moves borrow from [[dsa/02-data-structures/index|DSA 02-data-structures]] — motivation before machinery, definitions before terminology, concrete examples with predictions, and independent implementation tasks.

15 recurring problem-solving patterns, based on ["LeetCode was HARD until I Learned these 15 Patterns" (Ashish Pratap Singh, blog.algomaster.io)](https://blog.algomaster.io/p/15-leetcode-patterns), reworked and expanded with the mechanics already written up in the parent [[dsa/index|DSA notes]]. The pitch of the source article, worth keeping in mind: LeetCode is less about the number of problems solved and more about how many patterns you recognize — most "new" problems are a known pattern wearing a different costume.

Several of these link back to a foundations note for the underlying mechanics (traversal orders, DFS, BFS) rather than re-explaining them — this folder is about _recognizing which pattern applies and why_, not re-deriving the algorithm from scratch.

## The 15 patterns

Roughly ordered easiest to hardest to first get comfortable with — later ones lean on earlier ones (backtracking on DFS, for instance).

1. [[01-prefix-sum|01 — Prefix Sum]] — **[Beginner]** — O(1) range-sum queries after O(n) preprocessing
2. [[02-two-pointers|02 — Two Pointers]] — **[Beginner]** — converge from both ends of sorted data
3. [[03-sliding-window|03 — Sliding Window]] — **[Intermediate]** — contiguous subarray/substring, same-direction pointers
4. [[04-fast-slow-pointers|04 — Fast & Slow Pointers]] — **[Intermediate]** — cycle detection, O(1) space
5. [[05-linked-list-reversal|05 — Linked List In-place Reversal]] — **[Intermediate]** — in-place pointer rewiring
6. [[06-monotonic-stack|06 — Monotonic Stack]] — **[Intermediate]** — next greater/smaller element in O(n)
7. [[07-top-k-elements|07 — Top 'K' Elements]] — **[Intermediate]** — heap-based top/bottom k
8. [[08-overlapping-intervals|08 — Overlapping Intervals]] — **[Intermediate]** — sort by start, merge in one pass
9. [[09-modified-binary-search|09 — Modified Binary Search]] — **[Advanced]** — binary search on rotated/modified sorted data
10. [[10-binary-tree-traversal-pattern|10 — Binary Tree Traversal]] — **[Intermediate]** — choosing pre/in/postorder for the problem at hand
11. [[11-dfs-pattern|11 — DFS as a Problem-Solving Pattern]] — **[Intermediate]** — explore every path/branch, topological sort
12. [[12-bfs-pattern|12 — BFS as a Problem-Solving Pattern]] — **[Intermediate]** — shortest path/level order in unweighted structures
13. [[13-matrix-traversal|13 — Matrix Traversal]] — **[Intermediate]** — grids as implicit graphs
14. [[14-backtracking|14 — Backtracking]] — **[Advanced]** — explore + undo, generate all valid arrangements
15. [[15-dynamic-programming|15 — Dynamic Programming]] — **[Advanced]** — cache overlapping subproblems, memoization vs tabulation

## Question banks

One bank per lesson: micro-questions with the answers hidden behind toggles, for closed-book recall rather than reading. Method explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

- [[01-prefix-sum-qb|Prefix Sum]]
- [[02-two-pointers-qb|Two Pointers]]
- [[03-sliding-window-qb|Sliding Window]]
- [[04-fast-slow-pointers-qb|Fast & Slow Pointers]]
- [[05-linked-list-reversal-qb|Linked List Reversal]]
- [[06-monotonic-stack-qb|Monotonic Stack]]
- [[07-top-k-elements-qb|Top K Elements]]
- [[08-overlapping-intervals-qb|Overlapping Intervals]]
- [[09-modified-binary-search-qb|Modified Binary Search]]
- [[10-binary-tree-traversal-pattern-qb|Binary Tree Traversal Pattern]]
- [[11-dfs-pattern-qb|DFS Pattern]]
- [[12-bfs-pattern-qb|BFS Pattern]]
- [[13-matrix-traversal-qb|Matrix Traversal]]
- [[14-backtracking-qb|Backtracking]]
- [[15-dynamic-programming-qb|Dynamic Programming Pattern]]

---

## Related

- [[dsa/index|DSA fundamentals index]]
