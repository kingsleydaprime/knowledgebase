---
id: d6c87cdf-af9d-4d21-8b19-739106e9b996
---

# Pattern: BFS as a Problem-Solving Pattern

BFS (breadth-first search) as a pattern is solving problems by exploring everything one step away first, then everything two steps away, and so on. That makes it the natural way to find the shortest number of steps between two points. "People you may know" on social apps, which starts with friends of your friends, works like this.

## Before you start
<!-- bite: 5f01b464-797f-43b6-8a6b-0f4202009302 -->

- You should understand BFS traversal. See [[02-breadth-first-search|bfs]] if needed.
- You should understand queues. See [[05-stacks-and-queues|stacks and queues]] if needed.

**What you will be able to do after this lesson:**

1. Define the BFS problem-solving pattern and explain when to reach for it.
2. Implement level-order tree traversal using BFS.
3. Apply the pattern to multi-source spreading problems.
4. Explain why BFS guarantees shortest paths in unweighted graphs.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)
<!-- bite: 8a301830-61f1-44cd-8f37-88cd4f516595 -->

Imagine you're building a social network and you want to find the shortest connection path between two people. You could check all paths of length 1, then all paths of length 2, and so on. This is exactly what BFS does: explore nodes level by level, expanding outward in concentric rings from a starting vertex.

The mechanics — queue-based, level by level, why it guarantees shortest paths — are covered in [[02-breadth-first-search|bfs]]. This note is about recognizing the problem shape: **anything phrased as "minimum steps/levels/time to reach X"** in an unweighted setting is almost always BFS from the start state.

---

## 2. Definitions and terminology
<!-- bite: fa12e07e-bfb0-431a-9798-f9f27455b662 -->

| Term                      | Plain-English definition                                                                  | Example / analogy                                                   |
| ------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| **BFS**                   | Breadth-first search: explore nodes level by level, expanding outward in concentric rings | Ripples expanding outward from a pebble dropped in water            |
| **Level-order traversal** | Process a tree level by level                                                             | Print a tree level by level                                         |
| **Multi-source BFS**      | Start BFS from all initial sources simultaneously                                         | Rotting oranges: all rotten oranges spread simultaneously           |
| **Shortest path**         | The path with the fewest edges between two nodes                                          | The shortest connection path between two people in a social network |

---

## 3. How it works — step by step
<!-- bite: cbd6cbfc-3d3d-4bf7-a2fa-833a38cc1e76 -->

### Level-order tree traversal

```python
from collections import deque

def level_order(root):
    if root is None:
        return []
    result, queue = [], deque([root])
    while queue:
        level_size = len(queue)         # snapshot: exactly how many nodes are in this level
        level = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result
```

The `level_size = len(queue)` snapshot is the key trick that turns plain BFS into _level-order_ BFS — without it you'd process nodes but lose track of which level each one belonged to.

### Multi-source BFS ("Rotting Oranges")

```python
def oranges_rotting(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))        # every rotten orange starts in the queue at once
            elif grid[r][c] == 1:
                fresh += 1

    minutes = 0
    directions = [(0,1),(0,-1),(1,0),(-1,0)]
    while queue and fresh:
        minutes += 1
        for _ in range(len(queue)):         # process one full level = one minute
            r, c = queue.popleft()
            for dr, dc in directions:
                nr, nc = r+dr, c+dc
                if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))
    return minutes if fresh == 0 else -1
```

All initial rotten oranges seed the queue _before_ the first level runs — this is what makes it "multi-source": BFS naturally handles multiple simultaneous starting points the same way it handles one.

---

## 4. Implementation — complete runnable example
<!-- bite: fc2485ff-93ad-4fb8-bfea-16c0d5d16893 -->

**Runnable example:** save as `bfs_pattern_lab.py` and run `python3 bfs_pattern_lab.py`. It uses only Python's standard library and creates no external files.

```python
from collections import deque


def level_order(root):
    """Level-order traversal of a binary tree."""
    if root is None:
        return []
    result, queue = [], deque([root])
    while queue:
        level_size = len(queue)         # snapshot: exactly how many nodes are in this level
        level = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result


def oranges_rotting(grid):
    """Multi-source BFS: find minutes until all oranges are rotten."""
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))        # every rotten orange starts in the queue at once
            elif grid[r][c] == 1:
                fresh += 1

    minutes = 0
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    while queue and fresh:
        minutes += 1
        for _ in range(len(queue)):         # process one full level = one minute
            r, c = queue.popleft()
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))

    return minutes if fresh == 0 else -1


if __name__ == "__main__":
    # Test case 1: level-order traversal
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    root1 = TreeNode(3)
    root1.left = TreeNode(9)
    root1.right = TreeNode(20)
    root1.right.left = TreeNode(15)
    root1.right.right = TreeNode(7)

    result1 = level_order(root1)
    print(f"Test 1 - level-order traversal:")
    print(f"tree -> {result1}")
    expected1 = [[3], [9, 20], [15, 7]]
    assert result1 == expected1, f"Expected {expected1}, got {result1}"

    # Test case 2: rotting oranges
    grid2 = [
        [2, 1, 1],
        [1, 1, 0],
        [0, 1, 1]
    ]
    result2 = oranges_rotting(grid2)
    print(f"\nTest 2 - rotting oranges:")
    print(f"grid -> {result2} minutes")
    assert result2 == 4, f"Expected 4, got {result2}"

    # Test case 3: no fresh oranges
    grid3 = [
        [0, 2]
    ]
    result3 = oranges_rotting(grid3)
    print(f"\nTest 3 - no fresh oranges:")
    print(f"grid -> {result3} minutes")
    assert result3 == 0, f"Expected 0, got {result3}"

    print("\nbfs_pattern_lab: passed")
```

Expected output:

```text
Test 1 - level-order traversal:
tree -> [[3], [9, 20], [15, 7]]

Test 2 - rotting oranges:
grid -> 4 minutes

Test 3 - no fresh oranges:
grid -> 0 minutes

bfs_pattern_lab: passed
```

---

## 5. Complexity
<!-- bite: 8c17e334-e640-4fb0-97cf-807f002a9487 -->

O(V + E), or O(rows × cols) on a grid — same as plain BFS.

---

## 6. Tradeoffs and limitations
<!-- bite: 81696102-7603-40a3-beaa-699b5ac4257b -->

- **BFS guarantees shortest paths in unweighted graphs.** DFS does not.
- **BFS uses more memory than DFS** for wide graphs, because the queue can grow to O(V) in the worst case.
- **Multi-source BFS** is useful when you have multiple starting points and want to find the minimum distance from any starting point.

---

## Check your understanding
<!-- bite: c14bc980-60bc-4c87-8f9a-d068299fe35d -->

Try each one before you open the answer.

1. <!-- q: mcq id="679f34ce" -->
   A problem asks for the fewest moves to reach a goal, and every move costs the same. Which pattern fits?

   - [x] BFS from the start
   - [ ] DFS from the start
   - [ ] Backtracking over all paths
   - [ ] Sorting the states

   <details><summary>Answer</summary>

   BFS. It explores everything 1 move away, then 2 moves away, and so on, so the first time it reaches the goal is by the fewest moves.

   </details>

2. <!-- q: mcq id="641a9aef" -->
   In level_order, what does `level_size = len(queue)` at the top of each round do?

   - [ ] Limits the queue's memory
   - [x] Fixes how many nodes belong to the current level before their children are added
   - [ ] Counts the total number of nodes
   - [ ] Stops the loop at the last level

   <details><summary>Answer</summary>

   It snapshots the size of this level. The loop pops exactly that many, so the children it adds wait for the next round.

   </details>

3. <!-- q: mcq id="54abab0d" -->
   In "rotting oranges", what makes the BFS multi-source?

   - [ ] Running a separate BFS from each rotten orange
   - [x] Putting every rotten orange in the queue before the first round
   - [ ] Using two queues
   - [ ] Checking 8 neighbours instead of 4

   <details><summary>Answer</summary>

   All the starting points go in the queue at once, so the rot spreads from all of them together, one ring per minute.

   </details>

4. <!-- q: mcq id="fdf4e905" -->
   Compared with DFS, when does BFS cost more memory?

   - [ ] On deep, narrow graphs
   - [x] On wide graphs, where a whole level can sit in the queue
   - [ ] Never
   - [ ] Only on weighted graphs

   <details><summary>Answer</summary>

   On wide graphs. The queue can hold a whole level at once, up to O(V) nodes.

   </details>

5. <!-- q: open id="bb92989e" -->
   Why does BFS find the shortest path in an unweighted graph?

   <details><summary>Answer</summary>

   It visits every node at distance k before any node at distance k + 1. So the first time it reaches the target, no shorter route can be left unexplored, and that first route has the fewest edges.

   </details>

## Check your understanding: worked problems
<!-- bite: 7b17b45a-17df-44df-ab13-334578b0463d -->

Work each one out on paper first, then type your answer.

1. <!-- q: gap id="e5f078b7" answers="4;4;5;6" -->
   Fill in the gaps. Level-order traversal of this tree, root 1:

   | Node | Left child | Right child |
   | --- | --- | --- |
   | 1 (root) | 2 | 3 |
   | 2 | 4 | 5 |
   | 3 | none | 6 |
   | 5 | 8 | none |
   | 6 | 7 | none |
   | 4, 8, 7 | none | none |

   The tree has ___ levels. The third level, left to right, is ___, ___, ___.

   <details><summary>Answer</summary>

   4 levels: [1], [2, 3], [4, 5, 6], [8, 7]. The third level is 4, 5, 6.

   </details>

2. <!-- q: exact id="63b7003b" answer="3" -->
   Rotting oranges: 2 is rotten, 1 is fresh, 0 is empty. Each minute, rot spreads to fresh oranges directly up, down, left or right. How many minutes until no fresh orange is left?

   | | col 0 | col 1 | col 2 | col 3 |
   | --- | --- | --- | --- | --- |
   | row 0 | 2 | 1 | 1 | 0 |
   | row 1 | 0 | 1 | 0 | 1 |
   | row 2 | 1 | 1 | 1 | 2 |

   <details><summary>Answer</summary>

   3. Both rotten oranges start in the queue. The last fresh orange to rot is at row 2, col 0, three steps from the nearest rotten one.

   </details>

3. <!-- q: exact id="088a4a85" answer="-1" -->
   Rotting oranges: 2 is rotten, 1 is fresh, 0 is empty. Rot spreads up, down, left and right each minute. What does oranges_rotting return for this grid?

   | | col 0 | col 1 | col 2 |
   | --- | --- | --- | --- |
   | row 0 | 2 | 1 | 0 |
   | row 1 | 0 | 0 | 1 |
   | row 2 | 1 | 1 | 1 |

   <details><summary>Answer</summary>

   −1. Only the orange at (0, 1) can rot. The bottom-right group is cut off by empty cells, so some fresh oranges never rot.

   </details>

4. <!-- q: exact id="190c3352" answer="8" -->
   In this maze you can step up, down, left or right; # is a wall. What is the fewest steps from S to E?

   | | c0 | c1 | c2 | c3 | c4 | c5 |
   | --- | --- | --- | --- | --- | --- | --- |
   | r0 | S | . | # | . | . | . |
   | r1 | . | # | # | . | # | . |
   | r2 | . | . | . | . | # | . |
   | r3 | # | . | # | . | . | E |

   <details><summary>Answer</summary>

   8. Down to r2 c0 (2 steps), right to r2 c3 (3 more), down to r3 c3 (1), right to E (2). BFS from S reaches E at distance 8.

   </details>

## 8. Practice — independent task
<!-- bite: 3ea07554-0867-48f7-ac51-8bf5b15e519e -->

**Task:** Implement a function `shortest_path(grid, start, end)` that returns the length of the shortest path from `start` to `end` in a grid (0 = empty, 1 = obstacle). Use BFS. Test it with the following cases:

- `grid = [[0,0,0],[0,1,0],[0,0,0]], start = (0,0), end = (2,2)` → expected `4`
- `grid = [[0,1],[0,0]], start = (0,0), end = (1,1)` → expected `3`

**Done when:** your function returns the correct shortest path lengths for both test cases.

---

## Practice problems
<!-- bite: 0d8d5311-9404-4f32-9fb1-24b7dcc8eccc -->

**In the [[dsa/neetcode-150/index|NeetCode 150]]** — solved and written up here:

1. [[053-binary-tree-level-order-traversal|Binary Tree Level Order Traversal]] (LeetCode #102) — BFS where the level structure *is* the answer.
2. [[054-binary-tree-right-side-view|Binary Tree Right Side View]] (LeetCode #199) — the last node of each level.
3. [[085-rotting-oranges|Rotting Oranges]] (LeetCode #994) — **multi-source** BFS: every rotten orange starts in the queue.
4. [[086-walls-and-gates|Walls and Gates]] (LeetCode #286) — multi-source again, from every gate.
5. [[092-word-ladder|Word Ladder]] (LeetCode #127) — BFS over an implicit graph whose edges you compute on demand.
6. [[080-number-of-islands|Number of Islands]] (LeetCode #200) — flood fill works either way; BFS avoids the deep recursion.
7. [[081-clone-graph|Clone Graph]] (LeetCode #133) — the same problem as the DFS version — do both and compare.

**Not in the NeetCode 150** — worth doing on LeetCode directly, since they cover multi-source and state-space BFS, which the 150 only touches:

8. 01 Matrix (#542) — multi-source BFS from every zero — the cleanest drill of that idea.
9. Shortest Path in Binary Matrix (#1091) — eight-directional BFS, returning a length.
10. Minimum Depth of Binary Tree (#111) — BFS can stop early here and DFS cannot; that is the whole lesson.
11. Open the Lock (#752) — BFS over *states*, not positions.
12. Bus Routes (#815) — BFS where the nodes are routes rather than stops.

## Before moving on
<!-- bite: 4a3895f7-9ddf-484b-8924-f40d846966fd -->

You are done with this pattern when you can, closed-book:

- [ ] Explain why BFS finds shortest paths in *unweighted* graphs and DFS does not.
- [ ] Implement level-order traversal that groups nodes by depth.
- [ ] Solve a shortest-path-on-a-grid problem independently.
- [ ] State why BFS can use far more memory than DFS on a wide graph.

**Recap:** BFS explores level by level using a queue, so the first time it reaches a node it has done so in the fewest edges — which is why it finds shortest paths in unweighted graphs. The cost is memory: the queue can hold an entire level, which on a wide graph is far more than DFS's stack depth.

**Next:** [[13-matrix-traversal|matrix-traversal]] — grids as implicit graphs, where BFS and DFS apply directly without ever building an adjacency list.

## 9. Related
<!-- bite: 7315f391-9a36-4ec3-a39d-f4e4e1ee006c -->

- [[02-breadth-first-search|bfs]] — the underlying traversal algorithm
- [[13-matrix-traversal|matrix-traversal]] — grid-specific BFS
- [[10-binary-tree-traversal-pattern|binary-tree-traversal-pattern]] — tree-specific BFS
- [[01-growth-and-asymptotic-notation|algorithms]] — where the O(V + E) framing comes from
- [[12-bfs-pattern|bfs-pattern]] — this note

---

## 10. Further reading
<!-- bite: be1a0fd0-e7dd-4d2d-9f83-77b141eec417 -->

The pattern appears in many contexts beyond LeetCode:

- **Network routing:** Finding shortest paths in networks
- **Web crawling:** Crawling pages at depth 1 before crawling linked pages at depth 2
- **Social networks:** Finding connection degrees between people
- **Game AI:** Finding shortest paths in game maps

The core idea — exploring nodes level by level using a queue — is a fundamental algorithmic technique that appears whenever you need to find the shortest path or process nodes in order of their distance from a starting point.

## About this lesson
<!-- bite: 1b1248f5-8509-4eab-baae-ebdec3663bc0 -->

**Level:** Intermediate. **Covers:** A university-level introduction to the BFS problem-solving pattern: what it is, why it exists, how it works, and how to implement it independently.
