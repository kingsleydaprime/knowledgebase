# NeetCode 150 — Solved

Every problem of the [NeetCode 150](https://neetcode.io/practice) list, each in its own file, worked **extensively**: problem statement → brute force → optimal, with code, complexity, and the key insight. The one-line "why this problem is here" and the link to the underlying **concept note** stay in the tables below; the files are the full solutions.

This complements the concept notes in the folders above ([[04-data-structures/03-hash-maps|data-structures]], [[05-algorithms/01-algorithms|algorithms]], [[06-patterns/README|patterns]]) — read the concept first to learn the tool, then these to see it applied.

**Structure:** every solution lives flat in **`questions/`**, numbered `001`–`150` in NeetCode order (so the folder reads in curriculum order without nesting). The topic grouping lives *here in this index*, not in the folder layout — this README is the map, `questions/` is the content.

## Progress

- [x] Arrays & Hashing (9)
- [ ] Two Pointers (5)
- [ ] Sliding Window (6)
- [ ] Stack (7)
- [ ] Binary Search (7)
- [ ] Linked List (11)
- [ ] Trees (15)
- [ ] Tries (3)
- [ ] Heap / Priority Queue (7)
- [ ] Backtracking (9)
- [ ] Graphs (13)
- [ ] Advanced Graphs (6)
- [ ] 1-D Dynamic Programming (12)
- [ ] 2-D Dynamic Programming (11)
- [ ] Greedy (8)
- [ ] Intervals (6)
- [ ] Math & Geometry (8)
- [ ] Bit Manipulation (7)

Categories are filled in one at a time; a problem name becomes a link once its file is written.

## Arrays & Hashing — [[03-hash-maps|hash-maps]]

Trade space for O(1) lookup; recognize when a hash map/set collapses an O(n²) scan to O(n).

| # | Problem | Key idea |
|---|---|---|
| 217 | [[001-contains-duplicate\|Contains Duplicate]] | hash set membership |
| 242 | [[002-valid-anagram\|Valid Anagram]] | char-count map equality |
| 1 | [[003-two-sum\|Two Sum]] | map value → index; look for the complement |
| 49 | [[004-group-anagrams\|Group Anagrams]] | key by char-count signature |
| 347 | [[005-top-k-frequent-elements\|Top K Frequent Elements]] | count map + bucket sort |
| 271 | [[006-encode-and-decode-strings\|Encode and Decode Strings]] | length-prefix each string |
| 238 | [[007-product-of-array-except-self\|Product of Array Except Self]] | prefix × suffix, no division |
| 36 | [[008-valid-sudoku\|Valid Sudoku]] | hash sets per row/col/box |
| 128 | [[009-longest-consecutive-sequence\|Longest Consecutive Sequence]] | set; start a run only at its left edge |

## Two Pointers — [[02-two-pointers|two-pointers]]

| # | Problem | Key idea |
|---|---|---|
| 125 | Valid Palindrome | pointers in from both ends, skip non-alphanumerics |
| 167 | Two Sum II | inward pointers; move by sum vs target |
| 15 | 3Sum | sort, fix one, two-pointer the rest; skip dupes |
| 11 | Container With Most Water | widest first; move the shorter wall inward |
| 42 | Trapping Rain Water | two pointers tracking left/right max walls |

## Sliding Window — [[03-sliding-window|sliding-window]]

| # | Problem | Key idea |
|---|---|---|
| 121 | Best Time to Buy and Sell Stock | track min-so-far; window = buy…sell |
| 3 | Longest Substring Without Repeating Characters | grow; shrink on a repeat |
| 424 | Longest Repeating Character Replacement | valid while (len − maxfreq) ≤ k |
| 567 | Permutation in String | fixed window; compare char counts |
| 76 | Minimum Window Substring | expand to satisfy, contract to minimize |
| 239 | Sliding Window Maximum | monotonic deque of candidate maxima |

## Stack — [[07-stacks-and-queues|stacks-and-queues]]

| # | Problem | Key idea |
|---|---|---|
| 20 | Valid Parentheses | push opens, match/pop on closes |
| 155 | Min Stack | pair each value with the min-so-far |
| 150 | Evaluate Reverse Polish Notation | pop operands, push results |
| 22 | Generate Parentheses | backtracking with open/close counts |
| 739 | Daily Temperatures | monotonic stack of indices |
| 853 | Car Fleet | sort by position; monotonic stack of times |
| 84 | Largest Rectangle in Histogram | monotonic stack of increasing heights |

## Binary Search — [[09-modified-binary-search|modified-binary-search]]

| # | Problem | Key idea |
|---|---|---|
| 704 | Binary Search | the baseline half-and-discard |
| 74 | Search a 2D Matrix | treat the grid as one sorted array |
| 875 | Koko Eating Bananas | binary search on the answer |
| 153 | Find Minimum in Rotated Sorted Array | compare mid to right |
| 33 | Search in Rotated Sorted Array | find the sorted half, then bound |
| 981 | Time Based Key-Value Store | binary search over timestamps |
| 4 | Median of Two Sorted Arrays | binary search on the partition |

## Linked List — [[04-linked-lists|linked-lists]]

| # | Problem | Key idea |
|---|---|---|
| 206 | Reverse Linked List | iterative pointer flip |
| 21 | Merge Two Sorted Lists | two-pointer merge with a dummy |
| 143 | Reorder List | mid + reverse + interleave |
| 19 | Remove Nth Node From End | two pointers n apart |
| 138 | Copy List with Random Pointer | interleave clones or old→new map |
| 2 | Add Two Numbers | digit-by-digit with carry |
| 141 | Linked List Cycle | Floyd's fast/slow |
| 287 | Find the Duplicate Number | Floyd's on value-as-pointer |
| 146 | LRU Cache | hash map + doubly linked list |
| 23 | Merge K Sorted Lists | min-heap of k heads |
| 25 | Reverse Nodes in k-Group | reverse each k-block |

## Trees — [[01-trees|trees]] · [[02-traversal|traversal]]

| # | Problem | Key idea |
|---|---|---|
| 226 | Invert Binary Tree | swap children recursively |
| 104 | Maximum Depth of Binary Tree | 1 + max(left, right) |
| 543 | Diameter of Binary Tree | max(left height + right height) |
| 110 | Balanced Binary Tree | height check returning −1 on imbalance |
| 100 | Same Tree | structural + value recursion |
| 572 | Subtree of Another Tree | "same tree" at every node |
| 235 | Lowest Common Ancestor of a BST | descend by BST ordering |
| 102 | Binary Tree Level Order Traversal | BFS by level |
| 199 | Binary Tree Right Side View | BFS; last node per level |
| 1448 | Count Good Nodes in Binary Tree | DFS carrying max-on-path |
| 98 | Validate Binary Search Tree | DFS carrying (min, max) |
| 230 | Kth Smallest Element in a BST | in-order, stop at k |
| 105 | Construct Tree from Preorder & Inorder | root from pre, split via in |
| 124 | Binary Tree Maximum Path Sum | DFS best-arm + global max |
| 297 | Serialize and Deserialize Binary Tree | pre-order with null markers |

## Tries — [[09-tries|tries]]

| # | Problem | Key idea |
|---|---|---|
| 208 | Implement Trie (Prefix Tree) | insert / search / startsWith |
| 211 | Design Add and Search Words | wildcard `.` → branch DFS |
| 212 | Word Search II | one trie + grid backtracking |

## Heap / Priority Queue — [[08-heaps|heaps]] · [[07-top-k-elements|top-k]]

| # | Problem | Key idea |
|---|---|---|
| 703 | Kth Largest Element in a Stream | min-heap of size k |
| 1046 | Last Stone Weight | max-heap, smash two heaviest |
| 973 | K Closest Points to Origin | heap by squared distance |
| 215 | Kth Largest Element in an Array | heap O(n log k) vs Quickselect |
| 621 | Task Scheduler | max-heap by count + cooldown |
| 355 | Design Twitter | k-way merge via heap |
| 295 | Find Median from Data Stream | two heaps |

## Backtracking — [[14-backtracking|backtracking]]

| # | Problem | Key idea |
|---|---|---|
| 78 | Subsets | include/exclude each element |
| 39 | Combination Sum | reuse allowed; recurse on same index |
| 46 | Permutations | swap-in-place or used-set |
| 90 | Subsets II | sort, skip duplicate siblings |
| 40 | Combination Sum II | sort, each once, skip dup siblings |
| 79 | Word Search | grid DFS with visited + undo |
| 131 | Palindrome Partitioning | cut at every palindromic prefix |
| 17 | Letter Combinations of a Phone Number | product over digit→letters |
| 51 | N-Queens | place per row; column/diagonal sets |

## Graphs — [[06-graphs|graphs]] · [[13-matrix-traversal|matrix-traversal]]

| # | Problem | Key idea |
|---|---|---|
| 200 | Number of Islands | grid flood fill, count components |
| 133 | Clone Graph | DFS/BFS with old→new map |
| 695 | Max Area of Island | flood fill returning area |
| 417 | Pacific Atlantic Water Flow | reverse-flow BFS from both oceans |
| 130 | Surrounded Regions | mark border-connected regions safe |
| 994 | Rotting Oranges | multi-source BFS by minute |
| 286 | Walls and Gates | multi-source BFS from gates |
| 207 | Course Schedule | topological-sort feasibility |
| 210 | Course Schedule II | topological order itself |
| 684 | Redundant Connection | union-find; first cycle edge |
| 323 | Number of Connected Components | union-find; count roots |
| 261 | Graph Valid Tree | union-find; n−1 edges, no cycle |
| 127 | Word Ladder | BFS over one-letter-change neighbors |

## Advanced Graphs — [[06-dijkstra|dijkstra]] · [[12-minimum-spanning-tree|MST]] · [[11-topological-sort|topo-sort]]

| # | Problem | Key idea |
|---|---|---|
| 332 | Reconstruct Itinerary | Hierholzer's Eulerian path |
| 1584 | Min Cost to Connect All Points | MST (Prim's / Kruskal's) |
| 743 | Network Delay Time | Dijkstra, take the max |
| 778 | Swim in Rising Water | Dijkstra / binary search on max cell |
| 269 | Alien Dictionary | precedence edges → topological sort |
| 787 | Cheapest Flights Within K Stops | Bellman-Ford bounded to k+1 |

## 1-D Dynamic Programming — [[15-dynamic-programming|dynamic-programming]]

| # | Problem | Key idea |
|---|---|---|
| 70 | Climbing Stairs | Fibonacci shape |
| 746 | Min Cost Climbing Stairs | min of two prior + cost |
| 198 | House Robber | max(skip, rob + dp[i-2]) |
| 213 | House Robber II | two linear runs (drop first/last) |
| 5 | Longest Palindromic Substring | expand around center |
| 647 | Palindromic Substrings | count center expansions |
| 91 | Decode Ways | 1-digit and valid 2-digit splits |
| 322 | Coin Change | unbounded knapsack |
| 152 | Maximum Product Subarray | track running max and min |
| 139 | Word Break | dp[i] true if a word ends at i |
| 300 | Longest Increasing Subsequence | dp[i]=1+max(dp[j]<); O(n log n) |
| 416 | Partition Equal Subset Sum | subset-sum to total/2 |

## 2-D Dynamic Programming — [[15-dynamic-programming|dynamic-programming]]

| # | Problem | Key idea |
|---|---|---|
| 62 | Unique Paths | dp[r][c]=dp[r-1][c]+dp[r][c-1] |
| 1143 | Longest Common Subsequence | match → diagonal+1 |
| 309 | Buy/Sell Stock with Cooldown | hold/sold/rest state machine |
| 518 | Coin Change II | count combinations |
| 494 | Target Sum | ± signs → subset-sum count |
| 97 | Interleaving String | 2-D reachability |
| 329 | Longest Increasing Path in a Matrix | DFS + memo |
| 115 | Distinct Subsequences | match → sum; else carry |
| 72 | Edit Distance | 1+min(insert, delete, replace) |
| 312 | Burst Balloons | interval DP on last balloon |
| 10 | Regular Expression Matching | 2-D with `*`/`.` transitions |

## Greedy — [[10-greedy-algorithms|greedy]]

| # | Problem | Key idea |
|---|---|---|
| 53 | Maximum Subarray | Kadane's |
| 55 | Jump Game | farthest reachable index |
| 45 | Jump Game II | extend current jump's range |
| 134 | Gas Station | failing point + 1 if total ≥ 0 |
| 846 | Hand of Straights | count map + take runs from smallest |
| 1899 | Merge Triplets to Form Target | keep triplets never exceeding target |
| 763 | Partition Labels | extend to last index of each char |
| 678 | Valid Parenthesis String | track min/max open count |

## Intervals — [[08-overlapping-intervals|overlapping-intervals]]

| # | Problem | Key idea |
|---|---|---|
| 57 | Insert Interval | before / merge / after |
| 56 | Merge Intervals | sort by start, merge touching |
| 435 | Non-overlapping Intervals | sort by end; count removals |
| 252 | Meeting Rooms | sort; any overlap → false |
| 253 | Meeting Rooms II | min-heap of end times |
| 1851 | Minimum Interval to Include Each Query | sort + heap by size |

## Math & Geometry — [[14-math-and-geometry|math-and-geometry]]

| # | Problem | Key idea |
|---|---|---|
| 48 | Rotate Image | transpose + reverse rows |
| 54 | Spiral Matrix | four shrinking boundaries |
| 73 | Set Matrix Zeroes | use row 0 / col 0 as markers |
| 202 | Happy Number | cycle detection |
| 66 | Plus One | grade-school carry |
| 50 | Pow(x, n) | fast exponentiation |
| 43 | Multiply Strings | digit-by-digit multiply |
| 2013 | Detect Squares | point-count hash map |

## Bit Manipulation — [[13-bit-manipulation|bit-manipulation]]

| # | Problem | Key idea |
|---|---|---|
| 136 | Single Number | XOR everything; pairs cancel |
| 191 | Number of 1 Bits | x &= x-1 (Kernighan) |
| 338 | Counting Bits | count[i]=count[i>>1]+(i&1) |
| 190 | Reverse Bits | shift out, shift in, ×32 |
| 268 | Missing Number | XOR indices with values |
| 371 | Sum of Two Integers | XOR + carry loop |
| 7 | Reverse Integer | reverse digits with overflow guard |

## Related
- [[README|DSA index]] — the concept notes underneath
- [[06-patterns/README|patterns overview]] — the pattern layer these drill
