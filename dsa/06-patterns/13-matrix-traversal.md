# Pattern: Matrix Traversal

**[Intermediate]** — A university-level introduction to the matrix traversal pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You should understand DFS and BFS. See [[02-dfs|dfs]] and [[03-bfs|bfs]] if needed.
- You should understand 2D arrays. See [[01-arrays|arrays]] if needed.

**What you will be able to do after this lesson:**

1. Define the matrix traversal pattern and explain why a 2D grid is an implicit graph.
2. Implement flood fill using DFS on a grid.
3. Apply the pattern to counting connected regions (number of islands).
4. Explain the bounds check and why it's the key difference from plain graph traversal.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)

Imagine you're building a game like Minesweeper or Go. The game board is a 2D grid, and you need to find connected regions of cells (e.g., all empty cells connected to a clicked cell, or all stones of the same color). The grid is a graph where each cell is a node, and each cell is connected to its neighbors (usually 4, sometimes 8).

Once you see it that way, DFS and BFS apply directly; there's no new algorithm here, just a different way of expressing "neighbors."

---

## 2. Definitions and terminology

| Term                 | Plain-English definition                                                              | Example / analogy                                      |
| -------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| **Grid**             | A 2D array of cells                                                                   | A game board, an image                                 |
| **Implicit graph**   | A graph where nodes and edges are defined by the grid structure, not explicitly given | A grid where each cell is connected to its 4 neighbors |
| **Flood fill**       | Fill a connected region with a new value                                              | The "bucket fill" tool in paint programs               |
| **Connected region** | A set of cells that are connected to each other                                       | An island in a sea of water                            |
| **Bounds check**     | Checking if a cell is within the grid boundaries                                      | Making sure you don't go off the edge of the board     |

---

## 3. How it works — step by step

Instead of an adjacency list, neighbors are computed from `(row, col)` using direction offsets:

```python
directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]   # right, left, down, up
```

### Flood fill

```python
def flood_fill(image, sr, sc, new_color):
    old_color = image[sr][sc]
    if old_color == new_color:
        return image
    rows, cols = len(image), len(image[0])

    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols):
            return
        if image[r][c] != old_color:
            return
        image[r][c] = new_color
        for dr, dc in directions:
            dfs(r + dr, c + dc)

    dfs(sr, sc)
    return image
```

The **bounds check** (`0 <= r < rows and 0 <= c < cols`) is the one thing this pattern adds on top of plain graph DFS/BFS — there's no explicit neighbor list to bound the search, so the traversal has to check for the grid's edges itself. Marking a cell visited (here, by overwriting its value) still serves the same purpose it does in any graph traversal — avoiding revisiting and infinite loops.

### Counting connected regions ("Number of Islands")

Same traversal, but instead of one flood fill from a given start, loop over every cell and start a **new** DFS/BFS from any unvisited land cell — each one you start from is a new island, and the traversal marks everything connected to it as visited so it isn't counted twice.

```python
def num_islands(grid):
    rows, cols = len(grid), len(grid[0])
    visited = set()

    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols): return
        if (r, c) in visited or grid[r][c] == "0": return
        visited.add((r, c))
        for dr, dc in directions:
            dfs(r + dr, c + dc)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                dfs(r, c)
                count += 1
    return count
```

This "loop over every node, start a fresh traversal from any unvisited one" structure is exactly the disconnected-graph handling described in [[06-graphs|graphs]] — a grid is just a graph that happens to have a lot of disconnected components (the separate islands).

---

## 4. Implementation — complete runnable example

**Runnable example:** save as `matrix_traversal_lab.py` and run `python3 matrix_traversal_lab.py`. It uses only Python's standard library and creates no external files.

```python
def flood_fill(image, sr, sc, new_color):
    """Fill a connected region with a new color."""
    old_color = image[sr][sc]
    if old_color == new_color:
        return image
    rows, cols = len(image), len(image[0])

    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols):
            return
        if image[r][c] != old_color:
            return
        image[r][c] = new_color
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            dfs(r + dr, c + dc)

    dfs(sr, sc)
    return image


def num_islands(grid):
    """Count the number of connected regions (islands) in a grid."""
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    visited = set()

    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols):
            return
        if (r, c) in visited or grid[r][c] == "0":
            return
        visited.add((r, c))
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            dfs(r + dr, c + dc)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                dfs(r, c)
                count += 1
    return count


def max_area_of_island(grid):
    """Find the maximum area of an island in a grid."""
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    visited = set()

    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols):
            return 0
        if (r, c) in visited or grid[r][c] == "0":
            return 0
        visited.add((r, c))
        area = 1
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            area += dfs(r + dr, c + dc)
        return area

    max_area = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                max_area = max(max_area, dfs(r, c))
    return max_area


if __name__ == "__main__":
    # Test case 1: flood fill
    image1 = [
        [1, 1, 1],
        [1, 1, 0],
        [1, 0, 1]
    ]
    result1 = flood_fill(image1, 1, 1, 2)
    print(f"Test 1 - flood fill:")
    print(f"image={image1} -> {result1}")
    expected1 = [
        [2, 2, 2],
        [2, 2, 0],
        [2, 0, 1]
    ]
    assert result1 == expected1, f"Expected {expected1}, got {result1}"

    # Test case 2: number of islands
    grid2 = [
        ["1", "1", "0", "0", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "1", "1"]
    ]
    result2 = num_islands(grid2)
    print(f"\nTest 2 - number of islands:")
    print(f"grid={grid2} -> {result2}")
    assert result2 == 3, f"Expected 3, got {result2}"

    # Test case 3: max area of island
    grid3 = [
        ["1", "1", "0", "0", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "1", "1"]
    ]
    result3 = max_area_of_island(grid3)
    print(f"\nTest 3 - max area of island:")
    print(f"grid={grid3} -> {result3}")
    assert result3 == 4, f"Expected 4, got {result3}"

    print("\nmatrix_traversal_lab: passed")
```

Expected output:

```
Test 1 - flood fill:
image=[[2, 2, 2], [2, 2, 0], [2, 0, 1]] -> [[2, 2, 2], [2, 2, 0], [2, 0, 1]]

Test 2 - number of islands:
grid=[['1', '1', '0', '0', '0'], ['1', '1', '0', '0', '0'], ['0', '0', '1', '0', '0'], ['0', '0', '0', '1', '1']] -> 3

Test 3 - max area of island:
grid=[['1', '1', '0', '0', '0'], ['1', '1', '0', '0', '0'], ['0', '0', '1', '0', '0'], ['0', '0', '0', '1', '1']] -> 4

matrix_traversal_lab: passed
```

---

## 5. Complexity

O(rows × cols) — each cell is visited a constant number of times regardless of grid shape.

---

## 6. Tradeoffs and limitations

- **Grid size matters.** For very large grids, recursion depth may be an issue. Use an iterative BFS/DFS with an explicit stack/queue instead.
- **8-directional neighbors.** Some problems use 8 neighbors (including diagonals). Adjust the `directions` list accordingly.
- **Visited marking.** Marking a cell visited by overwriting its value works for flood fill, but for other problems you may need a separate `visited` set.

---

## 7. Check your understanding (self-assessment)

Attempt these without the note, then compare your reasoning below.

1. **Question:** Given a grid, trace through the flood fill algorithm step by step.
2. **Question:** Why is the bounds check the key difference from plain graph DFS/BFS?
3. **Question:** How would you modify the algorithm to count islands using BFS instead of DFS?

### Answers — after your attempt

1. Start at the given cell, mark it as visited, then recursively visit all 4 neighbors that have the same old color. Continue until all connected cells with the old color are visited.
2. In a plain graph, neighbors are given explicitly (adjacency list). In a grid, neighbors are computed from `(row, col)` using direction offsets, and the bounds check ensures you don't go off the grid.
3. Replace the recursive DFS with an iterative BFS using a queue. Start by adding the starting cell to the queue. While the queue is not empty, pop a cell, mark it as visited, and add all unvisited neighbors with the same color to the queue.

---

## 8. Practice — independent task

**Task:** Implement a function `count_islands(grid)` that returns the number of islands in a grid. Use the matrix traversal pattern. Test it with the following cases:

- `grid = [["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]` → expected `1`
- `grid = [["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]` → expected `3`

**Done when:** your function returns the correct number of islands for both test cases.

---

## 9. Related

- [[02-dfs|dfs]] — the underlying traversal algorithm
- [[12-bfs-pattern|bfs-pattern]] — BFS variant for matrix traversal
- [[06-graphs|graphs]] — grids as implicit graphs
- [[01-arrays|arrays]] — the underlying data structure
- [[13-matrix-traversal|matrix-traversal]] — this note

---

## 10. Further reading

The pattern appears in many contexts beyond LeetCode:

- **Image processing:** Flood fill, connected component labeling
- **Game development:** Pathfinding on grids, territory control
- **Geographic information systems:** Finding connected regions on maps
- **Network analysis:** Finding connected components in network topologies

The core idea — treating a 2D grid as an implicit graph and using DFS/BFS to explore connected regions — is a fundamental algorithmic technique that appears whenever you need to find connected components or spread across a grid.
