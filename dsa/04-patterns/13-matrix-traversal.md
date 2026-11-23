---
id: fed2a43a-10e2-4b26-ad52-ba487ee0ca87
---

# Pattern: Matrix Traversal

Matrix traversal is moving through a grid of cells, row by row or from one cell to its neighbours, to solve a problem. Many puzzles are grids underneath. Counting islands on a map, filling an area with colour in a paint app and moving pieces in a board game are all matrix traversal.

## Before you start
<!-- bite: 6fecbe87-b97a-4097-8a28-fdab4c7659c5 -->

- You should understand DFS and BFS. See [[01-depth-first-search|dfs]] and [[02-breadth-first-search|bfs]] if needed.
- You should understand 2D arrays. See [[01-arrays|arrays]] if needed.

**What you will be able to do after this lesson:**

1. Define the matrix traversal pattern and explain why a 2D grid is an implicit graph.
2. Implement flood fill using DFS on a grid.
3. Apply the pattern to counting connected regions (number of islands).
4. Explain the bounds check and why it's the key difference from plain graph traversal.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)
<!-- bite: 791275eb-4ab0-47ab-98ba-f02efce512eb -->

Imagine you're building a game like Minesweeper or Go. The game board is a 2D grid, and you need to find connected regions of cells (e.g., all empty cells connected to a clicked cell, or all stones of the same color). The grid is a graph where each cell is a node, and each cell is connected to its neighbors (usually 4, sometimes 8).

Once you see it that way, DFS and BFS apply directly; there's no new algorithm here, just a different way of expressing "neighbors."

---

## 2. Definitions and terminology
<!-- bite: 9b1a2a10-cc45-4435-84ea-b6383f845253 -->

| Term                 | Plain-English definition                                                              | Example / analogy                                      |
| -------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| **Grid**             | A 2D array of cells                                                                   | A game board, an image                                 |
| **Implicit graph**   | A graph where nodes and edges are defined by the grid structure, not explicitly given | A grid where each cell is connected to its 4 neighbors |
| **Flood fill**       | Fill a connected region with a new value                                              | The "bucket fill" tool in paint programs               |
| **Connected region** | A set of cells that are connected to each other                                       | An island in a sea of water                            |
| **Bounds check**     | Checking if a cell is within the grid boundaries                                      | Making sure you don't go off the edge of the board     |

---

## 3. How it works — step by step
<!-- bite: 454818b5-3c79-4822-b365-77886520d369 -->

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

This "loop over every node, start a fresh traversal from any unvisited one" structure is exactly the disconnected-graph handling described in [[09-graphs/index|graphs]] — a grid is just a graph that happens to have a lot of disconnected components (the separate islands).

---

## 4. Implementation — complete runnable example
<!-- bite: aa77d1dc-917a-4d21-a70b-e6567ea4950e -->

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

```text
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
<!-- bite: 70e42f49-8dba-4bda-ba05-9102dc8fae4f -->

O(rows × cols) — each cell is visited a constant number of times regardless of grid shape.

---

## 6. Tradeoffs and limitations
<!-- bite: 245987af-e41c-470e-a8fa-3ac071a05ac3 -->

- **Grid size matters.** For very large grids, recursion depth may be an issue. Use an iterative BFS/DFS with an explicit stack/queue instead.
- **8-directional neighbors.** Some problems use 8 neighbors (including diagonals). Adjust the `directions` list accordingly.
- **Visited marking.** Marking a cell visited by overwriting its value works for flood fill, but for other problems you may need a separate `visited` set.

---

## Check your understanding
<!-- bite: dd2f88f4-8369-4b62-b6f7-38008a75fc9c -->

Try each one before you open the answer.

1. <!-- q: mcq id="c5dd75a0" -->
   On a grid there is no adjacency list. What does grid traversal add on top of plain graph DFS or BFS?

   - [ ] A priority queue
   - [x] A bounds check, 0 ≤ r < rows and 0 ≤ c < cols, before using a neighbour
   - [ ] Sorting the cells
   - [ ] A second visited set

   <details><summary>Answer</summary>

   The bounds check. Neighbours come from direction offsets, so the code itself must stop at the edges of the grid.

   </details>

2. <!-- q: gap id="7c68f3a2" answers="2;8" -->
   Fill in the gaps. With 4-direction moves (up, down, left, right), a corner cell has ___ neighbours inside the grid. With 8-direction moves (diagonals too), a cell in the middle of the grid has ___ neighbours.

   <details><summary>Answer</summary>

   2 and 8. A corner loses the two moves that go off the edge; a middle cell keeps all eight.

   </details>

3. <!-- q: mcq id="326e67df" -->
   flood_fill returns straight away if the old colour equals the new colour. What would happen without that check?

   - [ ] Nothing changes; it is only a speed-up
   - [x] Filled cells still match the old colour, so DFS keeps revisiting them and never stops
   - [ ] It fills the whole grid
   - [ ] It raises an index error

   <details><summary>Answer</summary>

   Overwriting a cell is how flood fill marks it visited. If the new colour equals the old, nothing is marked, and the recursion bounces between neighbours forever.

   </details>

4. <!-- q: mcq id="3d2e536a" -->
   A grid is very large, and recursive DFS crashes with a recursion error. What is the fix?

   - [ ] Use 8 directions
   - [x] Use an iterative BFS or DFS with your own queue or stack
   - [ ] Remove the bounds check
   - [ ] Sort the grid first

   <details><summary>Answer</summary>

   Use an explicit queue or stack. A long snake-shaped region can be thousands of calls deep, which is past Python's recursion limit.

   </details>

5. <!-- q: open id="0a8fdba2" -->
   Number of islands loops over every cell and starts a new DFS from any land cell not yet visited. Why does this count each island exactly once?

   <details><summary>Answer</summary>

   A DFS marks every land cell connected to where it started. So the first time the loop meets a cell from an island, the whole island is marked, and later cells of that island are skipped. Each new DFS therefore begins on a different island, and counting starts counts islands.

   </details>

## Check your understanding: worked problems
<!-- bite: 0a5f7d87-6b7f-4c27-945a-85aae25edfbf -->

Work each one out on paper first, then type your answer.

1. <!-- q: exact id="1b4232df" answer="4" -->
   In this grid, 1 is land and 0 is water. Land cells join only up, down, left or right. How many islands are there?

   | | c0 | c1 | c2 | c3 | c4 |
   | --- | --- | --- | --- | --- | --- |
   | r0 | 1 | 1 | 0 | 0 | 0 |
   | r1 | 1 | 0 | 0 | 1 | 1 |
   | r2 | 0 | 0 | 0 | 1 | 0 |
   | r3 | 0 | 1 | 1 | 0 | 0 |
   | r4 | 0 | 1 | 0 | 0 | 1 |

   <details><summary>Answer</summary>

   4: the top-left group of 3, the group of 3 around r1 c3, the group of 3 around r3 c1, and the single cell at r4 c4.

   </details>

2. <!-- q: exact id="fe81794c" answer="3" -->
   In this grid, 1 is land and 0 is water. Now land cells also join diagonally (8 directions). How many islands are there?

   | | c0 | c1 | c2 | c3 | c4 |
   | --- | --- | --- | --- | --- | --- |
   | r0 | 1 | 1 | 0 | 0 | 0 |
   | r1 | 1 | 0 | 0 | 1 | 1 |
   | r2 | 0 | 0 | 0 | 1 | 0 |
   | r3 | 0 | 1 | 1 | 0 | 0 |
   | r4 | 0 | 1 | 0 | 0 | 1 |

   <details><summary>Answer</summary>

   3. The cell r2 c3 touches r3 c2 corner to corner, so those two groups merge into one island of 6. The top-left group and the single cell at r4 c4 stay separate.

   </details>

3. <!-- q: exact id="ac98f481" answer="6" -->
   In this grid, 1 is land and 0 is water, and land joins in all 8 directions, diagonals included. What is the area (number of cells) of the largest island?

   | | c0 | c1 | c2 | c3 | c4 |
   | --- | --- | --- | --- | --- | --- |
   | r0 | 1 | 1 | 0 | 0 | 0 |
   | r1 | 1 | 0 | 0 | 1 | 1 |
   | r2 | 0 | 0 | 0 | 1 | 0 |
   | r3 | 0 | 1 | 1 | 0 | 0 |
   | r4 | 0 | 1 | 0 | 0 | 1 |

   <details><summary>Answer</summary>

   6: r1 c3, r1 c4, r2 c3, r3 c2, r3 c1 and r4 c1, joined through the diagonal from r2 c3 to r3 c2.

   </details>

4. <!-- q: exact id="ce7dd82d" answer="7" -->
   Flood fill from row 0, col 0 with new colour 7, moving up, down, left and right. How many cells change colour?

   | | c0 | c1 | c2 | c3 |
   | --- | --- | --- | --- | --- |
   | r0 | 3 | 3 | 1 | 1 |
   | r1 | 3 | 1 | 1 | 2 |
   | r2 | 3 | 3 | 2 | 2 |
   | r3 | 1 | 3 | 3 | 2 |

   <details><summary>Answer</summary>

   7. Every 3 is joined to the start: r0 c0, r0 c1, r1 c0, r2 c0, r2 c1, r3 c1 and r3 c2.

   </details>

## 8. Practice — independent task
<!-- bite: a6e1e058-cede-44d2-9172-9f0958ee773c -->

**Task:** Implement a function `count_islands(grid)` that returns the number of islands in a grid. Use the matrix traversal pattern. Test it with the following cases:

- `grid = [["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]` → expected `1`
- `grid = [["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]` → expected `3`

**Done when:** your function returns the correct number of islands for both test cases.

---

## Practice problems
<!-- bite: 79f20b19-71aa-42ec-9cdb-6fccaaadc29c -->

**In the [[dsa/neetcode-150/index|NeetCode 150]]** — solved and written up here:

1. [[080-number-of-islands|Number of Islands]] (LeetCode #200) — the flood fill everything else here varies.
2. [[082-max-area-of-island|Max Area of Island]] (LeetCode #695) — flood fill that returns a value.
3. [[084-surrounded-regions|Surrounded Regions]] (LeetCode #130) — traverse from the border inward; the inversion is the trick.
4. [[083-pacific-atlantic-water-flow|Pacific Atlantic Water Flow]] (LeetCode #417) — two traversals, then intersect the results.
5. [[085-rotting-oranges|Rotting Oranges]] (LeetCode #994) — multi-source BFS on a grid.
6. [[076-word-search|Word Search]] (LeetCode #79) — DFS with backtracking; the visited marker must be undone on the way out.
7. [[136-rotate-image|Rotate Image]] (LeetCode #48) — transpose, then reverse each row, in place.
8. [[137-spiral-matrix|Spiral Matrix]] (LeetCode #54) — four shrinking boundaries; entirely about index discipline.
9. [[138-set-matrix-zeroes|Set Matrix Zeroes]] (LeetCode #73) — using row 0 and column 0 as the marker storage.
10. [[117-longest-increasing-path-in-a-matrix|Longest Increasing Path in a Matrix]] (LeetCode #329) — DFS plus memo on a grid.

**Not in the NeetCode 150** — worth doing on LeetCode directly, since they are the plain versions, worth doing before the 150's composites:

11. Flood Fill (#733) — the pattern with nothing else attached — start here.
12. Number of Closed Islands (#1254) — #200 with the border cases inverted.
13. Spiral Matrix II (#59) — writing in spiral order rather than reading.
14. Game of Life (#289) — in-place update using encoded intermediate states.
15. Maximal Square (#221) — where matrix traversal meets DP.

## Before moving on
<!-- bite: 6212521c-68ca-434f-9fc7-de98aa598deb -->

You are done with this pattern when you can, closed-book:

- [ ] Explain why a grid is a graph and what its edges are.
- [ ] Write the direction-vector idiom for four- and eight-way movement.
- [ ] Implement flood fill or island counting independently.
- [ ] Handle bounds checking and visited marking without a separate visited array.

**Recap:** A grid is a graph whose nodes are cells and whose edges are adjacency, so DFS and BFS apply unchanged — you just compute neighbours arithmetically instead of looking them up. The recurring idioms are a direction-vector list, a bounds check, and marking visited in place when mutation is allowed.

**Next:** [[14-backtracking|backtracking]] — DFS that *undoes* its choices on the way back out, which is what you need when exploring arrangements rather than a fixed structure.

## 9. Related
<!-- bite: 6b74aeb0-2f81-478d-8ca2-52b13c43db24 -->

- [[01-depth-first-search|dfs]] — the underlying traversal algorithm
- [[12-bfs-pattern|bfs-pattern]] — BFS variant for matrix traversal
- [[09-graphs/index|graphs]] — grids as implicit graphs
- [[01-arrays|arrays]] — the underlying data structure
- [[13-matrix-traversal|matrix-traversal]] — this note

---

## 10. Further reading
<!-- bite: 95db0ac0-19ba-4269-b8f0-08f3e0ff34c8 -->

The pattern appears in many contexts beyond LeetCode:

- **Image processing:** Flood fill, connected component labeling
- **Game development:** Pathfinding on grids, territory control
- **Geographic information systems:** Finding connected regions on maps
- **Network analysis:** Finding connected components in network topologies

The core idea — treating a 2D grid as an implicit graph and using DFS/BFS to explore connected regions — is a fundamental algorithmic technique that appears whenever you need to find connected components or spread across a grid.

## About this lesson
<!-- bite: 5713cb21-25fd-4637-b577-e76b69610cc2 -->

**Level:** Intermediate. **Covers:** A university-level introduction to the matrix traversal pattern: what it is, why it exists, how it works, and how to implement it independently.
