# NeetCode 150 — Problem Index

A map from all 150 problems of the [NeetCode 150](https://neetcode.io/practice) list to the **pattern or data-structure note** in this folder that teaches the idea behind each. The list is organized so each category drills one core technique — the point isn't to memorize 150 solutions but to recognize which of ~18 tools a new problem is asking for. Each row gives the one-line "why this problem is here."

Notes written specifically to close gaps this list exposed: [[04-data-structures/08-heaps|heaps]], [[04-data-structures/09-tries|tries]], [[04-data-structures/10-union-find|union-find]], [[05-algorithms/11-topological-sort|topological sort]], [[05-algorithms/12-minimum-spanning-tree|minimum spanning tree]], [[05-algorithms/13-bit-manipulation|bit manipulation]], and [[05-algorithms/14-math-and-geometry|math & geometry]].

## Arrays & Hashing — [[04-data-structures/03-hash-maps|hash-maps]]

The foundational category: trade space for O(1) lookup, and recognize when a hash map/set collapses an O(n²) scan to O(n).

| Problem | Key idea |
|---|---|
| Contains Duplicate | hash set membership |
| Valid Anagram | char-count map equality |
| Two Sum | map value → index; look for the complement |
| Group Anagrams | key by sorted string (or char-count tuple) |
| Top K Frequent Elements | count map + [[04-data-structures/08-heaps|heap]] or bucket sort |
| Encode and Decode Strings | length-prefix each string to make decoding unambiguous |
| Product of Array Except Self | prefix × suffix products, no division ([[06-patterns/01-prefix-sum|prefix-sum]]) |
| Valid Sudoku | hash sets per row/col/box |
| Longest Consecutive Sequence | set membership; start a run only at a sequence's left edge |

## Two Pointers — [[06-patterns/02-two-pointers|two-pointers]]

| Problem | Key idea |
|---|---|
| Valid Palindrome | pointers in from both ends, skip non-alphanumerics |
| Two Sum II (sorted) | inward pointers; move based on sum vs target |
| 3Sum | sort, fix one element, two-pointer the rest; skip dupes |
| Container With Most Water | widest first; move the shorter wall inward |
| Trapping Rain Water | two pointers tracking left/right max walls |

## Sliding Window — [[06-patterns/03-sliding-window|sliding-window]]

| Problem | Key idea |
|---|---|
| Best Time to Buy and Sell Stock | track min-so-far; window = buy…sell |
| Longest Substring Without Repeating Characters | grow window; shrink on a repeat (set/map) |
| Longest Repeating Character Replacement | window valid while (len − maxfreq) ≤ k |
| Permutation in String | fixed-width window; compare char counts |
| Minimum Window Substring | expand to satisfy, contract to minimize |
| Sliding Window Maximum | [[06-patterns/06-monotonic-stack|monotonic]] deque of candidate maxima |

## Stack — [[04-data-structures/07-stacks-and-queues|stacks-and-queues]]

| Problem | Key idea |
|---|---|
| Valid Parentheses | push opens, match/pop on closes |
| Min Stack | pair each value with the min-so-far |
| Evaluate Reverse Polish Notation | pop operands, push results |
| Generate Parentheses | [[06-patterns/14-backtracking|backtracking]] with open/close counts |
| Daily Temperatures | [[06-patterns/06-monotonic-stack|monotonic stack]] of indices awaiting a warmer day |
| Car Fleet | sort by position; monotonic stack of arrival times |
| Largest Rectangle in Histogram | monotonic stack of increasing bar heights |

## Binary Search — [[06-patterns/09-modified-binary-search|modified-binary-search]] · [[05-algorithms/05-searching|searching]]

| Problem | Key idea |
|---|---|
| Binary Search | the baseline half-and-discard |
| Search a 2D Matrix | treat the grid as one sorted array |
| Koko Eating Bananas | **binary search on the answer** (min viable speed) |
| Find Minimum in Rotated Sorted Array | compare mid to right to pick the sorted half |
| Search in Rotated Sorted Array | identify the sorted half, then bound the target |
| Time Based Key-Value Store | binary search over timestamps |
| Median of Two Sorted Arrays | binary search on the partition point, O(log(m+n)) |

## Linked List — [[04-data-structures/04-linked-lists|linked-lists]] · [[06-patterns/05-linked-list-reversal|reversal]] · [[06-patterns/04-fast-slow-pointers|fast-slow]]

| Problem | Key idea |
|---|---|
| Reverse Linked List | iterative pointer flip ([[06-patterns/05-linked-list-reversal|reversal]]) |
| Merge Two Sorted Lists | two-pointer merge with a dummy head |
| Reorder List | find middle ([[06-patterns/04-fast-slow-pointers|fast-slow]]) + reverse + interleave |
| Remove Nth Node From End | two pointers n apart |
| Copy List with Random Pointer | interleave clones, or a hash map old→new |
| Add Two Numbers | digit-by-digit with carry |
| Linked List Cycle | [[06-patterns/04-fast-slow-pointers|Floyd's]] fast/slow meet |
| Find the Duplicate Number | Floyd's cycle on the value-as-pointer array |
| LRU Cache | hash map + doubly linked list for O(1) evict |
| Merge K Sorted Lists | [[04-data-structures/08-heaps|min-heap]] of k heads (k-way merge) |
| Reverse Nodes in k-Group | reverse each k-block, stitch the boundaries |

## Trees — [[04-data-structures/05-trees/01-trees|trees]] · [[04-data-structures/05-trees/02-traversal|traversal]]

| Problem | Key idea |
|---|---|
| Invert Binary Tree | swap children recursively |
| Maximum Depth of Binary Tree | 1 + max(left, right) |
| Diameter of Binary Tree | longest path = max(left height + right height) |
| Balanced Binary Tree | height check returning −1 on imbalance |
| Same Tree | structural + value recursion |
| Subtree of Another Tree | "same tree" tried at every node |
| Lowest Common Ancestor of a BST | descend using the BST ordering |
| Binary Tree Level Order Traversal | [[06-patterns/12-bfs-pattern|BFS]] by level |
| Binary Tree Right Side View | BFS; take the last node per level |
| Count Good Nodes | [[06-patterns/11-dfs-pattern|DFS]] carrying max-on-path |
| Validate BST | DFS carrying (min, max) bounds |
| Kth Smallest Element in a BST | in-order traversal, stop at k |
| Construct Tree from Preorder & Inorder | root from preorder, split via inorder |
| Binary Tree Maximum Path Sum | DFS returning best downward arm, updating a global |
| Serialize and Deserialize Binary Tree | pre-order with null markers |

## Tries — [[04-data-structures/09-tries|tries]]

| Problem | Key idea |
|---|---|
| Implement Trie (Prefix Tree) | insert / search / startsWith |
| Design Add and Search Words | wildcard `.` → branch DFS over children |
| Word Search II | one trie of all words + grid [[06-patterns/14-backtracking|backtracking]] |

## Heap / Priority Queue — [[04-data-structures/08-heaps|heaps]] · [[06-patterns/07-top-k-elements|top-k]]

| Problem | Key idea |
|---|---|
| Kth Largest Element in a Stream | min-heap of size k |
| Last Stone Weight | max-heap, smash the two heaviest |
| K Closest Points to Origin | heap keyed by squared distance |
| Kth Largest Element in an Array | heap O(n log k) vs Quickselect O(n) |
| Task Scheduler | max-heap by count + cooldown queue |
| Design Twitter | k-way merge of followees' feeds via heap |
| Find Median from Data Stream | two heaps (max-heap low half, min-heap high half) |

## Backtracking — [[06-patterns/14-backtracking|backtracking]]

| Problem | Key idea |
|---|---|
| Subsets | include/exclude each element |
| Combination Sum | reuse allowed; recurse on same index |
| Permutations | swap-in-place or used-set |
| Subsets II | sort, skip duplicate siblings |
| Combination Sum II | sort, each element once, skip dup siblings |
| Word Search | grid DFS with visited-marking + undo |
| Palindrome Partitioning | cut at every palindromic prefix |
| Letter Combinations of a Phone Number | product over digit→letters |
| N-Queens | place per row; column/diagonal sets as constraints |

## Graphs — [[04-data-structures/06-graphs|graphs]] · [[06-patterns/13-matrix-traversal|matrix-traversal]]

| Problem | Key idea |
|---|---|
| Number of Islands | grid DFS/BFS flood fill, count components |
| Clone Graph | DFS/BFS with old→new hash map |
| Max Area of Island | flood fill returning area |
| Pacific Atlantic Water Flow | reverse-flow BFS from both oceans |
| Surrounded Regions | mark border-connected regions safe first |
| Rotting Oranges | multi-source [[06-patterns/12-bfs-pattern|BFS]] by minute |
| Walls and Gates | multi-source BFS from all gates |
| Course Schedule | cycle detection = [[05-algorithms/11-topological-sort|topological sort]] feasibility |
| Course Schedule II | topological order itself |
| Redundant Connection | [[04-data-structures/10-union-find|union-find]]; first cycle-closing edge |
| Number of Connected Components | union-find; count roots |
| Graph Valid Tree | union-find; n−1 edges and no cycle |
| Word Ladder | BFS over one-letter-change neighbors |

## Advanced Graphs — [[05-algorithms/06-dijkstra|dijkstra]] · [[05-algorithms/12-minimum-spanning-tree|MST]] · [[05-algorithms/11-topological-sort|topo-sort]]

| Problem | Key idea |
|---|---|
| Reconstruct Itinerary | Hierholzer's Eulerian path (DFS post-order) |
| Min Cost to Connect All Points | [[05-algorithms/12-minimum-spanning-tree|MST]] (Prim's / Kruskal's) |
| Network Delay Time | [[05-algorithms/06-dijkstra|Dijkstra]] from source, take the max |
| Swim in Rising Water | Dijkstra/binary-search on the max cell on a path |
| Alien Dictionary | build precedence edges → [[05-algorithms/11-topological-sort|topological sort]] |
| Cheapest Flights Within K Stops | Bellman-Ford / BFS bounded to k+1 relaxations |

## 1-D Dynamic Programming — [[06-patterns/15-dynamic-programming|dynamic-programming]]

| Problem | Key idea |
|---|---|
| Climbing Stairs | `dp[i]=dp[i-1]+dp[i-2]` (Fibonacci shape) |
| Min Cost Climbing Stairs | min of the two prior steps + cost |
| House Robber | `max(skip, rob + dp[i-2])` |
| House Robber II | two linear runs (drop first or last house) |
| Longest Palindromic Substring | expand around each center |
| Palindromic Substrings | count expansions around each center |
| Decode Ways | `dp[i]` from 1-digit and valid 2-digit splits |
| Coin Change | unbounded knapsack; fewest coins |
| Maximum Product Subarray | track running max *and* min (signs flip) |
| Word Break | `dp[i]` true if some valid word ends at i |
| Longest Increasing Subsequence | `dp[i]=1+max(dp[j]<)`; O(n log n) with binary search |
| Partition Equal Subset Sum | subset-sum to total/2 (0/1 knapsack) |

## 2-D Dynamic Programming — [[06-patterns/15-dynamic-programming|dynamic-programming]]

| Problem | Key idea |
|---|---|
| Unique Paths | `dp[r][c]=dp[r-1][c]+dp[r][c-1]` |
| Longest Common Subsequence | match → diagonal+1; else max of drops |
| Best Time to Buy/Sell with Cooldown | state machine: hold / sold / rest |
| Coin Change II | count combinations (loop coins outside) |
| Target Sum | assign ± signs → subset-sum count |
| Interleaving String | 2-D reachability over both strings' indices |
| Longest Increasing Path in a Matrix | DFS + memo on cells |
| Distinct Subsequences | match → sum both; else carry |
| Edit Distance | `1+min(insert, delete, replace)` |
| Burst Balloons | interval DP on last-balloon-to-burst |
| Regular Expression Matching | 2-D match with `*`/`.` transitions |

## Greedy — [[05-algorithms/10-greedy-algorithms|greedy]]

| Problem | Key idea |
|---|---|
| Maximum Subarray | Kadane's ([[05-algorithms/09-max-slice-algorithms|max-slice]]) |
| Jump Game | track the farthest reachable index |
| Jump Game II | BFS-like: extend the current jump's range |
| Gas Station | if total ≥ 0, the failing point + 1 is the start |
| Hand of Straights | count map + take runs from the smallest |
| Merge Triplets to Form Target | keep triplets that never exceed the target |
| Partition Labels | extend each partition to the last index of its chars |
| Valid Parenthesis String | track the min/max possible open count |

## Intervals — [[06-patterns/08-overlapping-intervals|overlapping-intervals]]

| Problem | Key idea |
|---|---|
| Insert Interval | before / merge-overlap / after |
| Merge Intervals | sort by start, merge touching |
| Non-overlapping Intervals | sort by end; greedily keep, count removals |
| Meeting Rooms | sort; any overlap → false |
| Meeting Rooms II | min-heap of end times (rooms in use) |
| Minimum Interval to Include Each Query | sort queries + [[04-data-structures/08-heaps|heap]] of intervals by size |

## Math & Geometry — [[05-algorithms/14-math-and-geometry|math-and-geometry]]

| Problem | Key idea |
|---|---|
| Rotate Image | transpose + reverse rows, in place |
| Spiral Matrix | four shrinking boundaries |
| Set Matrix Zeroes | use row 0 / col 0 as markers, O(1) space |
| Happy Number | cycle detection ([[06-patterns/04-fast-slow-pointers|fast-slow]] or set) |
| Plus One | grade-school carry, right to left |
| Pow(x, n) | fast exponentiation by squaring, O(log n) |
| Multiply Strings | digit-by-digit multiply with carries |
| Detect Squares | point-count [[04-data-structures/03-hash-maps|hash map]] over diagonals |

## Bit Manipulation — [[05-algorithms/13-bit-manipulation|bit-manipulation]]

| Problem | Key idea |
|---|---|
| Single Number | XOR everything; pairs cancel |
| Number of 1 Bits | `x &= x-1` (Brian Kernighan) |
| Counting Bits | `count[i]=count[i>>1]+(i&1)` |
| Reverse Bits | shift out one end, in the other, ×32 |
| Missing Number | XOR indices with values (or Gauss sum) |
| Sum of Two Integers | XOR (sum) + AND-shift (carry) loop |
| Reverse Integer | reverse digits with overflow guard |

## Related
- [[06-patterns/README|patterns overview]] — the pattern layer these problems drill
- [[README|DSA index]] — the concept notes underneath
