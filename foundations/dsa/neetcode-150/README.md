# NeetCode 150 — Solved

Every problem of the [NeetCode 150](https://neetcode.io/practice) list, each in its own file, worked **extensively**: problem statement → brute force → optimal, with code, complexity, and the key insight. The one-line "why this problem is here" and the link to the underlying **concept note** stay in the tables below; the files are the full solutions.

This complements the concept notes in the folders above ([[04-data-structures/03-hash-maps|data-structures]], [[05-algorithms/01-algorithms|algorithms]], [[06-patterns/README|patterns]]) — read the concept first to learn the tool, then these to see it applied.

**Structure:** every solution lives flat in **`questions/`**, numbered `001`–`150` in NeetCode order (so the folder reads in curriculum order without nesting). The topic grouping lives *here in this index*, not in the folder layout — this README is the map, `questions/` is the content.

## Progress

- [x] Arrays & Hashing (9)
- [x] Two Pointers (5)
- [x] Sliding Window (6)
- [x] Stack (7)
- [x] Binary Search (7)
- [x] Linked List (11)
- [x] Trees (15)
- [x] Tries (3)
- [x] Heap / Priority Queue (7)
- [x] Backtracking (9)
- [x] Graphs (13)
- [x] Advanced Graphs (6)
- [x] 1-D Dynamic Programming (12)
- [x] 2-D Dynamic Programming (11)
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
| 125 | [[010-valid-palindrome\|Valid Palindrome]] | pointers in from both ends, skip non-alphanumerics |
| 167 | [[011-two-sum-ii\|Two Sum II]] | inward pointers; move by sum vs target |
| 15 | [[012-3sum\|3Sum]] | sort, fix one, two-pointer the rest; skip dupes |
| 11 | [[013-container-with-most-water\|Container With Most Water]] | widest first; move the shorter wall inward |
| 42 | [[014-trapping-rain-water\|Trapping Rain Water]] | two pointers tracking left/right max walls |

## Sliding Window — [[03-sliding-window|sliding-window]]

| # | Problem | Key idea |
|---|---|---|
| 121 | [[015-best-time-to-buy-and-sell-stock\|Best Time to Buy and Sell Stock]] | track min-so-far; window = buy…sell |
| 3 | [[016-longest-substring-without-repeating-characters\|Longest Substring Without Repeating Characters]] | grow; shrink on a repeat |
| 424 | [[017-longest-repeating-character-replacement\|Longest Repeating Character Replacement]] | valid while (len − maxfreq) ≤ k |
| 567 | [[018-permutation-in-string\|Permutation in String]] | fixed window; compare char counts |
| 76 | [[019-minimum-window-substring\|Minimum Window Substring]] | expand to satisfy, contract to minimize |
| 239 | [[020-sliding-window-maximum\|Sliding Window Maximum]] | monotonic deque of candidate maxima |

## Stack — [[07-stacks-and-queues|stacks-and-queues]]

| # | Problem | Key idea |
|---|---|---|
| 20 | [[021-valid-parentheses\|Valid Parentheses]] | push opens, match/pop on closes |
| 155 | [[022-min-stack\|Min Stack]] | pair each value with the min-so-far |
| 150 | [[023-evaluate-reverse-polish-notation\|Evaluate Reverse Polish Notation]] | pop operands, push results |
| 22 | [[024-generate-parentheses\|Generate Parentheses]] | backtracking with open/close counts |
| 739 | [[025-daily-temperatures\|Daily Temperatures]] | monotonic stack of indices |
| 853 | [[026-car-fleet\|Car Fleet]] | sort by position; monotonic stack of times |
| 84 | [[027-largest-rectangle-in-histogram\|Largest Rectangle in Histogram]] | monotonic stack of increasing heights |

## Binary Search — [[09-modified-binary-search|modified-binary-search]]

| # | Problem | Key idea |
|---|---|---|
| 704 | [[028-binary-search\|Binary Search]] | the baseline half-and-discard |
| 74 | [[029-search-a-2d-matrix\|Search a 2D Matrix]] | treat the grid as one sorted array |
| 875 | [[030-koko-eating-bananas\|Koko Eating Bananas]] | binary search on the answer |
| 153 | [[031-find-minimum-in-rotated-sorted-array\|Find Minimum in Rotated Sorted Array]] | compare mid to right |
| 33 | [[032-search-in-rotated-sorted-array\|Search in Rotated Sorted Array]] | find the sorted half, then bound |
| 981 | [[033-time-based-key-value-store\|Time Based Key-Value Store]] | binary search over timestamps |
| 4 | [[034-median-of-two-sorted-arrays\|Median of Two Sorted Arrays]] | binary search on the partition |

## Linked List — [[04-linked-lists|linked-lists]]

| # | Problem | Key idea |
|---|---|---|
| 206 | [[035-reverse-linked-list\|Reverse Linked List]] | iterative pointer flip |
| 21 | [[036-merge-two-sorted-lists\|Merge Two Sorted Lists]] | two-pointer merge with a dummy |
| 143 | [[037-reorder-list\|Reorder List]] | mid + reverse + interleave |
| 19 | [[038-remove-nth-node-from-end\|Remove Nth Node From End]] | two pointers n apart |
| 138 | [[039-copy-list-with-random-pointer\|Copy List with Random Pointer]] | interleave clones or old→new map |
| 2 | [[040-add-two-numbers\|Add Two Numbers]] | digit-by-digit with carry |
| 141 | [[041-linked-list-cycle\|Linked List Cycle]] | Floyd's fast/slow |
| 287 | [[042-find-the-duplicate-number\|Find the Duplicate Number]] | Floyd's on value-as-pointer |
| 146 | [[043-lru-cache\|LRU Cache]] | hash map + doubly linked list |
| 23 | [[044-merge-k-sorted-lists\|Merge K Sorted Lists]] | min-heap of k heads |
| 25 | [[045-reverse-nodes-in-k-group\|Reverse Nodes in k-Group]] | reverse each k-block |

## Trees — [[01-trees|trees]] · [[02-traversal|traversal]]

| # | Problem | Key idea |
|---|---|---|
| 226 | [[046-invert-binary-tree\|Invert Binary Tree]] | swap children recursively |
| 104 | [[047-maximum-depth-of-binary-tree\|Maximum Depth of Binary Tree]] | 1 + max(left, right) |
| 543 | [[048-diameter-of-binary-tree\|Diameter of Binary Tree]] | max(left height + right height) |
| 110 | [[049-balanced-binary-tree\|Balanced Binary Tree]] | height check returning −1 on imbalance |
| 100 | [[050-same-tree\|Same Tree]] | structural + value recursion |
| 572 | [[051-subtree-of-another-tree\|Subtree of Another Tree]] | "same tree" at every node |
| 235 | [[052-lowest-common-ancestor-of-a-bst\|Lowest Common Ancestor of a BST]] | descend by BST ordering |
| 102 | [[053-binary-tree-level-order-traversal\|Binary Tree Level Order Traversal]] | BFS by level |
| 199 | [[054-binary-tree-right-side-view\|Binary Tree Right Side View]] | BFS; last node per level |
| 1448 | [[055-count-good-nodes-in-binary-tree\|Count Good Nodes in Binary Tree]] | DFS carrying max-on-path |
| 98 | [[056-validate-binary-search-tree\|Validate Binary Search Tree]] | DFS carrying (min, max) |
| 230 | [[057-kth-smallest-element-in-a-bst\|Kth Smallest Element in a BST]] | in-order, stop at k |
| 105 | [[058-construct-binary-tree-from-preorder-and-inorder-traversal\|Construct Tree from Preorder & Inorder]] | root from pre, split via in |
| 124 | [[059-binary-tree-maximum-path-sum\|Binary Tree Maximum Path Sum]] | DFS best-arm + global max |
| 297 | [[060-serialize-and-deserialize-binary-tree\|Serialize and Deserialize Binary Tree]] | pre-order with null markers |

## Tries — [[09-tries|tries]]

| # | Problem | Key idea |
|---|---|---|
| 208 | [[061-implement-trie-prefix-tree\|Implement Trie (Prefix Tree)]] | insert / search / startsWith |
| 211 | [[062-design-add-and-search-words-data-structure\|Design Add and Search Words]] | wildcard `.` → branch DFS |
| 212 | [[063-word-search-ii\|Word Search II]] | one trie + grid backtracking |

## Heap / Priority Queue — [[08-heaps|heaps]] · [[07-top-k-elements|top-k]]

| # | Problem | Key idea |
|---|---|---|
| 703 | [[064-kth-largest-element-in-a-stream\|Kth Largest Element in a Stream]] | min-heap of size k |
| 1046 | [[065-last-stone-weight\|Last Stone Weight]] | max-heap, smash two heaviest |
| 973 | [[066-k-closest-points-to-origin\|K Closest Points to Origin]] | heap by squared distance |
| 215 | [[067-kth-largest-element-in-an-array\|Kth Largest Element in an Array]] | heap O(n log k) vs Quickselect |
| 621 | [[068-task-scheduler\|Task Scheduler]] | max-heap by count + cooldown |
| 355 | [[069-design-twitter\|Design Twitter]] | k-way merge via heap |
| 295 | [[070-find-median-from-data-stream\|Find Median from Data Stream]] | two heaps |

## Backtracking — [[14-backtracking|backtracking]]

| # | Problem | Key idea |
|---|---|---|
| 78 | [[071-subsets\|Subsets]] | include/exclude each element |
| 39 | [[072-combination-sum\|Combination Sum]] | reuse allowed; recurse on same index |
| 46 | [[073-permutations\|Permutations]] | swap-in-place or used-set |
| 90 | [[074-subsets-ii\|Subsets II]] | sort, skip duplicate siblings |
| 40 | [[075-combination-sum-ii\|Combination Sum II]] | sort, each once, skip dup siblings |
| 79 | [[076-word-search\|Word Search]] | grid DFS with visited + undo |
| 131 | [[077-palindrome-partitioning\|Palindrome Partitioning]] | cut at every palindromic prefix |
| 17 | [[078-letter-combinations-of-a-phone-number\|Letter Combinations of a Phone Number]] | product over digit→letters |
| 51 | [[079-n-queens\|N-Queens]] | place per row; column/diagonal sets |

## Graphs — [[06-graphs|graphs]] · [[13-matrix-traversal|matrix-traversal]]

| # | Problem | Key idea |
|---|---|---|
| 200 | [[080-number-of-islands\|Number of Islands]] | grid flood fill, count components |
| 133 | [[081-clone-graph\|Clone Graph]] | DFS/BFS with old→new map |
| 695 | [[082-max-area-of-island\|Max Area of Island]] | flood fill returning area |
| 417 | [[083-pacific-atlantic-water-flow\|Pacific Atlantic Water Flow]] | reverse-flow BFS from both oceans |
| 130 | [[084-surrounded-regions\|Surrounded Regions]] | mark border-connected regions safe |
| 994 | [[085-rotting-oranges\|Rotting Oranges]] | multi-source BFS by minute |
| 286 | [[086-walls-and-gates\|Walls and Gates]] | multi-source BFS from gates |
| 207 | [[087-course-schedule\|Course Schedule]] | topological-sort feasibility |
| 210 | [[088-course-schedule-ii\|Course Schedule II]] | topological order itself |
| 684 | [[089-redundant-connection\|Redundant Connection]] | union-find; first cycle edge |
| 323 | [[090-number-of-connected-components\|Number of Connected Components]] | union-find; count roots |
| 261 | [[091-graph-valid-tree\|Graph Valid Tree]] | union-find; n−1 edges, no cycle |
| 127 | [[092-word-ladder\|Word Ladder]] | BFS over one-letter-change neighbors |

## Advanced Graphs — [[06-dijkstra|dijkstra]] · [[12-minimum-spanning-tree|MST]] · [[11-topological-sort|topo-sort]]

| # | Problem | Key idea |
|---|---|---|
| 332 | [[093-reconstruct-itinerary\|Reconstruct Itinerary]] | Hierholzer's Eulerian path |
| 1584 | [[094-min-cost-to-connect-all-points\|Min Cost to Connect All Points]] | MST (Prim's / Kruskal's) |
| 743 | [[095-network-delay-time\|Network Delay Time]] | Dijkstra, take the max |
| 778 | [[096-swim-in-rising-water\|Swim in Rising Water]] | Dijkstra / binary search on max cell |
| 269 | [[097-alien-dictionary\|Alien Dictionary]] | precedence edges → topological sort |
| 787 | [[098-cheapest-flights-within-k-stops\|Cheapest Flights Within K Stops]] | Bellman-Ford bounded to k+1 |

## 1-D Dynamic Programming — [[15-dynamic-programming|dynamic-programming]]

| # | Problem | Key idea |
|---|---|---|
| 70 | [[099-climbing-stairs\|Climbing Stairs]] | Fibonacci shape |
| 746 | [[100-min-cost-climbing-stairs\|Min Cost Climbing Stairs]] | min of two prior + cost |
| 198 | [[101-house-robber\|House Robber]] | max(skip, rob + dp[i-2]) |
| 213 | [[102-house-robber-ii\|House Robber II]] | two linear runs (drop first/last) |
| 5 | [[103-longest-palindromic-substring\|Longest Palindromic Substring]] | expand around center |
| 647 | [[104-palindromic-substrings\|Palindromic Substrings]] | count center expansions |
| 91 | [[105-decode-ways\|Decode Ways]] | 1-digit and valid 2-digit splits |
| 322 | [[106-coin-change\|Coin Change]] | unbounded knapsack |
| 152 | [[107-maximum-product-subarray\|Maximum Product Subarray]] | track running max and min |
| 139 | [[108-word-break\|Word Break]] | dp[i] true if a word ends at i |
| 300 | [[109-longest-increasing-subsequence\|Longest Increasing Subsequence]] | dp[i]=1+max(dp[j]<); O(n log n) |
| 416 | [[110-partition-equal-subset-sum\|Partition Equal Subset Sum]] | subset-sum to total/2 |

## 2-D Dynamic Programming — [[15-dynamic-programming|dynamic-programming]]

| # | Problem | Key idea |
|---|---|---|
| 62 | [[111-unique-paths\|Unique Paths]] | dp[r][c]=dp[r-1][c]+dp[r][c-1] |
| 1143 | [[112-longest-common-subsequence\|Longest Common Subsequence]] | match → diagonal+1 |
| 309 | [[113-best-time-to-buy-and-sell-stock-with-cooldown\|Buy/Sell Stock with Cooldown]] | hold/sold/rest state machine |
| 518 | [[114-coin-change-ii\|Coin Change II]] | count combinations |
| 494 | [[115-target-sum\|Target Sum]] | ± signs → subset-sum count |
| 97 | [[116-interleaving-string\|Interleaving String]] | 2-D reachability |
| 329 | [[117-longest-increasing-path-in-a-matrix\|Longest Increasing Path in a Matrix]] | DFS + memo |
| 115 | [[118-distinct-subsequences\|Distinct Subsequences]] | match → sum; else carry |
| 72 | [[119-edit-distance\|Edit Distance]] | 1+min(insert, delete, replace) |
| 312 | [[120-burst-balloons\|Burst Balloons]] | interval DP on last balloon |
| 10 | [[121-regular-expression-matching\|Regular Expression Matching]] | 2-D with `*`/`.` transitions |

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
