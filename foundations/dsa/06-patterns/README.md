# LeetCode Patterns

15 recurring problem-solving patterns, based on ["LeetCode was HARD until I Learned these 15 Patterns" (Ashish Pratap Singh, blog.algomaster.io)](https://blog.algomaster.io/p/15-leetcode-patterns), reworked and expanded with the mechanics already written up in the parent [[foundations/dsa/README|DSA notes]]. The pitch of the source article, worth keeping in mind: LeetCode is less about the number of problems solved and more about how many patterns you recognize — most "new" problems are a known pattern wearing a different costume.

Several of these link back to a foundations note for the underlying mechanics (traversal orders, DFS, BFS) rather than re-explaining them — this folder is about *recognizing which pattern applies and why*, not re-deriving the algorithm from scratch.

## The 15 patterns

Roughly ordered easiest to hardest to first get comfortable with — later ones lean on earlier ones (backtracking on DFS, for instance).

1. [[01-prefix-sum|prefix-sum]] — **[Beginner]** — O(1) range-sum queries after O(n) preprocessing
2. [[02-two-pointers|two-pointers]] — **[Beginner]** — converge from both ends of sorted data
3. [[03-sliding-window|sliding-window]] — **[Intermediate]** — contiguous subarray/substring, same-direction pointers
4. [[04-fast-slow-pointers|fast-slow-pointers]] — **[Intermediate]** — cycle detection, O(1) space
5. [[05-linked-list-reversal|linked-list-reversal]] — **[Intermediate]** — in-place pointer rewiring
6. [[06-monotonic-stack|monotonic-stack]] — **[Intermediate]** — next greater/smaller element in O(n)
7. [[07-top-k-elements|top-k-elements]] — **[Intermediate]** — heap-based top/bottom k
8. [[08-overlapping-intervals|overlapping-intervals]] — **[Intermediate]** — sort by start, merge in one pass
9. [[09-modified-binary-search|modified-binary-search]] — **[Advanced]** — binary search on rotated/modified sorted data
10. [[10-binary-tree-traversal-pattern|binary-tree-traversal-pattern]] — **[Intermediate]** — choosing pre/in/postorder for the problem at hand
11. [[11-dfs-pattern|dfs-pattern]] — **[Intermediate]** — explore every path/branch, topological sort
12. [[12-bfs-pattern|bfs-pattern]] — **[Intermediate]** — shortest path/level order in unweighted structures
13. [[13-matrix-traversal|matrix-traversal]] — **[Intermediate]** — grids as implicit graphs
14. [[14-backtracking|backtracking]] — **[Advanced]** — explore + undo, generate all valid arrangements
15. [[15-dynamic-programming|dynamic-programming]] — **[Advanced]** — cache overlapping subproblems, memoization vs tabulation

## Related
- [[foundations/dsa/README|DSA fundamentals index]]
