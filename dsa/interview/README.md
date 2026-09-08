# DSA — Interview Prep

From [[foundations/dsa/README|the DSA course]] and [[foundations/dsa/06-patterns/README|the 15 patterns]]. This folder is about **how to run a coding interview**, not about grinding more problems — the problems live in [[foundations/dsa/neetcode-150/interview-playbook|the NeetCode playbook]].

## Files
1. [[foundations/dsa/interview/01-the-coding-round|The Coding Round]] — the method, the pattern-recognition table, complexity talk, and the behaviours that get you rejected with a correct solution

## The uncomfortable truth about this round

**A correct solution reached in silence scores worse than a nearly-correct one narrated well.** The interviewer cannot read your mind and is explicitly grading communication. Most rejections at this stage are not "couldn't solve it" — they're "solved it in a way I couldn't follow" or "went silent for eight minutes."

## The 60-second pattern lookup

The single highest-value thing from [[foundations/dsa/06-patterns/README|the patterns folder]] — what the problem's phrasing tells you to reach for:

| The problem says… | Reach for | Pattern |
|---|---|---|
| sorted array, find a pair/triplet | two pointers | [[foundations/dsa/06-patterns/02-two-pointers\|02]] |
| contiguous subarray, "longest/shortest with…" | sliding window | [[foundations/dsa/06-patterns/03-sliding-window\|03]] |
| range sums, queried repeatedly | prefix sum | [[foundations/dsa/06-patterns/01-prefix-sum\|01]] |
| cycle in a linked list, find the middle | fast/slow pointers | [[foundations/dsa/06-patterns/04-fast-slow-pointers\|04]] |
| "next greater/smaller element" | monotonic stack | [[foundations/dsa/06-patterns/06-monotonic-stack\|06]] |
| top/smallest K, or a running median | heap | [[foundations/dsa/06-patterns/07-top-k-elements\|07]] |
| merge/insert intervals | sort by start, then sweep | [[foundations/dsa/06-patterns/08-overlapping-intervals\|08]] |
| sorted, or a monotonic predicate | binary search — **including on the answer** | [[foundations/dsa/06-patterns/09-modified-binary-search\|09]] |
| shortest path, unweighted | BFS | [[foundations/dsa/06-patterns/12-bfs-pattern\|12]] |
| all paths / connected components / islands | DFS | [[foundations/dsa/06-patterns/11-dfs-pattern\|11]] |
| all combinations/permutations/subsets | backtracking | [[foundations/dsa/06-patterns/14-backtracking\|14]] |
| "how many ways", "min/max cost", overlapping subproblems | DP | [[foundations/dsa/06-patterns/15-dynamic-programming\|15]] |
| dependencies / ordering / prerequisites | topological sort | [[foundations/dsa/05-algorithms/11-topological-sort\|topo sort]] |
| dynamic connectivity, grouping | union-find | [[foundations/dsa/04-data-structures/10-union-find\|union-find]] |

**"Binary search on the answer"** is the most under-used entry there — any problem of the form "find the minimum X such that a check passes," where the check is monotonic, is a binary search over the answer space rather than over an array. Recognising it turns a lot of hard-looking problems into medium ones.

## Related
- [[foundations/dsa/README|DSA course]] · [[foundations/dsa/06-patterns/README|the 15 patterns]]
- [[foundations/dsa/neetcode-150/interview-playbook|NeetCode 150 playbook]]
- [[languages/01-java/interview/01-language-and-collections|Java collections]] — know your language's data structures cold
- [[PRIMETECHIE|The Primetechie Path]] — Rank I gate
