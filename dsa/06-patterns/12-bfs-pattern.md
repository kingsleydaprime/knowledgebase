# Pattern: BFS as a Problem-Solving Pattern

**[Intermediate]** — A university-level introduction to the BFS problem-solving pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You should understand BFS traversal. See [[03-bfs|bfs]] if needed.
- You should understand queues. See [[07-stacks-and-queues|stacks and queues]] if needed.

**What you will be able to do after this lesson:**

1. Define the BFS problem-solving pattern and explain when to reach for it.
2. Implement level-order tree traversal using BFS.
3. Apply the pattern to multi-source spreading problems.
4. Explain why BFS guarantees shortest paths in unweighted graphs.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)

Imagine you're building a social network and you want to find the shortest connection path between two people. You could check all paths of length 1, then all paths of length 2, and so on. This is exactly what BFS does: explore nodes level by level, expanding outward in concentric rings from a starting vertex.

The mechanics — queue-based, level by level, why it guarantees shortest paths — are covered in [[03-bfs|bfs]]. This note is about recognizing the problem shape: **anything phrased as "minimum steps/levels/time to reach X"** in an unweighted setting is almost always BFS from the start state.

---

## 2. Definitions and terminology

| Term                      | Plain-English definition                                                                  | Example / analogy                                                   |
| ------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| **BFS**                   | Breadth-first search: explore nodes level by level, expanding outward in concentric rings | Ripples expanding outward from a pebble dropped in water            |
| **Level-order traversal** | Process a tree level by level                                                             | Print a tree level by level                                         |
| **Multi-source BFS**      | Start BFS from all initial sources simultaneously                                         | Rotting oranges: all rotten oranges spread simultaneously           |
| **Shortest path**         | The path with the fewest edges between two nodes                                          | The shortest connection path between two people in a social network |

---

## 3. How it works — step by step

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

```
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

O(V + E), or O(rows × cols) on a grid — same as plain BFS.

---

## 6. Tradeoffs and limitations

- **BFS guarantees shortest paths in unweighted graphs.** DFS does not.
- **BFS uses more memory than DFS** for wide graphs, because the queue can grow to O(V) in the worst case.
- **Multi-source BFS** is useful when you have multiple starting points and want to find the minimum distance from any starting point.

---

## 7. Check your understanding (self-assessment)

Attempt these without the note, then compare your reasoning below.

1. **Question:** Given a binary tree, trace through the level-order traversal algorithm step by step.
2. **Question:** Why does BFS guarantee shortest paths in unweighted graphs?
3. **Question:** What's the difference between single-source and multi-source BFS?

### Answers — after your attempt

1. Start with root in queue. Process root (level 0), add children to queue. Process children (level 1), add grandchildren to queue. Continue until queue is empty.
2. BFS explores all nodes at distance k before touching distance k+1. So the very first time BFS reaches a target node, it is guaranteed to have arrived via the shortest possible path (fewest edges).
3. Single-source BFS starts from one node. Multi-source BFS starts from all initial sources simultaneously. The number of levels processed is the time/distance the spread takes.

---

## 8. Practice — independent task

**Task:** Implement a function `shortest_path(grid, start, end)` that returns the length of the shortest path from `start` to `end` in a grid (0 = empty, 1 = obstacle). Use BFS. Test it with the following cases:

- `grid = [[0,0,0],[0,1,0],[0,0,0]], start = (0,0), end = (2,2)` → expected `4`
- `grid = [[0,1],[0,0]], start = (0,0), end = (1,1)` → expected `3`

**Done when:** your function returns the correct shortest path lengths for both test cases.

---

## 9. Related

- [[03-bfs|bfs]] — the underlying traversal algorithm
- [[13-matrix-traversal|matrix-traversal]] — grid-specific BFS
- [[10-binary-tree-traversal-pattern|binary-tree-traversal-pattern]] — tree-specific BFS
- [[01-algorithms|algorithms]] — where the O(V + E) framing comes from
- [[12-bfs-pattern|bfs-pattern]] — this note

---

## 10. Further reading

The pattern appears in many contexts beyond LeetCode:

- **Network routing:** Finding shortest paths in networks
- **Web crawling:** Crawling pages at depth 1 before crawling linked pages at depth 2
- **Social networks:** Finding connection degrees between people
- **Game AI:** Finding shortest paths in game maps

The core idea — exploring nodes level by level using a queue — is a fundamental algorithmic technique that appears whenever you need to find the shortest path or process nodes in order of their distance from a starting point.
